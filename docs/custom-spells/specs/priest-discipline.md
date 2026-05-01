# Priest — Discipline

**Source:** [`custom_spells_priest.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_priest.cpp)
**ID-Range:** 900900-900932
**Status:** Live (importiert aus `CustomSpells.md`)

> Priest SpellFamilyName = 6. Disc fokussiert auf Shield-Enhancement.

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900900 | Shields explode on breaking/fading | C++ | implementiert | Power Word: Shield (48066) und andere Absorb-Shields. AuraScript `OnRemove`: Wenn RemoveMode = EXPIRE (fade) oder ENEMY_SPELL (break durch Damage) → CastSpell(Shield-Explosion-Helper, triggered=true) zentriert auf Shield-Target. Explosion = Holy/Shadow AoE Damage im Radius, Damage skaliert mit verbleibendem/absorbiertem Shield-Amount. Braucht Helper-AoE-Spell (z.B. 900903). Sehr cool thematisch — Disc wird zum AoE-DPS via Shields. |
| 2 | 900901 | Shields +50% | DBC | implementiert | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% auf PW:Shield (48066) Absorb-Amount. SpellFamilyName=6, SpellFamilyFlags für PW:S. Erhöht Absorb-Wert um 50%. Stackt mit existierenden Talents (Improved PW:S, Twin Disciplines, etc.). |
| 3 | 900902 | Weakened Soul only 5 sec CD | DBC | implementiert | Weakened Soul (6788) Debuff hat normalerweise 15s Duration. DBC: Duration auf 5000ms setzen. Ermöglicht viel häufigeres Re-Shielding. Einfache DBC-Duration-Änderung. Synergiert stark mit 900900 (Shield Explosion) — mehr Shields = mehr Explosions. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Priest — Discipline (900900-900932)".
