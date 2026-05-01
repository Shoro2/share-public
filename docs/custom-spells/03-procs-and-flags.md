# Custom Spells — Procs & Flags

> Quelle: [`mod-custom-spells/PROCFLAGS_REFERENCE.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/PROCFLAGS_REFERENCE.md). Werte verifiziert gegen `azerothcore-wotlk/src/server/game/Spells/SpellMgr.h`.

## `spell_proc` Pflichtfelder

Jede passive Proc-Aura (DBC-Effekt `SPELL_AURA_PROC_TRIGGER_SPELL` oder `SPELL_AURA_DUMMY`, die per `OnEffectProc` reagieren soll) braucht einen Eintrag in `spell_proc`. Ohne den Eintrag wird `GetProcEffectMask()` immer 0 liefern und der Proc feuert nie.

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
   0,         -- SchoolMask (0 = alle)
   0,         -- SpellFamilyName (0 = alle, 4 = Warrior, etc.)
   0, 0, 0,   -- SpellFamilyMask0/1/2 (0 = alle, C++ filtert)
   0x8,       -- ProcFlags: TAKEN_MELEE_AUTO_ATTACK
   0,         -- SpellTypeMask (0 = alle, 1 = DAMAGE, 2 = HEAL, 4 = NO_DMG_HEAL)
   0,         -- SpellPhaseMask (0 = alle, 1 = CAST, 2 = HIT, 4 = FINISH)
   0,         -- HitMask (0 = NORMAL|CRITICAL|ABSORB)
   0, 0,      -- AttributesMask, DisableEffectsMask
   0,         -- ProcsPerMinute (0 = nutzt Chance statt PPM)
   100,       -- Chance %
   1000,      -- Cooldown ms (ICD)
   0);        -- Charges (0 = unbegrenzt)
```

Die Filterung wird typischerweise vollständig dem C++-`CheckProc` überlassen — deshalb stehen die Family-Felder oft auf 0.

## ProcFlags-Werte (vollständig)

| Flag | Hex | Bit | Bedeutung |
|------|-----|-----|-----------|
| `PROC_FLAG_NONE` | `0x0` | — | Kein Proc |
| `PROC_FLAG_KILLED` | `0x1` | 0 | Eigener Tod (von Aggressor getötet) |
| `PROC_FLAG_KILL` | `0x2` | 1 | Gegner getötet (XP/Honor-würdig) |
| `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` | `0x4` | 2 | Eigener Melee-Autoattack |
| `PROC_FLAG_TAKEN_MELEE_AUTO_ATTACK` | `0x8` | 3 | Gegnerischer Melee-Autoattack |
| `PROC_FLAG_DONE_SPELL_MELEE_DMG_CLASS` | `0x10` | 4 | Eigener Melee-Spell |
| `PROC_FLAG_TAKEN_SPELL_MELEE_DMG_CLASS` | `0x20` | 5 | Gegnerischer Melee-Spell |
| `PROC_FLAG_DONE_RANGED_AUTO_ATTACK` | `0x40` | 6 | Eigener Ranged-Autoattack |
| `PROC_FLAG_TAKEN_RANGED_AUTO_ATTACK` | `0x80` | 7 | Gegner-Ranged-Autoattack |
| `PROC_FLAG_DONE_SPELL_RANGED_DMG_CLASS` | `0x100` | 8 | Eigener Ranged-Spell (Steady/Aimed Shot) |
| `PROC_FLAG_TAKEN_SPELL_RANGED_DMG_CLASS` | `0x200` | 9 | Gegner-Ranged-Spell |
| `PROC_FLAG_DONE_SPELL_NONE_DMG_CLASS_POS` | `0x400` | 10 | Eigener positiver Non-Magic-Spell |
| `PROC_FLAG_TAKEN_SPELL_NONE_DMG_CLASS_POS` | `0x800` | 11 | — |
| `PROC_FLAG_DONE_SPELL_NONE_DMG_CLASS_NEG` | `0x1000` | 12 | Eigener negativer Non-Magic-Spell |
| `PROC_FLAG_TAKEN_SPELL_NONE_DMG_CLASS_NEG` | `0x2000` | 13 | — |
| `PROC_FLAG_DONE_SPELL_MAGIC_DMG_CLASS_POS` | `0x4000` | 14 | Eigener positiver Magic-Spell (**Heals!**) |
| `PROC_FLAG_TAKEN_SPELL_MAGIC_DMG_CLASS_POS` | `0x8000` | 15 | — |
| `PROC_FLAG_DONE_SPELL_MAGIC_DMG_CLASS_NEG` | `0x10000` | 16 | Eigener negativer Magic-Spell |
| `PROC_FLAG_TAKEN_SPELL_MAGIC_DMG_CLASS_NEG` | `0x20000` | 17 | — |
| `PROC_FLAG_DONE_PERIODIC` | `0x40000` | 18 | Eigener DoT/HoT-Tick |
| `PROC_FLAG_TAKEN_PERIODIC` | `0x80000` | 19 | Erhaltener DoT/HoT-Tick |
| `PROC_FLAG_TAKEN_DAMAGE` | `0x100000` | 20 | Beliebigen Schaden erhalten |
| `PROC_FLAG_DONE_TRAP_ACTIVATION` | `0x200000` | 21 | Trap-Aktivierung |
| `PROC_FLAG_DONE_MAINHAND_ATTACK` | `0x400000` | 22 | Mainhand-Hit (Auto+Spell) |
| `PROC_FLAG_DONE_OFFHAND_ATTACK` | `0x800000` | 23 | Offhand-Hit (Auto+Spell) |
| `PROC_FLAG_DEATH` | `0x1000000` | 24 | Stirbt |

## Häufige Kombinationen

| Hex | Zweck | Beispiele |
|-----|-------|-----------|
| `0x14` | Eigener Melee-Auto + Melee-Spell | Bladestorm CD-Reduce, Death Coil Proc, Extra Attack |
| `0x140` | Eigener Ranged-Auto + Ranged-Spell | Hunter Trap Proc |
| `0x10014` | Melee-Auto + Melee-Spell + Magic-Neg | Cleave Proc |

## SpellTypeMask, SpellPhaseMask, HitMask

| Feld | Wert | Bedeutung |
|------|------|-----------|
| `SpellTypeMask` | 0 | Alle Spell-Typen |
| | 1 | DAMAGE |
| | 2 | HEAL |
| | 4 | NO_DMG_HEAL |
| `SpellPhaseMask` | 0 | Alle Phasen (default ist HIT) |
| | 1 | CAST |
| | 2 | HIT |
| | 4 | FINISH |
| `HitMask` | 0 | Default: NORMAL\|CRITICAL\|ABSORB |
| | `PROC_HIT_NORMAL` | normaler Treffer |
| | `PROC_HIT_CRITICAL` | Crit |
| | `PROC_HIT_BLOCK` | geblockt |
| | `PROC_HIT_DODGE` | ausgewichen |
| | `PROC_HIT_PARRY` | pariert |
| | `PROC_HIT_ABSORB` | komplett absorbiert |

`HitMask` kann auch in C++ via `eventInfo.GetHitMask()` geprüft werden — oft sauberer als Filterung in `spell_proc`, weil so ein einzelner Eintrag mehrere Outcomes (Block + Crit) abdecken kann.

## SpellFamilyFlags-Verifikation

**Niemals** `SpellFamilyFlags` aus Online-Quellen (wowhead, wowdb) ungeprüft übernehmen. Die Server-DBC kann von Standard-WotLK-Werten abweichen — Diagnose-Pattern:

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

## Off-by-One BasePoints

`Spell.dbc` speichert intern `EffectBasePoints = real_value - 1`. Wer in `spell_dbc` `BasePoints=50` für "+50 %" schreibt, bekommt **+51 %** in-game. Zwei saubere Wege:

1. Konsequent `real_value - 1` ablegen (also `49` für +50 %).
2. Effekt zur Laufzeit über `DoEffectCalcAmount` setzen.

## DBC `EffectSpellClassMask` wird ignoriert

Die "Class Mask Target Spells" aus dem WoW Spell Editor (DBC-Felder `EffectSpellClassMaskA/B/C`) haben **keinen** Einfluss auf Procs bei `SPELL_AURA_PROC_TRIGGER_SPELL`. Filterung passiert ausschließlich über `spell_proc` und C++-`CheckProc`.

## Rekursionsschutz

Procs können Procs auslösen — das wird oft zur Falle.

- `PreventDefaultAction()` in `HandleProc()` aufrufen, sonst wird sowohl der Default-Handler (Trigger-Spell aus DBC) als auch der Custom-Cast ausgeführt.
- `SPELL_ATTR3_CAN_PROC_FROM_PROCS` in den DBC-Attributen kontrollieren — standardmäßig procen Triggered-Spells nicht weiter, gewollte Ketten müssen das Flag explizit setzen.
- Helper-Spells (per `CastSpell(target, ID, true)`) können die Quelle ihres Triggers erneut treffen. ICD in `spell_proc.Cooldown` setzen, um Spam-Loops bei AoE/DoT-Ticks zu verhindern (typisch 500–1000 ms).

## Bekannte Bug-Fixes (historisch)

Folgende `spell_proc`-Einträge hatten falsche ProcFlags (Werte aus der alten `share-public/CLAUDE.md`-Tabelle stimmten nicht). Korrigiert in `mod_custom_spells_*.sql`:

| SpellId | Beschreibung | Alt | Neu |
|---------|-------------|-----|-----|
| 900172 | Block→AoE | `0x2` (KILL) | `0x8` TAKEN_MELEE_AUTO |
| 900173 | Block→Enhanced TC | `0x2` | `0x8` |
| 900366 | DK Unholy DoT-AoE | `0x400000` (MAINHAND) | `0x40000` DONE_PERIODIC |
| 900405 | Shaman FS-Reset-LvB | `0x400000` | `0x40000` |
| 900566 | Hunter Trap Proc | `0x44` (Melee+Ranged-Auto) | `0x140` (Ranged-Auto+Spell) |
| 901066 | Druid HoT→Treant | `0x400000` | `0x40000` |
| 900933 | Priest Heal→Holy-Fire | `0x10000` (Magic-Neg) | `0x4000` (Magic-Pos) |
| 901101 | Global Kill→Heal | `0x1` (KILLED) | `0x2` KILL |
| 901104 | Global Counter-Attack | `0x2` (KILL) | `0x8` TAKEN_MELEE_AUTO |

Lehre: bei jedem neuen `spell_proc`-Eintrag ProcFlags + HitMask zur Sicherheit per Debug-Log verifizieren.
