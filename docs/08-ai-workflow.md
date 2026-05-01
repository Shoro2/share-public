# 08 — AI-Workflow

Konkrete Marschroute für KI-Sessions am Projekt. Kerngedanken: **klein lesen, klein schreiben, alles loggen.**

## 1. Lese-Strategie (verhindert Tool-Errors)

Drei Fehlerklassen treten regelmäßig auf, wenn man unbedacht große Files liest:

| Fehler | Auslöser | Workaround |
|--------|----------|------------|
| `result (NN characters) exceeds maximum allowed tokens` | Datei > ~25 K Tokens (~80 KB Text) bei `mcp__github__get_file_contents` | Tool schreibt das Ergebnis automatisch in `/root/.claude/projects/.../tool-results/*.txt` — von dort chunked weiterlesen |
| `File content (NN tokens) exceeds maximum allowed tokens (25000)` | `Read` ohne `limit:` auf großer Datei | immer `offset` + `limit` setzen (z.B. `limit: 300`) |
| `Stream idle timeout — partial response received` | zu lange / zu viele parallele Tool-Calls in einer Antwort | jeden `mcp__github__create_or_update_file` einzeln, nicht batched; Output zwischen Calls knapp halten |

### Empfohlene Reihenfolge

1. **Immer mit [`AI_GUIDE.md`](../AI_GUIDE.md) starten** — kleinster Einstiegspunkt, verlinkt alle Detail-Dokumente.
2. **Nur das relevante `docs/`-Kapitel** laden — alle <12 KB.
3. **Pro Modul-Repo** gilt die gleiche 4-File-Konvention (siehe Abschnitt "Per-Repo-Doku-Konvention" unten):
   - `INDEX.md` zuerst (Einstieg, ~1 KB),
   - `CLAUDE.md` für Zweck/Inhalt,
   - `data_structure.md` für Folder/Files,
   - `functions.md` für Mechaniken/Hooks/Konfig,
   - `log.md` für Commit-Historie,
   - `todo.md` für offene Aufgaben.
4. **Für Code/SQL/Configs**: gezielt mit `mcp__github__get_file_contents` und Pfad. Wenn Datei > 60 KB ist, vorher per `search_code` einzelne Symbole identifizieren.
5. **Für die alte `CLAUDE.md` in `share-public` (60 KB) im Notfall**:
   ```
   mcp__github__get_file_contents owner=shoro2 repo=share-public path=CLAUDE.md
       → Truncation-Datei /root/.claude/projects/.../tool-results/*.txt
   jq -r '.[1].text' <file>.txt > /tmp/sp_claude.md
   grep -E '^#' /tmp/sp_claude.md   # Sections finden
   Read file_path=/tmp/sp_claude.md offset=N limit=300  # Chunks lesen
   ```
6. **Für `mysql_column_list_all.txt` (riesig)** nur per `grep` nach Tabellennamen:
   ```
   grep '^`creature_template`' mysqldbextracts/mysql_column_list_all.txt
   ```
7. **DBC-Dateien sind binär** — niemals als Text lesen. Bearbeitung via `python_scripts/patch_dbc.py` / `copy_spells_dbc.py` oder via DB-Override-Tabellen (`*_dbc`).

## 2. Per-Repo-Doku-Konvention

In jedem Modul-/Core-Repo (also **alle ausser** `share-public`) gilt seit 2026-05 dieselbe Datei-Konvention:

| Datei | Größe | Zweck |
|-------|-------|-------|
| `INDEX.md` | < 1 KB | Einstiegspunkt; listet die anderen Files mit Größe + Einzeiler |
| `CLAUDE.md` | < 8 KB | **Inhalt/Zweck** — was ist dieses Modul, welche Rolle spielt es, welche IDs/DB-Tabellen gehören dazu (kein Mechanik-Detail!) |
| `data_structure.md` | < 6 KB | exakte Folder/File-Auflistung mit Einzeiler-Beschreibungen |
| `functions.md` | < 15 KB | Mechaniken, Hooks, Funktions-Signaturen, Konfig-Optionen, AIO-Handler — die "Wie funktioniert das?"-Details |
| `log.md` | wächst | minimaler Änderungslog, eine Zeile pro Commit mit Hash-Link |
| `todo.md` | klein | offene Aufgaben mit Priorität (`(hoch)`/`(mittel)`/`(niedrig)`); erledigte Items werden **entfernt** und in `log.md` dokumentiert (nicht durchgestrichen) |

**Cross-Cutting** liegt zentral in `share-public`:
- `share-public/claude_log.md` = Cross-Repo-Historie + größere Reviews
- `share-public/AI_GUIDE.md` + `docs/` = projektweite Doku

## 3. Schreib-Strategie (verhindert Stream-Timeouts)

- **Pro `mcp__github__create_or_update_file`-Aufruf eine Datei.** Nicht versuchen, 5+ Dateien per `push_files` zu bündeln, wenn der Inhalt jeweils >5 KB ist — der Stream kann idle-timeouten.
- **Output zwischen Tool-Calls knapp halten.** Lange Erläuterungstexte zwischen Calls erhöhen Timeout-Risiko.
- **Parallele Tool-Calls nur wenn klein und idempotent.** Max ~3 parallele `get_file_contents`-Reads gleichzeitig.
- **Existierende Dateien**: vor `Edit`/`create_or_update_file` SHA per `get_file_contents` holen. SHA ist im Result als `sha`-Feld.
- **Grosse Files updaten**: lokal in `/tmp/` zwischenkopieren, mit `Edit`/`Write` lokal anpassen, dann via `create_or_update_file` mit `content` und altem `sha` hochladen.

## 4. Branch-Konventionen

- **Branch pro Repo**: `claude/<beschreibung>-<sessionId>` (z.B. `claude/review-markdown-docs-bTSgu`). Selber Branch-Name in allen Repos die zur Session gehören.
- **Push** mit `git push -u origin <branch>`. Bei Netzwerkfehler max 4 Retries mit Exponential-Backoff (2s, 4s, 8s, 16s).
- **Niemals destruktive Git-Befehle** (`reset --hard`, `push --force`, `branch -D`) ohne explizite User-Anweisung.
- **Hooks nicht skippen** (`--no-verify`, `--no-gpg-sign`) ausser explizit erlaubt.
- **Niemals `--amend`** auf bereits gepushte Commits — neuen Commit erstellen.
- **Keine PRs ohne expliziten User-Wunsch.** Branch wird gepusht, der User entscheidet über PR.

## 5. Commit-Konventionen

Conventional Commits — siehe [07-codestyle.md](./07-codestyle.md#commit-message-format). Kurzform:

```
feat(Core/Spells): Add Life Leech stat
fix(DB/SAI): Missing spell to NPC Hogger
docs: Restructure AI guide into modular docs/
chore(DB): import pending files
```

## 6. Logging-Pflicht (`claude_log.md` + `log.md`)

Es gibt **zwei** Log-Ebenen:

### A) Cross-Repo / projekt-weit: `share-public/claude_log.md`

**Jede** nicht-triviale Änderung an einem Projekt-Repo wird hier protokolliert. Format:

```markdown
### YYYY-MM-DD

#### [repo-name] Kurzbeschreibung

- **Zeitstempel**: YYYY-MM-DD (HH:MM optional)
- **Repo**: repository-name
- **Problem** / **Änderungen** / **Lösung**: kurze Beschreibung
- **Betroffene Dateien**:
  - `pfad/zu/datei.cpp`
  - `pfad/zu/datei.sql`
- **Branch**: `claude/<name>-<id>`
- **Commit**: `abc1234` (falls bekannt)
```

Einsortieren nach Datum **absteigend** — neuester Eintrag oben, unmittelbar unterhalb der `## Änderungshistorie`-Sektion.

Bei größeren Reviews / Sessions, deren Inhalt allein schon mehrere KB Doku produziert, **separates Log-File** anlegen (Beispiel: `claude_log_2026-04-27_custom_spells_review.md`) und im Haupt-`claude_log.md` darauf verlinken.

### B) Pro-Repo: `<repo>/log.md`

Minimal-Log, eine Zeile pro Commit:

```markdown
- 2026-05-01 `abc1234` — feat(Core/Spells): Add Life Leech stat
```

Hier steht **nichts** über Pläne / TODOs / Zusammenhänge — nur die nackte Commit-Spur. Plan/TODO gehört nach `<repo>/todo.md` bzw. `share-public/claude_log.md`.

## 7. Plan-Dokumentation (TODOs)

Es gibt zwei Speicherorte:

| Was | Wohin |
|-----|-------|
| Modul-spezifische offene Aufgabe (gameplay, code, tests) | `<repo>/todo.md` mit Priorität-Tag `(hoch)/(mittel)/(niedrig)` |
| Cross-Repo-Roadmap, Phasenplan, abgeschlossene größere Pläne | `share-public/claude_log.md` unter `## Offene Pläne und TODOs` |

`todo.md` Format:

```markdown
## Sicherheit
- [ ] **(mittel)** Beschreibung — Begründung
## Performance
- [ ] **(niedrig)** ...
```

**Erledigte Items** in `todo.md` werden **entfernt** (nicht durchgestrichen) und im `log.md`-Commit-Eintrag des erledigenden Commits dokumentiert. Damit bleibt `todo.md` immer der aktuelle Stand der offenen Punkte.

## 8. Workflow-Schritt für Schritt

1. **Lies** `AI_GUIDE.md`, das passende `docs/`-Kapitel und im betroffenen Modul-Repo `INDEX.md` + relevante 4-File-Sektion.
2. **Prüfe `todo.md`** im Modul-Repo — vielleicht ist dein Auftrag schon dort gelistet.
3. **TODO-Liste** anlegen (`TodoWrite`) bei nicht-trivialen Aufgaben (≥3 Schritte).
4. **Branch erstellen** (`mcp__github__create_branch`) — `claude/<beschreibung>-<sessionId>`.
5. **Implementieren**, kleinteilige Commits, Conventional Commits.
6. **Update**:
   - `<repo>/log.md` — neue Commit-Zeile(n)
   - `<repo>/todo.md` — erledigtes Item entfernen
   - `share-public/claude_log.md` — Datums-Eintrag mit Repo-Tag
   - bei Strukturänderungen: `<repo>/data_structure.md` aktuell halten
   - bei neuen Mechaniken/Hooks: `<repo>/functions.md` ergänzen
7. **Push** mit Retries.
8. **Bei UI-Änderungen**: testen mit `/aio reset` oder Charakter-Reload, sonst alte Closures aktiv (siehe [04-aio-framework.md](./04-aio-framework.md#re-registrierungs-falle)).
9. **Zusammenfassung** an den User: Branch-URL nennen, was geändert wurde, was nicht.

## 9. Sprache

- **Logs / Doku**: Deutsch (Projektsprache)
- **Code-Kommentare**: Englisch
- **Commit-Messages**: Englisch (Conventional Commits)
- **Markdown-Tabellen-Header**: nach Bedarf — Mischung erlaubt, im Zweifel Deutsch.

## 10. Was NICHT tun

- **kein** ungefragter Build (`make -j`) — dauert lang, blockiert Session
- **keine** ungefragte SQL-Ausführung gegen produktive DBs
- **kein** PR ohne Userwunsch
- **kein** `git push --force`, `git reset --hard`, `git branch -D` ohne Anweisung
- **keine** Edits an `data/sql/base/` oder `data/sql/archive/` (CI-Warnung, Maintainer-Approval nötig)
- **keine** Konfig-/Settings-Dateien (`settings.local.json` etc.) ändern, ohne explizit gefragt zu werden
- **keine** Mehrfach-File-Pushes (`push_files` mit >2 Files á >5 KB) — Stream-Timeout-Risiko
- **keine** Volltext-Reads von Files ≥ 60 KB ohne Chunking-Strategie
- **keine** `todo.md`-Items durchstreichen/abhaken — entfernen und in `log.md` eintragen
