# tmp-blender-52 standalone continuation prompt

You are working on the repository that contains this file. Treat this repository alone as the source of truth.

Do not require or assume access to any other repository, prior chat, private workspace, user-specific path, or historical context. Do not hard-code the original GitHub owner. If this repository was cloned or forked, operate on the current repository and its current remote.

## First actions

1. Read `README.md`.
2. Read `.github/workflows/blender52-render.yml` completely.
3. Inspect `experiments/`, `results/`, `tools/`, and `docs/`.
4. Inspect the latest Git history and current GitHub Actions state when GitHub access is available.
5. Reuse the existing Blender 5.2 runtime/render/publish pipeline before creating a new one.

## Project purpose

This repository is a self-contained Blender 5.2 rendering sandbox designed to run on GitHub Actions.

The baseline pipeline is:

`experiment source -> cheap preflight -> Blender 5.2.2 headless render -> PNG frames -> ffmpeg MP4 -> validation -> Actions artifact -> persistent result -> Pages gallery -> Pages deploy`

Blender is intentionally downloaded by the workflow from the official Blender release archive. A developer should not need a locally installed Blender to use the GitHub Actions path.

## Development rules

- Inspect existing code and known-good experiments before writing new code.
- Build validation together with the feature. Do not treat process exit code alone as success.
- Run cheap syntax/static/preflight checks before expensive rendering.
- Use GitHub Actions for long renders or simulations.
- The normal heavy render timeout is 120 minutes unless the experiment has a concrete reason to use another limit.
- Diagnose failures from the actual workflow logs and generated files, then fix the root cause.
- Preserve useful regression checks after a failure is understood.
- Do not silently weaken validation just to make a failing render pass.
- Keep the workflow usable from a clean clone/fork. Avoid absolute paths and user-specific configuration.
- Avoid dependencies on files outside this repository.

## Creating a new experiment

Create a directory under `experiments/<experiment-id>/` with at least:

- `scene.py` — builds the scene and writes render output under `output52/`.
- `validate.py` — validates actual generated output.
- `experiment.json` — contains at least `id`, `title`, and `description`.

Follow the existing `experiments/hello-blender52/` experiment as the compatibility baseline.

The workflow accepts an experiment directory through `workflow_dispatch`. Keep new experiments compatible with that interface unless there is a strong reason to extend it.

## Output contract

An experiment should normally produce:

- `output52/frames/frame_%04d.png`
- `output52/preview.png`
- `output52/<experiment-id>.mp4` after ffmpeg
- `output52/<experiment-id>.blend`
- `output52/<experiment-id>-report.json` when useful
- `output52/blender-version.txt`
- `output52/validation.json` after validation

`validate.py` should check meaningful properties such as Blender version, frame count, image dimensions, non-empty/non-uniform image content, expected simulation state, topology/geometry state when relevant, and plausible file sizes.

## Blender 5.2 runtime compatibility

The existing workflow is the reference implementation for the runtime. Preserve these characteristics unless there is a measured reason to change them:

- Blender 5.2.2 official Linux x64 archive.
- Published SHA-256 checksum verification.
- Cached Blender runtime and Python dependencies.
- Xvfb for headless execution.
- software OpenGL via `LIBGL_ALWAYS_SOFTWARE=1`.
- dummy SDL audio driver.
- Blender headless verification before a render.
- ffmpeg H.264 MP4 generation from PNG frames.

When Blender 5.2 API behavior differs from older Blender versions, prefer a Blender 5.2-native solution rather than carrying obsolete compatibility code.

## Persistent results and Pages

Validated outputs are copied to `results/<experiment-id>/` by the workflow.

`tools/build_pages.py` regenerates the static Pages site under `docs/` from `results/`. Do not hand-maintain result cards if the generator can represent the result.

The gallery should remain snapshot-first: show a preview image initially, and load/play the MP4 only after user interaction.

Do not assume the Pages hostname is `2rwa.github.io`. On a fork, derive or report the current repository's Pages URL when possible.

## Git and GitHub behavior

When GitHub write tools or normal git credentials are available, commit completed changes to the current repository. Before writing, refresh the current branch/head so concurrent Actions result commits are not overwritten.

Generated result commits and Pages rebuild commits may be written by GitHub Actions. Expect concurrent writers and preserve the workflow's fetch/rebase or rebuild-on-latest-main behavior.

Do not decide GitHub operations are impossible merely because a local/container checkout lacks credentials. Check the actually available GitHub integration/tools first.

## Clean clone / fork expectations

For a clean local clone, source inspection and Python preflight should work without any external project files.

For a fork on GitHub, the owner may need to enable GitHub Actions and GitHub Pages and allow the workflow permissions needed for contents write and Pages deployment. Those are repository settings, not source dependencies.

The repository itself should contain everything needed to understand, modify, render through Actions, validate, persist results, and build the Pages gallery.

## Default task when no specific experiment is requested

If the user only says to continue or test the repository:

1. Inspect the latest Actions runs and repository state.
2. Confirm the `hello-blender52` baseline still passes end-to-end.
3. If it passes, choose a small Blender 5.2-specific experiment that exercises one additional capability without breaking the baseline.
4. Add validation for that capability.
5. Run it through the existing workflow.
6. Inspect the real rendered artifact/result, not only the workflow conclusion.
7. Keep the repository documentation current.

## Success criteria

A change is complete only when the relevant source is committed and the actual user-visible or machine-verifiable result has been checked. For render work, a green syntax check alone is not completion.
