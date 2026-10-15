local addonName, addon = ...
local media = addon.media
local path = "Interface\\AddOns\\" .. addonName .. "\\Media\\"
local defaults = { quest = true, level = true, rare = true, epic = true, legendary = true }
local qualityKeys = { [3] = "rare", [4] = "epic", [5] = "legendary" }
local db, category, options
local ready = false
local generations = {}
local equipmentGeneration, worldGeneration = 0, 0
local soundHandle, started, currentFrame, currentSheet

local cat = CreateFrame("Frame", nil, UIParent)
cat:SetSize(360, 360)
cat:SetPoint("CENTER", UIParent, "CENTER", 0, 30)
cat:SetFrameStrata("DIALOG")
cat:EnableMouse(false)
cat:Hide()
local texture = cat:CreateTexture(nil, "ARTWORK")
texture:SetAllPoints()

local function Stop()
    cat:Hide()
    cat:SetScript("OnUpdate", nil)
    if soundHandle and StopSound then StopSound(soundHandle) end
    soundHandle = nil
    texture:SetTexture(nil)
end

local function DrawFrame(index)
    if currentFrame == index then return end
    currentFrame = index
    local perSheet = media.columns * media.rows
    local sheet = math.floor(index / perSheet) + 1
    if sheet ~= currentSheet then
        texture:SetTexture(path .. string.format("Cat%02d.tga", sheet))
        currentSheet = sheet
    end
    local cell = index % perSheet
    local col, row = cell % media.columns, math.floor(cell / media.columns)
    texture:SetTexCoord(col / media.columns, (col + 1) / media.columns,
        row / media.rows, (row + 1) / media.rows)
end

local function Play(preview)
    if not db then return end
    if cat:IsShown() and not preview then return end
    Stop()
    started, currentFrame, currentSheet = GetTime(), nil, nil
    DrawFrame(0)
    cat:SetAlpha(db.opacity / 100)
    cat:Show()
    if db.volume > 0 then
        -- Pre-scaled audio provides addon-only volume on clients without file volume APIs.
        local played, handle = PlaySoundFile(path .. string.format("Clap%03d.ogg", db.volume), "Master")
        if played then soundHandle = handle end
    end
    cat:SetScript("OnUpdate", function()
        local frame = math.floor((GetTime() - started) * media.fps)
        if frame >= media.frames then Stop() else DrawFrame(frame) end
    end)
end

local function ItemQuality(link)
    if C_Item and C_Item.GetItemInfo then
        local _, _, quality = C_Item.GetItemInfo(link)
        return quality
    elseif GetItemInfo then
        local _, _, quality = GetItemInfo(link)
        return quality
    end
end

local function CheckEquipment(slot, generation, attempt)
    if not ready or generations[slot] ~= generation then return end
    local link = GetInventoryItemLink("player", slot)
    if not link then return end
    local quality = ItemQuality(link)
    if quality then
        local key = qualityKeys[quality]
        if key and db[key] then Play() end
    elseif attempt < 20 then
        -- Item information can arrive after the equipment event.
        C_Timer.After(0.25, function() CheckEquipment(slot, generation, attempt + 1) end)
    end
end

local function CreateOptions()
    options = CreateFrame("Frame")
    options.name = "Clapping Cat"
    local title = options:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
    title:SetPoint("TOPLEFT", 20, -20)
    title:SetText("Clapping Cat")
    local description = options:CreateFontString(nil, "ARTWORK", "GameFontHighlight")
    description:SetPoint("TOPLEFT", title, "BOTTOMLEFT", 0, -12)
    description:SetText("Choose when the cat celebrates. Changes are saved automatically.")
    local choices = {
        { "quest", "On quest completion (turn-in)" },
        { "level", "On level up" },
        { "rare", "On equipping a |cff0070ddRare (blue)|r item" },
        { "epic", "On equipping an |cffa335eeEpic (purple)|r item" },
        { "legendary", "On equipping a |cffff8000Legendary (orange)|r item" },
    }
    local checks = {}
    for index, choice in ipairs(choices) do
        local key = choice[1]
        local check = CreateFrame("CheckButton", nil, options, "InterfaceOptionsCheckButtonTemplate")
        check:SetPoint("TOPLEFT", 20, -80 - (index - 1) * 36)
        check.Text:SetText(choice[2])
        check:SetScript("OnClick", function(self)
            db[key] = self:GetChecked() and true or false
        end)
        checks[key] = check
    end
    local function AddSlider(key, label, y, step)
        local slider = CreateFrame("Slider", nil, options)
        slider:SetSize(280, 20)
        slider:SetPoint("TOPLEFT", 28, y)
        slider:SetOrientation("HORIZONTAL")
        slider:SetMinMaxValues(0, 100)
        slider:SetValueStep(step)
        slider:SetObeyStepOnDrag(true)
        slider:EnableMouse(true)
        local track = slider:CreateTexture(nil, "BACKGROUND")
        track:SetSize(280, 6)
        track:SetPoint("CENTER")
        track:SetColorTexture(0.25, 0.25, 0.25, 1)
        local thumb = slider:CreateTexture(nil, "OVERLAY")
        thumb:SetSize(24, 24)
        thumb:SetTexture("Interface\\Buttons\\UI-SliderBar-Button-Horizontal")
        slider:SetThumbTexture(thumb)
        local text = slider:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        text:SetPoint("BOTTOMLEFT", slider, "TOPLEFT", 0, 4)
        slider:SetScript("OnValueChanged", function(_, value)
            value = math.max(0, math.min(100, math.floor(value / step + 0.5) * step))
            db[key] = value
            text:SetText(label .. ": " .. value .. "%")
            if key == "opacity" then cat:SetAlpha(value / 100)
            elseif value == 0 and soundHandle then
                if StopSound then StopSound(soundHandle) end
                soundHandle = nil
            end
        end)
        return slider
    end
    local volume = AddSlider("volume", "Volume", -292, 5)
    local opacity = AddSlider("opacity", "Opacity", -352, 1)
    options:SetScript("OnShow", function()
        for key, check in pairs(checks) do check:SetChecked(db[key]) end
        volume:SetValue(db.volume)
        opacity:SetValue(db.opacity)
    end)
    local preview = CreateFrame("Button", nil, options, "UIPanelButtonTemplate")
    preview:SetSize(140, 28)
    preview:SetPoint("TOPLEFT", 24, -400)
    preview:SetText("Preview cat")
    preview:SetScript("OnClick", function() Play(true) end)
    local hint = options:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
    hint:SetPoint("TOPLEFT", preview, "BOTTOMLEFT", 0, -16)
    hint:SetText("Volume: 0% mutes; other changes apply on the next playback.\nOpacity updates immediately; 0% hides the cat.\nSound also follows your Master volume.\nCommands: /clapcat test, /clapcat stop")
    if Settings and Settings.RegisterCanvasLayoutCategory then
        category = Settings.RegisterCanvasLayoutCategory(options, options.name)
        Settings.RegisterAddOnCategory(category)
    elseif InterfaceOptions_AddCategory then
        InterfaceOptions_AddCategory(options)
    end
end

SLASH_CLAPPINGCAT1 = "/clapcat"
SlashCmdList.CLAPPINGCAT = function(message)
    message = (message or ""):lower():match("^%s*(.-)%s*$")
    if message == "test" then Play(true)
    elseif message == "stop" then Stop()
    elseif category then Settings.OpenToCategory(category:GetID())
    elseif options and InterfaceOptionsFrame_OpenToCategory then
        InterfaceOptionsFrame_OpenToCategory(options)
    end
end

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("PLAYER_LEAVING_WORLD")
events:RegisterEvent("QUEST_TURNED_IN")
events:RegisterEvent("PLAYER_LEVEL_UP")
events:RegisterEvent("PLAYER_EQUIPMENT_CHANGED")
events:SetScript("OnEvent", function(self, event, ...)
    if event == "ADDON_LOADED" then
        if ... ~= addonName then return end
        if type(ClappingCatDB) ~= "table" then ClappingCatDB = {} end
        db = ClappingCatDB
        for key, value in pairs(defaults) do
            if type(db[key]) ~= "boolean" then db[key] = value end
        end
        if type(db.volume) ~= "number" or db.volume ~= db.volume then
            db.volume = db.sound == false and 0 or 100
        end
        db.volume = math.max(0, math.min(100, math.floor(db.volume / 5 + 0.5) * 5))
        if type(db.opacity) ~= "number" or db.opacity ~= db.opacity then db.opacity = 100 end
        db.opacity = math.max(0, math.min(100, math.floor(db.opacity + 0.5)))
        db.sound = nil
        CreateOptions()
        self:UnregisterEvent("ADDON_LOADED")
    elseif event == "PLAYER_ENTERING_WORLD" then
        -- Ignore the equipment refresh sent during login and loading screens.
        ready = false
        worldGeneration = worldGeneration + 1
        local generation = worldGeneration
        C_Timer.After(1, function()
            if worldGeneration == generation then ready = db ~= nil end
        end)
    elseif event == "PLAYER_LEAVING_WORLD" then
        ready = false
        worldGeneration = worldGeneration + 1
        generations = {}
        Stop()
    elseif db and ready then
        if event == "QUEST_TURNED_IN" and db.quest then Play()
        elseif event == "PLAYER_LEVEL_UP" and db.level then Play()
        elseif event == "PLAYER_EQUIPMENT_CHANGED" then
            local slot, hasItem = ...
            equipmentGeneration = equipmentGeneration + 1
            generations[slot] = equipmentGeneration
            if hasItem then CheckEquipment(slot, generations[slot], 0) end
        end
    end
end)
