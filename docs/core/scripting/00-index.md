# scripting/ — `ScriptMgr` and the hook/module system

> `ScriptMgr` is the singleton everyone calls "the hook system". It owns one registry per `ScriptObject` subclass, dispatches each hook by iterating its registry, and is the bridge between modules and the core. Module discovery happens in CMake; static vs. dynamic linkage is selectable.

## Topic files

| File | Topic |
|---|---|
| [`01-script-mgr.md`](./01-script-mgr.md) | `ScriptMgr` singleton, registries, dispatch loop, `IncreaseScriptCount`, `SetScriptLoader` / `SetModulesLoader` |
| [`02-hook-classes.md`](./02-hook-classes.md) | All `*Script` hook classes inventoried, with where the engine calls them |
| [`03-script-objects.md`](./03-script-objects.md) | Concrete `ScriptObject`s (`CreatureScript`, `GameObjectScript`, `ItemScript`, `SpellScriptLoader`, `AuraScriptLoader`, `PlayerScript`, `WorldScript`, …) |
| [`04-instance-scripts.md`](./04-instance-scripts.md) | `InstanceScript` / `InstanceMapScript` / `BattlegroundMapScript`, boss state machine wiring |
| [`05-module-discovery.md`](./05-module-discovery.md) | `modules/` glob, `ModulesLoader.cpp.in.cmake`, `Add<modulename>Scripts()` convention |
| [`06-static-vs-dynamic.md`](./06-static-vs-dynamic.md) | `-DSCRIPTS=` / `-DMODULES=` linkage modes, what changes at runtime |
| [`07-custom-hooks.md`](./07-custom-hooks.md) | The two custom hooks added by this fork — `OnPlayerCheckReagent`, `OnPlayerConsumeReagent` (used by `mod-endless-storage`) |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Scripting/ScriptMgr.{h,cpp}` | Singleton + registries |
| `src/server/game/Scripting/ScriptDefines/*Script.h` (~56 files) | Hook class declarations |
| `src/server/game/Scripting/ScriptObject.{h,cpp}` | Base `ScriptObject` |
| `src/server/game/Scripting/ScriptLoader.{h,cpp}` | In-tree script loader |
| `modules/CMakeLists.txt` | Module glob + linkage |
| `modules/ModulesLoader.cpp.in.cmake` | Generated `Add*Scripts()` stub |
| `azerothcore-wotlk/functions.md` | Custom-hook list (canonical) |

## Cross-references

- Engine-side: every other `core/` folder cross-references at least one `*Script` class
- Project-side: [`../../02-architecture.md#hook-system-scriptmgr`](../../02-architecture.md), [`../../05-modules.md`](../../05-modules.md) (per-module loader functions), [`../../03-spell-system.md`](../../03-spell-system.md) (`SpellScript`/`AuraScript` user-facing view)
- Fork-specific: `azerothcore-wotlk/functions.md` (custom hooks), `azerothcore-wotlk/CLAUDE.md`
- External: `wiki/hooks-script`, `wiki/Create-a-Module`, Doxygen for `ScriptMgr`, `ScriptObject`, all `*Script` classes
