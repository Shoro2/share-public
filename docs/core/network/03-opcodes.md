# network — Opcodes

> The `enum Opcodes` and the global `OpcodeTable` (~1311-entry handler array) that maps every wire opcode to a `WorldSession::Handle*` method, a `SessionStatus` gate, and a `PacketProcessing` placement. This file covers the **catalog and naming**; the registration & dispatch mechanics live in [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Server/Protocol/Opcodes.h:29` | `enum Opcodes : uint16` — every CMSG/SMSG/MSG constant |
| `src/server/game/Server/Protocol/Opcodes.h:1341` | `NUM_MSG_TYPES = 0x51F` — sentinel one past the highest opcode value |
| `src/server/game/Server/Protocol/Opcodes.h:1344` | `enum OpcodeMisc { NUM_OPCODE_HANDLERS = NUM_MSG_TYPES, NULL_OPCODE = 0x0000 }` |
| `src/server/game/Server/Protocol/Opcodes.h:1350` | `typedef Opcodes OpcodeClient` / `OpcodeServer` (compile-time direction tag) |
| `src/server/game/Server/Protocol/Opcodes.h:1354` | `enum SessionStatus` (`STATUS_AUTHED`, `LOGGEDIN`, `TRANSFER`, `LOGGEDIN_OR_RECENTLY_LOGGOUT`, `NEVER`, `UNHANDLED`) |
| `src/server/game/Server/Protocol/Opcodes.h:1364` | `enum PacketProcessing` (`PROCESS_INPLACE`, `THREADUNSAFE`, `THREADSAFE`) |
| `src/server/game/Server/Protocol/Opcodes.h:1374` | `class OpcodeHandler` (base — `Name`, `Status`) |
| `src/server/game/Server/Protocol/Opcodes.h:1384` | `class ClientOpcodeHandler` (adds `ProcessingPlace`, `Call`) |
| `src/server/game/Server/Protocol/Opcodes.h:1402` | `class OpcodeTable` |
| `src/server/game/Server/Protocol/Opcodes.h:1428` | `extern OpcodeTable opcodeTable;` — global instance |
| `src/server/game/Server/Protocol/Opcodes.cpp:51` | `OpcodeTable opcodeTable;` definition |
| `src/server/game/Server/Protocol/Opcodes.cpp:123` | `OpcodeTable::Initialize()` — ~1300 `DEFINE_HANDLER(...)` lines, single source of truth |
| `src/server/game/Server/Protocol/Opcodes.cpp:1448` | `GetOpcodeNameForLoggingImpl<T>` — formats `[NAME 0xHHHH (DDDD)]` for logs |
| `src/server/game/Server/Protocol/Opcodes.cpp:1468` | `std::string GetOpcodeNameForLogging(Opcodes)` — use this from any log line |
| `src/server/game/World/World.cpp:927` | `opcodeTable.Initialize();` — called once during world boot |

## Key concepts

- **Naming prefix → direction** —
  - `CMSG_*` — Client → Server (handled).
  - `SMSG_*` — Server → Client (only sent; receiving one from the client is a hack/cheat — bound to `Handle_ServerSide`).
  - `MSG_*` — bidirectional (client may send, server may send the same opcode back; e.g. `MSG_MOVE_*` movement updates).
- **Wire format** — opcode is a `uint16` little-endian field inside the packet header. Client→server uses 2 bytes opcode + 2-byte size (`ClientPktHeader`, `WorldSocket.h:58`). Server→client uses 2 bytes opcode + 2-or-3-byte size (`ServerPktHeader`, `Protocol/ServerPktHeader.h:25`). Framing details: [`04-worldsocket.md`](./04-worldsocket.md).
- **Client build = 12340 (WotLK 3.3.5a)** — every opcode value below is keyed to that build. Builds outside the `build_info` table (`RealmList.cpp:57`) are rejected at the auth stage; mixing opcodes from a different expansion will land in the wrong slot. See [`08-realmlist.md`](./08-realmlist.md) for the build check.
- **`SessionStatus`** gates dispatch on the connection state (auth queue / logged-in / mid-transfer / never). Detailed semantics & matrix: [`../handlers/07-handler-registration.md#sessionstatus-gating`](../handlers/07-handler-registration.md).
- **`PacketProcessing`** decides whether the handler runs inline (`INPLACE`), in `World::UpdateSessions` (`THREADUNSAFE`), or in the per-map thread `Map::Update` (`THREADSAFE`). Detailed semantics: [`../handlers/07-handler-registration.md#packetprocessing--threading`](../handlers/07-handler-registration.md).
- **Sentinel handler functions** (defined on `WorldSession`):
  - `Handle_NULL` (`WorldSession.cpp:846`) — opcode is registered but unimplemented.
  - `Handle_EarlyProccess` (`WorldSession.cpp:852`) — should have been intercepted in `WorldSocket::ReadDataHandler` (e.g. `CMSG_PING`).
  - `Handle_ServerSide` (`WorldSession.cpp:858`) — bound to every `SMSG_*` so an inbound `SMSG_*` is logged and dropped.
  - `Handle_Deprecated` (`WorldSession.cpp:864`) — opcode intentionally retired.
- **Do not enumerate the table here.** The canonical inventory of all ~1311 opcodes is the `enum Opcodes` block in `Opcodes.h`. Use `git grep -n '^\s*[CSMS]MSG_' src/server/game/Server/Protocol/Opcodes.h` for a snapshot. Per-handler documentation lives in [`../handlers/`](../handlers/00-index.md).

## Opcode groups (orientation, hex ranges)

| Hex range | Subsystem (sample opcode → Handlers doc) |
|---|---|
| `0x001`–`0x031` | Cheats & debug (mostly `STATUS_NEVER` → `Handle_NULL`); `CMSG_DBLOOKUP`, `CMSG_GODMODE`, `CMSG_LEARN_SPELL`, … |
| `0x033`–`0x03D` | Auth & character screen (`CMSG_AUTH_SRP6_BEGIN`, `CMSG_CHAR_CREATE`, `CMSG_CHAR_ENUM`, `CMSG_CHAR_DELETE`, `CMSG_PLAYER_LOGIN`) → [`../handlers/01-character-handler.md`](../handlers/01-character-handler.md) |
| `0x03E`–`0x048` | World transfer & game time (`SMSG_NEW_WORLD`, `SMSG_TRANSFER_PENDING`, `SMSG_LOGIN_SETTIMESPEED`) |
| `0x049`–`0x09F` | Movement (`MSG_MOVE_START_FORWARD`, `MSG_MOVE_HEARTBEAT`, …) → [`../movement/`](../movement/00-index.md) |
| `0x0B5`–`0x100` | NPC interaction & queries (`SMSG_CREATURE_QUERY_RESPONSE`, `CMSG_GOSSIP_HELLO`) |
| `0x101`–`0x140` | Items, inventory, vendor, mail (`CMSG_SWAP_INV_ITEM`, `CMSG_SELL_ITEM`) |
| `0x130`–`0x16F` | Spell cast & aura (`CMSG_CAST_SPELL`, `SMSG_SPELL_GO`, `SMSG_AURA_UPDATE_ALL`) → [`../spells/`](../spells/00-index.md) |
| `0x170`–`0x1B0` | Combat (`SMSG_ATTACKERSTATEUPDATE`, `SMSG_SPELLNONMELEEDAMAGELOG`) → [`../combat/`](../combat/00-index.md) |
| `0x1DC`–`0x1F6` | Session control (`CMSG_PING = 0x1DC`, `SMSG_PONG = 0x1DD`, `SMSG_AUTH_CHALLENGE = 0x1EC`, `CMSG_AUTH_SESSION = 0x1ED`, `SMSG_AUTH_RESPONSE = 0x1EE`, `SMSG_COMPRESSED_UPDATE_OBJECT = 0x1F6`) |
| `0x200`–`0x27F` | Trade, friends, ignore, channels |
| `0x280`–`0x2E0` | Quest (`CMSG_QUESTGIVER_HELLO`, `SMSG_QUESTGIVER_QUEST_LIST`) → [`../quests/`](../quests/00-index.md) |
| `0x2E6`–`0x2E7` | Warden (`SMSG_WARDEN_DATA`, `CMSG_WARDEN_DATA`) → [`07-warden.md`](./07-warden.md) |
| `0x300`–`0x350` | Group / raid, LFG (`SMSG_GROUP_LIST`, `CMSG_LFG_JOIN`) → [`../social/`](../social/00-index.md) |
| `0x38C` | `CMSG_REALM_SPLIT` |
| `0x391` | `CMSG_TIME_SYNC_RESP` (timestamped on receive — see [`02-worldpacket.md`](./02-worldpacket.md)) |
| `0x407` | `CMSG_KEEP_ALIVE` (intercepted in `WorldSocket::ReadDataHandler`, never reaches the session queue) |
| `0x440`–`0x4FF` | Battlegrounds, calendar, vehicle, glyph, achievement → [`../battlegrounds/`](../battlegrounds/00-index.md), [`../entities/04-player.md`](../entities/04-player.md) |
| `0x518`–`0x51E` | Tail of the WotLK opcode space (`MSG_MOVE_SET_COLLISION_HGT`, `SMSG_MULTIPLE_MOVES`) |

The hex ranges are non-strict groupings; the authoritative cross-reference is `git grep -n` on the enum.

## Adding or renaming an opcode

1. **Edit** `Opcodes.h` — pick the next free hex slot inside the `enum Opcodes` block, name it per the convention above. Keep the `NUM_MSG_TYPES` sentinel at the very bottom.
2. **Register** it in `OpcodeTable::Initialize` (`Opcodes.cpp:123`) with `DEFINE_HANDLER(...)` (or `DEFINE_SERVER_OPCODE_HANDLER` for `SMSG_*`). Preserve the `/*0xNNN*/` alignment comment.
3. **Pick `SessionStatus` and `PacketProcessing`** per the matrices in [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md).
4. **Implement** the `WorldSession::Handle*Opcode` method under `src/server/game/Handlers/<feature>Handler.cpp`. Declare it in `WorldSession.h` in the matching `// XYZ handler` comment block.
5. The build is glob-based — no `CMakeLists.txt` edits needed.

The `ValidateAndSetClientOpcode` (`Opcodes.cpp:76`) and `ValidateAndSetServerOpcode` (`Opcodes.cpp:99`) checks reject `NULL_OPCODE`, out-of-range values, and double registration at boot — failures log to `network` and the slot is left empty (subsequent dispatch logs "No defined handler for opcode …").

## Logging

Every log line involving an opcode should format the value via `GetOpcodeNameForLogging(static_cast<OpcodeClient>(...))` (`Opcodes.cpp:1468`). The output is `[NAME 0x01ED (493)]`, which is parseable and stable across builds. Trace category is `network.opcode` (per-packet) and `network.opcode.buffer` (hex dump of the body — opt-in only).

## Hooks & extension points

—  Direct `OpcodeTable` is read-only after boot. To intercept dispatch, use the `ServerScript` hooks `CanPacketReceive` / `CanPacketSend` documented in [`02-worldpacket.md`](./02-worldpacket.md) and [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md).

## Cross-references

- Engine-side: [`02-worldpacket.md`](./02-worldpacket.md), [`04-worldsocket.md`](./04-worldsocket.md) (where the opcode is parsed off the wire), [`05-worldsession.md`](./05-worldsession.md) (the `Update` dispatch loop), [`../handlers/07-handler-registration.md`](../handlers/07-handler-registration.md) (`DEFINE_HANDLER` macro, `SessionStatus`, `PacketProcessing` matrices), [`../handlers/00-index.md`](../handlers/00-index.md) (per-handler docs).
- Project-side: [`../../04-aio-framework.md`](../../04-aio-framework.md) (AIO addon channel multiplexed on top of `CMSG_MESSAGECHAT`).
- External: Doxygen `classOpcodeTable`, `classClientOpcodeHandler`, `Opcodes_8h`.
