# 03 — Spell-System: SpellScripts, AuraScripts, Procs, DBC

## SpellScript / AuraScript — Klassen-Hierarchie

```
_SpellScript (abstrakte Basis)
├── SpellScript   → Spell-Effekte und Cast-Lifecycle
└── AuraScript    → Aura/Buff/Debuff-Mechaniken
```

Lifecycle:
1. **Registrierung** via `RegisterSpellScript(ClassName)` in einer `AddSC_*()`-Funktion
2. **Validate(SpellInfo*)** prüft DBC-Daten beim Server-Start (optional)
3. **Load()** — bei Instanzerstellung aufgerufen
4. **Register()** override — bindet Handler an Spell-Events
5. **Execute** — Handler werden bei Events aufgerufen

## SpellScript-Hooks

```cpp
// Cast-Lifecycle
SPELL_SCRIPT_HOOK_CHECK_CAST     // Vor Cast: kann blockieren
SPELL_SCRIPT_HOOK_BEFORE_CAST
SPELL_SCRIPT_HOOK_ON_CAST
SPELL_SCRIPT_HOOK_AFTER_CAST

// Effekt-Hooks
SPELL_SCRIPT_HOOK_EFFECT_LAUNCH
SPELL_SCRIPT_HOOK_EFFECT_HIT     // OnEffectHitTarget += SpellEffectFn(...)

// Hit-Hooks
SPELL_SCRIPT_HOOK_BEFORE_HIT     // Mit MissInfo
SPELL_SCRIPT_HOOK_HIT
SPELL_SCRIPT_HOOK_AFTER_HIT
```

## AuraScript-Hooks

```cpp
OnApply / OnRemove                // Aura applied/entfernt
OnEffectApply / OnEffectRemove    // einzelner Effekt
DoEffectCalcAmount                // berechnet Effekt-Stärke
DoEffectCalcPeriodic              // berechnet Periodic-Tick
DoEffectCalcSpellMod
DoCheckProc                       // kann Proc verhindern
OnProc / AfterProc / OnEffectProc // Proc-Handling
```

## Beispiel: SpellScript

```cpp
class spell_custom_paragon_strike : public SpellScript
{
    PrepareSpellScript(spell_custom_paragon_strike);

    void HandleDamage(SpellEffIndex /*effIndex*/)
    {
        Player* caster = GetCaster()->ToPlayer();
        if (!caster)
            return;

        float ap = caster->GetTotalAttackPowerValue(BASE_ATTACK);
        uint32 paragonLevel = caster->GetAuraCount(100000);
        int32 damage = static_cast<int32>((666.0f + ap * 0.66f) *
                       (1.0f + paragonLevel * 0.01f));
        SetHitDamage(damage);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_custom_paragon_strike::HandleDamage,
            EFFECT_0, SPELL_EFFECT_SCHOOL_DAMAGE);
    }
};
```

## Beispiel: AuraScript mit Proc

```cpp
class spell_custom_bloody_whirlwind_passive : public AuraScript
{
    PrepareAuraScript(spell_custom_bloody_whirlwind_passive);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        SpellInfo const* spellInfo = eventInfo.GetSpellInfo();
        if (!spellInfo) return false;
        // Bloodthirst (Warrior, family 4, flags[1]=0x00000400)
        return spellInfo->SpellFamilyName == 4
            && (spellInfo->SpellFamilyFlags[1] & 0x00000400);
    }

    void HandleProc(AuraEffect const* /*aurEff*/, ProcEventInfo& /*eventInfo*/)
    {
        PreventDefaultAction();
        GetTarget()->CastSpell(GetTarget(), 900115, true);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_custom_bloody_whirlwind_passive::CheckProc);
        OnEffectProc += AuraEffectProcFn(spell_custom_bloody_whirlwind_passive::HandleProc,
            EFFECT_1, SPELL_AURA_PROC_TRIGGER_SPELL);
    }
};
```

## Proc-System — vollständige Kette

```
Spell trifft Ziel
  └─ ProcSkillsAndAuras() → TriggerAurasProcOnEvent()
     └─ GetProcAurasTriggeredOnEvent() iteriert ALLE applied Auras
        └─ GetProcEffectMask()
           1. spell_proc Eintrag vorhanden?  (Nein → return 0)
           2. Triggered-Spell Check (SPELL_ATTR3_CAN_PROC_FROM_PROCS)
           3. CanSpellTriggerProcOnEvent()
              ├─ ProcFlags Match (z.B. 0x10 = DONE_SPELL_MELEE_DMG_CLASS)
              ├─ SpellFamilyName/Mask (aus spell_proc, NICHT aus DBC!)
              ├─ SpellTypeMask (DAMAGE=1, HEAL=2, NO_DMG_HEAL=4)
              ├─ SpellPhaseMask (HIT=2, CAST=1, FINISH=4)
              └─ HitMask (Default: NORMAL|CRITICAL|ABSORB)
           4. CallScriptCheckProcHandlers() ← dein CheckProc()
           5. CheckEffectProc() pro Effekt
           6. Chance-Roll (100 = immer)
        └─ TriggerProcOnEvent()
           ├─ CallScriptProcHandlers() ← dein HandleProc() + PreventDefaultAction()
           └─ Default: HandleProcTriggerSpellAuraProc → CastSpell
```

### Wichtig: DBC `EffectSpellClassMask` wird IGNORIERT

Die "Class Mask Target Spells" im WoW Spell Editor (DBC-Feld `EffectSpellClassMask`) hat **keinen** Einfluss auf Procs bei `SPELL_AURA_PROC_TRIGGER_SPELL`. Filterung passiert ausschließlich über die `spell_proc`-Tabelle und C++-Hooks.

### Kritisch: SpellFamilyFlags immer per Debug-Log verifizieren

SpellFamilyFlags in der Server-DBC können von "Standard-WotLK-Werten" abweichen. Niemals Flags aus Online-Quellen (wowhead, wowdb) ungeprüft übernehmen. Diagnose-Pattern:

```cpp
LOG_INFO("module", "CheckProc: spell {} family {} flags[0]=0x{:08X} flags[1]=0x{:08X}",
    spellInfo->Id, spellInfo->SpellFamilyName,
    spellInfo->SpellFamilyFlags[0], spellInfo->SpellFamilyFlags[1]);
```

### `spell_proc`-Tabelle — Pflichtfelder

```sql
INSERT INTO `spell_proc`
  (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`,
   `SpellFamilyMask1`, `SpellFamilyMask2`, `ProcFlags`, `SpellTypeMask`,
   `SpellPhaseMask`, `HitMask`, `AttributesMask`, `DisableEffectsMask`,
   `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`)
VALUES (900116, 0, 0, 0, 0, 0, 0x10, 1, 2, 0, 0, 0, 0, 100, 0, 0);
```

`SpellFamilyName=0` und `SpellFamilyMask*=0` heißt: "alles akzeptieren" — Filterung wird komplett dem C++ `CheckProc` überlassen.

### ProcFlags-Werte (geprüft gegen `SpellMgr.h`)

| Flag | Wert |
|------|------|
| `PROC_FLAG_KILL` | `0x2` |
| `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` | `0x4` |
| `PROC_FLAG_TAKEN_MELEE_AUTO_ATTACK` | `0x8` |
| `PROC_FLAG_DONE_SPELL_MELEE_DMG_CLASS` | `0x10` |
| `PROC_FLAG_DONE_SPELL_RANGED_DMG_CLASS` | `0x40` |
| `PROC_FLAG_DONE_SPELL_NONE_DMG_CLASS_POS` | `0x4000` |
| `PROC_FLAG_DONE_PERIODIC` | `0x40000` |
| `PROC_FLAG_TAKEN_DAMAGE` | `0x100000` |

Quellen: `azerothcore-wotlk/src/server/game/Spells/SpellMgr.h`. Vollständige Tabelle mit Korrekturen siehe `claude_log_2026-04-27_custom_spells_review.md` und `mod-custom-spells/PROCFLAGS_REFERENCE.md`.

### Off-by-One BasePoints

`Spell.dbc` speichert `EffectBasePoints = real_value - 1`. Wer in `spell_dbc` Inserts `BasePoints=50` für "+50%" schreibt, bekommt **+51%** in-game. Entweder konsequent `real_value - 1` ablegen oder Effekte über `DoEffectCalcAmount` zur Laufzeit setzen.

## SpellScript SQL-Registrierung

```sql
DELETE FROM `spell_script_names` WHERE `spell_id` IN (900106);
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
(900106, 'spell_custom_paragon_strike');
```

Für Proc-basierte Spells zusätzlich `spell_proc`-Eintrag (siehe oben).

## DBC-System

DBC = binäre Datendateien aus dem WoW-Client (Spells, Items, Enchants, Maps, etc.). Server liest sie beim Start und kann einige per DB überschreiben.

```
Server-Start
  └─ World::SetInitialWorldSettings()
     └─ LoadDBCStores(dataPath)
        ├─ Liest .dbc-Files (Header + Records + String Block)
        ├─ Befüllt DBCStorage<T>
        └─ Lädt DB-Overrides (z.B. spellitemenchantment_dbc, spell_dbc)
Spell.dbc → sSpellStore → SpellInfo (über SpellMgr)
```

### Wichtige Spell-bezogene DBC-Files

| File | Server-Store | Inhalt |
|------|--------------|--------|
| `Spell.dbc` | `sSpellStore` | Spell-Definitionen (234 Felder) |
| `SpellCastTimes.dbc` | `sSpellCastTimesStore` | Cast-Zeiten |
| `SpellDuration.dbc` | `sSpellDurationStore` | Dauer (Base/PerLevel/Max) |
| `SpellRadius.dbc` | `sSpellRadiusStore` | AoE-Radien |
| `SpellRange.dbc` | `sSpellRangeStore` | Reichweiten |
| `SpellItemEnchantment.dbc` | `sSpellItemEnchantmentStore` | Enchantments (Custom via `spellitemenchantment_dbc`-DB-Override) |
| `SpellDifficulty.dbc` | `sSpellDifficultyStore` | Spell-Varianten je Difficulty |

Komplette DBC-Liste (246 Files) in der alten `CLAUDE.md` Sektion "DBC-Datei-Inventar". Binär — nicht direkt lesen, sondern via Tools (`python_scripts/patch_dbc.py`, `copy_spells_dbc.py`).

### DBC-Override per DB

Beispiel — Custom Stamina-Enchantment für mod-paragon-itemgen:

```sql
INSERT INTO `spellitemenchantment_dbc`
  (`ID`, `Effect_1`, `EffectPointsMin_1`, `EffectArg_1`, `Name_Lang_enUS`)
VALUES (900042, 5, 42, 7, '+42 Stamina');
-- Effect 5 = ITEM_ENCHANTMENT_TYPE_STAT, Arg 7 = ITEM_MOD_STAMINA
```

Damit der Client den Enchantment-Namen im Tooltip zeigt, muss die Client-`SpellItemEnchantment.dbc` ebenfalls gepatched werden (`patch_dbc.py`). Bei mod-paragon-itemgen wird das umgangen, indem der Server die Stat-Werte per AIO direkt an den Client sendet — siehe [04-aio-framework.md](./04-aio-framework.md) und [05-modules.md](./05-modules.md#mod-paragon-itemgen).

## Spell.dbc Korruptions-Checks

Aus historischer Sitzung: `python_scripts/copy_spells_dbc.py` hatte einen Bug, bei dem Records nach Spell-ID in einem dict gespeichert wurden — Duplikate überschrieben sich. Heutiges Skript hat 6 Schutzmaßnahmen:
1. Dateigröße vs. Header-Validierung
2. String-Table Null-Byte-Prüfung
3. Duplikat-Erkennung
4. Format-String vs. Record-Size Konsistenz
5. Source ≠ Target Schutz
6. Post-Write-Verifikation

Wenn `Spell.dbc` jemals "kaputt" wirkt: Backup aus `ac-share/data/dbc/Spell.dbc` zurückspielen, dann via Skript Custom-Spells dazumergen.
