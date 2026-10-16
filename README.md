# Clapping Cat

A transparent animated cat and the original clip's audio celebrate:

- Quest turn-ins
- Level ups
- Equipping Rare (blue), Epic (purple), or Legendary (orange) items

Each trigger has its own checkbox under **Settings → AddOns → Clapping Cat**.
All five start enabled. Volume, opacity, and scale sliders, five position selectors, and a preview button are included.
Preferences are saved across characters on the same account.

## Install

1. Exit WoW.
2. Extract `ClappingCat.zip` into your chosen WoW client's `Interface/AddOns/` directory.
3. Confirm the resulting path is `Interface/AddOns/ClappingCat/ClappingCat.toc` (avoid an extra nested folder).
4. Start WoW and enable **Clapping Cat** in the AddOns list.
5. Type `/clapcat test` to check animation and sound, or `/clapcat` to open its options.

`/clapcat stop` stops the current celebration. Sound uses the Master channel and
respects the game's master sound toggle and volume. The addon volume slider uses
5% steps; 0% mutes and stops any active clapping. Other volume changes apply on
the next playback. Opacity uses 1% steps and updates immediately, including during
a preview; 0% hides the cat without muting it. Both default to 100% and are saved.
Existing disabled sound settings migrate to 0% volume.

## Behavior

The full clip plays once with click-through enabled. Top center is the default
position; top left, top right, bottom left, and bottom right are also available.
The scale slider spans 50–150% in 5% steps: 50% preserves the original size,
100% doubles it, and 150% triples it. Scale defaults to 50%. Scale and position
changes apply immediately during playback and persist across reloads. Triggers
during playback share the existing celebration instead of stacking or restarting.
Preview always restarts playback. Equipping an item triggers even if it is not an
upgrade; looting, removing gear, or merely having it equipped on login does not.
Re-equipping gear or using an equipment set can trigger a celebration.
Quest completion means the rewarded turn-in event, rather than finishing the last
objective in the quest log.

## Compatibility and testing

The manifest currently targets Forever interface `16001`; the user's exact build
is still unconfirmed. Settings registration includes modern Settings and legacy
Interface Options paths, and item queries support both namespaced and global APIs.
The v0.1.0 release was tested in-game by the user; occasional blank animation
frames were reported. All 102 source frames contain visible pixels, so the cause
of that flicker remains unconfirmed. The new scale and position controls have
automated coverage but still need in-game testing. Modern Classic/Retail versions
may work after setting the appropriate `Interface` value or enabling out-of-date
addons; compatibility with every version, especially original vanilla clients,
is not claimed.

In-game acceptance checks:

- Preview the cat and confirm the background is transparent and sound plays.
- Turn each trigger off and verify that event does not play the cat.
- Turn each on and perform its event, including each equipment quality.
- Reload and confirm preferences persist and equipped gear stays quiet on login.
- Trigger two events during playback and confirm there is only one sound.
- Set Volume to 0% and confirm animation still works without sound.
- Set Volume to 25%, 50%, and 100%, preview each, and compare loudness.
- Adjust Opacity and Scale during preview and confirm changes apply immediately.
- Check all five positions at 50%, 100%, and 150% scale and confirm placement.
- Reload and confirm all slider settings and the selected position persist.

## Assets and rebuilding

The addon contains 15 fps, 256-pixel transparent animation frames packed into
1024×1024, 32-bit TGA sheets, plus 20 OGG audio volume variants. These control only the cat
audio without changing the game's sound settings. It does not use the large editing MOV
at runtime. The original transparent master stays in Downloads.

Rebuild assets with Python 3 and FFmpeg:

```sh
python3 tools/build_media.py '/path/to/Clapping Cat Meme Transparent.mov'
```

The source clip's ownership/redistribution permissions are not supplied with this
project. No license to the original cat video or audio is granted here.
