# entities — Creature

> Run-time `Creature` (instance), shared `CreatureTemplate` (the row in `creature_template`), and the per-spawn `CreatureData` (the row in `creature`). Plus the spawn / respawn / linked-respawn pipeline. Cross-links: [`10-object-mgr.md`](./10-object-mgr.md), [`../ai/00-index.md`](../ai/00-index.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Creature/Creature.h:46` | `class Creature : public Unit, public GridObject<Creature>, public MovableMapObject, public UpdatableMapObject` |
| `src/server/game/Entities/Creature/CreatureData.h:186` | `struct CreatureTemplate` (mirrors `creature_template`) |
| `src/server/game/Entities/Creature/CreatureData.h:297` | `struct CreatureBaseStats` (`creature_classlevelstats`) |
| `src/server/game/Entities/Creature/CreatureData.h:369` | `struct CreatureData : public SpawnData` (mirrors `creature`) |
| `src/server/game/Entities/Creature/CreatureData.h:388` | `struct CreatureModelInfo` (`creature_model_info`) |
| `src/server/game/Entities/Creature/CreatureData.h:430` | `struct CreatureAddon` (`creature_addon`, `creature_template_addon`) |
| `src/server/game/Entities/Creature/CreatureData.h:444` | `struct VendorItem` |
| `src/server/game/Entities/Creature/TemporarySummon.h:49` | `class TempSummon : public Creature` |
| `src/server/game/Entities/Creature/TemporarySummon.h:86` | `class Minion / Guardian / Puppet` |
| `src/server/game/Entities/Creature/CreatureGroups.h:24` | `class CreatureGroup` (formations) |
| `src/server/game/Entities/Creature/Creature.cpp:1128` | `Creature::Create(ObjectGuid::LowType, Map*, phase, entry, vehId, x, y, z, ang, CreatureData*)` |
| `src/server/game/Entities/Creature/Creature.cpp:560` | `Creature::UpdateEntry(...)` (used by morph/transform) |
| `src/server/game/Entities/Creature/Creature.cpp:685` | `Creature::Update(uint32 diff)` (per-tick) |
| `src/server/game/Entities/Creature/Creature.cpp:1077` | `Creature::AIM_Initialize(CreatureAI*)` |
| `src/server/game/Entities/Creature/Creature.cpp:1357` | `Creature::SaveToDB()` |
| `src/server/game/Entities/Creature/Creature.cpp:1656` | `Creature::LoadCreatureFromDB(spawnId, Map*, addToMap, allowDuplicate)` |
| `src/server/game/Entities/Creature/Creature.cpp:1989` | `Creature::Respawn(bool force)` |
| `src/server/game/Entities/Creature/Creature.cpp:2128` | `Creature::DespawnOrUnsummon(msTimeToDespawn, forcedRespawnTimer)` |
| `src/server/game/Entities/Creature/Creature.cpp:2401` | `Creature::CallAssistance(Unit* target)` |
| `src/server/game/Globals/ObjectMgr.cpp:522` | `ObjectMgr::LoadCreatureTemplates()` |
| `src/server/game/Globals/ObjectMgr.cpp:584` | `ObjectMgr::LoadCreatureTemplate(Field*, bool triggerHook)` (single row) |
| `src/server/game/Globals/ObjectMgr.cpp:855` | `ObjectMgr::LoadCreatureTemplateAddons()` |
| `src/server/game/Globals/ObjectMgr.cpp:951` | `ObjectMgr::LoadCreatureCustomIDs()` (custom-id remap) |
| `src/server/game/Globals/ObjectMgr.cpp:2316` | `ObjectMgr::LoadCreatures()` (`creature` table → `_creatureDataStore`) |
| `src/server/game/Globals/ObjectMgr.cpp:1917` | `ObjectMgr::LoadLinkedRespawn()` (`linked_respawn`) |

## Key concepts

- **Three-layer data**:
  1. `CreatureTemplate` (one per `entry`, immutable runtime, ~80 fields including `Models`, `faction`, `npcflag`, `unit_class`, `unit_flags`, `family`, `type`, `lootid`, `spells[8]`, `AIName`, `MovementType`, `flags_extra`, `ScriptID`).
  2. `CreatureData` (one per spawn row, mutable per-spawn overrides: `displayid`, `equipmentId`, `spawntimesecs`, `wander_distance`, `currentwaypoint`, `npcflag`, `unit_flags`, `dynamicflags`).
  3. `Creature` instance (the in-world `Unit`, holds `CreatureTemplate const* m_creatureInfo` at `Creature.h:510` and `CreatureData const* m_creatureData` at `:511`).
- **`m_originalEntry` vs `entry`** (`Creature.h:497`) — set by `UpdateEntry` so polymorph / transform can revert. `GetEntry()` returns the current visible entry; `m_originalEntry` is the spawn-row entry.
- **`m_spawnId` vs `GetGUID()`** (`Creature.h:485`) — `m_spawnId` = stable id from the `creature.guid` column (zero for `TempSummon`s and not-yet-saved spawns); `GetGUID()` = full `ObjectGuid` (recreated each respawn). DB cross-references use `m_spawnId`.
- **Random spawn entries**: `creature` rows can have `id1`/`id2`/`id3` (`CreatureData.h:372-374`); the loader picks one per spawn at `LoadCreatureFromDB` time.
- **`CreatureBaseStats`** (`CreatureData.h:297`) — per-`level`/`unit_class` row in `creature_classlevelstats` providing base health/mana/AP/AD multipliers; `Creature::SelectLevel` (`Creature.h:66`) consumes them.
- **AI binding**: `AIM_Initialize` (`Creature.cpp:1077`) constructs the AI named in `AIName` (or via `ScriptID` for scripted bosses); falls back to default `CreatureAI`. See [`../ai/02-scripted-ai.md`](../ai/02-scripted-ai.md).
- **`flags_extra`** — per-`creature_template` extras (`CREATURE_FLAG_EXTRA_TRIGGER`, `_CIVILIAN`, `_GUARD`, `_AVOID_AOE`, …). Test via `Creature::HasFlagsExtra(uint32)` (`Creature.h:77`).
- **Formations** — `CreatureGroup* m_formation` (`Creature.h:533`); membership defined in `creature_formations` table, loaded by `CreatureGroup`-scoped code (see `CreatureGroups.cpp`). `IsFormationLeader / IsFormationLeaderMoveAllowed` at `Creature.h:365-367`.
- **Linked respawn**: `linked_respawn` (loaded `ObjectMgr.cpp:1917`) maps `(spawn guid) -> linked-spawn guid`. When a leader dies/respawns, linked spawns follow. Container: `LinkedRespawnContainer = std::map<ObjectGuid, ObjectGuid>` (`ObjectMgr.h:506`).

## Flow / data shape

### Spawn from grid load (the normal path)

```
Map::LoadGrid(...)               // see ../maps/04-grid-loading.md
  └─ for each CellObjectGuids creature in this cell:
       └─ Creature::LoadCreatureFromDB(spawnId, this)         // Creature.cpp:1656
            ├─ data = sObjectMgr->GetCreatureData(spawnId)    // ObjectMgr.h:1232
            ├─ entry = chosen from {id1,id2,id3}              // CreatureData.h:372-374
            ├─ Creature::Create(newGuid, map, phase, entry, vehId, x,y,z,o, data)
            │     ├─ CreateFromProto -> InitEntry
            │     ├─ SetUInt32Value(OBJECT_FIELD_GUID, …)
            │     ├─ SelectLevel
            │     ├─ LoadCreaturesAddon (movement, mount, auras)
            │     └─ LoadEquipment(data->equipmentId)
            ├─ AIM_Initialize(nullptr)                         // chooses AI by AIName/ScriptID
            └─ map->AddToMap(this)                             // adds to grid + visibility
```

### Programmatic summon (from script / spell)

```
WorldObject::SummonCreature(entry, x,y,z,ang, type, despawnMs, properties, visibleBySummonerOnly)
                                                                   // Object.cpp:2329
  └─ Map::SummonCreature(entry, pos, properties, duration, summoner, spellId, vehId, vis)
                                                                   // Object.cpp:2188
       ├─ pick TempSummon subclass via SummonPropertiesEntry:
       │     Pet / Guardian / Minion / Totem / Puppet / plain TempSummon
       ├─ TempSummon::Create + InitStats(duration)
       ├─ map->AddToMap
       └─ summon->InitSummon();  return ptr
```

### Respawn loop

```
Creature::Update(diff)                         // Creature.cpp:685
  ├─ if dead AND m_respawnTime <= now:
  │     Respawn(false);                        // :1989
  │       ├─ recreate update fields, restore HP/mana
  │       ├─ AIM_Initialize(nullptr)
  │       ├─ if linked-respawn leader: trigger followers
  │       └─ MotionMaster->InitDefault()
  ├─ if despawn-pending AND timer expired:
  │     DespawnOrUnsummon(...)                 // :2128
  ├─ else: i_AI->UpdateAI(diff)
  └─ Unit::Update(diff)
```

`m_respawnDelay` defaults from `CreatureData::spawntimesecs`; `Respawn(force=true)` ignores the timer (used by `.npc respawn` GM command and instance reset).

## Hooks & extension points

- `CreatureScript` (factory) — register via `RegisterCreatureAI(MyAI)` macro; see [`../ai/02-scripted-ai.md`](../ai/02-scripted-ai.md). The factory is keyed on the template's `ScriptID` (resolved from the `ScriptName` string via `sObjectMgr->GetScriptId(...)`).
- AI dispatch surface (`CreatureAI`): `Reset`, `JustEngagedWith`, `JustDied`, `EnterEvadeMode`, `KilledUnit`, `OnSpellCast`, `IsSummonedBy`, `MoveInLineOfSight`, `UpdateAI`. See [`../ai/00-index.md`](../ai/00-index.md).
- `ScriptMgr`: `OnCreatureCreate`, `OnCreatureRemove`, `OnCreatureUpdate` (general); `OnGossipHello`, `OnGossipSelect` (NPC menu); `OnQuestAccept`, `OnQuestReward` (quest giver).
- DB-driven AI: setting `AIName = 'SmartAI'` and populating `smart_scripts` (entryorguid + source_type=0) plugs into the SAI engine without C++.

## Cross-references

- Engine-side: [`../ai/00-index.md`](../ai/00-index.md), [`../ai/02-scripted-ai.md`](../ai/02-scripted-ai.md), [`../movement/01-motion-master.md`](../movement/01-motion-master.md), [`../maps/04-grid-loading.md`](../maps/04-grid-loading.md), [`10-object-mgr.md`](./10-object-mgr.md) (loader matrix), [`../combat/00-index.md`](../combat/00-index.md), [`../loot/00-index.md`](../loot/00-index.md), [`08-pet-vehicle.md`](./08-pet-vehicle.md) (`TempSummon` subclasses)
- Project-side: [`../../06-custom-ids.md`](../../06-custom-ids.md) (custom NPC entries), [`../../09-db-tables.md`](../../09-db-tables.md) (`creature_template`, `creature`, `creature_addon`, `creature_template_addon`, `creature_classlevelstats`, `creature_equip_template`, `creature_model_info`, `creature_loot_template`, `creature_text`, `linked_respawn`, `creature_formations`, `npc_vendor`, `npc_trainer`, `gossip_menu`, `smart_scripts`)
- External: Doxygen `classCreature`, `classTempSummon`, wiki "Creature template", "SmartAI"
