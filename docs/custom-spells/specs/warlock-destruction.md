# Warlock — Destruction

**Source:** [`custom_spells_warlock.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warlock.cpp)
**ID-Range:** 900866-900899
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900866 | Shadow Bolt +9 targets | C++ | implementiert | Shadow Bolt (47809) ist Single-Target. SpellScript `AfterHit` → Chain zu 9 weiteren Feinden. CastSpell(SB-Damage-Helper, triggered=true). Braucht Helper-Spell (z.B. 900871). |
| 2 | 900867 | Shadow Bolt +50% damage | DBC | implementiert | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% auf Shadow Bolt (47809). Einfacher Damage-Multiplikator. |
| 3 | 900868 | Chaos Bolt +50% damage | DBC | implementiert | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% auf Chaos Bolt (59172). Einfacher Damage-Multiplikator. |
| 4 | 900869 | Chaos Bolt cooldown -2 sec | DBC | implementiert | Passive Aura: `SPELL_AURA_ADD_FLAT_MODIFIER` (SPELLMOD_COOLDOWN) -2000ms auf Chaos Bolt (59172). Base CD 12s → 10s. Oder DBC direkt: `RecoveryTime` reduzieren. |
| 5 | 900870 | Chaos Bolt +9 targets | C++ | implementiert | Chaos Bolt (59172) ist Single-Target. SpellScript `AfterHit` → Chain zu 9 weiteren Feinden. CastSpell(CB-Damage-Helper, triggered=true). Chaos Bolt ignoriert Resistances — Helper-Spell sollte das ebenfalls tun (Attribute `SPELL_ATTR0_NO_IMMUNITIES` o.ä.). Braucht Helper-Spell (z.B. 900872). |

> **Helper-Spells Warlock**: 900800 (DoT AoE) → Shadow-AoE-Helper 900803. 900837 (Imp Firebolt +9) → Helper 900841. 900834 (Meta AoE) → Helper 900842. 900834 (Meta Heal) → Helper 900843. 900838 (FG Cleave) → Helper 900844. 900866 (SB +9) → Helper 900871. 900870 (CB +9) → Helper 900872. 900835 (Lesser Demons) braucht Custom Creature-Templates.

> **Besonders aufwändig**: 900802 (DoT Spread) kann exponentiell wachsen — braucht Target-Cap um Server-Performance zu schützen. 900835 (Lesser Demon Spawn) braucht Custom Creature-Templates pro Pet-Typ mit eigener AI. 900840 (Sacrifice All Bonuses) muss alle Pet-Typ-Buffs korrekt identifizieren und stacken. 900833 (Meta Duration Extension) + 900834 (Meta AoE+Heal) zusammen machen Demo-Lock zu einem permanent transformierten AoE-Healer-Tank-Hybrid.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Warlock — Destruction (900866-900899)".
