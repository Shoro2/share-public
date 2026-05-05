# Custom Spells — Adding a new spell

Step-by-step recipe for a new custom spell. Order matters: DBC first, then SQL, then C++, build & test at the end.

## Decision aid: DBC-only or DBC + C++?

### Pure DBC (no C++ needed)

Suitable for passive modifiers expressible solely through `SPELL_AURA_*` effects.

| Effect type | DBC aura | DBC MiscValue | Example |
|------------|----------|---------------|----------|
| Damage ± X % | `ADD_PCT_MODIFIER` (108) | `SPELLMOD_DAMAGE` (0) | MS +50 %, BT +50 % |
| Cooldown ± X s | `ADD_FLAT_MODIFIER` (107) | `SPELLMOD_COOLDOWN` (11) | MS CD −2 s (BasePoints=−2000) |
| Cast time ± X % | `ADD_PCT_MODIFIER` (108) | `SPELLMOD_CASTING_TIME` (14) | AB cast −50 % |
| Unlimited targets | direct DBC change | `MaxAffectedTargets=0` | WW, Cleave |

### C++ required

| Mechanic | Reason | Example |
|----------|-------|----------|
| Conditional procs | crit/target-count/CD logic | 20 % crit → Execute |
| Multi-spell triggers | one proc → multiple spells | TC → Rend + 5× Sunder |
| Single → AoE conversion | custom target selection | Revenge unlimited |
| Block/dodge/parry procs | HitMask filtering | AoE on block |
| Custom damage formula | non-standard calculation | Paragon Strike |
| Runtime CD manipulation | dynamic `ModifySpellCooldown` | Bladestorm CD −0.5 s |

## Step 1 — reserve an ID

- Pick the next free ID in the spec block (see [`02-id-blocks.md`](./02-id-blocks.md) and the spec file).
- Extend the table in the spec file, status `WIP`.
- If the spec range is full: document the extension in `02-id-blocks.md`.

## Step 2 — DBC entry (`spell_dbc`)

The `spell_dbc` table overrides values from `Spell.dbc` at server start. Example for a passive marker aura:

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
 1,                          -- CastingTimeIndex: instant
 21,                         -- DurationIndex: permanent
 1,                          -- RangeIndex: self
 6,                          -- Effect: APPLY_AURA
 50,                         -- BasePoints (real-1 — yields +51%! see below)
 1,                          -- ImplicitTargetA: TARGET_UNIT_CASTER
 108,                        -- EffectAura: ADD_PCT_MODIFIER
 0,                          -- EffectMiscValue: SPELLMOD_DAMAGE
 0x400,                      -- EffectSpellClassMaskA: target spell FamilyFlags[0]
 4,                          -- SpellFamilyName: Warrior
 132,                        -- SpellIconID
 'Prot: Revenge Damage',
 0x003F3F);                  -- Name_Lang_Mask: all locales → enUS
```

**Off-by-one BasePoints**: `Spell.dbc` stores `EffectBasePoints = real_value - 1`. So for +50 % store `49`, not `50`. Detail: [`03-procs-and-flags.md`](./03-procs-and-flags.md#off-by-one-basepoints).

Most important attributes:

| Attribute | Hex | Meaning |
|----------|-----|-----------|
| `SPELL_ATTR0_PASSIVE` | `0x40` | spell invisible, always active |
| `SPELL_ATTR0_NOT_SHAPESHIFT` | `0x10000000` | stays in all stances |
| `SPELL_ATTR3_DEATH_PERSISTENT` | `0x10000000` | survives death |

Common `EffectAura` values:

| Aura | Name | Use |
|------|------|-----------|
| 4 | `DUMMY` | marker aura (HasAura check in C++) |
| 42 | `PROC_TRIGGER_SPELL` | triggers a spell on proc |
| 107 | `ADD_FLAT_MODIFIER` | flat spell modifier |
| 108 | `ADD_PCT_MODIFIER` | percent spell modifier |

## Step 3 — `spell_proc` (only for procs)

If step 2 was a proc aura, add the proc entry now. Full template + ProcFlags table: [`03-procs-and-flags.md`](./03-procs-and-flags.md).

```sql
DELETE FROM `spell_proc` WHERE `SpellId` = 900172;
INSERT INTO `spell_proc` (...)
VALUES (900172, 0, 0, 0, 0, 0, 0x8, 0, 0, 0, 0, 0, 0, 100, 1000, 0);
```

## Step 4 — enum constant

In `src/custom_spells_<class>.cpp` (or `custom_spells_common.h`) add a speaking constant for the ID:

```cpp
enum CustomProtSpells
{
    SPELL_PROT_REVENGE_AOE_PASSIVE = 900169,
    SPELL_PROT_BLOCK_AOE           = 900172,
    HELPER_BLOCK_SHIELD_BURST      = 900174,
};
```

## Step 5 — SpellScript / AuraScript

Four patterns (see the architecture doc [`01-architecture.md`](./01-architecture.md#three-hook-strategies) for the high-level strategies):

**Pattern A — SpellScript hook on a Blizzard spell with AfterHit:**

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

**Pattern B — AuraScript with proc + HitMask filter:**

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

**Pattern C — AuraScript with CheckProc:** see [`docs/03-spell-system.md`](../03-spell-system.md#example-aurascript-with-proc) (Bloody Whirlwind example).

**Pattern D — SpellScript with OnEffectHitTarget (damage override):**

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

## Step 6 — register the script

In the `AddCustomSpells<Class>Scripts()` function (or `AddCustomSpellsGlobalScripts()`):

```cpp
void AddCustomSpellsProtScripts()
{
    RegisterSpellScript(spell_custom_prot_revenge_aoe);
    RegisterSpellScript(spell_custom_prot_block_aoe);
}
```

## Step 7 — `spell_script_names` SQL

```sql
-- Custom ID:
DELETE FROM `spell_script_names` WHERE `spell_id` = 900172;
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
  (900172, 'spell_custom_prot_block_aoe');

-- Hook on a Blizzard spell (Revenge 57823):
DELETE FROM `spell_script_names`
WHERE `spell_id` = 57823 AND `ScriptName` = 'spell_custom_prot_revenge_aoe';
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
  (57823, 'spell_custom_prot_revenge_aoe');
```

> When hooking on Blizzard spells: the C++ class runs on **every** cast of that spell. Always check `HasAura()` against a marker.

## Step 8 — patch the client DBC (only for visible spells)

`python_scripts/copy_spells_dbc.py` and `patch_dbc.py` in `share-public`. Marker auras and helper spells need no client patch.

## Step 9 — build & test

```bash
cd azerothcore-wotlk/build
make -j$(nproc) && make install
```

Start the server, apply the SQL, test in-game. Debug log for procs:

```cpp
LOG_INFO("module", "Proc {} on spell {} (family {} flags[0]=0x{:08X})",
    GetSpellInfo()->Id, eventInfo.GetSpellInfo()->Id,
    eventInfo.GetSpellInfo()->SpellFamilyName,
    eventInfo.GetSpellInfo()->SpellFamilyFlags[0]);
```

## Step 10 — update docs

In the spec file: change the spell row's status from `WIP` to `Live`. Add implementation notes if the spell is non-trivial (proc setup, formula, edge cases).

## Checklist

```
□ ID reserved + listed as WIP in the spec file
□ spell_dbc INSERT (BasePoints = real_value - 1!)
□ spell_proc INSERT (only on procs, ProcFlags verified via debug log)
□ Enum constant in custom_spells_<class>.cpp
□ SpellScript / AuraScript class implemented
□ RegisterSpellScript() in AddCustomSpells<Class>Scripts()
□ spell_script_names INSERT
□ (if helper) helper spell DBC + optional C++ script
□ (if visible) client Spell.dbc patched
□ Build succeeds (0 errors)
□ Tested in-game
□ Spec file: status to Live, optional implementation notes
```
