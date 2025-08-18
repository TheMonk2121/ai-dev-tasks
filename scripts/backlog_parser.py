#!/usr/bin/env python3.12.123.11
"""
Backlog Parser Module

This module provides robust parsing functionality for the 000_backlog.md file,
extracting todo items with metadata, dependency tracking, and priority analysis.

Author: AI Development Ecosystem
Version: 1.0
Last Updated: 2024-08-07
"""

import argparse
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

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
    dependencies: list[str]
    score_total: float | None = None
    human_required: bool = False
    human_reason: str | None = None
    default_executor: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

@dataclass
class ParsedBacklog:
    """Complete parsed backlog data structure."""
    tasks: list[Task]
    metadata: dict[str, Any]
    parse_time: datetime
    file_path: str
    total_tasks: int
    pending_tasks: int
    completed_tasks: int

class BacklogParser:
    """Parser for backlog file with comprehensive metadata extraction."""
    
    def __init__(self):
        """Initialize the backlog parser."""
        self.priority_map = {
            "🔥": TaskPriority.CRITICAL,
            "📈": TaskPriority.HIGH,
            "⭐": TaskPriority.MEDIUM,
            "🔧": TaskPriority.LOW
        }
        
        self.status_map = {
            "todo": TaskStatus.PENDING,
            "✅ done": TaskStatus.COMPLETED,
            "running": TaskStatus.RUNNING,
            "failed": TaskStatus.FAILED,
            "skipped": TaskStatus.SKIPPED
        }
        
        logger.info("Backlog parser initialized")
    
    def parse_backlog(self, backlog_file: str) -> list[Task]:
        """Parse the backlog file and extract tasks."""
        try:
            file_path = Path(backlog_file)
            if not file_path.exists():
                logger.error(f"Backlog file not found: {backlog_file}")
                return []
            
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            tasks = []
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if self._is_task_line(line):
                    task = self._parse_task_line(line, lines, i)
                    if task:
                        tasks.append(task)
            
            logger.info(f"Parsed {len(tasks)} tasks from {backlog_file}")
            return tasks
        
        except Exception as e:
            logger.error(f"Failed to parse backlog file: {e}")
            return []
    
    def parse_backlog_complete(self, backlog_file: str) -> ParsedBacklog:
        """Parse the backlog file with complete metadata."""
        tasks = self.parse_backlog(backlog_file)
        
        # Extract metadata
        metadata = self._extract_metadata(backlog_file)
        
        # Calculate statistics
        pending_tasks = len([t for t in tasks if t.status == TaskStatus.PENDING])
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        
        return ParsedBacklog(
            tasks=tasks,
            metadata=metadata,
            parse_time=datetime.now(),
            file_path=backlog_file,
            total_tasks=len(tasks),
            pending_tasks=pending_tasks,
            completed_tasks=completed_tasks
        )
    
    def _is_task_line(self, line: str) -> bool:
        """Check if a line represents a task entry."""
        return (line.startswith('| B‑') and 
                ('todo' in line or '✅ done' in line or 'running' in line))
    
    def _parse_task_line(self, line: str, lines: list[str], line_index: int) -> Task | None:
        """Parse a single task line from the backlog."""
        try:
            # Parse the main line
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 8:
                logger.warning(f"Insufficient parts in task line: {line}")
                return None
            
            # Extract basic fields
            task_id = parts[1].strip()
            title = parts[2].strip()
            priority_str = parts[3].strip()
            points_str = parts[4].strip()
            status_str = parts[5].strip()
            description = parts[6].strip()
            tech_footprint = parts[7].strip()
            dependencies = parts[8].strip() if len(parts) > 8 else ""
            
            # Parse priority
            priority = self.priority_map.get(priority_str, TaskPriority.LOW)
            
            # Parse points
            try:
                points = int(points_str)
            except ValueError:
                logger.warning(f"Invalid points value for task {task_id}: {points_str}")
                points = 0
            
            # Parse status
            status = self.status_map.get(status_str, TaskStatus.PENDING)
            
            # Parse dependencies
            dep_list = self._parse_dependencies(dependencies)
            
            # Parse metadata from comments
            metadata = self._parse_metadata_comments(lines, line_index)
            
            return Task(
                id=task_id,
                title=title,
                priority=priority,
                points=points,
                status=status,
                description=description,
                tech_footprint=tech_footprint,
                dependencies=dep_list,
                score_total=metadata.get('score_total'),
                human_required=metadata.get('human_required', False),
                human_reason=metadata.get('human_reason')
            )
        
        except Exception as e:
            logger.error(f"Failed to parse task line: {e}")
            return None
    
    def _parse_dependencies(self, dependencies_str: str) -> list[str]:
        """Parse dependencies string into list."""
        if not dependencies_str or dependencies_str == "None":
            return []
        
        # Handle different dependency formats
        if "[" in dependencies_str and "]" in dependencies_str:
            # Format: [B-001, B-002]
            match = re.search(r'\[(.*?)\]', dependencies_str)
            if match:
                deps = match.group(1).split(',')
                return [d.strip() for d in deps if d.strip()]
        
        # Format: B-001, B-002
        deps = dependencies_str.split(',')
        return [d.strip() for d in deps if d.strip()]
    
    def _parse_metadata_comments(self, lines: list[str], line_index: int) -> dict[str, Any]:
        """Parse metadata from HTML comments after the task line."""
        metadata = {}
        
        # Look for comment lines after the task line (up to 10 lines)
        for i in range(line_index + 1, min(line_index + 10, len(lines))):
            comment_line = lines[i].strip()
            
            # Skip empty lines
            if not comment_line:
                continue
            
            # Stop if we hit another task line
            if comment_line.startswith('| B‑'):
                break
            
            # Parse score_total
            if comment_line.startswith('<!--score_total:'):
                score_match = re.search(r'score_total:\s*([\d.]+)', comment_line)
                if score_match:
                    metadata['score_total'] = float(score_match.group(1))
            
            # Parse human_required
            elif 'human_required: true' in comment_line:
                metadata['human_required'] = True
                reason_match = re.search(r'reason:\s*(.+)', comment_line)
                if reason_match:
                    metadata['human_reason'] = reason_match.group(1).strip()
            
            # Parse progress
            elif comment_line.startswith('<!--progress:'):
                progress_match = re.search(r'progress:\s*(.+)', comment_line)
                if progress_match:
                    metadata['progress'] = progress_match.group(1).strip()
            
            # Parse score breakdown
            elif comment_line.startswith('<!--score:'):
                score_breakdown = {}
                score_match = re.search(r'score:\s*\{([^}]+)\}', comment_line)
                if score_match:
                    score_parts = score_match.group(1).split(',')
                    for part in score_parts:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            try:
                                score_breakdown[key.strip()] = float(value.strip())
                            except ValueError:
                                pass
                    metadata['score_breakdown'] = score_breakdown

            # Parse default executor
            elif comment_line.startswith('<!-- default_executor:'):
                exec_match = re.search(r'default_executor:\s*([^\-]+)', comment_line)
                if exec_match:
                    metadata['default_executor'] = exec_match.group(1).strip()
        
        return metadata
    
    def _extract_metadata(self, backlog_file: str) -> dict[str, Any]:
        """Extract general metadata from the backlog file."""
        try:
            with open(backlog_file, encoding='utf-8') as f:
                content = f.read()
            
            metadata = {}
            
            # Extract last updated timestamp
            last_updated_match = re.search(r'\*Last Updated:\s*([^*]+)\*', content)
            if last_updated_match:
                metadata['last_updated'] = last_updated_match.group(1).strip()
            
            # Extract previously updated timestamp
            prev_updated_match = re.search(r'\*Previously Updated:\s*([^*]+)\*', content)
            if prev_updated_match:
                metadata['previously_updated'] = prev_updated_match.group(1).strip()
            
            # Extract next review
            next_review_match = re.search(r'\*Next Review:\s*([^*]+)\*', content)
            if next_review_match:
                metadata['next_review'] = next_review_match.group(1).strip()
            
            # Extract AI backlog meta
            ai_meta_match = re.search(r'<!-- AI-BACKLOG-META(.*?)-->', content, re.DOTALL)
            if ai_meta_match:
                ai_meta_content = ai_meta_match.group(1)
                metadata['ai_meta'] = self._parse_ai_meta(ai_meta_content)
            
            return metadata
        
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            return {}
    
    def _parse_ai_meta(self, ai_meta_content: str) -> dict[str, str]:
        """Parse AI backlog meta information."""
        meta = {}
        
        # Extract next_prd_command
        next_prd_match = re.search(r'next_prd_command:\s*\|(.*?)\|', ai_meta_content, re.DOTALL)
        if next_prd_match:
            meta['next_prd_command'] = next_prd_match.group(1).strip()
        
        # Extract sprint_planning
        sprint_match = re.search(r'sprint_planning:\s*\|(.*?)\|', ai_meta_content, re.DOTALL)
        if sprint_match:
            meta['sprint_planning'] = sprint_match.group(1).strip()
        
        # Extract scoring_system
        scoring_match = re.search(r'scoring_system:\s*\|(.*?)\|', ai_meta_content, re.DOTALL)
        if scoring_match:
            meta['scoring_system'] = scoring_match.group(1).strip()
        
        # Extract execution_responsibility
        exec_match = re.search(r'execution_responsibility:\s*\|(.*?)\|', ai_meta_content, re.DOTALL)
        if exec_match:
            meta['execution_responsibility'] = exec_match.group(1).strip()
        
        # Extract completion_tracking
        completion_match = re.search(r'completion_tracking:\s*\|(.*?)\|', ai_meta_content, re.DOTALL)
        if completion_match:
            meta['completion_tracking'] = completion_match.group(1).strip()
        
        # Extract timestamp_updates
        timestamp_match = re.search(r'timestamp_updates:\s*\|(.*?)\|', ai_meta_content, re.DOTALL)
        if timestamp_match:
            meta['timestamp_updates'] = timestamp_match.group(1).strip()
        
        return meta
    
    def validate_task(self, task: Task) -> list[str]:
        """Validate a task for completeness and correctness."""
        errors = []
        
        # Check required fields
        if not task.id:
            errors.append("Task ID is missing")
        
        if not task.title:
            errors.append("Task title is missing")
        
        if task.points < 0:
            errors.append("Task points cannot be negative")
        
        # Check ID format
        if not re.match(r'^B‑\d+$', task.id):
            errors.append(f"Invalid task ID format: {task.id}")
        
        # Check dependencies
        for dep in task.dependencies:
            if not re.match(r'^B‑\d+$', dep):
                errors.append(f"Invalid dependency format: {dep}")
        
        return errors
    
    def get_task_statistics(self, tasks: list[Task]) -> dict[str, Any]:
        """Get comprehensive statistics about tasks."""
        stats = {
            'total_tasks': len(tasks),
            'by_status': {},
            'by_priority': {},
            'by_points': {},
            'human_required': 0,
            'avg_score': 0.0,
            'dependency_stats': {}
        }
        
        # Count by status
        for task in tasks:
            status = task.status.value
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Count by priority
        for task in tasks:
            priority = task.priority.value
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        # Count by points
        for task in tasks:
            points = task.points
            stats['by_points'][points] = stats['by_points'].get(points, 0) + 1
        
        # Count human required
        stats['human_required'] = len([t for t in tasks if t.human_required])
        
        # Calculate average score
        scores = [t.score_total for t in tasks if t.score_total is not None]
        if scores:
            stats['avg_score'] = sum(scores) / len(scores)
        
        # Dependency statistics
        total_deps = 0
        max_deps = 0
        for task in tasks:
            deps_count = len(task.dependencies)
            total_deps += deps_count
            max_deps = max(max_deps, deps_count)
        
        stats['dependency_stats'] = {
            'total_dependencies': total_deps,
            'max_dependencies': max_deps,
            'avg_dependencies': total_deps / len(tasks) if tasks else 0
        }
        
        return stats

    def _pending(self, task: Task) -> bool:
        return task.status == TaskStatus.PENDING

    def _score(self, task: Task) -> float:
        return task.score_total if task.score_total is not None else 0.0

    def _is_ai_executable(self, task: Task) -> bool:
        if task.human_required:
            return False
        if task.status != TaskStatus.PENDING:
            return False
        return (task.default_executor or '').strip() == '003_process-task-list.md'

    def generate_lanes(self, tasks: list[Task], p0_count: int = 5, p1_count: int = 7, p2_count: int = 8) -> dict[str, list[Task]]:
        """Create P0/P1/P2 lanes from pending tasks by score_total."""
        pending = [t for t in tasks if self._pending(t)]
        pending.sort(key=self._score, reverse=True)
        lanes = {
            'p0': pending[:p0_count],
            'p1': pending[p0_count:p0_count+p1_count],
            'p2': pending[p0_count+p1_count:p0_count+p1_count+p2_count],
        }
        return lanes

    def generate_ai_exec_queue(self, tasks: list[Task], limit: int = 10) -> list[Task]:
        """Create AI-executable queue ordered by score_total, limited."""
        queue = [t for t in tasks if self._is_ai_executable(t)]
        queue.sort(key=self._score, reverse=True)
        return queue[:limit]

    def _format_task_bullet(self, task: Task) -> str:
        score = f"{task.score_total:.1f}" if task.score_total is not None else "-"
        return f"- {task.id} — {task.title} (score {score})"

    def render_sections_markdown(self, tasks: list[Task]) -> dict[str, str]:
        """Render markdown for P0/P1/P2 lanes and AI-exec queue."""
        lanes = self.generate_lanes(tasks)
        aiq = self.generate_ai_exec_queue(tasks)

        p0_md = ["", *[self._format_task_bullet(t) for t in lanes['p0']], ""]
        p1_md = ["", *[self._format_task_bullet(t) for t in lanes['p1']], ""]
        p2_md = ["", *[self._format_task_bullet(t) for t in lanes['p2']], ""]
        ai_md = ["", *[self._format_task_bullet(t) for t in aiq], ""]

        return {
            'P0 Lane': "\n".join(p0_md),
            'P1 Lane': "\n".join(p1_md),
            'P2 Lane': "\n".join(p2_md),
            'AI-Executable Queue (003)': "\n".join(ai_md),
        }

    def inject_sections(self, backlog_file: str) -> bool:
        """Replace section bodies under P0/P1/P2/AQ headers with auto-generated lists."""
        tasks = self.parse_backlog(backlog_file)
        sections = self.render_sections_markdown(tasks)

        try:
            path = Path(backlog_file)
            text = path.read_text(encoding='utf-8')
            lines = text.splitlines()

            def replace_section(title: str, new_body_md: str):
                header = f"## {title}"
                try:
                    start = next(i for i, ln in enumerate(lines) if ln.strip() == header)
                except StopIteration:
                    return
                # find next header (## ) after start
                end = None
                for i in range(start + 1, len(lines)):
                    if lines[i].startswith('## '):
                        end = i
                        break
                if end is None:
                    end = len(lines)
                # keep the header line, replace content underneath with new_body_md
                new_block = [lines[start], new_body_md.strip()] if new_body_md.strip() else [lines[start]]
                lines[start:end] = new_block

            for title, body in sections.items():
                replace_section(title, body)

            path.write_text("\n".join(lines) + "\n", encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Section injection failed: {e}")
            return False
    
    def export_tasks_json(self, tasks: list[Task], output_file: str) -> bool:
        """Export tasks to JSON file."""
        try:
            data = {
                'tasks': [asdict(task) for task in tasks],
                'export_time': datetime.now().isoformat(),
                'total_tasks': len(tasks)
            }
            
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(tasks)} tasks to {output_file}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export tasks to JSON: {e}")
            return False
    
    def find_tasks_by_criteria(self, tasks: list[Task], 
                              status: str | None = None,
                              priority: str | None = None,
                              min_points: int | None = None,
                              max_points: int | None = None,
                              human_required: bool | None = None,
                              min_score: float | None = None) -> list[Task]:
        """Find tasks matching specific criteria."""
        filtered_tasks = tasks
        
        if status:
            filtered_tasks = [t for t in filtered_tasks if t.status.value == status]
        
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t.priority.value == priority]
        
        if min_points is not None:
            filtered_tasks = [t for t in filtered_tasks if t.points >= min_points]
        
        if max_points is not None:
            filtered_tasks = [t for t in filtered_tasks if t.points <= max_points]
        
        if human_required is not None:
            filtered_tasks = [t for t in filtered_tasks if t.human_required == human_required]
        
        if min_score is not None:
            filtered_tasks = [t for t in filtered_tasks if t.score_total and t.score_total >= min_score]
        
        return filtered_tasks

def main():
    """Backlog parser CLI with stats, export, and lane/queue generation/injection."""
    
    parser = argparse.ArgumentParser(description="Backlog Parser")
    parser.add_argument('backlog_file', help='Path to backlog file')
    parser.add_argument('--export', help='Export to JSON file')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--filter-status', help='Filter by status')
    parser.add_argument('--filter-priority', help='Filter by priority')
    parser.add_argument('--generate-sections', action='store_true', help='Print P0/P1/P2 lanes and AI-exec queue markdown')
    parser.add_argument('--write-sections', action='store_true', help='Inject P0/P1/P2 lanes and AI-exec queue into backlog file')
    
    args = parser.parse_args()
    
    parser = BacklogParser()
    
    # Parse backlog
    parsed = parser.parse_backlog_complete(args.backlog_file)
    
    print(f"Parsed {parsed.total_tasks} tasks from {args.backlog_file}")
    print(f"Pending: {parsed.pending_tasks}, Completed: {parsed.completed_tasks}")
    
    # Show statistics
    if args.stats:
        stats = parser.get_task_statistics(parsed.tasks)
        print("\nStatistics:")
        print(f"By Status: {stats['by_status']}")
        print(f"By Priority: {stats['by_priority']}")
        print(f"Human Required: {stats['human_required']}")
        print(f"Average Score: {stats['avg_score']:.2f}")
    
    # Filter tasks
    if args.filter_status or args.filter_priority:
        filtered = parser.find_tasks_by_criteria(
            parsed.tasks,
            status=args.filter_status,
            priority=args.filter_priority
        )
        print(f"\nFiltered tasks ({len(filtered)}):")
        for task in filtered:
            print(f"  {task.id}: {task.title}")
    
    # Export to JSON
    if args.export:
        if parser.export_tasks_json(parsed.tasks, args.export):
            print(f"Exported to {args.export}")
        else:
            print("Export failed")

    if args.generate_sections:
        sections = parser.render_sections_markdown(parsed.tasks)
        print("\n# Generated Sections\n")
        for title, md in sections.items():
            print(f"## {title}")
            print(md)

    if args.write_sections:
        if parser.inject_sections(args.backlog_file):
            print("Sections injected successfully.")
        else:
            print("Section injection failed.")

if __name__ == "__main__":
    main()
