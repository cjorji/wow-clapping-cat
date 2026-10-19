# Clapping Cat

Celebrate your adventures in WoW Forever with the clapping cat meme, complete with a transparent animation and sound.

## Features

Choose when the cat appears:

- Completing a quest (turning it in).
- Leveling up.
- Equipping a Rare (blue), Epic (purple), or Legendary (orange) item.

Each trigger can be enabled separately. Customize the cat with volume, opacity, and scale sliders, plus five screen positions: top center, top left, top right, bottom left, and bottom right.

## Download & Installation

1. Open the [latest release](https://github.com/cjorji/wow-clapping-cat/releases/latest) and download the **ClappingCat-vX.Y.Z.zip** attachment.
2. Exit WoW and extract the **ClappingCat** folder into your client's **Interface/AddOns/** folder.
3. Replace existing addon files when updating.
4. Start WoW and enable **Clapping Cat** in the AddOns list.

The final folder structure should be `Interface/AddOns/ClappingCat/ClappingCat.toc`.

## Usage

Type `/clapcat` or open **Settings → AddOns → Clapping Cat** to configure the addon.

- **Preview:** use the **Preview cat** button or `/clapcat test`.
- **Stop playback:** type `/clapcat stop`.
- **Volume:** 0–100%; 0% mutes. Other volume changes apply on the next playback. The game's Master volume also applies.
- **Opacity:** 0–100%; 0% hides the cat without muting it.
- **Scale:** 50–150%; 50% is the original size, 100% doubles it, and 150% triples it.
- **Position:** select one of the five positions. Top center is the default.

Scale, opacity, and position changes take effect immediately. Your settings are saved automatically and shared across characters on the same account.

The cat plays once per celebration. Events that occur during playback share the current celebration. Equipment triggers apply when equipping an item, including re-equipping gear; they do not require an upgrade.

## Compatibility & Support

Built for **WoW Forever** (interface 16001). Other WoW versions have not been confirmed compatible.

Occasional blank frames during playback are a known issue under investigation.

Found a problem? [Open an issue](https://github.com/cjorji/wow-clapping-cat/issues) and include your addon version, WoW client version, and steps to reproduce it.

## Media

Animation and audio are based on [this clapping cat clip](https://www.youtube.com/shorts/SX2JLYK6xqg). The original media belongs to its respective rights holders.
