# database — Schema updater (`DBUpdater` + `UpdateFetcher`)

> Startup-time machinery that auto-creates the three databases, populates them from `data/sql/base/`, and applies all `data/sql/updates/...` migrations whose hash isn't yet in the `updates` table. Cross-link: [`08-schema-policy.md`](./08-schema-policy.md) for **what** to put where; this file is about **how** it runs.

## Critical files

| File | Role |
|---|---|
| `src/server/database/Database/DatabaseLoader.h:32` | `class DatabaseLoader` — orchestrator |
| `src/server/database/Database/DatabaseLoader.h:44-53` | `enum DatabaseTypeFlags { DATABASE_LOGIN = 1, DATABASE_CHARACTER = 2, DATABASE_WORLD = 4, DATABASE_MASK_ALL = 7 }` |
| `src/server/database/Database/DatabaseLoader.cpp:46-50` | Ctor reads `Updates.AutoSetup` and `Updates.EnableDatabases` (mask) |
| `src/server/database/Database/DatabaseLoader.cpp:52-171` | `AddDatabase(pool, name)` — pushes 4 lazy lambdas: `_open`, `_populate`, `_update`, `_prepare` |
| `src/server/database/Database/DatabaseLoader.cpp:106-113` | Auto-create DB on `ER_BAD_DB_ERROR` if `Updates.AutoSetup=1` |
| `src/server/database/Database/DatabaseLoader.cpp:173-191` | `Load()` — runs the four phases in order |
| `src/server/database/Updater/DBUpdater.h:68` | `template<class T> class DBUpdater` — per-pool static helpers |
| `src/server/database/Updater/DBUpdater.cpp:68-164` | Per-DB specialisations: `GetConfigEntry()`, `GetTableName()`, `GetBaseFilesDirectory()`, `GetDBModuleName()` |
| `src/server/database/Updater/DBUpdater.cpp:174-221` | `Create(pool)` — `CREATE DATABASE` via shelled-out mysql binary |
| `src/server/database/Updater/DBUpdater.cpp:360-430` | `Populate(pool)` — applies every `*.sql` in `data/sql/base/db_<name>/` if the DB has zero tables |
| `src/server/database/Updater/DBUpdater.cpp:224-296` | `Update(pool, modulesList)` — guards `updates`/`updates_include` exist, runs `UpdateFetcher` |
| `src/server/database/Updater/DBUpdater.cpp:439/445` | `Apply(pool, query)` / `ApplyFile(pool, path)` — sync execute or shell-out to `mysql` CLI |
| `src/server/database/Updater/UpdateFetcher.h:42` | `class UpdateFetcher` — file-list + hash-diff logic |
| `src/server/database/Updater/UpdateFetcher.h:71-78` | `enum State { RELEASED, CUSTOM, PENDING, MODULE, ARCHIVED }` |
| `src/server/database/Updater/UpdateFetcher.h:80-127` | `struct AppliedFileEntry` (one row of the `updates` table) |
| `src/server/database/Updater/UpdateFetcher.cpp:64-72` | `GetFileList()` — walks every directory in `updates_include` |
| `src/server/database/Updater/UpdateFetcher.cpp:74-103` | `FillFileListRecursively` — depth ≤ 10, dedupes by filename |
| `src/server/database/Database/DatabaseLoader.cpp:67-77` | Reads `<Name>Database.WorkerThreads` / `SynchThreads` |
| `data/sql/base/db_world/updates.sql` | Schema of `updates` table (`name`, `hash`, `state`, `timestamp`, `speed`) |
| `data/sql/base/db_world/updates_include.sql` | Schema of `updates_include` (`path`, `state`) |

## Key concepts

- **Per-DB module name** — `LoginDatabase` → `auth`; `WorldDatabase` → `world`; `CharacterDatabase` → `characters` (`DBUpdater.cpp:97/130/163`). Used to compose `data/sql/updates/db_<modulename>/` directory paths.
- **Four-phase boot** — `DatabaseLoader::Load()` runs in this order, all-or-nothing:
  1. `OpenDatabases()` — connects, optionally retries (`Database.Reconnect.Attempts`/`Seconds`), creates the schema if missing + AutoSetup is on.
  2. `PopulateDatabases()` — if the connection sees zero tables, slurps every `*.sql` in `data/sql/base/db_<name>/` via the external `mysql` CLI.
  3. `UpdateDatabases()` — runs the `UpdateFetcher` differential.
  4. `PrepareStatements()` — invokes `pool.PrepareStatements()` (which calls `DoPrepareStatements()` on every connection).
- **`updates` table** — primary key `name` (filename), `hash` (SHA-1 of the SQL bytes), `state` enum (`RELEASED`/`CUSTOM`/`PENDING`/`MODULE`/`ARCHIVED`), `timestamp`, `speed_ms`. The fetcher reads this, compares to the on-disk file list, applies the missing ones, and records each application.
- **`updates_include` table** — list of relative paths that the fetcher walks. Default rows seed `$/data/sql/updates/db_<name>/`, `$/data/sql/updates/pending_db_<name>/`, `$/data/sql/custom/db_<name>/`, etc. (`$` = source directory). Modules add their own `data/sql/db-world/` (etc.) by inserting a `MODULE`-state row at install time.
- **State transitions** —
  - `PENDING`: applied from `pending_db_*/` (PR staging).
  - `RELEASED`: applied from `updates/db_*/` (post-merge migrations).
  - `ARCHIVED`: SQL was once applied but moved to `archive/db_*/`. With `Updates.ArchivedRedundancy=0` the fetcher tolerates an `ARCHIVED` row missing on disk; with it on, mismatches re-apply.
  - `CUSTOM`: applied from `data/sql/custom/db_*/`.
  - `MODULE`: applied from a module's own `data/sql/db-<name>/`.
- **Hash & rehash** — with `Updates.AllowRehash=1` (default) the fetcher recomputes the hash for each on-disk file; if it changed and the row exists, it just updates the hash without re-running. With `Updates.Redundancy=1` (default) it warns when a tracked update file is missing on disk.
- **Cleaning dead refs** — `Updates.CleanDeadRefMaxCount` caps how many "missing on disk" rows the fetcher will delete in one boot (default 3) — guards against accidentally wiping rows when an `updates_include` row was misconfigured.
- **Update file naming** — `YYYY_MM_DD_NN.sql` (e.g. `2025_01_05_03.sql`). Sort order is the apply order. PR-staging files use `pending_db_*/rev_<unix-ns>.sql`, generated by `data/sql/updates/pending_db_world/create_sql.sh` — they are renamed to `YYYY_MM_DD_NN.sql` on merge.
- **`mysql` binary** — `ApplyFile` shells out to the system `mysql` CLI (configured via `MySQLExecutable` in `*.conf`). `DBUpdaterUtil::CheckExecutable()` (`DBUpdater.cpp:40`) verifies it on boot and aborts if missing.

## Flow / data shape

```
worldserver / authserver main()
   └─ DatabaseLoader loader("server", DATABASE_MASK_ALL, modulesList)
   └─ loader.AddDatabase(LoginDatabase,     "Login")    // _open, _populate, _update, _prepare
   └─ loader.AddDatabase(WorldDatabase,     "World")
   └─ loader.AddDatabase(CharacterDatabase, "Character")
   └─ loader.Load()
        ├─ Process(_open)        for each pool: SetConnectionInfo(dsn, async, sync), pool.Open()
        │     └─ on ER_BAD_DB_ERROR + AutoSetup: DBUpdater<T>::Create(pool) (CREATE DATABASE …)
        │     └─ on CR_CONNECTION_ERROR: retry up to Database.Reconnect.Attempts
        ├─ Process(_populate)    if "SHOW TABLES" empty: DBUpdater<T>::Populate(pool)
        │                              └─ shells out: mysql … < base/db_<name>/*.sql (sorted)
        ├─ Process(_update)      DBUpdater<T>::Update(pool, modules)
        │     ├─ ensure `updates` and `updates_include` tables exist
        │     ├─ UpdateFetcher.Update(redundancy, allowRehash, archivedRedundancy, cleanMax)
        │     │     ├─ ReceiveIncludedDirectories()  — read `updates_include`
        │     │     ├─ for each dir, FillFileListRecursively() (.sql files only, depth ≤ 10)
        │     │     ├─ ReceiveAppliedFiles()          — read `updates`
        │     │     ├─ for each on-disk file not yet applied (or hash-mismatched):
        │     │     │     Apply (ad-hoc query) or ApplyFile (mysql CLI), insert/update row
        │     │     └─ CleanUp() — delete rows for files that vanished on disk
        │     └─ logs "X new and Y archived updates" / "up-to-date"
        └─ Process(_prepare)     pool.PrepareStatements() (see 06-connection-pool.md)
```

### Config knobs (worldserver.conf.dist; authserver mirrors them)

| Option | Default | Effect |
|---|---|---|
| `Updates.EnableDatabases` | `7` | Bitmask: `1`=Login, `2`=Character, `4`=World. Set to 0 to skip the updater entirely. |
| `Updates.AutoSetup` | `1` | If on, missing DB triggers `CREATE DATABASE`. |
| `Updates.Redundancy` | `1` | Warn when a previously applied update is missing on disk. |
| `Updates.ArchivedRedundancy` | `0` | Also enforce hash for archived files. |
| `Updates.AllowRehash` | `1` | Update hash row when the on-disk file changes (no re-apply). |
| `Updates.CleanDeadRefMaxCount` | `3` | Cap on rows to delete per boot when files vanished. |
| `Updates.ExceptionShutdownDelay` | `10000` ms | Pause before aborting on update failure. |

## Hooks & extension points

- **Modules** add their schema by inserting an `updates_include` row pointing at the module's `data/sql/db-<name>/` folder. Convention: each module ships an `include.sh` (sourced from `apps/bash_shared/common.sh:22`) that registers the path; the row's `state` column is `MODULE`. Module SQL files use the same `YYYY_MM_DD_NN.sql` naming and are deduped against the `updates` table.
- **PRs** drop a single `pending_db_*/rev_<ns>.sql` (file produced by `data/sql/updates/pending_db_*/create_sql.sh`); on merge, a maintainer renames it to `YYYY_MM_DD_NN.sql` and moves it to `updates/db_*/`. See [`08-schema-policy.md`](./08-schema-policy.md).
- A re-applicable script (idempotent — `CREATE TABLE IF NOT EXISTS`, `REPLACE INTO`, etc.) goes under `data/sql/custom/db_<name>/`. The fetcher gives it `CUSTOM` state and applies it whenever its hash changes.

## Cross-references

- Engine-side: [`08-schema-policy.md`](./08-schema-policy.md), [`06-connection-pool.md`](./06-connection-pool.md), [`../architecture/02-startup.md`](../architecture/02-startup.md)
- Project-side: [`../../02-architecture.md#sql-file-layout-in-azerothcore-wotlk`](../../02-architecture.md), [`../../05-modules.md`](../../05-modules.md)
- Doxygen: `classDatabaseLoader.html`, `classDBUpdater.html`, `classUpdateFetcher.html`
- Wiki: `wiki/Dealing-with-SQL-files`, `wiki/Upgrade-from-pre-2.0.0-to-latest-master`, `wiki/Upgrade-from-pre-3.0.0-to-latest-master`, `wiki/common-errors`
