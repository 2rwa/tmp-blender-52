from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXPERIMENTS = ROOT / "experiments"
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def collect():
    items = []
    if not RESULTS.exists():
        return items

    for result_dir in sorted(p for p in RESULTS.iterdir() if p.is_dir()):
        exp = result_dir.name
        manifest = load_json(EXPERIMENTS / exp / "experiment.json", {})
        validation = load_json(result_dir / "validation.json", {})

        asset_dir = ASSETS / exp
        asset_dir.mkdir(parents=True, exist_ok=True)

        preview = None
        for name in ("preview.png", "preview.jpg"):
            if copy_if_exists(result_dir / name, asset_dir / name):
                preview = f"assets/{exp}/{name}"
                break

        video = None
        if copy_if_exists(result_dir / "media.mp4", asset_dir / "media.mp4"):
            video = f"assets/{exp}/media.mp4"

        if (result_dir / "validation.json").is_file():
            copy_if_exists(
                result_dir / "validation.json",
                asset_dir / "validation.json",
            )

        items.append({
            "id": exp,
            "title": manifest.get("title", exp),
            "description": manifest.get("description", ""),
            "preview": preview,
            "video": video,
            "validation": validation,
        })

    return items


def card(item):
    exp = html.escape(item["id"])
    title = html.escape(str(item["title"]))
    desc = html.escape(str(item["description"]))
    version = html.escape(str(item["validation"].get("blender_version", "unknown")))
    frame_count = html.escape(str(item["validation"].get("frame_count", "—")))

    media = "<div class='media empty'>No preview</div>"
    if item["preview"]:
        preview = html.escape(item["preview"], quote=True)
        if item["video"]:
            video = html.escape(item["video"], quote=True)
            media = (
                f"<button class='media play' data-video='{video}' "
                f"aria-label='Play {title}'>"
                f"<img src='{preview}' alt='{title} preview' loading='lazy'>"
                "<span>▶ Play</span></button>"
            )
        else:
            media = (
                f"<div class='media'><img src='{preview}' "
                f"alt='{title} preview' loading='lazy'></div>"
            )

    return f"""
    <article class="card" data-search="{html.escape((title + ' ' + desc + ' ' + exp).lower(), quote=True)}">
      {media}
      <div class="body">
        <h2>{title}</h2>
        <p>{desc}</p>
        <dl>
          <div><dt>Blender</dt><dd>{version}</dd></div>
          <div><dt>Frames</dt><dd>{frame_count}</dd></div>
        </dl>
        <code>{exp}</code>
      </div>
    </article>
    """


def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    ASSETS.mkdir(parents=True, exist_ok=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    items = collect()
    cards = "\n".join(card(item) for item in items)
    if not cards:
        cards = "<p class='empty-state'>No rendered results yet.</p>"

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>tmp-blender-52</title>
  <style>
    :root {{ color-scheme: dark; font-family: system-ui, sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #0c0f14; color: #e9eef7; }}
    header {{ position: sticky; top: 0; z-index: 2; padding: 20px; background: #0c0f14e8; backdrop-filter: blur(10px); border-bottom: 1px solid #252b36; }}
    h1 {{ margin: 0 0 12px; font-size: clamp(1.4rem, 4vw, 2.2rem); }}
    header p {{ margin: 0 0 14px; color: #aeb8c8; }}
    input {{ width: min(700px, 100%); padding: 12px 14px; border: 1px solid #303746; border-radius: 10px; background: #151a22; color: inherit; font: inherit; }}
    main {{ width: min(1200px, calc(100% - 28px)); margin: 24px auto 60px; display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 18px; }}
    .card {{ overflow: hidden; border: 1px solid #252c38; border-radius: 16px; background: #121720; box-shadow: 0 12px 32px #0005; }}
    .media {{ width: 100%; aspect-ratio: 4/3; border: 0; padding: 0; background: #07090d; position: relative; display: grid; place-items: center; overflow: hidden; color: inherit; }}
    .media img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .play {{ cursor: pointer; }}
    .play span {{ position: absolute; bottom: 12px; right: 12px; padding: 8px 10px; border-radius: 9px; background: #000b; font-weight: 700; }}
    video {{ width: 100%; height: 100%; object-fit: contain; background: #000; }}
    .body {{ padding: 16px; }}
    h2 {{ margin: 0 0 8px; font-size: 1.1rem; }}
    .body p {{ min-height: 3em; color: #b8c2d0; line-height: 1.5; }}
    dl {{ display: flex; gap: 18px; margin: 14px 0; }}
    dl div {{ display: grid; gap: 2px; }}
    dt {{ color: #7e8b9e; font-size: .75rem; text-transform: uppercase; }}
    dd {{ margin: 0; }}
    code {{ color: #9cc7ff; font-size: .8rem; overflow-wrap: anywhere; }}
    .empty-state {{ color: #aeb8c8; }}
  </style>
</head>
<body>
  <header>
    <h1>tmp-blender-52</h1>
    <p>Blender 5.2 GitHub Actions render gallery — snapshot first, click to play.</p>
    <input id="search" type="search" placeholder="Filter experiments…" autocomplete="off">
  </header>
  <main id="grid">
    {cards}
  </main>
  <script>
    const search = document.querySelector('#search');
    search?.addEventListener('input', () => {{
      const q = search.value.trim().toLowerCase();
      document.querySelectorAll('.card').forEach(card => {{
        card.hidden = q && !card.dataset.search.includes(q);
      }});
    }});
    document.addEventListener('click', event => {{
      const button = event.target.closest('button[data-video]');
      if (!button) return;
      const video = document.createElement('video');
      video.src = button.dataset.video;
      video.controls = true;
      video.autoplay = true;
      video.playsInline = true;
      button.replaceWith(video);
    }});
  </script>
</body>
</html>
"""
    (DOCS / "index.html").write_text(page, encoding="utf-8")
    (DOCS / "data.json").write_text(
        json.dumps(items, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Built Pages gallery: {len(items)} result(s)")


if __name__ == "__main__":
    main()
