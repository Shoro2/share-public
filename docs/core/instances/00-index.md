# instances/ — Dungeons, raids, instance saves, dungeon finder

> Instances are private `Map` copies. Lockouts live in `InstanceSave` (per group/account, persisted), boss progress + scripted events live in `InstanceScript`, the dungeon finder queues groups via `LFGMgr`.

## Topic files

| File | Topic |
|---|---|
| [`01-instance-save.md`](./01-instance-save.md) | `InstanceSave`, `InstanceSaveMgr`, raid/heroic locks, character-bind vs. group-bind |
| [`02-instance-script.md`](./02-instance-script.md) | `InstanceScript` lifecycle, `OnCreatureCreate`/`OnGameObjectCreate`, `SetData`/`GetData`, `EncounterState` enum |
| [`03-difficulty.md`](./03-difficulty.md) | `Difficulty` enum, normal/heroic/10/25, mapping to `MapDifficulty.dbc` |
| [`04-dungeon-finder.md`](./04-dungeon-finder.md) | `LFGMgr`, queue, role check, teleport, reward distribution |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Instances/InstanceSave.{h,cpp}`, `InstanceSaveMgr.{h,cpp}` | Lockouts |
| `src/server/game/Instances/InstanceScript.{h,cpp}` | Boss state machine base |
| `src/server/game/Maps/InstanceMap.{h,cpp}`, `MapInstanced.{h,cpp}` | Per-instance map class |
| `src/server/game/DungeonFinding/LFGMgr.{h,cpp}` | Queue manager |
| `src/server/game/DungeonFinding/LFGGroupData.{h,cpp}`, `LFGPlayerData.{h,cpp}` | Per-group/player state |
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.h`, `BattlegroundMapScript.h` | Hook classes |

## Cross-references

- Engine-side: [`../maps/01-map-hierarchy.md`](../maps/01-map-hierarchy.md), [`../scripting/04-instance-scripts.md`](../scripting/04-instance-scripts.md), [`../ai/02-scripted-ai.md`](../ai/02-scripted-ai.md) (`BossAI` + `InstanceScript` interplay)
- Project-side: `mod-dungeon-challenge` is referenced from [`../../01-repos.md`](../../01-repos.md) (out of MCP scope, but related)
- External: Doxygen for `InstanceSave`, `InstanceScript`, `LFGMgr`
