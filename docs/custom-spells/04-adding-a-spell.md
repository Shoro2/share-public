# Custom Spells — Adding a New Spell

Step-by-Step Rezept für einen neuen Custom Spell. Reihenfolge ist wichtig: erst DBC, dann SQL, dann C++, am Ende Build & Test.

## Entscheidungshilfe: DBC-only oder DBC + C++?

### Rein DBC (kein C++ nötig)

Geeignet für passive Modifier, die sich allein über `SPELL_AURA_*`-Effekte ausdrücken lassen.

| Effekt-Typ | DBC Aura | DBC MiscValue | Beispiel |
|------------|----------|---------------|----------|
| Damage ± X % | `ADD_PCT_MODIFIER` (108) | `SPELLMOD_DAMAGE` (0) | MS +50 %, BT +50 % |
| Cooldown ± X s | `ADD_FLAT_MODIFIER` (107) | `SPELLMOD_COOLDOWN` (11) | MS CD −2 s (BasePoints=−2000) |
| Cast-Time ± X % | `ADD_PCT_MODIFIER` (108) | `SPELLMOD_CASTING_TIME` (14) | AB Cast −50 % |
| Unlimited Targets | direkte DBC-Änderung | `MaxAffectedTargets=0` | WW, Cleave |

### C++ erforderlich

| Mechanik | Grund | Beispiel |
|----------|-------|----------|
| Conditional Procs | Crit/Target-Count/CD-Logik | 20 % Crit → Execute |
| Multi-Spell Triggers | ein Proc → mehrere Spells | TC → Rend + 5× Sunder |
| Single → AoE Umbau | Custom Target-Selection | Revenge unlimited |
| Block/Dodge/Parry Procs | HitMask-Filtering | AoE on Block |
| Custom Damage-Formel | Nicht-Standard-Berechnung | Paragon Strike |
| Runtime CD-Manipulation | dynamisches `ModifySpellCooldown` | Bladestorm CD −0.5 s |

## Schritt 1 — ID reservieren

- Nächste freie ID im Spec-Block wählen (siehe [`02-id-blocks.md`](./02-id-blocks.md) und das Spec-File).
- Im Spec-File die Tabelle erweitern, Status `WIP`.
- Falls die Spec-Range voll ist: ins File `02-id-blocks.md` die Erweiterung dokumentieren.

## Schritt 2 — DBC-Eintrag (`spell_dbc`)

Die `spell_dbc`-Tabelle überschreibt beim Server-Start die Werte aus `Spell.dbc`. Beispiel für eine passive Marker-Aura:

```sql
DELETE FROM `spell_dbc` WHERE `ID` = 900168;
INSERT INTO `spell_dbc` (`ID`, `Attributes`, `AttributesEx3`,
    `CastingTimeIndex`, `DurationIndex`, `RangeIndex`,
    `Effect_1`, `EffectBasePoints_1`, `ImplicitTargetA_1`,
    `EffectAura_1`, `EffectMiscValue_1`,
    `EffectSpellClassMaskA_1`,
    `SpellFamilyName`, `SpellIconID`,
    `Name_Lang_enUS`, `Name_Lang_Mask`)
VALUES
(900168,
 0x10000040,                 -- Attributes: PASSIVE | NOT_SHAPESHIFT
 0x10000000,                 -- AttributesEx3: DEATH_PERSISTENT
 1,                          -- CastingTimeIndex: Instant
 21,                         -- DurationIndex: Permanent
 1,                          -- RangeIndex: Self
 6,                          -- Effect: APPLY_AURA
 50,                         -- BasePoints (real-1 — ergibt +51%! siehe unten)
 1,                          -- ImplicitTargetA: TARGET_UNIT_CASTER
 108,                        -- EffectAura: ADD_PCT_MODIFIER
 0,                          -- EffectMiscValue: SPELLMOD_DAMAGE
 0x400,                      -- EffectSpellClassMaskA: Ziel-Spell FamilyFlags[0]
 4,                          -- SpellFamilyName: Warrior
 132,                        -- SpellIconID
 'Prot: Revenge Damage',
 0x003F3F);                  -- Name_Lang_Mask: alle Locales → enUS
```

**Off-by-One BasePoints**: `Spell.dbc` speichert `EffectBasePoints = real_value - 1`. Für +50 % also `49` ablegen, nicht `50`. Detail: [`03-procs-and-flags.md`](./03-procs-and-flags.md#off-by-one-basepoints).

Wichtigste Attribute:

| Attribut | Hex | Bedeutung |
|----------|-----|-----------|
| `SPELL_ATTR0_PASSIVE` | `0x40` | Spell unsichtbar, immer aktiv |
| `SPELL_ATTR0_NOT_SHAPESHIFT` | `0x10000000` | Bleibt in allen Stances |
| `SPELL_ATTR3_DEATH_PERSISTENT` | `0x10000000` | Überlebt Tod |

Häufige `EffectAura`-Werte:

| Aura | Name | Anwendung |
|------|------|-----------|
| 4 | `DUMMY` | Marker-Aura (HasAura-Check in C++) |
| 42 | `PROC_TRIGGER_SPELL` | Triggert Spell bei Proc |
| 107 | `ADD_FLAT_MODIFIER` | Spell-Modifier flat |
| 108 | `ADD_PCT_MODIFIER` | Spell-Modifier prozentual |

## Schritt 3 — `spell_proc` (nur bei Procs)

Wenn Schritt 2 eine Proc-Aura war, jetzt den Proc-Eintrag dazu. Vollständiges Template + ProcFlags-Tabelle: [`03-procs-and-flags.md`](./03-procs-and-flags.md).

```sql
DELETE FROM `spell_proc` WHERE `SpellId` = 900172;
INSERT INTO `spell_proc` (...)
VALUES (900172, 0, 0, 0, 0, 0, 0x8, 0, 0, 0, 0, 0, 0, 100, 1000, 0);
```

## Schritt 4 — Enum-Konstante

In `src/custom_spells_<class>.cpp` (oder `custom_spells_common.h`) eine sprechende Konstante für die ID anlegen:

```cpp
enum CustomProtSpells
{
    SPELL_PROT_REVENGE_AOE_PASSIVE = 900169,
    SPELL_PROT_BLOCK_AOE           = 900172,
    HELPER_BLOCK_SHIELD_BURST      = 900174,
};
```

## Schritt 5 — SpellScript / AuraScript

Vier Patterns (siehe Architektur-Doku [`01-architecture.md`](./01-architecture.md#drei-hook-strategien) für die High-Level-Strategien):

**Pattern A — SpellScript-Hook auf Blizzard-Spell mit AfterHit:**

```cpp
class spell_custom_prot_revenge_aoe : public SpellScript
{
    PrepareSpellScript(spell_custom_prot_revenge_aoe);

    void HandleAfterHit()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !player->HasAura(SPELL_PROT_REVENGE_AOE_PASSIVE))
            return;
        if (!sConfigMgr->GetOption<bool>("CustomSpells.Enable", true))
            return;

        Unit* target = GetHitUnit();
        if (target)
            player->CastSpell(target, HELPER_BLOCK_SHIELD_BURST, true);
    }

    void Register() override
    {
        AfterHit += SpellHitFn(spell_custom_prot_revenge_aoe::HandleAfterHit);
    }
};
```

**Pattern B — AuraScript mit Proc + HitMask-Filter:**

```cpp
class spell_custom_prot_block_aoe : public AuraScript
{
    PrepareAuraScript(spell_custom_prot_block_aoe);

    void HandleProc(AuraEffect const* /*aurEff*/, ProcEventInfo& eventInfo)
    {
        PreventDefaultAction();
        if (!(eventInfo.GetHitMask() & PROC_HIT_BLOCK))
            return;

        Player* player = GetTarget()->ToPlayer();
        if (!player) return;
        player->CastSpell(player, HELPER_BLOCK_SHIELD_BURST, true);
    }

    void Register() override
    {
        OnEffectProc += AuraEffectProcFn(
            spell_custom_prot_block_aoe::HandleProc,
            EFFECT_0, SPELL_AURA_DUMMY);
    }
};
```

**Pattern C — AuraScript mit CheckProc:** siehe [`docs/03-spell-system.md`](../03-spell-system.md#beispiel-aurascript-mit-proc) (Bloody Whirlwind Beispiel).

**Pattern D — SpellScript mit OnEffectHitTarget (Damage-Override):**

```cpp
class spell_custom_paragon_strike : public SpellScript
{
    PrepareSpellScript(spell_custom_paragon_strike);

    void HandleDamage(SpellEffIndex /*effIndex*/)
    {
        Player* caster = GetCaster()->ToPlayer();
        if (!caster) return;
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

## Schritt 6 — Script registrieren

In der `AddCustomSpells<Class>Scripts()`-Funktion (oder `AddCustomSpellsGlobalScripts()`):

```cpp
void AddCustomSpellsProtScripts()
{
    RegisterSpellScript(spell_custom_prot_revenge_aoe);
    RegisterSpellScript(spell_custom_prot_block_aoe);
}
```

## Schritt 7 — `spell_script_names`-SQL

```sql
-- Eigene Custom-ID:
DELETE FROM `spell_script_names` WHERE `spell_id` = 900172;
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
  (900172, 'spell_custom_prot_block_aoe');

-- Hook auf Blizzard-Spell (Revenge 57823):
DELETE FROM `spell_script_names`
WHERE `spell_id` = 57823 AND `ScriptName` = 'spell_custom_prot_revenge_aoe';
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
  (57823, 'spell_custom_prot_revenge_aoe');
```

> Bei Hooks auf Blizzard-Spells: die C++-Klasse läuft bei **jedem** Cast dieses Spells. Immer `HasAura()` auf einen Marker prüfen.

## Schritt 8 — Client-DBC patchen (nur für sichtbare Spells)

`python_scripts/copy_spells_dbc.py` und `patch_dbc.py` in `share-public`. Marker-Auras und Helper-Spells brauchen keinen Client-Patch.

## Schritt 9 — Build & Test

```bash
cd azerothcore-wotlk/build
make -j$(nproc) && make install
```

Server starten, SQL einspielen, in-game testen. Debug-Log für Procs:

```cpp
LOG_INFO("module", "Proc {} on spell {} (family {} flags[0]=0x{:08X})",
    GetSpellInfo()->Id, eventInfo.GetSpellInfo()->Id,
    eventInfo.GetSpellInfo()->SpellFamilyName,
    eventInfo.GetSpellInfo()->SpellFamilyFlags[0]);
```

## Schritt 10 — Doku updaten

Im Spec-File: Status der Spell-Zeile von `WIP` auf `Live`. Implementation Notes ergänzen, falls der Spell nicht-trivial ist (Proc-Setup, Formel, Edge Cases).

## Checkliste

```
□ ID reserviert + im Spec-File als WIP eingetragen
□ spell_dbc INSERT (BasePoints = real_value - 1!)
□ spell_proc INSERT (nur bei Procs, ProcFlags via Debug-Log verifiziert)
□ Enum-Konstante in custom_spells_<class>.cpp
□ SpellScript / AuraScript Klasse implementiert
□ RegisterSpellScript() in AddCustomSpells<Class>Scripts()
□ spell_script_names INSERT
□ (wenn Helper) Helper-Spell DBC + ggf. C++ Script
□ (wenn sichtbar) Client-Spell.dbc gepatcht
□ Build erfolgreich (0 Errors)
□ In-Game getestet
□ Spec-File: Status auf Live, ggf. Implementation Notes
```
