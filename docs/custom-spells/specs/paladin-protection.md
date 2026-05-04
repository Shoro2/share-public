# Paladin — Protection

**Source:** [`custom_spells_paladin.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_paladin.cpp)
**ID-Range:** 900233-900265
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

> **ID-Shift**: Ursprünglich 900208-900238 geplant, aber 900208-900210 werden als Holy-Helper verwendet. Prot startet bei 900234.

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900234 | Consecration around you | DBC | nicht getestet | Marker-Aura (DUMMY). Consecration-DBC muss separat gepatcht werden. **Shared mit Holy (900205) und Ret**. |
| 2 | 900235 | Avenger's Shield +9 targets | DBC | nicht getestet | `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_JUMP_TARGETS` (17). BasePoints=9. EffectSpellClassMaskA=0x4000. |
| 3 | 900236 | Avenger's Shield +50% damage | DBC | nicht getestet | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x4000. |
| 4 | 900237 | Holy Shield charges +99 | DBC | nicht getestet | `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_CHARGES` (4). BasePoints=99. EffectSpellClassMaskB=0x20 (flags[1]). |
| 5 | 900238 | Holy Shield +50% damage | DBC | nicht getestet | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskB=0x20 (flags[1]). |
| 6 | 900239 | AS leaves Consecration | C++ | nicht getestet | Marker + C++ auf AS (-48827): `AfterHit` → CastSpell(Consec 48819, triggered). Prüft `HasAura(900239)`. |
| 7 | 900240 | Judgement → free AS | C++ | nicht getestet | Marker + C++ auf Judgement Damage (54158): `AfterHit` → CastSpell(AS 48827, triggered). Prüft `HasAura(900240)`. |
| 8 | 900241 | Judgement cd -2sec | DBC | nicht getestet | `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_COOLDOWN` (11). BasePoints=-2000ms. EffectSpellClassMaskA=0x800000. |

> **Hinweis Prot**: SpellFamilyFlags verifizieren: AS=0x4000(flags[0]), HolyShield=0x20(flags[1]), Judgement=0x800000(flags[0]). 900237 (charges +99) muss getestet werden ob SPELLMOD_CHARGES funktioniert.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Paladin — Prot (900233-900265)".
