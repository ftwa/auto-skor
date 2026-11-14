-- ==============================================================================
-- FISH IT! ROBLOX - DEEP FISH ASSET EXTRACTOR & IN-GAME PREVIEWER
-- Versi Mode Pratinjau: Memindai & Menampilkan Gambar untuk Direview Sebelum Diterapkan
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
        Text = "Memindai gambar ikan dari memori game & UI...",
        Duration = 4
    })
end)

print("=============================================================")
print("🎣 FISH IT! - ASSET EXTRACTOR WITH IN-GAME PREVIEW")
print("  (Mode Aman: Menampilkan gambar untuk direview dulu)")
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

-- Fungsi Pengecek Nama Ikan
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
        print(string.format("  [+] DITEMUKAN: %s [%s] -> ID: %s (%s)", fishName, (tier or ""):upper(), assetObj.asset_id, sourceDesc))
    end
end

-- ------------------------------------------------------------------------------
-- VECTOR 1: PEMINDAIAN MEMORI GC (GARBAGE COLLECTOR / DATA TABLES)
-- ------------------------------------------------------------------------------
print("\n[VECTOR 1] Memindai Data Tables game (GC Scanner)...")
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
                        registerExtractedFish(match.name, match.tier, possibleIcon, "GC Data Table")
                    end
                end

                for k, v in pairs(obj) do
                    if type(k) == "string" and type(v) == "table" then
                        local match = findMatchingFish(k)
                        if match then
                            local icon = v.Icon or v.icon or v.Image or v.image or v.Texture or v.texture or v.Thumbnail
                            if icon then
                                registerExtractedFish(match.name, match.tier, icon, "GC Dict [" .. k .. "]")
                            end
                        end
                    end
                end
            end
        end
    end)
end

-- ------------------------------------------------------------------------------
-- VECTOR 2: PEMINDAIAN MODULE SCRIPTS & ATTRIBUTES DI REPLICATED STORAGE
-- ------------------------------------------------------------------------------
print("\n[VECTOR 2] Memindai ReplicatedStorage Modules & Data...")
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
                registerExtractedFish(match.name, match.tier, attrIcon, "RS Attribute: " .. item.Name)
            end
            
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
-- IN-GAME PREVIEW GUI (REVIEW LANGSUNG DI LAYAR ROBLOX)
-- ------------------------------------------------------------------------------
local function tampilkanRobloxPreviewGui(resultsTable)
    pcall(function()
        local parentGui = (gethui and gethui()) or (cloneref and cloneref(game:GetService("CoreGui"))) or LocalPlayer:WaitForChild("PlayerGui")
        
        local old = parentGui:FindFirstChild("FishItPreviewGui")
        if old then old:Destroy() end

        local sg = Instance.new("ScreenGui")
        sg.Name = "FishItPreviewGui"
        sg.ResetOnSpawn = false
        sg.ZIndexBehavior = Enum.ZIndexBehavior.Sibling

        -- Main Container
        local main = Instance.new("Frame")
        main.Name = "MainFrame"
        main.Size = UDim2.new(0, 560, 0, 520)
        main.Position = UDim2.new(0.5, -280, 0.5, -260)
        main.BackgroundColor3 = Color3.fromRGB(15, 23, 42)
        main.BorderSizePixel = 0
        main.Active = true
        main.Draggable = true
        main.Parent = sg

        local corner = Instance.new("UICorner")
        corner.CornerRadius = UDim.new(0, 16)
        corner.Parent = main

        local stroke = Instance.new("UIStroke")
        stroke.Color = Color3.fromRGB(56, 189, 248)
        stroke.Thickness = 2
        stroke.Parent = main

        -- Header
        local header = Instance.new("Frame")
        header.Size = UDim2.new(1, 0, 0, 60)
        header.BackgroundColor3 = Color3.fromRGB(30, 41, 59)
        header.BorderSizePixel = 0
        header.Parent = main

        local hCorner = Instance.new("UICorner")
        hCorner.CornerRadius = UDim.new(0, 16)
        hCorner.Parent = header

        local title = Instance.new("TextLabel")
        title.Text = "🔍 PRATINJAU GAMBAR IKAN (FISH IT)"
        title.Font = Enum.Font.GothamBold
        title.TextSize = 16
        title.TextColor3 = Color3.fromRGB(240, 249, 255)
        title.Position = UDim2.new(0, 16, 0, 10)
        title.Size = UDim2.new(1, -60, 0, 20)
        title.TextXAlignment = Enum.TextXAlignment.Left
        title.BackgroundTransparency = 1
        title.Parent = header

        local subtitle = Instance.new("TextLabel")
        subtitle.Text = "Periksa gambar di bawah ini. Pastikan sesuai sebelum Anda terapkan ke papan skor."
        subtitle.Font = Enum.Font.Gotham
        subtitle.TextSize = 11
        subtitle.TextColor3 = Color3.fromRGB(148, 163, 184)
        subtitle.Position = UDim2.new(0, 16, 0, 32)
        subtitle.Size = UDim2.new(1, -60, 0, 16)
        subtitle.TextXAlignment = Enum.TextXAlignment.Left
        subtitle.BackgroundTransparency = 1
        subtitle.Parent = header

        local btnClose = Instance.new("TextButton")
        btnClose.Text = "✕"
        btnClose.Font = Enum.Font.GothamBold
        btnClose.TextSize = 16
        btnClose.TextColor3 = Color3.fromRGB(248, 113, 113)
        btnClose.BackgroundColor3 = Color3.fromRGB(51, 65, 85)
        btnClose.Size = UDim2.new(0, 32, 0, 32)
        btnClose.Position = UDim2.new(1, -44, 0, 14)
        btnClose.Parent = header
        local bCorner = Instance.new("UICorner")
        bCorner.CornerRadius = UDim.new(0, 8)
        bCorner.Parent = btnClose
        btnClose.MouseButton1Click:Connect(function()
            sg:Destroy()
        end)

        -- Scroll List
        local scroll = Instance.new("ScrollingFrame")
        scroll.Size = UDim2.new(1, -24, 0, 380)
        scroll.Position = UDim2.new(0, 12, 0, 70)
        scroll.BackgroundColor3 = Color3.fromRGB(11, 15, 25)
        scroll.BorderSizePixel = 0
        scroll.ScrollBarThickness = 6
        scroll.Parent = main
        local sCorner = Instance.new("UICorner")
        sCorner.CornerRadius = UDim.new(0, 10)
        sCorner.Parent = scroll

        local listLayout = Instance.new("UIListLayout")
        listLayout.Padding = UDim.new(0, 8)
        listLayout.SortOrder = Enum.SortOrder.LayoutOrder
        listLayout.Parent = scroll

        local padding = Instance.new("UIPadding")
        padding.PaddingTop = UDim.new(0, 8)
        padding.PaddingBottom = UDim.new(0, 8)
        padding.PaddingLeft = UDim.new(0, 8)
        padding.PaddingRight = UDim.new(0, 8)
        padding.Parent = scroll

        -- Populate Cards
        local count = 0
        for key, item in pairs(resultsTable) do
            count = count + 1
            local card = Instance.new("Frame")
            card.Size = UDim2.new(1, -12, 0, 64)
            card.BackgroundColor3 = Color3.fromRGB(30, 41, 59)
            card.BorderSizePixel = 0
            card.Parent = scroll
            local cCorner = Instance.new("UICorner")
            cCorner.CornerRadius = UDim.new(0, 10)
            cCorner.Parent = card

            -- Image Box
            local img = Instance.new("ImageLabel")
            img.Size = UDim2.new(0, 50, 0, 50)
            img.Position = UDim2.new(0, 7, 0, 7)
            img.BackgroundColor3 = Color3.fromRGB(15, 23, 42)
            img.Image = item.rbx_url or ("rbxassetid://" .. tostring(item.asset_id))
            img.ScaleType = Enum.ScaleType.Fit
            img.Parent = card
            local iCorner = Instance.new("UICorner")
            iCorner.CornerRadius = UDim.new(0, 8)
            iCorner.Parent = img

            -- Fish Name
            local nameLbl = Instance.new("TextLabel")
            nameLbl.Text = item.fish_name or key
            nameLbl.Font = Enum.Font.GothamBold
            nameLbl.TextSize = 13.5
            nameLbl.TextColor3 = Color3.fromRGB(241, 245, 249)
            nameLbl.Position = UDim2.new(0, 68, 0, 10)
            nameLbl.Size = UDim2.new(0, 240, 0, 18)
            nameLbl.TextXAlignment = Enum.TextXAlignment.Left
            nameLbl.BackgroundTransparency = 1
            nameLbl.Parent = card

            -- Tier Badge
            local tier = string.lower(item.tier or "secret")
            local tierColor = Color3.fromRGB(234, 179, 8)
            local tierText = "🟡 LEGEND"
            if tier == "forgotten" then
                tierColor = Color3.fromRGB(192, 132, 252)
                tierText = "🌌 FORGOTTEN"
            elseif tier == "secret" then
                tierColor = Color3.fromRGB(52, 211, 153)
                tierText = "🟢 SECRET"
            elseif tier == "mitos" or tier == "mythic" then
                tierColor = Color3.fromRGB(248, 113, 113)
                tierText = "🔴 MYTHIC"
            end

            local tierLbl = Instance.new("TextLabel")
            tierLbl.Text = tierText
            tierLbl.Font = Enum.Font.GothamBold
            tierLbl.TextSize = 10
            tierLbl.TextColor3 = tierColor
            tierLbl.Position = UDim2.new(0, 68, 0, 34)
            tierLbl.Size = UDim2.new(0, 110, 0, 16)
            tierLbl.TextXAlignment = Enum.TextXAlignment.Left
            tierLbl.BackgroundTransparency = 1
            tierLbl.Parent = card

            -- Asset ID
            local idLbl = Instance.new("TextLabel")
            idLbl.Text = "Asset ID: " .. tostring(item.asset_id) .. " (" .. tostring(item.source or "Source") .. ")"
            idLbl.Font = Enum.Font.Gotham
            idLbl.TextSize = 9.5
            idLbl.TextColor3 = Color3.fromRGB(148, 163, 184)
            idLbl.Position = UDim2.new(0, 190, 0, 34)
            idLbl.Size = UDim2.new(1, -200, 0, 16)
            idLbl.TextXAlignment = Enum.TextXAlignment.Left
            idLbl.BackgroundTransparency = 1
            idLbl.Parent = card
        end

        scroll.CanvasSize = UDim2.new(0, 0, 0, count * 72 + 16)

        -- Bottom Action Buttons
        local bottom = Instance.new("Frame")
        bottom.Size = UDim2.new(1, 0, 0, 55)
        bottom.Position = UDim2.new(0, 0, 1, -55)
        bottom.BackgroundColor3 = Color3.fromRGB(20, 29, 47)
        bottom.BorderSizePixel = 0
        bottom.Parent = main
        local btmCorner = Instance.new("UICorner")
        btmCorner.CornerRadius = UDim.new(0, 16)
        btmCorner.Parent = bottom

        local jsonStr = HttpService:JSONEncode(resultsTable)

        -- Tombol 1: Salin JSON
        local btnCopy = Instance.new("TextButton")
        btnCopy.Text = "📋 Salin JSON (" .. count .. " Ikan)"
        btnCopy.Font = Enum.Font.GothamBold
        btnCopy.TextSize = 12
        btnCopy.TextColor3 = Color3.fromRGB(255, 255, 255)
        btnCopy.BackgroundColor3 = Color3.fromRGB(2, 132, 199)
        btnCopy.Size = UDim2.new(0, 220, 0, 36)
        btnCopy.Position = UDim2.new(0, 16, 0, 10)
        btnCopy.Parent = bottom
        local c1 = Instance.new("UICorner")
        c1.CornerRadius = UDim.new(0, 8)
        c1.Parent = btnCopy
        btnCopy.MouseButton1Click:Connect(function()
            if setclipboard then
                setclipboard(jsonStr)
                btnCopy.Text = "✅ Tersalin ke Clipboard!"
                task.wait(2)
                btnCopy.Text = "📋 Salin JSON (" .. count .. " Ikan)"
            end
        end)

        -- Tombol 2: Kirim ke Auto Skor Preview
        local btnSend = Instance.new("TextButton")
        btnSend.Text = "🚀 Buka di Auto Skor Web"
        btnSend.Font = Enum.Font.GothamBold
        btnSend.TextSize = 12
        btnSend.TextColor3 = Color3.fromRGB(15, 23, 42)
        btnSend.BackgroundColor3 = Color3.fromRGB(52, 211, 153)
        btnSend.Size = UDim2.new(0, 220, 0, 36)
        btnSend.Position = UDim2.new(1, -236, 0, 10)
        btnSend.Parent = bottom
        local c2 = Instance.new("UICorner")
        c2.CornerRadius = UDim.new(0, 8)
        c2.Parent = btnSend
        btnSend.MouseButton1Click:Connect(function()
            if httpRequest then
                btnSend.Text = "⏳ Mengirim..."
                task.spawn(function()
                    pcall(function()
                        local res = httpRequest({
                            Url = "http://127.0.0.1:5000/api/preview_fish_assets",
                            Method = "POST",
                            Headers = {["Content-Type"] = "application/json"},
                            Timeout = 5,
                            Body = jsonStr
                        })
                        if res and (res.StatusCode == 200 or res.StatusCode == 201) then
                            btnSend.Text = "✅ Terkirim ke Pratinjau!"
                        else
                            btnSend.Text = "❌ Gagal (Server Offline)"
                        end
                    end)
                end)
            end
        end)

        sg.Parent = parentGui
    end)
end

-- ------------------------------------------------------------------------------
-- EKSEKUSI & TAMPILKAN PRATINJAU
-- ------------------------------------------------------------------------------
local countFound = 0
for _ in pairs(extractedAssets) do countFound = countFound + 1 end

print("\n=============================================================")
print(string.format("✅ EKSTRAKSI SELESAI: DITEMUKAN %d ASSET GAMBAR IKAN!", countFound))
print("  Membuka jendela pratinjau di layar game Anda...")
print("=============================================================")

local jsonOutput = HttpService:JSONEncode(extractedAssets)

-- 1. SALIN KE CLIPBOARD SECARA OTOMATIS
if setclipboard then
    setclipboard(jsonOutput)
    print("📋 [OK] Data JSON telah DISALIN KE CLIPBOARD Windows Anda.")
end

-- 2. SIMPAN SEBAGAI FILE PREVIEW
if writefile then
    pcall(function()
        writefile("fishit_extracted_preview.json", jsonOutput)
        print("💾 [OK] File pratinjau tersimpan di executor: workspace/fishit_extracted_preview.json")
    end)
end

-- 3. KIRIM KE ENDPOINT STAGING/PREVIEW (BUKAN TIMPA LANGSUNG)
if httpRequest then
    task.spawn(function()
        pcall(function()
            httpRequest({
                Url = "http://127.0.0.1:5000/api/preview_fish_assets",
                Method = "POST",
                Headers = {["Content-Type"] = "application/json"},
                Timeout = 4,
                Body = jsonOutput
            })
        end)
    end)
end

-- 4. BUKA JENDELA PRATINJAU LANGSUNG DI LAYAR ROBLOX
tampilkanRobloxPreviewGui(extractedAssets)

-- Notifikasi Selesai di Layar Roblox
pcall(function()
    StarterGui:SetCore("SendNotification", {
        Title = "🎉 Pratinjau Terbuka!",
        Text = string.format("Ditemukan %d gambar ikan asli. Silakan review langsung di layar!", countFound),
        Duration = 6
    })
end)

return extractedAssets
