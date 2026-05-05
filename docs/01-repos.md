# 01 — Repository overview

All 7 repos in detail. Branch note: AI sessions work per repo on a dedicated branch in the scheme `claude/<description>-<sessionId>`.

## share-public — central knowledge base

- **Purpose**: documentation, tools, AIO framework, DBC files, DB extracts, change log.
- **Languages**: Markdown / Lua / Python.
- **Important contents**:
  - `AI_GUIDE.md`, `docs/` — AI guide (new, modular)
  - `CLAUDE.md` — legacy overall doc (60 KB, deep reference)
  - `claude_log.md` — change history of all repos
  - `Dcore Concept.pdf` — original concept pitch (partially outdated)
  - `AIO_Server/`, `AIO_Client/` — AIO framework v1.75 (server Lua + WoW addon)
  - `dbc/` — 246 binary WoW 3.3.5a DBC files
  - `mysqldbextracts/` — full DB column structure (304 tables) + CSVs (`creature_template`, `item_template`)
  - `python_scripts/` — DBC patcher (`patch_dbc.py`, `copy_spells_dbc.py`), Paragon spell generator (`add_paragon_spell.py`), load test (`socket_stress_heavy.py`)
  - `SpellFamilies/` — research on SpellFamily flags

## azerothcore-wotlk — server core

- **Purpose**: AzerothCore fork (worldserver + authserver). Contains all custom modules under `modules/` and requires project-specific Spell.dbc patches.
- **Language**: C++17 (CMake, MySQL/MariaDB, Boost, OpenSSL).
- **Custom extensions beyond upstream**:
  - `OnPlayerCheckReagent` / `OnPlayerConsumeReagent` PlayerScript hooks (for mod-endless-storage crafting integration)
  - Custom Spell.dbc with custom spells (100xxx, 900xxx)
- **CI**: codestyle checks (C++, SQL), multi-compiler builds (clang-15/18, gcc-14, macOS, Windows).
- **Module overview**: `modules/` — custom modules are auto-detected via CMake.

## mod-paragon — account XP & 17-stat system

- **Purpose**: post-LV80 progression. Account-wide XP/level, 5 points/level, 17 distributable stats.
- **Architecture**: hybrid C++/Lua.
  - C++ aura system (`ParagonPlayer.cpp`): loads stats from the DB, applies invisible stack auras
  - Lua AIO UI (`Paragon_System_LUA/`): frame for distributing/resetting points
- **17 stats**: Str, Int, Agi, Spi, Sta, Haste, ArmorPen, SpellPower, Crit, MountSpeed, ManaRegen, Hit, Block, Expertise, Parry, Dodge, **LifeLeech** (heals % of damage dealt, also works through pets/totems).
- **Big+small spell system**: stats above 255 stacks via paired auras (stack ×100 + stack ×1).
- **DB tables** (acore_characters): `character_paragon` (account level/XP), `character_paragon_points` (per character, 17 stat columns).
- **Configurable**: 30+ `.conf` options (aura IDs, MaxStats[17], MaxLevel, XP rewards).

## mod-paragon-itemgen — auto enchantments on loot

- **Purpose**: on loot/craft/quest reward/vendor purchase, items are automatically given Paragon stat enchantments.
- **5-slot enchantment system** (PROP_ENCHANTMENT_SLOT 0–4 = DB slots 7–11):
  - Slot 7: Stamina (always)
  - Slot 8: main stat (player choice: Str/Agi/Int/Spi)
  - Slots 9–10: 2 random combat ratings from a role pool (Tank/MeleeDPS/CasterDPS/Healer)
  - Slot 11: on **cursed items** a passive spell or "Cursed" marker
- **Cursed items** (1% default chance): all stats ×1.5, soulbound, shadow visual, exclusive passive spell.
- **Tooltip display**: AIO-based (server reads slot IDs, decodes the stat from formula `900000 + statIndex × 1000 + amount`, sends to the client). Works without a client DBC patch; DBC patching only as a fallback for loot/quest/vendor tooltips.
- **DB tables** (acore_characters): `character_paragon_role`, `character_paragon_item`, `character_paragon_spec`. (acore_world): `paragon_passive_spell_pool`, `paragon_spec_spell_assign`, **`spellitemenchantment_dbc`** (~11,323 custom enchantments).
- **Enchantment ID layout** see [`06-custom-ids.md`](./06-custom-ids.md).

## mod-loot-filter — rule-based auto-sell/DE/delete

- **Purpose**: players define rules via the AIO UI for what should happen with looted items.
- **8 condition types**: Quality, Item Level, Sell Price, Item Class, Item Subclass, Cursed Status, Item ID, Name Contains.
- **3 comparison operators**: `=`, `>`, `<`.
- **4 actions**: Keep (whitelist) / Sell (vendor) / Disenchant / Delete.
- **Priority system**: lower value = checked first, first match wins.
- **DB tables** (acore_characters): `character_loot_filter` (rules), `character_loot_filter_settings` (master toggle + stats).
- **Integration**: hooks `OnPlayerLootItem` (intercept), detects cursed items via slot 11 enchantment IDs (920001, 950001-950099). UI: `/lf` or `/lootfilter`.

## mod-auto-loot — AOE loot

- **Purpose**: simple AOE looting in a 10-yd radius on the `OnPlayerUpdate` tick.
- **Condition**: player has ≥4 free inventory slots, is not in a group, `AOELoot.Enable=true`.
- **Behavior**:
  - Creature loot: all nearby corpse loots are consumed, gold accumulated. Full inventories → optional mail delivery of items.
  - Chests (GAMEOBJECT_TYPE_CHEST): if the player has Lockpicking (skill 186), the chest is opened via spell 2575 and looted.
- **Integration**: calls `sScriptMgr->OnPlayerLootItem()` — so mod-paragon-itemgen (auto enchant) and mod-loot-filter (filter) catch the item.
- **Has NO CLAUDE.md** — the documentation lives in the code (`src/mod_auto_loot.cpp`) and in this overview.

## mod-endless-storage — unlimited material storage + crafting

- **Purpose**: players store all crafting materials (cloth, leather, ore, herbs, gems, recipes) in a server-side "Endless Storage", retrievable via the AIO UI (slash `/es`).
- **Architecture**: pure Eluna/AIO module — no NPC, no gossip. Plus a C++ hook module (`mod_endless_storage_crafting.cpp`) for crafting reagent integration.
- **Tabs**: 15 material categories (subclasses) + 1 recipes tab (class 9).
- **Crafting integration**: implements the `OnPlayerCheckReagent` / `OnPlayerConsumeReagent` hooks added in azerothcore-wotlk. The inventory is used first, storage covers the rest — transparent for crafting.
- **DB table** (acore_characters): `custom_endless_storage` (character_id, item_entry, item_subclass, item_class, amount).
- **AIO specifics**: global handler table (`MY_Handlers` pattern) due to re-registration restrictions. Item info retry timer for uncached items.

## mod-custom-spells — custom spell effects

- **Purpose**: custom spell mechanics via SpellScript / AuraScript / OnPlayerSpellCast for spell IDs in the 900xxx range. One `.cpp` file per class, organized in spec blocks.
- **Three hook paths**:
  - **Custom spells** with their own ID + DBC entry + SpellScript
  - **Hooks on Blizzard spells** (e.g. Whirlwind, Bloodthirst, Revenge) via `spell_script_names` — required: `HasAura()` check on a marker
  - **AuraScript with proc** via `spell_proc` (filtered in C++ via `CheckProc`, because DBC `EffectSpellClassMask` is ignored)
- **ID blocks**: 33 IDs per spec, 900100–901099 for class specs, 901100–901199 for non-class globals. Details see [`docs/custom-spells/02-id-blocks.md`](./custom-spells/02-id-blocks.md).
- **Integration with mod-paragon**: many custom spells scale with `paragonLevel` (aura stack 100000) — e.g. `damage = 666 + AP × 0.66 × (1 + paragonLevel × 0.01)`.
- **DBC maintenance**: each custom spell needs a `spell_dbc` override + optionally a `spell_proc` entry. Mind the off-by-one BasePoints (`real_value - 1`).
- **Config**: `CustomSpells.Enable` (1/0).
- **Detail docs**: [`docs/custom-spells/`](./custom-spells/00-overview.md) — 33 spec files plus architecture, ID block, procs, and adding-a-spell guides.
