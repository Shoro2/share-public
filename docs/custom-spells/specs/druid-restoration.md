# Druid — Restoration

**Source:** [`custom_spells_druid.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_druid.cpp)
**ID-Range:** 901066-901099
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901066 | HoTs chance to summon Force of Nature | C++ | not tested | Proc aura (DUMMY). spell_proc: ProcFlags=0x40000 (periodic heal), 5% Chance, 5s ICD. C++ HandleProc → SummonCreature(901066 Healing Treant, 30s). Treant attacks enemy or follows player. |
| 2 | 901067 | Summons scale with healing power | C++/PlayerScript | not tested | DUMMY marker. `custom_druid_summon_scale_playerscript::OnPlayerUpdate` → every 3s: for each controlled unit → SetMaxHealth(baseHP + spellPower*10). |
| 3 | 901068 | Summons heal on death/despawn | C++/UnitScript | not tested | DUMMY marker. `custom_druid_summon_heal_unitscript::OnUnitDeath` → when the summon dies + Owner HasAura(901068) → CastSpell(901073 Nature Bloom). |
| 4 | 901069 | Thorns → chance to cast Rejuv | C++/UnitScript | not tested | DUMMY marker. `custom_druid_thorns_rejuv_unitscript::OnDamage` → when Victim=Player + HasAura(901069) + has Thorns → 20% chance → CastSpell(Rejuv R15, triggered). |
| 5 | 901070 | HoTs +50% healing | DBC | not tested | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x30 targets Rejuv+Regrowth. |
| 6 | 901071 | HoTs tick 2x fast + 2x duration | DBC | not tested | ADD_PCT_MODIFIER (108) + SPELLMOD_DURATION (17), BasePoints=100 (+100% duration). EffectSpellClassMaskA=0x30. Double duration = double ticks at same interval. |
| 7 | 901072 | Mana regen per missing mana% (+2%) | C++/PlayerScript | not tested | DUMMY marker. `custom_druid_mana_regen_playerscript::OnPlayerUpdate` → every 5s: missingPct × 0.02 × maxMana / 100 → EnergizeBySpell. Same pattern as Shaman Resto (900467). |
| H1 | 901073 | Helper: Nature Bloom (treant death heal) | DBC | not tested | Instant AoE Nature Heal. Effect=HEAL(10), Target=DEST_AREA_ALLY(30), 2000+500rnd, SchoolMask=8. |

> **Note Druid**: NPC 901066 (Healing Treant) exists in creature_template. 901071 (HoTs 2x) uses a duration multiplier — doubling duration means twice as many ticks at the same interval. For genuine "tick twice as fast" a C++ approach that halves EffectAmplitude would be needed. UnitScripts (901068/901069) fire for ALL unit events — Watch performance.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Druid — Resto (901066-901099)".
