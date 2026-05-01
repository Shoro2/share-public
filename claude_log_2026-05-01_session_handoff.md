# Session-Handoff 2026-05-01 → Folge-Session

> Dieses Dokument bringt eine **neue KI-Session** in <5 Minuten auf den Stand der vorherigen Session.
> Lies das, dann `claude_log_2026-05-01_phase_b.md`, dann pro betroffenem Repo `todo.md`.

## Was in der vorherigen Session passiert ist (Quick-Recap)

**Doku-Restrukturierung (Phase A + B)** — abgeschlossen, in 7 PRs gemerged/offen:

| PR | Repo |
|----|------|
| #30 (merged) + #31 (open) | share-public |
| #40 | mod-paragon |
| #26 | mod-paragon-itemgen |
| #17 | mod-loot-filter |
| #16 | mod-endless-storage |
| #3 | mod-auto-loot |
| #18 | azerothcore-wotlk |

**Konvention etabliert** (siehe `docs/08-ai-workflow.md`): jedes Modul-/Core-Repo hat **`INDEX.md`/`CLAUDE.md`/`data_structure.md`/`functions.md`/`log.md`/`todo.md`**. Cross-Repo-Historie bleibt in `share-public/claude_log.md`.

**Theme A (SQL-Injection-Mitigation)** — abgeschlossen:
- `share-public/AIO_Server/Dep_Validation/validation.lua` als shared Library, exposiert `_G.Validate`.
- mod-paragon (`Paragon_Server.lua`), mod-loot-filter (`LootFilter_Server.lua`), mod-endless-storage (`endless_storage_server.lua`) konsumieren die Lib.
- Erledigt M1, M4, M5 (Mittel-Prio).

**Quick-Wins** (alle abgeschlossen):
- `share-public/python_scripts/validate_dbc.py` — DBC-Pre-Push-Validator (Header / String-Table / Duplikat-IDs).
- mod-endless-storage M6 (Bulk-Withdraw via Shift/Ctrl-Click).

**Theme C/D entfernt**: AH-Hook-TODO + Anti-Farm/Reset-Cooldown — User-Entscheidung "won't fix".

## M2 (Race-Condition C++↔Lua in mod-paragon) — IN ARBEIT, nicht gepushed

User-Entscheidung 2026-05-01: Race ist **beobachtet** (nicht theoretisch), Lösungsweg: Option (a) "Lua-Allokationen an C++ delegieren". Constraint: voller `Player:ParagonAllocate`-Binding würde mod-eluna-Fork erfordern (nicht in Authorization). User hat zugestimmt zur **option-a-äquivalenten Praxis-Variante**.

### Wurzelursache (verifiziert durch Code-Lesen)

```
Player allociert in Lua → 2 separate async UPDATE-Statements (Stat + Unspent)
  ⏱ DB-Queue hat noch beide nicht committet
Player wechselt Map → C++ ApplyParagonStatEffects() liest DB
  → totalAllocated + unspent ≠ level*PPL  (wegen pending writes)
  → Integrity-Check feuert → DESTRUCTIVE RESET (Stats werden zerstört)
  → "There was an error loading your Paragon points..."
```

### Konkreter Patch-Plan (3 Files, ready to apply)

1. **`mod-paragon/Paragon_System_LUA/Paragon_Data.lua`** — neue Funktion:

   ```lua
   --- Atomic update: Stat-Allocation + unspent_points in einem einzigen UPDATE.
   -- Synchron via CharDBQuery → C++ map-change-Reads sehen sofort den neuen Stand.
   function Paragon.UpdateAllocationAndUnspent(characterID, dbColumn, newValue, newUnspent)
       CharDBQuery("UPDATE character_paragon_points SET "
           .. dbColumn .. " = " .. newValue
           .. ", unspent_points = " .. newUnspent
           .. " WHERE characterID = " .. characterID)
   end
   ```

   Alte `UpdateAllocation` und `UpdateUnspentPoints` lassen (Backwards-Compat für andere Caller, falls existent).

2. **`mod-paragon/Paragon_System_LUA/Paragon_Server.lua`** — `AllocatePoint` und `DeallocatePoint` umstellen:

   ```lua
   -- vorher (zwei getrennte async UPDATEs):
   Paragon.UpdateAllocation(characterID, stat.dbColumn, newValue)
   Paragon.UpdateUnspentPoints(characterID, newUnspent)
   -- nachher:
   Paragon.UpdateAllocationAndUnspent(characterID, stat.dbColumn, newValue, newUnspent)
   ```

3. **`mod-paragon/src/ParagonPlayer.cpp`** — In `ApplyParagonStatEffects()` den destructiven Reset durch Soft-Recovery ersetzen:

   ```cpp
   if ((totalAllocated + unspentPoints) != paragonLevel * conf_PPL)
   {
       // Soft-Recovery (vorher: destructive RESET aller Stats + unspent).
       // Lua schreibt jetzt atomar+sync, also sollte dieser Branch im Normalbetrieb
       // nie feuern. Defensiv: nur den unspent korrigieren, Stats unangetastet lassen,
       // damit ein evtl. transienter Mismatch keine Allokationen vernichtet.
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
       // KEIN early return mehr — auch bei mismatch: Auras applien.
   }

   RefreshParagonAura(player, statValues);
   ```

   Die destruktive Reset-Logik (alle Stats auf 0) bleibt **nur** im NPC-Reset-Pfad (`ParagonNPC.cpp` → `ResetParagonPoints`).

### Cleanup nach Implementation

- `mod-paragon/todo.md`: Item M2 ("Race-Condition C++↔Lua") entfernen.
- `mod-paragon/log.md`: Eintrag analog zu M1, mit Verweis auf den finalen Commit.

### Validierung (manuell durch User in-game)

- Vorher: Punkt allokieren → Map-Change innerhalb 100ms → Reset-Message kam, Punkte weg.
- Nachher: gleicher Vorgang → Punkt bleibt allokiert, kein Reset.

## Neue Information für die Folge-Session: `mod-ale`

User wird ein zusätzliches Repo `shoro2/mod-ale` zur GitHub-App-Authorization hinzufügen. Die Folge-Session sollte:

1. **Dieses Repo erkunden** (`mcp__github__get_file_contents` auf `/`) und einordnen, was es ist.
2. **Die Per-Repo-Doku-Konvention darauf anwenden** (siehe `share-public/docs/08-ai-workflow.md`):
   - `INDEX.md`, `CLAUDE.md`, `data_structure.md`, `functions.md`, `log.md`, `todo.md` anlegen.
   - Branch: `claude/<beschreibung>-<sessionId>`.
3. Falls `mod-ale` Lua/AIO-Code enthält und `CharDBExecute`/`CharDBQuery` nutzt, **die Validation-Lib einbauen** wie bei mod-paragon/loot-filter/endless-storage (siehe Theme-A-Pattern).
4. Falls `mod-ale` in einem der bestehenden Modul-`functions.md` als Konsument/Abhängigkeit referenziert werden sollte, ergänzen.

## Niedrig-Prio TODOs (siehe pro Repo `todo.md`)

Quick-Übersicht der noch offenen Items:

| Repo | Niedrig-Prio Items (Auszug) |
|------|------------------------------|
| mod-paragon | nach M2-Fix evtl. **`ParagonPlayer.cpp`-Split** (war ~26 KB → über Lese-Limit, in `todo.md` notiert) |
| mod-paragon-itemgen | M7 (BasePoints-Off-By-One Audit, **mittel-prio**), In-Memory-Cache, SQL→Generator-Skript |
| mod-loot-filter | Bulk-Import/Export, Server-Default-Regeln, Per-Quality-DE-Bonus |
| mod-endless-storage | server-getriebenes Tab-Layout, Crafting-Fallback via Server-Hook |
| mod-auto-loot | Mining/Herbalism/Skinning, Throttle-Cooldown |
| azerothcore-wotlk | nur Upstream-Sync-Hygiene + ein Hook-Markierungs-Item |

## Branch-Status (Stand 2026-05-01 ~16:40 UTC)

Alle Repos auf Branch `claude/review-markdown-docs-bTSgu`. Falls die Folge-Session einen frischen Branch will: vom jeweiligen Default-Branch (`main` / `master`) ausgehen, **nicht** von diesem Branch (er ist Doku-fokussiert und sollte nicht mit Code-Änderungen weiter beladen werden).

**Empfehlung für Folge-Session**: Vor M2-Implementation die offenen PRs (#16, #26, #40, #17, #3, #18, #31) mergen lassen, dann frischen Branch `claude/m2-paragon-race-fix-<id>` für die 3 Patches.

## Was DEFINITIV NICHT in der Folge-Session passieren sollte

- **Kein** Build (`make -j`).
- **Kein** PR-Merge ohne expliziten User-Wunsch.
- **Kein** Force-Push, kein Reset --hard.
- **Keine** Edits an `share-public/CLAUDE.md` (alte 60-KB-Doku) — die ist Tiefenreferenz, nicht das aktive Doku-Set.
- **Keine** Touch an die existierenden Phase-A/B-PRs (separate, fertig konzipierte Doku-Restrukturierung).
