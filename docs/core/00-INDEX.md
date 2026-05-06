# core/ — AzerothCore engine reference (master signpost)

> **Engine-internals reference** for the `azerothcore-wotlk` server core.
> Project- and customization-specific docs live one level up in [`docs/01-…`–`10-…`](../) and in [`docs/custom-spells/`](../custom-spells/00-overview.md). Read [`../AI_GUIDE.md`](../../AI_GUIDE.md) first.
>
> Every topic file in this tree follows the same 6-section shape: purpose · critical files (with `path:line`) · key concepts · flow/data · hooks · cross-refs. AI agents should be able to answer most "where is X implemented?" questions in **≤ 2 file reads** starting here.

## Read me first

- [`01-overview.md`](./01-overview.md) — 30k-foot view: processes, threads, lifecycle.
- [`02-glossary.md`](./02-glossary.md) — engine terminology (Map / Grid / Cell, Aura, Opcode, …).
- [`03-file-locator.md`](./03-file-locator.md) — alphabetical "I see file X, which doc covers it?".
- [`04-reading-strategy.md`](./04-reading-strategy.md) — how an AI/human should navigate this tree.

## By question

If the user asks… → read this.

| Question | File |
|---|---|
| How does a player log in (auth → world handoff)? | [`network/06-auth-srp6.md`](./network/06-auth-srp6.md) → [`network/05-worldsession.md`](./network/05-worldsession.md) → [`handlers/01-character-handler.md`](./handlers/01-character-handler.md) |
| What happens when a creature is spawned? | [`maps/04-grid-loading.md`](./maps/04-grid-loading.md) → [`entities/05-creature.md`](./entities/05-creature.md) |
| How does a spell cast flow internally? | [`spells/01-cast-lifecycle.md`](./spells/01-cast-lifecycle.md) |
| Where is a packet/opcode dispatched? | [`network/03-opcodes.md`](./network/03-opcodes.md) → [`handlers/00-index.md`](./handlers/00-index.md) |
| Where does the world tick come from? | [`architecture/03-update-loop.md`](./architecture/03-update-loop.md) |
| How do I add a new prepared statement? | [`database/02-prepared-statements.md`](./database/02-prepared-statements.md) |
| How do DB transactions work? | [`database/05-transactions.md`](./database/05-transactions.md) |
| How is `Spell.dbc` loaded? | [`dbc/01-loader.md`](./dbc/01-loader.md) → [`dbc/02-stores.md`](./dbc/02-stores.md) |
| How do I write a custom hook for a module? | [`scripting/02-hook-classes.md`](./scripting/02-hook-classes.md) → [`scripting/07-custom-hooks.md`](./scripting/07-custom-hooks.md) |
| Where is the `MotionMaster` documented? | [`movement/01-motion-master.md`](./movement/01-motion-master.md) |
| How does damage calculation work? | [`combat/01-damage-pipeline.md`](./combat/01-damage-pipeline.md) |
| How are dungeons / instance saves managed? | [`instances/01-instance-save.md`](./instances/01-instance-save.md) |
| How does the loot roll work? | [`loot/02-loot-roll.md`](./loot/02-loot-roll.md) |
| How is a battleground queue handled? | [`battlegrounds/01-bg-mgr.md`](./battlegrounds/01-bg-mgr.md) |
| How is config loaded / overridden? | [`world/02-config-mgr.md`](./world/02-config-mgr.md) |
| How does `ScriptMgr` register and dispatch hooks? | [`scripting/01-script-mgr.md`](./scripting/01-script-mgr.md) |
| How do MMaps / VMaps work? | [`maps/06-mmaps.md`](./maps/06-mmaps.md) · [`maps/07-vmaps.md`](./maps/07-vmaps.md) |

## By subsystem

| Folder | Covers |
|---|---|
| [`architecture/`](./architecture/00-index.md) | Process model, startup/shutdown, world tick, threading, build system |
| [`database/`](./database/00-index.md) | `WorldDatabase` / `CharacterDatabase` / `LoginDatabase`, prepared statements, query holders, transactions, SQL updater |
| [`dbc/`](./dbc/00-index.md) | DBC loader, format strings, ~80 storage instances, struct layout, DB overrides |
| [`network/`](./network/00-index.md) | `ByteBuffer`, `WorldPacket`, opcodes, `WorldSocket`, `WorldSession`, SRP6 auth, Warden |
| [`entities/`](./entities/00-index.md) | Object/Unit/Player/Creature hierarchy, GUIDs, update fields, `ObjectMgr` |
| [`spells/`](./spells/00-index.md) | Cast lifecycle, `SpellInfo`, aura system, targeting, effects, procs (engine view; user view in [`docs/03`](../03-spell-system.md)) |
| [`maps/`](./maps/00-index.md) | Map / instance map / battleground map, grids, cells, visibility, MMaps, VMaps |
| [`movement/`](./movement/00-index.md) | `MotionMaster`, generators, splines, pathfinder, formations |
| [`combat/`](./combat/00-index.md) | Damage pipeline, threat, resistance, combat state |
| [`ai/`](./ai/00-index.md) | `CreatureAI` hierarchy, `ScriptedAI`, `SmartAI`, pet AI |
| [`scripting/`](./scripting/00-index.md) | `ScriptMgr`, hook classes, module discovery, static/dynamic linkage |
| [`handlers/`](./handlers/00-index.md) | Opcode handlers (matrix file → opcodes) |
| [`instances/`](./instances/00-index.md) | Instance saves, `InstanceScript`, difficulty, dungeon finder |
| [`battlegrounds/`](./battlegrounds/00-index.md) | `BattlegroundMgr`, BG types, arena, battlefield |
| [`loot/`](./loot/00-index.md) | Loot stores, group rolls, conditions |
| [`quests/`](./quests/00-index.md) | Quest data, accept/complete/turn-in, objective tracking |
| [`social/`](./social/00-index.md) | Groups, guilds, mail, auction house, chat channels |
| [`world/`](./world/00-index.md) | `World` singleton, `ConfigMgr`, realm info, weather, game events, calendar |
| [`server-apps/`](./server-apps/00-index.md) | `authserver` and `worldserver` `main()` entry points |
| [`tools/`](./tools/00-index.md) | MMaps generator, VMaps extractor, map extractor, DBC extractor |

## See also (not duplicated here)

| Topic | Lives in |
|---|---|
| Custom modules (Paragon, Itemgen, Loot Filter, Endless Storage, Auto Loot, Custom Spells) | [`../05-modules.md`](../05-modules.md) |
| Custom spell/item/NPC/enchant IDs | [`../06-custom-ids.md`](../06-custom-ids.md) |
| User-side SpellScript / AuraScript / proc authoring | [`../03-spell-system.md`](../03-spell-system.md) + [`../custom-spells/`](../custom-spells/00-overview.md) |
| AIO server↔client UI | [`../04-aio-framework.md`](../04-aio-framework.md) |
| Full DB table inventory (304 tables) | [`../09-db-tables.md`](../09-db-tables.md) |
| DBC file inventory (246 files) | [`../10-dbc-inventory.md`](../10-dbc-inventory.md) |
| C++/SQL/Lua code style + CI | [`../07-codestyle.md`](../07-codestyle.md) |
| AI workflow / branch / log conventions | [`../08-ai-workflow.md`](../08-ai-workflow.md) |
| Logging system (`LOG_INFO` & friends) | `azerothcore-wotlk/doc/Logging.md` |
| Config policy | `azerothcore-wotlk/doc/ConfigPolicy.md` |
| Custom hooks added by this fork | `azerothcore-wotlk/functions.md` + [`scripting/07-custom-hooks.md`](./scripting/07-custom-hooks.md) |

## External (azerothcore.org / Doxygen)

Each topic file's "Cross-references" section links the relevant page(s); the comprehensive map lives in [`04-reading-strategy.md`](./04-reading-strategy.md#external-docs).

- Wiki: https://www.azerothcore.org/wiki/home
- Doxygen API: https://www.azerothcore.org/pages/doxygen/index.html

## Status (Phase 1 = skeleton)

Subfolder `00-index.md` files exist and list planned topic files; topic files (`01-…`, `02-…`, …) are filled in per phase-2 PR (one subsystem per PR, priority order in the [plan](../../).
