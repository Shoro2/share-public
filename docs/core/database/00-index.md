# database/ — MySQL access layer

> The three-pool DB architecture (`WorldDatabase`, `CharacterDatabase`, `LoginDatabase`), prepared statements, async vs. sync queries, query holders, transactions, and the schema/update mechanism.

## Topic files

| File | Topic |
|---|---|
| [`01-database-env.md`](./01-database-env.md) | Three global pools exposed via `DatabaseEnv.h`, separation of concerns |
| [`02-prepared-statements.md`](./02-prepared-statements.md) | `*DatabasePreparedStatement`, statement enum naming (`CHAR_SEL_*` etc.), parameter binding |
| [`03-async-vs-sync.md`](./03-async-vs-sync.md) | `Execute` (fire-and-forget), `Query` (sync), `AsyncQuery` (callback), `DirectExecute` |
| [`04-query-holders.md`](./04-query-holders.md) | `SQLQueryHolder<T>`, `SQLQueryHolderTask`, `SQLQueryHolderCallback`, batch login pattern |
| [`05-transactions.md`](./05-transactions.md) | `BeginTransaction()`, `CommitTransaction()`, atomic multi-statement updates |
| [`06-connection-pool.md`](./06-connection-pool.md) | `MySQLConnection`, `DatabaseWorkerPool`, sync vs. async connection slots |
| [`07-update-mechanism.md`](./07-update-mechanism.md) | `data/sql/updates/`, `Updater`, hash tracking, run-on-startup |
| [`08-schema-policy.md`](./08-schema-policy.md) | `base/` vs `updates/` vs `pending_*/` vs `archive/`, what to edit when |

## Critical files

| File | Role |
|---|---|
| `src/server/database/Database/DatabaseEnv.h` | Pool typedefs (lines 18–39) |
| `src/server/database/Database/DatabaseWorkerPool.{h,cpp}` | Pool template, worker dispatch |
| `src/server/database/Database/MySQLConnection.{h,cpp}` | Single MySQL connection, sync/async flags |
| `src/server/database/Database/PreparedStatement.{h,cpp}` | Parameter variant, `SetData<T>` |
| `src/server/database/Database/QueryHolder.{h,cpp}` | Multi-statement async batches |
| `src/server/database/Database/Transaction.{h,cpp}` | Multi-statement atomic ops |
| `src/server/database/Database/Implementation/WorldDatabase.h` | `enum WorldDatabaseStatements` |
| `src/server/database/Database/Implementation/CharacterDatabase.h` | `enum CharacterDatabaseStatements` |
| `src/server/database/Database/Implementation/LoginDatabase.h` | `enum LoginDatabaseStatements` |
| `src/server/database/Updater/*` | Schema migrator |
| `data/sql/base/db_{auth,characters,world}/` | Initial schemas (do not edit in PRs) |
| `data/sql/updates/{,pending_}db_{auth,characters,world}/` | Migrations |

## Cross-references

- Engine-side: [`../entities/10-object-mgr.md`](../entities/10-object-mgr.md) (heaviest DB consumer at startup), [`../architecture/04-threading.md`](../architecture/04-threading.md) (DB worker threads)
- Project-side: [`../../02-architecture.md#db-access`](../../02-architecture.md), [`../../09-db-tables.md`](../../09-db-tables.md) (table inventory)
- Fork-specific: `azerothcore-wotlk/functions.md` (DB setup commands)
- External: `wiki/Dealing-with-SQL-files`, `wiki/Upgrade-from-pre-2.0.0-to-latest-master`, `wiki/Upgrade-from-pre-3.0.0-to-latest-master`, `wiki/common-errors`
