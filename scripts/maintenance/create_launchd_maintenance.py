from __future__ import annotations

import os
import plistlib
import subprocess
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
Creates/updates a launchd job to run system maintenance daily at 3am.

- Writes plist to ~/Library/LaunchAgents/com.ai.maintenance.daily.plist
- Schedules: 03:00 local time
- Command: python3 scripts/maintenance.py
"""

PLIST_ID = "com.ai.maintenance.daily"
PLIST_PATH = Path.home() / "Library/LaunchAgents" / f"{PLIST_ID}.plist"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAINT_CMD = ["/usr/bin/env", "python3", str(PROJECT_ROOT / "scripts" / "maintenance.py")]

def ensure_launch_agents_dir() -> None:
    (Path.home() / "Library/LaunchAgents").mkdir(parents=True, exist_ok=True)

def write_plist() -> None:
    plist = {
        "Label": PLIST_ID,
        "ProgramArguments": MAINT_CMD,
        "StartCalendarInterval": {"Hour": 3, "Minute": 0},
        "StandardOutPath": str(PROJECT_ROOT / "artifacts" / "maintenance.out"),
        "StandardErrorPath": str(PROJECT_ROOT / "artifacts" / "maintenance.err"),
        "RunAtLoad": False,
        "KeepAlive": False,
        "EnvironmentVariables": {
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "PYTHONUNBUFFERED": "1",
        },
        # WorkingDirectory avoids relative path issues
        "WorkingDirectory": str(PROJECT_ROOT),
    }
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "artifacts").mkdir(parents=True, exist_ok=True)
    with open(PLIST_PATH, "wb") as fp:
        plistlib.dump(plist, fp)

def load_job() -> None:
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
    subprocess.run(["launchctl", "load", str(PLIST_PATH)], check=True)

def main() -> None:
    ensure_launch_agents_dir()
    write_plist()
    try:
        load_job()
        print(f"✅ launchd job installed and loaded: {PLIST_ID}")
        print(f"   Plist: {PLIST_PATH}")
        print("   Scheduled: daily at 03:00")
    except Exception as e:
        print(f"⚠️ Could not load launchd job automatically: {e}")
        print(f"   You can load it manually: launchctl load {PLIST_PATH}")

if __name__ == "__main__":
    main()
