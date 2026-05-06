# database — Connection pool & worker model

> The `MySQLConnection` ↔ `DatabaseWorkerPool<T>` ↔ `DatabaseWorker` triangle: how the three pools split connections into async-queue workers and sync-lock slots, and how queries are dispatched. Cross-link: [`../architecture/04-threading.md`](../architecture/04-threading.md).

## Critical files

| File | Role |
|---|---|
| `src/server/database/Database/MySQLConnection.h:42-52` | `struct MySQLConnectionInfo` — DSN parsed from config string `"host;port;user;pass;db[;ssl]"` |
| `src/server/database/Database/MySQLConnection.h:54` | `class MySQLConnection` — wraps one `MYSQL*` handle |
| `src/server/database/Database/MySQLConnection.h:35-40` | `enum ConnectionFlags { CONNECTION_ASYNC = 0x1, CONNECTION_SYNCH = 0x2, CONNECTION_BOTH }` |
| `src/server/database/Database/MySQLConnection.cpp:33-48` | `MySQLConnectionInfo` ctor — tokenises the DSN string |
| `src/server/database/Database/MySQLConnection.cpp:50-67` | The two `MySQLConnection` constructors (sync vs async — async one starts a `DatabaseWorker`) |
| `src/server/database/Database/MySQLConnection.cpp:87-167` | `Open()` — `mysql_real_connect`, sets `utf8mb4`, `mysql_autocommit(1)` |
| `src/server/database/Database/MySQLConnection.cpp:471-479` | `LockIfReady()` / `Unlock()` — the per-connection mutex used by sync slots |
| `src/server/database/Database/MySQLConnection.cpp:555-646` | `_HandleMySQLErrno` — auto-reconnect on `CR_SERVER_GONE/LOST`, fatal abort on schema errors |
| `src/server/database/Database/DatabaseWorker.h:31` | `class DatabaseWorker` — owns one `std::thread`, one async `MySQLConnection` |
| `src/server/database/Database/DatabaseWorker.cpp:22-32` | Ctor starts thread, dtor joins |
| `src/server/database/Database/DatabaseWorker.cpp:34-53` | `WorkerThread()` — `_queue->WaitAndPop` → `op->call()` → `delete op` |
| `src/server/database/Database/DatabaseWorkerPool.h:48` | `template<class T> class DatabaseWorkerPool` (signature) |
| `src/server/database/Database/DatabaseWorkerPool.h:51-56` | Internal `enum InternalIndex { IDX_ASYNC, IDX_SYNCH, IDX_SIZE }` |
| `src/server/database/Database/DatabaseWorkerPool.h:232-236` | `_queue`, `_connections[IDX_SIZE]`, `_connectionInfo`, `_async_threads`, `_synch_threads` |
| `src/server/database/Database/DatabaseWorkerPool.cpp:55-69` | Pool ctor — asserts `mysql_thread_safe` and client-version match (logs `ACE00043`/`ACE00046`) |
| `src/server/database/Database/DatabaseWorkerPool.cpp:78-84` | `SetConnectionInfo(dsn, async, synch)` |
| `src/server/database/Database/DatabaseWorkerPool.cpp:86-110` | `Open()` — opens N async + M sync connections via `OpenConnections` |
| `src/server/database/Database/DatabaseWorkerPool.cpp:112-134` | `Close()` — `_queue->Shutdown()`, then `.clear()` async then sync |
| `src/server/database/Database/DatabaseWorkerPool.cpp:418-457` | `OpenConnections(IDX_*, n)` — creates connections; sync ctor vs async ctor |
| `src/server/database/Database/DatabaseWorkerPool.cpp:480-506` | `GetFreeConnection()` — round-robin `try_lock` over sync slots |
| `src/server/database/Database/DatabaseWorkerPool.cpp:469-472` | `Enqueue(op)` — `_queue->Push(op)` (async) |
| `src/server/database/Database/DatabaseWorkerPool.cpp:351-371` | `KeepAlive()` — pings every sync conn + enqueues N async pings |
| `src/server/database/Database/DatabaseWorkerPool.cpp:136-178` | `PrepareStatements()` — invokes `DoPrepareStatements()` on every connection, then sizes `_preparedStatementSize` |
| `src/server/database/Database/SQLOperation.h:41` | `class SQLOperation` — base task interface (`Execute`, `SetConnection`) |
| `src/server/database/Database/DatabaseLoader.cpp:67-77` | Reads `*.WorkerThreads` + `*.SynchThreads` from config, calls `SetConnectionInfo` + `Open()` |
| `src/server/database/Database/MySQLConnection.cpp:493-503` | Sized check: prepared stmts only available on the slot type they were registered for |
| `src/server/game/World/World.cpp:1287-1290` | Periodic `KeepAlive()` for all three pools |

## Key concepts

- **Two slot vectors per pool** — `_connections[IDX_ASYNC]` (size = `WorkerThreads`) and `_connections[IDX_SYNCH]` (size = `SynchThreads`). Each connection inside is a `unique_ptr<T>`. Defaults: 1 / 1 (worldserver `.conf.dist:136-138`); typical production tuning: 2–4 async per pool.
- **Async slot = connection + worker** — every async `MySQLConnection` constructor starts a `DatabaseWorker` thread bound to that connection (`MySQLConnection.cpp:66`). The shared `ProducerConsumerQueue<SQLOperation*>` (`_queue`) is consumed by **all** async workers in that pool — so N async slots means N parallel async connections.
- **Sync slot = lockable connection** — sync connections have no worker thread. Callers acquire one with `GetFreeConnection()`, which round-robins `try_lock` until it gets one (`DatabaseWorkerPool.cpp:496-503`); it **spins forever** if all are busy. `Unlock()` must be called by every sync code path to avoid deadlock.
- **`CONNECTION_BOTH` flag** — a statement registered with `CONNECTION_BOTH` has its `MYSQL_STMT*` prepared on both slot types; `_ASYNC` saves memory in sync connections (and vice versa) by skipping preparation when the flag mask doesn't match (`MySQLConnection.cpp:510-514`).
- **Producer-consumer queue** — `Acore::ProducerConsumerQueue<T>` (in `src/common/Threading/PCQueue.h`). `WaitAndPop` is the blocking pop; `Cancel`/`Shutdown` is how `Close()` wakes idle workers (`DatabaseWorkerPool.cpp:119`).
- **Auto-reconnect** — `_HandleMySQLErrno` detects connection-lost errnos, calls `Open()` again, re-prepares all statements via `PrepareStatements()` (it's the same connection object, so its `m_stmts` vector is rebuilt). `m_reconnecting` skips the resize on re-entry.
- **Fatal errnos** — schema errors (`ER_BAD_FIELD_ERROR`, `ER_NO_SUCH_TABLE`, `ER_PARSE_ERROR`) `ABORT()` the server with `ACE00043`/`ACE00046`-style messages (`MySQLConnection.cpp:629-641`).
- **Min versions** — pool ctor enforces `MIN_MYSQL_CLIENT_VERSION = 8.0.0` (`DatabaseWorkerPool.h:33-39`); `OpenConnections` re-checks server version and refuses < 8.0 (`DatabaseWorkerPool.cpp:443-447`).

## Flow / data shape

```
DatabaseLoader (startup, see 07-update-mechanism.md)
   ├─ pool.SetConnectionInfo(dsn, asyncN, synchM)
   ├─ pool.Open()
   │    ├─ OpenConnections(IDX_ASYNC, N)  ── for i in N: make_unique<T>(_queue, info), open
   │    │                                        each async connection's ctor starts a DatabaseWorker thread
   │    └─ OpenConnections(IDX_SYNCH, M)  ── for i in M: make_unique<T>(info), open
   │                                            (no thread; LockIfReady-only)
   ├─ pool.PrepareStatements()
   │    └─ for each connection: DoPrepareStatements()  (registers all CHAR_*/WORLD_*/LOGIN_* enums)
   └─ ready

at runtime:

  async path                                sync path
  ─────────────────                         ─────────────────
  Execute(stmt) / AsyncQuery(stmt) /        Query(stmt) / DirectExecute(stmt)
  CommitTransaction / DelayQueryHolder       │
       │                                     │
       └─► _queue.Push(op)                   ├─ GetFreeConnection() → spin until try_lock
            │                                ├─ conn->Query / Execute
            │                                └─ conn->Unlock()
        ┌───┴───┐
        │       │   one of N async workers
        ▼       ▼
   DatabaseWorker::WorkerThread:
        op = _queue.WaitAndPop()
        op->SetConnection(its conn)
        op->call() → Execute()
        delete op

graceful shutdown:
  pool.Close() → _queue.Shutdown() (wakes workers with null op, they return)
                 → ~DatabaseWorker joins thread → ~MySQLConnection mysql_close
```

## Hooks & extension points

- Pool sizing is config-only (`<Pool>.WorkerThreads`, `<Pool>.SynchThreads` in `worldserver.conf.dist:126-150`). Modules don't add or resize pools.
- A custom DB connection class (a new logging DB, say) needs:
  1. Subclass `MySQLConnection` with its own `Statements` typedef + `DoPrepareStatements()`.
  2. Declare a global `DatabaseWorkerPool<MyConnection>` accessor in a header equivalent to `DatabaseEnv.h`.
  3. Register with a `DatabaseLoader::AddDatabase(myPool, "MyName")` call at startup.
- `KeepAlive()` is called periodically by `World::Update` (`World.cpp:1287-1290`); custom DB types should be added there if they're long-lived.

## Cross-references

- Engine-side: [`01-database-env.md`](./01-database-env.md), [`03-async-vs-sync.md`](./03-async-vs-sync.md), [`05-transactions.md`](./05-transactions.md), [`07-update-mechanism.md`](./07-update-mechanism.md), [`../architecture/04-threading.md`](../architecture/04-threading.md), [`../architecture/02-startup.md`](../architecture/02-startup.md)
- Project-side: [`../../02-architecture.md#db-access`](../../02-architecture.md)
- Doxygen: `classMySQLConnection.html`, `classDatabaseWorkerPool.html`, `classDatabaseWorker.html`
- Wiki: `wiki/common-errors` (`#ace00043`, `#ace00046` — MySQL client/server version mismatch)
