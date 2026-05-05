# Priest — Holy

**Source:** [`custom_spells_priest.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_priest.cpp)
**ID-Range:** 900933-900965
**Status:** implemented

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900933 | Direct heals have chance to cast Holy Fire on enemies in 10y radius of target | C++ | implemented | Passive Proc aura: `PROC_FLAG_DONE_SPELL_MAGIC_DMG_CLASS_POS` (Positive Spell = Heal). `HandleProc`: If Direct Heal (Flash Heal 48071, Greater Heal 48063, etc. — no HoT) → X% chance → Find all enemies in a 10yd radius around the heal target → CastSpell(Holy Fire 48135, triggered=true)  on each. Dual-Purpose-Heal: Healing + simultaneous AoE DPS. Needs a SpellFamily filter to trigger only on direct heals (not Renew/PoM). ICD recommended. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Priest — Holy (900933-900965)".
