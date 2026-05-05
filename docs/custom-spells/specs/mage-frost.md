# Mage — Frost

**Source:** [`custom_spells_mage.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_mage.cpp)
**ID-Range:** 900766-900774
**Status:** implemented

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900766 | Frostbolt +50% damage | DBC | implemented | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Frostbolt (42842). Simple damage multiplier. |
| 2 | 900767 | Frostbolt +9 targets | C++ | implemented | Frostbolt (42842) is single-target. SpellScript `AfterHit` → chain to 9 additional enemies. CastSpell(Frostbolt-Damage-Helper, triggered=true). Needs a helper spell (e.g. 900772). |
| 3 | 900768 | Ice Lance +50% damage | DBC | implemented | Passive aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Ice Lance (42914). Simple damage multiplier. |
| 4 | 900769 | Ice Lance +9 targets | C++ | implemented | Ice Lance (42914) is single-target Instant. SpellScript `AfterHit` → chain to 9 additional enemies. CastSpell(Ice-Lance-Damage-Helper, triggered=true). Needs a helper spell (e.g. 900773). |
| 5 | 900770 | Water Elemental is permanent | DBC/C++ | implemented | Summon Water Elemental (31687) has a 45s duration normally. DBC: Duration set to -1 (permanent) or a very high value. C++: If duration is hardcoded → `OnSummon` Hook → SetDuration(0) (permanent). Similar to a hunter pet — Water Ele stays until death/dismiss. |
| 6 | 900771 | Frost Comet Shower spell | C++ | implemented | New active spell: Channel or Instant → Spawns multiple frost comets at random positions in the target area over X seconds. Each comet = AoE Frost Damage + Slow. Implementation: periodic trigger → SummonGameObject or CastSpell(Comet-Impact-Helper) at a random position in the radius. Visually: Blizzard-like but with larger single impacts. Needs a helper spells + optional custom visual. Comparable to Meteor (Fire) but Frost-themed. |

> **Helper-Spells Mage**: 900702 (ABarr AoE) → Helper 900710. 900705 (AB +9) → Helper 900711. 900700 (Evoc Power) → Buff 900712. 900709 (Blink) → Helper 900713. 900734 (Fireball +9) → Helper 900739. 900735 (Pyro +9) → Helper 900740. 900767 (Frostbolt +9) → Helper 900772. 900769 (Ice Lance +9) → Helper 900773. 900771 (Comet Shower) → Helper 900774.

> **Particularly elaborate**: 900701 (Mana Regen Scaling) needs dynamic computation per regen tick. 900709 (Blink Target Location) needs a client-side ground target cursor — possibly a DBC spell target-type patch. 900738 (Pyro → Hot Streak Loop) is a guaranteed instant Pyro chain — extremely strong burst, balancing critical. 900771 (Frost Comet Shower) is an entirely new spell with custom visuals. Fire Meteor is similarly elaborate.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Mage — Frost (900766-900799)".
