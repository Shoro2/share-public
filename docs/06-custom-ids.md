# 06 — Custom-IDs-Registry

Kompakte Übersicht aller projekt-spezifischen IDs. Bevor neue IDs vergeben werden: hier prüfen.

## Spell-IDs

### 100xxx — Paragon-Auras

| ID | Zweck | System |
|----|-------|--------|
| 100000 | Level-Counter (Stack = Paragon-Level) | C++ |
| 100001 | Strength | C++/Lua (vereinheitlicht) |
| 100002 | Intellect | C++/Lua |
| 100003 | Agility | C++/Lua |
| 100004 | Spirit | C++/Lua |
| 100005 | Stamina | C++/Lua |
| 100016–100026 | Haste, ArmorPen, SpellPower, Crit, MountSpeed, ManaRegen, Hit, Block, Expertise, Parry, Dodge | C++/Lua |
| 100027 | Life Leech | C++/Lua |
| 100201–100227 | "Big" Paragon Stat Spells (×100/Stack via spell_dbc) | C++ |

### 900xxx — Custom Spells (mod-custom-spells)

> **Detail-Doku**: [`custom-spells/02-id-blocks.md`](./custom-spells/02-id-blocks.md) hat die vollständige Allokationstabelle pro Spec, jeder Spec hat ein eigenes File unter [`custom-spells/specs/`](./custom-spells/00-overview.md).

Kurzübersicht der wichtigsten cross-referenzierten Spells:

| ID | Name | Typ | Effekt |
|----|------|-----|--------|
| 900106 | Paragon Strike | SpellScript | SCHOOL_DAMAGE: 666 + 66% AP, +1%/Paragon-Level |
| 900107 | Bladestorm CD Reduce | SpellScript | DUMMY: -0.5 s CD pro Cast auf 46927 |
| 900114 | Whirlwind Proc Aura | Aura | 500 ms ICD |
| 900115 | Bloody Whirlwind Buff | Aura | Buff applied von 900116 |
| 900116 | Bloody Whirlwind Passive | AuraScript | PROC: bei Bloodthirst → 900115 |
| 900168–901108 | Custom Marker-Auras (~70+) | Passive | Trigger-Tags für Custom-Mechaniken |

(Die Marker-Auras brauchen einen Apply-Mechanismus — aktuell unklar, ob über `paragon_passive_spell_pool` oder GM-Test. Siehe TODOs in `claude_log_2026-04-27_custom_spells_review.md`.)

### Bestehende WoW-Spells, die wir overriden / referenzieren

| ID | Name | Was wir tun |
|----|------|-------------|
| 1680 | Whirlwind | AFTER_CAST → entfernt 900115 Stacks |
| 23881 | Bloodthirst | Trigger für 900116 |
| 46927 | Bladestorm | CD reduziert via 900107 |
| 2575 | Pickpocket / Open-Lock | Cast durch mod-auto-loot auf Truhen |

## Item-IDs

| ID | Zweck |
|----|-------|
| 920920 | Paragon Points (legacy — heute über `unspent_points` in DB) |

## NPC-IDs

| ID | Name | ScriptName | Zweck |
|----|------|------------|-------|
| 900100 | Paragon NPC | `npc_paragon` | Gossip: Info + Punkte-Reset |
| 900333 | Frost Wyrm | `npc_custom_frost_wyrm` | DK Frost Custom-Summon |
| 900436 | Spirit Wolf | (mod-custom-spells) | Shaman Enhance Wolf-Summon-Proc |
| 901066 | Healing Treant | (mod-custom-spells) | Druid Resto HoT-Treant-Proc |

## Enchantment-IDs (in `spellitemenchantment_dbc`)

### Layout

```
Basis: 900000
Formel: 900000 + statIndex × 1000 + amount   (amount = 1..666)

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

### Sondereinträge

| ID | Zweck |
|----|-------|
| 920001 | "Cursed"-Marker (kein Stat-Effekt, nur Slot-11-Label) |
| 950001–950099 | Passive-Spell-Enchantments (`ITEM_ENCHANTMENT_TYPE_EQUIP_SPELL`, nur Cursed Items) |

Pro Enchantment exakt ein `ITEM_ENCHANTMENT_TYPE_STAT` (type 5) Effekt: `Effect_1=5`, `EffectPointsMin_1=amount`, `EffectArg_1=ITEM_MOD_*`.

## Slash-Commands

| Command | Modul | Zweck |
|---------|-------|-------|
| `/paragon` | mod-paragon | Paragon-UI öffnen |
| `/lf`, `/lootfilter` | mod-loot-filter | Loot-Filter-UI |
| `/es`, `/storage` | mod-endless-storage | Endless-Storage-UI |
| `.paragon role|stat|info` | mod-paragon-itemgen | Rolle/Mainstat-Setup |
| `.lootfilter reload|toggle|stats` | mod-loot-filter | Server-Side-Commands |
| `/aio help|reset|version` | AIO | AIO-Maintenance |

## Reservierte ID-Bereiche (für neue Vergaben)

| Bereich | Reserviert für |
|---------|----------------|
| 100000–100999 | Paragon-Auras (C++/Lua) |
| 100200–100299 | Big-Stat-Auras |
| 900000–916999 | Stat-Enchantments + Custom-Spells |
| 920000–920999 | Cursed-Marker / Enchant-Special |
| 950000–950099 | Passive-Spell-Enchants |
| NPC 900000+ | Custom-NPCs |
| Item 920000+ | Custom-Items |

Vergibt ein neues Modul IDs ausserhalb dieser Bereiche, hier dokumentieren.

## Tabellen / String-IDs

| ID | Zweck | Modul |
|----|-------|-------|
| `npc_text.197760` | Paragon-NPC-Greeting | mod-paragon |
| `acore_string.50000` | "AOE Loot active"-Login-Hint | mod-auto-loot |
| `acore_string.50001` | "Item in mail" | mod-auto-loot |
