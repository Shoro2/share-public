# Project change log

This document is the central history of all work steps, changes, and plans in the WoW server project. Every entry contains a timestamp, the affected repository, and a description of the change.

---

## Change history

### 2026-05-01

#### [mod-ale] Onboarding: per-repo doc convention applied to the new repo

- **Timestamp**: 2026-05-01
- **Repo**: mod-ale
- **Context**: Repo `shoro2/mod-ale` is new in the GitHub MCP authorization. It is a fork of [Eluna](https://github.com/ElunaLuaEngine/Eluna), divergent under the name **ALE (AzerothCore Lua Engine)**, and provides the Lua/MoonScript script runtime for all the other Lua/AIO-based modules of this project (mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage, plus the `share-public/AIO_Server` framework).
- **Changes**:
  - Applied the 6-file doc convention (analogous to phases A/B): `INDEX.md`, `CLAUDE.md`, `data_structure.md`, `functions.md`, `log.md`, `todo.md`.
  - `CLAUDE.md` highlights the engine role (infrastructure, not a gameplay module) and lists all consumers + config options from `mod_ale.conf.dist` and `CMakeLists.txt`.
  - `data_structure.md` flags the AI-read-risk files: `LuaFunctions.cpp` (~96 KB), `LuaEngine.cpp` (~54 KB), `Hooks.h` (~30 KB), `LuaEngine.h` (~30 KB), `ALE_SC.cpp` (~40 KB) — search them symbolically via `grep`, do not read the whole file.
  - `functions.md` documents hook classes (Server/Player/Creature/GameObject/Item/Spell/Group/Guild/Map/BG), the most important Lua globals (`*DBQuery`/`*DBExecute`, Player API), `EventMgr`, `BytecodeCache`, `FileWatcher`, reload behavior, config impact, and the security pattern around the missing prepared statements (validation lib + atomic single-UPDATE pattern as in the M2 fix).
- **Validation lib NOT integrated**: ALE itself only provides the `*DBQuery`/`*DBExecute` API and does not make its own calls with player-supplied input. Validation is the consumer's job — already in place in `mod-paragon`, `mod-loot-filter`, `mod-endless-storage`.
- **Cross-refs added**:
  - `share-public/AI_GUIDE.md`: included mod-ale in the repo map, marked it as a build/runtime dependency of the other Lua modules; added the read-risk files to the "Avoid direct full-text reads" list.
  - `share-public/claude_log.md`: this entry.
- **Affected files**:
  - `mod-ale/INDEX.md` (NEW)
  - `mod-ale/CLAUDE.md` (NEW)
  - `mod-ale/data_structure.md` (NEW)
  - `mod-ale/functions.md` (NEW)
  - `mod-ale/log.md` (NEW)
  - `mod-ale/todo.md` (NEW)
  - `share-public/AI_GUIDE.md` (extended repo map)
  - `share-public/claude_log.md` (this entry)
- **Branches**:
  - `mod-ale`: `claude/mod-ale-onboarding-uElRt`
  - `share-public`: `claude/wow-server-docs-bugfix-uElRt`
- **Commits** (mod-ale):
  - `704cc13` — docs: add INDEX.md
  - `b2345d6` — docs: add CLAUDE.md
  - `20dfb83` — docs: add data_structure.md
  - `d412502` — docs: add functions.md
  - `8eac771` — docs: add log.md
  - `0d896be` — docs: add todo.md
- **Notes**: source state is `master` @ `1ab53ba`. Currently **no custom patches** — pure mirror of upstream. If project-specific changes to the engine become necessary, they belong as a commit at the top of `mod-ale/log.md` and cross-referenced here.

#### [mod-paragon] Fix: C++ ↔ Lua race condition on Paragon point allocation (M2)

- **Timestamp**: 2026-05-01
- **Repo**: mod-paragon
- **Problem**: Lua `AllocatePoint`/`DeallocatePoint` wrote the stat column and `unspent_points` as two separate asynchronous `CharDBExecute` UPDATEs. If the player changed map within a few ms, C++ `ApplyParagonStatEffects()` read an inconsistent state → integrity check `(totalAllocated + unspent) == level*PPL` failed → destructive reset wiped all stat allocations, the player saw "There was an error loading your Paragon points, please reallocate them!".
- **Solution**:
  1. New function `Paragon.UpdateAllocationAndUnspent(characterID, dbColumn, newValue, newUnspent)` in `Paragon_Data.lua`. Writes the stat column + `unspent_points` in a **synchronous** `CharDBQuery` UPDATE — the next C++ read query (on map change) is guaranteed to see both new values.
  2. `Paragon_Server.lua` `AllocatePoint`/`DeallocatePoint` call the new atomic function instead of the two separate async updates.
  3. `ParagonPlayer.cpp` `ApplyParagonStatEffects()` replaces the destructive reset with soft recovery: on a (theoretically no longer reachable) mismatch only `unspent_points` is recomputed (`level*PPL - totalAllocated`, clamped ≥0), stats stay untouched, auras are still applied. The destructive reset logic stays only on the NPC reset path (`ParagonNPC.cpp`).
- **Affected files**:
  - `Paragon_System_LUA/Paragon_Data.lua`
  - `Paragon_System_LUA/Paragon_Server.lua`
  - `src/ParagonPlayer.cpp`
- **Branch**: `claude/m2-paragon-race-fix-uElRt`
- **Commits**:
  - `8d8ec2d` — fix(Paragon/Lua): add atomic UpdateAllocationAndUnspent
  - `f856c7b` — fix(Paragon/Lua): use atomic update in Allocate/DeallocatePoint
  - `8222889` — fix(Paragon/C++): soft-recover paragon mismatch instead of destructive reset
  - `7d4c46f` — docs(todo): remove M2 race-condition item (fixed)
  - `32865ef` — docs(log): record M2 race-condition fix commits
- **Validation**: to be tested in-game by the user — before fix: allocate a point + immediately switch map → reset; after fix → point stays allocated, no reset.
- **Notes**: the M2 plan comes from `claude_log_2026-05-01_session_handoff.md`. Eluna provides no synchronous `CharDBExecute`, hence the unusual choice to send an UPDATE via `CharDBQuery` — its implementation blocks until the commit, which is exactly what we want here.

#### [Multi-Repo] Docs: Phase A — modular per-repo doc files (log.md / data_structure.md / functions.md)

- **Timestamp**: 2026-05-01
- **Repos**: azerothcore-wotlk, mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage, mod-auto-loot
- **Goal**: make the central CLAUDE.md files in every repo more readable by spreading content consistently across 4 focused files per repo. Avoids the 25 K-token and stream-timeout errors when reading the growing monolith CLAUDE.md.
- **Newly created per repo**:
  - `log.md` — minimal commit log (1 line per commit, with SHA link). Initial population with the last ~10 commits from `git log`.
  - `data_structure.md` — file/folder tree of the repo plus file purposes and size hints (which files are at the read limit, which are binary).
  - `functions.md` — mechanics and function reference (hooks, AIO handlers, DB queries, config, known limitations).
- **Special case mod-auto-loot**: had no `CLAUDE.md` at all — newly created in this phase (4 files instead of 3). Content reconstructed from `src/mod_auto_loot.cpp` and project-central logs.
- **Special case azerothcore-wotlk** (fork): `log.md` focuses on **custom changes** (reagent hooks, Spell.dbc), upstream sync merges only as a collective reference.
- **Existing `CLAUDE.md` files**: **not** touched in this phase. Phase B (separate) will reduce them to pure content docs and remove redundancy with `data_structure.md` / `functions.md`.
- **Branch**: `claude/review-markdown-docs-bTSgu` (in every repo).
- **Commits** (per repo):
  - mod-auto-loot: `cc0b452` (log.md), `756b887` (data_structure.md), `8f13cbf` (functions.md), `603d3e7` (CLAUDE.md NEW)
  - mod-loot-filter: `855cdef`, `ee7449f`, `727e3ed`
  - mod-endless-storage: `b77536b`, `d7e4c9a`, `3da60d2`
  - mod-paragon: `2d39f62`, `0f8c07f`, `78c2319`
  - mod-paragon-itemgen: `8a1fd2b`, `08ed1e7`, `1749558`
  - azerothcore-wotlk: `2348b52`, `1d558eb`, `2f3bafc`
- **Findings during phase A**:
  - **mod-endless-storage**: actual architecture (Lua-only since March 2026) deviated from the legacy `CLAUDE.md` state — phase A corrected this in `functions.md` and `data_structure.md`; the legacy CLAUDE.md describes outdated C++ crafting hooks.
  - **mod-paragon-itemgen**: `src/ParagonItemGen.cpp` at ~37 KB is close to the read limit — use chunked `Read offset/limit` or targeted `grep` if needed. SQL file `paragon_itemgen_enchantments.sql` (>100 KB for 11,323 entries) only via `grep`, never read whole.
  - **mod-paragon**: `ParagonPlayer.cpp` at ~26 KB also at the limit, but still readable.
- **Strategy for AI readability (in addition to the phase 0 modular docs in share-public)**:
  1. Same file names per repo (`log.md`, `data_structure.md`, `functions.md`, `CLAUDE.md`) → blindly navigable.
  2. Each new file <12 KB, in practice 2-8 KB → individually readable.
  3. Cross-refs in every file to its sibling files and to `share-public/AI_GUIDE.md`.
- **Phase B (planned separately, not in this session)**:
  - For each repo, walk the legacy `CLAUDE.md`, remove content that now lives in `data_structure.md`/`functions.md`, keep only pure content/purpose description.
  - Before each refactor: a before/after diff plan for user approval.
  - Goal: every `CLAUDE.md` < 8 KB, redundancy-free with its sibling files.

#### [share-public] Docs: modular AI doc structure (`AI_GUIDE.md` + `docs/`)

- **Timestamp**: 2026-05-01
- **Repo**: share-public
- **Problem**: the central `share-public/CLAUDE.md` has grown to ~60 KB / 1284 lines and can no longer be read reliably by AI tools (Claude Code, etc.) via `Read`/`mcp__github__get_file_contents` — it regularly trips the 25,000-token limit error. Additionally, `Stream idle timeout` errors appear when too many/large tool calls are bundled.
- **Solution**: a new modular doc structure as the preferred entry point for AI sessions:
  - `AI_GUIDE.md` (~6.4 KB) — top-level navigation: repo map, reading strategy, "where do I find what?".
  - `docs/01-repos.md` — all 7 repos in detail (mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-auto-loot, mod-endless-storage, azerothcore-wotlk, share-public).
  - `docs/02-architecture.md` — server architecture, 3 DBs, module system, hooks, logging.
  - `docs/03-spell-system.md` — SpellScripts, AuraScripts, full proc chain, corrected ProcFlags values, DBC system, BasePoints off-by-one.
  - `docs/04-aio-framework.md` — AIO APIs, handler pattern, re-registration trap, code caching, message limits.
  - `docs/05-modules.md` — depth per module: mechanics, DB tables, hooks, config options.
  - `docs/06-custom-ids.md` — custom IDs registry: spells (100xxx, 900xxx), enchants (900001-916666, 920001, 950001-950099), NPCs, items, slash commands, reserved ranges.
  - `docs/07-codestyle.md` — C++/SQL/Lua conventions, CI-enforced bans, commit format.
  - `docs/08-ai-workflow.md` — reading strategy to avoid token/timeout errors, write strategy (1 file per tool call), branch/logging conventions.
  - `README.md` extended from 14 B to ~2.7 KB: points to `AI_GUIDE.md`, lists all docs/ and repos.
- **Strategy to avoid the read errors** (now documented in `docs/08-ai-workflow.md`):
  1. Each `docs/` file <12 KB → no more 25 K-token error on Read.
  2. AI tools start at `AI_GUIDE.md`, then load only the relevant chapter.
  3. When the legacy 60-KB `CLAUDE.md` must be read: extract the truncation file (`/root/.claude/projects/.../tool-results/*.txt`) via `jq -r '.[1].text' > /tmp/file.md`, then `Read offset/limit` chunked.
  4. Write side: `mcp__github__create_or_update_file` once per file, not batched → no `Stream idle timeout`.
- **Backwards compatibility**: legacy `CLAUDE.md` stays unchanged (all module CLAUDE.md files still link to it). The new structure adds, it does not replace.
- **Affected files**:
  - `AI_GUIDE.md` (NEW)
  - `docs/01-repos.md` (NEW)
  - `docs/02-architecture.md` (NEW)
  - `docs/03-spell-system.md` (NEW)
  - `docs/04-aio-framework.md` (NEW)
  - `docs/05-modules.md` (NEW)
  - `docs/06-custom-ids.md` (NEW)
  - `docs/07-codestyle.md` (NEW)
  - `docs/08-ai-workflow.md` (NEW)
  - `README.md` (extended)
  - `claude_log.md` (this entry)
- **Branch**: `claude/review-markdown-docs-bTSgu`
- **Commits**: `222607f` (AI_GUIDE), `72fb3c1` (01-repos), `f663592` (02-architecture), `0a7a586` (03-spell-system), `44b8a43` (04-aio), `9233be9` (05-modules), `2bf9bef` (06-ids), `7a194de` (07-codestyle), `6cfa549` (08-workflow), `89a4406` (README)
- **Notes**: sources for the synthesis: existing `CLAUDE.md` (60 KB, read in chunks), `claude_log.md` (35 KB), `claude_log_2026-04-27_custom_spells_review.md`, all module CLAUDE.md (azerothcore-wotlk, mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage), `mod-auto-loot/src/mod_auto_loot.cpp` (no CLAUDE.md present — module behavior reconstructed from the source). `Dcore Concept.pdf` was classified by the user as partly outdated and was not included in detail, but is linked as a concept pitch in the new `AI_GUIDE.md`.

### 2026-04-28

#### [mod-paragon] Fix: Life Leech does not trigger for casters with pets/totems

- **Timestamp**: 2026-04-28
- **Repo**: mod-paragon
- **Problem**: the Life Leech stat only healed when the player themselves was the `attacker` in `Unit::DealDamage`. This dropped the heal for all caster specs whose main damage source is a pet or totem (Demonology Warlock with Felguard, Frost Mage with Water Elemental, Beast Mastery Hunter, all totem Shaman specs, the Frost DK's Dancing Rune Weapon, Mind Control). Direct player spell damage (Mage Fireball, Priest Smite, Warlock Shadow Bolt) worked — but the lookup `attacker->ToPlayer()` did not match for pets/totems, since their `attacker` is a `Creature`.
- **Solution**: `ParagonLifeLeech::OnDamage` now resolves the player owner of the attacker via `Unit::GetCharmerOrOwnerPlayerOrPlayerItself()`. With this, leech triggers for all sources controlled by the player (player, pet, totem, charmed unit). Additionally, self/friendly damage (fall damage, environmental, own spell splashes) is excluded via a victim-owner check, so the player does not heal back from their own HP loss.
- **Affected files**:
  - `mod-paragon/src/ParagonPlayer.cpp` (`ParagonLifeLeech::OnDamage`)
- **Branch**: `claude/fix-lifeleech-caster-0yYoZ`

### 2026-03-22

#### [mod-paragon] Feat: big+small spell pairs for stats above 255 stacks

- **Timestamp**: 2026-03-22
- **Repo**: mod-paragon
- **Solution**: two spells per stat — "small" (1× value/stack) and "big" (100× value/stack via spell_dbc). Allocation N: big=N/100, small=N%100. Example: 666 Str = 6×big(500) + 66×small(5) = 3330.
- **New files**: `data/sql/db-world/base/paragon_big_stat_spells.sql` (17 spell_dbc, IDs 100201-100227)
- **Commit**: 4ef8c53

#### [mod-paragon] Fix: uint8 aura stack limit for Paragon level and stats

- **Timestamp**: 2026-03-22
- **Repo**: mod-paragon
- **Problem**: GetAuraCount() wraps at 256 → level/points reset. Stats capped at 255.
- **Solution**: read level from DB cache, conf_MaxStats/MAX_POINTS to 666, level aura capped at 255.
- **Commit**: 31de184

#### [mod-paragon-itemgen] Fix: AIO-based tooltip display for paragon stats and cursed items

- **Timestamp**: 2026-03-22
- **Repo**: mod-paragon-itemgen
- **Problem**: paragon item stats and the cursed marker were no longer shown in the client tooltip. Cause: the tooltip display fully relied on a patched client SpellItemEnchantment.dbc. Without a patched DBC, the WoW 3.3.5 client cannot resolve the custom enchantment IDs (900001-920001).
- **Solution**: new AIO-based tooltip system:
  - Server reads enchantment data directly from the item's PROP_ENCHANTMENT slots (7-11)
  - Decodes stat type + amount from the enchantment ID formula (900000 + statIndex * 1000 + amount)
  - Sends data to the client via AIO on login and on inventory changes
  - Client caches the data by bag/slot position and shows custom tooltip lines
  - DBC text detection as a fallback for non-inventory tooltips (loot, quest, vendor)
- **Affected files**:
  - `Paragon_System_LUA/ItemGen_Server.lua` (full rewrite: AIO data provider)
  - `Paragon_System_LUA/ItemGen_Client.lua` (full rewrite: AIO cache + DBC fallback)
  - `CLAUDE.md` (documentation updated)
- **Commit**: a8111bb

#### [azerothcore-wotlk] Feature: Reagent Hooks for External Storage

- **Timestamp**: 2026-03-22
- **Repo**: azerothcore-wotlk
- **Changes**:
  - 2 new PlayerScript hooks: `OnPlayerCheckReagent` and `OnPlayerConsumeReagent`
  - Hook in `Spell::CheckItems()`: queries external sources when the inventory does not have enough
  - Hook in `Spell::TakeReagents()`: consumes from the external source before `DestroyItemCount`
  - Minimal core changes: 4 files, ~45 lines
- **Affected files**:
  - `src/server/game/Scripting/ScriptDefines/PlayerScript.h` (enum + virtual methods)
  - `src/server/game/Scripting/ScriptDefines/PlayerScript.cpp` (ScriptMgr impl)
  - `src/server/game/Scripting/ScriptMgr.h` (declarations)
  - `src/server/game/Spells/Spell.cpp` (hook calls)
- **Commit**: e99877b

#### [mod-endless-storage] Feature: Crafting Integration + UI Fixes

- **Timestamp**: 2026-03-22
- **Repo**: mod-endless-storage
- **Changes**:
  - C++ crafting integration: implements the `OnPlayerCheckReagent` and `OnPlayerConsumeReagent` hooks
  - Queries the `custom_endless_storage` table for missing reagents during crafting
  - Inventory is used first, storage covers the rest — transparent for the player
  - Fix: forward-declare `searchBox` and `logShown` before use in `SelectCategory`
  - Window height increased from 440 to 470px (+30px)
  - Log button moved from the category panel to the top right (next to the close button)
- **Affected files**:
  - `src/mod_endless_storage_crafting.cpp` (new)
  - `src/mod_endless_storage_loader.cpp` (updated)
  - `lua_scripts/Storage/endless_storage_client.lua`

### 2026-03-21

#### [mod-loot-filter] Feature: Complete Loot Filter Module

- **Timestamp**: 2026-03-21
- **Repo**: mod-loot-filter
- **Changes**:
  - Created a new AzerothCore module for automatic item filtering
  - C++ backend: PlayerScript with the OnPlayerLootItem hook, in-memory cache for filter rules, auto-sell (vendor), auto-disenchant (loot generation), auto-delete
  - 8 filter conditions: Quality, Item Level, Sell Price, Item Class, Item Subclass, Cursed Status, Item ID, Name Contains
  - 4 actions: Keep (whitelist), Sell, Disenchant, Delete
  - Priority system: rules are evaluated in priority order, first match wins
  - AIO Lua UI: scrollable rule list, dropdown menus for condition/action, preset buttons (Sell Grey, Sell White, DE Green, etc.), minimap button
  - SQL schema: `character_loot_filter` (rules) + `character_loot_filter_settings` (toggle + statistics)
  - Chat commands: `.lootfilter reload/toggle/stats`
  - Integration with mod-paragon-itemgen: detects cursed items via slot 11 enchantment (920001, 950001-950099)
  - Integration with mod-auto-loot: filters items picked up via auto-loot
  - Configuration: Enable, AllowSell, AllowDisenchant, AllowDelete, LogActions, MaxRulesPerChar
  - Created CLAUDE.md
- **Affected files**:
  - `src/LootFilter.h` (header: enums, constants)
  - `src/LootFilter.cpp` (core: filter logic, hooks, commands)
  - `src/mod_loot_filter_loader.cpp` (module loader)
  - `conf/loot_filter.conf.dist` (configuration)
  - `conf/conf.sh.dist` (SQL paths)
  - `include.sh` (build integration)
  - `data/sql/db-characters/loot_filter_tables.sql` (DB schema)
  - `Loot_Filter_LUA/LootFilter_Server.lua` (AIO server)
  - `Loot_Filter_LUA/LootFilter_Client.lua` (AIO client UI)
  - `CLAUDE.md` (documentation)
- **Branch**: `claude/mod-loot-filters-xdFB7`
- **Commit**: f0a9aa5

#### [mod-dungeon-challenge] Feature: Active Run Tracker UI

- **Timestamp**: 2026-03-21
- **Repo**: mod-dungeon-challenge
- **Changes**:
  - Implemented a new AIO-based active run tracker frame (similar to retail WoW's Mythic+ tracker)
  - Server side: Lua-based run tracking with Eluna hooks (PLAYER_EVENT_ON_MAP_CHANGE, PLAYER_EVENT_ON_KILL_CREATURE, PLAYER_EVENT_ON_KILLED_BY_CREATURE)
  - AIO messages: RunStart, BossKilled, DeathUpdate, RunCompleted, RunEnd
  - Client side: compact TrackerFrame (250px, TOPRIGHT, movable, position saved)
  - Features: real-time timer with color coding (green/yellow/red), +2/+3 threshold times (80%/60% of timer), boss kill checklist with individual kill times, death counter with penalty time display
  - Auto-show on run start, auto-hide 60s after completion
  - New slash command `/dc tracker` to toggle
  - Updated CLAUDE.md
- **Affected files**:
  - `lua_scripts/dungeon_challenge_server.lua` (extended: trackedRuns, BuildAffixString, Eluna event hooks)
  - `lua_scripts/dungeon_challenge_ui.lua` (extended: TrackerFrame, UpdateTrackerDisplay, run handler)
  - `CLAUDE.md` (updated)
- **Branch**: `claude/add-active-run-ui-I0l5q`

### 2026-03-20

#### [mod-dungeon-challenge] Feature: AIO client UI replaces gossip menus

- **Timestamp**: 2026-03-20
- **Repo**: mod-dungeon-challenge
- **Changes**:
  - Created a new AIO-based client UI: gossip menus replaced with real WoW frames
  - `dungeon_challenge_server.lua`: server script with AIO handlers, DB loading, GameObject gossip→AIO bridge
  - `dungeon_challenge_ui.lua`: full WoW UI with tabs (Dungeons, Leaderboard, My Runs, Records)
  - Features: dungeon selection, difficulty slider (1-20), confirm panel with affix details, leaderboard, personal best times, boss kill records
  - Slash command `/dc` to open the UI
  - All data is sent to the client on login via AIO.AddOnInit (dungeon data, affixes, config)
  - Updated CLAUDE.md with the new AIO architecture documentation
  - Marked the old `dungeon_challenge_gameobject.lua` as DEPRECATED
- **Affected files**:
  - `lua_scripts/dungeon_challenge_server.lua` (NEW)
  - `lua_scripts/dungeon_challenge_ui.lua` (NEW)
  - `CLAUDE.md` (updated)
- **Branch**: `claude/review-lua-communication-MItns`

#### [share-public] Docs: AIO framework documentation + mod-dungeon-challenge integration

- **Timestamp**: 2026-03-20
- **Repo**: share-public
- **Changes**:
  - Extended CLAUDE.md with an AIO framework section (APIs, architecture, file structure)
  - Repository table extended with mod-dungeon-challenge
  - Repository structure extended with the AIO_Server folder
  - Updated claude_log.md with change entries
- **Affected files**:
  - `CLAUDE.md` (updated)
  - `claude_log.md` (updated)
- **Branch**: `claude/review-lua-communication-MItns`

---

#### [mod-paragon] Fix: CREATE TABLE IF NOT EXISTS for SQL base scripts

- **Timestamp**: 2026-03-20
- **Repo**: mod-paragon
- **Changes**:
  - `character_paragon_points_create.sql` and `character_paragon_create.sql` used `CREATE TABLE` without `IF NOT EXISTS`
  - This caused ERROR 1050 (42S01) "Table already exists" in the auto-update system when the tables already existed
  - Switched both SQL files to `CREATE TABLE IF NOT EXISTS`
- **Affected files**:
  - `data/sql/db-characters/base/character_paragon_points_create.sql`
  - `data/sql/db-characters/base/character_paragon_create.sql`
- **Branch**: `claude/fix-duplicate-table-error-R8OB8`

---

#### [mod-dungeon-challenge] Feature: New dungeon challenge module (Mythic+ inspired)

- **Timestamp**: 2026-03-20
- **Repo**: mod-dungeon-challenge
- **Changes**:
  - Created a new AzerothCore module: a Mythic+-style dungeon challenge system
  - NPC-based UI: dungeon selection, difficulty (1-20), start a run, leaderboard
  - Affix system: ~5% of mobs receive random affixes (10 affix types)
  - Implemented affixes: Bolstering, Raging, Sanguine, Bursting, Fortified
  - Timer system with death penalty (-5s per death)
  - HP/dmg scaling per difficulty level
  - Leaderboard with DB persistence
  - Gold rewards (bonus for in-time completion)
  - 16 WotLK dungeons preconfigured
  - Full CLAUDE.md and README.md documentation
- **Affected files**:
  - `src/DungeonChallenge.h` - header with all data structures
  - `src/DungeonChallenge.cpp` - singleton manager
  - `src/DungeonChallengeNpc.cpp` - gossip NPC
  - `src/DungeonChallengeScripts.cpp` - event hooks
  - `src/mod_dungeon_challenge_loader.cpp` - loader
  - `data/sql/db-world/00_dungeon_challenge_world.sql` - world DB
  - `data/sql/db-characters/00_dungeon_challenge_characters.sql` - characters DB
  - `conf/mod_dungeon_challenge.conf.dist` - configuration
  - `CLAUDE.md`, `README.md` - documentation
- **Branch**: `claude/azeroth-dungeon-module-tPYFF`

---

### 2026-03-19

#### [mod-paragon] Feature: configurable max points per Paragon stat

- **Timestamp**: 2026-03-19
- **Repo**: mod-paragon
- **Changes**:
  - Maximum points per Paragon stat are now configurable via `mod_paragon.conf` (default: 255)
  - 17 new config options: `Paragon.MaxStr`, `Paragon.MaxInt`, `Paragon.MaxAgi`, `Paragon.MaxSpi`, `Paragon.MaxSta`, `Paragon.MaxHaste`, `Paragon.MaxArmorPen`, `Paragon.MaxSpellPower`, `Paragon.MaxCrit`, `Paragon.MaxHit`, `Paragon.MaxBlock`, `Paragon.MaxExpertise`, `Paragon.MaxParry`, `Paragon.MaxDodge`, `Paragon.MaxMountSpeed`, `Paragon.MaxManaRegen`, `Paragon.MaxLifeLeech`
  - C++: `conf_MaxStats[17]` array, loaded in `OnAfterConfigLoad()`, clamping in `RefreshParagonAura()`
  - Lua: `Paragon.MAX_POINTS` table in `Paragon_Data.lua`, referenced in all 17 stat definitions
  - Value `0` = no limit (only bounded by aura stack size)
- **Affected files**:
  - `mod-paragon/conf/mod_paragon.conf.dist`
  - `mod-paragon/src/ParagonPlayer.cpp`
  - `mod-paragon/Paragon_System_LUA/Paragon_Data.lua`
- **Branch**: `claude/configurable-paragon-stats-PfHFY`

#### [mod-paragon] Refactor: removed all v1/v2 version references

- **Timestamp**: 2026-03-19
- **Repo**: mod-paragon
- **Changes**:
  - `ParagonV2` → `Paragon` (global Lua table)
  - `PARAGON_V2_SERVER` → `PARAGON_SERVER`, `PARAGON_V2_CLIENT` → `PARAGON_CLIENT` (AIO handler)
  - `ParagonV2Frame` → `ParagonFrame`, `SLASH_PARAGONV2_1` → `SLASH_PARAGON1`
  - Comments: "Paragon System v2" → "Paragon System"
  - CLAUDE.md: removed legacy v1 store-system docs, updated file structure and descriptions
- **Affected files**:
  - `mod-paragon/Paragon_System_LUA/Paragon_Data.lua`
  - `mod-paragon/Paragon_System_LUA/Paragon_Server.lua`
  - `mod-paragon/Paragon_System_LUA/Paragon_Client.lua`
  - `mod-paragon/CLAUDE.md`
- **Branch**: `claude/configurable-paragon-stats-PfHFY`

### 2026-03-18

#### [mod-paragon, azerothcore-wotlk] Feature: Life Leech stat

- **Timestamp**: 2026-03-18
- **Repos**: mod-paragon, azerothcore-wotlk
- **Changes**:
  - New 17th Paragon stat: **Life Leech** (aura ID 100027)
  - Heals the player for a configurable percentage of damage dealt (default: 0.5% per stack)
  - Implemented via the performant `UnitScript::OnDamage` hook (option B) instead of the proc system
  - `ParagonPlayer.cpp`: STAT_COUNT 16→17, new conf_AuraIds[16], ParagonLifeLeech UnitScript class
  - `CharacterDatabase.cpp`: prepared statements extended with the `plifeleech` column (SEL, INS, RESET)
  - `character_paragon_points_create.sql`: new column `plifeleech`
  - `mod_paragon.conf.dist`: `Paragon.IdLifeLeech = 100027`, `Paragon.LifeLeechPct = 0.5`
  - `Paragon_Data.lua`: stat definition id=17, category Offensive, DB column order extended
  - Migration SQL: `ALTER TABLE` for existing DBs
- **Affected files**:
  - `mod-paragon/src/ParagonPlayer.cpp`
  - `mod-paragon/conf/mod_paragon.conf.dist`
  - `mod-paragon/data/sql/db-characters/base/character_paragon_points_create.sql`
  - `mod-paragon/data/sql/db-characters/updates/add_plifeleech_column.sql`
  - `mod-paragon/Paragon_System_LUA/Paragon_Data.lua`
  - `azerothcore-wotlk/src/server/database/Database/Implementation/CharacterDatabase.cpp`

#### [mod-paragon] Feature: Shift+Click for 10 points at once

- **Timestamp**: 2026-03-18
- **Repo**: mod-paragon
- **Changes**:
  - `Paragon_System_LUA/Paragon_Client.lua`: +/- buttons send `amount=10` when Shift is held, otherwise `amount=1`
  - `Paragon_System_LUA/Paragon_Server.lua`: `AllocatePoint` and `DeallocatePoint` accept an optional `amount` parameter. The amount is automatically clamped to available points, max cap, and current allocation.
- **Affected files**: `Paragon_System_LUA/Paragon_Client.lua`, `Paragon_System_LUA/Paragon_Server.lua`

#### [mod-paragon] Fix: missing GemProperties value in paragon_currency_item.sql

- **Timestamp**: 2026-03-18
- **Repo**: mod-paragon
- **Changes**:
  - `data/sql/db-world/base/paragon_currency_item.sql`: the INSERT had 138 columns but only 137 values — the value for `GemProperties` was missing. As a result, all subsequent values shifted by one position (`HolidayId` got `''`, `ScriptName` got `0`, `VerifiedBuild` was dropped entirely). This caused the auto-update of the world database to fail.
  - Fix: inserted `0` for `GemProperties`, so all 138 columns are mapped correctly.
- **Affected files**: `data/sql/db-world/base/paragon_currency_item.sql`

#### [share-public] Initial project documentation created

- **Timestamp**: 2026-03-18
- **Repo**: share-public
- **Changes**:
  - Created `CLAUDE.md`: central knowledge base for AI assistants with full documentation of the overall project (architecture, SpellScript system, DBC system, module system, all custom modules, custom IDs, DB tables, code style, build instructions)
  - Created `claude_log.md`: change history and project planning
- **Affected files**: `CLAUDE.md`, `claude_log.md`

> **Note**: earlier phase 3 and phase 4 detail entries on mod-paragon and mod-paragon-itemgen were trimmed because the corresponding implementation state is now fully documented in the modular `docs/05-modules.md` and in each module's `functions.md`.

---

## Open plans and TODOs

> **As of 2026-05-01**: most original TODOs are implemented. Active follow-up work see phase B (CLAUDE.md refactor per module, planned for a separate session).

#### [azerothcore-wotlk] Spell.dbc corruption resolved + validation built in (2026-03-18)

- **Repo**: azerothcore-wotlk, ac-share
- **Change**: restored `share/dbc/Spell.dbc` from a clean backup; 6 safeguards in `share-public/python_scripts/copy_spells_dbc.py` (size check, string-table null byte, duplicate detection, format consistency, source≠target, post-write verify).
- **Verified**: 49,880 records, 0 duplicates, 17 custom 900xxx + 17 custom 100xxx spells present.
- **Status**: ✅ done.

### Phase B (planned)

- [ ] Per repo, walk the existing `CLAUDE.md`, remove content that now lives in `data_structure.md` and `functions.md`, keep only pure content/purpose docs.
- [ ] Before/after diff plan for user approval.
- [ ] Goal: every `CLAUDE.md` < 8 KB, redundancy-free.

### Known leftovers

- [ ] **mod-paragon-itemgen: AH restriction** — blocked: AzerothCore has no `CanCreateAuction` hook, `OnAuctionAdd` is void. Cursed items are soulbound anyway.
- [ ] **mod-paragon: anti-farm measures** — no cooldowns/DR on XP sources.
- [ ] **mod-paragon: SQL injection risk in the Lua layer** — Eluna without prepared statements, still string-concat. Mitigation: server-side validation of handler args.

---

## Format template for new entries

```markdown
### YYYY-MM-DD

#### [repo-name] Short description

- **Timestamp**: YYYY-MM-DD HH:MM (UTC+1)
- **Repo**: repository-name
- **Changes**:
  - Description of change 1
  - Description of change 2
- **Affected files**: `file1.cpp`, `file2.sql`
- **Commit**: `abc1234` (if committed)
- **Branch**: `branch-name`
- **Notes**: additional context information
```
