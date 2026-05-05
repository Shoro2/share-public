# Phase A+B Wrap: Per-Repo doc convention (2026-05-01)

> Detail log for the multi-repo doc restructuring. Linked from `claude_log.md`.

## Goal

Establish the same lean 6-file doc convention in every module/core repo (i.e. all except `share-public`) so AI tools (Claude Code, etc.) can read project data reliably — without 25 K-token-limit errors or stream idle timeouts.

## Convention per repo

| File | Size | Purpose |
|-------|------:|-------|
| `INDEX.md` | <1 KB | entry point for AI — lists sibling files with size + purpose |
| `CLAUDE.md` | < 8 KB | **What/why** — purpose, role, custom IDs, DB table references (no mechanics detail!) |
| `data_structure.md` | < 6 KB | exact folder/file listing with one-liner descriptions |
| `functions.md` | < 15 KB | **How** — mechanics, hooks, function signatures, AIO handlers, config options |
| `log.md` | grows | minimal commit log (1 line per commit) |
| `todo.md` | small | open tasks with priority (`(high)` / `(medium)` / `(low)`) |

Cross-cutting stays centrally in `share-public`:
- `share-public/claude_log.md` = project-wide history + phase plans
- `share-public/AI_GUIDE.md` + `docs/` = project-wide docs, AI workflow

## Phase A — detail files created (earlier session)

Added in each of the 6 module/core repos (`mod-paragon`, `mod-paragon-itemgen`, `mod-loot-filter`, `mod-endless-storage`, `mod-auto-loot`, `azerothcore-wotlk`):

- `log.md` initially populated with the last ~10 commits
- `data_structure.md` with the folder/file tree
- `functions.md` with mechanics doc
- `mod-auto-loot` additionally got its first `CLAUDE.md` (didn't exist before)

## Phase A wrap — `todo.md` added (this session)

Per-repo new `todo.md` capturing the current state of open tasks (extracted from the `Known limitations` sections of the respective `functions.md` and reviews).

| Repo | Content focus |
|------|--------------------------|
| mod-auto-loot | Mining/herbalism/skinning missing; throttle cooldown |
| mod-loot-filter | SQL injection mitigation in Lua, bulk import/export, server defaults |
| mod-endless-storage | Doc drift (CLAUDE.md predates the March 2026 rewrite), bulk withdraw, crafting fallback |
| mod-paragon | SQL injection in Lua, C++↔Lua race condition, anti-farm |
| mod-paragon-itemgen | AH restriction blocked (no hook), BasePoints off-by-one, in-memory cache |
| azerothcore-wotlk | add `CanCreateAuction` hook, DBC validation CI |

## Phase A wrap — `08-ai-workflow.md` extended

`share-public/docs/08-ai-workflow.md` got a new **"Per-repo doc convention"** section (table of the 6 files + cross-cutting reference). Additionally a new **"Plan documentation (TODOs)"** section with the split:
- module-specific TODOs → `<repo>/todo.md`
- cross-repo roadmap → `share-public/claude_log.md`

Workflow step 6 was extended with the duty to also update `<repo>/log.md` and `<repo>/todo.md` on implementation commits.

## Phase B — slim CLAUDE.md (this session)

Per module/core repo the existing `CLAUDE.md` was rewritten:

- Removed: folder/file lists (now in `data_structure.md`), mechanics details (in `functions.md`), Known-Issues with `~~strikethrough~~` (open items in `todo.md`, completed ones cut).
- Kept: purpose, role in the overall project, custom-data index (IDs/tables/hook names), high-level mechanics (XP sources, scaling formula, tooltip system), license, cross-references to sibling files.

| Repo | Before | After | Reduction |
|------|-------:|--------:|----------:|
| mod-loot-filter | 9.6 KB | ~3.6 KB | -62 % |
| mod-endless-storage | 9.2 KB | ~3.9 KB | -58 % |
| mod-paragon | 13 KB | ~4.6 KB | -65 % |
| mod-paragon-itemgen | 14 KB | ~5.5 KB | -61 % |
| azerothcore-wotlk | 16 KB | ~4.6 KB | -71 % |
| mod-auto-loot | 4.1 KB (already lean) | unchanged | – |

All `CLAUDE.md` files are now **<6 KB** and therefore safely readable in a single `Read`/`get_file_contents` call.

## Phase B — INDEX.md added (this session)

`INDEX.md` was added to the 5 repos that were still missing one (`mod-loot-filter`, `mod-endless-storage`, `mod-paragon`, `mod-paragon-itemgen`, `azerothcore-wotlk`). `mod-auto-loot` already had one.

## Read/write strategies (lessons learned, now in 08-ai-workflow.md)

1. **Reading**: files >25 K tokens (truncation in `/tmp`) extract via `jq -r '.[1].text' > /tmp/file.md`, then `Read` with `offset/limit` chunked.
2. **Writing**: one file per `mcp__github__create_or_update_file`. Never 5+ files in parallel — stream idle timeout looms.
3. **Pattern consistency**: same file names in every repo (`INDEX.md`, `CLAUDE.md`, `data_structure.md`, `functions.md`, `log.md`, `todo.md`) → blindly navigable, no discovery search needed.

## Branch

`claude/review-markdown-docs-bTSgu` (in every repo).

## Status

- ✅ Phase A: detail files added in 6 repos
- ✅ todo.md added in 6 repos
- ✅ 08-ai-workflow.md extended with the per-repo doc convention
- ✅ Phase B: lean CLAUDE.md in 5 repos (mod-auto-loot already lean)
- ✅ INDEX.md added in 5 repos (mod-auto-loot already had one)
- ✅ claude_log.md updated with a wrap entry (link to this file)

## What was not done

- **no** PR on any repo (the user decides) — branch is pushed, ready for review.
- **no** touch to the legacy 60 KB `share-public/CLAUDE.md` itself — stays as a deep reference next to the new `docs/` structure. A possible phase C would dissolve it, but it isn't requested.
- **no** build or test against the server — pure documentation change.
