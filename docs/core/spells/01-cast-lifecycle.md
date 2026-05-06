# spells — Cast lifecycle

> Server-side state machine of one `Spell` instance from `prepare()` through `cast()` → `handle_immediate()`/`update()` → `finish()`. Cross-link: [`02-spell-info.md`](./02-spell-info.md) (input metadata), [`05-effects.md`](./05-effects.md) (effect dispatch), [`../handlers/04-spell-handler.md`](../handlers/04-spell-handler.md) (entry from `CMSG_CAST_SPELL`).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/Spell.h:234` | `enum SpellState { NULL, PREPARING, CASTING, FINISHED, IDLE, DELAYED }` |
| `src/server/game/Spells/Spell.h:250` | `enum SpellEffectHandleMode { LAUNCH, LAUNCH_TARGET, HIT, HIT_TARGET }` |
| `src/server/game/Spells/Spell.h:297` | `class Spell` — one-shot stateful cast object |
| `src/server/game/Spells/Spell.h:462` | `void cast(bool skipCheck)` |
| `src/server/game/Spells/Spell.h:464` | `void finish(bool ok = true)` |
| `src/server/game/Spells/Spell.h:476` | `void handle_immediate()` |
| `src/server/game/Spells/Spell.cpp:3404` | `Spell::prepare(targets, triggeredByAura)` — entry; computes power cost + cast time, stores `m_powerCost`/`m_casttime`, transitions to `SPELL_STATE_PREPARING`, schedules first `update()` |
| `src/server/game/Spells/Spell.cpp:3658` | `Spell::cancel(bool bySelf)` — abort path; sends `SMSG_SPELL_FAILURE`, transitions to `FINISHED`, calls `finish(false)` |
| `src/server/game/Spells/Spell.cpp:3731` | `Spell::cast(bool skipCheck)` — final cost check + reagent/item/aura consumption; sends `SMSG_SPELL_GO`; routes to `handle_immediate()` for instant or queues for `update()` traveltime/channel |
| `src/server/game/Spells/Spell.cpp:4053` | `Spell::handle_immediate()` — fan-out: `HandleEffects(LAUNCH)` then per-target `HandleEffects(LAUNCH_TARGET)` then per-target `HandleEffects(HIT_TARGET)`; sets `SPELL_STATE_FINISHED` for instants |
| `src/server/game/Spells/Spell.cpp:4349` | `Spell::update(diff)` — driven by `Unit::Update` for `m_currentSpells[CURRENT_*_SPELL]`; ticks cast bar, fires channel ticks, transitions PREPARING→CASTING→FINISHED |
| `src/server/game/Spells/Spell.cpp:4439` | `Spell::finish(bool ok)` — cleanup: removes from `m_currentSpells`, refunds power on failure, fires `SpellScript::AfterCast`, deletes `Spell` |
| `src/server/game/Spells/Spell.cpp:4755` | `SendSpellGo()` — visual + audible packet to nearby clients |
| `src/server/game/Spells/Spell.cpp:5164` | `SendChannelStart(duration)` — for channeled spells |
| `src/server/game/Spells/Spell.cpp:5593` | `Spell::HandleEffects(unit, item, go, effectIdx, mode)` — dispatches one of 124 `Spell::Effect*` functions in `SpellEffects.cpp` based on `SpellInfo::Effects[i].Effect` |
| `src/server/game/Spells/Spell.cpp:5619` | `Spell::CheckCast(strict, …)` — pre-cast validation (range, line-of-sight, target eligibility, requires-aura, area, equip, mounted, …) returns `SpellCastResult` |
| `src/server/game/Spells/Spell.cpp:6833` | `Spell::CheckCasterAuras(preventionOnly)` — silence/pacify/stun/cyclone gates |
| `src/server/game/Spells/Spell.cpp:822` | `Spell::SelectSpellTargets()` — runs target-selection effect-by-effect; see [`04-targeting.md`](./04-targeting.md) |
| `src/server/game/Spells/Spell.cpp:2200` | `Spell::prepareDataForTriggerSystem` — computes proc inputs (typeMask, hitMask, …); see [`06-proc-system.md`](./06-proc-system.md) |

## Key concepts

- **One `Spell` per cast.** Heap-allocated by the caster (`Unit::CastSpell`/`Player::CastSpell`), tracked in `m_currentSpells[CURRENT_GENERIC_SPELL | CURRENT_MELEE_SPELL | CURRENT_CHANNELED_SPELL | CURRENT_AUTOREPEAT_SPELL]`. Deleted by `finish()` via `SetReferencedFromCurrent(false)` + `Spell::Delete`.
- **Six states.** `NULL` (constructed) → `PREPARING` (cast bar visible) → `CASTING` (channeling tick or in-flight) → `FINISHED` (effects applied, awaiting GC) → `IDLE` (channel between ticks) → `DELAYED` (pushed back by damage). Set via `SetExecutedCurrently` and `m_spellState`.
- **Four effect modes.** `LAUNCH` (caster, once), `LAUNCH_TARGET` (per target, before flight), `HIT` (caster, on resolution), `HIT_TARGET` (per target, on resolution). `HandleEffects(target, …, mode)` is called from four call-sites in `Spell.cpp` (lines 4218, 8268, 8353, plus the per-target loop at 2558/3193).
- **Triggered casts.** A cast can be `_triggeredCastFlags` enabled; set via `Spell::Spell(caster, info, triggeredCastFlags, originalCasterGUID, skipCheck)` ctor. Triggered casts skip cost, cooldown, and most checks. Used for proc-driven spells.
- **`SpellCastResult`.** Returned by `CheckCast` and `CheckCasterAuras`. Non-`SUCCESS` aborts cast; client sees `SMSG_CAST_FAILED` (see `Spell::SendCastResult`). Common values: `SPELL_FAILED_NOT_READY`, `SPELL_FAILED_OUT_OF_RANGE`, `SPELL_FAILED_LINE_OF_SIGHT`, `SPELL_FAILED_BAD_TARGETS`, `SPELL_FAILED_REAGENTS`.

## Flow / data shape

```
client: CMSG_CAST_SPELL ────► WorldSession::HandleCastSpellOpcode (handlers/04)
                              └─ Player::CastSpell(...)                                (instant on caster)
                                 └─ new Spell(caster, info, …)
                                    └─ Spell::prepare(targets, …)            [3404]
                                       ├─ CheckCast(strict=true)             [5619]
                                       ├─ CheckCasterAuras                   [6833]
                                       ├─ TakePower / set m_powerCost        (cost computed)
                                       ├─ SelectSpellTargets                 [822]
                                       ├─ if cast time == 0:
                                       │    └─ cast(skipCheck=true)          [3731]
                                       └─ else: SPELL_STATE_PREPARING; schedule update()

         caster Unit::Update(diff) ──► Spell::update(diff)                   [4349]
                                       └─ on cast bar end:  cast(false)      [3731]
                                          ├─ second CheckCast(strict=false)
                                          ├─ TakeReagents / TakeItems        (consume)
                                          ├─ SendSpellGo                     [4755]
                                          ├─ if instant or non-targeted:
                                          │    handle_immediate()            [4053]
                                          ├─ if channeled: SendChannelStart  [5164]
                                          └─ if travel: queued, served by next update()

         handle_immediate()                                                  [4053]
            ├─ HandleEffects(LAUNCH)                                         [5593, mode=LAUNCH]
            ├─ for each target: HandleEffects(LAUNCH_TARGET)                 [mode=LAUNCH_TARGET]
            ├─ for each target: DoAllEffectOnTarget → HandleEffects(HIT_TARGET)
            ├─ HandleEffects(HIT)
            └─ finish(true)                                                  [4439]
```

`CMSG_CANCEL_CAST` and `Unit::InterruptSpell` route to `Spell::cancel(bool bySelf)` [3658].

## Hooks & extension points

`SpellScript` exposes the lifecycle to user code. Anchor handlers in `SpellScript.h`:

- `BeforeCast` (319), `OnCast` (321), `AfterCast` (323), `OnCheckCast` (328) — called from `prepare()`/`cast()`.
- `OnEffectLaunch` / `OnEffectLaunchTarget` (333–334) — called from inside `HandleEffects(LAUNCH/LAUNCH_TARGET)`.
- `OnEffectHit` / `OnEffectHitTarget` (335–336) — called from inside `HandleEffects(HIT/HIT_TARGET)`.
- `BeforeHit`, `OnHit`, `AfterHit` (341–347) — called once per target inside `DoAllEffectOnTarget`.

User-side authoring: see [`../../03-spell-system.md`](../../03-spell-system.md). Engine-side glue: [`08-script-bindings.md`](./08-script-bindings.md).

## Cross-references

- Engine-side: [`02-spell-info.md`](./02-spell-info.md), [`04-targeting.md`](./04-targeting.md), [`05-effects.md`](./05-effects.md), [`03-aura-system.md`](./03-aura-system.md), [`06-proc-system.md`](./06-proc-system.md), [`07-modifiers.md`](./07-modifiers.md), [`../handlers/04-spell-handler.md`](../handlers/04-spell-handler.md), [`../entities/04-player.md`](../entities/04-player.md) (`Player::CastSpell`), [`../combat/01-damage-pipeline.md`](../combat/01-damage-pipeline.md)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/`](../../custom-spells/00-overview.md)
- Fork-specific: `azerothcore-wotlk/CLAUDE.md` (custom-patched Spell.dbc IDs)
- External: Doxygen `classSpell`
