# Rogue — Subtlety

**Source:** [`custom_spells_rogue.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_rogue.cpp)
**ID-Range:** 900666-900699
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900666 | Energy regen +50% | DBC | not tested | SPELL_AURA_MOD_POWER_REGEN_PERCENT (110), MiscValue=3 (Energy). BasePoints=50. |
| 2 | 900667 | Hemorrhage +50% damage | DBC | not tested | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x2000000 targets Hemo. |
| 3 | 900668 | Hemorrhage +9 targets | C++ | not tested | DUMMY marker. C++ SpellScript on Hemo (-48660): `AfterHit` → finds up to 9 enemies in an 8yd radius → CastCustomSpell(900669, damage)  on each. Checks `HasAura(900668)`. |
| H1 | 900669 | Helper: Deep Cut | DBC | not tested | Instant Physical single-target damage. BasePoints via CastCustomSpell. |

> **Note Rogue**: Verify SpellFamilyFlags: SS=0x2(flags[0]), Mutilate=0x200000(flags[1]), Hemorrhage=0x2000000(flags[0]), BF=0x800(flags[1]). 900602 (Poison +50%) uses a broad mask — verify whether all poison spells are mapped correctly. 900635/900636 (BF Duration/Targets) use SPELLMOD_DURATION and SPELLMOD_JUMP_TARGETS respectively on the same BF mask — cannot conflict because they use different MiscValues.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Rogue — Subtlety (900666-900699)".
