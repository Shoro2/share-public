# core/01 — Engine overview (30k-foot view)

> One-page mental model of how `azerothcore-wotlk` runs. Drill down via [`00-INDEX.md`](./00-INDEX.md).

## Two processes

| Process | Path | Port | Role |
|---|---|---|---|
| `authserver` | `src/server/apps/authserver/` | 3724 | SRP6 login, realm list |
| `worldserver` | `src/server/apps/worldserver/` | 8085 | Gameplay |

They share `LoginDatabase` and a tiny TCP/realmlist relay; everything else is independent. Detail: [`server-apps/`](./server-apps/00-index.md), [`network/06-auth-srp6.md`](./network/06-auth-srp6.md), [`network/08-realmlist.md`](./network/08-realmlist.md).

## Three databases

| DB | Purpose |
|---|---|
| `acore_auth` | Accounts, realm list, IP bans |
| `acore_characters` | Character data, inventories, progression, custom Paragon tables |
| `acore_world` | Static world: creatures, items, quests, spells, loot, DBC overrides |

Connected through `WorldDatabase` / `CharacterDatabase` / `LoginDatabase` global pools — see [`database/01-database-env.md`](./database/01-database-env.md).

## Startup sequence (worldserver)

```
main()                                  src/server/apps/worldserver/Main.cpp
 └─ Config load                         core/world/02-config-mgr.md
 └─ Open MySQL pools                    core/database/06-connection-pool.md
 └─ World::SetInitialWorldSettings()    src/server/game/World/World.cpp
     ├─ LoadDBCStores()                 core/dbc/05-load-sequence.md
     ├─ ObjectMgr loads templates       core/entities/10-object-mgr.md
     ├─ MapMgr / Battleground init      core/maps/02-map-mgr.md
     └─ ScriptMgr::Initialize()         core/scripting/01-script-mgr.md
         └─ Addmodules*Scripts()        core/scripting/05-module-discovery.md
 └─ Start network listeners             core/network/04-worldsocket.md
 └─ World update loop                   core/architecture/03-update-loop.md
```

## The world tick

`World::Update(diff)` runs from a dedicated thread; per tick it:

1. Drains the network queue (incoming packets → `WorldSession::Update`).
2. Updates `MapMgr` (each loaded `Map` updates its grids → entities → AI → spells → movement).
3. Updates timed services (auctions, mails, weather, events, BG queues, calendar).
4. Flushes outgoing packets and DB async results.

Threading: 1 main world thread, N map-update threads (`MapUpdater`), 1+ DB worker threads per pool, 1+ I/O context threads (Boost.Asio). Detail: [`architecture/04-threading.md`](./architecture/04-threading.md).

## Layered code map

```
src/
├── common/                # Boost.Asio, crypto (SRP6, ARC4), logging, threading, configuration
│
├── server/
│   ├── apps/
│   │   ├── authserver/    # auth main()                    → core/server-apps/01-authserver.md
│   │   └── worldserver/   # world main()                   → core/server-apps/02-worldserver.md
│   │
│   ├── shared/
│   │   ├── Networking/    # TCP framing, encryption        → core/network/04-worldsocket.md
│   │   ├── Packets/       # ByteBuffer, WorldPacket        → core/network/01-bytebuffer.md, 02-worldpacket.md
│   │   ├── DataStores/    # DBC loaders + global stores    → core/dbc/
│   │   └── Realms/        # auth↔world realm sync          → core/network/08-realmlist.md
│   │
│   ├── database/
│   │   └── Database/      # Pools, prepared statements,    → core/database/
│   │                      #  query holders, transactions
│   │
│   ├── game/              # 51 subsystems, ~73k LOC of headers
│   │   ├── World/         # World singleton, weather       → core/world/
│   │   ├── Server/        # WorldSession, Opcodes          → core/network/05-worldsession.md, 03-opcodes.md
│   │   ├── Globals/       # ObjectMgr                      → core/entities/10-object-mgr.md
│   │   ├── Entities/      # Object → Unit → Player/...     → core/entities/01-object-hierarchy.md
│   │   ├── Spells/        # Spell, Aura, SpellMgr          → core/spells/
│   │   ├── Maps/          # Map, Grid, Cell                → core/maps/
│   │   ├── Movement/      # MotionMaster, MoveSpline       → core/movement/
│   │   ├── AI/            # CreatureAI, ScriptedAI, SmartAI→ core/ai/
│   │   ├── Scripting/     # ScriptMgr + hook registries    → core/scripting/
│   │   ├── Handlers/      # ~30 opcode handler files       → core/handlers/
│   │   ├── Instances/     # Saves, InstanceScript          → core/instances/
│   │   ├── Battlegrounds/ # BG, Arena, Battlefield         → core/battlegrounds/
│   │   ├── Loot/          # LootStore                      → core/loot/
│   │   ├── Quests/        # Quest data + flow              → core/quests/
│   │   ├── Groups/, Guilds/, Mails/, AuctionHouse/, Chat/  → core/social/
│   │   └── …
│   │
│   └── scripts/           # In-tree content scripts (bosses, GM commands, per-class spell scripts)
│
└── tools/                 # mmaps_generator, vmap*, map_extractor, dbc_extractor → core/tools/
```

## What this fork adds beyond upstream

- **Two custom PlayerScript hooks**: `OnPlayerCheckReagent`, `OnPlayerConsumeReagent` — used by `mod-endless-storage` for crafting integration. Source of truth: `azerothcore-wotlk/functions.md` and [`scripting/07-custom-hooks.md`](./scripting/07-custom-hooks.md).
- **Patched `Spell.dbc`** with custom spell IDs (`100xxx`, `900xxx`). Detail: [`../03-spell-system.md`](../03-spell-system.md), [`../06-custom-ids.md`](../06-custom-ids.md).

Everything else is upstream AzerothCore.

## Where things commonly go wrong (signpost)

| Symptom | Start here |
|---|---|
| Build fails / `-Werror` | [`architecture/05-build-system.md`](./architecture/05-build-system.md) + wiki/common-errors |
| DB updater complains | [`database/07-update-mechanism.md`](./database/07-update-mechanism.md) + wiki/Dealing-with-SQL-files |
| Custom DBC tooltip wrong | [`dbc/06-db-overrides.md`](./dbc/06-db-overrides.md) + [`../03-spell-system.md`](../03-spell-system.md) |
| Module not loaded | [`scripting/05-module-discovery.md`](./scripting/05-module-discovery.md) + [`scripting/06-static-vs-dynamic.md`](./scripting/06-static-vs-dynamic.md) |
| Hook not firing | [`scripting/01-script-mgr.md`](./scripting/01-script-mgr.md) + [`scripting/02-hook-classes.md`](./scripting/02-hook-classes.md) |
| Packet handler missing | [`network/03-opcodes.md`](./network/03-opcodes.md) + [`handlers/00-index.md`](./handlers/00-index.md) |

## See also

- [`02-glossary.md`](./02-glossary.md) — terminology used across this tree.
- [`03-file-locator.md`](./03-file-locator.md) — reverse lookup: filename → doc.
- [`04-reading-strategy.md`](./04-reading-strategy.md) — how to navigate efficiently.
