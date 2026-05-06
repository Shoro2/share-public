# quests/ — Quest system

> Quest definitions live in `quest_template` (loaded by `ObjectMgr`); per-character status lives in `character_queststatus*` tables and is mirrored on `Player` as `QuestStatusMap`. Acceptance, completion, and turn-in flow through `QuestHandler`.

## Topic files

| File | Topic |
|---|---|
| [`01-quest-data.md`](./01-quest-data.md) | `Quest` class, `QuestStatusData`, `quest_template_addon`, reward layout |
| [`02-quest-flow.md`](./02-quest-flow.md) | Accept → in-progress → complete → turn-in pipeline, `CompleteQuest`, `RewardQuest` |
| [`03-objective-tracking.md`](./03-objective-tracking.md) | Kill counters, item collect, exploration triggers, area triggers, spell objectives |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Quests/Quest.{h,cpp}` | `Quest` class, parsing |
| `src/server/game/Quests/QuestDef.h` | enums + flags |
| `src/server/game/Globals/ObjectMgr.cpp` | `LoadQuests`, `LoadQuestRelations` |
| `src/server/game/Handlers/QuestHandler.cpp` | Opcode dispatch |
| `src/server/game/Entities/Player/Player.cpp` | `AddQuest`, `SatisfyQuest*`, `CompleteQuest`, `RewardQuest` |

## Cross-references

- Engine-side: [`../entities/04-player.md`](../entities/04-player.md), [`../entities/10-object-mgr.md`](../entities/10-object-mgr.md), [`../handlers/00-index.md`](../handlers/00-index.md)
- Project-side: [`../../05-modules.md`](../../05-modules.md) (mod-paragon-itemgen hooks `OnPlayerQuestRewardItem`), [`../../09-db-tables.md`](../../09-db-tables.md) (`quest_*` tables)
- External: Doxygen for `Quest`, `Player::AddQuest`/`CompleteQuest`/`RewardQuest`
