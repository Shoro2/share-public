# AI_GUIDE — Guide for Claude Code & other AI assistants

> **Entry document**. Read this first. All detail chapters live in [`docs/`](./docs/).
> This file is intentionally kept small (< 8 KB) so it can be read reliably by AI tools.

## TL;DR — What is this project?

A **Custom WoW server for WotLK 3.3.5a** based on AzerothCore with several in-house modules around a **Paragon progression system** (post-level-80 XP/level/stats), **automatic item enchantments**, **loot filter**, **auto loot**, and **material storage**. Server↔client UI communication runs over the **AIO framework** (ALE/Lua + WoW addon).

The `share-public` repo is the **central knowledge base**: documentation, custom IDs, DBC files, DB extracTs, Python tools, the AIO framework, and the **change log** (`claude_log.md`) for all repos live here.

The basic concept pitch (with some outdated details) is in `Dcore Concept.pdf` at the root of this repo.

## Repo map (what does each repo do?)

| Repo | Language | Purpose | Detail |
|------|---------|-------|--------|
| [`share-public`](https://github.com/Shoro2/share-public) | MD/Lua/Py | Docs, tools, AIO framework, DBC, logs | this repo |
| [`azerothcore-wotlk`](https://github.com/Shoro2/azerothcore-wotlk) | C++17 | Server core (worldserver, authserver) | [docs/02](./docs/02-architecture.md) |
| [`mod-ale`](https://github.com/Shoro2/mod-ale) | C++/Lua | **Lua engine** (Eluna fork "ALE") — script runtime for all Lua/AIO modules | [`mod-ale/CLAUDE.md`](https://github.com/Shoro2/mod-ale/blob/master/CLAUDE.md) |
| [`mod-paragon`](https://github.com/Shoro2/mod-paragon) | C++/Lua | Account XP + 17-stat system after LV80 | [docs/05](./docs/05-modules.md#mod-paragon) |
| [`mod-paragon-itemgen`](https://github.com/Shoro2/mod-paragon-itemgen) | C++/Lua | Auto enchantments on loot (5 slots, cursed) | [docs/05](./docs/05-modules.md#mod-paragon-itemgen) |
| [`mod-loot-filter`](https://github.com/Shoro2/mod-loot-filter) | C++/Lua | Rule-based auto-sell/disenchant/delete | [docs/05](./docs/05-modules.md#mod-loot-filter) |
| [`mod-auto-loot`](https://github.com/Shoro2/mod-auto-loot) | C++ | AOE looting in a 10-yd radius | [docs/05](./docs/05-modules.md#mod-auto-loot) |
| [`mod-endless-storage`](https://github.com/Shoro2/mod-endless-storage) | Lua/SQL | AIO UI for unlimited material storage + crafting reagent hooks | [docs/05](./docs/05-modules.md#mod-endless-storage) |

`mod-ale` is a **build- and runtime dependency** of all Lua/AIO modules (mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage, plus the `share-public/AIO_Server`).

Other repos referenced from the code that are **not in scope here**: `mod-custom-spells` (Custom SpellScripts) and `mod-dungeon-challenge` (Mythic+-style). Both are currently **not** part of your GitHub MCP permissions — visible read-only via logs/refs.

## Where do I find what?

| Question | File |
|-------|-------|
| Which repos exist, what do they do? | [`docs/01-repos.md`](./docs/01-repos.md) |
| How is the server set up, which DBs are there? | [`docs/02-architecture.md`](./docs/02-architecture.md) |
| How do I write a SpellScript / aura / proc? | [`docs/03-spell-system.md`](./docs/03-spell-system.md) |
| How does the AIO framework work (server↔client UI)? | [`docs/04-aio-framework.md`](./docs/04-aio-framework.md) |
| What does module X do in detail? | [`docs/05-modules.md`](./docs/05-modules.md) |
| Which custom spell/item/NPC IDs are taken? | [`docs/06-custom-ids.md`](./docs/06-custom-ids.md) |
| C++/SQL/Lua style conventions | [`docs/07-codestyle.md`](./docs/07-codestyle.md) |
| How do I log my changes correctly? | [`docs/08-ai-workflow.md`](./docs/08-ai-workflow.md) |
| Full DB column structure (304 tables) | `mysqldbextracts/mysql_column_list_all.txt` |
| Client DBC files (246 of them) | `dbc/` (binary) |
| Full change history | `claude_log.md` |
| Detailed Custom Spells review | `claude_log_2026-04-27_custom_spells_review.md` |
| **AzerothCore engine internals & interfaces** (Map/Grid, Spell/Aura engine, DB pool, DBC loader, opcodes, hooks, …) | [`docs/core/00-INDEX.md`](./docs/core/00-INDEX.md) |

## Reading strategy for AI tools (IMPORTANT)

The repo contains some files whose size is at or above the read limit of the `Read`/`get_file_contents` tools. Strategy in order:

1. **Always start here** (`AI_GUIDE.md`). It is small and references all detail documents.
2. **Load only what you need.** Each file in [`docs/`](./docs/) is focused on a single topic (~3–15 KB).
3. **Avoid direct full-text reads of:**
   - `CLAUDE.md` (~60 KB) — preferentially replaced by [`docs/`](./docs/). If necessary: read by `grep`/header listing.
   - `claude_log.md` (~35 KB) — fine to read, but filter by date/section if needed.
   - `Dcore Concept.pdf` (~190 KB binary) — only for basic orientation; partially outdated.
   - `mysqldbextracts/mysql_column_list_all.txt` — only `grep` for specific tables.
   - `mod-ale/src/LuaEngine/LuaFunctions.cpp` (~96 KB), `LuaEngine.cpp` (~54 KB), `Hooks.h` (~30 KB) — search symbolically via `grep`/`search_code`.
4. **DBC files are binary** (WDBC). Do not read them directly — modify via the Python tool or DB override (`*_dbc` tables).

## Core workflow for AI sessions

1. **Read this document + the relevant `docs/` chapter** for the task.
2. **Plan**: for non-trivial tasks, set up a TODO list.
3. **Implement on a dedicated branch**: `claude/<description>-<sessionId>` per repo.
4. **Log** every change in `share-public/claude_log.md` (format see [`docs/08-ai-workflow.md`](./docs/08-ai-workflow.md)).
5. **Commits** in Conventional Commits format (`feat(Core/Spells): …`, `fix(DB/SAI): …`).
6. **No PRs without explicit user request** — push branches only.

## Quick facts (for fast orientation)

- **WoW version**: 3.3.5a (WotLK), build 12340
- **Core/module language**: C++17, CMake, MySQL/MariaDB
- **UI/tools language**: Lua (ALE/Eluna fork + WoW client) + Python 3 (DBC tools)
- **Three DBs**: `acore_auth`, `acore_characters`, `acore_world`
- **Ports**: 3724 (auth), 8085 (world)
- **Custom spell IDs**: from 100000 (auras), 900000+ (custom effects), 920001 (cursed marker), 950001–950099 (passives)
- **Custom enchantment IDs**: 900001–916666 (stat enchants), 920001 (cursed), 950001–950099 (passive spells)
- **Custom NPC IDs**: 900100 (Paragon NPC), among others
- **Custom item ID**: 920920 (Paragon points) — see [`docs/06-custom-ids.md`](./docs/06-custom-ids.md)
- **Project language (logs/docs)**: English | **Code comments**: English

## On the doc history

The original overall doc still lives in `CLAUDE.md` (60 KB) at the root. It is the canonical deep reference but is hard to read in one piece for AI tools because of its size. This doc structure (`AI_GUIDE.md` + `docs/`) is the **preferred reading source**. Both are maintained in parallel; on conflict the newer version wins — please consult the log.
