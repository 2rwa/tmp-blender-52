from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "ocean-wave-bake"
EXPECTED_FRAMES = 24
EXPECTED_SIZE = (640, 360)


def require(path: Path, size: int = 1) -> None:
    if not path.is_file():
        raise SystemExit(f"missing: {path}")
    if path.stat().st_size < size:
        raise SystemExit(f"too small: {path} ({path.stat().st_size})")


def main() -> None:
    report_path = OUT / f"{EXPERIMENT}-report.json"
    preview_path = OUT / "preview.png"
    video_path = OUT / f"{EXPERIMENT}.mp4"
    blend_path = OUT / f"{EXPERIMENT}.blend"

    require(OUT / "blender-version.txt")
    require(report_path, 700)
    require(preview_path, 5_000)
    require(video_path, 5_000)
    require(blend_path, 80_000)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not str(report.get("blender_version", "")).startswith("5.2.2"):
        raise SystemExit("unexpected Blender version")
    if report.get("engine") != "CYCLES":
        raise SystemExit("expected Cycles")
    if report.get("frame_count") != EXPECTED_FRAMES:
        raise SystemExit("unexpected frame count")
    if report.get("resolution") != list(EXPECTED_SIZE):
        raise SystemExit("unexpected resolution")
    if report.get("bake_size") < 128:
        raise SystemExit("wave bake unexpectedly small")

    frames = sorted(FRAMES.glob("frame_*.png"))
    if len(frames) != EXPECTED_FRAMES:
        raise SystemExit(f"wrong frame count: {len(frames)}")
    if hashlib.sha256(frames[0].read_bytes()).digest() == hashlib.sha256(frames[-1].read_bytes()).digest():
        raise SystemExit("ocean animation did not change")

    with Image.open(preview_path) as img:
        img.load()
        if img.size != EXPECTED_SIZE:
            raise SystemExit(f"wrong preview size: {img.size}")
        gray = img.convert("L")
        stat = ImageStat.Stat(gray)
        mean = float(stat.mean[0])
        std = float(stat.stddev[0])
        span = gray.getextrema()[1] - gray.getextrema()[0]

    if not 10 <= mean <= 235:
        raise SystemExit(f"implausible luminance: {mean:.2f}")
    if std < 8:
        raise SystemExit(f"preview too uniform: {std:.2f}")
    if span < 40:
        raise SystemExit(f"preview tonal span too small: {span}")

    result = {
        "experiment": EXPERIMENT,
        "variant_id": report.get("variant_id"),
        "variant_name": report.get("variant_name"),
        "frame_count": len(frames),
        "resolution": list(EXPECTED_SIZE),
        "mean_luma": round(mean, 3),
        "stddev": round(std, 3),
        "tonal_span": span,
        "video_size_bytes": video_path.stat().st_size,
        "blend_size_bytes": blend_path.stat().st_size,
        "wave_bake": True,
        "motion_present": True,
    }
    (OUT / "validation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
