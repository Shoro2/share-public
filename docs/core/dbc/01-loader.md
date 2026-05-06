# dbc — DBCFileLoader (raw `.dbc` parser)

> The low-level WDBC binary reader: opens a `.dbc`, validates the WDBC magic, parses the 5-uint32 header, computes per-field offsets from a format string, and produces a typed flat record array plus a string pool. It knows nothing about which DBC it is reading — the caller (`DBCStorage<T>`, see [`02-stores.md`](./02-stores.md)) supplies the format. Format characters are documented in [`03-format-strings.md`](./03-format-strings.md).

## Critical files

| File | Role |
|---|---|
| `src/common/DataStores/DBCFileLoader.h:25` | `enum DbcFieldFormat` — the 9 format characters (`x`, `X`, `s`, `f`, `i`, `b`, `d`, `n`, `l`) |
| `src/common/DataStores/DBCFileLoader.h:38` | `class DBCFileLoader` declaration |
| `src/common/DataStores/DBCFileLoader.h:46` | nested `class Record` — typed accessors `getFloat/getUInt/getUInt8/getString` |
| `src/common/DataStores/DBCFileLoader.h:95` | `AutoProduceData(fmt, count, indexTable)` — builds the typed array |
| `src/common/DataStores/DBCFileLoader.h:96` | `AutoProduceStrings(fmt, dataTable)` — resolves `char*` slots into a string pool |
| `src/common/DataStores/DBCFileLoader.h:97` | static `GetFormatRecordSize(format, index_pos)` — host-side `sizeof(record)` from the format string |
| `src/common/DataStores/DBCFileLoader.cpp:24` | `Load(filename, fmt)` — header parse + raw read |
| `src/common/DataStores/DBCFileLoader.cpp:47` | `WDBC` magic check (`0x43424457`) |
| `src/common/DataStores/DBCFileLoader.cpp:85-99` | per-field byte offset computation (byte vs 4-byte) |
| `src/common/DataStores/DBCFileLoader.cpp:101-104` | single-shot `fread` of records + string block |
| `src/common/DataStores/DBCFileLoader.cpp:128` | `GetFormatRecordSize` — sums the host-side struct size |
| `src/common/DataStores/DBCFileLoader.cpp:176` | `AutoProduceData` — allocates `dataTable` + index table, fills records |
| `src/common/DataStores/DBCFileLoader.cpp:276` | `AutoProduceStrings` — copies string-block, fixes `char*` pointers |

## Key concepts

- **WDBC header (20 bytes)** — five `uint32`s in this order: magic (`'WDBC'` = `0x43424457`), `recordCount`, `fieldCount`, `recordSize`, `stringSize`. Byte-swapped through `EndianConvert` for big-endian hosts.
- **Two-region payload** — `data[recordSize * recordCount]` followed immediately by `stringTable[stringSize]`. Both are loaded in a single `fread` (`cpp:104`).
- **Field offset table** — `fieldsOffset[fieldCount]`, computed once at load: byte fields (`b`, `X`) advance by 1, all other fields by 4. This lets `Record::getUInt(i)` index into a record without rescanning the format.
- **Format string** — a per-DBC C-string (e.g. `"niiiiiii"` for `Item.dbc`, see [`03-format-strings.md`](./03-format-strings.md)). `strlen(format)` must equal `fieldCount` or `AutoProduceData` returns `nullptr` (`cpp:190`).
- **Index field (`n` / `d`)** — at most one per format. With `n` (the indexed-uint32 ID) the index table is sized to `max(id) + 1` and entries are sparse (records with no entry for that ID stay `nullptr`). With `d` (sort-only) the field is consumed for ordering but **not stored** in the C++ struct, so the on-disk layout is one `uint32` wider than `sizeof(T)`.
- **String pool** — strings inside records are stored as offsets into the on-disk string block; `AutoProduceStrings` copies the block once and rewrites every `char*` slot in the typed array to point inside the copy. The original on-disk buffer is freed in `~DBCFileLoader`.
- **Locale layering** — `Load` reads only the default-locale strings. To overlay another locale the caller invokes `LoadStringsFrom(localizedPath)` which calls `AutoProduceStrings` again on a fresh dbc file but writes only into still-empty `char*` slots (`DBCFileLoader.cpp:307` — `if (!*slot || !**slot)`). Multiple `_stringPool` blocks accumulate in the storage (see [`02-stores.md`](./02-stores.md)).

## Flow / data shape

```
+0  uint32 magic     = 'WDBC' (0x43424457)
+4  uint32 recordCount
+8  uint32 fieldCount
+12 uint32 recordSize       // bytes per record, ≥ ΣfieldsOffset
+16 uint32 stringSize
+20 unsigned char data[recordSize * recordCount]
... unsigned char stringTable[stringSize]
```

`Load(path, fmt)`:
1. `fopen` → read 5 header `uint32`s, validate magic. Bail on any read short-count.
2. Allocate `fieldsOffset[fieldCount]`, walk `fmt` to fill it (`b`/`X` = +1 byte, everything else = +4 bytes).
3. Allocate `data[recordSize * recordCount + stringSize]`, slurp the rest of the file.
4. `stringTable` points at `data + recordSize*recordCount`.

`DBCStorageBase::Load` (the caller, see [`02-stores.md`](./02-stores.md)) then:
1. `dbc.AutoProduceData(fmt, _indexTableSize, indexTable)` →
   - new `dataTable[recordCount * GetFormatRecordSize(fmt)]`,
   - new `indexTable[indexTableSize]`,
   - copies each on-disk field into the host-side struct field per format char,
   - `n`/`d` field is read but acts as the index lookup,
   - returns `dataTable` (caller stores into `_dataTable`).
2. `dbc.AutoProduceStrings(fmt, dataTable)` → copies `stringTable` into a fresh `stringPool`, rewrites every `FT_STRING` slot to point inside it; returns the pool (caller pushes onto `_stringPool`).
3. The temporary `DBCFileLoader` goes out of scope; its on-disk buffer is `delete[]`-ed.

The host-side row size is computed independently from `recordSize` by `GetFormatRecordSize`, because the C++ `struct` may collapse fields the on-disk record skips (`d` and `x`). `LoadDBC<T>` asserts `GetFormatRecordSize(fmt) == sizeof(T)` at startup (`DBCStores.cpp:216`); a mismatch means the format string and the struct layout drifted (see [`03-format-strings.md`](./03-format-strings.md) and [`05-load-sequence.md`](./05-load-sequence.md)).

## Hooks & extension points

—. The loader is a leaf component; extension happens one layer up in `DBCStorage<T>` (`SetEntry`, `LoadFromDB`) — see [`02-stores.md`](./02-stores.md) and [`06-db-overrides.md`](./06-db-overrides.md). To add a new file format character you would have to extend both `DBCFileLoader::AutoProduceData` and `GetFormatRecordSize` (currently any unknown char hits the `default: ASSERT(false)` arm at `cpp:163`/`267`/`323`).

`FT_LOGIC` (`'l'`) is **declared but unsupported** — it `ASSERT`s in all three switch arms; it exists for cross-version compatibility with newer expansions.

## Cross-references

- Engine-side: [`02-stores.md`](./02-stores.md), [`03-format-strings.md`](./03-format-strings.md), [`05-load-sequence.md`](./05-load-sequence.md), [`06-db-overrides.md`](./06-db-overrides.md)
- Project-side: [`../../03-spell-system.md#dbc-system`](../../03-spell-system.md), [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md)
- Fork-specific: this fork ships a patched `Spell.dbc` — see `azerothcore-wotlk/CLAUDE.md` and [`../../06-custom-ids.md`](../../06-custom-ids.md)
- External: Doxygen `classDBCFileLoader.html`, `DBCFileLoader_8h.html`
