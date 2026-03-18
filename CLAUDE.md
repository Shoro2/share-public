# CLAUDE.md

Dieses Repository dient als zentrale Informationsgrundlage und Dateiaustauschmöglichkeit für KI-Assistenten (Claude Code, etc.), die am WoW-Server-Projekt arbeiten. Alle Arbeitsschritte, Pläne, Architektur-Entscheidungen und Änderungen werden hier dokumentiert und versioniert.

## Projekt-Übersicht: Custom WoW Server (WotLK 3.3.5a)

Das Gesamtprojekt besteht aus einem AzerothCore-basierten World of Warcraft Server mit mehreren Custom-Modulen:

| Repository | Zweck |
|------------|-------|
| [azerothcore-wotlk](https://github.com/Shoro2/azerothcore-wotlk) | Server-Core (C++17, CMake, MySQL). Enthält Worldserver, Authserver, Scripting-Framework, DBC-Loading, Datenbank-Layer |
| [mod-paragon](https://github.com/Shoro2/mod-paragon) | Post-Level-80 Paragon-Progressionssystem: Account-weites XP + Level, 5 Stat-Punkte pro Level, Aura-basierte Stat-Zuweisung |
| [mod-paragon-itemgen](https://github.com/Shoro2/mod-paragon-itemgen) | Automatische Bonus-Stat-Enchantments auf Items basierend auf Paragon-Level. 5-Slot-System, Rollen-Pools, Cursed Items |
| [mod-custom-spells](https://github.com/Shoro2/mod-custom-spells) | Custom SpellScripts (Paragon Strike, Bladestorm CD Reduce, Bloody Whirlwind) |
| [share-public](https://github.com/Shoro2/share-public) | **Dieses Repo** — Zentrale Dokumentation, KI-Kontext, Python-Tools, DBC-Dateien, DB-Extrakte, Änderungslog |

## Repository-Struktur (share-public)

```
share-public/
├── CLAUDE.md                          # Dieses Dokument — zentrale Projektdokumentation
├── claude_log.md                      # Änderungshistorie, Projektpläne, priorisierte TODOs
├── README.md                          # GitHub-Readme
├── dbc/                               # 246 WoW-Client DBC-Dateien (binär, WotLK 3.3.5a)
│   ├── Spell.dbc                      # Alle Spell-Definitionen
│   ├── SpellItemEnchantment.dbc       # Enchantment-Definitionen (Custom-Patching via patch_dbc.py)
│   ├── Map.dbc, Map.ini               # Map-Definitionen + Feld-Format-Referenz
│   ├── Item.dbc                       # Item-Basisdaten
│   ├── ChrClasses.dbc, ChrRaces.dbc  # Klassen/Rassen
│   ├── Talent.dbc, TalentTab.dbc     # Talentsystem
│   └── ... (246 Dateien total)        # Siehe DBC-Inventar weiter unten
├── mysqldbextracts/                   # MySQL-Datenbankextrakte
│   ├── mysql_column_list_all.txt      # Komplette DB-Spaltenstruktur (304 Tabellen, 4129 Spalten)
│   ├── creature_template.csv          # Kreatur-Template Export (29.949 Einträge, 49+ Spalten)
│   └── item_template.csv             # Item-Template Export (46.097 Einträge, 133+ Spalten)
└── python_scripts/                    # Python-Hilfsskripte für DBC-Manipulation und Testing
    ├── add_paragon_spell.py           # Generator für Paragon Passive Spell SQL-Einträge
    ├── copy_spells_dbc.py             # Kopiert spezifische Spells zwischen Spell.dbc-Dateien
    ├── patch_dbc.py                   # Patcht SpellItemEnchantment.dbc mit Custom-Enchantments
    └── socket_stress_heavy.py         # Load-Testing-Tool für Auth-/Worldserver
```

### Python-Scripts Übersicht

| Script | Zweck | Input → Output |
|--------|-------|----------------|
| `add_paragon_spell.py` | Generiert SQL für neue passive Paragon-Spells | Interaktiv → SQL (Enchantment IDs 950001-950099) |
| `copy_spells_dbc.py` | Kopiert Spells zwischen Spell.dbc-Dateien | Source.dbc + Spell-IDs → Target.dbc |
| `patch_dbc.py` | Patcht SpellItemEnchantment.dbc mit 11.323 Paragon-Enchantments + Cursed Marker + Passive Spells | Original .dbc → Gepatchte .dbc |
| `socket_stress_heavy.py` | Flutet Auth-/Worldserver mit Verbindungsversuchen (Load-Test) | Config → Statistiken |

## Architektur des Server-Cores (azerothcore-wotlk)

### Server-Aufbau

- **Authserver** (`src/server/apps/authserver/`): Authentifizierung und Realm-Auswahl (Port 3724)
- **Worldserver** (`src/server/apps/worldserver/`): Hauptserver für alle Gameplay-Logik (Port 8085)

### Drei Datenbanken

| Datenbank | Inhalt |
|-----------|--------|
| `acore_auth` | Accounts, Realm-Liste, Bans |
| `acore_characters` | Charakterdaten, Inventar, Fortschritt, Paragon-Tabellen |
| `acore_world` | Spielinhalte: Kreaturen, Items, Quests, Spells, Loot, DBC-Overrides |

### Quellcode-Struktur

```
src/
├── common/           # Shared Libraries (Netzwerk, Crypto, Logging, Threading)
├── server/
│   ├── game/         # Kern-Spiellogik (~52 Subsysteme)
│   │   ├── Spells/       # Spell-Mechaniken, Aura-System, SpellScript
│   │   ├── DataStores/   # DBC-Daten laden und bereitstellen
│   │   ├── Scripting/    # ScriptMgr, Hook-System, Script-Registrierung
│   │   ├── Entities/     # Player, Creature, Unit, Item, GameObject
│   │   └── ...           # Maps, Handlers, AI, Combat, Loot, etc.
│   ├── scripts/      # Content-Scripts (Bosse, Spells, Commands, Instanzen)
│   └── database/     # DB-Abstraktions-Layer
└── test/             # Unit Tests (Google Test)
```

## SpellScript-System (Kernkonzept)

### Wie SpellScripts funktionieren

SpellScripts sind C++-Klassen, die sich in den Spell-Ausführungsprozess einklinken. Sie ermöglichen es, das Verhalten einzelner Spells zur Laufzeit zu verändern, ohne den Core zu modifizieren.

### Klassen-Hierarchie

```
_SpellScript (abstrakte Basis)
├── SpellScript   — für Spell-Effekte und Casts
└── AuraScript    — für Aura/Buff/Debuff-Mechaniken
```

### SpellScript Lifecycle

1. **Registrierung**: `RegisterSpellScript(ClassName)` in einer `AddSC_*()` Funktion
2. **Validierung**: `Validate(SpellInfo const*)` — prüft DBC-Daten beim Server-Start
3. **Laden**: `Load()` — wird aufgerufen wenn Script-Instanz erstellt wird
4. **Hook-Registrierung**: `Register()` override — bindet Handler an Spell-Events
5. **Ausführung**: Handler werden bei entsprechenden Spell-Events aufgerufen

### Verfügbare SpellScript Hooks

```cpp
// Cast-Lifecycle
SPELL_SCRIPT_HOOK_CHECK_CAST      // Vor dem Cast: kann Cast verhindern
SPELL_SCRIPT_HOOK_BEFORE_CAST     // Vor dem eigentlichen Cast
SPELL_SCRIPT_HOOK_ON_CAST         // Beim Cast
SPELL_SCRIPT_HOOK_AFTER_CAST      // Nach dem Cast

// Effekt-Hooks
SPELL_SCRIPT_HOOK_EFFECT_LAUNCH   // Effekt wird abgeschickt
SPELL_SCRIPT_HOOK_EFFECT_HIT      // Effekt trifft Ziel

// Hit-Hooks
SPELL_SCRIPT_HOOK_BEFORE_HIT      // Vor dem Treffer (mit MissInfo)
SPELL_SCRIPT_HOOK_HIT             // Beim Treffer
SPELL_SCRIPT_HOOK_AFTER_HIT       // Nach dem Treffer
```

### AuraScript Hooks

```cpp
// Aura-Lifecycle
OnApply / OnRemove                // Aura wird angelegt/entfernt
OnEffectApply / OnEffectRemove    // Einzelner Effekt angelegt/entfernt

// Berechnungen
DoEffectCalcAmount                // Berechnet Effekt-Stärke
DoEffectCalcPeriodic              // Berechnet periodischen Tick
DoEffectCalcSpellMod              // Berechnet Spell-Modifikator

// Procs
DoCheckProc                       // Kann Proc verhindern
OnProc / AfterProc                // Proc-Behandlung
```

### Beispiel: Custom SpellScript

```cpp
class spell_custom_paragon_strike : public SpellScript
{
    PrepareSpellScript(spell_custom_paragon_strike);

    void HandleDamage(SpellEffIndex /*effIndex*/)
    {
        Player* caster = GetCaster()->ToPlayer();
        if (!caster)
            return;

        float ap = caster->GetTotalAttackPowerValue(BASE_ATTACK);
        uint32 paragonLevel = caster->GetAuraCount(100000);
        int32 damage = static_cast<int32>((666.0f + ap * 0.66f) * (1.0f + paragonLevel * 0.01f));
        SetHitDamage(damage);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_custom_paragon_strike::HandleDamage,
            EFFECT_0, SPELL_EFFECT_SCHOOL_DAMAGE);
    }
};
```

### Beispiel: AuraScript mit Proc

```cpp
class spell_custom_bloody_whirlwind_passive : public AuraScript
{
    PrepareAuraScript(spell_custom_bloody_whirlwind_passive);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        SpellInfo const* spellInfo = eventInfo.GetSpellInfo();
        if (!spellInfo)
            return false;
        // Nur bei Bloodthirst (Warrior SpellFamily 4, Flags[1]=0x00000400)
        return spellInfo->SpellFamilyName == 4
            && (spellInfo->SpellFamilyFlags[1] & 0x00000400);
    }

    void HandleProc(AuraEffect const* /*aurEff*/, ProcEventInfo& /*eventInfo*/)
    {
        PreventDefaultAction();
        GetTarget()->CastSpell(GetTarget(), 900115, true);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_custom_bloody_whirlwind_passive::CheckProc);
        OnEffectProc += AuraEffectProcFn(spell_custom_bloody_whirlwind_passive::HandleProc,
            EFFECT_1, SPELL_AURA_PROC_TRIGGER_SPELL);
    }
};
```

### AzerothCore Proc-System: Ablauf und Fallstricke

#### Proc-Kette (vollständiger Ablauf)

```
Spell trifft Ziel (z.B. Bloodthirst Hit)
    ↓
ProcSkillsAndAuras() → TriggerAurasProcOnEvent()
    ↓
GetProcAurasTriggeredOnEvent() iteriert ALLE applied Auras
    ↓
Für jede Aura: GetProcEffectMask()
    ├─ 1. spell_proc Eintrag vorhanden? (Nein → return 0)
    ├─ 2. Triggered-Spell Check (IsTriggered() → blockiert wenn kein SPELL_ATTR3_CAN_PROC_FROM_PROCS)
    ├─ 3. CanSpellTriggerProcOnEvent()
    │     ├─ ProcFlags Match (z.B. 0x10 = DONE_SPELL_MELEE_DMG_CLASS)
    │     ├─ SpellFamilyName/Mask (spell_proc Tabelle, NICHT DBC EffectSpellClassMask!)
    │     ├─ SpellTypeMask (DAMAGE=1, HEAL=2, NO_DMG_HEAL=4)
    │     ├─ SpellPhaseMask (HIT=2, CAST=1, FINISH=4)
    │     └─ HitMask (Default: NORMAL|CRITICAL|ABSORB)
    ├─ 4. CallScriptCheckProcHandlers() ← Dein CheckProc()
    ├─ 5. CheckEffectProc() pro Effekt
    └─ 6. Chance Roll (100 = immer)
    ↓
TriggerProcOnEvent()
    ├─ CallScriptProcHandlers() ← Dein HandleProc() + PreventDefaultAction()
    └─ (Default: HandleProcTriggerSpellAuraProc → CastSpell)
```

#### Wichtig: DBC EffectSpellClassMask wird NICHT geprüft!

Die "Class Mask Target Spells" im WoW Spell Editor (DBC-Feld `EffectSpellClassMask`) hat **keinen Einfluss** auf den Proc-Ablauf bei `SPELL_AURA_PROC_TRIGGER_SPELL`. Der Proc wird ausschließlich über die `spell_proc` Tabelle und C++ Script Hooks gefiltert. Die Class Mask im DBC kann beliebig sein oder leer — sie wird von `HandleProcTriggerSpellAuraProc()` ignoriert.

#### Kritisch: SpellFamilyFlags immer per Debug-Log verifizieren!

**SpellFamilyFlags in der DBC können von "Standard-WotLK-Werten" abweichen.** Beispiel aus der Praxis:

| Spell | Erwartete Flags (Online-Referenzen) | Tatsächliche Flags (unsere DBC) |
|-------|--------------------------------------|--------------------------------|
| Bloodthirst (23881) | `flags[0]=0x40000000` (Bit 30) | `flags[0]=0x00000000, flags[1]=0x00000400` (Bit 42) |

**Regel:** Niemals SpellFamilyFlags aus Online-Datenbanken (wowhead, wowdb, etc.) für C++ Code übernehmen, ohne sie gegen die eigene Spell.dbc zu verifizieren. Diagnose-Pattern:

```cpp
LOG_INFO("module", "CheckProc: spell {} family {} flags[0]=0x{:08X} flags[1]=0x{:08X}",
    spellInfo->Id, spellInfo->SpellFamilyName,
    spellInfo->SpellFamilyFlags[0], spellInfo->SpellFamilyFlags[1]);
```

#### spell_proc Tabelle — Pflichtfelder

```sql
INSERT INTO `spell_proc` (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`,
    `SpellFamilyMask1`, `SpellFamilyMask2`, `ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`,
    `HitMask`, `AttributesMask`, `DisableEffectsMask`, `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`)
VALUES (900116, 0, 0, 0, 0, 0, 0x10, 1, 2, 0, 0, 0, 0, 100, 0, 0);
--            │  │  │        │    │  │  │                  │
--            │  │  │        │    │  │  └─ Chance 100%     │
--            │  │  │        │    │  └─ SpellPhaseMask=HIT │
--            │  │  │        │    └─ SpellTypeMask=DAMAGE  │
--            │  │  │        └─ ProcFlags=DONE_SPELL_MELEE_DMG_CLASS
--            │  │  └─ FamilyMask=0 (kein DBC-Filter, Script entscheidet)
--            │  └─ FamilyName=0 (akzeptiert alle Spell-Familien)
--            └─ SchoolMask=0 (alle Schulen)
```

**Tipp:** `SpellFamilyName=0` und `SpellFamilyMask=0` in spell_proc bedeutet "akzeptiere alles" — die Filterung wird komplett dem C++ `CheckProc` überlassen.

### SQL-Registrierung

Jeder SpellScript muss in der `spell_script_names` Tabelle registriert werden:

```sql
DELETE FROM `spell_script_names` WHERE `spell_id` IN (900106);
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
(900106, 'spell_custom_paragon_strike');
```

Für Proc-basierte Spells zusätzlich `spell_proc`:

```sql
INSERT INTO `spell_proc` (`SpellId`, `ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`, `Chance`, `Cooldown`)
VALUES (900116, 0x10, 1, 2, 0, 100, 0);
```

## DBC-System (Data-Base-Client Files)

### Was sind DBC-Dateien?

DBC-Dateien sind binäre Datendateien aus dem WoW-Client, die Spielmechanik-Definitionen enthalten (Spells, Items, Enchantments, Maps, etc.). Der Server lädt diese beim Start und verwendet sie als Grundlage für die gesamte Spiellogik.

### DBC-Ladevorgang

```
Server-Start
    ↓
World::SetInitialWorldSettings()
    ↓
LoadDBCStores(dataPath)
    ↓
    ├─ Liest .dbc Dateien von Disk
    ├─ Parsed binäres Format (Header + Records + String Block)
    ├─ Speichert in DBCStorage<T> Templates
    └─ Fallback: Lädt Overrides aus DB (z.B. spellitemenchantment_dbc)
    ↓
Spell.dbc → sSpellStore → SpellInfo (über SpellMgr)
```

### Wichtige Spell-bezogene DBC-Dateien

| DBC-Datei | C++ Store | Inhalt |
|-----------|-----------|--------|
| `Spell.dbc` | `sSpellStore` | Alle Spell-Definitionen (ID, Effekte, Attribute, Zeiten) |
| `SpellCategory.dbc` | `sSpellCategoryStore` | Spell-Kategorien (Cooldown-Gruppen) |
| `SpellDuration.dbc` | `sSpellDurationStore` | Spell-Dauer (Base, Per-Level, Max) |
| `SpellCastTimes.dbc` | `sSpellCastTimesStore` | Cast-Zeiten |
| `SpellRadius.dbc` | `sSpellRadiusStore` | AoE-Radien |
| `SpellRange.dbc` | `sSpellRangeStore` | Spell-Reichweiten |
| `SpellItemEnchantment.dbc` | `sSpellItemEnchantmentStore` | Item-Enchantment-Definitionen |
| `SpellDifficulty.dbc` | `sSpellDifficultyStore` | Spell-Varianten nach Dungeon-Schwierigkeit |

### DBC-Feldformat

```cpp
enum DbcFieldFormat
{
    FT_NA = 'x',       // nicht verwendet, 4 Bytes
    FT_NA_BYTE = 'X',  // nicht verwendet, 1 Byte
    FT_STRING = 's',   // char* (Offset in String-Tabelle)
    FT_FLOAT = 'f',    // float
    FT_INT = 'i',      // uint32
    FT_BYTE = 'b',     // uint8
    FT_SORT = 'd',     // Sort-Feld
    FT_IND = 'n',      // Index-Feld
    FT_LOGIC = 'l'     // Boolean
};
```

### Zusammenspiel DBC ↔ SpellScript

```
    SpellInfo (aus Spell.dbc)
    ├── Id                    ← Spell-ID
    ├── Effects[0..2]         ← Bis zu 3 Effekte pro Spell
    │   ├── Effect            ← Effekt-Typ (SPELL_EFFECT_SCHOOL_DAMAGE, etc.)
    │   ├── ApplyAuraName     ← Aura-Typ (SPELL_AURA_PERIODIC_DAMAGE, etc.)
    │   ├── BasePoints        ← Basis-Wert des Effekts
    │   ├── DieSides          ← Random-Range
    │   ├── TriggerSpell      ← ID eines getriggerten Spells
    │   └── MiscValue         ← Zusatz-Parameter
    ├── Attributes            ← Spell-Flags (Channeled, Passive, etc.)
    ├── Category              ← Cooldown-Gruppe
    ├── CastTimeEntry         ← Verweis auf SpellCastTimes.dbc
    ├── DurationEntry         ← Verweis auf SpellDuration.dbc
    └── RangeEntry            ← Verweis auf SpellRange.dbc
```

**Im SpellScript wird SpellInfo so verwendet:**

```cpp
void Validate(SpellInfo const* spellInfo) override
{
    // Prüfe ob der erwartete Effekt-Typ im DBC korrekt ist
    if (spellInfo->Effects[EFFECT_0].ApplyAuraName != SPELL_AURA_MOD_POWER_REGEN)
    {
        LOG_ERROR("spells", "Spell {} hat falschen Aura-Typ", spellInfo->Id);
        return false;
    }
}
```

### DBC-Override über Datenbank

Für Custom-Enchantments (mod-paragon-itemgen) werden DBC-Einträge via `spellitemenchantment_dbc` Tabelle überschrieben:

```sql
-- Enchantment: +42 Stamina
INSERT INTO `spellitemenchantment_dbc` (`ID`, `Effect_1`, `EffectPointsMin_1`, `EffectArg_1`, `Name_Lang_enUS`)
VALUES (900042, 5, 42, 7, '+42 Stamina');
-- Type 5 = ITEM_ENCHANTMENT_TYPE_STAT, Arg 7 = ITEM_MOD_STAMINA
```

**Enchantment-ID-Schema (mod-paragon-itemgen):**

```
Basis: 900000
Formel: 900000 + statIndex × 1000 + amount (1-666)

Index 0  = Stamina     → 900001-900666
Index 1  = Strength    → 901001-901666
Index 2  = Agility     → 902001-902666
...
Index 16 = Mana Regen  → 916001-916666

920001 = "Cursed" Marker (nur Label, kein Stat-Effekt)
950001-950099 = Passive Spell Enchantments
```

### DBC-Patching für Client

Custom DBC-Einträge müssen auch im Client vorhanden sein, damit Tooltips korrekt angezeigt werden. Dafür gibt es:

1. **Server-seitig**: `spellitemenchantment_dbc` Tabelle in `acore_world` DB
2. **Client-seitig**: `tools/patch_dbc.py` aus mod-paragon-itemgen patcht die `SpellItemEnchantment.dbc` im Client-MPQ

## Modul-System (AzerothCore)

### Wie Module geladen werden

```
CMake Build-Phase:
    modules/CMakeLists.txt
    ↓ GetModuleSourceList()
    ↓ Für jedes Modul: Quellen sammeln, RegisterModuleScript()
    ↓ ConfigureScriptLoader() generiert ModulesLoader.cpp
    ↓ → Forward Declarations aller AddXXXScripts()
    ↓ → AddModulesScripts() ruft alle Loader auf

Server-Start:
    ScriptMgr::Initialize()
    ↓ SetScriptLoader(scriptLoaderCallback)
    ↓ SetModulesLoader(modulesLoaderCallback)
    ↓ AddModulesScripts()
    ↓ → Addmod_paragonScripts()
    ↓ → Addmod_custom_spellsScripts()
    ↓ → Addmod_paragon_itemgenScripts()
```

### Modul-Verzeichnisstruktur

```
modules/mein-modul/
├── CMakeLists.txt              # Build-Konfiguration (optional, Auto-Detection)
├── conf/
│   └── mein_modul.conf.dist   # Konfigurations-Template
├── data/sql/
│   ├── db-world/               # World-DB SQL
│   └── db-characters/          # Characters-DB SQL
├── src/
│   ├── mein_modul_loader.cpp   # Entry Point: AddmeinmodulScripts()
│   └── MeinModul.cpp           # Logik
└── include.sh                  # SQL-Pfad-Registrierung
```

### Loader-Namenskonvention

Die Loader-Funktion muss nach dem Modulnamen benannt werden, wobei `-` durch `_` ersetzt wird:

- `mod-paragon` → `Addmod_paragonScripts()`
- `mod-custom-spells` → `Addmod_custom_spellsScripts()`
- `mod-paragon-itemgen` → `Addmod_paragon_itemgenScripts()`

## Aktuelle Custom Spells (mod-custom-spells)

| Spell ID | Name | Typ | Effekt |
|----------|------|-----|--------|
| 900106 | Paragon Strike | SpellScript | SCHOOL_DAMAGE: 666 + 66% AP, +1%/Paragon-Level |
| 900107 | Bladestorm CD Reduce | AuraScript | PROC: Bei Melee-Damage → Bladestorm (46927) CD um 0.5s reduzieren |
| 900116 | Bloody Whirlwind Passive | AuraScript | PROC: Bei Bloodthirst → Buff 900115 anwenden |
| 1680 | Whirlwind Consume | SpellScript | AFTER_CAST: Entfernt alle Stacks von Buff 900115 |

## Paragon-System (mod-paragon)

### Kernmechanik

- **Account-weit**: Level und XP werden über alle Charaktere geteilt
- **Pro Charakter**: Stat-Punkt-Verteilung ist individuell
- **XP-Quellen**: Kreatur-Kills (nach Schwierigkeit), Quests (3 XP)
- **Level-Formel**: `100 × 1.1^(level-1)` XP pro Level (zählt herunter)
- **5 Punkte pro Level-Up** als Item 920920

### Aura-IDs

| Aura ID | Stat | System |
|---------|------|--------|
| 100000 | Level-Counter (Stack = Level) | C++ |
| 7507 | Strength | C++ |
| 100001 | Strength | Lua |
| 100002 | Intellect | C++/Lua |
| 100003 | Agility | C++/Lua |
| 100004 | Spirit | C++/Lua |
| 100005 | Stamina | C++/Lua |
| 100016-100026 | Haste, ArmorPen, SP, Crit, MountSpeed, ManaReg, Hit, Block, Expertise, Parry, Dodge | C++ |

### Bekannte Probleme

- C++ und Lua verwenden verschiedene Aura-IDs für Strength (7507 vs 100001)
- NPC-Script (`npc_paragon`) wird im Loader nicht registriert
- Punkt-Reset setzt nur 5 von 16 Stats zurück
- Keine Prepared Statements (SQL Injection Risiko)
- Konfiguration wird nicht aus `.conf` gelesen (alles hardcoded)

## Item-Generator (mod-paragon-itemgen)

### 5-Slot Enchantment System

| Slot | Inhalt | Quelle |
|------|--------|--------|
| 7 (PROP_0) | Stamina | Immer |
| 8 (PROP_1) | Main Stat (Str/Agi/Int/Spi) | Spieler-Wahl |
| 9 (PROP_2) | Combat Rating 1 | Zufällig aus Rollen-Pool |
| 10 (PROP_3) | Combat Rating 2 | Zufällig, kein Duplikat |
| 11 (PROP_4) | Passive Spell / "Cursed" / leer | Nur bei Cursed Items |

### Rollen-Pools

| Rolle | Combat Ratings |
|-------|----------------|
| Tank (0) | Dodge, Parry, Defense, Block, Hit, Expertise |
| DPS (1) | Crit, Haste, Hit, ArmorPen, Expertise, AP, SP |
| Healer (2) | Crit, Haste, SpellPower, ManaRegen |

### Cursed Items (Standard: 1% Chance)

- Alle Stats auf 150% des Max-Werts
- Item wird Soulbound
- Shadow-Visual auf dem Spieler
- Exklusiver passiver Spell-Bonus (Slot 11, spec-basiert)
- Lua-Addon färbt Tooltip lila

## Wichtige Spell/Item/NPC IDs

| Typ | ID | Beschreibung |
|-----|-----|-------------|
| Spell | 900106 | Paragon Strike |
| Spell | 900107 | Bladestorm CD Reduce |
| Spell | 900114 | Whirlwind Proc Aura (500ms ICD) |
| Spell | 900115 | Bloody Whirlwind Buff |
| Spell | 900116 | Bloody Whirlwind Passive |
| Spell | 1680 | Whirlwind (Override) |
| Spell | 46927 | Bladestorm (Original) |
| Spell | 23881 | Bloodthirst (Original) |
| Item | 920920 | Paragon Points (Unspent) |
| NPC | 900100 | Paragon Spec Selection NPC |
| Enchant | 900001-916666 | Stat-Enchantments (17 Stats × 666 Stufen) |
| Enchant | 920001 | "Cursed" Marker |
| Enchant | 950001-950099 | Passive Spell Enchantments |

## Datenbank-Tabellen (Custom)

### Characters DB

| Tabelle | Modul | Zweck |
|---------|-------|-------|
| `character_paragon` | mod-paragon | Account-weites Level/XP |
| `character_paragon_points` | mod-paragon | Pro-Charakter Stat-Verteilung (16 Stats) |
| `character_paragon_role` | mod-paragon-itemgen | Rolle + Main Stat Wahl |
| `character_paragon_item` | mod-paragon-itemgen | Tracking enchanteter Items |
| `character_paragon_spec` | mod-paragon-itemgen | Talent-Spec Auswahl |

### World DB

| Tabelle | Modul | Zweck |
|---------|-------|-------|
| `spell_script_names` | mod-custom-spells | SpellScript ↔ Spell-ID Zuordnung |
| `spell_proc` | mod-custom-spells | Proc-Konfiguration |
| `spellitemenchantment_dbc` | mod-paragon-itemgen | DBC-Override für 11.323 Custom-Enchantments |
| `paragon_passive_spell_pool` | mod-paragon-itemgen | Pool verfügbarer passiver Spells |
| `paragon_spec_spell_assign` | mod-paragon-itemgen | Spec → Spell Zuordnungen (gewichtet) |

## Komplette Datenbankstruktur (mysql_column_list_all.txt)

Die Datei `mysqldbextracts/mysql_column_list_all.txt` enthält die vollständige Spaltenstruktur aller 304 Tabellen der AzerothCore-Datenbank (acore_world + acore_characters + acore_auth). Insgesamt 4.129 Spalten.

### Tabellen-Übersicht nach Kategorie

#### Achievement-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `achievement_category_dbc` | 20 | ID, Name_Lang_* (16 Locales) |
| `achievement_criteria_data` | 5 | criteria_id, ScriptName, type, value1, value2 |
| `achievement_criteria_dbc` | 31 | Achievement_Id, Asset_Id, Description_Lang_* |
| `achievement_dbc` | 62 | Category, Description_Lang_*, Flags, ID, Map |
| `achievement_reward` | 8 | ID, ItemID, MailTemplateID, Sender, Subject |
| `achievement_reward_locale` | 4 | ID, Locale, Subject, Text |

#### Kreatur-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `creature` | 27 | guid, id1-id3, map, position_x/y/z, spawntimesecs |
| `creature_addon` | 8 | guid, path_id, mount, bytes1, bytes2, emote, auras |
| `creature_template` | 57 | entry, name, minlevel, maxlevel, faction, npcflag, ScriptName, AIName, DamageModifier, HealthModifier |
| `creature_template_addon` | 8 | entry, bytes1, bytes2, emote, auras |
| `creature_template_model` | 6 | CreatureID, Idx, CreatureDisplayID, Probability |
| `creature_template_movement` | 8 | CreatureId, Ground, Flight, Chase |
| `creature_template_resistance` | 4 | CreatureID, School, Resistance |
| `creature_template_spell` | 4 | CreatureID, Index, Spell |
| `creature_template_locale` | 5 | entry, locale, Name, Title |
| `creature_classlevelstats` | 18 | level, class, basehp0-4, basemana, basearmor, attackpower, Agility |
| `creature_equip_template` | 6 | CreatureID, ID, ItemID1-3 |
| `creature_text` | 13 | CreatureID, GroupID, ID, Text, Type, BroadcastTextId |
| `creature_loot_template` | 10 | Entry, Item, Chance, GroupId, MinCount, MaxCount |
| `creature_onkill_reputation` | 10 | creature_id, RewOnKillRepFaction1/2, RewOnKillRepValue1/2 |
| `creature_formations` | 7 | leaderGUID, memberGUID, dist, angle, groupAI |
| `creature_summon_groups` | 11 | entry, groupId, position_x/y/z |
| `creaturedisplayinfo_dbc` | 16 | ID, ModelID, CreatureModelScale, BloodID |
| `creaturefamily_dbc` | 28 | ID, Name_Lang_*, CategoryEnumID |
| `creaturemodeldata_dbc` | 28 | ID, ModelName, CollisionWidth/Height |
| `creaturespelldata_dbc` | 9 | ID, Spells_1-4, Availability_1-4 |
| `creaturetype_dbc` | 19 | ID, Name_Lang_*, Flags |

#### Item-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `item_template` | 138 | entry, class, subclass, name, Quality, ItemLevel, RequiredLevel, stat_type1-10, stat_value1-10, dmg_min1/2, dmg_max1/2, armor, spellid_1-5, socketColor_1-3, ScriptName |
| `item_template_locale` | 5 | ID, locale, Name, Description |
| `item_dbc` | 8 | ID, ClassID, SubclassID, DisplayInfoID, InventoryType |
| `item_enchantment_template` | 3 | entry, ench, chance |
| `item_set_names` | 4 | entry, name, InventoryType |
| `itemdisplayinfo_dbc` | 25 | ID, ModelName, Flags, GeosetGroup |
| `itemextendedcost_dbc` | 16 | ID, HonorPoints, ArenaPoints, ItemID_1-5, ItemCount_1-5 |
| `itemrandomproperties_dbc` | 24 | ID, Name_Lang_*, Enchantment_1-5 |
| `itemrandomsuffix_dbc` | 29 | ID, Name_Lang_*, Enchantment_1-5, AllocationPct_1-5 |
| `itemset_dbc` | 53 | ID, Name_Lang_*, ItemID_1-17, SetSpellID_1-8 |

#### Spell-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `spell_dbc` | 234 | ID, Attributes, AttributesEx-Ex7, SpellName_Lang_*, Effects, Targets, CastingTimeIndex, DurationIndex, RangeIndex, SpellFamilyName, SpellFamilyFlags |
| `spell_script_names` | 2 | spell_id, ScriptName |
| `spell_proc` | 16 | SpellId, ProcFlags, SpellTypeMask, Chance, Cooldown, Charges |
| `spell_area` | 10 | spell, area, quest_start/end, aura_spell, gender |
| `spell_bonus_data` | 6 | entry, direct_bonus, dot_bonus, ap_bonus, comments |
| `spell_custom_attr` | 2 | spell_id, attributes |
| `spell_enchant_proc_data` | 5 | entry, customChance, PPMChance, procEx |
| `spell_group` | 2 | id, spell_id |
| `spell_group_stack_rules` | 3 | group_id, stack_rule, description |
| `spell_linked_spell` | 4 | spell_trigger, spell_effect, type, comment |
| `spell_loot_template` | 10 | Entry, Item, Chance, GroupId |
| `spell_ranks` | 3 | first_spell_id, spell_id, rank |
| `spell_required` | 2 | spell_id, req_spell |
| `spell_target_position` | 8 | ID, EffectIndex, MapID, PositionX/Y/Z |
| `spell_threat` | 4 | entry, flatMod, pctMod, apPctMod |
| `spellcasttimes_dbc` | 4 | ID, Base, PerLevel, Minimum |
| `spellcategory_dbc` | 2 | ID, Flags |
| `spelldifficulty_dbc` | 5 | ID, DifficultySpellID_1-4 |
| `spellduration_dbc` | 4 | ID, Duration, DurationPerLevel, MaxDuration |
| `spellitemenchantment_dbc` | 38 | ID, Charges, Effect_1-3, EffectPointsMin_1-3, EffectPointsMax_1-3, EffectArg_1-3, Name_Lang_*, Condition_Id, Flags |
| `spellradius_dbc` | 4 | ID, Radius, RadiusPerLevel, RadiusMax |
| `spellrange_dbc` | 40 | ID, RangeMin/Max, DisplayName_Lang_* |
| `spellrunecost_dbc` | 5 | ID, Blood, Frost, Unholy, RunicPower |

#### Quest-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `quest_template` | 105 | ID, QuestType, Flags, RewardChoiceItemID1-6, RewardItemId1-4, RewardMoney, RewardXPDifficulty |
| `quest_template_addon` | 18 | ID, MaxLevel, AllowableClasses, ExclusiveGroup, BreadcrumbForQuestId |
| `quest_template_locale` | 12 | ID, locale, Title, Details, Objectives |
| `quest_details` | 10 | ID, Emote1-4, EmoteDelay1-4 |
| `quest_offer_reward` | 11 | ID, Emote1-4, RewardText |
| `quest_request_items` | 5 | ID, EmoteOnComplete, EmoteOnIncomplete, CompletionText |
| `quest_poi` | 9 | id, ObjectiveIndex, MapID, Floor, Flags |
| `questxp_dbc` | 11 | ID, Difficulty_1-10 |
| `questsort_dbc` | 18 | ID, SortName_Lang_* |

#### NPC & Gossip
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `npc_text` | 90 | ID, BroadcastTextID0-7, text0_0/text0_1 ... text7_0/text7_1 |
| `npc_vendor` | 7 | entry, item, maxcount, incrtime, ExtendedCost |
| `npc_trainer` | 7 | ID, SpellID, MoneyCost, ReqSkillLine, ReqSkillRank, ReqLevel |
| `npc_spellclick_spells` | 4 | npc_entry, spell_id, cast_flags, user_type |
| `gossip_menu` | 2 | MenuID, TextID |
| `gossip_menu_option` | 14 | MenuID, OptionID, OptionIcon, OptionText, ActionMenuID |

#### GameObject-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `gameobject` | 21 | guid, id, map, position_x/y/z |
| `gameobject_template` | 35 | entry, type, displayId, name, Data0-23, AIName, ScriptName |
| `gameobject_loot_template` | 10 | Entry, Item, Chance, GroupId |

#### Map & Area
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `map_dbc` | 66 | ID, Directory, InstanceType, MapName_Lang_*, MapType |
| `mapdifficulty_dbc` | 23 | ID, MapID, Difficulty, MaxPlayers |
| `areatable_dbc` | 36 | ID, ContinentID, AreaName_Lang_*, Flags, AreaBit |
| `worldmaparea_dbc` | 11 | ID, MapID, AreaID, AreaName |

#### Charakter & Klassen
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `chrclasses_dbc` | 60 | ID, Name_Lang_*, DisplayPower, Flags |
| `chrraces_dbc` | 69 | ID, Name_Lang_*, ClientFilestring, Alliance, BaseLanguage |
| `chartitles_dbc` | 37 | ID, Name1_Lang_*, Mask_ID |
| `charstartoutfit_dbc` | 77 | ClassID, RaceID, SexID, ItemID_1-24 |
| `playercreateinfo` | 8 | race, class, map, position_x/y/z |
| `player_class_stats` | 9 | Class, Level, BaseHP, BaseMana, Strength, Agility, Stamina, Intellect, Spirit |
| `player_race_stats` | 6 | Race, Strength, Agility, Stamina, Intellect, Spirit |
| `player_xp_for_level` | 2 | Level, Experience |

#### Talent-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `talent_dbc` | 23 | ID, TabID, TierID, ColumnIndex, SpellRank_1-9 |
| `talenttab_dbc` | 24 | ID, Name_Lang_*, ClassMask, BackgroundFile |
| `skillline_dbc` | 56 | ID, CategoryID, SkillCostsID, Name_Lang_* |
| `skilllineability_dbc` | 14 | ID, SkillLine, Spell, MinSkillLineRank, ClassMask |

#### Loot-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `creature_loot_template` | 10 | Entry, Item, Reference, Chance, QuestRequired, MinCount, MaxCount, GroupId |
| `gameobject_loot_template` | 10 | (gleiche Struktur) |
| `item_loot_template` | 10 | (gleiche Struktur) |
| `fishing_loot_template` | 10 | (gleiche Struktur) |
| `skinning_loot_template` | 10 | (gleiche Struktur) |
| `pickpocketing_loot_template` | 10 | (gleiche Struktur) |
| `milling_loot_template` | 10 | (gleiche Struktur) |
| `prospecting_loot_template` | 10 | (gleiche Struktur) |
| `disenchant_loot_template` | 10 | (gleiche Struktur) |
| `reference_loot_template` | 10 | (gleiche Struktur) |
| `mail_loot_template` | 10 | (gleiche Struktur) |
| `spell_loot_template` | 10 | (gleiche Struktur) |

#### Smart AI (SAI)
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `smart_scripts` | 31 | entryorguid, source_type, id, link, event_type, event_phase_mask, event_param1-6, action_type, action_param1-6, target_type, target_param1-4, comment |
| `conditions` | 15 | SourceTypeOrReferenceId, ConditionTypeOrReference, ConditionValue1-3, Comment |

#### Vehicle-System
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `vehicle_dbc` | 40 | ID, Flags, CameraFade*, CameraPitchOffset, CameraYawOffset |
| `vehicleseat_dbc` | 58 | ID, Flags, AttachmentID, AttachmentOffset* |
| `vehicle_accessory` | 7 | guid, accessory_entry, seat_id |
| `vehicle_template_accessory` | 7 | entry, accessory_entry, seat_id |

#### Kampf & Stats
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `gtchancetomeleecrit_dbc` | 2 | ID, Data |
| `gtchancetomeleecritbase_dbc` | 2 | ID, Data |
| `gtchancetospellcrit_dbc` | 2 | ID, Data |
| `gtchancetospellcritbase_dbc` | 2 | ID, Data |
| `gtcombatratings_dbc` | 2 | ID, Data |
| `gtregenhpperspt_dbc` | 2 | ID, Data |
| `gtregenmpperspt_dbc` | 2 | ID, Data |
| `scalingstatdistribution_dbc` | 22 | ID, StatID_1-10, Bonus_1-10 |
| `scalingstatvalues_dbc` | 24 | ID, Charlevel, verschiedene Armor/DPS-Werte |
| `randproppoints_dbc` | 16 | ID, Epic_1-5, Superior_1-5, Good_1-5 |

#### Fraktionen
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `faction_dbc` | 57 | ID, ReputationIndex, ReputationRaceMask, Name_Lang_*, Description_Lang_* |
| `factiontemplate_dbc` | 14 | ID, Faction, Flags, FriendGroup, EnemyGroup, Enemies_1-4, Friend_1-4 |

#### Custom-Tabellen (Paragon-Projekt)
| Tabelle | Spalten | Modul | Wichtige Felder |
|---------|---------|-------|-----------------|
| `paragon_passive_spell_pool` | 6 | mod-paragon-itemgen | spellId, enchantmentId, name, category, minParagonLevel, minItemLevel |
| `paragon_spec_spell_assign` | 3 | mod-paragon-itemgen | specId, enchantmentId, weight |

#### Sonstige wichtige Tabellen
| Tabelle | Spalten | Wichtige Felder |
|---------|---------|-----------------|
| `battleground_template` | 13 | ID, MinPlayersPerTeam, MaxPlayersPerTeam, Comment |
| `battlemasterlist_dbc` | 32 | ID, MapID_1-8, InstanceType |
| `game_event` | 10 | eventEntry, start_time, end_time, description |
| `game_tele` | 7 | id, name, map, position_x/y/z |
| `game_graveyard` | 6 | ID, Map, x, y, z, Comment |
| `instance_template` | 4 | map, parent, script, allowMount |
| `dungeonencounter_dbc` | 23 | ID, MapID, Difficulty, Name_Lang_* |
| `gemproperties_dbc` | 5 | ID, Enchant_Id, Type |
| `glyphproperties_dbc` | 4 | ID, SpellID, GlyphSlotFlags |
| `broadcast_text` | 14 | ID, MaleText, FemaleText, EmoteID1-3 |
| `warden_checks` | 8 | id, type, data, address, length |
| `disables` | 6 | sourceType, entry, flags, comment |
| `updates` | 5 | name, hash, state, timestamp, speed |

> **Vollständige Referenz**: Für die exakte Spaltenliste jeder Tabelle siehe `mysqldbextracts/mysql_column_list_all.txt`. Format: `` `tabellenname`.`spaltenname` ``

## DBC-Datei-Inventar (246 Dateien)

Der Ordner `dbc/` enthält alle 246 DBC-Dateien des WoW 3.3.5a Clients im WDBC-Binärformat. Diese Dateien definieren die clientseitige Spielmechanik und werden vom Server beim Start geladen.

### DBC-Dateien nach Kategorie

#### Spell-bezogen (22 Dateien)
| Datei | Server-Store | Inhalt |
|-------|-------------|--------|
| `Spell.dbc` | `sSpellStore` | Alle Spell-Definitionen (234 Felder, 936 Bytes/Record) |
| `SpellCastTimes.dbc` | `sSpellCastTimesStore` | Cast-Zeiten (Base, PerLevel, Minimum) |
| `SpellCategory.dbc` | `sSpellCategoryStore` | Spell-Kategorien (Cooldown-Gruppen) |
| `SpellChainEffects.dbc` | — | Visuelle Ketten-Effekte |
| `SpellDescriptionVariables.dbc` | — | Tooltip-Variablen |
| `SpellDifficulty.dbc` | `sSpellDifficultyStore` | Spell-Varianten nach Dungeon-Schwierigkeit |
| `SpellDispelType.dbc` | — | Dispel-Typen (Magic, Curse, Disease, Poison) |
| `SpellDuration.dbc` | `sSpellDurationStore` | Spell-Dauer (Duration, PerLevel, Max) |
| `SpellEffectCameraShakes.dbc` | — | Kamera-Shake bei Spell-Effekten |
| `SpellFocusObject.dbc` | `sSpellFocusObjectStore` | Benötigte Objekte zum Casten |
| `SpellIcon.dbc` | `sSpellIconStore` | Spell-Icon-Pfade |
| `SpellItemEnchantment.dbc` | `sSpellItemEnchantmentStore` | **Item-Enchantment-Definitionen** (38 Felder, Custom-Patching via `patch_dbc.py`) |
| `SpellItemEnchantmentCondition.dbc` | `sSpellItemEnchantmentConditionStore` | Enchantment-Bedingungen |
| `SpellMechanic.dbc` | — | Spell-Mechaniken (Stun, Root, Silence, etc.) |
| `SpellMissile.dbc` | — | Geschoss-Parameter |
| `SpellMissileMotion.dbc` | — | Geschoss-Bewegungsmuster |
| `SpellRadius.dbc` | `sSpellRadiusStore` | AoE-Radien (Radius, PerLevel, Max) |
| `SpellRange.dbc` | `sSpellRangeStore` | Spell-Reichweiten (Min, Max, Display) |
| `SpellRuneCost.dbc` | `sSpellRuneCostStore` | DK-Runenkosten (Blood, Frost, Unholy, RunicPower) |
| `SpellShapeshiftForm.dbc` | `sSpellShapeshiftFormStore` | Shapeshift-Formen (Druid, etc.) |
| `SpellVisual.dbc` | — | Visuelle Spell-Darstellung |
| `SpellVisualEffectName.dbc` | — | Effekt-Namen |
| `SpellVisualKit.dbc` | — | Visuelle Kit-Zusammenstellungen |
| `SpellVisualKitAreaModel.dbc` | — | Area-basierte visuelle Modelle |
| `SpellVisualKitModelAttach.dbc` | — | Modell-Attachment-Punkte |
| `SpellVisualPrecastTransitions.dbc` | — | Precast-Übergangseffekte |

#### Charakter/Spieler (10 Dateien)
| Datei | Inhalt |
|-------|--------|
| `ChrClasses.dbc` | Klassen-Definitionen (Name, DisplayPower, Flags) |
| `ChrRaces.dbc` | Rassen-Definitionen (Name, Faction, Models) |
| `CharBaseInfo.dbc` | Basis-Charakter-Info |
| `CharHairGeosets.dbc` | Frisuren-Geometrie |
| `CharHairTextures.dbc` | Frisuren-Texturen |
| `CharSections.dbc` | Charakter-Sektionen (Skin, Face, etc.) |
| `CharStartOutfit.dbc` | Start-Ausrüstung pro Klasse/Rasse |
| `CharTitles.dbc` | Verfügbare Titel |
| `CharVariations.dbc` | Charakter-Variationen |
| `CharacterFacialHairStyles.dbc` | Bart-Stile |

#### Item/Loot (16 Dateien)
| Datei | Inhalt |
|-------|--------|
| `Item.dbc` | Item-Basisdaten (Class, Subclass, DisplayInfo, InventoryType) |
| `ItemBagFamily.dbc` | Taschen-Familien (Ammo, Soul, Herb, etc.) |
| `ItemClass.dbc` | Item-Klassen (Weapon, Armor, Consumable, etc.) |
| `ItemCondExtCosts.dbc` | Erweiterte Kosten-Bedingungen |
| `ItemDisplayInfo.dbc` | Visuelle Item-Darstellung |
| `ItemExtendedCost.dbc` | Erweiterte Kosten (Honor, Arena, Token) |
| `ItemGroupSounds.dbc` | Item-Gruppen-Sounds |
| `ItemLimitCategory.dbc` | Item-Limit-Kategorien (Gems, etc.) |
| `ItemPetFood.dbc` | Pet-Futter-Typen |
| `ItemPurchaseGroup.dbc` | Kauf-Gruppen |
| `ItemRandomProperties.dbc` | "of the Bear"-Zufallseigenschaften |
| `ItemRandomSuffix.dbc` | Zufalls-Suffix-Enchantments |
| `ItemSet.dbc` | Set-Definitionen (Items, Set-Boni) |
| `ItemSubClass.dbc` | Item-Unterklassen |
| `ItemSubClassMask.dbc` | Unterklassen-Masken |
| `ItemVisualEffects.dbc` / `ItemVisuals.dbc` | Visuelle Effekte |

#### Map/Area/Welt (16 Dateien)
| Datei | Inhalt |
|-------|--------|
| `Map.dbc` | Map-Definitionen (66 Felder, Name, Type, Instance) |
| `MapDifficulty.dbc` | Schwierigkeitsgrade pro Map |
| `AreaTable.dbc` | Gebiets-Definitionen (Name, Flags, Level) |
| `AreaGroup.dbc` | Gebiets-Gruppen |
| `AreaPOI.dbc` | Points of Interest |
| `AreaTrigger.dbc` | Trigger-Zonen (Position, Radius) |
| `WorldMapArea.dbc` | Weltkarten-Gebiete |
| `WorldMapContinent.dbc` | Weltkarten-Kontinente |
| `WorldMapOverlay.dbc` | Weltkarten-Overlays |
| `WorldMapTransforms.dbc` | Weltkarten-Transformationen |
| `WorldSafeLocs.dbc` | Sichere Positionen (Friedhöfe, etc.) |
| `WorldStateUI.dbc` | Welt-Status-UI |
| `WorldStateZoneSounds.dbc` | Zonen-Sounds nach Status |
| `WorldChunkSounds.dbc` | Chunk-basierte Sounds |
| `DungeonMap.dbc` / `DungeonMapChunk.dbc` | Dungeon-Karten |
| `DungeonEncounter.dbc` | Dungeon-Encounter-Definitionen |

#### Talent/Skill (7 Dateien)
| Datei | Inhalt |
|-------|--------|
| `Talent.dbc` | Talent-Definitionen (TabID, Tier, Column, SpellRank_1-9) |
| `TalentTab.dbc` | Talent-Tabs (Name, ClassMask, Background) |
| `SkillLine.dbc` | Skill-Definitionen (Name, Category) |
| `SkillLineAbility.dbc` | Skill-Fähigkeiten (Spell ↔ Skill Zuordnung) |
| `SkillLineCategory.dbc` | Skill-Kategorien |
| `SkillRaceClassInfo.dbc` | Rassen/Klassen-Skill-Info |
| `SkillTiers.dbc` / `SkillCostsData.dbc` | Skill-Stufen und Kosten |

#### Kampf-Formeln (gt*.dbc, 12 Dateien)
| Datei | Inhalt |
|-------|--------|
| `gtBarberShopCostBase.dbc` | Friseur-Kosten pro Level |
| `gtChanceToMeleeCrit.dbc` | Melee-Crit-Chance pro Level/Klasse |
| `gtChanceToMeleeCritBase.dbc` | Basis-Melee-Crit |
| `gtChanceToSpellCrit.dbc` | Spell-Crit-Chance pro Level/Klasse |
| `gtChanceToSpellCritBase.dbc` | Basis-Spell-Crit |
| `gtCombatRatings.dbc` | Combat-Rating-Umrechnungen |
| `gtNPCManaCostScaler.dbc` | NPC-Manakosten-Skalierung |
| `gtOCTClassCombatRatingScalar.dbc` | Klassen-Combat-Rating-Skalare |
| `gtOCTRegenHP.dbc` | HP-Regeneration |
| `gtOCTRegenMP.dbc` | MP-Regeneration |
| `gtRegenHPPerSpt.dbc` | HP-Regen pro Spirit |
| `gtRegenMPPerSpt.dbc` | MP-Regen pro Spirit |

#### Faction (3 Dateien)
`Faction.dbc`, `FactionGroup.dbc`, `FactionTemplate.dbc`

#### Transport/Vehicle (7 Dateien)
`Vehicle.dbc`, `VehicleSeat.dbc`, `VehicleUIIndSeat.dbc`, `VehicleUIIndicator.dbc`, `TransportAnimation.dbc`, `TransportPhysics.dbc`, `TransportRotation.dbc`

#### Travel (4 Dateien)
`TaxiNodes.dbc`, `TaxiPath.dbc`, `TaxiPathNode.dbc`, `PvpDifficulty.dbc`

#### Audio (12 Dateien)
`SoundEntries.dbc`, `SoundEntriesAdvanced.dbc`, `SoundEmitters.dbc`, `SoundAmbience.dbc`, `SoundFilter.dbc`, `SoundFilterElem.dbc`, `SoundProviderPreferences.dbc`, `SoundSamplePreferences.dbc`, `SoundWaterType.dbc`, `ZoneMusic.dbc`, `ZoneIntroMusicTable.dbc`, `UISoundLookups.dbc`

#### Emotes (4 Dateien)
`Emotes.dbc`, `EmotesText.dbc`, `EmotesTextData.dbc`, `EmotesTextSound.dbc`

#### Holidays/Events (3 Dateien)
`Holidays.dbc`, `HolidayDescriptions.dbc`, `HolidayNames.dbc`

#### Sonstige (restliche Dateien)
`AnimationData.dbc`, `AttackAnimKits.dbc`, `AttackAnimTypes.dbc`, `AuctionHouse.dbc`, `BankBagSlotPrices.dbc`, `BannedAddOns.dbc`, `BarberShopStyle.dbc`, `BattlemasterList.dbc`, `CameraShakes.dbc`, `Cfg_Categories.dbc`, `Cfg_Configs.dbc`, `ChatChannels.dbc`, `ChatProfanity.dbc`, `CinematicCamera.dbc`, `CinematicSequences.dbc`, `CreatureDisplayInfo.dbc`, `CreatureDisplayInfoExtra.dbc`, `CreatureFamily.dbc`, `CreatureModelData.dbc`, `CreatureMovementInfo.dbc`, `CreatureSoundData.dbc`, `CreatureSpellData.dbc`, `CreatureType.dbc`, `CurrencyCategory.dbc`, `CurrencyTypes.dbc`, `DanceMoves.dbc`, `DeathThudLookups.dbc`, `DeclinedWord.dbc`, `DeclinedWordCases.dbc`, `DestructibleModelData.dbc`, `DurabilityCosts.dbc`, `DurabilityQuality.dbc`, `EnvironmentalDamage.dbc`, `Exhaustion.dbc`, `FileData.dbc`, `FootprintTextures.dbc`, `FootstepTerrainLookup.dbc`, `GameObjectArtKit.dbc`, `GameObjectDisplayInfo.dbc`, `GameTables.dbc`, `GameTips.dbc`, `GemProperties.dbc`, `GlyphProperties.dbc`, `GlyphSlot.dbc`, `GroundEffectDoodad.dbc`, `GroundEffectTexture.dbc`, `HelmetGeosetVisData.dbc`, `LFGDungeons.dbc`, `LFGDungeonExpansion.dbc`, `LFGDungeonGroup.dbc`, `LanguageWords.dbc`, `Languages.dbc`, `Light.dbc`, `LightFloatBand.dbc`, `LightIntBand.dbc`, `LightParams.dbc`, `LightSkybox.dbc`, `LiquidMaterial.dbc`, `LiquidType.dbc`, `LoadingScreens.dbc`, `LoadingScreenTaxiSplines.dbc`, `Lock.dbc`, `LockType.dbc`, `MailTemplate.dbc`, `Material.dbc`, `Movie.dbc`, `MovieFileData.dbc`, `MovieVariation.dbc`, `NPCSounds.dbc`, `NameGen.dbc`, `NamesProfanity.dbc`, `NamesReserved.dbc`, `ObjectEffect.dbc`, `ObjectEffectGroup.dbc`, `ObjectEffectModifier.dbc`, `ObjectEffectPackage.dbc`, `ObjectEffectPackageElem.dbc`, `OverrideSpellData.dbc`, `Package.dbc`, `PageTextMaterial.dbc`, `PaperDollItemFrame.dbc`, `ParticleColor.dbc`, `PetPersonality.dbc`, `PetitionType.dbc`, `PowerDisplay.dbc`, `QuestFactionReward.dbc`, `QuestInfo.dbc`, `QuestSort.dbc`, `QuestXP.dbc`, `RandPropPoints.dbc`, `Resistances.dbc`, `ScalingStatDistribution.dbc`, `ScalingStatValues.dbc`, `ScreenEffect.dbc`, `ServerMessages.dbc`, `SheatheSoundLookups.dbc`, `SpamMessages.dbc`, `StableSlotPrices.dbc`, `Startup_Strings.dbc`, `Stationery.dbc`, `StringLookups.dbc`, `SummonProperties.dbc`, `TeamContributionPoints.dbc`, `TerrainType.dbc`, `TerrainTypeSounds.dbc`, `TotemCategory.dbc`, `UnitBlood.dbc`, `UnitBloodLevels.dbc`, `VideoHardware.dbc`, `VocalUISounds.dbc`, `WMOAreaTable.dbc`, `WeaponImpactSounds.dbc`, `WeaponSwingSounds2.dbc`, `Weather.dbc`, `WowError_Strings.dbc`, `GMSurveyAnswers.dbc`, `GMSurveyCurrentSurvey.dbc`, `GMSurveyQuestions.dbc`, `GMSurveySurveys.dbc`, `GMTicketCategory.dbc`

#### Nicht-DBC-Dateien im dbc/ Ordner
| Datei | Inhalt |
|-------|--------|
| `Map.ini` | Feld-Format-Referenz für Map.dbc (66 Felder, alle ftInteger) |
| `component.wow-enUS.txt` | Client-Komponenten-Version |

## Code Style

### C++ (AzerothCore Standard)

- 4-Space Einrückung, keine Tabs
- UTF-8, LF Zeilenenden
- Max 80 Zeichen pro Zeile
- `Type const*` (nicht `const Type*`)
- `auto const&` (nicht `const auto&`)
- Keine Klammern um einzeilige if/else/for/while
- `UPPER_SNAKE_CASE` für Konstanten mit Prefix: `SPELL_CUSTOM_*`, `NPC_*`, `ITEM_*`
- `UpperCamelCase` für Klassen und Methoden
- `lowerCamelCase` für Parameter
- `_lowerCamelCase` für private Member

### SQL

- Backticks um Tabellen- und Spaltennamen
- DELETE vor INSERT (kein REPLACE)
- `SET @ENTRY := 7727;` für wiederholte Werte
- InnoDB, `utf8mb4`, `utf8mb4_unicode_ci`
- Keine Tabs, 4-Space Einrückung

### Lua

- Tab-Einrückung (Eluna/AIO Konvention)
- AIO Handler Pattern: `AIO.AddHandlers("NAME", {})`

## Build-Anleitung

```bash
# Core + Module bauen
mkdir -p build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$HOME/azeroth-server \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DSCRIPTS=static -DMODULES=static
make -j$(nproc)
make install
```

Module werden automatisch erkannt wenn sie in `azerothcore-wotlk/modules/` liegen:
```
modules/
├── mod-paragon/          → Symlink oder Clone
├── mod-paragon-itemgen/  → Symlink oder Clone
└── mod-custom-spells/    → Symlink oder Clone
```

## Workflow für KI-Assistenten

### Änderungen loggen

Jede Änderung an einem der Repos **muss** in `claude_log.md` dieses Repos erfasst werden mit:
- Zeitstempel (ISO 8601)
- Betroffenes Repo
- Beschreibung der Änderung
- Betroffene Dateien
- Commit-Hash (falls committed)

### Pläne dokumentieren

Geplante Features und Aufgaben werden ebenfalls in `claude_log.md` erfasst unter einer separaten Sektion.

### Konventionen

- Commit Messages: Conventional Commits Format
  - `feat(Core/Spells): Add new spell effect`
  - `fix(DB/SAI): Fix missing proc entry`
  - `docs: Update project documentation`
- Branch-Naming: `claude/<beschreibung>-<sessionId>`
- Sprache in Logs: Deutsch (Projektsprache) oder Englisch (Code-Kommentare)
