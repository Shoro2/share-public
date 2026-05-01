# 07 — Code-Style

Konzentrierter Auszug aus `azerothcore-wotlk/CLAUDE.md` plus Projekt-Praxis. CI ist scharf — bei C++ wird mit `-Werror` gebaut, codestyle-cpp.py / codestyle-sql.py blocken PRs.

## C++ (AzerothCore Standard)

- 4 Spaces Einrückung, **keine Tabs**
- UTF-8, **LF**-Zeilenenden
- max **80 Zeichen** pro Zeile
- keine Klammern um einzeilige `if`/`else`/`for`/`while`
- Multi-Line-Block-Klammern auf neuer Zeile (Allman-Stil), nicht trailing
- `'f'`-Suffix für Float-Literals: `234.3456f`
- niemals mehrere Pointer auf einer Zeile
- Header brauchen Include-Guards (`#ifndef __NAME_H` / `#define __NAME_H`)
- `{}` mit `fmt`-Formatierung in Logs/Output (nicht `%u`/`%s`)
- doppelte Semikolons `;;` verboten, kein Trailing-Whitespace, keine zwei Leerzeilen hintereinander

### Type-Syntax

- `Type const*` statt `const Type*` — z.B. `Player const* player`
- `auto const&` statt `const auto&`
- `static` vor Typ: `static uint32 someVar`
- WoW-Types via `Define.h`: `uint8`, `uint16`, `uint32`, `int32`, … (nicht `uint32_t`)

### Naming-Konventionen

| Element | Konvention | Beispiel |
|---------|------------|----------|
| Public/Protected Member | `UpperCamelCase` | `SomeGuid`, `ShadowBoltTimer` |
| Private Member | `_lowerCamelCase` | `_someGuid`, `_count` |
| Methoden | `UpperCamelCase` | `DoSomething(uint32 someNumber)` |
| Parameter | `lowerCamelCase` | `someNumber`, `targetPlayer` |
| Konstanten/Enums | `UPPER_SNAKE_CASE` mit Prefix | siehe unten |
| WorldObjects | `Type* var;` | `Player* player;`, `Creature* creature;` |

Standard-Prefixe für Konstanten:
- Spells: `SPELL_MAGE_FIREBALL`, `SPELL_GENERIC_BERSERK`, `SPELL_CUSTOM_*`
- NPCs: `NPC_IRON_CONSTRUCT`, Items: `ITEM_*`, GameObjects: `GO_*`, Quests: `QUEST_*`
- Texte: `SAY_AGGRO`, `EMOTE_JETS`
- Events: `EVENT_SPELL_SCORCH`
- Daten: `DATA_BOSS_ID`, Achievements: `ACHIEV_*`, Models: `MODEL_*`

### CI-enforced Verbote (codestyle-cpp.py)

| Verboten | Stattdessen |
|----------|-------------|
| `GetTypeId() == TYPEID_PLAYER` | `IsPlayer()`, `IsCreature()`, `IsItem()`, `IsGameObject()`, `IsDynamicObject()` |
| `Flags & ITEM_FLAG_*` | `HasFlag(ItemFlag)`, `HasFlag2(ItemFlag2)`, `HasFlagCu(ItemFlagsCustom)` |
| direkter `UNIT_NPC_FLAGS` | `GetNpcFlags()`, `HasNpcFlag()`, `SetNpcFlag()`, `RemoveNpcFlag()` |
| direkter `ITEM_FIELD_FLAGS` | `IsRefundable()`, `IsBOPTradable()`, `IsWrapped()` |
| `ObjectGuid::GetCounter()` direkt | `ObjectGuid::ToString().c_str()` |
| `const Type*`, `const auto&` | `Type const*`, `auto const&` |
| Tabs, mehrfach-Leerzeilen, Trailing-Whitespace | siehe oben |
| Opening-Brace auf gleicher Zeile wie `if`/`else` | neue Zeile |

### File-Header

Jede C++-Quelldatei beginnt mit dem GPL-v2-Header:

```cpp
/*
 * This file is part of the AzerothCore Project. See AUTHORS file for Copyright information
 *
 * This program is free software; you can redistribute it and/or modify
 * ...
 */
```

## SQL-Style

- Backticks um Tabellen- und Spaltennamen: `` `creature_template` ``
- Single-Quotes für Strings, keine Quotes für numerische Werte
- **DELETE vor INSERT** (kein `REPLACE`)
- DELETE/UPDATE muss mindestens den Primary Key in `WHERE` haben
- `IN (1, 2, 3)` für Mehrfachwerte bevorzugen
- Variablen für wiederholte Werte: `SET @ENTRY := 7727;`
- Mehrere Rows in einem `INSERT` zusammenfassen
- **Flag-Updates**: bitweise (`flags | 0x4`, `flags & ~0x8`) — nie das ganze Feld überschreiben
- Tabellen-Naming: `snake_case`, Spalten: `UpperCamelCase` (Akronyme groß: `PositionX`, `DisplayID`, `ItemGUID`)
- `INT` statt `INT(11)`, niemals `MEDIUMINT`
- Engine: **InnoDB only** (CI), Charset `utf8mb4`, Collation `utf8mb4_unicode_ci` (`utf8mb4_bin` für Name-Spalten)
- jedes Statement endet mit Semikolon
- 4 Spaces, keine Tabs, kein Trailing-Whitespace, keine doppelten Leerzeilen
- **`entryorguid` lowercase** (nicht `EntryOrGuid`)
- `broadcast_text`-Edits nur mit Sniff-Daten und Maintainer-Approval
- nie aus `creature_template`/`gameobject_template`/`item_template`/`quest_template` `DELETE`n
- SQL-Files mit Random-Filename in `data/sql/updates/pending_db_*/` ablegen, **nicht** in `base/` oder `archive/`

## Lua / Eluna / AIO

- **Tab-Einrückung** (Eluna/AIO Konvention)
- AIO-Handler-Pattern: `AIO.AddHandlers("NAME", handlers)` — Tabelle nach Registrierung in-place ergänzen
- AIO-Msg-Pattern: `AIO.Msg():Add("Name", "Handler", ...):Send(player)` (Server) bzw. `:Send()` (Client)
- `player` ist **immer** erstes Argument in JEDEM Handler — auch auf Client (dort: String mit Spielername)
- `AIO.AddAddon()` am Anfang von Client-Files: `if AIO.AddAddon() then return end`
- `AIO.AddOnInit(function(msg, player) … return msg end)` für Login-Daten
- Globale Handler-Tabelle bei Hot-Reload-Risiko (siehe [04-aio-framework.md](./04-aio-framework.md#re-registrierungs-falle))
- max 15 Argumente pro `msg:Add()` Block

## Commit Message Format

Conventional Commits:

```
Type(Scope/Subscope): Short description (max 50 chars)
```

| Type | Wofür |
|------|-------|
| `feat` | neues Feature |
| `fix` | Bugfix |
| `refactor` | Restrukturierung ohne Verhaltensänderung |
| `style` | rein kosmetisch (Whitespace, etc.) |
| `docs` | Dokumentation |
| `test` | Tests |
| `chore` | Maintenance (Imports, Tooling) |

Scopes: `Core` (C++), `DB` (SQL).
Subscopes: `Spells`, `Scripts`, `Server`, `SAI`, `Ulduar`, `ICC`, ...

Beispiele:
- `fix(Core/Spells): Fix damage calculation for Fireball`
- `fix(DB/SAI): Missing spell to NPC Hogger`
- `feat(Core/Commands): New GM command to do something`
- `chore(DB): import pending files`

**Regeln**: Subject capitalized, imperative mood, kein Punkt am Ende, max 50 Zeichen Title, max 72 Zeichen pro Body-Zeile.

## Branch-Naming

Für KI-Sessions:
```
claude/<beschreibung-mit-bindestrichen>-<sessionId>
```
Beispiele: `claude/fix-lifeleech-caster-0yYoZ`, `claude/review-markdown-docs-bTSgu`.

**Wichtig**: pro Repo ein eigener Branch — derselbe Branch-Name kann (und sollte) in mehreren Repos parallel existieren, wenn Cross-Repo-Arbeit nötig ist.

## CI-Pipelines (azerothcore-wotlk)

| Workflow | Trigger | Was |
|----------|---------|-----|
| `codestyle.yml` | `src/`-Änderungen | C++ codestyle + cppcheck |
| `sql-codestyle.yml` | `data/`-Änderungen | SQL codestyle |
| `core-build-pch.yml` | alle | clang-15+18 Linux mit PCH |
| `core-build-nopch.yml` | alle | clang-15+18, gcc-14 ohne PCH |
| `macos_build.yml`, `windows_build.yml` | alle | OS-Kompatibilität |
| `core_modules_build.yml` | alle | Modul-Compile-Check |

Kompiliert mit `-Werror`: jede Warnung lässt den Build fehlschlagen.
