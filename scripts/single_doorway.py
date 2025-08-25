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
from datetime import datetime
from pathlib import Path

# Optional imports (may not be available in all environments)
try:
    import psutil
except ImportError:
    psutil = None

try:
    from session_registry import SessionRegistry
except ImportError:
    SessionRegistry = None


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

    # Try to use venv Python if available
    try:
        from venv_manager import get_venv_python

        venv_python = get_venv_python()
        if venv_python:
            python_executable = venv_python
        else:
            python_executable = PY
    except ImportError:
        python_executable = PY

    if capture:
        return subprocess.check_output([python_executable, *args], text=True, env=env).strip()
    subprocess.check_call([python_executable, *args], env=env)
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
                file_path = parts[-1]
                # Monitor additional file types for Scribe
                if any(
                    pattern in file_path
                    for pattern in [
                        "000_backlog.md",
                        "PRD-",
                        "Task-List-",
                        "artifacts/worklogs/",
                        "artifacts/summaries/",
                        ".ai_state.json",
                    ]
                ):
                    files.append(file_path)
                # Also include all Python files (for code changes)
                elif file_path.endswith(".py"):
                    files.append(file_path)
                # Include all markdown files (for documentation changes)
                elif file_path.endswith(".md"):
                    files.append(file_path)
        return sorted(set(files))
    except Exception:
        return []


def _rehydrate(description: str, fast: bool, full: bool) -> None:
    # Prefer fast profile unless full explicitly requested
    args: list[str] = [
        "scripts/memory_up.sh",
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

    # Check instance limits
    current_instances = _count_scribe_instances()
    max_instances = 3

    if current_instances >= max_instances:
        print(f"⚠️  Warning: {current_instances} Scribe instances running (max: {max_instances})")
        if current_instances == max_instances:
            print("🔄 Stopping oldest instance to make room...")
            oldest_pid = _get_oldest_scribe_pid()
            if oldest_pid and _stop_scribe_instance(oldest_pid):
                print(f"✅ Stopped oldest instance (PID: {oldest_pid})")
                current_instances -= 1
            else:
                print("❌ Failed to stop oldest instance")
                sys.exit(1)
        else:
            print("❌ Too many instances running. Please stop some manually.")
            sys.exit(1)

    if current_instances >= 2:
        print(f"⚠️  Warning: {current_instances} instances running (approaching limit of {max_instances})")
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

    # Register session in session registry
    if SessionRegistry is None:
        print("⚠️  Session registry not available - continuing without registration")
    else:
        try:
            registry = SessionRegistry()
            registry.register_session(
                backlog_id=bid,
                pid=proc.pid,
                worklog_path=str(_worklog_path(bid)),
                session_type="brainstorming",  # Default, can be enhanced later
                priority="medium",
            )
        except Exception as e:
            print(f"⚠️  Failed to register session: {e}")

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

    # Update session registry
    if bid and SessionRegistry is not None:
        try:
            registry = SessionRegistry()
            registry.update_session_status(bid, "completed")
        except Exception as e:
            print(f"⚠️  Failed to update session registry: {e}")

    state["scribe"] = {}
    _save_state(state)
    print("📝 Scribe stopped")


def cmd_scribe_append(message: str, backlog_id: str | None) -> None:
    """Append a message to the current worklog."""
    bid = _detect_backlog_id(backlog_id) or _load_state().get("backlog_id")
    if not bid:
        print("❌ Cannot determine backlog_id. Provide --backlog-id or ensure scribe is running.")
        sys.exit(1)

    _append_worklog(bid, [f"- {message}"])
    print(f"📝 Added to {bid} worklog: {message}")


def _count_scribe_instances() -> int:
    """Count running Scribe instances."""
    if psutil is None:
        print("⚠️  psutil not available - cannot count instances")
        return 0

    count = 0
    for proc in psutil.process_iter(["pid", "cmdline"]):
        try:
            cmdline = proc.info["cmdline"]
            if (
                cmdline
                and "single_doorway.py" in " ".join(cmdline)
                and "scribe" in " ".join(cmdline)
                and "_daemon" in " ".join(cmdline)
            ):
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return count


def _get_oldest_scribe_pid() -> int | None:
    """Get PID of oldest running Scribe instance."""
    if psutil is None:
        print("⚠️  psutil not available - cannot get oldest PID")
        return None

    oldest_pid = None
    oldest_time = float("inf")

    for proc in psutil.process_iter(["pid", "cmdline", "create_time"]):
        try:
            cmdline = proc.info["cmdline"]
            if (
                cmdline
                and "single_doorway.py" in " ".join(cmdline)
                and "scribe" in " ".join(cmdline)
                and "_daemon" in " ".join(cmdline)
            ):
                if proc.info["create_time"] < oldest_time:
                    oldest_time = proc.info["create_time"]
                    oldest_pid = proc.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return oldest_pid


def _stop_scribe_instance(pid: int) -> bool:
    """Stop a specific Scribe instance by PID."""
    if psutil is None:
        print("⚠️  psutil not available - cannot stop instance")
        return False

    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)  # Wait up to 5 seconds
        return True
    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
        try:
            proc.kill()  # Force kill if terminate didn't work
            return True
        except psutil.NoSuchProcess:
            return False


def cmd_scribe_status(verbose: bool = False) -> None:
    """Show status of running Scribe instances."""
    if psutil is None:
        print("❌ psutil not available - cannot show status")
        return

    scribe_processes = []

    # Find all scribe daemon processes (filter for our specific script)
    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        try:
            cmdline = proc.info["cmdline"]
            if (
                cmdline
                and "single_doorway.py" in " ".join(cmdline)
                and "scribe" in " ".join(cmdline)
                and "_daemon" in " ".join(cmdline)
            ):
                scribe_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not scribe_processes:
        print("📝 No Scribe instances running")
        return

    print(f"📝 Found {len(scribe_processes)} Scribe instance(s):")

    for proc in scribe_processes:
        pid = proc["pid"]
        cmdline = " ".join(proc["cmdline"])
        create_time = datetime.fromtimestamp(proc["create_time"]).strftime("%Y-%m-%d %H:%M:%S")

        # Extract backlog ID from command line
        backlog_id = "unknown"
        for arg in proc["cmdline"]:
            if arg.startswith("--backlog-id"):
                backlog_id = arg.split("=")[1] if "=" in arg else "B-XXX"
                break

        print(f"  PID {pid}: {backlog_id} (started {create_time})")

        if verbose:
            print(f"    Command: {cmdline}")
            print(f"    Memory: {psutil.Process(pid).memory_info().rss / 1024 / 1024:.1f} MB")
            print()

    # Check state file
    state = _load_state()
    if state.get("backlog_id"):
        print(f"📋 Current state: {state['backlog_id']}")
        if state.get("scribe", {}).get("pid"):
            print(f"   Active PID: {state['scribe']['pid']}")


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


# Session registry command functions
def cmd_scribe_list(no_context: bool, status_filter: str | None) -> None:
    """List sessions from the session registry."""
    if SessionRegistry is None:
        print("❌ Session registry not available. Install session_registry.py")
        return

    try:
        registry = SessionRegistry()
        registry.list_sessions(show_context=not no_context, status_filter=status_filter)
    except Exception as e:
        print(f"❌ Failed to list sessions: {e}")


def cmd_scribe_tag(backlog_id: str, tags: list[str]) -> None:
    """Add context tags to a session."""
    if SessionRegistry is None:
        print("❌ Session registry not available. Install session_registry.py")
        return

    try:
        registry = SessionRegistry()
        registry.add_context_tags(backlog_id, tags)
    except Exception as e:
        print(f"❌ Failed to tag session: {e}")


def cmd_scribe_untag(backlog_id: str, tags: list[str]) -> None:
    """Remove context tags from a session."""
    if SessionRegistry is None:
        print("❌ Session registry not available. Install session_registry.py")
        return

    try:
        registry = SessionRegistry()
        registry.remove_context_tags(backlog_id, tags)
    except Exception as e:
        print(f"❌ Failed to untag session: {e}")


def cmd_scribe_info(backlog_id: str) -> None:
    """Show detailed information about a session."""
    if SessionRegistry is None:
        print("❌ Session registry not available. Install session_registry.py")
        return

    try:
        registry = SessionRegistry()
        session = registry.get_session_info(backlog_id)
        if session:
            print(f"\n📋 Session Info: {backlog_id}")
            print("=" * 50)
            print(f"Status: {session.status}")
            print(f"PID: {session.pid}")
            print(f"Started: {session.start_time}")
            print(f"Type: {session.context.session_type}")
            print(f"Priority: {session.context.priority}")
            print(f"Tags: {', '.join(sorted(session.context.tags))}")
            print(f"Worklog: {session.worklog_path}")
            if session.last_activity:
                print(f"Last Activity: {session.last_activity}")
        else:
            print(f"❌ Session {backlog_id} not found")
    except Exception as e:
        print(f"❌ Failed to get session info: {e}")


def cmd_scribe_cleanup() -> None:
    """Clean up old completed sessions."""
    if SessionRegistry is None:
        print("❌ Session registry not available. Install session_registry.py")
        return

    try:
        registry = SessionRegistry()
        registry.cleanup_completed_sessions()
    except Exception as e:
        print(f"❌ Failed to cleanup sessions: {e}")


def cmd_scribe_validate() -> None:
    """Validate that registered processes are still running."""
    if SessionRegistry is None:
        print("❌ Session registry not available. Install session_registry.py")
        return

    try:
        registry = SessionRegistry()
        registry.validate_processes()
    except Exception as e:
        print(f"❌ Failed to validate sessions: {e}")


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
    s_append = ssub.add_parser("append")
    s_append.add_argument("message", help="Message to append to worklog")
    s_append.add_argument("--backlog-id", help="Backlog ID (auto-detected if not provided)")

    s_status = ssub.add_parser("status")
    s_status.add_argument("--verbose", "-v", action="store_true", help="Show detailed status")

    # Session registry commands
    s_list = ssub.add_parser("list")
    s_list.add_argument("--no-context", action="store_true", help="Hide context tags")
    s_list.add_argument(
        "--status-filter", choices=["active", "completed", "paused", "orphaned"], help="Filter by status"
    )

    s_tag = ssub.add_parser("tag")
    s_tag.add_argument("--backlog-id", required=True, help="Backlog ID to tag")
    s_tag.add_argument("--tags", nargs="+", required=True, help="Context tags to add")

    s_untag = ssub.add_parser("untag")
    s_untag.add_argument("--backlog-id", required=True, help="Backlog ID to untag")
    s_untag.add_argument("--tags", nargs="+", required=True, help="Context tags to remove")

    s_info = ssub.add_parser("info")
    s_info.add_argument("--backlog-id", required=True, help="Backlog ID for detailed info")

    ssub.add_parser("cleanup")
    ssub.add_parser("validate")

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
        elif args.action == "append":
            cmd_scribe_append(args.message, args.backlog_id)
        elif args.action == "status":
            cmd_scribe_status(args.verbose)
        elif args.action == "list":
            cmd_scribe_list(args.no_context, args.status_filter)
        elif args.action == "tag":
            cmd_scribe_tag(args.backlog_id, args.tags)
        elif args.action == "untag":
            cmd_scribe_untag(args.backlog_id, args.tags)
        elif args.action == "info":
            cmd_scribe_info(args.backlog_id)
        elif args.action == "cleanup":
            cmd_scribe_cleanup()
        elif args.action == "validate":
            cmd_scribe_validate()


if __name__ == "__main__":
    main()
