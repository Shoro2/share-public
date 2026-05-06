# handlers — Character handler

> Char enum / create / delete / login / customize / rename / faction-change opcodes. The login path uses an async `LoginQueryHolder` to load a player's full record before instantiating `Player` — see [`../database/04-query-holders.md`](../database/04-query-holders.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Handlers/CharacterHandler.cpp:64` | `LoginQueryHolder` (extends `CharacterDatabaseQueryHolder`) |
| `src/server/game/Handlers/CharacterHandler.cpp:78` | `LoginQueryHolder::Initialize` (binds ~33 prepared statements) |
| `src/server/game/Handlers/CharacterHandler.cpp:228` | `WorldSession::HandleCharEnum` (callback for the async query) |
| `src/server/game/Handlers/CharacterHandler.cpp:256` | `WorldSession::HandleCharEnumOpcode` |
| `src/server/game/Handlers/CharacterHandler.cpp:273` | `WorldSession::HandleCharCreateOpcode` |
| `src/server/game/Handlers/CharacterHandler.cpp:609` | `WorldSession::HandleCharDeleteOpcode` |
| `src/server/game/Handlers/CharacterHandler.cpp:670` | `WorldSession::HandlePlayerLoginOpcode` (entry) |
| `src/server/game/Handlers/CharacterHandler.cpp:789` | `WorldSession::HandlePlayerLoginFromDB` (after holder completes) |
| `src/server/game/Handlers/CharacterHandler.cpp:1128` | `WorldSession::HandlePlayerLoginToCharInWorld` (re-attach to existing in-world player) |
| `src/server/game/Handlers/CharacterHandler.cpp:1261` | `WorldSession::HandlePlayerLoginToCharOutOfWorld` |
| `src/server/game/Handlers/CharacterHandler.cpp:1344` | `WorldSession::HandleCharRenameOpcode` |
| `src/server/game/Handlers/CharacterHandler.cpp:1377` | `WorldSession::HandleCharRenameCallBack` |
| `src/server/game/Handlers/CharacterHandler.cpp:1429` | `WorldSession::HandleSetPlayerDeclinedNames` |
| `src/server/game/Handlers/CharacterHandler.cpp:1508` | `WorldSession::HandleAlterAppearance` |
| `src/server/game/Handlers/CharacterHandler.cpp:1580` | `WorldSession::HandleRemoveGlyph` |
| `src/server/game/Handlers/CharacterHandler.cpp:1620` | `WorldSession::HandleCharCustomize` (entry) |
| `src/server/game/Handlers/CharacterHandler.cpp:1660` | `WorldSession::HandleCharCustomizeCallback` |
| `src/server/game/Handlers/CharacterHandler.cpp:1751` | `WorldSession::HandleEquipmentSetSave` |
| `src/server/game/Handlers/CharacterHandler.cpp:1822` | `WorldSession::HandleEquipmentSetDelete` |
| `src/server/game/Handlers/CharacterHandler.cpp:1832` | `WorldSession::HandleEquipmentSetUse` |
| `src/server/game/Handlers/CharacterHandler.cpp:1925` | `WorldSession::HandleCharFactionOrRaceChange` (entry; serves both `CMSG_CHAR_FACTION_CHANGE` and `CMSG_CHAR_RACE_CHANGE`) |
| `src/server/game/Handlers/CharacterHandler.cpp:1965` | `WorldSession::HandleCharFactionOrRaceChangeCallback` |

## Opcodes covered

Status legend: `A` = `STATUS_AUTHED` (pre-login, on character screen), `L` = `STATUS_LOGGEDIN`. Process legend: `TU` = `PROCESS_THREADUNSAFE`, `IP` = `PROCESS_INPLACE`. Source of truth for the registration: `src/server/game/Server/Protocol/Opcodes.cpp:185`–`1403`.

### Char-screen lifecycle (STATUS_AUTHED)

| Opcode | Handler | Purpose |
|---|---|---|
| `CMSG_CHAR_ENUM` (`0x037`) | `HandleCharEnumOpcode` | List characters on the account; async DB query feeds `HandleCharEnum`. |
| `CMSG_CHAR_CREATE` (`0x036`) | `HandleCharCreateOpcode` | Create a new character (race / class / appearance validation, `OnPlayerCreate`). |
| `CMSG_CHAR_DELETE` (`0x038`) | `HandleCharDeleteOpcode` | Delete a character; fires `OnPlayerDelete` / `OnPlayerFailedDelete`. |
| `CMSG_PLAYER_LOGIN` (`0x03D`) | `HandlePlayerLoginOpcode` | Begin world entry — see "Flow" below. |
| `CMSG_CHAR_RENAME` (`0x2C7`) | `HandleCharRenameOpcode` | Apply a rename. |
| `CMSG_SET_PLAYER_DECLINED_NAMES` (`0x419`) | `HandleSetPlayerDeclinedNames` | Russian declined names. |
| `CMSG_CHAR_CUSTOMIZE` (`0x473`) | `HandleCharCustomize` | Re-customise appearance after a paid token. |
| `CMSG_CHAR_FACTION_CHANGE` (`0x4D9`) | `HandleCharFactionOrRaceChange` | Faction change (paid). |
| `CMSG_CHAR_RACE_CHANGE` (`0x4F8`) | `HandleCharFactionOrRaceChange` | Race change (paid). |
| `CMSG_READY_FOR_ACCOUNT_DATA_TIMES` (`0x4FF`) | `HandleReadyForAccountDataTimes` | Account-data sync — actually lives in `MiscHandler.cpp`; cross-link [`06-misc-handler.md`](./06-misc-handler.md). |

### In-world character settings (STATUS_LOGGEDIN)

| Opcode | Handler | Purpose |
|---|---|---|
| `CMSG_TUTORIAL_FLAG` (`0x0FE`) | `HandleTutorialFlag` | Mark tutorial bit shown. |
| `CMSG_TUTORIAL_CLEAR` (`0x0FF`) | `HandleTutorialClear` | Clear all tutorial bits. |
| `CMSG_TUTORIAL_RESET` (`0x100`) | `HandleTutorialReset` | Reset to default. |
| `CMSG_SET_FACTION_ATWAR` (`0x125`) | `HandleSetFactionAtWar` | Toggle "at war" on a faction. |
| `CMSG_SET_FACTION_CHEAT` (`0x126`) | `HandleSetFactionCheat` | (cheat-only entry, normally NULL). |
| `CMSG_SET_FACTION_INACTIVE` (`0x317`) | `HandleSetFactionInactiveOpcode` | Mark a faction as inactive in the rep pane. |
| `CMSG_SET_WATCHED_FACTION` (`0x318`) | `HandleSetWatchedFactionOpcode` | Watched faction shown on the XP bar. |
| `CMSG_SHOWING_HELM` (`0x2B9`) | `HandleShowingHelmOpcode` | Toggle helm rendering. |
| `CMSG_SHOWING_CLOAK` (`0x2BA`) | `HandleShowingCloakOpcode` | Toggle cloak rendering. |
| `CMSG_ALTER_APPEARANCE` (`0x426`) | `HandleAlterAppearance` | Barbershop apply. |
| `CMSG_REMOVE_GLYPH` (`0x48A`) | `HandleRemoveGlyph` | Unsocket a glyph. |
| `CMSG_EQUIPMENT_SET_SAVE` (`0x4BD`) | `HandleEquipmentSetSave` | Save a saved-equipment-set slot. |
| `CMSG_DELETEEQUIPMENT_SET` (`0x13E`) | `HandleEquipmentSetDelete` | Delete a saved set. |
| `CMSG_EQUIPMENT_SET_USE` (`0x4D5`) | `HandleEquipmentSetUse` | Equip a saved set (issues swap operations). |

For the canonical opcode list: [`../network/03-opcodes.md`](../network/03-opcodes.md).

## Key concepts

- **Legit-character set**: `_legitCharacters` is populated by `HandleCharEnum` and checked in `HandlePlayerLoginOpcode` to prevent logging in with a character that does not belong to the account (`CharacterHandler.cpp:688`).
- **`LoginQueryHolder`**: a `CharacterDatabaseQueryHolder` of size `MAX_PLAYER_LOGIN_QUERY` that batches all character-load prepared statements (auras, spells, quest status, inventory, mail, achievements, glyphs, talents, skills, …) into one async DB round-trip. See `CharacterHandler.cpp:78` for the full list.
- **Two login paths**: if the player is already in-world from a prior session (DC, reconnect), `HandlePlayerLoginOpcode` re-attaches via `HandlePlayerLoginToCharInWorld` (no DB load). Otherwise the standard `LoginQueryHolder` async path is taken and `HandlePlayerLoginFromDB` constructs a fresh `Player` and calls `Player::LoadFromDB`.
- **Faction/race change & customize callbacks**: each takes a `std::shared_ptr<…Info>` captured into a `WithPreparedCallback` so the originally-submitted packet data survives the async hop.
- **Equipment sets** are stored in the `character_equipmentsets` table; they are the WotLK in-game gear-manager (the saved-set system, not the user-side mod-equipment-template).

## Flow / data shape

`HandlePlayerLoginOpcode` (cold path, no in-world player to reattach):

```
client CMSG_PLAYER_LOGIN
        │
        ▼
HandlePlayerLoginOpcode  (CharacterHandler.cpp:670)
        │  — IsLegitCharacterForAccount?
        │  — duplicate session check
        │  — m_playerLoading = true
        ▼
LoginQueryHolder::Initialize  (binds ~33 stmts)
        │
        ▼
CharacterDatabase.DelayQueryHolder  ──► async worker
        │
        ▼  (callback)
HandlePlayerLoginFromDB  (CharacterHandler.cpp:789)
        │  — new Player(this)
        │  — Player::LoadFromDB(guid, holder)
        │  — sScriptMgr->OnPlayerLogin / OnPlayerFirstLogin
        ▼
SendInitialPackets / world enter
```

The in-world reattach path (`HandlePlayerLoginToCharInWorld`, `:1128`) skips `LoginQueryHolder` entirely — the existing `Player*` is just rebound to the new session.

## Hooks & extension points

Fired from this handler file:

- `ScriptMgr::CanAccountCreateCharacter` (`:435`) — veto in `HandleCharCreateOpcode`.
- `ScriptMgr::OnPlayerCreate` (`:587`) — after `Player::SaveToDB`.
- `ScriptMgr::OnPlayerDelete`, `OnPlayerFailedDelete` (`:620`–`:661`).
- `ScriptMgr::OnPlayerFfaPvpStateUpdate` (`:960`).
- `ScriptMgr::OnPlayerLogin`, `OnPlayerFirstLogin` (`:1117`, `:1122`).

`PlayerScript` declarations live in `src/server/game/Scripting/ScriptDefines/PlayerScript.h`. See [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md) for class taxonomy and [`../../05-modules.md`](../../05-modules.md) for which modules use them.

## Cross-references

- Engine-side: [`../network/05-worldsession.md`](../network/05-worldsession.md) (dispatch loop), [`../network/03-opcodes.md`](../network/03-opcodes.md) (opcode list), [`../entities/04-player.md`](../entities/04-player.md) (`Player::LoadFromDB`), [`../database/04-query-holders.md`](../database/04-query-holders.md) (async holder mechanism), [`../database/02-prepared-statements.md`](../database/02-prepared-statements.md) (`CHAR_SEL_*`).
- Project-side: [`../../05-modules.md`](../../05-modules.md) for `OnPlayerLogin` / `OnPlayerFirstLogin` consumers.
- External: Doxygen `classWorldSession` (`HandlePlayerLoginOpcode`), `classLoginQueryHolder`.
