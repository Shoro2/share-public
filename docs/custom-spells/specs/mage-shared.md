# Mage — Shared

**Source:** [`custom_spells_mage.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_mage.cpp)
**ID-Range:** 900700
**Status:** Not tested (imported from `CustomSpells.md`)

> Mage SpellFamilyName = 3. "Channeling Evocation increases spell damage" applies to all 3 specs → shared spell. ID 900700 formally counts as part of the Arcane block (see [02-id-blocks.md](../02-id-blocks.md)), but is used spec-wide.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900700 | Channeling Evocation increases spell damage | C++ | not tested | Evocation (12051) is a channel spell (8s). Approach: AuraScript on Evocation → `OnApply`: Buff with `SPELL_AURA_MOD_DAMAGE_PERCENT_DONE` (ALL_SCHOOLS) stacked on the caster, increasing per tick. `OnRemove`: buff stays for X seconds or permanently. Alternative: Stacking aura during the channel, e.g. +10% Spell Damage per second of channeling → up to +80% after a full channel. Buff duration after the channel is configurable. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Mage — Shared (900700-900732)".
