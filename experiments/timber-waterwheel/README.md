# Timber Waterwheel

Procedural Blender 5.2.2 wooden waterwheel (overshot water supply).

- 16 individual paddles and lips, 12 spokes on each face, segmented rims, iron axle.
- Millrace / wooden flume, static falling-water sheet, river, rocky banks and reed details.
- Wheel parts remain independently editable and are parented to the animated Empty.
- Keyframed Y-axis wheel rotation for 48 frames at 24 fps.
- Designed for the repository's headless Blender 5.2 render workflow.
- Visual validation checks for nonuniform PNG output and differing video frames.
- Water is artistic geometry/material, **not** a physically simulated liquid solver.

Source: scene.py and model.py. Output: rendered PNG sequence, MP4, preview, .blend, model report, validation report, then Pages gallery.

Run via the **Timber waterwheel render** GitHub Actions workflow.
