# Custom Spells — Overview

Dokumentation für [`mod-custom-spells`](https://github.com/Shoro2/mod-custom-spells).

Dieser Ordner ist die kuratierte, entdeckungsfreundliche Sicht auf das Custom-Spell-System. Single-Source-of-Truth für den vollständigen ID-Katalog bleibt [`CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) im Mod-Repo.

## Basis-Doku

| Datei | Inhalt |
|-------|--------|
| [01-architecture.md](./01-architecture.md) | Repo-Layout, Hooks, Loader, Build/Install |
| [02-id-blocks.md](./02-id-blocks.md) | ID-Schema 900xxx + Allokationstabelle aller Specs |
| [03-procs-and-flags.md](./03-procs-and-flags.md) | `spell_proc`-Setup, ProcFlags, SpellFamilyFlags-Verifikation, Off-by-One BasePoints |
| [04-adding-a-spell.md](./04-adding-a-spell.md) | Step-by-Step Rezept für neue Custom Spells |
| [05-complex-spells.md](./05-complex-spells.md) | Querschnitts-Themen: Rekursion, Target-Caps, ICDs, Custom-NPCs, Owner→Pet, OnRemove-Detection, Channel/Cast, Client-Patches |

## Spec-Kataloge

### Warrior (900100–900199)
- [Arms](./specs/warrior-arms.md) · [Fury](./specs/warrior-fury.md) · [Protection](./specs/warrior-protection.md)

### Paladin (900200–900299)
- [Holy](./specs/paladin-holy.md) · [Protection](./specs/paladin-protection.md) · [Retribution](./specs/paladin-retribution.md)

### Death Knight (900300–900399)
- [Blood](./specs/death-knight-blood.md) · [Frost](./specs/death-knight-frost.md) · [Unholy](./specs/death-knight-unholy.md)

### Shaman (900400–900499)
- [Elemental](./specs/shaman-elemental.md) · [Enhancement](./specs/shaman-enhancement.md) · [Restoration](./specs/shaman-restoration.md)

### Hunter (900500–900599)
- [Shared](./specs/hunter-shared.md) · [Beast Mastery](./specs/hunter-beast-mastery.md) · [Marksmanship](./specs/hunter-marksmanship.md) · [Survival](./specs/hunter-survival.md)

### Rogue (900600–900699)
- [Assassination](./specs/rogue-assassination.md) · [Combat](./specs/rogue-combat.md) · [Subtlety](./specs/rogue-subtlety.md)

### Mage (900700–900799)
- [Shared](./specs/mage-shared.md) · [Arcane](./specs/mage-arcane.md) · [Fire](./specs/mage-fire.md) · [Frost](./specs/mage-frost.md)

### Warlock (900800–900899)
- [Affliction](./specs/warlock-affliction.md) · [Demonology](./specs/warlock-demonology.md) · [Destruction](./specs/warlock-destruction.md)

### Priest (900900–900999)
- [Discipline](./specs/priest-discipline.md) · [Holy](./specs/priest-holy.md) · [Shadow](./specs/priest-shadow.md)

### Druid (901000–901099)
- [Balance](./specs/druid-balance.md) · [Feral Tank](./specs/druid-feral-tank.md) · [Feral DPS](./specs/druid-feral-dps.md) · [Restoration](./specs/druid-restoration.md)

### Global / Non-Class (901100–901199)
- [global.md](./specs/global.md)

## Konventionen

- **Ein File pro Spec.** Klassen-Files existieren bewusst nicht — Specs wachsen unabhängig.
- **Kebab-Case Filenames**, keine Number-Prefixes in `specs/` (Reihenfolge irrelevant, Renames vermeiden).
- **Status-Marker** pro Spell: `Live`, `WIP`, `TODO`.
- **Implementation Notes** nur für nicht-triviale Spells (Procs, Formeln, Edge Cases). Trivials bleiben in der Tabelle.
- **Architektonisch heikle Spells** sind in [`05-complex-spells.md`](./05-complex-spells.md) gesammelt — dort stehen die wiederkehrenden Pattern (Rekursionsschutz, Target-Caps, ICDs, Custom-NPCs etc.) zentral.
