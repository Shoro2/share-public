# Hunter — Shared

**Source:** [`custom_spells_hunter.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_hunter.cpp)
**ID-Range:** 900500-900501
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

> Hunter SpellFamilyName = 9. "Get back arrows" und "Multishot unlimited targets" gelten für alle 3 Specs → shared Spells.

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900500 | Get back arrows (no ammo consumption) | C++/PlayerScript | nicht getestet | DUMMY Marker. `custom_hunter_arrows_playerscript::OnSpellCast` → nach jedem Ranged-Spell (SPELL_ATTR0_USES_RANGED_SLOT) → StoreNewItemInBestSlots(ammoId, 1). Prüft `HasAura(900500)`. |
| 2 | 900501 | Multi-Shot unlimited targets | C++ | nicht getestet | DUMMY Marker. C++ SpellScript auf Multi-Shot (-49048): `AfterHit` → findet ALLE Feinde im 10yd Radius um Target → DealDamage mit vollem Multi-Shot-Damage auf jeden. Prüft `HasAura(900501)`. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Hunter — Shared (900500-900501)".
