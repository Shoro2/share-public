# spells/ — Spell engine (engine view)

> **Engine-internals view** of the spell system: how a `Spell` is prepared and cast, how `SpellInfo` is built from DBC, how auras live on units, how procs are resolved, and how `SpellScript`/`AuraScript` plug in.
>
> The **author-facing** view ("how do I write a SpellScript?") lives in [`../../03-spell-system.md`](../../03-spell-system.md) and the per-spec deep-dives in [`../../custom-spells/`](../../custom-spells/00-overview.md). This folder does **not** repeat that material.

## Topic files

| File | Topic |
|---|---|
| [`01-cast-lifecycle.md`](./01-cast-lifecycle.md) | `Spell::prepare → cast → handle_immediate → finish`, state machine, queueing |
| [`02-spell-info.md`](./02-spell-info.md) | `SpellInfo` (DBC-derived), `SpellMgr` lookups, `LoadSpellInfoStore`, per-spell metadata |
| [`03-aura-system.md`](./03-aura-system.md) | `Aura`, `AuraEffect`, `AuraApplication`, per-target lifetime, removal modes |
| [`04-targeting.md`](./04-targeting.md) | `SpellTargets`, target masks, area resolution, `SelectImplicitTargets` |
| [`05-effects.md`](./05-effects.md) | `SpellEffectHandlerFn` dispatch table, the ~150 effect handlers in `SpellEffects.cpp` |
| [`06-proc-system.md`](./06-proc-system.md) | `ProcEvent`, proc flags, the `spell_proc` table, full chain (cross-link to [`../../03-spell-system.md#proc-system--full-chain`](../../03-spell-system.md)) |
| [`07-modifiers.md`](./07-modifiers.md) | `SpellModifier`, `AddPctMod` / `AddFlatMod`, talents that modify other spells |
| [`08-script-bindings.md`](./08-script-bindings.md) | C++ `SpellScript` / `AuraScript` ↔ engine bridge, how `Register()` wires hooks |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/Spell.{h,cpp}` | One in-flight cast |
| `src/server/game/Spells/SpellInfo.{h,cpp}` | Static spell descriptor |
| `src/server/game/Spells/SpellMgr.{h,cpp}` | Registry, proc tables, lookups |
| `src/server/game/Spells/SpellEffects.cpp` | All `EffectHandler` functions |
| `src/server/game/Spells/Auras/Aura.{h,cpp}`, `AuraEffect.{h,cpp}`, `AuraApplication.{h,cpp}` | Aura tri-class |
| `src/server/game/Spells/SpellScript.{h,cpp}` | Script hook glue |
| `src/server/game/Spells/SpellModifier.h` | Spell modifiers |

## Cross-references

- Engine-side: [`../entities/04-player.md`](../entities/04-player.md) (caster/target), [`../combat/01-damage-pipeline.md`](../combat/01-damage-pipeline.md), [`../dbc/04-structures.md`](../dbc/04-structures.md) (`SpellEntry`)
- Project-side (canonical for authors): [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/`](../../custom-spells/00-overview.md), [`../../06-custom-ids.md`](../../06-custom-ids.md)
- External: Doxygen for `Spell`, `SpellInfo`, `Aura`, `AuraEffect`, `SpellMgr`
