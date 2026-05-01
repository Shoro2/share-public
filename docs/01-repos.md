# 01 — Repositories im Überblick

Alle 7 Repos im Detail. Branch-Hinweis: KI-Sessions arbeiten pro Repo auf einem eigenen Branch im Schema `claude/<beschreibung>-<sessionId>`.

## share-public — zentrale Wissensbasis

- **Zweck**: Doku, Tools, AIO-Framework, DBC-Dateien, DB-Extrakte, Änderungslog.
- **Sprache**: Markdown / Lua / Python.
- **Wichtige Inhalte**:
  - `AI_GUIDE.md`, `docs/` — KI-Leitfaden (neu, modular)
  - `CLAUDE.md` — alte Gesamtdoku (60 KB, Tiefenreferenz)
  - `claude_log.md` — Änderungshistorie aller Repos
  - `Dcore Concept.pdf` — ursprünglicher Konzept-Pitch (teils outdated)
  - `AIO_Server/`, `AIO_Client/` — AIO-Framework v1.75 (Server-Lua + WoW-Addon)
  - `dbc/` — 246 binäre WoW-3.3.5a DBC-Dateien
  - `mysqldbextracts/` — komplette DB-Spaltenstruktur (304 Tabellen) + CSVs (`creature_template`, `item_template`)
  - `python_scripts/` — DBC-Patcher (`patch_dbc.py`, `copy_spells_dbc.py`), Paragon-Spell-Generator (`add_paragon_spell.py`), Load-Test (`socket_stress_heavy.py`)
  - `SpellFamilies/` — Recherche zu SpellFamily-Flags

## azerothcore-wotlk — Server-Core

- **Zweck**: AzerothCore-Fork (Worldserver + Authserver). Enthält alle Custom-Module unter `modules/` und benötigt projekt-spezifische Spell.dbc-Patches.
- **Sprache**: C++17 (CMake, MySQL/MariaDB, Boost, OpenSSL).
- **Custom-Erweiterungen über Upstream hinaus**:
  - `OnPlayerCheckReagent` / `OnPlayerConsumeReagent` PlayerScript-Hooks (für mod-endless-storage Crafting-Integration)
  - Custom Spell.dbc mit Custom-Spells (100xxx, 900xxx)
- **CI**: Codestyle-Checks (C++, SQL), Multi-Compiler-Builds (clang-15/18, gcc-14, macOS, Windows).
- **Modulübersicht**: `modules/` — Custom-Module werden per CMake auto-detected.

## mod-paragon — Account-XP & 17-Stat-System

- **Zweck**: Post-LV80 Progression. Account-weite XP/Level, 5 Punkte/Level, 17 verteilbare Stats.
- **Architektur**: Hybrid C++/Lua.
  - C++ Aura-System (`ParagonPlayer.cpp`): lädt Stats aus DB, applied unsichtbare Stack-Auras
  - Lua AIO-UI (`Paragon_System_LUA/`): Frame zum Verteilen/Resetten von Punkten
- **17 Stats**: Str, Int, Agi, Spi, Sta, Haste, ArmorPen, SpellPower, Crit, MountSpeed, ManaRegen, Hit, Block, Expertise, Parry, Dodge, **LifeLeech** (heilt % vom verursachten Schaden, funktioniert auch über Pets/Totems).
- **Big+Small-Spell-System**: Stats über 255 Stacks via gepaarter Auras (Stack ×100 + Stack ×1).
- **DB-Tabellen** (acore_characters): `character_paragon` (Account-Level/XP), `character_paragon_points` (per Character, 17 Stat-Spalten).
- **Konfigurierbar**: 30+ `.conf`-Optionen (Aura-IDs, MaxStats[17], MaxLevel, XP-Belohnungen).

## mod-paragon-itemgen — Auto-Enchantments auf Loot

- **Zweck**: Beim Looten/Craften/Quest-Reward/Vendor-Kauf werden Items automatisch mit Paragon-Stat-Enchantments versehen.
- **5-Slot-Enchantment-System** (PROP_ENCHANTMENT_SLOT 0–4 = DB-Slots 7–11):
  - Slot 7: Stamina (immer)
  - Slot 8: Main-Stat (Spielerwahl: Str/Agi/Int/Spi)
  - Slot 9–10: 2 zufällige Combat-Ratings aus Rollen-Pool (Tank/MeleeDPS/CasterDPS/Healer)
  - Slot 11: bei **Cursed Items** ein Passive-Spell oder "Cursed"-Marker
- **Cursed Items** (1% Default-Chance): alle Stats ×1.5, Soulbound, Shadow-Visual, exklusiver Passive-Spell.
- **Tooltip-Anzeige**: AIO-basiert (Server liest Slot-IDs, decodiert Stat aus Formel `900000 + statIndex × 1000 + amount`, sendet an Client). Funktioniert ohne DBC-Patch im Client; DBC-Patching nur als Fallback für Loot/Quest/Vendor-Tooltips.
- **DB-Tabellen** (acore_characters): `character_paragon_role`, `character_paragon_item`, `character_paragon_spec`. (acore_world): `paragon_passive_spell_pool`, `paragon_spec_spell_assign`, **`spellitemenchantment_dbc`** (~11.323 Custom-Enchantments).
- **Enchantment-ID-Layout** siehe [`06-custom-ids.md`](./06-custom-ids.md).

## mod-loot-filter — regelbasiertes Auto-Sell/DE/Delete

- **Zweck**: Spieler definieren per AIO-UI Regeln, was mit gelooteten Items passieren soll.
- **8 Bedingungstypen**: Quality, Item Level, Sell Price, Item Class, Item Subclass, Cursed Status, Item ID, Name Contains.
- **3 Vergleichsoperatoren**: `=`, `>`, `<`.
- **4 Aktionen**: Keep (Whitelist) / Sell (Vendor) / Disenchant / Delete.
- **Prioritätssystem**: niedrigerer Wert = wird zuerst geprüft, erster Match gewinnt.
- **DB-Tabellen** (acore_characters): `character_loot_filter` (Regeln), `character_loot_filter_settings` (Master-Toggle + Stats).
- **Integration**: Hooks `OnPlayerLootItem` (intercept), erkennt Cursed Items via Slot-11-Enchantment-IDs (920001, 950001-950099). UI: `/lf` oder `/lootfilter`.

## mod-auto-loot — AOE-Loot

- **Zweck**: Schlichtes AOE-Looting im 10-yd-Radius beim `OnPlayerUpdate`-Tick.
- **Bedingung**: Spieler hat ≥4 freie Inventarslots, ist nicht in Gruppe, `AOELoot.Enable=true`.
- **Verhalten**:
  - Kreaturen-Loot: alle nahegelegenen Corpse-Loots werden konsumiert, Gold akkumuliert. Volle Inventare → optionaler Mail-Versand der Items.
  - Truhen (GAMEOBJECT_TYPE_CHEST): Wenn Spieler Lockpicking (Skill 186) hat, wird die Truhe per Spell 2575 geöffnet und gelootet.
- **Integration**: Ruft `sScriptMgr->OnPlayerLootItem()` auf — damit fangen mod-paragon-itemgen (Auto-Enchant) und mod-loot-filter (Filter) das Item ein.
- **Hat KEIN CLAUDE.md** — die Dokumentation steckt im Code (`src/mod_auto_loot.cpp`) und in dieser Übersicht.

## mod-endless-storage — unbegrenztes Material-Lager + Crafting

- **Zweck**: Spieler hinterlegen alle Crafting-Materialien (Stoff, Leder, Erz, Kräuter, Gems, Rezepte) in einem servergespeicherten "Endless Storage", abrufbar via AIO-UI (Slash `/es`).
- **Architektur**: reines Eluna/AIO-Modul — kein NPC, kein Gossip. Dazu C++ Hook-Modul (`mod_endless_storage_crafting.cpp`) für Crafting-Reagenz-Integration.
- **Tabs**: 15 Material-Kategorien (Subclasses) + 1 Rezepte-Tab (Class 9).
- **Crafting-Integration**: implementiert die in azerothcore-wotlk hinzugefügten `OnPlayerCheckReagent` / `OnPlayerConsumeReagent` Hooks. Inventar wird zuerst genutzt, Storage deckt den Rest — transparent fürs Crafting.
- **DB-Tabelle** (acore_characters): `custom_endless_storage` (character_id, item_entry, item_subclass, item_class, amount).
- **AIO-Spezifika**: Globale Handler-Tabelle (`MY_Handlers`-Pattern) wegen Re-Registrierungs-Beschränkung. Item-Info-Retry-Timer für ungecachte Items.
