# handlers/ — Opcode handler matrix

> Every gameplay opcode is dispatched on `WorldSession` to a `Handle*Opcode(WorldPacket&)` method. The methods are grouped by feature into ~30 `*Handler.cpp` files. This folder documents the major handler files and the opcodes they own.

## Topic files

| File | Topic |
|---|---|
| [`01-character-handler.md`](./01-character-handler.md) | char enum, create, delete, login (`CMSG_PLAYER_LOGIN`), customise/rename, logout |
| [`02-movement-handler.md`](./02-movement-handler.md) | `MSG_MOVE_*`, anti-teleport, fall/jump, root/unroot ack |
| [`03-item-handler.md`](./03-item-handler.md) | equip, swap, destroy, sockets, refund, mail |
| [`04-spell-handler.md`](./04-spell-handler.md) | `CMSG_CAST_SPELL`, cancel, learn, cooldown sync |
| [`05-chat-handler.md`](./05-chat-handler.md) | `CMSG_MESSAGECHAT`, channels, /say/yell/whisper, language switching |
| [`06-misc-handler.md`](./06-misc-handler.md) | ping, time sync, who, area trigger, social list |
| [`07-handler-registration.md`](./07-handler-registration.md) | how `OpcodeTable` binds names → status → handler, `DEFINE_HANDLER`-like macros |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Handlers/CharacterHandler.cpp` (~100 KB) | char-related opcodes |
| `src/server/game/Handlers/MovementHandler.cpp` | movement opcodes |
| `src/server/game/Handlers/ItemHandler.cpp` (~54 KB) | item ops |
| `src/server/game/Handlers/SpellHandler.cpp` | spell casts |
| `src/server/game/Handlers/ChatHandler.cpp` | chat |
| `src/server/game/Handlers/MiscHandler.cpp` (~61 KB) | catch-all |
| `src/server/game/Handlers/AuctionHouseHandler.cpp` | AH (cross-link [`../social/04-auction-house.md`](../social/04-auction-house.md)) |
| `src/server/game/Handlers/MailHandler.cpp` | mail (cross-link [`../social/03-mail.md`](../social/03-mail.md)) |
| `src/server/game/Handlers/GroupHandler.cpp` | group/raid (cross-link [`../social/01-groups.md`](../social/01-groups.md)) |
| `src/server/game/Handlers/GuildHandler.cpp` | guild (cross-link [`../social/02-guilds.md`](../social/02-guilds.md)) |
| `src/server/game/Handlers/QuestHandler.cpp` | quest interaction (cross-link [`../quests/`](../quests/00-index.md)) |
| `src/server/game/Handlers/LootHandler.cpp` | loot (cross-link [`../loot/`](../loot/00-index.md)) |
| `src/server/game/Server/Opcodes.{h,cpp}` | `OpcodeTable` registration |

## Cross-references

- Engine-side: [`../network/03-opcodes.md`](../network/03-opcodes.md) (opcode list), [`../network/05-worldsession.md`](../network/05-worldsession.md) (dispatch)
- Project-side: [`../../04-aio-framework.md`](../../04-aio-framework.md) (custom AIO opcodes ride on existing addon-message opcodes)
- External: Doxygen for `WorldSession`, `OpcodeTable`
