# Hunter — Marksmanship

**Source:** [`custom_spells_hunter.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_hunter.cpp)
**ID-Range:** 900533-900565
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900533 | Auto Shot bounces +9 targets | C++ | not tested | DUMMY marker. C++ SpellScript on Auto Shot (75): `AfterHit` → finds up to 9 enemies in a 10yd radius around the target → CastCustomSpell(900535 Ricochet, damage)  on each. Checks `HasAura(900533)`. |
| 2 | 900534 | Multi-Shot Barrage (0.1s ticks for 2s, 50% slow) | C++ | not tested | Active spell: 2s PERIODIC_DUMMY (Amplitude=100ms). AuraScript: `OnApply` → CastSpell(900536 Slow), `OnRemove` → RemoveAura(900536). `HandlePeriodic` → CastSpell(Multi-Shot 49048, triggered). 20 Multi-Shots in 2s. |
| H1 | 900535 | Helper: Ricochet Shot | DBC | not tested | Instant Physical single-target damage. BasePoints via CastCustomSpell. |
| H2 | 900536 | Helper: Barrage Slow | DBC | not tested | 2s APPLY_AURA MOD_DECREASE_SPEED -50% on caster. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Hunter — Marksmanship (900533-900565)".
