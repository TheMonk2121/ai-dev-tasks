from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
Manual Scribe Update Trigger
Triggers Scribe updates for recent work and backlog changes.
"""

def get_active_backlog_id() -> str | None:
    """Get the currently active backlog ID."""
    state_file = Path(".ai_state.json")
    if state_file.exists():
        try:
            with open(state_file) as f:
                state = json.load(f)
            return state.get("backlog_id")
        except Exception:
            pass
    return None

def get_recent_changes() -> list[str]:
    """Get recent file changes that might be relevant."""
    try:
        # Get changes from last 24 hours
        result = subprocess.run(
            ["git", "log", "--since", "24 hours ago", "--name-only", "--pretty=format:"],
            capture_output=True,
            text=True,
            check=True,
        )

        files = []
        for line in result.stdout.splitlines():
            if line.strip() and not line.startswith("commit"):
                files.append(line.strip())

        return list(set(files))  # Remove duplicates
    except Exception:
        return []

def trigger_scribe_update(backlog_id: str, message: str) -> bool:
    """Trigger a Scribe update."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/single_doorway.py", "scribe", "append", message, "--backlog-id", backlog_id],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"✅ Scribe updated for {backlog_id}")
            return True
        else:
            print(f"❌ Scribe update failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error triggering Scribe update: {e}")
        return False

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="Manual Scribe Update Trigger")
    parser.add_argument("--message", type=str, help="Custom message for Scribe")
    parser.add_argument("--backlog-id", type=str, help="Specific backlog ID")
    parser.add_argument("--recent", action="store_true", help="Include recent changes in message")

    args = parser.parse_args()

    # Get backlog ID
    backlog_id = args.backlog_id or get_active_backlog_id()
    if not backlog_id:
        print("❌ No active backlog ID found")
        print("💡 Start Scribe first: python3 scripts/single_doorway.py scribe start --backlog-id B-XXX")
        sys.exit(1)

    # Build message
    if args.message:
        message = args.message
    elif args.recent:
        recent_files = get_recent_changes()
        if recent_files:
            file_list = ", ".join(recent_files[:10])  # Limit to 10 files
            if len(recent_files) > 10:
                file_list += f" (+{len(recent_files) - 10} more)"
            message = f"Recent work completed: {file_list}"
        else:
            message = "Work completed (no recent file changes detected)"
    else:
        message = "Manual work update triggered"

    # Trigger update
    print(f"📝 Triggering Scribe update for {backlog_id}...")
    print(f"💬 Message: {message}")

    success = trigger_scribe_update(backlog_id, message)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()