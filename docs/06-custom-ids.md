# 06 — Custom IDs registry

Compact overview of all project-specific IDs. Before assigning a new ID, check here.

## Spell IDs

### 100xxx — Paragon auras

| ID | Purpose | System |
|----|-------|--------|
| 100000 | level counter (stack = Paragon level) | C++ |
| 100001 | Strength | C++/Lua (unified) |
| 100002 | Intellect | C++/Lua |
| 100003 | Agility | C++/Lua |
| 100004 | Spirit | C++/Lua |
| 100005 | Stamina | C++/Lua |
| 100016–100026 | Haste, ArmorPen, SpellPower, Crit, MountSpeed, ManaRegen, Hit, Block, Expertise, Parry, Dodge | C++/Lua |
| 100027 | Life Leech | C++/Lua |
| 100201–100227 | "Big" Paragon stat spells (×100/stack via spell_dbc) | C++ |

### 900xxx — custom spells (mod-custom-spells)

> **Detail docs**: [`custom-spells/02-id-blocks.md`](./custom-spells/02-id-blocks.md) has the full allocation table per spec; each spec has its own file under [`custom-spells/specs/`](./custom-spells/00-overview.md).

Short overview of the most important cross-referenced spells:

| ID | Name | Type | Effect |
|----|------|-----|--------|
| 900106 | Paragon Strike | SpellScript | SCHOOL_DAMAGE: 666 + 66% AP, +1%/Paragon level |
| 900107 | Bladestorm CD reduce | SpellScript | DUMMY: -0.5 s CD per cast on 46927 |
| 900114 | Whirlwind proc aura | Aura | 500 ms ICD |
| 900115 | Bloody Whirlwind buff | Aura | buff applied by 900116 |
| 900116 | Bloody Whirlwind passive | AuraScript | PROC: on Bloodthirst → 900115 |
| 900168–901108 | custom marker auras (~70+) | Passive | trigger tags for custom mechanics |

(The marker auras need an apply mechanism — currently unclear whether via `paragon_passive_spell_pool` or GM testing. See TODOs in `claude_log_2026-04-27_custom_spells_review.md`.)

### Existing WoW spells we override / reference

| ID | Name | What we do |
|----|------|-------------|
| 1680 | Whirlwind | AFTER_CAST → removes 900115 stacks |
| 23881 | Bloodthirst | trigger for 900116 |
| 46927 | Bladestorm | CD reduced via 900107 |
| 2575 | Pickpocket / Open-Lock | cast by mod-auto-loot on chests |

## Item IDs

| ID | Purpose |
|----|-------|
| 920920 | Paragon points (legacy — today via `unspent_points` in DB) |

## NPC IDs

| ID | Name | ScriptName | Purpose |
|----|------|------------|-------|
| 900100 | Paragon NPC | `npc_paragon` | Gossip: info + point reset |
| 900333 | Frost Wyrm | `npc_custom_frost_wyrm` | DK Frost custom summon |
| 900436 | Spirit Wolf | (mod-custom-spells) | Shaman Enhance wolf summon proc |
| 901066 | Healing Treant | (mod-custom-spells) | Druid Resto HoT treant proc |

## Enchantment IDs (in `spellitemenchantment_dbc`)

### Layout

```
Base: 900000
Formula: 900000 + statIndex × 1000 + amount   (amount = 1..666)

statIndex 0  = Stamina      → 900001..900666
statIndex 1  = Strength     → 901001..901666
statIndex 2  = Agility      → 902001..902666
statIndex 3  = Intellect    → 903001..903666
statIndex 4  = Spirit       → 904001..904666
statIndex 5  = Dodge        → 905001..905666
statIndex 6  = Parry        → 906001..906666
statIndex 7  = Defense      → 907001..907666
statIndex 8  = Block        → 908001..908666
statIndex 9  = Hit          → 909001..909666
statIndex 10 = Crit         → 910001..910666
statIndex 11 = Haste        → 911001..911666
statIndex 12 = Expertise    → 912001..912666
statIndex 13 = ArmorPen     → 913001..913666
statIndex 14 = SpellPower   → 914001..914666
statIndex 15 = AttackPower  → 915001..915666
statIndex 16 = ManaRegen    → 916001..916666
```

### Special entries

| ID | Purpose |
|----|-------|
| 920001 | "Cursed" marker (no stat effect, only a slot 11 label) |
| 950001–950099 | passive spell enchantments (`ITEM_ENCHANTMENT_TYPE_EQUIP_SPELL`, cursed items only) |

Each enchantment has exactly one `ITEM_ENCHANTMENT_TYPE_STAT` (type 5) effect: `Effect_1=5`, `EffectPointsMin_1=amount`, `EffectArg_1=ITEM_MOD_*`.

## Slash commands

| Command | Module | Purpose |
|---------|-------|-------|
| `/paragon` | mod-paragon | open the Paragon UI |
| `/lf`, `/lootfilter` | mod-loot-filter | loot filter UI |
| `/es`, `/storage` | mod-endless-storage | Endless Storage UI |
| `.paragon role|stat|info` | mod-paragon-itemgen | role/main-stat setup |
| `.lootfilter reload|toggle|stats` | mod-loot-filter | server-side commands |
| `/aio help|reset|version` | AIO | AIO maintenance |

## Reserved ID ranges (for new assignments)

| Range | Reserved for |
|---------|----------------|
| 100000–100999 | Paragon auras (C++/Lua) |
| 100200–100299 | big-stat auras |
| 900000–916999 | stat enchantments + custom spells |
| 920000–920999 | cursed marker / enchant special |
| 950000–950099 | passive spell enchants |
| NPC 900000+ | custom NPCs |
| Item 920000+ | custom items |

If a new module assigns IDs outside these ranges, document them here.

## Tables / string IDs

| ID | Purpose | Module |
|----|-------|-------|
| `npc_text.197760` | Paragon NPC greeting | mod-paragon |
| `acore_string.50000` | "AOE Loot active" login hint | mod-auto-loot |
| `acore_string.50001` | "Item in mail" | mod-auto-loot |
