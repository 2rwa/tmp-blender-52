from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "yokohama-terrain"


def require_file(path: Path, minimum_size: int = 1) -> None:
    if not path.is_file():
        raise SystemExit(f"missing output: {path}")
    if path.stat().st_size < minimum_size:
        raise SystemExit(f"output too small: {path} ({path.stat().st_size} < {minimum_size})")


def main() -> None:
    version_path = OUT / "blender-version.txt"
    report_path = OUT / f"{EXPERIMENT}-report.json"
    preview_path = OUT / "preview.png"
    video_path = OUT / f"{EXPERIMENT}.mp4"
    blend_path = OUT / f"{EXPERIMENT}.blend"

    require_file(version_path)
    require_file(report_path, 500)
    require_file(preview_path, 4_000)
    require_file(video_path, 5_000)
    require_file(blend_path, 100_000)

    version_text = version_path.read_text(encoding="utf-8", errors="replace")
    if "Blender 5.2.2" not in version_text:
        raise SystemExit(f"unexpected Blender version: {version_text[:160]!r}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not str(report.get("blender_version", "")).startswith("5.2.2"):
        raise SystemExit(f"report Blender mismatch: {report.get('blender_version')!r}")
    if report.get("resolution") != [320, 180]:
        raise SystemExit(f"unexpected resolution: {report.get('resolution')}")
    if report.get("grid") != [96, 112]:
        raise SystemExit(f"unexpected terrain grid: {report.get('grid')}")
    if report.get("dem_zoom") != 11:
        raise SystemExit(f"unexpected DEM zoom: {report.get('dem_zoom')}")

    frames = sorted(FRAMES.glob("frame_*.png"))
    if len(frames) != 24:
        raise SystemExit(f"unexpected frame count: {len(frames)}")
    if report.get("frame_count") != 24:
        raise SystemExit(f"unexpected report frame_count: {report.get('frame_count')}")

    dem = report.get("dem", {})
    valid_ratio = float(dem.get("valid_ratio", 0.0))
    elev_min = float(dem.get("elevation_min_m", 0.0))
    elev_max = float(dem.get("elevation_max_m", 0.0))
    tile_count = int(dem.get("tile_count", 0))

    if valid_ratio < 0.45:
        raise SystemExit(f"too few valid Yokohama DEM samples: {valid_ratio:.3f}")
    if elev_max - elev_min < 40.0:
        raise SystemExit(f"terrain elevation range too small: {elev_min:.2f}..{elev_max:.2f}")
    if tile_count < 2:
        raise SystemExit(f"unexpectedly small DEM tile coverage: {tile_count}")

    with Image.open(preview_path) as image:
        image.load()
        if image.size != (320, 180):
            raise SystemExit(f"unexpected preview size: {image.size}")
        gray = image.convert("L")
        extrema = gray.getextrema()
        stat = ImageStat.Stat(gray)
        stddev = float(stat.stddev[0])

    if extrema[1] - extrema[0] < 45:
        raise SystemExit(f"preview contrast too low: {extrema}")
    if stddev < 10.0:
        raise SystemExit(f"preview too uniform: {stddev:.2f}")

    result = {
        "experiment": EXPERIMENT,
        "blender_version": report.get("blender_version"),
        "engine": report.get("engine"),
        "resolution": report.get("resolution"),
        "frame_count": len(frames),
        "dem_zoom": report.get("dem_zoom"),
        "dem_tile_count": tile_count,
        "dem_valid_ratio": round(valid_ratio, 4),
        "elevation_min_m": round(elev_min, 2),
        "elevation_max_m": round(elev_max, 2),
        "preview_sha256": hashlib.sha256(preview_path.read_bytes()).hexdigest(),
        "video_size_bytes": video_path.stat().st_size,
        "blend_size_bytes": blend_path.stat().st_size,
        "preview_stddev": round(stddev, 3),
    }
    (OUT / "validation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
