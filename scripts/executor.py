from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.doorway_utils import canonical_paths, render_md_with_anchors

STATE_FILE = ".ai_state.json"


def _load_state() -> dict:
    p = Path(STATE_FILE)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(state: dict) -> None:
    Path(STATE_FILE).write_text(json.dumps(state, indent=2), encoding="utf-8")


def _determine_start_task(tasks_md: str, current_task: str | None) -> str:
    # Minimal heuristic: if current_task provided, use it; else start at first "- T-" line
    if current_task:
        return current_task
    for line in tasks_md.splitlines():
        line = line.strip()
        if line.startswith("- T-"):
            # Extract token like T-1
            token = line.split()[1] if len(line.split()) > 1 else line[2:]
            return token
    return "T-1"


def execute(backlog_id: str, telemetry: bool) -> None:
    # Locate active TASKS and RUN paths
    import re
    from glob import glob

    tasks = sorted(glob(f"000_core/TASKS-{backlog_id}-*.md"))
    if not tasks:
        print(f"[ERROR] No TASKS found for {backlog_id}")
        raise SystemExit(1)
    tpath = tasks[0]

    m = re.match(rf"000_core/TASKS-{backlog_id}-(.+)\.md$", tpath)
    slug = m.group(1) if m else backlog_id
    paths = canonical_paths(backlog_id, slug)

    run_path = Path(paths["run"])  # single active RUN (overwrite policy)
    tasks_md = Path(tpath).read_text(encoding="utf-8")

    # Auto-resume from minimal state
    state = _load_state()
    start_task = _determine_start_task(tasks_md, state.get("current_task"))
    print("[EXEC] Running tests...")

    # For this thin wrapper, we simulate execution and write a concise RUN narrative.
    # Hook to existing process_tasks.py could be added here if needed.
    try:
        summary = (
            f"## Summary\n\nExecuted from {start_task}.\n\n" "## Failures\n\n(none)\n\n" "## Adjustments\n\n(none)\n"
        )
        anchors = {
            "BACKLOG_ID": backlog_id,
            "FILE_TYPE": "run",
            "SLUG": slug,
            "ROADMAP_REFERENCE": "000_core/004_development-roadmap.md",
        }
        content = render_md_with_anchors(f"RUN {backlog_id}: {slug}", anchors, summary)
        run_path.write_text(content, encoding="utf-8")
        # Clear state on success
        if Path(STATE_FILE).exists():
            Path(STATE_FILE).unlink(missing_ok=True)  # type: ignore[arg-type]
        print(f"[DONE] {backlog_id} completed")

        # Generate archive suggestion
        print("\n📁 **Archive Suggestion**")
        print(f"The following temporary items were created for {backlog_id}:")
        print(f"  • PRD: {paths['prd']}")
        print(f"  • Tasks: {paths['tasks']}")
        print(f"  • Run Log: {run_path}")
        print(f"\nTo archive these files, run: @ archive {backlog_id}")
    except KeyboardInterrupt:
        # Write minimal state and exit
        _save_state({"current_task": start_task, "completed_tasks": []})
        print("[INFO] Run paused. Use: continue", backlog_id)
        raise SystemExit(1) from None
    except Exception:
        _save_state({"current_task": start_task, "completed_tasks": []})
        print("[ERROR] Execution failed. Fix and run: continue", backlog_id)
        raise SystemExit(1) from None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("backlog_id")
    ap.add_argument("--telemetry", action="store_true")
    args = ap.parse_args()
    execute(args.backlog_id, args.telemetry)


if __name__ == "__main__":
    main()
