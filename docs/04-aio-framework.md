# 04 — AIO framework (server↔client UI communication)

AIO (Addon IO) lets you send Lua code from the server to the WoW client and communicate bidirectionally. With it you can build real WoW frames instead of gossip menus.

**In the repo:**
- `share-public/AIO_Server/` → copy into the server `lua_scripts/` directory (Eluna loads from there)
- `share-public/AIO_Client/` → into the client `Interface/AddOns/AIO_Client/`

Version 1.75. Both sides share the same `AIO.lua` code (~1300 lines).

## Architecture overview

```
Server (Eluna)                     Client (WoW addon)
   |                                   |
   +-- AIO.AddAddon("file.lua")        |
   |   sends code to the client ──────+→ loadstring()() executes
   +-- AIO.AddOnInit(func)             |
   |   initial data on login           |
   +-- AIO.Msg():Add():Send(player) ───+→ handler called
   +-- handler called ←────────────────+── AIO.Msg():Add():Send()
```

## Key APIs

| Function | Side | Purpose |
|----------|-------|-------|
| `AIO.AddAddon([path, name])` | server | register a file to send |
| `AIO.AddHandlers(name, table)` | both | register handler functions |
| `AIO.Msg()` | both | create a message |
| `msg:Add(name, handler, ...)` | both | append a handler call |
| `msg:Send(player)` / `msg:Send()` | server / client | send |
| `AIO.Handle(player, name, handler, ...)` | server | shorthand Msg+Add+Send |
| `AIO.Handle(name, handler, ...)` | client | shorthand |
| `AIO.AddOnInit(func)` | server | hook for the login message |
| `AIO.SavePosition(frame, char)` | client | save frame position |
| `AIO.AddSavedVar(key)` / `AddSavedVarChar(key)` | client | account/char variables |

## Handler pattern (IMPORTANT)

`AIO.AddHandlers()` wraps every handler function like this:

```lua
local function handler(player, key, ...)
    if key and handlertable[key] then
        handlertable[key](player, ...)
    end
end
```

→ **`player` is ALWAYS the first argument** in EVERY handler — on server **and** client.

| Side | What is `player`? |
|-------|-------------------|
| Server | Eluna player userdata (`:GetName()`, `:Teleport()`, ...) |
| Client | string with the player's name (from `UnitName("player")`) — **not nil!** |

Correct pattern:

```lua
-- Server
ServerHandlers.StartChallenge = function(player, mapId, difficulty)
    -- player = Eluna player
end

-- Client
ClientHandlers.InitDungeon = function(player, mapId, name, timerMin, bossCount)
    -- player = string, do NOT ignore it!
end
```

## Re-registration trap

`AIO.AddHandlers` has an `assert` that blocks registering the same handler name twice. If AIO sends code to the client a second time (e.g. after a code change), the second `loadstring()()` call fails at `AIO.AddHandlers`. Consequence: old closure variables stay active, new ones are never reached.

**Workaround — global handler table:**

```lua
if not MY_Handlers then MY_Handlers = {} end

-- Replace functions in place (new closure over the current locals)
MY_Handlers.MyFunc = function(player, ...)
    -- references CURRENT locals
end

if not MY_HandlersRegistered then
    AIO.AddHandlers("MyAddon", MY_Handlers)
    MY_HandlersRegistered = true
end
```

Works because the AIO wrapper holds a reference to the **table object**, not a copy of the functions.

## Message limits

| Direction | Max packet size | Transport |
|----------|---------------|-----------|
| Server → Client | 2560 bytes | Eluna `CHAT_MSG_ADDON` |
| Client → Server | 255 bytes | `SendAddonMessage(prefix, msg, "WHISPER", UnitName("player"))` |

- Long messages are split server-side and reassembled client-side.
- Incomplete messages expire after 15 s. Memory limit: 500 KB per player.
- **Max 15 arguments per `msg:Add()` block** on the server side.

## Code caching & CRC32

```
Server: AIO.AddAddon("file.lua")
   → read code → LuaSrcDiet (optional minify) → LZW compress → CRC32
   → store in AIO_ADDONSORDER: {name, crc, code}

Client login
   → sends {addon_name → crc} of all cached addons
Server compares
   ├─ CRC matches → do not send (saves bandwidth)
   └─ CRC differs → send new code → client updates AIO_sv_Addons
```

SavedVariables on the client:

| Variable | Scope | Contents |
|----------|-------|--------|
| `AIO_sv` | account | `AIO.AddSavedVar(key)` variables |
| `AIO_sv_char` | character | `AIO.AddSavedVarChar(key)` variables |
| `AIO_sv_Addons` | account | cache `{name → {name, crc, code}}` |

## Initialization flow (client)

```
ADDON_LOADED("AIO_Client")
  1. load SavedVars, restore _G[]
  2. collect CRC hashes of all addons
  3. send Init: AIO.Msg():Add("AIO", "Init", VERSION, {name→crc})
     (1s initial delay, 1.5x backoff until AIO_INITED)
  →  server replies
     ├─ new/changed addons → write to AIO_sv_Addons
     ├─ cached addons → read from cache
     └─ run all in order via RunAddon(name):
        code from cache → optional LZW decompress → loadstring(code, name)()
  AIO_INITED = true
```

## Force reload / reset

| Command | Effect |
|--------|---------|
| `AIO.Handle(player, "AIO", "ForceReload")` | invisible full-screen button → click triggers `ReloadUI()` |
| `AIO.Handle(player, "AIO", "ForceReset")` | clear cache + ForceReload |
| `/aio reset` (client) | manually clear the addon cache |
| `/aio version` | show version |
| `/aio help` | commands |

## AIO file structure of a custom module

```
lua_scripts/
├── AIO.lua, queue.lua, bit53.lua, LibCompress.lua,
│   lualzw-zeros/, Dep_Smallfolk/, Dep_LuaSrcDiet/, Dep_crc32lua/   ← AIO framework
├── my_addon_server.lua    # Eluna server script + AIO.AddAddon()
└── my_addon_client.lua    # client UI (sent to the WoW client via AIO)
```

## Practical tips

- **Tables as arguments** work (Smallfolk serializes them), but with many items prefer **flat sending** (1 AIO.Handle per entry) due to packet limits.
- **Do not fire something requiring a player object in OnInit** — on the very first login the player object is not yet "ready". `OnLogin` is safer.
- **`AIO.AddAddon()` at the top of the client file** with an early return:
  ```lua
  if AIO.AddAddon() then return end
  -- ... client code ...
  ```
  → Server path: AddAddon registers the file and returns true → no UI code is run on the server.
- **Item info cache**: `GetItemInfo()` is async on the client. Plan a retry timer for frame render (see mod-endless-storage `endless_storage_client.lua`).

## Example — minimal round-trip UI

```lua
-- server.lua (Eluna)
AIO.AddAddon()  -- without args → this file is not sent to the client
AIO.AddHandlers("MyMod", {
    HelloFromClient = function(player, msg)
        player:SendBroadcastMessage("Server got: " .. tostring(msg))
        AIO.Handle(player, "MyMod", "Reply", "ack")
    end,
})

-- client.lua
if AIO.AddAddon() then return end
local handlers = {}
handlers.Reply = function(player, msg)
    print("Server says:", msg)
end
AIO.AddHandlers("MyMod", handlers)

local btn = CreateFrame("Button", "MyBtn", UIParent, "UIPanelButtonTemplate")
btn:SetSize(120, 30); btn:SetPoint("CENTER"); btn:SetText("Send")
btn:SetScript("OnClick", function()
    AIO.Handle("MyMod", "HelloFromClient", "ping")
end)
```
