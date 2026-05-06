# ai/ — Creature AI

> AI is layered: every `Creature` owns one `CreatureAI`. The concrete kind is selected by `CreatureAIRegistry` (factory), or driven by data via `SmartAI`/`SmartScriptMgr`. `Pet`s use `PetAI`.

## Topic files

| File | Topic |
|---|---|
| [`01-ai-base.md`](./01-ai-base.md) | `UnitAI` → `CreatureAI`, virtual entry points (`UpdateAI`, `JustEngagedWith`, `EnterEvadeMode`, `Reset`, `MoveInLineOfSight`) |
| [`02-scripted-ai.md`](./02-scripted-ai.md) | `ScriptedAI`, `BossAI`, helper macros, event scheduler, `EventMap` |
| [`03-smart-ai.md`](./03-smart-ai.md) | `SmartAI`, `SmartScriptMgr`, `smart_scripts` table, event/action/target taxonomy |
| [`04-pet-ai.md`](./04-pet-ai.md) | `PetAI`, `ControlledAI`, charm pets, autocast |

## Critical files

| File | Role |
|---|---|
| `src/server/game/AI/CreatureAI.{h,cpp}` | Base class |
| `src/server/game/AI/CreatureAIImpl.h` | Inline helpers |
| `src/server/game/AI/CoreAI/*` | Built-in fallback AIs |
| `src/server/game/AI/ScriptedAI/ScriptedCreature.{h,cpp}` | `ScriptedAI`, `BossAI` |
| `src/server/game/AI/SmartScripts/SmartAI.{h,cpp}`, `SmartScript.{h,cpp}`, `SmartScriptMgr.{h,cpp}` | SAI runtime + DB loader |
| `src/server/game/AI/PetAI.{h,cpp}` | Pet behaviour |
| `src/server/game/Globals/CreatureAIRegistry.{h,cpp}` | Factory |

## Cross-references

- Engine-side: [`../entities/05-creature.md`](../entities/05-creature.md), [`../movement/01-motion-master.md`](../movement/01-motion-master.md), [`../combat/02-threat-system.md`](../combat/02-threat-system.md), [`../scripting/03-script-objects.md`](../scripting/03-script-objects.md) (`CreatureScript` AI factory hook)
- Project-side: [`../../02-architecture.md#hook-system-scriptmgr`](../../02-architecture.md)
- External: Doxygen for `CreatureAI`, `ScriptedAI`, `BossAI`, `SmartAI`, `EventMap`
