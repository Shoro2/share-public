# Warlock — Demonology

**Source:** [`custom_spells_warlock.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_warlock.cpp)
**ID-Range:** 900833-900865
**Status:** Not tested (imported from `CustomSpells.md`)

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900833 | Killing an enemy increases Demon Form duration | C++ | not tested | Metamorphosis (47241) has 30s duration. `PlayerScript::OnKill` or `KillCredit` hook: If the player is in Metamorphosis (HasAura 47241) → ExtendAura Duration by X seconds (e.g. +5s per kill). `Aura::SetDuration(GetDuration() + 5000)`. No cap or with cap (e.g. max 120s). Farming sustain mechanic. |
| 2 | 900834 | Demon Form: periodic shadow AoE + self heal | C++ | not tested | Passive aura only active during Metamorphosis (47241). Periodic tick every X seconds → CastSpell(Shadow-AoE-Helper, triggered=true) around the caster + CastSpell(Heal-Helper, triggered=true) on Caster. Heal = % of damage dealt or flat. Approach: AuraScript on Metamorphosis → `OnPeriodicTick` or a separate periodic-trigger spell active only while the Meta aura is present. |
| 3 | 900835 | Demons have chance to spawn lesser version of themselves | C++ | not tested | Proc aura on Warlock-Pet: `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` (0x4). `HandleProc`: X% chance → SummonCreature(Lesser-Version-NPC) at the pet position. Lesser version: temporary NPC (e.g. 30s duration), reduced stats (50% HP/damage), same NPC type but with a suffix. Needs custom creature templates per pet type (Lesser Imp, Lesser Felguard, etc.). ICD recommended (e.g. 30s). |
| 4 | 900836 | Imp Firebolt +50% damage | DBC | not tested | Passive Aura on Warlock (transferred to Pet): `SPELL_AURA_ADD_PCT_MODIFIER` +50% on Imp Firebolt (47964). Or: aura applied directly to the pet via Owner-Aura-Scaling. Simple damage multiplier. |
| 5 | 900837 | Imp Firebolt +9 targets | C++ | not tested | Imp Firebolt (47964) is single-target. SpellScript `AfterHit` → chain to 9 additional enemies in range. CastSpell(Firebolt-Damage-Helper, triggered=true). Needs a helper spell (e.g. 900841). The imp becomes an AoE caster. |
| 6 | 900838 | Felguard AoE unlimited targets | DBC/C++ | not tested | Felguard Cleave (47994) normally hits a limited number of targets. DBC: remove or set very high `MaxAffectedTargets`. C++: `OnObjectAreaTargetSelect` → no target limit. |
| 7 | 900839 | Felguard +50% damage | DBC | not tested | Passive aura: `SPELL_AURA_MOD_DAMAGE_PERCENT_DONE` +50% on Felguard (all schools). Applied via Owner-to-Pet Aura Scaling. Simple damage multiplier for all Felguard abilities. |
| 8 | 900840 | Sacrificing pet grants ALL pet bonuses | C++ | not tested | Demonic Sacrifice (18788) normally grants a buff depending on the sacrificed pet type (Imp→Fire Dmg, VW→HP Regen, etc.). Approach: SpellScript Override → On sacrifice → ApplyAura for ALL pet type buffs at once (Imp-Bonus + VW-Bonus + Succubus-Bonus + Felhunter-Bonus + Felguard-Bonus). Needs a list of all sacrifice buff IDs and apply them all at once. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Warlock — Demonology (900833-900865)".
