# combat/ — Combat pipeline

> Damage / heal calculation, threat tracking, resistance & mitigation, and how units enter/leave combat.

## Topic files

| File | Topic |
|---|---|
| [`01-damage-pipeline.md`](./01-damage-pipeline.md) | `CalculateMeleeDamage`, `DealDamage`, `AbsorbInfo`, `MeleeDamageBonusDone/Taken`, school masks |
| [`02-threat-system.md`](./02-threat-system.md) | `ThreatMgr`, `ThreatList`, `HostileRefMgr`, threat mods, taunt |
| [`03-resistance-mitigation.md`](./03-resistance-mitigation.md) | Armor reduction, resist roll, glancing/parry/dodge/block, miss chance |
| [`04-combat-state.md`](./04-combat-state.md) | `SetInCombatWith`, `EnterCombat`, leashing, combat timer, regen suppression |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Combat/CombatManager.{h,cpp}` | Per-unit combat reference book-keeping |
| `src/server/game/Combat/ThreatMgr.{h,cpp}` | Threat tracking |
| `src/server/game/Combat/HostileRefMgr.{h,cpp}` | Reverse threat refs |
| `src/server/game/Entities/Unit/Unit.cpp` | `DealDamage`, `CalculateMeleeDamage`, `MeleeSpellHitResult` |

## Cross-references

- Engine-side: [`../entities/01-object-hierarchy.md`](../entities/01-object-hierarchy.md) (Unit lives here), [`../spells/01-cast-lifecycle.md`](../spells/01-cast-lifecycle.md), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md) (`UnitScript::OnDamage`, `OnHeal`)
- Project-side: [`../../05-modules.md`](../../05-modules.md) (Paragon's `LifeLeech` rides on `OnDamage`), [`../../03-spell-system.md`](../../03-spell-system.md)
- External: Doxygen for `Unit`, `ThreatMgr`, `HostileRefMgr`
