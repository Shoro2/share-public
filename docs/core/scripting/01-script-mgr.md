# scripting — `ScriptMgr` singleton, registries and dispatch

> Single entry point through which the engine calls every C++ script. Owns one templated registry per `ScriptObject` subclass, dispatches each hook by iterating that registry, and is wired to two loader callbacks (in-tree scripts + modules) at startup. See [`02-hook-classes.md`](./02-hook-classes.md) for the hook catalog and [`03-script-objects.md`](./03-script-objects.md) for how a `ScriptObject` registers itself.

## Critical files

| File | Role |
|---|---|
| `src/server/game/Scripting/ScriptMgr.h:110` | declaration of `class ScriptMgr` (~640 hook methods, grouped by `public:` blocks per script type) |
| `src/server/game/Scripting/ScriptMgr.h:135` | `SetScriptLoader` / `SetModulesLoader` — two function-pointer callbacks (workaround for `game ↔ scripts` circular dep) |
| `src/server/game/Scripting/ScriptMgr.h:127` | `IncreaseScriptCount` / `DecreaseScriptCount` / `GetScriptCount` (atomic counter shown at startup) |
| `src/server/game/Scripting/ScriptMgr.h:725` | private members: `_scriptCount`, `_scheduledScripts` (`std::atomic<long>`), `_script_loader_callback`, `_modules_loader_callback` |
| `src/server/game/Scripting/ScriptMgr.h:735` | `#define sScriptMgr ScriptMgr::instance()` (the global accessor) |
| `src/server/game/Scripting/ScriptMgr.h:737` | `template<class TScript> class ScriptRegistry` — one specialization per hook class |
| `src/server/game/Scripting/ScriptMgr.h:752` | `static ScriptMap ScriptPointerList` — `std::map<uint32, TScript*>` (the actual registry) |
| `src/server/game/Scripting/ScriptMgr.h:754` | `static ScriptVector ALScripts` — *after-load* deferred scripts (DB-bound types) |
| `src/server/game/Scripting/ScriptMgr.h:757` | `static EnabledHooksVector EnabledHooks` — per-hook enabled lists for the `CALL_ENABLED_HOOKS` fast path |
| `src/server/game/Scripting/ScriptMgr.h:764` | `AddScript(TScript*, std::vector<uint16> enabledHooks)` — called from each `ScriptObject` constructor |
| `src/server/game/Scripting/ScriptMgr.h:791` | `AddALScripts()` — second pass after `LoadDatabase` resolves DB script names to IDs |
| `src/server/game/Scripting/ScriptMgr.h:868` | `GetScriptById(uint32)` — used by every dispatch that targets a specific (DB-bound) script |
| `src/server/game/Scripting/ScriptMgr.cpp:55` | `ScriptMgr::instance()` (Meyers singleton) |
| `src/server/game/Scripting/ScriptMgr.cpp:61` | `Initialize()` — calls both loader callbacks then `InitEnabledHooksIfNeeded` per registry |
| `src/server/game/Scripting/ScriptMgr.cpp:109` | `Unload()` — `delete` all script pointers via `SCR_CLEAR<T>()` |
| `src/server/game/Scripting/ScriptMgr.cpp:162` | `LoadDatabase()` — calls `ScriptRegistry<T>::AddALScripts()` for every DB-bound type |
| `src/server/game/Scripting/ScriptMgr.cpp:192` | `CheckIfScriptsInDatabaseExist()` — warns about DB script names with no C++ implementation |
| `src/server/game/Scripting/ScriptMgrMacros.h:72` | `CALL_ENABLED_HOOKS` macro — short-circuits if the per-hook registry is empty |
| `src/server/game/Scripting/ScriptMgrMacros.h:76` | `CALL_ENABLED_BOOLEAN_HOOKS` (default `true` short-circuit), `..._WITH_DEFAULT_FALSE` variant |
| `src/server/game/Scripting/ScriptMgrMacros.h:23` | `IsValidBoolScript<>`, `GetReturnAIScript<>`, `ExecuteScript<>` — reusable foreach templates |
| `src/server/apps/worldserver/Main.cpp:265` | callback wiring: `SetScriptLoader(AddScripts)` + `SetModulesLoader(AddModulesScripts)` |
| `src/server/apps/worldserver/Main.cpp:275` | `sScriptMgr->Initialize()` (right after callback wiring) |
| `src/server/game/World/World.cpp:860` | `sScriptMgr->LoadDatabase()` — second pass after world DB is ready |

## Key concepts

- **Singleton** — `sScriptMgr` macro yields the lone instance; never construct one yourself.
- **`ScriptObject`** — abstract base; every hook class derives from it (see [`02-glossary.md`](../02-glossary.md) and [`03-script-objects.md`](./03-script-objects.md)).
- **`ScriptRegistry<T>`** — a *separate* static map per script type `T`. Lookup is `ScriptRegistry<PlayerScript>::ScriptPointerList` etc.
- **Two-stage registration**:
  1. *Constructor pass* — code-only (`IsDatabaseBound() == false`) scripts are immediately added to `ScriptPointerList` with a synthetic id.
  2. *After-load pass* (`AddALScripts()`) — DB-bound scripts (`CreatureScript`, `ItemScript`, `SpellScriptLoader`, …) wait until `ObjectMgr::GetScriptId(name)` can resolve their name against `instance_template.script` / `creature_template.ScriptName` / `item_template.ScriptName` / `spell_script_names` / etc.
- **Per-hook fast path** — `EnabledHooks[hookEnum]` lists only the scripts that actually override that virtual; an empty list → zero work in the dispatcher.
- **Two loader callbacks** — `_script_loader_callback` (in-tree `AddScripts()`, generated from `src/server/scripts/ScriptLoader.cpp.in.cmake`) and `_modules_loader_callback` (`AddModulesScripts()` from `modules/ModulesLoader.cpp.in.cmake`). See [`05-module-discovery.md`](./05-module-discovery.md).
- **Script count** — every successful `AddScript` calls `IncreaseScriptCount()`; the boot log line `>> Loaded N C++ scripts in X ms` reads `GetScriptCount()`.

## Flow / data shape

```
worldserver Main.cpp
  ├─ sScriptMgr->SetScriptLoader(&AddScripts)       // in-tree
  ├─ sScriptMgr->SetModulesLoader(&AddModulesScripts)
  └─ sScriptMgr->Initialize()
        ├─ AddSC_SmartScripts(); lfg::AddSC_LFGScripts();
        ├─ ASSERT(_script_loader_callback)          // both callbacks must be set
        ├─ _script_loader_callback();   // → AddScripts() in generated ScriptLoader.cpp
        │     └─ AddSC_hunter_spell_scripts(); ... (one void per src/server/scripts/* subdir)
        │           └─ each constructor of XScript("name") → ScriptRegistry<X>::AddScript(this)
        ├─ _modules_loader_callback();  // → AddModulesScripts() in generated ModulesLoader.cpp
        │     └─ Addmod_paragonScripts(); Addmod_loot_filterScripts(); ...
        └─ ScriptRegistry<T>::InitEnabledHooksIfNeeded(<T>HOOK_END)  // for every T

(later, once World DB is up)
World::SetInitialWorldSettings()
  └─ sScriptMgr->LoadDatabase()
        ├─ ScriptRegistry<WorldMapScript>::AddALScripts();
        ├─ ScriptRegistry<InstanceMapScript>::AddALScripts();
        ├─ ScriptRegistry<CreatureScript>::AddALScripts();   // resolves names → IDs
        ├─ ... (every IsDatabaseBound() == true type)
        └─ CheckIfScriptsInDatabaseExist()                   // log unmatched DB names
```

The dispatch primitive (any of the ~640 `ScriptMgr::On*` methods) follows one of three shapes (`src/server/game/Scripting/ScriptMgrMacros.h:72-86`):

```cpp
// void hook with N enabled scripts
void ScriptMgr::OnPlayerLevelChanged(Player* p, uint8 oldLevel)
{
    CALL_ENABLED_HOOKS(PlayerScript, PLAYERHOOK_ON_LEVEL_CHANGED,
        script->OnPlayerLevelChanged(p, oldLevel));
}
// → if EnabledHooks[h].empty() return; else for(s : ...) action
```

For **DB-bound, single-script** dispatch the pattern is direct: `ScriptRegistry<T>::GetScriptById(creature->GetScriptId())->OnX(...)` (e.g. `CreatureScript::OnGossipHello` at `src/server/game/Scripting/ScriptDefines/CreatureScript.cpp:24`).

## Hooks & extension points

- **Add a new hook**: declare it on the appropriate `*Script` class in `ScriptDefines/`, add a matching enum to `*Hook`, declare a dispatch method in `ScriptMgr.h` and define it in the corresponding `*.cpp` using one of the `CALL_ENABLED_*` macros, then call `sScriptMgr->OnX(...)` from the engine site. Wiki: `wiki/hooks-script`.
- **Add a new `*Script` family**: derive a class from `ScriptObject`, add a `ScriptRegistry<T>::InitEnabledHooksIfNeeded(...)` call to `Initialize()` (`ScriptMgr.cpp:80`) and a `SCR_CLEAR<T>()` to `Unload()` (`ScriptMgr.cpp:111`).
- Modules typically only **override** existing hooks; see [`02-hook-classes.md`](./02-hook-classes.md) for the catalog and [`05-module-discovery.md`](./05-module-discovery.md) for the loader plumbing.

## Cross-references

- Engine-side: [`02-hook-classes.md`](./02-hook-classes.md), [`03-script-objects.md`](./03-script-objects.md), [`05-module-discovery.md`](./05-module-discovery.md), [`06-static-vs-dynamic.md`](./06-static-vs-dynamic.md), [`../architecture/00-index.md`](../architecture/00-index.md) (startup ordering)
- Project-side: [`../../02-architecture.md#hook-system-scriptmgr`](../../02-architecture.md), [`../../05-modules.md`](../../05-modules.md)
- Fork-specific: `azerothcore-wotlk/functions.md`, `azerothcore-wotlk/CLAUDE.md`
- External: `wiki/hooks-script`, `wiki/Create-a-Module`, Doxygen `classScriptMgr`, `classScriptObject`, `classScriptRegistry`
