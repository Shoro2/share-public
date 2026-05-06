# battlegrounds/ — Battlegrounds, arenas, battlefields

> `BattlegroundMgr` allocates `Battleground` objects (each with its own `BattlegroundMap`) and runs the queue. Arenas are battlegrounds with rated MMR and `ArenaTeam` book-keeping. Battlefields (Wintergrasp, Tol Barad) are open-world large-scale PvP.

## Topic files

| File | Topic |
|---|---|
| [`01-bg-mgr.md`](./01-bg-mgr.md) | `BattlegroundMgr`, queue (`BattlegroundQueue`), `BattlegroundQueueTypeId`, MMR matching |
| [`02-bg-types.md`](./02-bg-types.md) | WSG, AB, AV, EOTS, SOTA, IOC — per-zone classes |
| [`03-arena.md`](./03-arena.md) | `ArenaTeam`, seasons, rated queue, MMR formula |
| [`04-battlefield.md`](./04-battlefield.md) | Wintergrasp, Tol Barad, `BattlefieldMgr` |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Battlegrounds/Battleground.{h,cpp}` | Base BG class |
| `src/server/game/Battlegrounds/BattlegroundMgr.{h,cpp}` | Allocator + queue front-end |
| `src/server/game/Battlegrounds/BattlegroundQueue.{h,cpp}` | Queueing + matchmaking |
| `src/server/game/Battlegrounds/Zones/Battleground*.{h,cpp}` | Per-zone implementations |
| `src/server/game/Battlegrounds/ArenaTeam.{h,cpp}`, `ArenaTeamMgr.{h,cpp}` | Arena teams + seasons |
| `src/server/game/Maps/BattlegroundMap.{h,cpp}` | BG-specific map |
| `src/server/game/Battlefield/Battlefield.{h,cpp}`, `BattlefieldMgr.{h,cpp}`, `Zones/*` | Battlefields |

## Cross-references

- Engine-side: [`../maps/01-map-hierarchy.md`](../maps/01-map-hierarchy.md), [`../instances/01-instance-save.md`](../instances/01-instance-save.md) (BG seasons share lockout logic), [`../scripting/04-instance-scripts.md`](../scripting/04-instance-scripts.md)
- Project-side: nothing custom in this fork
- External: Doxygen for `Battleground`, `BattlegroundMgr`, `ArenaTeam`, `Battlefield`
