# database — Transactions (atomic multi-statement writes)

> `BeginTransaction()` → `Append(...)` → `CommitTransaction(trans)`. All-or-nothing semantics with built-in deadlock retry on the async path. Builds on [`02-prepared-statements.md`](./02-prepared-statements.md) (you append both ad-hoc strings and prepared statements).

## Critical files

| File | Role |
|---|---|
| `src/server/database/Database/Transaction.h:30` | `class TransactionBase` — base, holds the `m_queries` vector |
| `src/server/database/Database/Transaction.h:42-48` | `Append(sv sql)` / variadic `Append(sv, args…)` for ad-hoc |
| `src/server/database/Database/Transaction.h:53` | `protected AppendPreparedStatement(stmt*)` |
| `src/server/database/Database/Transaction.h:61` | `template<typename T> class Transaction` — typed `Append(PreparedStatement<T>*)` |
| `src/server/database/Database/Transaction.cpp:33-48` | `Append` / `AppendPreparedStatement` bodies (push to `m_queries`) |
| `src/server/database/Database/Transaction.cpp:50-94` | `Cleanup()` — frees prepared stmts + clears strings on destruction or failure |
| `src/server/database/Database/Transaction.h:74` | `class TransactionTask : public SQLOperation` (async wrapper) |
| `src/server/database/Database/Transaction.cpp:96-129` | `TransactionTask::Execute()` — wraps `TryExecute()` with deadlock retry |
| `src/server/database/Database/Transaction.cpp:30` | `DEADLOCK_MAX_RETRY_TIME_MS = 1min` — bound on retry loop |
| `src/server/database/Database/Transaction.cpp:28` | `static std::mutex TransactionTask::_deadlockLock` — serialises retries |
| `src/server/database/Database/Transaction.h:95` | `class TransactionWithResultTask : public TransactionTask` (async + future) |
| `src/server/database/Database/Transaction.h:108` | `class TransactionCallback` (consumer-side, like `QueryCallback`) |
| `src/server/database/Database/DatabaseWorkerPool.h:170` | `BeginTransaction() -> SQLTransaction<T>` |
| `src/server/database/Database/DatabaseWorkerPool.h:174-178` | `CommitTransaction(trans)` (async) / `AsyncCommitTransaction(trans)` |
| `src/server/database/Database/DatabaseWorkerPool.h:182` | `DirectCommitTransaction(trans&)` — sync, blocks |
| `src/server/database/Database/DatabaseWorkerPool.h:186-190` | `ExecuteOrAppend(trans, sql)` / `ExecuteOrAppend(trans, stmt*)` — sentinel-aware helper |
| `src/server/database/Database/DatabaseWorkerPool.cpp:247-273` | `BeginTransaction` + `CommitTransaction` bodies |
| `src/server/database/Database/DatabaseWorkerPool.cpp:301-331` | `DirectCommitTransaction` body — sync deadlock loop (5 retries) |
| `src/server/database/Database/MySQLConnection.cpp:367-454` | `BeginTransaction`/`CommitTransaction`/`RollbackTransaction`/`ExecuteTransaction` (raw MySQL layer) |
| `src/server/database/Database/SQLOperation.h:33` | `struct SQLElementData { variant<…stmt*, string>; type; }` — what gets queued in `m_queries` |
| `src/server/database/Database/DatabaseEnvFwd.h:69-71` | `using {Char,Login,World}DatabaseTransaction = std::shared_ptr<Transaction<…>>` |

## Key concepts

- **`SQLTransaction<T>`** — `std::shared_ptr<Transaction<T>>`. Idiomatic name in code is `trans`. The aliases live in `DatabaseEnvFwd.h:69-71`.
- **Element types** — a transaction holds a `std::vector<SQLElementData>` (`SQLOperation.h:33`); each element is either an owned `PreparedStatementBase*` or an owned `std::string` (raw SQL). On commit they are run **in append order** under one MySQL transaction (`MySQLConnection::ExecuteTransaction`, cpp:382).
- **Atomicity** — `MySQLConnection::ExecuteTransaction` runs `START TRANSACTION` + queries + `COMMIT`. On any error from a single query, it `ROLLBACK`s and returns the MySQL errno (cpp:411-415).
- **Deadlock retry** — for `CommitTransaction` (async): on `ER_LOCK_DEADLOCK`, `TransactionTask::Execute` re-tries the whole transaction under a global `_deadlockLock` mutex, polling for up to 1 minute (`Transaction.cpp:103-122`). This serialises retries across async workers so they don't keep deadlocking each other.
- **Sync deadlock retry** — `DirectCommitTransaction` retries up to 5 times inline (`DatabaseWorkerPool.cpp:317-324`).
- **Single-query transactions** — in `ACORE_DEBUG` builds, `CommitTransaction` logs a warning when the transaction has 0 or 1 queries (`DatabaseWorkerPool.cpp:259-269`); for size 0 it short-circuits without enqueueing.
- **Cleanup** — `~TransactionBase` (`Transaction.h:40`) calls `Cleanup()`, which `delete`s every owned prepared-statement pointer and clears strings (`Transaction.cpp:50-94`). Therefore: never reuse a `PreparedStatement*` after appending it. The transaction owns it.
- **`ExecuteOrAppend(trans, x)`** — the helper that means "if a valid transaction handle is supplied, append to it; otherwise just `Execute(x)` standalone." Pattern used when a function wants to participate in a caller-provided transaction or run independently.

## Flow / data shape

### Async transaction (the standard pattern)

```cpp
// src/server/game/Entities/Player/Player.cpp:2510 (and ~30 other call sites)
CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();

// Mix raw SQL and prepared statements freely:
auto stmt = CharacterDatabase.GetPreparedStatement(CHAR_DEL_GIFT);
stmt->SetData(0, lowGuid);
trans->Append(stmt);                                // owns the stmt now

trans->Append("DELETE FROM character_inventory WHERE guid = {}", lowGuid);

CharacterDatabase.CommitTransaction(trans);
// trans is consumed; on async deadlock TransactionTask retries up to 1 min
```

### Async with completion callback

```cpp
auto cb = CharacterDatabase.AsyncCommitTransaction(trans);
cb.AfterComplete([](bool ok) { /* invoked once future is set */ });
// owner adds cb to its AsyncCallbackProcessor<TransactionCallback>;
// see WorldSession.h:1165 _transactionCallbacks
```

### Sync (rare; startup or test code)

```cpp
// Returns once MySQL has COMMITed (or after 5 retries on deadlock).
CharacterDatabase.DirectCommitTransaction(trans);
```

### Element flow

```
BeginTransaction()
   └─ make_shared<Transaction<CharacterDatabaseConnection>>()

trans->Append(stmt) / trans->Append("UPDATE …", args)
   └─ m_queries.emplace_back({.element = stmt|string, .type = PREPARED|RAW})

CommitTransaction(trans)                       // async
   └─ Enqueue(new TransactionTask(trans))
   └─ async worker:
       └─ TransactionTask::Execute()
           └─ MySQLConnection::ExecuteTransaction(trans)
               BEGIN
               for each SQLElementData:
                   conn->Execute(stmt|sql) ; abort+ROLLBACK on error
               COMMIT
           └─ on ER_LOCK_DEADLOCK: lock _deadlockLock, retry loop ≤ 1 min
           └─ on permanent failure: trans->Cleanup() (frees owned stmts)
```

## Hooks & extension points

- Modules wanting atomic writes use the same `BeginTransaction`/`Append`/`CommitTransaction` triple — no engine plumbing needed.
- A function that may be called inside or outside an existing transaction should accept `SQLTransaction<T>& trans` and use `pool.ExecuteOrAppend(trans, x)` (see `DatabaseWorkerPool.cpp:553-569`). This is the idiomatic "compose-friendly" pattern in the engine (cf. many `Player::Save…` helpers).
- For a custom DB type, define a `Transaction<NewConnection>` typedef in your header and use the existing `TransactionTask` machinery — no new task class needed.

## Cross-references

- Engine-side: [`02-prepared-statements.md`](./02-prepared-statements.md), [`03-async-vs-sync.md`](./03-async-vs-sync.md), [`06-connection-pool.md`](./06-connection-pool.md)
- Project-side: [`../../02-architecture.md#db-access`](../../02-architecture.md)
- Doxygen: `classTransactionBase.html`, `classTransactionTask.html`, `classMySQLConnection.html`
- Wiki: `wiki/common-errors` (deadlock + reconnect codes)
