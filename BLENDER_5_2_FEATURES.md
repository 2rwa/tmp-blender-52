# Blender 5.2 LTS feature render study

This repository renders five small experiments that exercise Blender 5.2-specific features with Blender 5.2.2 on GitHub Actions.

## Official 5.2 sources

- Blender 5.2 LTS release overview: https://www.blender.org/download/releases/5-2/
- Physics release notes: https://developer.blender.org/docs/release_notes/5.2/physics/
- Rendering release notes: https://developer.blender.org/docs/release_notes/5.2/rendering/
- Compositor release notes: https://developer.blender.org/docs/release_notes/5.2/compositor/
- Geometry Nodes physics article: https://code.blender.org/2026/07/geometry-nodes-physics/

## Selected render experiments

| Experiment | Blender 5.2 feature | Runtime validation |
| --- | --- | --- |
| feature52-cloth-tearing | Experimental Geometry Nodes Cloth Dynamics / XPBD tearing | Requires an actual topology split and increased vertex count |
| feature52-thin-wall | Principled BSDF Thin Wall input | Requires the 5.2 Thin Wall socket to exist and be enabled |
| feature52-shader-scene-time | Scene Time node in shader graphs | Requires the node and visible frame-to-frame luminance change |
| feature52-compositor-blank-image | New Blank Image compositor node | Requires the new node and its Size socket |
| feature52-compositor-string-to-image | New String to Image compositor node | Requires the new node and exact rendered text input |

The dedicated workflow is .github/workflows/blender52-feature-showcase.yml. It runs all five experiments in parallel, validates the real rendered outputs, uploads artifacts, and commits all five validated results together under results/. The existing Pages workflow then rebuilds the gallery.
