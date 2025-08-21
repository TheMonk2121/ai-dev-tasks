from __future__ import annotations

import argparse
import contextlib
import glob
import os
import platform
import shutil
import subprocess
import sys


def _select_python() -> str:
    # Prefer explicit env, then python3.12 if present, else current interpreter
    if os.environ.get("PYTHON"):
        return os.environ["PYTHON"]
    py312 = shutil.which("python3.12")
    if py312:
        return py312
    return sys.executable


PY = _select_python()


def _run(*args: str, capture: bool = False) -> str | None:
    env = os.environ.copy()
    cwd = os.getcwd()
    env["PYTHONPATH"] = f"{cwd}:{env.get('PYTHONPATH','')}" if env.get("PYTHONPATH") else cwd
    if capture:
        return subprocess.check_output([PY, *args], text=True, env=env).strip()
    subprocess.check_call([PY, *args], env=env)
    return None


def cmd_generate(description: str, telemetry: bool, no_roadmap_advisory: bool) -> None:
    # FORCE PRE-WORKFLOW ENFORCEMENT
    print("🚀 ENFORCING PRE-WORKFLOW REQUIREMENTS...")
    try:
        _run("scripts/pre_workflow_hook.py", f"workflow generation: {description}", "planner", "smoke")
    except subprocess.CalledProcessError:
        print("❌ Pre-workflow enforcement failed - cannot proceed")
        sys.exit(1)

    intake_args: list[str] = ["scripts/backlog_intake.py", description]
    if no_roadmap_advisory:
        intake_args.append("--no-roadmap-advisory")
    backlog_id = _run(*intake_args, capture=True)
    assert backlog_id, "backlog_intake.py must print the backlog ID"

    _run("scripts/prd_generator.py", backlog_id)
    _run("scripts/task_generator.py", backlog_id)

    exec_args: list[str] = ["scripts/executor.py", backlog_id]
    if telemetry:
        exec_args.append("--telemetry")
    _run(*exec_args)


def cmd_continue(backlog_id: str, telemetry: bool) -> None:
    args: list[str] = ["scripts/executor.py", backlog_id]
    if telemetry:
        args.append("--telemetry")
    _run(*args)


def cmd_archive(backlog_id: str) -> None:
    _run("scripts/archive_move.py", backlog_id)


def cmd_open(backlog_id: str) -> None:
    patterns = [
        f"600_archives/artifacts/000_core_temp_files/PRD-{backlog_id}-*.md",
        f"600_archives/artifacts/000_core_temp_files/TASKS-{backlog_id}-*.md",
        f"600_archives/artifacts/000_core_temp_files/RUN-{backlog_id}-*.md",
    ]
    files: list[str] = []
    for pat in patterns:
        files.extend(sorted(glob.glob(pat)))

    for f in files:
        print(f)

    if not files:
        return

    sysname = platform.system()
    if sysname == "Darwin":
        opener = ["open"]
    elif sysname == "Windows":
        opener = ["cmd", "/c", "start", ""]
    else:
        opener = ["xdg-open"]

    with contextlib.suppress(Exception):
        subprocess.Popen([*opener, files[0]])


def main() -> None:
    parser = argparse.ArgumentParser(prog="single_doorway")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("description")
    g.add_argument("--telemetry", action="store_true")
    g.add_argument("--no-roadmap-advisory", action="store_true")

    c = sub.add_parser("continue")
    c.add_argument("backlog_id")
    c.add_argument("--telemetry", action="store_true")

    a = sub.add_parser("archive")
    a.add_argument("backlog_id")

    o = sub.add_parser("open")
    o.add_argument("backlog_id")

    args = parser.parse_args()

    if args.cmd == "generate":
        cmd_generate(args.description, args.telemetry, args.no_roadmap_advisory)
    elif args.cmd == "continue":
        cmd_continue(args.backlog_id, args.telemetry)
    elif args.cmd == "archive":
        cmd_archive(args.backlog_id)
    elif args.cmd == "open":
        cmd_open(args.backlog_id)


if __name__ == "__main__":
    main()
