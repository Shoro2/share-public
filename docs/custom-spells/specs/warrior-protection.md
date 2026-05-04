# Warrior — Protection

**Source:** [`custom_spells_warrior.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warrior.cpp)
**ID-Range:** 900166-900199
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900168 | Revenge +50% damage | DBC | nicht getestet | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x400 (Revenge). spell_dbc Entry. |
| 2 | 900169 | Revenge unlimited targets | C++ | nicht getestet | Passive Marker-Aura (DUMMY). C++ SpellScript auf Revenge (57823): `AfterHit` → `AnyUnfriendlyUnitInObjectRangeCheck(8yd)` → DealDamage auf alle Feinde. Prüft `HasAura(900169)`. |
| 3 | 900170 | Thunderclap → Rend + 5× Sunder Armor | C++ | nicht getestet | Passive Marker-Aura (DUMMY). C++ SpellScript auf TC (47502): `AfterHit` pro Target → CastSpell(Rend 47465) + 5× CastSpell(SunderArmor 58567). Prüft `HasAura(900170)`. |
| 4 | 900171 | Thunderclap +50% damage | DBC | nicht getestet | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x80 (TC). spell_dbc Entry. |
| 5 | 900172 | AoE damage on Block | C++ | nicht getestet | Proc-Aura (DUMMY) mit spell_proc: ProcFlags=0x2, 100% Chance, 1s ICD. C++ HandleProc: Prüft `PROC_HIT_BLOCK` → CastSpell(900174). |
| 6 | 900173 | 10% Block → Enhanced Thunderclap | C++ | nicht getestet | Proc-Aura (DUMMY) mit spell_proc: ProcFlags=0x2, 10% Chance, 3s ICD. C++ HandleProc: Prüft `PROC_HIT_BLOCK` → CastSpell(900175). |
| H1 | 900174 | Helper: Block AoE Damage | DBC | nicht getestet | Instant AoE Physical Damage. Effect=SCHOOL_DAMAGE(2), Target=SRC_AREA_ENEMY(22), BasePoints=500+100rnd, Radius=8yd. |
| H2 | 900175 | Helper: Enhanced Thunderclap | DBC | nicht getestet | Instant AoE Physical Damage. Effect=SCHOOL_DAMAGE(2), Target=SRC_AREA_ENEMY(22), BasePoints=1000+200rnd, Radius=10yd. |

> **Hinweis Prot**: 900168/900171 sind rein DBC (kein C++ nötig). 900169/900170 hooken auf bestehende Spells (57823/47502) und prüfen Marker-Aura via HasAura. 900172/900173 nutzen das Proc-System mit Block-Detection. SpellFamilyFlags für Revenge (0x400) und TC (0x80) müssen in-game verifiziert werden.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Warrior — Prot (900166-900199)".
