from __future__ import annotations

from pathlib import Path

from scripts.doorway_utils import (
    ANCHOR_KEYS,
    atomic_write,
    canonical_paths,
    content_unchanged,
    detect_duplicates,
    next_versioned,
    render_md_with_anchors,
    slugify,
)

def test_slugify_and_paths(tmp_path: Path) -> None:
    slug = slugify("Fix the notification system!")
    assert slug == "Fix-The-Notification-System"
    paths = canonical_paths("B-097", slug)
    assert paths["prd"].endswith("PRD-B-097-Fix-The-Notification-System.md")

def test_atomic_write_and_versioning(tmp_path: Path) -> None:
    p = tmp_path / "file.md"
    atomic_write(str(p), "a")
    assert p.read_text() == "a"
    assert content_unchanged(str(p), "a")
    v2 = next_versioned(str(p))
    assert v2.endswith("-v2.md")

def test_dedupe_simple() -> None:
    existing = [("B-001", "Fix notifications"), ("B-002", "Add metrics")]
    exact, fuzzy = detect_duplicates("fix notifications", existing)
    assert "B-001" in exact
    assert "B-002" not in exact
    assert isinstance(fuzzy, list)

def test_render_md_with_anchors() -> None:
    md = render_md_with_anchors(
        "PRD Title",
        {
            "BACKLOG_ID": "B-123",
            "FILE_TYPE": "prd",
            "SLUG": "X",
            "ROADMAP_REFERENCE": "400_guides/400_project-overview.md",
        },
        "Body",
    )
    lines = md.splitlines()
    assert lines[0].startswith("# ")
    for k in ANCHOR_KEYS:
        assert any(f"<!-- {k}:" in ln for ln in lines)
