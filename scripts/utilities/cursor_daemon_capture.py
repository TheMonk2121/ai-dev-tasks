#!/usr/bin/env python3
"""
Cursor Daemon Capture System
A robust, non-blocking automatic conversation capture system.
"""

import os
import signal
import sys
import threading
import time
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
# Import our working integration
from utilities.cursor_working_integration import CursorWorkingIntegration

from src.common.db_dsn import resolve_dsn


class CursorDaemonCapture:
    """Daemon-based automatic conversation capture system."""

    dsn: str

    def __init__(self, dsn_param: str | None = None) -> None:
        resolved_dsn = resolve_dsn()
        if dsn_param is not None:
            self.dsn: Any = dsn_param
        else:
            self.dsn: Any = resolved_dsn
        self.pid_file: str = os.path.expanduser("~/.cursor_capture_daemon.pid")
        self.session_file: str = os.path.expanduser("~/.cursor_active_session.json")
        self.log_file: str = os.path.expanduser("~/.cursor_capture.log")
        self.current_integration: CursorWorkingIntegration | None = None
        self.running: bool = False
        self.daemon_thread: threading.Thread | None = None

        print("🚀 Cursor Daemon Capture System")
        print("=" * 50)

    def start_daemon(self) -> bool:
        """Start the capture daemon."""
        if self.is_running():
            print("⚠️  Daemon already running")
            return False

        try:
            print("🎯 Starting capture daemon...")

            # Start daemon in background thread
            self.daemon_thread = threading.Thread(target=self._daemon_loop, daemon=True)
            self.daemon_thread.start()

            # Save PID
            with open(self.pid_file, "w") as f:
                _ = f.write(str(os.getpid()))

            # Wait a moment for daemon to start
            time.sleep(1)

            if self.is_running():
                print("✅ Daemon started successfully")
                print(f"   PID file: {self.pid_file}")
                print(f"   Log file: {self.log_file}")
                return True
            else:
                print("❌ Failed to start daemon")
                return False

        except Exception as e:
            print(f"❌ Error starting daemon: {e}")
            return False

    def stop_daemon(self) -> bool:
        """Stop the capture daemon."""
        if not self.is_running():
            print("⚠️  Daemon not running")
            return False

        try:
            print("🛑 Stopping capture daemon...")

            # Read PID and kill process
            if os.path.exists(self.pid_file):
                with open(self.pid_file) as f:
                    pid = int(f.read().strip())

                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)

                    # Check if still running
                    try:
                        os.kill(pid, 0)
                        # Still running, force kill
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Process already dead

                except ProcessLookupError:
                    pass  # Process already dead

            # Clean up files
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)

            self.running: Any = False
            print("✅ Daemon stopped")
            return True

        except Exception as e:
            print(f"❌ Error stopping daemon: {e}")
            return False

    def is_running(self) -> bool:
        """Check if daemon is running."""
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())

            # Check if process is running
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, ValueError):
            # Process not running, clean up PID file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            return False

    def _daemon_loop(self) -> None:
        """Main daemon loop."""
        self.running: Any = True
        self._log("Daemon started")

        try:
            while self.running:
                # Check for new conversations
                self._check_for_conversations()
                time.sleep(5)  # Check every 5 seconds

        except Exception as e:
            self._log(f"Daemon error: {e}")
        finally:
            self.running: Any = False
            self._log("Daemon stopped")

    def _check_for_conversations(self) -> None:
        """Check for new conversations to capture."""
        try:
            # This is where you would implement the actual conversation detection
            # For now, we'll just maintain the session
            if not self.current_integration:
                self.current_integration: Any = CursorWorkingIntegration(self.dsn)
                self._log(f"New session started: {self.current_integration.session_id}")

        except Exception as e:
            self._log(f"Error checking conversations: {e}")

    def _log(self, message: str) -> None:
        """Log a message."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"

        try:
            with open(self.log_file, "a") as f:
                _: Any = f.write(log_entry)
        except Exception:
            pass  # Ignore log errors

    def capture_query(
        self, query: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> str | None:
        """Capture a user query."""
        if not self.current_integration:
            self.current_integration: Any = CursorWorkingIntegration(self.dsn)

        try:
            turn_id = self.current_integration.capture_user_query(query, metadata or {})
            self._log(f"Captured query: {query[:50]}...")
            return turn_id
        except Exception as e:
            self._log(f"Error capturing query: {e}")
            return None

    def capture_response(
        self,
        response: str,
        query_turn_id: str | None = None,
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> str | None:
        """Capture an AI response."""
        if not self.current_integration:
            self.current_integration: Any = CursorWorkingIntegration(self.dsn)

        try:
            turn_id = self.current_integration.capture_ai_response(response, query_turn_id, metadata or {})
            self._log(f"Captured response: {response[:50]}...")
            return turn_id
        except Exception as e:
            self._log(f"Error capturing response: {e}")
            return None

    def get_status(self) -> dict[str, str | int | bool | dict[str, str | int | float | bool | None]]:
        """Get daemon status."""
        if not self.is_running():
            return {"running": False, "message": "Daemon not running"}

        try:
            if self.current_integration:
                stats = self.current_integration.get_session_stats()
                return {
                    "running": True,
                    "session_id": self.current_integration.session_id,
                    "thread_id": self.current_integration.thread_id,
                    "stats": stats,
                }
            else:
                return {"running": True, "message": "Daemon running, no active session"}
        except Exception as e:
            return {"running": True, "error": str(e)}


def main() -> None:
    """Main function."""
    import argparse

    parser: Any = argparse.ArgumentParser(description="Cursor Daemon Capture System")
    _: Any = parser.add_argument("--start", action="store_true", help="Start daemon")
    _: Any = parser.add_argument("--stop", action="store_true", help="Stop daemon")
    _: Any = parser.add_argument("--status", action="store_true", help="Show status")
    _: Any = parser.add_argument("--restart", action="store_true", help="Restart daemon")

    args: Any = parser.parse_args()

    daemon = CursorDaemonCapture()

    if getattr(args, "start", False):
        success: Any = daemon.start_daemon()
        sys.exit(0 if success else 1)
    elif getattr(args, "stop", False):
        success: Any = daemon.stop_daemon()
        sys.exit(0 if success else 1)
    elif getattr(args, "restart", False):
        _: Any = daemon.stop_daemon()
        time.sleep(2)
        success: Any = daemon.start_daemon()
        sys.exit(0 if success else 1)
    elif getattr(args, "status", False):
        status: Any = daemon.get_status()
        if status["running"]:
            print("🟢 Daemon is RUNNING")
            if "session_id" in status:
                print(f"   Session: {status['session_id']}")
                print(f"   Thread: {status['thread_id']}")
        else:
            print("🔴 Daemon is NOT RUNNING")
            if "message" in status:
                print(f"   {status['message']}")
        sys.exit(0)
    else:
        print("Usage: python cursor_daemon_capture.py --start|--stop|--status|--restart")
        sys.exit(1)


if __name__ == "__main__":
    main()
