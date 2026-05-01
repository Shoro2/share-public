# Mage — Frost

**Source:** [`custom_spells_mage.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_mage.cpp)
**ID-Range:** 900766-900799
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900766 | Frostbolt +50% damage | DBC | implementiert | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% auf Frostbolt (42842). Einfacher Damage-Multiplikator. |
| 2 | 900767 | Frostbolt +9 targets | C++ | implementiert | Frostbolt (42842) ist Single-Target. SpellScript `AfterHit` → Chain zu 9 weiteren Feinden. CastSpell(Frostbolt-Damage-Helper, triggered=true). Braucht Helper-Spell (z.B. 900772). |
| 3 | 900768 | Ice Lance +50% damage | DBC | implementiert | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% auf Ice Lance (42914). Einfacher Damage-Multiplikator. |
| 4 | 900769 | Ice Lance +9 targets | C++ | implementiert | Ice Lance (42914) ist Single-Target Instant. SpellScript `AfterHit` → Chain zu 9 weiteren Feinden. CastSpell(Ice-Lance-Damage-Helper, triggered=true). Braucht Helper-Spell (z.B. 900773). |
| 5 | 900770 | Water Elemental is permanent | DBC/C++ | implementiert | Summon Water Elemental (31687) hat normalerweise 45s Duration. DBC: Duration auf -1 (permanent) oder sehr hohen Wert setzen. C++: Falls Duration hardcoded → `OnSummon` Hook → SetDuration(0) (permanent). Ähnlich wie Hunter Pet — Water Ele bleibt bis Tod/Dismiss. |
| 6 | 900771 | Frost Comet Shower spell | C++ | implementiert | Neuer aktiver Spell: Channel oder Instant → Spawnt mehrere Frost-Comets an zufälligen Positionen im Target-Bereich über X Sekunden. Jeder Comet = AoE Frost Damage + Slow. Implementierung: Periodic Trigger → SummonGameObject oder CastSpell(Comet-Impact-Helper) an Random-Position im Radius. Visuell: Blizzard-ähnlich aber mit größeren Einzel-Impacts. Braucht Helper-Spells + ggf. Custom Visual. Vergleichbar mit Meteor (Fire) aber Frost-themed. |

> **Helper-Spells Mage**: 900702 (ABarr AoE) → Helper 900710. 900705 (AB +9) → Helper 900711. 900700 (Evoc Power) → Buff 900712. 900709 (Blink) → Helper 900713. 900734 (Fireball +9) → Helper 900739. 900735 (Pyro +9) → Helper 900740. 900767 (Frostbolt +9) → Helper 900772. 900769 (Ice Lance +9) → Helper 900773. 900771 (Comet Shower) → Helper 900774.

> **Besonders aufwändig**: 900701 (Mana Regen Scaling) braucht dynamische Berechnung pro Regen-Tick. 900709 (Blink Target Location) braucht Client-seitig Ground-Target-Cursor — evtl. DBC-Spell-Target-Type-Patch nötig. 900738 (Pyro → Hot Streak Loop) ist ein guaranteed Instant-Pyro-Chain — extrem starker Burst, Balancing kritisch. 900771 (Frost Comet Shower) ist ein komplett neuer Spell mit Custom-Visuals. Fire Meteor ist ähnlich aufwändig.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Mage — Frost (900766-900799)".
