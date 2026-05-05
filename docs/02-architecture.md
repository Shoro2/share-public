# 02 — Server architecture

## Two executables

- **authserver** (`src/server/apps/authserver/`) — auth + realm selection, port **3724**.
- **worldserver** (`src/server/apps/worldserver/`) — gameplay, port **8085**.

## Three databases

| DB | Contents |
|----|--------|
| `acore_auth` | accounts, realm list, bans |
| `acore_characters` | character data, inventories, progression, **Paragon tables** |
| `acore_world` | game content: creatures, items, quests, spells, loot, **DBC overrides** |

Full column list: `mysqldbextracts/mysql_column_list_all.txt` (304 tables, 4129 columns).

## Source layout (`azerothcore-wotlk/src/`)

```
src/
├── common/         # Networking (Asio), crypto, logging, threading, MMaps
├── server/
│   ├── game/       # ~52 subsystems — Spells, Entities (Player/Creature/Unit/Item),
│   │               # Maps, Handlers, AI, Combat, Loot, Quests, Groups, Guilds,
│   │               # Battlegrounds, DungeonFinding, DataStores (DBC), Conditions, ...
│   ├── scripts/    # Content scripts (bosses, spells, GM commands, instances)
│   ├── database/   # DB abstraction + schema updater
│   └── shared/     # Auth↔World shared packets/network
└── test/           # GTest unit tests
```

### Key subsystems in `src/server/game/`

| Subsystem | Purpose |
|-----------|-------|
| Entities/ | `Player`, `Creature`, `Unit`, `Item`, `GameObject` |
| Spells/ | spell mechanics, aura system, effects |
| Scripting/ | `ScriptMgr`, `ScriptObject` subclasses, hook system |
| Handlers/ | client packet handlers (methods on `WorldSession`) |
| DataStores/ | DBC loading (see [03-spell-system.md](./03-spell-system.md)) |
| Conditions/ | DB-driven condition logic |
| Loot/ | loot generation |
| Globals/ | `ObjectMgr` and global caches |

## Scripts layout (`src/server/scripts/`)

```
Commands/        # GM commands (cs_*.cpp)
Spells/          # spell_dk.cpp, spell_mage.cpp, ... (per class)
EasternKingdoms/ Kalimdor/ Northrend/ Outland/   # zones, dungeons, raids
World/ Events/ Pet/ OutdoorPvP/ Custom/
```

Custom modules do NOT live here, but in `modules/` (see below).

## Module system

External modules under `modules/<name>/`. The CMake build statically or dynamically integrates all detected modules:

```
CMake phase
  └─ modules/CMakeLists.txt
     └─ GetModuleSourceList()
        └─ ConfigureScriptLoader() → generates ModulesLoader.cpp
            ├─ forward declarations of all AddXXXScripts()
            └─ AddModulesScripts() calls all loaders
Server start
  └─ ScriptMgr::Initialize()
     └─ AddModulesScripts() → Addmod_paragonScripts() / Addmod_loot_filterScripts() / ...
```

**Loader naming convention**: module directory name with `-` → `_`.
- `mod-paragon` → `Addmod_paragonScripts()`
- `mod-paragon-itemgen` → `Addmod_paragon_itemgenScripts()`
- `mod-loot-filter` → `Addmod_loot_filterScripts()`

Disable a module: `-DDISABLED_AC_MODULES="mod-foo;mod-bar"`.

Standard module layout:
```
modules/my-module/
├── CMakeLists.txt        # optional, auto-detection
├── conf/
│   └── my_module.conf.dist
├── data/sql/
│   ├── db-world/
│   └── db-characters/
├── src/
│   ├── my_module_loader.cpp     # AddXXXScripts()
│   └── MyModule.cpp
└── include.sh                    # SQL paths for auto-update
```

## Hook system (`ScriptMgr`)

Defined in `src/server/game/Scripting/ScriptMgr.h`. Important hook classes for custom modules:

| Hook class | Typical hooks |
|-------------|----------------|
| `WorldScript` | `OnAfterConfigLoad`, `OnStartup`, `OnShutdown`, `OnUpdate` |
| `PlayerScript` | `OnLogin`, `OnLogout`, `OnLootItem`, `OnLevelChanged`, `OnMapChanged`, `OnCheckReagent`, `OnConsumeReagent`, `OnCanSendError*`, ... |
| `UnitScript` | `OnDamage`, `OnHeal`, `OnAuraApply`, `OnAuraRemove` |
| `CreatureScript` | gossip hooks (`OnGossipHello`, `OnGossipSelect`), AI factory |
| `SpellScript` / `AuraScript` | spell/aura lifecycle (see [03-spell-system.md](./03-spell-system.md)) |
| `CommandScript` | `.foo` GM commands (`GetCommands()` → `ChatCommandTable`) |
| `ItemScript`, `GameObjectScript`, `InstanceMapScript` | item-use, GO-use, instance logic |

## Logging framework

```cpp
LOG_ERROR("category", "Msg with {} formatting", var);
LOG_WARN("category", "...");
LOG_INFO("category", "...");
LOG_DEBUG("category", "...");
LOG_TRACE("category", "...");
```

Standard categories: `network`, `network.opcode`, `server`, `sql.sql`, `misc`. Custom modules idiomatically use their module name, e.g. `LOG_INFO("mod-paragon", "...")`.

## DB access

- **Prepared statements everywhere** — `CharacterDatabasePreparedStatement*`, `WorldDatabasePreparedStatement*`, `LoginDatabasePreparedStatement*`.
- Statement IDs as enums (`CHAR_SEL_*`, `CHAR_INS_*`, `CHAR_UPD_*`, `CHAR_DEL_*`).
- Async: `CharacterDatabase.Execute(stmt)` (fire-and-forget).
- Transactions: `CharacterDatabase.BeginTransaction()` → `CommitTransaction(trans)`.

## SQL file layout in azerothcore-wotlk

| Path | Purpose |
|------|-------|
| `data/sql/updates/pending_db_world/` (+ `pending_db_characters/`, `pending_db_auth/`) | **New SQL changes** with random filenames |
| `data/sql/updates/db_world/` (+ others) | After PR merge |
| `data/sql/base/...` | Initial schemas — **never modify in PRs** |
| `data/sql/archive/` | Old archived updates |

In custom modules SQL files live under `data/sql/db-world/` or `data/sql/db-characters/` and are registered via `include.sh`.

## Build commands

```bash
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/azeroth-server \
         -DCMAKE_BUILD_TYPE=RelWithDebInfo \
         -DSCRIPTS=static -DMODULES=static
make -j$(nproc)
make install
```

CMake 3.16–3.22, compilers: clang-15+/gcc-14+. Important flags:
- `SCRIPTS`: none/static/dynamic/minimal-* (default: static)
- `MODULES`: none/static/dynamic (default: static)
- `BUILD_TESTING=ON` enables GTest
- `USE_COREPCH` / `USE_SCRIPTPCH` (default: ON)

The build is compiled with `-Werror` — warnings are errors.

> Note for AI: **do not** build unprompted — the build takes a long time. Only on explicit user request.
