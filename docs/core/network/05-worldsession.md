# network — WorldSession

> The per-connection state object that owns a `Player*`, the inbound packet queue, the auth-queue flag, the per-account mute/security/locale, the Warden instance, and the `Update` loop that drains queued opcodes through the `OpcodeTable` dispatch (see [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md)). The bytes get here via [`04-worldsocket.md`](./04-worldsocket.md); the per-handler implementations live in [`../handlers/`](../handlers/00-index.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Server/WorldSession.h:284` | `class PacketFilter` (base — `Process(WorldPacket*)`) |
| `src/server/game/Server/WorldSession.h:297` | `class MapSessionFilter` — used by `Map::Update` |
| `src/server/game/Server/WorldSession.h:310` | `class WorldSessionFilter` — used by `World::UpdateSessions` |
| `src/server/game/Server/WorldSession.h:383` | `class WorldSession` |
| `src/server/game/Server/WorldSession.h:386` | ctor `(id, name, accountFlags, sock, sec, expansion, mute, locale, recruiter, isARecruiter, skipQueue, totalTime)` |
| `src/server/game/Server/WorldSession.h:416` | `void SendPacket(WorldPacket const* packet)` |
| `src/server/game/Server/WorldSession.h:443` | `uint32 GetAccountId() const` |
| `src/server/game/Server/WorldSession.h:444` | `Player* GetPlayer() const` (the per-session player pointer) |
| `src/server/game/Server/WorldSession.h:453` | `std::string const& GetRemoteAddress()` |
| `src/server/game/Server/WorldSession.h:460` | `void InitWarden(SessionKey const&, std::string const& os)` |
| `src/server/game/Server/WorldSession.h:464` | `void SetInQueue(bool)` |
| `src/server/game/Server/WorldSession.h:482` | `void KickPlayer(bool setKicked = true)` (overload uses `"Unknown reason"`) |
| `src/server/game/Server/WorldSession.h:483` | `void KickPlayer(std::string const& reason, bool setKicked = true)` |
| `src/server/game/Server/WorldSession.h:492` | `void QueuePacket(WorldPacket* new_packet)` |
| `src/server/game/Server/WorldSession.h:493` | `bool Update(uint32 diff, PacketFilter& updater)` |
| `src/server/game/Server/WorldSession.h:1170` | `class DosProtection` (inner) — `EvaluateOpcode` returns `Policy::Process / Kick / Ban / Log / BlockingThrottle / DropPacket` |
| `src/server/game/Server/WorldSession.h:1219`–`1271` | private state: `_player`, `m_Socket`, `m_Address`, `_security`, `_accountId`, `_warden`, `m_inQueue`, `_recvQueue`, … |
| `src/server/game/Server/WorldSession.cpp:63` | `MapSessionFilter::Process` — accepts `INPLACE` always; `THREADSAFE` only if player `IsInWorld` |
| `src/server/game/Server/WorldSession.cpp:85` | `WorldSessionFilter::Process` — everything except `THREADSAFE` of an in-world player |
| `src/server/game/Server/WorldSession.cpp:107` | ctor — initializes throttling, marks account online |
| `src/server/game/Server/WorldSession.cpp:159` | dtor — `LogoutPlayer(true)` if still bound, drains `_recvQueue`, marks account offline |
| `src/server/game/Server/WorldSession.cpp:283` | `SendPacket(WorldPacket const*)` — `CanPacketSend` veto, `m_Socket->SendPacket(*packet)` |
| `src/server/game/Server/WorldSession.cpp:333` | `QueuePacket(WorldPacket*)` — adds to `_recvQueue` (used by `WorldSocket::ReadDataHandler`) |
| `src/server/game/Server/WorldSession.cpp:358` | `Update(diff, PacketFilter&)` — main per-tick drain loop |
| `src/server/game/Server/WorldSession.cpp:379` | `MAX_PROCESSED_PACKETS_IN_SAME_WORLDSESSION_UPDATE = 150` |
| `src/server/game/Server/WorldSession.cpp:389` | `AntiDOS.EvaluateOpcode(*packet, currentTime)` — DOS gate |
| `src/server/game/Server/WorldSession.cpp:410`–`486` | `switch (opHandle->Status)` — `SessionStatus` gating block |
| `src/server/game/Server/WorldSession.cpp:537` | `_recvQueue.readd(...)` — re-injects throttled packets next tick |
| `src/server/game/Server/WorldSession.cpp:565` | `_warden->Update(diff)` — only inside `World::UpdateSessions` |
| `src/server/game/Server/WorldSession.cpp:592` | `HandleSocketClosed` — graceful drop without saving if conditions match |
| `src/server/game/Server/WorldSession.cpp:610` | `LogoutPlayer(bool save)` — group/guild/BG cleanup, `SaveToDB`, `SMSG_LOGOUT_COMPLETE` |
| `src/server/game/Server/WorldSession.cpp:794` | `KickPlayer(reason, setKicked)` — closes socket, optional `_kicked = true` |
| `src/server/game/Server/WorldSession.cpp:846` | `Handle_NULL` (sentinel) |
| `src/server/game/Server/WorldSession.cpp:852` | `Handle_EarlyProccess` (sentinel) |
| `src/server/game/Server/WorldSession.cpp:858` | `Handle_ServerSide` (sentinel — `SMSG_*` arrived from client) |
| `src/server/game/Server/WorldSession.cpp:864` | `Handle_Deprecated` (sentinel) |
| `src/server/game/Server/WorldSession.cpp:1337` | `InitWarden` — `WardenWin` for `os == "Win"`; `WardenMac` is commented out |
| `src/server/game/Server/WorldSessionMgr.h:32` | `class WorldSessionMgr` (singleton via `sWorldSessionMgr`) |
| `src/server/game/Server/WorldSessionMgr.cpp:91` | `UpdateSessions(diff)` — drains add-queue, runs `Update(WorldSessionFilter)`, prunes dead sessions |
| `src/server/game/Server/WorldSessionMgr.cpp:182` | `KickAll()` — iterates `_sessions` + `_offlineSessions` |
| `src/server/game/Server/WorldSessionMgr.cpp:204` | `AddSession(WorldSession*)` — enqueues; insert happens next `UpdateSessions` tick |
| `src/server/game/Server/WorldSessionMgr.cpp:209` | `AddQueuedPlayer(WorldSession*)` — sets `m_inQueue`, sends `AUTH_WAIT_QUEUE` |
| `src/server/game/Server/WorldSessionMgr.cpp:218` | `RemoveQueuedPlayer(WorldSession*)` — pops one, calls `InitializeSession()` on next in line |
| `src/server/game/Server/WorldSessionMgr.cpp:277` | `AddSession_(WorldSession*)` — kicks any existing session for the same account, then inserts |

## Key concepts

- **Lifetime** —
  1. Created by `WorldSocket::HandleAuthSessionCallback` (`WorldSocket.cpp:708`).
  2. Enqueued via `sWorldSessionMgr->AddSession`; absorbed on the next `UpdateSessions` tick (`WorldSessionMgr.cpp:100`).
  3. If the active count is over `Player.AmountLimit` and `_skipQueue` is false, `AddSession_` calls `AddQueuedPlayer` and the client sees `SMSG_AUTH_RESPONSE(AUTH_WAIT_QUEUE, position)`.
  4. Dispatch runs; on disconnect `HandleSocketClosed` may park the session in `_offlineSessions` for up to 60 s for reconnect tolerance.
  5. Destructor saves the player (if still bound) and marks the account offline.
- **Two-phase per-tick dispatch** — `WorldSessionMgr::UpdateSessions` calls `Update(diff, WorldSessionFilter)` (single-threaded), and `Map::Update` calls `Update(diff, MapSessionFilter)` (per-map thread). The two filters partition the recv-queue so each packet is processed exactly once. Matrix: [`../handlers/07-handler-registration.md#packetprocessing--threading`](../handlers/07-handler-registration.md).
- **Recv queue** — `LockedQueue<WorldPacket*> _recvQueue` (`WorldSession.h:1252`). Producer is the network thread (`WorldSocket::ReadDataHandler` → `QueuePacket`); `_recvQueue.next(packet, updater)` dequeues only entries the filter accepts; `_recvQueue.readd(begin, end)` re-injects packets that hit the per-tick cap.
- **`MAX_PROCESSED_PACKETS_IN_SAME_WORLDSESSION_UPDATE = 150`** — caps per-tick handler invocations per session per filter. Set inline in `Update` (`WorldSession.cpp:379`).
- **DOS protection** — `AntiDOS.EvaluateOpcode` runs before every dispatch (`WorldSession.cpp:389`). It looks up an `AntiDosOpcodePolicy` keyed by opcode (in `WorldGlobals`), counts packets per second, and returns `Process / Log / BlockingThrottle / Kick / Ban / DropPacket`. Configured via `worldserver.conf` `WorldThrottlingMap.*` keys.
- **Sentinel logging from the switch**: `STATUS_NEVER` → `"Received not allowed opcode …"` (`:479`); `STATUS_UNHANDLED` → debug `"Received not handled opcode …"` (`:483`). `Handle_NULL` / `Handle_ServerSide` / `Handle_Deprecated` are bound per-opcode in `OpcodeTable` — see [`03-opcodes.md`](./03-opcodes.md).
- **Hyperlink validation kicks** — `ValidateHyperlinksAndMaybeKick` (`:808`) / `DisallowHyperlinksAndMaybeKick` (`:822`) honor `Chat.StrictLinkChecking.Kick`. The dispatch loop catches `WorldPackets::InvalidHyperlinkException` / `IllegalHyperlinkException` (`:488`/`:498`) and `ByteBufferException` (`:513`) so a malformed packet only loses one packet.
- **Account-online bookkeeping** — ctor runs `UPDATE account SET online = 1` (`WorldSession.cpp:154`); `~WorldSession` runs `online = 0` plus a `totaltime` update (`:161`/`:179`).
- **Time sync** — in the `MapSessionFilter` path, `Update` ticks `_timeSyncTimer` and emits `SendTimeSync()` every 10 s (`:546`). The `CMSG_TIME_SYNC_RESP` reply (timestamped — see [`02-worldpacket.md`](./02-worldpacket.md)) feeds `_timeSyncClockDelta`.
- **`m_Address`** holds the dotted IP captured at construction (`:152`). Use `GetRemoteAddress()` for any logging.
- **`KickPlayer(setKicked = true)`** closes the socket immediately; `setKicked = false` skips the accelerated drop from `_offlineSessions`.

## Flow / data shape

```
WorldSocket::ReadDataHandler          (network thread)
        │
        ▼
WorldSession::QueuePacket(packet)  ──► _recvQueue
        │
        ▼  drained twice per world tick (one filter per phase):

World::UpdateSessions(diff)
  └─ WorldSessionMgr::UpdateSessions(diff)              (WorldSessionMgr.cpp:91)
       └─ for each session: Update(diff, WorldSessionFilter(session))
            while _recvQueue.next(packet, filter):
              AntiDOS.EvaluateOpcode → Process/Kick/Throttle/...
              switch (opHandle->Status): LOGGEDIN | TRANSFER | AUTHED | NEVER | UNHANDLED
              catch(ByteBufferException) → log + drop one packet
            if (ProcessUnsafe()): _warden->Update(diff)
            if (ShouldLogOut(now)): LogoutPlayer(true)

Map::Update(diff)                                       (per-map thread)
  └─ for each player on this map: Update(diff, MapSessionFilter(session))
       (same loop, opposite filter — only INPLACE + THREADSAFE-while-in-world)
```

## Hooks & extension points

- `sScriptMgr->CanPacketSend(WorldSession*, WorldPacket const&)` — `SendPacket :324` (veto outbound).
- `sScriptMgr->CanPacketReceive(WorldSession*, WorldPacket const&)` — `Update :428 / :446 / :456 / :472` (one site per status branch).
- `sScriptMgr->OnPlayerBeforeLogout(Player*)` / `OnPlayerLogout(Player*)` — `LogoutPlayer :622` / `:756`.
- `sScriptMgr->OnSocketOpen(...)` / `OnSocketClose(...)` — fired in `WorldSocketThread` (see [`04-worldsocket.md`](./04-worldsocket.md)); the session is *not* attached at `OnSocketOpen`.

For the full hook surface on `ServerScript` / `PlayerScript` / `AccountScript`, see [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).

## Cross-references

- Engine-side: [`04-worldsocket.md`](./04-worldsocket.md) (where `QueuePacket` is fed), [`03-opcodes.md`](./03-opcodes.md) and [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md) (status & processing matrices), [`../handlers/00-index.md`](../handlers/00-index.md), [`../entities/04-player.md`](../entities/04-player.md) (`Player` ↔ `WorldSession` two-way pointer), [`../architecture/03-update-loop.md`](../architecture/03-update-loop.md) (when `World::UpdateSessions` and `Map::Update` are scheduled).
- Project-side: [`../../05-modules.md`](../../05-modules.md) (modules using session-level hooks).
- External: Doxygen `classWorldSession`, `classWorldSessionMgr`, `classMapSessionFilter`, `classWorldSessionFilter`, `WorldSession_8h`.
