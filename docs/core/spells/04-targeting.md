# spells — Targeting

> Per-effect target selection: each `SpellInfo::Effects[i]` carries `TargetA`/`TargetB` enums that drive `Spell::SelectSpellTargets` to populate the per-effect target list. Cross-link [`01-cast-lifecycle.md`](./01-cast-lifecycle.md) (caller), [`02-spell-info.md`](./02-spell-info.md) (effect data source).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/SpellDefines.h` | `enum SpellTargetSelectionCategories`, `enum SpellTargetReferenceTypes`, `enum SpellTargetObjectTypes`, `enum SpellTargetCheckTypes`, `enum SpellTargetDirectionTypes` — the 5 category enums that classify each `Targets` value |
| `src/server/game/Spells/SpellInfo.h` | `SpellEffectInfo::TargetA` / `TargetB` (`SpellImplicitTargetInfo`), `SpellEffectInfo::ChainTarget`, `SpellEffectInfo::RadiusEntry` (DBC pointer) |
| `src/server/game/Spells/Spell.h:120` | `class SpellCastTargets` — the client-supplied target packet (unit, item, GO, dest position) |
| `src/server/game/Spells/Spell.cpp:822` | `Spell::SelectSpellTargets()` — outer loop over the 3 effects, calls `SelectImplicitTargets` for `TargetA`/`TargetB` |
| `src/server/game/Spells/Spell.cpp` | `Spell::SelectImplicitTargets(effIndex, targetType, refType, ...)` — switch on `Category` (NEAREST/AT_DEST/CHANNEL/CASTER/AREA/CONE/CHAIN/TRAJ/...) and dispatches |
| `src/server/game/Spells/Spell.cpp` | `Spell::SearchAreaTargets`, `SearchChainTargets`, `SearchConeTargets`, `SearchTargets` (template) — geometry helpers; use `Acore::AreaCheck` predicates |
| `src/server/game/Grids/Notifiers/GridNotifiers.h` | `Acore::AnyAoETargetUnitInObjectRangeCheck`, `Acore::AnyDeadUnitObjectInRangeCheck`, `Acore::WorldObjectSpellTargetCheck`, etc. — the predicate functors used by `SearchAreaTargets` |
| `src/server/game/Spells/Spell.h:474` | `void prepareDataForTriggerSystem(...)` — also computes target-related proc fields |
| `src/server/game/Spells/SpellInfo.cpp` | `SpellInfo::GetMaxRange(positive, caster)`, `GetMinRange(positive)` — read `SpellRange.dbc` via `SpellRangeStore` |

## Key concepts

- **Implicit vs explicit targets.** *Explicit* targets come from the client packet (`SpellCastTargets`): the unit/item/GO/destination the player clicked. *Implicit* targets are derived per-effect from the `TargetA`/`TargetB` enum on each effect — e.g. an AOE around the caster, the caster's pet, all party members of the explicit unit, etc.
- **`Targets` enum is dense (~150 values).** Each value classifies into 5 orthogonal axes (declared in `SpellDefines.h`):
  - **Selection category** — `NEAREST` / `AT_DEST` / `CHANNEL` / `DEFAULT` / `CONE` / `AREA` / `CHAIN` / `TRAJ` / `LINE` / `LASTTARGETLOC`.
  - **Reference type** — what the geometry is anchored to: `SRC` (caster), `TARGET` (explicit unit), `DEST` (explicit position), `CASTER` (synonym for SRC).
  - **Object type** — `UNIT` / `GAMEOBJECT` / `CORPSE` / `DEST` / `ITEM` / `UNIT_AND_DEST`.
  - **Check type** — `ENEMY` / `ALLY` / `PARTY` / `RAID` / `SUMMONED` / `THREAT` / `ENTRY` (creature_id match, used for fixate/totem dispel).
  - **Direction type** — `FRONT` / `BACK` / `RIGHT` / `LEFT` / `FRONT_RIGHT` / `BACK_LEFT` / … (cone offsets).
  - These are decoded by `SpellImplicitTargetInfo::GetCategory()`, `GetReferenceType()`, etc.
- **Two passes per effect.** `SelectSpellTargets` calls `SelectImplicitTargets` first for `TargetA`, then for `TargetB`. The two lists are *unioned* into the effect's `m_UniqueTargetInfo`/`m_UniqueGOTargetInfo`/`m_UniqueItemInfo`. Unique-by-GUID — repeats are deduped.
- **Range & radius.** Distance check uses `SpellInfo::GetMaxRange()` (mid-cast) and the per-effect `RadiusEntry` (DBC `SpellRadius.dbc`). Some `Targets` values (e.g. *DEST_AREA*) override range with the radius.
- **Line of sight.** `Spell::CheckCast` (and per-target adjustments inside `SelectImplicitTargets`) call `WorldObject::IsWithinLOSInMap` — VMaps-backed. Cross-link [`../maps/07-vmaps.md`](../maps/07-vmaps.md).
- **Chain targets.** `ChainTarget > 1` (e.g. Chain Lightning, Heal-jumps). `SearchChainTargets` walks outward from the explicit target by `JumpDistance` (`SpellInfo::EffectChainAmplitude` / DBC). Targets must satisfy `WorldObjectSpellTargetCheck` (faction, in-combat, line-of-sight).
- **`m_targets` (`SpellCastTargets`).** Holds `m_objectTargetGUID` (the click target), `m_itemTargetGUID`, `m_dst`/`m_src` (positions for ground-targeted), and `m_targetMask` flags. Filled by `WorldSession::HandleCastSpellOpcode` from the wire packet. Read by `SelectSpellTargets` for explicit lookups.

## Flow / data shape

```
Spell::cast(skipCheck) ──► Spell::SelectSpellTargets()                 [Spell.cpp:822]
   for effIndex in 0..MAX_SPELL_EFFECTS-1:
      effInfo = m_spellInfo->Effects[effIndex]
      SelectImplicitTargets(effIndex, effInfo.TargetA, …)
         switch (info.GetCategory()):
            CHANNEL → SelectImplicitChannelTargets(…)
            NEAREST → SelectImplicitNearbyTargets(…)
            CONE    → SelectImplicitConeTargets(…)            ─┐
            AREA    → SelectImplicitAreaTargets(…)             │  use SearchAreaTargets
            CHAIN   → SelectImplicitChainTargets(…)            │  + GridNotifier predicates
            TRAJ    → SelectImplicitTrajTargets(…)            ─┘
            CASTER  → AddUnitTarget(m_caster, …)
            DEFAULT → AddUnitTarget(m_targets.GetUnitTarget(), …)
      SelectImplicitTargets(effIndex, effInfo.TargetB, …)        // same, second pass

   AddUnitTarget(unit, …) → m_UniqueTargetInfo.push_back(TargetInfo{guid, effMask, …})
   AddGOTarget(go, …)     → m_UniqueGOTargetInfo
   AddItemTarget(item, …) → m_UniqueItemInfo
```

`Spell::handle_immediate` later iterates `m_UniqueTargetInfo` and calls `DoAllEffectOnTarget(target)` per entry, which calls `HandleEffects(target, ..., HIT_TARGET)` for each effect-bit set on that target.

## Hooks & extension points

`SpellScript` exposes target selection via three hook lists in `SpellScript.h`:

- `OnObjectAreaTargetSelect` (353) — invoked from `SelectImplicitAreaTargets`; the script may filter (`targets.remove_if(...)`) or insert.
- `OnObjectTargetSelect` (358) — invoked for single-object selects (e.g. `TARGET_UNIT_TARGET_ENEMY`).
- `OnDestinationTargetSelect` (363) — invoked when a destination is computed; the script may move/replace `target.dest`.

Each hook is bound to one `(effIndex, targetType)` pair via the `EffectHandler`/`TargetHook` macros. See [`08-script-bindings.md`](./08-script-bindings.md) and authoring examples in [`../../03-spell-system.md`](../../03-spell-system.md).

`SmartAI` data-driven targeting (`smart_scripts.target_type`) is unrelated to the spell-targeting system here — that resolves *before* `Spell::prepare`. Cross-link [`../ai/03-smart-ai.md`](../ai/03-smart-ai.md).

## Cross-references

- Engine-side: [`01-cast-lifecycle.md`](./01-cast-lifecycle.md), [`02-spell-info.md`](./02-spell-info.md), [`05-effects.md`](./05-effects.md), [`08-script-bindings.md`](./08-script-bindings.md), [`../maps/05-visibility.md`](../maps/05-visibility.md), [`../maps/07-vmaps.md`](../maps/07-vmaps.md)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/05-complex-spells.md`](../../custom-spells/05-complex-spells.md)
- External: Doxygen `classSpell`, `structSpellEffectInfo`, `classSpellImplicitTargetInfo`
