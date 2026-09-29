# tmp-blender-52

Blender 5.2 rendering sandbox for GitHub Actions.

The runtime/bootstrap flow is adapted from the known-good Blender 5.2.2 path in `2rwa/tmp-blender-rigid-cloth`.

## Baseline

- Blender 5.2.2 official Linux x64 archive
- SHA-256 verification against Blender's published checksum file
- cached Blender/Pillow/EGL runtime
- headless execution with Xvfb + software OpenGL
- PNG frame sequence -> ffmpeg H.264 MP4
- output validation beyond process exit status
- 120 minute render-job timeout

## Layout

- `.github/workflows/blender52-render.yml` — render/validate/artifact workflow
- `experiments/hello-blender52/scene.py` — minimal Blender 5.2 render scene
- `experiments/hello-blender52/validate.py` — validates the produced media and Blender version
- `experiments/hello-blender52/experiment.json` — experiment metadata

Push changes under `experiments/**` or run the workflow manually with an experiment folder name.
