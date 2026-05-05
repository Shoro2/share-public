# Paladin — Retribution

**Source:** [`custom_spells_paladin.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_paladin.cpp)
**ID-Range:** 900266-900299
**Status:** implemented

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900268 | Consecration around you | DBC | implemented | Marker aura (DUMMY). **Shared concept with Holy (900205) and Prot (900234)**. Separate ID per spec. |
| 2 | 900269 | Judgement cd -2sec | DBC | implemented | `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_COOLDOWN` (11). BasePoints=-2000ms. EffectSpellClassMaskA=0x800000. **Shared concept with Prot (900241)**. |
| 3 | 900270 | Divine Storm +6 targets | DBC | implemented | Marker aura (DUMMY). DS base spell (53385) needs a DBC patch: `MaxAffectedTargets` set to 10. No SpellMod for AoE targets available. |
| 4 | 900271 | Divine Storm +50% damage | DBC | implemented | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskB=0x20000 (DS flags[1], verify!). |
| 5 | 900272 | Crusader Strike +50% damage | DBC | implemented | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x1 (CS flags[0], verify!). |
| 6 | 900273 | Crusader Strike +9 targets | C++ | implemented | Marker aura (DUMMY). C++ SpellScript on CS (-35395): `AfterHit` → DealDamage on 9 extra enemies in 8yd. Checks `HasAura(900273)`. |
| 7 | 900274 | CS/Judge/DS → Exorcism buff | C++ | implemented | Passive Proc aura (DUMMY). spell_proc: ProcFlags=0x10, 100%. C++ CheckProc filters on CS(35395)/Judge(54158)/DS(53385). HandleProc → CastSpell(900275). |
| H1 | 900275 | Exorcism Power (buff) | DBC | implemented | Stacking Buff: `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). +50% Exorcism dmg per stack, max 10. 30s Duration. Consumed by Exorcism (48801) via C++ AfterCast. |

> **Note Ret**: Verify SpellFamilyFlags: DS=0x20000(flags[1]), CS=0x1(flags[0]), Exorcism=0x200000(flags[0]). 900270 (DS +6 targets) needs a DBC patch on the base spell. Exorcism-Buff (900275) EffectSpellClassMaskA=0x200000 must correctly match Exorcism.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Paladin — Ret (900266-900299)".
