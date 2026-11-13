-- ============================================================
-- FISH IT UNIFIED BRIDGE - HIGH PERFORMANCE EDITION (ZERO LAG)
-- Dioptimalkan khusus untuk Turnamen Auto Skor Galatama
-- ============================================================
local cloneref = cloneref or function(o) return o end
local cclosure = newcclosure or function(f) return f end

local Players = cloneref(game:GetService("Players"))
local HttpService = cloneref(game:GetService("HttpService"))
local TextChatService = cloneref(game:GetService("TextChatService"))
local ReplicatedStorage = cloneref(game:GetService("ReplicatedStorage"))
local LocalPlayer = Players.LocalPlayer

local httpRequest = (syn and syn.request) or (http and http.request) or http_request or request
if not httpRequest then
    warn("⚠️ [FISH IT BRIDGE] Executor Anda tidak mendukung HTTP Request atau permission belum aktif!")
end

-- ============================================================
-- KONFIGURASI TARGET SERVER & ANTI-LAG (PENTING)
-- ============================================================
-- Pilihan TARGET_MODE:
-- "AUTO"     : Otomatis! Jika MasterAutoSkor_Lokal.exe aktif di PC, pakai Localhost (0ms). Jika tidak, pakai Cloud Vercel.
-- "LOCAL"    : 100% Offline di PC Anda (http://127.0.0.1:5000) via MasterAutoSkor_Lokal.exe - Tercepat, super enteng
-- "CLOUD"    : Online via Vercel (https://auto-skor.vercel.app) via MasterAutoSkor_Online.exe
local TARGET_MODE = "AUTO"

local ENABLE_ANTI_LAG_BOOST  = true   -- TRUE: Mengoptimalkan FPS Roblox (Shadows & effects off)
local ENABLE_WEATHER_SCANNER = false  -- Set TRUE jika ingin deteksi cuaca/potion (Default FALSE agar 100% BEBAS LAG)
local ENABLE_PLAYER_PRESENCE = false  -- Set TRUE jika butuh tracking join/leave (Default FALSE agar koneksi ringan)
local HTTP_TIMEOUT_SEC       = 4      -- Batas waktu timeout 4 detik agar memory Roblox tidak tertahan

local LOCAL_URL = "http://127.0.0.1:5000"
local CLOUD_URL = "https://auto-skor.vercel.app"
local BASE_URL = CLOUD_URL

if TARGET_MODE == "LOCAL" then
    BASE_URL = LOCAL_URL
elseif TARGET_MODE == "CLOUD" then
    BASE_URL = CLOUD_URL
elseif TARGET_MODE == "AUTO" then
    -- Deteksi otomatis apakah server Python lokal MasterAutoSkor.exe sedang aktif
    pcall(function()
        if httpRequest then
            local check = httpRequest({
                Url = LOCAL_URL .. "/api/catch",
                Method = "GET",
                Timeout = 1.0
            })
            if check and check.StatusCode == 200 then
                BASE_URL = LOCAL_URL
            end
        end
    end)
end

local CATCH_URL = BASE_URL .. "/api/catch"
local PLAYER_EVENT_URL = BASE_URL .. "/api/player-event"
local WEATHER_URL = BASE_URL .. "/api/weather"

print("============================================================")
print("  🎣 AUTO SKOR GALATAMA - FISH IT BRIDGE (HIGH PERFORMANCE) ")
print("  🌐 Target Server: " .. BASE_URL .. " [" .. TARGET_MODE .. "]")
print("  🚀 Anti-Lag Boost: " .. (ENABLE_ANTI_LAG_BOOST and "AKTIF (60+ FPS)" or "NONAKTIF"))
print("  ⚡ Status: SINKRON OTOMATIS KE MASTER APP & TIKTOK STUDIO ")
print("============================================================")

-- ============================================================
-- 0. FITUR ANTI-LAG & FPS BOOSTER ROBLOX
-- ============================================================
if ENABLE_ANTI_LAG_BOOST then
    task.spawn(function()
        pcall(function()
            local Lighting = cloneref(game:GetService("Lighting"))
            Lighting.GlobalShadows = false
            Lighting.FogEnd = 9e9
            
            for _, v in ipairs(Lighting:GetChildren()) do
                if v:IsA("BlurEffect") or v:IsA("SunRaysEffect") or v:IsA("DepthOfFieldEffect") or v:IsA("BloomEffect") then
                    v.Enabled = false
                end
            end

            local terrain = workspace:FindFirstChildOfClass("Terrain")
            if terrain then
                terrain.WaterWaveSize = 0
                terrain.WaterWaveSpeed = 0
                terrain.WaterReflectance = 0
            end

            print("🚀 [ANTI-LAG BOOSTER] Grafik Roblox berhasil diringankan untuk turnamen!")
        end)
    end)
end

-- Pembersih memori Lua berkala (mencegah memory leak di executor)
task.spawn(function()
    while true do
        task.wait(60)
        collectgarbage("collect")
    end
end)

local env = getgenv and getgenv()
local CLEANUP_KEY = "_FishItUnifiedBridge"

if env and env[CLEANUP_KEY] then
    pcall(env[CLEANUP_KEY])
end

local activeConnections = {}

-- ============================================================
-- 1. DAFTAR VARIAN / MUTASI IKAN RESMI
-- ============================================================
local KNOWN_VARIANTS = {
    "shiny", "big", "giant",
    "galaxy", "sandy", "albino", "ghost", "haunted",
    "midnight", "corrupt", "radioactive", "holographic", "gemstone",
    "binary", "gold", "frozen", "glitch", "equinox",
    "disco", "elemental", "solar", "bloodmoon", "festive", "lightning",
    "fairy dust", "color burn", "crystalized", "moon fragment", "8-bit", "stone", "duskbreaker"
}
table.sort(KNOWN_VARIANTS, function(a, b) return #a > #b end)

-- ============================================================
-- 2. DETEKSI TIER IKAN & PEMISAH VARIAN
-- ============================================================
local function determineTier(rawText, cleanText)
    local hex = rawText:match('color=["\']#?(%x%x%x%x%x%x)["\']')
    if hex then
        local r = tonumber(hex:sub(1, 2), 16) or 0
        local g = tonumber(hex:sub(3, 4), 16) or 0
        local b = tonumber(hex:sub(5, 6), 16) or 0

        if (g > 170 and (b > 110 or r < 130)) or (r > 110 and b > 140 and g < 110) then
            return "SECRET"
        elseif r > 200 and g < 90 then
            return "MYTHIC"
        elseif r > 190 and g > 110 and b < 90 then
            return "LEGENDARY"
        end
    end

    local chanceStr = cleanText:match("with%s+a%s+1%s+in%s+([%w%.]+)%s+chance")
    if chanceStr then
        local upper = string.upper(chanceStr)
        local num = tonumber(string.match(upper, "[%d%.]+")) or 0

        if string.find(upper, "M") or (string.find(upper, "K") and num >= 400) then
            return "SECRET"
        elseif string.find(upper, "K") and num >= 50 then
            return "MYTHIC"
        elseif string.find(upper, "K") and num >= 5 then
            return "LEGENDARY"
        elseif string.find(upper, "K") and num >= 1 then
            return "RARE"
        end
    end

    return "NORMAL"
end

local function splitFishAndVariant(fullFishName)
    local detectedVariants = {}
    local cleanFish = fullFishName

    for _, v in ipairs(KNOWN_VARIANTS) do
        local target = string.lower(v)
        local escapedTarget = string.gsub(target, "([%^%$%(%)%%%.%[%]%*%+%-%?])", "%%%1")
        while true do
            local lowerClean = string.lower(cleanFish)
            local s, e = string.find(lowerClean, "%f[%w]" .. escapedTarget .. "%f[%W]")
            if not s then
                s, e = string.find(lowerClean, target, 1, true)
                if s then
                    local charBefore = s > 1 and string.sub(lowerClean, s - 1, s - 1) or " "
                    local charAfter = e < #lowerClean and string.sub(lowerClean, e + 1, e + 1) or " "
                    if string.find(charBefore, "%w") or string.find(charAfter, "%w") then
                        s = nil
                    end
                end
            end

            if s and e then
                local originalText = string.sub(cleanFish, s, e)
                table.insert(detectedVariants, originalText)
                cleanFish = string.sub(cleanFish, 1, s - 1) .. " " .. string.sub(cleanFish, e + 1)
            else
                break
            end
        end
    end

    cleanFish = string.gsub(cleanFish, "%s+", " ")
    cleanFish = string.match(cleanFish, "^%s*(.-)%s*$") or fullFishName
    local variantResult = #detectedVariants > 0 and table.concat(detectedVariants, ", ") or "None"
    return cleanFish, variantResult
end

-- ============================================================
-- 3. FUNGSI PENGIRIMAN DATA NON-BLOCKING DENGAN DEDUPLIKASI
-- ============================================================
local processedCatchHash = {}

local function sendToPython(player, fish, variant, tier)
    if not httpRequest then return end

    -- Cegah pengiriman dobel jika event chat direplikasi berulang kali
    local catchKey = string.format("%s_%s_%s_%s", tostring(player), tostring(fish), tostring(variant), tostring(tier))
    local now = tick()
    if processedCatchHash[catchKey] and (now - processedCatchHash[catchKey]) < 1.5 then
        return
    end
    processedCatchHash[catchKey] = now

    task.spawn(function()
        pcall(function()
            local res = httpRequest({
                Url = CATCH_URL,
                Method = "POST",
                Headers = {["Content-Type"] = "application/json"},
                Timeout = HTTP_TIMEOUT_SEC,
                Body = HttpService:JSONEncode({
                    player = player,
                    fish = fish,
                    variant = variant,
                    tier = tier,
                    jobid = tostring(game.JobId)
                })
            })
            if res and (res.StatusCode == 200 or res.StatusCode == 201) then
                print(string.format("🎣 [AUTO SKOR SYNC] Poin Masuk: [%s] %s (%s)", player, fish, tier))
            end
        end)
    end)
end

local function sendPlayerEvent(playerName, eventType)
    if not httpRequest or not ENABLE_PLAYER_PRESENCE then return end

    task.spawn(function()
        pcall(function()
            httpRequest({
                Url = PLAYER_EVENT_URL,
                Method = "POST",
                Headers = {["Content-Type"] = "application/json"},
                Timeout = HTTP_TIMEOUT_SEC,
                Body = HttpService:JSONEncode({
                    player = playerName,
                    event = eventType
                })
            })
        end)
    end)
end

local function sendWeatherToPython(identity, eventName)
    if not httpRequest or not ENABLE_WEATHER_SCANNER then return end

    local username = identity and identity.username or "Server Global"
    local displayName = identity and identity.displayName or "Global Event"
    local userId = identity and identity.userId or 0

    local data = {
        event = eventName,
        weather = eventName,
        player = username,
        username = username,
        nickname = displayName,
        userid = userId,
        jobid = tostring(game.JobId),
        timestamp = os.time()
    }

    task.spawn(function()
        pcall(function()
            httpRequest({
                Url = WEATHER_URL,
                Method = "POST",
                Headers = {["Content-Type"] = "application/json"},
                Timeout = HTTP_TIMEOUT_SEC,
                Body = HttpService:JSONEncode(data)
            })
        end)
    end)
end

local function getPlayerIdentity(identifier)
    local targetPlayer = nil
    pcall(function()
        if typeof(identifier) == "Instance" then
            if identifier:IsA("Player") then
                targetPlayer = identifier
            else
                local character = identifier:IsA("Model") and identifier or identifier:FindFirstAncestorWhichIsA("Model")
                if character then
                    targetPlayer = Players:GetPlayerFromCharacter(character)
                end
            end
        elseif type(identifier) == "string" then
            targetPlayer = Players:FindFirstChild(identifier)
        elseif type(identifier) == "number" then
            targetPlayer = Players:GetPlayerByUserId(identifier)
        end
    end)

    if targetPlayer then
        return {
            username = targetPlayer.Name,
            displayName = targetPlayer.DisplayName,
            userId = targetPlayer.UserId
        }
    end
    return nil
end

-- ============================================================
-- 4. PARSER CHAT TANGKAPAN IKAN (SANGAT RINGAN, 0 CPU DELAY)
-- ============================================================
local function processChatMessage(rawText)
    if not rawText or type(rawText) ~= "string" then return end
    -- Cek kata kunci awal agar tidak memproses pesan obrolan biasa
    if not string.find(rawText:lower(), "obtained") then return end

    local clean = string.gsub(rawText, "<[^>]+>", "")
    clean = string.gsub(clean, "^%[.-%]:%s*", "")

    local targetPlayerObj = Players.LocalPlayer
    local playerName = targetPlayerObj and targetPlayerObj.Name or "Unknown"

    local extractedPlayer, rawFishName = string.match(clean, "^(.-)%s+obtained%s+an?%s+(.-)%s*%b()")
    if not extractedPlayer then
        extractedPlayer, rawFishName = string.match(clean, "^(.-)%s+obtained%s+an?%s+(.-)%s+with")
    end
    if not extractedPlayer then
        extractedPlayer, rawFishName = string.match(clean, "^(.-)%s+obtained%s+an?%s+(.-)$")
    end

    if extractedPlayer then
        local foundPlr = Players:FindFirstChild(string.match(extractedPlayer, "^%s*(.-)%s*$"))
        if foundPlr then
            playerName = foundPlr.Name
        else
            playerName = string.match(extractedPlayer, "^%s*(.-)%s*$")
        end
    end

    if not rawFishName then return end

    local baseFish, variant = splitFishAndVariant(rawFishName)
    local tier = determineTier(rawText, clean)

    print(string.format("🐟 [TANGKAPAN] %s -> %s [%s | %s]", playerName, baseFish, tier, variant))
    sendToPython(playerName, baseFish, variant, tier)
end

-- ============================================================
-- 5. SCANNER POTION & CUACA (HANYA AKTIF JIKA DIPERLUKAN)
-- ============================================================
if ENABLE_WEATHER_SCANNER then
    local lastAuroraTriggerTime = 0
    local AURORA_COOLDOWN_DURATION = 1800
    local activeSessions = {}
    local SESSION_COOLDOWN = 5

    pcall(function()
        for _, desc in ipairs(ReplicatedStorage:GetDescendants()) do
            if desc:IsA("RemoteEvent") then
                local success, conn = pcall(function()
                    return desc.OnClientEvent:Connect(function(...)
                        local args = {...}
                        local foundIdentity = nil
                        local detectedName = nil
                        local isValidAction = false

                        for _, arg in ipairs(args) do
                            local argType = typeof(arg)
                            if argType == "string" then
                                local s = arg:lower()
                                if s ~= "equippedpotions" and s ~= "potions" and not s:match("^potions/") then
                                    if s:find("potion") or s:find("borealis") or s:find("meteor") or s:find("shower") then
                                        detectedName = arg
                                        if s:find("aurora") or s:find("borealis") then
                                            detectedName = "Aurora Borealis"
                                        elseif s:find("meteor") or s:find("shower") then
                                            detectedName = "Meteor Shower"
                                        end
                                        isValidAction = true
                                    end
                                end
                            elseif argType == "Instance" then
                                local iden = getPlayerIdentity(arg)
                                if iden then
                                    foundIdentity = iden
                                end
                            end
                        end

                        if isValidAction and detectedName then
                            local now = os.time()
                            if detectedName == "Aurora Borealis" then
                                if (now - lastAuroraTriggerTime) < AURORA_COOLDOWN_DURATION then
                                    return
                                end
                                lastAuroraTriggerTime = now
                            end

                            local sessionKey = tostring(detectedName) .. (foundIdentity and foundIdentity.username or "global")
                            if activeSessions[sessionKey] and (now - activeSessions[sessionKey]) < SESSION_COOLDOWN then
                                return
                            end
                            activeSessions[sessionKey] = now

                            if foundIdentity then
                                sendWeatherToPython(foundIdentity, tostring(detectedName))
                            else
                                sendWeatherToPython(nil, tostring(detectedName))
                            end
                        end
                    end)
                end)
                if success and conn then
                    table.insert(activeConnections, conn)
                end
            end
        end
    end)
end

-- ============================================================
-- 6. HOOK CHAT EVENT (SANGAT CEPAT & AMAN)
-- ============================================================
pcall(function()
    if TextChatService.ChatVersion == Enum.ChatVersion.TextChatService then
        local c = TextChatService.MessageReceived:Connect(cclosure(function(msg)
            if msg and msg.Text then processChatMessage(msg.Text) end
        end))
        table.insert(activeConnections, c)
    else
        local legacy = ReplicatedStorage:FindFirstChild("DefaultChatSystemChatEvents")
        if legacy then
            local onMsg = legacy:FindFirstChild("OnMessageDoneFiltering")
            if onMsg then
                local c = onMsg.OnClientEvent:Connect(cclosure(function(data)
                    if data and data.Message then processChatMessage(data.Message) end
                end))
                table.insert(activeConnections, c)
            end
        end
    end
end)

-- Presence listener (hanya jika diaktifkan)
if ENABLE_PLAYER_PRESENCE then
    local cAdd = Players.PlayerAdded:Connect(cclosure(function(player)
        sendPlayerEvent(player.Name, "JOIN")
    end))
    table.insert(activeConnections, cAdd)

    local cRem = Players.PlayerRemoving:Connect(cclosure(function(player)
        sendPlayerEvent(player.Name, "LEAVE")
    end))
    table.insert(activeConnections, cRem)
end

-- ============================================================
-- 7. CLEANUP HANDLER (PREVENT DUPLICATE THREADS)
-- ============================================================
local function stopMonitor()
    for _, conn in ipairs(activeConnections) do
        pcall(function() conn:Disconnect() end)
    end
    table.clear(activeConnections)
    print("🧹 [FISH IT BRIDGE] Handler sebelumnya dibersihkan dengan aman.")
end

if env then
    env[CLEANUP_KEY] = stopMonitor
end
