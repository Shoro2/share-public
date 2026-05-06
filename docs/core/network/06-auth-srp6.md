# network — Authentication & SRP6

> The two-stage login: (1) the client speaks the SRP6 protocol with **authserver** (port 3724) to derive a 40-byte session key from the account password, and (2) reuses that key when it later connects to **worldserver** (port 8085) for the `CMSG_AUTH_SESSION` proof. This file maps both sides; the wire framing layer is in [`04-worldsocket.md`](./04-worldsocket.md), the realm-list reply that follows in [`08-realmlist.md`](./08-realmlist.md).

## Critical files

Authserver (port 3724):

| File | Role |
|---|---|
| `src/server/apps/authserver/Server/AuthSession.h:37` | `enum AuthStatus { CHALLENGE, LOGON_PROOF, RECONNECT_PROOF, AUTHED, WAITING_FOR_REALM_LIST, CLOSED }` |
| `src/server/apps/authserver/Server/AuthSession.h:48` | `struct AccountInfo` — row from `account` (login, lock state, ban, security level) |
| `src/server/apps/authserver/Server/AuthSession.h:64` | `class AuthSession final : public Socket<AuthSession>` |
| `src/server/apps/authserver/Server/AuthSession.h:95` | `Optional<Acore::Crypto::SRP6> _srp6` — per-session SRP6 instance |
| `src/server/apps/authserver/Server/AuthSession.h:96` | `SessionKey _sessionKey = {}` — 40-byte session key, set by `VerifyChallengeResponse` |
| `src/server/apps/authserver/Server/AuthSession.h:113` | `struct AuthHandler { AuthStatus status; size_t packetSize; bool (AuthSession::*handler)(); }` |
| `src/server/apps/authserver/Server/AuthSession.cpp:37` | `enum eAuthCmd { AUTH_LOGON_CHALLENGE = 0x00, AUTH_LOGON_PROOF = 0x01, AUTH_RECONNECT_CHALLENGE = 0x02, AUTH_RECONNECT_PROOF = 0x03, REALM_LIST = 0x10, XFER_* = 0x30…0x34 }` |
| `src/server/apps/authserver/Server/AuthSession.cpp:53` | `struct AUTH_LOGON_CHALLENGE_C` (cmd, error, size, gamename, version, build, platform, os, country, timezone, ip, I_len, I[]) |
| `src/server/apps/authserver/Server/AuthSession.cpp:73` | `struct AUTH_LOGON_PROOF_C` (cmd, A[32], clientM[20], crc_hash[20], number_of_keys, securityFlags) |
| `src/server/apps/authserver/Server/AuthSession.cpp:84` | `struct AUTH_LOGON_PROOF_S` (cmd, error, M2[20], AccountFlags, SurveyId, LoginFlags) |
| `src/server/apps/authserver/Server/AuthSession.cpp:104` | `struct AUTH_RECONNECT_PROOF_C` (cmd, R1[16], R2[20], R3[20], number_of_keys) |
| `src/server/apps/authserver/Server/AuthSession.cpp:115` | `VersionChallenge` — 16-byte hard-coded version-verify constant |
| `src/server/apps/authserver/Server/AuthSession.cpp:122` | `InitHandlers()` — wires the 5 sub-opcodes to handlers/sizes |
| `src/server/apps/authserver/Server/AuthSession.cpp:284` | `HandleLogonChallenge` — parses login, async `LOGIN_SEL_LOGONCHALLENGE` |
| `src/server/apps/authserver/Server/AuthSession.cpp:318` | `LogonChallengeCallback` — IP/country/ban/TOTP checks; constructs `_srp6`; sends `B`, `g`, `N`, `s` |
| `src/server/apps/authserver/Server/AuthSession.cpp:457` | `HandleLogonProof` — `_srp6->VerifyChallengeResponse`, `LOGIN_UPD_LOGONPROOF`, sends `M2` |
| `src/server/apps/authserver/Server/AuthSession.cpp:621` | `HandleReconnectChallenge` — random `_reconnectProof[16]` |
| `src/server/apps/authserver/Server/AuthSession.cpp:682` | `HandleReconnectProof` — verifies SHA1(login + R1 + _reconnectProof + K) == R2 |
| `src/server/apps/authserver/Server/AuthSession.cpp:727` | `HandleRealmList` — see [`08-realmlist.md`](./08-realmlist.md) |
| `src/server/apps/authserver/Authentication/AuthCodes.cpp:25` | `Is{Pre|Post}BCAcceptedClientBuild` / `IsAcceptedClientBuild` (queries `RealmList::GetBuildInfo`) |

SRP6 + crypto primitives:

| File | Role |
|---|---|
| `src/common/Cryptography/Authentication/AuthDefines.h:24` | `SESSION_KEY_LENGTH = 40`, `using SessionKey = std::array<uint8, 40>` |
| `src/common/Cryptography/Authentication/SRP6.h:28` | `class Acore::Crypto::SRP6` |
| `src/common/Cryptography/Authentication/SRP6.h:31` | `SALT_LENGTH = 32`, `VERIFIER_LENGTH = 32`, `EPHEMERAL_KEY_LENGTH = 32` |
| `src/common/Cryptography/Authentication/SRP6.h:40` | `static const g` (= `{7}`); `:41` `static const N` (safe prime) |
| `src/common/Cryptography/Authentication/SRP6.h:44` | `MakeRegistrationData(login, password)` → `(salt, verifier)` (account creation) |
| `src/common/Cryptography/Authentication/SRP6.h:47` | `static CheckLogin(login, password, salt, verifier)` (offline re-verification) |
| `src/common/Cryptography/Authentication/SRP6.h:52` | `static GetSessionVerifier(A, clientM, K)` — produces M2 |
| `src/common/Cryptography/Authentication/SRP6.h:57` | ctor — picks random `b`, computes `B = 3v + g^b mod N` |
| `src/common/Cryptography/Authentication/SRP6.h:58` | `std::optional<SessionKey> VerifyChallengeResponse(A, clientM)` |
| `src/common/Cryptography/Authentication/SRP6.cpp:27` | `N` = `894B645E…` (32 bytes, hard-coded safe prime) |
| `src/common/Cryptography/Authentication/SRP6.cpp:39` | `CalculateVerifier` — `v = g^H(s ‖ H(USER ":" PASS)) mod N` |
| `src/common/Cryptography/Authentication/SRP6.cpp:50` | `SHA1Interleave(S)` — splits, hashes, interleaves into 40-byte K |
| `src/common/Cryptography/Authentication/SRP6.cpp:87` | `VerifyChallengeResponse` — single-use; rejects `(A mod N) == 0`; `K = SHA1Interleave((A·v^u)^b)`; checks `H(NgHash, H(login), s, A, B, K) == clientM` |

Worldserver-side reuse of the session key: `WorldSocket.cpp:529`–`:711` (see [`04-worldsocket.md`](./04-worldsocket.md)) and `AuthCrypt::Init` (`src/common/Cryptography/Authentication/AuthCrypt.cpp:22`).

`account` table columns relevant to login: `username`, `salt`, `verifier`, `sessionkey`, `last_ip`, `locked`, `lock_country`, `os`, `Flags`, `mutetime`, `expansion`, `totp_secret`. Loaded by `LOGIN_SEL_ACCOUNT_INFO_BY_NAME` (worldserver) and `LOGIN_SEL_LOGONCHALLENGE` (authserver). Schema in `acore_auth`; see [`../database/`](../database/00-index.md), [`../../09-db-tables.md`](../../09-db-tables.md).

## Key concepts

- **SRP6 in one paragraph** — the client and server share `(N, g)` and a per-account salt `s` and verifier `v = g^H(s‖H(login:password))`. The password is **never** transmitted. Client picks random `a`, sends `A = g^a`. Server picks random `b`, sends `B = 3v + g^b` plus `s`. Both compute `u = H(A‖B)` and a shared secret `S`, then `K = SHA1Interleave(S)` (40 bytes). The client proves it knows `K` with `M = H(H(N) ⊕ H(g), H(login), s, A, B, K)`; the server replies `M2 = H(A, M, K)`.
- **Where the password lives** — never on the server. Only `(salt, verifier)` is stored in `account`. Password change rewrites both via `MakeRegistrationData` (`SRP6.cpp:31`).
- **Session key reuse** — the 40-byte `K` returned from authserver SRP6 is later read from `account.sessionkey` by worldserver (`WorldSocket.cpp:548`/`:582`). Worldserver verifies the client by recomputing `SHA1(login ‖ 4 zero bytes ‖ LocalChallenge ‖ _authSeed ‖ sessionKey)` and matching the client digest from `CMSG_AUTH_SESSION` (`WorldSocket.cpp:613`–`:629`).
- **`CMSG_AUTH_SRP6_BEGIN` / `_PROOF` / `_RECODE` opcodes** (`0x033`/`0x034`/`0x035`, `Opcodes.h:81`) and `SMSG_AUTH_SRP6_RESPONSE = 0x039` are bound to `Handle_NULL` in the WotLK opcode table — they are remnants of the in-game password-change UI, **not** the normal login path. Real login uses authserver `AUTH_LOGON_*` and worldserver `CMSG_AUTH_SESSION = 0x1ED` / `SMSG_AUTH_CHALLENGE = 0x1EC` / `SMSG_AUTH_RESPONSE = 0x1EE`.
- **TOTP** — when `account.totp_secret` is non-NULL, `LogonChallengeCallback` (`AuthSession.cpp:391`) AES-decrypts it via `SecretMgr` and sets `securityFlags |= 0x04`. The client appends a 6-digit token after `AUTH_LOGON_PROOF_C`; validated via `Acore::Crypto::TOTP::ValidateToken` (`:487`).
- **Wrong-password lockout** — `WrongPass.MaxCount` / `BanTime` / `BanType` (`AuthSession.cpp:569`–`:613`). Auto-bans via `LOGIN_INS_ACCOUNT_AUTO_BANNED` / `LOGIN_INS_IP_AUTO_BANNED`.
- **Reconnect path** — a client with a valid `_sessionKey` can skip SRP6 by sending `AUTH_RECONNECT_CHALLENGE`. Server replies with a random 16-byte `_reconnectProof`; client must echo `R2 = SHA1(login‖R1‖_reconnectProof‖sessionKey)`.
- **Build & version verification** — `VerifyVersion` checks the client executable hash against the `build_info` table's `WindowsHash`/`MacHash`. Mismatch → `WOW_FAIL_VERSION_INVALID`.
- **Account flags vs ACCOUNT_FLAG_GM** — `account.Flags` is forwarded in `AUTH_LOGON_PROOF_S.AccountFlags` (`AuthSession.cpp:535`); `WorldSession::ValidateAccountFlags` (`WorldSession.cpp:196`) reconciles against `account_access.gmLevel`.

## Flow / data shape

Initial logon (full SRP6, port 3724):

```
client                                   authserver
  │  ──── AUTH_LOGON_CHALLENGE ───────► │  HandleLogonChallenge
  │   build, os, country, login          │  AsyncQuery LOGIN_SEL_LOGONCHALLENGE
  │                                      │   → LogonChallengeCallback
  │                                      │   _srp6.emplace(login, s, v)
  │  ◄── reply: WOW_SUCCESS, B(32), g,  │
  │      N(32), s(32), VersionChallenge, │
  │      securityFlags                   │
  │                                      │
  │  ──── AUTH_LOGON_PROOF ──────────── ►│  HandleLogonProof
  │   A(32), clientM(20), crc_hash(20)   │   _srp6->VerifyChallengeResponse → K
  │                                      │   LOGIN_UPD_LOGONPROOF (sessionkey, last_ip, …)
  │  ◄── AUTH_LOGON_PROOF_S (M2, flags) │   _status = STATUS_AUTHED
  │                                      │
  │  ──── REALM_LIST ──────────────────►│  HandleRealmList (see 08-realmlist.md)
```

Subsequent worldserver login (port 8085, key reuse):

```
client                                   worldserver
  │  ───── TCP connect ─────────────── ►│  WorldSocket::Start (IP ban check)
  │  ◄─── SMSG_AUTH_CHALLENGE ─────────│  4-byte _authSeed + 32 random bytes
  │  ──── CMSG_AUTH_SESSION ─────────── ►│  HandleAuthSession → AuthSessionCallback
  │   build, account, LocalChallenge,    │   _authCrypt.Init(K)        ← header crypto ON
  │   digest = SHA1(login‖0000‖          │   verify digest, OS allow-list, IP/country lock
  │   LocalChallenge‖_authSeed‖K)        │   new WorldSession; InitWarden
  │  ◄─── SMSG_AUTH_RESPONSE (AUTH_OK   │   sWorldSessionMgr->AddSession(...)
  │      or AUTH_WAIT_QUEUE)             │
```

## Hooks & extension points

- `sScriptMgr->OnAccountLogin(uint32 accountId)` — fired in `WorldSocket::HandleAuthSessionCallback` (`WorldSocket.cpp:702`) after all checks pass.
- `sScriptMgr->OnFailedAccountLogin(uint32)` — IP-mismatch (`:642`), country-mismatch (`:654`), banned (`:675`), security-level too low (`:687`).
- `sScriptMgr->OnLastIpUpdate(uint32, std::string const&)` — `:706`.
- Authserver does **not** expose `ScriptMgr` (it links no script subsystem); to react to authserver-level events, intercept on the worldserver side via the hooks above.

## Cross-references

- Engine-side: [`04-worldsocket.md`](./04-worldsocket.md) (worldserver-side digest + `AuthCrypt::Init`), [`08-realmlist.md`](./08-realmlist.md) (the `REALM_LIST` reply that follows logon proof), [`07-warden.md`](./07-warden.md) (initialized from the same `K`), [`05-worldsession.md`](./05-worldsession.md) (`WorldSession` is constructed at the end of the world-side handshake), [`../server-apps/`](../server-apps/00-index.md) (`authserver` and `worldserver` `main()`).
- Project-side: [`../../02-architecture.md`](../../02-architecture.md) (auth/world split, port numbers, `acore_auth` schema).
- External: Doxygen `classAcore_1_1Crypto_1_1SRP6`, `classAuthSession`, `SRP6_8h`. RFC 2945 (SRP), RFC 5054 (SRP-TLS) — the WoW variant uses `k = 3` (constant, not `H(N, g)`), so it is technically SRP6 not SRP6a.
