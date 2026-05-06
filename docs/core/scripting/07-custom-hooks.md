# scripting — Fork-specific custom hooks

> This fork's only documented engine-level extensions over upstream AzerothCore are two `PlayerScript` hooks intended to let an external storage plug into the spell-cast reagent pipeline: `OnPlayerCheckReagent` and `OnPlayerConsumeReagent`. **As of the current source tree, neither hook is wired into the engine** — the historical consumer (`mod-endless-storage`) migrated to a Lua/AIO path and the C++ patch was either reverted or never committed. This file documents the *contract* (per `azerothcore-wotlk/functions.md`), the *intended* call sites, and the *current actual state* of the source. For the upstream hook catalog see [`02-hook-classes.md`](./02-hook-classes.md); for module discovery see [`05-module-discovery.md`](./05-module-discovery.md).

## Critical files

| File | Role |
|---|---|
| `azerothcore-wotlk/functions.md` | **canonical contract** for the two custom hooks (signature, call site, semantics) |
| `azerothcore-wotlk/CLAUDE.md` (Custom extensions table) | top-level summary; marks both hooks as *"historical; currently unused"* |
| `share-public/docs/05-modules.md` (mod-endless-storage section) | consumer description — notes the Lua-path migration |
| `share-public/docs/02-architecture.md` (Hook system table) | mentions `OnCheckReagent` / `OnConsumeReagent` in the `PlayerScript` row |
| `src/server/game/Scripting/ScriptDefines/PlayerScript.h` | upstream player hooks; **no** `OnPlayerCheckReagent` / `OnPlayerConsumeReagent` virtuals present in current tree (verified by grep, see "Current state" below) |
| `src/server/game/Scripting/ScriptDefines/PlayerScript.cpp` | upstream `ScriptMgr::OnPlayer*` dispatchers; **no** matching dispatcher present |
| `src/server/game/Scripting/ScriptMgr.h` | no method declaration for either hook in the current tree |
| `src/server/game/Spells/Spell.cpp:5490` | `Spell::TakeReagents()` — *intended* call site for `OnPlayerConsumeReagent` (currently calls only `DestroyItemCount`) |
| `src/server/game/Spells/Spell.cpp:7280-7288` | `Spell::CheckItems()` reagent path — *intended* call site for `OnPlayerCheckReagent` (currently no `sScriptMgr->` call here) |

## Documented contract (per `functions.md`)

```cpp
// PlayerScript.h (intended)
virtual bool OnPlayerCheckReagent(Player* player, Spell* spell,
                                  uint32 itemId, uint32 itemCount, uint32& foundCount);

virtual bool OnPlayerConsumeReagent(Player* player, Spell* spell,
                                    uint32 itemId, uint32& itemCount);
```

| Hook | Engine call site (intended) | Semantics |
|---|---|---|
| `OnPlayerCheckReagent` | `Spell::CheckItems()` (reagent loop) | called when inventory is short of a reagent. Implementer can increase `foundCount` (additively) by the amount available externally. Return `true` if cast may now proceed. |
| `OnPlayerConsumeReagent` | `Spell::TakeReagents()` (per reagent, before `DestroyItemCount`) | called for every reagent. Implementer may reduce the still-to-consume `itemCount` by the amount taken from the external store. Return `true` if any was consumed externally. |

Documented diff scope (per `functions.md`): ~45 lines of code split across `PlayerScript.{h,cpp}`, `ScriptMgr.h`, and `Spell.cpp` (one `sScriptMgr->OnPlayerCheckReagent` call inside the `CheckItems()` reagent loop, one `sScriptMgr->OnPlayerConsumeReagent` call inside `TakeReagents()`).

Documented enum extension: `PLAYERHOOK_ON_CHECK_REAGENT`, `PLAYERHOOK_ON_CONSUME_REAGENT` — to be inserted into the `PlayerHook` enum (`PlayerScript.h:30`) before `PLAYERHOOK_END`.

## Current state in the source tree

Verified by `grep -rn "Reagent" src/server/game/Scripting/ src/server/game/Spells/`:

- `PlayerScript.h` / `PlayerScript.cpp`: **no** `OnPlayerCheckReagent` / `OnPlayerConsumeReagent` virtual or dispatcher; **no** `PLAYERHOOK_ON_CHECK_REAGENT` / `PLAYERHOOK_ON_CONSUME_REAGENT` enum entries.
- `ScriptMgr.h`: **no** declaration for either method.
- `Spell.cpp::CheckItems()` / `Spell::TakeReagents()`: **no** `sScriptMgr->OnPlayer*Reagent` call.
- The only `Reagent` references in this subtree are upstream stock (`SPELL_FAILED_REAGENTS`, `SpellInfo::Reagent[]`, `HandleNoReagentUseAura`, `CanNoReagentCast`, `TRIGGERED_IGNORE_POWER_AND_REAGENT_COST`).

The `azerothcore-wotlk/CLAUDE.md` "Custom extensions" table tags both rows as `(historical; currently unused)`, and `share-public/docs/05-modules.md` says of `mod-endless-storage` that the Lua path now handles crafting integration. So the **doc-vs-code drift** is intentional: the hooks are reserved for re-introduction if the C++ path is needed again, but presently only `functions.md` describes them.

If/when re-added, the patch shape is the one above; the call sites in `Spell.cpp` (lines 5490, 7280-7288) are the natural insertion points.

## Hooks & extension points

- **Re-implementing the hooks** — follow the standard add-a-hook recipe ([`02-hook-classes.md`](./02-hook-classes.md) "Hooks & extension points"): add the virtuals to `PlayerScript.h` (with `PLAYERHOOK_ON_CHECK_REAGENT`/`..._CONSUME_REAGENT` enum entries), add `ScriptMgr::OnPlayerCheckReagent`/`OnPlayerConsumeReagent` declarations to `ScriptMgr.h`, define the dispatchers in `PlayerScript.cpp` using `CALL_ENABLED_BOOLEAN_HOOKS` (since both return `bool`), and call them from `Spell.cpp::CheckItems()` and `Spell::TakeReagents()` respectively. Then a module's `PlayerScript` override can implement either hook and fan into the external-storage backend.
- **Alternative path (current)** — modules that need to influence reagent availability use the AIO/Lua channel. See [`../../05-modules.md#mod-endless-storage`](../../05-modules.md) for the design.

## Cross-references

- Engine-side: [`02-hook-classes.md`](./02-hook-classes.md), [`01-script-mgr.md`](./01-script-mgr.md), [`05-module-discovery.md`](./05-module-discovery.md), [`../spells/00-index.md`](../spells/00-index.md) (Spell::CheckItems / TakeReagents)
- Project-side: [`../../02-architecture.md#hook-system-scriptmgr`](../../02-architecture.md), [`../../05-modules.md#mod-endless-storage`](../../05-modules.md)
- Fork-specific: `azerothcore-wotlk/functions.md` (canonical hook spec), `azerothcore-wotlk/CLAUDE.md` (custom-extensions table)
- External: `wiki/hooks-script` (general "how to add a hook" guide), Doxygen `classPlayerScript`, `classScriptMgr`
