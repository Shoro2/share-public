# Death Knight — Unholy

**Source:** [`custom_spells_dk.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_dk.cpp)
**ID-Range:** 900366-900399
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900366 | DoTs → Shadow AoE proc | C++ | implementiert | Proc-Aura (DUMMY). spell_proc: ProcFlags=0x400000 (DONE_PERIODIC), 20% Chance, 2s ICD. C++ HandleProc → CastSpell(900367, triggered) auf DoT-Target. |
| H1 | 900367 | Shadow Eruption (helper) | DBC | implementiert | Instant AoE Shadow Damage. Effect=SCHOOL_DAMAGE(2), Target=DEST_AREA_ENEMY(15), SchoolMask=32(Shadow), BasePoints=600+150rnd, 8yd. |

> **Hinweis DK**: Heart Strike SpellFamilyFlags[0]=0x2000000 verifizieren! 900300 (3 DRW) castet DRW nochmal als triggered — kann zu Aura-Stacking-Issues führen wenn nicht korrekt behandelt. 900333 (Frost Wyrm) hat eigene creature_template (NPC 900333) + CreatureScript (`npc_custom_frost_wyrm`) mit Frost Breath AI. DisplayID 26752 (Sindragosa-style), Scale 0.5, 2× Gargoyle HP.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "DK — Unholy (900366-900399)".
