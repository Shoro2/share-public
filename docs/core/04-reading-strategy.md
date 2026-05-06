# core/04 — Reading strategy

> How an AI session (or a human) should navigate this tree without reading the entire codebase.

## Hard rules

- **Never load this whole tree.** It is intentionally split so you can read 1–3 small files per question.
- **Don't read `azerothcore-wotlk` source until you have the doc that points at it.** Lookups via `00-INDEX.md` and `03-file-locator.md` answer most "where is X?" questions in two reads.
- **Don't duplicate facts** that already live in [`../01`–`../10`](../) or [`../custom-spells/`](../custom-spells/00-overview.md). Link instead.

## The two-step lookup

1. **Have a question?** → [`00-INDEX.md`](./00-INDEX.md) ("by question" + "by subsystem" tables).
2. **Have a filename?** → [`03-file-locator.md`](./03-file-locator.md).

If neither helps, fall back to [`02-glossary.md`](./02-glossary.md) (term-based) or `grep` over `docs/core/`.

## Topic-file shape (so you know where the fact lives)

Every topic file follows the same six sections, in this order:

1. **Purpose** (1 sentence + cross-links).
2. **Critical files** — table of `path:line → role`.
3. **Key concepts** — bullet list, terms link to [`02-glossary.md`](./02-glossary.md).
4. **Flow / data shape** — short narrative or ASCII diagram, fits on one screen.
5. **Hooks & extension points** — where module authors plug in.
6. **Cross-references** — engine-side, project-side, external (wiki / Doxygen).

Skim the table of contents first; jump to the section you need.

## Question recipes

| You want to … | Read in this order |
|---|---|
| add a custom hook | [`scripting/02-hook-classes.md`](./scripting/02-hook-classes.md) → [`scripting/07-custom-hooks.md`](./scripting/07-custom-hooks.md) → `azerothcore-wotlk/functions.md` |
| add a prepared statement | [`database/02-prepared-statements.md`](./database/02-prepared-statements.md) → enum file under `Implementation/` |
| trace a packet from receive to handler | [`network/04-worldsocket.md`](./network/04-worldsocket.md) → [`network/05-worldsession.md`](./network/05-worldsession.md) → [`handlers/00-index.md`](./handlers/00-index.md) → handler doc |
| understand a spell cast | [`spells/01-cast-lifecycle.md`](./spells/01-cast-lifecycle.md) → [`spells/05-effects.md`](./spells/05-effects.md) (effect handler) |
| understand an aura/proc | [`spells/03-aura-system.md`](./spells/03-aura-system.md) → [`spells/06-proc-system.md`](./spells/06-proc-system.md) → [`../03-spell-system.md`](../03-spell-system.md) (user-side detail) |
| add a `creature_template` field | `creature_template` row in [`../09-db-tables.md`](../09-db-tables.md) → `ObjectMgr::LoadCreatureTemplates` in [`entities/10-object-mgr.md`](./entities/10-object-mgr.md) → [`entities/05-creature.md`](./entities/05-creature.md) |
| understand grid loading | [`maps/03-grids-cells.md`](./maps/03-grids-cells.md) → [`maps/04-grid-loading.md`](./maps/04-grid-loading.md) → [`maps/05-visibility.md`](./maps/05-visibility.md) |
| write a `BossAI` | [`ai/02-scripted-ai.md`](./ai/02-scripted-ai.md) → [`scripting/04-instance-scripts.md`](./scripting/04-instance-scripts.md) |
| add SQL migration | [`database/07-update-mechanism.md`](./database/07-update-mechanism.md) → wiki/Dealing-with-SQL-files |

## Avoiding redundancy with existing docs

If you find yourself about to write a paragraph about one of these, **stop and link instead**:

| If the topic is … | The canonical home is … |
|---|---|
| Repository purpose / list | [`../01-repos.md`](../01-repos.md) |
| Source-tree top level + module concept | [`../02-architecture.md`](../02-architecture.md) |
| `SpellScript`/`AuraScript` user authoring | [`../03-spell-system.md`](../03-spell-system.md) |
| AIO server↔client UI | [`../04-aio-framework.md`](../04-aio-framework.md) |
| Custom modules in this fork | [`../05-modules.md`](../05-modules.md) |
| Custom spell/item/NPC IDs | [`../06-custom-ids.md`](../06-custom-ids.md) |
| C++/SQL/Lua style + CI | [`../07-codestyle.md`](../07-codestyle.md) |
| Branch / log / commit conventions | [`../08-ai-workflow.md`](../08-ai-workflow.md) |
| All 304 DB tables | [`../09-db-tables.md`](../09-db-tables.md) |
| All 246 DBC files | [`../10-dbc-inventory.md`](../10-dbc-inventory.md) |
| Custom spell deep dive (per spec) | [`../custom-spells/`](../custom-spells/00-overview.md) |
| Logging system (`LOG_INFO`, levels, appenders) | `azerothcore-wotlk/doc/Logging.md` |
| Config policy (presets, env vars) | `azerothcore-wotlk/doc/ConfigPolicy.md` |
| Custom hooks added by this fork | `azerothcore-wotlk/functions.md` |

## File-size guardrails

- Soft cap **~12 KB / ~400 lines** per topic file.
- If you exceed it, split into `0X-topic-a.md` + `0X-topic-b.md` and update the parent `00-index.md`.
- Tables are denser than prose — prefer them for inventory-style content.
- Code snippets ≤ 30 lines; for longer, link to the source file.

## External docs

The official wiki and Doxygen are referenced from each topic file's "Cross-references" section. Use them as deep targets, do not copy their content.

| Wiki page | Used by core/ folder |
|---|---|
| `wiki/installation`, `wiki/install-with-docker` | `architecture/`, `server-apps/` |
| `wiki/hooks-script` | `scripting/` |
| `wiki/Create-a-Module` | `scripting/` |
| `wiki/Dealing-with-SQL-files` | `database/` |
| `wiki/How-to-test-a-PR` | this file |
| `wiki/commit-message-guidelines` | linked from [`../07-codestyle.md`](../07-codestyle.md) |
| `wiki/common-errors` (incl. `#ace00043`, `#ace00046`) | `architecture/`, `database/` |
| `wiki/contribute` | this file |
| `wiki/faq` | top-level "see also" |
| `wiki/how-to-use-changelog` | linked from [`../08-ai-workflow.md`](../08-ai-workflow.md) |
| `wiki/issue-tracker-standards` | this file |
| `wiki/project-versioning` | `architecture/` |
| `wiki/Upgrade-from-pre-2.0.0…`, `…3.0.0…` | `database/07-update-mechanism.md` (historical migrations) |
| `pages/doxygen/index.html` | every topic file (deep API reference) |

**Doxygen URL pattern** (verified by browsing on first successful fetch — current pattern is the standard `class<Name>.html` / `<File>_8h.html`):

```
https://www.azerothcore.org/pages/doxygen/class<ClassName>.html
https://www.azerothcore.org/pages/doxygen/<HeaderFileName>_8h.html
```

## Contributing to this tree

- Branch: `claude/<description>-<sessionId>` per repo (see [`../08-ai-workflow.md`](../08-ai-workflow.md)).
- Log every change in `claude_log.md`.
- One PR per subsystem in Phase 2 — keeps the diff reviewable.
- When upstream `azerothcore-wotlk` is pulled, sweep the `path:line` references that may have shifted (a CI check is on the wishlist).

## See also

- [`00-INDEX.md`](./00-INDEX.md), [`01-overview.md`](./01-overview.md), [`02-glossary.md`](./02-glossary.md), [`03-file-locator.md`](./03-file-locator.md).
- Wiki/Doxygen — see table above.
