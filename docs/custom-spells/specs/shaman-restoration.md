# Shaman — Restoration

**Source:** [`custom_spells_shaman.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_shaman.cpp)
**ID-Range:** 900466-900499
**Status:** implemented

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900466 | Totems follow player | PlayerScript | implemented | DUMMY marker. Shared `custom_totem_follow_playerscript` also checks `HasAura(900466)`. |
| 2 | 900467 | Mana regen +2% per missing mana% | C++/PlayerScript | implemented | DUMMY marker. `custom_mana_regen_playerscript::OnPlayerUpdate` → every 5s: missingPct = (1 - curMana/maxMana) × 100 → EnergizeBySpell(maxMana × missingPct × 0.02 / 100). At 50% missing → +1% maxMana/5s. At 90% missing → +1.8% maxMana/5s. |

> **Note Enhance**: 900435 (Summons +50%) is currently a marker only — the actual damage boost must be implemented via pet scaling or an owner→pet aura transfer. 900434 (Maelstrom AoE) casts the AoE helper directly on all controlled units at 5 stacks — the AoE fires once, not every attack for 5s (simplified). 900438 (Wolf CL) uses UnitScript::OnDamage which fires for ALL damage events — watch performance.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Shaman — Restoration (900466-900499)".
