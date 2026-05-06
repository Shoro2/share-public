# spells — SpellScript / AuraScript bindings

> The C++ glue between user-authored `SpellScript`/`AuraScript` classes and the engine — how a registered hook gets invoked from inside `Spell::HandleEffects`, `Aura::*Apply`, etc. User-side authoring stays in [`../../03-spell-system.md`](../../03-spell-system.md); this file covers the engine plumbing.

## Critical files

| File | Role |
|---|---|
| `src/server/game/Spells/SpellScript.h:55` | `class _SpellScript` — common base for `SpellScript` and `AuraScript`; owns `m_currentScriptState`, `m_scriptName`, `m_scriptSpellId`, validation helpers (`ValidateSpellInfo`, `ValidateSpellEffect`) |
| `src/server/game/Spells/SpellScript.h:181` | `class SpellScript : public _SpellScript` — cast-side script |
| `src/server/game/Spells/SpellScript.h:319-347` | `BeforeCast`/`OnCast`/`AfterCast` (319/321/323), `OnCheckCast` (328), `OnEffectLaunch`/`OnEffectLaunchTarget` (333/334), `OnEffectHit`/`OnEffectHitTarget` (335/336), `BeforeHit`/`OnHit`/`AfterHit` (341/345/347) |
| `src/server/game/Spells/SpellScript.h:353/358/363` | target-selection hooks: `OnObjectAreaTargetSelect` / `OnObjectTargetSelect` / `OnDestinationTargetSelect` |
| `src/server/game/Spells/SpellScript.h:517` | `class AuraScript : public _SpellScript` — aura-side script |
| `src/server/game/Spells/SpellScript.h:732-764` | `DoCheckAreaTarget` (732), `OnDispel`/`AfterDispel` (738/742), `OnEffectApply`/`AfterEffectApply` (749/753), `OnEffectRemove`/`AfterEffectRemove` (760/764) |
| `src/server/game/Spells/SpellScript.cpp` | `_SpellScript::_Init` / `_Register` / `_Validate` / `_Load` lifecycle; `SpellScript::_Init` glues to a parent `Spell*`; `AuraScript::_Init` glues to a parent `Aura*` |
| `src/server/game/Spells/Spell.cpp` | call sites: `m_spellScript->_Register()` (after construction), `m_spellScript->BeforeCast.Call()` (in `cast`), `OnEffectHit.Call(effIdx)` (in `HandleEffects`), `OnObjectAreaTargetSelect.Call(targets)` (in `SelectImplicitAreaTargets`) |
| `src/server/game/Spells/Auras/SpellAuras.cpp` | call sites: `m_aura->_Register()`, `OnEffectApply.Call(aurEff, mode)`, `OnProc.Call(eventInfo)`, `AfterEffectRemove.Call(...)` |
| `src/server/game/Scripting/ScriptMgr.cpp` | `ScriptMgr::CreateSpellScripts(spellId, std::vector<SpellScript*>&)` and `CreateAuraScripts(...)` — invoked at `Spell::LoadScripts()` / `Aura::LoadScripts()` to look up registered factories |
| `src/server/game/Scripting/ScriptDefines/SpellScriptLoader.h` | `class SpellScriptLoader : public ScriptObject` — the `ScriptObject` subclass module authors derive; provides `GetSpellScript()`/`GetAuraScript()` factories returning fresh instances |

## Key concepts

- **Two parallel script-class trees, one mechanism.** `SpellScript` lives on a `Spell*`, lifetime = one cast. `AuraScript` lives on an `Aura*`, lifetime = one buff instance. Both inherit `_SpellScript` (which inherits indirectly from `ScriptObject` — see [`../scripting/03-script-objects.md`](../scripting/03-script-objects.md)).
- **`HookList<T>`.** Each public hook (e.g. `OnEffectHit`) is a `HookList<EffectHandler>` template. Multiple `+= EffectHandler(...)` calls inside `Register()` add multiple handlers to the same hook; the engine fires them in registration order.
- **Registration must happen in `Register()`.** The engine calls `_Register()` once after construction; this in turn calls the user override `Register()`. Adding hooks outside `Register()` is undefined.
- **Per-effect binding via macros.** `SpellEffectFn(class::method, EFFECT_0, SPELL_EFFECT_DUMMY)`, `AuraEffectApplyFn(class::method, EFFECT_0, SPELL_AURA_DUMMY, AURA_EFFECT_HANDLE_REAL)`, etc. — these wrap a member-function pointer, the effect index it applies to, and the effect type to filter.
- **`PrepareSpellScript(class)` / `PrepareAuraScript(class)` macros** are required at the top of every user script class. They define the `_GetScriptName()` virtual and the validation hook plumbing.
- **Multiple scripts per spell allowed.** `ScriptMgr::CreateSpellScripts(id, out)` returns *all* registered factories' instances. Each gets its own `_Register()` and runs independently.
- **Validation runs before any cast/apply.** `_Validate(spellInfo)` (called via `ScriptMgr::OnValidateSpellScript(...)`) lets a script declare prerequisite spell IDs (`ValidateSpellInfo({...})`) and prerequisite effect indices. Failure logs an error and silently disables the script.

## Flow / data shape

```
worldserver startup ──► Module's Add{Module}Scripts() (see scripting/05-module-discovery.md)
   ├─ new MySpellScriptLoader("MySpellScript_5061")    // registers factory in ScriptMgr
   └─ ...

Spell::Spell(caster, info, ...)
   └─ Spell::LoadScripts()
        └─ sScriptMgr->CreateSpellScripts(info->Id, m_loadedScripts)
            for each registered SpellScriptLoader matching info->Id (or family):
                m_loadedScripts.push_back(loader->GetSpellScript())   // fresh instance
        └─ for s in m_loadedScripts:
              s->_Init(this, info->Id)
              s->_Validate(info)            // user-declared spell-id/effect prereqs
              s->_Register()                // user fills HookLists

Spell::cast(...) lifecycle:
   m_spellScript->BeforeCast.Call(this)        // [SpellScript.h:319]
   ... reagent / cost / targeting ...
   m_spellScript->OnCast.Call(this)            // [321]
   ... handle_immediate / DoAllEffectOnTarget ...
       Spell::HandleEffects(target, ..., HIT_TARGET)
          before default switch: m_spellScript->OnEffectHitTarget.Call(effIdx)
                                                                 // [336]
          if no override consumed it: default Effect{Name}(effIdx)
   ... finish ...
   m_spellScript->AfterCast.Call(this)         // [323]
   delete m_spellScript    (when Spell is deleted in finish)

Aura lifecycle (similar, AuraScript):
   Aura::_ApplyForTarget → m_auraScript->OnEffectApply.Call(aurEff, mode)
                                                                 // [749]
   Aura::Update          → m_auraScript->OnEffectPeriodic.Call(aurEff)
   Aura::HandleProc      → m_auraScript->DoCheckProc.Call(eventInfo)
                          → m_auraScript->OnProc.Call(eventInfo)
   Aura::_UnapplyForTarget → m_auraScript->OnEffectRemove.Call(aurEff, mode)
                                                                 // [760]
```

A handler can suppress the default behavior by:
- Returning `SPELL_FAILED_*` from `OnCheckCast` (aborts cast).
- Calling `PreventHitDefaultEffect(effIdx)` inside `OnEffectHitTarget` (skips engine's default `Effect{Name}` for that target).
- Setting `eventInfo.SetProcSuppressed()` in `OnProc` (the engine still consumes a charge but skips trigger spell).

## Registration entry points

A module loader file (e.g. `mod_my_spell_loader.cpp`) wires script classes via:

```cpp
class spell_paragon_haste : public SpellScriptLoader {
public:
    spell_paragon_haste() : SpellScriptLoader("spell_paragon_haste") {}
    SpellScript* GetSpellScript() const override { return new spell_paragon_haste_SpellScript(); }
};

void AddSC_paragon_spells() {
    new spell_paragon_haste();
}
```

`AddSC_paragon_spells` is called from `Add{module}Scripts()` (one entry generated by the module CMake glue — see [`../scripting/05-module-discovery.md`](../scripting/05-module-discovery.md)).

For the user-side template + worked examples: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/04-adding-a-spell.md`](../../custom-spells/04-adding-a-spell.md).

## Hooks & extension points

This whole file *is* the extension surface. The script binding machinery is the only sanctioned way to alter spell or aura behavior without modifying core. Other extension paths:

- Modify `SpellInfo` itself: prefer `spell_dbc` table override ([`../dbc/06-db-overrides.md`](../dbc/06-db-overrides.md)) over a script.
- Modify proc rules: prefer `spell_proc` row over a script ([`06-proc-system.md`](./06-proc-system.md)).
- Add a new effect or aura type: requires core enum + handler addition (last resort).

## Cross-references

- Engine-side: [`01-cast-lifecycle.md`](./01-cast-lifecycle.md), [`03-aura-system.md`](./03-aura-system.md), [`04-targeting.md`](./04-targeting.md), [`05-effects.md`](./05-effects.md), [`06-proc-system.md`](./06-proc-system.md), [`07-modifiers.md`](./07-modifiers.md), [`../scripting/01-script-mgr.md`](../scripting/01-script-mgr.md), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md), [`../scripting/03-script-objects.md`](../scripting/03-script-objects.md)
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/04-adding-a-spell.md`](../../custom-spells/04-adding-a-spell.md), [`../../05-modules.md`](../../05-modules.md)
- External: Doxygen `classSpellScript`, `classAuraScript`, `classSpellScriptLoader`, `class__SpellScript`
