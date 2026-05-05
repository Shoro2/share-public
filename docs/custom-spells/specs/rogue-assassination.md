# Rogue — Assassination

**Source:** [`custom_spells_rogue.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_rogue.cpp)
**ID-Range:** 900600-900632
**Status:** Not tested (imported from `CustomSpells.md`)

> Rogue SpellFamilyName = 8. Mutilate flags[1]=0x200000, Poison flags[0]=0x8000+flags[1]=0x10000 (verify!).

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900600 | Energy regen +50% | DBC | not tested | SPELL_AURA_MOD_POWER_REGEN_PERCENT (110), MiscValue=3 (Energy). BasePoints=50. |
| 2 | 900601 | Mutilate +50% damage | DBC | not tested | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskB=0x200000 targets Mutilate. |
| 3 | 900602 | Poison damage +50% | DBC | not tested | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x8000 + EffectSpellClassMaskB=0x10000 targets Poison spells. |
| 4 | 900603 | Poison Nova proc (15%, 3s ICD) | C++ | not tested | Proc aura (DUMMY). spell_proc: ProcFlags=0x10000 (spell magic dmg), SchoolMask=8(Nature), SpellFamily=8(Rogue), 15% chance, 3s ICD. C++ HandleProc → CastSpell(900604 Poison Nova). |
| H1 | 900604 | Helper: Poison Nova AoE | DBC | not tested | Instant AoE Nature Damage. Effect=SCHOOL_DAMAGE(2), Target=DEST_AREA_ENEMY(15), SchoolMask=8(Nature), 800+200rnd, 8yd. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Rogue — Assassination (900600-900632)".
