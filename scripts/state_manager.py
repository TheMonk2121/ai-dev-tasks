#!/usr/bin/env python3.12.123.11
"""
State Management Module

This module provides comprehensive state management for task execution,
tracking progress, completed tasks, error states, and execution history.

Author: AI Development Ecosystem
Version: 1.0
Last Updated: 2024-08-07
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ExecutionRecord:
    """Execution record data structure."""
    task_id: str
    status: TaskStatus
    started_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None
    retry_count: int = 0
    progress: float = 0.0
    execution_time: float | None = None
    metadata: dict[str, Any] | None = None

@dataclass
class TaskMetadata:
    """Task metadata data structure."""
    task_id: str
    title: str
    priority: str
    points: int
    description: str
    tech_footprint: str
    dependencies: str
    score_total: float | None = None
    human_required: bool = False
    human_reason: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class StateManager:
    """Comprehensive state management system for task execution."""
    
    def __init__(self, db_path: str = "task_execution.db"):
        """Initialize the state manager with database connection."""
        self.db_path = db_path
        self.conn = self._init_database()
        logger.info(f"State manager initialized with database: {db_path}")
    
    def _init_database(self) -> sqlite3.Connection:
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        
        # Create task_executions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_executions (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                progress REAL DEFAULT 0.0,
                execution_time REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create task_metadata table
        conn.execute("""
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
        """)
        
        # Create execution_history table for detailed history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                message TEXT,
                metadata TEXT,
                FOREIGN KEY (task_id) REFERENCES task_executions (task_id)
            )
        """)
        
        # Create performance_metrics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                task_id TEXT PRIMARY KEY,
                avg_execution_time REAL,
                success_rate REAL,
                total_executions INTEGER DEFAULT 0,
                successful_executions INTEGER DEFAULT 0,
                failed_executions INTEGER DEFAULT 0,
                last_execution TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_task_executions_status ON task_executions (status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_task_executions_started_at ON task_executions (started_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_execution_history_task_id ON execution_history (task_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_execution_history_timestamp ON execution_history (timestamp)")
        
        conn.commit()
        logger.info("Database tables and indexes created successfully")
        return conn
    
    def start_task_execution(self, task_id: str, metadata: dict[str, Any] | None = None) -> bool:
        """Start execution of a task."""
        try:
            cursor = self.conn.cursor()
            
            # Insert or update execution record
            cursor.execute("""
                INSERT OR REPLACE INTO task_executions 
                (task_id, status, started_at, retry_count, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                TaskStatus.RUNNING.value,
                datetime.now().isoformat(),
                0,
                json.dumps(metadata) if metadata else None,
                datetime.now().isoformat()
            ))
            
            # Add to execution history
            cursor.execute("""
                INSERT INTO execution_history (task_id, status, timestamp, message, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                task_id,
                TaskStatus.RUNNING.value,
                datetime.now().isoformat(),
                "Task execution started",
                json.dumps(metadata) if metadata else None
            ))
            
            self.conn.commit()
            logger.info(f"Started execution of task {task_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to start task execution for {task_id}: {e}")
            return False
    
    def complete_task_execution(self, task_id: str, success: bool = True, 
                              error_message: str | None = None,
                              execution_time: float | None = None) -> bool:
        """Complete execution of a task."""
        try:
            cursor = self.conn.cursor()
            
            # Get current execution record
            cursor.execute("SELECT started_at, retry_count FROM task_executions WHERE task_id = ?", (task_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"No execution record found for task {task_id}")
                return False
            
            started_at = datetime.fromisoformat(result[0])
            retry_count = result[1]
            completed_at = datetime.now()
            
            # Calculate execution time if not provided
            if execution_time is None:
                execution_time = (completed_at - started_at).total_seconds()
            
            # Determine status
            status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            
            # Update execution record
            cursor.execute("""
                UPDATE task_executions 
                SET status = ?, completed_at = ?, error_message = ?, execution_time = ?, updated_at = ?
                WHERE task_id = ?
            """, (
                status.value,
                completed_at.isoformat(),
                error_message,
                execution_time,
                datetime.now().isoformat(),
                task_id
            ))
            
            # Add to execution history
            cursor.execute("""
                INSERT INTO execution_history (task_id, status, timestamp, message, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                task_id,
                status.value,
                completed_at.isoformat(),
                f"Task execution {'completed' if success else 'failed'}",
                json.dumps({
                    "execution_time": execution_time,
                    "error_message": error_message,
                    "retry_count": retry_count
                })
            ))
            
            # Update performance metrics
            self._update_performance_metrics(task_id, success, execution_time)
            
            self.conn.commit()
            logger.info(f"Completed execution of task {task_id} with status {status.value}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to complete task execution for {task_id}: {e}")
            return False
    
    def update_task_progress(self, task_id: str, progress: float, 
                           message: str | None = None) -> bool:
        """Update progress of a running task."""
        try:
            cursor = self.conn.cursor()
            
            # Update progress
            cursor.execute("""
                UPDATE task_executions 
                SET progress = ?, updated_at = ?
                WHERE task_id = ?
            """, (progress, datetime.now().isoformat(), task_id))
            
            # Add progress to history
            if message:
                cursor.execute("""
                    INSERT INTO execution_history (task_id, status, timestamp, message)
                    VALUES (?, ?, ?, ?)
                """, (
                    task_id,
                    TaskStatus.RUNNING.value,
                    datetime.now().isoformat(),
                    f"Progress: {progress:.1%} - {message}"
                ))
            
            self.conn.commit()
            logger.debug(f"Updated progress for task {task_id}: {progress:.1%}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update progress for task {task_id}: {e}")
            return False
    
    def retry_task_execution(self, task_id: str, error_message: str | None = None) -> bool:
        """Retry execution of a failed task."""
        try:
            cursor = self.conn.cursor()
            
            # Get current retry count
            cursor.execute("SELECT retry_count FROM task_executions WHERE task_id = ?", (task_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"No execution record found for task {task_id}")
                return False
            
            retry_count = result[0] + 1
            
            # Update retry count and reset status
            cursor.execute("""
                UPDATE task_executions 
                SET status = ?, retry_count = ?, error_message = ?, updated_at = ?
                WHERE task_id = ?
            """, (
                TaskStatus.PENDING.value,
                retry_count,
                error_message,
                datetime.now().isoformat(),
                task_id
            ))
            
            # Add retry to history
            cursor.execute("""
                INSERT INTO execution_history (task_id, status, timestamp, message)
                VALUES (?, ?, ?, ?)
            """, (
                task_id,
                TaskStatus.PENDING.value,
                datetime.now().isoformat(),
                f"Retry attempt {retry_count}"
            ))
            
            self.conn.commit()
            logger.info(f"Retry {retry_count} initiated for task {task_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to retry task execution for {task_id}: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> ExecutionRecord | None:
        """Get current status of a task."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT task_id, status, started_at, completed_at, error_message, 
                       retry_count, progress, execution_time, metadata
                FROM task_executions 
                WHERE task_id = ?
            """, (task_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            return ExecutionRecord(
                task_id=result[0],
                status=TaskStatus(result[1]),
                started_at=datetime.fromisoformat(result[2]),
                completed_at=datetime.fromisoformat(result[3]) if result[3] else None,
                error_message=result[4],
                retry_count=result[5],
                progress=result[6],
                execution_time=result[7],
                metadata=json.loads(result[8]) if result[8] else None
            )
        
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            return None
    
    def get_execution_history(self, task_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get execution history for a task."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT status, timestamp, message, metadata
                FROM execution_history 
                WHERE task_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (task_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "status": row[0],
                    "timestamp": row[1],
                    "message": row[2],
                    "metadata": json.loads(row[3]) if row[3] else None
                })
            
            return history
        
        except Exception as e:
            logger.error(f"Failed to get execution history for {task_id}: {e}")
            return []
    
    def get_all_task_statuses(self) -> dict[str, ExecutionRecord]:
        """Get status of all tasks."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT task_id, status, started_at, completed_at, error_message, 
                       retry_count, progress, execution_time, metadata
                FROM task_executions
                ORDER BY updated_at DESC
            """)
            
            tasks = {}
            for row in cursor.fetchall():
                tasks[row[0]] = ExecutionRecord(
                    task_id=row[0],
                    status=TaskStatus(row[1]),
                    started_at=datetime.fromisoformat(row[2]),
                    completed_at=datetime.fromisoformat(row[3]) if row[3] else None,
                    error_message=row[4],
                    retry_count=row[5],
                    progress=row[6],
                    execution_time=row[7],
                    metadata=json.loads(row[8]) if row[8] else None
                )
            
            return tasks
        
        except Exception as e:
            logger.error(f"Failed to get all task statuses: {e}")
            return {}
    
    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive execution statistics."""
        try:
            cursor = self.conn.cursor()
            
            # Status counts
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM task_executions
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())
            
            # Performance metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    AVG(execution_time) as avg_execution_time,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tasks,
                    SUM(retry_count) as total_retries
                FROM task_executions
            """)
            performance = cursor.fetchone()
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) as recent_executions
                FROM task_executions
                WHERE updated_at >= datetime('now', '-24 hours')
            """)
            recent_count = cursor.fetchone()[0]
            
            return {
                "status_counts": status_counts,
                "total_tasks": performance[0],
                "avg_execution_time": performance[1],
                "completed_tasks": performance[2],
                "failed_tasks": performance[3],
                "total_retries": performance[4],
                "recent_executions": recent_count,
                "success_rate": (performance[2] / performance[0] * 100) if performance[0] > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def store_task_metadata(self, metadata: TaskMetadata) -> bool:
        """Store task metadata."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO task_metadata 
                (task_id, title, priority, points, description, tech_footprint, 
                 dependencies, score_total, human_required, human_reason, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.task_id,
                metadata.title,
                metadata.priority,
                metadata.points,
                metadata.description,
                metadata.tech_footprint,
                metadata.dependencies,
                metadata.score_total,
                metadata.human_required,
                metadata.human_reason,
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            logger.info(f"Stored metadata for task {metadata.task_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store metadata for task {metadata.task_id}: {e}")
            return False
    
    def get_task_metadata(self, task_id: str) -> TaskMetadata | None:
        """Get task metadata."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT task_id, title, priority, points, description, tech_footprint,
                       dependencies, score_total, human_required, human_reason, created_at, updated_at
                FROM task_metadata 
                WHERE task_id = ?
            """, (task_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            return TaskMetadata(
                task_id=result[0],
                title=result[1],
                priority=result[2],
                points=result[3],
                description=result[4],
                tech_footprint=result[5],
                dependencies=result[6],
                score_total=result[7],
                human_required=bool(result[8]),
                human_reason=result[9],
                created_at=datetime.fromisoformat(result[10]) if result[10] else None,
                updated_at=datetime.fromisoformat(result[11]) if result[11] else None
            )
        
        except Exception as e:
            logger.error(f"Failed to get metadata for task {task_id}: {e}")
            return None
    
    def _update_performance_metrics(self, task_id: str, success: bool, execution_time: float) -> None:
        """Update performance metrics for a task."""
        try:
            cursor = self.conn.cursor()
            
            # Get current metrics
            cursor.execute("""
                SELECT total_executions, successful_executions, failed_executions, avg_execution_time
                FROM performance_metrics 
                WHERE task_id = ?
            """, (task_id,))
            
            result = cursor.fetchone()
            if result:
                total_executions = result[0] + 1
                successful_executions = result[1] + (1 if success else 0)
                failed_executions = result[2] + (0 if success else 1)
                
                # Calculate new average execution time
                old_avg = result[3] or 0
                new_avg = ((old_avg * (total_executions - 1)) + execution_time) / total_executions
                
                cursor.execute("""
                    UPDATE performance_metrics 
                    SET total_executions = ?, successful_executions = ?, failed_executions = ?,
                        avg_execution_time = ?, last_execution = ?, updated_at = ?
                    WHERE task_id = ?
                """, (
                    total_executions, successful_executions, failed_executions,
                    new_avg, datetime.now().isoformat(), datetime.now().isoformat(), task_id
                ))
            else:
                # Create new metrics record
                cursor.execute("""
                    INSERT INTO performance_metrics 
                    (task_id, total_executions, successful_executions, failed_executions,
                     avg_execution_time, last_execution, updated_at)
                    VALUES (?, 1, ?, ?, ?, ?, ?)
                """, (
                    task_id,
                    1 if success else 0,
                    0 if success else 1,
                    execution_time,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            
            self.conn.commit()
        
        except Exception as e:
            logger.error(f"Failed to update performance metrics for {task_id}: {e}")
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """Clean up old execution history records."""
        try:
            cursor = self.conn.cursor()
            
            # Count records to be deleted
            cursor.execute(f"""
                SELECT COUNT(*) FROM execution_history 
                WHERE timestamp < datetime('now', '-{days} days')
            """)
            
            count = cursor.fetchone()[0]
            
            # Delete old records
            cursor.execute(f"""
                DELETE FROM execution_history 
                WHERE timestamp < datetime('now', '-{days} days')
            """)
            
            self.conn.commit()
            logger.info(f"Cleaned up {count} old execution history records")
            return count
        
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return 0
    
    def reset_state(self) -> bool:
        """Reset all execution state."""
        try:
            cursor = self.conn.cursor()
            
            # Clear all tables
            cursor.execute("DELETE FROM task_executions")
            cursor.execute("DELETE FROM execution_history")
            cursor.execute("DELETE FROM performance_metrics")
            
            self.conn.commit()
            logger.info("Reset all execution state")
            return True
        
        except Exception as e:
            logger.error(f"Failed to reset state: {e}")
            return False
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("State manager database connection closed")

def main():
    """CLI interface for the state manager (dev utilities)."""
    import argparse
    import csv
    
    parser = argparse.ArgumentParser(description="State Manager CLI")
    parser.add_argument('--db', default='test_task_execution.db', help='Database path')
    parser.add_argument('--task-id', default='B-049', help='Task ID to operate on')
    parser.add_argument('--action', choices=['start', 'complete', 'status', 'history', 'stats', 'reset'],
                       default='status', help='Action to perform')
    parser.add_argument('--stats', action='store_true', help='Shortcut to print statistics (alias of action=stats)')
    parser.add_argument('--export-csv', metavar='FILE', help='Export performance metrics to CSV file')
    
    args = parser.parse_args()
    
    # Allow --stats as an alias
    if args.stats:
        args.action = 'stats'
    
    state_manager = StateManager(args.db)
    
    try:
        if args.action == 'start':
            success = state_manager.start_task_execution(args.task_id, {"trigger": "cli"})
            print(f"Started task execution: {success}")
        
        elif args.action == 'complete':
            success = state_manager.complete_task_execution(args.task_id, success=True)
            print(f"Completed task execution: {success}")
        
        elif args.action == 'status':
            status = state_manager.get_task_status(args.task_id)
            if status:
                print(f"Task status: {status}")
            else:
                print("No status found for task")
        
        elif args.action == 'history':
            history = state_manager.get_execution_history(args.task_id)
            print(f"Execution history ({len(history)} records):")
            for record in history:
                print(f"  {record['timestamp']}: {record['status']} - {record['message']}")
        
        elif args.action == 'stats':
            stats = state_manager.get_statistics()
            print("Execution statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            # Optional CSV export
            if args.export_csv:
                # Compose a simple metrics row set from statistics
                with open(args.export_csv, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['metric', 'value'])
                    for key, value in stats.items():
                        writer.writerow([key, value])
                print(f"Exported statistics to {args.export_csv}")
        
        elif args.action == 'reset':
            success = state_manager.reset_state()
            print(f"Reset state: {success}")
    
    finally:
        state_manager.close()

if __name__ == "__main__":
    main()
