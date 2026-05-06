# world/ — `World` singleton, configuration, realm, weather, events, calendar

> The `World` singleton is the global entry point for everything that isn't a `Map` — it owns config, realm info, weather, world states, game events, calendar. Other singletons (`ConfigMgr`, `WeatherMgr`, `GameEventMgr`, `CalendarMgr`) are nested here.

## Topic files

| File | Topic |
|---|---|
| [`01-world-singleton.md`](./01-world-singleton.md) | `World` class, `m_worldStates`, `setRates`, world-wide flags, `WorldStateMgr` |
| [`02-config-mgr.md`](./02-config-mgr.md) | `ConfigMgr` singleton, `LoadAppConfigs`, `LoadModulesConfigs`, env override, `GetOption<T>` |
| [`03-realm-info.md`](./03-realm-info.md) | `Realm` struct, realm flags, build/version, realmlist sync (cross-link [`../network/08-realmlist.md`](../network/08-realmlist.md)) |
| [`04-weather.md`](./04-weather.md) | `Weather`, `WeatherMgr`, zone-based weather updates |
| [`05-game-events.md`](./05-game-events.md) | `GameEventMgr`, holiday events, conditional spawns |
| [`06-calendar.md`](./06-calendar.md) | `CalendarMgr`, in-game calendar, holiday flags |

## Critical files

| File | Role |
|---|---|
| `src/server/game/World/World.{h,cpp}` (~319 lines header) | Global world singleton |
| `src/server/game/World/WorldState.{h,cpp}`, `WorldStateMgr.{h,cpp}` | World-state map |
| `src/common/Configuration/Config.{h,cpp}` | `ConfigMgr` |
| `src/server/shared/Realms/Realm.{h,cpp}` | Realm record |
| `src/server/game/Weather/Weather.{h,cpp}`, `WeatherMgr.{h,cpp}` | Weather |
| `src/server/game/Events/GameEventMgr.{h,cpp}` | Game events |
| `src/server/game/Calendar/CalendarMgr.{h,cpp}` | Calendar |
| `azerothcore-wotlk/doc/ConfigPolicy.md` | Config policy (canonical) |
| `azerothcore-wotlk/doc/Logging.md` | Logging system (canonical, used everywhere) |

## Cross-references

- Engine-side: [`../architecture/03-update-loop.md`](../architecture/03-update-loop.md) (where `World::Update` runs), [`../network/08-realmlist.md`](../network/08-realmlist.md), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md) (`WorldScript`)
- Project-side: [`../../02-architecture.md#logging-framework`](../../02-architecture.md), [`../../05-modules.md`](../../05-modules.md) (modules typically register `WorldScript::OnAfterConfigLoad`)
- External: Doxygen for `World`, `ConfigMgr`, `WeatherMgr`, `GameEventMgr`, `CalendarMgr`
