# Hunter — Shared

**Source:** [`custom_spells_hunter.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_hunter.cpp)
**ID-Range:** 900500-900501
**Status:** Not tested (imported from `CustomSpells.md`)

> Hunter SpellFamilyName = 9. "Get back arrows" and "Multishot unlimited targets" apply to all 3 specs → shared spells.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900500 | Get back arrows (no ammo consumption) | C++/PlayerScript | not tested | DUMMY marker. `custom_hunter_arrows_playerscript::OnSpellCast` → after each Ranged spell (SPELL_ATTR0_USES_RANGED_SLOT) → StoreNewItemInBestSlots(ammoId, 1). Checks `HasAura(900500)`. |
| 2 | 900501 | Multi-Shot unlimited targets | C++ | not tested | DUMMY marker. C++ SpellScript on Multi-Shot (-49048): `AfterHit` → finds ALL enemies in a 10yd radius around the target → DealDamage with full Multi-Shot damage on each. Checks `HasAura(900501)`. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Hunter — Shared (900500-900501)".
