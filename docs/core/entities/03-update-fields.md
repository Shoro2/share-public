# entities — Update fields

> The `m_uint32Values` array, the per-index dirty mask, and how dirty fields turn into `SMSG_UPDATE_OBJECT` blocks. Cross-links: [`01-object-hierarchy.md`](./01-object-hierarchy.md), [`../network/02-worldpacket.md`](../network/02-worldpacket.md), [`../maps/05-visibility.md`](../maps/05-visibility.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Object/Updates/UpdateFields.h:23` | `enum EObjectFields` (root layout: GUID/TYPE/ENTRY/SCALE_X) |
| `src/server/game/Entities/Object/Updates/UpdateFields.h:30` | `OBJECT_END = 0x0006` (offset where derived enums start) |
| `src/server/game/Entities/Object/Updates/UpdateFields.h:33-73` | `enum EItemFields` → `ITEM_END = OBJECT_END + 0x003A` |
| `src/server/game/Entities/Object/Updates/UpdateFields.h:76-81` | `enum EContainerFields` → `CONTAINER_END = ITEM_END + 0x004A` |
| `src/server/game/Entities/Object/Updates/UpdateFields.h:84-175` | `enum EUnitFields` → `UNIT_END = OBJECT_END + 0x008E` |
| `src/server/game/Entities/Object/Updates/UpdateFields.h:175-392` | Player block (continuation of `EUnitFields` namespace) → `PLAYER_END = UNIT_END + 0x049A` |
| `src/server/game/Entities/Object/Updates/UpdateFields.h:395-405` | `enum EGameObjectFields` → `GAMEOBJECT_END = OBJECT_END + 0x000C` |
| `src/server/game/Entities/Object/Updates/UpdateFields.h:408-415` | `enum EDynamicObjectFields` → `DYNAMICOBJECT_END = OBJECT_END + 0x0006` |
| `src/server/game/Entities/Object/Updates/UpdateFields.h:418-430` | `enum ECorpseFields` → `CORPSE_END = OBJECT_END + 0x001E` |
| `src/server/game/Entities/Object/Updates/UpdateMask.h:24` | `class UpdateMask` (per-index bitset) |
| `src/server/game/Entities/Object/Updates/UpdateData.h:26` | `enum OBJECT_UPDATE_TYPE` (CREATE_OBJECT / VALUES / OUT_OF_RANGE / …) |
| `src/server/game/Entities/Object/Updates/UpdateData.h:36` | `enum OBJECT_UPDATE_FLAGS` (`UPDATEFLAG_LIVING`, `UPDATEFLAG_HAS_TARGET`, …) |
| `src/server/game/Entities/Object/Updates/UpdateData.h:51` | `class UpdateData` (per-target accumulator) |
| `src/server/game/Entities/Object/Updates/UpdateData.cpp:48` | `UpdateData::BuildPacket(WorldPacket&)` (final assembly) |
| `src/server/game/Entities/Object/Updates/UpdateFieldFlags.h:24` | `enum UpdatefieldFlags` (`UF_FLAG_PUBLIC / OWNER / PRIVATE / ITEM_OWNER / SPECIAL_INFO / PARTY_MEMBER / DYNAMIC`) |
| `src/server/game/Entities/Object/Updates/UpdateFieldFlags.h:38-42` | per-class flag-arrays: `ItemUpdateFieldFlags[CONTAINER_END]`, `UnitUpdateFieldFlags[PLAYER_END]`, `GameObjectUpdateFieldFlags[GAMEOBJECT_END]`, `DynamicObjectUpdateFieldFlags[DYNAMICOBJECT_END]`, `CorpseUpdateFieldFlags[CORPSE_END]` |
| `src/server/game/Entities/Object/Object.h:188` | `GetValuesCount()` — size of `m_uint32Values` |
| `src/server/game/Entities/Object/Object.h:257-263` | union `m_int32Values / m_uint32Values / m_floatValues` (single allocation, three views) |
| `src/server/game/Entities/Object/Object.h:264` | `UpdateMask _changesMask` |
| `src/server/game/Entities/Object/Object.h:274` | `bool m_objectUpdated` (set by `AddToObjectUpdateIfNeeded`) |
| `src/server/game/Entities/Object/Object.cpp:113` | `Object::_InitValues()` — allocate + `_changesMask.SetCount(m_valuesCount)` |
| `src/server/game/Entities/Object/Object.cpp:178` | `Object::BuildCreateUpdateBlockForPlayer(UpdateData*, Player*)` |
| `src/server/game/Entities/Object/Object.cpp:246` | `Object::BuildValuesUpdateBlockForPlayer(UpdateData*, Player*)` |
| `src/server/game/Entities/Object/Object.cpp:258` | `Object::BuildOutOfRangeUpdateBlock(UpdateData*)` |
| `src/server/game/Entities/Object/Object.cpp:332` | `Object::BuildMovementUpdate(ByteBuffer*, uint16 flags)` |
| `src/server/game/Entities/Object/Object.cpp:486` | `Object::BuildValuesUpdate(uint8 updateType, ByteBuffer*, Player*)` — writes mask + dirty values |
| `src/server/game/Entities/Object/Object.cpp:513` | `Object::AddToObjectUpdateIfNeeded()` — push to map's update queue |
| `src/server/game/Entities/Object/Object.cpp:522` | `Object::ClearUpdateMask(bool remove)` (called per-tick) |
| `src/server/game/Entities/Object/Object.cpp:534` | `Object::BuildFieldsUpdate(Player*, UpdateDataMapType&)` |
| `src/server/game/Entities/Object/Object.cpp:548` | `Object::GetUpdateFieldData(Player const* target, uint32*& flags)` — picks the per-class flags array + visibility mask |

## Key concepts

- **One contiguous `uint32` array per object.** `m_uint32Values` (`Object.h:260`) is a flat block sized to the leaf class's `_END` value; `_InitValues` allocates exactly `m_valuesCount` slots and zero-fills (`Object.cpp:113`). `int32`/`float` views share the same memory (union at `Object.h:257`).
- **Per-index visibility flags.** Every leaf class has a precomputed `uint32 *UpdateFieldFlags[]` (`UpdateFieldFlags.h:38-42`) telling who is allowed to see each field. Values are an OR of `UF_FLAG_*` bits (`UpdateFieldFlags.h:24`):
  - `PUBLIC` — every observer
  - `OWNER` — Unit's owner / Item's owner Player
  - `PRIVATE` — only the entity itself (Player viewing own data)
  - `ITEM_OWNER` — only the Player who owns this Item
  - `SPECIAL_INFO` — see-invisibility / GM viewers (`Object.cpp:GetUpdateFieldData`)
  - `PARTY_MEMBER` — group teammates only
  - `DYNAMIC` — calculated at write time (e.g. `UNIT_DYNAMIC_FLAGS`)
- **`UpdateMask`** (`UpdateMask.h:24`) — a per-index bit vector resized to `m_valuesCount`. `SetBit(i)` flips the bit; `AppendToPacket(ByteBuffer*)` writes it as 32-bit blocks (the client expects fixed `ClientUpdateMaskType = uint32`, see `UpdateMask.h:28`).
- **Dirty-tracking flow.** Setters in `Object.cpp` (`SetUInt32Value`, `SetFloatValue`, …) compare-and-swap the slot, set the bit in `_changesMask`, then call `AddToObjectUpdateIfNeeded()` (`Object.cpp:639` etc.). `m_objectUpdated` flags the object for the map's broadcast pass.
- **Two block types.** `UPDATETYPE_CREATE_OBJECT(2)` / `_CREATE_OBJECT2(3)` carries the full movement block + every visible field (used on enter-grid). `UPDATETYPE_VALUES(0)` carries only dirty fields. `UPDATETYPE_OUT_OF_RANGE_OBJECTS(4)` is just a list of GUIDs to delete client-side. Enum at `UpdateData.h:26`.
- **`UpdateData` is per-target.** `UpdateDataMapType = std::unordered_map<Player*, UpdateData>` (`Object.h:100`). `BuildFieldsUpdate(Player*, map)` (`Object.cpp:534`) picks/creates the entry for that target and appends the per-target block; `BuildPacket` (`UpdateData.cpp:48`) finalises into one `SMSG_UPDATE_OBJECT`.
- **Field counts (block sizes).**
  - Object (root): 6
  - Item: 64 (= `OBJECT_END(6) + 0x003A`)
  - Container: 138 (= `ITEM_END(64) + 0x004A`, adds bag-slot guids)
  - Unit: 148 (= `OBJECT_END(6) + 0x008E`)
  - Player: 1326 (= `UNIT_END(148) + 0x049A` — the giant block)
  - GameObject: 18 (= `OBJECT_END(6) + 0x000C`)
  - DynamicObject: 12 (= `OBJECT_END(6) + 0x0006`)
  - Corpse: 36 (= `OBJECT_END(6) + 0x001E`)

## Flow / data shape

### Per-tick broadcast (cold path: object enters a player's grid)

```
Map::Update(diff)
  └─ for each Player p in active cells
       └─ for each Object o newly visible to p
            └─ o->BuildCreateUpdateBlockForPlayer(&updData[p], p)   // Object.cpp:178
                  ├─ build movement block (BuildMovementUpdate)
                  ├─ build values block:
                  │    BuildValuesUpdate(UPDATETYPE_CREATE_OBJECT, &buf, p)  // :486
                  │      ├─ flags = GetUpdateFieldData(p, ...)              // :548
                  │      └─ for each i in 0..m_valuesCount:
                  │           if visibility ok AND (creating OR _changesMask[i]):
                  │             mask.SetBit(i); buf << m_uint32Values[i]
                  └─ updData[p].AddUpdateBlock(buf)
  └─ for each (player, UpdateData) pair: data.BuildPacket(packet); player->SendDirectMessage(packet)
```

### Per-tick broadcast (hot path: existing observers, only changed fields)

```
Object::SetUInt32Value(idx, value)         // Object.cpp:639
  ├─ if m_uint32Values[idx] == value: return
  ├─ m_uint32Values[idx] = value
  ├─ _changesMask.SetBit(idx)
  └─ AddToObjectUpdateIfNeeded()           // sets m_objectUpdated, enqueues with map

…tick boundary…

Map::SendObjectUpdates()
  └─ for each updated object o:
       └─ o->BuildUpdate(updateMap)         // virtual; Item overrides at Item.h:360
            └─ for each Player p in range that can see o:
                 BuildFieldsUpdate(p, updateMap)
                   └─ BuildValuesUpdateBlockForPlayer(&updateMap[p], p)  // Object.cpp:246
       └─ o->ClearUpdateMask(false)         // wipe dirty bits
```

### `OBJECT_UPDATE_FLAGS` (per-block movement flags, `UpdateData.h:36`)

| Flag | Meaning |
|---|---|
| `UPDATEFLAG_SELF` | Update describes the receiving player |
| `UPDATEFLAG_TRANSPORT` | Object is a transport (path progress field follows) |
| `UPDATEFLAG_HAS_TARGET` | Pack-guid of current target follows |
| `UPDATEFLAG_LOWGUID` | Append low-guid as `uint32` |
| `UPDATEFLAG_LIVING` | Full `MovementInfo` + speeds + (optional) spline follows |
| `UPDATEFLAG_STATIONARY_POSITION` | x/y/z/o, no movement |
| `UPDATEFLAG_VEHICLE` | vehicle id + orientation follows |
| `UPDATEFLAG_POSITION` | path-progress + position pair (transports) |
| `UPDATEFLAG_ROTATION` | packed quaternion (GameObject) |

`m_updateFlag` is set in each leaf constructor (e.g. `Player` adds `UPDATEFLAG_SELF | UPDATEFLAG_LIVING | UPDATEFLAG_HAS_POSITION`).

## Hooks & extension points

- Modules generally do NOT add new update fields — the `*_END` constants are baked into the WotLK 3.3.5a wire protocol and the `*UpdateFieldFlags[]` arrays are sized to them. Synthesising a new field would also require client-side support.
- Module-private state attaches via `Object::CustomData` (`Object.h:231`, a `DataMap`), not via the values array. Paragon uses this. See [`../../05-modules.md`](../../05-modules.md).
- To force a single field to be re-sent (e.g. after a server-side recomputation), call `Object::ForceValuesUpdateAtIndex(uint32 i)` (`Object.h:199`). Marks the bit dirty without changing the value.
- Adding a `UF_FLAG_*`-style visibility predicate would mean editing `Object::GetUpdateFieldData` (`Object.cpp:548`) and the per-class flag arrays in `UpdateFieldFlags.cpp` — not module-friendly.

## Cross-references

- Engine-side: [`01-object-hierarchy.md`](./01-object-hierarchy.md) (the `Build*` virtuals overridden per leaf), [`02-object-guid.md`](./02-object-guid.md) (`OBJECT_FIELD_GUID` is the first slot), [`../network/02-worldpacket.md`](../network/02-worldpacket.md) (`SMSG_UPDATE_OBJECT` framing), [`../maps/05-visibility.md`](../maps/05-visibility.md) (when objects (dis)appear from a target), [`../handlers/02-movement-handler.md`](../handlers/02-movement-handler.md) (movement block back-channel)
- Project-side: [`../../05-modules.md`](../../05-modules.md) (`CustomData` usage)
- External: Doxygen `classUpdateData`, `classUpdateMask`
