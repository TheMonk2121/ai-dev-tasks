#!/usr/bin/env python3
"""
Real-time Cursor chat monitoring system.
Monitors Cursor's actual chat interface and automatically captures conversations.
"""

import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from types import FrameType
from typing import cast

import psutil

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
# Import our working integration
from src.common.db_dsn import resolve_dsn

from .cursor_working_integration import CursorWorkingIntegration


class CursorRealtimeMonitor:
    """Real-time monitoring system for Cursor AI conversations."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or resolve_dsn()
        self.current_integration: CursorWorkingIntegration | None = None
        self.monitoring_active: bool = False
        self.session_file: str = os.path.expanduser("~/.cursor_realtime_monitor.json")
        self.log_file: str = os.path.expanduser("~/.cursor_monitor.log")
        self.cursor_processes: list[psutil.Process] = []
        self.last_check: float = time.time()

        # Cursor chat history locations to monitor
        self.cursor_dirs: list[Path] = [
            Path.home() / "Library/Application Support/Cursor",
            Path.home() / ".cursor",
            Path.home() / "Library/Application Support/Cursor/User/History",
        ]

        print("🚀 Cursor Realtime Monitor System")
        print("=" * 50)

        # Set up signal handlers for graceful shutdown
        _ = signal.signal(signal.SIGINT, self._signal_handler)
        _ = signal.signal(signal.SIGTERM, self._signal_handler)

    def _log(self, message: str) -> None:
        """Log a message to the log file."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"

        try:
            with open(self.log_file, "a") as f:
                _ = f.write(log_entry)
        except Exception:
            pass  # Ignore log errors

    def _signal_handler(self, signum: int, _frame: FrameType | None) -> None:
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.stop_monitoring()
        sys.exit(0)

    def find_cursor_processes(self) -> list[psutil.Process]:
        """Find running Cursor processes."""
        cursor_processes = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["name"] and "Cursor" in proc.info["name"]:
                    cursor_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return cursor_processes

    def find_cursor_chat_files(self) -> list[Path]:
        """Find Cursor chat history files."""
        chat_files = []

        for cursor_dir in self.cursor_dirs:
            if cursor_dir.exists():
                # Look for common chat file patterns
                patterns = [
                    "**/*chat*.json",
                    "**/*conversation*.json",
                    "**/*history*.json",
                    "**/chat_history/**/*.json",
                    "**/conversations/**/*.json",
                ]

                for pattern in patterns:
                    try:
                        files = list(cursor_dir.glob(pattern))
                        chat_files.extend(files)
                    except Exception:
                        continue

        # Filter for recent files (last 24 hours)
        recent_files = []
        cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago

        for file_path in chat_files:
            try:
                if file_path.stat().st_mtime > cutoff_time:
                    recent_files.append(file_path)
            except Exception:
                continue

        return recent_files

    def parse_chat_file(self, file_path: Path) -> list[dict[str, object]]:
        """Parse a Cursor chat file and extract conversations."""
        conversations: list[dict[str, object]] = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Try to parse as JSON
            try:
                data = cast(dict[str, object] | list[object], json.loads(content))
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            conversations.append(item)
                else:
                    conversations.append(data)
            except json.JSONDecodeError:
                # Try to extract JSON objects from the content
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("{") and line.endswith("}"):
                        try:
                            line_data = cast(dict[str, object], json.loads(line))
                            conversations.append(line_data)
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            self._log(f"Error parsing chat file {file_path}: {e}")

        return conversations

    def extract_conversation_data(self, conversation: dict[str, object]) -> dict[str, object] | None:
        """Extract conversation data from a parsed chat object."""
        try:
            # Look for common conversation patterns
            messages: list[object] | None = None
            if "messages" in conversation:
                messages = conversation["messages"]
            elif "conversation" in conversation:
                messages = conversation["conversation"]
            elif "turns" in conversation:
                messages = conversation["turns"]
            else:
                # Try to find message-like data
                messages = []
                for _key, value in conversation.items():
                    if isinstance(value, list) and len(value) > 0:
                        if isinstance(value[0], dict) and any(k in value[0] for k in ["content", "text", "message"]):
                            messages = value
                            break

            if not messages:
                return None

            # Extract user and AI messages
            user_messages: list[str] = []
            ai_messages: list[str] = []

            for msg in messages:
                if isinstance(msg, dict):
                    content = str(msg.get("content", msg.get("text", msg.get("message", ""))))
                    role = str(msg.get("role", msg.get("type", "unknown")))

                    if role in ["user", "human", "question"]:
                        user_messages.append(content)
                    elif role in ["assistant", "ai", "answer", "response"]:
                        ai_messages.append(content)

            if user_messages or ai_messages:
                return {
                    "user_messages": user_messages,
                    "ai_messages": ai_messages,
                    "timestamp": str(
                        conversation.get("timestamp", conversation.get("created_at", datetime.now().isoformat()))
                    ),
                    "source_file": str(conversation.get("source_file", "unknown")),
                }

        except Exception as e:
            self._log(f"Error extracting conversation data: {e}")

        return None

    def capture_conversation(self, conversation_data: dict[str, object]) -> None:
        """Capture a conversation to the database."""
        try:
            if not self.current_integration:
                self.current_integration = CursorWorkingIntegration(self.dsn)
                self._log(f"New session started: {self.current_integration.session_id}")

            # Capture user messages
            user_messages = conversation_data.get("user_messages", [])
            if isinstance(user_messages, list):
                for user_msg in user_messages:
                    if isinstance(user_msg, str) and user_msg.strip():
                        user_metadata: dict[str, str | int | float | bool | None] = {
                            "source": "cursor_realtime",
                            "timestamp": str(conversation_data.get("timestamp", "")),
                        }
                        turn_id = self.current_integration.capture_user_query(user_msg, user_metadata)
                        if turn_id:
                            self._log(f"Captured user message: {user_msg[:50]}...")

            # Capture AI messages
            ai_messages = conversation_data.get("ai_messages", [])
            if isinstance(ai_messages, list):
                for ai_msg in ai_messages:
                    if isinstance(ai_msg, str) and ai_msg.strip():
                        ai_metadata: dict[str, str | int | float | bool | None] = {
                            "source": "cursor_realtime",
                            "timestamp": str(conversation_data.get("timestamp", "")),
                        }
                        turn_id = self.current_integration.capture_ai_response(
                            ai_msg,
                            None,  # No specific query turn ID
                            ai_metadata,
                        )
                        if turn_id:
                            self._log(f"Captured AI message: {ai_msg[:50]}...")

        except Exception as e:
            self._log(f"Error capturing conversation: {e}")

    def check_for_new_conversations(self):
        """Check for new conversations and capture them."""
        try:
            # Find Cursor chat files
            chat_files = self.find_cursor_chat_files()

            if not chat_files:
                return

            # Process each file
            for file_path in chat_files:
                # Check if file was modified recently
                if file_path.stat().st_mtime <= self.last_check:
                    continue

                self._log(f"Processing chat file: {file_path}")

                # Parse the file
                conversations = self.parse_chat_file(file_path)

                # Extract and capture conversation data
                for conversation in conversations:
                    conv_data = self.extract_conversation_data(conversation)
                    if conv_data:
                        self.capture_conversation(conv_data)

            # Update last check time
            self.last_check = time.time()

        except Exception as e:
            self._log(f"Error checking for conversations: {e}")

    def start_monitoring(self):
        """Start real-time monitoring."""
        if self.monitoring_active:
            print("⚠️  Monitoring already active")
            return

        print("🎯 Starting real-time Cursor monitoring...")

        # Check if Cursor is running
        cursor_processes = self.find_cursor_processes()
        if not cursor_processes:
            print("⚠️  No Cursor processes found. Make sure Cursor is running.")
            return

        print(f"✅ Found {len(cursor_processes)} Cursor process(es)")

        # Initialize integration
        self.current_integration = CursorWorkingIntegration(self.dsn)
        self.monitoring_active = True

        # Save session info
        session_data = {
            "active": True,
            "session_id": self.current_integration.session_id,
            "thread_id": self.current_integration.thread_id,
            "started_at": datetime.now().isoformat(),
            "cursor_processes": [p.pid for p in cursor_processes],
        }

        with open(self.session_file, "w") as f:
            json.dump(session_data, f, indent=2)

        print("✅ Monitoring started")
        print(f"   Session ID: {self.current_integration.session_id}")
        print(f"   Thread ID: {self.current_integration.thread_id}")
        print(f"   Monitoring {len(cursor_processes)} Cursor process(es)")
        print(f"   Session file: {self.session_file}")
        print(f"   Log file: {self.log_file}")
        print("\n💡 The system is now monitoring Cursor for new conversations!")
        print("   Press Ctrl+C to stop monitoring")

        # Start monitoring loop
        self._monitoring_loop()

    def stop_monitoring(self):
        """Stop real-time monitoring."""
        if not self.monitoring_active:
            print("⚠️  No active monitoring to stop")
            return

        print("🛑 Stopping real-time monitoring...")

        if self.current_integration:
            # Get final stats
            stats = self.current_integration.get_session_stats()
            print("📊 Final session stats:")
            for key, value in stats.items():
                print(f"   {key}: {value}")

            # Close session
            self.current_integration.close_session()

        self.monitoring_active = False
        self.current_integration = None

        # Clear session file
        if os.path.exists(self.session_file):
            os.remove(self.session_file)

        print("✅ Monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self.monitoring_active:
                # Check for new conversations
                self.check_for_new_conversations()

                # Check if Cursor is still running
                cursor_processes = self.find_cursor_processes()
                if not cursor_processes:
                    print("⚠️  Cursor processes not found. Stopping monitoring.")
                    break

                # Sleep for a bit
                time.sleep(2)  # Check every 2 seconds

        except KeyboardInterrupt:
            pass
        finally:
            self.stop_monitoring()

    def get_status(self) -> dict[str, object]:
        """Get current monitoring status."""
        cursor_processes = self.find_cursor_processes()

        status: dict[str, object] = {
            "monitoring_active": self.monitoring_active,
            "cursor_processes_found": len(cursor_processes),
            "session_active": self.current_integration is not None,
        }

        if self.current_integration:
            stats = self.current_integration.get_session_stats()
            # Update status with stats, converting to compatible types
            for key, value in stats.items():
                status[key] = value

        return status


def main() -> None:
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Realtime Monitor System")
    _ = parser.add_argument("--start", action="store_true", help="Start monitoring")
    _ = parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    _ = parser.add_argument("--status", action="store_true", help="Show status")
    _ = parser.add_argument("--test", action="store_true", help="Test conversation detection")

    args: argparse.Namespace = parser.parse_args()

    # Initialize monitor
    monitor = CursorRealtimeMonitor()

    start: bool = getattr(args, "start", False)
    stop: bool = getattr(args, "stop", False)
    status: bool = getattr(args, "status", False)
    test: bool = getattr(args, "test", False)

    if start:
        monitor.start_monitoring()
    elif stop:
        monitor.stop_monitoring()
    elif status:
        status_data = monitor.get_status()
        monitoring_active = status_data.get("monitoring_active", False)
        if monitoring_active:
            print("🟢 Monitoring is ACTIVE")
            cursor_processes = status_data.get("cursor_processes_found", 0)
            print(f"   Cursor processes: {cursor_processes}")
            session_active = status_data.get("session_active", False)
            if session_active:
                session_id = status_data.get("session_id", "Unknown")
                message_count = status_data.get("message_count", 0)
                print(f"   Session: {session_id}")
                print(f"   Messages: {message_count}")
        else:
            print("🔴 Monitoring is INACTIVE")
            cursor_processes = status_data.get("cursor_processes_found", 0)
            print(f"   Cursor processes found: {cursor_processes}")
    elif test:
        print("🧪 Testing conversation detection...")
        chat_files = monitor.find_cursor_chat_files()
        print(f"Found {len(chat_files)} chat files:")
        for file_path in chat_files:
            print(f"  - {file_path}")

        if chat_files:
            print("\nTesting file parsing...")
            conversations = monitor.parse_chat_file(chat_files[0])
            print(f"Parsed {len(conversations)} conversations from {chat_files[0]}")

            for i, conv in enumerate(conversations[:2]):  # Show first 2
                conv_data = monitor.extract_conversation_data(conv)
                if conv_data:
                    user_messages = conv_data.get("user_messages", [])
                    ai_messages = conv_data.get("ai_messages", [])
                    user_count = len(user_messages) if isinstance(user_messages, list) else 0
                    ai_count = len(ai_messages) if isinstance(ai_messages, list) else 0
                    print(f"  Conversation {i+1}: {user_count} user, {ai_count} AI messages")
    else:
        print("Usage: python cursor_realtime_monitor.py --start|--stop|--status|--test")
        print("\nCommands:")
        print("  --start      Start real-time monitoring of Cursor conversations")
        print("  --stop       Stop monitoring")
        print("  --status     Show current monitoring status")
        print("  --test       Test conversation detection without starting monitoring")


if __name__ == "__main__":
    main()
