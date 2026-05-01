# Global / Non-Class Spells

**Source:** [`custom_spells_global.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_global.cpp)
**ID-Range:** 901100-901199
**Status:** Live (importiert aus `CustomSpells.md`)

> Globale Passive-Spells die für ALLE Klassen gelten. SpellFamilyName = 0 (Generic). Werden allen Spielern auf Paragon-Level automatisch granted.

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 901100 | Cast while moving | DBC/C++ | implementiert | Passive Aura: Muss alle Spells des Spielers betreffen. Ansatz: `SPELL_ATTR5_CAN_CHANNEL_WHEN_MOVING` reicht nur für Channels. Für alle Casts: C++ Hook auf `Spell::CheckCast()` → Skip `SPELL_FAILED_MOVING` Check wenn Aura aktiv. Oder: `Player::isMoving()` Override. Alternativ DBC: Aura mit `SPELL_AURA_CAST_WHILE_WALKING` (Aura 330, existiert in WotLK-DBC). Mächtigster globaler Buff — eliminiert Cast-Time-Weakness komplett für alle Caster-Klassen. |
| 2 | 901101 | Kill enemy → heal 5% total HP | C++ | implementiert | Passive Proc-Aura: `PROC_FLAG_KILL` (0x1). `HandleProc`: `GetCaster()->CastCustomSpell(Heal-Helper, SPELLVALUE_BASE_POINT0, MaxHealth * 5 / 100, GetCaster(), triggered=true)`. Oder: `GetCaster()->ModifyHealth(MaxHealth * 0.05)`. Einfacher On-Kill-Heal. Kein ICD nötig (Kill-Events sind natürlich rate-limited). Braucht ggf. Helper-Heal-Spell (z.B. 901105) für Combat-Log-Visibility. |
| 3 | 901102 | Attacks 25% chance to hit again (Extra Attack) | C++/DBC | implementiert | Passive Proc-Aura: `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` (0x4) + `PROC_FLAG_DONE_SPELL_MELEE_DMG_CLASS` (0x10). Chance 25%. `HandleProc`: CastSpell(Extra-Attack-Helper, triggered=true) auf Target — wiederholt den letzten Angriff. Für Melee: `SPELL_AURA_ADD_EXTRA_ATTACKS` (wie Windfury/Sword Spec). Für Ranged/Spell: SpellScript `AfterHit` → CastSpell(gleicher Spell, triggered=true) mit 25% Chance. Achtung: Muss rekursive Procs verhindern (Extra-Attack triggert nicht nochmal). |
| 4 | 901103 | Spells/abilities 10% chance to hit all enemies within 10y | C++ | implementiert | Passive Proc-Aura: `PROC_FLAG_DONE_SPELL_MAGIC_DMG_CLASS_NEG` + `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` + `PROC_FLAG_DONE_RANGED_AUTO_ATTACK`. Chance 10%. `HandleProc`: Finde alle Feinde im 10yd Radius um Target → CastSpell(Damage-Helper, triggered=true) auf jedes. Damage = gleicher Amount wie Original-Hit. Braucht ProcEventInfo → GetDamageInfo → GetDamage() für Damage-Wert. Braucht Helper-Damage-Spell (z.B. 901106). ICD empfohlen (z.B. 1s). |
| 5 | 901104 | Avoid attack → counter attack | C++ | implementiert | Passive Proc-Aura: `PROC_FLAG_TAKEN_MELEE_AUTO_ATTACK` (0x2) mit `PROC_HIT_DODGE|PROC_HIT_PARRY|PROC_HIT_BLOCK` (Avoid-Events). `HandleProc`: Wenn Dodge/Parry/Block → CastSpell(Counter-Attack-Helper, triggered=true) auf Attacker. Counter Attack = Instant Melee-Damage zurück. Vergleichbar mit Rogue Riposte oder Warrior Overpower Proc — aber automatisch und für alle Klassen. Braucht Helper-Damage-Spell (z.B. 901107). |

> **Helper-Spells Non-Class**: 901101 (Kill Heal) → Heal-Helper 901105. 901102 (Extra Attack) → Helper 901108. 901103 (AoE Proc) → Damage-Helper 901106. 901104 (Counter Attack) → Damage-Helper 901107.

> **Besonders aufwändig**: 901100 (Cast While Moving) ist der mächtigste Buff im gesamten System — verändert das Gameplay fundamental für alle Caster. Muss robust implementiert sein (Channel + Cast + Interruptible-Spells). 901102 (Extra Attack 25%) muss rekursive Procs sauber verhindern. 901103 (10% AoE Proc) braucht ICD um Spam bei schnellen DoT-Ticks zu verhindern.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Non-Class — Global (901100-901199)".
