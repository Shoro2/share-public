# Phase A+B Wrap: Per-Repo Doku-Konvention (2026-05-01)

> Detail-Log zur Multi-Repo-Doku-Restrukturierung. Verlinkt aus `claude_log.md`.

## Ziel

Pro Modul-/Core-Repo (also alle ausser `share-public`) die gleiche schlanke 6-File-Doku-Konvention etablieren, damit KI-Tools (Claude Code, etc.) die Projektdaten zuverlässig lesen können — ohne 25 K-Token-Limit-Errors oder Stream-Idle-Timeouts.

## Konvention pro Repo

| Datei | Größe | Zweck |
|-------|------:|-------|
| `INDEX.md` | <1 KB | Einstiegspunkt für KI — listet Geschwister-Files mit Größe + Zweck |
| `CLAUDE.md` | < 8 KB | **Was/Warum** — Zweck, Rolle, Custom-IDs, DB-Tabellen-Bezüge (kein Mechanik-Detail!) |
| `data_structure.md` | < 6 KB | exakte Folder/File-Auflistung mit Einzeiler-Beschreibungen |
| `functions.md` | < 15 KB | **Wie** — Mechaniken, Hooks, Funktions-Signaturen, AIO-Handler, Konfig-Optionen |
| `log.md` | wächst | minimaler Commit-Log (1 Zeile pro Commit) |
| `todo.md` | klein | offene Aufgaben mit Priorität (`(hoch)` / `(mittel)` / `(niedrig)`) |

Cross-Cutting bleibt zentral in `share-public`:
- `share-public/claude_log.md` = projekt-weite Historie + Phasenpläne
- `share-public/AI_GUIDE.md` + `docs/` = projekt-weite Doku, KI-Workflow

## Phase A — Detail-Files erstellt (frühere Session)

In jedem der 6 Modul-/Core-Repos angelegt (`mod-paragon`, `mod-paragon-itemgen`, `mod-loot-filter`, `mod-endless-storage`, `mod-auto-loot`, `azerothcore-wotlk`):

- `log.md` mit Initial-Befüllung der letzten ~10 Commits
- `data_structure.md` mit Folder/File-Tree
- `functions.md` mit Mechanik-Doku
- `mod-auto-loot` zusätzlich erstmalig `CLAUDE.md` bekommen (vorher nicht vorhanden)

## Phase A-Wrap — `todo.md` ergänzt (diese Session)

Pro Repo neue `todo.md` mit dem aktuellen Stand offener Aufgaben (extrahiert aus den `Bekannte Einschränkungen`-Sektionen der jeweiligen `functions.md` und Reviews).

| Repo | Inhaltliche Schwerpunkte |
|------|--------------------------|
| mod-auto-loot | Mining/Herbalism/Skinning fehlt; Throttle-Cooldown |
| mod-loot-filter | SQL-Injection-Mitigation in Lua, Bulk-Import/Export, Server-Defaults |
| mod-endless-storage | Doku-Drift (CLAUDE.md vor März-2026-Rewrite veraltet), Bulk-Withdraw, Crafting-Fallback |
| mod-paragon | SQL-Injection in Lua, Race-Condition C++↔Lua, Anti-Farm |
| mod-paragon-itemgen | AH-Restriction blockiert (kein Hook), BasePoints-Off-By-One, In-Memory-Cache |
| azerothcore-wotlk | `CanCreateAuction`-Hook ergänzen, DBC-Validierungs-CI |

## Phase A-Wrap — `08-ai-workflow.md` erweitert

`share-public/docs/08-ai-workflow.md` um Sektion **"Per-Repo-Doku-Konvention"** ergänzt (Tabelle der 6 Files + Cross-Cutting-Verweis). Zusätzlich neue Sektion **"Plan-Dokumentation (TODOs)"** mit Trennung:
- Modul-spezifische TODOs → `<repo>/todo.md`
- Cross-Repo-Roadmap → `share-public/claude_log.md`

Workflow-Schritt 6 ergänzt um die Pflicht, bei Implementierungs-Commits auch `<repo>/log.md` und `<repo>/todo.md` zu aktualisieren.

## Phase B — Schlanke CLAUDE.md (diese Session)

Pro Modul/Core-Repo die bestehende `CLAUDE.md` umgeschrieben:

- Entfernt: Folder/File-Listen (jetzt in `data_structure.md`), Mechanik-Details (in `functions.md`), Known-Issues mit `~~strikethrough~~` (offene Punkte in `todo.md`, erledigte gestrichen).
- Behalten: Zweck, Rolle im Gesamtprojekt, Custom-Daten-Index (IDs/Tabellen/Hooks-Namen), High-Level-Mechaniken (XP-Quellen, Skalierungs-Formel, Tooltip-System), Lizenz, Cross-Refs zu Geschwister-Files.

| Repo | Vorher | Nachher | Reduktion |
|------|-------:|--------:|----------:|
| mod-loot-filter | 9.6 KB | ~3.6 KB | -62 % |
| mod-endless-storage | 9.2 KB | ~3.9 KB | -58 % |
| mod-paragon | 13 KB | ~4.6 KB | -65 % |
| mod-paragon-itemgen | 14 KB | ~5.5 KB | -61 % |
| azerothcore-wotlk | 16 KB | ~4.6 KB | -71 % |
| mod-auto-loot | 4.1 KB (bereits schlank) | unverändert | – |

Alle `CLAUDE.md`-Files jetzt **<6 KB** und damit safely lesbar in einem `Read`/`get_file_contents`-Call.

## Phase B — INDEX.md ergänzt (diese Session)

INDEX.md in den 5 Repos hinzugefügt, in denen sie noch fehlte (`mod-loot-filter`, `mod-endless-storage`, `mod-paragon`, `mod-paragon-itemgen`, `azerothcore-wotlk`). `mod-auto-loot` hatte bereits eine.

## Lese-/Schreib-Strategien (Lessons Learned, jetzt in 08-ai-workflow.md)

1. **Lesen**: Files >25 K-Token (Truncation in `/tmp`) per `jq -r '.[1].text' > /tmp/file.md` extrahieren, dann `Read` mit `offset/limit` chunkweise.
2. **Schreiben**: pro `mcp__github__create_or_update_file` immer **eine** Datei. Niemals 5+ Files parallel — Stream-Idle-Timeout droht.
3. **Pattern-Konsistenz**: gleiche Filenamen in jedem Repo (`INDEX.md`, `CLAUDE.md`, `data_structure.md`, `functions.md`, `log.md`, `todo.md`) → blind navigierbar, keine Discovery-Suche.

## Branch

`claude/review-markdown-docs-bTSgu` (in jedem Repo).

## Status

- ✅ Phase A: Detail-Files in 6 Repos angelegt
- ✅ todo.md in 6 Repos ergänzt
- ✅ 08-ai-workflow.md um Per-Repo-Doku-Konvention erweitert
- ✅ Phase B: schlanke CLAUDE.md in 5 Repos (mod-auto-loot bereits schlank)
- ✅ INDEX.md in 5 Repos ergänzt (mod-auto-loot bereits vorhanden)
- ✅ claude_log.md mit Wrap-Eintrag versehen (Verweis auf diese Datei)

## Was nicht gemacht wurde

- **kein** PR auf irgendeinem Repo (User entscheidet) — Branch ist gepusht, bereit zum Review.
- **kein** Touch an die alte 60-KB `share-public/CLAUDE.md` selbst — bleibt als Tiefenreferenz neben der neuen `docs/`-Struktur erhalten. Eine eventuelle Phase C würde sie auflösen, ist aber nicht beauftragt.
- **kein** Build oder Test gegen den Server — reine Doku-Änderung.
