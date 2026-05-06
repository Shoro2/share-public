# movement/ — Movement engine

> `MotionMaster` schedules `MovementGenerator` slots; `MoveSpline` is the server-side mirror of the client's interpolation; `PathGenerator` queries Detour for a path; `CreatureGroup` ties formations together.

## Topic files

| File | Topic |
|---|---|
| [`01-motion-master.md`](./01-motion-master.md) | `MotionMaster` slot stack (`MOTION_SLOT_*`), idle/active/controlled |
| [`02-generators.md`](./02-generators.md) | `IdleMovementGenerator`, `RandomMovementGenerator`, `WaypointMovementGenerator`, `FollowMovementGenerator`, `ChaseMovementGenerator`, `FleeingMovementGenerator`, `PointMovementGenerator`, … |
| [`03-spline.md`](./03-spline.md) | `MoveSpline`, `MoveSplineInit`, `MoveSplineFlag`, packets (`SMSG_MONSTER_MOVE`) |
| [`04-pathfinder.md`](./04-pathfinder.md) | `PathGenerator` → Detour, raycasts, fallbacks |
| [`05-formation.md`](./05-formation.md) | `CreatureGroup`, `creature_formations`, leader following |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Movement/MotionMaster.{h,cpp}` | Slot stack |
| `src/server/game/Movement/MovementGenerator.{h,cpp}` | Generator interface |
| `src/server/game/Movement/MovementGenerators/*Generator.{h,cpp}` | Concrete generators |
| `src/server/game/Movement/Spline/MoveSpline*.{h,cpp}` | Spline math + init |
| `src/server/game/Movement/PathGenerator.{h,cpp}` | Detour wrapper |
| `src/server/game/Movement/CreatureGroups.{h,cpp}` | Formation / leader binding |

## Cross-references

- Engine-side: [`../entities/05-creature.md`](../entities/05-creature.md) (uses `MotionMaster`), [`../maps/06-mmaps.md`](../maps/06-mmaps.md) (Detour navmesh), [`../ai/02-scripted-ai.md`](../ai/02-scripted-ai.md) (AI pushes movement)
- Fork-specific: none beyond upstream
- External: Doxygen for `MotionMaster`, `MovementGenerator`, `MoveSpline`, `PathGenerator`
