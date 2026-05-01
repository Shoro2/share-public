# Druid — Balance

**Source:** [`custom_spells_druid.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_druid.cpp)
**ID-Range:** 901000-901032
**Status:** Live (importiert aus `CustomSpells.md`)

> Druid SpellFamilyName = 7. Moonfire flags[0]=0x2, Starfall flags[0]=0x100 (verify!).

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901000 | Moonfire +9 targets | C++ | implementiert | DUMMY Marker. C++ SpellScript auf Moonfire (-48463): `AfterHit` → findet bis zu 9 Feinde im 10yd Radius → CastSpell(Moonfire R14, triggered) auf jeden. Prüft `HasAura(901000)`. |
| 2 | 901001 | Moonfire +50% damage | DBC | implementiert | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x2 targets Moonfire. |
| 3 | 901002 | Starfall +9 targets | DBC | implementiert | ADD_FLAT_MODIFIER (107) + SPELLMOD_JUMP_TARGETS (17). EffectSpellClassMaskA=0x100 targets Starfall. BasePoints=9. |
| 4 | 901003 | Starfall +50% damage | DBC | implementiert | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x100. |
| 5 | 901004 | Spell dmg reduces Starfall CD | C++ | implementiert | Proc-Aura (DUMMY). spell_proc: ProcFlags=0x10010 (spell magic dmg), 100% Chance, 1s ICD. C++ HandleProc → ModifySpellCooldown(Starfall, -1000). CheckProc filtert auf Druid SpellFamily. |
| 6 | 901005 | Starfall stacks to 10 | DBC | implementiert | ADD_FLAT_MODIFIER (107) + SPELLMOD_CHARGES (4). EffectSpellClassMaskA=0x100. BasePoints=9 (+9 charges). |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Druid — Balance (901000-901032)".
