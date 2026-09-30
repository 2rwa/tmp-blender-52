# backrooms-note-repro

Reproduction experiment based on 木谷 修, 「blender 5.2 バックルームを作る」 (2026-09-28):
https://note.com/kitaniosam/n/ne760c5e78985

## Reproduced technique

- Blender 5.2 / Cycles
- overall room footprint: about 65 m x 15 m
- simple maze-like wall layout with a small bevel on wall edges
- ceiling luminous panels with emission strength 1.0
- area lights at the same positions, power 80 W
- 30 mm camera for stronger perspective
- noisy carpet with bump
- reduced saturation and slightly softened contrast in Blender's compositor
- one extra front area light, following the article's final lighting adjustment

## Intentional differences

The A24 wallpaper image mentioned by the article is **not copied**. This experiment uses a self-contained procedural yellow wallpaper material so the GitHub/Actions build has no third-party texture dependency. The exact floor plan is also an original approximation; the goal is to reproduce the rendering technique and atmosphere, not a pixel-identical scene.

The workflow renders a 1-second, 24-frame micro-dolly with subtle fluorescent flicker so the existing Pages gallery can expose both a preview image and playable MP4 while preserving the article's still-image composition.
