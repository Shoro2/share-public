# Druid — Restoration

**Source:** [`custom_spells_druid.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_druid.cpp)
**ID-Range:** 901066-901099
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901066 | HoTs chance to summon Force of Nature | C++ | implementiert | Proc-Aura (DUMMY). spell_proc: ProcFlags=0x40000 (periodic heal), 5% Chance, 5s ICD. C++ HandleProc → SummonCreature(901066 Healing Treant, 30s). Treant attacks enemy or follows player. |
| 2 | 901067 | Summons scale with healing power | C++/PlayerScript | implementiert | DUMMY Marker. `custom_druid_summon_scale_playerscript::OnPlayerUpdate` → alle 3s: für jede Controlled Unit → SetMaxHealth(baseHP + spellPower*10). |
| 3 | 901068 | Summons heal on death/despawn | C++/UnitScript | implementiert | DUMMY Marker. `custom_druid_summon_heal_unitscript::OnUnitDeath` → wenn Summon stirbt + Owner HasAura(901068) → CastSpell(901073 Nature Bloom). |
| 4 | 901069 | Thorns → chance to cast Rejuv | C++/UnitScript | implementiert | DUMMY Marker. `custom_druid_thorns_rejuv_unitscript::OnDamage` → wenn Victim=Player + HasAura(901069) + has Thorns → 20% chance → CastSpell(Rejuv R15, triggered). |
| 5 | 901070 | HoTs +50% healing | DBC | implementiert | ADD_PCT_MODIFIER (108) + SPELLMOD_DAMAGE (0). EffectSpellClassMaskA=0x30 targets Rejuv+Regrowth. |
| 6 | 901071 | HoTs tick 2x fast + 2x duration | DBC | implementiert | ADD_PCT_MODIFIER (108) + SPELLMOD_DURATION (17), BasePoints=100 (+100% duration). EffectSpellClassMaskA=0x30. Double duration = double ticks at same interval. |
| 7 | 901072 | Mana regen per missing mana% (+2%) | C++/PlayerScript | implementiert | DUMMY Marker. `custom_druid_mana_regen_playerscript::OnPlayerUpdate` → alle 5s: missingPct × 0.02 × maxMana / 100 → EnergizeBySpell. Same pattern as Shaman Resto (900467). |
| H1 | 901073 | Helper: Nature Bloom (treant death heal) | DBC | implementiert | Instant AoE Nature Heal. Effect=HEAL(10), Target=DEST_AREA_ALLY(30), 2000+500rnd, SchoolMask=8. |

> **Hinweis Druid**: NPC 901066 (Healing Treant) existiert in creature_template. 901071 (HoTs 2x) nutzt Duration-Multiplikator — verdoppelt Duration heißt doppelt so viele Ticks bei gleichem Intervall. Für echtes "doppelt so schnelles Ticken" bräuchte man einen C++ Ansatz der EffectAmplitude halbiert. UnitScripts (901068/901069) feuern für ALLE Unit Events — Performance beobachten.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Druid — Resto (901066-901099)".
