# database — Async vs sync dispatch

> Four entry points on `DatabaseWorkerPool<T>` (`Execute`, `DirectExecute`, `Query`, `AsyncQuery`) plus the "fire across the queue" tasks built on top. Where each is allowed and what it costs. Builds on [`02-prepared-statements.md`](./02-prepared-statements.md). For multi-statement batches see [`04-query-holders.md`](./04-query-holders.md), for atomic groups see [`05-transactions.md`](./05-transactions.md).

## Critical files

| File | Role |
|---|---|
| `src/server/database/Database/DatabaseWorkerPool.h:82-97` | `Execute(sv)` / `Execute(stmt*)` — async fire-and-forget |
| `src/server/database/Database/DatabaseWorkerPool.h:105-120` | `DirectExecute(sv)` / `DirectExecute(stmt*)` — sync write, blocks |
| `src/server/database/Database/DatabaseWorkerPool.h:128-144` | `Query(sv)` / `Query(stmt*)` — sync read, returns `QueryResult` / `PreparedQueryResult` |
| `src/server/database/Database/DatabaseWorkerPool.h:152-157` | `AsyncQuery(sv)` / `AsyncQuery(stmt*)` — async read, returns `QueryCallback` |
| `src/server/database/Database/DatabaseWorkerPool.cpp:515-551` | `Execute` / `DirectExecute` bodies (template) |
| `src/server/database/Database/DatabaseWorkerPool.cpp:181-234` | `Query` / `AsyncQuery` bodies (template) |
| `src/server/database/Database/DatabaseWorkerPool.cpp:480-506` | `GetFreeConnection()` — round-robin lock on a sync connection |
| `src/server/database/Database/AdhocStatement.h:26` | `class BasicStatementTask : public SQLOperation` (raw-string variant) |
| `src/server/database/Database/AdhocStatement.cpp:39` | `BasicStatementTask::Execute()` — sets the `QueryResultPromise` if async |
| `src/server/database/Database/PreparedStatement.cpp:84` | `PreparedStatementTask::Execute()` — same pattern for prepared |
| `src/server/database/Database/QueryCallback.h:28` | `class QueryCallback` — future + chained `WithCallback`/`WithChainingCallback` |
| `src/server/database/Database/QueryCallback.cpp:186` | `QueryCallback::InvokeIfReady()` — called by per-session processor each tick |
| `src/server/database/Database/QueryResult.h:48` | `class ResultSet` — raw-string result rows |
| `src/server/database/Database/QueryResult.h:98` | `class PreparedResultSet` — prepared-statement result rows |
| `src/server/game/Server/WorldSession.h:1152` | `QueryCallbackProcessor& GetQueryProcessor()` (consumer side) |
| `src/server/database/Database/DatabaseWorkerPool.h:209-214` | `WarnAboutSyncQueries(bool)` — `ACORE_DEBUG`-only stack-trace dump for sync calls |

## Key concepts

- **Async path** — operation is wrapped in an `SQLOperation` subclass (`BasicStatementTask`, `PreparedStatementTask`, `TransactionTask`, `SQLQueryHolderTask`) and pushed onto the pool's single `ProducerConsumerQueue<SQLOperation*>`. Async worker threads (`DatabaseWorker::WorkerThread` in `DatabaseWorker.cpp:34`) pop and dispatch on dedicated async connections.
- **Sync path** — caller `try_lock`s a free synchronous connection (`MySQLConnection::LockIfReady`, cpp:471) and runs the query inline. `GetFreeConnection()` spins until a slot is free.
- **Result handles** — both `QueryResult` and `PreparedQueryResult` are `std::shared_ptr` to a `ResultSet` / `PreparedResultSet` (`DatabaseEnvFwd.h:27,45`). Empty result is a null `shared_ptr`; check with `if (result)` before `Fetch()`.
- **`QueryCallback`** — wraps a `std::future<…ResultSet>`. Lives on the consumer (typically `WorldSession`) and is polled by `_queryProcessor` each tick. Supports chained callbacks (`WithChainingPreparedCallback` returns the same `QueryCallback&` you can call again) for sequential async pipelines without nested lambdas.
- **`WarnAboutSyncQueries`** — when compiled with `ACORE_DEBUG` and toggled on for a thread, every sync call logs a `boost::stacktrace` to `sql.performances` (`DatabaseWorkerPool.cpp:483-488`). Used to find accidental sync queries on the world thread.

## Flow / data shape

```
                       ┌── adhoc string ───┐  ┌── prepared (typed) ──┐
                       ▼                   ▼  ▼                      ▼
async write   pool.Execute(sv)            pool.Execute(stmt*)
              └──> BasicStatementTask     └──> PreparedStatementTask
                       │                          │
                       └────► async queue ────────┘ ──► async DB worker

sync write    pool.DirectExecute(sv) / DirectExecute(stmt*)
              └──> GetFreeConnection() -> MySQLConnection::Execute -> Unlock

sync read     pool.Query(sv)               pool.Query(stmt*)
              └──> GetFreeConnection() -> Query -> Unlock
              returns QueryResult / PreparedQueryResult (null on empty)

async read    pool.AsyncQuery(sv)          pool.AsyncQuery(stmt*)
              └──> Basic/Prepared task with promise
                       │
                       └─► async queue ─► future set ─► QueryCallback ─►
                            consumer's QueryCallbackProcessor::ProcessReadyCallbacks()
```

### When to use which

| Need | Use | Why |
|---|---|---|
| Async write from gameplay code (most common) | `pool.Execute(stmt)` | Doesn't stall the world thread. |
| Sync write from startup-only code (one-shot setup) | `pool.DirectExecute(sv, args...)` | Simpler than the async machinery; world isn't ticking yet. |
| Sync read for a small lookup that the caller can't continue without (avoid in tick) | `pool.Query(stmt)` | Blocks; only acceptable if no realistic alternative. |
| Async read whose continuation runs in the consumer's tick | `pool.AsyncQuery(stmt)` + `WithPreparedCallback(...)` | The result is delivered through the per-session/world `QueryCallbackProcessor` next tick. |
| Multi-statement read at one logical event (e.g. login) | `SQLQueryHolder<T>` + `pool.DelayQueryHolder(holder)` | One async dispatch, one callback when **all** rows are ready. See [`04-query-holders.md`](./04-query-holders.md). |
| Atomic group of writes | `pool.BeginTransaction()` → `Append…` → `CommitTransaction(trans)` | All-or-nothing, deadlock-retry. See [`05-transactions.md`](./05-transactions.md). |

### Async result via `QueryCallback`

```cpp
CharacterDatabase.AsyncQuery(stmt)
    .WithPreparedCallback([this](PreparedQueryResult result)
    {
        if (result)
            DoSomethingWith(result->Fetch());
    });
// returned QueryCallback is moved into _queryProcessor by the caller's
// idiom (e.g. WorldSession::AddQueryCallback). Polled each session tick.
```

## Hooks & extension points

- Modules pick the correct entry point based on context. The chained-callback API (`WithChainingPreparedCallback`) is the supported way to express async dependencies (no need to add a custom `SQLOperation` subclass).
- A consumer that owns its own `QueryCallbackProcessor` (or `AsyncCallbackProcessor<T>`) can drive callbacks at any cadence; gameplay code typically uses the per-`WorldSession` processor at `WorldSession.h:1164`.

## Cross-references

- Engine-side: [`02-prepared-statements.md`](./02-prepared-statements.md), [`04-query-holders.md`](./04-query-holders.md), [`05-transactions.md`](./05-transactions.md), [`06-connection-pool.md`](./06-connection-pool.md), [`../network/05-worldsession.md`](../network/05-worldsession.md)
- Project-side: [`../../02-architecture.md#db-access`](../../02-architecture.md)
- Doxygen: `classDatabaseWorkerPool.html`, `classQueryCallback.html`, `classMySQLConnection.html`
