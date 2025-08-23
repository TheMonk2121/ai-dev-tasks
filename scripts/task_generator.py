from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from subprocess import TimeoutExpired

from scripts.doorway_utils import (
    atomic_write,
    canonical_paths,
    content_unchanged,
    next_versioned,
    render_md_with_anchors,
)

PY = sys.executable

def _generate_tasks_body_from_prd(prd_path: str, timeout_s: int = 12) -> str:
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
            timeout=timeout_s,
        )
        return out
    except TimeoutExpired:
        return "\n\n## Tasks\n\n- T-1 Implement\n- T-2 Test\n"
    except Exception:
        return "\n\n## Tasks\n\n- T-1 Do the thing\n- T-2 Verify with tests\n"

def generate(backlog_id: str, timeout_s: int = 12) -> str:
    # Derive paths by finding the PRD path for this backlog_id
    import re
    from glob import glob

    prds = sorted(glob(f"600_archives/artifacts/000_core_temp_files/PRD-{backlog_id}-*.md"))
    if not prds:
        raise SystemExit(f"No PRD found for {backlog_id}")
    m = re.match(rf"600_archives/artifacts/000_core_temp_files/PRD-{backlog_id}-(.+)\.md$", prds[0])
    slug = m.group(1) if m else backlog_id

    paths = canonical_paths(backlog_id, slug)
    tasks_path = Path(paths["tasks"])  # active TASKS path

    body = _generate_tasks_body_from_prd(prds[0], timeout_s)
    anchors = {
        "BACKLOG_ID": backlog_id,
        "FILE_TYPE": "tasks",
        "SLUG": slug,
        "ROADMAP_REFERENCE": "400_guides/400_project-overview.md",
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
    ap.add_argument("--timeout", type=int, default=12)  # NEW
    args = ap.parse_args()
    generate(args.backlog_id, args.timeout)

if __name__ == "__main__":
    main()
