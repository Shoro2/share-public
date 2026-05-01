# Mage — Shared

**Source:** [`custom_spells_mage.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_mage.cpp)
**ID-Range:** 900700-900732
**Status:** Live (importiert aus `CustomSpells.md`)

> Mage SpellFamilyName = 3. "Channeling Evocation increases spell damage" gilt für alle 3 Specs → shared Spell.

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900700 | Channeling Evocation increases spell damage | C++ | implementiert | Evocation (12051) ist ein Channel-Spell (8s). Ansatz: AuraScript auf Evocation → `OnApply`: Buff mit `SPELL_AURA_MOD_DAMAGE_PERCENT_DONE` (ALL_SCHOOLS) auf Caster stacken, pro Tick steigend. `OnRemove`: Buff bleibt X Sekunden oder permanent. Alternativ: Während Channel stacking Aura, z.B. +10% Spell Damage pro Sekunde Channel → bis +80% nach vollem Channel. Duration des Buffs nach Channel konfigurierbar. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Mage — Shared (900700-900732)".
