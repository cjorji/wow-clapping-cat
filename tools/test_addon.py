"""Exercise addon event behavior in Lua using a small WoW API stub (requires lupa)."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[1]


def runtime(modern=True, saved=None):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
        now, plays, stopped, timers, frames, inventory, qualities = 0, 0, 0, {}, {}, {}, {}
        SlashCmdList = {}
        local methods = {}
        function methods:SetScript(name, fn) self.scripts[name] = fn end
        function methods:RegisterEvent(event) self.events[event] = true end
        function methods:UnregisterEvent(event) self.events[event] = nil end
        function methods:Show() self.shown = true end
        function methods:Hide() self.shown = false end
        function methods:IsShown() return self.shown end
        function methods:SetChecked(value) self.checked = value end
        function methods:GetChecked() return self.checked end
        function methods:SetTexture(value) self.texture = value end
        function methods:SetTexCoord(...) self.coords = {...} end
        function methods:SetText(value) self.text = value end
        function methods:SetAlpha(value) self.alpha = value end
        function methods:SetOrientation() end
        function methods:SetMinMaxValues(low, high) self.minimum, self.maximum = low, high end
        function methods:SetValueStep() end
        function methods:SetObeyStepOnDrag() end
        function methods:SetColorTexture() end
        function methods:SetThumbTexture() end
        function methods:SetValue(value)
            self.value = value
            if self.scripts.OnValueChanged then self.scripts.OnValueChanged(self, value) end
        end
        function methods:SetSize(width, height) self.width, self.height = width, height end
        function methods:SetPoint(...) self.point = {...} end
        function methods:ClearAllPoints() self.point = nil end
        function methods:SetFrameStrata() end
        function methods:EnableMouse() end
        function methods:SetAllPoints() end
        local function object()
            return setmetatable({scripts = {}, events = {}}, {__index = methods})
        end
        function methods:CreateTexture() return object() end
        function methods:CreateFontString() return object() end
        function CreateFrame(kind, name, parent, template)
            local obj = object()
            obj.Text = object()
            obj.kind, obj.parent, obj.template = kind, parent, template
            table.insert(frames, obj)
            return obj
        end
        function GetTime() return now end
        function PlaySoundFile(path, channel)
            assert(path:match('Clap%d%d%d.ogg$') and channel == 'Master')
            plays = plays + 1
            lastSoundPath = path
            return true, plays
        end
        function StopSound() stopped = stopped + 1 end
        function GetInventoryItemLink(unit, slot) return inventory[slot] end
        function GetItemInfo(link) return 'item', link, qualities[link] end
        C_Item = {GetItemInfo = GetItemInfo}
        C_Timer = {After = function(delay, fn) table.insert(timers, {at = now + delay, fn = fn}) end}
        function advance(seconds)
            now = now + seconds
            local due = timers
            timers = {}
            for _, timer in ipairs(due) do
                if timer.at <= now then timer.fn() else table.insert(timers, timer) end
            end
            for _, frame in ipairs(frames) do
                if frame.shown and frame.scripts.OnUpdate then frame.scripts.OnUpdate(frame, seconds) end
            end
        end
        function emit(event, ...)
            for _, frame in ipairs(frames) do
                if frame.events[event] then frame.scripts.OnEvent(frame, event, ...) end
            end
        end
        UIParent = object()
        Settings = {
            RegisterCanvasLayoutCategory = function(panel, name)
                registeredPanel = panel
                return {GetID = function() return 123 end}
            end,
            RegisterAddOnCategory = function(category) assert(category:GetID() == 123) end,
            OpenToCategory = function(id) opened = id end,
        }
        function InterfaceOptions_AddCategory(panel) registeredPanel = panel end
        function InterfaceOptionsFrame_OpenToCategory(panel) opened = panel.name end
    ''')
    if not modern:
        lua.execute('Settings = nil; C_Item = nil')
    if saved:
        lua.globals().ClappingCatDB = lua.table_from(saved)
    addon = lua.table()
    for file in ['Media.lua', 'ClappingCat.lua']:
        lua.execute((root / 'ClappingCat' / file).read_text(), 'ClappingCat', addon)
    lua.execute("emit('ADDON_LOADED', 'AnotherAddon'); assert(registeredPanel == nil)")
    lua.execute("emit('ADDON_LOADED', 'ClappingCat')")
    return lua


for modern in (True, False):
    lua = runtime(modern)
    lua.execute('''
        assert(ClappingCatDB.quest and ClappingCatDB.rare and ClappingCatDB.volume == 100 and ClappingCatDB.opacity == 100)
        emit('PLAYER_ENTERING_WORLD')
        inventory[1], qualities.blue = 'blue', 3
        emit('PLAYER_EQUIPMENT_CHANGED', 1, true)
        assert(plays == 0) -- startup refresh
        advance(1)
        emit('QUEST_TURNED_IN', 123)
        emit('PLAYER_LEVEL_UP', 2)
        assert(plays == 1) -- simultaneous triggers coalesce
        advance(7)
        emit('PLAYER_LEVEL_UP', 3)
        assert(plays == 2)
        advance(7)
        ClappingCatDB.quest = false
        emit('QUEST_TURNED_IN', 124)
        assert(plays == 2)
        for quality = 3, 5 do
            inventory[1] = 'quality' .. quality
            qualities[inventory[1]] = quality
            emit('PLAYER_EQUIPMENT_CHANGED', 1, true)
            assert(plays == quality)
            advance(7)
        end
        ClappingCatDB.rare = false
        inventory[1] = 'blue'
        emit('PLAYER_EQUIPMENT_CHANGED', 1, true)
        assert(plays == 5)
        inventory[1], qualities.white = 'white', 1
        emit('PLAYER_EQUIPMENT_CHANGED', 1, true)
        emit('PLAYER_EQUIPMENT_CHANGED', 1, false)
        assert(plays == 5)
        -- Delayed item data resolves, while replaced items cancel their retry.
        inventory[1] = 'uncached'
        emit('PLAYER_EQUIPMENT_CHANGED', 1, true)
        qualities.uncached = 4
        advance(0.25)
        assert(plays == 6)
        advance(7)
        inventory[1] = 'stale'
        emit('PLAYER_EQUIPMENT_CHANGED', 1, true)
        inventory[1], qualities.stale = nil, 5
        emit('PLAYER_EQUIPMENT_CHANGED', 1, false)
        advance(0.25)
        assert(plays == 6)
        SlashCmdList.CLAPPINGCAT('test')
        assert(plays == 7)
        SlashCmdList.CLAPPINGCAT('stop')
        assert(not frames[1]:IsShown())
        ClappingCatDB.volume = 0
        SlashCmdList.CLAPPINGCAT('test')
        assert(plays == 7 and frames[1]:IsShown())
        -- Checkboxes and sliders update saved state.
        registeredPanel.scripts.OnShow(registeredPanel)
        local count = 0
        for _, frame in ipairs(frames) do
            if frame.template == 'InterfaceOptionsCheckButtonTemplate' then
                count = count + 1
                frame:SetChecked(false)
                frame.scripts.OnClick(frame)
            end
        end
        assert(count == 5)
        local sliders = {}
        for _, frame in ipairs(frames) do
            if frame.kind == 'Slider' then table.insert(sliders, frame) end
        end
        assert(#sliders == 3)
        sliders[2]:SetValue(37)
        assert(ClappingCatDB.opacity == 37 and frames[1].alpha == 0.37)
        sliders[1]:SetValue(55)
        assert(ClappingCatDB.volume == 55)
        SlashCmdList.CLAPPINGCAT('test')
        assert(lastSoundPath:match('Clap055.ogg$') and frames[1].alpha == 0.37)
        local previousStops = stopped
        sliders[1]:SetValue(0)
        assert(stopped == previousStops + 1 and frames[1]:IsShown())
        local previousPlays = plays
        sliders[2]:SetValue(0)
        SlashCmdList.CLAPPINGCAT('test')
        assert(plays == previousPlays and frames[1].alpha == 0)
        sliders[1]:SetValue(55)
        sliders[2]:SetValue(37)
        assert(sliders[3].minimum == 50 and sliders[3].maximum == 150)
        for _, value in ipairs({50, 100, 150}) do
            sliders[3]:SetValue(value)
            assert(ClappingCatDB.scale == value and frames[1].width == 360 * value / 50)
        end
        local positions = {'TOP', 'TOPLEFT', 'TOPRIGHT', 'BOTTOMLEFT', 'BOTTOMRIGHT'}
        local radios = {}
        for _, frame in ipairs(frames) do
            if frame.template == 'UIRadioButtonTemplate' then table.insert(radios, frame) end
        end
        assert(#radios == 5)
        for index, radio in ipairs(radios) do
            radio.scripts.OnClick(radio)
            assert(ClappingCatDB.position == positions[index])
            assert(frames[1].point[1] == positions[index])
            for otherIndex, other in ipairs(radios) do
                assert(other:GetChecked() == (otherIndex == index))
            end
        end
        assert(frames[1]:IsShown())
        SlashCmdList.CLAPPINGCAT('')
        assert(opened ~= nil)
    ''')
    saved = dict(lua.globals().ClappingCatDB.items())
    reload = runtime(modern, saved)
    reload.execute('''
        assert(ClappingCatDB.volume == 55 and ClappingCatDB.opacity == 37)
        assert(ClappingCatDB.scale == 150 and ClappingCatDB.position == 'BOTTOMRIGHT')
        for _, key in ipairs({'quest', 'level', 'rare', 'epic', 'legendary'}) do
            assert(ClappingCatDB[key] == false)
        end
    ''')
    migrated = runtime(modern, {'sound': False})
    migrated.execute("assert(ClappingCatDB.scale == 50 and ClappingCatDB.position == 'TOP')")
    migrated.execute('assert(ClappingCatDB.volume == 0 and ClappingCatDB.opacity == 100 and ClappingCatDB.sound == nil)')
    invalid = runtime(modern, {'volume': 999, 'opacity': -5, 'scale': 999, 'position': 'INVALID'})
    invalid.execute("assert(ClappingCatDB.scale == 150 and ClappingCatDB.position == 'TOP')")
    invalid.execute('assert(ClappingCatDB.volume == 100 and ClappingCatDB.opacity == 0)')
    print(('Modern' if modern else 'Legacy') + ' API: triggers, coalescing, cache retries, sliders, mute, migration, and saved preferences passed')

# Validate the actual packaged asset layout and alpha channel.
import struct
metadata = (root / 'ClappingCat' / 'Media.lua').read_text()
assert 'frames = 102' in metadata
for sheet in sorted((root / 'ClappingCat' / 'Media').glob('*.tga')):
    raw = sheet.read_bytes()
    header = struct.unpack('<BBBHHBHHHHBB', raw[:18])
    assert header[2] == 2 and header[8:12] == (1024, 1024, 32, 40)
    assert len(raw) == 18 + 1024 * 1024 * 4
    alpha = raw[21::4]
    assert min(alpha) == 0 and max(alpha) == 255
# Every active frame must contain visible pixels, including both sides of sheet boundaries.
for index in range(102):
    raw = (root / 'ClappingCat' / 'Media' / f'Cat{index // 16 + 1:02d}.tga').read_bytes()
    x, y = index % 4 * 256, index % 16 // 4 * 256
    assert any(raw[18 + ((y + row) * 1024 + x) * 4 + 3:
                   18 + ((y + row) * 1024 + x + 256) * 4:4].strip(b'\x00')
               for row in range(256)), f'Blank animation frame {index}'
print('All seven sprite sheets and 102 active frames: layout, alpha, and nonblank content passed')

audio = sorted((root / 'ClappingCat' / 'Media').glob('Clap*.ogg'))
assert len(audio) == 20
assert {p.name for p in audio} == {f'Clap{v:03d}.ogg' for v in range(5, 101, 5)}
print('All 20 volume variants present')
