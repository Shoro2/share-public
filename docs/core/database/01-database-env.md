# database — DatabaseEnv (the three pools)

> The three global `DatabaseWorkerPool<T>` accessors (`WorldDatabase`, `CharacterDatabase`, `LoginDatabase`) and the typedef glue that resolves their connection / statement / transaction types. Every other file in this folder builds on these. Project-side overview: [`../../02-architecture.md#three-databases`](../../02-architecture.md).

## Critical files

| File | Role |
|---|---|
| `src/server/database/Database/DatabaseEnv.h:33` | `extern DatabaseWorkerPool<WorldDatabaseConnection> WorldDatabase` |
| `src/server/database/Database/DatabaseEnv.h:35` | `extern DatabaseWorkerPool<CharacterDatabaseConnection> CharacterDatabase` |
| `src/server/database/Database/DatabaseEnv.h:37` | `extern DatabaseWorkerPool<LoginDatabaseConnection> LoginDatabase` |
| `src/server/database/Database/DatabaseEnv.cpp:20-22` | Definitions (the three globals live here) |
| `src/server/database/Database/DatabaseEnvFwd.h:31-33` | Forward decls of the three `*Connection` types |
| `src/server/database/Database/DatabaseEnvFwd.h:40-42` | `using {Char,Login,World}DatabasePreparedStatement = PreparedStatement<…Connection>` |
| `src/server/database/Database/DatabaseEnvFwd.h:69-71` | `using {Char,Login,World}DatabaseTransaction = SQLTransaction<…Connection>` |
| `src/server/database/Database/DatabaseEnvFwd.h:80-82` | `using {Char,Login,World}DatabaseQueryHolder = SQLQueryHolder<…Connection>` |
| `src/server/database/Database/Implementation/WorldDatabase.h:126` | `class WorldDatabaseConnection : public MySQLConnection` |
| `src/server/database/Database/Implementation/CharacterDatabase.h` | `class CharacterDatabaseConnection : public MySQLConnection` |
| `src/server/database/Database/Implementation/LoginDatabase.h:139` | `class LoginDatabaseConnection : public MySQLConnection` |
| `src/server/database/Database/DatabaseLoader.cpp:31-33` | Default DSN strings (`acore_auth`, `acore_characters`, `acore_world`) |

## Key concepts

- **`DatabaseWorkerPool<T>`** — templated connection pool, one async worker queue + one or more sync slots. See [`06-connection-pool.md`](./06-connection-pool.md).
- **Connection class** — a thin wrapper around one `MYSQL*` handle that owns its prepared-statement table. The three `*Connection` subclasses only override `DoPrepareStatements()`.
- **Statement enum** (`T::Statements`) — each `*Connection` typedefs `Statements` to its enum (`WorldDatabaseStatements`, etc.) so `pool.GetPreparedStatement(WORLD_SEL_X)` is type-checked. See [`02-prepared-statements.md`](./02-prepared-statements.md).
- **What goes in which DB**:
  - `LoginDatabase` (`acore_auth`) — accounts, realm list, IP/account bans, logging, autobroadcast, MOTD, TOTP secrets. ~100 prepared statements.
  - `CharacterDatabase` (`acore_characters`) — every per-character row: characters, inventory, auras, quest status, mail, guilds, channels, instances, arena teams, calendar. ~486 prepared statements (the bulk of the engine's DB traffic).
  - `WorldDatabase` (`acore_world`) — game content (read-mostly): creature/gameobject templates, spawns, loot, quests, vendors, smart_scripts, game_events, DBC overrides. ~89 prepared statements.

## Flow / data shape

How a caller resolves to a real MySQL row:

```
caller
  └─ CharacterDatabase                              // global from DatabaseEnv.h:35
       │  (DatabaseWorkerPool<CharacterDatabaseConnection>)
       │
       ├─ GetPreparedStatement(CHAR_SEL_CHARACTER)  // -> CharacterDatabasePreparedStatement*
       │     │
       │     └─ index 0..MAX_CHARACTERDATABASE_STATEMENTS-1
       │        (resolved on a connection's m_stmts[index])
       │
       ├─ Query / Execute / AsyncQuery / DelayQueryHolder
       │     │
       │     └─ picks a free CharacterDatabaseConnection
       │           └─ MySQLConnection::Execute / Query (mysql_stmt_execute)
       │
       └─ BeginTransaction / CommitTransaction
             │
             └─ TransactionTask -> async worker -> MySQLConnection::ExecuteTransaction
```

The three globals are constructed at static-init time but unusable until `DatabaseLoader` opens them at startup (see [`07-update-mechanism.md`](./07-update-mechanism.md)).

## Hooks & extension points

- Modules don't extend the three pools directly; they consume them via the globals (e.g. `CharacterDatabase.Execute(...)`).
- A module that needs a custom prepared statement appends an enum value at the bottom of the relevant enum and adds a matching `PrepareStatement(...)` line in the `*Connection::DoPrepareStatements()` body. Example in this repo: `WORLD_SEL_PARAGON_SPEC_SPELL_ASSIGN` at `WorldDatabase.h:121` (registered at `WorldDatabase.cpp:116`). Detail in [`02-prepared-statements.md`](./02-prepared-statements.md).
- A wholly new database (e.g. a logging DB) requires defining a new `*Connection` subclass + a new global pool — uncommon and out of scope here.

## Cross-references

- Engine-side: [`02-prepared-statements.md`](./02-prepared-statements.md), [`06-connection-pool.md`](./06-connection-pool.md), [`07-update-mechanism.md`](./07-update-mechanism.md), [`../architecture/04-threading.md`](../architecture/04-threading.md), [`../entities/10-object-mgr.md`](../entities/10-object-mgr.md)
- Project-side: [`../../02-architecture.md#three-databases`](../../02-architecture.md), [`../../09-db-tables.md`](../../09-db-tables.md)
- Doxygen: `classDatabaseWorkerPool.html`, `DatabaseEnv_8h.html`
- Wiki: `wiki/Dealing-with-SQL-files`
