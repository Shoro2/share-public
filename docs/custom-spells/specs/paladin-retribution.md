# Paladin — Retribution

**Source:** [`custom_spells_paladin.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_paladin.cpp)
**ID-Range:** 900266-900299
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900268 | Consecration around you | DBC | implementiert | Marker-Aura (DUMMY). **Shared Konzept mit Holy (900205) und Prot (900234)**. Separate ID pro Spec. |
| 2 | 900269 | Judgement cd -2sec | DBC | implementiert | `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_COOLDOWN` (11). BasePoints=-2000ms. EffectSpellClassMaskA=0x800000. **Shared Konzept mit Prot (900241)**. |
| 3 | 900270 | Divine Storm +6 targets | DBC | implementiert | Marker-Aura (DUMMY). DS-Base-Spell (53385) braucht DBC-Patch: `MaxAffectedTargets` auf 10. Kein SpellMod für AoE-Targets verfügbar. |
| 4 | 900271 | Divine Storm +50% damage | DBC | implementiert | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskB=0x20000 (DS flags[1], verify!). |
| 5 | 900272 | Crusader Strike +50% damage | DBC | implementiert | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x1 (CS flags[0], verify!). |
| 6 | 900273 | Crusader Strike +9 targets | C++ | implementiert | Marker-Aura (DUMMY). C++ SpellScript auf CS (-35395): `AfterHit` → DealDamage auf 9 Extra-Feinde in 8yd. Prüft `HasAura(900273)`. |
| 7 | 900274 | CS/Judge/DS → Exorcism buff | C++ | implementiert | Passive Proc-Aura (DUMMY). spell_proc: ProcFlags=0x10, 100%. C++ CheckProc filtert auf CS(35395)/Judge(54158)/DS(53385). HandleProc → CastSpell(900275). |
| H1 | 900275 | Exorcism Power (buff) | DBC | implementiert | Stacking Buff: `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). +50% Exorcism dmg pro Stack, max 10. 30s Duration. Consumed by Exorcism (48801) via C++ AfterCast. |

> **Hinweis Ret**: SpellFamilyFlags verifizieren: DS=0x20000(flags[1]), CS=0x1(flags[0]), Exorcism=0x200000(flags[0]). 900270 (DS +6 targets) braucht DBC-Patch auf Base-Spell. Exorcism-Buff (900275) EffectSpellClassMaskA=0x200000 muss korrekt Exorcism matchen.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Paladin — Ret (900266-900299)".
