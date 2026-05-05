# 03 — Spell system: SpellScripts, AuraScripts, procs, DBC

## SpellScript / AuraScript — class hierarchy

```
_SpellScript (abstract base)
├── SpellScript   → spell effects and cast lifecycle
└── AuraScript    → aura/buff/debuff mechanics
```

Lifecycle:
1. **Registration** via `RegisterSpellScript(ClassName)` in an `AddSC_*()` function
2. **Validate(SpellInfo*)** checks DBC data on server start (optional)
3. **Load()** — called on instance creation
4. **Register()** override — binds handlers to spell events
5. **Execute** — handlers are called on events

## SpellScript hooks

```cpp
// Cast lifecycle
SPELL_SCRIPT_HOOK_CHECK_CAST     // Before cast: can block
SPELL_SCRIPT_HOOK_BEFORE_CAST
SPELL_SCRIPT_HOOK_ON_CAST
SPELL_SCRIPT_HOOK_AFTER_CAST

// Effect hooks
SPELL_SCRIPT_HOOK_EFFECT_LAUNCH
SPELL_SCRIPT_HOOK_EFFECT_HIT     // OnEffectHitTarget += SpellEffectFn(...)

// Hit hooks
SPELL_SCRIPT_HOOK_BEFORE_HIT     // With MissInfo
SPELL_SCRIPT_HOOK_HIT
SPELL_SCRIPT_HOOK_AFTER_HIT
```

## AuraScript hooks

```cpp
OnApply / OnRemove                // aura applied/removed
OnEffectApply / OnEffectRemove    // single effect
DoEffectCalcAmount                // calculates effect strength
DoEffectCalcPeriodic              // calculates periodic tick
DoEffectCalcSpellMod
DoCheckProc                       // can prevent the proc
OnProc / AfterProc / OnEffectProc // proc handling
```

## Example: SpellScript

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

## Example: AuraScript with proc

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

## Proc system — full chain

```
Spell hits target
  └─ ProcSkillsAndAuras() → TriggerAurasProcOnEvent()
     └─ GetProcAurasTriggeredOnEvent() iterates ALL applied auras
        └─ GetProcEffectMask()
           1. spell_proc entry present?  (No → return 0)
           2. Triggered-spell check (SPELL_ATTR3_CAN_PROC_FROM_PROCS)
           3. CanSpellTriggerProcOnEvent()
              ├─ ProcFlags match (e.g. 0x10 = DONE_SPELL_MELEE_DMG_CLASS)
              ├─ SpellFamilyName/Mask (from spell_proc, NOT from DBC!)
              ├─ SpellTypeMask (DAMAGE=1, HEAL=2, NO_DMG_HEAL=4)
              ├─ SpellPhaseMask (HIT=2, CAST=1, FINISH=4)
              └─ HitMask (default: NORMAL|CRITICAL|ABSORB)
           4. CallScriptCheckProcHandlers() ← your CheckProc()
           5. CheckEffectProc() per effect
           6. Chance roll (100 = always)
        └─ TriggerProcOnEvent()
           ├─ CallScriptProcHandlers() ← your HandleProc() + PreventDefaultAction()
           └─ Default: HandleProcTriggerSpellAuraProc → CastSpell
```

### Important: DBC `EffectSpellClassMask` is IGNORED

The "Class Mask Target Spells" in the WoW Spell Editor (DBC field `EffectSpellClassMask`) has **no** effect on procs from `SPELL_AURA_PROC_TRIGGER_SPELL`. Filtering happens exclusively through the `spell_proc` table and C++ hooks.

### Critical: always verify SpellFamilyFlags via debug log

SpellFamilyFlags in the server DBC may differ from "standard WotLK values". Never blindly take flags from online sources (wowhead, wowdb). Diagnostic pattern:

```cpp
LOG_INFO("module", "CheckProc: spell {} family {} flags[0]=0x{:08X} flags[1]=0x{:08X}",
    spellInfo->Id, spellInfo->SpellFamilyName,
    spellInfo->SpellFamilyFlags[0], spellInfo->SpellFamilyFlags[1]);
```

### `spell_proc` table — required fields

```sql
INSERT INTO `spell_proc`
  (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`,
   `SpellFamilyMask1`, `SpellFamilyMask2`, `ProcFlags`, `SpellTypeMask`,
   `SpellPhaseMask`, `HitMask`, `AttributesMask`, `DisableEffectsMask`,
   `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`)
VALUES (900116, 0, 0, 0, 0, 0, 0x10, 1, 2, 0, 0, 0, 0, 100, 0, 0);
```

`SpellFamilyName=0` and `SpellFamilyMask*=0` means: "accept everything" — filtering is left entirely to the C++ `CheckProc`.

### ProcFlags values (verified against `SpellMgr.h`)

| Flag | Value |
|------|------|
| `PROC_FLAG_KILL` | `0x2` |
| `PROC_FLAG_DONE_MELEE_AUTO_ATTACK` | `0x4` |
| `PROC_FLAG_TAKEN_MELEE_AUTO_ATTACK` | `0x8` |
| `PROC_FLAG_DONE_SPELL_MELEE_DMG_CLASS` | `0x10` |
| `PROC_FLAG_DONE_SPELL_RANGED_DMG_CLASS` | `0x40` |
| `PROC_FLAG_DONE_SPELL_NONE_DMG_CLASS_POS` | `0x4000` |
| `PROC_FLAG_DONE_PERIODIC` | `0x40000` |
| `PROC_FLAG_TAKEN_DAMAGE` | `0x100000` |

Sources: `azerothcore-wotlk/src/server/game/Spells/SpellMgr.h`.

> **Full table** of all ProcFlags + common combinations + documented bug fixes: [`custom-spells/03-procs-and-flags.md`](./custom-spells/03-procs-and-flags.md). Historical context: `claude_log_2026-04-27_custom_spells_review.md`.

### Off-by-one BasePoints

`Spell.dbc` stores `EffectBasePoints = real_value - 1`. Anyone writing `BasePoints=50` for "+50%" in a `spell_dbc` insert will get **+51%** in-game. Either consistently store `real_value - 1` or set effects at runtime via `DoEffectCalcAmount`.

## SpellScript SQL registration

```sql
DELETE FROM `spell_script_names` WHERE `spell_id` IN (900106);
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
(900106, 'spell_custom_paragon_strike');
```

For proc-based spells, additionally a `spell_proc` entry (see above).

## DBC system

DBC = binary data files from the WoW client (spells, items, enchants, maps, etc.). The server reads them at start and can override some via DB.

```
Server start
  └─ World::SetInitialWorldSettings()
     └─ LoadDBCStores(dataPath)
        ├─ reads .dbc files (header + records + string block)
        ├─ populates DBCStorage<T>
        └─ loads DB overrides (e.g. spellitemenchantment_dbc, spell_dbc)
Spell.dbc → sSpellStore → SpellInfo (via SpellMgr)
```

### Important spell-related DBC files

| File | Server store | Contents |
|------|--------------|--------|
| `Spell.dbc` | `sSpellStore` | spell definitions (234 fields) |
| `SpellCastTimes.dbc` | `sSpellCastTimesStore` | cast times |
| `SpellDuration.dbc` | `sSpellDurationStore` | duration (base/per level/max) |
| `SpellRadius.dbc` | `sSpellRadiusStore` | AoE radii |
| `SpellRange.dbc` | `sSpellRangeStore` | ranges |
| `SpellItemEnchantment.dbc` | `sSpellItemEnchantmentStore` | enchantments (custom via `spellitemenchantment_dbc` DB override) |
| `SpellDifficulty.dbc` | `sSpellDifficultyStore` | spell variants per difficulty |

Full DBC list (246 files) in the legacy `CLAUDE.md` section "DBC file inventory". Binary — do not read directly, use the tools (`python_scripts/patch_dbc.py`, `copy_spells_dbc.py`).

### `spell_dbc` column reference (most relevant fields)

The `spell_dbc` table has 257 columns — it mirrors `Spell.dbc`. The fields below are the ones that come up most often when authoring a custom spell or override:

| Column | Type | Description |
|--------|-----|-------------|
| `ID` | uint | Unique spell ID |
| `Attributes` | uint | Flags: `0x40`=PASSIVE, `0x10000000`=NOT_SHAPESHIFT |
| `AttributesEx` | uint | Extended flags 1 |
| `AttributesEx2` | uint | Extended flags 2 |
| `AttributesEx3` | uint | Extended flags 3 (`0x10000000`=DEATH_PERSISTENT) |
| `CastingTimeIndex` | uint | 1=instant, other values → `SpellCastTimes.dbc` |
| `DurationIndex` | uint | 0=instant, 21=permanent, other → `SpellDuration.dbc` |
| `RangeIndex` | uint | 1=self, 4=30yd, 6=100yd → `SpellRange.dbc` |
| `ProcTypeMask` | uint | Proc trigger flags (overridden by `spell_proc`) |
| `ProcChance` | uint | Proc chance (overridden by `spell_proc`) |
| `Effect_1/2/3` | uint | 2=SCHOOL_DAMAGE, 6=APPLY_AURA, 3=DUMMY |
| `EffectDieSides_1/2/3` | int | Random range for damage (0=no random) |
| `EffectBasePoints_1/2/3` | int | Base value (damage, modifier %, etc.) — see off-by-one below |
| `ImplicitTargetA_1/2/3` | uint | 1=SELF, 6=ENEMY, 22=SRC_AREA_ENEMY |
| `EffectRadiusIndex_1/2/3` | uint | 8=5yd, 13=8yd, 14=10yd, 28=30yd |
| `EffectAura_1/2/3` | uint | Aura type: 4=DUMMY, 108=ADD_PCT_MODIFIER |
| `EffectMiscValue_1/2/3` | int | Aura specific: 0=SPELLMOD_DAMAGE, 11=SPELLMOD_COOLDOWN |
| `EffectTriggerSpell_1/2/3` | uint | Spell ID triggered on proc |
| `EffectSpellClassMaskA/B/C_1` | uint | SpellFamilyFlags[0/1/2] of the **target** spell |
| `SpellFamilyName` | uint | 0=Generic, 4=Warrior, 10=Paladin, 15=DK |
| `SpellClassMask_1/2/3` | uint | SpellFamilyFlags of **this** spell (for proc matching) |
| `SpellIconID` | uint | Icon ID from `SpellIcon.dbc` |
| `MaxTargets` | uint | Max targets (0=unlimited) |
| `SchoolMask` | uint | 1=Physical, 2=Holy, 4=Fire, 16=Shadow, 32=Arcane |
| `Name_Lang_enUS` | string | Spell name (English) |
| `Name_Lang_Mask` | uint | `0x003F3F` = all locales use enUS |

#### Common `EffectAura` values

| Aura ID | Name | MiscValue | Use |
|---------|------|-----------|-----------|
| 4 | `DUMMY` | — | Marker aura (C++ checks via `HasAura`) |
| 42 | `PROC_TRIGGER_SPELL` | — | Triggers another spell on proc |
| 107 | `ADD_FLAT_MODIFIER` | 0=DAMAGE, 11=COOLDOWN | Flat spell modifier |
| 108 | `ADD_PCT_MODIFIER` | 0=DAMAGE, 11=COOLDOWN, 14=CAST_TIME | Percent spell modifier |

#### Identifying the target spell via `EffectSpellClassMask`

The mask must match the `SpellFamilyFlags` of the target spell. Three 32-bit fields, one per family-flag word:

- `EffectSpellClassMaskA_1` → `SpellFamilyFlags[0]`
- `EffectSpellClassMaskB_1` → `SpellFamilyFlags[1]`
- `EffectSpellClassMaskC_1` → `SpellFamilyFlags[2]`

> **Always verify `SpellFamilyFlags` against your own `Spell.dbc`**, not against online DBs. See the diagnostic LOG_INFO pattern under "Critical: always verify SpellFamilyFlags via debug log" above.

### DBC override via DB

Example — custom Stamina enchantment for mod-paragon-itemgen:

```sql
INSERT INTO `spellitemenchantment_dbc`
  (`ID`, `Effect_1`, `EffectPointsMin_1`, `EffectArg_1`, `Name_Lang_enUS`)
VALUES (900042, 5, 42, 7, '+42 Stamina');
-- Effect 5 = ITEM_ENCHANTMENT_TYPE_STAT, Arg 7 = ITEM_MOD_STAMINA
```

For the client to show the enchantment name in the tooltip, the client `SpellItemEnchantment.dbc` must also be patched (`patch_dbc.py`). With mod-paragon-itemgen this is bypassed by having the server send stat values directly to the client via AIO — see [04-aio-framework.md](./04-aio-framework.md) and [05-modules.md](./05-modules.md#mod-paragon-itemgen).

## Spell.dbc corruption checks

From a historical session: `python_scripts/copy_spells_dbc.py` had a bug where records were stored in a dict keyed by spell ID — duplicates overwrote each other. Today's script has 6 safeguards:
1. file size vs. header validation
2. string-table null-byte check
3. duplicate detection
4. format string vs. record size consistency
5. source ≠ target protection
6. post-write verification

If `Spell.dbc` ever appears "broken": restore the backup from `ac-share/data/dbc/Spell.dbc`, then re-merge custom spells via the script.
