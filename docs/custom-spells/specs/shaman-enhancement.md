# Shaman — Enhancement

**Source:** [`custom_spells_shaman.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_shaman.cpp)
**ID-Range:** 900433-900465
**Status:** Live (importiert aus `CustomSpells.md`)

> Maelstrom Weapon (53817) stacks to 5. Feral Spirit (51533) summons 2 Spirit Wolves (NPC 29264).

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900433 | Totems follow player | PlayerScript | implementiert | DUMMY Marker. Shared `custom_totem_follow_playerscript` prüft auch `HasAura(900433)`. Teleportiert Totems alle 2s. |
| 2 | 900434 | 5 Maelstrom stacks → summons AoE 5s | C++ | implementiert | DUMMY Marker. C++ AuraScript auf Maelstrom Weapon (53817): `OnEffectApply` bei Stack=5 → CastSpell(900439 Buff) + CastSpell(900440 AoE) auf alle Controlled Units. |
| 3 | 900435 | Summons +50% damage | DBC | implementiert | DUMMY Marker (BasePoints=50). Aktuell nur Marker — Pet-Scaling für +50% muss via C++ pet scaling oder owner aura transfer implementiert werden. |
| 4 | 900436 | Auto attacks → summon wolf | C++ | implementiert | Proc-Aura (DUMMY). spell_proc: ProcFlags=0x4 (melee auto), 10%, 5s ICD. C++ HandleProc → SummonCreature(900436 Spirit Wolf, 15s). NPC 900436 hat DisplayID 27074 (Wolf). |
| 5 | 900437 | Spirit Wolves inherit haste | C++ | implementiert | DUMMY Marker. C++ SpellScript auf Feral Spirit (51533): `AfterCast` → liest Owner Haste (UNIT_MOD_CAST_SPEED) → SetAttackTime auf Wolves. |
| 6 | 900438 | Spirit Wolves 5% CL on hit | C++/UnitScript | implementiert | DUMMY Marker. `custom_wolf_cl_unitscript::OnDamage` → wenn Attacker=Spirit Wolf (29264) + Owner HasAura(900438) → 5% CastSpell(CL 49271). |
| H1 | 900439 | Maelstrom Fury (buff) | DBC | implementiert | 5s DUMMY Buff (DurationIndex=18). Visueller Marker für empowered summons. |
| H2 | 900440 | Spirit Howl (AoE helper) | DBC | implementiert | Instant AoE Physical Damage. Effect=SCHOOL_DAMAGE(2), Target=SRC_AREA_ENEMY(22), 800+200rnd, 8yd. |

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Shaman — Enhancement (900433-900465)".
