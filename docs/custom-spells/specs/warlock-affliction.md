# Warlock — Affliction

**Source:** [`custom_spells_warlock.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warlock.cpp)
**ID-Range:** 900800-900832
**Status:** Not tested (imported from `CustomSpells.md`)

> Warlock SpellFamilyName = 5. Affliction focuses on DoT amplification and DoT spread.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900800 | DoTs have a chance to deal shadow damage AoE | C++ | not tested | Passive Proc aura: `PROC_FLAG_DONE_PERIODIC` (0x400000). `HandleProc`: If a periodic damage tick from a Warlock DoT → X% chance → CastSpell(Shadow-AoE-Helper, triggered=true) centered on the DoT target. Shadow AoE = area damage around the target. Needs a helper AoE spell (e.g. 900803). ICD recommended (e.g. 2s). |
| 2 | 900801 | Corruption +50% damage | DBC | not tested | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Corruption (47813). SpellFamilyName=5, SpellFamilyFlags for Corruption. Simple damage multiplier for periodic + initial damage. |
| 3 | 900802 | DoTs have a chance to spread to 2 additional targets on tick | C++ | not tested | Passive Proc aura: `PROC_FLAG_DONE_PERIODIC`. `HandleProc`: If DoT tick → X% chance → Find the 2 nearest enemies in range that do NOT have the DoT → ApplyAura(same DoT) onto them. Must extract the DoT spell ID from ProcEventInfo and cast onto new targets. Very strong spread mechanic — can grow exponentially! May need a max target cap per cast. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Warlock — Affliction (900800-900832)".
