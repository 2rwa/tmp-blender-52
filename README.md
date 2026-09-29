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
- persistent validated results under `results/`
- GitHub Pages gallery generated from `results/`

## Layout

- `.github/workflows/blender52-render.yml` — render, validate, persist, build Pages, deploy
- `experiments/hello-blender52/scene.py` — minimal Blender 5.2 render scene
- `experiments/hello-blender52/validate.py` — validates the produced media and Blender version
- `experiments/hello-blender52/experiment.json` — experiment metadata
- `results/` — validated persistent render outputs
- `tools/build_pages.py` — rebuilds the static gallery from `results/`
- `docs/` — generated GitHub Pages site

Push changes under `experiments/**` or run the workflow manually with an experiment folder name.

## Standalone continuation prompt

For an AI or another developer starting from a clean clone/fork, read [`PROMPT.md`](./PROMPT.md). It is intentionally self-contained and does not require the original workspace, prior chat history, or another repository.

## Pages

https://2rwa.github.io/tmp-blender-52/

The gallery uses preview-first cards; clicking a preview loads and plays the MP4. New experiments appear automatically after their validated result is committed.
