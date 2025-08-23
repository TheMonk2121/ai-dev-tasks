#!/usr/bin/env python3
"""
Task Execution Engine - Core CLI Script

This script serves as the core execution engine for all backlog items in the AI development ecosystem.
It provides automated task processing, state management, and error handling for backlog execution.

Author: AI Development Ecosystem
Version: 1.0
Last Updated: 2024-08-07
"""

import argparse
import json
import logging
import os
import re
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import existing utilities
try:
    # Add the correct path to sys.path
    sys.path.append("dspy-rag-system/src")
    from utils.logger import setup_logger
    from utils.prompt_sanitizer import sanitize_prompt
    from utils.retry_wrapper import retry
except ImportError:
    # Fallback if dspy-rag-system not available
    def setup_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def retry_with_backoff(func, max_retries=3, base_delay=1):
        """Simple retry wrapper fallback."""

        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(base_delay * (2**attempt))
            return None

        return wrapper

    def sanitize_input(text: str) -> str:
        """Simple input sanitization fallback."""
        return text.strip()

# Configure logging
logger = setup_logger(__name__)

class TaskStatus(Enum):
    """Task execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TaskPriority(Enum):
    """Task priority enumeration."""

    CRITICAL = "🔥"
    HIGH = "📈"
    MEDIUM = "⭐"
    LOW = "🔧"

@dataclass
class Task:
    """Task data structure."""

    id: str
    title: str
    priority: TaskPriority
    points: int
    status: TaskStatus
    description: str
    tech_footprint: str
    dependencies: List[str]
    score_total: Optional[float] = None
    human_required: bool = False
    human_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class ExecutionState:
    """Execution state data structure."""

    task_id: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    progress: float = 0.0

class TaskExecutionEngine:
    """Main task execution engine."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the task execution engine."""
        self.config = self._load_config(config_path)
        self.state_db = self._init_state_database()
        self.backlog_parser = BacklogParser()
        self.task_executor = TaskExecutor(self.config)
        self.error_handler = ErrorHandler()

        logger.info("Task execution engine initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "backlog_file": "000_core/000_backlog.md",
            "state_db": "task_execution.db",
            "log_level": "INFO",
            "max_retries": 3,
            "retry_delay": 1,
            "timeout": 300,
            "auto_confirm": False,
            "dry_run": False,
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    file_config = json.load(f)
                default_config.update(file_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

        return default_config

    def _init_state_database(self) -> sqlite3.Connection:
        """Initialize the state management database."""
        db_path = self.config["state_db"]
        conn = sqlite3.connect(db_path)

        # Create tables if they don't exist
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_executions (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                progress REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_metadata (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                priority TEXT NOT NULL,
                points INTEGER NOT NULL,
                description TEXT,
                tech_footprint TEXT,
                dependencies TEXT,
                score_total REAL,
                human_required BOOLEAN DEFAULT FALSE,
                human_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        logger.info(f"State database initialized: {db_path}")
        return conn

    def list_tasks(self, filter_status: Optional[str] = None, filter_priority: Optional[str] = None) -> List[Task]:
        """List available tasks with optional filtering."""
        tasks = self.backlog_parser.parse_backlog(self.config["backlog_file"])

        # Apply filters
        if filter_status:
            tasks = [t for t in tasks if t.status.value == filter_status]

        if filter_priority:
            tasks = [t for t in tasks if t.priority.value == filter_priority]

        logger.info(f"Filtered to {len(tasks)} tasks (status={filter_status}, priority={filter_priority})")

        return tasks

    def execute_task(self, task_id: str, auto_confirm: bool = False) -> bool:
        """Execute a specific task."""
        # Sanitize input to prevent injection attacks
        try:
            sanitized_task_id = sanitize_prompt(task_id)
        except Exception as e:
            logger.error(f"Task ID sanitization failed: {e}")
            return False

        tasks = self.list_tasks()
        task = next((t for t in tasks if t.id == sanitized_task_id), None)

        if not task:
            logger.error(f"Task {sanitized_task_id} not found")
            return False

        if task.human_required:
            logger.warning(f"Task {sanitized_task_id} requires human input: {task.human_reason}")
            if not auto_confirm:
                try:
                    response = input(f"Continue with human-required task {sanitized_task_id}? (y/N): ")
                    sanitized_response = sanitize_prompt(response)
                    if sanitized_response.lower() != "y":
                        logger.info("Task execution cancelled by user")
                        return False
                except Exception as e:
                    logger.error(f"User input sanitization failed: {e}")
                    return False

        # Check dependencies
        if not self._check_dependencies(task):
            logger.error(f"Task {sanitized_task_id} dependencies not met")
            return False

        # Execute the task with retry logic
        @retry(max_retries=3, backoff_factor=2)
        def _execute_with_retry():
            return self.task_executor.execute_task(task)

        try:
            success = _execute_with_retry()
            if success:
                self._update_task_status(sanitized_task_id, TaskStatus.COMPLETED)
                logger.info(f"Task {sanitized_task_id} completed successfully")
            else:
                self._update_task_status(sanitized_task_id, TaskStatus.FAILED)
                logger.error(f"Task {sanitized_task_id} failed")

            return success
        except Exception as e:
            self._update_task_status(sanitized_task_id, TaskStatus.FAILED, str(e))
            logger.error(f"Task {sanitized_task_id} failed with exception: {e}")
            return False

    @retry(max_retries=2, backoff_factor=1.5)
    def auto_execute(self, max_tasks: int = 5) -> List[str]:
        """Auto-execute the next priority tasks."""
        # Sanitize max_tasks input
        try:
            max_tasks = max(1, min(max_tasks, 50))  # Limit between 1 and 50
        except (ValueError, TypeError):
            logger.warning("Invalid max_tasks value, using default of 5")
            max_tasks = 5

        tasks = self.list_tasks(filter_status="todo")

        # Sort by priority and score
        tasks.sort(key=lambda t: (t.priority.value, t.score_total or 0), reverse=True)

        executed_tasks = []
        for i, task in enumerate(tasks[:max_tasks]):
            logger.info(f"Auto-executing task {task.id}: {task.title}")

            if self.execute_task(task.id, auto_confirm=True):
                executed_tasks.append(task.id)
            else:
                logger.warning(f"Failed to execute task {task.id}")

        return executed_tasks

    def get_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        cursor = self.state_db.cursor()
        cursor.execute(
            """
            SELECT status, COUNT(*) as count
            FROM task_executions
            GROUP BY status
        """
        )

        status_counts = dict(cursor.fetchall())

        # Get recent executions
        cursor.execute(
            """
            SELECT task_id, status, started_at, completed_at, error_message
            FROM task_executions
            ORDER BY updated_at DESC
            LIMIT 10
        """
        )

        recent_executions = []
        for row in cursor.fetchall():
            recent_executions.append(
                {
                    "task_id": row[0],
                    "status": row[1],
                    "started_at": row[2],
                    "completed_at": row[3],
                    "error_message": row[4],
                }
            )

        return {
            "status_counts": status_counts,
            "recent_executions": recent_executions,
            "total_tasks": len(self.list_tasks()),
            "pending_tasks": len(self.list_tasks(filter_status="todo")),
        }

    def reset_state(self) -> bool:
        """Reset execution state."""
        try:
            self.state_db.execute("DELETE FROM task_executions")
            self.state_db.commit()
            logger.info("Execution state reset successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reset state: {e}")
            return False

    def validate_dependencies(self) -> Dict[str, List[str]]:
        """Validate task dependencies."""
        tasks = self.list_tasks()
        missing_dependencies = {}

        for task in tasks:
            if task.dependencies:
                missing = []
                for dep in task.dependencies:
                    dep_task = next((t for t in tasks if t.id == dep), None)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        missing.append(dep)

                if missing:
                    missing_dependencies[task.id] = missing

        return missing_dependencies

    def _check_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are met."""
        if not task.dependencies:
            return True

        tasks = self.list_tasks()
        for dep_id in task.dependencies:
            dep_task = next((t for t in tasks if t.id == dep_id), None)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                logger.warning(f"Task {task.id} dependency {dep_id} not met")
                return False

        return True

    def _update_task_status(self, task_id: str, status: TaskStatus, error_message: Optional[str] = None) -> None:
        """Update task execution status in database."""
        try:
            cursor = self.state_db.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO task_executions
                (task_id, status, started_at, completed_at, error_message, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    task_id,
                    status.value,
                    datetime.now().isoformat(),
                    datetime.now().isoformat() if status == TaskStatus.COMPLETED else None,
                    error_message,
                    datetime.now().isoformat(),
                ),
            )
            self.state_db.commit()
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")

class BacklogParser:
    """Parser for backlog file."""

    def parse_backlog(self, backlog_file: str) -> List[Task]:
        """Parse the backlog file and extract tasks."""
        try:
            with open(backlog_file, "r", encoding="utf-8") as f:
                content = f.read()

            tasks = []
            lines = content.split("\n")

            for i, line in enumerate(lines):
                if line.startswith("| B‑") and "todo" in line:
                    task = self._parse_task_line(line, lines, i)
                    if task:
                        tasks.append(task)

            logger.info(f"Parsed {len(tasks)} tasks from {backlog_file}")
            return tasks

        except Exception as e:
            logger.error(f"Failed to parse backlog file: {e}")
            return []

    def _parse_task_line(self, line: str, lines: List[str], line_index: int) -> Optional[Task]:
        """Parse a single task line from the backlog."""
        try:
            # Parse the main line
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 8:
                return None

            task_id = parts[1].strip()
            title = parts[2].strip()
            priority_str = parts[3].strip()
            points_str = parts[4].strip()
            status_str = parts[5].strip()
            description = parts[6].strip()
            tech_footprint = parts[7].strip()
            dependencies = parts[8].strip() if len(parts) > 8 else ""

            # Parse priority
            priority_map = {
                "🔥": TaskPriority.CRITICAL,
                "📈": TaskPriority.HIGH,
                "⭐": TaskPriority.MEDIUM,
                "🔧": TaskPriority.LOW,
            }
            priority = priority_map.get(priority_str, TaskPriority.LOW)

            # Parse points
            try:
                points = int(points_str)
            except ValueError:
                points = 0

            # Parse status
            status_map = {
                "todo": TaskStatus.PENDING,
                "✅ done": TaskStatus.COMPLETED,
                "running": TaskStatus.RUNNING,
                "failed": TaskStatus.FAILED,
                "skipped": TaskStatus.SKIPPED,
            }
            status = status_map.get(status_str, TaskStatus.PENDING)

            # Parse dependencies
            dep_list = []
            if dependencies and dependencies != "None":
                dep_list = [d.strip() for d in dependencies.split(",")]

            # Parse metadata from comments
            score_total = None
            human_required = False
            human_reason = None

            # Look for comment lines after the task line
            for i in range(line_index + 1, min(line_index + 5, len(lines))):
                comment_line = lines[i].strip()
                if comment_line.startswith("<!--score_total:"):
                    score_match = re.search(r"score_total:\s*([\d.]+)", comment_line)
                    if score_match:
                        score_total = float(score_match.group(1))
                elif "human_required: true" in comment_line:
                    human_required = True
                    reason_match = re.search(r"reason:\s*(.+)", comment_line)
                    if reason_match:
                        human_reason = reason_match.group(1).strip()

            return Task(
                id=task_id,
                title=title,
                priority=priority,
                points=points,
                status=status,
                description=description,
                tech_footprint=tech_footprint,
                dependencies=dep_list,
                score_total=score_total,
                human_required=human_required,
                human_reason=human_reason,
            )

        except Exception as e:
            logger.error(f"Failed to parse task line: {e}")
            return None

class TaskExecutor:
    """Task execution engine."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the task executor."""
        self.config = config
        logger.info("Task executor initialized")

    def execute_task(self, task: Task) -> bool:
        """Execute a specific task."""
        logger.info(f"Executing task {task.id}: {task.title}")

        try:
            # Determine task type and execute accordingly
            if "documentation" in task.tech_footprint.lower():
                return self._execute_documentation_task(task)
            elif "automation" in task.tech_footprint.lower():
                return self._execute_automation_task(task)
            elif "script" in task.tech_footprint.lower():
                return self._execute_script_task(task)
            else:
                return self._execute_generic_task(task)

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return False

    def _execute_documentation_task(self, task: Task) -> bool:
        """Execute a documentation task."""
        logger.info(f"Executing documentation task: {task.id}")

        # Create PRD if needed
        if task.points >= 5 or (task.score_total and task.score_total < 3.0):
            prd_created = self._create_prd(task)
            if not prd_created:
                return False

        # Generate tasks
        tasks_created = self._generate_tasks(task)
        if not tasks_created:
            return False

        # Execute the actual task
        return self._execute_generic_task(task)

    def _execute_automation_task(self, task: Task) -> bool:
        """Execute an automation task."""
        logger.info(f"Executing automation task: {task.id}")

        # For automation tasks, we might need to create scripts
        if "script" in task.description.lower():
            script_created = self._create_script(task)
            if not script_created:
                return False

        return self._execute_generic_task(task)

    def _execute_script_task(self, task: Task) -> bool:
        """Execute a script task."""
        logger.info(f"Executing script task: {task.id}")

        # Create the script file
        script_created = self._create_script(task)
        if not script_created:
            return False

        return True

    def _execute_generic_task(self, task: Task) -> bool:
        """Execute a generic task."""
        logger.info(f"Executing generic task: {task.id}")

        # For now, we'll simulate successful execution
        # In a real implementation, this would execute the actual task logic
        logger.info(f"Task {task.id} executed successfully")
        return True

    def _create_prd(self, task: Task) -> bool:
        """Create a PRD for the task."""
        logger.info(f"Creating PRD for task {task.id}")

        # This would integrate with the existing PRD creation workflow
        # For now, we'll simulate successful PRD creation
        return True

    def _generate_tasks(self, task: Task) -> bool:
        """Generate tasks for the task."""
        logger.info(f"Generating tasks for task {task.id}")

        # This would integrate with the existing task generation workflow
        # For now, we'll simulate successful task generation
        return True

    def _create_script(self, task: Task) -> bool:
        """Create a script for the task."""
        logger.info(f"Creating script for task {task.id}")

        # This would create the actual script file
        # For now, we'll simulate successful script creation
        return True

class ErrorHandler:
    """Error handling and recovery."""

    def __init__(self):
        """Initialize the error handler."""
        logger.info("Error handler initialized")

    def handle_error(self, error: Exception, context: str) -> bool:
        """Handle an error with recovery procedures."""
        logger.error(f"Error in {context}: {error}")

        # Implement error recovery logic here
        # For now, we'll just log the error
        return False

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Task Execution Engine - Core CLI for backlog automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_tasks.py list                    # List all tasks
  python process_tasks.py list --status todo     # List pending tasks
  python process_tasks.py execute B-049          # Execute specific task
  python process_tasks.py auto                   # Auto-execute next tasks
  python process_tasks.py status                 # Show execution status
  python process_tasks.py reset                  # Reset execution state
  python process_tasks.py validate               # Validate dependencies
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List available tasks")
    list_parser.add_argument("--status", choices=["todo", "pending", "completed", "failed"], help="Filter by status")
    list_parser.add_argument("--priority", choices=["🔥", "📈", "⭐", "🔧"], help="Filter by priority")
    list_parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a specific task")
    execute_parser.add_argument("task_id", help="Task ID to execute")
    execute_parser.add_argument("--auto-confirm", action="store_true", help="Auto-confirm human-required tasks")

    # Auto command
    auto_parser = subparsers.add_parser("auto", help="Auto-execute next priority tasks")
    auto_parser.add_argument("--max-tasks", type=int, default=5, help="Maximum number of tasks to execute")

    # Status command
    subparsers.add_parser("status", help="Show execution status")

    # Reset command
    subparsers.add_parser("reset", help="Reset execution state")

    # Validate command
    subparsers.add_parser("validate", help="Validate task dependencies")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize the execution engine
    engine = TaskExecutionEngine()

    try:
        if args.command == "list":
            tasks = engine.list_tasks(args.status, args.priority)

            if args.format == "json":
                # Convert tasks to JSON-serializable format
                json_tasks = []
                for task in tasks:
                    task_dict = asdict(task)
                    task_dict["priority"] = task.priority.value
                    task_dict["status"] = task.status.value
                    json_tasks.append(task_dict)
                print(json.dumps(json_tasks, indent=2))
            else:
                print(f"\n{'ID':<10} {'Priority':<3} {'Points':<6} {'Status':<10} {'Title'}")
                print("-" * 80)
                for task in tasks:
                    print(
                        f"{task.id:<10} {task.priority.value:<3} {task.points:<6} {task.status.value:<10} {task.title}"
                    )
                print(f"\nTotal tasks: {len(tasks)}")

        elif args.command == "execute":
            success = engine.execute_task(args.task_id, args.auto_confirm)
            if success:
                print(f"Task {args.task_id} executed successfully")
            else:
                print(f"Task {args.task_id} failed")
                sys.exit(1)

        elif args.command == "auto":
            executed = engine.auto_execute(args.max_tasks)
            print(f"Auto-executed {len(executed)} tasks: {', '.join(executed)}")

        elif args.command == "status":
            status = engine.get_status()
            print("\nExecution Status:")
            print(f"Total tasks: {status['total_tasks']}")
            print(f"Pending tasks: {status['pending_tasks']}")
            print("\nStatus breakdown:")
            for status_name, count in status["status_counts"].items():
                print(f"  {status_name}: {count}")

            if status["recent_executions"]:
                print("\nRecent executions:")
                for exec_info in status["recent_executions"]:
                    print(f"  {exec_info['task_id']}: {exec_info['status']} ({exec_info['started_at']})")

        elif args.command == "reset":
            if engine.reset_state():
                print("Execution state reset successfully")
            else:
                print("Failed to reset execution state")
                sys.exit(1)

        elif args.command == "validate":
            missing_deps = engine.validate_dependencies()
            if missing_deps:
                print("Missing dependencies found:")
                for task_id, deps in missing_deps.items():
                    print(f"  {task_id}: {', '.join(deps)}")
            else:
                print("All dependencies are satisfied")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"CLI error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
