# Hunter — Marksmanship

**Source:** [`custom_spells_hunter.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_hunter.cpp)
**ID-Range:** 900533-900565
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900533 | Auto Shot bounces +9 targets | C++ | nicht getestet | DUMMY Marker. C++ SpellScript auf Auto Shot (75): `AfterHit` → findet bis zu 9 Feinde im 10yd Radius um Target → CastCustomSpell(900535 Ricochet, damage) auf jeden. Prüft `HasAura(900533)`. |
| 2 | 900534 | Multi-Shot Barrage (0.1s ticks for 2s, 50% slow) | C++ | nicht getestet | Aktiver Spell: 2s PERIODIC_DUMMY (Amplitude=100ms). AuraScript: `OnApply` → CastSpell(900536 Slow), `OnRemove` → RemoveAura(900536). `HandlePeriodic` → CastSpell(Multi-Shot 49048, triggered). 20 Multi-Shots in 2s. |
| H1 | 900535 | Helper: Ricochet Shot | DBC | nicht getestet | Instant Physical single-target damage. BasePoints via CastCustomSpell. |
| H2 | 900536 | Helper: Barrage Slow | DBC | nicht getestet | 2s APPLY_AURA MOD_DECREASE_SPEED -50% on caster. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Hunter — Marksmanship (900533-900565)".
