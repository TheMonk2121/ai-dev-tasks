from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

#!/usr/bin/env python3
"""
Task Status Updater

Updates task completion status and displays the current state of the task list
for the 003_process-task-list.md workflow.
"""

class TaskStatusUpdater:
    """Update and display task completion status."""

    def __init__(self, task_file: str):
        self.task_file = Path(task_file)
        self.content = self.task_file.read_text() if self.task_file.exists() else ""

    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update a specific task's status.

        Args:
            task_id: Task ID (e.g., "T-1", "T-2")
            status: New status ("⏳", "✅", "❌")

        Returns:
            bool: True if updated successfully
        """
        if not self.task_file.exists():
            return False

        # Pattern to match task headers with status (both old bracket and new emoji formats)
        pattern = rf"(### (?:\[[ x!]\]|[⏳✅❌]) {re.escape(task_id)} .*?)(\n)"

        # Find current status
        current_match = re.search(pattern, self.content)
        if not current_match:
            return False

        # Replace with new status
        new_header = f"### {status} {task_id}"
        task_title = current_match.group(1).split(" ", 3)[-1]  # Get the task title
        new_content = f"{new_header} {task_title}\n"

        # Update the content
        self.content = re.sub(pattern, new_content, self.content)

        # Write back to file
        self.task_file.write_text(self.content)
        return True

    def get_task_status(self, task_id: str) -> str:
        """Get current status of a task."""
        pattern = rf"### \[([ x!])\] {re.escape(task_id)}"
        match = re.search(pattern, self.content)
        return match.group(1) if match else "?"

    def display_task_list(self, show_completed: bool = True) -> None:
        """Display the current task list with status."""
        if not self.task_file.exists():
            print("❌ Task file not found")
            return

        # Extract header information
        header_match = re.search(r"# TASKS ([^:]+): (.+)", self.content)
        if header_match:
            backlog_id = header_match.group(1)
            title = header_match.group(2)
            print(f"\n📋 **Task List: {backlog_id} - {title}**")
            print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Find all tasks
        task_pattern = r"### \[([ x!])\] (T-\d+) (.+?)(?:\n- \*\*Priority\*\*|\n---|\n$)"
        tasks = re.findall(task_pattern, self.content, re.DOTALL)

        if not tasks:
            print("❌ No tasks found in file")
            return

        # Group tasks by status
        pending_tasks = []
        completed_tasks = []
        blocked_tasks = []

        for status, task_id, title in tasks:
            task_info = {"id": task_id, "title": title.strip(), "status": status}

            if status == "x":
                completed_tasks.append(task_info)
            elif status == "!":
                blocked_tasks.append(task_info)
            else:
                pending_tasks.append(task_info)

        # Display summary
        total_tasks = len(tasks)
        completed_count = len(completed_tasks)
        pending_count = len(pending_tasks)
        blocked_count = len(blocked_tasks)

        print("\n📊 **Progress Summary:**")
        print(f"   ✅ Completed: {completed_count}/{total_tasks}")
        print(f"   ⏳ Pending: {pending_count}/{total_tasks}")
        print(f"   🚫 Blocked: {blocked_count}/{total_tasks}")
        print(f"   📈 Progress: {(completed_count/total_tasks)*100:.1f}%")

        # Display pending tasks
        if pending_tasks:
            print("\n🎯 **Next Tasks:**")
            for task in pending_tasks:
                print(f"   {task['id']}: {task['title']}")

        # Display blocked tasks
        if blocked_tasks:
            print("\n🚫 **Blocked Tasks:**")
            for task in blocked_tasks:
                print(f"   {task['id']}: {task['title']}")

        # Display completed tasks (if requested)
        if show_completed and completed_tasks:
            print("\n✅ **Completed Tasks:**")
            for task in completed_tasks:
                print(f"   {task['id']}: {task['title']}")

        # Show next action
        if pending_tasks:
            next_task = pending_tasks[0]
            print(f"\n🚀 **Next Action:** Begin {next_task['id']} - {next_task['title']}")
        elif blocked_tasks:
            print("\n⚠️  **Action Required:** Resolve blocked tasks before continuing")
        else:
            print("\n🎉 **All Tasks Complete!**")

def update_and_display_task_status(task_file: str, completed_task_id: str | None = None) -> None:
    """
    Update task status and display the current state.

    Args:
        task_file: Path to the task file
        completed_task_id: Task ID that was just completed (optional)
    """
    updater = TaskStatusUpdater(task_file)

    # Update completion status if provided
    if completed_task_id:
        success = updater.update_task_status(completed_task_id, "✅")
        if success:
            print(f"✅ Updated {completed_task_id} to completed status")
        else:
            print(f"❌ Failed to update {completed_task_id}")

    # Display current task list
    updater.display_task_list()

def main():
    """Main function for testing."""

    if len(sys.argv) < 2:
        print("Usage: python task_status_updater.py <task_file> [completed_task_id]")
        return

    task_file = sys.argv[1]
    completed_task_id = sys.argv[2] if len(sys.argv) > 2 else None

    update_and_display_task_status(task_file, completed_task_id)

if __name__ == "__main__":
    main()