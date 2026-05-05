# Hunter — Beast Mastery

**Source:** [`custom_spells_hunter.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_hunter.cpp)
**ID-Range:** 900502-900532
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900502 | Pet damage +50% | C++/UnitScript | not tested | DUMMY marker. `custom_hunter_pet_unitscript::OnDamage` → when Attacker=Pet + Owner HasAura(900502) → damage *= 1.5f. |
| 2 | 900503 | Pet attack speed +50% | C++/PlayerScript | not tested | DUMMY marker. `custom_hunter_pet_speed_playerscript::OnPlayerUpdate` → every 3s: SetAttackTime(BASE_ATTACK, CreateAttackTime * 0.5f) on Pet. Checks `HasAura(900503)`. |
| 3 | 900504 | Pet AoE damage proc | C++/UnitScript | not tested | DUMMY marker. `custom_hunter_pet_aoe_unitscript::OnDamage` → when the pet hits + Owner HasAura(900504) → 15% chance → CastSpell(900505 Beast Cleave). |
| H1 | 900505 | Helper: Beast Cleave AoE | DBC | not tested | Instant AoE Physical Damage. Effect=SCHOOL_DAMAGE(2), Target=DEST_AREA_ENEMY(15), 800+200rnd, 8yd. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Hunter — Beast Mastery (900502-900532)".
