# Paladin — Holy

**Source:** [`custom_spells_paladin.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_paladin.cpp)
**ID-Range:** 900200-900232
**Status:** Not tested (imported from `CustomSpells.md`)

> Paladin SpellFamilyName = 10. Holy Shock (20473) is a dummy spell that routes to Damage (25912+) or heal (25914+) . Scripts hook on the Damage/Heal-Varianten via negative spell_script_names IDs (-25912, -25914 = all ranks).

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900200 | Holy Shock AoE damage | C++ | not tested | Marker aura (DUMMY). C++ SpellScript on HS-Damage (-25912): `AfterHit` → CastSpell(900208) AoE Holy Damage around the target. Checks `HasAura(900200)`. |
| 2 | 900201 | Holy Shock AoE heal | C++ | not tested | Marker aura (DUMMY). C++ SpellScript on HS-Heal (-25914): `AfterHit` → CastSpell(900209) AoE Holy Heal around the target. Checks `HasAura(900201)`. |
| 3 | 900202 | Holy Shock always both | C++ | not tested | Marker aura (DUMMY). Two scripts: (a) on HS-Damage: `AfterHit` → auto-heal the closest injured ally (HS-Heal R7). (b) on HS-Heal: `AfterHit` → auto-damage the closest enemy (HS-Damage R7). Checks `HasAura(900202)`. |
| 4 | 900203 | Holy Shock +50% | DBC | not tested | Passive aura: `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x200000 (Holy Shock). spell_dbc Entry. |
| 5 | 900204 | Consecration also heals | C++ | not tested | Marker aura (DUMMY). C++ AuraScript on Consecration (48819): `OnEffectPeriodic` → CastSpell(900210) AoE Holy Heal around the caster. Checks `HasAura(900204)`. |
| 6 | 900205 | Consecration around you | DBC | not tested | Marker aura. The Consecration DBC must be patched separately (TargetA → `TARGET_DEST_CASTER`). **Shared with Prot and Ret**. |
| 7 | 900206 | Consecration +50% | DBC | not tested | Passive aura: `ADD_PCT_MODIFIER` (108) + `SPELLMOD_DAMAGE` (0). EffectSpellClassMaskA=0x20 (Consecration). |
| 8 | 900207 | Consecration +5sec | DBC | not tested | Passive aura: `ADD_FLAT_MODIFIER` (107) + `SPELLMOD_DURATION` (17). BasePoints=5000ms. EffectSpellClassMaskA=0x20. |
| H1 | 900208 | Helper: HS AoE Damage | DBC | not tested | Instant AoE Holy Damage. Effect=SCHOOL_DAMAGE(2), Target=DEST_AREA_ENEMY(15), BasePoints=800+100rnd, 10yd. |
| H2 | 900209 | Helper: HS AoE Heal | DBC | not tested | Instant AoE Holy Heal. Effect=HEAL(10), Target=DEST_AREA_ALLY(30), BasePoints=800+100rnd, 10yd. |
| H3 | 900210 | Helper: Consec Heal Tick | DBC | not tested | Instant AoE Holy Heal. Effect=HEAL(10), Target=SRC_AREA_ALLY(31), BasePoints=200+50rnd, 8yd. |

> **Note Holy**: SpellFamilyFlags for Holy Shock (0x200000) and Consecration (0x20) must be verified in-game. 900205 (Consec around you) additionally needs a DBC patch on the base spell (48819) to change TargetA — the marker aura alone is not enough.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Paladin — Holy (900200-900232)".
