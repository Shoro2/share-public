# Mage — Fire

**Source:** [`custom_spells_mage.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_mage.cpp)
**ID-Range:** 900733-900740
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900733 | Fireball +50% damage | DBC | not tested | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Fireball (42833). SpellFamilyName=3, SpellFamilyFlags for Fireball. Simple damage multiplier. |
| 2 | 900734 | Fireball +9 targets | C++ | not tested | Fireball (42833) is single-target Projectile. SpellScript `AfterHit` → chain to 9 additional enemies in range. CastSpell(Fireball-Damage-Helper, triggered=true). Needs a helper spell (e.g. 900739). |
| 3 | 900735 | Pyroblast +9 targets | C++ | not tested | Pyroblast (42891) is single-target. SpellScript `AfterHit` → chain to 9 additional enemies. CastSpell(Pyro-Damage-Helper, triggered=true). Needs a helper spell (e.g. 900740). |
| 4 | 900736 | Pyroblast +50% damage | DBC | not tested | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Pyroblast (42891). Simple damage multiplier. |
| 5 | 900737 | Fire Blast off GCD and usable while casting | DBC/C++ | not tested | Fire Blast (42873): DBC → `StartRecoveryCategory` = 0 (off GCD). set the `SPELL_ATTR4_CAN_CAST_WHILE_CASTING` attribute. Lets Fire Blast be used as a weave spell during Fireball/Pyroblast casts. Comparable to retail Fire Mage design. |
| 6 | 900738 | Pyroblast now triggers Hot Streak | C++ | not tested | Hot Streak (48108) normally procs after 2 consecutive crits. Approach: A Pyroblast cast (even non-crit) → automatically apply the Hot Streak buff (48108). SpellScript on Pyroblast `AfterCast` → AuraScript: ApplyAura(Hot Streak). Effect: every Pyroblast guarantees the next instant Pyroblast. Extremely strong damage loop! |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Mage — Fire (900733-900765)".
