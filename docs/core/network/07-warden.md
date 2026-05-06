# network — Warden

> The Blizzard anti-cheat module loaded inside the WoW client and driven by the server. Each `WorldSession` may own a `Warden` (currently only the Windows variant is wired) that periodically requests memory / Lua / module checks, validates the client's reply, and applies a configurable LOG / KICK / BAN penalty on failure. The transport is `SMSG_WARDEN_DATA` (`0x2E6`) / `CMSG_WARDEN_DATA` (`0x2E7`), wrapped by an additional ARC4 stream.

## Critical files

| File | Role |
|---|---|
| `src/server/game/Warden/Warden.h:27` | `enum WardenOpcodes` (sub-opcodes inside `*MSG_WARDEN_DATA`): client `MODULE_MISSING / MODULE_OK / CHEAT_CHECKS_RESULT / MEM_CHECKS_RESULT / HASH_RESULT / MODULE_FAILED`; server `MODULE_USE / MODULE_CACHE / CHEAT_CHECKS_REQUEST / MODULE_INITIALIZE / MEM_CHECKS_REQUEST / HASH_REQUEST` |
| `src/server/game/Warden/Warden.h:46` | `enum WardenCheckType` (`MEM_CHECK = 0xF3`, `PAGE_CHECK_A/B = 0xB2/0xBF`, `MPQ_CHECK = 0x98`, `LUA_EVAL_CHECK = 139`, `DRIVER_CHECK = 0x71`, `TIMING_CHECK = 0x57`, `PROC_CHECK = 0x7E`, `MODULE_CHECK = 0xD9`) |
| `src/server/game/Warden/Warden.h:65` | `struct WardenModuleUse` — sent as `SMSG_WARDEN_DATA(MODULE_USE)` (16-byte ID + 16-byte key + size) |
| `src/server/game/Warden/Warden.h:73` | `struct WardenModuleTransfer` — module bytes streamed in 500-byte bursts |
| `src/server/game/Warden/Warden.h:80` | `struct WardenHashRequest` — 16-byte seed |
| `src/server/game/Warden/Warden.h:92` | `struct ClientWardenModule` — in-memory cache of one .bin module |
| `src/server/game/Warden/Warden.h:102` | `class Warden` (abstract base; pure virtuals `Init`, `GetModuleForClient`, `InitializeModule`, `RequestHash`, `HandleHashResult`, `IsCheckInProgress`, `ForceChecks`, `RequestChecks`, `HandleData`) |
| `src/server/game/Warden/Warden.h:140`–`152` | private state: `_inputKey[16]`, `_outputKey[16]`, `_seed[16]`, two `Acore::Crypto::ARC4`, `_checkTimer`, `_clientResponseTimer`, `_dataSent`, `_module`, `_initialized` |
| `src/server/game/Warden/Warden.cpp:31` | base ctor — `_checkTimer = 10000` (10 s default until first request) |
| `src/server/game/Warden/Warden.cpp:50` | `SendModuleToClient` — chunks `_module->CompressedData` into 500-byte `WARDEN_SMSG_MODULE_CACHE` packets, encrypted with `_outputCrypto` |
| `src/server/game/Warden/Warden.cpp:76` | `RequestModule` — sends `WARDEN_SMSG_MODULE_USE` |
| `src/server/game/Warden/Warden.cpp:98` | `Update(diff)` — if `_dataSent`, ticks `_clientResponseTimer` and kicks on `> Warden.ClientResponseDelay` ms; otherwise counts down `_checkTimer` and calls `RequestChecks()` when it elapses |
| `src/server/game/Warden/Warden.cpp:133` | `DecryptData` / `EncryptData` — XOR through `_inputCrypto` / `_outputCrypto` |
| `src/server/game/Warden/Warden.cpp:143` | `IsValidCheckSum` / `BuildChecksum` — XOR-folded SHA1 (5 × `uint32`) for the per-payload integrity word |
| `src/server/game/Warden/Warden.cpp:184` | `GetWardenActionStr(uint32)` — `LOG`/`KICK`/`BAN` |
| `src/server/game/Warden/Warden.cpp:199` | `ApplyPenalty(checkId, reason)` — pulls `WardenCheck` from `sWardenCheckMgr`, runs `KickPlayer` (`KICK`) or `sBan->BanAccount` (`BAN`), writes a `LOG_INFO("warden", ...)` line either way |
| `src/server/game/Warden/Warden.cpp:279` | `ProcessLuaCheckResponse` — addon-message-based Lua check return path |
| `src/server/game/Warden/Warden.cpp:320` | `WorldSession::HandleWardenDataOpcode(WorldPacket&)` — decrypts, demuxes by sub-opcode |
| `src/server/game/Warden/WardenWin.h:31` | `struct WardenInitModuleRequest` — three sub-commands sent in one packet (SFile* APIs, FrameScript::Execute, PerformanceCounter offsets) |
| `src/server/game/Warden/WardenWin.h:70` | `class WardenWin : public Warden` |
| `src/server/game/Warden/WardenWin.cpp:37` | Lua eval prefix/midfix/postfix template (`SendAddonMessage(_TW, ..., 'GUILD')`) — total payload < 256 bytes |
| `src/server/game/Warden/WardenWin.cpp:113` | `WardenWin::Init(session, K)` — derives `_inputKey` / `_outputKey` via `SessionKeyGenerator<SHA1>(K)`, initializes ARC4 streams, copies `Module.Seed` into `_seed`, calls `RequestModule()` |
| `src/server/game/Warden/WardenWin.cpp:138` | `GetModuleForClient` — wraps the static `Module` blob from `WardenModuleWin.h` into a heap `ClientWardenModule` (sets `Id = MD5(CompressedData)`) |
| `src/server/game/Warden/WardenWin.cpp:156` | `InitializeModule` — sends a triple-`MODULE_INITIALIZE` packet binding three function pointers in client memory |
| `src/server/game/Warden/WardenWin.cpp:213` | `RequestHash` — `WARDEN_SMSG_HASH_REQUEST` with 16-byte seed |
| `src/server/game/Warden/WardenWin.cpp:230` | `HandleHashResult` — constant-time compares the 20-byte SHA1 against `Module.ClientKeySeedHash`; on success rotates `_inputKey`/`_outputKey` to the seeded keys and sets `_initialized = true` |
| `src/server/game/Warden/WardenWin.cpp:266` | `ForceChecks` / `:277` `RequestChecks` — pulls per-type quotas from `Warden.NumMemChecks` / `NumLuaChecks` / `NumOtherChecks`, builds a `CHEAT_CHECKS_REQUEST` payload from `sWardenCheckMgr->CheckIdPool[type]`, marks `_dataSent = true`, resets `_clientResponseTimer` |
| `src/server/game/Warden/WardenMac.cpp` | Mac module — full set of overrides exists but is **not** instantiated (`WorldSession::InitWarden` only does `WardenWin` for `os == "Win"`; the `WardenMac` branch is commented out at `WorldSession.cpp:1346` because the Mac build crashes the client) |
| `src/server/game/Warden/WardenCheckMgr.h:25` | `enum WardenActions { WARDEN_ACTION_LOG, _KICK, _BAN }` |
| `src/server/game/Warden/WardenCheckMgr.h:34` | `enum WardenCheckTypes { MEM_TYPE = 0, LUA_TYPE = 1, OTHER_TYPE = 2 }` |
| `src/server/game/Warden/WardenCheckMgr.h:43` | `struct WardenCheck { Type, Data, Address, Length, Str, Comment, CheckId, IdStr, Action }` |
| `src/server/game/Warden/WardenCheckMgr.h:63` | `class WardenCheckMgr` (singleton via `sWardenCheckMgr`) |
| `src/server/game/Warden/WardenCheckMgr.h:79` | `std::vector<uint16> CheckIdPool[MAX_WARDEN_CHECK_TYPES]` |
| `src/server/game/Warden/WardenCheckMgr.cpp:40` | `LoadWardenChecks` — short-circuits if `Warden.Enabled` is false; reads `SELECT MAX(id) FROM warden_checks`, sizes the vector, then `SELECT id, type, data, result, address, length, str, comment FROM warden_checks ORDER BY id` |
| `src/server/game/Warden/WardenCheckMgr.cpp:94` | per-row default `Action = Warden.ClientCheckFailAction` (capped at `BAN`); LUA checks must have IDs ≤ 9999 |
| `src/server/game/Warden/WardenCheckMgr.cpp:?` | `LoadWardenOverrides` — reads `warden_check_overrides` to bump `Action` per check |
| `src/server/game/Warden/WardenPayloadMgr.{h,cpp}` | `WardenPayloadMgr` — registry of dynamically-injected Lua payloads with IDs ≥ `WardenPayloadOffsetMin` |
| `src/server/game/Server/WorldSession.cpp:1337` | `WorldSession::InitWarden(SessionKey const& K, std::string const& os)` — `WardenWin` if `os == "Win"`; `OSX` branch commented out; otherwise `_warden` stays nullptr |
| `src/server/game/Server/WorldSocket.cpp:603`–`:610` | OS allow-list — when `Warden.Enabled = 1`, only `os == "Win"` or `"OSX"` accounts pass auth |
| `src/server/game/Server/WorldSession.cpp:565`–`:578` | `_warden->Update(diff)` is called once per world tick from `WorldSession::Update` (only inside `World::UpdateSessions`, never in the map filter) |

## Key concepts

- **Two-stage encryption** — outer header is encrypted by `AuthCrypt` (see [`04-worldsocket.md`](./04-worldsocket.md)); the **body** of `*MSG_WARDEN_DATA` is additionally encrypted by Warden's own `_inputCrypto` / `_outputCrypto` ARC4 streams, keyed by 16-byte values derived from the SRP6 session key via `SessionKeyGenerator<SHA1>`. After the client's first successful `HASH_RESULT`, the keys are rotated to `Module.ClientKeySeed` / `Module.ServerKeySeed` (`WardenWin.cpp:244`).
- **Module loading** — `WardenWin::GetModuleForClient` returns a single global `ClientWardenModule` built from the static `Module` blob in `WardenModuleWin.h` (the bytes are the actual Blizzard Warden DLL). The MD5 of the bytes is the module ID. The client either says `MODULE_OK` (it has the cached module) or `MODULE_MISSING` (server streams the bytes via `SendModuleToClient` in 500-byte chunks).
- **Check pipeline (steady state)** — every `Warden.NumMemChecks + NumLuaChecks + NumOtherChecks` checks per cycle (default 5+1+5):
  1. `Warden::Update` decrements `_checkTimer`. When it hits 0, `RequestChecks` runs.
  2. `WardenWin::RequestChecks` (`WardenWin.cpp:277`) pulls random IDs from `sWardenCheckMgr->CheckIdPool[type]` (re-seeding the pool when empty), assembles a `CHEAT_CHECKS_REQUEST` packet (per-check tag byte + check-specific payload), encrypts and sends. Sets `_dataSent = true`.
  3. The client runs the checks and replies with `WARDEN_CMSG_CHEAT_CHECKS_RESULT`. `HandleData` walks the response, comparing each check's reply against `WardenCheckResult.Result` from `sWardenCheckMgr` (for `MEM_CHECK`/`MPQ_CHECK`) or evaluating the Lua return (for `LUA_EVAL_CHECK`).
  4. On any mismatch, `ApplyPenalty(checkId, reason)` runs the configured action.
- **Failure-to-respond kick** — if `_dataSent` is true and `_clientResponseTimer` exceeds `Warden.ClientResponseDelay * 1000` ms, `Warden::Update` (`Warden.cpp:107`) kicks the player.
- **`LoadWardenChecks` data path** — `worldserver` startup → `WardenCheckMgr::LoadWardenChecks` reads from `warden_checks` (DB-driven). Override the default action per-check via `warden_check_overrides`. Both tables live in `acore_world` (see [`../../09-db-tables.md`](../../09-db-tables.md)).
- **Sub-opcode dispatch** — `WorldSession::HandleWardenDataOpcode` (`Warden.cpp:320`) is bound in `OpcodeTable` for `CMSG_WARDEN_DATA`. It decrypts the body via `_warden->DecryptData(...)` and switches on the first byte (`enum WardenOpcodes`):
  - `MODULE_MISSING` → `SendModuleToClient`
  - `MODULE_OK` → `RequestHash`
  - `CHEAT_CHECKS_RESULT` → `HandleData`
  - `HASH_RESULT` → `HandleHashResult` then `InitializeModule`
  - `MEM_CHECKS_RESULT` / `MODULE_FAILED` → currently NYI (logged as debug).
- **OS allow-list** — when Warden is enabled, the worldserver auth handshake rejects accounts whose `account.os` is neither `"Win"` nor `"OSX"` (`WorldSocket.cpp:604`). Inside `InitWarden`, only the `Win` path actually constructs a `WardenWin`; `OSX` accounts pass auth but get `_warden = nullptr` (and so no checks run).
- **Penalty configuration** — `Warden.ClientCheckFailAction` (`0`/`1`/`2` ↔ LOG/KICK/BAN) sets the default per row at load time. `warden_check_overrides.action` overrides individual rows. `Warden.BanDuration` (seconds) is the duration used for `WARDEN_ACTION_BAN` (`Warden.cpp:237`).

## Flow / data shape

```
WorldSocket::HandleAuthSessionCallback                      (per-session, once)
    └─ if (Warden.Enabled) WorldSession::InitWarden(K, os)
         └─ os == "Win":  _warden = make_unique<WardenWin>()
                          _warden->Init(this, K)
                            ├─ derive _inputKey / _outputKey from K (SHA1-based KDF)
                            ├─ _inputCrypto.Init(_inputKey); _outputCrypto.Init(_outputKey)
                            ├─ _module = static Win module (MD5 → Id)
                            └─ RequestModule()  → SMSG_WARDEN_DATA(MODULE_USE)

client                                          server (per WorldSession::Update)
  CMSG_WARDEN_DATA(MODULE_OK)        ─►  HandleWardenDataOpcode  →  RequestHash
  CMSG_WARDEN_DATA(MODULE_MISSING)   ─►                            SendModuleToClient (chunks)
  CMSG_WARDEN_DATA(HASH_RESULT)      ─►                            HandleHashResult
                                                                     - rotate keys to Module.*
                                                                     - _initialized = true
                                                                   InitializeModule (3-bind)

  loop:
                                       ◄─  Warden::Update              (_checkTimer reaches 0)
                                          RequestChecks()
                                          - pull random check IDs
                                          - build payload, encrypt
                                          - SMSG_WARDEN_DATA(CHEAT_CHECKS_REQUEST)
  CMSG_WARDEN_DATA(CHEAT_CHECKS_RESULT) ─►  HandleData
                                              - parse, compare to WardenCheckResult.Result
                                              - on mismatch: ApplyPenalty(checkId, "")

  no reply for too long             ─► _clientResponseTimer > Warden.ClientResponseDelay
                                       _session->KickPlayer("Warden: clientResponseTimer ...")
```

## Hooks & extension points

—  Warden has no `ScriptMgr` veto hook (compare `CanPacketReceive` for normal opcodes). Module authors who want to react to a Warden penalty observe player kicks/bans through the standard `OnPlayerKick` / `BanMgr` paths.

To add a new check, insert a row into `acore_world.warden_checks` (id, type, data, result, address, length, str, comment) and reload the world. Lua-only checks live with `type = LUA_EVAL_CHECK` and four-digit IDs at most. Per-check action override goes into `warden_check_overrides`.

For dynamic Lua payloads at runtime (e.g., from a custom module), use `Warden::GetPayloadMgr()` (`Warden.cpp:315`) — the `WardenPayloadMgr` allocates IDs ≥ `WardenPayloadOffsetMin` so they don't collide with DB-loaded checks.

## Cross-references

- Engine-side: [`04-worldsocket.md`](./04-worldsocket.md) (`InitWarden` is called from `HandleAuthSessionCallback`; OS allow-list), [`06-auth-srp6.md`](./06-auth-srp6.md) (where the session key Warden derives from is minted), [`05-worldsession.md`](./05-worldsession.md) (`_warden->Update` is ticked from `WorldSession::Update`), [`../database/`](../database/00-index.md) (`warden_checks`/`warden_check_overrides` tables), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).
- Project-side: [`../../09-db-tables.md`](../../09-db-tables.md) (`warden_checks` schema).
- External: Doxygen `classWarden`, `classWardenWin`, `classWardenCheckMgr`, `Warden_8h`. Wiki: `wiki/Warden-Anti-Cheat`.
