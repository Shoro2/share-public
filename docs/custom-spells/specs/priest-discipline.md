# Priest — Discipline

**Source:** [`custom_spells_priest.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_priest.cpp)
**ID-Range:** 900900-900932
**Status:** Not tested (imported from `CustomSpells.md`)

> Priest SpellFamilyName = 6. Disc focuses on shield enhancement.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900900 | Shields explode on breaking/fading | C++ | not tested | Power Word: Shield (48066) and other absorb shields. AuraScript `OnRemove`: If RemoveMode = EXPIRE (fade) or ENEMY_SPELL (break by damage) → CastSpell(Shield-Explosion-Helper, triggered=true) centered on the shield target. Explosion = Holy/Shadow AoE damage in a radius, Damage scales with the remaining/absorbed shield amount. Needs a helper AoE spell (e.g. 900903). Very cool thematically — Disc becomes AoE DPS via shields. |
| 2 | 900901 | Shields +50% | DBC | not tested | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on PW:Shield (48066) absorb amount. SpellFamilyName=6, SpellFamilyFlags for PW:S. Increases the absorb value by 50%. Stacks with existing talents (Improved PW:S, Twin Disciplines, etc.). |
| 3 | 900902 | Weakened Soul only 5 sec CD | DBC | not tested | Weakened Soul (6788) Debuff normally has 15s duration. DBC: set duration to 5000ms. Enables much more frequent re-shielding. Simple DBC duration change. Synergizes strongly with 900900 (Shield Explosion) — more shields = more explosions. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Priest — Discipline (900900-900932)".
