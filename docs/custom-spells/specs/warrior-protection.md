# Warrior — Protection

**Source:** [`custom_spells_warrior.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warrior.cpp)
**ID-Range:** 900166-900199
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900168 | Revenge +50% damage | DBC | not tested | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x400 (Revenge). spell_dbc Entry. |
| 2 | 900169 | Revenge unlimited targets | C++ | not tested | Passive marker aura (DUMMY). C++ SpellScript on Revenge (57823): `AfterHit` → `AnyUnfriendlyUnitInObjectRangeCheck(8yd)` → DealDamage on all enemies. Checks `HasAura(900169)`. |
| 3 | 900170 | Thunderclap → Rend + 5× Sunder Armor | C++ | not tested | Passive marker aura (DUMMY). C++ SpellScript on TC (47502): `AfterHit` per target → CastSpell(Rend 47465) + 5× CastSpell(SunderArmor 58567). Checks `HasAura(900170)`. |
| 4 | 900171 | Thunderclap +50% damage | DBC | not tested | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x80 (TC). spell_dbc Entry. |
| 5 | 900172 | AoE damage on Block | C++ | not tested | Proc aura (DUMMY) with spell_proc: ProcFlags=0x2, 100% chance, 1s ICD. C++ HandleProc: Checks `PROC_HIT_BLOCK` → CastSpell(900174). |
| 6 | 900173 | 10% Block → Enhanced Thunderclap | C++ | not tested | Proc aura (DUMMY) with spell_proc: ProcFlags=0x2, 10% chance, 3s ICD. C++ HandleProc: Checks `PROC_HIT_BLOCK` → CastSpell(900175). |
| H1 | 900174 | Helper: Block AoE Damage | DBC | not tested | Instant AoE Physical Damage. Effect=SCHOOL_DAMAGE(2), Target=SRC_AREA_ENEMY(22), BasePoints=500+100rnd, Radius=8yd. |
| H2 | 900175 | Helper: Enhanced Thunderclap | DBC | not tested | Instant AoE Physical Damage. Effect=SCHOOL_DAMAGE(2), Target=SRC_AREA_ENEMY(22), BasePoints=1000+200rnd, Radius=10yd. |

> **Note Prot**: 900168/900171 are pure DBC (no C++ needed). 900169/900170 hook into existing spells (57823/47502) and check the marker aura via HasAura. 900172/900173 use the proc system with block detection. SpellFamilyFlags for Revenge (0x400) and TC (0x80) must be verified in-game.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Warrior — Prot (900166-900199)".
