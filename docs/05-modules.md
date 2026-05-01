# 05 — Module im Detail

Tiefere technische Übersicht jedes Custom-Moduls. Für eine Repo-Karte siehe [01-repos.md](./01-repos.md).

---

## mod-paragon

**Loader-Funktion**: `Addmod_paragonScripts()` in `src/Paragon_loader.cpp`.

### Kernmechanik

- **Account-weit**: Level + XP geteilt über alle Charaktere des Accounts.
- **Per-Character**: Stat-Verteilung (`unspent_points` + 17 Stat-Spalten).
- **XP-Quellen** (Tabelle):

| Encounter-Typ | XP |
|---------------|----|
| Regular Elite | 1 |
| Dungeon Elite | 1 |
| Heroic Dungeon Elite | 2 |
| Dungeon Boss | 3 |
| Heroic Dungeon Boss | 5 |
| Raid Boss | 10 |
| World Boss | 20 |
| Daily/Weekly Quest | 3 |

Group-Kills geben XP an alle Group-Members auf derselben Map.

- **Level-Formel**: `100 * 1.1^(level-1)` XP, zählt **herunter** zu 0.
- **5 Stat-Punkte pro Level-Up**, gespeichert als `unspent_points` in DB (kein Item).

### Zwei parallele Allokationspfade (auf gleicher DB-Tabelle)

1. **C++ Aura-System** (`ParagonPlayer.cpp`): bei Login/MapChange Stats aus DB lesen, als unsichtbare Stack-Auras anwenden. Cache: `std::unordered_map<uint32, ParagonCache>` mit Mutex.
2. **Lua AIO-UI** (`Paragon_System_LUA/`): Frame mit Tabs (Primary/Offensive/Defensive/Utility), +/- Buttons (Shift+Click = 10), Reset-Button.

### 17 Stats / Aura-IDs

| Stat | Aura-ID | DB-Spalte |
|------|---------|-----------|
| Level-Counter (Stack=Level) | 100000 | (über `character_paragon`) |
| Strength | 100001 | `pstrength` |
| Intellect | 100002 | `pintellect` |
| Agility | 100003 | `pagility` |
| Spirit | 100004 | `pspirit` |
| Stamina | 100005 | `pstamina` |
| Haste, ArmorPen, SpellPower, Crit, MountSpeed, ManaRegen, Hit, Block, Expertise, Parry, Dodge | 100016–100026 | `phaste`…`pdodge` |
| Life Leech | 100027 | `plifeleech` |

Alle Aura-IDs **konfigurierbar** via `mod_paragon.conf` (`Paragon.IdStr`, …). MaxStats[17] ebenfalls konfigurierbar (Default 255). 0 = unbegrenzt.

### Big+Small-Spell-Paare (Stat > 255)

Stack-Limit der Auras: 255. Workaround = zwei Spells pro Stat:
- "Big" (Wert ×100/Stack, IDs 100201–100227)
- "Small" (Wert ×1/Stack)

Allokation N: `big = N/100`, `small = N%100`. Beispiel: 666 Str = 6×Big(500) + 66×Small(5) = 3330. Levelaura selbst auf 255 gecapped (= 25.500 Levels).

### Life Leech — Pet-/Totem-Korrekt

Resolved via `Unit::GetCharmerOrOwnerPlayerOrPlayerItself()` — funktioniert für Pets/Totems/Charms (Demonology Felguard, Frost Mage Water Elemental, BM Hunter, Shaman Totems, DK Dancing Rune Weapon). Selbstschaden-Heal wird über Victim-Owner-Check ausgeschlossen.

### DB-Tabellen (acore_characters)

| Tabelle | Spalten |
|---------|---------|
| `character_paragon` | `accountID` PK, `level`, `xp` (counts down) |
| `character_paragon_points` | `characterID` PK, `unspent_points`, 17 Stat-Spalten |

### Bekanntes Issue

- SQL-Injection-Risiko in Lua-DB-Calls (`CharDBExecute` mit String-Concat — Eluna API hat keine Prepared Statements). Werte sollten validiert werden.

---

## mod-paragon-itemgen

**Loader-Funktion**: `Addmod_paragon_itemgenScripts()` in `src/MP_loader.cpp`.

### 5-Slot Enchantment-System

Items bekommen Bonus-Stat-Enchantments via `PROP_ENCHANTMENT_SLOT_0..4` (DB-Slots 7–11):

| Slot | Inhalt | Quelle |
|------|--------|--------|
| 7 | Stamina | immer |
| 8 | Main-Stat (Str/Agi/Int/Spi) | Spielerwahl |
| 9 | Combat-Rating 1 | Rollen-Pool |
| 10 | Combat-Rating 2 | Rollen-Pool, kein Duplikat von 9 |
| 11 | Passive-Spell / "Cursed"-Marker / leer | nur Cursed Items |

### Skalierung

`amount = ceil(paragonLevel × scalingFactor × qualityMultiplier)`, gecapped auf 666. Random-Roll pro Slot von 1 bis amount.

### Rollen-Pools

| Rolle | Pool |
|-------|------|
| Tank (0) | Dodge, Parry, Defense, Block, Hit, Expertise |
| DPS Melee (Str/Agi main) | Crit, Haste, Hit, ArmorPen, Expertise, AP |
| DPS Caster (Int/Spi main) | Crit, Haste, Hit, SpellPower, ManaRegen |
| Healer (2) | Crit, Haste, SpellPower, ManaRegen |

DPS-Pool wählt sich automatisch via `mainStat` (Str/Agi → Melee, Int/Spi → Caster).

### Cursed Items (1% Default)

- alle Stats × `conf_CursedMultiplier` (Default 1.5), gecapped auf 666
- Soulbound (`item->SetBinding(true)`)
- Shadow-Visual (`SendPlaySpellVisual(conf_CursedVisualKit)`, Default 5765)
- bei Spec → Passive-Spell aus `paragon_passive_spell_pool` (IDs 950001–950099) in Slot 11
- ohne Spec → "Cursed"-Marker (920001) in Slot 11
- Normale Items bekommen **keine** Passives.

### Tooltip-System (zweischichtig)

1. **AIO-Daten (Primärweg)**: Server liest Slots 7–11 vom Item, decodiert `(slot, enchantmentId)` → `statIndex = (id - 900000) / 1000`, `amount = (id - 900000) % 1000`. Sendet pro Item-Position via AIO an Client. Cache nach Bag/Slot. **Funktioniert ohne Client-DBC-Patch** für Inventar/Equipment.
2. **DBC-Text-Fallback**: Scant Tooltip auf "Paragon +", "Cursed", "Passive:" — nur greifbar bei vorgepatchter Client-`SpellItemEnchantment.dbc` (`patch_dbc.py`). Greift bei Loot/Quest/Vendor-Tooltips, wo Slot 7–11 nicht direkt am Item-Instance bekannt sind.

### Hooks

| PlayerScript-Hook | Trigger |
|-------------------|---------|
| `OnPlayerLootItem` | Mob/Chest-Loot |
| `OnPlayerCreateItem` | Crafting |
| `OnPlayerQuestRewardItem` | Quest-Reward |
| `OnPlayerAfterStoreOrEquipNewItem` | Vendor-Kauf |
| `OnPlayerCanSetTradeItem` | Trade-Restriction |
| `OnPlayerCanSendMail` | Mail-Restriction |

### Chat-Commands (`.paragon`)

- `.paragon role tank|dps|healer` (`PLAYER_FLAGS_RESTING` required)
- `.paragon stat str|agi|int|spi` (resting required)
- `.paragon info`

### DB-Tabellen

| Tabelle | DB | Zweck |
|---------|----|-------|
| `character_paragon_role` | characters | role + mainStat |
| `character_paragon_item` | characters | enchantment-Tracking pro itemGuid |
| `character_paragon_spec` | characters | Spec-Auswahl |
| `paragon_passive_spell_pool` | world | Pool von Passives (spellId, enchantmentId, name, category, minParagonLevel, minItemLevel) |
| `paragon_spec_spell_assign` | world | Spec→Spell-Gewichtung |
| `spellitemenchantment_dbc` | world | DBC-Override für ~11.323 Custom-Enchantments |

### Auction-House-Restriktion

Blockiert: `OnAuctionAdd` ist void, `CanCreateAuction` existiert nicht. Cursed Items sind ohnehin Soulbound. Nicht-Cursed Paragon-Items sind theoretisch handelbar.

---

## mod-loot-filter

**Loader-Funktion**: `Addmod_loot_filterScripts()` in `src/mod_loot_filter_loader.cpp`.

Per-Character-Filter-Regeln, evaluiert beim `OnPlayerLootItem`-Hook (in-memory cache).

### Conditions, Operators, Actions

| Condition | ID | Op verfügbar |
|-----------|----|--------------|
| Quality | 0 | =, >, < |
| ItemLevel | 1 | =, >, < |
| SellPrice | 2 | =, >, < |
| ItemClass | 3 | =, >, < |
| ItemSubclass | 4 | =, >, < |
| IsCursed | 5 | bool |
| ItemId | 6 | =, >, < |
| NameContains | 7 | substring |

Actions: Keep(0) / Sell(1) / Disenchant(2) / Delete(3). Priority: niedrigster Wert zuerst, erste Match gewinnt.

### Cursed-Detection

Über Slot-11-Enchantment-IDs:
- `920001` = "Cursed"-Marker
- `950001-950099` = Passive-Spell-Enchant

### DB-Tabellen

| Tabelle | Zweck |
|---------|-------|
| `character_loot_filter` | Regeln (characterId, ruleId, conditionType, conditionOp, conditionValue, conditionStr, action, priority, enabled) |
| `character_loot_filter_settings` | Master-Toggle + Statistiken (totalSold, totalDisenchanted, totalDeleted) |

### Commands

`.lootfilter reload | toggle | stats`. UI: `/lf` oder `/lootfilter`.

### Konfig-Optionen

`LootFilter.Enable`, `AllowSell`, `AllowDisenchant`, `AllowDelete`, `LogActions`, `MaxRulesPerChar=30`.

---

## mod-auto-loot

**Loader-Funktion**: `AddSC_AutoLoot()` in `src/mod_auto_loot_loader.cpp`. **Kein CLAUDE.md vorhanden** — gesamte Doku in dieser Section + `src/mod_auto_loot.cpp`.

### Verhalten

Im `OnPlayerUpdate`-Tick (jeder Frame):
- nur wenn `AOELoot.Enable=true`, Spieler nicht in Gruppe, ≥4 freie Inventarslots
- iteriert alle toten Creatures im 10-yd-Radius (`GetDeadCreatureListInGrid`)
- für jedes Loot-Item:
  - **stackable Items** (`MaxCount != 1`): in Inventar, ggf. via Mail nachsenden (`AOELoot.MailEnable`)
  - **unique Items** (`MaxCount == 1`): nur looten, wenn Spieler das Item noch NICHT hat
- aggregiert Gold, sendet `SMSG_LOOT_MONEY_NOTIFY`, updated Achievement
- ruft **`sScriptMgr->OnPlayerLootItem()`** für jedes Item auf — Hook-Kette: mod-paragon-itemgen (Auto-Enchant) und mod-loot-filter (Filter) greifen.

### Truhen

Wenn Spieler `Lockpicking` (Skill 186) hat: nahegelegene `GAMEOBJECT_TYPE_CHEST` werden via Spell `2575` "geöffnet" und gelootet. Truhe wird despawned nach erfolgreichem Looten.

### Konfig

`AOELoot.Enable=true`, `AOELoot.MailEnable=true`, plus String-IDs:
- `AOE_ACORE_STRING_MESSAGE = 50000` (Login-Welcome)
- `AOE_ITEM_IN_THE_MAIL = 50001`

---

## mod-endless-storage

**Loader-Funktionen**: 
- C++: `Addmod_endless_storageScripts()` in `src/mod_endless_storage_loader.cpp` (Crafting-Hooks)
- Lua: `lua_scripts/endless_storage_server.lua` + `endless_storage_client.lua` (UI)

### UI / Tabs

15 Material-Kategorien (`ITEM_SUBCLASS_*` der TradeGoods + Gems) + Rezepte-Tab (`ITEM_CLASS_RECIPE`). Slash `/es` oder `/storage`.

### Akzeptierte Item-Klassen

| Klasse | Bedingung | Tab |
|--------|-----------|-----|
| `ITEM_CLASS_TRADE_GOODS` (7) | `MaxStackSize > 1` | nach Subclass |
| `ITEM_CLASS_GEM` (3) | `MaxStackSize > 1` | Jewelcrafting |
| `ITEM_CLASS_RECIPE` (9) | alle | Rezepte |

### DB-Tabelle (acore_characters)

`custom_endless_storage`: `character_id`, `item_entry`, `item_subclass`, `item_class`, `amount` (PK = `character_id, item_entry`).

### Server-Handler

| Handler | Funktion |
|---------|----------|
| `ES.RequestData(player, catIndex)` | Kategorie laden, `UpdateItems` an Client |
| `ES.Withdraw(player, itemEntry, catIndex)` | 1 Stack entnehmen → `AddItem` → Refresh |
| `ES.Deposit(player, catIndex)` | Inventar-Slots 23–38 + Bags 19–22 scannen, in DB schreiben |

Item-Template-Cache (`itemInfoCache`) reduziert Worlddb-Queries.

### Crafting-Integration

Die in azerothcore-wotlk hinzugefügten Hooks `OnPlayerCheckReagent` und `OnPlayerConsumeReagent` werden in `mod_endless_storage_crafting.cpp` implementiert:
- `Spell::CheckItems()` fragt zusätzlich `custom_endless_storage` ab, wenn Inventar-Reagenzien fehlen
- `Spell::TakeReagents()` konsumiert aus Storage, **bevor** `DestroyItemCount` greift
- Player merkt nichts — Crafting "sieht" alle Materialien automatisch.
