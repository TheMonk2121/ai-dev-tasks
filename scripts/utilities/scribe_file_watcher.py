from __future__ import annotations
import json
import subprocess
import sys
import time
from pathlib import Path
    import argparse
#!/usr/bin/env python3
"""
Scribe File System Watcher
Monitors file changes and triggers Scribe updates for relevant files.
"""

# File patterns to monitor
MONITOR_PATTERNS = [
    "000_backlog.md",
    "PRD-",
    "Task-List-",
    "artifacts/worklogs/",
    "artifacts/summaries/",
    ".ai_state.json",
]

class ScribeFileWatcher:
    """Monitors file changes and triggers Scribe updates."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.state_file = self.project_root / ".ai_state.json"
        self.last_check = time.time()
        self.known_files: set[str] = set()

    def get_active_backlog_id(self) -> str | None:
        """Get the currently active backlog ID from state file."""
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    state = json.load(f)
                return state.get("backlog_id")
        except Exception:
            pass
        return None

    def should_monitor_file(self, file_path: str) -> bool:
        """Check if a file should be monitored."""
        return any(pattern in file_path for pattern in MONITOR_PATTERNS)

    def get_changed_files(self) -> list[str]:
        """Get list of changed files since last check."""
        try:
            # Get all changed files (staged and unstaged)
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)

            changed_files = []
            for line in result.stdout.splitlines():
                if line.strip():
                    file_path = line.split()[-1]
                    if self.should_monitor_file(file_path):
                        changed_files.append(file_path)

            return changed_files
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []

    def trigger_scribe_update(self, files: list[str], backlog_id: str) -> bool:
        """Trigger Scribe update for changed files."""
        try:
            file_list = ", ".join(files[:5])  # Limit to first 5 files
            if len(files) > 5:
                file_list += f" (+{len(files) - 5} more)"

            message = f"Files changed: {file_list}"

            # Use single_doorway.py to append to worklog
            result = subprocess.run(
                [sys.executable, "scripts/single_doorway.py", "scribe", "append", message, "--backlog-id", backlog_id],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"✅ Scribe updated for {backlog_id}: {message}")
                return True
            else:
                print(f"⚠️  Scribe update failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error triggering Scribe update: {e}")
            return False

    def watch_once(self) -> bool:
        """Check for changes once and trigger updates if needed."""
        backlog_id = self.get_active_backlog_id()
        if not backlog_id:
            return False

        changed_files = self.get_changed_files()
        if not changed_files:
            return False

        # Filter out files we've already seen
        new_files = [f for f in changed_files if f not in self.known_files]
        if new_files:
            self.known_files.update(new_files)
            return self.trigger_scribe_update(new_files, backlog_id)

        return False

    def watch_continuous(self, interval: int = 30) -> None:
        """Continuously monitor files for changes."""
        print(f"🔍 Starting Scribe file watcher (interval: {interval}s)")
        print(f"📁 Monitoring patterns: {MONITOR_PATTERNS}")

        try:
            while True:
                self.watch_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Scribe file watcher stopped")

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="Scribe File System Watcher")
    parser.add_argument("--once", action="store_true", help="Check once and exit")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--backlog-id", type=str, help="Specific backlog ID to monitor")

    args = parser.parse_args()

    watcher = ScribeFileWatcher()

    if args.backlog_id:
        # Override the backlog ID from state file
        watcher.state_file = Path(".ai_state.json")
        with open(watcher.state_file, "w") as f:
            json.dump({"backlog_id": args.backlog_id}, f)

    if args.once:
        success = watcher.watch_once()
        sys.exit(0 if success else 1)
    else:
        watcher.watch_continuous(args.interval)

if __name__ == "__main__":
    main()