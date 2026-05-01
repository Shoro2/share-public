# Custom Spells — ID-Block-Schema

## Schema

- **Range**: 900xxx für Custom Spells. Wird durchgängig für SpellScripts, AuraScripts, Marker-Auras und Helper-Spells genutzt.
- **Block-Größe**: 33 IDs pro Spec (33 × 3 Specs = 99 IDs/Klasse, plus 1 Slot Reserve am Ende).
- **Sub-Allokation pro Spec**: typischerweise die ersten 5–10 IDs für sichtbare Player-Spells, danach Helper, Marker und Proc-Auras in derselben Range.
- **Hunter / Mage Shared-Range**: erste 2 IDs (Hunter 900500–900501) bzw. 33 IDs (Mage Shared 900700–900732) für klassenweite Spells, die nicht spec-spezifisch sind.
- **Druid bekommt 100er-Block** (901000–901099), weil 4 Specs (Balance, Feral Tank, Feral DPS, Resto). Feral wird absichtlich in Tank vs. DPS getrennt, weil die Mechaniken zu unterschiedlich sind.
- **901100–901199**: Non-Class Global Spells (Cast-While-Moving, Extra Attack, AoE Proc, etc.).

Querverweis: [`docs/06-custom-ids.md`](../06-custom-ids.md) für globale ID-Räume aller Mods (100xxx Paragon, 920xxx Cursed-Marker, 950xxx Passive-Enchants, etc.).

## Allokation

| Klasse | Spec | Range | Detail-Doku |
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
| Mage | Shared | 900700–900732 | [mage-shared](./specs/mage-shared.md) |
| Mage | Arcane | 900700–900732 | [mage-arcane](./specs/mage-arcane.md) |
| Mage | Fire | 900733–900765 | [mage-fire](./specs/mage-fire.md) |
| Mage | Frost | 900766–900799 | [mage-frost](./specs/mage-frost.md) |
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

> Mage Shared und Mage Arcane teilen sich die Range 900700–900732 in `CustomSpells.md`. Klärung in Phase 3 (Inhalte aus Source/CustomSpells.md übertragen).

## Reservierte Marker / Helper innerhalb der Blöcke

Innerhalb jedes Spec-Blocks tauchen drei Sorten von IDs auf:

| Typ | Beispiel | Zweck |
|-----|----------|-------|
| Player-Spell | 900106 Paragon Strike | sichtbar in Spellbook |
| Marker-Aura | 900168 Prot: Revenge Damage | passive Trigger-Tag, `HasAura()`-Check |
| Helper-Spell | 900174 Block Shield Burst | wird per `CastSpell(target, ID, true)` aus C++ getriggert |

Marker und Helper sind nicht direkt cast-bar — sie tragen `SPELL_ATTR0_PASSIVE` (`0x40`) bzw. werden nur intern gerufen.

## Externe Referenzen

- Master-Source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "ID-Block-Schema" und "Aktuelle Belegung"
- DBC-Status pro Klasse: `mod-custom-spells/CLAUDE.md` Sektion "DBC Status"
