# handlers — Handler registration & dispatch

> How `Opcodes.cpp` binds every `CMSG_*` / `MSG_*` to a `WorldSession::Handle*` method, what `STATUS_*` and `PROCESS_*` mean, and how `WorldSession::Update` routes packets to the right thread.

## Critical files

Registration & table (`src/server/game/Server/Protocol/`):

| File | Role |
|---|---|
| `Opcodes.h:1346` | `NUM_OPCODE_HANDLERS = NUM_MSG_TYPES`, `NULL_OPCODE = 0x0000` |
| `Opcodes.h:1354` | `enum SessionStatus` (`STATUS_AUTHED`, `LOGGEDIN`, `TRANSFER`, `LOGGEDIN_OR_RECENTLY_LOGGOUT`, `NEVER`, `UNHANDLED`) |
| `Opcodes.h:1364` | `enum PacketProcessing` (`PROCESS_INPLACE`, `THREADUNSAFE`, `THREADSAFE`) |
| `Opcodes.h:1374` | `class OpcodeHandler` (base — `Name`, `Status`) |
| `Opcodes.h:1384` | `class ClientOpcodeHandler` (adds `ProcessingPlace`, abstract `Call(WorldSession*, WorldPacket&)`) |
| `Opcodes.h:1402` | `class OpcodeTable` (~1356-entry array) |
| `Opcodes.h:1428` | `extern OpcodeTable opcodeTable;` |
| `Opcodes.cpp:25` | `template<class PacketClass, …> class PacketHandler` (typed packet) |
| `Opcodes.cpp:39` | `class PacketHandler<WorldPacket, …>` (raw-packet specialisation) |
| `Opcodes.cpp:51` | `OpcodeTable opcodeTable;` (single global instance) |
| `Opcodes.cpp:76` | `OpcodeTable::ValidateAndSetClientOpcode` (rejects duplicate / out-of-range / NULL) |
| `Opcodes.cpp:99` | `OpcodeTable::ValidateAndSetServerOpcode` (binds `Handle_ServerSide`) |
| `Opcodes.cpp:123` | `OpcodeTable::Initialize` — ~1100 lines of `DEFINE_HANDLER(...)` |
| `Opcodes.cpp:125` | `#define DEFINE_HANDLER(opcode, status, processing, handler)` |
| `Opcodes.cpp:128` | `#define DEFINE_SERVER_OPCODE_HANDLER(opcode, status)` (`static_assert` status ∈ {NEVER, UNHANDLED}) |
| `src/server/game/World/World.cpp:927` | `opcodeTable.Initialize();` — called once during world boot |

Dispatch (`src/server/game/Server/`):

| File | Role |
|---|---|
| `WorldSession.cpp:358` | `WorldSession::Update(diff, PacketFilter&)` — drains `_recvQueue` and dispatches |
| `WorldSession.cpp:410`–`486` | the `switch (opHandle->Status)` that gates dispatch on session state |
| `WorldSession.cpp:846` | `Handle_NULL` — sentinel for unimplemented opcodes |
| `WorldSession.cpp:852` | `Handle_EarlyProccess` — opcodes that must be handled by `WorldSocket` (e.g. PING) |
| `WorldSession.cpp:858` | `Handle_ServerSide` — fires if a server-side opcode arrives from the client |
| `WorldSession.cpp:864` | `Handle_Deprecated` — logs and drops |
| `WorldSession.h:284` | `class PacketFilter` (base) |
| `WorldSession.h:297` | `class MapSessionFilter` — used by `Map::Update` |
| `WorldSession.h:310` | `class WorldSessionFilter` — used by `World::UpdateSessions` |
| `WorldSession.cpp:63` | `MapSessionFilter::Process` — only `THREADSAFE` (or `INPLACE` while in-world) |
| `WorldSession.cpp:85` | `WorldSessionFilter::Process` — everything except `THREADSAFE`-while-in-world |

## How registration works

The whole binding is a single function — `OpcodeTable::Initialize()` in `Opcodes.cpp` — that consists of ~1100 lines of:

```cpp
DEFINE_HANDLER(CMSG_PLAYER_LOGIN,   STATUS_AUTHED,   PROCESS_THREADUNSAFE, &WorldSession::HandlePlayerLoginOpcode);
DEFINE_HANDLER(CMSG_CAST_SPELL,     STATUS_LOGGEDIN, PROCESS_THREADSAFE,   &WorldSession::HandleCastSpellOpcode);
DEFINE_SERVER_OPCODE_HANDLER(SMSG_AUTH_RESPONSE, STATUS_NEVER);
```

The macro (`Opcodes.cpp:125`) expands to a templated `ValidateAndSetClientOpcode<decltype(handler), handler>(opcode, #opcode, status, processing)`. The template deduces the *packet class* from the handler's parameter type: a handler taking `WorldPackets::Item::SwapItem&` is bound through the typed `PacketHandler` (`Opcodes.cpp:25`), which calls `nicePacket.Read()` before invoking the method. A handler taking the raw `WorldPacket&` uses the specialisation at `:39`, which forwards the packet untouched.

Validation in `ValidateAndSetClientOpcode` (`:76`):

- Rejects `NULL_OPCODE` (`0x0000`).
- Rejects opcodes ≥ `NUM_OPCODE_HANDLERS`.
- Refuses to overwrite a previously-set entry (logs an error).

`Initialize()` is invoked exactly once, from `World::SetInitialWorldSettings` at `World.cpp:927`. After that the table is read-only.

Server-side opcodes (`SMSG_*`) get bound to a sentinel handler `WorldSession::Handle_ServerSide` (`WorldSession.cpp:858`); receiving one from the client logs an error and drops the packet.

## SessionStatus gating

| Constant | Value | Required state | Used by |
|---|---|---|---|
| `STATUS_AUTHED` | 0 | Player authenticated, not in world (`_player == nullptr`); `m_inQueue == false` | char screen, account-data sync, realm-split |
| `STATUS_LOGGEDIN` | 1 | `_player != nullptr && _player->IsInWorld()` | the bulk of gameplay opcodes |
| `STATUS_TRANSFER` | 2 | `_player != nullptr && !_player->IsInWorld()` | `MSG_MOVE_WORLDPORT_ACK` |
| `STATUS_LOGGEDIN_OR_RECENTLY_LOGGOUT` | 3 | as `LOGGEDIN`, plus tolerance for in-flight packets just after logout | `CMSG_LOGOUT_CANCEL` |
| `STATUS_NEVER` | 4 | Opcode not accepted from client (deprecated / server-side) | every `SMSG_*`, all `*_CHEAT` opcodes |
| `STATUS_UNHANDLED` | 5 | Not yet implemented | placeholder rows |

Gating is enforced in `WorldSession::Update`'s big `switch` (`WorldSession.cpp:410`–`486`):

- `STATUS_LOGGEDIN`: drops the packet if `!_player`. If the player just logged out (`m_playerRecentlyLogout`), the packet is silently dropped without logging — assumed network lag.
- `STATUS_TRANSFER`: only dispatches if `_player && !_player->IsInWorld()`.
- `STATUS_AUTHED`: bypass if the session is in the auth queue (`m_inQueue`). `CMSG_CHAR_ENUM` clears `m_playerRecentlyLogout`.
- `STATUS_NEVER`: log "Received not allowed opcode …".
- `STATUS_UNHANDLED`: log debug "Received not handled opcode …".

`sScriptMgr->CanPacketReceive` is consulted before dispatch in every status branch (veto point).

## PacketProcessing & threading

| Constant | Where the handler runs | Latency | Use when |
|---|---|---|---|
| `PROCESS_INPLACE` | wherever the packet arrives — does not require map / world locks | lowest | trivial / read-only handlers (queries, item-text, hover-ack) |
| `PROCESS_THREADUNSAFE` | `World::UpdateSessions()` only — single-threaded relative to other sessions | medium | handlers that mutate global state (login, gossip dispatch, logout, auction, mail send) |
| `PROCESS_THREADSAFE` | `Map::Update()` (per-map thread) once player is in-world | lowest in-world | handlers that touch map / unit state (movement, cast, set-selection) |

The two filter classes pick which packets to drain on each tick:

- `MapSessionFilter::Process` (`WorldSession.cpp:63`): returns `true` only for `INPLACE` or for `THREADSAFE` while the player `IsInWorld()`. Used in `Map::Update`.
- `WorldSessionFilter::Process` (`WorldSession.cpp:85`): returns `true` for everything *except* `THREADSAFE` packets of an in-world player (those are handled by `MapSessionFilter`). Used in `World::UpdateSessions`.

Together they ensure each packet is processed exactly once and never under the wrong lock.

## Adding a new handler

Six steps. Search the codebase for any existing opcode (e.g. `CMSG_TUTORIAL_FLAG`) and copy the pattern.

1. **Add the opcode constant** in `src/server/game/Server/Protocol/Opcodes.h` (the `enum Opcodes` block; pick the next unused hex slot or the WotLK-known value).
2. **Declare the handler** on `WorldSession` in `src/server/game/Server/WorldSession.h` (in the appropriate "// XYZ handler" comment block).
3. **Implement** in the matching `*Handler.cpp` under `src/server/game/Handlers/` (or create one for a new subsystem). Convention: file groups by feature, method name `Handle<Name>Opcode` taking `WorldPacket&` (or a `WorldPackets::*` struct for newer opcodes).
4. **Register** with `DEFINE_HANDLER(...)` in the right slot of `OpcodeTable::Initialize` in `Opcodes.cpp` — preserve the `/*0xNNN*/` comment alignment.
5. **Pick status & processing**:
   - char screen / before login → `STATUS_AUTHED`.
   - in-world gameplay → `STATUS_LOGGEDIN`.
   - if it touches global state (DB, ObjectMgr, world singleton) → `PROCESS_THREADUNSAFE`.
   - if it touches map / unit state → `PROCESS_THREADSAFE`.
   - if it is read-only or send-only → `PROCESS_INPLACE`.
6. **CMakeLists**: no action required — handler files are globbed under `src/server/game/Handlers/`.

A new typed `WorldPackets::Foo::Bar` struct lives in `src/server/game/Server/Packets/`; for raw `WorldPacket` handlers, no extra step is needed.

## Sentinel handlers

| Sentinel | When fired | Effect |
|---|---|---|
| `Handle_NULL` | Opcode is registered with `&WorldSession::Handle_NULL` (slot intentionally unimplemented) | Logs `"Received unhandled opcode …"`. |
| `Handle_EarlyProccess` | Opcode should have been intercepted by `WorldSocket` before reaching `WorldSession` (e.g. `CMSG_PING`, `CMSG_AUTH_SESSION`) | Logs an error — indicates a bug in `WorldSocket::ReadDataHandler`. |
| `Handle_ServerSide` | A `SMSG_*` arrived from the client (cheat / corrupt) | Logs and drops. |
| `Handle_Deprecated` | Opcode is intentionally retired | Logs and drops. |

`CMSG_PING` itself never reaches `WorldSession` — it is handled in `src/server/game/Server/WorldSocket.cpp:734` (`WorldSocket::HandlePing`). Same for `CMSG_AUTH_SESSION` (auth handshake) — see [`../network/04-worldsocket.md`](../network/04-worldsocket.md).

## Flow / data shape

```
client packet ─► WorldSocket::ReadDataHandler  (network thread)
        │  if PING / AUTH_SESSION → handled here, return
        ▼
WorldSession::QueuePacket(packet)  ──► _recvQueue
        │
        ▼  (per-tick drain, in two phases)
World::UpdateSessions(diff)
        │  for each session:
        │      WorldSessionFilter filter(session)
        │      session->Update(diff, filter)
        │          for each packet matching WorldSessionFilter:
        │              switch (status) { dispatch via opHandle->Call(this, *packet); }
        │
Map::Update(diff)
        │  for each player in this map:
        │      MapSessionFilter filter(session)
        │      session->Update(diff, filter)
        │          for each packet matching MapSessionFilter:
        │              switch (status) { dispatch via opHandle->Call(this, *packet); }
```

DOS protection (`AntiDOS.EvaluateOpcode`) and the `MAX_PROCESSED_PACKETS_IN_SAME_WORLDSESSION_UPDATE = 150` (`WorldSession.cpp:379`) cap apply to both phases.

## Hooks & extension points

- `sScriptMgr->CanPacketReceive(WorldSession*, WorldPacket const&)` — fired before every `opHandle->Call` (4 call-sites between `:428` and `:472`). Veto by returning `false`.
- `sScriptMgr->CanPacketSend(WorldSession*, WorldPacket const&)` — fired in `WorldSession::SendPacket` (`:324`).

Both hooks are on `ServerScript` (`src/server/game/Scripting/ScriptDefines/ServerScript.h`). See [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).

## Cross-references

- Engine-side: [`../network/03-opcodes.md`](../network/03-opcodes.md) (full opcode list), [`../network/04-worldsocket.md`](../network/04-worldsocket.md) (`WorldSocket::HandlePing`, early-process opcodes), [`../network/05-worldsession.md`](../network/05-worldsession.md) (`WorldSession::Update` deep-dive, DOS protection), [`../architecture/03-update-loop.md`](../architecture/03-update-loop.md) (when `World::UpdateSessions` and `Map::Update` are called), [`../scripting/01-script-mgr.md`](../scripting/01-script-mgr.md) (`CanPacketReceive` / `CanPacketSend`).
- Project-side: [`../../05-modules.md`](../../05-modules.md) (modules using `CanPacketReceive`); [`azerothcore-wotlk/functions.md`](../../../azerothcore-wotlk/functions.md) (custom hooks added by this fork).
- External: Doxygen `classOpcodeTable`, `classClientOpcodeHandler`, `classWorldSession` (`Update`).
