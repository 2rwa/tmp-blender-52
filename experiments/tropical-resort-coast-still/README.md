# Tropical resort coast — Cycles still

Still-image iteration for a southern/tropical resort shoreline.

## Current pass

Pass 3 replaces the failed low-angle Ocean Modifier patch with an explicit
shoreline-following water surface. The goal is to establish believable
transparent shallows before returning to animation or a full spectral ocean.

- Cycles CPU
- one 960×540 frame
- shoreline-following water mesh with three geometric wave scales
- generated-coordinate shallow-to-deep water tint
- high transmission near shore, lower transmission offshore
- sloped pale sand seabed visible through the water
- reef / sea-grass patches for underwater depth cues
- separate water volume disabled after it produced flat tank-like bands
- small fragmented foam ribbons instead of broad quad strips
- diagonal shoreline composition
- AgX color management

The old TMA experiment remains useful as a spectral reference, but the still
shot now prioritizes robust shoreline contact and visual debugging.

## Acceptance

The validator checks:

- Blender 5.2.2 and Cycles
- exactly one rendered frame
- shoreline-following water model is active
- 960×540 output
- non-flat tonal distribution
- blue-dominant sky
- cyan/blue-green lagoon bias
- visible separation between sky, lagoon, and beach foreground
