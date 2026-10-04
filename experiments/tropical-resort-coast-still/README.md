# Tropical resort coast — Cycles still

First-pass still-image experiment for a southern/tropical resort shoreline.

## Goal

Prove the sea and beach themselves before attempting animation.

- Cycles CPU
- one 960×540 frame
- Blender Ocean Modifier using the TMA shallow-water spectrum
- low wind and low choppiness for a calm lagoon
- real sloped white-sand seabed visible through transmissive water
- separate water absorption/scattering volume so depth changes the color
- wet-sand material around the waterline
- fragmented shoreline foam as a still-image approximation
- dark reef / sea-grass patches under the water for depth cues
- two procedural normal scales for sub-grid ripples
- AgX color management

The ocean modifier is intentionally responsible only for the larger surface spectrum. Fine ripples, shoreline foam, water optics, and seabed variation are separate layers.

## First render acceptance

The validator checks more than file existence:

- Blender 5.2.2 and Cycles
- exactly one rendered frame
- TMA spectrum and calm wind range
- 960×540 output
- non-flat tonal distribution
- blue-dominant sky
- cyan/blue-green lagoon bias
- visible separation between sky, lagoon, and beach foreground

This is deliberately a still-only experiment. The generic renderer may package the single frame into a tiny MP4 artifact, but Pages treats this experiment as a still image.
