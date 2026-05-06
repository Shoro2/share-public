# entities — Player tour

> Pointer-style table of `Player.h` (3069 lines): each documented section maps to its line range plus the kind of methods inside, so an AI can jump straight to the cluster it needs. Cross-links: [`01-object-hierarchy.md`](./01-object-hierarchy.md), [`../handlers/01-character-handler.md`](../handlers/01-character-handler.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Player/Player.h:1083` | `class Player : public Unit, public GridObject<Player>` |
| `src/server/game/Entities/Player/Player.cpp:157` | `Player::Player(WorldSession*)` ctor |
| `src/server/game/Entities/Player/Player.cpp:484` | `Player::Create(LowType, CharacterCreateInfo*)` |
| `src/server/game/Entities/Player/PlayerStorage.cpp:4980` | `Player::LoadFromDB(ObjectGuid, CharacterDatabaseQueryHolder const&)` |
| `src/server/game/Entities/Player/PlayerStorage.cpp:7119` | `Player::SaveToDB(bool create, bool logout)` |
| `src/server/game/Entities/Player/PlayerUpdates.cpp:53` | `Player::Update(uint32 p_time)` (per-tick driver) |
| `src/server/game/Entities/Player/Player.cpp` (~17000 lines), `PlayerStorage.cpp`, `PlayerQuest.cpp`, `PlayerGossip.cpp`, `PlayerMisc.cpp`, `PlayerUpdates.cpp` | Implementation split |
| `src/server/game/Entities/Player/PlayerTaxi.{h,cpp}` | `class PlayerTaxi` |
| `src/server/game/Entities/Player/SocialMgr.{h,cpp}` | `class PlayerSocial`, friend list |
| `src/server/game/Entities/Player/CinematicMgr.{h,cpp}` | `class CinematicMgr` |
| `src/server/game/Entities/Player/TradeData.{h,cpp}` | `class TradeData` (open-trade window state) |
| `src/server/game/Entities/Player/KillRewarder.{h,cpp}` | `class KillRewarder` (XP/honor pipeline) |

## Section map (by line range in `Player.h`)

The header has explicit `/*** … SYSTEM ***/` banners; this is the directory.

| Lines | Section | Representative methods |
|---|---|---|
| 1090–1247 | Lifecycle, flags, taxi, pet, chat, GM/dev flags | `Create`, `Update`, `TeleportTo`, `SetGameMaster`, `SummonPet`, `Say/Yell/Whisper/TextEmote`, `m_taxi.ActivateTaxiPathTo` |
| 1248–1422 | **STORAGE SYSTEM** (inventory, bags, equip, bank, buyback) | `GetItemByPos`, `CanStoreItem`, `StoreNewItem`, `EquipItem`, `BankItem`, `DestroyItem`, `SwapItem`, `SetVisibleItemSlot`, `IsBankPos / IsEquipmentPos / IsInventoryPos` |
| 1423–1436 | **GOSSIP SYSTEM** | `PrepareGossipMenu`, `SendPreparedGossip`, `OnGossipSelect` plumbing |
| 1437–1577 | **QUEST SYSTEM** | `CanTakeQuest`, `AddQuest`, `RewardQuest`, `FailQuest`, `KilledMonsterCredit`, quest-slot getters/setters writing to `PLAYER_QUEST_LOG_*` |
| 1578–1590 | **LOAD SYSTEM** | `LoadFromDB(guid, holder)` (paired with [`../database/04-query-holders.md`](../database/04-query-holders.md)), `Initialize`, static `LoadPositionFromDB` |
| 1591–1670 | **SAVE SYSTEM** | `SaveToDB(create, logout)`, `SaveInventoryAndGoldToDB`, static `Customize`, `SavePositionInDB`, `DeleteFromDB`, money helpers (`GetMoney/SetMoney/ModifyMoney`) |
| 1671–2165 | **MAILED ITEMS SYSTEM** + spell book + cooldown + glyph + talent | `_SaveMail`, spell-book (`learnSpell`, `removeSpell`, `HasActiveSpell`), spell modifier list, glyph slots, talent reset, action bar, `SendInitialActionButtons` |
| 2166–2282 | **PVP SYSTEM** | duel state, honor calc, FFA-PvP, sanctuary, dishonorable kills, `_pvpInfo` |
| 2283–2328 | **BATTLEGROUND SYSTEM** (player side) | `GetBattleground`, `SetBattlegroundId`, `LeaveBattleground`, BG queue id state |
| 2329–2336 | **OUTDOOR PVP SYSTEM** | `GetOutdoorPvP`, capture-point hooks |
| 2337–2343 | **ENVIRONMENTAL SYSTEM** | underwater, lava, slime damage timers |
| 2344–2363 | **FLOOD FILTER SYSTEM** | chat-spam throttle counters |
| 2364–2464 | **VARIOUS SYSTEMS** | rest, achievement (`AchievementMgr* m_achievementMgr`), reputation (`ReputationMgr* m_reputationMgr`), arena teams, currency, weather, areatrigger, transport |
| 2465–2497 | **INSTANCE SYSTEM** | `GetInstanceBind`, `BindToInstance`, `IsLockedToInstance`, instance reset |
| 2498–2586 | **GROUP SYSTEM** | `SetGroup`, `GetGroup`, `GetSubGroup`, raid update mask, group invite state |
| 2587–2585+ | **private** member declarations |

> The section banners after `private:` (2680+) declare protected/private storage backing the public APIs above (e.g. `_SaveSpells`, `_SaveQuestStatus`, `_LoadInventory`, `_LoadAuras`).

## Sub-objects owned by `Player` (composition)

| Member (declared near) | Type | Purpose |
|---|---|---|
| `m_taxi` (`Player.h:1158`) | `PlayerTaxi` | Known taxi nodes + active flight path |
| `m_social` (`Player.h:1156` getter) | `PlayerSocial*` | Friend / ignore list, owned by `SocialMgr` |
| `_cinematicMgr` (`Player.cpp:157` ctor init) | `CinematicMgr` | Active cinematic state |
| `m_petStable` | `std::unique_ptr<PetStable>` | Stable + current-pet metadata; see `Player::GetPetStable` (`Player.h:1221`) |
| `m_achievementMgr` | `AchievementMgr*` | Achievement criteria tracking |
| `m_reputationMgr` | `ReputationMgr*` | Faction standings |
| `m_trade` | `TradeData*` | Open trade window |
| `m_session` | `WorldSession*` | Owning network session |
| `m_movementInfo` (inherited from `WorldObject`) | `MovementInfo` | Last-received client move |
| `m_mover` | `Unit*` | Server-side authority for movement (self by default; vehicle/charm switches it) |

## Key concepts

- **Two-phase login.** The `Player*` is constructed AFTER the `LoginQueryHolder` async fetch completes, then `Player::LoadFromDB(guid, holder)` consumes the holder's results in one synchronous pass. See [`../handlers/01-character-handler.md`](../handlers/01-character-handler.md) for the holder layout.
- **`m_uint32Values` is the source of truth** for everything visible to the client (level, gold, equipment slots, quest log, faction standings cap). Sub-managers feed into it via setters from `Object`. Money is a single `PLAYER_FIELD_COINAGE` uint32 (`Player.h:1623`).
- **Quest log** lives entirely in update fields: `PLAYER_QUEST_LOG_1_1` + `slot * MAX_QUEST_OFFSET + offset` (id / state / counts / time). The C++ helpers (`GetQuestSlotQuestId`, `SetQuestSlotState`, …) at `Player.h:1502-1534` are the only correct way to manipulate them.
- **Inventory addressing**: a 16-bit `pos = (bag << 8) | slot`. `bag = INVENTORY_SLOT_BAG_0` (255) means the player itself; other values are bag containers. Static predicates `IsInventoryPos/IsEquipmentPos/IsBankPos/IsBagPos` (`Player.h:1275-1281`) gate which storage region a position belongs to.
- **`CharacterDatabaseTransaction` for save**. `SaveToDB(create, logout)` (`PlayerStorage.cpp:7119`) builds one transaction containing inventory, gold, auras, spells, quest status, glyphs, talents, achievements, reputation, mails, equipment-set rows; commits via `CharacterDatabase.CommitTransaction(trans)` (see [`../database/05-transactions.md`](../database/05-transactions.md)).
- **`m_mover`** — set by `Player::SetMover(Unit*)`. Movement opcodes ([`../handlers/02-movement-handler.md`](../handlers/02-movement-handler.md)) operate on `m_mover` rather than `this`, which is how vehicles, charm, and possess all redirect input.

## Flow / data shape

### Per-tick update (cold path: player in world)

```
WorldSession::Update(diff)
  └─ … process queued opcodes …
Player::Update(p_time)             (PlayerUpdates.cpp:53)
  ├─ Unit::Update(p_time)          // auras, combat, spline, regen
  ├─ UpdateMirrorTimers            // breath, fatigue, environment
  ├─ UpdateNextMailTimeAndUnreads
  ├─ UpdateLFGChannel              // zone-based chat reattach
  ├─ Regenerate*                   // health/mana/runes/energy
  ├─ check pending logout, save, instance reset
  └─ trigger Heartbeat() (every HEARTBEAT_INTERVAL = 5.2 s)
```

### Save (logout / periodic)

```
Player::SaveToDB(create=false, logout=true)        // PlayerStorage.cpp:7119
  └─ SaveToDB(trans, create, logout)               // :7128
       ├─ static SavePositionInDB
       ├─ characters row UPDATE (level, money, race, class, …)
       ├─ _SaveInventory(trans)
       ├─ _SaveQuestStatus(trans)
       ├─ _SaveSpells(trans), _SaveSpellCooldowns
       ├─ _SaveAuras
       ├─ _SaveSkills
       ├─ _SaveActions
       ├─ _SaveGlyphs, _SaveTalents
       ├─ _SaveSocial (delegates to PlayerSocial)
       ├─ achievementMgr->SaveToDB(trans)
       ├─ reputationMgr->SaveToDB(trans)
       └─ CharacterDatabase.CommitTransaction(trans)
```

All `_Save*` use prepared statements from `CHAR_DEL_*` + `CHAR_INS_*` pairs (delete-then-insert pattern). Statement enum: `CharacterDatabase.h:23` ([`../database/02-prepared-statements.md`](../database/02-prepared-statements.md)).

## Hooks & extension points

The `PlayerScript` class fires from across `Player.cpp` and the handler files. Most-used hooks (declared in `src/server/game/Scripting/ScriptDefines/PlayerScript.h`):

| Hook | Where fired (representative call site) |
|---|---|
| `OnPlayerLogin / OnPlayerFirstLogin` | `CharacterHandler.cpp:1117, 1122` |
| `OnPlayerLogout / OnPlayerSave` | `Player.cpp` (logout path) / `PlayerStorage.cpp` (`SaveToDB` exit) |
| `OnPlayerLevelChanged` | `Player::GiveLevel` |
| `OnPlayerMoneyChanged` | `Player::ModifyMoney` |
| `OnPlayerLootItem` | `LootHandler.cpp` |
| `OnPlayerMapChanged` | `Player::TeleportTo` |
| `OnCheckReagent / OnConsumeReagent` (custom this fork) | spell cast + cost path; see `azerothcore-wotlk/functions.md` |
| `CanAccountCreateCharacter` | `CharacterHandler.cpp:435` |

Modules that attach state to a `Player` without subclassing put it in `Object::CustomData` (`Object.h:231`) — Paragon does this for account-wide stat points; see [`../../05-modules.md`](../../05-modules.md).

## Cross-references

- Engine-side: [`../handlers/01-character-handler.md`](../handlers/01-character-handler.md) (login/create/delete/customize), [`../handlers/02-movement-handler.md`](../handlers/02-movement-handler.md) (movement opcodes that target `m_mover`), [`../handlers/03-item-handler.md`](../handlers/03-item-handler.md), [`../handlers/04-spell-handler.md`](../handlers/04-spell-handler.md), [`../database/04-query-holders.md`](../database/04-query-holders.md), [`../database/05-transactions.md`](../database/05-transactions.md), [`07-item.md`](./07-item.md), [`08-pet-vehicle.md`](./08-pet-vehicle.md), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md)
- Project-side: [`../../05-modules.md`](../../05-modules.md) (`PlayerScript` consumers), [`../../09-db-tables.md`](../../09-db-tables.md) (`characters`, `character_inventory`, `character_queststatus`, `character_spell`, `character_aura`, `character_talent`, `character_glyphs`, `character_action`, `character_reputation`, `character_achievement`, `character_skills`, `character_social`, `character_equipmentsets`)
- External: Doxygen `classPlayer`
