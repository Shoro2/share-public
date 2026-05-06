# database — Query holders (multi-statement async batches)

> `SQLQueryHolder<T>` lets a caller fire N prepared statements as one async batch and receive a single callback once **all** results are ready. Used most heavily by player login. Builds on [`03-async-vs-sync.md`](./03-async-vs-sync.md).

## Critical files

| File | Role |
|---|---|
| `src/server/database/Database/QueryHolder.h:24` | `class SQLQueryHolderBase` (base) |
| `src/server/database/Database/QueryHolder.h:42` | `template<typename T> class SQLQueryHolder` (typed wrapper) |
| `src/server/database/Database/QueryHolder.h:52` | `class SQLQueryHolderTask : public SQLOperation` |
| `src/server/database/Database/QueryHolder.h:68` | `class SQLQueryHolderCallback` (callback handle) |
| `src/server/database/Database/QueryHolder.cpp:25` | `SetPreparedQueryImpl(idx, stmt*)` — append at index |
| `src/server/database/Database/QueryHolder.cpp:37` | `GetPreparedResult(idx)` — read after completion |
| `src/server/database/Database/QueryHolder.cpp:46` | `SetPreparedResult(idx, result)` — populated by the worker thread |
| `src/server/database/Database/QueryHolder.cpp:69` | `SetSize(size)` — pre-allocate the queries vector |
| `src/server/database/Database/QueryHolder.cpp:77-86` | `SQLQueryHolderTask::Execute()` — runs all statements on **one** connection |
| `src/server/database/Database/QueryHolder.cpp:88-97` | `SQLQueryHolderCallback::InvokeIfReady()` — polled by the session processor |
| `src/server/database/Database/DatabaseWorkerPool.cpp:236-244` | `pool.DelayQueryHolder(holder)` — enqueue the task, return the callback |
| `src/server/database/Database/DatabaseEnvFwd.h:80-82` | `using {Char,Login,World}DatabaseQueryHolder = SQLQueryHolder<…>` |
| `src/server/database/Database/DatabaseEnvFwd.h:84` | `class SQLQueryHolderCallback` fwd |
| `src/server/game/Server/WorldSession.h:1166` | `AsyncCallbackProcessor<SQLQueryHolderCallback> _queryHolderProcessor` |

## Key concepts

- **Holder** — a heap-shared `std::shared_ptr<SQLQueryHolder<T>>` owning a vector of `(stmt*, result)` pairs sized by `SetSize(N)`. The owner sets statement at index `i` with `SetPreparedQuery(i, stmt)`; the worker fills `result` for each `i`.
- **Index = enum** — convention: define a per-feature `enum *QueryIndex { …, MAX_*_QUERY }` and use the enum values as the holder slot indices. Login uses `enum PlayerLoginQueryIndex` (`Player.h:855`); enum holes (e.g. `_AURAS = 3` not `1`) are vestigial — `MAX_PLAYER_LOGIN_QUERY` is what `SetSize` receives.
- **Single-connection execution** — `SQLQueryHolderTask::Execute()` runs every statement on the **same** async connection it lands on (`QueryHolder.cpp:80-83`). All statements in the holder must therefore be `CONNECTION_ASYNC` or `CONNECTION_BOTH` (otherwise `m_stmts[i]` is null on the async slot — see `03-async-vs-sync.md`).
- **Callback** — `pool.DelayQueryHolder(holder)` returns an `SQLQueryHolderCallback` (move-only). The owner attaches a continuation via `.AfterComplete([](SQLQueryHolderBase const& holder){ … })` and registers it with their `AsyncCallbackProcessor`. `InvokeIfReady()` (cpp:88) is polled each tick.
- **Result access** — inside the continuation, `holder.GetPreparedResult(QUERY_INDEX)` returns the `PreparedQueryResult` (possibly null). Result objects have shared ownership; passing them to other methods is safe.

## Flow / data shape

The canonical example — player login. The handler defines a holder subclass that knows the player guid + account id and queues ~36 reads at construction:

```cpp
// src/server/game/Handlers/CharacterHandler.cpp:64
class LoginQueryHolder : public CharacterDatabaseQueryHolder
{
    uint32 m_accountId;
    ObjectGuid m_guid;
public:
    LoginQueryHolder(uint32 accountId, ObjectGuid guid)
        : m_accountId(accountId), m_guid(guid) { }
    bool Initialize();                      // builds the batch
};

// src/server/game/Handlers/CharacterHandler.cpp:78
bool LoginQueryHolder::Initialize()
{
    SetSize(MAX_PLAYER_LOGIN_QUERY);                                  // line 80
    bool res = true;
    auto lowGuid = m_guid.GetCounter();

    auto stmt = CharacterDatabase.GetPreparedStatement(CHAR_SEL_CHARACTER);
    stmt->SetData(0, lowGuid);
    res &= SetPreparedQuery(PLAYER_LOGIN_QUERY_LOAD_FROM, stmt);      // line 87
    // ... ~35 more SetPreparedQuery calls (auras, spells, quest status,
    //     reputation, inventory, mail, social, achievements, glyphs, …)
    return res;
}
```

Dispatch and callback (same file):

```cpp
// CharacterHandler.cpp:778-786
auto holder = std::make_shared<LoginQueryHolder>(GetAccountId(), playerGuid);
if (!holder->Initialize())
    return;

m_playerLoading = true;
AddQueryHolderCallback(CharacterDatabase.DelayQueryHolder(holder))
    .AfterComplete([this](SQLQueryHolderBase const& holder)
    {
        HandlePlayerLoginFromDB(static_cast<LoginQueryHolder const&>(holder));
    });
```

`HandlePlayerLoginFromDB` (cpp:789) then reads each row via `holder.GetPreparedResult(PLAYER_LOGIN_QUERY_LOAD_*)` and feeds the loaded `Player` struct.

### Lifecycle

```
construct holder (shared_ptr)
   └─ Initialize(): SetSize, build stmts, SetPreparedQuery(idx, stmt)
DelayQueryHolder(holder)
   └─ enqueue SQLQueryHolderTask(holder)
   └─ return SQLQueryHolderCallback(holder, future)
async worker thread
   └─ for i = 0..N-1: m_holder.SetPreparedResult(i, conn->Query(stmt))
   └─ promise.set_value()
session tick
   └─ _queryHolderProcessor polls callback.InvokeIfReady()
       └─ AfterComplete callback fires with holder ref
           └─ holder.GetPreparedResult(idx) -> PreparedQueryResult
```

## Hooks & extension points

- Need a multi-statement async load (e.g. guild bank load, mail-load on demand)? Subclass `CharacterDatabaseQueryHolder`/`LoginDatabaseQueryHolder`/`WorldDatabaseQueryHolder`, define an index enum, override an `Initialize()` method, queue with `pool.DelayQueryHolder(holder)` and consume via `AsyncCallbackProcessor<SQLQueryHolderCallback>` on your owner.
- Modules can use the existing pools' query holders the same way; no engine changes needed.
- The holder runs all statements on **one** async connection — if you need parallelism across multiple connections, fan out via independent `AsyncQuery(stmt)` calls instead.

## Cross-references

- Engine-side: [`03-async-vs-sync.md`](./03-async-vs-sync.md), [`02-prepared-statements.md`](./02-prepared-statements.md), [`../handlers/01-character-handler.md`](../handlers/01-character-handler.md), [`../entities/04-player.md`](../entities/04-player.md)
- Project-side: —
- Doxygen: `classSQLQueryHolderBase.html`, `classSQLQueryHolderCallback.html`
