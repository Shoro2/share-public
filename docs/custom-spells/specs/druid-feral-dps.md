# Druid — Feral DPS

**Source:** [`custom_spells_druid.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_druid.cpp)
**ID-Range:** 901049-901065
**Status:** implemented

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901049 | Swipe Cat applies bleed | C++ | implemented | DUMMY marker. C++ SpellScript on Swipe Cat (62078): `AfterHit` → CastSpell(901050 Rake Bleed DoT, triggered). Checks `HasAura(901049)`. |
| H1 | 901050 | Helper: Rake Bleed DoT | DBC | implemented | APPLY_AURA PERIODIC_DAMAGE. 300+50rnd Physical per 3s tick, 12s duration. |
| 2 | 901051 | Energy regen +50% | DBC | implemented | SPELL_AURA_MOD_POWER_REGEN_PERCENT (110), MiscValue=3 (Energy). BasePoints=50. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Druid — Feral DPS (901049-901065)".
