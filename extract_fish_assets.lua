-- ==============================================================================
-- FISH IT! ROBLOX - DEEP FISH ASSET & IMAGE EXTRACTOR
-- Khusus Auto Skor Galatama - Mengambil Asset ID Gambar Ikan Langsung dari Game
-- ==============================================================================

local cloneref = cloneref or function(o) return o end
local Players = cloneref(game:GetService("Players"))
local HttpService = cloneref(game:GetService("HttpService"))
local ReplicatedStorage = cloneref(game:GetService("ReplicatedStorage"))
local StarterGui = cloneref(game:GetService("StarterGui"))
local Workspace = cloneref(game:GetService("Workspace"))
local LocalPlayer = Players.LocalPlayer

local httpRequest = (syn and syn.request) or (http and http.request) or http_request or request
local setclipboard = setclipboard or toclipboard or set_clipboard
local writefile = writefile or write_file

-- Notifikasi Mulai di Layar Roblox
pcall(function()
    StarterGui:SetCore("SendNotification", {
        Title = "🔍 Fish It Extractor",
        Text = "Memulai ekstraksi gambar ikan langsung dari memori & UI game...",
        Duration = 5
    })
end)

print("=============================================================")
print("🎣 FISH IT! - DIRECT SOURCE ASSET & IMAGE EXTRACTOR")
print("=============================================================")

-- ------------------------------------------------------------------------------
-- 1. DAFTAR 70 IKAN TURNAMEN TARGET (FORGOTTEN, SECRET, MITOS, LEGEND)
-- ------------------------------------------------------------------------------
local TARGET_FISH_DB = {
    -- FORGOTTEN (4)
    ["sea eater"] = {name = "Sea Eater", tier = "forgotten"},
    ["trench warden"] = {name = "Trench Warden", tier = "forgotten"},
    ["forgotten hydra"] = {name = "Forgotten Hydra", tier = "forgotten"},
    ["frostbite leviathan"] = {name = "Frostbite Leviathan", tier = "forgotten"},

    -- SECRET (36)
    ["crystal crab"] = {name = "Crystal Crab", tier = "secret"},
    ["orca"] = {name = "Orca", tier = "secret"},
    ["worm fish"] = {name = "Worm Fish", tier = "secret"},
    ["ghost shark"] = {name = "Ghost Shark", tier = "secret"},
    ["megalodon"] = {name = "Megalodon", tier = "secret"},
    ["blob shark"] = {name = "Blob Shark", tier = "secret"},
    ["lochness monster"] = {name = "Lochness Monster", tier = "secret"},
    ["monster shark"] = {name = "Monster Shark", tier = "secret"},
    ["eerie shark"] = {name = "Eerie Shark", tier = "secret"},
    ["armored shark"] = {name = "Armored Shark", tier = "secret"},
    ["scare"] = {name = "Scare", tier = "secret"},
    ["kraken"] = {name = "Kraken", tier = "secret"},
    ["giant squid"] = {name = "Giant Squid", tier = "secret"},
    ["queen crab"] = {name = "Queen Crab", tier = "secret"},
    ["king crab"] = {name = "King Crab", tier = "secret"},
    ["robot kraken"] = {name = "Robot Kraken", tier = "secret"},
    ["panther eel"] = {name = "Panther Eel", tier = "secret"},
    ["grand maja"] = {name = "Grand Maja", tier = "secret"},
    ["ancient lochness monster"] = {name = "Ancient Lochness Monster", tier = "secret"},
    ["gladiator shark"] = {name = "Gladiator Shark", tier = "secret"},
    ["mosasaur shark"] = {name = "Mosasaur Shark", tier = "secret"},
    ["talon serpent"] = {name = "Talon Serpent", tier = "secret"},
    ["ancient relic crocodile"] = {name = "Ancient Relic Crocodile", tier = "secret"},
    ["big king jelly"] = {name = "Big King Jelly", tier = "secret"},
    ["great whale"] = {name = "Great Whale", tier = "secret"},
    ["frostborn shark"] = {name = "Frostborn Shark", tier = "secret"},
    ["blood shark"] = {name = "Blood Shark", tier = "secret"},
    ["giant sunfish"] = {name = "Giant Sunfish", tier = "secret"},
    ["golem shark"] = {name = "Golem Shark", tier = "secret"},
    ["sinking titan"] = {name = "Sinking Titan", tier = "secret"},
    ["oarfish"] = {name = "Oarfish", tier = "secret"},
    ["retro maja"] = {name = "Retro Maja", tier = "secret"},
    ["hacker shark"] = {name = "Hacker Shark", tier = "secret"},

    -- MITOS (12)
    ["dotted stingray"] = {name = "Dotted Stingray", tier = "mitos"},
    ["manta ray"] = {name = "Manta Ray", tier = "mitos"},
    ["hammerhead shark"] = {name = "Hammerhead Shark", tier = "mitos"},
    ["shark"] = {name = "Shark", tier = "mitos"},
    ["loggerhead turtle"] = {name = "Loggerhead Turtle", tier = "mitos"},
    ["prismy seahorse"] = {name = "Prismy Seahorse", tier = "mitos"},
    ["blueflame ray"] = {name = "Blueflame Ray", tier = "mitos"},
    ["magma shark"] = {name = "Magma Shark", tier = "mitos"},
    ["hawks turtle"] = {name = "Hawks Turtle", tier = "mitos"},
    ["abyss seahorse"] = {name = "Abyss Seahorse", tier = "mitos"},
    ["thresher shark"] = {name = "Thresher Shark", tier = "mitos"},
    ["blob fish"] = {name = "Blob Fish", tier = "mitos"},

    -- LEGEND (18)
    ["lined cardinal fish"] = {name = "Lined Cardinal Fish", tier = "legend"},
    ["yellowfin tuna"] = {name = "Yellowfin Tuna", tier = "legend"},
    ["lake sturgeon"] = {name = "Lake Sturgeon", tier = "legend"},
    ["chrome tuna"] = {name = "Chrome Tuna", tier = "legend"},
    ["bumblebee grouper"] = {name = "Bumblebee Grouper", tier = "legend"},
    ["lobster"] = {name = "Lobster", tier = "legend"},
    ["lavafin tuna"] = {name = "Lavafin Tuna", tier = "legend"},
    ["starjam tang"] = {name = "Starjam Tang", tier = "legend"},
    ["greenbee grouper"] = {name = "Greenbee Grouper", tier = "legend"},
    ["blue lobster"] = {name = "Blue Lobster", tier = "legend"},
    ["enchanted angelfish"] = {name = "Enchanted Angelfish", tier = "legend"},
    ["magic tang"] = {name = "Magic Tang", tier = "legend"},
    ["temple spokes tuna"] = {name = "Temple Spokes Tuna", tier = "legend"},
    ["manoai statue fish"] = {name = "Manoai Statue Fish", tier = "legend"},
    ["ruby"] = {name = "Ruby", tier = "legend"},
    ["axolotl"] = {name = "Axolotl", tier = "legend"},
    ["synodontis"] = {name = "Synodontis", tier = "legend"},
    ["deep sea crab"] = {name = "Deep Sea Crab", tier = "legend"}
}

local extractedAssets = {}

-- Fungsi Pembersih ID Aset Roblox -> URL PNG Web CDN
local function cleanAndFormatAsset(rawAsset)
    if not rawAsset or type(rawAsset) ~= "string" and type(rawAsset) ~= "number" then return nil end
    local str = tostring(rawAsset)
    local assetId = string.match(str, "%d+")
    if not assetId or #assetId < 4 then return nil end
    
    return {
        asset_id = assetId,
        rbx_url = "rbxassetid://" .. assetId,
        web_png_url = string.format("https://www.roblox.com/asset-thumbnail/image?assetId=%s&width=420&height=420&format=png", assetId),
        cdn_delivery = string.format("https://assetdelivery.roblox.com/v1/asset/?id=%s", assetId)
    }
end

-- Fungsi Pengecek Nama Ikan
local function findMatchingFish(testString)
    if not testString or type(testString) ~= "string" then return nil end
    local clean = string.lower(testString):gsub("[^%w%s]", ""):gsub("%s+", " "):match("^%s*(.-)%s*$")
    if not clean or #clean == 0 then return nil end

    -- 1. Exact match di target
    if TARGET_FISH_DB[clean] then
        return TARGET_FISH_DB[clean]
    end

    -- 2. Contains match
    for fKey, fInfo in pairs(TARGET_FISH_DB) do
        if clean == fKey or string.find(clean, fKey, 1, true) or string.find(fKey, clean, 1, true) then
            return fInfo
        end
    end
    return nil
end

-- Simpan Aset Hasil Temuan
local function registerExtractedFish(fishName, tier, assetRaw, sourceDesc)
    local assetObj = cleanAndFormatAsset(assetRaw)
    if not assetObj then return end

    local cleanKey = string.lower(fishName):gsub("[^%w]", "")
    if not extractedAssets[cleanKey] then
        extractedAssets[cleanKey] = {
            fish_name = fishName,
            tier = tier or "unknown",
            asset_id = assetObj.asset_id,
            rbx_url = assetObj.rbx_url,
            web_png_url = assetObj.web_png_url,
            source = sourceDesc or "Game Source"
        }
        print(string.format("  [+] DITEMUKAN: %s [%s] -> ID: %s (%s)", fishName, tier:upper(), assetObj.asset_id, sourceDesc))
    end
end

-- ------------------------------------------------------------------------------
-- VECTOR 1: PEMINDAIAN MEMORI GC (GARBAGE COLLECTOR / DATA TABLES)
-- ------------------------------------------------------------------------------
print("\n[VECTOR 1] Memindai Data Tables internal game (GC Scanner)...")
local getgcFunc = getgc or (debug and debug.getgc)
if getgcFunc then
    pcall(function()
        local objects = getgcFunc(true)
        for _, obj in ipairs(objects) do
            if type(obj) == "table" then
                -- Cek apakah tabel mendefinisikan item/fish
                local possibleName = obj.Name or obj.name or obj.Title or obj.title or obj.FishName or obj.fish or obj.ItemName
                local possibleIcon = obj.Icon or obj.icon or obj.Image or obj.image or obj.Texture or obj.texture or obj.AssetId or obj.Thumbnail
                local possibleTier = obj.Tier or obj.tier or obj.Rarity or obj.rarity

                if possibleName and possibleIcon then
                    local match = findMatchingFish(tostring(possibleName))
                    if match then
                        registerExtractedFish(match.name, match.tier, possibleIcon, "GC Data Table")
                    end
                end

                -- Cek format dictionary [FishName] = { Icon = ... }
                for k, v in pairs(obj) do
                    if type(k) == "string" and type(v) == "table" then
                        local match = findMatchingFish(k)
                        if match then
                            local icon = v.Icon or v.icon or v.Image or v.image or v.Texture or v.texture or v.Thumbnail
                            if icon then
                                registerExtractedFish(match.name, match.tier, icon, "GC Dict Table [" .. k .. "]")
                            end
                        end
                    end
                end
            end
        end
    end)
else
    print("  [!] getgc tidak didukung executor ini, beralih ke Vector 2 & 3.")
end

-- ------------------------------------------------------------------------------
-- VECTOR 2: PEMINDAIAN MODULE SCRIPTS DI REPLICATED STORAGE
-- ------------------------------------------------------------------------------
print("\n[VECTOR 2] Memindai ReplicatedStorage Modules & Data...")
pcall(function()
    local allDesc = ReplicatedStorage:GetDescendants()
    for _, item in ipairs(allDesc) do
        -- A. Cek ModuleScript yang mungkin berisi config ikan
        if item:IsA("ModuleScript") then
            local itemName = string.lower(item.Name)
            if string.find(itemName, "fish") or string.find(itemName, "item") or string.find(itemName, "data") or string.find(itemName, "catalog") or string.find(itemName, "index") or string.find(itemName, "book") then
                pcall(function()
                    local required = require(item)
                    if type(required) == "table" then
                        for k, v in pairs(required) do
                            if type(v) == "table" then
                                local nameVal = v.Name or v.name or v.Title or k
                                local iconVal = v.Icon or v.icon or v.Image or v.image or v.Texture or v.Thumbnail
                                if nameVal and iconVal then
                                    local match = findMatchingFish(tostring(nameVal))
                                    if match then
                                        registerExtractedFish(match.name, match.tier, iconVal, "Module: " .. item.Name)
                                    end
                                end
                            end
                        end
                    end
                end)
            end
        end

        -- B. Cek Model / ValueObject / Attributes
        local match = findMatchingFish(item.Name)
        if match then
            local attrIcon = item:GetAttribute("Icon") or item:GetAttribute("Image") or item:GetAttribute("Texture") or item:GetAttribute("AssetId")
            if attrIcon then
                registerExtractedFish(match.name, match.tier, attrIcon, "RS Attribute: " .. item.Name)
            end
            
            -- Cek apakah ada Decal / Texture / MeshPart di dalamnya
            local decal = item:FindFirstChildWhichIsA("Decal", true) or item:FindFirstChildWhichIsA("Texture", true)
            if decal and decal.Texture then
                registerExtractedFish(match.name, match.tier, decal.Texture, "RS Model Decal: " .. item.Name)
            end
            local mesh = item:FindFirstChildWhichIsA("SpecialMesh", true) or item:FindFirstChildWhichIsA("MeshPart", true)
            if mesh then
                local tex = (mesh:IsA("SpecialMesh") and mesh.TextureId) or (mesh:IsA("MeshPart") and mesh.TextureID)
                if tex and #tex > 5 then
                    registerExtractedFish(match.name, match.tier, tex, "RS Mesh Texture: " .. item.Name)
                end
            end
        end
    end
end)

-- ------------------------------------------------------------------------------
-- VECTOR 3: PEMINDAIAN PLAYERGUI (FISH CATALOG / INDEX / JOURNAL / INVENTORY)
-- ------------------------------------------------------------------------------
print("\n[VECTOR 3] Memindai PlayerGui (Catalog, Index & Inventory)...")
pcall(function()
    local playerGui = LocalPlayer:FindFirstChild("PlayerGui")
    if playerGui then
        local allGui = playerGui:GetDescendants()
        for _, elem in ipairs(allGui) do
            if elem:IsA("ImageLabel") or elem:IsA("ImageButton") then
                local img = elem.Image
                if img and #img > 5 then
                    -- Cari teks nama ikan dari elemen ini, parent, atau sibling TextLabel
                    local matchedFish = findMatchingFish(elem.Name)
                    if not matchedFish and elem.Parent then
                        matchedFish = findMatchingFish(elem.Parent.Name)
                    end
                    if not matchedFish and elem.Parent then
                        -- Cari TextLabel di container yang sama
                        for _, sibling in ipairs(elem.Parent:GetChildren()) do
                            if sibling:IsA("TextLabel") and #sibling.Text > 0 then
                                matchedFish = findMatchingFish(sibling.Text)
                                if matchedFish then break end
                            end
                        end
                    end

                    if matchedFish then
                        registerExtractedFish(matchedFish.name, matchedFish.tier, img, "PlayerGui: " .. elem:GetFullName())
                    end
                end
            end
        end
    end
end)

-- ------------------------------------------------------------------------------
-- RINGKASAN HASIL & EKSPOR DATA
-- ------------------------------------------------------------------------------
local countFound = 0
for _ in pairs(extractedAssets) do countFound = countFound + 1 end

print("\n=============================================================")
print(string.format("✅ EKSTRAKSI SELESAI: DITEMUKAN %d ASSET GAMBAR IKAN!", countFound))
print("=============================================================")

local jsonOutput = HttpService:JSONEncode(extractedAssets)

-- 1. SALIN KE CLIPBOARD WINDOWS (Bisa langsung Ctrl + V)
if setclipboard then
    setclipboard(jsonOutput)
    print("📋 [OK] Seluruh data JSON berhasil DISALIN KE CLIPBOARD Windows Anda!")
end

-- 2. SIMPAN KE FILE WORKSPACE EXECUTOR
if writefile then
    pcall(function()
        writefile("fishit_assets_dump.json", jsonOutput)
        print("💾 [OK] File tersimpan di folder executor: workspace/fishit_assets_dump.json")
    end)
end

-- 3. KIRIM OTOMATIS KE MASTER ENGINE AUTO SKOR (JIKA RUNNING)
if httpRequest then
    task.spawn(function()
        pcall(function()
            local res = httpRequest({
                Url = "http://127.0.0.1:5000/api/import_fish_assets",
                Method = "POST",
                Headers = {["Content-Type"] = "application/json"},
                Timeout = 5,
                Body = jsonOutput
            })
            if res and (res.StatusCode == 200 or res.StatusCode == 201) then
                print("⚡ [OK] Berhasil disinkronkan langsung ke MasterAutoSkor_Lokal.exe di PC Anda!")
            end
        end)
    end)
end

-- Tampilkan Notifikasi Akhir di Layar Roblox
pcall(function()
    StarterGui:SetCore("SendNotification", {
        Title = "🎉 Ekstraksi Selesai!",
        Text = string.format("Ditemukan %d gambar ikan asli. Data disalin ke Clipboard!", countFound),
        Duration = 8
    })
end)

return extractedAssets
