from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from scripts.doorway_utils import (
    atomic_write,
    canonical_paths,
    content_unchanged,
    next_versioned,
    render_md_with_anchors,
)

PY = sys.executable


def _generate_tasks_body_from_prd(prd_path: str) -> str:
    # Delegate to the existing automation if available; otherwise produce a minimal stub.
    try:
        out = subprocess.check_output(
            [
                PY,
                "scripts/task_generation_automation.py",
                "--prd",
                prd_path,
                "--output",
                "task-list",
            ],
            text=True,
        )
        return out
    except Exception:
        return "\n\n## Tasks\n\n- T-1 Do the thing\n- T-2 Verify with tests\n"


def generate(backlog_id: str) -> str:
    # Derive paths by finding the PRD path for this backlog_id
    import re
    from glob import glob

    prds = sorted(glob(f"000_core/PRD-{backlog_id}-*.md"))
    if not prds:
        raise SystemExit(f"No PRD found for {backlog_id}")
    m = re.match(rf"000_core/PRD-{backlog_id}-(.+)\.md$", prds[0])
    slug = m.group(1) if m else backlog_id

    paths = canonical_paths(backlog_id, slug)
    tasks_path = Path(paths["tasks"])  # active TASKS path

    body = _generate_tasks_body_from_prd(prds[0])
    anchors = {
        "BACKLOG_ID": backlog_id,
        "FILE_TYPE": "tasks",
        "SLUG": slug,
        "ROADMAP_REFERENCE": "000_core/004_development-roadmap.md",
    }
    content = render_md_with_anchors(f"TASKS {backlog_id}: {slug}", anchors, body)

    out_path = tasks_path
    if tasks_path.exists() and not content_unchanged(str(tasks_path), content):
        out_path = Path(next_versioned(str(tasks_path)))

    atomic_write(str(out_path), content)
    print(f"[TASKS] Created {out_path.name}")
    return str(out_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("backlog_id")
    args = ap.parse_args()
    generate(args.backlog_id)


if __name__ == "__main__":
    main()
