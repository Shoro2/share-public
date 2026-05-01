# AI_GUIDE — Leitfaden für Claude Code & andere KI-Assistenten

> **Einstiegsdokument**. Lies dies zuerst. Alle Detail-Kapitel liegen in [`docs/`](./docs/).
> Diese Datei wird bewusst klein gehalten (< 8 KB) damit sie zuverlässig von KI-Tools gelesen werden kann.

## TL;DR — Was ist das Projekt?

Ein **Custom WoW-Server für WotLK 3.3.5a** auf AzerothCore-Basis mit mehreren eigenen Modulen rund um ein **Paragon-Progressionssystem** (Post-Level-80 XP/Level/Stats), **automatische Item-Enchantments**, **Loot-Filter**, **Auto-Loot** und **Material-Storage**. Die Server↔Client-Kommunikation der UIs läuft über das **AIO-Framework** (ALE/Lua + WoW-Addon).

Das Repo `share-public` ist die **zentrale Wissensbasis**: hier liegen Doku, Custom-IDs, DBC-Dateien, DB-Extrakte, Python-Tools, das AIO-Framework und der **Änderungslog** (`claude_log.md`) für alle Repos.

Der grundlegende Konzept-Pitch (mit teils veralteten Details) liegt als `Dcore Concept.pdf` im Wurzelverzeichnis dieses Repos.

## Repo-Karte (was tut welches Repo?)

| Repo | Sprache | Zweck | Detail |
|------|---------|-------|--------|
| [`share-public`](https://github.com/Shoro2/share-public) | MD/Lua/Py | Doku, Tools, AIO-Framework, DBC, Logs | dieses Repo |
| [`azerothcore-wotlk`](https://github.com/Shoro2/azerothcore-wotlk) | C++17 | Server-Core (worldserver, authserver) | [docs/02](./docs/02-architecture.md) |
| [`mod-ale`](https://github.com/Shoro2/mod-ale) | C++/Lua | **Lua-Engine** (Eluna-Fork "ALE") — Skript-Runtime für alle Lua/AIO-Module | [`mod-ale/CLAUDE.md`](https://github.com/Shoro2/mod-ale/blob/master/CLAUDE.md) |
| [`mod-paragon`](https://github.com/Shoro2/mod-paragon) | C++/Lua | Account-XP + 17-Stat-System nach LV80 | [docs/05](./docs/05-modules.md#mod-paragon) |
| [`mod-paragon-itemgen`](https://github.com/Shoro2/mod-paragon-itemgen) | C++/Lua | Auto-Enchantments auf Loot (5 Slots, Cursed) | [docs/05](./docs/05-modules.md#mod-paragon-itemgen) |
| [`mod-loot-filter`](https://github.com/Shoro2/mod-loot-filter) | C++/Lua | Regelbasiertes Auto-Sell/Disenchant/Delete | [docs/05](./docs/05-modules.md#mod-loot-filter) |
| [`mod-auto-loot`](https://github.com/Shoro2/mod-auto-loot) | C++ | AOE-Looting im 10-yd-Radius | [docs/05](./docs/05-modules.md#mod-auto-loot) |
| [`mod-endless-storage`](https://github.com/Shoro2/mod-endless-storage) | Lua/SQL | AIO-UI für unbegrenztes Material-Lager + Crafting-Reagenz-Hooks | [docs/05](./docs/05-modules.md#mod-endless-storage) |

`mod-ale` ist eine **Build- und Laufzeit-Abhängigkeit** für alle Lua/AIO-Module (mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage sowie das `share-public/AIO_Server`).

Weitere im Code referenzierte, **nicht in diesem Scope liegende** Repos: `mod-custom-spells` (Custom SpellScripts) und `mod-dungeon-challenge` (Mythic+-Style). Beide sind aktuell **nicht** Teil deiner GitHub-MCP-Berechtigungen — nur lesend über Logs/Refs sichtbar.

## Wo finde ich was?

| Frage | Datei |
|-------|-------|
| Welche Repos gibt es, was machen sie? | [`docs/01-repos.md`](./docs/01-repos.md) |
| Wie ist der Server aufgebaut, welche DBs gibt es? | [`docs/02-architecture.md`](./docs/02-architecture.md) |
| Wie schreibe ich ein SpellScript / Aura / Proc? | [`docs/03-spell-system.md`](./docs/03-spell-system.md) |
| Wie funktioniert das AIO-Framework (Server↔Client-UI)? | [`docs/04-aio-framework.md`](./docs/04-aio-framework.md) |
| Was tut Modul X im Detail? | [`docs/05-modules.md`](./docs/05-modules.md) |
| Welche Custom Spell/Item/NPC-IDs sind vergeben? | [`docs/06-custom-ids.md`](./docs/06-custom-ids.md) |
| C++/SQL/Lua Style-Konventionen | [`docs/07-codestyle.md`](./docs/07-codestyle.md) |
| Wie logge ich meine Änderungen korrekt? | [`docs/08-ai-workflow.md`](./docs/08-ai-workflow.md) |
| Vollständige DB-Spaltenstruktur (304 Tabellen) | `mysqldbextracts/mysql_column_list_all.txt` |
| DBC-Dateien des Clients (246 Stück) | `dbc/` (binär) |
| Komplette Änderungshistorie | `claude_log.md` |
| Detaillierte Custom-Spells-Review | `claude_log_2026-04-27_custom_spells_review.md` |

## Lese-Strategie für KI-Tools (WICHTIG)

Im Repo gibt es einige Dateien, deren Größe an oder über dem Lese-Limit der `Read`/`get_file_contents`-Tools liegt. Reihenfolge der Strategie:

1. **Beginne immer hier** (`AI_GUIDE.md`). Sie ist klein und referenziert alle Detaildokumente.
2. **Lade nur was du brauchst.** Jede Datei in [`docs/`](./docs/) ist auf ein Thema fokussiert (~3–15 KB).
3. **Vermeide direkte Volltext-Reads von:**
   - `CLAUDE.md` (~60 KB) — bevorzugt durch [`docs/`](./docs/) ersetzt. Wenn nötig: per `grep`/Header-Listing einlesen.
   - `claude_log.md` (~35 KB) — ok zu lesen, aber bei Bedarf per Datum/Section filtern.
   - `Dcore Concept.pdf` (~190 KB binär) — nur zur grundsätzlichen Einordnung; teilweise veraltet.
   - `mysqldbextracts/mysql_column_list_all.txt` — nur per `grep` für konkrete Tabellen abfragen.
   - `mod-ale/src/LuaEngine/LuaFunctions.cpp` (~96 KB), `LuaEngine.cpp` (~54 KB), `Hooks.h` (~30 KB) — symbolisch via `grep`/`search_code` durchsuchen.
4. **DBC-Dateien sind binär** (WDBC). Nicht direkt lesen — via Python-Tool oder DB-Override (`*_dbc` Tabellen) bearbeiten.

## Kern-Workflow für KI-Sessions

1. **Lies dieses Dokument + relevantes `docs/`-Kapitel** für die Aufgabe.
2. **Plane**: Bei nicht-trivialen Aufgaben TODO-Liste anlegen.
3. **Implementiere auf einem dedizierten Branch**: `claude/<beschreibung>-<sessionId>` pro Repo.
4. **Logge** jede Änderung in `share-public/claude_log.md` (Format siehe [`docs/08-ai-workflow.md`](./docs/08-ai-workflow.md)).
5. **Commits** im Conventional-Commits-Format (`feat(Core/Spells): …`, `fix(DB/SAI): …`).
6. **Keine PRs ohne expliziten User-Request** — nur Branches pushen.

## Quick-Facts (für schnelle Orientierung)

- **WoW-Version**: 3.3.5a (WotLK), Build 12340
- **Sprache Core/Module**: C++17, CMake, MySQL/MariaDB
- **Sprache UI/Tools**: Lua (ALE/Eluna-Fork + WoW Client) + Python 3 (DBC-Tools)
- **Drei DBs**: `acore_auth`, `acore_characters`, `acore_world`
- **Ports**: 3724 (auth), 8085 (world)
- **Custom-Spell-IDs**: ab 100000 (Auras), 900000+ (Custom-Effekte), 920001 (Cursed-Marker), 950001–950099 (Passives)
- **Custom-Enchantment-IDs**: 900001–916666 (Stat-Enchants), 920001 (Cursed), 950001–950099 (Passive Spells)
- **Custom-NPC-IDs**: 900100 (Paragon-NPC) u.a.
- **Custom-Item-ID**: 920920 (Paragon-Punkte) — siehe [`docs/06-custom-ids.md`](./docs/06-custom-ids.md)
- **Projektsprache (Logs/Doku)**: Deutsch | **Code-Kommentare**: Englisch

## Zur Historie der Doku

Die ursprüngliche Gesamtdoku liegt weiterhin in `CLAUDE.md` (60 KB) im Wurzelverzeichnis. Sie ist die kanonische Tiefenreferenz, ist aber für KI-Tools wegen ihrer Größe schwer am Stück lesbar. Diese Doku-Struktur (`AI_GUIDE.md` + `docs/`) ist die **bevorzugte Lese-Quelle**. Beide werden parallel gepflegt; bei Konflikten gewinnt die neuere Version — bitte den Log konsultieren.
