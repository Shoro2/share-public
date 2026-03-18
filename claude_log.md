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

#### [mod-paragon-itemgen] Phase 4: Gameplay-Verbesserungen

- **Zeitstempel**: 2026-03-18
- **Repo**: mod-paragon-itemgen
- **Änderungen**:
  - **4.1 Combat Rating Pool Split**: DPS Pool aufgeteilt in Melee (Str/Agi → Crit, Haste, Hit, ArmorPen, Expertise, AP) und Caster (Int/Spi → Crit, Haste, Hit, SpellPower, ManaRegen). Pool-Auswahl erfolgt automatisch basierend auf `mainStat` des Spielers. Funktionssignaturen `GetCombatRatingPool()` und `PickTwoRandomRatings()` um `mainStat`-Parameter erweitert.
  - **4.2 PROP_ENCHANTMENT_SLOT Konflikt**: Items mit Random Properties ("of the Bear") werden bewusst überschrieben (Paragon-Stats sind wertvoller). Debug-Log bei Override, Spieler erhält Chat-Hinweis. Dokumentation in CLAUDE.md aktualisiert.
  - **4.3 AH Restriction**: Verifiziert blockiert — `OnAuctionAdd` ist void, kein `CanCreateAuction`-Hook in AzerothCore vorhanden. Cursed Items sind bereits Soulbound. Status dokumentiert.
- **Betroffene Dateien**: `src/ParagonItemGen.cpp`, `CLAUDE.md`
- **Branch**: `claude/review-share-public-todos-a2euu`

#### [mod-paragon] Phase 3: Architektur-Verbesserungen

- **Zeitstempel**: 2026-03-18
- **Repo**: mod-paragon
- **Änderungen**:
  - **3.1 Konfiguration aktivieren**: Neuer `ParagonConfig` WorldScript mit `OnAfterConfigLoad`-Hook. 30+ Konfigurations-Optionen werden aus `mod_paragon.conf` geladen (Enable, Aura-IDs, XP-Belohnungen, PPL, MaxLevel, PartyReduce). Alle hardcodierten Werte durch `conf_*` Variablen ersetzt.
  - **3.2 Aura-IDs vereinheitlicht**: `AURA_STRENGTH` von `7507` auf `100001` geändert. C++ und Lua verwenden jetzt identische Aura-IDs für alle 16 Stats. Config-Datei entsprechend aktualisiert.
  - **3.3 Code-Duplikation eliminiert**: 32 identische `RemoveAura`/`AddAura`/`SetAuraStack` Zeilen durch datengesteuerte Schleife ersetzt. `RefreshParagonAura()` verwendet jetzt `conf_AuraIds[16]` Array + `for`-Schleife. Signatur vereinfacht auf `(Player*, uint32 const[16])`.
  - **3.4 In-Memory Caching**: `std::unordered_map<uint32, ParagonCache>` mit Mutex-Schutz. Cache wird bei Login befüllt, bei XP-Gewinn/Level-Up aktualisiert, bei Logout invalidiert. `OnPlayerMapChanged` liest aus Cache statt DB-Query. `IncreaseParagonXP` nutzt Cache als primäre Datenquelle.
  - **3.5 Max Level Cap**: Neue Config-Option `Paragon.MaxLevel` (Default: 0 = kein Limit). Level-Up wird verhindert wenn `paragonLevel >= maxLevel`. XP-Gewinn wird komplett gestoppt wenn Cap erreicht.
  - **Bonus**: Ungenutzte Lua-Includes entfernt (`lua.h`, `lauxlib.h`, `LuaEngine.h`), ungenutztes `debug`-Flag entfernt, `RegisterParagonEluna` Declaration entfernt, `SetAuraStack` durch sichereres `GetAura()->SetStackAmount()` ersetzt.
- **Betroffene Dateien**: `src/ParagonPlayer.cpp`, `src/ParagonUtils.h`, `conf/mod_paragon.conf.dist`
- **Branch**: `claude/review-share-public-todos-a2euu`

---

## Offene Pläne und TODOs

#### [azerothcore-wotlk] Spell.dbc Korruption behoben + Validierung eingebaut

- **Zeitstempel**: 2026-03-18
- **Repo**: azerothcore-wotlk, ac-share
- **Ursache der Korruption**:
  - Die `Spell.dbc` in `azerothcore-wotlk/share/dbc/` war schwer beschädigt:
    - 34.658 doppelte Spell-IDs bei 49.880 Records (nur 15.222 einzigartig)
    - Dateigröße 2.234 Bytes zu klein gegenüber dem Header
    - String-Table korrupt (kein Null-Byte am Anfang)
    - Ungültige IDs wie 131073, 720897 — typisch für verschobene Daten
  - Ursache: `read_dbc()` in `copy_spells_dbc.py` speicherte Records in einem dict nach Spell-ID. Duplikate überschrieben sich gegenseitig — ein erneuter Lauf verschlimmerte die Korruption
- **Änderungen**:
  - **Spell.dbc wiederhergestellt** aus sauberem Backup (`ac-share/data/dbc/Spell.dbc`)
  - **Danach**: User hat aktuelle Spell.dbc mit allen Custom Spells nach `ac-share/data/dbc/Spell.dbc` hochgeladen (Commit `6238199`)
  - **Spell.dbc nach `azerothcore-wotlk/share/dbc/` kopiert** (diese Sitzung)
  - **6 Schutzmaßnahmen in `copy_spells_dbc.py`** eingebaut:
    1. Dateigröße vs. Header-Validierung
    2. String-Table Null-Byte-Prüfung
    3. Duplikat-Erkennung (bricht bei korrupter Eingabe ab)
    4. Format-String vs. Record-Size Konsistenzprüfung
    5. Source == Target Schutz (verhindert Selbst-Überschreibung)
    6. Post-Write Verifikation
- **Verifizierung der neuen Spell.dbc**:
  - 49.880 Records, alle unique (0 Duplikate)
  - Dateigröße 49.008.266 Bytes (stimmt mit Header überein)
  - String Table OK (beginnt mit Null-Byte)
  - 17 Custom 900xxx Spells (900100-900116) vorhanden
  - 17 Custom 100xxx Spells (100000-100026) vorhanden
- **Betroffene Dateien**: `share/dbc/Spell.dbc`, `share/copy_spells_dbc.py`
- **Commit (alte Sitzung)**: `2c7c070` (PR #9, gemergt)
- **Branch**: `claude/fix-spell-dbc-corruption-CQPsh` (alte Sitzung), `claude/fix-spell-dbc-corruption-CuZz4` (diese Sitzung)

---

### Hohe Priorität

- [x] **mod-paragon: Schema-Mismatch beheben** — `character_paragon_points` SQL erweitern auf 16 Spalten ✅ (Umgesetzt: Alle 16 Spalten in `character_paragon_points_create.sql` vorhanden)
- [x] **mod-paragon: NPC-Script registrieren** — `AddMyNPCScripts()` in `Paragon_loader.cpp` aufrufen ✅
- [x] **mod-paragon: Parry/Dodge Reihenfolge** — Kein Bug, Reihenfolge stimmt überein ✅ (kein Fix nötig)
- [x] **mod-paragon: Punkt-Reset vervollständigen** — `ResetParagonPoints()` auf alle 16 Stats erweitert ✅

### Mittlere Priorität

- [x] **mod-paragon: Konfiguration aktivieren** — `sConfigMgr->GetOption<>()` für alle hardcodierten Werte eingebaut ✅ (WorldScript `ParagonConfig::OnAfterConfigLoad`, 30+ Config-Optionen)
- [x] **mod-paragon: C++ und Lua Aura-IDs vereinheitlichen** — AURA_STRENGTH von 7507 auf 100001 geändert, alle IDs jetzt konsistent mit Lua-System ✅
- [x] **mod-paragon: Prepared Statements** — 13 Queries auf CharacterDatabasePreparedStatement umgestellt ✅
- [x] **mod-paragon-itemgen: Prepared Statements** — 14 Queries auf Prepared Statements umgestellt (Character + World DB) ✅
- [x] **mod-paragon-itemgen: Combat Rating Pool Split** — DPS Pool in Melee (Str/Agi) und Caster (Int/Spi) aufgeteilt ✅

### Niedrige Priorität / Verbesserungen

- [x] **mod-paragon: Code-Duplikation reduzieren** — 16 identische RemoveAura/AddAura Blöcke durch datengesteuerte Schleife ersetzt ✅ (Array `conf_AuraIds[16]` + `for`-Schleife in `RefreshParagonAura`)
- [x] **mod-paragon: In-Memory Caching** — Paragon Level/XP in `std::unordered_map<uint32, ParagonCache>` gecacht, Map-Change liest aus Cache statt DB ✅
- [x] **mod-paragon: Max Level Cap** — Konfigurierbares `Paragon.MaxLevel` (Default: 0 = kein Limit) ✅
- [x] **mod-paragon: XP Overflow Fix** — `pow(1.1, level-1)` Overflow bei hohen Levels verhindern ✅
- [ ] **mod-paragon-itemgen: AH Restriction** — Blockiert: AzerothCore hat keinen `CanCreateAuction`-Hook, `OnAuctionAdd` ist void. Cursed Items sind bereits Soulbound.
- [x] **mod-paragon-itemgen: PROP_ENCHANTMENT_SLOT Konflikt** — Random Properties werden bewusst überschrieben, Spieler erhält Chat-Hinweis ✅

---

## Implementierungsplan (Stand: 2026-03-18)

Die offenen TODOs werden in 4 Phasen umgesetzt. Die Reihenfolge folgt dem Prinzip: **erst kritische Bugs fixen, dann Sicherheit, dann Architektur, dann Extras**.

---

### Phase 1: Kritische Bugfixes (mod-paragon)

Direkte Gameplay-Auswirkungen. Kleine, gezielte Änderungen mit sofortigem Effekt.

#### 1.1 NPC-Script registrieren
- **Datei**: `mod-paragon/src/Paragon_loader.cpp`
- **Aufwand**: 2 Zeilen
- **Änderung**: Forward Declaration `void AddMyNPCScripts();` hinzufügen und `AddMyNPCScripts();` in `Addmod_paragonScripts()` aufrufen
- **Test**: NPC 900100 im Spiel ansprechen → Gossip-Menü muss erscheinen

#### 1.2 Parry/Dodge Reihenfolge fixen
- **Datei**: `mod-paragon/src/ParagonPlayer.cpp`, Zeile 143
- **Aufwand**: 1 Zeile
- **Änderung**: Aufruf von `RefreshParagonAura()` korrigieren — `pdodge, pparry` zu `pparry, pdodge` tauschen (passend zur Funktionssignatur)
- **Test**: Punkte in Parry/Dodge investieren → korrekte Aura-Stacks prüfen (`.aura 100025` / `.aura 100026`)

#### 1.3 Punkt-Reset vervollständigen
- **Datei**: `mod-paragon/src/ParagonNPC.cpp`, Zeile 53
- **Aufwand**: 1 Zeile (SQL erweitern)
- **Änderung**: UPDATE-Statement auf alle 16 Spalten erweitern:
  ```sql
  UPDATE character_paragon_points SET pstrength=0, pintellect=0, pagility=0, pspirit=0, pstamina=0,
  phaste=0, parmpen=0, pspellpower=0, pcrit=0, pmspeed=0, pmreg=0, phit=0, pblock=0,
  pexpertise=0, pparry=0, pdodge=0 WHERE characterID = '{}'
  ```
- **Test**: Punkte verteilen → Reset → alle Stats müssen 0 sein, Punkte als Items zurück

#### 1.4 XP Overflow Fix
- **Datei**: `mod-paragon/src/ParagonPlayer.cpp`, Zeile 348-349
- **Aufwand**: ~5 Zeilen
- **Änderung**:
  - `newXP` als `int64` statt `uint32` deklarieren
  - `pow(1.1, level-1)` Ergebnis mit `std::min()` cappen (z.B. auf `INT32_MAX`)
  - Overflow-Check korrekt formulieren (`if (newXP < 0) newXP = 0;`)
- **Test**: Charakter auf Level 100+ testen → kein Crash/Wrap-Around

---

### Phase 2: Sicherheit — Prepared Statements

SQL-Injection-Risiko eliminieren. Systematisch pro Modul.

#### 2.1 mod-paragon: Prepared Statements
- **Dateien**:
  - `mod-paragon/src/ParagonPlayer.cpp` (12 Queries)
  - `mod-paragon/src/ParagonNPC.cpp` (1 Query)
  - Neue Datei: `mod-paragon/src/ParagonDatabaseStatements.h` (Statement-Enum + Definitionen)
- **Aufwand**: ~80 Zeilen
- **Vorgehen**:
  1. Enum `ParagonDatabaseStatements` definieren (z.B. `PARAGON_SEL_POINTS`, `PARAGON_UPD_POINTS`, etc.)
  2. Statements in `CharacterDatabaseConnection::DoPrepareStatements()` registrieren — oder alternativ eigene Init-Funktion im `OnStartup`-Hook
  3. Alle `.Query("SELECT ...")`/`.Execute("UPDATE ...")` durch `PreparedStatement` ersetzen
- **Test**: Alle bestehenden Funktionen müssen weiterhin korrekt funktionieren

#### 2.2 mod-paragon-itemgen: Prepared Statements
- **Dateien**:
  - `mod-paragon-itemgen/src/ParagonItemGen.cpp` (8 Queries)
  - `mod-paragon-itemgen/src/ParagonItemGenCommands.cpp` (Queries prüfen)
  - `mod-paragon-itemgen/src/ParagonItemGenNPC.cpp` (Queries prüfen)
- **Aufwand**: ~60 Zeilen
- **Vorgehen**: Analog zu 2.1

---

### Phase 3: Architektur-Verbesserungen (mod-paragon)

Wartbarkeit und Korrektheit verbessern. Jeder Punkt ist unabhängig umsetzbar.

#### 3.1 Konfiguration aktivieren
- **Dateien**:
  - `mod-paragon/src/ParagonPlayer.cpp` (Hauptänderung)
  - `mod-paragon/conf/mod_paragon.conf.dist` (erweitern um fehlende Optionen: Haste/ArmorPen/SP/Crit/MSpeed/MReg/Hit/Block/Expertise/Parry/Dodge Aura-IDs)
- **Aufwand**: ~40 Zeilen
- **Änderung**:
  - Statische Variablen für Config-Werte anlegen (z.B. `static uint32 CONF_AURA_STRENGTH;`)
  - Im `OnStartup`- oder `OnAfterConfigLoad`-Hook alle Werte via `sConfigMgr->GetOption<uint32>("Paragon.IdStr", 7507)` laden
  - Hardcodierte Werte durch Config-Variablen ersetzen
- **Test**: Config-Werte ändern → Server neu starten → geänderte Werte aktiv

#### 3.2 C++/Lua Aura-IDs vereinheitlichen
- **Dateien**:
  - `mod-paragon/src/ParagonPlayer.cpp`, Zeile 21 (`AURA_STRENGTH = 7507`)
  - `mod-paragon/Paragon_System_LUA/Paragon_Data.lua`, Zeile 49 (`auraId = 100001`)
- **Aufwand**: 1 Zeile + DBC-Prüfung
- **Entscheidung nötig**: Welche ID ist korrekt?
  - **Option A**: C++ auf `100001` ändern (konsistent mit Lua und dem `100xxx` Schema) — erfordert DBC-Eintrag für Spell 100001
  - **Option B**: Lua auf `7507` ändern — nur wenn Spell 7507 Strength-Aura korrekt abbildet
  - **Empfehlung**: Option A (100001), da alle anderen Stats bereits `100xxx` folgen
- **Test**: Strength-Punkte vergeben → Aura muss auf dem Charakter sichtbar sein und korrekt wirken

#### 3.3 Code-Duplikation reduzieren
- **Datei**: `mod-paragon/src/ParagonPlayer.cpp`, Zeilen 44-95
- **Aufwand**: ~30 Zeilen (16×3 Zeilen → 1 Schleife)
- **Änderung**:
  ```cpp
  struct ParagonStatMapping {
      uint32 auraId;
      uint8 value;
  };
  // Array befüllen, dann:
  for (auto const& stat : statMappings) {
      player->RemoveAura(stat.auraId);
      if (stat.value > 0) {
          player->AddAura(stat.auraId, player);
          if (Aura* aura = player->GetAura(stat.auraId))
              aura->SetStackAmount(stat.value);
      }
  }
  ```
- **Test**: Punkte verteilen → alle Auras korrekt angewendet

#### 3.4 In-Memory Caching
- **Dateien**:
  - `mod-paragon/src/ParagonPlayer.cpp`
  - Ggf. neuer Header `ParagonPlayerData.h`
- **Aufwand**: ~50 Zeilen
- **Änderung**:
  - `std::unordered_map<uint32, ParagonData>` als Cache (accountId → {level, xp})
  - Cache befüllen bei Login, aktualisieren bei XP-Gewinn/Level-Up
  - Cache invalidieren bei Logout
  - Map-Change liest aus Cache statt DB
- **Test**: Häufige Map-Changes → keine DB-Queries in Logs für Paragon-Abfragen

#### 3.5 Max Level Cap
- **Dateien**:
  - `mod-paragon/src/ParagonPlayer.cpp` (Level-Up-Logik)
  - `mod-paragon/conf/mod_paragon.conf.dist` (neue Option `Paragon.MaxLevel`)
- **Aufwand**: ~10 Zeilen
- **Änderung**:
  - Config-Option `Paragon.MaxLevel` (Default: 0 = kein Limit)
  - Vor Level-Up prüfen: `if (maxLevel > 0 && currentLevel >= maxLevel) { /* XP überschuss verwerfen oder cappen */ }`
- **Test**: MaxLevel auf 10 setzen → ab Level 10 kein weiterer Aufstieg

---

### Phase 4: Verbesserungen (mod-paragon-itemgen)

Gameplay-Verbesserungen, nicht sicherheitskritisch.

#### 4.1 Combat Rating Pool Split
- **Datei**: `mod-paragon-itemgen/src/ParagonItemGen.cpp`, Zeilen 120-125
- **Aufwand**: ~20 Zeilen
- **Änderung**:
  - DPS-Pool aufteilen in `MELEE_DPS_COMBAT_RATINGS` (Crit, Haste, Hit, ArmorPen, Expertise, AP) und `CASTER_DPS_COMBAT_RATINGS` (Crit, Haste, Hit, SP, ManaRegen)
  - Pool-Auswahl basierend auf `mainStat`: Strength/Agility → Melee, Intellect/Spirit → Caster
- **Test**: Melee-Char darf kein Spell Power rollen, Caster kein Armor Penetration

#### 4.2 PROP_ENCHANTMENT_SLOT Konflikt
- **Datei**: `mod-paragon-itemgen/src/ParagonItemGen.cpp`
- **Aufwand**: ~10 Zeilen
- **Änderung**:
  - Vor Enchantment-Anwendung prüfen ob Item bereits Random Properties hat (`item->GetItemRandomPropertyId() != 0`)
  - Entweder: Items mit Random Properties überspringen, oder bewusst überschreiben mit Log-Meldung
  - **Empfehlung**: Überschreiben (Paragon-Stats sind wertvoller als "of the Bear"), aber mit Chat-Hinweis an den Spieler
- **Test**: Item mit "of the Bear" durch Paragon-System laufen lassen → Enchantments korrekt

#### 4.3 AH Restriction
- **Status**: **BLOCKIERT** — AzerothCore hat keinen `CanListAuction`-Hook
- **Optionen**:
  - **Option A**: Core-Patch für `CanListAuction`-Hook in `azerothcore-wotlk` (aufwändig, Fork-spezifisch)
  - **Option B**: Workaround — alle Paragon-Items automatisch Soulbound machen (einfach, aber einschränkend)
  - **Option C**: Akzeptieren — Cursed Items sind bereits Soulbound, normale Paragon-Items können gehandelt werden
  - **Empfehlung**: Option C vorerst, Option A nur bei tatsächlichem Bedarf
- **Aufwand**: Option A: ~50 Zeilen Core-Patch + Hook-Implementation | Option C: 0

---

### Zusammenfassung der Reihenfolge

| Phase | Punkte | Aufwand (geschätzt) | Abhängigkeiten |
|-------|--------|---------------------|----------------|
| **1: Bugfixes** | 1.1–1.4 | Klein (je 1-5 Zeilen) | Keine — sofort umsetzbar |
| **2: Sicherheit** | 2.1–2.2 | Mittel (~140 Zeilen) | Keine |
| **3: Architektur** | 3.1–3.5 | Mittel (~130 Zeilen) | 3.2 nach Entscheidung Aura-ID, 3.5 nach 3.1 (Config) |
| **4: Extras** | 4.1–4.3 | Klein-Mittel | 4.3 blockiert durch Core |

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
