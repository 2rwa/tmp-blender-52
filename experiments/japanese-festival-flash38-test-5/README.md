# Gemini 3.8 Flash Low: five-model controlled experiment

A separate, isolated experiment to assess generated Blender Python model quality.

- Model sources are generated without exposing repository structure, private files, or credentials to the model.
- Generation runs on a private self-hosted orchestration runner; the generated Python is validated on a secret-free ephemeral GitHub-hosted runner before it is promoted here.
- Five separate prompts target a mikoshi, ryuteki, kiseru, ceremonial hoe, and festival yagura.
- Each generated script is standalone and defines `build_model()`.
- Do not modify or replace the existing festival/performing-arts 100 model collection.
- The generated/ directory is populated only if all five candidates pass safety, structure, and Blender rendering checks.
- 500x400, 144 frames at 24 fps, six-second Workbench turntables.
- Provenance: Gemini 3.8 Flash Low via agy, then independent validation.

This is an experimental geometry dataset, not historically verified reproductions.
