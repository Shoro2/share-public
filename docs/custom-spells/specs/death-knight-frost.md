# Death Knight — Frost

**Source:** [`custom_spells_dk.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_dk.cpp)
**ID-Range:** 900333-900365
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900333 | Ghoul → Frost Wyrm | C++ | not tested | Marker aura (DUMMY). C++ SpellScript on Raise Dead (46584): `AfterCast` → despawns the ghoul, SummonCreature(900333 Frost Wyrm). Checks `HasAura(900333)`. Frost Wyrm NPC has its own AI (`npc_custom_frost_wyrm`), 2× Gargoyle HP, casts Frost Breath. |
| H1 | 900368 | Frost Breath | DBC+C++ | not tested | 2s Cast, Cone 20yd, 5000+1000rnd Frost Damage + 50% Slow 6s. C++ `spell_custom_frost_breath` scales damage with owner AP (5000 + 50% AP). |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "DK — Frost (900333-900365)".
