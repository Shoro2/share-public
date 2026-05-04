# Death Knight — Blood

**Source:** [`custom_spells_dk.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_dk.cpp)
**ID-Range:** 900300-900332
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

> DK SpellFamilyName = 15. Dancing Rune Weapon (49028) beschwört ein Rune Weapon (NPC 27893) das Spells des DK kopiert.

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900300 | 3 Rune Weapons gleichzeitig | C++ | nicht getestet | Marker-Aura (DUMMY). C++ SpellScript auf DRW (49028): `AfterCast` → 2× CastSpell(DRW, triggered=true). Prüft `HasAura(900300)`. |
| 2 | 900301 | Rune Weapon double-casts | C++ | nicht getestet | Marker-Aura (DUMMY). C++ AuraScript auf DRW (49028): `OnEffectProc` → extra CastSpell/DealMeleeDamage. Prüft `HasAura(900301)`. Rune Weapon castet jeden Spell 2× statt 1×. |
| 3 | 900302 | Heart Strike +50% damage | DBC | nicht getestet | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x2000000 (HS flags[0], verify!). |
| 4 | 900303 | Heart Strike +9 targets | C++ | nicht getestet | Marker-Aura (DUMMY). C++ SpellScript auf HS (-55050): `AfterHit` → DealDamage auf 9 Extra-Feinde in 8yd. Prüft `HasAura(900303)`. |
| 5 | 900304 | Dealing damage → chance Death Coil | C++ | nicht getestet | Proc-Aura (DUMMY). spell_proc: ProcFlags=0x14, 15% Chance, 3s ICD. C++ HandleProc → CastSpell(47632 Death Coil Damage, triggered). |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "DK — Blood (900300-900332)".
