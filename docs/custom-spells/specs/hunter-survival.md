# Hunter — Survival

**Source:** [`custom_spells_hunter.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_hunter.cpp)
**ID-Range:** 900566-900599
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900566 | Chance to drop explosion on damage | C++ | nicht getestet | Proc-Aura (DUMMY). spell_proc: ProcFlags=0x44 (ranged auto + ranged spell), 15% Chance, 2s ICD. C++ HandleProc → CastSpell(900567 Explosive Burst, triggered) auf Target. |
| H1 | 900567 | Helper: Explosive Burst | DBC | nicht getestet | Instant AoE Fire Damage. Effect=SCHOOL_DAMAGE(2), Target=DEST_AREA_ENEMY(15), SchoolMask=4(Fire), 1000+200rnd, 8yd. |

> **Hinweis Hunter**: 900500 (Arrows) nutzt StoreNewItemInBestSlots was ein neues Item-Stack erstellt — bei vollen Bags könnte es fehlschlagen. 900534 (Barrage) castet 20 Multi-Shots in 2s — Performance bei vielen Mobs beobachten. Pet UnitScripts (900502/900504) feuern für ALLE Damage-Events — prüfen ob Creature ein Pet mit Owner ist um Performance zu schützen.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Hunter — Survival (900566-900599)".
