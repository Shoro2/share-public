# CLAUDE.md

Zentrale Informationsgrundlage für KI-Assistenten am Custom WoW Server (WotLK 3.3.5a, AzerothCore-basiert). **Diese Datei ist nur ein Wegweiser** — die eigentlichen Inhalte liegen thematisch geteilt in `docs/`. Lade jeweils nur die Dokumente, die du für deine Aufgabe brauchst.

## Lese-Strategie für KI

> Lies **niemals** alle Dokumente am Stück. Springe gezielt nach Thema. Vollständige Strategie: [docs/08-ai-workflow.md](./docs/08-ai-workflow.md).

## Doc-Index

| Datei | Inhalt |
|-------|--------|
| [docs/01-repos.md](./docs/01-repos.md) | Alle 7 Repos im Detail, share-public-Verzeichnisstruktur, Python-Scripts |
| [docs/02-architecture.md](./docs/02-architecture.md) | Server-Architektur (auth/world), 3 Datenbanken, Quellcode-Layout |
| [docs/03-spell-system.md](./docs/03-spell-system.md) | SpellScript/AuraScript, Proc-System, DBC-Lade-Mechanik, Override-Pfade |
| [docs/04-aio-framework.md](./docs/04-aio-framework.md) | AIO Server↔Client UI-Kommunikation, Handler-Pattern, Client-Addon |
| [docs/05-modules.md](./docs/05-modules.md) | Modul-System, Custom Spells, Paragon, Itemgen, Loot-Filter, Endless Storage |
| [docs/06-custom-ids.md](./docs/06-custom-ids.md) | Spell-/Item-/NPC-/Enchant-IDs des Projekts |
| [docs/07-codestyle.md](./docs/07-codestyle.md) | C++/SQL/Lua Code-Style, CI-Anforderungen |
| [docs/08-ai-workflow.md](./docs/08-ai-workflow.md) | AI-Workflow, Lese-/Schreibstrategie, Logging-Pflicht |
| [docs/09-db-tables.md](./docs/09-db-tables.md) | DB-Tabellen-Inventar nach Kategorie (Custom + AzerothCore) |
| [docs/10-dbc-inventory.md](./docs/10-dbc-inventory.md) | DBC-Datei-Inventar (246 Dateien) nach Kategorie |

## Repo-Karte

| Repo | Zweck | Pfad lokal |
|------|-------|------------|
| `azerothcore-wotlk` | Server-Core (C++17, CMake, MySQL) | `/home/user/azerothcore-wotlk` |
| `mod-paragon` | Account-weites Paragon-Level + Stat-Punkte | `/home/user/mod-paragon` |
| `mod-paragon-itemgen` | 5-Slot Bonus-Enchantments auf Items | `/home/user/mod-paragon-itemgen` |
| `mod-loot-filter` | Charakter-spezifische Loot-Filter | `/home/user/mod-loot-filter` |
| `mod-endless-storage` | Unendliches Lager pro Charakter | `/home/user/mod-endless-storage` |
| `mod-auto-loot` | Automatisches Looten | `/home/user/mod-auto-loot` |
| `mod-ale` | (siehe Repo-CLAUDE.md) | `/home/user/mod-ale` |
| `share-public` | **Dieses Repo** — Doku, DBCs, DB-Extrakte, AIO, Python-Tools | `/home/user/share-public` |

Jedes Modul-Repo hat eine eigene kurze `CLAUDE.md` mit Modul-spezifischen Details.

## Build (Schnellreferenz)

```bash
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/azeroth-server \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DSCRIPTS=static -DMODULES=static
make -j$(nproc)
make install
```

Module werden automatisch erkannt, wenn sie in `azerothcore-wotlk/modules/` liegen (Symlink oder Clone). Details: [docs/02-architecture.md](./docs/02-architecture.md).

## Konventionen (Pflicht)

- **Branch**: `claude/<beschreibung>-<sessionId>` pro Repo
- **Logging**: jede Änderung → `claude_log.md` (Zeitstempel ISO 8601, Repo, Beschreibung, Dateien, Commit-Hash)
- **Pläne**: ebenfalls in `claude_log.md` unter separater Sektion
- **Commits**: Conventional Commits (`feat(Core/Spells): ...`, `fix(DB/SAI): ...`, `docs: ...`)
- **Sprache**: Logs in Deutsch, Code-Kommentare Englisch

Vollständige AI-Workflow-Regeln: [docs/08-ai-workflow.md](./docs/08-ai-workflow.md).
