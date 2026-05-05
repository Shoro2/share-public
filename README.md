# share-public

Central knowledge base and data hub for a custom **WoW WotLK 3.3.5a** server project on AzerothCore. This holds documentation, custom IDs, DBC files, database extracts, Python tools, the AIO framework, and the project-wide change history.

## Entry point for AI tools (Claude Code etc.)

➡️ **[AI_GUIDE.md](./AI_GUIDE.md)** — slim entry document with the repo map, reading strategy, and references to all detail chapters in [`docs/`](./docs/).

The detail docs are modular and topic-focused (each file <12 KB) so they can be read reliably by AI tools without running into token limits:

- [`docs/01-repos.md`](./docs/01-repos.md) — all 7 repos in detail
- [`docs/02-architecture.md`](./docs/02-architecture.md) — server architecture
- [`docs/03-spell-system.md`](./docs/03-spell-system.md) — SpellScripts, DBC, procs
- [`docs/04-aio-framework.md`](./docs/04-aio-framework.md) — server↔client UI
- [`docs/05-modules.md`](./docs/05-modules.md) — module deep dive
- [`docs/06-custom-ids.md`](./docs/06-custom-ids.md) — all custom IDs
- [`docs/07-codestyle.md`](./docs/07-codestyle.md) — C++/SQL/Lua conventions
- [`docs/08-ai-workflow.md`](./docs/08-ai-workflow.md) — branch/log/workflow rules

## Change history

📝 **[`claude_log.md`](./claude_log.md)** — full change history of all repos in the project with date, repo, files, and branch. Every AI session maintains this log.

## Repo contents

| Path | Contents |
|------|--------|
| [`AI_GUIDE.md`](./AI_GUIDE.md) + [`docs/`](./docs/) | AI guide (modular, new) |
| `CLAUDE.md` | legacy overall doc (60 KB deep reference, still maintained) |
| `claude_log.md` | change history & TODOs |
| `Dcore Concept.pdf` | original concept pitch (partially outdated) |
| `dbc/` | 246 binary WoW 3.3.5a DBC files |
| `mysqldbextracts/` | DB column structure (304 tables) + CSV exports |
| `AIO_Server/`, `AIO_Client/` | AIO framework v1.75 (Eluna + WoW addon) |
| `python_scripts/` | DBC patcher, Paragon spell generator, load test tool |
| `SpellFamilies/` | research data on SpellFamily flags |

## Related repos

- [azerothcore-wotlk](https://github.com/Shoro2/azerothcore-wotlk) — server core
- [mod-paragon](https://github.com/Shoro2/mod-paragon) — account XP & 17-stat system
- [mod-paragon-itemgen](https://github.com/Shoro2/mod-paragon-itemgen) — auto enchantments on loot
- [mod-loot-filter](https://github.com/Shoro2/mod-loot-filter) — rule-based auto-sell/DE/delete
- [mod-auto-loot](https://github.com/Shoro2/mod-auto-loot) — AOE loot
- [mod-endless-storage](https://github.com/Shoro2/mod-endless-storage) — material storage + crafting hooks
