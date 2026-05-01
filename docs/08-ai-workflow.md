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
3. **Für Code/SQL/Configs**: gezielt mit `mcp__github__get_file_contents` und Pfad. Wenn Datei > 60 KB ist, vorher per `search_code` einzelne Symbole identifizieren.
4. **Für die alte `CLAUDE.md` (60 KB) im Notfall**:
   ```
   mcp__github__get_file_contents owner=shoro2 repo=share-public path=CLAUDE.md
       → Truncation-Datei /root/.claude/projects/.../tool-results/*.txt
   jq -r '.[1].text' <file>.txt > /tmp/sp_claude.md
   grep -E '^#' /tmp/sp_claude.md   # Sections finden
   Read file_path=/tmp/sp_claude.md offset=N limit=300  # Chunks lesen
   ```
5. **Für `mysql_column_list_all.txt` (riesig)** nur per `grep` nach Tabellennamen:
   ```
   grep '^`creature_template`' mysqldbextracts/mysql_column_list_all.txt
   ```
6. **DBC-Dateien sind binär** — niemals als Text lesen. Bearbeitung via `python_scripts/patch_dbc.py` / `copy_spells_dbc.py` oder via DB-Override-Tabellen (`*_dbc`).

## 2. Schreib-Strategie (verhindert Stream-Timeouts)

- **Pro `mcp__github__create_or_update_file`-Aufruf eine Datei.** Nicht versuchen, 5+ Dateien per `push_files` zu bündeln, wenn der Inhalt jeweils >5 KB ist — der Stream kann idle-timeouten.
- **Output zwischen Tool-Calls knapp halten.** Lange Erläuterungstexte zwischen Calls erhöhen Timeout-Risiko.
- **Parallele Tool-Calls nur wenn klein und idempotent.** Max ~3 parallele `get_file_contents`-Reads gleichzeitig.
- **Existierende Dateien**: vor `Edit`/`create_or_update_file` SHA per `get_file_contents` holen. SHA ist im Result als `sha`-Feld.
- **Grosse Files updaten**: lokal in `/tmp/` zwischenkopieren, mit `Edit`/`Write` lokal anpassen, dann via `create_or_update_file` mit `content` und altem `sha` hochladen.

## 3. Branch-Konventionen

- **Branch pro Repo**: `claude/<beschreibung>-<sessionId>` (z.B. `claude/review-markdown-docs-bTSgu`). Selber Branch-Name in allen Repos die zur Session gehören.
- **Push** mit `git push -u origin <branch>`. Bei Netzwerkfehler max 4 Retries mit Exponential-Backoff (2s, 4s, 8s, 16s).
- **Niemals destruktive Git-Befehle** (`reset --hard`, `push --force`, `branch -D`) ohne explizite User-Anweisung.
- **Hooks nicht skippen** (`--no-verify`, `--no-gpg-sign`) ausser explizit erlaubt.
- **Niemals `--amend`** auf bereits gepushte Commits — neuen Commit erstellen.
- **Keine PRs ohne expliziten User-Wunsch.** Branch wird gepusht, der User entscheidet über PR.

## 4. Commit-Konventionen

Conventional Commits — siehe [07-codestyle.md](./07-codestyle.md#commit-message-format). Kurzform:

```
feat(Core/Spells): Add Life Leech stat
fix(DB/SAI): Missing spell to NPC Hogger
docs: Restructure AI guide into modular docs/
chore(DB): import pending files
```

## 5. Logging-Pflicht (`claude_log.md`)

**Jede** Änderung an einem Projekt-Repo wird in `share-public/claude_log.md` protokolliert. Format:

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

## 6. Plan-Dokumentation

Geplante Features / TODOs werden in `claude_log.md` unter `## Offene Pläne und TODOs` priorisiert:

```markdown
### Hohe Priorität
- [ ] **mod-X: Beschreibung** — kurz Begründung
- [x] **mod-Y: erledigt** — abhaken statt löschen

### Mittlere Priorität
…

### Niedrige Priorität / Verbesserungen
…
```

## 7. Workflow-Schritt für Schritt

1. **Lies** `AI_GUIDE.md` und das passende `docs/`-Kapitel.
2. **TODO-Liste** anlegen (`TodoWrite`) bei nicht-trivialen Aufgaben (≥3 Schritte).
3. **Branch erstellen** (lokal oder remote via `mcp__github__create_branch`) — `claude/<beschreibung>-<sessionId>`.
4. **Implementieren**, kleinteilige Commits, Conventional Commits.
5. **Logge** in `claude_log.md` (immer in `share-public`).
6. **Push** mit Retries.
7. **Bei UI-Änderungen**: testen mit `/aio reset` oder Charakter-Reload, sonst alte Closures aktiv (siehe [04-aio-framework.md](./04-aio-framework.md#re-registrierungs-falle)).
8. **Zusammenfassung** an den User: Branch-URL nennen, was geändert wurde, was nicht.

## 8. Sprache

- **Logs / Doku**: Deutsch (Projektsprache)
- **Code-Kommentare**: Englisch
- **Commit-Messages**: Englisch (Conventional Commits)
- **Markdown-Tabellen-Header**: nach Bedarf — Mischung erlaubt, im Zweifel Deutsch.

## 9. Was NICHT tun

- **kein** ungefragter Build (`make -j`) — dauert lang, blockiert Session
- **keine** ungefragte SQL-Ausführung gegen produktive DBs
- **kein** PR ohne Userwunsch
- **kein** `git push --force`, `git reset --hard`, `git branch -D` ohne Anweisung
- **keine** Edits an `data/sql/base/` oder `data/sql/archive/` (CI-Warnung, Maintainer-Approval nötig)
- **keine** Konfig-/Settings-Dateien (`settings.local.json` etc.) ändern, ohne explizit gefragt zu werden
- **keine** Mehrfach-File-Pushes (`push_files` mit >2 Files á >5 KB) — Stream-Timeout-Risiko
- **keine** Volltext-Reads von Files ≥ 60 KB ohne Chunking-Strategie
