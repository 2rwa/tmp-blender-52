from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat

OUT = Path("output52")
FRAMES = OUT / "frames"
FRAME_END = 36


def base(experiment):
    report_path = OUT / f"{experiment}-report.json"
    paths = {
        "version": OUT / "blender-version.txt",
        "report": report_path,
        "preview": OUT / "preview.png",
        "video": OUT / f"{experiment}.mp4",
        "blend": OUT / f"{experiment}.blend",
    }
    minimums = {"version": 1, "report": 100, "preview": 2000, "video": 5000, "blend": 50000}
    for key, path in paths.items():
        if not path.is_file() or path.stat().st_size < minimums[key]:
            raise SystemExit(f"missing/small output: {path}")

    version = paths["version"].read_text(encoding="utf-8", errors="replace")
    if "Blender 5.2.2" not in version:
        raise SystemExit(f"unexpected Blender version: {version[:120]!r}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not str(report.get("blender_version", "")).startswith("5.2.2"):
        raise SystemExit(f"report Blender mismatch: {report.get('blender_version')!r}")
    frames = sorted(FRAMES.glob("frame_*.png"))
    if len(frames) != FRAME_END:
        raise SystemExit(f"frame count mismatch: {len(frames)}")

    with Image.open(paths["preview"]) as image:
        image.load()
        if image.size != (480, 360):
            raise SystemExit(f"preview size mismatch: {image.size}")
        gray = image.convert("L")
        extrema = gray.getextrema()
        stddev = float(ImageStat.Stat(gray).stddev[0])
    if extrema[1] - extrema[0] < 25 or stddev < 5:
        raise SystemExit(f"preview lacks useful contrast: extrema={extrema}, stddev={stddev}")

    result = {
        "experiment": experiment,
        "blender_version": report.get("blender_version"),
        "engine": report.get("engine"),
        "frame_count": len(frames),
        "preview_sha256": hashlib.sha256(paths["preview"].read_bytes()).hexdigest(),
        "preview_stddev": round(stddev, 3),
        "video_size_bytes": paths["video"].stat().st_size,
        "blend_size_bytes": paths["blend"].stat().st_size,
    }
    return report, result


def run(experiment):
    report, result = base(experiment)
    feature = report.get("feature") or {}

    if experiment == "feature52-thin-wall":
        if feature.get("node_idname") != "ShaderNodeBsdfPrincipled":
            raise SystemExit(f"unexpected Principled node: {feature}")
        if feature.get("thin_wall_input_present") is not True or feature.get("thin_wall_enabled") is not True:
            raise SystemExit(f"Thin Wall feature not active: {feature}")

    elif experiment == "feature52-shader-scene-time":
        if feature.get("node_idname") != "GeometryNodeInputSceneTime":
            raise SystemExit(f"Scene Time node missing: {feature}")
        means = []
        for frame in (1, 7, 13, 19, 25, 31, 36):
            with Image.open(FRAMES / f"frame_{frame:04d}.png") as im:
                means.append(float(ImageStat.Stat(im.convert("L")).mean[0]))
        if max(means) - min(means) < 4:
            raise SystemExit(f"Scene Time render did not visibly animate: {means}")
        result["sample_luma"] = [round(v, 3) for v in means]

    elif experiment == "feature52-compositor-blank-image":
        if feature.get("node_idname") != "CompositorNodeBlankImage":
            raise SystemExit(f"Blank Image node missing: {feature}")
        if feature.get("size_socket_present") is not True:
            raise SystemExit(f"Blank Image size socket missing: {feature}")

    elif experiment == "feature52-compositor-string-to-image":
        if feature.get("node_idname") != "CompositorNodeStringToImage":
            raise SystemExit(f"String to Image node missing: {feature}")
        if feature.get("string") != "BLENDER 5.2":
            raise SystemExit(f"String to Image content mismatch: {feature}")

    else:
        raise SystemExit(f"unknown showcase experiment: {experiment}")

    result["feature"] = feature
    (OUT / "validation.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
