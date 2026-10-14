# Gemini 3.8 Flash High — Workbench colored 3D models (5)

Controlled comparison against the existing Gemini 3.8 Flash Low and Claude Sonnet 5.5 Medium experiments.
All five subject IDs and source prompts are held constant: wagasa, chochin, sensu, tsuzumi, kagura suzu.

The five generated Python scripts define build_model() and undergo an isolated, no-network Blender 5.2.2
quality gate on Yamada. Every material must use matching viewport diffuse_color and Principled BSDF Base Color.
Passing sources are published here; GitHub Actions produces five Workbench 500x400,
144-frame 24-fps turntables and stores .blend, .glb, preview and video.
This experiment is not a guarantee of historical fidelity.
