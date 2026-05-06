# server-apps/ — `authserver` and `worldserver` `main()`

> The two executables are thin wrappers. `authserver` does SRP6 + realm relay; `worldserver` brings up the gameplay. Both share the same `common/` (Asio, threading, crypto, config, logging).

## Topic files

| File | Topic |
|---|---|
| [`01-authserver.md`](./01-authserver.md) | `Main.cpp` flow, `AuthSession` lifecycle, realmlist relay, signal handling |
| [`02-worldserver.md`](./02-worldserver.md) | `Main.cpp` flow, console commands, signal handling, crash dumps |

## Critical files

| File | Role |
|---|---|
| `src/server/apps/authserver/Main.cpp` | Auth entry |
| `src/server/apps/authserver/Server/AuthSession.{h,cpp}` | SRP6 |
| `src/server/apps/authserver/Server/RealmList.{h,cpp}` | Realm registry |
| `src/server/apps/worldserver/Main.cpp` | World entry |
| `src/server/apps/worldserver/CommandLine/CliRunnable.{h,cpp}` | Console commands |
| `src/server/apps/worldserver/RemoteAccess/*` | RA console |
| `conf/dist/authserver.conf.dist`, `worldserver.conf.dist` | Default configs |

## Cross-references

- Engine-side: [`../architecture/01-process-model.md`](../architecture/01-process-model.md), [`../architecture/02-startup-shutdown.md`](../architecture/02-startup-shutdown.md), [`../network/06-auth-srp6.md`](../network/06-auth-srp6.md), [`../network/08-realmlist.md`](../network/08-realmlist.md), [`../world/02-config-mgr.md`](../world/02-config-mgr.md)
- Fork-specific: `azerothcore-wotlk/functions.md` (DB-setup + run commands), `azerothcore-wotlk/doc/Logging.md`, `azerothcore-wotlk/doc/ConfigPolicy.md`
- External: `wiki/installation`, `wiki/install-with-docker`, `wiki/common-errors`
