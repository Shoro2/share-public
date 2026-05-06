# social/ — Groups, guilds, mail, auction house, channels

> Player-to-player and player-to-system social systems. Each lives in its own subsystem with a singleton manager (`GuildMgr`, `MailMgr`, `AuctionHouseMgr`, `ChannelMgr`); groups are owned by `GroupMgr`.

## Topic files

| File | Topic |
|---|---|
| [`01-groups.md`](./01-groups.md) | `Group`, raid, role assignment, ready check, marker icons, distribute loot |
| [`02-guilds.md`](./02-guilds.md) | `Guild`, `GuildBank`, ranks, achievements, `_guild` DB tables |
| [`03-mail.md`](./03-mail.md) | `MailMgr`, `Mail`, expiration, `ServerMailMgr` (system mail), `mod-paragon-itemgen` mail integration |
| [`04-auction-house.md`](./04-auction-house.md) | `AuctionHouseMgr`, factions (Alliance/Horde/Goblin), bid resolution |
| [`05-channels.md`](./05-channels.md) | `ChannelMgr`, world chat, dynamic channels, custom channels |

## Critical files

| File | Role |
|---|---|
| `src/server/game/Groups/Group.{h,cpp}`, `GroupMgr.{h,cpp}` | Party/raid |
| `src/server/game/Guilds/Guild.{h,cpp}`, `GuildMgr.{h,cpp}` | Guilds |
| `src/server/game/Mails/Mail.{h,cpp}`, `MailMgr.{h,cpp}` | Mailbox |
| `src/server/game/AuctionHouse/AuctionHouseMgr.{h,cpp}`, `AuctionHouseSearcher.{h,cpp}` | AH |
| `src/server/game/Chat/Channels/Channel.{h,cpp}`, `ChannelMgr.{h,cpp}` | Channels |
| `src/server/game/Handlers/{Group,Guild,Mail,AuctionHouse,Chat}Handler.cpp` | Opcode dispatch |

## Cross-references

- Engine-side: [`../entities/04-player.md`](../entities/04-player.md), [`../handlers/00-index.md`](../handlers/00-index.md), [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md) (`GuildScript`, `MailScript`, `AuctionHouseScript`, `ChannelScript`, …)
- Project-side: [`../../05-modules.md`](../../05-modules.md) (mod-auto-loot mails overflow items; mod-paragon-itemgen blocks auctions/trades for cursed items)
- External: Doxygen for `Guild`, `Group`, `Mail`, `AuctionHouseMgr`, `ChannelMgr`
