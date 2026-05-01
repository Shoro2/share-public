# Rogue — Combat

**Source:** [`custom_spells_rogue.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_rogue.cpp)
**ID-Range:** 900633-900665
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900633 | SS +50% damage | DBC | implementiert | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x2 targets SS. |
| 2 | 900634 | SS +9 targets | C++ | implementiert | DUMMY Marker. C++ SpellScript auf SS (-48638): `AfterHit` → findet bis zu 9 Feinde im 8yd Radius → CastCustomSpell(900638, damage) auf jeden. Prüft `HasAura(900634)`. |
| 3 | 900635 | Blade Flurry 2min duration | DBC | implementiert | ADD_FLAT_MODIFIER (107) + SPELLMOD_DURATION (17). BasePoints=105000 (15s base +105s = 120s). EffectSpellClassMaskB=0x800. |
| 4 | 900636 | Blade Flurry +9 targets | DBC | implementiert | ADD_FLAT_MODIFIER (107) + SPELLMOD_JUMP_TARGETS (17). BasePoints=9. EffectSpellClassMaskB=0x800. |
| 5 | 900637 | Energy regen +50% | DBC | implementiert | SPELL_AURA_MOD_POWER_REGEN_PERCENT (110), MiscValue=3 (Energy). BasePoints=50. |
| H1 | 900638 | Helper: Sinister Slash | DBC | implementiert | Instant Physical single-target damage. BasePoints via CastCustomSpell. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Rogue — Combat (900633-900665)".
