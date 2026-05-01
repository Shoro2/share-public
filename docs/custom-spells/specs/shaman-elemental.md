# Shaman — Elemental

**Source:** [`custom_spells_shaman.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_shaman.cpp)
**ID-Range:** 900400-900432
**Status:** Live (importiert aus `CustomSpells.md`)

> Shaman SpellFamilyName = 11. Chain Lightning flags[0]=0x2, Flame Shock flags[0]=0x10000000, Lightning Overload icon=2018.

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900400 | Chain Lightning +6 targets, no dmg reduction | C++ | implementiert | Marker-Aura (DUMMY). C++ SpellScript auf CL (-49271): `AfterHit` → CastCustomSpell(900408) auf 6 Extra-Feinde in 12yd mit vollem Damage. Prüft `HasAura(900400)`. |
| 2 | 900401 | Totems follow player | C++/PlayerScript | implementiert | Marker-Aura (DUMMY). `custom_totem_follow_playerscript::OnPlayerUpdate` → alle 2s prüft ob Totems >5yd entfernt → NearTeleportTo(Player). Prüft `HasAura(900401)`. |
| 3 | 900402 | Fire Elemental → Ragnaros | C++ | implementiert | Marker-Aura (DUMMY). C++ SpellScript auf Fire Ele Totem (2894): `AfterCast` → SetDisplayId(11121 Ragnaros), Scale 0.35, 2× HP. Prüft `HasAura(900402)`. |
| 4 | 900403 | Lightning Overload + Lava Burst | C++ | implementiert | Marker-Aura (DUMMY). C++ SpellScript auf LvB (-51505): `AfterHit` → prüft LO Talent (icon 2018), doppelte Proc-Chance, CastCustomSpell(LvB, halber Damage, triggered). Prüft `HasAura(900403)`. |
| 5 | 900404 | Lava Burst spreads Flame Shock | C++ | implementiert | Marker-Aura (DUMMY). C++ SpellScript auf LvB (-51505): `AfterHit` → prüft ob Target FS hat (flags[0]=0x10000000), CastSpell(FS) auf 5 Extra-Feinde in 10yd. Prüft `HasAura(900404)`. |
| 6 | 900405 | Flame Shock ticks → reset LvB CD | C++ | implementiert | Proc-Aura (DUMMY). spell_proc: ProcFlags=0x400000, SpellFamilyMask0=0x10000000, 15% Chance, 2s ICD. C++ HandleProc → RemoveSpellCooldown(51505). |
| 7 | 900406 | Lava Burst two charges | C++ | implementiert | Stacking DUMMY (CumulativeAura=2). C++ SpellScript auf LvB (-51505): `AfterCast` → Stack-Count als Charge-Tracker (1=first charge used→reset CD, 2=second charge→normal CD). Prüft `HasAura(900406)`. |
| 8 | 900407 | Clearcasting → Lava Burst instant | DBC | implementiert | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_CASTING_TIME` (14) = -100%. EffectSpellClassMaskB=0x1000 (LvB flags, verify!). Macht LvB permanent instant wenn Passive aktiv. |
| H1 | 900408 | Chain Lightning Arc (helper) | DBC | implementiert | Instant Nature Damage. Effect=SCHOOL_DAMAGE(2), Target=ENEMY(6), SchoolMask=8(Nature). BasePoints überschrieben via CastCustomSpell. |

> **Hinweis Ele**: Lava Burst SpellFamilyFlags in EffectSpellClassMaskB für 900407 muss verifiziert werden (0x1000 ist Schätzung). 900401 (Totem Follow) nutzt NearTeleportTo statt MoveFollow da Totems keine echte Bewegung haben — kann zu visuellen Rucklern führen. 900402 (Ragnaros) ist nur ein Display-Swap + HP-Buff, keine eigene AI. 900406 (LvB Charges) nutzt Aura-Stacks als Charge-Tracker — funktioniert aber kann bei schnellem Casting Edge-Cases haben.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Shaman — Elemental (900400-900432)".
