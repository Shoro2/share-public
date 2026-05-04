# Death Knight — Frost

**Source:** [`custom_spells_dk.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_dk.cpp)
**ID-Range:** 900333-900365
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900333 | Ghoul → Frost Wyrm | C++ | nicht getestet | Marker-Aura (DUMMY). C++ SpellScript auf Raise Dead (46584): `AfterCast` → Despawns Ghoul, SummonCreature(900333 Frost Wyrm). Prüft `HasAura(900333)`. Frost Wyrm NPC hat eigene AI (`npc_custom_frost_wyrm`), 2× Gargoyle HP, castet Frost Breath. |
| H1 | 900368 | Frost Breath | DBC+C++ | nicht getestet | 2s Cast, Cone 20yd, 5000+1000rnd Frost Damage + 50% Slow 6s. C++ `spell_custom_frost_breath` skaliert Damage mit Owner AP (5000 + 50% AP). |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "DK — Frost (900333-900365)".
