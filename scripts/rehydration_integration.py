#!/usr/bin/env python3
"""
Auto rehydration integration helpers for Scribe sessions.

Environment:
- AUTO_REHYDRATE: "1" to enable (default: "0")
- REHYDRATE_MINUTES: debounce window in minutes (default: "10")
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional

STATE_PATH = Path(".rehydrate_state.json")


def _now_ts() -> float:
    return time.time()


def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_state(state: dict) -> None:
    try:
        with open(STATE_PATH, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def is_enabled() -> bool:
    return os.getenv("AUTO_REHYDRATE", "0") == "1"


def get_debounce_minutes() -> int:
    try:
        return int(os.getenv("REHYDRATE_MINUTES", "10"))
    except ValueError:
        return 10


def should_trigger(backlog_id: Optional[str]) -> bool:
    if not is_enabled():
        return False
    if not backlog_id:
        return False
    state = _load_state()
    last_ts = state.get(backlog_id, 0)
    window_sec = max(get_debounce_minutes(), 0) * 60
    return (_now_ts() - last_ts) >= window_sec


def record_trigger(backlog_id: Optional[str]) -> None:
    if not backlog_id:
        return
    state = _load_state()
    state[backlog_id] = _now_ts()
    _save_state(state)


def rehydrate_with_debounce(
    backlog_id: Optional[str],
    role: str = "planner",
    query: str = "current project status and core documentation",
) -> bool:
    if not should_trigger(backlog_id):
        return False
    try:
        # Call the shell script directly to avoid import/path issues
        cmd = [
            "./scripts/memory_up.sh",
            "-q",
            query,
            "-r",
            role,
        ]
        result = subprocess.run(cmd, check=False)
        ok = result.returncode == 0
        return ok
    finally:
        # Record last trigger time regardless of success to prevent rapid retries
        record_trigger(backlog_id)
