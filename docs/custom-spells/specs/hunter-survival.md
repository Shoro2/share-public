# Hunter — Survival

**Source:** [`custom_spells_hunter.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_hunter.cpp)
**ID-Range:** 900566-900599
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900566 | Chance to drop explosion on damage | C++ | not tested | Proc aura (DUMMY). spell_proc: ProcFlags=0x44 (ranged auto + ranged spell), 15% chance, 2s ICD. C++ HandleProc → CastSpell(900567 Explosive Burst, triggered) on Target. |
| H1 | 900567 | Helper: Explosive Burst | DBC | not tested | Instant AoE Fire Damage. Effect=SCHOOL_DAMAGE(2), Target=DEST_AREA_ENEMY(15), SchoolMask=4(Fire), 1000+200rnd, 8yd. |

> **Note Hunter**: 900500 (Arrows) uses StoreNewItemInBestSlots, which creates a new item stack — may fail when bags are full. 900534 (Barrage) casts 20 Multi-Shots in 2s — watch performance with many mobs. Pet UnitScripts (900502/900504) fire for ALL damage events — check whether the creature is a pet with an owner to protect performance.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Hunter — Survival (900566-900599)".
