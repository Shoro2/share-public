# Custom Spells — ID block scheme

## Scheme

- **Range**: 900xxx for custom spells. Used uniformly for SpellScripts, AuraScripts, marker auras, and helper spells.
- **Block size**: 33 IDs per spec (33 × 3 specs = 99 IDs/class, plus 1 reserve slot at the end).
- **Sub-allocation per spec**: typically the first 5–10 IDs are visible player spells, then helper, marker and proc auras within the same range.
- **Hunter / Mage shared range**: first 2 IDs (Hunter 900500–900501) or one ID (Mage 900700) for class-wide spells that are not spec-specific.
- **Druid gets a 100-ID block** (901000–901099) because of 4 specs (Balance, Feral Tank, Feral DPS, Resto). Feral is intentionally split into Tank vs. DPS because the mechanics differ too much.
- **901100–901199**: non-class global spells (Cast-While-Moving, extra attack, AoE proc, etc.).

Cross reference: [`docs/06-custom-ids.md`](../06-custom-ids.md) for the global ID spaces of all mods (100xxx Paragon, 920xxx cursed marker, 950xxx passive enchants, etc.).

## Allocation

| Class | Spec | Range | Detail doc |
|--------|------|-------|-------------|
| Warrior | Arms | 900100–900107 | [warrior-arms](./specs/warrior-arms.md) |
| Warrior | Fury | 900108–900121 | [warrior-fury](./specs/warrior-fury.md) |
| Warrior | Protection | 900166–900199 | [warrior-protection](./specs/warrior-protection.md) |
| Paladin | Holy | 900200–900232 | [paladin-holy](./specs/paladin-holy.md) |
| Paladin | Protection | 900233–900265 | [paladin-protection](./specs/paladin-protection.md) |
| Paladin | Retribution | 900266–900299 | [paladin-retribution](./specs/paladin-retribution.md) |
| Death Knight | Blood | 900300–900332 | [death-knight-blood](./specs/death-knight-blood.md) |
| Death Knight | Frost | 900333–900365 | [death-knight-frost](./specs/death-knight-frost.md) |
| Death Knight | Unholy | 900366–900399 | [death-knight-unholy](./specs/death-knight-unholy.md) |
| Shaman | Elemental | 900400–900432 | [shaman-elemental](./specs/shaman-elemental.md) |
| Shaman | Enhancement | 900433–900465 | [shaman-enhancement](./specs/shaman-enhancement.md) |
| Shaman | Restoration | 900466–900499 | [shaman-restoration](./specs/shaman-restoration.md) |
| Hunter | Shared | 900500–900501 | [hunter-shared](./specs/hunter-shared.md) |
| Hunter | Beast Mastery | 900502–900532 | [hunter-beast-mastery](./specs/hunter-beast-mastery.md) |
| Hunter | Marksmanship | 900533–900565 | [hunter-marksmanship](./specs/hunter-marksmanship.md) |
| Hunter | Survival | 900566–900599 | [hunter-survival](./specs/hunter-survival.md) |
| Rogue | Assassination | 900600–900632 | [rogue-assassination](./specs/rogue-assassination.md) |
| Rogue | Combat | 900633–900665 | [rogue-combat](./specs/rogue-combat.md) |
| Rogue | Subtlety | 900666–900699 | [rogue-subtlety](./specs/rogue-subtlety.md) |
| Mage | Shared | 900700 | [mage-shared](./specs/mage-shared.md) |
| Mage | Arcane | 900700–900713 | [mage-arcane](./specs/mage-arcane.md) |
| Mage | _free_ | 900714–900732 | (reserved) |
| Mage | Fire | 900733–900740 | [mage-fire](./specs/mage-fire.md) |
| Mage | _free_ | 900741–900765 | (reserved) |
| Mage | Frost | 900766–900774 | [mage-frost](./specs/mage-frost.md) |
| Mage | _free_ | 900775–900799 | (reserved) |
| Warlock | Affliction | 900800–900832 | [warlock-affliction](./specs/warlock-affliction.md) |
| Warlock | Demonology | 900833–900865 | [warlock-demonology](./specs/warlock-demonology.md) |
| Warlock | Destruction | 900866–900899 | [warlock-destruction](./specs/warlock-destruction.md) |
| Priest | Discipline | 900900–900932 | [priest-discipline](./specs/priest-discipline.md) |
| Priest | Holy | 900933–900965 | [priest-holy](./specs/priest-holy.md) |
| Priest | Shadow | 900966–900999 | [priest-shadow](./specs/priest-shadow.md) |
| Druid | Balance | 901000–901032 | [druid-balance](./specs/druid-balance.md) |
| Druid | Feral Tank | 901033–901048 | [druid-feral-tank](./specs/druid-feral-tank.md) |
| Druid | Feral DPS | 901049–901065 | [druid-feral-dps](./specs/druid-feral-dps.md) |
| Druid | Restoration | 901066–901099 | [druid-restoration](./specs/druid-restoration.md) |
| — | Global / Non-Class | 901100–901199 | [global](./specs/global.md) |

> **Mage layout**: range conflict between Shared and Arcane resolved: 900700 is the single shared spell (Channeling Evocation, all 3 specs), 900700–900713 is the overall Arcane block (i.e. shared ID 900700 plus 13 Arcane spells 900701–900713). Fire 900733–900740, Frost 900766–900774 — the gaps between are reserved for later additions.

## Reserved markers / helpers within blocks

Inside each spec block three kinds of IDs appear:

| Type | Example | Purpose |
|-----|----------|-------|
| Player spell | 900106 Paragon Strike | visible in the spellbook |
| Marker aura | 900168 Prot: Revenge Damage | passive trigger tag, `HasAura()` check |
| Helper spell | 900174 Block Shield Burst | triggered via `CastSpell(target, ID, true)` from C++ |

Markers and helpers are not directly castable — they carry `SPELL_ATTR0_PASSIVE` (`0x40`) or are only invoked internally.

## External references

- master source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) sections "ID block scheme" and "Current allocation"
- DBC status per class: `mod-custom-spells/CLAUDE.md` section "DBC Status"
