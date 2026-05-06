# scripting — `InstanceScript`, `BossInfo`, encounter wiring

> An `InstanceMapScript` is the registry-level entry that owns one `InstanceScript` *per instance map* (per group/copy). The `InstanceScript` tracks per-encounter state (`BossInfo`/`EncounterState`), boss-controlled doors/minions, persistent save/load and provides helper APIs for boss AIs (`BossAI`). DB binding is via `instance_template.script` → `ObjectMgr::GetScriptId`. See [`03-script-objects.md`](./03-script-objects.md) for the registration mechanics and [`../ai/02-scripted-ai.md`](../ai/02-scripted-ai.md) for `BossAI`.

## Critical files

| File | Role |
|---|---|
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.h:23` | declaration of `class InstanceMapScript : public ScriptObject, public MapScript<InstanceMap>` |
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.h:34` | virtual `GetInstanceScript(InstanceMap*)` factory |
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.h:37` | `template<typename IS> class GenericInstanceMapScript` (factory wrapper) |
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.h:45` | `#define RegisterInstanceScript(script_name, mapId)` |
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.cpp:21` | `ScriptMgr::CreateInstanceScript(InstanceMap*)` — `GetScriptById(map->GetScriptId()) → GetInstanceScript(map)` |
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.cpp:29` | `InstanceMapScript::InstanceMapScript(name, mapId)` — registers in `ScriptRegistry<InstanceMapScript>` |
| `src/server/game/Scripting/ScriptDefines/InstanceMapScript.cpp:35` | `checkValidity()` — error if mapId is not a dungeon |
| `src/server/game/Instances/InstanceScript.h:142` | declaration of `class InstanceScript : public ZoneScript` |
| `src/server/game/Instances/InstanceScript.h:56` | `enum EncounterState : uint8` — `NOT_STARTED / IN_PROGRESS / FAIL / DONE / SPECIAL / TO_BE_DECIDED` |
| `src/server/game/Instances/InstanceScript.h:111` | `struct BossInfo` — state + per-type DoorSet + MinionSet + CreatureBoundary |
| `src/server/game/Instances/InstanceScript.h:66` | `enum DoorType` — ROOM / PASSAGE / SPAWN_HOLE |
| `src/server/game/Instances/InstanceScript.h:74` | `struct DoorData { entry, bossId, type }` |
| `src/server/game/Instances/InstanceScript.h:100` | `struct MinionData { entry, bossId }` |
| `src/server/game/Instances/InstanceScript.h:80` | `struct BossBoundaryEntry / BossBoundaryData` (initializer-list builder for `LoadBossBoundaries`) |
| `src/server/game/Instances/InstanceScript.h:251` | `virtual bool SetBossState(uint32 id, EncounterState state)` |
| `src/server/game/Instances/InstanceScript.h:252` | `GetBossState`, `GetBossInfo`, `GetBossBoundary`, `GetEncounterCount`, `GetCompletedEncounterMask` |
| `src/server/game/Instances/InstanceScript.h:267` | `SetCompletedEncountersMask(uint32 newMask, bool save)` |
| `src/server/game/Instances/InstanceScript.h:295` | `IsBossDone(id)`, `AllBossesDone()`, `AllBossesDone({...})` |
| `src/server/game/Instances/InstanceScript.h:304-341` | save/load helpers: `SetHeaders`, `SetBossNumber`, `LoadBossBoundaries`, `LoadDoorData`, `LoadMinionData`, `LoadObjectData`, `LoadSummonData`, `ReadSaveDataHeaders/BossStates`, `WriteSaveDataHeaders/BossStates` |
| `src/server/game/Instances/InstanceScript.h:282` | `MarkAreaTriggerDone`, `IsAreaTriggerDone` (for `OnlyOnceAreaTriggerScript`) |
| `src/server/game/Maps/Map.cpp:2079` | `InstanceMap::CreateInstanceScript(load, data, completedEncounterMask)` — call site of `sScriptMgr->CreateInstanceScript(this)` |
| `src/server/game/Maps/Map.cpp:2088` | precedes with `sScriptMgr->OnBeforeCreateInstanceScript(...)` (see `AllMapScript`) |
| `src/server/game/Maps/Map.h:660` | `Map::GetInstanceScript()` accessor |
| `src/server/game/Globals/ObjectMgr.cpp:6470` | `ObjectMgr::LoadInstanceTemplate()` — reads `instance_template (map, parent, script, allowMount)` |
| `src/server/game/Globals/ObjectMgr.cpp:6501` | `instanceTemplate.ScriptId = GetScriptId(fields[2].Get<std::string>())` (binds DB string → registry id) |
| `src/server/game/AI/ScriptedAI/ScriptedCreature.h:484` | `class BossAI : public ScriptedAI` — typical AI returned by an instance creature script (see `Reset()/_Reset()`, `JustEngagedWith()/_JustEngagedWith()`, `JustDied()/_JustDied()` at lines 524-527) |

## Key concepts

- **Two layers** — `InstanceMapScript` (the registry-level *factory*, registered once at boot) and `InstanceScript` (the per-instance *state object*, instantiated each time a group enters). The `RegisterInstanceScript(script_name, mapId)` macro creates a `GenericInstanceMapScript<script_name>` whose `GetInstanceScript()` returns `new script_name(map)`.
- **`BossInfo`** — one entry per encounter, indexed by the `bossId` you pass to `SetBossNumber(N)` in your `InstanceScript` constructor. Each `BossInfo` carries `state` (`EncounterState`), one `DoorSet` per `DoorType`, a `MinionSet`, and a `CreatureBoundary` (gameplay area).
- **`SetBossState(id, state)`** — central state transition; should be `override`-d by your script if you need side effects (open doors, save to DB, fire achievements, send `Encounter*` packets).
- **Persistence** — stored in `acore_characters.instance` `data` column. `Load(char const*)` and `GetSaveData()` are virtual; helpers `WriteSaveDataHeaders/BossStates` and `ReadSaveDataHeaders/BossStates` handle the standard format. `WriteSaveDataMore`/`ReadSaveDataMore` are extension points for per-instance custom state.
- **`completedEncounters`** — bitmask packed into the `Encounter*` opcodes; bit positions correspond to `DungeonEncounter.dbc` boss numbers, *not* internal `bossId`. Set via `SetCompletedEncountersMask(mask, save)`.
- **Doors** — `LoadDoorData(DoorData[])` registers entries; the engine then auto-flips state on `SetBossState` (open on DONE for `DOOR_TYPE_PASSAGE`; close on `IN_PROGRESS` for `DOOR_TYPE_ROOM`; open on `IN_PROGRESS` for `DOOR_TYPE_SPAWN_HOLE`).
- **Minions** — `LoadMinionData(MinionData[])` ties trash entries to a boss; their state can be batch-updated via `UpdateMinionState`.
- **Objects** — `LoadObjectData(creatureData[], gameObjectData[])` registers GUIDs by *type constant* so script code can query `GetCreature(type)` / `GetGameObject(type)` without hunting GUIDs.

## Flow / data shape

```
Author writes:
  class instance_my_dungeon : public InstanceScript {
      void Initialize() override { SetBossNumber(N); LoadBossBoundaries(...); LoadDoorData(...); ... }
      bool SetBossState(uint32 id, EncounterState state) override {
          if (!InstanceScript::SetBossState(id, state)) return false;
          /* react: open doors via HandleGameObject, fire DoSendNotifyToInstance, ... */
          return true;
      }
  };
  void AddSC_instance_my_dungeon() {
      RegisterInstanceScript(instance_my_dungeon, 999);   // 999 = mapId
  }

Boot path:
  ScriptMgr::Initialize() → AddScripts() / AddModulesScripts()
    → InstanceMapScript ctor (DB-bound) goes into ScriptRegistry<InstanceMapScript>::ALScripts
  ObjectMgr::LoadInstanceTemplate()    // reads instance_template.script -> ScriptId
  ScriptMgr::LoadDatabase()
    → ScriptRegistry<InstanceMapScript>::AddALScripts()
        → resolves GetName() → ObjectMgr::GetScriptId("instance_my_dungeon")
        → places script under that id in ScriptPointerList

Per group entering:
  InstanceMap::CreateInstanceScript(load, data, completedMask)   // Map.cpp:2079
    ├─ sScriptMgr->OnBeforeCreateInstanceScript(...)             // AllMapScript fan-out
    ├─ i_script_id = GetInstanceTemplate()->ScriptId
    ├─ instance_data = sScriptMgr->CreateInstanceScript(this)    // → GetScriptById(i_script_id)->GetInstanceScript(this)
    ├─ instance_data->Initialize()                               // (only if !load)
    ├─ instance_data->SetCompletedEncountersMask(completedMask, false)
    ├─ instance_data->Load(data)                                 // restore boss states
    └─ instance_data->LoadInstanceSavedGameobjectStateData()
```

`BossAI` (`ScriptedCreature.h:484`) shorthand — call `_Reset()`, `_JustEngagedWith()`, `_JustDied()` from your boss's `Reset()` / `JustEngagedWith()` / `JustDied()` to update the bound `InstanceScript` automatically (default implementations at lines 524-527 just forward).

## Hooks & extension points

- **`SetBossState` override** — primary place to chain to `DoUpdateAchievementCriteria`, broadcast packets, despawn trash, or open the next room.
- **`OnPlayerEnter` / `OnPlayerLeave`** (`InstanceScript.h:186/189`) — instance-specific player tracking (debuffs, scaling).
- **`CheckRequiredBosses` / `CheckAchievementCriteriaMeet`** (lines 262-265) — block entry / extra credit logic.
- **`AllMapScript::OnBeforeCreateInstanceScript`** (`AllMapScript.h:67`) — last-chance hook to substitute the `InstanceScript` (used by `mod-ale` to inject a Lua-driven script). Engine call site: `Map.cpp:2088`.
- **Persistent custom data** — override `WriteSaveDataMore` / `ReadSaveDataMore`; for indexed counters use `StorePersistentData(idx, value)` + `GetPersistentData(idx)` (`InstanceScript.h:257-258`) and `SetPersistentDataCount(N)` in `Initialize`.

## Cross-references

- Engine-side: [`01-script-mgr.md`](./01-script-mgr.md), [`02-hook-classes.md`](./02-hook-classes.md), [`03-script-objects.md`](./03-script-objects.md), [`../instances/00-index.md`](../instances/00-index.md), [`../ai/02-scripted-ai.md`](../ai/02-scripted-ai.md), [`../maps/00-index.md`](../maps/00-index.md)
- Project-side: [`../../02-architecture.md`](../../02-architecture.md)
- Fork-specific: `azerothcore-wotlk/functions.md`
- External: `wiki/hooks-script`, Doxygen `classInstanceMapScript`, `classInstanceScript`, `classBossAI`
