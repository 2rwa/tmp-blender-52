"""Check generated media, wheel geometry census and actual visible rotation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

OUT = Path("output52")
EXPERIMENT = "timber-waterwheel"
FRAMES = OUT / "frames"


def require_file(path, minimum):
    if not path.is_file() or path.stat().st_size < minimum:
        raise SystemExit("missing or undersized: %s" % path)


def main():
    paths = {
        "preview": OUT / "preview.png",
        "blend": OUT / (EXPERIMENT + ".blend"),
        "video": OUT / (EXPERIMENT + ".mp4"),
        "report": OUT / (EXPERIMENT + "-report.json"),
        "version": OUT / "blender-version.txt",
    }
    for kind, path in paths.items():
        require_file(path, {
            "preview": 4000, "blend": 40000, "video": 15000,
            "report": 500, "version": 5,
        }[kind])

    version = paths["version"].read_text(encoding="utf-8", errors="replace")
    if "Blender 5.2.2" not in version:
        raise SystemExit("wrong Blender runtime: " + version[:100])
    report = json.loads(paths["report"].read_text(encoding="utf-8"))
    if not report["blender_version"].startswith("5.2.2"):
        raise SystemExit("report Blender version mismatch")
    if report["frame_count"] != 48 or report["resolution"] != [768, 432]:
        raise SystemExit("wrong render settings in report")
    if report["wheel_axis"] != "Y" or report["rotation_degrees"] != 135.0:
        raise SystemExit("wheel animation wrong")
    counts = report["wheel_component_counts"]
    expected = {"rim": 48, "spoke": 24, "paddle": 16,
                "lip": 16, "bolt": 32, "hub": 3, "axle": 1}
    for component, total in expected.items():
        if counts.get(component) != total:
            raise SystemExit("wrong %s count: %s != %s" %
                             (component, counts.get(component), total))
    if report["mesh_objects"] < 160:
        raise SystemExit("expected full editable scene geometry")

    frames = sorted(FRAMES.glob("frame_*.png"))
    if len(frames) != 48:
        raise SystemExit("missing frames: %s" % len(frames))
    with Image.open(paths["preview"]) as image:
        image.load()
        if image.size != (768, 432):
            raise SystemExit("preview dimensions incorrect")
        gray = image.convert("L")
        contrast = gray.getextrema()[1] - gray.getextrema()[0]
        stddev = ImageStat.Stat(gray).stddev[0]
    if contrast < 40 or stddev < 12:
        raise SystemExit("flat/dark/empty preview: contrast=%s std=%s" %
                         (contrast, stddev))

    with Image.open(frames[0]) as first, Image.open(frames[11]) as later:
        first.load()
        later.load()
        if first.size != later.size or first.size != (768, 432):
            raise SystemExit("frame dimensions mismatch")
        diff = ImageChops.difference(first.convert("RGB"), later.convert("RGB"))
        motion_score = sum(ImageStat.Stat(diff).mean) / 3
    if motion_score < 0.8:
        raise SystemExit("rendered waterwheel appears stationary: %.4f" %
                         motion_score)

    output = {
        "experiment": EXPERIMENT,
        "status": "validated",
        "blender_version": report["blender_version"],
        "frame_count": len(frames),
        "resolution": report["resolution"],
        "mesh_objects": report["mesh_objects"],
        "wheel_component_counts": counts,
        "rotation_degrees": report["rotation_degrees"],
        "preview_contrast": contrast,
        "preview_stddev": round(stddev, 3),
        "frame_1_to_12_rgb_difference": round(motion_score, 3),
        "preview_sha256": hashlib.sha256(paths["preview"].read_bytes()).hexdigest(),
        "blend_size_bytes": paths["blend"].stat().st_size,
        "video_size_bytes": paths["video"].stat().st_size,
    }
    (OUT / "validation.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
