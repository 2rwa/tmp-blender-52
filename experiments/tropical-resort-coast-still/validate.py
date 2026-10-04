from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageStat

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "tropical-resort-coast-still"
EXPECTED_SIZE = (960, 540)


def require(path: Path, minimum_size: int = 1) -> None:
    if not path.is_file():
        raise SystemExit(f"missing: {path}")
    if path.stat().st_size < minimum_size:
        raise SystemExit(f"too small: {path} ({path.stat().st_size} < {minimum_size})")


def rgb_mean(image: Image.Image) -> tuple[float, float, float]:
    stat = ImageStat.Stat(image.convert("RGB"))
    return tuple(float(v) for v in stat.mean[:3])


def distance(a, b) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def main() -> None:
    preview = OUT / "preview.png"
    frame = FRAMES / "frame_0001.png"
    report_path = OUT / f"{EXPERIMENT}-report.json"
    video = OUT / f"{EXPERIMENT}.mp4"
    blend = OUT / f"{EXPERIMENT}.blend"

    require(OUT / "blender-version.txt")
    require(preview, 18_000)
    require(frame, 18_000)
    require(report_path, 700)
    require(video, 1_000)
    require(blend, 100_000)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not str(report.get("blender_version", "")).startswith("5.2.2"):
        raise SystemExit(f"unexpected Blender: {report.get('blender_version')!r}")
    if report.get("engine") != "CYCLES":
        raise SystemExit("expected Cycles")
    if report.get("frame_count") != 1 or not report.get("still_only"):
        raise SystemExit("expected one-frame still experiment")

    ocean = report.get("ocean", {})
    if ocean.get("spectrum") != "SHORELINE_GERSTNER_PROXY":
        raise SystemExit(f"expected shoreline-following water mesh: {ocean}")
    if ocean.get("shoreline_following") is not True:
        raise SystemExit(f"water mesh must follow shoreline: {ocean}")

    with Image.open(preview) as image:
        image.load()
        if image.size != EXPECTED_SIZE:
            raise SystemExit(f"wrong preview size: {image.size}")
        rgb = image.convert("RGB")
        gray = rgb.convert("L")
        stat = ImageStat.Stat(gray)
        mean = float(stat.mean[0])
        std = float(stat.stddev[0])
        span = gray.getextrema()[1] - gray.getextrema()[0]

        w, h = rgb.size
        sky = rgb.crop((0, 0, w, int(h * 0.30)))
        lagoon = rgb.crop((int(w * 0.18), int(h * 0.32), int(w * 0.82), int(h * 0.72)))
        foreground = rgb.crop((0, int(h * 0.72), w, h))
        sky_mean = rgb_mean(sky)
        lagoon_mean = rgb_mean(lagoon)
        foreground_mean = rgb_mean(foreground)

    if not 25.0 <= mean <= 235.0:
        raise SystemExit(f"implausible luminance: {mean:.2f}")
    if std < 20.0:
        raise SystemExit(f"image too uniform: {std:.2f}")
    if span < 90:
        raise SystemExit(f"tonal span too small: {span}")
    if sky_mean[2] <= sky_mean[0] * 1.02:
        raise SystemExit(f"sky is not blue-dominant enough: {sky_mean}")
    if (lagoon_mean[1] + lagoon_mean[2]) * 0.5 <= lagoon_mean[0] * 0.96:
        raise SystemExit(f"lagoon lost cyan/blue-green bias: {lagoon_mean}")
    if distance(sky_mean, lagoon_mean) < 5.0:
        raise SystemExit("sky and lagoon are visually indistinct")
    if distance(lagoon_mean, foreground_mean) < 6.0:
        raise SystemExit("lagoon and beach foreground are visually indistinct")

    result = {
        "experiment": EXPERIMENT,
        "created_at": "2026-10-04T19:07:00+09:00",
        "blender_version": report.get("blender_version"),
        "engine": report.get("engine"),
        "frame_count": 1,
        "still_only": True,
        "resolution": list(EXPECTED_SIZE),
        "samples": report.get("samples"),
        "spectrum": ocean.get("spectrum"),
        "mean_luma": round(mean, 3),
        "stddev_luma": round(std, 3),
        "tonal_span": span,
        "sky_rgb_mean": [round(v, 2) for v in sky_mean],
        "lagoon_rgb_mean": [round(v, 2) for v in lagoon_mean],
        "foreground_rgb_mean": [round(v, 2) for v in foreground_mean],
        "preview_sha256": hashlib.sha256(preview.read_bytes()).hexdigest(),
        "preview_size_bytes": preview.stat().st_size,
        "blend_size_bytes": blend.stat().st_size,
    }
    (OUT / "validation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
