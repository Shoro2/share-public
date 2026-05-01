# Warlock — Demonology

**Source:** [`custom_spells_warlock.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warlock.cpp)
**ID-Range:** 900833-900865
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900833 | Killing an enemy increases Demon Form duration | C++ | implementiert | Metamorphosis (47241) hat 30s Duration. `PlayerScript::OnKill` oder `KillCredit`-Hook: Wenn Player in Metamorphosis (HasAura 47241) → ExtendAura Duration um X Sekunden (z.B. +5s pro Kill). `Aura::SetDuration(GetDuration() + 5000)`. Kein Cap oder mit Cap (z.B. max 120s). Farming-Sustain-Mechanik. |
| 2 | 900834 | Demon Form: periodic shadow AoE + self heal | C++ | implementiert | Passive Aura aktiv nur während Metamorphosis (47241). Periodic Tick alle X Sekunden → CastSpell(Shadow-AoE-Helper, triggered=true) um Caster + CastSpell(Heal-Helper, triggered=true) auf Caster. Heal = % des Damage dealt oder flat. Ansatz: AuraScript auf Metamorphosis → `OnPeriodicTick` oder separater Periodic-Trigger-Spell der nur aktiv ist wenn Meta-Aura vorhanden. |
| 3 | 900835 | Demons have chance to spawn lesser version of themselves | C++ | implementiert | Proc-Aura auf Warlock-Pet: `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` (0x4). `HandleProc`: Chance X% → SummonCreature(Lesser-Version-NPC) an Pet-Position. Lesser Version: Temporärer NPC (z.B. 30s Duration), reduzierte Stats (50% HP/Damage), gleicher NPC-Typ aber mit Suffix. Braucht Custom Creature-Templates pro Pet-Typ (Lesser Imp, Lesser Felguard, etc.). ICD empfohlen (z.B. 30s). |
| 4 | 900836 | Imp Firebolt +50% damage | DBC | implementiert | Passive Aura auf Warlock (transferred to Pet): `SPELL_AURA_ADD_PCT_MODIFIER` +50% auf Imp Firebolt (47964). Oder: Aura direkt auf Pet via Owner-Aura-Scaling. Einfacher Damage-Multiplikator. |
| 5 | 900837 | Imp Firebolt +9 targets | C++ | implementiert | Imp Firebolt (47964) ist Single-Target. SpellScript `AfterHit` → Chain zu 9 weiteren Feinden im Radius. CastSpell(Firebolt-Damage-Helper, triggered=true). Braucht Helper-Spell (z.B. 900841). Imp wird zum AoE-Caster. |
| 6 | 900838 | Felguard AoE unlimited targets | DBC/C++ | implementiert | Felguard Cleave (47994) trifft normalerweise begrenzte Targets. DBC: `MaxAffectedTargets` entfernen/sehr hoch. C++: `OnObjectAreaTargetSelect` → kein Target-Limit. |
| 7 | 900839 | Felguard +50% damage | DBC | implementiert | Passive Aura: `SPELL_AURA_MOD_DAMAGE_PERCENT_DONE` +50% auf Felguard (alle Schools). Applied via Owner-to-Pet Aura Scaling. Einfacher Damage-Multiplikator für alle Felguard-Abilities. |
| 8 | 900840 | Sacrificing pet grants ALL pet bonuses | C++ | implementiert | Demonic Sacrifice (18788) gibt normalerweise einen Buff abhängig vom geopferten Pet-Typ (Imp→Fire Dmg, VW→HP Regen, etc.). Ansatz: SpellScript Override → Beim Sacrifice → ApplyAura für ALLE Pet-Typ-Buffs gleichzeitig (Imp-Bonus + VW-Bonus + Succubus-Bonus + Felhunter-Bonus + Felguard-Bonus). Braucht Liste aller Sacrifice-Buff-IDs und Apply aller auf einmal. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Warlock — Demonology (900833-900865)".
