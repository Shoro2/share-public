# loot/ — Loot generation

> Loot is data-driven: `*_loot_template` tables feed typed `LootStore` instances; rolls are resolved by `Loot` + `LootItem` at drop time; conditions filter who is eligible.

## Topic files

| File | Topic |
|---|---|
| [`01-loot-store.md`](./01-loot-store.md) | `LootStore` types: `LootTemplates_Creature`, `_Gameobject`, `_Item`, `_Reference`, `_Mail`, `_Disenchant`, `_Prospecting`, `_Milling`, `_Pickpocketing`, `_Skinning`, `_Spell`, `_Fishing` |
| [`02-loot-roll.md`](./02-loot-roll.md) | `LootItem`, `LootRoll`, master loot vs. group loot vs. need/greed, ML/threshold |
| [`03-loot-conditions.md`](./03-loot-conditions.md) | `ConditionMgr`, `loot_conditions`, applied to loot rows + spells + quests |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Loot/LootMgr.{h,cpp}` | Loot store types + load |
| `src/server/game/Loot/LootItemStorage.{h,cpp}` | Persistent item loot |
| `src/server/game/Conditions/ConditionMgr.{h,cpp}` | Condition evaluation |
| `src/server/game/Handlers/LootHandler.cpp` | Opcode dispatch |
| `data/sql/base/db_world/{creature,gameobject,disenchant,...}_loot_template.sql` | Static loot data |

## Cross-references

- Engine-side: [`../entities/05-creature.md`](../entities/05-creature.md), [`../entities/06-gameobject.md`](../entities/06-gameobject.md), [`../entities/07-item.md`](../entities/07-item.md), [`../handlers/00-index.md`](../handlers/00-index.md) (LootHandler)
- Project-side: [`../../05-modules.md`](../../05-modules.md) (mod-loot-filter, mod-paragon-itemgen, mod-auto-loot all hook `OnPlayerLootItem`)
- External: Doxygen for `Loot`, `LootMgr`, `ConditionMgr`
