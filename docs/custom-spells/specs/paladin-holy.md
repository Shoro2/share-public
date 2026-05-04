# Paladin — Holy

**Source:** [`custom_spells_paladin.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_paladin.cpp)
**ID-Range:** 900200-900232
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

> Paladin SpellFamilyName = 10. Holy Shock (20473) ist ein Dummy-Spell der auf Damage (25912+) oder Heal (25914+) routet. Scripts hooken auf die Damage/Heal-Varianten via negative spell_script_names IDs (-25912, -25914 = alle Ränge).

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900200 | Holy Shock AoE damage | C++ | nicht getestet | Marker-Aura (DUMMY). C++ SpellScript auf HS-Damage (-25912): `AfterHit` → CastSpell(900208) AoE Holy Damage um Target. Prüft `HasAura(900200)`. |
| 2 | 900201 | Holy Shock AoE heal | C++ | nicht getestet | Marker-Aura (DUMMY). C++ SpellScript auf HS-Heal (-25914): `AfterHit` → CastSpell(900209) AoE Holy Heal um Target. Prüft `HasAura(900201)`. |
| 3 | 900202 | Holy Shock always both | C++ | nicht getestet | Marker-Aura (DUMMY). Zwei Scripts: (a) auf HS-Damage: `AfterHit` → auto-heal nächsten verletzten Ally (HS-Heal R7). (b) auf HS-Heal: `AfterHit` → auto-damage nächsten Feind (HS-Damage R7). Prüft `HasAura(900202)`. |
| 4 | 900203 | Holy Shock +50% | DBC | nicht getestet | Passive Aura: `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x200000 (Holy Shock). spell_dbc Entry. |
| 5 | 900204 | Consecration also heals | C++ | nicht getestet | Marker-Aura (DUMMY). C++ AuraScript auf Consecration (48819): `OnEffectPeriodic` → CastSpell(900210) AoE Holy Heal um Caster. Prüft `HasAura(900204)`. |
| 6 | 900205 | Consecration around you | DBC | nicht getestet | Marker-Aura. Consecration-DBC muss separat gepatcht werden (TargetA → `TARGET_DEST_CASTER`). **Shared mit Prot und Ret**. |
| 7 | 900206 | Consecration +50% | DBC | nicht getestet | Passive Aura: `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x20 (Consecration). |
| 8 | 900207 | Consecration +5sec | DBC | nicht getestet | Passive Aura: `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_DURATION` (17). BasePoints=5000ms. EffectSpellClassMaskA=0x20. |
| H1 | 900208 | Helper: HS AoE Damage | DBC | nicht getestet | Instant AoE Holy Damage. Effect=SCHOOL_DAMAGE(2), Target=DEST_AREA_ENEMY(15), BasePoints=800+100rnd, 10yd. |
| H2 | 900209 | Helper: HS AoE Heal | DBC | nicht getestet | Instant AoE Holy Heal. Effect=HEAL(10), Target=DEST_AREA_ALLY(30), BasePoints=800+100rnd, 10yd. |
| H3 | 900210 | Helper: Consec Heal Tick | DBC | nicht getestet | Instant AoE Holy Heal. Effect=HEAL(10), Target=SRC_AREA_ALLY(31), BasePoints=200+50rnd, 8yd. |

> **Hinweis Holy**: SpellFamilyFlags für Holy Shock (0x200000) und Consecration (0x20) müssen in-game verifiziert werden. 900205 (Consec around you) braucht zusätzlich einen DBC-Patch auf den Base-Spell (48819) um TargetA zu ändern — die Marker-Aura allein reicht nicht.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Paladin — Holy (900200-900232)".
