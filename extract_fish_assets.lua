-- ==============================================================================
-- FISH IT! ROBLOX - DEEP FISH ASSET EXTRACTOR (FOLDER INSPECTION MODE)
-- Ekstraksi gambar ikan dari game langsung ke folder Windows Explorer untuk dilihat dulu
-- ==============================================================================

local cloneref = cloneref or function(o) return o end
local Players = cloneref(game:GetService("Players"))
local HttpService = cloneref(game:GetService("HttpService"))
local ReplicatedStorage = cloneref(game:GetService("ReplicatedStorage"))
local StarterGui = cloneref(game:GetService("StarterGui"))
local LocalPlayer = Players.LocalPlayer

local httpRequest = (syn and syn.request) or (http and http.request) or http_request or request
local setclipboard = setclipboard or toclipboard or set_clipboard
local writefile = writefile or write_file

-- Notifikasi Mulai di Layar Roblox
pcall(function()
    StarterGui:SetCore("SendNotification", {
        Title = "🔍 Fish It Extractor",
        Text = "Memindai gambar ikan dari game...",
        Duration = 3
    })
end)

print("=============================================================")
print("🎣 FISH IT! - DIRECT ASSET EXTRACTOR (FOLDER MODE)")
print("=============================================================")

-- ------------------------------------------------------------------------------
-- 1. DAFTAR 70 IKAN TURNAMEN TARGET
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

local function cleanAndFormatAsset(rawAsset)
    if not rawAsset or (type(rawAsset) ~= "string" and type(rawAsset) ~= "number") then return nil end
    local str = tostring(rawAsset)
    local assetId = string.match(str, "%d+")
    if not assetId or #assetId < 4 then return nil end
    
    return {
        asset_id = assetId,
        rbx_url = "rbxassetid://" .. assetId,
        web_png_url = string.format("https://www.roblox.com/asset-thumbnail/image?assetId=%s&width=420&height=420&format=png", assetId)
    }
end

local function findMatchingFish(testString)
    if not testString or type(testString) ~= "string" then return nil end
    local clean = string.lower(testString):gsub("[^%w%s]", ""):gsub("%s+", " "):match("^%s*(.-)%s*$")
    if not clean or #clean == 0 then return nil end

    if TARGET_FISH_DB[clean] then
        return TARGET_FISH_DB[clean]
    end

    for fKey, fInfo in pairs(TARGET_FISH_DB) do
        if clean == fKey or string.find(clean, fKey, 1, true) or string.find(fKey, clean, 1, true) then
            return fInfo
        end
    end
    return nil
end

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
        print(string.format("  [+] %s [%s] -> ID: %s (%s)", fishName, (tier or ""):upper(), assetObj.asset_id, sourceDesc))
    end
end

-- ------------------------------------------------------------------------------
-- 1. PEMINDAIAN MEMORI GC (DATA TABLES)
-- ------------------------------------------------------------------------------
local getgcFunc = getgc or (debug and debug.getgc)
if getgcFunc then
    pcall(function()
        local objects = getgcFunc(true)
        for _, obj in ipairs(objects) do
            if type(obj) == "table" then
                local possibleName = obj.Name or obj.name or obj.Title or obj.title or obj.FishName or obj.fish or obj.ItemName
                local possibleIcon = obj.Icon or obj.icon or obj.Image or obj.image or obj.Texture or obj.texture or obj.AssetId or obj.Thumbnail
                local possibleTier = obj.Tier or obj.tier or obj.Rarity or obj.rarity

                if possibleName and possibleIcon then
                    local match = findMatchingFish(tostring(possibleName))
                    if match then
                        registerExtractedFish(match.name, match.tier, possibleIcon, "Data Table")
                    end
                end

                for k, v in pairs(obj) do
                    if type(k) == "string" and type(v) == "table" then
                        local match = findMatchingFish(k)
                        if match then
                            local icon = v.Icon or v.icon or v.Image or v.image or v.Texture or v.texture or v.Thumbnail
                            if icon then
                                registerExtractedFish(match.name, match.tier, icon, "Table Dict [" .. k .. "]")
                            end
                        end
                    end
                end
            end
        end
    end)
end

-- ------------------------------------------------------------------------------
-- 2. PEMINDAIAN REPLICATED STORAGE
-- ------------------------------------------------------------------------------
pcall(function()
    local allDesc = ReplicatedStorage:GetDescendants()
    for _, item in ipairs(allDesc) do
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

        local match = findMatchingFish(item.Name)
        if match then
            local attrIcon = item:GetAttribute("Icon") or item:GetAttribute("Image") or item:GetAttribute("Texture") or item:GetAttribute("AssetId")
            if attrIcon then
                registerExtractedFish(match.name, match.tier, attrIcon, "Attribute: " .. item.Name)
            end
            
            local decal = item:FindFirstChildWhichIsA("Decal", true) or item:FindFirstChildWhichIsA("Texture", true)
            if decal and decal.Texture then
                registerExtractedFish(match.name, match.tier, decal.Texture, "Decal: " .. item.Name)
            end
            local mesh = item:FindFirstChildWhichIsA("SpecialMesh", true) or item:FindFirstChildWhichIsA("MeshPart", true)
            if mesh then
                local tex = (mesh:IsA("SpecialMesh") and mesh.TextureId) or (mesh:IsA("MeshPart") and mesh.TextureID)
                if tex and #tex > 5 then
                    registerExtractedFish(match.name, match.tier, tex, "Mesh: " .. item.Name)
                end
            end
        end
    end
end)

-- ------------------------------------------------------------------------------
-- 3. PEMINDAIAN PLAYERGUI (CATALOG / INDEX / JOURNAL / INVENTORY)
-- ------------------------------------------------------------------------------
pcall(function()
    local playerGui = LocalPlayer:FindFirstChild("PlayerGui")
    if playerGui then
        local allGui = playerGui:GetDescendants()
        for _, elem in ipairs(allGui) do
            if elem:IsA("ImageLabel") or elem:IsA("ImageButton") then
                local img = elem.Image
                if img and #img > 5 then
                    local matchedFish = findMatchingFish(elem.Name)
                    if not matchedFish and elem.Parent then
                        matchedFish = findMatchingFish(elem.Parent.Name)
                    end
                    if not matchedFish and elem.Parent then
                        for _, sibling in ipairs(elem.Parent:GetChildren()) do
                            if sibling:IsA("TextLabel") and #sibling.Text > 0 then
                                matchedFish = findMatchingFish(sibling.Text)
                                if matchedFish then break end
                            end
                        end
                    end

                    if matchedFish then
                        registerExtractedFish(matchedFish.name, matchedFish.tier, img, "PlayerGui: " .. elem.Name)
                    end
                end
            end
        end
    end
end)

-- ------------------------------------------------------------------------------
-- SIMPAN HASIL & BUKA FOLDER WINDOWS
-- ------------------------------------------------------------------------------
local countFound = 0
for _ in pairs(extractedAssets) do countFound = countFound + 1 end

local jsonOutput = HttpService:JSONEncode(extractedAssets)

-- 1. Salin ke Clipboard Windows
if setclipboard then
    setclipboard(jsonOutput)
end

-- 2. Simpan ke File di Folder Executor
if writefile then
    pcall(function()
        writefile("hasil_ekstraksi_ikan.json", jsonOutput)
    end)
end

-- 3. Kirim ke Server Lokal untuk Mengunduh Gambar & Membuka Folder Explorer
if httpRequest then
    task.spawn(function()
        pcall(function()
            httpRequest({
                Url = "http://127.0.0.1:5000/api/save_to_folder",
                Method = "POST",
                Headers = {["Content-Type"] = "application/json"},
                Timeout = 5,
                Body = jsonOutput
            })
        end)
    end)
end

-- Notifikasi Selesai di Layar Roblox
pcall(function()
    StarterGui:SetCore("SendNotification", {
        Title = "✅ Ekstraksi Selesai!",
        Text = string.format("Ditemukan %d gambar ikan. Membuka folder hasil di Windows...", countFound),
        Duration = 6
    })
end)

print(string.format("✅ Ekstraksi selesai! Ditemukan %d gambar ikan asli.", countFound))
return extractedAssets
