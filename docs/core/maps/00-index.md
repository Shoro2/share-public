# maps/ — Maps, grids, cells, MMaps, VMaps

> A `Map` is the world container. It owns a 64×64 grid of cells per axis; entities live in cells, cells live in grids, grids load on demand, and `MapMgr` allocates `Map` instances for continents / dungeons / battlegrounds.

## Topic files

| File | Topic |
|---|---|
| [`01-map-hierarchy.md`](./01-map-hierarchy.md) | `Map` / `InstanceMap` / `BattlegroundMap` / `MapInstanced`, who owns what |
| [`02-map-mgr.md`](./02-map-mgr.md) | `MapMgr` allocation, instance lifecycle, `MapUpdater` thread pool |
| [`03-grids-cells.md`](./03-grids-cells.md) | `GridDefines.h`, cell math, `MAX_NUMBER_OF_GRIDS=64`, `SIZE_OF_GRIDS` |
| [`04-grid-loading.md`](./04-grid-loading.md) | `ObjectGridLoader`, `EnsureGridLoaded`, lazy load triggers, despawn |
| [`05-visibility.md`](./05-visibility.md) | Visibility distance, `NotifyVisibilityChanged*`, broadcast helpers |
| [`06-mmaps.md`](./06-mmaps.md) | Detour navmeshes, `MMapMgr`, runtime tile loading |
| [`07-vmaps.md`](./07-vmaps.md) | Vector collision, line-of-sight, height queries |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Maps/Map.{h,cpp}` | Base map class |
| `src/server/game/Maps/MapMgr.{h,cpp}` | Map allocation |
| `src/server/game/Maps/MapUpdater.{h,cpp}` | Parallel map updates |
| `src/server/game/Maps/MapInstanced.{h,cpp}` | Continent maps with instance children |
| `src/server/game/Maps/InstanceMap.{h,cpp}` | Dungeon/raid map |
| `src/server/game/Maps/BattlegroundMap.{h,cpp}` | BG-specific map |
| `src/server/game/Grids/Grid.h`, `GridLoader.h`, `GridReference.h`, `GridDefines.h` | Grid plumbing |
| `src/server/game/Grids/Cells/Cell.{h,cpp}`, `CellImpl.h` | Cell helpers |
| `src/server/game/Grids/ObjectGridLoader.{h,cpp}` | Object spawn on grid load |
| `src/server/game/Grids/Notifiers/GridNotifiers*.{h,cpp}` | Visibility/range queries |
| `src/server/game/Maps/MMaps/*` | MMaps integration |
| `src/server/game/Maps/VMaps/*` | VMaps integration |

## Cross-references

- Engine-side: [`../entities/05-creature.md`](../entities/05-creature.md) (creatures spawn on grid load), [`../movement/04-pathfinder.md`](../movement/04-pathfinder.md), [`../instances/02-instance-script.md`](../instances/02-instance-script.md)
- Project-side: [`../../02-architecture.md`](../../02-architecture.md) (top-level subsystem map)
- External: `wiki/common-errors` (MMaps/VMaps missing), Doxygen for `Map`, `MapMgr`, `Grid`, `Cell`
