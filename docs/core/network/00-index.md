# network/ — client/server protocol layer

> Everything below `WorldSession::Handle*Opcode` — bytes on the wire, framing, opcodes, encryption, auth handshake, anti-cheat, realm relay.

## Topic files

| File | Topic |
|---|---|
| [`01-bytebuffer.md`](./01-bytebuffer.md) | `ByteBuffer`, typed `<<` / `>>`, exception types, default size |
| [`02-worldpacket.md`](./02-worldpacket.md) | `WorldPacket = ByteBuffer + opcode`, reuse via `Initialize`, receive timestamp |
| [`03-opcodes.md`](./03-opcodes.md) | `enum Opcodes`, `OpcodeTable`, `CMSG`/`SMSG`/`MSG` naming, version 12340 |
| [`04-worldsocket.md`](./04-worldsocket.md) | TCP framing, header struct, ARC4 stream cipher, `WorldSocket::HandleAuthSession` |
| [`05-worldsession.md`](./05-worldsession.md) | Per-player state, queue, dispatch loop, `KickPlayer`, `m_Address` |
| [`06-auth-srp6.md`](./06-auth-srp6.md) | `AuthSession`, SRP6 step opcodes (`CMSG_AUTH_SRP6_BEGIN`/`PROOF`), session key |
| [`07-warden.md`](./07-warden.md) | Warden client check pipeline, mem-check / page-check requests |
| [`08-realmlist.md`](./08-realmlist.md) | `authserver` → `worldserver` realm sync, realm flags, build/version mismatch |

## Critical files

| File | Role |
|---|---|
| `src/server/shared/Packets/ByteBuffer.{h,cpp}` | Wire serialization primitive |
| `src/server/game/Server/WorldPacket.h` | Opcode-bearing buffer |
| `src/server/game/Server/Opcodes.{h,cpp}` | Opcode enum + table |
| `src/server/game/Server/Protocol/*` | Specific packet structs |
| `src/server/game/Server/WorldSocket.{h,cpp}` | TCP socket, header framing, encryption |
| `src/server/game/Server/WorldSocketMgr.{h,cpp}` | Listener, accept loop |
| `src/server/game/Server/WorldSession.{h,cpp}` | Per-session dispatch |
| `src/server/game/Server/WorldSessionMgr.{h,cpp}` | Sessions registry |
| `src/server/apps/authserver/Server/AuthSession.{h,cpp}` | Authserver SRP6 session |
| `src/server/game/Warden/*` | Warden checks |
| `src/server/shared/Realms/*` | Realm record sync |

## Cross-references

- Engine-side: [`../handlers/00-index.md`](../handlers/00-index.md) (where opcodes get handled), [`../entities/04-player.md`](../entities/04-player.md) (`Player` ↔ `WorldSession`), [`../scripting/01-script-mgr.md`](../scripting/01-script-mgr.md) (`OnPacketReceive`/`Send` hooks)
- Project-side: [`../../04-aio-framework.md`](../../04-aio-framework.md) (custom AIO layer rides over `SMSG_*`/`CMSG_*` opcodes)
- External: `wiki/common-errors` (auth/connect errors), Doxygen for `WorldPacket`, `ByteBuffer`, `WorldSession`
