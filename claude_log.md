# Projekt-Änderungslog

Dieses Dokument dient als zentrale Historie aller Arbeitsschritte, Änderungen und Pläne im WoW-Server-Projekt. Jeder Eintrag enthält einen Zeitstempel, das betroffene Repository und eine Beschreibung der Änderung.

---

## Änderungshistorie

### 2026-03-18

#### [share-public] Initiale Projektdokumentation erstellt

- **Zeitstempel**: 2026-03-18
- **Repo**: share-public
- **Änderungen**:
  - `CLAUDE.md` erstellt: Zentrale Wissensbasis für KI-Assistenten mit vollständiger Dokumentation des Gesamtprojekts
    - Architektur des AzerothCore-Servers
    - SpellScript-System (Lifecycle, Hooks, Beispiele)
    - DBC-System (Ladevorgang, Feldformat, Zusammenspiel mit SpellScripts)
    - Modul-System (Ladevorgang, Verzeichnisstruktur, Namenskonventionen)
    - Dokumentation aller Custom-Module (mod-paragon, mod-paragon-itemgen, mod-custom-spells)
    - Alle Custom Spell/Item/NPC/Enchantment IDs
    - Datenbank-Tabellen Übersicht
    - Code Style Guidelines
    - Build-Anleitung
  - `claude_log.md` erstellt: Änderungshistorie und Projektplanung
- **Betroffene Dateien**: `CLAUDE.md`, `claude_log.md`

#### [Bestandsaufnahme] Aktueller Projektzustand aller Repos

Vollständige Analyse aller 5 Repositories durchgeführt:

**azerothcore-wotlk**:
- Server-Core auf Basis von AzerothCore (WotLK 3.3.5a)
- Vollständige CLAUDE.md vorhanden (354 Zeilen)
- Enthält SpellScript-Framework, DBC-Loading, Modul-System

**mod-paragon** (Paragon-Progressionssystem):
- Account-weites XP/Level-System nach Level 80
- Zwei unabhängige Stat-Allokationssysteme (C++ mit 16 Stats, Lua/AIO mit 5 Stats)
- CLAUDE.md vorhanden (266 Zeilen) mit 19 dokumentierten Known Issues
- Kritische Bugs: NPC-Script nicht registriert, Schema-Mismatch (5 vs 16 Spalten), Parry/Dodge vertauscht

**mod-paragon-itemgen** (Item-Enchantment-Generator):
- 5-Slot Enchantment-System basierend auf Paragon-Level
- 11.323 Custom-Enchantments in spellitemenchantment_dbc
- Rollen-basierte Stat-Pools (Tank/DPS/Healer)
- Cursed Items System mit passiven Spells
- CLAUDE.md vorhanden (232 Zeilen)
- DBC-Patching-Tools vorhanden (patch_dbc.py, add_paragon_spell.py)

**mod-custom-spells** (Custom SpellScripts):
- 4 Custom Spells implementiert (Paragon Strike, Bladestorm CD Reduce, Bloody Whirlwind Passive/Consume)
- CLAUDE.md vorhanden (69 Zeilen)
- Saubere Modul-Struktur mit SQL-Registrierung

**share-public** (dieses Repo):
- Zuvor nur README.md ("# share-public")
- Jetzt zentrale Dokumentations-Hub

---

## Offene Pläne und TODOs

### Hohe Priorität

- [ ] **mod-paragon: Schema-Mismatch beheben** — `character_paragon_points` SQL erweitern auf 16 Spalten (phaste, parmpen, pspellpower, pcrit, pmspeed, pmreg, phit, pblock, pexpertise, pparry, pdodge)
- [ ] **mod-paragon: NPC-Script registrieren** — `AddMyNPCScripts()` in `Paragon_loader.cpp` aufrufen
- [ ] **mod-paragon: Parry/Dodge Reihenfolge fixen** — Parameter-Reihenfolge in `ApplyParagonStatEffects()` korrigieren (Zeile 144)
- [ ] **mod-paragon: Punkt-Reset vervollständigen** — `ResetParagonPoints()` muss alle 16 Stats zurücksetzen

### Mittlere Priorität

- [ ] **mod-paragon: Konfiguration aktivieren** — `sConfigMgr->GetOption<>()` für alle hardcodierten Werte einbauen
- [ ] **mod-paragon: C++ und Lua Aura-IDs vereinheitlichen** — Strength: 7507 (C++) vs 100001 (Lua) Konflikt lösen
- [ ] **mod-paragon: Prepared Statements** — String-formatierte Queries durch Prepared Statements ersetzen
- [ ] **mod-paragon-itemgen: Prepared Statements** — Ebenfalls DB-Queries absichern
- [ ] **mod-paragon-itemgen: Combat Rating Pool Split** — DPS Pool in Melee/Caster aufteilen

### Niedrige Priorität / Verbesserungen

- [ ] **mod-paragon: Code-Duplikation reduzieren** — 16 identische RemoveAura/AddAura Blöcke in datengesteuerte Schleife umwandeln
- [ ] **mod-paragon: In-Memory Caching** — Paragon Level/Points im Player-Data cachen statt bei jedem Map-Change DB abfragen
- [ ] **mod-paragon: Max Level Cap** — Konfigurierbares Maximum für Paragon Level
- [ ] **mod-paragon: XP Overflow Fix** — `pow(1.1, level-1)` Overflow bei hohen Levels verhindern
- [ ] **mod-paragon-itemgen: AH Restriction** — Auction House Hook fehlt im Core
- [ ] **mod-paragon-itemgen: PROP_ENCHANTMENT_SLOT Konflikt** — Items mit Random Properties ("of the Bear") werden überschrieben

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
