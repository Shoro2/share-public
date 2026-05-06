# spells — Proc system

> Aura-driven side-effects that fire when a *triggering* spell event matches a *listening* aura's proc filters. Filters live in the `spell_proc` DB table; runtime dispatch is `Unit::TriggerAurasProcOnEvent`. Cross-link [`03-aura-system.md`](./03-aura-system.md), [`01-cast-lifecycle.md`](./01-cast-lifecycle.md), [`../../03-spell-system.md`](../../03-spell-system.md) (user-side `OnProc` authoring).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/SpellMgr.h:34` | `class ProcEventInfo;` forward |
| `src/server/game/Spells/SpellMgr.h:106` | `enum ProcFlags` — high-level event family (e.g. `PROC_FLAG_KILLED`, `PROC_FLAG_TAKEN_DAMAGE`, `PROC_FLAG_DEAL_HARMFUL_SPELL`, `PROC_FLAG_DONE_PERIODIC`) |
| `src/server/game/Spells/SpellMgr.h:196` | `enum ProcFlagsExLegacy` (kept for backward compat) |
| `src/server/game/Spells/SpellMgr.h:236` | `enum ProcFlagsSpellType` — bitmask filter on the *triggering* spell's effect type (`PROC_SPELL_TYPE_DAMAGE`, `_HEAL`, `_NO_DMG_HEAL`) |
| `src/server/game/Spells/SpellMgr.h:245` | `enum ProcFlagsSpellPhase` — bitmask filter on cast phase (`PROC_SPELL_PHASE_CAST`, `_HIT`, `_FINISH`) |
| `src/server/game/Spells/SpellMgr.h:254` | `enum ProcFlagsHit` — bitmask filter on hit outcome (`PROC_HIT_NORMAL`, `_CRITICAL`, `_MISS`, `_DODGE`, `_PARRY`, `_BLOCK`, `_ABSORB`, `_REFLECT`, `_INTERRUPT`, `_FULL_BLOCK`) |
| `src/server/game/Spells/SpellMgr.h:283` | `struct SpellProcEntry` — one `spell_proc` row: `ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`, `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges` (see column comments at lines 290–297) |
| `src/server/game/Spells/SpellMgr.cpp:1887` | `SpellMgr::LoadSpellProcs()` — populates `mSpellProcMap` from `spell_proc` DB table |
| `src/server/game/Entities/Unit/Unit.h:439` | `class ProcEventInfo` — runtime context: `actor`, `actionTarget`, `procTarget`, `typeMask`, `spellTypeMask`, `spellPhaseMask`, `hitMask`, `Spell*`, `DamageInfo*`, `HealInfo*`, `triggeredByAuraSpell`, `procAuraEffectIndex` |
| `src/server/game/Entities/Unit/Unit.cpp:292` | `ProcEventInfo::ProcEventInfo(...)` ctor |
| `src/server/game/Entities/Unit/Unit.cpp:12861` | `Unit::TriggerAurasProcOnEvent(CalcDamageInfo&)` — convenience wrapper for melee/ranged auto-attacks |
| `src/server/game/Entities/Unit/Unit.cpp:12867` | `Unit::TriggerAurasProcOnEvent(myProcAuras, targetProcAuras, actionTarget, typeMaskActor, typeMaskActionTarget, spellTypeMask, spellPhaseMask, hitMask, Spell*, DamageInfo*, HealInfo*)` — main entry; builds two `ProcEventInfo`s (actor-side, target-side) and dispatches |
| `src/server/game/Entities/Unit/Unit.cpp:12903` | `Unit::TriggerAurasProcOnEvent(eventInfo, aurasTriggeringProc)` — leaf; runs each `AuraApplication`'s proc, applies cooldown + charge consumption + AuraScript hooks |
| `src/server/game/Spells/Spell.cpp:2200` | `Spell::prepareDataForTriggerSystem(triggeredByAura)` — computes the `typeMask` and `hitMask` for the cast just resolved |

## Key concepts

- **Two separate proc paths fire per event.** When unit A spell-hits unit B, the engine builds two `ProcEventInfo`s:
  - **Actor-side**: A's auras with matching `PROC_FLAG_DONE_*` flags.
  - **Target-side**: B's auras with matching `PROC_FLAG_TAKEN_*` flags.
  Both run inside the same `TriggerAurasProcOnEvent(..., 12867)` call.
- **Five-axis filter.** A proc fires only if the event matches *all* of: `ProcFlags & typeMask`, `SpellTypeMask & spellTypeMask`, `SpellPhaseMask & spellPhaseMask`, `HitMask & hitMask`, plus per-row `Chance`/`ProcsPerMinute`. Empty (0) means "match anything".
- **`spell_proc` overrides DBC.** A row in `spell_proc` (loaded at line 1887) overwrites the `procFlags`/`procChance`/`procCharges` fields baked into the `SpellEntry` DBC row — see column comment at SpellMgr.h:290 ("if nonzero — overwrite procFlags field for given Spell.dbc entry"). Custom spells use `spell_proc` rows instead of patching `Spell.dbc` for proc data.
- **`PPM` (procs-per-minute).** When `ProcsPerMinute > 0`, the engine computes `chance = PPM * weaponSpeedSec / 60`. Used for weapon-strike-based procs (Windfury, Vampiric Strike).
- **Charges & cooldown.** A proc with `Charges > 0` decrements on every fire; the aura is removed when charges hit 0. `Cooldown > 0` (ms) per-spell suppresses re-fire (anti-machine-gun procs).
- **Triggered-by-aura suppression.** `eventInfo.triggeredByAuraSpell` is set when the *cause* of the event was itself a triggered spell from another aura; this prevents some proc loops (e.g. an aura that triggers itself).

## Flow / data shape

```
Spell::cast finishes (or melee swing lands) ──► one of:
  Spell.cpp:2200        Spell::prepareDataForTriggerSystem
  Unit.cpp:12861        Unit::TriggerAurasProcOnEvent(CalcDamageInfo&)         (melee)

Both build:
  typeMaskActor       (e.g. PROC_FLAG_DEAL_HARMFUL_SPELL)
  typeMaskActionTarget (e.g. PROC_FLAG_TAKEN_DAMAGE)
  spellTypeMask, spellPhaseMask, hitMask

Unit::TriggerAurasProcOnEvent(myAuras, targetAuras, …)                          [Unit.cpp:12867]
   ├─ ProcEventInfo myEvent(this, actionTarget, actionTarget, typeMaskActor, …) [12870]
   ├─ Unit::TriggerAurasProcOnEvent(myEvent, myAuras)                           [12903]
   │     for each AuraApplication in myAuras:
   │        if (procEntry filter passes && Aura::IsProcOnCooldown == false)
   │           if (random() < Chance):
   │              AuraScript::OnProc(eventInfo)             // user hook returns true=proceed
   │              Aura::HandleProc(eventInfo)              // engine: invoke AuraEffect::HandleProc per effect
   │                 ├─ trigger SpellEntry from AuraEffect::GetSpellEffectInfo (TriggerSpell)
   │                 ├─ apply Charges decrement
   │                 └─ start ProcCooldown
   │
   └─ ProcEventInfo targetEvent(this, actionTarget, this, typeMaskActionTarget, …) [12892]
      Unit::TriggerAurasProcOnEvent(targetEvent, targetAuras)
```

For an end-to-end example with table rows, see [`../../03-spell-system.md`](../../03-spell-system.md) and [`../../custom-spells/03-procs-and-flags.md`](../../custom-spells/03-procs-and-flags.md).

## Hooks & extension points

`AuraScript` (`SpellScript.h:517`) provides three proc hook points:

| Hook | Fires | Typical use |
|---|---|---|
| `DoCheckProc` | before charge consumption + chance roll | reject the proc based on event content |
| `OnProc` | after rules pass, before engine `HandleProc` | run user logic (cast spell, energize, modify event) |
| `AfterProc` | after engine handled the proc | cleanup (remove debuff, log) |

Plus per-effect prepare/handle:
- `DoPrepareProc` — fill in event metadata before `OnProc` is called.
- `DoEffectProc(EFFECT_0..2)` — invoked once per `AuraEffect` of the proccing aura; the script may suppress the default trigger.

User-side authoring guide: [`../../03-spell-system.md`](../../03-spell-system.md). DB-driven authoring (`spell_proc` rows): [`../../custom-spells/03-procs-and-flags.md`](../../custom-spells/03-procs-and-flags.md).

## Cross-references

- Engine-side: [`01-cast-lifecycle.md`](./01-cast-lifecycle.md) (sets `prepareDataForTriggerSystem`), [`03-aura-system.md`](./03-aura-system.md) (`AuraEffect::HandleProc`), [`05-effects.md`](./05-effects.md), [`08-script-bindings.md`](./08-script-bindings.md), [`../combat/01-damage-pipeline.md`](../combat/01-damage-pipeline.md) (where `CalcDamageInfo` for melee comes from)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/03-procs-and-flags.md`](../../custom-spells/03-procs-and-flags.md), [`../../09-db-tables.md`](../../09-db-tables.md) (`spell_proc` schema)
- External: Doxygen `classProcEventInfo`, `classSpellMgr`
