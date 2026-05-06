# entities — ObjectMgr

> The world-DB cache singleton. Loads ~95 tables synchronously at server startup, owns all entity templates / spawn rows / locale strings, and hands out global GUID generators. Cross-links: [`05-creature.md`](./05-creature.md), [`06-gameobject.md`](./06-gameobject.md), [`07-item.md`](./07-item.md), [`../database/03-async-vs-sync.md`](../database/03-async-vs-sync.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Globals/ObjectMgr.h:726` | `class ObjectMgr` (singleton; `ObjectMgr::instance()` at `:735`) |
| `src/server/game/Globals/ObjectMgr.h:761-845` | Template getters (`GetGameObjectTemplate`, `GetCreatureTemplate`, `GetItemTemplate`, `GetQuestTemplate`, …) |
| `src/server/game/Globals/ObjectMgr.h:1133-1138` | `GetGenerator<HighGuid>()` — returns the per-type sequence generator |
| `src/server/game/Globals/ObjectMgr.h:1140-1146` | `GenerateAuctionID / GenerateMailID / GeneratePetNumber / GenerateCreatureSpawnId / GenerateGameObjectSpawnId` |
| `src/server/game/Globals/ObjectMgr.h:506-512` | Container typedefs (`LinkedRespawnContainer`, `CreatureDataContainer`, `GameObjectDataContainer`, …) |
| `src/server/game/Globals/ObjectMgr.cpp` (~11000 lines) | Loader implementations |
| `src/server/game/World/World.cpp:300` | `World::SetInitialWorldSettings()` — drives every loader at startup |

## Key concepts

- **Synchronous startup loaders.** Every `ObjectMgr::Load*` is called from `World::SetInitialWorldSettings()` (`World.cpp:300`). They issue `WorldDatabase.Query(...)` blocking calls — no holders, no async (see [`../database/03-async-vs-sync.md`](../database/03-async-vs-sync.md)). The world tick does NOT start until all loaders finish.
- **Container shape.** Most loaders fill an `std::unordered_map<id, Struct>` (e.g. `_creatureTemplateStore`, `_gameObjectTemplateStore`, `_itemTemplateStore`). Some keep an additional flat vector for fast iteration (e.g. `_itemTemplateStoreFast` at `ObjectMgr.h:784`, `_questTemplatesFast` at `ObjectMgr.h:839` — used by `GetQuestTemplate`).
- **Single-row reload.** `LoadCreatureTemplate(Field*, bool triggerHook)` (`:584`) and `LoadGameObjectTemplate*` (`AddGameobjectInfo` at `ObjectMgr.h:768`) are the entry points used by `.reload creature_template` / `.reload gameobject_template` GM commands and by module init code that wants to add a custom row at runtime.
- **Order matters.** Many loaders carry a "must be after X" comment; `World.cpp` enforces the order. Examples: `LoadCreatures` requires `LoadCreatureTemplates`; `LoadCreatureAddons` needs both; `LoadLinkedRespawn` needs both spawn tables; `LoadVehicleTemplateAccessories` needs `LoadCreatureTemplates` and `LoadNPCSpellClickSpells`. Reordering breaks startup.
- **Global GUID generators**, one per `Global` `HighGuid`. After all spawns are loaded, `World::SetInitialWorldSettings` calls `sObjectMgr->SetHighestGuids()` (`ObjectMgr.h:1131`) to seed every generator past the highest in-use counter. Overflow in any generator triggers `HandleCounterOverflow` → fatal shutdown (`ObjectGuid.cpp:93`).
- **Validation on load.** Each `Load*` runs sanity checks (`CheckCreatureTemplate` at `:1037`, `CheckCreatureMovement` at `:1038`); invalid rows are logged with `LOG_ERROR("sql.sql", ...)` and dropped from the cache. The world starts even with bad rows; the warnings show in `Server.log`.
- **Locale tables** are loaded separately and merged into the same struct (`Name` field becomes localised at access time via `GetNameForLocaleIdx`).

## Loader matrix (call order in `World::SetInitialWorldSettings`)

Grouped by phase; line numbers point to `ObjectMgr.cpp` unless prefixed. Locale tables (`creature_locale`, `gameobject_locale`, `item_locale`, …) are loaded individually but always merged into the parent template's localised string slot — they are bundled below.

### Phase 1 — strings & locales (`World.cpp:352-466`)

`LoadAcoreStrings` (`acore_string`), `LoadModuleStrings` + `…Locale`, `LoadBroadcastTexts` (`:6614`) + `…Locales` (`:6690`), and 12 `Load*Locales` for creature / gameobject / item / itemset / quest / quest-offer-reward / quest-request-items / npctext / pagetext / gossipmenuitems / pointofinterest / petname.

### Phase 2 — texts & gameobject templates (`World.cpp:473-510`)

| Loader | Table | Container |
|---|---|---|
| `LoadPageTexts` (`:6387`) | `page_text` | `_pageTextStore` |
| `LoadGameObjectTemplate` (`:7804`) | `gameobject_template` | `_gameObjectTemplateStore` |
| `LoadGameObjectTemplateAddons` (`:7993`) | `gameobject_template_addon` | `_gameObjectTemplateAddonStore` |
| `LoadGossipText` (`:6614`) | `npc_text` | `_npcTextStore` |

### Phase 3 — items (`World.cpp:521-525`)

`LoadItemTemplates` (`:3234`) → `_itemTemplateStore` + `_itemTemplateStoreFast`; `LoadItemSetNames` (`:3884`) → `_itemSetNameStore`.

### Phase 4 — creature templates & spawns (`World.cpp:527-578`)

| Loader | Table | Container / notes |
|---|---|---|
| `LoadCreatureModelInfo` (`:1709`) | `creature_model_info` | `_creatureModelStore` |
| `LoadCreatureCustomIDs` (`:951`) | (custom remap) | rewrites template entries |
| `LoadCreatureTemplates` (`:522`) | `creature_template` | `_creatureTemplateStore` |
| `LoadEquipmentTemplates` (`:1479`) | `creature_equip_template` | `_equipmentInfoStore` |
| `LoadCreatureTemplateAddons` (`:855`) | `creature_template_addon` | `_creatureTemplateAddonStore` |
| `LoadCreatureTemplateModels / …Resistances / …Spells` (`:711, :763, :809`) | `creature_template_*` | filled back into template |
| `LoadReputationRewardRate / …OnKill / …SpilloverTemplate` (`:8196, :8284, :8358`) | `reputation_*` | three rep stores |
| `LoadPointsOfInterest` (`:8475`) | `points_of_interest` | `_pointsOfInterestStore` |
| `LoadCreatureClassLevelStats` | `creature_classlevelstats` | `_creatureBaseStatsStore` |
| `LoadCreatures` (`:2316`) | `creature` (per-spawn) | `_creatureDataStore` |
| `LoadCreatureSparring` (`:2674`) | `creature_sparring` | `_creatureSparringStore` |
| `LoadTempSummons` (`:2149`), `LoadGameObjectSummons` (`:2235`) | `*_summon_groups` | summon-group stores |
| `LoadCreatureAddons` (`:1261`) | `creature_addon` | `_creatureAddonStore` |
| `LoadCreatureMovementOverrides` (`:1557`) | `creature_movement_override` | `_creatureMovementOverrides` |

### Phase 5 — gameobject spawns + quest items + linked respawn (`World.cpp:581-593`)

`LoadGameobjects` (`:2845`) → `_gameObjectDataStore`; `LoadGameObjectAddons` (`:1362`); `LoadGameObjectQuestItems` / `LoadCreatureQuestItems`; `LoadLinkedRespawn` (`:1917`) → `_linkedRespawnStore`.

### Phase 6 — quests + scripts (`World.cpp:599-616`, `:846-873`)

| Loader | Table | Container |
|---|---|---|
| `LoadQuests` (`:4998`) | `quest_template` | `_questTemplates` + `_questTemplatesFast` |
| `LoadQuestPOI` (`:8523`) | `quest_poi*` | `_questPOIStore` |
| `LoadQuestStartersAndEnders` → `LoadGameobject…` / `LoadCreature…` Quest Starters/Enders (`:8751, :8765, :8779, :8793`) | `*_questrelation`, `*_involvedrelation` | 4 quest-relation maps |
| `LoadQuestGreetings` + `…Locales` (`:6924, :6978`) | `quest_greeting*` | `_questGreetingStore` |
| `LoadQuestMoneyRewards` | `quest_money_reward` | `_questMoneyRewards` |
| `LoadSpellScripts / EventScripts / WaypointScripts` (`:6158, :6186, :6230`) | `*_scripts` | `ScriptMapMap` (`sSpellScripts`, …) |
| `LoadSpellScriptNames` (`:6257`) | `spell_script_names` | `_spellScriptsStore` |
| `ValidateSpellScripts`, `InitializeSpellInfoPrecomputedData` | (in-memory) | sanity + post-fill |

### Phase 7 — area triggers + access requirements (`World.cpp:625-668`)

`LoadNPCSpellClickSpells` (`:8606`); vehicle trio `LoadVehicleTemplateAccessories / Vehicle Accessories / VehicleSeatAddon` (`:3968, :4024, :4068`); area-trigger quartet `LoadAreaTriggers / …Teleports / Quest…Triggers / …Scripts` (`:7285, :7335, :6848, :7138`); `LoadAccessRequirements` (`:7396`); `LoadTavernAreaTriggers` (`:7097`); `LoadInstanceEncounters` (`:6521`); `LoadInstanceTemplate` (`:6470`).

### Phase 8 — player, npc lists, factions (`World.cpp:683-813`)

`LoadPlayerInfo` (`:4263`) → `_playerInfo[race][class]`; `LoadExplorationBaseXP` (`:8072`); pet trio `LoadPetNames / Number / LevelInfo` (`:8112, :8144, :4124`); `LoadMailLevelRewards`; `LoadFishingBaseSkillLevel` (`:9407`); `LoadReservedPlayerNames` DB+DBC (`:8807, :8845`); `LoadProfanityNames` DB+DBC (`:8910, :8948`); `LoadGameObjectForQuests` (`:9193`); `LoadGameTele` (`:9547`); `LoadTrainers / CreatureDefaultTrainers`; `LoadGossipMenu / GossipMenuItems`; `LoadVendors`; five `LoadFactionChange*` loaders for race/faction-change remap tables.

### Phase 9 — runtime housekeeping

- `ReturnOrDeleteOldMails(serverUp=false)` — deletes expired mail at startup; called again per-day from the world tick.
- `SetHighestGuids()` — must run after every `Load*` so generators don't reuse a live id.

## Flow / data shape

### Lookup pattern (per-tick hot path)

```cpp
// Templates: O(1) hash lookup
CreatureTemplate const* tmpl = sObjectMgr->GetCreatureTemplate(entry);  // ObjectMgr.h:770
if (!tmpl) return nullptr;

// Spawn rows: O(1) hash lookup by spawn id (from creature.guid column)
CreatureData const* data = sObjectMgr->GetCreatureData(spawnId);        // ObjectMgr.h:1232

// Items: O(1) flat-array lookup (uses _itemTemplateStoreFast)
ItemTemplate const* iproto = sObjectMgr->GetItemTemplate(itemId);       // ObjectMgr.h:782

// Quests: O(1) flat-array lookup with bounds check
Quest const* q = sObjectMgr->GetQuestTemplate(questId);                 // ObjectMgr.h:837
```

### GUID generation

```cpp
// Persistent global ids
uint32 newAuctionId = sObjectMgr->GenerateAuctionID();        // ObjectMgr.h:1140
uint32 newMailId    = sObjectMgr->GenerateMailID();           // :1142
uint32 newPetNum    = sObjectMgr->GeneratePetNumber();        // :1143

// Per-spawn ids (DB primary keys for creature/gameobject)
ObjectGuid::LowType spawnId = sObjectMgr->GenerateCreatureSpawnId();   // :1144
spawnId = sObjectMgr->GenerateGameObjectSpawnId();                     // :1145

// Generic global GUID (compile-time HighGuid check)
auto& gen = sObjectMgr->GetGenerator<HighGuid::Item>();        // :1133
ObjectGuid::LowType lowGuid = gen.Generate();
```

## Hooks & extension points

- Module rows: a module can register its own creature/gameobject/item templates by inserting into the world DB and calling `sObjectMgr->LoadCreatureTemplate(field, true)` / `AddGameobjectInfo(...)` from its `OnAfterConfigLoad` (or post-startup) hook. The `triggerHook` flag fires `ScriptMgr::OnAfterDatabaseLoadCreatureTemplates` so other modules can patch.
- Re-loading a row at runtime: GM commands `.reload creature_template`, `.reload gameobject_template`, `.reload quest_template` invoke the same loaders.
- Custom IDs: see [`../../06-custom-ids.md`](../../06-custom-ids.md) for the project's reserved entry ranges. `LoadCreatureCustomIDs` (`:951`) is the renumbering hook that this fork uses.

## Cross-references

- Engine-side: [`05-creature.md`](./05-creature.md), [`06-gameobject.md`](./06-gameobject.md), [`07-item.md`](./07-item.md), [`02-object-guid.md`](./02-object-guid.md) (generator counters), [`../database/03-async-vs-sync.md`](../database/03-async-vs-sync.md) (loaders are sync), [`../scripting/01-script-mgr.md`](../scripting/01-script-mgr.md) (`ScriptName` strings resolve via `_scriptNamesStore` → `GetScriptId`)
- Project-side: [`../../09-db-tables.md`](../../09-db-tables.md) (full table inventory), [`../../06-custom-ids.md`](../../06-custom-ids.md) (custom ID ranges)
- External: Doxygen `classObjectMgr`, wiki "Database structure"
