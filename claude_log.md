# Project change log

This document is the central history of all work steps, changes, and plans in the WoW server project. Every entry contains a timestamp, the affected repository, and a description of the change.

---

## Change history

### 2026-05-01

#### [mod-ale] Onboarding: per-repo doc convention applied to the new repo

- **Timestamp**: 2026-05-01
- **Repo**: mod-ale
- **Context**: Repo `shoro2/mod-ale` is new in the GitHub MCP authorization. It is a fork of [Eluna](https://github.com/ElunaLuaEngine/Eluna), divergent under the name **ALE (AzerothCore Lua Engine)**, and provides the Lua/MoonScript script runtime for all the other Lua/AIO-based modules of this project (mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage, plus the `share-public/AIO_Server` framework).
- **Changes**:
  - Applied the 6-file doc convention (analogous to phases A/B): `INDEX.md`, `CLAUDE.md`, `data_structure.md`, `functions.md`, `log.md`, `todo.md`.
  - `CLAUDE.md` highlights the engine role (infrastructure, not a gameplay module) and lists all consumers + config options from `mod_ale.conf.dist` and `CMakeLists.txt`.
  - `data_structure.md` flags the AI-read-risk files: `LuaFunctions.cpp` (~96 KB), `LuaEngine.cpp` (~54 KB), `Hooks.h` (~30 KB), `LuaEngine.h` (~30 KB), `ALE_SC.cpp` (~40 KB) — search them symbolically via `grep`, do not read the whole file.
  - `functions.md` documents hook classes (Server/Player/Creature/GameObject/Item/Spell/Group/Guild/Map/BG), the most important Lua globals (`*DBQuery`/`*DBExecute`, Player API), `EventMgr`, `BytecodeCache`, `FileWatcher`, reload behavior, config impact, and the security pattern around the missing prepared statements (validation lib + atomic single-UPDATE pattern as in the M2 fix).
- **Validation lib NOT integrated**: ALE itself only provides the `*DBQuery`/`*DBExecute` API and does not make its own calls with player-supplied input. Validation is the consumer's job — already in place in `mod-paragon`, `mod-loot-filter`, `mod-endless-storage`.
- **Cross-refs added**:
  - `share-public/AI_GUIDE.md`: included mod-ale in the repo map, marked it as a build/runtime dependency of the other Lua modules; added the read-risk files to the "Avoid direct full-text reads" list.
  - `share-public/claude_log.md`: this entry.
- **Affected files**:
  - `mod-ale/INDEX.md` (NEW)
  - `mod-ale/CLAUDE.md` (NEW)
  - `mod-ale/data_structure.md` (NEW)
  - `mod-ale/functions.md` (NEW)
  - `mod-ale/log.md` (NEW)
  - `mod-ale/todo.md` (NEW)
  - `share-public/AI_GUIDE.md` (extended repo map)
  - `share-public/claude_log.md` (this entry)
- **Branches**:
  - `mod-ale`: `claude/mod-ale-onboarding-uElRt`
  - `share-public`: `claude/wow-server-docs-bugfix-uElRt`
- **Commits** (mod-ale):
  - `704cc13` — docs: add INDEX.md
  - `b2345d6` — docs: add CLAUDE.md
  - `20dfb83` — docs: add data_structure.md
  - `d412502` — docs: add functions.md
  - `8eac771` — docs: add log.md
  - `0d896be` — docs: add todo.md
- **Notes**: source state is `master` @ `1ab53ba`. Currently **no custom patches** — pure mirror of upstream. If project-specific changes to the engine become necessary, they belong as a commit at the top of `mod-ale/log.md` and cross-referenced here.

#### [mod-paragon] Fix: C++ ↔ Lua race condition on Paragon point allocation (M2)

- **Timestamp**: 2026-05-01
- **Repo**: mod-paragon
- **Problem**: Lua `AllocatePoint`/`DeallocatePoint` wrote the stat column and `unspent_points` as two separate asynchronous `CharDBExecute` UPDATEs. If the player changed map within a few ms, C++ `ApplyParagonStatEffects()` read an inconsistent state → integrity check `(totalAllocated + unspent) == level*PPL` failed → destructive reset wiped all stat allocations, the player saw "There was an error loading your Paragon points, please reallocate them!".
- **Solution**:
  1. New function `Paragon.UpdateAllocationAndUnspent(characterID, dbColumn, newValue, newUnspent)` in `Paragon_Data.lua`. Writes the stat column + `unspent_points` in a **synchronous** `CharDBQuery` UPDATE — the next C++ read query (on map change) is guaranteed to see both new values.
  2. `Paragon_Server.lua` `AllocatePoint`/`DeallocatePoint` call the new atomic function instead of the two separate async updates.
  3. `ParagonPlayer.cpp` `ApplyParagonStatEffects()` replaces the destructive reset with soft recovery: on a (theoretically no longer reachable) mismatch only `unspent_points` is recomputed (`level*PPL - totalAllocated`, clamped ≥0), stats stay untouched, auras are still applied. The destructive reset logic stays only on the NPC reset path (`ParagonNPC.cpp`).
- **Affected files**:
  - `Paragon_System_LUA/Paragon_Data.lua`
  - `Paragon_System_LUA/Paragon_Server.lua`
  - `src/ParagonPlayer.cpp`
- **Branch**: `claude/m2-paragon-race-fix-uElRt`
- **Commits**:
  - `8d8ec2d` — fix(Paragon/Lua): add atomic UpdateAllocationAndUnspent
  - `f856c7b` — fix(Paragon/Lua): use atomic update in Allocate/DeallocatePoint
  - `8222889` — fix(Paragon/C++): soft-recover paragon mismatch instead of destructive reset
  - `7d4c46f` — docs(todo): remove M2 race-condition item (fixed)
  - `32865ef` — docs(log): record M2 race-condition fix commits
- **Validation**: to be tested in-game by the user — before fix: allocate a point + immediately switch map → reset; after fix → point stays allocated, no reset.
- **Notes**: the M2 plan comes from `claude_log_2026-05-01_session_handoff.md`. Eluna provides no synchronous `CharDBExecute`, hence the unusual choice to send an UPDATE via `CharDBQuery` — its implementation blocks until the commit, which is exactly what we want here.

#### [Multi-Repo] Docs: Phase A — modular per-repo doc files (log.md / data_structure.md / functions.md)

- **Timestamp**: 2026-05-01
- **Repos**: azerothcore-wotlk, mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage, mod-auto-loot
- **Goal**: make the central CLAUDE.md files in every repo more readable by spreading content consistently across 4 focused files per repo. Avoids the 25 K-token and stream-timeout errors when reading the growing monolith CLAUDE.md.
- **Newly created per repo**:
  - `log.md` — minimal commit log (1 line per commit, with SHA link). Initial population with the last ~10 commits from `git log`.
  - `data_structure.md` — file/folder tree of the repo plus file purposes and size hints (which files are at the read limit, which are binary).
  - `functions.md` — mechanics and function reference (hooks, AIO handlers, DB queries, config, known limitations).
- **Special case mod-auto-loot**: had no `CLAUDE.md` at all — newly created in this phase (4 files instead of 3). Content reconstructed from `src/mod_auto_loot.cpp` and project-central logs.
- **Special case azerothcore-wotlk** (fork): `log.md` focuses on **custom changes** (reagent hooks, Spell.dbc), upstream sync merges only as a collective reference.
- **Existing `CLAUDE.md` files**: **not** touched in this phase. Phase B (separate) will reduce them to pure content docs and remove redundancy with `data_structure.md` / `functions.md`.
- **Branch**: `claude/review-markdown-docs-bTSgu` (in every repo).
- **Commits** (per repo):
  - mod-auto-loot: `cc0b452` (log.md), `756b887` (data_structure.md), `8f13cbf` (functions.md), `603d3e7` (CLAUDE.md NEW)
  - mod-loot-filter: `855cdef`, `ee7449f`, `727e3ed`
  - mod-endless-storage: `b77536b`, `d7e4c9a`, `3da60d2`
  - mod-paragon: `2d39f62`, `0f8c07f`, `78c2319`
  - mod-paragon-itemgen: `8a1fd2b`, `08ed1e7`, `1749558`
  - azerothcore-wotlk: `2348b52`, `1d558eb`, `2f3bafc`
- **Findings during phase A**:
  - **mod-endless-storage**: actual architecture (Lua-only since March 2026) deviated from the legacy `CLAUDE.md` state — phase A corrected this in `functions.md` and `data_structure.md`; the legacy CLAUDE.md describes outdated C++ crafting hooks.
  - **mod-paragon-itemgen**: `src/ParagonItemGen.cpp` at ~37 KB is close to the read limit — use chunked `Read offset/limit` or targeted `grep` if needed. SQL file `paragon_itemgen_enchantments.sql` (>100 KB for 11,323 entries) only via `grep`, never read whole.
  - **mod-paragon**: `ParagonPlayer.cpp` at ~26 KB also at the limit, but still readable.
- **Strategy for AI readability (in addition to the phase 0 modular docs in share-public)**:
  1. Same file names per repo (`log.md`, `data_structure.md`, `functions.md`, `CLAUDE.md`) → blindly navigable.
  2. Each new file <12 KB, in practice 2-8 KB → individually readable.
  3. Cross-refs in every file to its sibling files and to `share-public/AI_GUIDE.md`.
- **Phase B (planned separately, not in this session)**:
  - For each repo, walk the legacy `CLAUDE.md`, remove content that now lives in `data_structure.md`/`functions.md`, keep only pure content/purpose description.
  - Before each refactor: a before/after diff plan for user approval.
  - Goal: every `CLAUDE.md` < 8 KB, redundancy-free with its sibling files.

#### [share-public] Docs: modular AI doc structure (`AI_GUIDE.md` + `docs/`)

- **Timestamp**: 2026-05-01
- **Repo**: share-public
- **Problem**: the central `share-public/CLAUDE.md` has grown to ~60 KB / 1284 lines and can no longer be read reliably by AI tools (Claude Code, etc.) via `Read`/`mcp__github__get_file_contents` — it regularly trips the 25,000-token limit error. Additionally, `Stream idle timeout` errors appear when too many/large tool calls are bundled.
- **Solution**: a new modular doc structure as the preferred entry point for AI sessions:
  - `AI_GUIDE.md` (~6.4 KB) — top-level navigation: repo map, reading strategy, "where do I find what?".
  - `docs/01-repos.md` — all 7 repos in detail (mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-auto-loot, mod-endless-storage, azerothcore-wotlk, share-public).
  - `docs/02-architecture.md` — server architecture, 3 DBs, module system, hooks, logging.
  - `docs/03-spell-system.md` — SpellScripts, AuraScripts, full proc chain, corrected ProcFlags values, DBC system, BasePoints off-by-one.
  - `docs/04-aio-framework.md` — AIO APIs, handler pattern, re-registration trap, code caching, message limits.
  - `docs/05-modules.md` — depth per module: mechanics, DB tables, hooks, config options.
  - `docs/06-custom-ids.md` — custom IDs registry: spells (100xxx, 900xxx), enchants (900001-916666, 920001, 950001-950099), NPCs, items, slash commands, reserved ranges.
  - `docs/07-codestyle.md` — C++/SQL/Lua conventions, CI-enforced bans, commit format.
  - `docs/08-ai-workflow.md` — reading strategy to avoid token/timeout errors, write strategy (1 file per tool call), branch/logging conventions.
  - `README.md` extended from 14 B to ~2.7 KB: points to `AI_GUIDE.md`, lists all docs/ and repos.
- **Strategy to avoid the read errors** (now documented in `docs/08-ai-workflow.md`):
  1. Each `docs/` file <12 KB → no more 25 K-token error on Read.
  2. AI tools start at `AI_GUIDE.md`, then load only the relevant chapter.
  3. When the legacy 60-KB `CLAUDE.md` must be read: extract the truncation file (`/root/.claude/projects/.../tool-results/*.txt`) via `jq -r '.[1].text' > /tmp/file.md`, then `Read offset/limit` chunked.
  4. Write side: `mcp__github__create_or_update_file` once per file, not batched → no `Stream idle timeout`.
- **Backwards compatibility**: legacy `CLAUDE.md` stays unchanged (all module CLAUDE.md files still link to it). The new structure adds, it does not replace.
- **Affected files**:
  - `AI_GUIDE.md` (NEW)
  - `docs/01-repos.md` (NEW)
  - `docs/02-architecture.md` (NEW)
  - `docs/03-spell-system.md` (NEW)
  - `docs/04-aio-framework.md` (NEW)
  - `docs/05-modules.md` (NEW)
  - `docs/06-custom-ids.md` (NEW)
  - `docs/07-codestyle.md` (NEW)
  - `docs/08-ai-workflow.md` (NEW)
  - `README.md` (extended)
  - `claude_log.md` (this entry)
- **Branch**: `claude/review-markdown-docs-bTSgu`
- **Commits**: `222607f` (AI_GUIDE), `72fb3c1` (01-repos), `f663592` (02-architecture), `0a7a586` (03-spell-system), `44b8a43` (04-aio), `9233be9` (05-modules), `2bf9bef` (06-ids), `7a194de` (07-codestyle), `6cfa549` (08-workflow), `89a4406` (README)
- **Notes**: sources for the synthesis: existing `CLAUDE.md` (60 KB, read in chunks), `claude_log.md` (35 KB), `claude_log_2026-04-27_custom_spells_review.md`, all module CLAUDE.md (azerothcore-wotlk, mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage), `mod-auto-loot/src/mod_auto_loot.cpp` (no CLAUDE.md present — module behavior reconstructed from the source). `Dcore Concept.pdf` was classified by the user as partly outdated and was not included in detail, but is linked as a concept pitch in the new `AI_GUIDE.md`.

### 2026-04-28

#### [mod-paragon] Fix: Life Leech does not trigger for casters with pets/totems

- **Timestamp**: 2026-04-28
- **Repo**: mod-paragon
- **Problem**: the Life Leech stat only healed when the player themselves was the `attacker` in `Unit::DealDamage`. This dropped the heal for all caster specs whose main damage source is a pet or totem (Demonology Warlock with Felguard, Frost Mage with Water Elemental, Beast Mastery Hunter, all totem Shaman specs, the Frost DK's Dancing Rune Weapon, Mind Control). Direct player spell damage (Mage Fireball, Priest Smite, Warlock Shadow Bolt) worked — but the lookup `attacker->ToPlayer()` did not match for pets/totems, since their `attacker` is a `Creature`.
- **Solution**: `ParagonLifeLeech::OnDamage` now resolves the player owner of the attacker via `Unit::GetCharmerOrOwnerPlayerOrPlayerItself()`. With this, leech triggers for all sources controlled by the player (player, pet, totem, charmed unit). Additionally, self/friendly damage (fall damage, environmental, own spell splashes) is excluded via a victim-owner check, so the player does not heal back from their own HP loss.
- **Affected files**:
  - `mod-paragon/src/ParagonPlayer.cpp` (`ParagonLifeLeech::OnDamage`)
- **Branch**: `claude/fix-lifeleech-caster-0yYoZ`

### 2026-03 (archived)

> Earlier entries from 2026-03-22 down to 2026-03-18 are archived in [`claude_log_2026-03.md`](./claude_log_2026-03.md). Topics: mod-paragon big+small stat aura pairs, Paragon NPC/Lua/UI overhaul, mod-paragon-itemgen 5-slot enchantment system, mod-loot-filter pickup/auto-sell, mod-endless-storage materials drop, AzerothCore Spell.dbc corruption fix and validation, mod-auto-loot creation.

---

## Open plans and TODOs

> **As of 2026-05-01**: most original TODOs are implemented. Active follow-up work see phase B (CLAUDE.md refactor per module, planned for a separate session).

#### [azerothcore-wotlk] Spell.dbc corruption resolved + validation built in (2026-03-18)

- **Repo**: azerothcore-wotlk, ac-share
- **Change**: restored `share/dbc/Spell.dbc` from a clean backup; 6 safeguards in `share-public/python_scripts/copy_spells_dbc.py` (size check, string-table null byte, duplicate detection, format consistency, source≠target, post-write verify).
- **Verified**: 49,880 records, 0 duplicates, 17 custom 900xxx + 17 custom 100xxx spells present.
- **Status**: ✅ done.

### Phase B (planned)

- [ ] Per repo, walk the existing `CLAUDE.md`, remove content that now lives in `data_structure.md` and `functions.md`, keep only pure content/purpose docs.
- [ ] Before/after diff plan for user approval.
- [ ] Goal: every `CLAUDE.md` < 8 KB, redundancy-free.

### Known leftovers

- [ ] **mod-paragon-itemgen: AH restriction** — blocked: AzerothCore has no `CanCreateAuction` hook, `OnAuctionAdd` is void. Cursed items are soulbound anyway.
- [ ] **mod-paragon: anti-farm measures** — no cooldowns/DR on XP sources.
- [ ] **mod-paragon: SQL injection risk in the Lua layer** — Eluna without prepared statements, still string-concat. Mitigation: server-side validation of handler args.

---

## Format template for new entries

```markdown
### YYYY-MM-DD

#### [repo-name] Short description

- **Timestamp**: YYYY-MM-DD HH:MM (UTC+1)
- **Repo**: repository-name
- **Changes**:
  - Description of change 1
  - Description of change 2
- **Affected files**: `file1.cpp`, `file2.sql`
- **Commit**: `abc1234` (if committed)
- **Branch**: `branch-name`
- **Notes**: additional context information
```
