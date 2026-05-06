# CLAUDE.md

Central information base for AI assistants on the Custom WoW server (WotLK 3.3.5a, AzerothCore-based). **This file is only a signpost** — the actual content is split by topic in `docs/`. Load only the documents you need for your task.

## Reading strategy for AI

> **Never** read all documents at once. Jump in by topic. Full strategy: [docs/08-ai-workflow.md](./docs/08-ai-workflow.md).

## Doc index

| File | Contents |
|-------|--------|
| [docs/01-repos.md](./docs/01-repos.md) | All 7 repos in detail, share-public directory structure, Python scripts |
| [docs/02-architecture.md](./docs/02-architecture.md) | Server architecture (auth/world), 3 databases, source code layout |
| [docs/03-spell-system.md](./docs/03-spell-system.md) | SpellScript/AuraScript, proc system, DBC loading, override paths |
| [docs/04-aio-framework.md](./docs/04-aio-framework.md) | AIO server↔client UI communication, handler patterns, client addon |
| [docs/05-modules.md](./docs/05-modules.md) | Module system, Custom Spells, Paragon, Itemgen, Loot Filter, Endless Storage |
| [docs/06-custom-ids.md](./docs/06-custom-ids.md) | Spell/item/NPC/enchant IDs of the project |
| [docs/07-codestyle.md](./docs/07-codestyle.md) | C++/SQL/Lua code style, CI requirements |
| [docs/08-ai-workflow.md](./docs/08-ai-workflow.md) | AI workflow, read/write strategy, logging duty |
| [docs/09-db-tables.md](./docs/09-db-tables.md) | DB table inventory by category (Custom + AzerothCore) |
| [docs/10-dbc-inventory.md](./docs/10-dbc-inventory.md) | DBC file inventory (246 files) by category |
| [docs/core/00-INDEX.md](./docs/core/00-INDEX.md) | **AzerothCore engine reference** — internals & interfaces (signpost tree, ~25 small files, see [docs/core/04-reading-strategy.md](./docs/core/04-reading-strategy.md)) |

## Repo map

| Repo | Purpose | Local path |
|------|-------|------------|
| `azerothcore-wotlk` | Server core (C++17, CMake, MySQL) | `/home/user/azerothcore-wotlk` |
| `mod-paragon` | Account-wide Paragon level + stat points | `/home/user/mod-paragon` |
| `mod-paragon-itemgen` | 5-slot bonus enchantments on items | `/home/user/mod-paragon-itemgen` |
| `mod-loot-filter` | Character-specific loot filter | `/home/user/mod-loot-filter` |
| `mod-endless-storage` | Unlimited storage per character | `/home/user/mod-endless-storage` |
| `mod-auto-loot` | Automatic looting | `/home/user/mod-auto-loot` |
| `mod-ale` | (see repo CLAUDE.md) | `/home/user/mod-ale` |
| `share-public` | **This repo** — docs, DBCs, DB extracts, AIO, Python tools | `/home/user/share-public` |

Every module repo has its own short `CLAUDE.md` with module-specific details.

## Build (quick reference)

```bash
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/azeroth-server \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DSCRIPTS=static -DMODULES=static
make -j$(nproc)
make install
```

Modules are detected automatically when placed in `azerothcore-wotlk/modules/` (symlink or clone). Details: [docs/02-architecture.md](./docs/02-architecture.md).

## Conventions (mandatory)

- **Branch**: `claude/<description>-<sessionId>` per repo
- **Logging**: every change → `claude_log.md` (ISO 8601 timestamp, repo, description, files, commit hash)
- **Plans**: also in `claude_log.md` under a separate section
- **Commits**: Conventional Commits (`feat(Core/Spells): ...`, `fix(DB/SAI): ...`, `docs: ...`)
- **Language**: logs in English, code comments in English

Full AI workflow rules: [docs/08-ai-workflow.md](./docs/08-ai-workflow.md).
