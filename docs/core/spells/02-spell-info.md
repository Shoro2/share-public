# spells — SpellInfo & SpellMgr

> Compiled, denormalized representation of a `SpellEntry` DBC row, used by the engine in place of raw `SpellEntry`. Built once at server start by `SpellMgr::LoadSpellInfoStore`. Cross-link [`../dbc/04-structures.md`](../dbc/04-structures.md) (raw `SpellEntry`), [`01-cast-lifecycle.md`](./01-cast-lifecycle.md) (consumer), [`05-effects.md`](./05-effects.md) (per-effect data).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/SpellInfo.h:32` | `class SpellInfo;` forward |
| `src/server/game/Spells/SpellInfo.h` | `class SpellInfo` — full definition; ~190 fields mapped to `SpellEntry` columns + computed |
| `src/server/game/Spells/SpellInfo.h:304` | `bool IsAura()` / `bool IsAura(AuraType)` |
| `src/server/game/Spells/SpellInfo.h:468` | `bool IsPassive()` |
| `src/server/game/Spells/SpellInfo.h:479` | `bool IsPassiveStackableWithRanks()` |
| `src/server/game/Spells/SpellInfo.h:509` | `bool IsAuraExclusiveBySpecificWith(other)` |
| `src/server/game/Spells/SpellInfo.h:518` | `bool IsAuraEffectEqual(other)` — used by stack/refresh logic |
| `src/server/game/Spells/SpellInfo.cpp` | implementations of `Calc*Bonus`, `CalcArmorPenetrationPct`, `GetEffectMechanic`, `GetSchoolMask`, `GetMaxRange`, `GetMinRange` etc. |
| `src/server/game/Spells/SpellMgr.h:641` | `class SpellMgr` (singleton via `sSpellMgr`) — owns `SpellInfoStore`, `SpellChainStore`, `SpellLearnSkillStore`, proc tables |
| `src/server/game/Spells/SpellMgr.cpp:2903` | `SpellMgr::LoadSpellInfoStore()` — iterates `sSpellStore` (DBC), constructs `SpellInfo` per row, applies `LoadSpellInfoCorrections`/`LoadSpellInfoCustomAttributes`/`LoadSpellInfoSpellSpecificAndAuraState` overlays |
| `src/server/game/Spells/SpellMgr.cpp:1423` | `LoadSpellLearnSkills` |
| `src/server/game/Spells/SpellMgr.cpp:1476` | `LoadSpellTargetPositions` (`spell_target_position` table) |
| `src/server/game/Spells/SpellMgr.cpp:1887` | `LoadSpellProcs` (`spell_proc` table) — see [`06-proc-system.md`](./06-proc-system.md) |
| `src/server/game/Spells/SpellInfoCorrections.cpp` | per-id fixups applied after DBC load (typo rows, missing flags, attribute holes — large file with thousands of `case` lines) |
| `src/server/game/Spells/SpellInfoCustomAttributes.cpp` | sets the `SPELL_ATTR0_CU_*` bitmask used by gameplay (e.g. `_SHARE_DAMAGE`, `_DONT_BREAK_STEALTH`, `_BINARY_SPELL`) |

## Key concepts

- **`sSpellMgr->GetSpellInfo(spellId)`** is the canonical lookup. Never read `sSpellStore.LookupEntry(id)` directly in gameplay code — it gives you the raw DBC row without overlays.
- **`SpellInfo::Effects[MAX_SPELL_EFFECTS]`** (`MAX_SPELL_EFFECTS = 3`) is an array of `SpellEffectInfo`. Each carries `Effect` (the effect enum), `ApplyAuraName` (if the effect is `APPLY_AURA`), `BasePoints`, `DieSides`, `RealPointsPerLevel`, `PointsPerComboPoint`, `Mechanic`, `TargetA`/`TargetB` (target masks — see [`04-targeting.md`](./04-targeting.md)), `RadiusEntry`, `ChainTarget`, `ItemType`, `MiscValue`, `MiscValueB`.
- **Custom attributes** (`SPELL_ATTR0_CU_*`) are AzerothCore-specific bitmasks layered on top of Blizzard's `SPELL_ATTR0_…SPELL_ATTR8_*`. They live in `SpellInfo::AttributesCu` and are tested via `HasAttribute(SPELL_ATTR0_CU_*)`.
- **Spell rank chain.** `SpellChainNode` (one per rank) holds `prev`, `next`, `first`, `last`, `rank`. Built from `spell_ranks` table via `SpellMgr::LoadSpellRanks()`. Used by `Player::HasActiveSpell` for talent ranks.
- **Spell learn map.** `SpellLearnSkillStore` ↔ `SpellLearnSpellMap` ↔ `SpellLearnSpellNode` — populated from `spell_learn_spell` table + DBC. `Player::learnSpell` consults these.
- **Bonus tables.** Cached per-spell coefficients: `SpellBonusMap` (`spell_bonus_data`), `SpellGroupSpellEffectMap`, `SpellPetAuraMap`. Each has its own loader on `SpellMgr`.

## Flow / data shape

```
worldserver startup ──► sSpellMgr->LoadSpellInfoStore()         [SpellMgr.cpp:2903]
   ├─ for entry in sSpellStore (DBC):
   │     mSpellInfoMap[id] = new SpellInfo(entry)
   │        SpellInfo ctor copies + denormalizes the SpellEntry columns
   │        and computes derived fields (SchoolMask, RangeMin/Max, etc.)
   ├─ LoadSpellInfoCorrections          (per-id case overlays)
   ├─ LoadSpellInfoSpellSpecificAndAuraState
   └─ LoadSpellInfoCustomAttributes     (AttributesCu bitmask)

later loaders fill out side caches:
   LoadSpellRanks, LoadSpellLearnSkills, LoadSpellTargetPositions,
   LoadSpellProcs, LoadSpellBonusess, LoadSpellGroups, LoadEnchantCustomAttr,
   LoadPetLevelupSpellMap, LoadPetDefaultSpells.
```

Lookup pattern at runtime:

```cpp
SpellInfo const* info = sSpellMgr->GetSpellInfo(spellId);
if (!info)
    return;                // unknown spell id
if (info->IsPassive())
    /* …apply as aura without cast bar… */
int32 dmg = info->Effects[EFFECT_0].CalcValue(caster);
```

Custom-spell ID ranges (this fork): `100000–`, `900100–`, `920001`, `950001–950099` — see `azerothcore-wotlk/CLAUDE.md` and [`../../06-custom-ids.md`](../../06-custom-ids.md). All custom rows go through the same `SpellInfo` pipeline; the only difference is that they live in the patched `Spell.dbc` shipped at `azerothcore-wotlk/share/dbc/Spell.dbc`.

## Hooks & extension points

`SpellMgr` is not a `ScriptObject`; you cannot hook into `SpellInfo` construction directly. To override per-id behavior, the canonical paths are:

- **DB override** — add a row to `spell_dbc` (cross-link [`../dbc/06-db-overrides.md`](../dbc/06-db-overrides.md)). Applied after DBC load, before `SpellInfo` creation, so the resulting `SpellInfo` sees the overridden values.
- **Custom attribute overlay** — add a case to `LoadSpellInfoCustomAttributes` to flip `SPELL_ATTR0_CU_*` bits on a specific id. Engine-side; lives in core code.
- **`SpellScript` / `AuraScript`** — for runtime per-cast behavior. See [`08-script-bindings.md`](./08-script-bindings.md) and [`../../03-spell-system.md`](../../03-spell-system.md).

## Cross-references

- Engine-side: [`../dbc/04-structures.md`](../dbc/04-structures.md), [`../dbc/06-db-overrides.md`](../dbc/06-db-overrides.md), [`01-cast-lifecycle.md`](./01-cast-lifecycle.md), [`04-targeting.md`](./04-targeting.md), [`05-effects.md`](./05-effects.md), [`06-proc-system.md`](./06-proc-system.md)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../06-custom-ids.md`](../../06-custom-ids.md), [`../../09-db-tables.md`](../../09-db-tables.md) (`spell_*` family), [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md)
- Fork-specific: `azerothcore-wotlk/CLAUDE.md` (custom Spell.dbc patching)
- External: Doxygen `classSpellInfo`, `classSpellMgr`
