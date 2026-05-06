# spells — Spell modifiers

> Per-`Player` `SpellModifier` list that lets passive auras tweak the numeric output of *other* spells (cast time, cost, damage, duration, crit %, …) without touching the spells themselves. Cross-link [`03-aura-system.md`](./03-aura-system.md) (`SPELL_AURA_ADD_FLAT_MODIFIER` / `_ADD_PCT_MODIFIER` are the bridges), [`01-cast-lifecycle.md`](./01-cast-lifecycle.md) (caller).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/SpellDefines.h:74` | `enum SpellModOp` — what attribute is being modified (`SPELLMOD_DAMAGE`, `SPELLMOD_DURATION`, `SPELLMOD_COST`, `SPELLMOD_CASTING_TIME`, `SPELLMOD_CRITICAL_CHANCE`, `SPELLMOD_RANGE`, `SPELLMOD_RADIUS`, `SPELLMOD_THREAT`, …) |
| `src/server/game/Entities/Player/Player.h:92` | `enum SpellModType { SPELLMOD_FLAT, SPELLMOD_PCT }` |
| `src/server/game/Entities/Player/Player.h:181` | `struct SpellModifier { spellId, op, type, value, mask[3], charges, lastAffectedAuraSpellId }` |
| `src/server/game/Entities/Player/Player.h` | `Player::m_spellMods[MAX_SPELLMOD][SPELLMOD_END]` — 2-D registry of active modifiers, keyed by `SpellModOp` and `SpellModType` |
| `src/server/game/Entities/Player/Player.cpp:9759` | `Player::ApplySpellMod(spellId, op, basevalue, spell, temporaryPet)` — main consumer; iterates `m_spellMods[op]` and applies matching modifiers to `basevalue` |
| `src/server/game/Entities/Player/Player.cpp:9837-9839` | template instantiations: `int32`, `uint32`, `float` |
| `src/server/game/Entities/Player/Player.cpp:9841` | `Player::AddSpellMod(SpellModifier* mod, bool apply)` — register/unregister; called from `AuraEffect::HandleAddFlatModifier` / `HandleAddPctModifier` (`apply=true`) and on aura removal (`apply=false`) |
| `src/server/game/Spells/Auras/SpellAuraEffects.cpp` | `AuraEffect::HandleAddFlatModifier` / `HandleAddPctModifier` — owners; allocate the `SpellModifier` from `AuraEffect`-side state and call `Player::AddSpellMod` |
| `src/server/game/Spells/SpellScript.h` | `AuraScript::DoEffectCalcSpellMod` hook — user-side override for the modifier amount before it is registered |

## Key concepts

- **Two flavors per attribute.** Each `SpellModOp` can have flat (`SPELLMOD_FLAT`, additive) and percent (`SPELLMOD_PCT`, multiplicative) modifiers. The engine applies *all* flats first, then *all* percents — order is enforced inside `Player::ApplySpellMod`.
- **Mask-gated by spell family.** A `SpellModifier` only affects target spells whose `SpellInfo::SpellFamilyName == mod->spellFamilyName` and whose `SpellInfo::SpellFamilyFlags` has any bit set in `mod->mask[]`. The DBC's `SpellClassMask[3]` for the modifier's source spell becomes the `mask[]`. Cross-link [`../../custom-spells/03-procs-and-flags.md`](../../custom-spells/03-procs-and-flags.md) for SpellFamily/Flag research.
- **Charges = N-shot consumables.** A modifier with `charges > 0` decrements every time it modifies a value; on charge 0 the source aura is removed. Used for "next spell costs no mana" effects (e.g. *Clearcasting*).
- **`m_spellMods` is per-Player.** Creature/NPC casters do **not** carry this list. Modifiers from passive auras on a Creature are applied directly via the aura mechanic without the SpellMod indirection. (The struct exists only on `Player`.)
- **Owner of the modifier.** When the engine wants to discount cast time on a *triggered* sub-cast, it looks up the player via `Spell::GetSpellModOwner` (returns `m_originalCaster` if it is a Player). For auto-attacks/melee, modifiers can apply to the weapon swing's threat/damage via the same dispatch.

## Flow / data shape

```
Cast a passive aura (e.g. talent) that has SPELL_AURA_ADD_PCT_MODIFIER:
    SPELL_EFFECT_APPLY_AURA  →  AuraEffect ctor
                                AuraType = SPELL_AURA_ADD_PCT_MODIFIER
    Aura applied              →  AuraEffect::HandleAddPctModifier(application, REAL, true)
                                ├─ allocate SpellModifier{ op=DAMAGE, type=PCT, value=+10, mask[]=… }
                                └─ Player::AddSpellMod(mod, apply=true)                [9841]
                                       └─ m_spellMods[op][type].push_back(mod)

Cast a target spell (the consumer):
    Spell::prepare       ──►  uses Player::ApplySpellMod(spellId, SPELLMOD_CASTING_TIME, m_casttime, this)
    Spell::cast          ──►  uses Player::ApplySpellMod(spellId, SPELLMOD_COST, m_powerCost, this)
    HandleEffects (HIT)  ──►  uses Player::ApplySpellMod(spellId, SPELLMOD_DAMAGE, damage, this)

Player::ApplySpellMod(spellId, op, basevalue, spell):                          [9759]
   info = sSpellMgr->GetSpellInfo(spellId)
   for type in {FLAT, PCT}:
      for mod in m_spellMods[op][type]:
         if (info->SpellFamilyName != mod->spellFamilyName) continue
         if (!(info->SpellFamilyFlags & mod->mask)) continue
         if (type == FLAT) basevalue += mod->value
         else              basevalue *= 1.0f + mod->value/100.0f
         if (mod->charges > 0 && --mod->charges == 0) drop_aura()
   return basevalue

Aura removed:
    AuraEffect::HandleAddPctModifier(application, REAL, apply=false)
    └─ Player::AddSpellMod(mod, apply=false)
         └─ m_spellMods[op][type].erase(mod); free
```

## Hooks & extension points

User-side overrides via `AuraScript`:

- `DoEffectCalcSpellMod` — invoked once per modifier when the source aura's `SPELL_AURA_ADD_*_MODIFIER` effect is applied. The script may rewrite `mod->value` or `mod->mask[]` before `Player::AddSpellMod` registers it.
- `OnEffectApply` / `OnEffectRemove` (with `EffectIndex` matching the modifier effect) can replace the standard register/unregister with custom logic — but in 99% of cases the default handler is correct.

There is **no** "enumerate all modifiers" engine hook. To inspect a Player's active modifiers in C++, walk `Player::m_spellMods[op][type]` directly.

User-side authoring: [`../../03-spell-system.md`](../../03-spell-system.md). Engine-side glue: [`08-script-bindings.md`](./08-script-bindings.md).

## Cross-references

- Engine-side: [`01-cast-lifecycle.md`](./01-cast-lifecycle.md), [`03-aura-system.md`](./03-aura-system.md), [`05-effects.md`](./05-effects.md), [`08-script-bindings.md`](./08-script-bindings.md), [`../entities/04-player.md`](../entities/04-player.md) (where `m_spellMods` lives)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/03-procs-and-flags.md`](../../custom-spells/03-procs-and-flags.md)
- External: Doxygen `classPlayer` (member `m_spellMods`), `structSpellModifier`, `enumSpellModOp`
