# Rogue — Subtlety

**Source:** [`custom_spells_rogue.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_rogue.cpp)
**ID-Range:** 900666-900699
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900666 | Energy regen +50% | DBC | implementiert | SPELL_AURA_MOD_POWER_REGEN_PERCENT (110), MiscValue=3 (Energy). BasePoints=50. |
| 2 | 900667 | Hemorrhage +50% damage | DBC | implementiert | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x2000000 targets Hemo. |
| 3 | 900668 | Hemorrhage +9 targets | C++ | implementiert | DUMMY Marker. C++ SpellScript auf Hemo (-48660): `AfterHit` → findet bis zu 9 Feinde im 8yd Radius → CastCustomSpell(900669, damage) auf jeden. Prüft `HasAura(900668)`. |
| H1 | 900669 | Helper: Deep Cut | DBC | implementiert | Instant Physical single-target damage. BasePoints via CastCustomSpell. |

> **Hinweis Rogue**: SpellFamilyFlags verifizieren: SS=0x2(flags[0]), Mutilate=0x200000(flags[1]), Hemorrhage=0x2000000(flags[0]), BF=0x800(flags[1]). 900602 (Poison +50%) nutzt breite Mask — verifizieren ob alle Poison-Spells korrekt gemapped werden. 900635/900636 (BF Duration/Targets) nutzen SPELLMOD_DURATION bzw SPELLMOD_JUMP_TARGETS auf gleicher BF-Mask — können sich gegenseitig nicht stören da verschiedene MiscValues.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Rogue — Subtlety (900666-900699)".
