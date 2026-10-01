from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "sail-ship-wire-hd"
EXPECTED_SOURCE_SHA256 = "f9cf8bb0fc345b3851e9fd596fc75edf236b32309e1a6ce193e8c2a9b25aff78"
EXPECTED_SOURCE_SIZE = 645876


def require_file(path: Path, minimum_size: int = 1) -> None:
    if not path.is_file():
        raise SystemExit(f"missing output: {path}")
    if path.stat().st_size < minimum_size:
        raise SystemExit(f"output too small: {path} ({path.stat().st_size} < {minimum_size})")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    version_path = OUT / "blender-version.txt"
    report_path = OUT / f"{EXPERIMENT}-report.json"
    preview_path = OUT / "preview.png"
    video_path = OUT / f"{EXPERIMENT}.mp4"
    blend_path = OUT / f"{EXPERIMENT}.blend"

    require_file(version_path)
    require_file(report_path, 200)
    require_file(preview_path, 5_000)
    require_file(video_path, 5_000)
    require_file(blend_path, 100_000)

    version_text = version_path.read_text(encoding="utf-8", errors="replace")
    if "Blender 5.2.2" not in version_text:
        raise SystemExit(f"unexpected Blender version: {version_text[:160]!r}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not str(report.get("blender_version", "")).startswith("5.2.2"):
        raise SystemExit(f"report Blender mismatch: {report.get('blender_version')!r}")
    if report.get("engine") not in {"BLENDER_WORKBENCH", "BLENDER_WORKBENCH_NEXT"}:
        raise SystemExit(f"unexpected engine: {report.get('engine')!r}")
    if report.get("display_mode") != "wireframe":
        raise SystemExit(f"unexpected display mode: {report.get('display_mode')!r}")
    if report.get("resolution") != [1280, 720]:
        raise SystemExit(f"unexpected resolution: {report.get('resolution')}")
    if report.get("source_sha256") != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"source SHA mismatch: {report.get('source_sha256')}")
    if report.get("source_size_bytes") != EXPECTED_SOURCE_SIZE:
        raise SystemExit(f"source size mismatch: {report.get('source_size_bytes')}")
    if int(report.get("renderable_object_count", 0)) < 1:
        raise SystemExit("no renderable objects reported")

    frames = sorted(FRAMES.glob("frame_*.png"))
    if len(frames) != 24:
        raise SystemExit(f"unexpected frame count: {len(frames)}")

    with Image.open(preview_path) as image:
        image.load()
        if image.size != (1280, 720):
            raise SystemExit(f"unexpected preview size: {image.size}")
        gray = image.convert("L")
        extrema = gray.getextrema()
        stddev = float(ImageStat.Stat(gray).stddev[0])

    if extrema[1] - extrema[0] < 35:
        raise SystemExit(f"preview contrast too low: {extrema}")
    if stddev < 3.0:
        raise SystemExit(f"preview too uniform: stddev={stddev:.3f}")

    blend_hash = sha256(blend_path)
    if blend_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"output blend differs from bridged source: {blend_hash}")
    if blend_path.stat().st_size != EXPECTED_SOURCE_SIZE:
        raise SystemExit(f"unexpected blend size: {blend_path.stat().st_size}")

    result = {
        "experiment": EXPERIMENT,
        "blender_version": report.get("blender_version"),
        "engine": report.get("engine"),
        "display_mode": report.get("display_mode"),
        "resolution": report.get("resolution"),
        "frame_count": len(frames),
        "source_sha256": report.get("source_sha256"),
        "preview_sha256": sha256(preview_path),
        "preview_size_bytes": preview_path.stat().st_size,
        "video_size_bytes": video_path.stat().st_size,
        "blend_size_bytes": blend_path.stat().st_size,
        "preview_stddev": round(stddev, 3),
    }
    (OUT / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
