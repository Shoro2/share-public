# Death Knight — Unholy

**Source:** [`custom_spells_dk.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_dk.cpp)
**ID-Range:** 900366-900399
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900366 | DoTs → Shadow AoE proc | C++ | not tested | Proc aura (DUMMY). spell_proc: ProcFlags=0x400000 (DONE_PERIODIC), 20% chance, 2s ICD. C++ HandleProc → CastSpell(900367, triggered) on the DoT target. |
| H1 | 900367 | Shadow Eruption (helper) | DBC | not tested | Instant AoE Shadow Damage. Effect=SCHOOL_DAMAGE(2), Target=DEST_AREA_ENEMY(15), SchoolMask=32(Shadow), BasePoints=600+150rnd, 8yd. |

> **Note DK**: Verify Heart Strike SpellFamilyFlags[0]=0x2000000! 900300 (3 DRW) recasts DRW as triggered — may cause aura stacking issues if not handled correctly. 900333 (Frost Wyrm) has its own creature_template (NPC 900333) + CreatureScript (`npc_custom_frost_wyrm`) with Frost Breath AI. DisplayID 26752 (Sindragosa style), scale 0.5, 2× Gargoyle HP.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "DK — Unholy (900366-900399)".
