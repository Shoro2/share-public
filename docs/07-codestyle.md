# 07 — Code style

Concentrated excerpt of `azerothcore-wotlk/CLAUDE.md` plus project practice. CI is strict — C++ is built with `-Werror`, codestyle-cpp.py / codestyle-sql.py block PRs.

## C++ (AzerothCore standard)

- 4-space indent, **no tabs**
- UTF-8, **LF** line endings
- max **80 characters** per line
- no braces around single-line `if`/`else`/`for`/`while`
- multi-line block braces on a new line (Allman style), not trailing
- `'f'` suffix for float literals: `234.3456f`
- never multiple pointers on one line
- headers need include guards (`#ifndef __NAME_H` / `#define __NAME_H`)
- `{}` with `fmt` formatting in logs/output (not `%u`/`%s`)
- double semicolons `;;` forbidden, no trailing whitespace, no two consecutive blank lines

### Type syntax

- `Type const*` instead of `const Type*` — e.g. `Player const* player`
- `auto const&` instead of `const auto&`
- `static` before the type: `static uint32 someVar`
- WoW types via `Define.h`: `uint8`, `uint16`, `uint32`, `int32`, … (not `uint32_t`)

### Naming conventions

| Element | Convention | Example |
|---------|------------|----------|
| Public/protected member | `UpperCamelCase` | `SomeGuid`, `ShadowBoltTimer` |
| Private member | `_lowerCamelCase` | `_someGuid`, `_count` |
| Methods | `UpperCamelCase` | `DoSomething(uint32 someNumber)` |
| Parameters | `lowerCamelCase` | `someNumber`, `targetPlayer` |
| Constants/enums | `UPPER_SNAKE_CASE` with prefix | see below |
| WorldObjects | `Type* var;` | `Player* player;`, `Creature* creature;` |

Standard prefixes for constants:
- Spells: `SPELL_MAGE_FIREBALL`, `SPELL_GENERIC_BERSERK`, `SPELL_CUSTOM_*`
- NPCs: `NPC_IRON_CONSTRUCT`, items: `ITEM_*`, GameObjects: `GO_*`, quests: `QUEST_*`
- Texts: `SAY_AGGRO`, `EMOTE_JETS`
- Events: `EVENT_SPELL_SCORCH`
- Data: `DATA_BOSS_ID`, achievements: `ACHIEV_*`, models: `MODEL_*`

### CI-enforced bans (codestyle-cpp.py)

| Forbidden | Use instead |
|----------|-------------|
| `GetTypeId() == TYPEID_PLAYER` | `IsPlayer()`, `IsCreature()`, `IsItem()`, `IsGameObject()`, `IsDynamicObject()` |
| `Flags & ITEM_FLAG_*` | `HasFlag(ItemFlag)`, `HasFlag2(ItemFlag2)`, `HasFlagCu(ItemFlagsCustom)` |
| direct `UNIT_NPC_FLAGS` | `GetNpcFlags()`, `HasNpcFlag()`, `SetNpcFlag()`, `RemoveNpcFlag()` |
| direct `ITEM_FIELD_FLAGS` | `IsRefundable()`, `IsBOPTradable()`, `IsWrapped()` |
| `ObjectGuid::GetCounter()` directly | `ObjectGuid::ToString().c_str()` |
| `const Type*`, `const auto&` | `Type const*`, `auto const&` |
| Tabs, multiple blank lines, trailing whitespace | see above |
| Opening brace on the same line as `if`/`else` | new line |

### File header

Every C++ source file starts with the GPL v2 header:

```cpp
/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify
 * ...
 */
```

## SQL style

- Backticks around table and column names: `` `creature_template` ``
- Single quotes for strings, no quotes for numeric values
- **DELETE before INSERT** (no `REPLACE`)
- DELETE/UPDATE must include at least the primary key in `WHERE`
- prefer `IN (1, 2, 3)` for multiple values
- variables for repeated values: `SET @ENTRY := 7727;`
- combine multiple rows in one `INSERT`
- **flag updates**: bitwise (`flags | 0x4`, `flags & ~0x8`) — never overwrite the entire field
- table naming: `snake_case`, columns: `UpperCamelCase` (acronyms uppercase: `PositionX`, `DisplayID`, `ItemGUID`)
- `INT` instead of `INT(11)`, never `MEDIUMINT`
- engine: **InnoDB only** (CI), charset `utf8mb4`, collation `utf8mb4_unicode_ci` (`utf8mb4_bin` for name columns)
- every statement ends with a semicolon
- 4 spaces, no tabs, no trailing whitespace, no double blank lines
- **`entryorguid` lowercase** (not `EntryOrGuid`)
- `broadcast_text` edits only with sniff data and maintainer approval
- never `DELETE` from `creature_template`/`gameobject_template`/`item_template`/`quest_template`
- place SQL files with a random filename in `data/sql/updates/pending_db_*/`, **not** in `base/` or `archive/`

## Lua / Eluna / AIO

- **Tab indentation** (Eluna/AIO convention)
- AIO handler pattern: `AIO.AddHandlers("NAME", handlers)` — extend the table in place after registration
- AIO Msg pattern: `AIO.Msg():Add("Name", "Handler", ...):Send(player)` (server) or `:Send()` (client)
- `player` is **always** the first argument in EVERY handler — also on the client (there: a string with the player's name)
- `AIO.AddAddon()` at the top of client files: `if AIO.AddAddon() then return end`
- `AIO.AddOnInit(function(msg, player) … return msg end)` for login data
- global handler table for hot-reload risk (see [04-aio-framework.md](./04-aio-framework.md#re-registration-trap))
- max 15 arguments per `msg:Add()` block

## Commit message format

Conventional Commits:

```
Type(Scope/Subscope): Short description (max 50 chars)
```

| Type | For what |
|------|-------|
| `feat` | new feature |
| `fix` | bugfix |
| `refactor` | restructure without behavior change |
| `style` | purely cosmetic (whitespace, etc.) |
| `docs` | documentation |
| `test` | tests |
| `chore` | maintenance (imports, tooling) |

Scopes: `Core` (C++), `DB` (SQL).
Subscopes: `Spells`, `Scripts`, `Server`, `SAI`, `Ulduar`, `ICC`, ...

Examples:
- `fix(Core/Spells): Fix damage calculation for Fireball`
- `fix(DB/SAI): Missing spell to NPC Hogger`
- `feat(Core/Commands): New GM command to do something`
- `chore(DB): import pending files`

**Rules**: subject capitalized, imperative mood, no period at the end, max 50 chars title, max 72 chars per body line.

## Branch naming

For AI sessions:
```
claude/<description-with-hyphens>-<sessionId>
```
Examples: `claude/fix-lifeleech-caster-0yYoZ`, `claude/review-markdown-docs-bTSgu`.

**Important**: one branch per repo — the same branch name can (and should) exist in parallel across multiple repos when cross-repo work is needed.

## CI pipelines (azerothcore-wotlk)

| Workflow | Trigger | What |
|----------|---------|-----|
| `codestyle.yml` | `src/` changes | C++ codestyle + cppcheck |
| `sql-codestyle.yml` | `data/` changes | SQL codestyle |
| `core-build-pch.yml` | all | clang-15+18 Linux with PCH |
| `core-build-nopch.yml` | all | clang-15+18, gcc-14 without PCH |
| `macos_build.yml`, `windows_build.yml` | all | OS compatibility |
| `core_modules_build.yml` | all | module compile check |

Compiled with `-Werror`: any warning fails the build.
