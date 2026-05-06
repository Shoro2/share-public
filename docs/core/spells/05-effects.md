# spells — Effect dispatch

> Each `SpellInfo::Effects[i].Effect` (one of ~150 `SPELL_EFFECT_*` enum values) routes via `Spell::HandleEffects(target, …, mode)` to one of 124 `Spell::Effect*` functions in `SpellEffects.cpp`. Cross-link [`01-cast-lifecycle.md`](./01-cast-lifecycle.md) (caller), [`03-aura-system.md`](./03-aura-system.md) (`SPELL_EFFECT_APPLY_AURA` is the bridge to auras).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/SharedDefines.h` | `enum SpellEffects { SPELL_EFFECT_NONE = 0, SPELL_EFFECT_INSTAKILL = 1, …, TOTAL_SPELL_EFFECTS }` (~150 values; only ~124 are wired to a handler — the rest are `EffectNULL`/`EffectUnused`) |
| `src/server/game/Spells/Spell.h:250` | `enum SpellEffectHandleMode { LAUNCH, LAUNCH_TARGET, HIT, HIT_TARGET }` |
| `src/server/game/Spells/Spell.cpp:5593` | `Spell::HandleEffects(unit, item, go, effectIdx, mode)` — the dispatcher; switches on `m_spellInfo->Effects[i].Effect` and calls the matching `EffectXxx` member function |
| `src/server/game/Spells/SpellEffects.cpp` | implementations of the 124 `Spell::Effect*` member functions (one per non-null effect) |
| `src/server/game/Spells/SpellEffects.cpp:5009` | inside `Spell::EffectKnockBack` (representative example) |
| `src/server/game/Spells/SpellEffects.cpp:5123` | inside `Spell::EffectPullTowards` |
| `src/server/game/Spells/Spell.cpp:4218` | `HandleEffects(nullptr, nullptr, nullptr, j, SPELL_EFFECT_HANDLE_HIT)` — caster-side post-resolution |
| `src/server/game/Spells/Spell.cpp:8268` | `HandleEffects(nullptr, nullptr, nullptr, i, SPELL_EFFECT_HANDLE_LAUNCH)` — caster-side pre-resolution |
| `src/server/game/Spells/Spell.cpp:8353` | `HandleEffects(unit, nullptr, nullptr, i, SPELL_EFFECT_HANDLE_LAUNCH_TARGET)` — per-target pre-resolution |
| `src/server/game/Spells/Spell.cpp:2558,3193` | per-target `HIT_TARGET` calls inside `DoAllEffectOnTarget` and the magnet-redirect path |

## Key concepts

- **Effects array is fixed-length 3.** `MAX_SPELL_EFFECTS = 3`; the engine iterates indices `EFFECT_0..2` for every cast, even if only some are non-`SPELL_EFFECT_NONE`. `m_spellInfo->Effects[i].Effect == SPELL_EFFECT_NONE` short-circuits.
- **Mode separates "before" from "after" resolution.** `LAUNCH`/`LAUNCH_TARGET` fire **before** the target list is finalized — used to compute initial damage, pick chain pivots, or trigger immediate visual effects. `HIT`/`HIT_TARGET` fire **after** the target list is final — most damage/aura application happens here.
- **Two scopes per mode.** `LAUNCH` and `HIT` are **caster-scoped** (called once with `target=nullptr`). `LAUNCH_TARGET` and `HIT_TARGET` are **per-target** (called once per `m_UniqueTargetInfo` entry).
- **Switch in `HandleEffects` is hand-written.** `Spell.cpp:5593` contains a long `switch (m_spellInfo->Effects[i].Effect)` directly invoking `EffectXxx(i)`. Adding a new effect requires (a) the enum entry in `SharedDefines.h`, (b) the `case` in the switch, and (c) the implementation in `SpellEffects.cpp`.
- **Default fallthrough is silent.** Unmapped effects log via `LOG_DEBUG("spells", "Spell::HandleEffects ... unknown effect")` and return — they will *not* abort the cast. Unwired but enum-listed effects (`EffectUnused1..N`, `EffectNULL`) are explicitly handled.

## Effect categories (SPELL_EFFECT_* groups)

Sample of the 124 wired effects, grouped by purpose. The full enum lives at `SharedDefines.h`; per-effect implementation in `SpellEffects.cpp` (one function per `case`).

| Category | Representative effects |
|---|---|
| **Direct damage / heal** | `SCHOOL_DAMAGE`, `WEAPON_DAMAGE`, `WEAPON_DAMAGE_NOSCHOOL`, `NORMALIZED_WEAPON_DMG`, `WEAPON_PERCENT_DAMAGE`, `HEAL`, `HEAL_PCT`, `HEAL_MAX_HEALTH`, `HEALTH_LEECH`, `HEAL_MECHANICAL` |
| **Aura attach / detach** | `APPLY_AURA`, `APPLY_AREA_AURA_PARTY`, `APPLY_AREA_AURA_RAID`, `APPLY_AREA_AURA_FRIEND`, `APPLY_AREA_AURA_ENEMY`, `APPLY_AREA_AURA_PET`, `APPLY_AREA_AURA_OWNER`, `DISPEL`, `DISPEL_MECHANIC` |
| **Power / resource** | `ENERGIZE`, `ENERGIZE_PCT`, `POWER_BURN`, `POWER_DRAIN`, `MANA_DRAIN`, `RESURRECT`, `RESURRECT_NEW` |
| **Movement / position** | `TELEPORT_UNITS`, `TELEPORT_UNITS_FACE_CASTER`, `KNOCK_BACK`, `KNOCK_BACK_DEST`, `PULL_TOWARDS`, `PULL_TOWARDS_DEST`, `LEAP`, `LEAP_BACK`, `JUMP`, `JUMP_DEST` |
| **Summon / pet** | `SUMMON`, `SUMMON_PET`, `SUMMON_PLAYER`, `SUMMON_OBJECT_WILD`, `SUMMON_OBJECT_SLOT1..4`, `TRANSFORM`, `DISMISS_PET` |
| **Item / loot** | `CREATE_ITEM`, `CREATE_RANDOM_ITEM`, `OPEN_LOCK`, `OPEN_LOCK_ITEM`, `ENCHANT_ITEM`, `ENCHANT_ITEM_TEMPORARY`, `ENCHANT_ITEM_PRISMATIC`, `DESTROY_ITEM`, `LOOT_BONUS` |
| **Skill / talent / spell** | `LEARN_SPELL`, `LEARN_PET_SPELL`, `SKILL`, `SKILL_STEP`, `SKINNING`, `TRADE_SKILL`, `TEACH_FIELD_BUFF`, `DUEL`, `STUCK` |
| **Stealth / detect / leap** | `BIND`, `RECALL`, `STEALTH`, `STEALTH_DETECT`, `INVISIBILITY`, `INVISIBILITY_DETECT`, `THREAT`, `THREAT_ALL` |
| **GameObject / world** | `OPEN_LOCK`, `ACTIVATE_OBJECT`, `WMO_DAMAGE`, `WMO_REPAIR`, `WMO_CHANGE`, `KILL_GAME_OBJECT`, `TRANS_DOOR`, `INSTAKILL` |
| **Trigger / channel / proc** | `TRIGGER_SPELL`, `TRIGGER_MISSILE`, `TRIGGER_SPELL_2`, `TRIGGER_SPELL_WITH_VALUE`, `PERSISTENT_AREA_AURA`, `CHARGE`, `CHARGE_DEST` |
| **Combat — special** | `INTERRUPT_CAST`, `BLOCK`, `PARRY`, `DODGE`, `BLOCK_REGEN`, `INSTAKILL`, `SCRIPT_EFFECT` (the catch-all delegating to `SpellScript::OnEffectHit`/`OnEffectHitTarget`), `SEND_EVENT` |

`SCRIPT_EFFECT` is the canonical place for custom one-off behavior — see [`08-script-bindings.md`](./08-script-bindings.md). The fork's custom Spell.dbc rows commonly use `SCRIPT_EFFECT` + a registered `SpellScript` implementation.

## Flow / data shape

```
Spell::handle_immediate()                     [4053]
  ├─ HandleEffects(nullptr, nullptr, nullptr, i, LAUNCH)              [8268]
  │     └─ switch effect → EffectKnockBack(i) / EffectSchoolDmg(i) / …
  │
  ├─ for each (target, effMask) in m_UniqueTargetInfo:
  │     HandleEffects(target, nullptr, nullptr, i, LAUNCH_TARGET)     [8353]
  │
  ├─ Spell::DoAllEffectOnTarget(targetInfo)
  │     └─ for each effIdx set in effMask:
  │           HandleEffects(unitTarget, …, effIdx, HIT_TARGET)        [2558,3193]
  │
  └─ HandleEffects(nullptr, …, i, HIT)                                [4218]
```

A specific `Spell::Effect*` function (e.g. `Spell::EffectSchoolDamage`):
- reads `m_spellInfo->Effects[effIndex]` for `BasePoints`, `MiscValue`, …
- computes `damage = effInfo.CalcValue(m_caster) + bonusFromMods`
- delegates to `Unit::DealDamage` (cross-link [`../combat/01-damage-pipeline.md`](../combat/01-damage-pipeline.md))
- updates `m_caster->ProcDamageAndSpell` inputs (cross-link [`06-proc-system.md`](./06-proc-system.md))

## Hooks & extension points

`SpellScript`'s `EffectHandler` hook list (`SpellScript.h:333-336`) lets a script attach to a specific `(effIndex, effectName)` pair:

```cpp
class spell_my_custom : public SpellScript {
    void HandleHit(SpellEffIndex effIndex)
    {
        if (Unit* tgt = GetHitUnit())
            tgt->CastSpell(tgt, MY_TRIGGER_SPELL, true);
    }
    void Register() override {
        OnEffectHitTarget += SpellEffectFn(spell_my_custom::HandleHit, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};
```

The engine fires `OnEffectLaunch` / `OnEffectLaunchTarget` / `OnEffectHit` / `OnEffectHitTarget` from inside `HandleEffects`, *replacing* the default behavior if the script registered against the same `(effIndex, effectName)`. See [`08-script-bindings.md`](./08-script-bindings.md) for the registration API and [`../../03-spell-system.md`](../../03-spell-system.md) for full authoring examples.

## Cross-references

- Engine-side: [`01-cast-lifecycle.md`](./01-cast-lifecycle.md), [`02-spell-info.md`](./02-spell-info.md), [`03-aura-system.md`](./03-aura-system.md), [`04-targeting.md`](./04-targeting.md), [`08-script-bindings.md`](./08-script-bindings.md), [`../combat/01-damage-pipeline.md`](../combat/01-damage-pipeline.md)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/05-complex-spells.md`](../../custom-spells/05-complex-spells.md)
- External: Doxygen `classSpell` (member list shows all `Effect*` overloads)
