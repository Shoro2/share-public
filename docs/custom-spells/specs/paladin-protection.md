# Paladin — Protection

**Source:** [`custom_spells_paladin.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_paladin.cpp)
**ID-Range:** 900233-900265
**Status:** implemented

> **ID-Shift**: Originally planned as 900208-900238, but 900208-900210 are used as Holy helpers. Prot starts at 900234.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900234 | Consecration around you | DBC | implemented | Marker aura (DUMMY). The Consecration DBC must be patched separately. **Shared with Holy (900205) and Ret**. |
| 2 | 900235 | Avenger's Shield +9 targets | DBC | implemented | `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_JUMP_TARGETS` (17). BasePoints=9. EffectSpellClassMaskA=0x4000. |
| 3 | 900236 | Avenger's Shield +50% damage | DBC | implemented | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x4000. |
| 4 | 900237 | Holy Shield charges +99 | DBC | implemented | `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_CHARGES` (4). BasePoints=99. EffectSpellClassMaskB=0x20 (flags[1]). |
| 5 | 900238 | Holy Shield +50% damage | DBC | implemented | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskB=0x20 (flags[1]). |
| 6 | 900239 | AS leaves Consecration | C++ | implemented | Marker + C++ on AS (-48827): `AfterHit` → CastSpell(Consec 48819, triggered). Checks `HasAura(900239)`. |
| 7 | 900240 | Judgement → free AS | C++ | implemented | Marker + C++ on Judgement Damage (54158): `AfterHit` → CastSpell(AS 48827, triggered). Checks `HasAura(900240)`. |
| 8 | 900241 | Judgement cd -2sec | DBC | implemented | `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_COOLDOWN` (11). BasePoints=-2000ms. EffectSpellClassMaskA=0x800000. |

> **Note Prot**: Verify SpellFamilyFlags: AS=0x4000(flags[0]), HolyShield=0x20(flags[1]), Judgement=0x800000(flags[0]). 900237 (charges +99) must be tested whether SPELLMOD_CHARGES works.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Paladin — Prot (900233-900265)".
