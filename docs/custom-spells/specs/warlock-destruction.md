# Warlock — Destruction

**Source:** [`custom_spells_warlock.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warlock.cpp)
**ID-Range:** 900866-900899
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900866 | Shadow Bolt +9 targets | C++ | not tested | Shadow Bolt (47809) is single-target. SpellScript `AfterHit` → chain to 9 additional enemies. CastSpell(SB-Damage-Helper, triggered=true). Needs a helper spell (e.g. 900871). |
| 2 | 900867 | Shadow Bolt +50% damage | DBC | not tested | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Shadow Bolt (47809). Simple damage multiplier. |
| 3 | 900868 | Chaos Bolt +50% damage | DBC | not tested | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Chaos Bolt (59172). Simple damage multiplier. |
| 4 | 900869 | Chaos Bolt cooldown -2 sec | DBC | not tested | Passive aura: `SPELL_AURA_ADD_FLAT_MODIFIER` (SPELLMOD_COOLDOWN) -2000ms on Chaos Bolt (59172). Base CD 12s → 10s. Or DBC directly: reduce `RecoveryTime`. |
| 5 | 900870 | Chaos Bolt +9 targets | C++ | not tested | Chaos Bolt (59172) is single-target. SpellScript `AfterHit` → chain to 9 additional enemies. CastSpell(CB-Damage-Helper, triggered=true). Chaos Bolt ignores resistances — the helper spell should do the same (attribute `SPELL_ATTR0_NO_IMMUNITIES` or similar). Needs a helper spell (e.g. 900872). |

> **Helper-Spells Warlock**: 900800 (DoT AoE) → Shadow-AoE-Helper 900803. 900837 (Imp Firebolt +9) → Helper 900841. 900834 (Meta AoE) → Helper 900842. 900834 (Meta Heal) → Helper 900843. 900838 (FG Cleave) → Helper 900844. 900866 (SB +9) → Helper 900871. 900870 (CB +9) → Helper 900872. 900835 (Lesser Demons) needs custom creature templates.

> **Particularly elaborate**: 900802 (DoT Spread) can grow exponentially — needs a target cap to protect server performance. 900835 (Lesser Demon Spawn) needs custom creature templates per pet type with their own AI. 900840 (Sacrifice All Bonuses) must identify and stack all pet type buffs correctly. 900833 (Meta Duration Extension) + 900834 (Meta AoE+Heal) together turn Demo-Lock into a permanently transformed AoE healer-tank hybrid.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Warlock — Destruction (900866-900899)".
