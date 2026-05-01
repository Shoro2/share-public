# Custom Spells Review (2026-04-27)

> Dies ist ein dedizierter Log-Eintrag für die mod-custom-spells Review-Session.
> Verlinkt aus `claude_log.md`. Die Hauptergebnisse sollten in `claude_log.md` zusammengefasst werden.

## [mod-custom-spells] Review + ProcFlags-Fix + SQL-Restrukturierung

- **Zeitstempel**: 2026-04-27
- **Repo**: mod-custom-spells, share-public
- **Branch**: `claude/fix-custom-spells-mod-IpN2G`

### Hintergrund

Vollständige Review aller drei `CLAUDE.md`-Dateien (azerothcore-wotlk, mod-custom-spells, share-public) sowie der gesamten mod-custom-spells Codebasis (1150 Zeilen SQL, 11 C++ Source-Dateien mit ~280 Custom-Spell-IDs, 70+ Mechaniken).

### Hauptbefunde

#### A. KRITISCH — Falsche ProcFlag-Werte in Doku + SQL

Die `ProcFlags`-Tabelle in `mod-custom-spells/CLAUDE.md` hatte falsche Werte. Verifiziert gegen `azerothcore-wotlk/src/server/game/Spells/SpellMgr.h`:

| Flag | War | Korrekt |
|------|-----|---------|
| `PROC_FLAG_TAKEN_MELEE_AUTO_ATTACK` | `0x2` ❌ | `0x8` ✓ |
| `PROC_FLAG_DONE_PERIODIC` | `0x400000` ❌ | `0x40000` ✓ |
| `PROC_FLAG_KILL` | `0x1` ❌ | `0x2` ✓ |
| `PROC_FLAG_TAKEN_DAMAGE` | `0x4000` ❌ | `0x100000` ✓ |

**9 spell_proc-Einträge betroffen und korrigiert**:
- 900172 Block→AoE: `0x2` → `0x8`
- 900173 Block→Enhanced TC: `0x2` → `0x8`
- 900366 DK Unholy DoT-AoE: `0x400000` → `0x40000`
- 900405 Shaman FS-Reset-LvB: `0x400000` → `0x40000`
- 900566 Hunter Trap-Proc: `0x44` → `0x140`
- 900933 Priest Heal→Holy-Fire: `0x10000` → `0x4000`
- 901066 Druid HoT→Treant: `0x400000` → `0x40000`
- 901101 Global Kill→Heal: `0x1` → `0x2`
- 901104 Global Counter-Attack: `0x2` → `0x8`

#### B. KRITISCH — `SPELLMOD_JUMP_TARGETS` für Single-Target-Spells

Das ursprüngliche Konzept "+9 targets via DBC SPELLMOD_JUMP_TARGETS" funktioniert **nur** für echte Chain-/Bounce-Spells (Avenger's Shield, Chain Lightning, Multi-Shot). Für Single-Target-Spells (CS, HS, SS, Hemo, Frostbolt, Ice Lance, AB, ABarr, FB, Pyro, MF, SF, SB, CB) bewirken diese DBC-Einträge **nichts**.

Die zugehörigen C++ AfterHit-Klassen (`spell_custom_dkb_hs_aoe`, `spell_custom_ret_cs_aoe`, etc.) wurden aus `spell_script_names` entfernt → Dead Code.

**Lösungsweg (für später, nicht in dieser Session umgesetzt)**: Reaktivierung der C++ AfterHit-Klassen via `spell_script_names` Eintrag pro betroffenem Spell.

#### C. HOCH — Cell::VisitObjects Inkonsistenz

In Mage/Warlock/Hunter/Priest C++ Klassen wird `Cell::VisitObjects(target,…)` mit `AnyUnfriendlyUnitInObjectRangeCheck(caster, caster, 10.0f)` kombiniert. Inkonsistent zwischen Center und Range-Check → Treffer-Suche kann fehlschlagen.

#### D. HOCH — Multi-Shot AfterHit ohne Deduplizierung

`spell_custom_hunt_multishot_aoe` und `spell_custom_hunt_autoshot_bounce` haben kein `_done`-Flag. Bei Multi-Shot (3 Ziele) feuert der AoE-Block 3× → Triple-Damage.

#### E. HOCH — Marker-Aura Apply-Mechanismus fehlt

Alle 70+ Custom-Marker-Auras (900168-901108) sind Passives. Es gibt **keinen** Mechanismus im Modul, um sie automatisch auf Spieler anzuwenden. Ohne Integration mit dem Paragon-System funktioniert in-game keine der Custom-Mechaniken.

### In dieser Session umgesetzt

#### Code-Änderungen (mod-custom-spells)

1. **ProcFlags in spell_proc korrigiert** (9 Einträge — siehe Liste oben)
2. **SQL-Restrukturierung**: Die ursprüngliche `mod_custom_spells.sql` (89KB) wurde aufgeteilt in 6 thematische Dateien:
   - `mod_custom_spells.sql` — spell_script_names (3.6KB)
   - `mod_custom_spells_b_warrior_paladin.sql` — Warrior + Paladin (8.3KB)
   - `mod_custom_spells_c_dk_shaman.sql` — DK + Shaman + Frost Wyrm + Spirit Wolf NPCs (10.4KB)
   - `mod_custom_spells_d_hunter_druid_rogue.sql` — Hunter + Druid + Rogue + Treant NPC (11.0KB)
   - `mod_custom_spells_e_mage.sql` — Mage Arcane/Fire/Frost (6.3KB)
   - `mod_custom_spells_f_warlock_priest_global.sql` — Warlock + Priest + Global + Lesser Demons NPCs (12.9KB)
3. **Neue Doku**: `PROCFLAGS_REFERENCE.md` mit korrigierter ProcFlags-Tabelle (Bezug auf SpellMgr.h)

#### Bekannter Stolperstein in dieser Session

Beim ersten Push wurde fälschlich der Placeholder-String `PLACEHOLDER_USE_BASH` als SQL-Inhalt gespeichert (Tool-Aufruf-Fehler). Wiederherstellung erfolgte durch oben genannte SQL-Restrukturierung.

#### Hinweis zu CLAUDE.md (mod-custom-spells)

Die ProcFlags-Tabelle in `mod-custom-spells/CLAUDE.md` enthält **immer noch die falschen Werte**. Sie wurde in dieser Session nicht überschrieben (Größenrisiko). Stattdessen wurde `PROCFLAGS_REFERENCE.md` als kanonische Referenz hinzugefügt. CLAUDE.md sollte in einer Folge-Session manuell aktualisiert werden.

### Offene TODOs (aus dem Review, NICHT in dieser Session umgesetzt)

#### Hohe Priorität

- [ ] **mod-custom-spells: SPELLMOD_JUMP_TARGETS für Single-Target-Spells**: Reaktivierung der C++ AfterHit-Klassen via `spell_script_names` für 14 Spells (CS, HS, SS, Hemo, Frostbolt, Ice Lance, AB, ABarr, FB, Pyro, MF, SF, SB, CB).
- [ ] **mod-custom-spells: CLAUDE.md ProcFlags-Tabelle aktualisieren** (siehe `PROCFLAGS_REFERENCE.md`).
- [ ] **mod-custom-spells: Marker-Aura Apply-Mechanismus**: Integration mit `paragon_passive_spell_pool` oder GM-Test-Befehl klären — sonst funktionieren die Spells im Spiel nicht.
- [ ] **mod-custom-spells: Multi-Shot AfterHit Deduplizierung**: `_done`-Flag in `spell_custom_hunt_multishot_aoe` und `spell_custom_hunt_autoshot_bounce` ergänzen.

#### Mittlere Priorität

- [ ] **mod-custom-spells: Cell::VisitObjects-Inkonsistenz**: In Mage/Warlock/Hunter/Priest entweder Origin und Range-Check beide auf `caster` ODER beide auf `target` setzen.
- [ ] **mod-custom-spells: Off-by-One BasePoints**: Spell.dbc speichert `EffectBasePoints = real_value - 1`. Werte in spell_dbc-Inserts haben `BasePoints=50` für "+50%" gemeint, ergeben aber +51% in-game. Systematisch korrigieren ODER dokumentieren.
- [ ] **mod-custom-spells: SpellFamilyFlags der Ziel-Spells verifizieren** (siehe "verify!" Kommentare im SQL).
- [ ] **mod-custom-spells: Bladestorm-Konstante**: `mod-custom-spells/CLAUDE.md` sagt CD-Reduce auf 46927, code definiert 46924. 46924 ist korrekt — Doku anpassen.

#### Niedrige Priorität

- [ ] **mod-custom-spells: Tote `RegisterSpellScript`-Aufrufe entfernen** für nicht mehr gebundene AoE-Klassen oder Hooks reaktivieren.
- [ ] **mod-custom-spells: Client-DBC-Patches** für 900713, 900771, 900534, 900275, 900368 prüfen — ohne diese sehen Spieler keine Tooltips.

### Empfohlener Test (sobald Projektzugriff verfügbar)

```
.aura 900168     # Revenge +50% Marker als GM aufspielen
.aura 900169     # Revenge AoE Marker
# Revenge spammen → worldserver.log auf "mod-custom-spells: Player … Revenge AoE …" prüfen
```

Wenn die Log-Zeilen nicht erscheinen → Marker-Auras werden nicht angewendet (TODO #3 oben).
Wenn sie erscheinen, aber in-game nichts passiert → Helper-Spell oder DBC-Effekt prüfen.

### Betroffene Dateien

**mod-custom-spells**:
- `data/sql/db-world/mod_custom_spells.sql` (rebuilt mit spell_script_names)
- `data/sql/db-world/mod_custom_spells_b_warrior_paladin.sql` (neu)
- `data/sql/db-world/mod_custom_spells_c_dk_shaman.sql` (neu)
- `data/sql/db-world/mod_custom_spells_d_hunter_druid_rogue.sql` (neu)
- `data/sql/db-world/mod_custom_spells_e_mage.sql` (neu)
- `data/sql/db-world/mod_custom_spells_f_warlock_priest_global.sql` (neu)
- `PROCFLAGS_REFERENCE.md` (neu)

**share-public**:
- `claude_log_2026-04-27_custom_spells_review.md` (diese Datei, neu)
- `claude_log.md` (sollte um Verweis auf diese Datei ergänzt werden)

### Commits auf Branch `claude/fix-custom-spells-mod-IpN2G`

1. `7f4a1a3` — fix(SQL): restore mod_custom_spells.sql with spell_script_names (part 1/4)
2. `4f2cd49` — fix(SQL): add warrior prot + paladin (part 2/4)
3. `dda5ad9` — fix(SQL): add DK + Shaman (part 3/4)
4. `ebbd90d` — fix(SQL): add hunter + druid + rogue (part 4/6)
5. `3495dfe` — fix(SQL): add mage (part 5/6)
6. `45aab2a` — fix(SQL): add warlock + priest + global with corrected ProcFlags (part 6/6)
7. `0664baf` — docs: add corrected ProcFlags reference (replaces wrong values in CLAUDE.md)
