# Shaman — Enhancement

**Source:** [`custom_spells_shaman.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_shaman.cpp)
**ID-Range:** 900433-900465
**Status:** implemented

> Maelstrom Weapon (53817) stacks to 5. Feral Spirit (51533) summons 2 Spirit Wolves (NPC 29264).

| # | Spell ID | Effect | Approach | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900433 | Totems follow player | PlayerScript | implemented | DUMMY marker. Shared `custom_totem_follow_playerscript` also checks `HasAura(900433)`. Teleports totems every 2s. |
| 2 | 900434 | 5 Maelstrom stacks → summons AoE 5s | C++ | implemented | DUMMY marker. C++ AuraScript on Maelstrom Weapon (53817): `OnEffectApply` at stack=5 → CastSpell(900439 Buff) + CastSpell(900440 AoE) on all controlled units. |
| 3 | 900435 | Summons +50% damage | DBC | implemented | DUMMY Marker (BasePoints=50). Currently a marker only — Pet scaling for +50% must be implemented via C++ pet scaling or owner aura transfer. |
| 4 | 900436 | Auto attacks → summon wolf | C++ | implemented | Proc aura (DUMMY). spell_proc: ProcFlags=0x4 (melee auto), 10%, 5s ICD. C++ HandleProc → SummonCreature(900436 Spirit Wolf, 15s). NPC 900436 has DisplayID 27074 (Wolf). |
| 5 | 900437 | Spirit Wolves inherit haste | C++ | implemented | DUMMY marker. C++ SpellScript on Feral Spirit (51533): `AfterCast` → reads owner haste (UNIT_MOD_CAST_SPEED) → SetAttackTime on Wolves. |
| 6 | 900438 | Spirit Wolves 5% CL on hit | C++/UnitScript | implemented | DUMMY marker. `custom_wolf_cl_unitscript::OnDamage` → when Attacker=Spirit Wolf (29264) + Owner HasAura(900438) → 5% CastSpell(CL 49271). |
| H1 | 900439 | Maelstrom Fury (buff) | DBC | implemented | 5s DUMMY Buff (DurationIndex=18). Visual marker for empowered summons. |
| H2 | 900440 | Spirit Howl (AoE helper) | DBC | implemented | Instant AoE Physical Damage. Effect=SCHOOL_DAMAGE(2), Target=SRC_AREA_ENEMY(22), 800+200rnd, 8yd. |

---

> Original source: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) section "Shaman — Enhancement (900433-900465)".
