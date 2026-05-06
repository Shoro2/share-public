# network — Realm list

> The mechanism that hands the client a list of clickable realms after authserver SRP6 succeeds, plus the periodic `realmlist` table sync that keeps each realm's IP / population / flags fresh. Worldserver registers itself as a row in this table; authserver reads it. Builds on [`06-auth-srp6.md`](./06-auth-srp6.md) (the `REALM_LIST` reply happens after `AUTH_LOGON_PROOF`).

## Critical files

| File | Role |
|---|---|
| `src/server/shared/Realms/Realm.h:25` | `enum RealmFlags` (`NONE=0x00, VERSION_MISMATCH=0x01, OFFLINE=0x02, SPECIFYBUILD=0x04, UNK1=0x08, UNK2=0x10, RECOMMENDED=0x20, NEW=0x40, FULL=0x80`) |
| `src/server/shared/Realms/Realm.h:38` | `struct RealmHandle { uint32 Realm; }` (PK in `realmlist`) |
| `src/server/shared/Realms/Realm.h:52` | `enum RealmType` (`NORMAL=0, PVP=1, NORMAL2=4, RP=6, RPPVP=8, MAX_CLIENT_REALM_TYPE=14, FFA_PVP=16` — custom; collapsed to `PVP` for the client) |
| `src/server/shared/Realms/Realm.h:67` | `struct Realm { Id, Build, ExternalAddress, LocalAddress, LocalSubnetMask, Port, Name, Type, Flags, Timezone, AllowedSecurityLevel, PopulationLevel; GetAddressForClient(...) }` |
| `src/server/shared/Realms/Realm.cpp` | `Realm::GetAddressForClient` — returns `LocalAddress` if the client IP is on the same subnet as `LocalSubnetMask`, else `ExternalAddress` |
| `src/server/shared/Realms/RealmList.h:39` | `struct RealmBuildInfo { Build, Major, Minor, BugfixVersion, HotfixVersion, WindowsHash[20], MacHash[20] }` (one row per accepted client build) |
| `src/server/shared/Realms/RealmList.h:51` | `class RealmList` (singleton via `sRealmList`) |
| `src/server/shared/Realms/RealmList.h:54` | `typedef std::map<RealmHandle, Realm> RealmMap` |
| `src/server/shared/Realms/RealmList.h:61` | `RealmMap const& GetRealms() const` |
| `src/server/shared/Realms/RealmList.h:62` | `Realm const* GetRealm(RealmHandle const&) const` |
| `src/server/shared/Realms/RealmList.h:64` | `RealmBuildInfo const* GetBuildInfo(uint32 build) const` |
| `src/server/shared/Realms/RealmList.cpp:37` | `Initialize(ioContext, updateInterval)` — `LoadBuildInfo()` then `UpdateRealms(error_code{})` (initial sync) |
| `src/server/shared/Realms/RealmList.cpp:54` | `LoadBuildInfo` — `SELECT … FROM build_info ORDER BY build ASC` (used by `IsAcceptedClientBuild` / `VerifyVersion`) |
| `src/server/shared/Realms/RealmList.cpp:94` | `UpdateRealm` — upserts a `Realm` row in `_realms`; re-allocates ip-address ptrs only on change |
| `src/server/shared/Realms/RealmList.cpp:128` | `UpdateRealms(error)` — `LOGIN_SEL_REALMLIST`, DNS-resolves addresses, swaps `_realms`, logs adds/removes, re-arms `_updateTimer` |
| `src/server/shared/Realms/RealmList.cpp:236` | `GetRealm(RealmHandle const&)` |
| `src/server/shared/Realms/RealmList.cpp:247` | `GetBuildInfo(uint32 build)` — linear scan of `_builds` |
| `src/server/apps/authserver/Server/AuthSession.cpp:43` | `REALM_LIST = 0x10` (authserver sub-opcode) |
| `src/server/apps/authserver/Server/AuthSession.cpp:130` | `handlers[REALM_LIST] = { STATUS_AUTHED, 5, &AuthSession::HandleRealmList }` |
| `src/server/apps/authserver/Server/AuthSession.cpp:727` | `HandleRealmList` — async `LOGIN_SEL_REALM_CHARACTER_COUNTS` (per-account counts) |
| `src/server/apps/authserver/Server/AuthSession.cpp:739` | `RealmListCallback` — iterates `sRealmList->GetRealms()`; serializes `Type`, `lock`, `Flags`, name, `GetAddressForClient`, pop, charCount, timezone |
| `src/server/apps/authserver/Server/AuthSession.cpp:758` | build compatibility check (`realm.Build == _build`) → flips `REALM_FLAG_OFFLINE | REALM_FLAG_SPECIFYBUILD` |
| `src/server/apps/authserver/Server/AuthSession.cpp:782` | security gate (`realm.AllowedSecurityLevel > _accountInfo.SecurityLevel` → `lock = 1`) |
| `src/server/apps/authserver/Server/AuthSession.cpp:795`–`:798` | post-BC clients receive `realm.Id.Realm`; pre-BC get `0x0` placeholder |
| `src/server/game/Server/WorldSocket.cpp:541` | worldserver: `recvPacket >> authSession->RealmID;` (client's chosen realm) |
| `src/server/game/Server/WorldSocket.cpp:593` | `if (RealmID != realm.Id.Realm)` → `SendAuthResponseError(REALM_LIST_REALM_NOT_FOUND)` + close |

DB tables involved (all in `acore_auth`):

| Table | Purpose |
|---|---|
| `realmlist` | one row per registered realm; `id`, `name`, `address`, `localAddress`, `localSubnetMask`, `port`, `icon` (= `RealmType`), `flag`, `timezone`, `allowedSecurityLevel`, `population`, `gamebuild` |
| `build_info` | one row per accepted client build; `build`, `majorVersion`, `minorVersion`, `bugfixVersion`, `hotfixVersion`, `winChecksumSeed` (40 hex chars), `macChecksumSeed` (40 hex chars) |
| `realmcharacters` | per-(realm, account) character count, fed back into the `REALM_LIST` reply (`AuthSession.cpp:734`) |

## Key concepts

- **Two consumers, one table** — both `authserver` (during `HandleRealmList`) and `worldserver` (during `RealmList::Initialize` from `Main.cpp` startup) construct `sRealmList` and pull from `realmlist`. Separate processes; periodic `_updateInterval` re-sync keeps drift bounded.
- **Periodic sync** — `Initialize` takes `uint32 updateInterval` (seconds; configured via `RealmsStateUpdateDelay` in `authserver.conf`). After initial sync, `UpdateRealms` re-arms the `steady_timer` (`RealmList.cpp:231`). Interval `0` = "load once at boot" (`:229`).
- **DNS resolution at sync time** — `realmlist.address` may be a hostname; `Acore::Asio::Resolver` resolves it (`:163`). Failure logs and skips the realm for that cycle.
- **Address selection** — `Realm::GetAddressForClient(clientAddr)` returns `LocalAddress` if the client IP is on the same subnet as `LocalSubnetMask`, else `ExternalAddress`. Lets one realm row serve both LAN and Internet players.
- **Build mismatch** — `RealmListCallback` (`:758`) flips a realm to `REALM_FLAG_OFFLINE | REALM_FLAG_SPECIFYBUILD` if `realm.Build != _build`. Realm name is suffixed `(M.m.b)` for pre-BC clients (`:778`), so the user sees which build the realm is for.
- **`build_info` = source of truth** — `IsAcceptedClientBuild(build)` (both servers) returns true iff `sRealmList->GetBuildInfo(build) != nullptr`. Adding a new client build to a fork needs an `INSERT INTO build_info` row plus matching `winChecksumSeed`/`macChecksumSeed`.
- **Realm ID consistency** — worldserver reads `RealmID` from `worldserver.conf`, sets `realm.Id.Realm` at startup. `HandleAuthSession` enforces `authSession->RealmID == realm.Id.Realm` (`WorldSocket.cpp:593`); misconfigured `RealmID` → every login fails with `REALM_LIST_REALM_NOT_FOUND`.
- **`realm` global** — `src/server/shared/Realms/Realm.{h,cpp}` declares one `Realm` instance per process (the worldserver's singleton). Used wherever the worldserver needs to know its own row.
- **AzerothCore custom flag** — `REALM_TYPE_FFA_PVP = 16` (`Realm.h:62`) is project-side, beyond `MAX_CLIENT_REALM_TYPE = 14`. `RealmList::UpdateRealms` reduces it to `REALM_TYPE_PVP` for the client (`:186`); the FFA-PVP behavior is handled inside worldserver.

## Flow / data shape

Authserver realm-list cycle:

```
worldserver process                              authserver process
   ↓ on world tick                                  ↓ every RealmsStateUpdateDelay s
UPDATE realmlist                                 RealmList::UpdateRealms()
  SET population = X,                              SELECT * FROM realmlist
      flag = ...                                   for each row:
                                                     resolve DNS
                                                     UpdateRealm(handle, ...)
                                                     log "Added realm" or "Updating realm"
                                                   _updateTimer->expires_at(now+interval)

client                          authserver
  ──── REALM_LIST (5 bytes) ─────►  HandleRealmList   (status must be STATUS_AUTHED)
                                    AsyncQuery LOGIN_SEL_REALM_CHARACTER_COUNTS
                                       ↓
                                    RealmListCallback
                                    pkt = ByteBuffer
                                    for each realm in sRealmList->GetRealms():
                                       check build → maybe set REALM_FLAG_OFFLINE
                                       check security → lock = 1 if AllowedSecurityLevel >
                                                                        account.SecurityLevel
                                       pkt << Type(uint8)
                                       pkt << lock(uint8)        // post-BC only
                                       pkt << flag(uint8)
                                       pkt << name(string)
                                       pkt << "ip:port"          // GetAddressForClient
                                       pkt << pop(float)
                                       pkt << charCount(uint8)
                                       pkt << timezone(uint8)
                                       pkt << realmId(uint8)     // post-BC only
                                    SendPacket(pkt)
```

Subsequent worldserver login enforces the realm ID:

```
client (clicked realm with id N)               worldserver
  ──── CMSG_AUTH_SESSION (RealmID=N) ──────►  HandleAuthSession (WorldSocket.cpp:529)
                                              authSession->RealmID = N
                                              ...
                                              HandleAuthSessionCallback (:555)
                                              if (authSession->RealmID != realm.Id.Realm)
                                                  SendAuthResponseError(REALM_LIST_REALM_NOT_FOUND);
                                                  DelayedCloseSocket();
```

## Hooks & extension points

—  No `ScriptMgr` hook fires from `RealmList::UpdateRealms` (it runs on the authserver process, which has no script subsystem). To react to realm-list changes, modify the source in `RealmList.cpp` directly (the file lives in `src/server/shared`, so the change applies to both authserver and worldserver).

To register a new realm, `INSERT INTO realmlist` (or `UPDATE` an existing row) in `acore_auth`. The next `UpdateRealms` cycle (default ~`RealmsStateUpdateDelay` seconds) picks it up; restart authserver to skip the delay.

To accept a new client build, `INSERT INTO build_info` (with the matching `winChecksumSeed`/`macChecksumSeed`); the next `LoadBuildInfo` (i.e. process restart) is required because `_builds` is filled only at `Initialize` time.

## Cross-references

- Engine-side: [`06-auth-srp6.md`](./06-auth-srp6.md) (the `REALM_LIST` sub-opcode lives next to `AUTH_LOGON_*`), [`04-worldsocket.md`](./04-worldsocket.md) (worldserver-side realm-ID enforcement in `HandleAuthSessionCallback`), [`../server-apps/`](../server-apps/00-index.md) (where `sRealmList->Initialize(...)` is called from each `main()`), [`../database/`](../database/00-index.md).
- Project-side: [`../../02-architecture.md`](../../02-architecture.md) (auth/world process split, ports), [`../../09-db-tables.md`](../../09-db-tables.md) (`realmlist` / `build_info` / `realmcharacters`).
- External: Doxygen `classRealmList`, `structRealm`, `structRealmBuildInfo`, `Realm_8h`, `RealmList_8h`. Wiki: `wiki/installation` (configuring `realmlist`).
