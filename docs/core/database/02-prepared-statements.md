# database — Prepared statements

> How a prepared statement is registered, indexed by enum, parameterised via `SetData<T>`, and executed against the right connection slot. Builds on [`01-database-env.md`](./01-database-env.md). For sync/async dispatch see [`03-async-vs-sync.md`](./03-async-vs-sync.md).

## Critical files

| File | Role |
|---|---|
| `src/server/database/Database/PreparedStatement.h:67` | `class PreparedStatementBase` (base, type-erased) |
| `src/server/database/Database/PreparedStatement.h:155` | `template<typename T> class PreparedStatement` (typed handle) |
| `src/server/database/Database/PreparedStatement.h:41` | `struct PreparedStatementData` — `std::variant` of all bindable scalars + `string` + `Binary` |
| `src/server/database/Database/PreparedStatement.h:76-114` | `SetData<T>` overloads (numeric / enum / string_view / nullptr / binary array / `std::chrono`) |
| `src/server/database/Database/PreparedStatement.h:117-121` | `SetArguments(args...)` — variadic positional bind |
| `src/server/database/Database/PreparedStatement.cpp:25-50` | `SetValidData` implementations — fills the variant slot at `index` |
| `src/server/database/Database/PreparedStatement.h:169` | `class PreparedStatementTask : public SQLOperation` (the enqueueable wrapper) |
| `src/server/database/Database/MySQLConnection.h:97-98` | `GetPreparedStatement(uint32 index)`, `PrepareStatement(uint32 index, sv sql, ConnectionFlags)` |
| `src/server/database/Database/MySQLConnection.cpp:505-535` | `PrepareStatement(...)` body — calls `mysql_stmt_init` + `mysql_stmt_prepare`, stores in `m_stmts[index]` |
| `src/server/database/Database/MySQLConnection.cpp:202-251` | `Execute(PreparedStatementBase*)` — `BindParameters` + `mysql_stmt_execute` |
| `src/server/database/Database/MySQLConnection.h:35-40` | `enum ConnectionFlags { CONNECTION_ASYNC = 0x1, CONNECTION_SYNCH = 0x2, CONNECTION_BOTH }` |
| `src/server/database/Database/Implementation/CharacterDatabase.h:23` | `enum CharacterDatabaseStatements : uint32` — naming-rule comment |
| `src/server/database/Database/Implementation/CharacterDatabase.cpp:21` | `void CharacterDatabaseConnection::DoPrepareStatements()` — all `PrepareStatement(...)` calls |
| `src/server/database/Database/Implementation/WorldDatabase.h:23` | `enum WorldDatabaseStatements` |
| `src/server/database/Database/Implementation/WorldDatabase.cpp:21` | `WorldDatabaseConnection::DoPrepareStatements()` |
| `src/server/database/Database/Implementation/LoginDatabase.h:23` | `enum LoginDatabaseStatements` |

## Key concepts

- **Statement enum** — a per-DB `enum *DatabaseStatements : uint32`. Each value is the index into `m_stmts[]` on every connection of that pool. Last value is always `MAX_*DATABASE_STATEMENTS` (used to size the vector at `CharacterDatabase.cpp:24`).
- **Naming convention** (enforced by header comment in each enum):
  ```
  {DB}_{SEL|INS|UPD|DEL|REP}_{Summary of data changed}
  ```
  - `DB` ∈ `CHAR`, `WORLD`, `LOGIN`. `REP` = `REPLACE INTO`. Match the enum suffix to the calling function name when the action affects multiple fields.
- **Connection flag** — third arg to `PrepareStatement(...)` decides which connection class prepares the statement: `CONNECTION_ASYNC` for fire-and-forget writes, `CONNECTION_SYNCH` for code paths that block, `CONNECTION_BOTH` if both are needed (rare; e.g. `CHAR_SEL_DATA_BY_NAME`). A statement marked async cannot be used from `Query()`; calling it on the wrong slot logs an error and returns null (`MySQLConnection.cpp:493`).
- **Index counts** (current count of `PrepareStatement(...)` calls):
  - `CharacterDatabase`: 486
  - `LoginDatabase`: 100
  - `WorldDatabase`: 89
- **`PreparedStatement<T>` vs `PreparedStatementBase`** — the typed wrapper exists only so `pool.Execute(stmt)` requires a statement of the matching pool type at compile time. The variant data lives in the base.
- **Parameter binding** — slots are 0-indexed, count fixed by `m_stmts[i]->GetParameterCount()` (set in `DatabaseWorkerPool::PrepareStatements`, see `DatabaseWorkerPool.cpp:166-172`). Out-of-range `SetData(idx, …)` `ASSERT`s.

## Flow / data shape

### Registration (once, on connection open)

```cpp
// src/server/database/Database/Implementation/CharacterDatabase.cpp
void CharacterDatabaseConnection::DoPrepareStatements()
{
    if (!m_reconnecting)
        m_stmts.resize(MAX_CHARACTERDATABASE_STATEMENTS);          // line 24

    PrepareStatement(CHAR_SEL_CHARACTER,
        "SELECT guid, account, name, ... FROM characters WHERE guid = ?",
        CONNECTION_ASYNC);                                          // line 69
    // ... 485 more
}
```
`MySQLConnection::PrepareStatement` (cpp:505) skips the call when the connection's flag mask doesn't include the requested flag — saving memory in sync-only connections.

### Per-call usage (idiomatic)

```cpp
// Async write, fire-and-forget
auto stmt = CharacterDatabase.GetPreparedStatement(CHAR_DEL_QUEST_STATUS_DAILY_CHAR);
stmt->SetData(0, lowGuid);                  // bind ? at index 0
CharacterDatabase.Execute(stmt);            // enqueue, returns immediately

// Or one-shot positional bind via variadic
auto stmt2 = CharacterDatabase.GetPreparedStatement(CHAR_INS_BATTLEGROUND_RANDOM);
stmt2->SetArguments(lowGuid);
CharacterDatabase.Execute(stmt2);

// Sync read, blocks calling thread
auto stmt3 = CharacterDatabase.GetPreparedStatement(CHAR_SEL_CHARACTER_NAME_DATA);
stmt3->SetData(0, lowGuid);
PreparedQueryResult result = CharacterDatabase.Query(stmt3);
if (result) { Field* f = result->Fetch(); /* … */ }
```

`stmt` is heap-allocated by `GetPreparedStatement(...)` (`DatabaseWorkerPool.cpp:334`) and is consumed by exactly one of `Execute` / `DirectExecute` / `Query` / `Append(trans)`. The wrapper is deleted by the task's destructor (`PreparedStatementTask::~PreparedStatementTask` in `PreparedStatement.cpp:76`). **Do not reuse a `stmt*` across calls.**

### Parameter types accepted by `SetData<T>`

| Family | Where the overload lives | Notes |
|---|---|---|
| Arithmetic (`uint8`–`int64`, `bool`, `float`, `double`) | `PreparedStatement.h:77` | Enabled via `Acore::Types::is_default<T>` |
| `enum`/`enum class` | `PreparedStatement.h:84` | Cast to `std::underlying_type_t<T>` |
| `std::string_view` | `PreparedStatement.h:90` | Stored as `std::string` |
| `nullptr` / no-arg | `PreparedStatement.h:96` | Binds SQL `NULL` |
| `std::array<uint8, N>` | `PreparedStatement.h:103` | Converted to `std::vector<uint8>` |
| `std::chrono::duration` | `PreparedStatement.h:111` | Optional `convertToUin32` (defaults true) |

## Hooks & extension points

To add a prepared statement (e.g. for a custom module embedded in core):

1. Append the enum value **before** `MAX_*DATABASE_STATEMENTS` in the relevant `Implementation/*.h`. Follow the `{DB}_{verb}_{summary}` naming rule. Example: `WORLD_SEL_PARAGON_SPEC_SPELL_ASSIGN` at `WorldDatabase.h:121`.
2. Add a matching `PrepareStatement(ENUM, "SQL ?", CONNECTION_*)` line inside `DoPrepareStatements()` in the matching `.cpp`. Pick the flag based on whether the call site uses `Execute` / `Query` / `BeginTransaction`. Example: `WorldDatabase.cpp:116`.
3. Use `pool.GetPreparedStatement(ENUM)` at the call site as shown above.

For module SQL schema additions (table creation), see [`08-schema-policy.md`](./08-schema-policy.md).

## Cross-references

- Engine-side: [`03-async-vs-sync.md`](./03-async-vs-sync.md), [`05-transactions.md`](./05-transactions.md), [`04-query-holders.md`](./04-query-holders.md)
- Project-side: [`../../02-architecture.md#db-access`](../../02-architecture.md), [`../../05-modules.md`](../../05-modules.md) (`mod-paragon-itemgen` example)
- Doxygen: `classPreparedStatementBase.html`, `classMySQLConnection.html`
- Wiki: `wiki/Dealing-with-SQL-files`
