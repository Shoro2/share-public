# Death Knight — Blood

**Source:** [`custom_spells_dk.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_dk.cpp)
**ID-Range:** 900300-900332
**Status:** Not tested (imported from `CustomSpells.md`)

> DK SpellFamilyName = 15. Dancing Rune Weapon (49028) summons a Rune Weapon (NPC 27893) that mirrors the DK's spells.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900300 | 3 Rune Weapons simultaneously | C++ | not tested | Marker aura (DUMMY). C++ SpellScript on DRW (49028): `AfterCast` → 2× CastSpell(DRW, triggered=true). Checks `HasAura(900300)`. |
| 2 | 900301 | Rune Weapon double-casts | C++ | not tested | Marker aura (DUMMY). C++ AuraScript on DRW (49028): `OnEffectProc` → extra CastSpell/DealMeleeDamage. Checks `HasAura(900301)`. Rune Weapon casts every spell 2× instead of 1×. |
| 3 | 900302 | Heart Strike +50% damage | DBC | not tested | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x2000000 (HS flags[0], verify!). |
| 4 | 900303 | Heart Strike +9 targets | C++ | not tested | Marker aura (DUMMY). C++ SpellScript on HS (-55050): `AfterHit` → DealDamage on 9 extra enemies in 8yd. Checks `HasAura(900303)`. |
| 5 | 900304 | Dealing damage → chance Death Coil | C++ | not tested | Proc aura (DUMMY). spell_proc: ProcFlags=0x14, 15% chance, 3s ICD. C++ HandleProc → CastSpell(47632 Death Coil Damage, triggered). |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "DK — Blood (900300-900332)".
