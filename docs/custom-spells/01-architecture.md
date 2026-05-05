# Custom Spells — Architecture

## Repo layout (`mod-custom-spells/`)

```
src/
  mod_custom_spells_loader.cpp   — Module entry, Addmod_custom_spellsScripts()
  custom_spells.cpp              — Master switch (PlayerScript OnPlayerSpellCast)
  custom_spells_common.h         — Shared includes/constants/enums
  custom_spells_global.cpp       — Non-class spells (901100–901199)
  custom_spells_<class>.cpp      — One per class: warrior, paladin, dk, shaman,
                                   hunter, rogue, druid, mage, warlock, priest
conf/
  mod_custom_spells.conf.dist    — CustomSpells.Enable
data/sql/db-world/
  mod_custom_spells.sql          — spell_dbc, spell_script_names, spell_proc
```

The loader function name follows the AzerothCore convention: module folder name with `-` replaced by `_`, i.e. `Addmod_custom_spellsScripts()`. The core finds it automatically during static linking.

## Three hook strategies

For every new spell there are three ways to wire up the desired behavior. Which one fits depends on whether the effect needs its own spell cast or hooks into a Blizzard spell.

### Strategy 1 — Custom spells (own ID + SpellScript)

Custom 900xxx ID, DBC entry in `spell_dbc`, C++ class inheriting from `SpellScript`. Linked via `spell_script_names`. The spell is cast explicitly by the player (or triggered via `CastSpell`).

Examples: Paragon Strike (900106), Bloody Whirlwind buff (900115).

### Strategy 2 — Hook on Blizzard spells

The C++ class hooks via `spell_script_names` onto an existing ID (e.g. 1680 Whirlwind, 23881 Bloodthirst, 57823 Revenge, 47502 Thunderclap). It runs on **every** cast of that spell — therefore required: a `HasAura()` check on a marker spell that is only active for players with the desired mechanic.

```cpp
void HandleAfterHit()
{
    Player* player = GetCaster()->ToPlayer();
    if (!player || !player->HasAura(SPELL_PROT_REVENGE_AOE_PASSIVE))
        return;
    // Custom logic only for players with the marker aura
}
```

Examples: `spell_custom_prot_revenge_aoe` hooks on Revenge, checks the marker 900169.

### Strategy 3 — AuraScript with proc

Passive aura (DBC effect `SPELL_AURA_PROC_TRIGGER_SPELL` or `SPELL_AURA_DUMMY`) is armed via `spell_proc`. On the trigger event the engine first calls `CheckProc()` (filter), then `HandleProc()` with `PreventDefaultAction()` and a custom cast.

Important: **DBC `EffectSpellClassMask` is ignored** — filtering runs exclusively through `spell_proc` + a C++ `CheckProc`. Detail in [`03-procs-and-flags.md`](./03-procs-and-flags.md).

## OnPlayerSpellCast master switch

`custom_spells.cpp` contains a PlayerScript hook on `OnPlayerSpellCast` that reacts via a `switch` to specific custom spell IDs (e.g. for spells that should only trigger a simple side effect without needing an own SpellScript). For more complex cases prefer strategies 1–3.

## Loader order

`Addmod_custom_spellsScripts()` calls all `AddCustomSpells<Class>Scripts()` functions (one per class file) plus `AddCustomSpellsGlobalScripts()`. Order is not critical — all registrations end up in the manager maps of `SpellMgr` / `ScriptMgr`.

## DBC maintenance

Every custom spell needs an entry in `spell_dbc` (DB override for `Spell.dbc`). The server loads `Spell.dbc` first at start, then layers the `spell_dbc` table over it. Tooltips in the client however access the client `Spell.dbc` directly — therefore visible spells must additionally be patched into the client DBC (`python_scripts/patch_dbc.py` in `share-public`).

Mind the off-by-one BasePoints: `Spell.dbc` stores `EffectBasePoints = real_value - 1`. Detail in [`docs/03-spell-system.md`](../03-spell-system.md#off-by-one-basepoints).

## Build / install

```bash
cd azerothcore-wotlk/modules
git clone <repo-url> mod-custom-spells
cd ../build && cmake .. -DSCRIPTS=static -DMODULES=static && make -j$(nproc) && make install
```

Apply SQL from `data/sql/db-world/` to `acore_world`. Config:

```bash
cp etc/mod_custom_spells.conf.dist etc/mod_custom_spells.conf
```

## Configuration

| Option | Default | Purpose |
|--------|---------|-------|
| `CustomSpells.Enable` | `1` | module enabled (1) / disabled (0) |

All SpellScripts check `sConfigMgr->GetOption<bool>("CustomSpells.Enable", true)` as the first step so the module can be hard-disabled at runtime.

## Cross references

- [`02-id-blocks.md`](./02-id-blocks.md) — ID scheme and allocation per spec
- [`03-procs-and-flags.md`](./03-procs-and-flags.md) — spell_proc, ProcFlags, SpellFamilyFlags
- [`04-adding-a-spell.md`](./04-adding-a-spell.md) — step-by-step for new spells
- [`docs/03-spell-system.md`](../03-spell-system.md) — SpellScript/AuraScript class hierarchy + proc pipeline
