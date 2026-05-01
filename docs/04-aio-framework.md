# 04 — AIO-Framework (Server↔Client UI-Kommunikation)

AIO (Addon IO) ermöglicht es, Lua-Code vom Server an den WoW-Client zu senden und bidirektional zu kommunizieren. Damit lassen sich echte WoW-Frames bauen statt Gossip-Menüs.

**Liegt im Repo:**
- `share-public/AIO_Server/` → ins Server-`lua_scripts/`-Verzeichnis kopieren (Eluna lädt von dort)
- `share-public/AIO_Client/` → in Client-`Interface/AddOns/AIO_Client/`

Version 1.75. Beide Seiten teilen denselben `AIO.lua`-Code (~1300 Zeilen).

## Architektur-Übersicht

```
Server (Eluna)                     Client (WoW Addon)
   |                                   |
   +-- AIO.AddAddon("file.lua")        |
   |   sendet Code an Client  ─────────+→ loadstring()() führt aus
   +-- AIO.AddOnInit(func)             |
   |   Initial-Daten bei Login         |
   +-- AIO.Msg():Add():Send(player) ───+→ Handler aufgerufen
   +-- Handler aufgerufen ←────────────+── AIO.Msg():Add():Send()
```

## Schlüssel-APIs

| Funktion | Seite | Zweck |
|----------|-------|-------|
| `AIO.AddAddon([path, name])` | Server | Datei zum Senden registrieren |
| `AIO.AddHandlers(name, table)` | beide | Handler-Funktionen registrieren |
| `AIO.Msg()` | beide | Nachricht erstellen |
| `msg:Add(name, handler, ...)` | beide | Handler-Aufruf anhängen |
| `msg:Send(player)` / `msg:Send()` | Server / Client | Senden |
| `AIO.Handle(player, name, handler, ...)` | Server | Shorthand Msg+Add+Send |
| `AIO.Handle(name, handler, ...)` | Client | Shorthand |
| `AIO.AddOnInit(func)` | Server | Hook für Login-Nachricht |
| `AIO.SavePosition(frame, char)` | Client | Frame-Position speichern |
| `AIO.AddSavedVar(key)` / `AddSavedVarChar(key)` | Client | Account/Char-Variablen |

## Handler-Pattern (WICHTIG)

`AIO.AddHandlers()` wrappt alle Handler-Funktionen so:

```lua
local function handler(player, key, ...)
    if key and handlertable[key] then
        handlertable[key](player, ...)
    end
end
```

→ **`player` ist IMMER das erste Argument** in JEDEM Handler — auf Server **und** Client.

| Seite | Was ist `player`? |
|-------|-------------------|
| Server | Eluna Player-Userdata (`:GetName()`, `:Teleport()`, ...) |
| Client | String mit Spielername (aus `UnitName("player")`) — **nicht nil!** |

Korrektes Pattern:

```lua
-- Server
ServerHandlers.StartChallenge = function(player, mapId, difficulty)
    -- player = Eluna Player
end

-- Client
ClientHandlers.InitDungeon = function(player, mapId, name, timerMin, bossCount)
    -- player = String, NICHT ignorieren!
end
```

## Re-Registrierungs-Falle

`AIO.AddHandlers` hat einen `assert`, der zweimaliges Registrieren desselben Handler-Namens blockiert. Wenn AIO Code ein zweites Mal an den Client schickt (z.B. nach Code-Änderung), schlägt der zweite `loadstring()()`-Aufruf am `AIO.AddHandlers` fehl. Folge: alte Closure-Variablen bleiben aktiv, neue werden nie erreicht.

**Workaround — globale Handler-Tabelle:**

```lua
if not MY_Handlers then MY_Handlers = {} end

-- Funktionen in-place ersetzen (neue Closure über aktuelle Locals)
MY_Handlers.MyFunc = function(player, ...)
    -- referenziert AKTUELLE locals
end

if not MY_HandlersRegistered then
    AIO.AddHandlers("MyAddon", MY_Handlers)
    MY_HandlersRegistered = true
end
```

Funktioniert weil der AIO-Wrapper eine Referenz auf das **Tabellen-Objekt** hält, nicht eine Kopie der Funktionen.

## Nachrichten-Limits

| Richtung | Max Paketgröße | Transport |
|----------|---------------|-----------|
| Server → Client | 2560 Bytes | Eluna `CHAT_MSG_ADDON` |
| Client → Server | 255 Bytes | `SendAddonMessage(prefix, msg, "WHISPER", UnitName("player"))` |

- Lange Nachrichten werden serverseitig gesplittet und clientseitig reassembliert.
- Unvollständige Nachrichten verfallen nach 15 s. Memory-Limit: 500 KB pro Spieler.
- **Max 15 Argumente pro `msg:Add()` Block** auf Server-Seite.

## Code-Caching & CRC32

```
Server: AIO.AddAddon("file.lua")
   → Code lesen → LuaSrcDiet (optional Minify) → LZW komprimieren → CRC32
   → in AIO_ADDONSORDER speichern: {name, crc, code}

Client Login
   → sendet {addon_name → crc} aller gecachten Addons
Server vergleicht
   ├─ CRC stimmt → nicht senden (Bandbreite sparen)
   └─ CRC anders → neuen Code senden → Client aktualisiert AIO_sv_Addons
```

SavedVariables auf Client:

| Variable | Scope | Inhalt |
|----------|-------|--------|
| `AIO_sv` | Account | `AIO.AddSavedVar(key)` Variablen |
| `AIO_sv_char` | Character | `AIO.AddSavedVarChar(key)` Variablen |
| `AIO_sv_Addons` | Account | Cache `{name → {name, crc, code}}` |

## Initialisierungs-Ablauf (Client)

```
ADDON_LOADED("AIO_Client")
  1. SavedVars laden, _G[] wiederherstellen
  2. CRC-Hashes aller Addons sammeln
  3. Init senden: AIO.Msg():Add("AIO", "Init", VERSION, {name→crc})
     (1s Initialdelay, 1.5x Backoff bis AIO_INITED)
  →  Server antwortet
     ├─ neue/geänderte Addons → in AIO_sv_Addons schreiben
     ├─ gecachte Addons → aus Cache lesen
     └─ alle in Reihenfolge ausführen via RunAddon(name):
        Code aus Cache → ggf. LZW dekomprimieren → loadstring(code, name)()
  AIO_INITED = true
```

## Force-Reload / Reset

| Befehl | Wirkung |
|--------|---------|
| `AIO.Handle(player, "AIO", "ForceReload")` | unsichtbarer Vollbild-Button → Klick triggert `ReloadUI()` |
| `AIO.Handle(player, "AIO", "ForceReset")` | Cache leeren + ForceReload |
| `/aio reset` (Client) | manuell Addon-Cache leeren |
| `/aio version` | Version anzeigen |
| `/aio help` | Befehle |

## AIO-Datei-Struktur eines Custom-Moduls

```
lua_scripts/
├── AIO.lua, queue.lua, bit53.lua, LibCompress.lua,
│   lualzw-zeros/, Dep_Smallfolk/, Dep_LuaSrcDiet/, Dep_crc32lua/   ← AIO Framework
├── my_addon_server.lua    # Eluna-Server-Script + AIO.AddAddon()
└── my_addon_client.lua    # Client-UI (per AIO an WoW-Client gesendet)
```

## Praxistipps

- **Tabellen als Argumente** funktionieren (Smallfolk serialisiert), aber bei vielen Items besser **flach senden** (1 AIO.Handle pro Eintrag) wegen Paket-Limits.
- **Nicht in OnInit feuern, was ein Player-Objekt verlangt** — beim allerersten Login ist das Player-Objekt noch nicht "ready". `OnLogin` ist sicherer.
- **`AIO.AddAddon()` am Anfang der Client-Datei** mit Early-Return:
  ```lua
  if AIO.AddAddon() then return end
  -- ... Client-Code ...
  ```
  → Server-Pfad: AddAddon registriert die Datei und returns true → kein UI-Code wird auf Server ausgeführt.
- **Item-Info-Cache**: `GetItemInfo()` ist auf Client async. Bei Frame-Render einen Retry-Timer einplanen (siehe mod-endless-storage `endless_storage_client.lua`).

## Beispiel — minimale Round-Trip-UI

```lua
-- server.lua (Eluna)
AIO.AddAddon()  -- ohne args → diese Datei wird nicht zum Client geschickt
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
