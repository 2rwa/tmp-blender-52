"""Add GitHub-hosted .blend downloads to the generated Pages gallery.

Run after tools/build_pages.py. Keep large .blend files out of Pages assets.
"""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"

STYLE = """
    .blend-download { display: inline-flex; align-items: center; margin-top: 12px;
      padding: 9px 13px; border: 1px solid #608bb8; border-radius: 9px;
      background: #203a55; color: #ecf5ff; text-decoration: none;
      font-size: .88rem; font-weight: 650; }
    .blend-download:hover, .blend-download:focus-visible {
      background: #315879; outline-offset: 3px; }
"""


def add_download_links(page: str, items: list[dict], repo: str,
                       results: Path) -> tuple[str, list[dict], int]:
    """Return patched HTML, augmented index data, count of available files."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid GitHub repository name: " + repr(repo))

    updated = []
    links = 0
    for original in items:
        item = dict(original)
        exp = item["id"]
        if not isinstance(exp, str) or exp in (".", "..") or Path(exp).name != exp:
            raise ValueError("Unsafe experiment name: " + repr(exp))
        blend_file = results / exp / (exp + ".blend")
        if blend_file.is_file():
            safe_exp = quote(exp, safe="")
            safe_repo = "/".join(quote(piece, safe="") for piece in repo.split("/"))
            url = (
                f"https://raw.githubusercontent.com/{safe_repo}/main/"
                f"results/{safe_exp}/{safe_exp}.blend"
            )
            marker = "<code>" + html.escape(exp) + "</code>"
            if page.count(marker) != 1:
                raise ValueError(f"Expected exactly one card for {exp!r}")
            href = html.escape(url, quote=True)
            # Re-runs should not append the same link twice.
            download = (
                f'<a class="blend-download" href="{href}" '
                f'aria-label="Download Blender file for {html.escape(exp, quote=True)}">'
                "&#8595; Download .blend</a>"
            )
            if download not in page:
                page = page.replace(marker, marker + "\n        " + download, 1)
            item["blend"] = url
            links += 1
        else:
            item["blend"] = None
        updated.append(item)

    if links and ".blend-download {" not in page:
        if "</style>" not in page:
            raise ValueError("Expected generated gallery CSS block")
        page = page.replace("</style>", STYLE + "  </style>", 1)
    return page, updated, links


def main() -> None:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        raise SystemExit("GITHUB_REPOSITORY must be set (e.g. 2rwa/tmp-blender-52)")
    index_file = DOCS / "index.html"
    data_file = DOCS / "data.json"
    before = index_file.read_text(encoding="utf-8")
    items = json.loads(data_file.read_text(encoding="utf-8"))
    after, updated, count = add_download_links(before, items, repo, RESULTS)
    if count == 0:
        raise SystemExit("No .blend files found: expected published results")
    index_file.write_text(after, encoding="utf-8")
    data_file.write_text(
        json.dumps(updated, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Added {count} Blender download links to Pages gallery")


if __name__ == "__main__":
    main()
