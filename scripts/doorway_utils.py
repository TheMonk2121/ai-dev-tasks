from __future__ import annotations

import os
import re
import tempfile
from datetime import date
from difflib import SequenceMatcher


# ---------- Naming / Slugs / Paths ----------
def slugify(title: str) -> str:
    """Convert an arbitrary title into Capitalized-Kebab form."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")
    return "-".join(word.capitalize() for word in cleaned.split("-") if word)


def canonical_paths(backlog_id: str, slug: str) -> dict[str, str]:
    """Return canonical active and archive paths for PRD/TASKS/RUN files."""
    return {
        "prd": f"000_core/PRD-{backlog_id}-{slug}.md",
        "tasks": f"000_core/TASKS-{backlog_id}-{slug}.md",
        "run": f"000_core/RUN-{backlog_id}-{slug}.md",
        "arch_prd": f"600_archives/prds/PRD-{backlog_id}-{slug}.md",
        "arch_tasks": f"600_archives/tasks/TASKS-{backlog_id}-{slug}.md",
        "arch_run": f"600_archives/runs/RUN-{backlog_id}-{slug}_{date.today():%Y-%m-%d}.md",
    }


# ---------- Safe IO ----------
def atomic_write(path: str, text: str) -> None:
    """Write text to path atomically (via temporary file + rename)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path) or ".")
    os.close(fd)
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp_path, path)


def content_unchanged(path: str, text: str) -> bool:
    """Return True if the file exists and content is identical to text."""
    return os.path.exists(path) and open(path, encoding="utf-8").read() == text


def next_versioned(path: str) -> str:
    """Return the next -vN filename (starting at -v2) that doesn't exist."""
    base, ext = os.path.splitext(path)
    n = 2
    while True:
        candidate = f"{base}-v{n}{ext}"
        if not os.path.exists(candidate):
            return candidate
        n += 1


# ---------- Dedupe (Live Backlog only) ----------
def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", text.lower())).strip()


def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def detect_duplicates(
    title: str, existing: list[tuple[str, str]]
) -> tuple[list[str], list[str]]:
    """
    Detect duplicates within the Live Backlog.

    existing: list of (backlog_id, title)
    Returns (exact_ids, fuzzy_ids) using a 0.85 threshold.
    """
    normalized = _norm(title)
    exact = [bid for bid, ttl in existing if _norm(ttl) == normalized]
    fuzzy = [
        bid
        for bid, ttl in existing
        if _norm(ttl) != normalized and fuzzy_ratio(title, ttl) >= 0.85
    ]
    return exact, fuzzy


# ---------- Markdown anchors / H1 ----------
ANCHOR_KEYS = ("BACKLOG_ID", "FILE_TYPE", "SLUG", "ROADMAP_REFERENCE")


def render_md_with_anchors(h1: str, anchors: dict[str, str], body: str = "") -> str:
    """Render a markdown document with a single H1 and standardized anchors."""
    lines: list[str] = []
    lines.append(f"# {h1}")  # single H1
    for key in ANCHOR_KEYS:
        if key in anchors:
            lines.append(f"<!-- {key}: {anchors[key]} -->")
    lines.append("")
    if body:
        lines.append(body.rstrip() + "\n")
    else:
        lines.append("")
    return "\n".join(lines)
