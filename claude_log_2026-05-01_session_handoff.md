# Session handoff 2026-05-01 → next session

> This document brings a **new AI session** up to speed in <5 minutes from the previous session.
> Read this, then `claude_log_2026-05-01_phase_b.md`, then `todo.md` per affected repo.

## What happened in the previous session (quick recap)

**Doc restructuring (phases A + B)** — completed, in 7 PRs merged/open:

| PR | Repo |
|----|------|
| #30 (merged) + #31 (open) | share-public |
| #40 | mod-paragon |
| #26 | mod-paragon-itemgen |
| #17 | mod-loot-filter |
| #16 | mod-endless-storage |
| #3 | mod-auto-loot |
| #18 | azerothcore-wotlk |

**Convention established** (see `docs/08-ai-workflow.md`): every module/core repo has **`INDEX.md`/`CLAUDE.md`/`data_structure.md`/`functions.md`/`log.md`/`todo.md`**. Cross-repo history stays in `share-public/claude_log.md`.

**Theme A (SQL injection mitigation)** — completed:
- `share-public/AIO_Server/Dep_Validation/validation.lua` as a shared library, exposing `_G.Validate`.
- mod-paragon (`Paragon_Server.lua`), mod-loot-filter (`LootFilter_Server.lua`), mod-endless-storage (`endless_storage_server.lua`) consume the library.
- Resolves M1, M4, M5 (medium priority).

**Quick wins** (all completed):
- `share-public/python_scripts/validate_dbc.py` — DBC pre-push validator (header / string table / duplicate IDs).
- mod-endless-storage M6 (bulk withdraw via Shift/Ctrl-click).

**Themes C/D removed**: AH hook TODO + anti-farm/reset cooldown — user decision "won't fix".

## M2 (C++↔Lua race condition in mod-paragon) — IN PROGRESS, not pushed

User decision 2026-05-01: race is **observed** (not theoretical), resolution: option (a) "delegate Lua allocations to C++". Constraint: a full `Player:ParagonAllocate` binding would require a mod-eluna fork (not in authorization). User agreed to the **option-a-equivalent practical variant**.

### Root cause (verified by code reading)

```
Player allocates in Lua → 2 separate async UPDATE statements (stat + unspent)
  ⏱ DB queue has neither committed yet
Player changes map → C++ ApplyParagonStatEffects() reads from DB
  → totalAllocated + unspent ≠ level*PPL  (because of pending writes)
  → integrity check fires → DESTRUCTIVE RESET (stats are destroyed)
  → "There was an error loading your Paragon points..."
```

### Concrete patch plan (3 files, ready to apply)

1. **`mod-paragon/Paragon_System_LUA/Paragon_Data.lua`** — new function:

   ```lua
   --- Atomic update: stat allocation + unspent_points in a single UPDATE.
   -- Synchronous via CharDBQuery → C++ map-change reads see the new state immediately.
   function Paragon.UpdateAllocationAndUnspent(characterID, dbColumn, newValue, newUnspent)
       CharDBQuery("UPDATE character_paragon_points SET "
           .. dbColumn .. " = " .. newValue
           .. ", unspent_points = " .. newUnspent
           .. " WHERE characterID = " .. characterID)
   end
   ```

   Keep the old `UpdateAllocation` and `UpdateUnspentPoints` (backwards compatibility for other callers, if any).

2. **`mod-paragon/Paragon_System_LUA/Paragon_Server.lua`** — switch `AllocatePoint` and `DeallocatePoint`:

   ```lua
   -- before (two separate async UPDATEs):
   Paragon.UpdateAllocation(characterID, stat.dbColumn, newValue)
   Paragon.UpdateUnspentPoints(characterID, newUnspent)
   -- after:
   Paragon.UpdateAllocationAndUnspent(characterID, stat.dbColumn, newValue, newUnspent)
   ```

3. **`mod-paragon/src/ParagonPlayer.cpp`** — in `ApplyParagonStatEffects()`, replace the destructive reset with a soft recovery:

   ```cpp
   if ((totalAllocated + unspentPoints) != paragonLevel * conf_PPL)
   {
       // Soft recovery (previously: destructive RESET of all stats + unspent).
       // Lua now writes atomically + synchronously, so this branch should not fire
       // in normal operation. Defensively: only correct unspent, leave stats untouched
       // so a possibly transient mismatch does not destroy allocations.
       uint32 totalPoints = paragonLevel * conf_PPL;
       int64 expectedUnspent = static_cast<int64>(totalPoints) - static_cast<int64>(totalAllocated);
       if (expectedUnspent < 0) expectedUnspent = 0;

       if (static_cast<uint32>(expectedUnspent) != unspentPoints)
       {
           LOG_WARN("module.paragon",
               "ApplyParagonStatEffects: mismatch for player {} (GUID {}, level={}, total_alloc={}, unspent={}, expected_unspent={}). "
               "Soft-recover unspent without resetting stats.",
               player->GetName(), player->GetGUID().ToString(),
               paragonLevel, totalAllocated, unspentPoints, expectedUnspent);

           CharacterDatabasePreparedStatement* setStmt =
               CharacterDatabase.GetPreparedStatement(CHAR_UPD_PARAGON_UNSPENT_SET);
           setStmt->SetData(0, static_cast<uint32>(expectedUnspent));
           setStmt->SetData(1, characterID);
           CharacterDatabase.Execute(setStmt);
       }
       // No early return anymore — even on mismatch: apply auras.
   }

   RefreshParagonAura(player, statValues);
   ```

   The destructive reset logic (all stats to 0) stays **only** in the NPC reset path (`ParagonNPC.cpp` → `ResetParagonPoints`).

### Cleanup after implementation

- `mod-paragon/todo.md`: remove item M2 ("C++↔Lua race condition").
- `mod-paragon/log.md`: entry analogous to M1 with reference to the final commit.

### Validation (manual by the user in-game)

- Before: allocate a point → map change within 100ms → reset message appeared, points gone.
- After: same flow → point stays allocated, no reset.

## New information for the next session: `mod-ale`

The user will add an additional repo `shoro2/mod-ale` to the GitHub app authorization. The next session should:

1. **Explore the repo** (`mcp__github__get_file_contents` on `/`) and classify what it is.
2. **Apply the per-repo doc convention** (see `share-public/docs/08-ai-workflow.md`):
   - create `INDEX.md`, `CLAUDE.md`, `data_structure.md`, `functions.md`, `log.md`, `todo.md`.
   - Branch: `claude/<description>-<sessionId>`.
3. If `mod-ale` contains Lua/AIO code and uses `CharDBExecute`/`CharDBQuery`, **integrate the validation lib** like in mod-paragon/loot-filter/endless-storage (see the Theme A pattern).
4. If `mod-ale` should be referenced as a consumer/dependency in one of the existing module `functions.md` files, add it.

## Low priority TODOs (see per-repo `todo.md`)

Quick overview of the still-open items:

| Repo | Low priority items (excerpt) |
|------|------------------------------|
| mod-paragon | after the M2 fix, possibly **`ParagonPlayer.cpp` split** (was ~26 KB → over the read limit, noted in `todo.md`) |
| mod-paragon-itemgen | M7 (BasePoints off-by-one audit, **medium priority**), in-memory cache, SQL→generator script |
| mod-loot-filter | bulk import/export, server default rules, per-quality DE bonus |
| mod-endless-storage | server-driven tab layout, crafting fallback via server hook |
| mod-auto-loot | mining/herbalism/skinning, throttle cooldown |
| azerothcore-wotlk | only upstream sync hygiene + a hook marking item |

## Branch status (as of 2026-05-01 ~16:40 UTC)

All repos on branch `claude/review-markdown-docs-bTSgu`. If the next session wants a fresh branch: start from the respective default branch (`main` / `master`), **not** from this branch (it is doc-focused and shouldn't be loaded with further code changes).

**Recommendation for the next session**: have the open PRs (#16, #26, #40, #17, #3, #18, #31) merged first before the M2 implementation, then a fresh branch `claude/m2-paragon-race-fix-<id>` for the 3 patches.

## What should DEFINITELY NOT happen in the next session

- **No** build (`make -j`).
- **No** PR merge without explicit user request.
- **No** force push, no `git reset --hard`.
- **No** edits to `share-public/CLAUDE.md` (the legacy 60 KB doc) — it is the deep reference, not the active doc set.
- **No** touch on the existing phase A/B PRs (separate, finalized doc restructuring).
