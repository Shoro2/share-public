# entities/ — Object hierarchy

> The `Object → WorldObject → Unit → Player/Creature/...` class tree, GUIDs, update fields, and `ObjectMgr` (the central template/cache loader).

## Topic files

| File | Topic |
|---|---|
| [`01-object-hierarchy.md`](./01-object-hierarchy.md) | Class tree from `Object` down, abstract vs. concrete, what each layer adds |
| [`02-object-guid.md`](./02-object-guid.md) | `ObjectGuid`, `HighGuid`, packed-guid wire format |
| [`03-update-fields.md`](./03-update-fields.md) | `m_uint32Values`, `UpdateMask`, `BuildValuesUpdate`, dirty-tracking |
| [`04-player.md`](./04-player.md) | `Player.h` tour (3069 lines), what lives where, sub-managers |
| [`05-creature.md`](./05-creature.md) | `Creature`, `CreatureTemplate`, `creature_template`/`creature` DB rows, respawn |
| [`06-gameobject.md`](./06-gameobject.md) | `GameObject`, `GameObjectTemplate`, GO types, scripts |
| [`07-item.md`](./07-item.md) | `Item`, `ItemTemplate`, dynamic enchantments, slot semantics |
| [`08-pet-vehicle.md`](./08-pet-vehicle.md) | `Pet`, `Vehicle`, `Totem`, `DynamicObject` |
| [`09-corpse-transport.md`](./09-corpse-transport.md) | `Corpse`, `Transport`, `MotionTransport` |
| [`10-object-mgr.md`](./10-object-mgr.md) | `ObjectMgr` — central caches, world-DB loaders, ID ranges |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Object/Object.{h,cpp}` | Root class, update-field machinery |
| `src/server/game/Entities/Object/ObjectGuid.{h,cpp}` | GUID encoding |
| `src/server/game/Entities/Unit/Unit.{h,cpp}` | Combat-capable base |
| `src/server/game/Entities/Player/Player.h` (~3069 lines) | Player class declaration |
| `src/server/game/Entities/Creature/Creature.{h,cpp}`, `CreatureData.h` | Creature + spawn data |
| `src/server/game/Entities/GameObject/GameObject.{h,cpp}`, `GameObjectData.h` | GO + spawn data |
| `src/server/game/Entities/Item/Item.{h,cpp}`, `ItemTemplate.h` | Item runtime + template |
| `src/server/game/Entities/Pet/Pet.{h,cpp}` | Pet specialization |
| `src/server/game/Entities/Vehicle/Vehicle.{h,cpp}` | Seat owner |
| `src/server/game/Entities/Corpse/*`, `Transport/*` | Body / mover |
| `src/server/game/Globals/ObjectMgr.{h,cpp}` | Loaders + caches |

## Cross-references

- Engine-side: [`../maps/04-grid-loading.md`](../maps/04-grid-loading.md) (where entities are added to a grid), [`../movement/01-motion-master.md`](../movement/01-motion-master.md), [`../combat/00-index.md`](../combat/00-index.md), [`../spells/03-aura-system.md`](../spells/03-aura-system.md)
- Project-side: [`../../05-modules.md`](../../05-modules.md) (Paragon stores invisible auras on `Player`), [`../../06-custom-ids.md`](../../06-custom-ids.md) (custom NPC/item IDs), [`../../09-db-tables.md`](../../09-db-tables.md) (per-table layout)
- External: Doxygen for `Object`, `Unit`, `Player`, `Creature`, `GameObject`, `Item`, `ObjectMgr`
