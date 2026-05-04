# Priest — Holy

**Source:** [`custom_spells_priest.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_priest.cpp)
**ID-Range:** 900933-900965
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900933 | Direct heals have chance to cast Holy Fire on enemies in 10y radius of target | C++ | nicht getestet | Passive Proc-Aura: `PROC_FLAG_DONE_SPELL_MAGIC_DMG_CLASS_POS` (Positive Spell = Heal). `HandleProc`: Wenn Direct Heal (Flash Heal 48071, Greater Heal 48063, etc. — kein HoT) → Chance X% → Finde alle Feinde im 10yd Radius um Heal-Target → CastSpell(Holy Fire 48135, triggered=true) auf jeden. Dual-Purpose-Heal: Heilen + gleichzeitig AoE DPS. Braucht SpellFamily-Filter um nur Direct Heals zu triggern (nicht Renew/PoM). ICD empfohlen. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Priest — Holy (900933-900965)".
