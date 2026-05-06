# network — WorldSocket

> The TCP socket on port 8085 that frames every `WorldPacket`, ARC4-encrypts the headers after auth, intercepts `CMSG_PING` / `CMSG_AUTH_SESSION` / `CMSG_KEEP_ALIVE` before they touch a `WorldSession`, and hands everything else to `WorldSession::QueuePacket`. Listener: [`WorldSocketMgr`](#critical-files); per-session continuation: [`05-worldsession.md`](./05-worldsession.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Server/WorldSocket.h:32` | `class EncryptableAndCompressiblePacket : public WorldPacket` (send-queue node) |
| `src/server/game/Server/WorldSocket.h:42` | `NeedsCompression()` — true iff `SMSG_UPDATE_OBJECT && size() > 100` |
| `src/server/game/Server/WorldSocket.h:58` | `struct ClientPktHeader { uint16 size; uint32 cmd; }` (6 bytes on wire — first two are payload+cmd length, last four are opcode in little-endian; `cmd` validated against `NUM_OPCODE_HANDLERS`) |
| `src/server/game/Server/WorldSocket.h:70` | `class WorldSocket final : public Socket<WorldSocket>` |
| `src/server/game/Server/WorldSocket.h:122` | `std::array<uint8, 4> _authSeed` — random seed sent in `SMSG_AUTH_CHALLENGE` |
| `src/server/game/Server/WorldSocket.h:123` | `AuthCrypt _authCrypt` — header encryption, idle until `Init(SessionKey)` |
| `src/server/game/Server/WorldSocket.h:128` | `_worldSessionLock` (mutex) + `_worldSession` pointer (assigned after auth) |
| `src/server/game/Server/Protocol/ServerPktHeader.h:25` | `struct ServerPktHeader { uint32 size; uint8 header[5]; }` — 4 bytes (small) or 5 bytes (large >32 KiB), MSB of first byte = `0x80` flag |
| `src/server/game/Server/WorldSocket.cpp:41` | `compressBuff()` — zlib `deflate` for `SMSG_COMPRESSED_UPDATE_OBJECT` |
| `src/server/game/Server/WorldSocket.cpp:97` | `EncryptableAndCompressiblePacket::CompressIfNeeded` |
| `src/server/game/Server/WorldSocket.cpp:119` | `WorldSocket(IoContextTcpSocket&&)` — generates `_authSeed`, allocates header buffer |
| `src/server/game/Server/WorldSocket.cpp:128` | `Start` — async `LOGIN_SEL_IP_INFO` for IP ban check |
| `src/server/game/Server/WorldSocket.cpp:138` | `CheckIpCallback` — drops banned IPs, then `HandleSendAuthSession` + `AsyncRead` |
| `src/server/game/Server/WorldSocket.cpp:164` | `Update` — drains `_bufferQueue` into `MessageBuffer`s, encrypts headers if authed |
| `src/server/game/Server/WorldSocket.cpp:222` | `HandleSendAuthSession` — emits `SMSG_AUTH_CHALLENGE` (`uint32(1)` + 4-byte seed + 32-byte random) |
| `src/server/game/Server/WorldSocket.cpp:241` | `ReadHandler` — header/body framing state machine |
| `src/server/game/Server/WorldSocket.cpp:305` | `ReadHeaderHandler` — decrypts header if authed; rejects bad size/opcode |
| `src/server/game/Server/WorldSocket.cpp:332` | `struct ClientAuthSession` — parsed payload of `CMSG_AUTH_SESSION` |
| `src/server/game/Server/WorldSocket.cpp:347` | `struct AccountInfo` — row from `account` join query |
| `src/server/game/Server/WorldSocket.cpp:401` | `ReadDataHandler` — opcode demux for `CMSG_PING`/`AUTH_SESSION`/`KEEP_ALIVE`/`TIME_SYNC_RESP` |
| `src/server/game/Server/WorldSocket.cpp:494` | `_worldSession->QueuePacket(packetToQueue)` — hand-off to `WorldSession` |
| `src/server/game/Server/WorldSocket.cpp:518` | `SendPacket` — wraps in `EncryptableAndCompressiblePacket`, MPSC enqueue |
| `src/server/game/Server/WorldSocket.cpp:529` | `HandleAuthSession` — reads `Build`, account name, digest; async account query |
| `src/server/game/Server/WorldSocket.cpp:555` | `HandleAuthSessionCallback` — SHA1 verifies digest, attaches `WorldSession`, calls `InitWarden` |
| `src/server/game/Server/WorldSocket.cpp:726` | `SendAuthResponseError(uint8 code)` — short `SMSG_AUTH_RESPONSE` |
| `src/server/game/Server/WorldSocket.cpp:734` | `HandlePing` — overspeed-ping kicker + `SMSG_PONG` reply |
| `src/server/game/Server/WorldSocketMgr.h:31` | `class WorldSocketMgr : public SocketMgr<WorldSocket>` |
| `src/server/game/Server/WorldSocketMgr.cpp:25` | `class WorldSocketThread : public NetworkThread<WorldSocket>` (calls `OnSocketOpen`/`OnSocketClose` script hooks) |
| `src/server/game/Server/WorldSocketMgr.cpp:51` | `StartWorldNetwork(ioContext, bindIp, port, threadCount)` — entry from `worldserver/Main.cpp:353` |
| `src/server/game/Server/WorldSocketMgr.cpp:84` | `OnSocketOpen` — sets `Network.OutKBuff` socket-level + `TCP_NODELAY` per `Network.TcpNodelay` config |
| `src/common/Cryptography/Authentication/AuthCrypt.h:24` | `class AuthCrypt` — wraps two `Acore::Crypto::ARC4` streams (in/out) |
| `src/common/Cryptography/Authentication/AuthCrypt.cpp:22` | `Init(SessionKey const& K)` — derives keys via HMAC-SHA1, drops first 1024 ARC4 bytes (ARC4-drop1024) |

## Key concepts

- **One thread per `NetworkThread<WorldSocket>`** — the listener accepts connections in `Main.cpp` and round-robins them via `OnSocketAccept` (`WorldSocketMgr.cpp:53`). Each thread runs a Boost.Asio `io_context`.
- **Header framing state machine** — `ReadHandler` (`WorldSocket.cpp:241`) loops: drain bytes into `_headerBuffer` (6 bytes) → `ReadHeaderHandler` (decrypt, validate) → drain into `_packetBuffer` (sized from header) → `ReadDataHandler` to dispatch → reset both buffers.
- **Header encryption (post-auth)** — once `_authCrypt.Init(account.SessionKey)` runs in `HandleAuthSessionCallback` (`WorldSocket.cpp:582`), every received header is XOR-decrypted with the client-decrypt ARC4 stream, and every sent header is XOR-encrypted with the server-encrypt stream (only the header — the body is plaintext). Keys are derived via HMAC-SHA1 from two hard-coded 16-byte constants (`AuthCrypt.cpp:24`/`:27`) keyed by the 40-byte `SessionKey` from SRP6. The first 1024 stream bytes are discarded ("ARC4-drop1024").
- **Big-packet path** — `ServerPktHeader::isLargePacket()` returns true when payload size > `0x7FFF`. The 5-byte form prepends `0x80 | (size >> 16)` so the high bit signals "third length byte present" (`ServerPktHeader.h:32`). `ClientPktHeader::IsValidSize` enforces `size < 10240` for inbound (`WorldSocket.h:63`).
- **Compression** — `EncryptableAndCompressiblePacket::NeedsCompression` (`WorldSocket.h:42`) only fires for `SMSG_UPDATE_OBJECT` payloads larger than 100 bytes. The compressed packet's opcode is rewritten to `SMSG_COMPRESSED_UPDATE_OBJECT` (`0x1F6`) and the body becomes `[uint32 originalSize][zlib-deflated bytes]` (`WorldSocket.cpp:115`).
- **Outbound queue** — `SendPacket` enqueues onto the lock-free `MPSCQueue<EncryptableAndCompressiblePacket, …> _bufferQueue` (`WorldSocket.h:134`); the network thread's `Update` (`WorldSocket.cpp:164`) packs them into `_sendBufferSize`-sized `MessageBuffer`s before the kernel write. `_sendBufferSize` defaults to 4096 and grows up to the largest single packet ≤ 64 KiB seen (`WorldSocket.cpp:200`).
- **Early-process opcodes** — `CMSG_PING` (`HandlePing`), `CMSG_AUTH_SESSION` (`HandleAuthSession`), `CMSG_KEEP_ALIVE` (resets idle timer), and `CMSG_TIME_SYNC_RESP` (timestamps the packet) are switched on directly in `ReadDataHandler` and never enter the `WorldSession` recv queue. Their entries in `OpcodeTable` are bound to the sentinel `Handle_EarlyProccess` so a stray dispatch is a server-side bug.
- **DOS guards** — over-speed pings: `_OverSpeedPings` increments if two `CMSG_PING`s are < 27 s apart; > `Network.MaxOverspeedPings` kicks the player (`WorldSocket.cpp:756`). Header validation rejects `size < 4` or `size >= 10240` and opcode `>= NUM_OPCODE_HANDLERS` (`ReadHeaderHandler` `:318`).
- **OS allow-list when Warden is on** — `HandleAuthSessionCallback` rejects any account whose `account.os` is not `"Win"` or `"OSX"` if `Warden.Enabled = 1` (`WorldSocket.cpp:604`).

## Flow / data shape

```
TCP listener (Main.cpp:353 → WorldSocketMgr::StartWorldNetwork)
        │
        ▼  accept
NetworkThread<WorldSocket>::SocketAdded  → ScriptMgr::OnSocketOpen
        │
        ▼
WorldSocket::Start()
        │   AsyncQuery LOGIN_SEL_IP_INFO  (banned IP?)
        ▼   yes → SendAuthResponseError(AUTH_REJECT) + close
WorldSocket::HandleSendAuthSession()
        │   SMSG_AUTH_CHALLENGE = uint32(1) + 4-byte _authSeed + 32-byte random
        ▼
client → CMSG_AUTH_SESSION  (build, login, LocalChallenge, digest, AddonInfo)
        │
        ▼
WorldSocket::HandleAuthSession  (ReadDataHandler :429)
        │   AsyncQuery LOGIN_SEL_ACCOUNT_INFO_BY_NAME
        ▼
WorldSocket::HandleAuthSessionCallback  (:555)
        │   _authCrypt.Init(account.SessionKey)            ← header encryption ON
        │   verify SHA1(login || 0,0,0,0 || LocalChallenge || _authSeed || SessionKey)
        │       == client digest                           else AUTH_FAILED + close
        │   build new WorldSession(...)
        │   _worldSession->InitWarden(SessionKey, account.OS)  if Warden.Enabled
        │   sWorldSessionMgr->AddSession(_worldSession)
        ▼
steady state: ReadHandler loop → ReadHeaderHandler (decrypt) → ReadDataHandler → either:
        • CMSG_PING       → HandlePing → SMSG_PONG   (no session-side enqueue)
        • CMSG_KEEP_ALIVE → ResetTimeOutTime         (no enqueue)
        • CMSG_TIME_SYNC_RESP → new WorldPacket(..., GameTime::Now()); enqueue
        • everything else → new WorldPacket(...); _worldSession->QueuePacket(packet)
```

The reverse path (server → client):

```
WorldSession::SendPacket(WorldPacket*)             ← user code
        │   sScriptMgr->CanPacketSend (veto)
        ▼
WorldSocket::SendPacket  (:518)
        │   new EncryptableAndCompressiblePacket(packet, _authCrypt.IsInitialized())
        ▼
MPSCQueue _bufferQueue  ──► WorldSocket::Update (:164)  on the network thread
        │   queued->CompressIfNeeded();      // SMSG_UPDATE_OBJECT > 100 only
        │   ServerPktHeader header(size+2, opcode);
        │   if NeedsEncryption(): _authCrypt.EncryptSend(header.header, len)
        ▼
MessageBuffer  ──► kernel write
```

## Hooks & extension points

- `sScriptMgr->OnNetworkStart()` / `OnNetworkStop()` — fired from `WorldSocketMgr::StartWorldNetwork` (`WorldSocketMgr.cpp:73`) / `StopNetwork` (`:81`).
- `sScriptMgr->OnSocketOpen(std::shared_ptr<WorldSocket>)` / `OnSocketClose(...)` — fired from `WorldSocketThread::SocketAdded`/`SocketRemoved` (`WorldSocketMgr.cpp:31`/`:36`). The session is **not** attached yet at `OnSocketOpen` (only after `HandleAuthSessionCallback`).
- `sScriptMgr->OnAccountLogin(uint32 accountId)` / `OnFailedAccountLogin(uint32)` — fired in `HandleAuthSessionCallback` on the success / IP-mismatch / country-mismatch / banned / overlimit paths (`WorldSocket.cpp:702`/`:642`/`:654`/`:675`/`:687`).
- `sScriptMgr->OnLastIpUpdate(uint32 accountId, std::string const& ip)` — fired right after `OnAccountLogin` (`WorldSocket.cpp:706`).
- `sScriptMgr->CanPacketSend(...)` — last gate before the bytes hit the socket. See [`02-worldpacket.md`](./02-worldpacket.md).

Hook contract surface lives in `src/server/game/Scripting/ScriptDefines/ServerScript.h` and `AccountScript.h`. See [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).

## Cross-references

- Engine-side: [`02-worldpacket.md`](./02-worldpacket.md), [`03-opcodes.md`](./03-opcodes.md), [`05-worldsession.md`](./05-worldsession.md) (queue drain & `Update`), [`06-auth-srp6.md`](./06-auth-srp6.md) (where the `SessionKey` consumed here was minted), [`07-warden.md`](./07-warden.md) (`InitWarden` is called from `HandleAuthSessionCallback`), [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md) (`Handle_EarlyProccess` sentinel).
- Project-side: [`../../02-architecture.md`](../../02-architecture.md) (worldserver port 8085).
- External: Doxygen `classWorldSocket`, `classWorldSocketMgr`, `classAuthCrypt`, `WorldSocket_8h`. Wiki: `wiki/common-errors`.
