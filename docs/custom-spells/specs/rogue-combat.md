# Rogue — Combat

**Source:** [`custom_spells_rogue.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_rogue.cpp)
**ID-Range:** 900633-900665
**Status:** implemented

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900633 | SS +50% damage | DBC | implemented | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x2 targets SS. |
| 2 | 900634 | SS +9 targets | C++ | implemented | DUMMY marker. C++ SpellScript on SS (-48638): `AfterHit` → finds up to 9 enemies in an 8yd radius → CastCustomSpell(900638, damage)  on each. Checks `HasAura(900634)`. |
| 3 | 900635 | Blade Flurry 2min duration | DBC | implemented | ADD_FLAT_MODIFIER (107) + SPELLMOD_DURATION (17). BasePoints=105000 (15s base +105s = 120s). EffectSpellClassMaskB=0x800. |
| 4 | 900636 | Blade Flurry +9 targets | DBC | implemented | ADD_FLAT_MODIFIER (107) + SPELLMOD_JUMP_TARGETS (17). BasePoints=9. EffectSpellClassMaskB=0x800. |
| 5 | 900637 | Energy regen +50% | DBC | implemented | SPELL_AURA_MOD_POWER_REGEN_PERCENT (110), MiscValue=3 (Energy). BasePoints=50. |
| H1 | 900638 | Helper: Sinister Slash | DBC | implemented | Instant Physical single-target damage. BasePoints via CastCustomSpell. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Rogue — Combat (900633-900665)".
