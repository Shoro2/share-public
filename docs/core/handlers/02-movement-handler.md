# handlers — Movement handler

> All `MSG_MOVE_*` heartbeat / direction packets, every speed-change ACK, teleport ACKs, transport boarding, time-sync, knock-back ACK, and the anti-cheat hook surface — funnelled through `HandleMovementOpcodes` and a few specialist methods.

## Critical files

| File | Role |
|---|---|
| `src/server/game/Handlers/MovementHandler.cpp:45` | `WorldSession::HandleMoveWorldportAckOpcode` (entry) |
| `src/server/game/Handlers/MovementHandler.cpp:51` | `WorldSession::HandleMoveWorldportAck` (real worker — far-teleport finaliser) |
| `src/server/game/Handlers/MovementHandler.cpp:274` | `WorldSession::HandleMoveTeleportAck` (near-teleport ACK) |
| `src/server/game/Handlers/MovementHandler.cpp:344` | `WorldSession::HandleMovementOpcodes` (catch-all for ~30 `MSG_MOVE_*` opcodes) |
| `src/server/game/Handlers/MovementHandler.cpp:398` | `WorldSession::SynchronizeMovement` (uses `_timeSyncClockDelta`) |
| `src/server/game/Handlers/MovementHandler.cpp:412` | `WorldSession::HandleMoverRelocation` (transport / vehicle boarding bookkeeping) |
| `src/server/game/Handlers/MovementHandler.cpp:518` | `WorldSession::VerifyMovementInfo` (anti-cheat veto) |
| `src/server/game/Handlers/MovementHandler.cpp:601` | `WorldSession::ProcessMovementInfo` (composite verify + apply) |
| `src/server/game/Handlers/MovementHandler.cpp:665` | `WorldSession::HandleForceSpeedChangeAck` (8 speed-change opcodes share this) |
| `src/server/game/Handlers/MovementHandler.cpp:767` | `WorldSession::HandleSetActiveMoverOpcode` |
| `src/server/game/Handlers/MovementHandler.cpp:782` | `WorldSession::HandleMoveNotActiveMover` |
| `src/server/game/Handlers/MovementHandler.cpp:803` | `WorldSession::HandleMountSpecialAnimOpcode` |
| `src/server/game/Handlers/MovementHandler.cpp:811` | `WorldSession::HandleMoveKnockBackAck` |
| `src/server/game/Handlers/MovementHandler.cpp:851` | `WorldSession::HandleSummonResponseOpcode` |
| `src/server/game/Handlers/MovementHandler.cpp:875` | `WorldSession::HandleMoveTimeSkippedOpcode` |
| `src/server/game/Handlers/MovementHandler.cpp:907` | `WorldSession::HandleTimeSyncResp` |
| `src/server/game/Handlers/MovementHandler.cpp:978` | `WorldSession::HandleMoveRootAck` (also serves unroot) |

`HandleMoveSplineDoneOpcode` is in `TaxiHandler.cpp:203`. `HandleMoveFlagChangeOpcode` (hover, water-walk, feather-fall, gravity, fly ACKs) lives in `MiscHandler.cpp:1505`.

## Opcodes covered

`PROCESS_THREADSAFE` for everything except worldport/teleport ACKs and `MOUNT_SPECIAL_ANIM`/`SUMMON_RESPONSE`/`SET_ACTIVE_MOVER` (those are `THREADUNSAFE`). Source: `Opcodes.cpp:312`–`1434`.

### `HandleMovementOpcodes` (one method, many opcodes)

All client direction / state changes route through this single dispatcher and end with a `mover->SendMessageToSet`. ~30 opcodes use it; representative entries:

| Opcode | Purpose |
|---|---|
| `MSG_MOVE_START_FORWARD` (`0x0B5`) | Begin forward movement. |
| `MSG_MOVE_START_BACKWARD` (`0x0B6`) | Begin backward. |
| `MSG_MOVE_STOP` (`0x0B7`) | Stop translation. |
| `MSG_MOVE_START_STRAFE_LEFT` / `_RIGHT` (`0x0B8`/`0x0B9`) | Strafe. |
| `MSG_MOVE_STOP_STRAFE` (`0x0BA`) | Stop strafe. |
| `MSG_MOVE_JUMP` (`0x0BB`) | Jump (also fires `AnticheatHandleDoubleJump`). |
| `MSG_MOVE_START_TURN_LEFT` / `_RIGHT` / `STOP_TURN` (`0x0BC`–`0x0BE`) | Yaw turn. |
| `MSG_MOVE_START_PITCH_UP` / `_DOWN` / `STOP_PITCH` (`0x0BF`–`0x0C1`) | Pitch (vehicles, flight). |
| `MSG_MOVE_SET_RUN_MODE` / `WALK_MODE` (`0x0C2`/`0x0C3`) | Walk-toggle. |
| `MSG_MOVE_FALL_LAND` (`0x0C9`) | Land — feeds `Player::UpdateFallInformationIfNeed`. |
| `MSG_MOVE_START_SWIM` / `STOP_SWIM` (`0x0CA`/`0x0CB`) | Swim state. |
| `MSG_MOVE_SET_FACING` / `SET_PITCH` (`0x0DA`/`0x0DB`) | Facing/pitch resync. |
| `MSG_MOVE_HEARTBEAT` (`0x0EE`) | Idle heartbeat (~ every 500 ms). |
| `CMSG_MOVE_FALL_RESET` (`0x2CA`) | Reset fall info, no rebroadcast. |
| `CMSG_MOVE_CHNG_TRANSPORT` (`0x38D`) | Switch transports, no rebroadcast. |
| `CMSG_MOVE_SET_FLY` (`0x346`) | Activate fly state. |
| `MSG_MOVE_START_ASCEND` / `STOP_ASCEND` / `START_DESCEND` (`0x359`/`0x35A`/`0x3A7`) | Vertical flight. |

### Specialist handlers

| Opcode | Handler | Purpose |
|---|---|---|
| `MSG_MOVE_WORLDPORT_ACK` (`0x0DC`) | `HandleMoveWorldportAckOpcode` (`STATUS_TRANSFER`) | Far-teleport finaliser; loads dest map, calls `Map::AddPlayerToMap`. |
| `MSG_MOVE_TELEPORT_ACK` (`0x0C7`) | `HandleMoveTeleportAck` | Near-teleport ACK. |
| `CMSG_FORCE_RUN_SPEED_CHANGE_ACK` (`0x0E3`) and 7 siblings | `HandleForceSpeedChangeAck` | Speed change confirmation; mismatch → kick or correct. Switch on opcode at `:717`. |
| `CMSG_FORCE_MOVE_ROOT_ACK` (`0x0E9`) / `_UNROOT_ACK` (`0x0EB`) | `HandleMoveRootAck` | Root/unroot confirmation. |
| `CMSG_MOVE_KNOCK_BACK_ACK` (`0x0F0`) | `HandleMoveKnockBackAck` | Knock-back confirmation, applies new vector. |
| `CMSG_MOVE_HOVER_ACK` (`0x0F6`), `_FEATHER_FALL_ACK` (`0x2CF`), `_WATER_WALK_ACK` (`0x2D0`), `_GRAVITY_DISABLE/ENABLE_ACK` (`0x4CF`/`0x4D1`), `MOVE_SET_CAN_FLY_ACK` (`0x345`) | `HandleMoveFlagChangeOpcode` (in `MiscHandler.cpp`) | Generic flag-bit ACK. |
| `CMSG_MOVE_SET_COLLISION_HGT_ACK` (`0x517`) | `HandleForceSpeedChangeAck` | Reuses the same handler — see `:701`. |
| `CMSG_SET_ACTIVE_MOVER` (`0x26A`) | `HandleSetActiveMoverOpcode` | Mind-control / vehicle-seat possession switch. |
| `CMSG_MOVE_NOT_ACTIVE_MOVER` (`0x2D1`) | `HandleMoveNotActiveMover` | Drop possession. |
| `CMSG_MOUNTSPECIAL_ANIM` (`0x171`) | `HandleMountSpecialAnimOpcode` | `/mountspecial`. |
| `CMSG_SUMMON_RESPONSE` (`0x2AC`) | `HandleSummonResponseOpcode` | Summon-accept. |
| `CMSG_MOVE_TIME_SKIPPED` (`0x2CE`) | `HandleMoveTimeSkippedOpcode` | Notify of client-side time gap. |
| `CMSG_TIME_SYNC_RESP` (`0x391`) | `HandleTimeSyncResp` | Reply to server-issued `SMSG_TIME_SYNC_REQ`; updates `_timeSyncClockDelta`. |

For the canonical opcode list with hex values, see [`../network/03-opcodes.md`](../network/03-opcodes.md).

## Key concepts

- **`MovementInfo`**: parsed by `WorldSession::ReadMovementInfo` (declared in `WorldSession.h`); contains flags, position, transport, fall, swim/jump info. Written back by `WriteMovementInfo`.
- **Mover**: `_player->m_mover` is the unit whose movement the client is currently driving — usually the player, but can be a vehicle, a possessed unit, or a player under mind-control. Movement opcodes that reference a different GUID than the current mover are silently dropped (`:366`).
- **Time sync**: server periodically sends `SMSG_TIME_SYNC_REQ` (in `WorldSession::Update` at `WorldSession.cpp:548`); client replies with `CMSG_TIME_SYNC_RESP`. The 64-bit delta is stored in `_timeSyncClockDelta` and applied to incoming `MovementInfo.time` by `SynchronizeMovement` (`:398`).
- **Worldport vs teleport**: far teleports cross map boundaries and require the destination map to be created/loaded — `HandleMoveWorldportAck` does the heavy lifting (`Map::CreateMap`, `Map::AddPlayerToMap`). Near teleports stay on the same map and only update the player's position.
- **Anti-cheat surface**: `VerifyMovementInfo` and `ProcessMovementInfo` call into `sScriptMgr->Anticheat*` hooks (see hooks below).
- **Speed-change ACK race**: client sends one ACK per forced speed change but bundles run/mounted into a single packet — `HandleForceSpeedChangeAck` decrements `_player->m_forced_speed_changes[...]` and only validates the last one (`:743`).

## Flow / data shape

```
client sends MSG_MOVE_*
        │
        ▼
HandleMovementOpcodes  (MovementHandler.cpp:344)
        │  guid match?
        ▼
ReadMovementInfo      (parses position, flags, transport, fall)
        │
        ▼
ProcessMovementInfo   (:601)
        │  ├─► VerifyMovementInfo  (:518) ─► Anticheat hooks
        │  └─► HandleMoverRelocation  (:412) ─► transport bookkeeping, UpdatePosition
        │
        ▼
mover->SendMessageToSet(...)   (rebroadcast to grid)
```

Far teleport:

```
GM port / quest / spell ─► Player::TeleportTo
        │  SetSemaphoreTeleportFar
        │  SendNewWorld          (server-issued NEW_WORLD)
        ▼
client replies MSG_MOVE_WORLDPORT_ACK  (STATUS_TRANSFER opcode)
        │
        ▼
HandleMoveWorldportAck  (:51)
        │  ResetMap → SetMap → AddPlayerToMap
        ▼
SendInitialPacketsAfterAddToMap
```

## Hooks & extension points

Anti-cheat and movement hooks fired from this handler:

- `sScriptMgr->AnticheatUpdateMovementInfo` (`:524`, `:544`, `:575`, `:586`).
- `sScriptMgr->AnticheatHandleDoubleJump` (`:554`).
- `sScriptMgr->AnticheatCheckMovementInfo` (`:562`).
- `sScriptMgr->AnticheatSetJumpingbyOpcode` (`:624`, `:634`).
- `sScriptMgr->AnticheatSetUnderACKmount` (`:462`, `:733`).
- `sScriptMgr->OnPlayerMove` (`:647`).

These belong to `MovementHandlerScript` / `PlayerScript`. See [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md). `HandleMoveFlagChangeOpcode` adds `sScriptMgr->AnticheatSetCanFlybyServer` (`MiscHandler.cpp:1531`).

## Cross-references

- Engine-side: [`../network/05-worldsession.md`](../network/05-worldsession.md) (dispatch + `_timeSyncTimer`), [`../network/03-opcodes.md`](../network/03-opcodes.md) (opcode list), [`../movement/01-motion-master.md`](../movement/01-motion-master.md), [`../movement/03-spline.md`](../movement/03-spline.md), [`../entities/09-corpse-transport.md`](../entities/09-corpse-transport.md) (`Transport::AddPassenger`), [`../maps/01-map-hierarchy.md`](../maps/01-map-hierarchy.md) (worldport target map).
- Project-side: anti-cheat hooks consumed by external modules — see [`../../05-modules.md`](../../05-modules.md).
- External: Doxygen `classWorldSession` (`HandleMovementOpcodes`, `HandleMoveWorldportAck`).
