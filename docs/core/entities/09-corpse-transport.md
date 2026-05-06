# entities — Corpse, Transport, MotionTransport

> Player corpses (and the bones they decay into), the GameObject-derived `Transport` family, and how transport-relative coordinates work for passengers. Cross-links: [`06-gameobject.md`](./06-gameobject.md), [`08-pet-vehicle.md`](./08-pet-vehicle.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Corpse/Corpse.h:26` | `enum CorpseType { BONES=0, RESURRECTABLE_PVE=1, RESURRECTABLE_PVP=2 }` |
| `src/server/game/Entities/Corpse/Corpse.h:35` | `#define CORPSE_RECLAIM_RADIUS 39` |
| `src/server/game/Entities/Corpse/Corpse.h:37` | `enum CorpseFlags` (`BONES`, `HIDE_HELM`, `HIDE_CLOAK`, `LOOTABLE`) |
| `src/server/game/Entities/Corpse/Corpse.h:48` | `class Corpse : public WorldObject, public GridObject<Corpse>` |
| `src/server/game/Entities/Corpse/Corpse.cpp:67` | `Corpse::Create(LowType guidlow, Player* owner)` |
| `src/server/game/Entities/Corpse/Corpse.cpp:90` | `Corpse::SaveToDB()` |
| `src/server/game/Entities/Corpse/Corpse.cpp:119, 124` | `Corpse::DeleteFromDB(...)` (member + static) |
| `src/server/game/Entities/Corpse/Corpse.cpp:131` | `Corpse::LoadCorpseFromDB(LowType guid, Field* fields)` |
| `src/server/game/Entities/Corpse/Corpse.cpp:183` | `Corpse::IsExpired(time_t t)` |
| `src/server/game/Entities/Corpse/Corpse.cpp:195` | `Corpse::ResetGhostTime()` |
| `src/server/game/Entities/Transport/Transport.h:29` | `class Transport : public GameObject, public TransportBase` (abstract) |
| `src/server/game/Entities/Transport/Transport.h:36` | `typedef std::set<WorldObject*> PassengerSet` |
| `src/server/game/Entities/Transport/Transport.h:50` | `class MotionTransport : public Transport` (path-driven boats / zeppelins) |
| `src/server/game/Entities/Transport/Transport.h:114` | `class StaticTransport : public Transport` (lifts / dungeon ferries — interpolated by anim) |
| `src/server/game/Entities/Transport/Transport.cpp:47` | `MotionTransport::CreateMoTrans(LowType guidlow, entry, mapid, x,y,z,ang, animprogress)` |
| `src/server/game/Entities/Transport/Transport.cpp:138` | `MotionTransport::Update(uint32 diff)` (advance keyframes) |
| `src/server/game/Entities/Transport/Transport.cpp:248` | `MotionTransport::UpdatePosition(x,y,z,o)` |
| `src/server/game/Entities/Transport/Transport.cpp:264` | `MotionTransport::AddPassenger(WorldObject*, withAll)` |
| `src/server/game/Entities/Transport/Transport.cpp:318` | `MotionTransport::CreateNPCPassenger(LowType guid, CreatureData const*)` |
| `src/server/game/Entities/Transport/Transport.cpp:366` | `MotionTransport::CreateGOPassenger(LowType guid, GameObjectData const*)` |
| `src/server/game/Entities/Transport/Transport.cpp:620` | `MotionTransport::UpdatePassengerPositions(PassengerSet&)` |
| `src/server/game/Entities/Transport/Transport.cpp:727` | `StaticTransport::Create(...)` |
| `src/server/game/Maps/TransportMgr.h:41` | `struct KeyFrame` |
| `src/server/game/Maps/TransportMgr.h:70` | `struct TransportTemplate` (path + key-frame vector) |
| `src/server/game/Maps/TransportMgr.h:87` | `struct TransportAnimation` |
| `src/server/game/Maps/TransportMgr.h:101` | `class TransportMgr` (singleton; loads templates, spawns continents) |
| `src/server/game/Maps/TransportMgr.cpp:51` | `TransportMgr::LoadTransportTemplates()` (`transports` table → templates) |
| `src/server/game/Maps/TransportMgr.cpp:115` | `TransportMgr::GeneratePath(GameObjectTemplate const*, TransportTemplate*)` |
| `src/server/game/Maps/TransportMgr.cpp:359` | `TransportMgr::CreateTransport(entry, guid, Map*)` (factory for `MotionTransport`) |
| `src/server/game/Maps/TransportMgr.cpp:420` | `TransportMgr::SpawnContinentTransports()` (per-continent spawn at world start) |
| `src/server/game/Maps/TransportMgr.cpp:493` | `TransportMgr::CreateInstanceTransports(Map*)` |

## Key concepts

### Corpse

- **Two kinds of corpses, one class.** `CorpseType::BONES` is the post-decay marker — owner gone, no resurrect possible, only insignia loot in BG. `RESURRECTABLE_PVE` / `RESURRECTABLE_PVP` is the reclaimable body.
- **Always belongs to a Player.** Mob deaths leave a `Creature` in `JUST_DIED` state for `m_corpseDelay` seconds, not a `Corpse` instance.
- **Persisted** in the `corpse` table (mapped by `CharacterDatabase`). `SaveToDB` writes immediately on death; `DeleteFromDB(ownerGuid, trans)` (`Corpse.cpp:124`) is used at character delete and on resurrect.
- **Reclaim window**: ghost player must be within `CORPSE_RECLAIM_RADIUS = 39` yards. Helper at `Corpse.h:35`. After config-driven decay (`m_time`), `IsExpired(now)` returns true and the corpse converts to bones; original is removed.
- **`CORPSE_FLAG_LOOTABLE` (0x20)** — set on insignia loot in BG; `loot` member at `Corpse.h:77` holds the rolled drop. `lootRecipient` (the killer's `Player*`) at `:78`.
- **Looking up**: `ObjectAccessor::GetCorpseForPlayerGUID` is the canonical lookup; the corpse is also cached by spawn cell (`Corpse::SetCellCoord` / `GetCellCoord`).

### Transport family

- **`Transport` is abstract.** It declares the `PassengerSet` and the pure-virtual `AddPassenger / RemovePassenger` (`Transport.h:37-38`); concrete subclasses are `MotionTransport` and `StaticTransport`.
- **`MotionTransport`** (path-driven boats, zeppelins, gunships, deeprun tram) advances along a `KeyFrameVec` (`Transport.h:77`). Each `KeyFrame` (`TransportMgr.h:41`) wraps a `TaxiPathNodeEntry` plus interpolation state. `Update(diff)` (`Transport.cpp:138`) walks the keyframes, fires arrival/departure events, and calls `UpdatePassengerPositions`.
- **`StaticTransport`** (instance lifts, vehicles in Dalaran, Naxx ferries) is animation-driven, not path-driven — uses `TransportAnimation` (`TransportMgr.h:87`) plus `m_goValue.Transport.PathProgress` to interpolate a fixed loop. `GetPeriod()` reads `AnimationInfo->TotalTime` (`Transport.h:136`).
- **Static passengers.** `MotionTransport::LoadStaticPassengers` reads `creature.transport_*` and `gameobject.transport_*` columns and pre-spawns NPCs/GOs that ride the transport for its lifetime (the gunship guards, Orgrimmar zeppelin barker). `_staticPassengers` is held separately so they don't get unloaded with regular passengers.
- **Lifecycle on map start.** `TransportMgr::SpawnContinentTransports()` (`TransportMgr.cpp:420`) is called from `World::SetInitialWorldSettings`; instance transports come up later in `Map::AddInstanceTransports` calling `TransportMgr::CreateInstanceTransports(this)` (`TransportMgr.cpp:493`).
- **Path generation.** `TransportMgr::GeneratePath(...)` (`TransportMgr.cpp:115`) walks the GameObject's `MoTransport` taxi-path and constructs the `KeyFrameVec`, computing accel/decel and per-segment durations.
- **Wire flag**: `UPDATEFLAG_TRANSPORT` (`UpdateData.h:40`) makes the client treat the path-progress field as a transport progress field.

### Transport-relative coordinates

Passengers store their **offset** from the transport's anchor in `MovementInfo::transport.pos` (`Object.h:308-313`). Conversion utilities live on `TransportBase` and are called by overrides in each concrete class:

- `Transport::CalculatePassengerPosition(x, y, z, o)` — local offset → world coords (e.g. `Transport.h:33`).
- `Transport::CalculatePassengerOffset(x, y, z, o)` — world coords → local offset (e.g. `Transport.h:34`).

When a movement opcode arrives with `MOVEFLAG_ONTRANSPORT` set, `MovementHandler` runs the offset through `CalculatePassengerPosition` to produce the player's true world position. See [`../handlers/02-movement-handler.md`](../handlers/02-movement-handler.md).

## Flow / data shape

### Player death → corpse → bones

```
Player::KillPlayer (Player.cpp; PlayerStorage)
  └─ Player::CreateCorpse()
       └─ Corpse* c = new Corpse(CORPSE_RESURRECTABLE_*)
       └─ c->Create(newLowGuid, player)              // Corpse.cpp:67
       └─ c->SaveToDB()                              // Corpse.cpp:90 (CHAR_INS_CORPSE)
       └─ map->AddToMap(c)
…30 minutes (default decay)…
Corpse::Update / world tick
  └─ if c->IsExpired(now):                           // Corpse.cpp:183
       └─ ConvertToBones (sets type=CORPSE_BONES, removes owner reclaim)
…bones decay…
Corpse::DeleteFromDB(trans)                          // Corpse.cpp:119
```

### MotionTransport tick

```
MotionTransport::Update(diff)                        // Transport.cpp:138
  ├─ advance _positionChangeTimer
  ├─ if reached _nextFrame:
  │     _currentFrame = _nextFrame; ++_nextFrame;
  │     DoEventIfAny(*_currentFrame, departure=true)
  │     update GAMEOBJECT_LEVEL (period field)
  ├─ pos = interpolate(_currentFrame, _nextFrame, perc)
  ├─ if pos crossed map boundary: TeleportTransport(newMapId, …)
  ├─ UpdatePosition(pos.x, pos.y, pos.z, o)          // Transport.cpp:248
  └─ UpdatePassengerPositions(_passengers)           // Transport.cpp:620
       └─ for each passenger:
            CalculatePassengerPosition(local → world)
            passenger->Relocate(world)
```

## Hooks & extension points

- `TransportScript` (declared in `Scripting/ScriptDefines/TransportScript.h`): `OnAddPassenger`, `OnRemovePassenger`, `OnUpdate`, `OnRelocate`. Wired by `MotionTransport::Update` and `MotionTransport::AddPassenger`.
- Corpse has no dedicated script class. Player resurrection / release hooks live on `PlayerScript` (`OnPlayerReleasedGhost`, custom in this fork).
- Adding a new transport route: insert into the `transports` world-DB table → `TransportMgr` re-loads → `GameObjectTemplate` of type `MO_TRANSPORT` carries the path id → `TaxiPathNode.dbc` provides node coordinates. No code change needed.

## Cross-references

- Engine-side: [`06-gameobject.md`](./06-gameobject.md) (`Transport` IS a `GameObject`), [`08-pet-vehicle.md`](./08-pet-vehicle.md) (`Vehicle` shares the `TransportBase` mixin), [`../handlers/02-movement-handler.md`](../handlers/02-movement-handler.md) (`MOVEFLAG_ONTRANSPORT` decoding), [`../maps/04-grid-loading.md`](../maps/04-grid-loading.md) (transports cross map boundaries via `TeleportTransport`), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md) (`TransportScript`)
- Project-side: [`../../09-db-tables.md`](../../09-db-tables.md) (`transports`, `corpse`, `creature` (`transport_guid`/`_x/_y/_z/_o` columns), `gameobject` (same))
- External: Doxygen `classCorpse`, `classMotionTransport`, `classStaticTransport`, `classTransportMgr`, wiki "Transports"
