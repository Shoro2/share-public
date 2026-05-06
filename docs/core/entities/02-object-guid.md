# entities — Object GUID

> 64-bit object identifier with embedded high-tag and (optional) entry, plus the variable-length packed form used on the wire. Cross-links: [`01-object-hierarchy.md`](./01-object-hierarchy.md), [`03-update-fields.md`](./03-update-fields.md), [`../network/02-worldpacket.md`](../network/02-worldpacket.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Object/ObjectGuid.h:30` | `enum TypeID` (8 client-visible types) |
| `src/server/game/Entities/Object/ObjectGuid.h:44` | `enum TypeMask` (bitmask form, used by `Object::isType`) |
| `src/server/game/Entities/Object/ObjectGuid.h:57` | `enum class HighGuid` — high 16 bits of the raw `uint64` |
| `src/server/game/Entities/Object/ObjectGuid.h:74-106` | `ObjectGuidTraits<HighGuid>` + `GUID_TRAIT_GLOBAL` / `GUID_TRAIT_MAP_SPECIFIC` macros |
| `src/server/game/Entities/Object/ObjectGuid.h:117` | `class ObjectGuid` — `uint64` wrapper |
| `src/server/game/Entities/Object/ObjectGuid.h:120` | `static ObjectGuid const Empty` (zero) |
| `src/server/game/Entities/Object/ObjectGuid.h:124-128` | `Create<HighGuid>(...)` factory templates (compile-time switch on `Global`/`MapSpecific`) |
| `src/server/game/Entities/Object/ObjectGuid.h:142-150` | `GetRawValue / GetHigh / GetEntry / GetCounter` accessors |
| `src/server/game/Entities/Object/ObjectGuid.h:162-178` | `Is*()` family (`IsCreature, IsPlayer, IsItem, IsAnyTypeCreature, …`) |
| `src/server/game/Entities/Object/ObjectGuid.h:180-201` | `static GetTypeId(HighGuid) -> TypeID` mapping |
| `src/server/game/Entities/Object/ObjectGuid.h:215-237` | `HasEntry(HighGuid)` — controls whether the middle 24 bits are entry or counter |
| `src/server/game/Entities/Object/ObjectGuid.h:262` | `class PackedGuid` (variable-length wire form, 1-9 bytes) |
| `src/server/game/Entities/Object/ObjectGuid.h:280` | `class ObjectGuidGeneratorBase` |
| `src/server/game/Entities/Object/ObjectGuid.h:296` | `template<HighGuid> class ObjectGuidGenerator` (sequence per type) |
| `src/server/game/Entities/Object/ObjectGuid.h:310-314` | `ByteBuffer` `<<` / `>>` for full and packed forms |
| `src/server/game/Entities/Object/ObjectGuid.cpp:26` | `GetTypeName(HighGuid)` (string form for logs) |
| `src/server/game/Entities/Object/ObjectGuid.cpp:47` | `ToString()` |
| `src/server/game/Entities/Object/ObjectGuid.cpp:93` | `HandleCounterOverflow(HighGuid)` — fatal error + shutdown |

## Key concepts

- **Raw layout (`uint64`)** — high 16 bits = `HighGuid`, the rest depends on whether the high tag carries an entry:
  - `HasEntry()` = true (`HighGuid::Unit, Pet, Vehicle, GameObject, Transport`) → `[high:16][entry:24][counter:24]`
  - `HasEntry()` = false (`HighGuid::Player, Item, DynamicObject, Corpse, Mo_Transport, Instance, Group`) → `[high:16][unused:16 zero][counter:32]`
  - Packed in `ObjectGuid` constructor at `ObjectGuid.h:131-133`. The non-entry counter range is therefore much larger (`0xFFFFFFFF` vs `0x00FFFFFF`, see `GetMaxCounter` at `ObjectGuid.h:152`).
- **`HighGuid` constants** — values mirror Blizz client (`ObjectGuid.h:59-72`):
  - `Player = 0x0000`, `Item / Container = 0x4000`, `GameObject = 0xF110`, `Transport = 0xF120`, `Unit = 0xF130`, `Pet = 0xF140`, `Vehicle = 0xF150`, `DynamicObject = 0xF100`, `Corpse = 0xF101`, `Mo_Transport = 0x1FC0`, `Instance = 0x1F40`, `Group = 0x1F50`.
- **Global vs map-specific** — `ObjectGuidTraits<H>::Global / ::MapSpecific` (`ObjectGuid.h:75-79`) decides which `Create<>` overload is callable; map-specific guids (`Unit`, `Pet`, `Vehicle`, `GameObject`, `Transport`, `DynamicObject`, `Corpse`) take an `entry`. Player/Item/Group/Instance/Mo_Transport are global.
- **Two `Create<>` templates** (`ObjectGuid.h:124-128`):
  ```cpp
  ObjectGuid::Create<HighGuid::Player>(lowGuid);                 // global
  ObjectGuid::Create<HighGuid::Unit>(creatureEntry, spawnId);    // map-specific
  ```
  SFINAE on `ObjectGuidTraits<H>::Global` enforces correctness at compile time. Calling the wrong overload won't link.
- **`PackedGuid`** — wire-efficient form: 1 mask byte indicating which of the 8 raw bytes are non-zero, followed only by the non-zero bytes. Buffer is at least 9 bytes (`PACKED_GUID_MIN_BUFFER_SIZE`, `ObjectGuid.h:260`). See [`../network/02-worldpacket.md`](../network/02-worldpacket.md) for `ByteBuffer::appendPackGUID` (called from the `<<` operator at `ObjectGuid.h:313`).
- **GUID generators** — one per `HighGuid` for global types; `ObjectGuidGeneratorBase::HandleCounterOverflow` (`ObjectGuid.cpp:93`) logs `LOG_ERROR("entities.object", ...)` and aborts the server. Map-specific guids are generated from the per-`Map` generator (see [`../maps/`](../maps/00-index.md)). Held by `ObjectMgr` for global types — see [`10-object-mgr.md`](./10-object-mgr.md) under `GenerateAuctionID / GenerateMailID / GenerateCreatureSpawnId / GenerateGameObjectSpawnId`.
- **`LowType`** is `uint32` (`ObjectGuid.h:122`). Most APIs and DB columns use `LowType` (the counter portion) as the persistent id.

## Flow / data shape

### Construction & inspection

```cpp
// Build a player guid from a DB lowguid
ObjectGuid g = ObjectGuid::Create<HighGuid::Player>(lowGuid);

// Build a creature guid (needs entry + spawnId since Unit::HasEntry == true)
ObjectGuid g = ObjectGuid::Create<HighGuid::Unit>(entry, spawnId);

// Inspect
g.GetRawValue();       // uint64
g.GetHigh();           // HighGuid::Player
g.GetEntry();          // 0 if HasEntry()==false, else 24-bit entry
g.GetCounter();        // ObjectGuid::LowType (24 or 32 bits)
g.GetTypeId();         // -> TYPEID_PLAYER (via static map)
g.IsAnyTypeCreature(); // Unit | Pet | Vehicle
g.IsAnyTypeGameObject(); // GameObject | Transport | Mo_Transport
```

### Wire (un)packing

```cpp
// Send: full 8-byte guid
WorldPacket data(SMSG_X);
data << objectGuid;           // ByteBuffer&::operator<< for ObjectGuid (ObjectGuid.h:310)

// Send: packed (variable length 1-9 bytes)
data << objectGuid.WriteAsPacked();   // PackedGuid form

// Receive: packed
ObjectGuid read;
data >> read.ReadAsPacked();  // PackedGuidReader (ObjectGuid.h:111)
```

`Object::GetPackGUID()` (`Object.h:116`) returns a cached `PackedGuid&` — used by every `Build*UpdateBlock` to avoid re-packing the same source GUID per frame.

### Helpers

- `ObjectGuid::Empty` — comparison sentinel (`!objectGuid` is shorthand for `IsEmpty()`).
- `ObjectGuid::ToString()` — `"Type: <name>… "` for log lines.
- `ObjectGuid::GetTypeName(HighGuid)` — string for the high-tag (`"Player"`, `"Creature"`, …).
- `std::hash<ObjectGuid>` specialisation at `ObjectGuid.h:318` — guids are usable as `unordered_map`/`unordered_set` keys.

### `HighGuid` ↔ `TypeID` mapping (from `ObjectGuid.h:180-198`)

| HighGuid | TypeID |
|---|---|
| `Item`, `Container` | `TYPEID_ITEM` |
| `Unit`, `Pet`, `Vehicle` | `TYPEID_UNIT` |
| `Player` | `TYPEID_PLAYER` |
| `GameObject`, `Mo_Transport` | `TYPEID_GAMEOBJECT` |
| `DynamicObject` | `TYPEID_DYNAMICOBJECT` |
| `Corpse` | `TYPEID_CORPSE` |
| `Instance`, `Group` | `TYPEID_OBJECT` (server-only, never exposed) |

Note: `Transport` (`0xF120`, GO-type-transport) maps via the `default:` arm (`TYPEID_OBJECT`) but instances live in the GameObject tree — the function predates the `Transport` HighGuid being added to GO sub-types. In practice transports are always queried via `IsTransport()` / `IsAnyTypeGameObject()`.

## Hooks & extension points

— None. `ObjectGuid` is value-semantic and final; modules consume it but don't extend it. New high-tags would require coordinated changes in `Object::_Create`, `ObjectMgr::SetHighestGuids`, and the wire protocol — out of scope for module authors.

## Cross-references

- Engine-side: [`01-object-hierarchy.md`](./01-object-hierarchy.md), [`03-update-fields.md`](./03-update-fields.md), [`10-object-mgr.md`](./10-object-mgr.md) (`GenerateXxxId` for global counters), [`../network/02-worldpacket.md`](../network/02-worldpacket.md) (`ByteBuffer::appendPackGUID`)
- Project-side: [`../../06-custom-ids.md`](../../06-custom-ids.md) (custom NPC/item entries that flow through `ObjectGuid::Create<HighGuid::Unit>`)
- External: Doxygen `classObjectGuid`, `classPackedGuid`
