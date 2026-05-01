# share-public

Zentrale Wissensbasis und Daten-Hub für ein Custom **WoW WotLK 3.3.5a** Server-Projekt auf AzerothCore-Basis. Hier liegen Doku, Custom-IDs, DBC-Dateien, Datenbank-Extrakte, Python-Tools, das AIO-Framework und die projektweite Änderungshistorie.

## Einstieg für KI-Tools (Claude Code etc.)

➡️ **[AI_GUIDE.md](./AI_GUIDE.md)** — Schlankes Einstiegsdokument mit Repo-Karte, Lese-Strategie und Verweisen auf alle Detail-Kapitel in [`docs/`](./docs/).

Die Detail-Doku ist modular und thematisch fokussiert (jede Datei <12 KB), damit sie zuverlässig von KI-Tools eingelesen werden kann ohne in Token-Limits zu laufen:

- [`docs/01-repos.md`](./docs/01-repos.md) — alle 7 Repos im Detail
- [`docs/02-architecture.md`](./docs/02-architecture.md) — Server-Architektur
- [`docs/03-spell-system.md`](./docs/03-spell-system.md) — SpellScripts, DBC, Procs
- [`docs/04-aio-framework.md`](./docs/04-aio-framework.md) — Server↔Client UI
- [`docs/05-modules.md`](./docs/05-modules.md) — Modul-Tiefe
- [`docs/06-custom-ids.md`](./docs/06-custom-ids.md) — alle Custom-IDs
- [`docs/07-codestyle.md`](./docs/07-codestyle.md) — C++/SQL/Lua-Konventionen
- [`docs/08-ai-workflow.md`](./docs/08-ai-workflow.md) — Branch-/Log-/Workflow-Regeln

## Änderungshistorie

📝 **[`claude_log.md`](./claude_log.md)** — vollständige Änderungshistorie aller Repos im Projekt mit Datum, Repo, Files und Branch. Jede KI-Session pflegt diesen Log.

## Repo-Inhalte

| Pfad | Inhalt |
|------|--------|
| [`AI_GUIDE.md`](./AI_GUIDE.md) + [`docs/`](./docs/) | KI-Leitfaden (modular, neu) |
| `CLAUDE.md` | alte Gesamtdoku (60 KB Tiefenreferenz, weiterhin gepflegt) |
| `claude_log.md` | Änderungshistorie & TODOs |
| `Dcore Concept.pdf` | ursprünglicher Konzept-Pitch (teils outdated) |
| `dbc/` | 246 binäre WoW-3.3.5a DBC-Dateien |
| `mysqldbextracts/` | DB-Spaltenstruktur (304 Tabellen) + CSV-Exporte |
| `AIO_Server/`, `AIO_Client/` | AIO-Framework v1.75 (Eluna + WoW-Addon) |
| `python_scripts/` | DBC-Patcher, Paragon-Spell-Generator, Load-Test-Tool |
| `SpellFamilies/` | Recherche-Daten zu SpellFamily-Flags |

## Verwandte Repos

- [azerothcore-wotlk](https://github.com/Shoro2/azerothcore-wotlk) — Server-Core
- [mod-paragon](https://github.com/Shoro2/mod-paragon) — Account-XP & 17-Stat-System
- [mod-paragon-itemgen](https://github.com/Shoro2/mod-paragon-itemgen) — Auto-Enchantments auf Loot
- [mod-loot-filter](https://github.com/Shoro2/mod-loot-filter) — Regelbasiertes Auto-Sell/DE/Delete
- [mod-auto-loot](https://github.com/Shoro2/mod-auto-loot) — AOE-Loot
- [mod-endless-storage](https://github.com/Shoro2/mod-endless-storage) — Material-Storage + Crafting-Hooks
