# Project change log — 2026-03 archive

> Older entries from `claude_log.md`. New entries belong in [`claude_log.md`](./claude_log.md).

---

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
