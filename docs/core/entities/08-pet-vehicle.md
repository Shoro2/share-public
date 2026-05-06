# entities — Pet, Vehicle, Totem, DynamicObject

> The "specialised Unit" sub-tree (`TempSummon → Minion → Guardian → Pet`, plus `Totem` and `Puppet`), the `Vehicle` passenger-seat behavior, and `DynamicObject` (server-side spell area anchor). Cross-links: [`05-creature.md`](./05-creature.md), [`01-object-hierarchy.md`](./01-object-hierarchy.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Creature/TemporarySummon.h:24` | `enum SummonerType` (CREATURE / GAMEOBJECT / MAP) |
| `src/server/game/Entities/Creature/TemporarySummon.h:32` | `struct TempSummonData` |
| `src/server/game/Entities/Creature/TemporarySummon.h:41` | `struct GameObjectSummonData` |
| `src/server/game/Entities/Creature/TemporarySummon.h:49` | `class TempSummon : public Creature` |
| `src/server/game/Entities/Creature/TemporarySummon.h:86` | `class Minion : public TempSummon` |
| `src/server/game/Entities/Creature/TemporarySummon.h:105` | `class Guardian : public Minion` |
| `src/server/game/Entities/Creature/TemporarySummon.h:124` | `class Puppet : public Minion` |
| `src/server/game/Entities/Pet/Pet.h:40` | `class Pet : public Guardian` |
| `src/server/game/Entities/Pet/PetDefines.h:30` | `enum PetType { SUMMON_PET=0, HUNTER_PET=1, MAX_PET_TYPE=4 }` |
| `src/server/game/Entities/Pet/PetDefines.h:40` | `enum PetSaveMode : int8` (`AS_DELETED=-1, AS_CURRENT=0, FIRST_STABLE_SLOT=1, LAST_STABLE_SLOT=4, NOT_IN_SLOT=100`) |
| `src/server/game/Entities/Pet/PetDefines.h:49-69` | `enum HappinessState / PetSpellState / PetSpellType` |
| `src/server/game/Entities/Pet/Pet.h:28` | `struct PetSpell` (active state, spell-state, type) |
| `src/server/game/Entities/Pet/Pet.cpp:216` | `Pet::LoadPetFromDB(owner, petEntry, petnumber, current, healthPct, fullMana)` |
| `src/server/game/Entities/Pet/Pet.cpp:502` | `Pet::SavePetToDB(PetSaveMode mode)` |
| `src/server/game/Entities/Pet/Pet.cpp:599` | `Pet::DeleteFromDB(LowType guidlow)` (static) |
| `src/server/game/Entities/Pet/Pet.cpp:652` | `Pet::Update(uint32 diff)` |
| `src/server/game/Entities/Pet/Pet.cpp:881` | `Pet::Remove(PetSaveMode mode, bool returnreagent)` |
| `src/server/game/Entities/Vehicle/Vehicle.h:27` | `class Vehicle : public TransportBase` |
| `src/server/game/Entities/Vehicle/VehicleDefines.h:38` | `enum VehicleFlags` (NO_STRAFE, NO_JUMPING, FULLSPEEDTURNING, …) |
| `src/server/game/Entities/Vehicle/VehicleDefines.h:50` | `enum VehicleSpells` (`VEHICLE_SPELL_RIDE_HARDCODED = 46598`) |
| `src/server/game/Entities/Vehicle/VehicleDefines.h:59` | `enum class VehicleExitParameters` |
| `src/server/game/Entities/Vehicle/VehicleDefines.h:85` | `struct VehicleSeatAddon` |
| `src/server/game/Entities/Vehicle/Vehicle.cpp:73` | `Vehicle::Install()` (called from `Unit::CreateVehicleKit`) |
| `src/server/game/Entities/Vehicle/Vehicle.cpp:88` | `Vehicle::InstallAllAccessories(bool evading)` |
| `src/server/game/Entities/Vehicle/Vehicle.cpp:275` | `Vehicle::InstallAccessory(entry, seatId, minion, type, summonTime)` |
| `src/server/game/Entities/Vehicle/Vehicle.cpp:319` | `Vehicle::AddPassenger(Unit*, int8 seatId)` |
| `src/server/game/Entities/Vehicle/Vehicle.cpp:467` | `Vehicle::RemovePassenger(Unit*)` |
| `src/server/game/Entities/Totem/Totem.h:23` | `enum TotemType { PASSIVE, ACTIVE, STATUE }` |
| `src/server/game/Entities/Totem/Totem.h:50` | `class Totem : public Minion` |
| `src/server/game/Entities/DynamicObject/DynamicObject.h:27` | `enum DynamicObjectType { PORTAL, AREA_SPELL, FARSIGHT_FOCUS }` |
| `src/server/game/Entities/DynamicObject/DynamicObject.h:34` | `class DynamicObject : public WorldObject, public GridObject<DynamicObject>, …` |

## Comparison table

| Class | Base | TypeID | Persisted? | Owner | Lifetime | Typical use |
|---|---|---|---|---|---|---|
| `TempSummon` | `Creature` | `TYPEID_UNIT` | No (overrides `SaveToDB` to no-op) | `m_summonerGUID` | `m_timer` (despawn type) | Generic `WorldObject::SummonCreature` |
| `Minion` | `TempSummon` | `TYPEID_UNIT` | No | `m_owner` (`Unit*`) | follows owner | warlock pets (controlled), totems |
| `Guardian` | `Minion` | `TYPEID_UNIT` | No | owner | controlled by `m_owner` | water elemental, hunter eagle minions |
| `Pet` | `Guardian` | `TYPEID_UNIT` | YES (`character_pet`) | `Player` only | persisted across logout | hunter / warlock pet |
| `Totem` | `Minion` | `TYPEID_UNIT` | No | shaman | `m_duration` ms | shaman totem |
| `Puppet` | `Minion` | `TYPEID_UNIT` | No | player (charm-style) | spell duration | mind-control style possession |
| `Vehicle` | `TransportBase` (NOT `Object`) | n/a | No | wraps a `Unit*` host | host's lifetime | passenger seat manager attached to a `Creature`/`Player` |
| `DynamicObject` | `WorldObject` | `TYPEID_DYNAMICOBJECT` | No | spell caster | `_duration` ms (or aura's) | persistent area spell anchor (Blizzard, Consecration), farsight focus |

## Key concepts

- **Summon factory dispatch.** `Map::SummonCreature(...)` (`Object.cpp:2188`) reads the `SummonPropertiesEntry` (DBC `SummonProperties.dbc`) to choose which `TempSummon` subclass to instantiate. Slot/Type bits in the entry route to `Pet`, `Guardian`, `Minion`, `Totem`, `Puppet`, or plain `TempSummon`. Then `summon->InitStats(duration)` and `summon->InitSummon()` finish setup.
- **`TempSummonType`** (declared `Object.h:47`) drives despawn behavior: `TIMED_OR_DEAD_DESPAWN`, `TIMED_OR_CORPSE_DESPAWN`, `TIMED_DESPAWN`, `DEAD_DESPAWN`, `MANUAL_DESPAWN`, etc. Stored on `TempSummon::m_type`.
- **`Pet` is the only persistent summon.** It overrides `Creature::SaveToDB` to `ABORT()` (`Pet.h:167-174`) and uses its own `SavePetToDB(mode)` against `character_pet`. It can be in current slot (`PET_SAVE_AS_CURRENT`), one of 4 stable slots, or "not in slot". `LoadPetFromDB` is async-friendly via the player login holder.
- **`m_petStable`** lives on `Player` (`Player.h:1221`) as `std::unique_ptr<PetStable>` — caches per-account pet metadata so the chooser UI works without a round-trip.
- **`Vehicle` is a behavior, not an entity.** No GUID, no update fields. `Unit::CreateVehicleKit(uint32 vehicleId, uint32 creatureEntry)` constructs one and friend-exposes its private ctor (`Vehicle.h:63`); `Unit::RemoveVehicleKit()` tears it down. Public access via `unit->GetVehicleKit()` and `unit->GetVehicle()` (the seat the unit is sitting on).
- **Seat semantics.** `Vehicle::Seats` is a `SeatMap` (`SeatMap.h`) keyed by seat id. Each entry holds a `VehicleSeatEntry const*` (DBC) plus `PassengerInfo` (guid + selectability). `AddPassenger(passenger, seatId=-1)` (`-1` = next free). `EjectPassenger(...)` is the violent removal; `RemovePassenger(...)` is voluntary dismount.
- **Vehicle accessories** — sub-units automatically summoned into seats. Defined in `vehicle_template_accessory` and `vehicle_accessory` tables (loaded `ObjectMgr.cpp:3968, 4024`); installed by `InstallAllAccessories` on enter / reset.
- **`Totem`** = `Minion` with a duration timer + restricted stats updates. Most stat-recompute virtuals are no-ops (`Totem.h:64-71`). Two named instances (`SENTRY_TOTEM_ENTRY = 3968`, `EARTHBIND_TOTEM_ENTRY = 2630`) are special-cased.
- **`DynamicObject`** wraps a server-side spell-area anchor. It has its own GUID (`HighGuid::DynamicObject`), is grid-resident (the spell visual + per-tick re-target loop runs against it), and can be attached to an `Aura` via `SetAura` (`DynamicObject.h:51`). When used as `FARSIGHT_FOCUS` it relays the player's view to a distant point (warlock Eye of Kilrogg).

## Flow / data shape

### Pet load on player login

```
HandlePlayerLoginFromDB                        // ../handlers/01-character-handler.md
  └─ Player::LoadFromDB(guid, holder)
       └─ PetStable* stable = … (loaded via holder)
       └─ if currentPet present:
             pet = new Pet(player, type)
             pet->LoadPetFromDB(player, entry, number, current=true)   // Pet.cpp:216
                 ├─ map->AddToMap(pet)
                 ├─ _LoadAuras / _LoadSpells / _LoadSpellCooldowns
                 └─ player->SetMinion(pet, true)
```

### Vehicle ride (Player mounts a vehicle Creature)

```
caster casts SPELL_RIDE_HARDCODED (46598) on target Unit
  └─ Spell::EffectActivateRune (or enter-vehicle effect)
       └─ Player::EnterVehicle(target, seatId)
            └─ target->GetVehicleKit()->AddPassenger(player, seatId)   // Vehicle.cpp:319
                 ├─ assign Seats[seatId].Passenger.Guid = player->GetGUID()
                 ├─ player->m_vehicle = vehicleKit;  player->SetMover(vehicleKit->GetBase())
                 ├─ apply seat-flag movement restrictions
                 └─ relocate player to seat-relative position
```

`m_mover` swap on the player is what redirects movement opcodes to the vehicle (see [`../handlers/02-movement-handler.md`](../handlers/02-movement-handler.md) and [`04-player.md`](./04-player.md) "m_mover").

### DynamicObject lifecycle (area spell)

```
Spell::EffectPersistentAreaAura
  └─ new DynamicObject() + CreateDynamicObject(guid, caster, spellId, pos, radius, AREA_SPELL)
       └─ map->AddToMap(dynObj)
       └─ Aura::Create(...) attached, SetAura(aura)
DynamicObject::Update(p_time)                  // DynamicObject.h:46
  ├─ aura->Update(diff)                        // re-target nearby units
  └─ _duration -= diff;  if (_duration <= 0): Remove();
```

## Hooks & extension points

- `PetScript` (declared in `Scripting/ScriptDefines/PetScript.h`): `OnInitStatsForLevel`, `OnUpdate`, `OnSummon`, `OnRelease`. Most modules attach pet-related logic via `PlayerScript::OnPetAddedToWorld` (custom hook in this fork — see `azerothcore-wotlk/functions.md`).
- Vehicle: no top-level script; vehicles use `CreatureScript` AI on the host `Creature` and react to seat events by overriding `CreatureAI::PassengerBoarded(passenger, seatId, apply)`.
- Totem: scripted as ordinary `CreatureScript` AI; behavior is gated by `Totem::Update` (`Totem.h:55`).
- DynamicObject: rarely scripted directly; the owning `Aura` carries the scripted behavior. See [`../spells/03-aura-system.md`](../spells/03-aura-system.md).

## Cross-references

- Engine-side: [`05-creature.md`](./05-creature.md) (base class, summon factory), [`01-object-hierarchy.md`](./01-object-hierarchy.md) (placement in tree), [`04-player.md`](./04-player.md) (`m_petStable`, `m_mover`, vehicle ride), [`../spells/03-aura-system.md`](../spells/03-aura-system.md) (DynamicObject's aura), [`../handlers/04-spell-handler.md`](../handlers/04-spell-handler.md) (`CMSG_PET_*`, `CMSG_PLAYER_VEHICLE_ENTER` paths)
- Project-side: [`../../09-db-tables.md`](../../09-db-tables.md) (`character_pet`, `character_pet_declinedname`, `pet_aura`, `pet_spell`, `pet_spell_cooldown`, `vehicle_accessory`, `vehicle_template_accessory`, `vehicle_seat_addon`)
- External: Doxygen `classPet`, `classVehicle`, `classTotem`, `classDynamicObject`, `classTempSummon`
