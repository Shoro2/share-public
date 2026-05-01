# Druid — Feral DPS

**Source:** [`custom_spells_druid.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_druid.cpp)
**ID-Range:** 901049-901065
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901049 | Swipe Cat applies bleed | C++ | implementiert | DUMMY Marker. C++ SpellScript auf Swipe Cat (62078): `AfterHit` → CastSpell(901050 Rake Bleed DoT, triggered). Prüft `HasAura(901049)`. |
| H1 | 901050 | Helper: Rake Bleed DoT | DBC | implementiert | APPLY_AURA PERIODIC_DAMAGE. 300+50rnd Physical per 3s tick, 12s duration. |
| 2 | 901051 | Energy regen +50% | DBC | implementiert | SPELL_AURA_MOD_POWER_REGEN_PERCENT (110), MiscValue=3 (Energy). BasePoints=50. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Druid — Feral DPS (901049-901065)".
