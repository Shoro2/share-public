# network — WorldPacket

> A `ByteBuffer` plus a 16-bit opcode and an optional `ReceivedTime`. Every CMSG/SMSG/MSG that crosses a `WorldSocket` is a `WorldPacket`. Builds on [`01-bytebuffer.md`](./01-bytebuffer.md); read targets are wired up in [`03-opcodes.md`](./03-opcodes.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Server/WorldPacket.h:25` | `class WorldPacket : public ByteBuffer` |
| `src/server/game/Server/WorldPacket.h:29` | `WorldPacket()` — empty container (opcode = `NULL_OPCODE`, reserve = 0) |
| `src/server/game/Server/WorldPacket.h:31` | `explicit WorldPacket(uint16 opcode, std::size_t res = 200)` — primary outbound ctor |
| `src/server/game/Server/WorldPacket.h:34` | move ctor |
| `src/server/game/Server/WorldPacket.h:37` | move-with-receivedTime ctor (used for `CMSG_TIME_SYNC_RESP`, `WorldSocket.cpp:461`) |
| `src/server/game/Server/WorldPacket.h:65` | ctor `(opcode, MessageBuffer&&)` — adopts the inbound payload buffer without copy |
| `src/server/game/Server/WorldPacket.h:68` | `void Initialize(uint16 opcode, std::size_t newres = 200)` — reuse pattern |
| `src/server/game/Server/WorldPacket.h:75` | `uint16 GetOpcode() const` |
| `src/server/game/Server/WorldPacket.h:76` | `void SetOpcode(uint16)` |
| `src/server/game/Server/WorldPacket.h:78` | `TimePoint GetReceivedTime() const` |
| `src/server/game/Server/WorldPacket.h:81` | `uint16 m_opcode{NULL_OPCODE}` |
| `src/server/game/Server/WorldPacket.h:82` | `TimePoint m_receivedTime` (default-initialized; non-zero only for selected opcodes) |

## Key concepts

- **Inheritance, not composition** — `WorldPacket` *is-a* `ByteBuffer`, so all operators and helpers from [`01-bytebuffer.md`](./01-bytebuffer.md) apply directly.
- **Opcode field** — `m_opcode` is a `uint16`; the wire-level value of one of `enum Opcodes` (see [`03-opcodes.md`](./03-opcodes.md)). `NULL_OPCODE = 0x0000` is reserved.
- **Default reserve = 200 bytes** — `ByteBuffer::DEFAULT_SIZE` (4 KiB) is overridden by the opcode ctor to a size that fits most outbound packets without re-allocation. Pass an explicit `res` for known-large opcodes (e.g. character enum, talents).
- **`Initialize(opcode, res)` reuse** — clears the storage, re-reserves, and replaces the opcode. Used by tight loops that emit many same-shape packets back-to-back (e.g., update-block builders) so the `vector<uint8>` capacity is paid for once.
- **`m_receivedTime`** — only set for opcodes whose handler needs the precise arrival timestamp (cross-thread clock-delta computation in `WorldSession::HandleTimeSyncResp`). For everything else `GetReceivedTime()` returns the default-constructed `TimePoint` (zero) — do not rely on it.
- **Copy semantics are deep** — copy ctor and `operator=` copy the underlying `_storage` vector. Move ctors transfer ownership and reset the source's cursors. The send path (`WorldSession::SendPacket → WorldSocket::SendPacket → EncryptableAndCompressiblePacket`) copies the packet once into a heap-allocated wrapper; callers may throw away their `WorldPacket` immediately after calling `SendPacket`.
- **No `WorldPackets::` typed structs in WotLK** — Cataclysm-and-later cores ship a `src/server/game/Server/Packets/` subtree with one C++ struct per opcode. The WotLK core uses raw `WorldPacket&` handlers throughout and only includes a tiny `WorldPackets::Character::LogoutComplete`-style helper namespace (`WorldSession.cpp:778`); the dispatch machinery in `Opcodes.cpp` is templated to allow either form (see `PacketHandler` / `PacketHandler<WorldPacket, …>` at `Opcodes.cpp:25`/`:39`), so future migration is mechanical.

## Flow / data shape

Outbound (server → client):

```cpp
WorldPacket data(SMSG_PONG, 4);          // opcode + 4-byte reserve
data << uint32(ping);
session->SendPacket(&data);              // copies, queues; safe to discard data
```

Inbound (client → server) — built inside `WorldSocket::ReadDataHandler` (`WorldSocket.cpp:401`):

```cpp
ClientPktHeader* header = ...;
OpcodeClient opcode = static_cast<OpcodeClient>(header->cmd);
WorldPacket packet(opcode, std::move(_packetBuffer));   // adopts MessageBuffer
// special-cased opcodes (PING, AUTH_SESSION, KEEP_ALIVE) handled inline;
// everything else is moved onto the heap and queued:
WorldPacket* queued =
    (opcode == CMSG_TIME_SYNC_RESP)
        ? new WorldPacket(std::move(packet), GameTime::Now())   // record arrival
        : new WorldPacket(std::move(packet));
session->QueuePacket(queued);
```

Inside the per-handler dispatch, the typed-packet specialization moves the buffer into a `WorldPackets::Foo::Bar` instance and calls its `Read()` (`Opcodes.cpp:31`); the raw-packet specialization passes the `WorldPacket&` straight through (`Opcodes.cpp:45`).

Header layout on the wire (sent as a separate framed prefix, *not* serialized into the packet's `_storage`): see [`04-worldsocket.md`](./04-worldsocket.md) — `ClientPktHeader` (4 bytes), `ServerPktHeader` (4 or 5 bytes when payload > 32 KiB).

## Hooks & extension points

- `sScriptMgr->CanPacketSend(WorldSession*, WorldPacket const&)` — last gate before the packet hits the socket. Implemented in `WorldSession::SendPacket` (`WorldSession.cpp:324`). Returning `false` drops the packet silently. See [`../scripting/01-script-mgr.md`](../scripting/01-script-mgr.md).
- `sScriptMgr->CanPacketReceive(WorldSession*, WorldPacket const&)` — last gate before dispatch. Fired in every status branch of `WorldSession::Update` (4 sites between `WorldSession.cpp:428` and `:472`). See [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md).

There is no `OnWorldPacketBuilt` style hook — the packet is constructed in caller code and only becomes observable once it reaches `SendPacket`. Modules that want to mutate an outbound packet should intercept it in `CanPacketSend`.

## Cross-references

- Engine-side: [`01-bytebuffer.md`](./01-bytebuffer.md) (every `<<` / `>>` operator), [`03-opcodes.md`](./03-opcodes.md) (table of `m_opcode` values), [`04-worldsocket.md`](./04-worldsocket.md) (framing, encryption, compression of `SMSG_UPDATE_OBJECT`), [`05-worldsession.md`](./05-worldsession.md) (`SendPacket`/`QueuePacket`), [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md) (typed-packet vs raw-packet `PacketHandler`).
- Project-side: [`../../04-aio-framework.md`](../../04-aio-framework.md) (custom AIO Lua channel rides over `SMSG_*`/`CMSG_*` opcodes — payload is a `WorldPacket` body).
- External: Doxygen `classWorldPacket`, `WorldPacket_8h`.
