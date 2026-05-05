# Priest — Shadow

**Source:** [`custom_spells_priest.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_priest.cpp)
**ID-Range:** 900966-900999
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900966 | DoTs have a chance to deal shadow damage AoE | C++ | not tested | Same approach as Warlock 900800. Passive Proc aura: `PROC_FLAG_DONE_PERIODIC`. `HandleProc`: If a Shadow DoT tick fires (SW:Pain 48125, VT 48160, Devouring Plague 48300) → X% chance → CastSpell(Shadow-AoE-Helper, triggered=true) on the target. Needs a helper AoE spell (e.g. 900968). ICD recommended. |
| 2 | 900967 | DoTs have a chance to spread to 2 additional targets on tick | C++ | not tested | Same approach as Warlock 900802. Passive Proc aura: `PROC_FLAG_DONE_PERIODIC`. `HandleProc`: DoT tick → X% chance → Find the 2 nearest enemies without the DoT → ApplyAura(same DoT). Must extract the DoT spell ID from ProcEventInfo. Same warning: can grow exponentially, needs a target cap. |

> **Helper-Spells Priest**: 900900 (Shield Explosion) → Holy/Shadow-AoE-Helper 900903. 900966 (DoT AoE) → Shadow-AoE-Helper 900968.

> **Particularly elaborate**: 900900 (Shield Explosion) needs correct `OnRemove` detection (fade vs. dispel vs. break) and damage scaling based on the shield amount. 900933 (Heal → Holy Fire AoE) is a novel dual-purpose concept — must cleanly distinguish direct heals from HoTs. Shadow DoT mechanics (900966/900967) are identical to Warlock — code can be shared.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Priest — Shadow (900966-900999)".
