# core/03 — File locator (reverse lookup)

> "I am looking at file `X` in `azerothcore-wotlk/src/…` — which doc covers it?"
> Alphabetical by file name. Multi-file subsystems point to the subfolder index.

Path prefix `src/server/game/` is abbreviated to `…/game/` and `src/server/shared/` to `…/shared/`.

| File / pattern | Doc |
|---|---|
| `…/game/AI/CoreAI/*.h/.cpp` | [`ai/01-ai-base.md`](./ai/01-ai-base.md) |
| `…/game/AI/ScriptedAI/ScriptedCreature.h/.cpp` | [`ai/02-scripted-ai.md`](./ai/02-scripted-ai.md) |
| `…/game/AI/SmartScripts/SmartAI.{h,cpp}`, `SmartScript*.{h,cpp}` | [`ai/03-smart-ai.md`](./ai/03-smart-ai.md) |
| `…/game/AuctionHouse/*` | [`social/04-auction-house.md`](./social/04-auction-house.md) |
| `…/game/Battlefield/*` | [`battlegrounds/04-battlefield.md`](./battlegrounds/04-battlefield.md) |
| `…/game/Battlegrounds/Arena*` | [`battlegrounds/03-arena.md`](./battlegrounds/03-arena.md) |
| `…/game/Battlegrounds/Battleground.{h,cpp}` | [`battlegrounds/00-index.md`](./battlegrounds/00-index.md) |
| `…/game/Battlegrounds/BattlegroundMgr.{h,cpp}` | [`battlegrounds/01-bg-mgr.md`](./battlegrounds/01-bg-mgr.md) |
| `…/game/Battlegrounds/Zones/*` | [`battlegrounds/02-bg-types.md`](./battlegrounds/02-bg-types.md) |
| `…/game/Calendar/*` | [`world/06-calendar.md`](./world/06-calendar.md) |
| `…/game/Chat/Channels/*` | [`social/05-channels.md`](./social/05-channels.md) |
| `…/game/Combat/*` | [`combat/00-index.md`](./combat/00-index.md) |
| `…/shared/Configuration/*` (and `…/common/Configuration/Config.{h,cpp}`) | [`world/02-config-mgr.md`](./world/02-config-mgr.md) |
| `…/game/Conditions/*` | [`loot/03-loot-conditions.md`](./loot/03-loot-conditions.md) (cross-cuts loot/quests/spells) |
| `…/game/DungeonFinding/LFGMgr.{h,cpp}` | [`instances/04-dungeon-finder.md`](./instances/04-dungeon-finder.md) |
| `…/game/Entities/Corpse/*` | [`entities/09-corpse-transport.md`](./entities/09-corpse-transport.md) |
| `…/game/Entities/Creature/*` | [`entities/05-creature.md`](./entities/05-creature.md) |
| `…/game/Entities/DynamicObject/*` | [`entities/08-pet-vehicle.md`](./entities/08-pet-vehicle.md) |
| `…/game/Entities/GameObject/*` | [`entities/06-gameobject.md`](./entities/06-gameobject.md) |
| `…/game/Entities/Item/*` | [`entities/07-item.md`](./entities/07-item.md) |
| `…/game/Entities/Object/Object.{h,cpp}` | [`entities/01-object-hierarchy.md`](./entities/01-object-hierarchy.md), [`entities/03-update-fields.md`](./entities/03-update-fields.md) |
| `…/game/Entities/Object/ObjectGuid.{h,cpp}` | [`entities/02-object-guid.md`](./entities/02-object-guid.md) |
| `…/game/Entities/Object/Updater/UpdateMask.h` | [`entities/03-update-fields.md`](./entities/03-update-fields.md) |
| `…/game/Entities/Pet/*` | [`entities/08-pet-vehicle.md`](./entities/08-pet-vehicle.md) |
| `…/game/Entities/Player/Player.{h,cpp}` | [`entities/04-player.md`](./entities/04-player.md) |
| `…/game/Entities/Totem/*` | [`entities/08-pet-vehicle.md`](./entities/08-pet-vehicle.md) |
| `…/game/Entities/Transport/*` | [`entities/09-corpse-transport.md`](./entities/09-corpse-transport.md) |
| `…/game/Entities/Unit/Unit.{h,cpp}` | [`entities/01-object-hierarchy.md`](./entities/01-object-hierarchy.md) |
| `…/game/Entities/Vehicle/*` | [`entities/08-pet-vehicle.md`](./entities/08-pet-vehicle.md) |
| `…/game/Events/GameEventMgr.{h,cpp}` | [`world/05-game-events.md`](./world/05-game-events.md) |
| `…/game/Globals/ObjectMgr.{h,cpp}` | [`entities/10-object-mgr.md`](./entities/10-object-mgr.md) |
| `…/game/Grids/*` | [`maps/03-grids-cells.md`](./maps/03-grids-cells.md), [`maps/04-grid-loading.md`](./maps/04-grid-loading.md) |
| `…/game/Groups/Group.{h,cpp}` | [`social/01-groups.md`](./social/01-groups.md) |
| `…/game/Guilds/Guild.{h,cpp}`, `GuildMgr.{h,cpp}` | [`social/02-guilds.md`](./social/02-guilds.md) |
| `…/game/Handlers/AuctionHouseHandler.cpp` | [`social/04-auction-house.md`](./social/04-auction-house.md) |
| `…/game/Handlers/CharacterHandler.cpp` | [`handlers/01-character-handler.md`](./handlers/01-character-handler.md) |
| `…/game/Handlers/ChatHandler.cpp` | [`handlers/05-chat-handler.md`](./handlers/05-chat-handler.md) |
| `…/game/Handlers/ItemHandler.cpp` | [`handlers/03-item-handler.md`](./handlers/03-item-handler.md) |
| `…/game/Handlers/MiscHandler.cpp` | [`handlers/06-misc-handler.md`](./handlers/06-misc-handler.md) |
| `…/game/Handlers/MovementHandler.cpp` | [`handlers/02-movement-handler.md`](./handlers/02-movement-handler.md) |
| `…/game/Handlers/SpellHandler.cpp` | [`handlers/04-spell-handler.md`](./handlers/04-spell-handler.md) |
| `…/game/Instances/InstanceSaveMgr.{h,cpp}` | [`instances/01-instance-save.md`](./instances/01-instance-save.md) |
| `…/game/Instances/InstanceScript.{h,cpp}` | [`instances/02-instance-script.md`](./instances/02-instance-script.md) |
| `…/game/Loot/Loot{Mgr,Itemlist,Roll}.{h,cpp}` | [`loot/`](./loot/00-index.md) |
| `…/game/Mails/*` | [`social/03-mail.md`](./social/03-mail.md) |
| `…/game/Maps/Map.{h,cpp}` | [`maps/01-map-hierarchy.md`](./maps/01-map-hierarchy.md) |
| `…/game/Maps/MapMgr.{h,cpp}` | [`maps/02-map-mgr.md`](./maps/02-map-mgr.md) |
| `…/game/Maps/MMaps/*` | [`maps/06-mmaps.md`](./maps/06-mmaps.md) |
| `…/game/Maps/VMaps/*` | [`maps/07-vmaps.md`](./maps/07-vmaps.md) |
| `…/game/Movement/MotionMaster.{h,cpp}` | [`movement/01-motion-master.md`](./movement/01-motion-master.md) |
| `…/game/Movement/MovementGenerator*.{h,cpp}` | [`movement/02-generators.md`](./movement/02-generators.md) |
| `…/game/Movement/Spline/MoveSpline*.{h,cpp}` | [`movement/03-spline.md`](./movement/03-spline.md) |
| `…/game/Movement/PathGenerator.{h,cpp}` | [`movement/04-pathfinder.md`](./movement/04-pathfinder.md) |
| `…/game/Movement/CreatureGroups.{h,cpp}` | [`movement/05-formation.md`](./movement/05-formation.md) |
| `…/game/Quests/*` | [`quests/`](./quests/00-index.md) |
| `…/game/Scripting/ScriptMgr.{h,cpp}` | [`scripting/01-script-mgr.md`](./scripting/01-script-mgr.md) |
| `…/game/Scripting/ScriptDefines/*Script.h` | [`scripting/02-hook-classes.md`](./scripting/02-hook-classes.md), [`scripting/03-script-objects.md`](./scripting/03-script-objects.md) |
| `…/game/Server/Opcodes.{h,cpp}` | [`network/03-opcodes.md`](./network/03-opcodes.md) |
| `…/game/Server/Protocol/*` | [`network/03-opcodes.md`](./network/03-opcodes.md) |
| `…/game/Server/WorldPacket.h` | [`network/02-worldpacket.md`](./network/02-worldpacket.md) |
| `…/game/Server/WorldSession.{h,cpp}`, `…/game/Server/WorldSessionMgr.{h,cpp}` | [`network/05-worldsession.md`](./network/05-worldsession.md) |
| `…/game/Server/WorldSocket.{h,cpp}`, `WorldSocketMgr.{h,cpp}` | [`network/04-worldsocket.md`](./network/04-worldsocket.md) |
| `…/game/Spells/Auras/Aura.{h,cpp}`, `AuraEffect*`, `AuraApplication*` | [`spells/03-aura-system.md`](./spells/03-aura-system.md) |
| `…/game/Spells/Spell.{h,cpp}` | [`spells/01-cast-lifecycle.md`](./spells/01-cast-lifecycle.md) |
| `…/game/Spells/SpellEffects.cpp` | [`spells/05-effects.md`](./spells/05-effects.md) |
| `…/game/Spells/SpellInfo.{h,cpp}` | [`spells/02-spell-info.md`](./spells/02-spell-info.md) |
| `…/game/Spells/SpellMgr.{h,cpp}` | [`spells/02-spell-info.md`](./spells/02-spell-info.md), [`spells/06-proc-system.md`](./spells/06-proc-system.md) |
| `…/game/Spells/SpellScript.{h,cpp}` | [`spells/08-script-bindings.md`](./spells/08-script-bindings.md) |
| `…/game/Tickets/*` | (out of scope for Phase 1; cross-link to `world/00-index.md`) |
| `…/game/Warden/*` | [`network/07-warden.md`](./network/07-warden.md) |
| `…/game/Weather/Weather*.{h,cpp}` | [`world/04-weather.md`](./world/04-weather.md) |
| `…/game/World/World.{h,cpp}` | [`world/01-world-singleton.md`](./world/01-world-singleton.md) |
| `…/shared/DataStores/DBCFileLoader.{h,cpp}` | [`dbc/01-loader.md`](./dbc/01-loader.md) |
| `…/shared/DataStores/DBCStore.h` | [`dbc/02-stores.md`](./dbc/02-stores.md) |
| `…/shared/DataStores/DBCStores.{h,cpp}` | [`dbc/02-stores.md`](./dbc/02-stores.md), [`dbc/05-load-sequence.md`](./dbc/05-load-sequence.md) |
| `…/shared/DataStores/DBCStructure.h` | [`dbc/04-structures.md`](./dbc/04-structures.md) |
| `…/shared/DataStores/DBCfmt.h` | [`dbc/03-format-strings.md`](./dbc/03-format-strings.md) |
| `…/shared/Realms/*` | [`network/08-realmlist.md`](./network/08-realmlist.md) |
| `src/server/database/Database/DatabaseEnv.h` | [`database/01-database-env.md`](./database/01-database-env.md) |
| `src/server/database/Database/DatabaseWorker*.{h,cpp}` | [`database/03-async-vs-sync.md`](./database/03-async-vs-sync.md) |
| `src/server/database/Database/Implementation/{World,Character,Login}Database.h` | [`database/02-prepared-statements.md`](./database/02-prepared-statements.md) |
| `src/server/database/Database/MySQLConnection.{h,cpp}` | [`database/06-connection-pool.md`](./database/06-connection-pool.md) |
| `src/server/database/Database/PreparedStatement.{h,cpp}` | [`database/02-prepared-statements.md`](./database/02-prepared-statements.md) |
| `src/server/database/Database/QueryHolder.{h,cpp}` | [`database/04-query-holders.md`](./database/04-query-holders.md) |
| `src/server/database/Database/Transaction.{h,cpp}` | [`database/05-transactions.md`](./database/05-transactions.md) |
| `src/server/database/Updater/*` | [`database/07-update-mechanism.md`](./database/07-update-mechanism.md) |
| `src/server/apps/authserver/Main.cpp` | [`server-apps/01-authserver.md`](./server-apps/01-authserver.md) |
| `src/server/apps/worldserver/Main.cpp` | [`server-apps/02-worldserver.md`](./server-apps/02-worldserver.md) |
| `src/tools/mmaps_generator/*` | [`tools/01-mmaps-generator.md`](./tools/01-mmaps-generator.md) |
| `src/tools/vmap*/*` | [`tools/02-vmaps-extractor.md`](./tools/02-vmaps-extractor.md) |
| `src/tools/map_extractor/*` | [`tools/03-map-extractor.md`](./tools/03-map-extractor.md) |
| `src/tools/dbc_extractor/*` | [`tools/04-dbc-extractor.md`](./tools/04-dbc-extractor.md) |
| `modules/CMakeLists.txt`, `modules/ModulesLoader.cpp.in.cmake` | [`scripting/05-module-discovery.md`](./scripting/05-module-discovery.md) |
| `data/sql/base/db_*/`, `data/sql/updates/{,pending_}db_*/` | [`database/07-update-mechanism.md`](./database/07-update-mechanism.md), [`database/08-schema-policy.md`](./database/08-schema-policy.md) |

If your file isn't here, fall back to [`00-INDEX.md`](./00-INDEX.md) (subsystem table) or `grep` for the file's header comment in this folder.
