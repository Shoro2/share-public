# dbc/ — DBC client-data loading

> How `azerothcore-wotlk` reads the binary `.dbc` files shipped with the WoW 3.3.5a client, populates ~80 typed global stores, and merges DB-side overrides on top.

## Topic files

| File | Topic |
|---|---|
| [`01-loader.md`](./01-loader.md) | `DBCFileLoader`, header validation, record + string-block layout, `AutoProduceData` / `AutoProduceStrings` |
| [`02-stores.md`](./02-stores.md) | `DBCStorage<T>` template, the ~80 `s*Store` global instances, lookup ergonomics |
| [`03-format-strings.md`](./03-format-strings.md) | Format characters (`n`, `i`, `s`, `f`, `b`, `d`, `x`), how `DBCfmt.h` rows mirror `DBCStructure.h` |
| [`04-structures.md`](./04-structures.md) | `DBCStructure.h` tour grouped by category (Spell-related, Item-related, Map-related, …) |
| [`05-load-sequence.md`](./05-load-sequence.md) | `LoadDBCStores(dataPath)` order, dependency graph, missing-file warnings |
| [`06-db-overrides.md`](./06-db-overrides.md) | `spell_dbc`, `spellitemenchantment_dbc` and other overrides, when they apply, how they merge |

## Critical files

| File | Role |
|---|---|
| `src/common/DataStores/DBCFileLoader.{h,cpp}` | Raw `.dbc` parser, field-format engine |
| `src/server/shared/DataStores/DBCStore.h` | Templated typed storage |
| `src/server/shared/DataStores/DBCStores.{h,cpp}` | Declarations + `LoadDBCStores()` |
| `src/server/shared/DataStores/DBCfmt.h` | Format strings for every typed store |
| `src/server/shared/DataStores/DBCStructure.h` | Per-DBC C++ struct definitions |
| `azerothcore-wotlk/share/dbc/*.dbc` | The actual data files (this fork ships custom `Spell.dbc`) |

## Cross-references

- Engine-side: [`../spells/02-spell-info.md`](../spells/02-spell-info.md) (heaviest DBC consumer), [`../entities/10-object-mgr.md`](../entities/10-object-mgr.md) (loads override tables)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md) (DBC overrides for custom spells, `spell_dbc` columns), [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md) (full 246-file inventory), [`../../06-custom-ids.md`](../../06-custom-ids.md) (custom ID ranges)
- Fork-specific: this fork ships a patched `Spell.dbc` with custom IDs (`100xxx`, `900xxx`) — see [`../../03-spell-system.md`](../../03-spell-system.md)
- External: `wiki/common-errors` (DBC mismatch errors), Doxygen for `DBCFileLoader`, `DBCStorage`
