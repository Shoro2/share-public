# spells — Aura system

> The buff/debuff/passive layer. Three-class split: `Aura` (the buff *instance*), `AuraApplication` (per-target attachment), `AuraEffect` (one of up to 3 effects of the aura). Cross-link [`01-cast-lifecycle.md`](./01-cast-lifecycle.md) (creator), [`07-modifiers.md`](./07-modifiers.md) (`SPELL_AURA_ADD_FLAT_MODIFIER` etc.), [`08-script-bindings.md`](./08-script-bindings.md) (AuraScript glue).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/Auras/SpellAuras.h:36` | `class AuraApplication` — per-target attachment of an `Aura` |
| `src/server/game/Spells/Auras/SpellAuras.h:86` | `class Aura` — one buff instance, may apply to N targets |
| `src/server/game/Spells/Auras/SpellAuras.h:93` | `static Aura* TryRefreshStackOrCreate(spellInfo, tryEffMask, owner, caster, …)` — the canonical construction path; reuses an existing `Aura` if stack/refresh applies, otherwise calls `TryCreate` |
| `src/server/game/Spells/Auras/SpellAuras.h:94` | `static Aura* TryCreate(spellInfo, effMask, owner, caster, …)` — bare construction without stack rules |
| `src/server/game/Spells/Auras/SpellAuras.cpp` | `Aura::_ApplyForTarget`, `_UnapplyForTarget`, `RecalculateAmountOfEffects`, `Update`, `RefreshDuration`, `ModStackAmount` |
| `src/server/game/Spells/Auras/SpellAuraEffects.h:38` | `class AuraEffect` — one effect's runtime state (current `Amount`, periodic timer, modifier owner) |
| `src/server/game/Spells/Auras/SpellAuraEffects.cpp` | per-`AuraType` handlers: `AuraEffect::HandleAuraDummy`, `HandleModStat`, `HandlePeriodicDamage`, `HandleAddPctModifier`, `HandleAddFlatModifier`, … (250+ handlers, one per aura type) |
| `src/server/game/Spells/Auras/SpellAuraDefines.h` | `enum AuraType { SPELL_AURA_NONE, SPELL_AURA_BIND_SIGHT, …, TOTAL_AURAS }` (~270 values) |
| `src/server/game/Spells/Auras/SpellAuraDefines.h` | `enum AuraEffectHandleModes { AURA_EFFECT_HANDLE_REAL, AURA_EFFECT_HANDLE_REAPPLY, AURA_EFFECT_HANDLE_CHANGE_AMOUNT, … }` |
| `src/server/game/Entities/Unit/Unit.cpp` | `Unit::_ApplyAura`, `Unit::_AddAura`, `Unit::RemoveAura(...)`, `Unit::GetAura(spellId)`, `Unit::GetAuraApplication`, `Unit::HasAuraType` — caller-side adapters around the Aura class |
| `src/server/game/Entities/Unit/Unit.h` | `typedef std::multimap<uint32, AuraApplication*> AuraApplicationMap` — the per-Unit aura table |

## Key concepts

- **`Aura` vs `AuraApplication` vs `AuraEffect`.**
  - **`Aura`** owns the spell-side state: caster GUID, base amount, duration, charges, stack count, the up-to-3 `AuraEffect` instances. One `Aura` may apply to many targets (e.g. AOE buff) — each target gets its own `AuraApplication`.
  - **`AuraApplication`** is the per-target attachment: target pointer, slot in `Unit::m_visibleAuras`, removed flag. Stored in `Unit::m_appliedAuras` keyed by spell id.
  - **`AuraEffect`** owns one effect's runtime state: amount (after modifiers), periodic timer, target. Iterates via `Aura::GetEffect(EFFECT_0..2)`.
- **Construction path.** `Spell::HandleEffects` for `SPELL_EFFECT_APPLY_AURA` calls `Aura::TryRefreshStackOrCreate` — if a same-spell aura already exists on the target with a compatible caster, refresh; else `TryCreate`. `TryCreate` chooses subclass `UnitAura` (target is Unit) or `DynObjAura` (target is dynobject for area auras).
- **Aura type dispatch.** Each `AuraEffect` has an `AuraType` (from `SpellInfo::Effects[i].ApplyAuraName`). `AuraEffect::HandleEffect(application, mode, apply)` dispatches via the `AuraEffectHandlerFn[]` table to `HandleXxx` (e.g. `HandleAddFlatModifier`, `HandlePeriodicDamage`). Mode `REAL` = first apply / final remove; `REAPPLY` = stack/refresh; `CHANGE_AMOUNT` = recompute on owner-stat change.
- **Periodic auras.** `AuraEffect::IsPeriodic()` true → `Aura::Update(diff)` ticks `_periodicTimer`; on overflow calls `AuraEffect::PeriodicTick(application)` which dispatches per type (`HandlePeriodicDamage`, `HandlePeriodicHeal`, `HandlePeriodicEnergize`, `HandlePeriodicTriggerSpell`, …).
- **Stack & refresh.** `IsAuraExclusiveBySpecificWith` (SpellInfo:509) decides if a same-target same-spell may stack. Refresh resets duration; stack increments `Aura::_stackAmount` and recalculates effect amounts.
- **Removal modes.** `AuraRemoveMode { DEFAULT, INTERRUPT, CANCEL, ENEMY_SPELL, EXPIRE, DEATH }`. Different modes trigger different cleanup paths (e.g. `EXPIRE` allows proc-on-fade; `DEATH` skips most listeners).
- **Visible aura slots.** A Unit has 64 visible aura slots (`m_visibleAuras[64]`) sent in update fields. `AuraApplication::SetSlot` claims one. Hidden auras (passives, server-only) don't take a slot.

## Flow / data shape

```
Spell::HandleEffects(target, …, SPELL_EFFECT_HANDLE_HIT_TARGET)              [Spell.cpp:5593]
  └─ case SPELL_EFFECT_APPLY_AURA in SpellEffects.cpp
       └─ Aura::TryRefreshStackOrCreate(…)                                   [SpellAuras.h:93]
          ├─ existing? → Aura::ModStackAmount or RefreshDuration
          └─ else → TryCreate
                    └─ new UnitAura(spellInfo, owner, caster, …)
                       └─ Aura::_InitEffects(effMask, caster, baseAmount)
                          └─ for each set bit: new AuraEffect(this, idx, …)
                                                  └─ ApplyAuraName → handler

Unit::_ApplyAura(application, effMask):                                       [Unit.cpp]
  ├─ inserts AuraApplication into m_appliedAuras
  ├─ for each effect: AuraEffect::HandleEffect(app, REAL, apply=true)
  │                     └─ HandleXxx (e.g. HandlePeriodicDamage stores _periodicTimer)
  └─ Aura::HandleAuraSpecificMods                                            (charges, immunities)

per tick:
  Unit::Update ──► AuraApplication::GetBase()->Update(diff)
                     ├─ tick periodic AuraEffects
                     ├─ decrement Aura::m_duration
                     └─ if expired → Unit::RemoveAura(removeMode = EXPIRE)
                                       └─ AuraEffect::HandleEffect(REAL, apply=false)
```

## Hooks & extension points

`AuraScript` (declared at `SpellScript.h:517`) gives user code lifecycle hooks. Useful handler lists, with anchor lines:

- `DoCheckAreaTarget` (732), `OnDispel` / `AfterDispel` (738/742), `OnEffectApply` / `AfterEffectApply` (749/753), `OnEffectRemove` / `AfterEffectRemove` (760/764) — see [`08-script-bindings.md`](./08-script-bindings.md) for the full list.
- Periodic-tick hooks: `OnEffectPeriodic`, `OnEffectUpdatePeriodic`, `OnEffectAbsorb`, `OnEffectManaShield`.
- Override the calculated amount: `DoEffectCalcAmount`, `DoEffectCalcPeriodic`, `DoEffectCalcSpellMod`.
- Authoring guide: [`../../03-spell-system.md`](../../03-spell-system.md). Engine-side glue: [`08-script-bindings.md`](./08-script-bindings.md).

## Cross-references

- Engine-side: [`01-cast-lifecycle.md`](./01-cast-lifecycle.md), [`05-effects.md`](./05-effects.md) (`SPELL_EFFECT_APPLY_AURA` is one of 124 effects), [`06-proc-system.md`](./06-proc-system.md) (proc auras read amount/charges from `AuraEffect`), [`07-modifiers.md`](./07-modifiers.md) (`SPELL_AURA_ADD_FLAT_MODIFIER` is the bridge to `Player::m_spellMods`)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/03-procs-and-flags.md`](../../custom-spells/03-procs-and-flags.md)
- External: Doxygen `classAura`, `classAuraEffect`, `classAuraApplication`, `classAuraScript`
