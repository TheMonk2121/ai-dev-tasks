from __future__ import annotations

import os
import re
import shutil
from glob import glob

from scripts.doorway_utils import canonical_paths


def _ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _extract_slug_from_prd_path(prd_path: str, backlog_id: str) -> str:
    m = re.match(rf"600_archives/artifacts/000_core_temp_files/PRD-{re.escape(backlog_id)}-(.+)\.md$", prd_path)
    if not m:
        raise SystemExit(f"Cannot infer slug from {prd_path}")
    return m.group(1)


def _collision_path(path: str) -> str:
    # For RUN only: add -vN if same-date file already exists
    base, ext = os.path.splitext(path)
    cand = path
    n = 2
    while os.path.exists(cand):
        cand = f"{base}-v{n}{ext}"
        n += 1
    return cand


def _find_active_paths(backlog_id: str) -> tuple[str, str, str]:
    prd = sorted(glob(f"600_archives/artifacts/000_core_temp_files/PRD-{backlog_id}-*.md"))
    tasks = sorted(glob(f"600_archives/artifacts/000_core_temp_files/TASKS-{backlog_id}-*.md"))
    run = sorted(glob(f"600_archives/artifacts/000_core_temp_files/RUN-{backlog_id}-*.md"))
    if not (prd and tasks and run):
        raise SystemExit(f"Missing files for {backlog_id}: PRD/TASKS/RUN not all present")
    return prd[0], tasks[0], run[0]


def main(backlog_id: str) -> None:
    prd_path, tasks_path, run_path = _find_active_paths(backlog_id)
    slug = _extract_slug_from_prd_path(prd_path, backlog_id)

    paths = canonical_paths(backlog_id, slug)
    dst_prd = paths["arch_prd"]
    dst_tasks = paths["arch_tasks"]
    dst_run = _collision_path(paths["arch_run"])  # handle same-date collisions

    for src, dst in ((prd_path, dst_prd), (tasks_path, dst_tasks), (run_path, dst_run)):
        _ensure_parent(dst)
        shutil.move(src, dst)
        print(f"[ARCHIVE] {os.path.basename(dst)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/archive_move.py B-###")
    main(sys.argv[1])
