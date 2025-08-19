from __future__ import annotations

import argparse
from pathlib import Path

from scripts.backlog_parser import BacklogParser  # type: ignore
from scripts.doorway_utils import (
    atomic_write,
    canonical_paths,
    content_unchanged,
    next_versioned,
    render_md_with_anchors,
    slugify,
)


def _build_prd_content(backlog_id: str, slug: str) -> str:
    anchors = {
        "BACKLOG_ID": backlog_id,
        "FILE_TYPE": "prd",
        "SLUG": slug,
        "ROADMAP_REFERENCE": "000_core/004_development-roadmap.md",
    }
    body = "\n\n## TL;DR\n\nDescribe the TL;DR here.\n"
    return render_md_with_anchors(f"PRD {backlog_id}: {slug}", anchors, body)


def generate(backlog_id: str) -> str:
    # Prefer slug derived from backlog title via BacklogParser; fallback to existing PRD filename; else backlog_id
    slug: str | None = None
    try:
        parser = BacklogParser()
        tasks = parser.parse_backlog("000_core/000_backlog.md")
        for t in tasks:
            if t.id == backlog_id:
                slug = slugify(t.title)
                break
    except Exception:
        # Lightweight fallback: infer from TASKS/PRD filenames or default to backlog_id
        slug = None

    if slug is None:
        import re
        from glob import glob

        existing = sorted(glob(f"000_core/PRD-{backlog_id}-*.md"))
        if existing:
            m = re.match(rf"000_core/PRD-{backlog_id}-(.+)\.md$", existing[0])
            slug = m.group(1) if m else backlog_id
        else:
            slug = backlog_id

    paths = canonical_paths(backlog_id, slug)
    prd_path = Path(paths["prd"])  # active PRD path

    content = _build_prd_content(backlog_id, slug)
    out_path = prd_path
    if prd_path.exists() and not content_unchanged(str(prd_path), content):
        out_path = Path(next_versioned(str(prd_path)))

    atomic_write(str(out_path), content)
    print(f"[PRD] Created {out_path.name}")
    return str(out_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("backlog_id")
    args = ap.parse_args()
    generate(args.backlog_id)


if __name__ == "__main__":
    main()
