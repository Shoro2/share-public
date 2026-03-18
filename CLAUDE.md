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
| [share-public](https://github.com/Shoro2/share-public) | **Dieses Repo** — Zentrale Dokumentation, KI-Kontext, Änderungslog |

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
        // Nur bei Bloodthirst (Warrior SpellFamily 4, Flag 0x40000000)
        return spellInfo->SpellFamilyName == 4
            && (spellInfo->SpellFamilyFlags[0] & 0x40000000);
    }

    void OnProc(AuraEffect const* /*aurEff*/, ProcEventInfo& eventInfo)
    {
        GetTarget()->CastSpell(GetTarget(), 900115, true);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_custom_bloody_whirlwind_passive::CheckProc);
        OnEffectProc += AuraEffectProcFn(spell_custom_bloody_whirlwind_passive::OnProc,
            EFFECT_0, SPELL_AURA_DUMMY);
    }
};
```

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
| 900107 | Bladestorm CD Reduce | SpellScript | DUMMY: Reduziert Bladestorm (46927) CD um 0.5s pro Cast |
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
