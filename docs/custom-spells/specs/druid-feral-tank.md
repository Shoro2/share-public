# Druid — Feral Tank

**Source:** [`custom_spells_druid.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_druid.cpp)
**ID-Range:** 901033-901048
**Status:** implemented

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901033 | Swipe Bear applies bleed | C++ | implemented | DUMMY marker. C++ SpellScript on Swipe Bear (-48562): `AfterHit` → CastSpell(901034 Swipe Bleed DoT, triggered). Checks `HasAura(901033)`. |
| H1 | 901034 | Helper: Swipe Bleed DoT | DBC | implemented | APPLY_AURA PERIODIC_DAMAGE. 300+50rnd Physical per 3s tick, 12s duration. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Druid — Feral Tank (901033-901048)".
