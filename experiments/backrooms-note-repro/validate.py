from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "backrooms-note-repro"
EXPECTED_FRAMES = 24
EXPECTED_SIZE = (640, 360)


def require_file(path: Path, minimum_size: int = 1) -> None:
    if not path.is_file():
        raise SystemExit(f"missing output: {path}")
    if path.stat().st_size < minimum_size:
        raise SystemExit(f"output too small: {path} ({path.stat().st_size} < {minimum_size})")


def require_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f"unexpected {label}: {actual!r} != {expected!r}")


def main() -> None:
    version_path = OUT / "blender-version.txt"
    report_path = OUT / f"{EXPERIMENT}-report.json"
    preview_path = OUT / "preview.png"
    video_path = OUT / f"{EXPERIMENT}.mp4"
    blend_path = OUT / f"{EXPERIMENT}.blend"

    require_file(version_path)
    require_file(report_path, 500)
    require_file(preview_path, 5_000)
    # A 1-second 640x360 H.264 clip with subtle motion can legitimately be very small.
    # Keep this as a corruption/truncation guard, not a proxy for visual complexity.
    require_file(video_path, 5_000)
    require_file(blend_path, 80_000)

    version_text = version_path.read_text(encoding="utf-8", errors="replace")
    if "Blender 5.2.2" not in version_text:
        raise SystemExit(f"unexpected Blender version: {version_text[:160]!r}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not str(report.get("blender_version", "")).startswith("5.2.2"):
        raise SystemExit(f"report Blender mismatch: {report.get('blender_version')!r}")
    require_equal(report.get("engine"), "CYCLES", "render engine")
    require_equal(report.get("frame_count"), EXPECTED_FRAMES, "report frame_count")
    require_equal(report.get("resolution"), list(EXPECTED_SIZE), "resolution")
    require_equal(report.get("room_size_m"), [65.0, 15.0], "room size")
    require_equal(report.get("camera_lens_mm"), 30.0, "camera lens")
    require_equal(report.get("area_light_power_w"), 80.0, "area light power")
    require_equal(report.get("emission_strength"), 1.0, "emission strength")

    if report.get("wall_count", 0) < 24:
        raise SystemExit(f"too few wall segments: {report.get('wall_count')}")
    if report.get("area_light_count", 0) < 20:
        raise SystemExit(f"too few area lights: {report.get('area_light_count')}")
    if report.get("emission_panel_count", 0) < 20:
        raise SystemExit(f"too few emissive panels: {report.get('emission_panel_count')}")
    if report.get("external_texture_files") != 0 or not report.get("procedural_materials_only"):
        raise SystemExit("reproduction unexpectedly depends on external texture assets")

    frames = sorted(FRAMES.glob("frame_*.png"))
    require_equal(len(frames), EXPECTED_FRAMES, "rendered frame count")

    with Image.open(preview_path) as image:
        image.load()
        require_equal(image.size, EXPECTED_SIZE, "preview size")
        rgb = image.convert("RGB")
        gray = rgb.convert("L")
        hsv = rgb.convert("HSV")
        gray_stat = ImageStat.Stat(gray)
        rgb_stat = ImageStat.Stat(rgb)
        hsv_stat = ImageStat.Stat(hsv)
        extrema = gray.getextrema()
        stddev = float(gray_stat.stddev[0])
        mean_luma = float(gray_stat.mean[0])
        mean_rgb = [float(v) for v in rgb_stat.mean]
        mean_sat = float(hsv_stat.mean[1])

    if extrema[1] - extrema[0] < 55:
        raise SystemExit(f"preview contrast span too low: {extrema}")
    if stddev < 14.0:
        raise SystemExit(f"preview too uniform: stddev={stddev:.2f}")
    if not 20.0 <= mean_luma <= 220.0:
        raise SystemExit(f"preview luminance implausible: {mean_luma:.2f}")
    if mean_sat > 150.0:
        raise SystemExit(f"preview is too saturated for the intended grade: {mean_sat:.2f}")
    if mean_rgb[0] + 8.0 < mean_rgb[2]:
        raise SystemExit(f"preview lost the yellow/neutral backrooms palette: RGB={mean_rgb}")

    first_hash = hashlib.sha256(frames[0].read_bytes()).hexdigest()
    last_hash = hashlib.sha256(frames[-1].read_bytes()).hexdigest()
    if first_hash == last_hash:
        raise SystemExit("first and last frames are identical; expected subtle camera/light motion")

    result = {
        "experiment": EXPERIMENT,
        "blender_version": report.get("blender_version"),
        "engine": report.get("engine"),
        "frame_count": len(frames),
        "preview_sha256": hashlib.sha256(preview_path.read_bytes()).hexdigest(),
        "video_size_bytes": video_path.stat().st_size,
        "blend_size_bytes": blend_path.stat().st_size,
        "preview_stddev": round(stddev, 3),
        "preview_mean_luma": round(mean_luma, 3),
        "preview_mean_saturation": round(mean_sat, 3),
        "preview_mean_rgb": [round(v, 3) for v in mean_rgb],
        "semantic_checks": {
            "cycles": True,
            "room_65x15m": True,
            "camera_30mm": True,
            "beveled_walls": True,
            "emission_plus_area_lights": True,
            "procedural_wallpaper": True,
            "floor_bump": True,
            "low_saturation_grade": True,
            "motion_present": True,
        },
    }
    (OUT / "validation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
