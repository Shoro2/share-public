# Shaman — Elemental

**Source:** [`custom_spells_shaman.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_shaman.cpp)
**ID-Range:** 900400-900432
**Status:** implemented

> Shaman SpellFamilyName = 11. Chain Lightning flags[0]=0x2, Flame Shock flags[0]=0x10000000, Lightning Overload icon=2018.

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900400 | Chain Lightning +6 targets, no dmg reduction | C++ | implemented | Marker aura (DUMMY). C++ SpellScript on CL (-49271): `AfterHit` → CastCustomSpell(900408) on 6 extra enemies in 12yd at full damage. Checks `HasAura(900400)`. |
| 2 | 900401 | Totems follow player | C++/PlayerScript | implemented | Marker aura (DUMMY). `custom_totem_follow_playerscript::OnPlayerUpdate` → every 2s checks whether totems are >5yd away → NearTeleportTo(Player). Checks `HasAura(900401)`. |
| 3 | 900402 | Fire Elemental → Ragnaros | C++ | implemented | Marker aura (DUMMY). C++ SpellScript on Fire Ele Totem (2894): `AfterCast` → SetDisplayId(11121 Ragnaros), Scale 0.35, 2× HP. Checks `HasAura(900402)`. |
| 4 | 900403 | Lightning Overload + Lava Burst | C++ | implemented | Marker aura (DUMMY). C++ SpellScript on LvB (-51505): `AfterHit` → checks LO talent (icon 2018), doubled proc chance, CastCustomSpell(LvB, half damage, triggered). Checks `HasAura(900403)`. |
| 5 | 900404 | Lava Burst spreads Flame Shock | C++ | implemented | Marker aura (DUMMY). C++ SpellScript on LvB (-51505): `AfterHit` → checks if the target has FS (flags[0]=0x10000000), CastSpell(FS) on 5 extra enemies in 10yd. Checks `HasAura(900404)`. |
| 6 | 900405 | Flame Shock ticks → reset LvB CD | C++ | implemented | Proc aura (DUMMY). spell_proc: ProcFlags=0x400000, SpellFamilyMask0=0x10000000, 15% chance, 2s ICD. C++ HandleProc → RemoveSpellCooldown(51505). |
| 7 | 900406 | Lava Burst two charges | C++ | implemented | Stacking DUMMY (CumulativeAura=2). C++ SpellScript on LvB (-51505): `AfterCast` → stack count as charge tracker (1=first charge used→reset CD, 2=second charge→normal CD). Checks `HasAura(900406)`. |
| 8 | 900407 | Clearcasting → Lava Burst instant | DBC | implemented | `ADD_PCT_MODIFIER` (108) + `SPELLMOD_CASTING_TIME` (14) = -100%. EffectSpellClassMaskB=0x1000 (LvB flags, verify!). Makes LvB permanently instant while the passive is active. |
| H1 | 900408 | Chain Lightning Arc (helper) | DBC | implemented | Instant Nature Damage. Effect=SCHOOL_DAMAGE(2), Target=ENEMY(6), SchoolMask=8(Nature). BasePoints overridden via CastCustomSpell. |

> **Note Ele**: Lava Burst SpellFamilyFlags in EffectSpellClassMaskB for 900407 must be verified (0x1000 is an estimate). 900401 (Totem Follow) uses NearTeleportTo instead of MoveFollow because totems have no real movement — may lead to visual jitter. 900402 (Ragnaros) is only a display swap + HP buff, no custom AI. 900406 (LvB Charges) uses aura stacks as a charge tracker — works but may have edge cases under fast casting.

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Shaman — Elemental (900400-900432)".
