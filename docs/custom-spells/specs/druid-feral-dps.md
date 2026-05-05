# Druid — Feral DPS

**Source:** [`custom_spells_druid.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_druid.cpp)
**ID-Range:** 901049-901065
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901049 | Swipe Cat applies bleed | C++ | not tested | DUMMY marker. C++ SpellScript on Swipe Cat (62078): `AfterHit` → CastSpell(901050 Rake Bleed DoT, triggered). Checks `HasAura(901049)`. |
| H1 | 901050 | Helper: Rake Bleed DoT | DBC | not tested | APPLY_AURA PERIODIC_DAMAGE. 300+50rnd Physical per 3s tick, 12s duration. |
| 2 | 901051 | Energy regen +50% | DBC | not tested | SPELL_AURA_MOD_POWER_REGEN_PERCENT (110), MiscValue=3 (Energy). BasePoints=50. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Druid — Feral DPS (901049-901065)".
