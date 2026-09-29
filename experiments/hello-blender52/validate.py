from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "hello-blender52"


def require_file(path: Path, minimum_size: int = 1) -> None:
    if not path.is_file():
        raise SystemExit(f"missing output: {path}")
    if path.stat().st_size < minimum_size:
        raise SystemExit(
            f"output too small: {path} ({path.stat().st_size} < {minimum_size})"
        )


def main() -> None:
    version_path = OUT / "blender-version.txt"
    report_path = OUT / f"{EXPERIMENT}-report.json"
    preview_path = OUT / "preview.png"
    video_path = OUT / f"{EXPERIMENT}.mp4"
    blend_path = OUT / f"{EXPERIMENT}.blend"

    require_file(version_path)
    require_file(report_path, 100)
    require_file(preview_path, 2_000)
    require_file(video_path, 5_000)
    require_file(blend_path, 50_000)

    version_text = version_path.read_text(encoding="utf-8", errors="replace")
    if "Blender 5.2.2" not in version_text:
        raise SystemExit(f"unexpected Blender version: {version_text[:160]!r}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not str(report.get("blender_version", "")).startswith("5.2.2"):
        raise SystemExit(
            f"report Blender mismatch: {report.get('blender_version')!r}"
        )

    frames = sorted(FRAMES.glob("frame_*.png"))
    if len(frames) != 48:
        raise SystemExit(f"unexpected frame count: {len(frames)}")

    if report.get("frame_count") != 48:
        raise SystemExit(f"unexpected report frame_count: {report.get('frame_count')}")

    if report.get("resolution") != [480, 360]:
        raise SystemExit(f"unexpected resolution: {report.get('resolution')}")

    with Image.open(preview_path) as image:
        image.load()
        if image.size != (480, 360):
            raise SystemExit(f"unexpected preview size: {image.size}")
        gray = image.convert("L")
        extrema = gray.getextrema()
        stat = ImageStat.Stat(gray)
        stddev = float(stat.stddev[0])

    if extrema[1] - extrema[0] < 45:
        raise SystemExit(f"preview contrast too low: {extrema}")
    if stddev < 9.0:
        raise SystemExit(f"preview too uniform: {stddev:.2f}")

    result = {
        "experiment": EXPERIMENT,
        "blender_version": report.get("blender_version"),
        "engine": report.get("engine"),
        "frame_count": len(frames),
        "preview_sha256": hashlib.sha256(preview_path.read_bytes()).hexdigest(),
        "video_size_bytes": video_path.stat().st_size,
        "blend_size_bytes": blend_path.stat().st_size,
        "preview_stddev": round(stddev, 3),
    }

    (OUT / "validation.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
