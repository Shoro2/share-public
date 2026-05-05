# 08 — AI workflow

Concrete marching orders for AI sessions on the project. Core ideas: **read small, write small, log everything.**

## 1. Reading strategy (avoids tool errors)

Three error classes regularly come up when large files are read carelessly:

| Error | Cause | Workaround |
|--------|----------|------------|
| `result (NN characters) exceeds maximum allowed tokens` | file > ~25 K tokens (~80 KB text) on `mcp__github__get_file_contents` | the tool automatically writes the result to `/root/.claude/projects/.../tool-results/*.txt` — read it from there in chunks |
| `File content (NN tokens) exceeds maximum allowed tokens (25000)` | `Read` without `limit:` on a large file | always set `offset` + `limit` (e.g. `limit: 300`) |
| `Stream idle timeout — partial response received` | too long / too many parallel tool calls in one response | issue each `mcp__github__create_or_update_file` separately, not batched; keep output short between calls |

### Recommended order

1. **Always start with [`AI_GUIDE.md`](../AI_GUIDE.md)** — smallest entry point, links all detail documents.
2. **Load only the relevant `docs/` chapter** — all <12 KB.
3. **Per module repo** the same 4-file convention applies (see "Per-repo doc convention" below):
   - `INDEX.md` first (entry, ~1 KB),
   - `CLAUDE.md` for purpose/contents,
   - `data_structure.md` for folders/files,
   - `functions.md` for mechanics/hooks/config,
   - `log.md` for commit history,
   - `todo.md` for open tasks.
4. **For code/SQL/configs**: target `mcp__github__get_file_contents` with a path. If a file is > 60 KB, identify single symbols via `search_code` first.
5. **For the legacy `CLAUDE.md` in `share-public` (60 KB) when needed**:
   ```
   mcp__github__get_file_contents owner=shoro2 repo=share-public path=CLAUDE.md
       → truncation file /root/.claude/projects/.../tool-results/*.txt
   jq -r '.[1].text' <file>.txt > /tmp/sp_claude.md
   grep -E '^#' /tmp/sp_claude.md   # find sections
   Read file_path=/tmp/sp_claude.md offset=N limit=300  # read chunks
   ```
6. **For `mysql_column_list_all.txt` (huge)** only via `grep` for table names:
   ```
   grep '^`creature_template`' mysqldbextracts/mysql_column_list_all.txt
   ```
7. **DBC files are binary** — never read as text. Edit via `python_scripts/patch_dbc.py` / `copy_spells_dbc.py` or via DB override tables (`*_dbc`).

## 2. Per-repo doc convention

Every module/core repo (i.e. **all except** `share-public`) has shared the same file convention since 2026-05:

| File | Size | Purpose |
|-------|-------|-------|
| `INDEX.md` | < 1 KB | entry point; lists the other files with size + one-liner |
| `CLAUDE.md` | < 8 KB | **Content/purpose** — what is this module, what role does it play, which IDs/DB tables belong to it (no mechanics detail!) |
| `data_structure.md` | < 6 KB | exact folder/file listing with one-liner descriptions |
| `functions.md` | < 15 KB | mechanics, hooks, function signatures, config options, AIO handlers — the "how does it work?" details |
| `log.md` | grows | minimal change log, one line per commit with hash link |
| `todo.md` | small | open tasks with priority (`(high)`/`(medium)`/`(low)`); completed items are **removed** and documented in `log.md` (not crossed out) |

**Cross-cutting** lives centrally in `share-public`:
- `share-public/claude_log.md` = cross-repo history + larger reviews
- `share-public/AI_GUIDE.md` + `docs/` = project-wide documentation

## 3. Writing strategy (avoids stream timeouts)

- **One file per `mcp__github__create_or_update_file` call.** Don't try to bundle 5+ files via `push_files` if the contents are each >5 KB — the stream may idle-timeout.
- **Keep output between tool calls short.** Long explanatory text between calls increases timeout risk.
- **Parallel tool calls only when small and idempotent.** Max ~3 parallel `get_file_contents` reads at once.
- **Existing files**: before `Edit`/`create_or_update_file` fetch the SHA via `get_file_contents`. The SHA is in the result's `sha` field.
- **Updating large files**: copy locally to `/tmp/`, edit with `Edit`/`Write` locally, then upload via `create_or_update_file` with `content` and the old `sha`.

## 4. Branch conventions

- **Branch per repo**: `claude/<description>-<sessionId>` (e.g. `claude/review-markdown-docs-bTSgu`). Same branch name across all repos involved in the session.
- **Push** with `git push -u origin <branch>`. On network failure max 4 retries with exponential backoff (2s, 4s, 8s, 16s).
- **Never destructive Git commands** (`reset --hard`, `push --force`, `branch -D`) without explicit user instruction.
- **Don't skip hooks** (`--no-verify`, `--no-gpg-sign`) unless explicitly allowed.
- **Never `--amend`** on already-pushed commits — create a new commit.
- **No PRs without explicit user request.** Branch is pushed, the user decides about PRs.

## 5. Commit conventions

Conventional Commits — see [07-codestyle.md](./07-codestyle.md#commit-message-format). Short form:

```
feat(Core/Spells): Add Life Leech stat
fix(DB/SAI): Missing spell to NPC Hogger
docs: Restructure AI guide into modular docs/
chore(DB): import pending files
```

## 6. Logging duty (`claude_log.md` + `log.md`)

There are **two** log levels:

### A) Cross-repo / project-wide: `share-public/claude_log.md`

**Every** non-trivial change to a project repo is recorded here. Format:

```markdown
### YYYY-MM-DD

#### [repo-name] Short description

- **Timestamp**: YYYY-MM-DD (HH:MM optional)
- **Repo**: repository-name
- **Problem** / **Changes** / **Solution**: short description
- **Affected files**:
  - `path/to/file.cpp`
  - `path/to/file.sql`
- **Branch**: `claude/<name>-<id>`
- **Commit**: `abc1234` (if known)
```

Sort by date **descending** — newest entry on top, immediately below the `## Change history` section.

For larger reviews / sessions whose content alone produces several KB of doc, create a **separate log file** (example: `claude_log_2026-04-27_custom_spells_review.md`) and link it from the main `claude_log.md`.

### B) Per repo: `<repo>/log.md`

Minimal log, one line per commit:

```markdown
- 2026-05-01 `abc1234` — feat(Core/Spells): Add Life Leech stat
```

This file contains **nothing** about plans / TODOs / context — only the bare commit trail. Plan/TODO belongs in `<repo>/todo.md` or `share-public/claude_log.md`.

## 7. Plan documentation (TODOs)

There are two storage locations:

| What | Where |
|-----|-------|
| Module-specific open task (gameplay, code, tests) | `<repo>/todo.md` with priority tag `(high)/(medium)/(low)` |
| Cross-repo roadmap, phase plan, completed major plans | `share-public/claude_log.md` under `## Open plans and TODOs` |

`todo.md` format:

```markdown
## Security
- [ ] **(medium)** Description — rationale
## Performance
- [ ] **(low)** ...
```

**Completed items** in `todo.md` are **removed** (not crossed out) and documented in the `log.md` commit entry of the resolving commit. That keeps `todo.md` always reflecting the current open items.

## 8. Workflow step by step

1. **Read** `AI_GUIDE.md`, the matching `docs/` chapter, and in the affected module repo `INDEX.md` + the relevant 4-file section.
2. **Check `todo.md`** in the module repo — your task may already be listed.
3. **TODO list** via `TodoWrite` for non-trivial tasks (≥3 steps).
4. **Create the branch** (`mcp__github__create_branch`) — `claude/<description>-<sessionId>`.
5. **Implement**, small commits, Conventional Commits.
6. **Update**:
   - `<repo>/log.md` — new commit line(s)
   - `<repo>/todo.md` — remove completed items
   - `share-public/claude_log.md` — date entry with repo tag
   - on structural changes: keep `<repo>/data_structure.md` up to date
   - on new mechanics/hooks: extend `<repo>/functions.md`
7. **Push** with retries.
8. **For UI changes**: test with `/aio reset` or character reload, otherwise old closures stay active (see [04-aio-framework.md](./04-aio-framework.md#re-registration-trap)).
9. **Summary** to the user: name the branch URL, what changed, what didn't.

## 9. Language

- **Logs / docs**: English (project language)
- **Code comments**: English
- **Commit messages**: English (Conventional Commits)
- **Markdown table headers**: as needed — mixing allowed, when in doubt English.

## 10. What NOT to do

- **No** unprompted build (`make -j`) — takes long, blocks the session
- **no** unprompted SQL execution against production DBs
- **no** PR without user request
- **no** `git push --force`, `git reset --hard`, `git branch -D` without instruction
- **no** edits to `data/sql/base/` or `data/sql/archive/` (CI warning, maintainer approval required)
- **do not** modify config/settings files (`settings.local.json` etc.) without being explicitly asked
- **no** multi-file pushes (`push_files` with >2 files of >5 KB each) — stream timeout risk
- **no** full-text reads of files ≥ 60 KB without a chunking strategy
- **don't** cross out / tick `todo.md` items — remove them and add to `log.md`
