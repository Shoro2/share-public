# entities — Object hierarchy

> The C++ class tree rooted at `Object`, the per-layer additions (GUID, position, AI, sub-tables), and the most-overridden virtuals. Cross-links: [`02-object-guid.md`](./02-object-guid.md), [`03-update-fields.md`](./03-update-fields.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Object/Object.h:104` | `class Object` — root, owns `m_uint32Values` and update mask |
| `src/server/game/Entities/Object/Object.h:474` | `class WorldObject : public Object, public WorldLocation` — adds map/zone/phase/name/visibility |
| `src/server/game/Entities/Unit/Unit.h:663` | `class Unit : public WorldObject` — combat, auras, stats, movement |
| `src/server/game/Entities/Player/Player.h:1083` | `class Player : public Unit, public GridObject<Player>` |
| `src/server/game/Entities/Creature/Creature.h:46` | `class Creature : public Unit, public GridObject<Creature>, public MovableMapObject, public UpdatableMapObject` |
| `src/server/game/Entities/Creature/TemporarySummon.h:49` | `class TempSummon : public Creature` (root of summon hierarchy) |
| `src/server/game/Entities/Creature/TemporarySummon.h:86` | `class Minion : public TempSummon` |
| `src/server/game/Entities/Creature/TemporarySummon.h:105` | `class Guardian : public Minion` |
| `src/server/game/Entities/Pet/Pet.h:40` | `class Pet : public Guardian` |
| `src/server/game/Entities/Totem/Totem.h:50` | `class Totem : public Minion` |
| `src/server/game/Entities/GameObject/GameObject.h:119` | `class GameObject : public WorldObject, public GridObject<GameObject>, public MovableMapObject, public UpdatableMapObject` |
| `src/server/game/Entities/Transport/Transport.h:29` | `class Transport : public GameObject, public TransportBase` |
| `src/server/game/Entities/Transport/Transport.h:50` | `class MotionTransport : public Transport` |
| `src/server/game/Entities/Transport/Transport.h:114` | `class StaticTransport : public Transport` |
| `src/server/game/Entities/Item/Item.h:219` | `class Item : public Object` (no `WorldObject` — items have no map position) |
| `src/server/game/Entities/Corpse/Corpse.h:48` | `class Corpse : public WorldObject, public GridObject<Corpse>` |
| `src/server/game/Entities/DynamicObject/DynamicObject.h:34` | `class DynamicObject : public WorldObject, public GridObject<DynamicObject>, public MovableMapObject, public UpdatableMapObject` |
| `src/server/game/Entities/Vehicle/Vehicle.h:27` | `class Vehicle : public TransportBase` (NOT a WorldObject — wraps a `Unit*` host) |

## Key concepts

- **`TypeID`** ([`02-object-guid.md`](./02-object-guid.md), `ObjectGuid.h:30`) — runtime tag stored in `m_objectTypeId`. Eight values: `OBJECT, ITEM, CONTAINER, UNIT, PLAYER, GAMEOBJECT, DYNAMICOBJECT, CORPSE`. Used by `Is*()` / `To*()` casts (`Object.h:201-225`).
- **`TypeMask`** (`ObjectGuid.h:44`) — bitmask form for "is one of these types?" queries via `Object::isType(uint16)` (`Object.h:130`).
- **Diamond?** — `Player`/`Creature`/`GameObject`/`Corpse`/`DynamicObject` use multiple inheritance from `WorldObject` plus the `GridObject<T>` mixin to participate in grid linkage. There is no diamond on `Object`: each leaf class has exactly one `Object` sub-object.
- **`Item` is intentionally NOT a `WorldObject`.** It has GUID + update fields but no map/grid presence; the owning `Player`'s storage decides where it lives. See [`07-item.md`](./07-item.md).
- **`Vehicle` is NOT in the `Object` tree at all.** It is a passenger-seat owner attached to a `Unit` via `Unit::CreateVehicleKit(...)` (`Vehicle.h:63`). The `Unit` is the entity; `Vehicle` is a behavior object. See [`08-pet-vehicle.md`](./08-pet-vehicle.md).
- **`GridObject<T>`** (`Object.h:361`) — CRTP mixin holding a `GridReference<T>` so the entity can be linked into the per-cell intrusive list. Players/Creatures/GameObjects/Corpses/DynamicObjects use it; `Item` does not.
- **`MovableMapObject` / `UpdatableMapObject`** (`Object.h:413, 431`) — flags + relocation queue hooks used by [`maps/`](../maps/00-index.md) for move-state tracking.

## Flow / data shape

```
                                 Object  (Object.h:104)
                                 │  m_uint32Values, _changesMask, GUID, TypeID
              ┌──────────────────┼──────────────────┬─────────────┐
              │                  │                  │             │
        WorldObject            Item             (none)        (none)
        (positioned)         (Item.h:219)
        ├─ map/zone/phase
        ├─ name
        └─ visibility
              │
   ┌──────────┼─────────────┬────────────┬───────────────────┐
   │          │             │            │                   │
  Unit   GameObject     Corpse     DynamicObject       (no others)
  (combat) (clickable) (player    (spell anchor)
   │       │            body)
   │       └─ Transport ─► MotionTransport / StaticTransport
   │
   ├─ Player  (own data: PvP, talents, taxi, achievements, social, …)
   └─ Creature
       └─ TempSummon
           ├─ Minion
           │   ├─ Guardian ─► Pet           (Pet.h:40 — full pet API)
           │   └─ Totem                     (Totem.h:50)
           └─ Puppet                        (TemporarySummon.h:124)

  Sibling, NOT in Object tree:
    Vehicle  (Vehicle.h:27)   — passenger holder, owns no GUID, attached to a Unit
    TransportBase             — pure helper, base for Vehicle and Transport mixin
```

### Per-layer "what this adds"

| Layer | Adds (most relevant) |
|---|---|
| `Object` | `m_uint32Values` array, `_changesMask`, GUID, packed-GUID, `TypeID`, `TypeMask`, `Get/SetUInt32Value`, `BuildCreateUpdateBlockForPlayer` (`Object.h:132`) |
| `WorldObject` | `Map*`, `m_phaseMask`, `m_InstanceId`, name, visibility, distance helpers, `SummonCreature`, `SummonGameObject` (`Object.h:474+`) |
| `Unit` | combat state (attackers/victim), auras, threat, `CharmInfo`, movement spline, `MotionMaster`, `UnitAI`, vehicle kit (`Unit.h:663`) |
| `Player` | inventory, quest log, talents, social, group, achievements, taxi, friend list, mail (see [`04-player.md`](./04-player.md) for the section tour) |
| `Creature` | `CreatureTemplate*`, spawn id, faction, lootid, equipment, react state, `CreatureAI` (see [`05-creature.md`](./05-creature.md)) |
| `GameObject` | `GameObjectTemplate*`, type-discriminated union (door/chest/trap/…), `GameObjectAI`, loot, rotation (see [`06-gameobject.md`](./06-gameobject.md)) |

## Most-overridden virtuals (override matrix)

| Virtual (declared at) | Player | Creature | Pet | GameObject | DynObj | Corpse | Item |
|---|---|---|---|---|---|---|---|
| `Update(uint32 diff)` (`Object.h:481` `WorldObject::Update`) | `PlayerUpdates.cpp:53` | `Creature.cpp:685` | `Pet.h:72` | `GameObject.cpp:438` | `DynamicObject.h:46` | — | — |
| `AddToWorld() / RemoveFromWorld()` (`Object.h:111`) | `Player.h:1095` | `Creature.h:52` | `Pet.h:46` | `GameObject` (cpp) | `DynamicObject.h:40` | `Corpse.h:54` | (Object base) |
| `BuildValuesUpdate(uint8, ByteBuffer*, Player*)` (`Object.h:250`) | overridden | overridden | (inherited) | overridden | overridden | `Corpse.h:57` | (Object) |
| `BuildCreateUpdateBlockForPlayer(...)` (`Object.h:132`) | overridden | (inherited) | (inherited) | overridden | (inherited) | (inherited) | (inherited) |
| `CleanupsBeforeDelete(bool)` (`Object.h:563` `WorldObject`) | overridden | overridden | — | overridden | `DynamicObject.h:43` | — | — |
| `setDeathState(DeathState, bool)` (`Unit.h`) | `Player.h:1208` | overridden | `Pet.h:71` | n/a | n/a | n/a | n/a |
| `Heartbeat()` (`Object.h:227`, every 5.2 s) | overridden | overridden | (inherited) | (inherited) | (inherited) | (inherited) | (inherited) |
| `AddToObjectUpdate / RemoveFromObjectUpdate` (`Object.h:270` pure-virtual) | implemented | implemented | (inherited) | implemented | implemented | implemented | `Item.h:361` |

`HEARTBEAT_INTERVAL` is `5s + 200ms` (`Object.h:102`); the world tick fires `Heartbeat()` on this cadence for every entity that overrides it.

## Hooks & extension points

- `ScriptMgr` exposes per-class scripts: `PlayerScript`, `UnitScript`, `CreatureScript` / AI factory, `GameObjectScript`, `ItemScript`, `DynamicObjectScript`. Class taxonomy and dispatch site: [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).
- Adding a new entity family is intentionally rare; prefer specialising via `TempSummon` or `CreatureScript` AI.
- `CustomData` (`Object.h:231`) is a `DataMap` slot for module-private state attached to any `Object` without subclassing — used by Paragon to stash account-level data on `Player`. See [`../../05-modules.md`](../../05-modules.md).

## Cross-references

- Engine-side: [`02-object-guid.md`](./02-object-guid.md) (GUID layer), [`03-update-fields.md`](./03-update-fields.md) (the values array), [`04-player.md`](./04-player.md), [`05-creature.md`](./05-creature.md), [`06-gameobject.md`](./06-gameobject.md), [`07-item.md`](./07-item.md), [`08-pet-vehicle.md`](./08-pet-vehicle.md), [`09-corpse-transport.md`](./09-corpse-transport.md), [`../maps/04-grid-loading.md`](../maps/04-grid-loading.md) (`AddToWorld` actually inserts into a grid)
- Project-side: [`../../02-architecture.md`](../../02-architecture.md) (top-level subsystem placement), [`../../05-modules.md`](../../05-modules.md) (`CustomData` consumers)
- External: Doxygen `classObject`, `classWorldObject`, `classUnit`, `classPlayer`, `classCreature`, `classGameObject`, `classItem`
