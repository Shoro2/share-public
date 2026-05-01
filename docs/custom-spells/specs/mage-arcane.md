# Mage — Arcane

**Source:** [`custom_spells_mage.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_mage.cpp)
**ID-Range:** 900700-900732
**Status:** Live (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900701 | Mana regen +2% per missing mana % | C++ | implementiert | Dynamische Mana-Regen-Skalierung. `PlayerScript::OnUpdateManaRegen` oder periodic Aura-Tick: Berechne fehlende Mana% → setze Regen-Bonus = fehlende% × 2%. Bei 50% Mana fehlen → +100% Mana Regen. Bei 90% fehlen → +180%. Passive Aura mit `SPELL_AURA_OBS_MOD_POWER` oder C++ Hook auf `Player::RegenerateMana()`. Sehr starke Mana-Sustain-Mechanik. |
| 2 | 900702 | Arcane Barrage +50% damage | DBC | implementiert | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` +50% auf Arcane Barrage (44781). SpellFamilyName=3, SpellFamilyFlags für Barrage. Einfacher Damage-Multiplikator. |
| 3 | 900703 | Arcane Barrage +9 targets | DBC/C++ | implementiert | Arcane Barrage (44781) trifft normalerweise 3 Targets. DBC: `MaxAffectedTargets` auf 10+ setzen. Oder C++: `OnObjectAreaTargetSelect` → Target-Limit entfernen. |
| 4 | 900704 | Arcane Blast cast time -50% | DBC | implementiert | Passive Aura: `SPELL_AURA_ADD_PCT_MODIFIER` (SPELLMOD_CASTING_TIME) -50% auf Arcane Blast (42897). Base Cast Time 2.5s → 1.25s. Stapelt mit Arcane Blast Debuff (noch schneller mit Stacks). |
| 5 | 900705 | Arcane Blast +9 targets | C++ | implementiert | Arcane Blast (42897) ist Single-Target. SpellScript `AfterHit` → Chain zu 9 weiteren Feinden im Radius. CastSpell(AB-Damage-Helper, triggered=true). Braucht Helper-Spell (z.B. 900710). |
| 6 | 900706 | Arcane Charges stack up to 8 | DBC/C++ | implementiert | Arcane Blast Debuff (36032) stackt normalerweise bis 4. DBC: `StackAmount` auf 8 setzen. C++: Falls hardcoded → `AuraScript::OnStackChange` → Allow stacks >4. Jeder Stack erhöht AB Damage +15% und Mana Cost +150% (Base-Werte). 8 Stacks = +120% Damage, +1200% Mana Cost. Balancing beachten! |
| 7 | 900707 | Arcane Explosion generates 1 Arcane Charge (like Arcane Blast) | C++ | implementiert | Arcane Explosion (42921) ist AoE Instant. SpellScript `AfterCast` → ApplyAura(Arcane Blast Debuff 36032, 1 Stack) auf Caster. Gleiche Mechanik wie AB aber ohne Consume. AE wird zu einem AoE Arcane Charge Generator. |
| 8 | 900708 | Below 30% health → activate Mana Shield + restore all mana | C++ | implementiert | Passive Proc-Aura: `PROC_FLAG_TAKEN_DAMAGE` (0x4000). `HandleProc`: Wenn Health <30% → CastSpell(Mana Shield 43020, triggered=true) + SetPower(MANA, MaxMana). ICD empfohlen (z.B. 60s) um Abuse zu verhindern. Sehr starke Überlebens-Mechanik: Volle Mana + Shield bei Low HP. |
| 9 | 900709 | Blink target location selection | C++ | implementiert | Blink (1953) teleportiert normalerweise 20yd vorwärts. Ansatz: Override Blink → Click-to-Blink mit Target-Location. SpellScript `HandleDummy`: Lese SpellDestination → Teleport Caster dorthin (max Range z.B. 40yd). DBC: Spell Target-Type auf `TARGET_DEST_DEST` ändern. Braucht Client-seitig: Spell zeigt Ground-Target-Cursor. Vergleichbar mit Heroic Leap Targeting. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Mage — Arcane (900700-900732)".
