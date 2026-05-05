# Custom Spells — Procs & flags

> Source: [`mod-custom-spells/PROCFLAGS_REFERENCE.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/PROCFLAGS_REFERENCE.md). Values verified against `azerothcore-wotlk/src/server/game/Spells/SpellMgr.h`.

## `spell_proc` required fields

Every passive proc aura (DBC effect `SPELL_AURA_PROC_TRIGGER_SPELL` or `SPELL_AURA_DUMMY` that should react via `OnEffectProc`) needs an entry in `spell_proc`. Without that entry, `GetProcEffectMask()` will always return 0 and the proc will never fire.

```sql
DELETE FROM `spell_proc` WHERE `SpellId` = 900172;
INSERT INTO `spell_proc`
  (`SpellId`, `SchoolMask`, `SpellFamilyName`,
   `SpellFamilyMask0`, `SpellFamilyMask1`, `SpellFamilyMask2`,
   `ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`,
   `AttributesMask`, `DisableEffectsMask`,
   `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`)
VALUES
  (900172,    -- SpellId
   0,         -- SchoolMask (0 = all)
   0,         -- SpellFamilyName (0 = all, 4 = Warrior, etc.)
   0, 0, 0,   -- SpellFamilyMask0/1/2 (0 = all, C++ filters)
   0x8,       -- ProcFlags: TAKEN_MELEE_AUTO_ATTACK
   0,         -- SpellTypeMask (0 = all, 1 = DAMAGE, 2 = HEAL, 4 = NO_DMG_HEAL)
   0,         -- SpellPhaseMask (0 = all, 1 = CAST, 2 = HIT, 4 = FINISH)
   0,         -- HitMask (0 = NORMAL|CRITICAL|ABSORB)
   0, 0,      -- AttributesMask, DisableEffectsMask
   0,         -- ProcsPerMinute (0 = use Chance instead of PPM)
   100,       -- Chance %
   1000,      -- Cooldown ms (ICD)
   0);        -- Charges (0 = unlimited)
```

Filtering is typically left entirely to the C++ `CheckProc` — that is why the family fields are often 0.

## ProcFlags values (full)

| Flag | Hex | Bit | Meaning |
|------|-----|-----|-----------|
| `PROC_FLAG_NONE` | `0x0` | — | no proc |
| `PROC_FLAG_KILLED` | `0x1` | 0 | own death (killed by an aggressor) |
| `PROC_FLAG_KILL` | `0x2` | 1 | killed an enemy (XP/honor-eligible) |
| `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` | `0x4` | 2 | own melee auto-attack |
| `PROC_FLAG_TAKEN_MELEE_AUTO_ATTACK` | `0x8` | 3 | enemy melee auto-attack |
| `PROC_FLAG_DONE_SPELL_MELEE_DMG_CLASS` | `0x10` | 4 | own melee spell |
| `PROC_FLAG_TAKEN_SPELL_MELEE_DMG_CLASS` | `0x20` | 5 | enemy melee spell |
| `PROC_FLAG_DONE_RANGED_AUTO_ATTACK` | `0x40` | 6 | own ranged auto-attack |
| `PROC_FLAG_TAKEN_RANGED_AUTO_ATTACK` | `0x80` | 7 | enemy ranged auto-attack |
| `PROC_FLAG_DONE_SPELL_RANGED_DMG_CLASS` | `0x100` | 8 | own ranged spell (Steady/Aimed Shot) |
| `PROC_FLAG_TAKEN_SPELL_RANGED_DMG_CLASS` | `0x200` | 9 | enemy ranged spell |
| `PROC_FLAG_DONE_SPELL_NONE_DMG_CLASS_POS` | `0x400` | 10 | own positive non-magic spell |
| `PROC_FLAG_TAKEN_SPELL_NONE_DMG_CLASS_POS` | `0x800` | 11 | — |
| `PROC_FLAG_DONE_SPELL_NONE_DMG_CLASS_NEG` | `0x1000` | 12 | own negative non-magic spell |
| `PROC_FLAG_TAKEN_SPELL_NONE_DMG_CLASS_NEG` | `0x2000` | 13 | — |
| `PROC_FLAG_DONE_SPELL_MAGIC_DMG_CLASS_POS` | `0x4000` | 14 | own positive magic spell (**heals!**) |
| `PROC_FLAG_TAKEN_SPELL_MAGIC_DMG_CLASS_POS` | `0x8000` | 15 | — |
| `PROC_FLAG_DONE_SPELL_MAGIC_DMG_CLASS_NEG` | `0x10000` | 16 | own negative magic spell |
| `PROC_FLAG_TAKEN_SPELL_MAGIC_DMG_CLASS_NEG` | `0x20000` | 17 | — |
| `PROC_FLAG_DONE_PERIODIC` | `0x40000` | 18 | own DoT/HoT tick |
| `PROC_FLAG_TAKEN_PERIODIC` | `0x80000` | 19 | received DoT/HoT tick |
| `PROC_FLAG_TAKEN_DAMAGE` | `0x100000` | 20 | any damage taken |
| `PROC_FLAG_DONE_TRAP_ACTIVATION` | `0x200000` | 21 | trap activation |
| `PROC_FLAG_DONE_MAINHAND_ATTACK` | `0x400000` | 22 | main-hand hit (auto+spell) |
| `PROC_FLAG_DONE_OFFHAND_ATTACK` | `0x800000` | 23 | off-hand hit (auto+spell) |
| `PROC_FLAG_DEATH` | `0x1000000` | 24 | dies |

## Common combinations

| Hex | Purpose | Examples |
|-----|-------|-----------|
| `0x14` | own melee auto + melee spell | Bladestorm CD reduce, Death Coil proc, extra attack |
| `0x140` | own ranged auto + ranged spell | Hunter Trap proc |
| `0x10014` | melee auto + melee spell + magic neg | Cleave proc |

## SpellTypeMask, SpellPhaseMask, HitMask

| Field | Value | Meaning |
|------|------|-----------|
| `SpellTypeMask` | 0 | all spell types |
| | 1 | DAMAGE |
| | 2 | HEAL |
| | 4 | NO_DMG_HEAL |
| `SpellPhaseMask` | 0 | all phases (default is HIT) |
| | 1 | CAST |
| | 2 | HIT |
| | 4 | FINISH |
| `HitMask` | 0 | default: NORMAL\|CRITICAL\|ABSORB |
| | `PROC_HIT_NORMAL` | normal hit |
| | `PROC_HIT_CRITICAL` | crit |
| | `PROC_HIT_BLOCK` | blocked |
| | `PROC_HIT_DODGE` | dodged |
| | `PROC_HIT_PARRY` | parried |
| | `PROC_HIT_ABSORB` | fully absorbed |

`HitMask` can also be checked in C++ via `eventInfo.GetHitMask()` — often cleaner than filtering in `spell_proc`, because a single entry can cover multiple outcomes (block + crit).

## SpellFamilyFlags verification

**Never** take `SpellFamilyFlags` from online sources (wowhead, wowdb) at face value. The server DBC can differ from standard WotLK values — diagnostic pattern:

```cpp
bool CheckProc(ProcEventInfo& eventInfo)
{
    SpellInfo const* spellInfo = eventInfo.GetSpellInfo();
    if (!spellInfo) return false;
    LOG_INFO("module", "CheckProc: spell {} family {} flags[0]=0x{:08X} flags[1]=0x{:08X}",
        spellInfo->Id, spellInfo->SpellFamilyName,
        spellInfo->SpellFamilyFlags[0], spellInfo->SpellFamilyFlags[1]);
    return spellInfo->SpellFamilyName == 4
        && (spellInfo->SpellFamilyFlags[1] & 0x00000400);
}
```

## Off-by-one BasePoints

`Spell.dbc` internally stores `EffectBasePoints = real_value - 1`. Anyone writing `BasePoints=50` in `spell_dbc` for "+50 %" gets **+51 %** in-game. Two clean ways:

1. consistently store `real_value - 1` (i.e. `49` for +50 %).
2. set the effect at runtime via `DoEffectCalcAmount`.

## DBC `EffectSpellClassMask` is ignored

The "Class Mask Target Spells" from the WoW Spell Editor (DBC fields `EffectSpellClassMaskA/B/C`) have **no** effect on procs from `SPELL_AURA_PROC_TRIGGER_SPELL`. Filtering happens exclusively through `spell_proc` and the C++ `CheckProc`.

## Recursion guard

Procs can trigger procs — that often becomes a trap.

- Call `PreventDefaultAction()` in `HandleProc()`, otherwise both the default handler (trigger spell from DBC) and the custom cast will run.
- Check `SPELL_ATTR3_CAN_PROC_FROM_PROCS` in the DBC attributes — by default triggered spells do not proc further; intentional chains must set the flag explicitly.
- Helper spells (via `CastSpell(target, ID, true)`) can hit the source of their trigger again. Set an ICD in `spell_proc.Cooldown` to prevent spam loops on AoE/DoT ticks (typical 500–1000 ms).

## Known bug fixes (historical)

The following `spell_proc` entries had wrong ProcFlags (values from the old `share-public/CLAUDE.md` table were incorrect). Corrected in `mod_custom_spells_*.sql`:

| SpellId | Description | Old | New |
|---------|-------------|-----|-----|
| 900172 | Block→AoE | `0x2` (KILL) | `0x8` TAKEN_MELEE_AUTO |
| 900173 | Block→Enhanced TC | `0x2` | `0x8` |
| 900366 | DK Unholy DoT-AoE | `0x400000` (MAINHAND) | `0x40000` DONE_PERIODIC |
| 900405 | Shaman FS-Reset-LvB | `0x400000` | `0x40000` |
| 900566 | Hunter Trap Proc | `0x44` (Melee+Ranged Auto) | `0x140` (Ranged Auto+Spell) |
| 901066 | Druid HoT→Treant | `0x400000` | `0x40000` |
| 900933 | Priest Heal→Holy-Fire | `0x10000` (Magic-Neg) | `0x4000` (Magic-Pos) |
| 901101 | Global Kill→Heal | `0x1` (KILLED) | `0x2` KILL |
| 901104 | Global Counter-Attack | `0x2` (KILL) | `0x8` TAKEN_MELEE_AUTO |

Lesson: for every new `spell_proc` entry, verify ProcFlags + HitMask via debug log to be safe.
