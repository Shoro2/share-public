# Global / Non-Class Spells

**Source:** [`custom_spells_global.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_global.cpp)
**ID-Range:** 901100-901199
**Status:** Not tested (imported from `CustomSpells.md`)

> Global passive spells that apply to ALL classes. SpellFamilyName = 0 (Generic). Granted automatically to all players at Paragon level.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901100 | Cast while moving | DBC/C++ | not tested | Passive aura: Must affect all of the player's spells. Approach: `SPELL_ATTR5_CAN_CHANNEL_WHEN_MOVING` only covers channels. For all casts: C++ Hook on `Spell::CheckCast()` → skip the `SPELL_FAILED_MOVING` check when the aura is active. Or: `Player::isMoving()` Override. Alternatively DBC: aura with `SPELL_AURA_CAST_WHILE_WALKING` (Aura 330, exists in WotLK DBC). Most powerful global buff — eliminates cast-time weakness completely for all caster classes. |
| 2 | 901101 | Kill enemy → heal 5% total HP | C++ | not tested | Passive Proc aura: `PROC_FLAG_KILL` (0x1). `HandleProc`: `GetCaster()->CastCustomSpell(Heal-Helper, SPELLVALUE_BASE_POINT0, MaxHealth * 5 / 100, GetCaster(), triggered=true)`. Or: `GetCaster()->ModifyHealth(MaxHealth * 0.05)`. Simple on-kill heal. No ICD needed (kill events are naturally rate-limited). May need  Helper-Heal-Spell (e.g. 901105) for combat log visibility. |
| 3 | 901102 | Attacks 25% chance to hit again (Extra Attack) | C++/DBC | not tested | Passive Proc aura: `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` (0x4) + `PROC_FLAG_DONE_SPELL_MELEE_DMG_CLASS` (0x10). Chance 25%. `HandleProc`: CastSpell(Extra-Attack-Helper, triggered=true) on Target — repeats the last attack. For melee: `SPELL_AURA_ADD_EXTRA_ATTACKS` (like Windfury/Sword Spec). For ranged/spell: SpellScript `AfterHit` → CastSpell(same spell, triggered=true) with 25% chance. Caution: must prevent recursive procs (extra attack must not trigger again). |
| 4 | 901103 | Spells/abilities 10% chance to hit all enemies within 10y | C++ | not tested | Passive Proc aura: `PROC_FLAG_DONE_SPELL_MAGIC_DMG_CLASS_NEG` + `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` + `PROC_FLAG_DONE_RANGED_AUTO_ATTACK`. Chance 10%. `HandleProc`: Find all enemies in a 10yd radius around the target → CastSpell(Damage-Helper, triggered=true) on each. Damage = same amount as the original hit. Needs ProcEventInfo → GetDamageInfo → GetDamage() for the damage value. Needs helper damage spell (e.g. 901106). ICD recommended (e.g. 1s). |
| 5 | 901104 | Avoid attack → counter attack | C++ | not tested | Passive Proc aura: `PROC_FLAG_TAKEN_MELEE_AUTO_ATTACK` (0x2) with `PROC_HIT_DODGE|PROC_HIT_PARRY|PROC_HIT_BLOCK` (avoid events). `HandleProc`: If Dodge/Parry/Block → CastSpell(Counter-Attack-Helper, triggered=true) on the attacker. Counter Attack = instant melee damage back. Comparable to Rogue Riposte or Warrior Overpower Proc — but automatic and for all classes. Needs helper damage spell (e.g. 901107). |

> **Helper-Spells Non-Class**: 901101 (Kill Heal) → Heal-Helper 901105. 901102 (Extra Attack) → Helper 901108. 901103 (AoE Proc) → Damage-Helper 901106. 901104 (Counter Attack) → Damage-Helper 901107.

> **Particularly elaborate**: 901100 (Cast While Moving) is the most powerful buff in the entire system — fundamentally changes gameplay for all casters. Must be implemented robustly (channel + cast + interruptible spells). 901102 (Extra Attack 25%) must cleanly prevent recursive procs. 901103 (10% AoE Proc) needs ICD to prevent spam on fast DoT ticks.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Non-Class — Global (901100-901199)".
