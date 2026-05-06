# network — Warden

> The Blizzard anti-cheat module loaded inside the WoW client and driven by the server. Each `WorldSession` may own a `Warden` (currently only the Windows variant is wired) that periodically requests memory / Lua / module checks, validates the client's reply, and applies a configurable LOG / KICK / BAN penalty on failure. The transport is `SMSG_WARDEN_DATA` (`0x2E6`) / `CMSG_WARDEN_DATA` (`0x2E7`), wrapped by an additional ARC4 stream.

## Critical files

| File | Role |
|---|---|
| `src/server/game/Warden/Warden.h:27` | `enum WardenOpcodes` — `*MSG_WARDEN_DATA` sub-opcodes (client `MODULE_*`, `CHEAT_CHECKS_RESULT`, `HASH_RESULT`; server `MODULE_USE/CACHE/INITIALIZE`, `*_REQUEST`) |
| `src/server/game/Warden/Warden.h:46` | `enum WardenCheckType` (`MEM_CHECK=0xF3`, `PAGE_CHECK_A/B=0xB2/0xBF`, `MPQ_CHECK=0x98`, `LUA_EVAL_CHECK=139`, `DRIVER_CHECK=0x71`, `TIMING_CHECK=0x57`, `PROC_CHECK=0x7E`, `MODULE_CHECK=0xD9`) |
| `src/server/game/Warden/Warden.h:65` | `struct WardenModuleUse` — `SMSG_WARDEN_DATA(MODULE_USE)` (ID16 + key16 + size) |
| `src/server/game/Warden/Warden.h:73` | `struct WardenModuleTransfer` — module bytes streamed in 500-byte bursts |
| `src/server/game/Warden/Warden.h:80` | `struct WardenHashRequest` — 16-byte seed |
| `src/server/game/Warden/Warden.h:92` | `struct ClientWardenModule` — in-memory cache of one module |
| `src/server/game/Warden/Warden.h:102` | `class Warden` (abstract; virtuals `Init`, `GetModuleForClient`, `InitializeModule`, `RequestHash`, `HandleHashResult`, `RequestChecks`, `HandleData`) |
| `src/server/game/Warden/Warden.h:140`–`152` | private state: `_inputKey/_outputKey/_seed`, two `ARC4`, `_checkTimer`, `_clientResponseTimer`, `_dataSent`, `_module`, `_initialized` |
| `src/server/game/Warden/Warden.cpp:31` | base ctor — `_checkTimer = 10000` (10 s) |
| `src/server/game/Warden/Warden.cpp:50` | `SendModuleToClient` — 500-byte `WARDEN_SMSG_MODULE_CACHE` chunks, encrypted via `_outputCrypto` |
| `src/server/game/Warden/Warden.cpp:76` | `RequestModule` — sends `WARDEN_SMSG_MODULE_USE` |
| `src/server/game/Warden/Warden.cpp:98` | `Update(diff)` — if `_dataSent`, ticks `_clientResponseTimer` (kicks on `> Warden.ClientResponseDelay` ms); else counts `_checkTimer` and calls `RequestChecks()` |
| `src/server/game/Warden/Warden.cpp:133` | `DecryptData` / `EncryptData` (`_inputCrypto` / `_outputCrypto`) |
| `src/server/game/Warden/Warden.cpp:143` | `IsValidCheckSum` / `BuildChecksum` — XOR-folded SHA1 (5 × `uint32`) integrity word |
| `src/server/game/Warden/Warden.cpp:199` | `ApplyPenalty(checkId, reason)` — runs `KickPlayer` or `sBan->BanAccount`; always logs to `warden` |
| `src/server/game/Warden/Warden.cpp:279` | `ProcessLuaCheckResponse` — addon-message-based Lua check return path |
| `src/server/game/Warden/Warden.cpp:320` | `WorldSession::HandleWardenDataOpcode(WorldPacket&)` — decrypts, demuxes by sub-opcode |
| `src/server/game/Warden/WardenWin.h:31` | `struct WardenInitModuleRequest` — triple sub-command (SFile* APIs, FrameScript::Execute, PerformanceCounter) |
| `src/server/game/Warden/WardenWin.h:70` | `class WardenWin : public Warden` |
| `src/server/game/Warden/WardenWin.cpp:37` | Lua eval prefix/midfix/postfix template (`SendAddonMessage('_TW', …, 'GUILD')`); total < 256 bytes |
| `src/server/game/Warden/WardenWin.cpp:113` | `WardenWin::Init(session, K)` — derives keys via `SessionKeyGenerator<SHA1>(K)`, init ARC4, copies `Module.Seed`, calls `RequestModule()` |
| `src/server/game/Warden/WardenWin.cpp:138` | `GetModuleForClient` — wraps static `Module` blob from `WardenModuleWin.h`; `Id = MD5(CompressedData)` |
| `src/server/game/Warden/WardenWin.cpp:156` | `InitializeModule` — triple-`MODULE_INITIALIZE` binding three client function pointers |
| `src/server/game/Warden/WardenWin.cpp:213` | `RequestHash` — `WARDEN_SMSG_HASH_REQUEST` with 16-byte seed |
| `src/server/game/Warden/WardenWin.cpp:230` | `HandleHashResult` — constant-time SHA1 vs `Module.ClientKeySeedHash`; on success rotates keys to `Module.{Client,Server}KeySeed` and sets `_initialized = true` |
| `src/server/game/Warden/WardenWin.cpp:266` | `ForceChecks` / `:277` `RequestChecks` — quotas from `Warden.NumMemChecks/NumLuaChecks/NumOtherChecks`, payload from `sWardenCheckMgr->CheckIdPool[type]`, sets `_dataSent = true` |
| `src/server/game/Warden/WardenMac.cpp` | Mac override set exists but **not** instantiated — `WorldSession::InitWarden` `OSX` branch is commented out (`WorldSession.cpp:1346`) because the Mac build crashes the client |
| `src/server/game/Warden/WardenCheckMgr.h:25` | `enum WardenActions { LOG, KICK, BAN }` |
| `src/server/game/Warden/WardenCheckMgr.h:34` | `enum WardenCheckTypes { MEM_TYPE=0, LUA_TYPE=1, OTHER_TYPE=2 }` |
| `src/server/game/Warden/WardenCheckMgr.h:43` | `struct WardenCheck { Type, Data, Address, Length, Str, Comment, CheckId, IdStr, Action }` |
| `src/server/game/Warden/WardenCheckMgr.h:63`/`:79` | `class WardenCheckMgr` (singleton); `std::vector<uint16> CheckIdPool[MAX_WARDEN_CHECK_TYPES]` |
| `src/server/game/Warden/WardenCheckMgr.cpp:40` | `LoadWardenChecks` — short-circuits if `Warden.Enabled = 0`; reads `SELECT MAX(id) FROM warden_checks`, then `SELECT id, type, data, result, address, length, str, comment FROM warden_checks ORDER BY id` |
| `src/server/game/Warden/WardenCheckMgr.cpp:94` | per-row default `Action = Warden.ClientCheckFailAction` (capped at `BAN`); LUA checks must have IDs ≤ 9999 |
| `src/server/game/Warden/WardenPayloadMgr.{h,cpp}` | dynamic Lua-payload registry, IDs ≥ `WardenPayloadOffsetMin` |
| `src/server/game/Server/WorldSession.cpp:1337` | `InitWarden(K, os)` — `WardenWin` if `os == "Win"`; `OSX` branch commented; else `_warden` stays nullptr |
| `src/server/game/Server/WorldSocket.cpp:603`–`:610` | OS allow-list — `Warden.Enabled = 1` rejects accounts whose `os` ≠ `"Win"` / `"OSX"` |
| `src/server/game/Server/WorldSession.cpp:565`–`:578` | `_warden->Update(diff)` runs from `WorldSession::Update`, only inside `World::UpdateSessions` |

## Key concepts

- **Two-stage encryption** — outer header is encrypted by `AuthCrypt` (see [`04-worldsocket.md`](./04-worldsocket.md)); the **body** of `*MSG_WARDEN_DATA` is additionally encrypted by Warden's own `_inputCrypto` / `_outputCrypto` ARC4 streams, keyed by 16-byte values derived from the SRP6 session key via `SessionKeyGenerator<SHA1>`. After the client's first successful `HASH_RESULT`, the keys are rotated to `Module.ClientKeySeed` / `Module.ServerKeySeed` (`WardenWin.cpp:244`).
- **Module loading** — `WardenWin::GetModuleForClient` returns a single global `ClientWardenModule` built from the static `Module` blob in `WardenModuleWin.h` (Blizzard Warden DLL bytes). The MD5 of the bytes is the module ID. The client either says `MODULE_OK` (cached) or `MODULE_MISSING` (server streams via `SendModuleToClient` in 500-byte chunks).
- **Check pipeline (steady state)** — per cycle (`Warden.NumMemChecks + NumLuaChecks + NumOtherChecks`):
  1. `Warden::Update` decrements `_checkTimer`; when it hits 0, `RequestChecks` runs.
  2. `WardenWin::RequestChecks` pulls random IDs from `sWardenCheckMgr->CheckIdPool[type]` (re-seeds when empty), assembles a `CHEAT_CHECKS_REQUEST`, encrypts, sends, sets `_dataSent = true`.
  3. The client replies with `WARDEN_CMSG_CHEAT_CHECKS_RESULT`. `HandleData` walks the response, comparing each reply against `WardenCheckResult.Result` (for `MEM_CHECK`/`MPQ_CHECK`) or evaluating the Lua return.
  4. On any mismatch, `ApplyPenalty(checkId, reason)` runs the configured action.
- **Failure-to-respond kick** — if `_dataSent` and `_clientResponseTimer` > `Warden.ClientResponseDelay * 1000` ms, `Warden::Update` (`Warden.cpp:107`) kicks the player.
- **`LoadWardenChecks` data path** — worldserver startup → `WardenCheckMgr::LoadWardenChecks` reads `warden_checks` (DB-driven). Per-check action override: `warden_check_overrides`. Both tables in `acore_world` (see [`../../09-db-tables.md`](../../09-db-tables.md)).
- **Sub-opcode dispatch** — `HandleWardenDataOpcode` (`Warden.cpp:320`) bound to `CMSG_WARDEN_DATA` in `OpcodeTable`. Decrypts the body and switches on the first byte: `MODULE_MISSING`→`SendModuleToClient`; `MODULE_OK`→`RequestHash`; `CHEAT_CHECKS_RESULT`→`HandleData`; `HASH_RESULT`→`HandleHashResult` then `InitializeModule`; `MEM_CHECKS_RESULT`/`MODULE_FAILED`→NYI (debug log).
- **OS allow-list** — Warden enabled rejects accounts whose `account.os` ≠ `"Win"` / `"OSX"` (`WorldSocket.cpp:604`). Inside `InitWarden`, only the `Win` path constructs a `WardenWin`; `OSX` accounts pass auth but get `_warden = nullptr`.
- **Penalty configuration** — `Warden.ClientCheckFailAction` (`0`/`1`/`2` ↔ LOG/KICK/BAN) sets the default per row at load time. `warden_check_overrides.action` overrides individual rows. `Warden.BanDuration` (seconds) for `WARDEN_ACTION_BAN` (`Warden.cpp:237`).

## Flow / data shape

```
WorldSocket::HandleAuthSessionCallback                  (per-session, once)
  └─ if (Warden.Enabled) WorldSession::InitWarden(K, os)
       └─ os == "Win": _warden = make_unique<WardenWin>(); _warden->Init(this, K)
            ├─ derive _inputKey / _outputKey from K (SHA1-based KDF)
            ├─ _inputCrypto.Init(_inputKey); _outputCrypto.Init(_outputKey)
            ├─ _module = static Win module (MD5 → Id)
            └─ RequestModule() → SMSG_WARDEN_DATA(MODULE_USE)

client                                       server  (in WorldSession::Update)
  CMSG_WARDEN_DATA(MODULE_OK)        ─►  HandleWardenDataOpcode → RequestHash
  CMSG_WARDEN_DATA(MODULE_MISSING)   ─►                          SendModuleToClient
  CMSG_WARDEN_DATA(HASH_RESULT)      ─►  HandleHashResult (rotate keys, _initialized=true)
                                          → InitializeModule (3-bind)

  loop:                              ◄─ Warden::Update (_checkTimer expired)
                                        RequestChecks() — random IDs, encrypt,
                                        SMSG_WARDEN_DATA(CHEAT_CHECKS_REQUEST)
  CMSG_WARDEN_DATA(CHEAT_CHECKS_RESULT) ─► HandleData
                                            compare reply vs WardenCheckResult.Result
                                            mismatch → ApplyPenalty(checkId, "")

  no reply too long              ─► _clientResponseTimer > Warden.ClientResponseDelay
                                    _session->KickPlayer("Warden: ...")
```

## Hooks & extension points

—  Warden has no `ScriptMgr` veto hook. Module authors who want to react to a Warden penalty observe through the standard `BanMgr` path or by polling `WorldSession::GetWarden()`.

To add a new check, insert a row into `acore_world.warden_checks` (id, type, data, result, address, length, str, comment) and reload the world. LUA checks (`type = LUA_EVAL_CHECK`) must use four-digit IDs. Per-check action override → `warden_check_overrides`.

Dynamic runtime Lua payloads (from a module) → `Warden::GetPayloadMgr()` (`Warden.cpp:315`); `WardenPayloadMgr` allocates IDs ≥ `WardenPayloadOffsetMin` to avoid DB collisions.

## Cross-references

- Engine-side: [`04-worldsocket.md`](./04-worldsocket.md) (`InitWarden` is called from `HandleAuthSessionCallback`; OS allow-list), [`06-auth-srp6.md`](./06-auth-srp6.md) (where the session key Warden derives from is minted), [`05-worldsession.md`](./05-worldsession.md) (`_warden->Update` is ticked from `WorldSession::Update`), [`../database/`](../database/00-index.md) (`warden_checks`/`warden_check_overrides` tables), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).
- Project-side: [`../../09-db-tables.md`](../../09-db-tables.md) (`warden_checks` schema).
- External: Doxygen `classWarden`, `classWardenWin`, `classWardenCheckMgr`, `Warden_8h`. Wiki: `wiki/Warden-Anti-Cheat`.
