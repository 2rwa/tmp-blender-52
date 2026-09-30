# ocean-wave-bake

Blender 5.2 ocean experiment inspired by:

- https://www.youtube.com/watch?v=qD6gM8Z2978

The referenced creator describes a workflow using baked wave data as an image texture. This experiment keeps the same idea but remains self-contained for GitHub Actions:

- large-scale waves: generated geometry displacement
- fine waves: generated normal-bake PNG loaded through an Image Texture node
- render: Cycles CPU
- preview workflow: 320x180, one frame, 10 variants in parallel
- later full render: 640x360, 24 frames, one second

Generated bake images are stored in each render artifact under bake/.
