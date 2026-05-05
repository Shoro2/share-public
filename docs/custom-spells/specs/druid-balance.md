# Druid — Balance

**Source:** [`custom_spells_druid.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_druid.cpp)
**ID-Range:** 901000-901032
**Status:** Not tested (imported from `CustomSpells.md`)

> Druid SpellFamilyName = 7. Moonfire flags[0]=0x2, Starfall flags[0]=0x100 (verify!).

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901000 | Moonfire +9 targets | C++ | not tested | DUMMY marker. C++ SpellScript on Moonfire (-48463): `AfterHit` → finds up to 9 enemies in a 10yd radius → CastSpell(Moonfire R14, triggered)  on each. Checks `HasAura(901000)`. |
| 2 | 901001 | Moonfire +50% damage | DBC | not tested | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x2 targets Moonfire. |
| 3 | 901002 | Starfall +9 targets | DBC | not tested | ADD_FLAT_MODIFIER (107) + SPELLMOD_JUMP_TARGETS (17). EffectSpellClassMaskA=0x100 targets Starfall. BasePoints=9. |
| 4 | 901003 | Starfall +50% damage | DBC | not tested | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x100. |
| 5 | 901004 | Spell dmg reduces Starfall CD | C++ | not tested | Proc aura (DUMMY). spell_proc: ProcFlags=0x10010 (spell magic dmg), 100% chance, 1s ICD. C++ HandleProc → ModifySpellCooldown(Starfall, -1000). CheckProc filters on Druid SpellFamily. |
| 6 | 901005 | Starfall stacks to 10 | DBC | not tested | ADD_FLAT_MODIFIER (107) + SPELLMOD_CHARGES (4). EffectSpellClassMaskA=0x100. BasePoints=9 (+9 charges). |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Druid — Balance (901000-901032)".
