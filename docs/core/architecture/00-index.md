# architecture/ — process model, lifecycle, threading, build

> How the binaries are wired up — from `main()` through the world tick to the build system that produces them. Stays high-level; per-subsystem detail lives elsewhere.

## Topic files

| File | Topic |
|---|---|
| [`01-process-model.md`](./01-process-model.md) | `authserver` ↔ `worldserver` split, ports, IPC, what each owns |
| [`02-startup-shutdown.md`](./02-startup-shutdown.md) | `main()` → `World::SetInitialWorldSettings()`, signal handling, exit cleanup |
| [`03-update-loop.md`](./03-update-loop.md) | `World::Update(diff)`, tick budget, timer slots |
| [`04-threading.md`](./04-threading.md) | I/O context, `MapUpdater`, `DatabaseWorker`, `ProducerConsumerQueue`, locking patterns |
| [`05-build-system.md`](./05-build-system.md) | CMake structure, important flags (`SCRIPTS`, `MODULES`, `BUILD_TESTING`, `USE_COREPCH`), PCH, `-Werror` |

## Critical files

| File | Role |
|---|---|
| `src/server/apps/authserver/Main.cpp` | authserver entry point |
| `src/server/apps/worldserver/Main.cpp` | worldserver entry point |
| `src/server/game/World/World.h`, `World.cpp` | world singleton + tick |
| `src/common/Threading/*` | MPSC queues, thread pool primitives |
| `src/server/game/Maps/MapUpdater.{h,cpp}` | parallel map updates |
| `CMakeLists.txt` (root), `src/cmake/macros/*.cmake` | build system |
| `conf/dist/config.cmake`, `conf/config.cmake` | build-time config defaults |

## Cross-references

- Engine-side: [`../world/01-world-singleton.md`](../world/01-world-singleton.md), [`../database/06-connection-pool.md`](../database/06-connection-pool.md), [`../network/04-worldsocket.md`](../network/04-worldsocket.md)
- Project-side: [`../../02-architecture.md`](../../02-architecture.md) (high-level project view), [`../../07-codestyle.md`](../../07-codestyle.md) (CI / `-Werror`)
- Fork-specific: `azerothcore-wotlk/data_structure.md`, `azerothcore-wotlk/functions.md` (build commands, DB setup)
- External: `wiki/installation`, `wiki/install-with-docker`, `wiki/common-errors`, `wiki/project-versioning`
