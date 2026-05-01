# 02 — Server-Architektur

## Zwei Executables

- **authserver** (`src/server/apps/authserver/`) — Auth + Realm-Auswahl, Port **3724**.
- **worldserver** (`src/server/apps/worldserver/`) — Gameplay, Port **8085**.

## Drei Datenbanken

| DB | Inhalt |
|----|--------|
| `acore_auth` | Accounts, Realmliste, Bans |
| `acore_characters` | Charakterdaten, Inventare, Fortschritt, **Paragon-Tabellen** |
| `acore_world` | Spielinhalte: Creatures, Items, Quests, Spells, Loot, **DBC-Overrides** |

Vollständige Spaltenliste: `mysqldbextracts/mysql_column_list_all.txt` (304 Tabellen, 4129 Spalten).

## Source-Layout (`azerothcore-wotlk/src/`)

```
src/
├── common/         # Networking (Asio), Crypto, Logging, Threading, MMaps
├── server/
│   ├── game/       # ~52 Subsysteme — Spells, Entities (Player/Creature/Unit/Item),
│   │               # Maps, Handlers, AI, Combat, Loot, Quests, Groups, Guilds,
│   │               # Battlegrounds, DungeonFinding, DataStores (DBC), Conditions, ...
│   ├── scripts/    # Content-Scripts (Bosse, Spells, GM-Commands, Instanzen)
│   ├── database/   # DB-Abstraktion + Schema-Updater
│   └── shared/     # Auth↔World gemeinsame Packets/Network
└── test/           # GTest-Unit-Tests
```

### Key-Subsysteme in `src/server/game/`

| Subsystem | Zweck |
|-----------|-------|
| Entities/ | `Player`, `Creature`, `Unit`, `Item`, `GameObject` |
| Spells/ | Spell-Mechaniken, Aura-System, Effekte |
| Scripting/ | `ScriptMgr`, `ScriptObject`-Subclasses, Hook-System |
| Handlers/ | Client-Packet-Handler (Methoden auf `WorldSession`) |
| DataStores/ | DBC-Loading (siehe [03-spell-system.md](./03-spell-system.md)) |
| Conditions/ | DB-getriebene Condition-Logik |
| Loot/ | Loot-Generierung |
| Globals/ | `ObjectMgr` und globale Caches |

## Scripts-Layout (`src/server/scripts/`)

```
Commands/        # GM-Commands (cs_*.cpp)
Spells/          # spell_dk.cpp, spell_mage.cpp, ... (per Klasse)
EasternKingdoms/ Kalimdor/ Northrend/ Outland/   # Zonen, Dungeons, Raids
World/ Events/ Pet/ OutdoorPvP/ Custom/
```

Custom-Module liegen NICHT hier, sondern in `modules/` (siehe unten).

## Modul-System

External-Module unter `modules/<name>/`. Beim CMake-Build werden alle gefundenen Module statisch oder dynamisch eingebunden:

```
CMake-Phase
  └─ modules/CMakeLists.txt
     └─ GetModuleSourceList()
        └─ ConfigureScriptLoader() → generiert ModulesLoader.cpp
            ├─ Forward-Declarations aller AddXXXScripts()
            └─ AddModulesScripts() ruft alle Loader auf
Server-Start
  └─ ScriptMgr::Initialize()
     └─ AddModulesScripts() → Addmod_paragonScripts() / Addmod_loot_filterScripts() / ...
```

**Loader-Naming-Konvention**: Modul-Verzeichnisname mit `-` → `_`.
- `mod-paragon` → `Addmod_paragonScripts()`
- `mod-paragon-itemgen` → `Addmod_paragon_itemgenScripts()`
- `mod-loot-filter` → `Addmod_loot_filterScripts()`

Ein Modul deaktivieren: `-DDISABLED_AC_MODULES="mod-foo;mod-bar"`.

Standard-Modul-Layout:
```
modules/mein-modul/
├── CMakeLists.txt        # optional, Auto-Detection
├── conf/
│   └── mein_modul.conf.dist
├── data/sql/
│   ├── db-world/
│   └── db-characters/
├── src/
│   ├── mein_modul_loader.cpp     # AddXXXScripts()
│   └── MeinModul.cpp
└── include.sh                     # SQL-Pfade fürs Auto-Update
```

## Hook-System (`ScriptMgr`)

Definiert in `src/server/game/Scripting/ScriptMgr.h`. Wichtige Hook-Klassen für Custom-Module:

| Hook-Klasse | Typische Hooks |
|-------------|----------------|
| `WorldScript` | `OnAfterConfigLoad`, `OnStartup`, `OnShutdown`, `OnUpdate` |
| `PlayerScript` | `OnLogin`, `OnLogout`, `OnLootItem`, `OnLevelChanged`, `OnMapChanged`, `OnCheckReagent`, `OnConsumeReagent`, `OnCanSendError*`, ... |
| `UnitScript` | `OnDamage`, `OnHeal`, `OnAuraApply`, `OnAuraRemove` |
| `CreatureScript` | Gossip-Hooks (`OnGossipHello`, `OnGossipSelect`), AI-Factory |
| `SpellScript` / `AuraScript` | Spell/Aura-Lifecycle (siehe [03-spell-system.md](./03-spell-system.md)) |
| `CommandScript` | `.foo` GM-Commands (`GetCommands()` → `ChatCommandTable`) |
| `ItemScript`, `GameObjectScript`, `InstanceMapScript` | Item-Use, GO-Use, Instance-Logic |

## Logging-Framework

```cpp
LOG_ERROR("category", "Msg with {} formatting", var);
LOG_WARN("category", "...");
LOG_INFO("category", "...");
LOG_DEBUG("category", "...");
LOG_TRACE("category", "...");
```

Standard-Kategorien: `network`, `network.opcode`, `server`, `sql.sql`, `misc`. Custom-Module nutzen idiomatisch ihren Modulnamen, z.B. `LOG_INFO("mod-paragon", "...")`.

## DB-Zugriff

- **Prepared Statements überall** — `CharacterDatabasePreparedStatement*`, `WorldDatabasePreparedStatement*`, `LoginDatabasePreparedStatement*`.
- Statement-IDs als Enums (`CHAR_SEL_*`, `CHAR_INS_*`, `CHAR_UPD_*`, `CHAR_DEL_*`).
- Async: `CharacterDatabase.Execute(stmt)` (fire-and-forget).
- Transaktionen: `CharacterDatabase.BeginTransaction()` → `CommitTransaction(trans)`.

## SQL-Datei-Ablage in azerothcore-wotlk

| Pfad | Zweck |
|------|-------|
| `data/sql/updates/pending_db_world/` (+ `pending_db_characters/`, `pending_db_auth/`) | **Neue SQL-Änderungen** mit Random-Filenames |
| `data/sql/updates/db_world/` (+ andere) | Nach PR-Merge |
| `data/sql/base/...` | Initiale Schemas — **niemals in PRs ändern** |
| `data/sql/archive/` | Alte archivierte Updates |

In Custom-Modulen liegen SQL-Files unter `data/sql/db-world/` bzw. `data/sql/db-characters/` und werden via `include.sh` registriert.

## Build-Befehle

```bash
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/azeroth-server \
         -DCMAKE_BUILD_TYPE=RelWithDebInfo \
         -DSCRIPTS=static -DMODULES=static
make -j$(nproc)
make install
```

CMake 3.16–3.22, Compiler: clang-15+/gcc-14+. Wichtige Flags:
- `SCRIPTS`: none/static/dynamic/minimal-* (default: static)
- `MODULES`: none/static/dynamic (default: static)
- `BUILD_TESTING=ON` aktiviert GTest
- `USE_COREPCH` / `USE_SCRIPTPCH` (default: ON)

Build wird mit `-Werror` kompiliert — Warnungen sind Errors.

> Hinweis für KI: **nicht** ungefragt builden — der Build dauert lang. Nur auf expliziten Userwunsch.
