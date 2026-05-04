# Warrior — Fury

**Source:** [`custom_spells_warrior.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warrior.cpp)
**ID-Range:** 900108-900121
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

> **Besonderheit**: Die Fury-Spells wurden manuell direkt in Spell.dbc erstellt (IDs 900108-900121),
> nicht über das ID-Block-Schema (900133-900165). Sie liegen daher im Arms-Bereich der ID-Tabelle,
> sind aber funktional Fury-Spells. Kein C++ nötig — alle Effekte laufen über DBC passive Auras,
> Proc-Trigger und spell_proc. Die alten C++/SQL-Einträge (900138-900145) wurden entfernt.

| # | Spell ID | Effekt | Ansatz | Status |
|---|----------|--------|--------|--------|
| 1 | 900108 | Whirlwind unlimited targets | DBC | nicht getestet |
| 2 | 900109 | Improved Bloodthirst Damage | DBC | nicht getestet |
| 3 | 900110 | Bloodthirst Cleave | DBC | nicht getestet |
| 4 | 900111 | Improved Whirlwind Damage | DBC | nicht getestet |
| 5 | 900112 | Cleave unlimited targets | DBC | nicht getestet |
| 6 | 900113 | Whirly Attacks (Proc) | DBC | nicht getestet |
| 7 | 900114 | Whirly Attacks (Passive) | DBC | nicht getestet |
| 8 | 900115 | Bloody Whirlwind (Aura) | DBC | nicht getestet |
| 9 | 900116 | Bloody Whirlwind (Passive) | DBC | nicht getestet |
| 10 | 900117 | Speedy Bloodthirst (Passive) | DBC | nicht getestet |
| 11 | 900118 | Whirlwind: Overpower (Passive) | DBC | nicht getestet |
| 12 | 900119 | Whirlwind: Bloodthirst (Passive) | DBC | nicht getestet |
| 13 | 900120 | Whirlwind: Overpower (Proc) | DBC | nicht getestet |
| 14 | 900121 | Whirlwind: Bloodthirst (Proc) | DBC | nicht getestet |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Warrior — Fury (900108-900121)".
