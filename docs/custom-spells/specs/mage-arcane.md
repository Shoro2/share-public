# Mage — Arcane

**Source:** [`custom_spells_mage.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_mage.cpp)
**ID-Range:** 900700-900713
**Status:** implemented

> 900700 is the spec-wide Evocation buff, documented in its own file [mage-shared](./mage-shared.md). The Arcane block 900701–900713 contains the Arcane-specific spells.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900701 | Mana regen +2% per missing mana % | C++ | implemented | Dynamic Mana-Regen-scaling. `PlayerScript::OnUpdateManaRegen` or periodic aura tick: Compute missing mana% → set regen bonus = missing% × 2%. At 50% mana missing → +100% Mana Regen. At 90% missing → +180%. Passive aura with `SPELL_AURA_OBS_MOD_POWER` or C++ hook on `Player::RegenerateMana()`. Very strong mana sustain mechanic. |
| 2 | 900702 | Arcane Barrage +50% damage | DBC | implemented | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Arcane Barrage (44781). SpellFamilyName=3, SpellFamilyFlags for Barrage. Simple damage multiplier. |
| 3 | 900703 | Arcane Barrage +9 targets | DBC/C++ | implemented | Arcane Barrage (44781) normally hits 3 Targets. DBC: set `MaxAffectedTargets` to 10+. Or C++: `OnObjectAreaTargetSelect` → remove target limit. |
| 4 | 900704 | Arcane Blast cast time -50% | DBC | implemented | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` (SPELLMOD_CASTING_TIME) -50% on Arcane Blast (42897). Base Cast Time 2.5s → 1.25s. Stacks with Arcane Blast Debuff (even faster with stacks). |
| 5 | 900705 | Arcane Blast +9 targets | C++ | implemented | Arcane Blast (42897) is single-target. SpellScript `AfterHit` → chain to 9 additional enemies in range. CastSpell(AB-Damage-Helper, triggered=true). Needs a helper spell (e.g. 900710). |
| 6 | 900706 | Arcane Charges stack up to 8 | DBC/C++ | implemented | Arcane Blast Debuff (36032) normally stacks up to 4. DBC: set `StackAmount` to 8. C++: If hardcoded → `AuraScript::OnStackChange` → Allow stacks >4. Each stack increases AB damage +15% and mana cost +150% (base values). 8 Stacks = +120% Damage, +1200% Mana Cost. Watch balancing! |
| 7 | 900707 | Arcane Explosion generates 1 Arcane Charge (like Arcane Blast) | C++ | implemented | Arcane Explosion (42921) is AoE instant. SpellScript `AfterCast` → ApplyAura(Arcane Blast Debuff 36032, 1 stack) on the caster. Same mechanic as AB but without consumption. AE becomes a AoE Arcane Charge Generator. |
| 8 | 900708 | Below 30% health → activate Mana Shield + restore all mana | C++ | implemented | Passive Proc aura: `PROC_FLAG_TAKEN_DAMAGE` (0x4000). `HandleProc`: If health <30% → CastSpell(Mana Shield 43020, triggered=true) + SetPower(MANA, MaxMana). ICD recommended (e.g. 60s) to prevent abuse. Very strong survival mechanic: Full mana + shield at low HP. |
| 9 | 900709 | Blink target location selection | C++ | implemented | Blink (1953) normally teleports 20yd forward. Approach: Override Blink → Click-to-Blink with a target location. SpellScript `HandleDummy`: Read SpellDestination → teleport the caster there (max range e.g. 40yd). DBC: change spell target type to `TARGET_DEST_DEST`. Client-side: spell shows a ground target cursor. Comparable to Heroic Leap targeting. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Mage — Arcane (900700-900732)".
