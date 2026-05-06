# scripting — Catalog of `*Script` hook classes

> Inventory of every `ScriptObject` subclass shipped by AzerothCore, grouped by lifecycle. Each row points at its declaration file (with line) and the corresponding `XHook` enum so dispatch sites and override authors can find each other in one read. The high-level table in [`../../02-architecture.md#hook-system-scriptmgr`](../../02-architecture.md) shows only the most common rows; this file is the full reference. All files below live under `src/server/game/Scripting/`.

## Critical files

| File | Role |
|---|---|
| `ScriptDefines/AllScriptsObjects.h:21` | aggregate `#include` — pulls every hook class into `ScriptMgr.h` |
| `ScriptObject.h:42` | base class `ScriptObject` (ctor: `name`, `totalAvailableHooks`) |
| `ScriptObject.h:69` | template `UpdatableScript<TObject>` (per-frame `OnUpdate`) |
| `ScriptObject.h:79` | template `MapScript<TMap>` (specialized for `Map`/`InstanceMap`/`BattlegroundMap`) |
| `ScriptMgrMacros.h:23` | `IsValidBoolScript<>`, `GetReturnAIScript<>`, `ExecuteScript<>` foreach helpers |

## Key concepts

- **Naming** — `XScript` is the C++ class authors derive from; `XHOOK_*` is the per-hook enum used by `CALL_ENABLED_HOOKS`; `XHOOK_END` sentinel sizes `EnabledHooks` (see `ScriptMgr.cpp:80`).
- **`IsDatabaseBound()`** — when `true`, the script binds to a name from a DB column (`creature_template.ScriptName`, `instance_template.script`, `spell_script_names.ScriptName`, …). Such scripts go through `ScriptRegistry<T>::AddALScripts()` after `World DB` is loaded; everything else is registered from its constructor.
- **`AllXScript` ("global" variants)** — `AllCreatureScript`, `AllGameObjectScript`, `AllItemScript`, `AllMapScript`, `AllSpellScript`, `AllBattlegroundScript` — fire on **every** entity of that type, not just one identified by a DB script name.
- **Compatibility aliases** — `using SpellSC = AllSpellScript;` (`AllSpellScript.h:109`), `using BGScript = AllBattlegroundScript;` (`AllBattlegroundScript.h:172`), `using CommandSC = AllCommandScript;`. Old code may use either name.

## Hook class inventory

### Server / world / database lifecycle (no DB binding, code-only)

| Class | Hook enum | File:line | Typical hooks |
|---|---|---|---|
| `WorldScript` | `WorldHook` | `WorldScript.h:43` | `OnAfterConfigLoad`, `OnStartup/Shutdown`, `OnUpdate`, `OnBeforeWorldInitialized`, `OnBeforeFinalizePlayerWorldSession`, `OnAfterUnloadAllMaps` |
| `ServerScript` | `ServerHook` | `ServerScript.h:36` | `OnNetworkStart/Stop`, `OnSocketOpen/Close`, `CanPacketSend/Receive` |
| `DatabaseScript` | `DatabaseHook` | `DatabaseScript.h:31` | `OnAfterDatabasesLoaded`, `OnAfterDatabaseLoadCreatureTemplates` |
| `FormulaScript` | `FormulaHook` | `FormulaScript.h:40` | `OnHonorCalculation`, `OnGainCalculation`, `OnGroupRateCalculation`, `OnAfterArenaRatingCalculation` |
| `AccountScript` | `AccountHook` | `AccountScript.h:38` | `OnAccountLogin`, `OnLastIpUpdate`, `OnPasswordChange`, `CanAccountCreateCharacter` |
| `MovementHandlerScript` | `MovementHook` | `MovementHandlerScript.h:31` | `OnPlayerMove(Player*, MovementInfo, opcode)` |
| `MiscScript` | `MiscHook` | `MiscScript.h:48` | object/player/group construct/destruct, `OnItemCreate`, `CanSendAuctionHello`, `ValidateSpellAtCastSpell` |
| `GlobalScript` | `GlobalHook` | `GlobalScript.h:54` | loot post-processing (`OnAfterRefCount`, `OnItemRoll`), `OnAfterUpdateEncounterState`, `OnLoadSpellCustomAttr`, `OnInstanceIdRemoved` |
| `ConditionScript` | — (DB-bound) | `ConditionScript.h:23` | `OnConditionCheck` (`Condition.ScriptName`) |
| `ModuleScript` | — | `ModuleScript.h` | placeholder for module-only types |

### Player

| Class | Hook enum | File:line | Notes |
|---|---|---|---|
| `PlayerScript` | `PlayerHook` (~210 entries, `..._JUST_DIED..PLAYERHOOK_END`) | `PlayerScript.h:217` | Largest hook class. Enum at lines 30-214; methods at 217-832. Dispatchers in `PlayerScript.cpp` (944 lines). |

Frequently used `PlayerScript` overrides (samples, all in `PlayerScript.h`): `OnPlayerLogin` (:323), `OnPlayerLogout` (:329), `OnPlayerLevelChanged` (:257), `OnPlayerMapChanged` (:353), `OnPlayerLootItem` (:419), plus `OnPlayerCreateItem`, `OnPlayerQuestRewardItem`, `OnPlayerAfterStoreOrEquipNewItem`, `OnPlayerCanSendMail`, `OnPlayerCanSetTradeItem`, `OnPlayerCanSendErrorAlreadyLooted`, `OnPlayerEnterCombat`, `OnPlayerLeaveCombat`. The fork has no additional `PlayerScript` hooks beyond upstream — see [`07-custom-hooks.md`](./07-custom-hooks.md).

### Combat / units / spells

| Class | Hook enum | File:line | Notes |
|---|---|---|---|
| `UnitScript` | `UnitHook` | `UnitScript.h:53` | `OnDamage/Heal`, `ModifyMeleeDamage`, `ModifySpellDamageTaken`, `ModifyHealReceived`, `OnAuraApply/Remove`, `OnUnitEnterCombat/Death`, `OnDisplayIdChange`, `OnUnitSetShapeshiftForm` |
| `SpellScriptLoader` | — (DB-bound) | `SpellScriptLoader.h:25` | factory `GetSpellScript()` / `GetAuraScript()`; macros `RegisterSpellScript(...)`, `RegisterSpellAndAuraScriptPair(...)` (lines 87-90). User view: [`../../03-spell-system.md`](../../03-spell-system.md). |
| `AllSpellScript` (alias `SpellSC`) | `AllSpellHook` | `AllSpellScript.h:46` | `OnSpellCast/Prepare`, `OnSpellCheckCast`, `OnDummyEffect` (3 overloads), `OnCalcMaxDuration`, scaling hooks |

### Creatures, GameObjects, Items, Pets, Vehicles

| Class | DB binding | File:line | Notes |
|---|---|---|---|
| `CreatureScript` | `creature_template.ScriptName` | `CreatureScript.h:24` | gossip + `GetAI(Creature*)`. Macros `RegisterCreatureAI(ai)` (:71), `RegisterCreatureAIWithFactory(ai, fn)` (:81). |
| `AllCreatureScript` | none (fires per creature) | `AllCreatureScript.h:23` | `OnAllCreatureUpdate`, `OnBeforeCreatureSelectLevel`, `OnCreatureAddWorld/RemoveWorld`, `OnCreatureSaveToDB`, `CanCreatureGossip*` |
| `GameObjectScript` | `gameobject_template.ScriptName` | `GameObjectScript.h:24` | gossip + `OnDestroyed/Damaged/LootStateChanged`, `GetAI(GameObject*)`. Macros `RegisterGameObjectAI(...)`, `RegisterGameObjectAIWithFactory(...)`. |
| `AllGameObjectScript` | none | `AllGameObjectScript.h` | global GO update / gossip hooks |
| `ItemScript` | `item_template.ScriptName` | `ItemScript.h:23` | `OnUse`, `OnQuestAccept`, `OnExpire`, `OnRemove`, `OnCastItemCombatSpell`, gossip |
| `AllItemScript` | none | `AllItemScript.h` | item-wide hooks (every item) |
| `PetScript` | none | `PetScript.h:35` | `OnInitStatsForLevel`, `CanUnlearnSpellSet/Default`, `OnPetAddToWorld` |
| `VehicleScript` | yes | `VehicleScript.h` | `OnInstall`, `OnReset`, `OnAddPassenger` |
| `DynamicObjectScript` | yes | `DynamicObjectScript.h` | `OnDynamicObjectUpdate` |
| `TransportScript` | yes | `TransportScript.h` | passenger add/remove, relocate |
| `AreaTriggerScript` | `areatrigger_scripts.ScriptName` | `AreaTriggerScript.h` | `OnTrigger` |

### Maps / instances / battlegrounds / arenas / outdoor PvP

| Class | DB binding | File:line | Notes |
|---|---|---|---|
| `WorldMapScript` | continent mapId | `WorldMapScript.h:23` | derives `MapScript<Map>`; `isAfterLoadScript() == true` |
| `InstanceMapScript` | `instance_template.script` | `InstanceMapScript.h:23` | `GetInstanceScript(InstanceMap*)` factory; macro `RegisterInstanceScript(name, mapId)` (:45). Detail: [`04-instance-scripts.md`](./04-instance-scripts.md). |
| `BattlegroundMapScript` | BG mapId | `BattlegroundMapScript.h:23` | derives `MapScript<BattlegroundMap>` |
| `AllMapScript` | none | `AllMapScript.h:36` | `OnPlayerEnterAll/LeaveAll`, `OnBeforeCreateInstanceScript`, `OnDestroyInstance`, `OnCreateMap/DestroyMap/MapUpdate` |
| `BattlegroundScript` | BG type id | `BattlegroundScript.h` | factory `CreateBattleground(BattlegroundTypeId)` |
| `AllBattlegroundScript` (alias `BGScript`) | none | `AllBattlegroundScript.h:56` | full BG/queue lifecycle (`OnBattlegroundStart/Update/End`, `OnQueueUpdate`, MMR hooks) |
| `BattlefieldScript` | yes (Wintergrasp etc.) | `BattlefieldScript.h` | factory + lifecycle |
| `ArenaScript` | none | `ArenaScript.h` | arena-rating tweaks |
| `ArenaTeamScript` | none | `ArenaTeamScript.h:35` | `OnGetSlotByType`, `OnGetArenaPoints`, `OnTypeIDToQueueID` |
| `OutdoorPvPScript` | yes | `OutdoorPvPScript.h` | factory `CreateOutdoorPvP` |

### Social / commerce / chat

| Class | Hook enum | File:line | Notes |
|---|---|---|---|
| `GroupScript` | `GroupHook` | `GroupScript.h:39` | `OnAddMember`, `OnInviteMember`, `OnChangeLeader`, `OnDisband`, `CanGroupJoinBattlegroundQueue` |
| `GuildScript` | `GuildHook` | `GuildScript.h:42` | guild lifecycle, bank events, MOTD |
| `MailScript` | `MailHook` | `MailScript.h:30` | `OnBeforeMailDraftSendMailTo` |
| `AuctionHouseScript` | `AuctionHouseHook` | `AuctionHouseScript.h:40` | add/remove/expire/successful + 6 mail-pre hooks |
| `WeatherScript` | yes (zone) | `WeatherScript.h` | `OnChange`, `OnUpdate` |
| `CommandScript` | — | `CommandScript.h:24` | abstract `GetCommands() → ChatCommandTable` (used by `.foo` GM commands) |
| `AllCommandScript` (alias `CommandSC`) | — | `AllCommandScript.h` | global pre/post-command hooks |
| `TicketScript` | `TicketHook` | `TicketScript.h` | GM ticket lifecycle |

### Achievements / loot

| Class | Hook enum | File:line | Notes |
|---|---|---|---|
| `AchievementScript` | `AchievementHook` | `AchievementScript.h:36` | `IsCompletedCriteria`, `IsRealmCompleted`, `OnBeforeCheckCriteria`, `CanCheckCriteria` |
| `AchievementCriteriaScript` | `criteria_data.ScriptName` | `AchievementCriteriaScript.h` | `OnCheck` |
| `LootScript` | `LootHook` | `LootScript.h` | `OnLootMoney` |

### Other

| Class | File:line | Notes |
|---|---|---|
| `WorldObjectScript` | `WorldObjectScript.h` | object lifecycle on map; `OnWorldObjectCreate/Destroy/SetMap/ResetMap/Update` |
| `GameEventScript` | `GameEventScript.h` | game-event start/stop |
| `ALEScript` | `ALEScript.h` | optional `mod-ale` (Eluna-like) integration; not a stock module |

## Flow / data shape — example dispatch

Enum-driven, void-returning hook (typical `PlayerScript`, `PlayerScript.cpp:97`):

```cpp
void ScriptMgr::OnPlayerLevelChanged(Player* p, uint8 oldLevel)
{
    CALL_ENABLED_HOOKS(PlayerScript, PLAYERHOOK_ON_LEVEL_CHANGED,
        script->OnPlayerLevelChanged(p, oldLevel));
}
```

DB-bound, single-script lookup (`CreatureScript::OnGossipHello`, `CreatureScript.cpp:24`):

```cpp
auto tempScript = ScriptRegistry<CreatureScript>::GetScriptById(creature->GetScriptId());
return tempScript ? tempScript->OnGossipHello(player, creature) : false;
// (preceded by an AllCreatureScript fan-out via IsValidBoolScript<>)
```

Boolean hooks use `CALL_ENABLED_BOOLEAN_HOOKS` (default `true`) or `..._WITH_DEFAULT_FALSE`; see `ScriptMgrMacros.h:76-86`.

## Hooks & extension points

- **Authoring a new hook**: add to the relevant `XScript.h` (virtual + new `XHOOK_*` enum entry before `XHOOK_END`), declare on `ScriptMgr.h`, define in `XScript.cpp` with `CALL_ENABLED_HOOKS`, and call `sScriptMgr->OnX(...)` from the engine site. Reference: `wiki/hooks-script`.
- **Choosing between `XScript` and `AllXScript`**: pick `AllX` when you need a fan-out across every entity (modules); pick `X` when you bind by DB script name to one specific entry.

## Cross-references

- Engine-side: [`01-script-mgr.md`](./01-script-mgr.md), [`03-script-objects.md`](./03-script-objects.md), [`04-instance-scripts.md`](./04-instance-scripts.md), [`07-custom-hooks.md`](./07-custom-hooks.md), [`../handlers/00-index.md`](../handlers/00-index.md), [`../spells/00-index.md`](../spells/00-index.md)
- Project-side: [`../../02-architecture.md#hook-system-scriptmgr`](../../02-architecture.md), [`../../03-spell-system.md`](../../03-spell-system.md), [`../../05-modules.md`](../../05-modules.md)
- Fork-specific: `azerothcore-wotlk/functions.md` (excerpt table), `azerothcore-wotlk/CLAUDE.md`
- External: `wiki/hooks-script`, Doxygen for `classScriptMgr` and each `class<Name>Script`
