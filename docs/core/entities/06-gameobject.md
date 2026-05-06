# entities — GameObject

> Run-time `GameObject` plus the type-discriminated `GameObjectTemplate` data union (door / chest / button / goober / trap / capture-point / destructible-building / transport / …) and the loot/use trigger pipeline. Cross-links: [`10-object-mgr.md`](./10-object-mgr.md), [`09-corpse-transport.md`](./09-corpse-transport.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/GameObject/GameObject.h:108` | `enum LootState { GO_NOT_READY, GO_READY, GO_ACTIVATED, GO_JUST_DEACTIVATED }` |
| `src/server/game/Entities/GameObject/GameObject.h:119` | `class GameObject : public WorldObject, public GridObject<GameObject>, public MovableMapObject, public UpdatableMapObject` |
| `src/server/game/Entities/GameObject/GameObject.h:75` | `enum class GameObjectActions` (transport AI / spell-effect actions) |
| `src/server/game/Entities/GameObject/GameObject.h:49` | `union GameObjectValue` (per-type runtime state: Transport / FishingHole / CapturePoint / Building) |
| `src/server/game/Entities/GameObject/GameObjectData.h:31` | `struct GameObjectTemplate` (mirrors `gameobject_template`; per-type union starts at field 41) |
| `src/server/game/Entities/GameObject/GameObjectData.h:666` | `struct GameObjectTemplateAddon` (`gameobject_template_addon` — faction, flags, mingold/maxgold) |
| `src/server/game/Entities/GameObject/GameObjectData.h:698` | `struct GameObjectAddon` (per-spawn addon row) |
| `src/server/game/Entities/GameObject/GameObjectData.h:706` | `enum GOState { GO_STATE_ACTIVE, GO_STATE_READY, GO_STATE_ACTIVE_ALTERNATIVE, GO_STATE_DESTROYED }` |
| `src/server/game/Entities/GameObject/GameObjectData.h:714` | `struct GameObjectData : public SpawnData` (mirrors `gameobject` row) |
| `src/server/shared/SharedDefines.h:1562` | `enum GameobjectTypes` (`GAMEOBJECT_TYPE_DOOR=0` … `GAMEOBJECT_TYPE_TRAPDOOR=35`) |
| `src/server/shared/SharedDefines.h:1605` | `enum GameObjectFlags : uint32` (`GO_FLAG_LOCKED`, `GO_FLAG_INTERACT_COND`, `GO_FLAG_DAMAGED`, `GO_FLAG_DESTROYED`, …) |
| `src/server/shared/SharedDefines.h:1629` | `enum GameObjectDestructibleState` |
| `src/server/game/Entities/GameObject/GameObject.cpp:270` | `GameObject::Create(LowType, name_id, Map*, phase, x, y, z, ang, rotation, animprogress, GOState, artKit)` |
| `src/server/game/Entities/GameObject/GameObject.cpp:438` | `GameObject::Update(uint32 diff)` |
| `src/server/game/Entities/GameObject/GameObject.cpp:973` | `GameObject::Delete()` |
| `src/server/game/Entities/GameObject/GameObject.cpp:1018, 1032` | `GameObject::SaveToDB(...)` |
| `src/server/game/Entities/GameObject/GameObject.cpp:1163` | `GameObject::DeleteFromDB()` |
| `src/server/game/Entities/GameObject/GameObject.cpp:1405` | `GameObject::UseDoorOrButton(timeToRestore, alternative, user)` |
| `src/server/game/Entities/GameObject/GameObject.cpp:1455` | `GameObject::Use(Unit* user)` — the type-dispatch switch |
| `src/server/game/Entities/GameObject/GameObject.cpp:2232` | `GameObject::UpdatePackedRotation()` |
| `src/server/game/Globals/ObjectMgr.cpp:7804` | `ObjectMgr::LoadGameObjectTemplate()` |
| `src/server/game/Globals/ObjectMgr.cpp:7993` | `ObjectMgr::LoadGameObjectTemplateAddons()` |
| `src/server/game/Globals/ObjectMgr.cpp:1362` | `ObjectMgr::LoadGameObjectAddons()` |
| `src/server/game/Globals/ObjectMgr.cpp:2845` | `ObjectMgr::LoadGameobjects()` (per-spawn rows from `gameobject`) |
| `src/server/game/Globals/ObjectMgr.cpp:9193` | `ObjectMgr::LoadGameObjectForQuests()` (quest-related GO list) |

## Key concepts

- **Three-layer data**, mirroring `Creature`:
  1. `GameObjectTemplate` — one per `entry`, immutable. Contains the discriminated union (33+ named struct branches under `union { … }` at `GameObjectData.h:41`), keyed by `type` (`GameobjectTypes`).
  2. `GameObjectData` — one per spawn row (`gameobject`).
  3. `GameObject` — the in-world instance, holds `GameObjectTemplate const* m_goInfo`, `GameObjectData const* m_goData`, and a runtime `GameObjectValue m_goValue` (`GameObject.h:49`) for type-specific state.
- **`GameobjectTypes`** (36 values, `SharedDefines.h:1562`):
  - `0 DOOR`, `1 BUTTON`, `2 QUESTGIVER`, `3 CHEST`, `5 GENERIC`, `6 TRAP`, `7 CHAIR`, `8 SPELL_FOCUS`, `9 TEXT`, `10 GOOBER`, `11 TRANSPORT`, `13 CAMERA`, `15 MO_TRANSPORT`, `18 SUMMONING_RITUAL`, `19 MAILBOX`, `21 GUARDPOST`, `22 SPELLCASTER`, `23 MEETINGSTONE`, `24 FLAGSTAND`, `25 FISHINGHOLE`, `26 FLAGDROP`, `27 MINI_GAME`, `29 CAPTURE_POINT`, `30 AURA_GENERATOR`, `31 DUNGEON_DIFFICULTY`, `32 BARBER_CHAIR`, `33 DESTRUCTIBLE_BUILDING`, `35 TRAPDOOR`. The union member to read is determined by `type` — read `GameObject::Use` (`GameObject.cpp:1455`) for the canonical switch.
- **`GOState`** (`GameObjectData.h:706`):
  - `GO_STATE_ACTIVE = 0` — open / triggered (door open, chest opened)
  - `GO_STATE_READY = 1` — closed / armed (default)
  - `GO_STATE_ACTIVE_ALTERNATIVE = 2` — alternative open (e.g. door swing other direction)
  - `GO_STATE_DESTROYED = 3` — wreckage (destructible buildings)
  - Stored in `GAMEOBJECT_BYTES_1` byte 0; `GameObject::SetGoState` triggers visual + collision update.
- **`LootState` (server-side state machine, `GameObject.h:108`)**:
  - For containers: `GO_READY (close) → GO_ACTIVATED (open) → GO_JUST_DEACTIVATED → GO_READY → …`
  - For bobber: `GO_NOT_READY → GO_READY (close) → GO_ACTIVATED (caught) → GO_JUST_DEACTIVATED → <delete>`
  - Comments at `GameObject.h:104-107` enumerate door/closed and door/open variants.
- **Rotation**: world rotation is a `G3D::Quat WorldRotation`; the network/DB form is the 64-bit packed quaternion `m_packedRotation` (computed by `UpdatePackedRotation` at `GameObject.cpp:2232`). Setters: `SetWorldRotationAngles(z,y,x)` / `SetWorldRotation(quat)` (`GameObject.h:147-148`). Stored on the wire as `UPDATEFLAG_ROTATION` (see [`03-update-fields.md`](./03-update-fields.md)).
- **AI**: `GameObjectAI* m_AI` (`GameObject.h:306`); registered through `GameObjectScript` factory. Most GOs use the default no-op AI; capture points / boss-room doors / vehicle-spawning transports get bespoke AIs. Hook list is small: `OnUpdate`, `OnSpellHit`, `Reset`, `OnStateChanged`.
- **Linked traps** — chest / door templates can name a `linkedTrap` entry that triggers on activation (`GameObject::TriggeringLinkedGameObject` at `GameObject.h:269`, called from `Use`).
- **Destructible buildings (type 33)** — `m_goValue.Building.Health / MaxHealth`; `ModifyHealth` at `GameObject.h:290`, `SetDestructibleState` at `:293` switches between `GO_DESTRUCTIBLE_INTACT / DAMAGED / DESTROYED`.
- **Transport sub-tree** — `Transport`, `MotionTransport` (path-driven), `StaticTransport` (instance ferries / lifts) live under `GameObject`. See [`09-corpse-transport.md`](./09-corpse-transport.md).
- **`m_spawnId`** — same convention as `Creature::m_spawnId`: stable id from the `gameobject.guid` column, zero for summoned/non-persisted GOs.

## Flow / data shape

### Spawn from grid load

```
Map::LoadGrid(...)
  └─ for each CellObjectGuids gameobject in cell:
       └─ GameObject::LoadGameObjectFromDB(guid, this, addToMap=true)
            ├─ data = sObjectMgr->GetGameObjectData(guid)         // ObjectMgr.h:1267
            ├─ tmpl = sObjectMgr->GetGameObjectTemplate(data->id)
            ├─ GameObject::Create(newGuid, data->id, this, …)     // GameObject.cpp:270
            │     ├─ m_goInfo = tmpl
            │     ├─ SetWorldRotation
            │     ├─ SetGoType / SetGoState / SetGoArtKit
            │     ├─ initialize m_goValue per type
            │     └─ AIM_Initialize() (factory by ScriptID)
            └─ map->AddToMap(this)
```

### Use pipeline (player right-clicks a GO)

```
client CMSG_GAMEOBJ_USE / GAMEOBJ_REPORT_USE
        │
        ▼
GameObjectHandler::HandleGameObjectUseOpcode             // ../handlers/03-item-handler.md neighbour
        │
        ▼
GameObject::Use(user)                                    // GameObject.cpp:1455
        │  switch (GetGoType()):
        │   GAMEOBJECT_TYPE_DOOR     → UseDoorOrButton(autoCloseTime)
        │   GAMEOBJECT_TYPE_BUTTON   → UseDoorOrButton; trigger linkedTrap
        │   GAMEOBJECT_TYPE_QUESTGIVER → SendGossipMenuFor(user, gossipID)
        │   GAMEOBJECT_TYPE_CHEST    → SendLoot(LOOT_CORPSE)
        │   GAMEOBJECT_TYPE_GOOBER   → cast spellID; eventId; questId
        │   GAMEOBJECT_TYPE_FISHINGNODE → spawn bobber state machine
        │   GAMEOBJECT_TYPE_SPELLCASTER → CastSpell(user, spellId)
        │   GAMEOBJECT_TYPE_MEETINGSTONE → DungeonFinder summon
        │   …
        │
        ▼
ScriptMgr::OnGameObjectUse / OnGossipHello / OnQuestAccept hooks
```

### Per-tick update

```
GameObject::Update(diff)                                 // GameObject.cpp:438
  ├─ m_AI->UpdateAI(diff)
  ├─ switch (m_lootState):
  │   GO_NOT_READY → arm trap if cast complete
  │   GO_READY     → check periodic loot regen, capture-point pulse
  │   GO_ACTIVATED → update door animation, fishing-pulse, transport-anim
  │   GO_JUST_DEACTIVATED → trigger respawn timer, reset LootState
  └─ if m_respawnTime <= now: Respawn()                  // GameObject.h:188
```

## Hooks & extension points

- `GameObjectScript` (factory) for `GameObjectAI` — register via `RegisterGameObjectScriptName(MyAI)` macro. Hooks: `OnGossipHello`, `OnGossipSelect`, `OnQuestAccept`, `OnQuestReward`, `OnReportUse`, `OnSpellHit`, `OnLootStateChanged`.
- `ScriptMgr::OnGameObjectUse` is fired from `GameObject::Use` early — useful to veto interactions.
- DB-driven scripting: `smart_scripts` with `source_type = 1` (gameobject); `gameobject_scripts` table for one-shot script chains; `event_scripts` for spell-event hooks.
- Quest involvement: `gameobject_questrelation` / `gameobject_involvedrelation` (loaded by `LoadGameobjectQuestStarters / LoadGameobjectQuestEnders`, [`10-object-mgr.md`](./10-object-mgr.md)).

## Cross-references

- Engine-side: [`10-object-mgr.md`](./10-object-mgr.md), [`../maps/04-grid-loading.md`](../maps/04-grid-loading.md), [`../loot/02-loot-roll.md`](../loot/02-loot-roll.md), [`09-corpse-transport.md`](./09-corpse-transport.md) (`Transport` / `MotionTransport` / `StaticTransport` extend `GameObject`), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md), [`03-update-fields.md`](./03-update-fields.md) (`GAMEOBJECT_END = OBJECT_END + 0x000C`)
- Project-side: [`../../09-db-tables.md`](../../09-db-tables.md) (`gameobject_template`, `gameobject_template_addon`, `gameobject`, `gameobject_addon`, `gameobject_loot_template`, `gameobject_questrelation`, `gameobject_involvedrelation`, `gameobject_questitem`, `transports`)
- External: Doxygen `classGameObject`, `structGameObjectTemplate`, wiki "GameObject Templates"
