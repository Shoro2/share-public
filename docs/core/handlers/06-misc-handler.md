# handlers — Misc handler

> The catch-all bucket: logout flow, repop / spirit healer, gossip selection, who, area triggers, action buttons / bars, account-data sync, world-state UI timer, instance difficulty, far-sight, complaint / bug report, played time, inspect, missile trajectory, world-teleport (`.tele`), realm-split, hearth-and-resurrect, set-title, cinematic complete, move-flag ACKs, … ~50 unrelated handlers in one file (`MiscHandler.cpp` is ~1775 lines).

> **Ping** is *not* here — it is intercepted at the socket layer (`WorldSocket::HandlePing`, `WorldSocket.cpp:734`) before any opcode dispatch. **Time-sync response** is in `MovementHandler.cpp:907`.

## Critical files (grouped)

### Logout

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:425` | `WorldSession::HandleLogoutRequestOpcode` (begin 20s logout timer) |
| `src/server/game/Handlers/MiscHandler.cpp:485` | `WorldSession::HandlePlayerLogoutOpcode` (instant logout) |
| `src/server/game/Handlers/MiscHandler.cpp:489` | `WorldSession::HandleLogoutCancelOpcode` |

### Death / corpse / resurrection

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:58` | `WorldSession::HandleRepopRequestOpcode` (release spirit) |
| `src/server/game/Handlers/MiscHandler.cpp:642` | `WorldSession::HandleReclaimCorpseOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:677` | `WorldSession::HandleResurrectResponseOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1649` | `WorldSession::HandleAreaSpiritHealerQueryOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1672` | `WorldSession::HandleAreaSpiritHealerQueueOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1695` | `WorldSession::HandleHearthAndResurrect` (priest spell 8690 follow-up) |

### Gossip / NPC interaction

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:88` | `WorldSession::HandleGossipSelectOptionOpcode` (NPC / GO / item / menu) |

### World query / discovery

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:219` | `WorldSession::HandleWhoOpcode` (uses `sWhoListCacheMgr`) |
| `src/server/game/Handlers/MiscHandler.cpp:986` | `WorldSession::HandleInspectOpcode` (gear/talent inspect) |
| `src/server/game/Handlers/MiscHandler.cpp:1028` | `WorldSession::HandleInspectHonorStatsOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1090` | `WorldSession::HandleWhoisOpcode` (GM-only) |
| `src/server/game/Handlers/MiscHandler.cpp:1599` | `WorldSession::HandleQueryInspectAchievements` |
| `src/server/game/Handlers/MiscHandler.cpp:1196` | `WorldSession::HandleFarSightOpcode` (camera / spy) |

### Action UI

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:908` | `WorldSession::HandleSetActionButtonOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:961` | `WorldSession::HandleSetActionBarToggles` |
| `src/server/game/Handlers/MiscHandler.cpp:588` | `WorldSession::HandleLoadActionsSwitchSpec` (callback after spec switch) |

### Account-data sync (STATUS_AUTHED)

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:819` | `WorldSession::HandleUpdateAccountData` (zlib-decompress saved variables) |
| `src/server/game/Handlers/MiscHandler.cpp:872` | `WorldSession::HandleRequestAccountData` |
| `src/server/game/Handlers/MiscHandler.cpp:1633` | `WorldSession::HandleReadyForAccountDataTimes` |

### Area / zone / state

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:530` | `WorldSession::HandleZoneUpdateOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:543` | `WorldSession::HandleSetSelectionOpcode` (target unit) |
| `src/server/game/Handlers/MiscHandler.cpp:569` | `WorldSession::HandleStandStateChangeOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:700` | `WorldSession::HandleAreaTriggerOpcode` (trigger entry, tavern / dungeon port) |
| `src/server/game/Handlers/MiscHandler.cpp:509` | `WorldSession::HandleTogglePvP` |
| `src/server/game/Handlers/MiscHandler.cpp:1623` | `WorldSession::HandleWorldStateUITimerUpdate` |

### Instance difficulty

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:1264` | `WorldSession::HandleResetInstancesOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1277` | `WorldSession::HandleSetDungeonDifficultyOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1327` | `WorldSession::HandleSetRaidDifficultyOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1716` | `WorldSession::HandleInstanceLockResponse` |

### Misc

| File | Role |
|---|---|
| `src/server/game/Handlers/MiscHandler.cpp:625` | `WorldSession::HandleBugOpcode` (`/bug`) |
| `src/server/game/Handlers/MiscHandler.cpp:949` | `WorldSession::HandleCompleteCinematic` |
| `src/server/game/Handlers/MiscHandler.cpp:955` | `WorldSession::HandleNextCinematicCamera` |
| `src/server/game/Handlers/MiscHandler.cpp:977` | `WorldSession::HandlePlayedTime` |
| `src/server/game/Handlers/MiscHandler.cpp:1060` | `WorldSession::HandleWorldTeleportOpcode` (`.tele`) |
| `src/server/game/Handlers/MiscHandler.cpp:1150` | `WorldSession::HandleComplainOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1177` | `WorldSession::HandleRealmSplitOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1245` | `WorldSession::HandleSetTitleOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1484` | `WorldSession::HandleCancelMountAuraOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1505` | `WorldSession::HandleMoveFlagChangeOpcode` (hover/water-walk/feather-fall/gravity/fly ACKs) |
| `src/server/game/Handlers/MiscHandler.cpp:1569` | `WorldSession::HandleRequestPetInfo` |
| `src/server/game/Handlers/MiscHandler.cpp:1589` | `WorldSession::HandleSetTaxiBenchmarkOpcode` |
| `src/server/game/Handlers/MiscHandler.cpp:1733` | `WorldSession::HandleUpdateMissileTrajectory` |

DB-callback helpers: `HandleLoadActionsSwitchSpec` (`:588`), `HandleCharacterAuraFrozen` (`:599`).

## Opcodes covered

The "Critical files (grouped)" table above already maps every opcode to its handler — see `Opcodes.cpp:139`–`1410` for status/processing. Notable status assignments:

- `STATUS_AUTHED` (allowed at char screen): `CMSG_REQUEST_ACCOUNT_DATA`, `CMSG_UPDATE_ACCOUNT_DATA`, `CMSG_READY_FOR_ACCOUNT_DATA_TIMES`, `CMSG_REALM_SPLIT`, `CMSG_SET_ACTIONBAR_TOGGLES`.
- `STATUS_LOGGEDIN_OR_RECENTLY_LOGGOUT`: `CMSG_LOGOUT_CANCEL` only — handles in-flight cancel after `_player` was nulled.
- All others: `STATUS_LOGGEDIN`.

Notable threading:

- `PROCESS_THREADSAFE` (run inside `Map::Update`): `CMSG_REPOP_REQUEST`, `CMSG_RESURRECT_RESPONSE`, `CMSG_RECLAIM_CORPSE`, `CMSG_HEARTH_AND_RESURRECT`, `CMSG_WHO`, `CMSG_SET_SELECTION`, `CMSG_NEXT_CINEMATIC_CAMERA`, `CMSG_COMPLETE_CINEMATIC`, all `CMSG_MOVE_*_ACK` flag opcodes routed to `HandleMoveFlagChangeOpcode`.
- `PROCESS_THREADUNSAFE` (run inside `World::UpdateSessions`): logout, gossip select, account data, instance difficulty, far-sight, world teleport, complain, who-is, request-pet-info, missile trajectory.
- `PROCESS_INPLACE`: inspect, query achievements, area trigger, zone update, set title, played time, world-state UI timer, cancel-mount-aura.

For the canonical opcode list with hex values and exact status/processing per slot: [`../network/03-opcodes.md`](../network/03-opcodes.md).

## Key concepts

- **Logout transaction**: `HandleLogoutRequestOpcode` (`:425`) starts a 20s timer (immediate in resting / GM / dead state). The actual save / world-leave happens in `WorldSession::LogoutPlayer` (in `WorldSession.cpp`, not this file). `HandleLogoutCancelOpcode` accepts state `STATUS_LOGGEDIN_OR_RECENTLY_LOGGOUT` so a packet that arrives just after `_player == nullptr` still aborts the timer cleanly.
- **Gossip dispatch tree**: `HandleGossipSelectOptionOpcode` resolves the source GUID type (creature / GO / item / player-menu) and fires the chain
  `Unit::AI::sGossipSelect(Code) → ScriptMgr::OnGossipSelect(Code) → Player::OnGossipSelect`. A `false` return from the script chain falls through to the default handler. Coded options append a string captured before the dispatch (`:172`).
- **Area triggers** (`HandleAreaTriggerOpcode`, `:700`): radius check, then in order: tavern handler → script `OnAreaTrigger` → quest progress → battleground area trigger → outdoor PvP → `AreaTriggerTeleport` lookup. Teleport may be denied via `Map::PlayerCannotEnter`.
- **Account data**: 8 typed slots (per-character + per-account), zlib-compressed JSON-like blobs that hold UI variables (chat config, raid frames, addon settings).
- **Who list**: served from a snapshot in `sWhoListCacheMgr` — the `Update()` thread refreshes it periodically so `HandleWhoOpcode` is read-only and `THREADSAFE`.
- **Far-sight**: `Player::SetViewpoint` switches the client camera to a non-player object (Eye of Kilrogg, mind-vision target, BG spectator).
- **`HandleMoveFlagChangeOpcode`** is dispatched here despite belonging logically to movement — the file boundary is purely historical.

## Flow / data shape

Logout (interactive):

```
client CMSG_LOGOUT_REQUEST
        │
        ▼
HandleLogoutRequestOpcode  (:425)
        │  in combat? eligible? resting? GM?
        │  set m_logoutTimer = 20s   (or 0 immediate)
        │  SMSG_LOGOUT_RESPONSE  (status code)
        ▼
WorldSession::Update tick(s) ─► WorldSession::LogoutPlayer  (in WorldSession.cpp)
        │  Player::SaveToDB
        │  remove from map / world
        │  SMSG_LOGOUT_COMPLETE
```

Gossip select on a creature:

```
client CMSG_GOSSIP_SELECT_OPTION (guid, menuId, optionId, [code])
        │
        ▼
HandleGossipSelectOptionOpcode  (:88)
        │  guid kind switch (creature/GO/item/player-menu)
        │  removeFakeDeath
        │  unit->AI()->sGossipSelect(player, menuId, optionId)
        │  if (!sScriptMgr->OnGossipSelect(...))
        │      Player::OnGossipSelect(unit, optionId, menuId)  // default
```

## Hooks & extension points

- `sScriptMgr->OnGossipSelect` / `OnGossipSelectCode` (`:177`–`:214`).
- `sScriptMgr->OnPlayerGossipSelect` / `OnPlayerGossipSelectCode` (`:191`, `:214`).
- `sScriptMgr->OnAreaTrigger` (`:736`).
- `sScriptMgr->OnPlayerFfaPvpStateUpdate` (`:754`).
- `sScriptMgr->AnticheatSetCanFlybyServer` (`:1531`).

`PlayerScript`/`AreaTriggerScript`/`CreatureScript` definitions: `src/server/game/Scripting/ScriptDefines/`. See [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).

## Cross-references

- Engine-side: [`../network/03-opcodes.md`](../network/03-opcodes.md), [`../network/05-worldsession.md`](../network/05-worldsession.md) (`LogoutPlayer`, time-sync timer), [`../entities/04-player.md`](../entities/04-player.md) (`Player::OnGossipSelect`, `SaveToDB`), [`../entities/09-corpse-transport.md`](../entities/09-corpse-transport.md) (`Corpse`), [`../instances/01-instance-save.md`](../instances/01-instance-save.md) (difficulty-switch), [`../maps/01-map-hierarchy.md`](../maps/01-map-hierarchy.md) (`Map::PlayerCannotEnter`).
- Project-side: [`../../05-modules.md`](../../05-modules.md) (modules using gossip/area-trigger hooks).
- External: Doxygen `classWorldSession`.
