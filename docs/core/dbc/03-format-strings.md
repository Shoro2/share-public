# dbc — Format strings (`DBCfmt.h`)

> Each DBC has a single `char constexpr Xxxfmt[]` that names every on-disk field by type, in order. The format is consumed by both `DBCFileLoader` (to read the binary) and the matching `DBCStorage<T>` (its host-side struct in [`04-structures.md`](./04-structures.md) must be byte-compatible). When format and struct drift, `LoadDBC` aborts at startup.

## Critical files

| File | Role |
|---|---|
| `src/common/DataStores/DBCFileLoader.h:25` | `enum DbcFieldFormat` — the canonical character → meaning map |
| `src/server/shared/DataStores/DBCfmt.h:21` | first format string (`Achievementfmt`) — file is one string per DBC |
| `src/server/shared/DataStores/DBCfmt.h:108` | `SpellEntryfmt` — the longest, 234 chars |
| `src/server/shared/DataStores/DBCfmt.h:71` | `Itemfmt = "niiiiiii"` — minimal example |
| `src/server/shared/DataStores/DBCfmt.h:21` | `Achievementfmt` — typical with a `s` localized name run |
| `src/common/DataStores/DBCFileLoader.cpp:128` | `GetFormatRecordSize(format, *index_pos)` — host-side `sizeof(record)` summed from chars |
| `src/server/game/DataStores/DBCStores.cpp:213-217` | `LoadDBC<T>` `ASSERT(GetFormatRecordSize(fmt) == sizeof(T))` — the drift check |

## Key concepts

- **One character = one on-disk field.** `strlen(fmt)` must equal the WDBC header's `fieldCount` or `AutoProduceData` returns null (`DBCFileLoader.cpp:190`).
- **The 9 format characters** (verified against `DBCFileLoader.h:25-36`):

| Char | Constant | On-disk size | Host-side type | Notes |
|---|---|---|---|---|
| `n` | `FT_IND` | 4 bytes | `uint32` | Indexed primary key — at most one per fmt; the value drives the `T**` slot |
| `i` | `FT_INT` | 4 bytes | `uint32` (or `int32` in struct) | Plain integer field |
| `f` | `FT_FLOAT` | 4 bytes | `float` | IEEE-754 little-endian |
| `s` | `FT_STRING` | 4 bytes | `char const*` | On disk: offset into string block; resolved by `AutoProduceStrings` |
| `b` | `FT_BYTE` | 1 byte | `uint8` | Sub-byte alignment is on the file (not the struct) |
| `x` | `FT_NA` | 4 bytes | — (skipped) | Field exists on disk, **not stored** in the host struct |
| `X` | `FT_NA_BYTE` | 1 byte | — (skipped) | Same as `x` but byte-wide |
| `d` | `FT_SORT` | 4 bytes | — (skipped, but acts as index) | Like `n`, but the value is **not stored**; used when the struct lacks an explicit ID field |
| `l` | `FT_LOGIC` | — | — | **Unsupported** — `ASSERT(false)` in all switch arms; reserved for future expansions |

- **`n` vs `d`** — `n` keeps the ID column in the C++ struct, `d` does not. `Itemfmt = "niiiiiii"` → `ItemEntry` starts with `uint32 ID`. `MapDifficultyEntryfmt = "diisxxx…"` → `MapDifficultyEntry` skips the disk-side ID and starts with `uint32 MapId`.
- **String-name runs** — most localized strings are 17 fields wide on disk: 16 locale slots (`s` × 16) plus a `uint32` flag word (`x`). The pattern `ssssssssssssssssx` is everywhere in `DBCfmt.h` (e.g. `Achievementfmt:21` has it twice for `name` and a skipped `description`). Only the first non-empty locale `s` is kept; later locale overlays via `LoadStringsFrom` fill the still-empty slots (see [`01-loader.md`](./01-loader.md)).
- **Skipped fields are not free** — `x` and `X` advance the on-disk read cursor but emit no host-side bytes. The matching C++ struct documents them as `// 4 unused` comments next to the field index.
- **Drift check at startup** — `LoadDBC<T>(…, "Foo.dbc", "foo_dbc")` (`DBCStores.cpp:213`) asserts `DBCFileLoader::GetFormatRecordSize(storage.GetFormat()) == sizeof(T)` before doing anything else. If you add or remove a non-skipped field in either the fmt or the struct without updating the other, the server fails to start with `LoadDBC_assert_print` logging "Size … set by format string (…) not equal size of C++ structure (…)".

## Flow / data shape

Three example formats and what they decode into.

### Item.dbc — minimal

```
Itemfmt = "niiiiiii"                          // DBCfmt.h:71

struct ItemEntry {                            // DBCStructure.h:1142
    uint32 ID;            // n
    uint32 ClassID;       // i
    uint32 SubclassID;    // i
    int32  SoundOverrideSubclassID; // i (signed in struct, fmt is just "size")
    int32  Material;      // i
    uint32 DisplayInfoID; // i
    uint32 InventoryType; // i
    uint32 SheatheType;   // i
};                        // sizeof = 32 bytes ↔ GetFormatRecordSize("niiiiiii") = 32
```

### Achievement.dbc — typical struct with strings, dropped fields, and back-end data

```
Achievementfmt = "niixssssssssssssssssxxxxxxxxxxxxxxxxxxiixixxxxxxxxxxxxxxxxxxii"
                  ^                  ^                ^^ ^      ^^                ^^
                  ID required-faction │              Name run + lang_mask         count + refAchievement
                                      mapID
```

Fields summary (`DBCStructure.h:39`):
- `n` ID, `i` requiredFaction (signed in struct), `i` mapID, `x` parentAchievement (skipped)
- `ssssssssssssssssx` 16-locale Name + lang_mask (the `Name` array, `lang_mask` skipped)
- `xxxxxxxxxxxxxxxxxx` 18× description+desc_flags (skipped — server doesn't need it)
- `i` categoryId, `i` points, `x` OrderInCategory, `i` flags, `x` icon
- `xxxxxxxxxxxxxxxxxx` 18× titleReward+titleReward_flags (skipped)
- `i` count, `i` refAchievement

### Spell.dbc — 234 fields (the longest)

`SpellEntryfmt` (`DBCfmt.h:108`) is 234 characters — **never inline this in a doc**. The matching `SpellEntry` struct is `DBCStructure.h:1641-1750`. Field-by-field comments in the struct align with the on-disk index. The format mixes long `i`-runs (effect arrays of 3, e.g. `iii fff` = the three-effect die-sides plus three real-points-per-level), the obligatory two `ssssssssssssssssx` runs (Name + Rank), and two `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` blocks for Description / ToolTip that the server doesn't need.

This fork ships a **patched** `Spell.dbc` (custom IDs in the `100xxx` and `900xxx` ranges) — the format is unchanged, only rows are added. See `azerothcore-wotlk/CLAUDE.md` and [`../../06-custom-ids.md`](../../06-custom-ids.md).

## Hooks & extension points

—. Format strings are append-only inside `DBCfmt.h`; you cannot register one from a module. To override DBC content at runtime use the `LoadFromDB` path described in [`06-db-overrides.md`](./06-db-overrides.md), which reuses the same fmt to parse the `*_dbc` SQL table column-by-column.

When you change a fmt:
1. Edit `DBCfmt.h` (string constant).
2. Edit the matching struct in `DBCStructure.h` so `sizeof(struct)` equals the new `GetFormatRecordSize(fmt)`.
3. Edit the matching `_dbc` SQL schema under `data/sql/base/db_world/` if a `LoadFromDB` table exists for it (the `DBCDatabaseLoader` walks fmt × SQL columns in lock-step — `DBCDatabaseLoader.cpp:85-117`).
4. Verify by starting the server: a mismatch fires `LOG_ERROR("dbc", "Size of '<file>' set by format string …")` then `ASSERT`s.

## Cross-references

- Engine-side: [`01-loader.md`](./01-loader.md), [`02-stores.md`](./02-stores.md), [`04-structures.md`](./04-structures.md), [`06-db-overrides.md`](./06-db-overrides.md)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md)
- Fork-specific: `azerothcore-wotlk/CLAUDE.md` (custom Spell.dbc — same format, additional rows)
- External: Doxygen `DBCFileLoader_8h.html` (the `DbcFieldFormat` enum)
