# Warrior — Fury

**Source:** [`custom_spells_warrior.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warrior.cpp)
**ID-Range:** 900108-900121
**Status:** tested

> **Special note**: The Fury spells were created manually directly in Spell.dbc (IDs 900108-900121),
> not via the ID block scheme (900133-900165). They therefore sit in the Arms range of the ID table,
> but are functionally Fury spells. No C++ needed — all effects run through DBC passive auras,
> proc triggers and spell_proc. The old C++/SQL entries (900138-900145) were removed.

| # | Spell ID | Effect | Approach | Status |
|---|----------|--------|--------|--------|
| 1 | 900108 | Whirlwind unlimited targets | DBC | tested |
| 2 | 900109 | Improved Bloodthirst Damage | DBC | tested |
| 3 | 900110 | Bloodthirst Cleave | DBC | tested |
| 4 | 900111 | Improved Whirlwind Damage | DBC | tested |
| 5 | 900112 | Cleave unlimited targets | DBC | tested |
| 6 | 900113 | Whirly Attacks (Proc) | DBC | tested |
| 7 | 900114 | Whirly Attacks (Passive) | DBC | tested |
| 8 | 900115 | Bloody Whirlwind (Aura) | DBC | tested |
| 9 | 900116 | Bloody Whirlwind (Passive) | DBC | tested |
| 10 | 900117 | Speedy Bloodthirst (Passive) | DBC | tested |
| 11 | 900118 | Whirlwind: Overpower (Passive) | DBC | tested |
| 12 | 900119 | Whirlwind: Bloodthirst (Passive) | DBC | tested |
| 13 | 900120 | Whirlwind: Overpower (Proc) | DBC | tested |
| 14 | 900121 | Whirlwind: Bloodthirst (Proc) | DBC | tested |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Warrior — Fury (900108-900121)".
