from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageStat

OUT = Path("output52-preview")
FRAMES = OUT / "frames"
EXPERIMENT = "backrooms-note-repro"
EXPECTED_FRAMES = 3
EXPECTED_SIZE = (320, 180)


def require_file(path: Path, minimum_size: int = 1) -> None:
    if not path.is_file():
        raise SystemExit(f"missing preview output: {path}")
    if path.stat().st_size < minimum_size:
        raise SystemExit(
            f"preview output too small: {path} ({path.stat().st_size} < {minimum_size})"
        )


def adjacent_edge_stats(gray: Image.Image) -> tuple[float, float]:
    pixels = gray.load()
    width, height = gray.size
    total_diff = 0
    comparisons = 0
    strong_edges = 0

    for y in range(height):
        for x in range(width - 1):
            diff = abs(pixels[x + 1, y] - pixels[x, y])
            total_diff += diff
            comparisons += 1
            if diff > 12:
                strong_edges += 1

    for y in range(height - 1):
        for x in range(width):
            diff = abs(pixels[x, y + 1] - pixels[x, y])
            total_diff += diff
            comparisons += 1
            if diff > 12:
                strong_edges += 1

    return total_diff / comparisons, strong_edges / comparisons


def main() -> None:
    report_path = OUT / f"{EXPERIMENT}-report.json"
    preview_path = OUT / "preview.png"

    require_file(report_path, 500)
    require_file(preview_path, 2_000)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not report.get("fast_preview"):
        raise SystemExit("preview scene did not run in fast-preview mode")
    if report.get("frame_count") != EXPECTED_FRAMES:
        raise SystemExit(f"unexpected preview frame count: {report.get('frame_count')}")
    if report.get("resolution") != list(EXPECTED_SIZE):
        raise SystemExit(f"unexpected preview resolution: {report.get('resolution')}")
    if not str(report.get("blender_version", "")).startswith("5.2.2"):
        raise SystemExit(f"unexpected Blender version: {report.get('blender_version')!r}")

    center_ray = float(report.get("center_ray_distance_m", 0.0))
    if center_ray < 5.0:
        raise SystemExit(f"preview camera hits a wall too soon: {center_ray:.3f} m")

    frames = sorted(FRAMES.glob("frame_*.png"))
    if len(frames) != EXPECTED_FRAMES:
        raise SystemExit(f"unexpected number of preview frames: {len(frames)}")

    with Image.open(preview_path) as image:
        image.load()
        if image.size != EXPECTED_SIZE:
            raise SystemExit(f"unexpected preview size: {image.size}")
        rgb = image.convert("RGB")
        gray = rgb.convert("L")
        stat = ImageStat.Stat(gray)
        extrema = gray.getextrema()
        mean_luma = float(stat.mean[0])
        stddev = float(stat.stddev[0])
        gradient_mean, strong_edge_fraction = adjacent_edge_stats(gray)

    if not 20.0 <= mean_luma <= 225.0:
        raise SystemExit(f"preview luminance implausible: {mean_luma:.2f}")
    if extrema[1] - extrema[0] < 50:
        raise SystemExit(f"preview tonal span too small: {extrema}")
    if stddev < 12.0:
        raise SystemExit(f"preview too uniform: stddev={stddev:.3f}")

    # The previous bad render was a close-up procedural wall.  It had useful
    # luminance statistics, but almost no geometric edges:
    # mean adjacent difference ~= 0.49 and strong-edge fraction ~= 0.
    if gradient_mean < 1.25:
        raise SystemExit(
            f"preview lacks scene structure: gradient_mean={gradient_mean:.3f}"
        )
    if strong_edge_fraction < 0.002:
        raise SystemExit(
            "preview lacks enough structural edges: "
            f"strong_edge_fraction={strong_edge_fraction:.6f}"
        )

    result = {
        "experiment": EXPERIMENT,
        "fast_preview": True,
        "resolution": list(EXPECTED_SIZE),
        "frame_count": len(frames),
        "center_ray_distance_m": center_ray,
        "mean_luma": round(mean_luma, 3),
        "stddev": round(stddev, 3),
        "gradient_mean": round(gradient_mean, 4),
        "strong_edge_fraction": round(strong_edge_fraction, 6),
        "gate": "pass",
    }
    (OUT / "preview-validation.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
