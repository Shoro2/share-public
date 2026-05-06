# handlers — Chat handler

> One mega-handler for `CMSG_MESSAGECHAT` (~570 lines of switch-on-`type`), plus client emote, text emote, chat-ignored, and channel-decline. Channel commands (`/join`, `/leave`, `/list`, `/kick`, …) are in `ChannelHandler.cpp` (cross-link [`../social/05-channels.md`](../social/05-channels.md)).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Handlers/ChatHandler.cpp:59` | `WorldSession::HandleMessagechatOpcode` — entry, validates type & language, dispatches by `ChatMsg type` |
| `src/server/game/Handlers/ChatHandler.cpp:350` | `sScriptMgr->OnPlayerBeforeSendChatMessage` (universal pre-send hook) |
| `src/server/game/Handlers/ChatHandler.cpp:354` | `case CHAT_MSG_SAY/EMOTE/YELL` — `Player::Say` / `TextEmote` / `Yell` |
| `src/server/game/Handlers/ChatHandler.cpp:376` | `case CHAT_MSG_WHISPER` — name normalize, faction check, GM silence |
| `src/server/game/Handlers/ChatHandler.cpp:421` | `case CHAT_MSG_PARTY` / `CHAT_MSG_PARTY_LEADER` |
| `src/server/game/Handlers/ChatHandler.cpp:444` | `case CHAT_MSG_GUILD` — `Guild::BroadcastToGuild` |
| `src/server/game/Handlers/ChatHandler.cpp:458` | `case CHAT_MSG_OFFICER` |
| `src/server/game/Handlers/ChatHandler.cpp:472` | `case CHAT_MSG_RAID` / `RAID_LEADER` |
| `src/server/game/Handlers/ChatHandler.cpp:510` | `case CHAT_MSG_RAID_WARNING` |
| `src/server/game/Handlers/ChatHandler.cpp:525` | `case CHAT_MSG_BATTLEGROUND` / `BATTLEGROUND_LEADER` |
| `src/server/game/Handlers/ChatHandler.cpp:555` | `case CHAT_MSG_CHANNEL` — `Channel::Say` |
| `src/server/game/Handlers/ChatHandler.cpp:578` | `case CHAT_MSG_AFK` |
| `src/server/game/Handlers/ChatHandler.cpp:604` | `case CHAT_MSG_DND` |
| `src/server/game/Handlers/ChatHandler.cpp:634` | `WorldSession::HandleEmoteOpcode` (one-shot wave / hardcoded set) |
| `src/server/game/Handlers/ChatHandler.cpp:684` | `WorldSession::HandleTextEmoteOpcode` (`/dance`, `/cry`, …) |
| `src/server/game/Handlers/ChatHandler.cpp:748` | `WorldSession::HandleChatIgnoredOpcode` (notify sender they are ignored) |
| `src/server/game/Handlers/ChatHandler.cpp:765` | `WorldSession::HandleChannelDeclineInvite` |

## Opcodes covered

All `STATUS_LOGGEDIN`. Source: `Opcodes.cpp:280`–`1171`.

| Opcode | Handler | Purpose |
|---|---|---|
| `CMSG_MESSAGECHAT` (`0x095`) | `HandleMessagechatOpcode` | All chat (say / yell / whisper / party / guild / channel / AFK / DND / addon). |
| `CMSG_EMOTE` (`0x102`) | `HandleEmoteOpcode` | Hardcoded one-shot emotes (wave / none). |
| `CMSG_TEXT_EMOTE` (`0x104`) | `HandleTextEmoteOpcode` | `/dance`, `/sit`, etc.; broadcast as `SMSG_TEXT_EMOTE`. |
| `CMSG_CHAT_IGNORED` (`0x225`) | `HandleChatIgnoredOpcode` | "Player has ignored you" notification. |
| `CMSG_DECLINE_CHANNEL_INVITE` (`0x410`) | `HandleChannelDeclineInvite` | Decline a channel invite. |
| `CMSG_SET_CHANNEL_WATCH` (`0x3EF`) | `HandleSetChannelWatch` (channel-watch list) | Stub-level; lives in `ChannelHandler.cpp`. |

For the canonical opcode list: [`../network/03-opcodes.md`](../network/03-opcodes.md). Channel-specific opcodes (`CMSG_JOIN_CHANNEL` 0x097, `CMSG_LEAVE_CHANNEL` 0x098, `CMSG_CHANNEL_*` …) live in `ChannelHandler.cpp` and are documented in [`../social/05-channels.md`](../social/05-channels.md).

## Key concepts

- **Message-type dispatch**: `HandleMessagechatOpcode` reads `(type, lang)` first, then optionally `to` (whisper) / `channel` (channel) and `msg`. The big `switch (type)` at `:352` selects the broadcast strategy.
- **Universal pre-validation** (top of `HandleMessagechatOpcode`):
  - Type bound (`type < MAX_CHAT_MSG_TYPE`, `:67`).
  - `LANG_UNIVERSAL` allowed only for AFK/DND (anti-cheat, `:74`).
  - Language must be a known `LanguageDesc` and the speaker must have the language skill or `SPELL_AURA_COMPREHEND_LANGUAGE` for it (`:85`–`:111`).
  - First-login mute: under `CONFIG_CHAT_MUTE_FIRST_LOGIN` minutes the player can only use party/raid/guild/etc. (`:115`).
- **Spectator gag**: arena spectators are blocked from say/yell/emote/AFK/DND (`:152`).
- **Faction wall**: cross-faction whispers require `CONFIG_ALLOW_TWO_SIDE_INTERACTION_CHAT` (`:400`).
- **GM silence (`spell 1852`)**: a GM-applied debuff that prevents whispers (`:408`).
- **Auto-whisper-whitelist**: GMs auto-whitelist anyone they whisper to (`:415`).
- **Group disambiguation**: `Player::GetOriginalGroup()` is checked first for raid/party chat so battleground temp groups don't shadow the player's real group (`:425`).
- **Channel routing**: `ChannelMgr::forTeam(teamId)->GetChannel(name, sender)->Say(...)`; channel objects are documented in [`../social/05-channels.md`](../social/05-channels.md).
- **`autoReplyMsg`**: AFK/DND store the away-message on the `Player` object; toggling without a message clears state (`:584`–`:621`).
- **Addon messages**: `lang == LANG_ADDON` (-1) is the AIO transport — see [`../../04-aio-framework.md`](../../04-aio-framework.md). The handler counts `_addonMessageReceiveCount` for metrics (`:347`).

## Flow / data shape

```
client CMSG_MESSAGECHAT  (type, lang, [to|channel], msg)
        │
        ▼
HandleMessagechatOpcode  (ChatHandler.cpp:59)
        │  type / lang validation
        │  language-skill / aura check
        │  first-login mute check
        │  spectator gag
        │  hyperlink validation (throws WorldPackets::*HyperlinkException)
        │
        ▼
sScriptMgr->OnPlayerBeforeSendChatMessage   (:350)
        │
        ▼
switch (type)
  ├─ SAY/YELL/EMOTE  ─► sender->Say|Yell|TextEmote (level req)
  ├─ WHISPER         ─► sender->Whisper(msg, lang, receiver)
  ├─ PARTY/RAID/BG   ─► Group::BroadcastPacket
  ├─ GUILD/OFFICER   ─► Guild::BroadcastToGuild
  ├─ CHANNEL         ─► Channel::Say
  └─ AFK/DND         ─► Player::ToggleAFK / ToggleDND
```

Hyperlink errors (`InvalidHyperlinkException`, `IllegalHyperlinkException`) are caught in `WorldSession::Update` (`WorldSession.cpp:488`) and may kick the player under `CONFIG_CHAT_STRICT_LINK_CHECKING_KICK`.

## Hooks & extension points

- `sScriptMgr->OnPlayerBeforeSendChatMessage` (`:350`) — universal pre-broadcast.
- `sScriptMgr->OnPlayerCanUseChat` (multiple call-sites, `:436`–`:623`) — overload taking `Group*` / `Guild*` / `Channel*` / `Player*` (whisper) / no extra (general). Veto by returning `false`.
- `sScriptMgr->OnPlayerEmote` (`:648`) — `HandleEmoteOpcode`.
- `sScriptMgr->OnPlayerTextEmote` (`:708`) — `HandleTextEmoteOpcode`.

`PlayerScript` declarations: `src/server/game/Scripting/ScriptDefines/PlayerScript.h`. See [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).

## Cross-references

- Engine-side: [`../social/05-channels.md`](../social/05-channels.md) (channel system + `ChannelHandler.cpp`), [`../social/01-groups.md`](../social/01-groups.md) (`Group::BroadcastPacket`), [`../social/02-guilds.md`](../social/02-guilds.md) (`Guild::BroadcastToGuild`), [`../entities/04-player.md`](../entities/04-player.md) (`Player::Say` / `Whisper` / `TextEmote`), [`../network/03-opcodes.md`](../network/03-opcodes.md), [`../network/05-worldsession.md`](../network/05-worldsession.md) (hyperlink-exception handling).
- Project-side: [`../../04-aio-framework.md`](../../04-aio-framework.md) (`LANG_ADDON` transport), [`../../05-modules.md`](../../05-modules.md).
- External: Doxygen `classWorldSession` (`HandleMessagechatOpcode`).
