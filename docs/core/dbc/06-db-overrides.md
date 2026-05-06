# dbc — DB override layer (`*_dbc` tables)

> Every DBC store can layer a SQL table on top of the binary file: `LoadDBC<T>(... , "<table>_dbc")` calls `DBCStorage<T>::LoadFromDB`, which delegates to `DBCDatabaseLoader`. The DB rows **override or extend** records already loaded from the `.dbc`. ~110 such tables ship under `data/sql/base/db_world/*_dbc.sql`. This is the only built-in mechanism for runtime DBC customisation; the project also ships a **patched** client `Spell.dbc` (custom IDs `100xxx` / `900xxx`) for content the override layer cannot express.

## Critical files

| File | Role |
|---|---|
| `src/server/shared/DataStores/DBCDatabaseLoader.h:24` | `struct DBCDatabaseLoader` — single-shot loader, ctor + `Load(records&, indexTable&)` |
| `src/server/shared/DataStores/DBCDatabaseLoader.cpp:24` | ctor — table name, fmt, target string pool; precomputes `_recordSize` |
| `src/server/shared/DataStores/DBCDatabaseLoader.cpp:38` | `Load(records, indexTable)` — runs `SELECT * FROM <table> ORDER BY ID DESC` |
| `src/server/shared/DataStores/DBCDatabaseLoader.cpp:40` | SQL pattern: `StringFormat("SELECT * FROM `{}` ORDER BY `ID` DESC", _sqlTableName)` |
| `src/server/shared/DataStores/DBCDatabaseLoader.cpp:55-64` | index-table grow path (DB ID > DBC max ID) |
| `src/server/shared/DataStores/DBCDatabaseLoader.cpp:85-117` | per-row fmt walker, type-switch in lock-step with SQL columns |
| `src/server/shared/DataStores/DBCDatabaseLoader.cpp:118` | `ASSERT(sqlColumnNumber == result->GetFieldCount(), …)` — column-count check |
| `src/server/shared/DataStores/DBCDatabaseLoader.cpp:136` | `CloneStringToPool` — keeps `char const*` slot alive |
| `src/server/shared/DataStores/DBCStore.cpp:74` | `DBCStorageBase::LoadFromDB` — entry from the typed wrapper |
| `src/server/game/DataStores/DBCStores.cpp:239-240` | `if (dbTable) storage.LoadFromDB(dbTable, storage.GetFormat());` |
| `data/sql/base/db_world/spell_dbc.sql` | `CREATE TABLE spell_dbc (ID, Category, …)` — 234-column mirror of `Spell.dbc` |
| `data/sql/base/db_world/spellitemenchantment_dbc.sql` | used by `mod-paragon-itemgen` |
| `data/sql/base/db_world/areatable_dbc.sql` | sample non-spell override |

## Key concepts

- **Override is a record-level upsert.** Each DB row's primary key (the `n` or `d`-indexed `ID` column) addresses the existing `T*` slot and **replaces the entire record** with DB data. There is no field-level merge: every column in the row is bound, every fmt-described field of `T` is overwritten.
- **DB rows can extend the index table.** If a DB row's ID is greater than the max ID seen in the .dbc file, `DBCDatabaseLoader::Load` reallocates and zeroes the index table (`DBCDatabaseLoader.cpp:55-64`), then writes the new slot. This is how custom IDs work: the `.dbc` doesn't need to contain ID `9001234` for an override row at that ID to "appear".
- **`ORDER BY ID DESC` is mandatory.** The select clause hard-codes `ORDER BY \`ID\` DESC` because the size of the new index table is set from the **first** row of the result (`max ID`). Without `DESC`, a DB row beyond the .dbc's range would crash with an out-of-bounds write.
- **fmt is shared, schema must match.** The same `*fmt[]` string drives the `.dbc` parser (`DBCFileLoader::AutoProduceData`) and the SQL parser (`DBCDatabaseLoader::Load` switch at `cpp:85-113`). The SQL table must have one column per fmt char in the same order; the assert at `cpp:118` catches mismatches at runtime.
- **String pool grows.** Every DB-sourced `s` (FT_STRING) value goes through `CloneStringToPool` (`cpp:136`); the heap copies are owned by the same `_stringPool` that holds the .dbc string blocks. They survive until `~DBCStorageBase`.
- **Skip chars (`x`, `X`, `d`) consume a SQL column** without writing to the host struct (`cpp:106-109`). The columns must still exist in the SQL table — leaving them out fires the column-count assert.
- **No prepared statement.** `DBCDatabaseLoader` uses `WorldDatabase.Query(StringFormat("SELECT * FROM `{}` …"))` with the table name spliced in (`cpp:40`). This bypasses the prepared-statement cache (see [`../database/02-prepared-statements.md`](../database/02-prepared-statements.md)) — acceptable because the loader runs once at startup and the names are compile-time constants.

### When the override fires

```
LoadDBC<T>(...)
  ├─ ASSERT sizeof(T) == GetFormatRecordSize(fmt)
  ├─ storage.Load(dbcPath/Foo.dbc)              ← reads binary
  ├─ for locale in availableDbcLocales:
  │     storage.LoadStringsFrom(dbcPath/<locale>/Foo.dbc)
  └─ if dbTable:
       storage.LoadFromDB("foo_dbc", fmt)        ← LAST step, AFTER locales
            └─ DBCDatabaseLoader::Load
                 ├─ SELECT * FROM foo_dbc ORDER BY ID DESC
                 ├─ resize index table to max(records, top_id+1)
                 └─ for each row: write/overwrite indexTable[ID]
```

So the precedence is **DB > all DBC locale layers**, and after `LoadDBC` returns the store cannot tell whether a given row originated in `.dbc` or DB.

### Inventory of override tables

About 110 `*_dbc` tables exist under `data/sql/base/db_world/`. The canonical mapping (`Spell.dbc → spell_dbc → spell_dbc.sql`) is the `LOAD_DBC(store, "File.dbc", "table_dbc")` line for each store in `DBCStores.cpp:272-383` — third macro arg is the SQL table name. The `_dbc` suffix marks every override table; their categories mirror the binary DBC categories listed in [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md):

- **Spell** (~13): `spell_dbc`, `spellcasttimes_dbc`, `spellcategory_dbc`, `spelldifficulty_dbc`, `spellduration_dbc`, `spellitemenchantment_dbc`, `spellradius_dbc`, `spellrange_dbc`, `spellrunecost_dbc`, `spellshapeshiftform_dbc`, `spellvisual_dbc`, `spellfocusobject_dbc`, `spellitemenchantmentcondition_dbc`.
- **Achievement / map / area / item / creature / skill / talent / faction / vehicle / character** — one `_dbc` table per `s*Store` declared in `DBCStores.h:78-198`. Examples: `map_dbc`, `areatable_dbc`, `item_dbc`, `creaturefamily_dbc`, `talent_dbc`, `chrclasses_dbc`, `vehicle_dbc`.
- **Combat / stat (`gt*`)** (~11): `gtcombatratings_dbc`, `gtchancetomeleecrit_dbc`, `gtchancetospellcrit_dbc`, `gtoctregenhp_dbc`, `gtregenhpperspt_dbc`, …
- **Misc**: `currencytypes_dbc`, `gameobjectdisplayinfo_dbc`, `glyphproperties_dbc`, `gemproperties_dbc`, `holidays_dbc`, `lfgdungeons_dbc`, `liquidtype_dbc`, `lock_dbc`, `dungeonencounter_dbc`, `mailtemplate_dbc`, `pvpdifficulty_dbc`, `questxp_dbc`, `scalingstatvalues_dbc`, `soundentries_dbc`, `summonproperties_dbc`, …

Full DB table inventory (304 tables): [`../../09-db-tables.md`](../../09-db-tables.md).

### `spell_dbc` and the `mod-paragon-itemgen` pattern

`spell_dbc` mirrors `Spell.dbc` 1-to-1 (234 columns). User-side documentation of the most-used columns lives in [`../../03-spell-system.md#spell_dbc-column-reference-most-relevant-fields`](../../03-spell-system.md). Typical usage: insert a row at a custom ID to register a server-side spell that lives only in the DB (provided the corresponding spell ID also exists in the patched client `Spell.dbc`).

`spellitemenchantment_dbc` is the override path used by `mod-paragon-itemgen` (see [`../../05-modules.md#mod-paragon-itemgen`](../../05-modules.md)). Inserting a row at an unused enchantment ID makes that enchantment usable in `item_template.RandomProperty` etc. without re-patching the client `SpellItemEnchantment.dbc` for stat values — only the **name** still requires a client patch (or the AIO bypass that the module uses). See [`../../03-spell-system.md#dbc-override-via-db`](../../03-spell-system.md).

## Flow / data shape

```
SELECT * FROM spell_dbc ORDER BY ID DESC;
        │
        ▼
DBCDatabaseLoader::Load
        │  result.GetRowCount() rows × _recordSize bytes
        ▼
new char[rowCount * recordSize]   ─┐
new uint32[rowCount] newIndexes   │  built sequentially
        │                          │
        for each row:              │
          fields = result->Fetch();│
          dataValue = &dataTable[N * recordSize]
          for each fmt char:        │  copy or skip per FT_*
            FT_INT  → reinterpret_cast<uint32*>(dataValue+off) = fields[col].Get<uint32>()
            FT_FLOAT→ … <float>
            FT_BYTE → … <uint8>
            FT_STRING→ CloneStringToPool(fields[col].Get<string>())
            FT_SORT/FT_NA/FT_NA_BYTE → ++col, no write
          ++newRecords
        │
        ▼
for i in [0, newRecords):
   indexTable[newIndexes[i]] = &dataTable[i * recordSize];
                                                │
                                                ▼
                              DBCStorage<T>::_indexTable.AsT[ID] now points
                              into the freshly-allocated dataTable region
```

The previous `.dbc`-sourced row at the same ID is **not freed** — the underlying `_dataTable` allocations stay alive (managed by `DBCStorageBase::~DBCStorageBase`). Only the index pointer is rewritten. This is harmless because `_dataTable` is one big buffer, not per-row allocations.

## Hooks & extension points

- **Insert into `*_dbc` tables.** Standard SQL — no code change required. Examples:
  - `INSERT INTO spell_dbc (ID, …) VALUES (900100, …);` to override or add a server-side spell row.
  - `INSERT INTO spellitemenchantment_dbc (ID, Effect_1, EffectPointsMin_1, EffectArg_1, Name_Lang_enUS) VALUES (900042, 5, 42, 7, '+42 Stamina');` (see [`../../03-spell-system.md#dbc-override-via-db`](../../03-spell-system.md)).
- **Module pre-load hook.** `OnLoadCustomDatabaseTable` (`World.cpp:375`) fires immediately *before* `LoadDBCStores`. Use it to install `*_dbc` rows your module ships, so they are merged in this run.
- **No partial-field overrides.** Because the loader writes the full record, leaving columns at defaults will overwrite the DBC value too. Always SELECT the existing row first if you want to "patch" one field.
- **Patched client `Spell.dbc` (this fork).** When the override layer is insufficient — typically because the client needs to know the spell exists at all (icon, tooltip, animation) — `share-public/dbc/Spell.dbc` itself is patched with custom IDs in the `100xxx` and `900xxx` ranges. Patching is done by `share-public/python_scripts/copy_spells_dbc.py` (with the 6-safeguard guard documented in [`../../03-spell-system.md#spelldbc-corruption-checks`](../../03-spell-system.md)). The same file is then read at startup by `DBCFileLoader` (see [`01-loader.md`](./01-loader.md)) — both layers can coexist on the same ID, with `spell_dbc` taking precedence by virtue of being applied last (`LoadDBC` step 4 in [`05-load-sequence.md`](./05-load-sequence.md)).

## Cross-references

- Engine-side: [`01-loader.md`](./01-loader.md), [`02-stores.md`](./02-stores.md), [`03-format-strings.md`](./03-format-strings.md), [`05-load-sequence.md`](./05-load-sequence.md), [`../database/02-prepared-statements.md`](../database/02-prepared-statements.md) (note: this loader does **not** use prepared statements), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md) (`OnLoadCustomDatabaseTable` hook)
- Project-side: [`../../03-spell-system.md#dbc-override-via-db`](../../03-spell-system.md), [`../../05-modules.md#mod-paragon-itemgen`](../../05-modules.md), [`../../06-custom-ids.md`](../../06-custom-ids.md), [`../../09-db-tables.md`](../../09-db-tables.md), [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md)
- Fork-specific: `azerothcore-wotlk/CLAUDE.md` (custom Spell.dbc rows: 100000-100027, 100201-100227, 900100-900116, 920920, …)
- External: `wiki/Dealing-with-SQL-files`, Doxygen `structDBCDatabaseLoader.html`
