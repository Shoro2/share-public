-- share-public/AIO_Server/Dep_Validation/validation.lua
--
-- Mini-Validation-Lib zur SQL-Injection-Mitigation im Eluna/Lua-Layer.
-- Eluna's CharDBExecute / CharDBQuery kennen keine Prepared Statements, daher
-- müssen alle vom Client kommenden Argumente vor dem String-Concat geprüft
-- werden.
--
-- Verwendung:
--   local Validate = dofile("lua_scripts/Dep_Validation/validation.lua")
--   if not Validate.IsIntInRange(statId, 1, 17) then
--       return Validate.Reject(player, "AllocatePoint", "statId out of range")
--   end
--
-- Konsumenten (Stand 2026-05): mod-paragon (Paragon_Server.lua),
-- mod-loot-filter (LootFilter_Server.lua), mod-endless-storage
-- (endless_storage_server.lua).

local M = {}

-- ---------------------------------------------------------------------------
-- Type / Range
-- ---------------------------------------------------------------------------

-- True wenn v eine echte Integer-Zahl ist (kein Bruchteil, kein NaN, kein Inf).
function M.IsInt(v)
    if type(v) ~= "number" then return false end
    if v ~= v then return false end           -- NaN
    if v == math.huge or v == -math.huge then return false end
    return v == math.floor(v)
end

function M.IsIntInRange(v, lo, hi)
    return M.IsInt(v) and v >= lo and v <= hi
end

function M.IsPositiveInt(v, cap)
    cap = cap or 2147483647
    return M.IsInt(v) and v >= 1 and v <= cap
end

function M.IsNonNegativeInt(v, cap)
    cap = cap or 2147483647
    return M.IsInt(v) and v >= 0 and v <= cap
end

-- ---------------------------------------------------------------------------
-- Strings
-- ---------------------------------------------------------------------------

function M.IsStringMaxLen(s, n)
    return type(s) == "string" and #s <= n
end

-- True wenn s ein String ist, dessen Länge in [minLen, maxLen] liegt.
function M.IsStringInRange(s, minLen, maxLen)
    return type(s) == "string" and #s >= minLen and #s <= maxLen
end

-- Escapt einfache Quotes für rohes SQL-String-Concat.
-- ACHTUNG: dies ist KEIN Ersatz für Prepared Statements; wenn vermeidbar
-- die Quote-Eingabe nicht als SQL-Wert konkatieren, sondern auf Whitelists
-- mappen (siehe LootFilter conditionType etc.).
function M.SqlEscape(s)
    if type(s) ~= "string" then return "" end
    return s:gsub("'", "''"):gsub("\\", "\\\\")
end

-- ---------------------------------------------------------------------------
-- Whitelists
-- ---------------------------------------------------------------------------

-- True wenn v als Schlüssel im Lookup-Set steht. Set wird mit ToSet erzeugt:
--   local OPS = Validate.ToSet({0, 1, 2})
--   Validate.IsInWhitelist(op, OPS)
function M.IsInWhitelist(v, set)
    return set[v] == true
end

-- Konvertiert eine Sequenz {1,2,3} in {[1]=true,[2]=true,[3]=true}.
function M.ToSet(list)
    local s = {}
    for _, v in ipairs(list) do s[v] = true end
    return s
end

-- ---------------------------------------------------------------------------
-- Coercion (vorsichtig einsetzen — meistens reicht reine Validierung)
-- ---------------------------------------------------------------------------

-- v→Int oder default. Akzeptiert Number und String. Bricht bei Floats / NaN.
function M.CoerceInt(v, default)
    if type(v) == "number" then return M.IsInt(v) and v or default end
    if type(v) == "string" then
        local n = tonumber(v)
        if n and M.IsInt(n) then return n end
    end
    return default
end

-- v→IntInRange oder default.
function M.CoerceIntInRange(v, lo, hi, default)
    local n = M.CoerceInt(v, nil)
    if n and n >= lo and n <= hi then return n end
    return default
end

-- ---------------------------------------------------------------------------
-- Reject-Helper
-- ---------------------------------------------------------------------------

-- Loggt eine abgelehnte Handler-Eingabe und gibt false zurück, damit der
-- Aufrufer früh exiten kann:
--   if not Validate.IsInt(x) then return Validate.Reject(player, "MyHandler", "x not int") end
-- Vorteil: einheitliches Log-Format quer durch alle Module.
function M.Reject(player, handler, reason)
    local name = "?"
    if type(player) == "userdata" and player.GetName then
        name = player:GetName()
    elseif type(player) == "string" then
        name = player
    end
    print(string.format(
        "[Validate] reject handler=%s player=%s reason=%s",
        tostring(handler), tostring(name), tostring(reason)
    ))
    return false
end

-- ---------------------------------------------------------------------------
-- Self-Test (manuell ausführen, kein automatischer Run beim Load)
-- ---------------------------------------------------------------------------

function M.SelfTest()
    assert(M.IsInt(0))
    assert(M.IsInt(1))
    assert(M.IsInt(-1))
    assert(M.IsInt(2147483647))
    assert(not M.IsInt(1.5))
    assert(not M.IsInt("1"))
    assert(not M.IsInt(0/0))
    assert(not M.IsInt(math.huge))
    assert(not M.IsInt(nil))

    assert(M.IsIntInRange(5, 1, 10))
    assert(not M.IsIntInRange(0, 1, 10))
    assert(not M.IsIntInRange(11, 1, 10))

    assert(M.IsPositiveInt(1))
    assert(not M.IsPositiveInt(0))
    assert(M.IsPositiveInt(100, 100))
    assert(not M.IsPositiveInt(101, 100))

    assert(M.IsStringMaxLen("hello", 10))
    assert(not M.IsStringMaxLen("hellohellohello", 10))
    assert(not M.IsStringMaxLen(42, 10))

    local set = M.ToSet({0, 1, 2})
    assert(M.IsInWhitelist(0, set))
    assert(M.IsInWhitelist(2, set))
    assert(not M.IsInWhitelist(3, set))
    assert(not M.IsInWhitelist("0", set))

    assert(M.CoerceInt(5) == 5)
    assert(M.CoerceInt("5") == 5)
    assert(M.CoerceInt("abc", -1) == -1)
    assert(M.CoerceInt(1.5, -1) == -1)
    assert(M.CoerceInt(nil, -1) == -1)

    assert(M.CoerceIntInRange(5, 1, 10) == 5)
    assert(M.CoerceIntInRange(15, 1, 10, -1) == -1)
    assert(M.CoerceIntInRange("3", 1, 10) == 3)

    assert(M.SqlEscape("foo'bar") == "foo''bar")
    assert(M.SqlEscape([[a\b]]) == [[a\\b]])

    print("[Validate] SelfTest OK")
    return true
end

return M
