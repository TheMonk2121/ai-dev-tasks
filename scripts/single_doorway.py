from __future__ import annotations

import argparse
import contextlib
import glob
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


def _select_python() -> str:
    # Prefer explicit env, then python3.12 if present, else current interpreter
    if os.environ.get("PYTHON"):
        return os.environ["PYTHON"]
    # Prefer the current interpreter (respects venv) over a global python3.12
    if sys.executable:
        return sys.executable
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


# --- Lightweight state + worklog utilities ---
STATE_FILE = Path(".ai_state.json")
WORKLOG_DIR = Path("artifacts/worklogs")


def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _current_branch() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
    except Exception:
        return ""


def _detect_backlog_id(explicit: str | None = None) -> str | None:
    if explicit:
        return explicit
    # Infer from branch name pattern like feat/B-123-...
    m = re.search(r"B-\d+", _current_branch())
    if m:
        return m.group(0)
    # Try state file
    state = _load_state()
    return state.get("backlog_id")


def _worklog_path(backlog_id: str) -> Path:
    WORKLOG_DIR.mkdir(parents=True, exist_ok=True)
    return WORKLOG_DIR / f"{backlog_id}.md"


def _append_worklog(backlog_id: str, lines: list[str]) -> None:
    path = _worklog_path(backlog_id)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    header = [f"\n## {timestamp}", ""]
    path.write_text(
        (path.read_text() if path.exists() else f"# Worklog {backlog_id}\n") + "\n".join(header + lines) + "\n"
    )


def _git_changed_files() -> list[str]:
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        files: list[str] = []
        for line in out.splitlines():
            parts = line.strip().split()
            if parts:
                files.append(parts[-1])
        return sorted(set(files))
    except Exception:
        return []


def _rehydrate(description: str, fast: bool, full: bool) -> None:
    # Prefer fast profile unless full explicitly requested
    args: list[str] = [
        "scripts/cursor_memory_rehydrate.py",
        "coder",
        description,
    ]
    if full:
        pass  # defaults in script are full-enough
    else:
        if fast:
            args.extend(["--no-rrf", "--dedupe", "file", "--expand-query", "off", "--no-entity-expansion"])
    try:
        _run(*args)
    except subprocess.CalledProcessError:
        # Non-blocking: pre_workflow_hook will enforce separately
        pass


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""


def _remote_head(branch: str) -> str:
    try:
        out = subprocess.check_output(["git", "ls-remote", "--heads", "origin", f"refs/heads/{branch}"], text=True)
        return out.split()[0] if out.strip() else ""
    except Exception:
        return ""


def cmd_generate(description: str, telemetry: bool, no_roadmap_advisory: bool, fast: bool, full: bool) -> None:
    _rehydrate(description, fast=fast, full=full)
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


def cmd_continue(backlog_id: str, telemetry: bool, fast: bool, full: bool) -> None:
    _rehydrate(f"continue {backlog_id}", fast=fast, full=full)
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


# --- Scribe implementation ---


def cmd_scribe_start(backlog_id: str | None, interval: int, fast: bool, full: bool, idle_timeout: int) -> None:
    bid = _detect_backlog_id(backlog_id)
    if not bid:
        print("❌ Cannot determine backlog_id. Provide --backlog-id or create branch feat/B-XYZ-...")
        sys.exit(1)
    _rehydrate(f"scribe start {bid}", fast=fast, full=full)
    _append_worklog(bid, ["- Session started", f"- Branch: {_current_branch()}".strip()])
    # Spawn daemon
    proc = subprocess.Popen(
        [
            PY,
            __file__,
            "scribe",
            "_daemon",
            "--backlog-id",
            bid,
            "--interval",
            str(interval),
            "--idle-timeout",
            str(idle_timeout),
        ]
    )
    state = _load_state()
    state.update(
        {
            "backlog_id": bid,
            "branch": _current_branch(),
            "scribe": {"pid": proc.pid, "interval": interval, "worklog": str(_worklog_path(bid))},
        }
    )
    _save_state(state)
    print(f"📝 Scribe started (PID {proc.pid}) for {bid}. Writing to {state['scribe']['worklog']}")


def cmd_scribe_stop(backlog_id: str | None) -> None:
    state = _load_state()
    info = state.get("scribe", {})
    pid = info.get("pid")
    bid = _detect_backlog_id(backlog_id) or state.get("backlog_id")
    if not pid:
        print("⚠️  Scribe not running")
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception:
        pass
    if bid:
        _append_worklog(bid, ["- Session stopped"])
    state["scribe"] = {}
    _save_state(state)
    print("📝 Scribe stopped")


def cmd_scribe_daemon(backlog_id: str, interval: int, idle_timeout: int) -> None:
    bid = backlog_id
    last_snapshot: set[str] = set()
    start_branch = _current_branch()
    last_change_ts = time.time()
    last_remote = _remote_head(start_branch)
    last_local = _git_head()
    while True:
        try:
            changed = set(_git_changed_files())
            new = sorted(changed - last_snapshot)
            last_snapshot = changed
            bullets: list[str] = []
            if new:
                bullets.append(f"- Changes: {len(new)} file(s)")
                for p in new[:10]:
                    bullets.append(f"  - {p}")
                if len(new) > 10:
                    bullets.append(f"  - (+{len(new) - 10} more)")
                last_change_ts = time.time()
            # Auto-stop on idle timeout
            if time.time() - last_change_ts >= max(60, idle_timeout):
                bullets.append("- Idle timeout reached; stopping scribe")
                if bullets:
                    _append_worklog(bid, bullets)
                break
            # Auto-stop on branch switch
            current_branch = _current_branch()
            if current_branch and current_branch != start_branch:
                bullets.append(f"- Branch switched to {current_branch}; stopping scribe")
                _append_worklog(bid, bullets)
                break
            # Auto-stop after successful push (remote head catches up to local and changes are clear)
            local_head = _git_head()
            remote_head = _remote_head(current_branch or start_branch)
            if (
                local_head
                and remote_head
                and local_head == remote_head
                and (remote_head != last_remote or local_head != last_local)
                and not changed
            ):
                _append_worklog(bid, ["- Remote is up-to-date with local; stopping scribe after push"])
                break
            last_remote = remote_head or last_remote
            last_local = local_head or last_local
            if bullets:
                _append_worklog(bid, bullets)
        except Exception:
            # Keep daemon resilient
            pass
        time.sleep(max(10, interval))


def main() -> None:
    parser = argparse.ArgumentParser(prog="single_doorway")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("description")
    g.add_argument("--telemetry", action="store_true")
    g.add_argument("--no-roadmap-advisory", action="store_true")
    g.add_argument("--fast", action="store_true")
    g.add_argument("--full", action="store_true")

    c = sub.add_parser("continue")
    c.add_argument("backlog_id")
    c.add_argument("--telemetry", action="store_true")
    c.add_argument("--fast", action="store_true")
    c.add_argument("--full", action="store_true")

    a = sub.add_parser("archive")
    a.add_argument("backlog_id")

    o = sub.add_parser("open")
    o.add_argument("backlog_id")

    s = sub.add_parser("scribe")
    ssub = s.add_subparsers(dest="action", required=True)
    s_start = ssub.add_parser("start")
    s_start.add_argument("--backlog-id")
    s_start.add_argument("--interval", type=int, default=60)
    s_start.add_argument("--fast", action="store_true")
    s_start.add_argument("--full", action="store_true")
    s_start.add_argument("--idle-timeout", type=int, default=1800)
    s_stop = ssub.add_parser("stop")
    s_stop.add_argument("--backlog-id")
    s_daemon = ssub.add_parser("_daemon")
    s_daemon.add_argument("--backlog-id", required=True)
    s_daemon.add_argument("--interval", type=int, default=60)
    s_daemon.add_argument("--idle-timeout", type=int, default=1800)

    args = parser.parse_args()

    if args.cmd == "generate":
        cmd_generate(
            args.description,
            args.telemetry,
            args.no_roadmap_advisory,
            getattr(args, "fast", False),
            getattr(args, "full", False),
        )
    elif args.cmd == "continue":
        cmd_continue(args.backlog_id, args.telemetry, getattr(args, "fast", False), getattr(args, "full", False))
    elif args.cmd == "archive":
        cmd_archive(args.backlog_id)
    elif args.cmd == "open":
        cmd_open(args.backlog_id)
    elif args.cmd == "scribe":
        if args.action == "start":
            cmd_scribe_start(
                args.backlog_id,
                args.interval,
                getattr(args, "fast", False),
                getattr(args, "full", False),
                args.idle_timeout,
            )
        elif args.action == "stop":
            cmd_scribe_stop(args.backlog_id)
        elif args.action == "_daemon":
            cmd_scribe_daemon(args.backlog_id, args.interval, args.idle_timeout)


if __name__ == "__main__":
    main()
