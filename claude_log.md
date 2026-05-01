# Projekt-Änderungslog

Dieses Dokument dient als zentrale Historie aller Arbeitsschritte, Änderungen und Pläne im WoW-Server-Projekt. Jeder Eintrag enthält einen Zeitstempel, das betroffene Repository und eine Beschreibung der Änderung.

---

## Änderungshistorie

### 2026-05-01

#### [mod-paragon] Fix: Race-Condition C++ ↔ Lua bei Paragon-Punkt-Allokation (M2)

- **Zeitstempel**: 2026-05-01
- **Repo**: mod-paragon
- **Problem**: Lua-`AllocatePoint`/`DeallocatePoint` schrieben Stat-Spalte und `unspent_points` als zwei getrennte asynchrone `CharDBExecute`-UPDATEs. Wechselte der Spieler innerhalb weniger ms die Map, las C++ `ApplyParagonStatEffects()` einen inkonsistenten Stand → Integrity-Check `(totalAllocated + unspent) == level*PPL` schlug fehl → destruktiver Reset zerstörte alle Stat-Allokationen, Spieler bekam "There was an error loading your Paragon points, please reallocate them!".
- **Lösung**:
  1. Neue Funktion `Paragon.UpdateAllocationAndUnspent(characterID, dbColumn, newValue, newUnspent)` in `Paragon_Data.lua`. Schreibt Stat-Spalte + `unspent_points` in einem **synchronen** `CharDBQuery`-UPDATE — die nächste C++-Lese-Query (auf Map-Change) sieht garantiert beide neuen Werte.
  2. `Paragon_Server.lua` `AllocatePoint`/`DeallocatePoint` rufen die neue atomare Funktion statt der zwei separaten async-Updates auf.
  3. `ParagonPlayer.cpp` `ApplyParagonStatEffects()` ersetzt den destruktiven Reset durch Soft-Recovery: bei (theoretisch nicht mehr erreichbarem) Mismatch wird nur `unspent_points` neu berechnet (`level*PPL - totalAllocated`, clamped ≥0), Stats bleiben unangetastet, Auras werden weiterhin appliziert. Destruktive Reset-Logik bleibt nur im NPC-Reset-Pfad (`ParagonNPC.cpp`).
- **Betroffene Dateien**:
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
- **Validierung**: User-seitig in-game zu testen — vor Fix Punkt allokieren + sofort Map wechseln → Reset; nach Fix → Punkt bleibt erhalten, kein Reset.
- **Notizen**: M2-Plan stammt aus `claude_log_2026-05-01_session_handoff.md`. Eluna bietet kein synchrones `CharDBExecute`, deshalb die ungewöhnliche Wahl, ein UPDATE per `CharDBQuery` zu schicken — dessen Implementierung blockiert bis zum Commit, was hier genau erwünscht ist.

#### [Multi-Repo] Docs: Phase A — Modulare Per-Repo-Doku-Files (log.md / data_structure.md / functions.md)

- **Zeitstempel**: 2026-05-01
- **Repos**: azerothcore-wotlk, mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage, mod-auto-loot
- **Ziel**: zentrale CLAUDE.md-Files in jedem Repo lesbarer machen, indem Inhalte konsequent auf 4 fokussierte Files pro Repo verteilt werden. Vermeidet die 25 K-Token- und Stream-Timeout-Errors beim Lesen wachsender Monolith-CLAUDE.md.
- **Pro Repo neu erstellt**:
  - `log.md` — minimaler Commit-Log (1 Zeile pro Commit, mit SHA-Link). Initial-Befüllung mit den letzten ~10 Commits aus `git log`.
  - `data_structure.md` — Datei-/Ordner-Tree des Repos plus Datei-Zwecke und Größenhinweise (welche Files am Lese-Limit, welche binär).
  - `functions.md` — Mechanik- und Funktions-Referenz (Hooks, AIO-Handler, DB-Queries, Konfig, bekannte Einschränkungen).
- **Sonderfall mod-auto-loot**: hatte gar keine `CLAUDE.md` — wurde in dieser Phase neu erstellt (4 Files statt 3). Inhalt rekonstruiert aus `src/mod_auto_loot.cpp` und projekt-zentralen Logs.
- **Sonderfall azerothcore-wotlk** (Fork): `log.md` fokussiert auf **Custom-Änderungen** (Reagent-Hooks, Spell.dbc), Upstream-Sync-Merges nur als Sammelreferenz.
- **Bestehende `CLAUDE.md`-Files**: in dieser Phase **nicht** angefasst. Phase B (separat) wird sie auf reine Inhalts-Doku reduzieren und Redundanz mit `data_structure.md` / `functions.md` entfernen.
- **Branch**: `claude/review-markdown-docs-bTSgu` (in jedem Repo).
- **Commits** (pro Repo):
  - mod-auto-loot: `cc0b452` (log.md), `756b887` (data_structure.md), `8f13cbf` (functions.md), `603d3e7` (CLAUDE.md NEU)
  - mod-loot-filter: `855cdef`, `ee7449f`, `727e3ed`
  - mod-endless-storage: `b77536b`, `d7e4c9a`, `3da60d2`
  - mod-paragon: `2d39f62`, `0f8c07f`, `78c2319`
  - mod-paragon-itemgen: `8a1fd2b`, `08ed1e7`, `1749558`
  - azerothcore-wotlk: `2348b52`, `1d558eb`, `2f3bafc`
- **Befunde während Phase A**:
  - **mod-endless-storage**: tatsächliche Architektur (Lua-only seit März 2026) wich vom alten `CLAUDE.md`-Stand ab — Phase A hat das in `functions.md` und `data_structure.md` korrigiert; das alte CLAUDE.md beschreibt veraltete C++-Crafting-Hooks.
  - **mod-paragon-itemgen**: `src/ParagonItemGen.cpp` ist mit ~37 KB knapp am Lese-Limit — bei Bedarf chunked Read mit `Read offset/limit` oder gezielt `grep`. SQL-Datei `paragon_itemgen_enchantments.sql` (>100 KB für 11.323 Einträge) nur per `grep` durchsuchen, nie am Stück lesen.
  - **mod-paragon**: `ParagonPlayer.cpp` ist mit ~26 KB ebenfalls am Limit, aber noch lesbar.
- **Strategie für KI-Lesbarkeit (ergänzend zu der Phase 0 Modular-Doku in share-public)**:
  1. Pro Repo gleiche Datei-Namen (`log.md`, `data_structure.md`, `functions.md`, `CLAUDE.md`) → blind navigierbar.
  2. Jede neue Datei <12 KB, in der Praxis 2-8 KB → einzeln lesbar.
  3. Cross-Refs in jedem File auf die Geschwister-Files und auf `share-public/AI_GUIDE.md`.
- **Phase B (separat geplant, nicht in dieser Session)**:
  - Pro Repo das alte `CLAUDE.md` durchgehen, Inhalte die jetzt in `data_structure.md`/`functions.md` stehen entfernen, nur reine Inhalts-/Zweck-Beschreibung lassen.
  - Vor jedem Refactor: Vorher/Nachher-Diff-Plan zur Abnahme an User.
  - Ziel: jedes `CLAUDE.md` < 8 KB, redundanzfrei zu seinen Geschwister-Files.

#### [share-public] Docs: Modulare KI-Doku-Struktur (`AI_GUIDE.md` + `docs/`)

- **Zeitstempel**: 2026-05-01
- **Repo**: share-public
- **Problem**: Die zentrale `share-public/CLAUDE.md` ist auf ~60 KB / 1284 Zeilen gewachsen und lässt sich von KI-Tools (Claude Code, etc.) nicht mehr zuverlässig per `Read`/`mcp__github__get_file_contents` einlesen — sie kippt regelmäßig in den 25 000-Token-Limit-Error. Zusätzlich treten `Stream idle timeout`-Fehler auf, wenn zu viele/große Tool-Aufrufe gebündelt werden.
- **Lösung**: Neue modulare Doku-Struktur als bevorzugter Einstiegspunkt für KI-Sessions:
  - `AI_GUIDE.md` (~6.4 KB) — Top-Level Navigation: Repo-Karte, Lese-Strategie, "wo finde ich was?".
  - `docs/01-repos.md` — alle 7 Repos im Detail (mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-auto-loot, mod-endless-storage, azerothcore-wotlk, share-public).
  - `docs/02-architecture.md` — Server-Architektur, 3 DBs, Modul-System, Hooks, Logging.
  - `docs/03-spell-system.md` — SpellScripts, AuraScripts, vollständige Proc-Kette, korrigierte ProcFlags-Werte, DBC-System, BasePoints-Off-By-One.
  - `docs/04-aio-framework.md` — AIO-APIs, Handler-Pattern, Re-Registrierungs-Falle, Code-Caching, Nachrichten-Limits.
  - `docs/05-modules.md` — Tiefe pro Modul: Mechaniken, DB-Tabellen, Hooks, Konfig-Optionen.
  - `docs/06-custom-ids.md` — Custom-IDs-Registry: Spells (100xxx, 900xxx), Enchants (900001-916666, 920001, 950001-950099), NPCs, Items, Slash-Commands, reservierte Bereiche.
  - `docs/07-codestyle.md` — C++/SQL/Lua-Konventionen, CI-enforced Verbote, Commit-Format.
  - `docs/08-ai-workflow.md` — Lese-Strategie zur Vermeidung der Token-/Timeout-Fehler, Schreib-Strategie (1 File pro Tool-Call), Branch-/Logging-Konventionen.
  - `README.md` von 14 B auf ~2.7 KB erweitert: zeigt auf `AI_GUIDE.md`, listet alle docs/ und Repos.
- **Strategie zur Vermeidung der Lese-Errors** (jetzt in `docs/08-ai-workflow.md` dokumentiert):
  1. Jede `docs/`-Datei <12 KB → kein 25 K-Token-Error mehr beim Read.
  2. KI-Tools fangen mit `AI_GUIDE.md` an, laden gezielt nur das relevante Kapitel.
  3. Bei Notwendigkeit, die alte 60-KB-`CLAUDE.md` zu lesen: Truncation-Datei (`/root/.claude/projects/.../tool-results/*.txt`) per `jq -r '.[1].text' > /tmp/file.md` extrahieren, dann mit `Read offset/limit` chunkweise lesen.
  4. Schreib-Seite: `mcp__github__create_or_update_file` einzeln pro Datei, nicht batched → kein `Stream idle timeout`.
- **Backwards-Kompatibilität**: Alte `CLAUDE.md` bleibt unverändert (alle Modul-CLAUDE.md-Dateien linken weiterhin darauf). Neue Struktur ergänzt, nicht ersetzt.
- **Betroffene Dateien**:
  - `AI_GUIDE.md` (NEU)
  - `docs/01-repos.md` (NEU)
  - `docs/02-architecture.md` (NEU)
  - `docs/03-spell-system.md` (NEU)
  - `docs/04-aio-framework.md` (NEU)
  - `docs/05-modules.md` (NEU)
  - `docs/06-custom-ids.md` (NEU)
  - `docs/07-codestyle.md` (NEU)
  - `docs/08-ai-workflow.md` (NEU)
  - `README.md` (erweitert)
  - `claude_log.md` (dieser Eintrag)
- **Branch**: `claude/review-markdown-docs-bTSgu`
- **Commits**: `222607f` (AI_GUIDE), `72fb3c1` (01-repos), `f663592` (02-architecture), `0a7a586` (03-spell-system), `44b8a43` (04-aio), `9233be9` (05-modules), `2bf9bef` (06-ids), `7a194de` (07-codestyle), `6cfa549` (08-workflow), `89a4406` (README)
- **Notizen**: Quellen für die Synthese: bestehende `CLAUDE.md` (60 KB, chunked gelesen), `claude_log.md` (35 KB), `claude_log_2026-04-27_custom_spells_review.md`, alle Modul-CLAUDE.md (azerothcore-wotlk, mod-paragon, mod-paragon-itemgen, mod-loot-filter, mod-endless-storage), `mod-auto-loot/src/mod_auto_loot.cpp` (kein CLAUDE.md vorhanden — Modul-Verhalten aus dem Source rekonstruiert). `Dcore Concept.pdf` wurde laut User als teilweise outdated eingeordnet und nicht im Detail einbezogen, ist aber im neuen `AI_GUIDE.md` als Konzept-Pitch verlinkt.

### 2026-04-28

#### [mod-paragon] Fix: Life Leech triggert nicht für Caster mit Pets/Totems

- **Zeitstempel**: 2026-04-28
- **Repo**: mod-paragon
- **Problem**: Der Life-Leech-Stat heilte nur, wenn der Spieler selbst der `attacker` in `Unit::DealDamage` war. Damit ging der Heal für alle Caster-Specs verloren, deren Hauptschadensquelle ein Pet oder Totem ist (Demonology Warlock mit Felguard, Frost Mage mit Water Elemental, Beast Mastery Hunter, sämtliche Totem-Shaman-Specs, Dancing Rune Weapon des Frost-DKs, Mind Control). Direkter Spell-Schaden des Spielers (Mage Fireball, Priest Smite, Warlock Shadow Bolt) hat funktioniert — der Lookup `attacker->ToPlayer()` matchte aber nicht für Pets/Totems, weil deren `attacker` ein `Creature` ist.
- **Lösung**: `ParagonLifeLeech::OnDamage` löst jetzt über `Unit::GetCharmerOrOwnerPlayerOrPlayerItself()` den Player-Owner des Angreifers auf. Damit triggert Leech für alle vom Spieler kontrollierten Quellen (Player, Pet, Totem, Charmed Unit). Zusätzlich wird Selbst-/Friendly-Schaden (Fall-Damage, Environmental, eigene Spell-Splashes) über einen Victim-Owner-Check ausgeschlossen, damit der Spieler sich nicht aus eigenem HP-Verlust hochheilt.
- **Betroffene Dateien**:
  - `mod-paragon/src/ParagonPlayer.cpp` (`ParagonLifeLeech::OnDamage`)
- **Branch**: `claude/fix-lifeleech-caster-0yYoZ`

### 2026-03-22

#### [mod-paragon] Feat: Big+Small Spell-Paare für Stats über 255 Stacks

- **Zeitstempel**: 2026-03-22
- **Repo**: mod-paragon
- **Lösung**: Zwei Spells pro Stat — "Small" (1x Wert/Stack) und "Big" (100x Wert/Stack via spell_dbc). Allokation N: big=N/100, small=N%100. Beispiel: 666 Str = 6×Big(500) + 66×Small(5) = 3330.
- **Neue Dateien**: `data/sql/db-world/base/paragon_big_stat_spells.sql` (17 spell_dbc, IDs 100201-100227)
- **Commit**: 4ef8c53

#### [mod-paragon] Fix: uint8 Aura Stack Limit für Paragon Level und Stats

- **Zeitstempel**: 2026-03-22
- **Repo**: mod-paragon
- **Problem**: GetAuraCount() wraps bei 256 → Level-/Punkte-Reset. Stats auf 255 gedeckelt.
- **Lösung**: Level aus DB-Cache, conf_MaxStats/MAX_POINTS auf 666, Level-Aura auf 255 gecapped.
- **Commit**: 31de184

#### [mod-paragon-itemgen] Fix: AIO-based tooltip display for paragon stats and cursed items

- **Zeitstempel**: 2026-03-22
- **Repo**: mod-paragon-itemgen
- **Problem**: Paragon item stats und Cursed-Marker wurden im Client-Tooltip nicht mehr angezeigt. Ursache: Die Tooltip-Anzeige hing vollständig von einer gepatchten Client-SpellItemEnchantment.dbc ab. Ohne gepatchte DBC kann der WoW 3.3.5-Client die Custom-Enchantment-IDs (900001-920001) nicht auflösen.
- **Lösung**: Neues AIO-basiertes Tooltip-System:
  - Server liest Enchantment-Daten direkt aus den Item-PROP_ENCHANTMENT-Slots (7-11)
  - Dekodiert Stat-Typ + Amount aus der Enchantment-ID-Formel (900000 + statIndex * 1000 + amount)
  - Sendet Daten per AIO an den Client bei Login und Inventar-Änderungen
  - Client cached Daten nach Bag/Slot-Position und zeigt Custom-Tooltip-Zeilen an
  - DBC-Text-Erkennung als Fallback für Nicht-Inventar-Tooltips (Loot, Quest, Vendor)
- **Betroffene Dateien**:
  - `Paragon_System_LUA/ItemGen_Server.lua` (kompletter Rewrite: AIO-Daten-Provider)
  - `Paragon_System_LUA/ItemGen_Client.lua` (kompletter Rewrite: AIO-Cache + DBC-Fallback)
  - `CLAUDE.md` (Dokumentation aktualisiert)
- **Commit**: a8111bb

#### [azerothcore-wotlk] Feature: Reagent Hooks for External Storage

- **Zeitstempel**: 2026-03-22
- **Repo**: azerothcore-wotlk
- **Änderungen**:
  - 2 neue PlayerScript Hooks: `OnPlayerCheckReagent` und `OnPlayerConsumeReagent`
  - Hook in `Spell::CheckItems()`: Fragt externe Quellen wenn Inventar nicht reicht
  - Hook in `Spell::TakeReagents()`: Konsumiert aus externer Quelle vor `DestroyItemCount`
  - Minimale Core-Änderungen: 4 Dateien, ~45 Zeilen
- **Betroffene Dateien**:
  - `src/server/game/Scripting/ScriptDefines/PlayerScript.h` (enum + virtual methods)
  - `src/server/game/Scripting/ScriptDefines/PlayerScript.cpp` (ScriptMgr impl)
  - `src/server/game/Scripting/ScriptMgr.h` (declarations)
  - `src/server/game/Spells/Spell.cpp` (hook calls)
- **Commit**: e99877b

#### [mod-endless-storage] Feature: Crafting Integration + UI Fixes

- **Zeitstempel**: 2026-03-22
- **Repo**: mod-endless-storage
- **Änderungen**:
  - C++ Crafting-Integration: Implementiert `OnPlayerCheckReagent` und `OnPlayerConsumeReagent` Hooks
  - Fragt `custom_endless_storage` Tabelle ab für fehlende Reagenzien beim Craften
  - Inventar wird zuerst benutzt, Storage deckt den Rest — transparent für den Spieler
  - Fix: `searchBox` und `logShown` Forward-Deklaration vor Nutzung in `SelectCategory`
  - Fensterhöhe von 440 auf 470px erhöht (+30px)
  - Log-Button von Kategorie-Panel nach oben rechts verschoben (neben Close-Button)
- **Betroffene Dateien**:
  - `src/mod_endless_storage_crafting.cpp` (neu)
  - `src/mod_endless_storage_loader.cpp` (aktualisiert)
  - `lua_scripts/Storage/endless_storage_client.lua`

### 2026-03-21

#### [mod-loot-filter] Feature: Complete Loot Filter Module

- **Zeitstempel**: 2026-03-21
- **Repo**: mod-loot-filter
- **Änderungen**:
  - Neues AzerothCore-Modul für automatische Item-Filterung erstellt
  - C++ Backend: PlayerScript mit OnPlayerLootItem Hook, In-Memory-Cache für Filterregeln, Auto-Sell (Vendor), Auto-Disenchant (Loot-Generierung), Auto-Delete
  - 8 Filterbedingungen: Quality, Item Level, Sell Price, Item Class, Item Subclass, Cursed Status, Item ID, Name Contains
  - 4 Aktionen: Keep (Whitelist), Sell, Disenchant, Delete
  - Prioritätssystem: Regeln werden in Prioritätsreihenfolge ausgewertet, erster Match gewinnt
  - AIO Lua UI: Scrollbare Regelliste, Dropdown-Menüs für Condition/Action, Preset-Buttons (Sell Grey, Sell White, DE Green, etc.), Minimap-Button
  - SQL Schema: `character_loot_filter` (Regeln) + `character_loot_filter_settings` (Toggle + Statistiken)
  - Chat Commands: `.lootfilter reload/toggle/stats`
  - Integration mit mod-paragon-itemgen: Erkennt Cursed Items via Slot 11 Enchantment (920001, 950001-950099)
  - Integration mit mod-auto-loot: Filtert Items die durch Auto-Loot aufgehoben werden
  - Konfiguration: Enable, AllowSell, AllowDisenchant, AllowDelete, LogActions, MaxRulesPerChar
  - CLAUDE.md erstellt
- **Betroffene Dateien**:
  - `src/LootFilter.h` (Header: Enums, Konstanten)
  - `src/LootFilter.cpp` (Core: Filter-Logik, Hooks, Commands)
  - `src/mod_loot_filter_loader.cpp` (Module Loader)
  - `conf/loot_filter.conf.dist` (Konfiguration)
  - `conf/conf.sh.dist` (SQL-Pfade)
  - `include.sh` (Build-Integration)
  - `data/sql/db-characters/loot_filter_tables.sql` (DB Schema)
  - `Loot_Filter_LUA/LootFilter_Server.lua` (AIO Server)
  - `Loot_Filter_LUA/LootFilter_Client.lua` (AIO Client UI)
  - `CLAUDE.md` (Dokumentation)
- **Branch**: `claude/mod-loot-filters-xdFB7`
- **Commit**: f0a9aa5

#### [mod-dungeon-challenge] Feature: Active Run Tracker UI

- **Zeitstempel**: 2026-03-21
- **Repo**: mod-dungeon-challenge
- **Änderungen**:
  - Neues AIO-basiertes Active Run Tracker Frame implementiert (ähnlich Retail WoW Mythic+ Tracker)
  - Server-seitig: Lua-basiertes Run-Tracking mit Eluna Hooks (PLAYER_EVENT_ON_MAP_CHANGE, PLAYER_EVENT_ON_KILL_CREATURE, PLAYER_EVENT_ON_KILLED_BY_CREATURE)
  - AIO Messages: RunStart, BossKilled, DeathUpdate, RunCompleted, RunEnd
  - Client-seitig: Kompaktes TrackerFrame (250px, TOPRIGHT, bewegbar, Position gespeichert)
  - Features: Echtzeit-Timer mit Farbcodierung (grün/gelb/rot), +2/+3 Threshold-Zeiten (80%/60% der Timerzeit), Boss-Kill-Checkliste mit individuellen Kill-Zeiten, Death-Counter mit Strafzeit-Anzeige
  - Auto-Show bei Run-Start, Auto-Hide 60s nach Completion
  - Neuer Slash Command `/dc tracker` zum Toggling
  - CLAUDE.md aktualisiert
- **Betroffene Dateien**:
  - `lua_scripts/dungeon_challenge_server.lua` (erweitert: trackedRuns, BuildAffixString, Eluna Event Hooks)
  - `lua_scripts/dungeon_challenge_ui.lua` (erweitert: TrackerFrame, UpdateTrackerDisplay, Run-Handler)
  - `CLAUDE.md` (aktualisiert)
- **Branch**: `claude/add-active-run-ui-I0l5q`

### 2026-03-20

#### [mod-dungeon-challenge] Feature: AIO Client UI ersetzt Gossip-Menüs

- **Zeitstempel**: 2026-03-20
- **Repo**: mod-dungeon-challenge
- **Änderungen**:
  - Neues AIO-basiertes Client-UI erstellt: Gossip-Menüs durch echte WoW-Frames ersetzt
  - `dungeon_challenge_server.lua`: Server-Script mit AIO-Handlern, DB-Laden, GameObject-Gossip→AIO-Brücke
  - `dungeon_challenge_ui.lua`: Vollständiges WoW-UI mit Tabs (Dungeons, Leaderboard, My Runs, Records)
  - Features: Dungeon-Auswahl, Difficulty-Slider (1-20), Confirm-Panel mit Affix-Details, Leaderboard, persönliche Bestzeiten, Boss-Kill-Records
  - Slash Command `/dc` zum Öffnen der UI
  - Alle Daten werden beim Login via AIO.AddOnInit an den Client gesendet (dungeon data, affixes, config)
  - CLAUDE.md aktualisiert mit neuer AIO-Architektur-Dokumentation
  - Alte `dungeon_challenge_gameobject.lua` als DEPRECATED markiert
- **Betroffene Dateien**:
  - `lua_scripts/dungeon_challenge_server.lua` (NEU)
  - `lua_scripts/dungeon_challenge_ui.lua` (NEU)
  - `CLAUDE.md` (aktualisiert)
- **Branch**: `claude/review-lua-communication-MItns`

#### [share-public] Docs: AIO Framework Dokumentation + mod-dungeon-challenge Integration

- **Zeitstempel**: 2026-03-20
- **Repo**: share-public
- **Änderungen**:
  - CLAUDE.md um AIO Framework Sektion ergänzt (APIs, Architektur, Datei-Struktur)
  - Repository-Tabelle um mod-dungeon-challenge erweitert
  - Repository-Struktur um AIO_Server Ordner ergänzt
  - claude_log.md mit Änderungseinträgen aktualisiert
- **Betroffene Dateien**:
  - `CLAUDE.md` (aktualisiert)
  - `claude_log.md` (aktualisiert)
- **Branch**: `claude/review-lua-communication-MItns`

---

#### [mod-paragon] Fix: CREATE TABLE IF NOT EXISTS für SQL-Base-Scripts

- **Zeitstempel**: 2026-03-20
- **Repo**: mod-paragon
- **Änderungen**:
  - `character_paragon_points_create.sql` und `character_paragon_create.sql` verwendeten `CREATE TABLE` ohne `IF NOT EXISTS`
  - Dies verursachte ERROR 1050 (42S01) "Table already exists" beim Auto-Update-System, wenn die Tabellen bereits existierten
  - Beide SQL-Dateien auf `CREATE TABLE IF NOT EXISTS` umgestellt
- **Betroffene Dateien**:
  - `data/sql/db-characters/base/character_paragon_points_create.sql`
  - `data/sql/db-characters/base/character_paragon_create.sql`
- **Branch**: `claude/fix-duplicate-table-error-R8OB8`

---

#### [mod-dungeon-challenge] Feature: Neues Dungeon Challenge Modul (Mythic+ inspiriert)

- **Zeitstempel**: 2026-03-20
- **Repo**: mod-dungeon-challenge
- **Änderungen**:
  - Neues AzerothCore-Modul erstellt: Mythic+-ähnliches Dungeon-Challenge-System
  - NPC-basierte UI: Dungeon-Auswahl, Schwierigkeit (1-20), Run starten, Bestenliste
  - Affix-System: ~5% der Mobs erhalten zufällige Affixe (10 Affix-Typen)
  - Implementierte Affixe: Bolstering, Raging, Sanguine, Bursting, Fortified
  - Timer-System mit Tod-Strafe (-5s pro Tod)
  - HP/DMG-Skalierung pro Schwierigkeitsstufe
  - Bestenliste mit DB-Persistenz
  - Gold-Belohnungen (Bonus für In-Time-Completion)
  - 16 WotLK-Dungeons vorkonfiguriert
  - Vollständige CLAUDE.md und README.md Dokumentation
- **Betroffene Dateien**:
  - `src/DungeonChallenge.h` - Header mit allen Datenstrukturen
  - `src/DungeonChallenge.cpp` - Singleton-Manager
  - `src/DungeonChallengeNpc.cpp` - Gossip-NPC
  - `src/DungeonChallengeScripts.cpp` - Event-Hooks
  - `src/mod_dungeon_challenge_loader.cpp` - Loader
  - `data/sql/db-world/00_dungeon_challenge_world.sql` - World-DB
  - `data/sql/db-characters/00_dungeon_challenge_characters.sql` - Characters-DB
  - `conf/mod_dungeon_challenge.conf.dist` - Konfiguration
  - `CLAUDE.md`, `README.md` - Dokumentation
- **Branch**: `claude/azeroth-dungeon-module-tPYFF`

---

### 2026-03-19

#### [mod-paragon] Feature: Konfigurierbare Max-Punkte pro Paragon-Stat

- **Zeitstempel**: 2026-03-19
- **Repo**: mod-paragon
- **Änderungen**:
  - Maximale Punkte pro Paragon-Stat sind jetzt über `mod_paragon.conf` konfigurierbar (Standard: 255)
  - 17 neue Config-Optionen: `Paragon.MaxStr`, `Paragon.MaxInt`, `Paragon.MaxAgi`, `Paragon.MaxSpi`, `Paragon.MaxSta`, `Paragon.MaxHaste`, `Paragon.MaxArmorPen`, `Paragon.MaxSpellPower`, `Paragon.MaxCrit`, `Paragon.MaxHit`, `Paragon.MaxBlock`, `Paragon.MaxExpertise`, `Paragon.MaxParry`, `Paragon.MaxDodge`, `Paragon.MaxMountSpeed`, `Paragon.MaxManaRegen`, `Paragon.MaxLifeLeech`
  - C++: `conf_MaxStats[17]` Array, geladen in `OnAfterConfigLoad()`, Clamping in `RefreshParagonAura()`
  - Lua: `Paragon.MAX_POINTS` Tabelle in `Paragon_Data.lua`, referenziert in allen 17 Stat-Definitionen
  - Wert `0` = kein Limit (nur durch Aura-Stack-Größe begrenzt)
- **Betroffene Dateien**:
  - `mod-paragon/conf/mod_paragon.conf.dist`
  - `mod-paragon/src/ParagonPlayer.cpp`
  - `mod-paragon/Paragon_System_LUA/Paragon_Data.lua`
- **Branch**: `claude/configurable-paragon-stats-PfHFY`

#### [mod-paragon] Refactor: Alle v1/v2 Versionsverweise entfernt

- **Zeitstempel**: 2026-03-19
- **Repo**: mod-paragon
- **Änderungen**:
  - `ParagonV2` → `Paragon` (globale Lua-Tabelle)
  - `PARAGON_V2_SERVER` → `PARAGON_SERVER`, `PARAGON_V2_CLIENT` → `PARAGON_CLIENT` (AIO Handler)
  - `ParagonV2Frame` → `ParagonFrame`, `SLASH_PARAGONV2_1` → `SLASH_PARAGON1`
  - Kommentare: "Paragon System v2" → "Paragon System"
  - CLAUDE.md: Legacy v1 Store-System-Doku entfernt, Dateistruktur und Beschreibungen aktualisiert
- **Betroffene Dateien**:
  - `mod-paragon/Paragon_System_LUA/Paragon_Data.lua`
  - `mod-paragon/Paragon_System_LUA/Paragon_Server.lua`
  - `mod-paragon/Paragon_System_LUA/Paragon_Client.lua`
  - `mod-paragon/CLAUDE.md`
- **Branch**: `claude/configurable-paragon-stats-PfHFY`

### 2026-03-18

#### [mod-paragon, azerothcore-wotlk] Feature: Life Leech Stat

- **Zeitstempel**: 2026-03-18
- **Repos**: mod-paragon, azerothcore-wotlk
- **Änderungen**:
  - Neuer 17. Paragon-Stat: **Life Leech** (Aura ID 100027)
  - Heilt den Spieler für einen konfigurierbaren Prozentsatz des verursachten Schadens (Standard: 0.5% pro Stack)
  - Implementiert via performantem `UnitScript::OnDamage` Hook (Option B) statt Proc-System
  - `ParagonPlayer.cpp`: STAT_COUNT 16→17, neues conf_AuraIds[16], ParagonLifeLeech UnitScript-Klasse
  - `CharacterDatabase.cpp`: Prepared Statements um `plifeleech` Spalte erweitert (SEL, INS, RESET)
  - `character_paragon_points_create.sql`: Neue Spalte `plifeleech`
  - `mod_paragon.conf.dist`: `Paragon.IdLifeLeech = 100027`, `Paragon.LifeLeechPct = 0.5`
  - `Paragon_Data.lua`: Stat-Definition id=17, Kategorie Offensive, DB-Column-Order erweitert
  - Migration-SQL: `ALTER TABLE` für bestehende DBs
- **Betroffene Dateien**:
  - `mod-paragon/src/ParagonPlayer.cpp`
  - `mod-paragon/conf/mod_paragon.conf.dist`
  - `mod-paragon/data/sql/db-characters/base/character_paragon_points_create.sql`
  - `mod-paragon/data/sql/db-characters/updates/add_plifeleech_column.sql`
  - `mod-paragon/Paragon_System_LUA/Paragon_Data.lua`
  - `azerothcore-wotlk/src/server/database/Database/Implementation/CharacterDatabase.cpp`

#### [mod-paragon] Feature: Shift+Click für 10 Punkte auf einmal

- **Zeitstempel**: 2026-03-18
- **Repo**: mod-paragon
- **Änderungen**:
  - `Paragon_System_LUA/Paragon_Client.lua`: +/- Buttons senden `amount=10` wenn Shift gehalten wird, sonst `amount=1`
  - `Paragon_System_LUA/Paragon_Server.lua`: `AllocatePoint` und `DeallocatePoint` akzeptieren optionalen `amount`-Parameter. Betrag wird automatisch auf verfügbare Punkte, Max-Cap und aktuelle Allocation geclampt.
- **Betroffene Dateien**: `Paragon_System_LUA/Paragon_Client.lua`, `Paragon_System_LUA/Paragon_Server.lua`

#### [mod-paragon] Fix: Missing GemProperties value in paragon_currency_item.sql

- **Zeitstempel**: 2026-03-18
- **Repo**: mod-paragon
- **Änderungen**:
  - `data/sql/db-world/base/paragon_currency_item.sql`: INSERT hatte 138 Spalten aber nur 137 Werte — der Wert für `GemProperties` fehlte. Dadurch verschoben sich alle nachfolgenden Werte um eine Position (`HolidayId` bekam `''`, `ScriptName` bekam `0`, `VerifiedBuild` fiel komplett weg). Dies führte zum Fehler beim Auto-Update der World-Datenbank.
  - Fix: `0` für `GemProperties` eingefügt, damit alle 138 Spalten korrekt zugeordnet werden.
- **Betroffene Dateien**: `data/sql/db-world/base/paragon_currency_item.sql`

#### [share-public] Initiale Projektdokumentation erstellt

- **Zeitstempel**: 2026-03-18
- **Repo**: share-public
- **Änderungen**:
  - `CLAUDE.md` erstellt: Zentrale Wissensbasis für KI-Assistenten mit vollständiger Dokumentation des Gesamtprojekts (Architektur, SpellScript-System, DBC-System, Modul-System, alle Custom Module, Custom IDs, DB-Tabellen, Code Style, Build-Anleitung)
  - `claude_log.md` erstellt: Änderungshistorie und Projektplanung
- **Betroffene Dateien**: `CLAUDE.md`, `claude_log.md`

> **Hinweis**: Frühere Phase-3- und Phase-4-Detail-Einträge zu mod-paragon und mod-paragon-itemgen wurden gekürzt, da der zugehörige Implementierungsstand jetzt vollständig in den modularen `docs/05-modules.md` und in jedem Modul-`functions.md` dokumentiert ist.

---

## Offene Pläne und TODOs

> **Stand 2026-05-01**: die meisten ursprünglichen TODOs sind umgesetzt. Aktive Folgearbeit siehe Phase B (CLAUDE.md-Refactor pro Modul, geplant für eine separate Session).

#### [azerothcore-wotlk] Spell.dbc Korruption behoben + Validierung eingebaut (2026-03-18)

- **Repo**: azerothcore-wotlk, ac-share
- **Änderung**: `share/dbc/Spell.dbc` aus sauberem Backup wiederhergestellt; 6 Schutzmaßnahmen in `share-public/python_scripts/copy_spells_dbc.py` (Größencheck, String-Table-Null-Byte, Duplikat-Erkennung, Format-Konsistenz, Source≠Target, Post-Write-Verify).
- **Verifiziert**: 49.880 Records, 0 Duplikate, 17 Custom 900xxx + 17 Custom 100xxx Spells vorhanden.
- **Status**: ✅ erledigt.

### Phase B (geplant)

- [ ] Pro Repo bestehende `CLAUDE.md` durchgehen, Inhalte die jetzt in `data_structure.md` und `functions.md` stehen entfernen, nur reine Inhalts-/Zweck-Doku lassen.
- [ ] Vorher/Nachher-Diff-Plan zur Abnahme an User.
- [ ] Ziel: jedes `CLAUDE.md` < 8 KB, redundanzfrei.

### Bekannte Restposten

- [ ] **mod-paragon-itemgen: AH Restriction** — blockiert: AzerothCore hat keinen `CanCreateAuction`-Hook, `OnAuctionAdd` ist void. Cursed Items sind ohnehin Soulbound.
- [ ] **mod-paragon: Anti-Farm-Maßnahmen** — keine Cooldowns/DR auf XP-Quellen.
- [ ] **mod-paragon: SQL-Injection-Risiko in Lua-Layer** — Eluna ohne PreparedStatements, weiterhin String-Concat. Mitigation: serverseitige Validierung der Handler-Args.

---

## Format-Vorlage für neue Einträge

```markdown
### YYYY-MM-DD

#### [repo-name] Kurzbeschreibung

- **Zeitstempel**: YYYY-MM-DD HH:MM (UTC+1)
- **Repo**: repository-name
- **Änderungen**:
  - Beschreibung der Änderung 1
  - Beschreibung der Änderung 2
- **Betroffene Dateien**: `datei1.cpp`, `datei2.sql`
- **Commit**: `abc1234` (falls committed)
- **Branch**: `branch-name`
- **Notizen**: Zusätzliche Kontextinformationen
```
