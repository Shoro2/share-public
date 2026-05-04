# Priest — Shadow

**Source:** [`custom_spells_priest.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_priest.cpp)
**ID-Range:** 900966-900999
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900966 | DoTs have a chance to deal shadow damage AoE | C++ | nicht getestet | Gleicher Ansatz wie Warlock 900800. Passive Proc-Aura: `PROC_FLAG_DONE_PERIODIC`. `HandleProc`: Wenn Shadow-DoT-Tick (SW:Pain 48125, VT 48160, Devouring Plague 48300) → Chance X% → CastSpell(Shadow-AoE-Helper, triggered=true) am Target. Braucht Helper-AoE-Spell (z.B. 900968). ICD empfohlen. |
| 2 | 900967 | DoTs have a chance to spread to 2 additional targets on tick | C++ | nicht getestet | Gleicher Ansatz wie Warlock 900802. Passive Proc-Aura: `PROC_FLAG_DONE_PERIODIC`. `HandleProc`: DoT-Tick → Chance X% → Finde 2 nächste Feinde ohne den DoT → ApplyAura(gleicher DoT). Muss DoT-Spell-ID aus ProcEventInfo extrahieren. Gleiche Warnung: kann exponentiell wachsen, braucht Target-Cap. |

> **Helper-Spells Priest**: 900900 (Shield Explosion) → Holy/Shadow-AoE-Helper 900903. 900966 (DoT AoE) → Shadow-AoE-Helper 900968.

> **Besonders aufwändig**: 900900 (Shield Explosion) braucht korrekte `OnRemove`-Detection (fade vs. dispel vs. break) und Damage-Skalierung basierend auf Shield-Amount. 900933 (Heal → Holy Fire AoE) ist ein neuartiges Dual-Purpose-Konzept — muss sauber zwischen Direct Heals und HoTs unterscheiden. Shadow-DoT-Mechaniken (900966/900967) sind identisch zu Warlock — Code kann geshared werden.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Priest — Shadow (900966-900999)".
