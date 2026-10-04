from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "sweep-results")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "sweep-comparison")
OUT.mkdir(parents=True, exist_ok=True)

THUMB = (640, 360)
LABEL_H = 58
COLS = 2


def band_ratio(image: Image.Image) -> float:
    gray = image.convert("L")
    w, h = gray.size
    px = gray.load()
    y0 = int(h * 0.22)
    y1 = int(h * 0.42)
    ratio = 0.0
    for yy in range(y0, y1):
        dark = sum(1 for xx in range(w) if px[xx, yy] < 55)
        ratio = max(ratio, dark / w)
    return ratio


items = []
for variant_file in ROOT.rglob("variant.json"):
    info = json.loads(variant_file.read_text(encoding="utf-8"))
    preview = variant_file.parent / "preview.png"
    if preview.is_file():
        items.append((int(info["variant"]), info, preview))
items.sort()

if len(items) != 10:
    raise SystemExit(f"expected 10 variants, found {len(items)}")

font = ImageFont.load_default()
metrics = []
tiles = []

for variant, info, path in items:
    with Image.open(path) as src:
        image = src.convert("RGB")
        ratio = band_ratio(image)
        stat = ImageStat.Stat(image.convert("L"))
        mean = float(stat.mean[0])
        std = float(stat.stddev[0])
        image.thumbnail(THUMB)
        tile = Image.new("RGB", (THUMB[0], THUMB[1] + LABEL_H), "white")
        tile.paste(image, ((THUMB[0] - image.width) // 2, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((8, THUMB[1] + 8), f"V{variant:02d} {info['name']}", fill="black", font=font)
        draw.text((8, THUMB[1] + 30), f"dark-band={ratio:.3f}  mean={mean:.1f}  std={std:.1f}", fill="black", font=font)
        tiles.append(tile)
        metrics.append({
            "variant": variant,
            "name": info["name"],
            "description": info["description"],
            "dark_band_ratio": round(ratio, 4),
            "mean_luma": round(mean, 2),
            "stddev_luma": round(std, 2),
        })

rows = (len(tiles) + COLS - 1) // COLS
sheet = Image.new("RGB", (THUMB[0] * COLS, (THUMB[1] + LABEL_H) * rows), "white")
for i, tile in enumerate(tiles):
    x = (i % COLS) * THUMB[0]
    y = (i // COLS) * (THUMB[1] + LABEL_H)
    sheet.paste(tile, (x, y))

sheet.save(OUT / "contact-sheet.jpg", quality=91, optimize=True)
metrics.sort(key=lambda item: item["dark_band_ratio"])
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(metrics, indent=2, ensure_ascii=False))
