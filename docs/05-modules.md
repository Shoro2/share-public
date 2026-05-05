# 05 — Modules in detail

Deeper technical overview of each custom module. For a repo map see [01-repos.md](./01-repos.md).

---

## mod-paragon

**Loader function**: `Addmod_paragonScripts()` in `src/Paragon_loader.cpp`.

### Core mechanic

- **Account-wide**: level + XP shared across all characters of the account.
- **Per character**: stat distribution (`unspent_points` + 17 stat columns).
- **XP sources** (table):

| Encounter type | XP |
|---------------|----|
| Regular elite | 1 |
| Dungeon elite | 1 |
| Heroic dungeon elite | 2 |
| Dungeon boss | 3 |
| Heroic dungeon boss | 5 |
| Raid boss | 10 |
| World boss | 20 |
| Daily/weekly quest | 3 |

Group kills give XP to all group members on the same map.

- **Level formula**: `100 * 1.1^(level-1)` XP, counts **down** to 0.
- **5 stat points per level-up**, stored as `unspent_points` in DB (no item).

### Two parallel allocation paths (on the same DB table)

1. **C++ aura system** (`ParagonPlayer.cpp`): on login/MapChange, read stats from DB and apply as invisible stack auras. Cache: `std::unordered_map<uint32, ParagonCache>` with mutex.
2. **Lua AIO UI** (`Paragon_System_LUA/`): frame with tabs (Primary/Offensive/Defensive/Utility), +/- buttons (Shift+click = 10), reset button.

### 17 stats / aura IDs

| Stat | Aura ID | DB column |
|------|---------|-----------|
| Level counter (stack=level) | 100000 | (via `character_paragon`) |
| Strength | 100001 | `pstrength` |
| Intellect | 100002 | `pintellect` |
| Agility | 100003 | `pagility` |
| Spirit | 100004 | `pspirit` |
| Stamina | 100005 | `pstamina` |
| Haste, ArmorPen, SpellPower, Crit, MountSpeed, ManaRegen, Hit, Block, Expertise, Parry, Dodge | 100016–100026 | `phaste`…`pdodge` |
| Life Leech | 100027 | `plifeleech` |

All aura IDs **configurable** via `mod_paragon.conf` (`Paragon.IdStr`, …). MaxStats[17] is also configurable (default 255). 0 = unlimited.

### Big+small spell pairs (stat > 255)

Aura stack limit: 255. Workaround = two spells per stat:
- "Big" (value ×100/stack, IDs 100201–100227)
- "Small" (value ×1/stack)

Allocation N: `big = N/100`, `small = N%100`. Example: 666 Str = 6×Big(500) + 66×Small(5) = 3330. Level aura itself is capped at 255 (= 25,500 levels).

### Life Leech — pet/totem correct

Resolved via `Unit::GetCharmerOrOwnerPlayerOrPlayerItself()` — works for pets/totems/charms (Demonology Felguard, Frost Mage Water Elemental, BM Hunter, Shaman totems, DK Dancing Rune Weapon). Self-damage heal is excluded via the victim-owner check.

### DB tables (acore_characters)

| Table | Columns |
|---------|---------|
| `character_paragon` | `accountID` PK, `level`, `xp` (counts down) |
| `character_paragon_points` | `characterID` PK, `unspent_points`, 17 stat columns |

### Known issue

- SQL injection risk in Lua DB calls (`CharDBExecute` with string concatenation — Eluna API has no prepared statements). Values should be validated.

---

## mod-paragon-itemgen

**Loader function**: `Addmod_paragon_itemgenScripts()` in `src/MP_loader.cpp`.

### 5-slot enchantment system

Items receive bonus stat enchantments via `PROP_ENCHANTMENT_SLOT_0..4` (DB slots 7–11):

| Slot | Contents | Source |
|------|--------|--------|
| 7 | Stamina | always |
| 8 | main stat (Str/Agi/Int/Spi) | player choice |
| 9 | combat rating 1 | role pool |
| 10 | combat rating 2 | role pool, no duplicate of 9 |
| 11 | passive spell / "Cursed" marker / empty | cursed items only |

### Scaling

`amount = ceil(paragonLevel × scalingFactor × qualityMultiplier)`, capped at 666. Random roll per slot from 1 to amount.

### Role pools

| Role | Pool |
|-------|------|
| Tank (0) | Dodge, Parry, Defense, Block, Hit, Expertise |
| DPS Melee (Str/Agi main) | Crit, Haste, Hit, ArmorPen, Expertise, AP |
| DPS Caster (Int/Spi main) | Crit, Haste, Hit, SpellPower, ManaRegen |
| Healer (2) | Crit, Haste, SpellPower, ManaRegen |

The DPS pool is selected automatically via `mainStat` (Str/Agi → melee, Int/Spi → caster).

### Cursed items (1% default)

- all stats × `conf_CursedMultiplier` (default 1.5), capped at 666
- soulbound (`item->SetBinding(true)`)
- shadow visual (`SendPlaySpellVisual(conf_CursedVisualKit)`, default 5765)
- with spec → passive spell from `paragon_passive_spell_pool` (IDs 950001–950099) into slot 11
- without spec → "Cursed" marker (920001) in slot 11
- normal items get **no** passives.

### Tooltip system (two-layered)

1. **AIO data (primary path)**: server reads slots 7–11 from the item, decodes `(slot, enchantmentId)` → `statIndex = (id - 900000) / 1000`, `amount = (id - 900000) % 1000`. Sends per item position via AIO to the client. Cache by bag/slot. **Works without a client DBC patch** for inventory/equipment.
2. **DBC text fallback**: scans the tooltip for "Paragon +", "Cursed", "Passive:" — only available with a pre-patched client `SpellItemEnchantment.dbc` (`patch_dbc.py`). Works for loot/quest/vendor tooltips where slots 7–11 are not directly known on the item instance.

### Hooks

| PlayerScript hook | Trigger |
|-------------------|---------|
| `OnPlayerLootItem` | mob/chest loot |
| `OnPlayerCreateItem` | crafting |
| `OnPlayerQuestRewardItem` | quest reward |
| `OnPlayerAfterStoreOrEquipNewItem` | vendor purchase |
| `OnPlayerCanSetTradeItem` | trade restriction |
| `OnPlayerCanSendMail` | mail restriction |

### Chat commands (`.paragon`)

- `.paragon role tank|dps|healer` (`PLAYER_FLAGS_RESTING` required)
- `.paragon stat str|agi|int|spi` (resting required)
- `.paragon info`

### DB tables

| Table | DB | Purpose |
|---------|----|-------|
| `character_paragon_role` | characters | role + mainStat |
| `character_paragon_item` | characters | enchantment tracking per itemGuid |
| `character_paragon_spec` | characters | spec selection |
| `paragon_passive_spell_pool` | world | pool of passives (spellId, enchantmentId, name, category, minParagonLevel, minItemLevel) |
| `paragon_spec_spell_assign` | world | spec→spell weighting |
| `spellitemenchantment_dbc` | world | DBC override for ~11,323 custom enchantments |

### Auction house restriction

Blocked: `OnAuctionAdd` is void, `CanCreateAuction` does not exist. Cursed items are soulbound anyway. Non-cursed Paragon items are theoretically tradable.

---

## mod-loot-filter

**Loader function**: `Addmod_loot_filterScripts()` in `src/mod_loot_filter_loader.cpp`.

Per-character filter rules, evaluated on the `OnPlayerLootItem` hook (in-memory cache).

### Conditions, operators, actions

| Condition | ID | Available op |
|-----------|----|--------------|
| Quality | 0 | =, >, < |
| ItemLevel | 1 | =, >, < |
| SellPrice | 2 | =, >, < |
| ItemClass | 3 | =, >, < |
| ItemSubclass | 4 | =, >, < |
| IsCursed | 5 | bool |
| ItemId | 6 | =, >, < |
| NameContains | 7 | substring |

Actions: Keep(0) / Sell(1) / Disenchant(2) / Delete(3). Priority: lowest value first, first match wins.

### Cursed detection

Via slot 11 enchantment IDs:
- `920001` = "Cursed" marker
- `950001-950099` = passive spell enchant

### DB tables

| Table | Purpose |
|---------|-------|
| `character_loot_filter` | rules (characterId, ruleId, conditionType, conditionOp, conditionValue, conditionStr, action, priority, enabled) |
| `character_loot_filter_settings` | master toggle + statistics (totalSold, totalDisenchanted, totalDeleted) |

### Commands

`.lootfilter reload | toggle | stats`. UI: `/lf` or `/lootfilter`.

### Config options

`LootFilter.Enable`, `AllowSell`, `AllowDisenchant`, `AllowDelete`, `LogActions`, `MaxRulesPerChar=30`.

---

## mod-auto-loot

**Loader function**: `AddSC_AutoLoot()` in `src/mod_auto_loot_loader.cpp`. **No CLAUDE.md** — full doc lives in this section + `src/mod_auto_loot.cpp`.

### Behavior

In the `OnPlayerUpdate` tick (every frame):
- only if `AOELoot.Enable=true`, the player is not in a group, ≥4 free inventory slots
- iterates all dead creatures in a 10-yd radius (`GetDeadCreatureListInGrid`)
- for each loot item:
  - **stackable items** (`MaxCount != 1`): into inventory, optionally sent on by mail (`AOELoot.MailEnable`)
  - **unique items** (`MaxCount == 1`): only looted if the player does NOT already have the item
- aggregates gold, sends `SMSG_LOOT_MONEY_NOTIFY`, updates the achievement
- calls **`sScriptMgr->OnPlayerLootItem()`** for each item — hook chain: mod-paragon-itemgen (auto-enchant) and mod-loot-filter (filter) take effect.

### Chests

If the player has `Lockpicking` (skill 186): nearby `GAMEOBJECT_TYPE_CHEST` objects are "opened" via spell `2575` and looted. The chest is despawned after a successful loot.

### Config

`AOELoot.Enable=true`, `AOELoot.MailEnable=true`, plus string IDs:
- `AOE_ACORE_STRING_MESSAGE = 50000` (login welcome)
- `AOE_ITEM_IN_THE_MAIL = 50001`

---

## mod-endless-storage

**Loader functions**:
- C++: `Addmod_endless_storageScripts()` in `src/mod_endless_storage_loader.cpp` (crafting hooks)
- Lua: `lua_scripts/endless_storage_server.lua` + `endless_storage_client.lua` (UI)

### UI / tabs

15 material categories (`ITEM_SUBCLASS_*` of TradeGoods + Gems) + recipes tab (`ITEM_CLASS_RECIPE`). Slash `/es` or `/storage`.

### Accepted item classes

| Class | Condition | Tab |
|--------|-----------|-----|
| `ITEM_CLASS_TRADE_GOODS` (7) | `MaxStackSize > 1` | by subclass |
| `ITEM_CLASS_GEM` (3) | `MaxStackSize > 1` | Jewelcrafting |
| `ITEM_CLASS_RECIPE` (9) | all | Recipes |

### DB table (acore_characters)

`custom_endless_storage`: `character_id`, `item_entry`, `item_subclass`, `item_class`, `amount` (PK = `character_id, item_entry`).

### Server handlers

| Handler | Function |
|---------|----------|
| `ES.RequestData(player, catIndex)` | load category, `UpdateItems` to client |
| `ES.Withdraw(player, itemEntry, catIndex)` | take 1 stack → `AddItem` → refresh |
| `ES.Deposit(player, catIndex)` | scan inventory slots 23–38 + bags 19–22, write into DB |

The item template cache (`itemInfoCache`) reduces worlddb queries.

### Crafting integration

The hooks `OnPlayerCheckReagent` and `OnPlayerConsumeReagent` added in azerothcore-wotlk are implemented in `mod_endless_storage_crafting.cpp`:
- `Spell::CheckItems()` additionally queries `custom_endless_storage` when inventory reagents are missing
- `Spell::TakeReagents()` consumes from storage **before** `DestroyItemCount` kicks in
- the player notices nothing — crafting "sees" all materials automatically.

---

## mod-custom-spells

**Loader function**: `Addmod_custom_spellsScripts()` in `src/mod_custom_spells_loader.cpp`.

Custom spell mechanics in the 900xxx ID range. One `.cpp` file per class that registers all spec blocks. Full spec docs as one-file-per-spec under [`docs/custom-spells/`](./custom-spells/00-overview.md) — only the essentials are here for the module overview.

### Three hook strategies

1. **Custom spells** (own ID, own DBC entry, own `SpellScript` via `RegisterSpellScript`).
2. **Hook on Blizzard spells** — `spell_script_names` links an existing ID (e.g. 1680 Whirlwind, 23881 Bloodthirst, 57823 Revenge) to a custom C++ class. **Required**: `HasAura()` check on a marker spell, otherwise the effect kicks in for every player.
3. **AuraScript with proc** — passive aura is armed via `spell_proc`. Filtering in C++ via `CheckProc`, because DBC `EffectSpellClassMask` is ignored by `SPELL_AURA_PROC_TRIGGER_SPELL` (see [03-spell-system.md](./03-spell-system.md#important-dbc-effectspellclassmask-is-ignored)).

### Source layout (`mod-custom-spells/src/`)

| File | Contents |
|------|--------|
| `mod_custom_spells_loader.cpp` | `Addmod_custom_spellsScripts()` entry point |
| `custom_spells.cpp` | master switch (PlayerScript `OnPlayerSpellCast`) |
| `custom_spells_common.h` | shared constants/includes |
| `custom_spells_global.cpp` | non-class spells 901100–901199 |
| `custom_spells_<class>.cpp` | one file per class |

### ID block scheme (short form)

| Range | Contents |
|-------|--------|
| 900100–900199 | Warrior (Arms/Fury/Prot) |
| 900200–900299 | Paladin (Holy/Prot/Ret) |
| 900300–900399 | Death Knight (Blood/Frost/Unholy) |
| 900400–900499 | Shaman (Ele/Enh/Resto) |
| 900500–900599 | Hunter (Shared/BM/MM/Surv) |
| 900600–900699 | Rogue (Assa/Combat/Sub) |
| 900700–900799 | Mage (Shared/Arcane/Fire/Frost) |
| 900800–900899 | Warlock (Affli/Demo/Destro) |
| 900900–900999 | Priest (Disc/Holy/Shadow) |
| 901000–901099 | Druid (Balance/Feral Tank/Feral DPS/Resto) |
| 901100–901199 | Global / non-class |

Full allocation per spec: [`custom-spells/02-id-blocks.md`](./custom-spells/02-id-blocks.md).

### Integration with other modules

- **mod-paragon**: many custom spells scale with `paragonLevel` (aura stack 100000) — e.g. Paragon Strike (900106).
- **azerothcore-wotlk**: requires Spell.dbc patches for own custom spell IDs (tooltips). Server-side a `spell_dbc` override is enough.
- **Config**: `CustomSpells.Enable` (1/0) in `mod_custom_spells.conf.dist`.

### Known issues

- Several ProcFlags values in the legacy `CLAUDE.md` were wrong — corrected in [`custom-spells/03-procs-and-flags.md`](./custom-spells/03-procs-and-flags.md) and in the mod repo at `PROCFLAGS_REFERENCE.md`.
- Mage Shared (900700–900732) and Mage Arcane (900700–900732) share the same range in the master plan — still to be clarified.
