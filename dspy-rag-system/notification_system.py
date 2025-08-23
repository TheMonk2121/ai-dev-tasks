#!/usr/bin/env python3
"""
Notification System for DSPy RAG
Sends notifications when new files are processed.
"""

import json
import logging
import os
import subprocess
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


class NotificationSystem:
    """Handles notifications for the RAG system"""

    def __init__(self):
        self.notification_log = "notification_history.json"
        self.load_notification_history()

    def load_notification_history(self):
        """Load notification history from file"""
        try:
            if os.path.exists(self.notification_log):
                with open(self.notification_log, "r") as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception as e:
            logger.error(f"Error loading notification history: {e}")
            self.history = []

    def save_notification_history(self):
        """Save notification history to file"""
        try:
            with open(self.notification_log, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving notification history: {e}")

    def send_macos_notification(self, title, message, subtitle=""):
        """Send macOS notification"""
        try:
            script = f"""
            display notification "{message}" with title "{title}" subtitle "{subtitle}"
            """
            subprocess.run(["osascript", "-e", script], check=True)
            logger.info(f"✅ macOS notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send macOS notification: {e}")
            return False

    def send_terminal_notification(self, title, message):
        """Send terminal notification"""
        try:
            logger.info(
                "🔔 Terminal notification sent",
                extra={
                    "component": "notification_system",
                    "action": "terminal_notification",
                    "title": title,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                },
            )
            print(f"\n🔔 NOTIFICATION: {title}")
            print(f"   {message}")
            print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)
            return True
        except Exception as e:
            logger.error(
                f"❌ Failed to send terminal notification: {e}",
                extra={"component": "notification_system", "action": "terminal_notification_error", "error": str(e)},
            )
            return False

    def send_desktop_notification(self, title, message, subtitle=""):
        """Send desktop notification using terminal-notifier"""
        try:
            subprocess.run(
                ["terminal-notifier", "-title", title, "-message", message, "-subtitle", subtitle, "-sound", "default"],
                check=True,
            )
            logger.info(f"✅ Desktop notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send desktop notification: {e}")
            return False

    def notify_file_processed(self, filename, chunks_count, file_size):
        """Notify when a file is processed"""
        title = "📄 RAG File Processed"
        message = f"Added {filename} to knowledge base"
        subtitle = f"{chunks_count} chunks, {file_size} bytes"

        # Send different types of notifications
        success = False

        # Try macOS notification first
        if self.send_macos_notification(title, message, subtitle):
            success = True

        # Try terminal notification
        if self.send_terminal_notification(title, message):
            success = True

        # Try desktop notification (if terminal-notifier is installed)
        if self.send_desktop_notification(title, message, subtitle):
            success = True

        # Log the notification
        notification = {
            "timestamp": datetime.now().isoformat(),
            "type": "file_processed",
            "filename": filename,
            "chunks_count": chunks_count,
            "file_size": file_size,
            "success": success,
        }

        self.history.append(notification)
        self.save_notification_history()

        return success

    def notify_system_status(self, total_chunks, total_documents):
        """Notify system status"""
        title = "📊 RAG System Status"
        message = f"Knowledge base updated: {total_chunks} chunks, {total_documents} documents"

        self.send_macos_notification(title, message)
        self.send_terminal_notification(title, message)

    def get_notification_history(self, limit=10):
        """Get recent notification history"""
        return self.history[-limit:] if self.history else []


def setup_notifications():
    """Set up notification system"""
    logger.info(
        "🔔 Setting up RAG Notification System", extra={"component": "notification_system", "action": "setup_start"}
    )
    print("🔔 Setting up RAG Notification System...")
    print("=" * 50)

    # Check if terminal-notifier is available
    try:
        subprocess.run(["terminal-notifier", "-help"], capture_output=True, check=True)
        logger.info(
            "✅ terminal-notifier available",
            extra={"component": "notification_system", "action": "terminal_notifier_check", "status": "available"},
        )
        print("✅ terminal-notifier available")
    except Exception:
        logger.warning(
            "⚠️  terminal-notifier not installed",
            extra={"component": "notification_system", "action": "terminal_notifier_check", "status": "not_installed"},
        )
        print("⚠️  terminal-notifier not installed")
        print("   Install with: brew install terminal-notifier")

    # Test macOS notifications
    notification_system = NotificationSystem()
    test_success = notification_system.send_macos_notification("RAG System Test", "Notification system is working!")

    if test_success:
        logger.info(
            "✅ macOS notifications working",
            extra={"component": "notification_system", "action": "macos_test", "status": "success"},
        )
        print("✅ macOS notifications working")
    else:
        logger.error(
            "❌ macOS notifications not working",
            extra={"component": "notification_system", "action": "macos_test", "status": "failed"},
        )
        print("❌ macOS notifications not working")

    return notification_system


if __name__ == "__main__":
    notification_system = setup_notifications()

    print("\n📋 Notification Options Available:")
    print("   1. macOS native notifications")
    print("   2. Terminal notifications")
    print("   3. Desktop notifications (if terminal-notifier installed)")
    print("\n💡 The system will automatically notify you when:")
    print("   - New files are processed")
    print("   - System status changes")
    print("   - Errors occur")
