# scripting — `ScriptObject` derivation, registration and AI factories

> A concrete script (a class deriving from `CreatureScript`, `PlayerScript`, …) registers *itself* in its constructor by calling `ScriptRegistry<T>::AddScript(this)`. This file covers the constructor pattern, the `Add*Scripts()` aggregator function used by the loader, and the `Generic*Script` / factory templates that bridge from a script to a per-instance `CreatureAI` / `GameObjectAI` / `SpellScript` / `AuraScript`. Hook catalog is in [`02-hook-classes.md`](./02-hook-classes.md); the dispatcher in [`01-script-mgr.md`](./01-script-mgr.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Scripting/ScriptObject.h:42` | base `ScriptObject` — owns `_name` and `_totalAvailableHooks`; `friend class ScriptMgr` |
| `src/server/game/Scripting/ScriptObject.h:53` | `GetName()` — returned by `ObjectMgr::GetScriptName(id)` for DB binding |
| `src/server/game/Scripting/ScriptObject.h:69` | `template<class TObject> class UpdatableScript` — adds `OnUpdate(TObject*, uint32 diff)` |
| `src/server/game/Scripting/ScriptObject.h:79` | `template<class TMap> class MapScript` — `OnCreate/OnDestroy/OnLoadGridMap/OnPlayerEnter/OnPlayerLeave/OnUpdate` |
| `src/server/game/Scripting/ScriptObject.cpp:32` | `MapScript<TMap>::checkMap()` — verifies the bound map ID exists in `sMapStore` |
| `src/server/game/Scripting/ScriptObject.cpp:41` | `template class AC_GAME_API MapScript<Map/InstanceMap/BattlegroundMap>` (explicit instantiations) |
| `src/server/game/Scripting/ScriptDefines/CreatureScript.cpp:198` | example DB-bound `CreatureScript::CreatureScript(name)` constructor — calls `ScriptRegistry<CreatureScript>::AddScript(this)` |
| `src/server/game/Scripting/ScriptDefines/CreatureScript.h:63` | `template<class AI> class GenericCreatureScript` (factory wrapper) |
| `src/server/game/Scripting/ScriptDefines/CreatureScript.h:71` | `#define RegisterCreatureAI(ai_name) new GenericCreatureScript<ai_name>(#ai_name)` |
| `src/server/game/Scripting/ScriptDefines/CreatureScript.h:73` | `template<class AI, AI*(*Factory)(Creature*)> class FactoryCreatureScript` |
| `src/server/game/Scripting/ScriptDefines/CreatureScript.h:81` | `#define RegisterCreatureAIWithFactory(ai_name, factory_fn) ...` |
| `src/server/game/Scripting/ScriptDefines/GameObjectScript.h:69` | `GenericGameObjectScript<AI>` + `#define RegisterGameObjectAI(...)` (lines 77, 86) |
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.h:37` | `template<typename IS> class GenericInstanceMapScript` + `#define RegisterInstanceScript(script_name, mapId)` (line 45) |
| `src/server/game/Scripting/ScriptDefines/SpellScriptLoader.h:25` | `SpellScriptLoader::GetSpellScript()` / `GetAuraScript()` factories |
| `src/server/game/Scripting/ScriptDefines/SpellScriptLoader.h:49` | `template<typename... Ts> GenericSpellAndAuraScriptLoader` |
| `src/server/game/Scripting/ScriptDefines/SpellScriptLoader.h:87` | `#define RegisterSpellScript(spell_script)` and `RegisterSpellAndAuraScriptPair(...)` |
| `src/server/game/Scripting/ScriptMgr.h:764` | `ScriptRegistry<T>::AddScript` — called from every `XScript` constructor |
| `src/server/game/Scripting/ScriptMgr.h:868` | `ScriptRegistry<T>::GetScriptById` — used by DB-bound dispatchers |
| `src/server/scripts/ScriptLoader.cpp.in.cmake:53` | `AddScripts()` — generated aggregator that calls every `AddSC_*()` collected by CMake |
| `src/server/game/AI/ScriptedAI/ScriptedCreature.h:484` | `class BossAI : public ScriptedAI` — typical AI returned by an instance creature script |
| `src/server/game/AI/SmartScripts/SmartAI.cpp:1494` | `void AddSC_SmartScripts()` — example aggregator (called from `ScriptMgr::Initialize`) |

## Key concepts

- **Naming = DB key** — `IsDatabaseBound()` scripts must `new MyScript("script_name_in_db")`. The string is the value of `creature_template.ScriptName` / `gameobject_template.ScriptName` / `item_template.ScriptName` / `instance_template.script` / `spell_script_names.ScriptName` / `areatrigger_scripts.ScriptName` / `criteria_data.ScriptName`. Mismatch → log warning at boot (`ScriptMgr::CheckIfScriptsInDatabaseExist`, `ScriptMgr.cpp:192`).
- **Code-only scripts** (`PlayerScript`, `WorldScript`, `UnitScript`, `MailScript`, all `All*Script`, …) take an arbitrary unique name; it's not bound to a DB column.
- **`AddSC_xxx()` convention** — each `.cpp` file under `src/server/scripts/<area>/` exposes a free function `void AddSC_xxx()` whose body `new`s every script in the file. CMake aggregates them into `AddScripts()` (the `_script_loader_callback`). Modules use the equivalent `Add<modulename>Scripts()` (see [`05-module-discovery.md`](./05-module-discovery.md)).
- **Factory pattern for AI** — `CreatureScript::GetAI(Creature*)` returns a per-creature `CreatureAI` instance. The `GenericCreatureScript<AI>` wrapper does the `new AI(creature)` for you; `FactoryCreatureScript<AI, fn>` lets you supply a custom factory function (typically used to dispatch on `instance_id`, `map_id`, or to consult an `InstanceScript` before constructing). Same shape for `GameObjectScript::GetAI` and `InstanceMapScript::GetInstanceScript`.
- **Lifetime** — `ScriptMgr::Unload()` (`ScriptMgr.cpp:109`) `delete`s every script in every registry on shutdown. Authors never call `delete` themselves.
- **Hot-reload** is not supported in stock AzerothCore; `ScriptReloadMgr` exists in fragments only.

## Flow / data shape

```
// 1. Author writes a hook class
class MyPlayerScript : public PlayerScript
{
public:
    MyPlayerScript() : PlayerScript("my_player_script") { }
    void OnPlayerLogin(Player* p) override { /* ... */ }
};

// 2. Author writes an aggregator function (one per .cpp file)
void AddSC_MyModule()
{
    new MyPlayerScript();                          // code-only registration
    RegisterCreatureAI(my_boss_ai);                // expands to GenericCreatureScript<my_boss_ai>
    RegisterInstanceScript(instance_my_dungeon, 999); // expands to GenericInstanceMapScript<instance_my_dungeon>
    RegisterSpellScript(spell_my_thing);           // expands to GenericSpellAndAuraScriptLoader<...>
}

// 3. CMake collects every AddSC_xxx() into the generated AddScripts()
//    or, for modules, into Add<modulename>Scripts()  (see 05-module-discovery.md)

// 4. At Main.cpp:275 → ScriptMgr::Initialize() invokes both callbacks,
//    each MyXScript constructor calls ScriptRegistry<XScript>::AddScript(this).

// 5. Engine dispatch site:
//    sScriptMgr->OnPlayerLogin(player);
//      → CALL_ENABLED_HOOKS(PlayerScript, PLAYERHOOK_ON_LOGIN, script->OnPlayerLogin(player));
```

For a DB-bound creature script the path is:

```
ObjectMgr::LoadCreatureTemplates()           // reads creature_template.ScriptName -> id
sScriptMgr->LoadDatabase()                   // ScriptRegistry<CreatureScript>::AddALScripts()
   → resolves each script's GetName() to id via sObjectMgr->GetScriptId()

(later, when a creature spawns)
Creature::IsAIEnabled / SelectAI            // creature->GetScriptId()
   → ScriptMgr::GetCreatureAI(creature)    (CreatureScript.cpp:156)
       → first AllCreatureScript fan-out via GetReturnAIScript<>
       → fallback to ScriptRegistry<CreatureScript>::GetScriptById(scriptId)->GetAI(creature)
```

## Hooks & extension points

- **`Register*` macros** — prefer the macros over hand-writing the `Generic*Script` wrapper; they make the `name` and the AI class identical, which is also what the DB column expects.
- **Mixed registrations in one file** — fine: one `AddSC_MyModule()` may `new` a `WorldScript`, several `CreatureScript`s, and `RegisterSpellScript(...)`s side by side.
- **Custom factory** — when an AI needs constructor args beyond `Creature*`, use `RegisterCreatureAIWithFactory(ai_name, factory_fn)` (`CreatureScript.h:81`).
- For SpellScript/AuraScript user-side details (effect handlers, `OnEffectHit`, proc filters), see [`../../03-spell-system.md`](../../03-spell-system.md) and [`../spells/00-index.md`](../spells/00-index.md).

## Cross-references

- Engine-side: [`01-script-mgr.md`](./01-script-mgr.md), [`02-hook-classes.md`](./02-hook-classes.md), [`04-instance-scripts.md`](./04-instance-scripts.md), [`05-module-discovery.md`](./05-module-discovery.md), [`../ai/02-scripted-ai.md`](../ai/02-scripted-ai.md), [`../spells/00-index.md`](../spells/00-index.md)
- Project-side: [`../../02-architecture.md`](../../02-architecture.md), [`../../03-spell-system.md`](../../03-spell-system.md), [`../../05-modules.md`](../../05-modules.md)
- Fork-specific: `azerothcore-wotlk/functions.md`
- External: `wiki/hooks-script`, `wiki/Create-a-Module`, Doxygen `classScriptObject`, `classGenericCreatureScript`, `classSpellScriptLoader`
