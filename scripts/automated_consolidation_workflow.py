#!/usr/bin/env python3
"""
Automated Consolidation Workflow Engine for B-1032

Executes consolidation plans, manages the consolidation process, and provides
rollback capabilities. Part of the t-t3 Authority Structure Implementation.
"""

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConsolidationStatus(Enum):
    """Status of consolidation operations."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class WorkflowStep(Enum):
    """Steps in the consolidation workflow."""

    VALIDATE_OPPORTUNITY = "validate_opportunity"
    CREATE_BACKUP = "create_backup"
    MERGE_CONTENT = "merge_content"
    UPDATE_REFERENCES = "update_references"
    VALIDATE_RESULT = "validate_result"
    COMMIT_CHANGES = "commit_changes"


@dataclass
class ConsolidationPlan:
    """A consolidation plan with execution details."""

    plan_id: str
    opportunity_id: str
    source_guides: List[str]
    target_guide: str
    consolidation_type: str
    merge_strategy: str
    estimated_effort: str
    risk_level: str
    steps: List[Dict[str, Any]]
    status: ConsolidationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class WorkflowExecution:
    """Execution details for a workflow step."""

    step_id: str
    plan_id: str
    step_type: WorkflowStep
    status: ConsolidationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result_data: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class ConsolidationResult:
    """Result of a consolidation operation."""

    plan_id: str
    success: bool
    target_guide_path: str
    merged_content_size: int
    removed_guides: List[str]
    updated_references: int
    validation_score: float
    rollback_available: bool
    execution_time_seconds: float
    result_timestamp: datetime


class AutomatedConsolidationWorkflow:
    """Main automated consolidation workflow engine."""

    def __init__(self, guides_dir: str = "400_guides", output_dir: str = "artifacts/consolidation"):
        self.guides_dir = Path(guides_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database for workflow tracking
        self.db_path = self.output_dir / "consolidation_workflow.db"
        self._init_database()

        # Backup directory for rollback capability
        self.backup_dir = self.output_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Workflow configuration
        self.workflow_config = {
            "max_concurrent_plans": 3,
            "timeout_seconds": 300,  # 5 minutes per plan
            "auto_rollback_on_failure": True,
            "validation_threshold": 0.7,
            "backup_retention_days": 30,
        }

    def _init_database(self):
        """Initialize SQLite database for workflow tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consolidation_plans (
                    id TEXT PRIMARY KEY,
                    opportunity_id TEXT,
                    source_guides TEXT,
                    target_guide TEXT,
                    consolidation_type TEXT,
                    merge_strategy TEXT,
                    estimated_effort TEXT,
                    risk_level TEXT,
                    steps TEXT,
                    status TEXT,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    id TEXT PRIMARY KEY,
                    plan_id TEXT,
                    step_type TEXT,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration_seconds REAL,
                    result_data TEXT,
                    error_message TEXT,
                    FOREIGN KEY (plan_id) REFERENCES consolidation_plans (id)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consolidation_results (
                    plan_id TEXT PRIMARY KEY,
                    success BOOLEAN,
                    target_guide_path TEXT,
                    merged_content_size INTEGER,
                    removed_guides TEXT,
                    updated_references INTEGER,
                    validation_score REAL,
                    rollback_available BOOLEAN,
                    execution_time_seconds REAL,
                    result_timestamp TEXT,
                    FOREIGN KEY (plan_id) REFERENCES consolidation_plans (id)
                )
            """
            )

    def create_consolidation_plan(self, opportunity: Dict[str, Any]) -> ConsolidationPlan:
        """Create a consolidation plan from an opportunity."""
        plan_id = f"plan_{int(time.time())}_{hashlib.md5(str(opportunity).encode()).hexdigest()[:8]}"

        # Define workflow steps
        steps = [
            {
                "step_id": f"{plan_id}_validate",
                "step_type": WorkflowStep.VALIDATE_OPPORTUNITY.value,
                "description": "Validate consolidation opportunity",
                "required": True,
                "timeout": 60,
            },
            {
                "step_id": f"{plan_id}_backup",
                "step_type": WorkflowStep.CREATE_BACKUP.value,
                "description": "Create backup of source guides",
                "required": True,
                "timeout": 120,
            },
            {
                "step_id": f"{plan_id}_merge",
                "step_type": WorkflowStep.MERGE_CONTENT.value,
                "description": "Merge content according to strategy",
                "required": True,
                "timeout": 300,
            },
            {
                "step_id": f"{plan_id}_references",
                "step_type": WorkflowStep.UPDATE_REFERENCES.value,
                "description": "Update cross-references",
                "required": True,
                "timeout": 180,
            },
            {
                "step_id": f"{plan_id}_validate_result",
                "step_type": WorkflowStep.VALIDATE_RESULT.value,
                "description": "Validate consolidation result",
                "required": True,
                "timeout": 120,
            },
            {
                "step_id": f"{plan_id}_commit",
                "step_type": WorkflowStep.COMMIT_CHANGES.value,
                "description": "Commit consolidation changes",
                "required": True,
                "timeout": 60,
            },
        ]

        plan = ConsolidationPlan(
            plan_id=plan_id,
            opportunity_id=opportunity.get("id", "unknown"),
            source_guides=opportunity.get("source_guides", []),
            target_guide=opportunity.get("target_guide", ""),
            consolidation_type=opportunity.get("consolidation_type", ""),
            merge_strategy=opportunity.get("merge_strategy", ""),
            estimated_effort=opportunity.get("estimated_effort", ""),
            risk_level=opportunity.get("risk_level", ""),
            steps=steps,
            status=ConsolidationStatus.PENDING,
            created_at=datetime.now(),
        )

        # Store plan in database
        self._store_consolidation_plan(plan)

        return plan

    def execute_consolidation_plan(self, plan: ConsolidationPlan) -> ConsolidationResult:
        """Execute a consolidation plan."""
        print(f"🚀 Executing consolidation plan: {plan.plan_id}")
        print(f"📁 Target: {plan.target_guide}")
        print(f"🔗 Sources: {', '.join(plan.source_guides)}")

        start_time = time.time()
        plan.started_at = datetime.now()
        plan.status = ConsolidationStatus.IN_PROGRESS
        self._update_plan_status(plan)

        try:
            # Execute each step
            for step_config in plan.steps:
                step_execution = self._execute_workflow_step(plan, step_config)

                if step_execution.status == ConsolidationStatus.FAILED:
                    plan.status = ConsolidationStatus.FAILED
                    plan.error_message = step_execution.error_message
                    self._update_plan_status(plan)

                    if self.workflow_config["auto_rollback_on_failure"]:
                        self._rollback_consolidation(plan)

                    return ConsolidationResult(
                        plan_id=plan.plan_id,
                        success=False,
                        target_guide_path="",
                        merged_content_size=0,
                        removed_guides=[],
                        updated_references=0,
                        validation_score=0.0,
                        rollback_available=False,
                        execution_time_seconds=time.time() - start_time,
                        result_timestamp=datetime.now(),
                    )

            # Plan completed successfully
            plan.status = ConsolidationStatus.COMPLETED
            plan.completed_at = datetime.now()
            self._update_plan_status(plan)

            # Generate result
            result = self._generate_consolidation_result(plan, time.time() - start_time)
            self._store_consolidation_result(result)

            print(f"✅ Consolidation plan completed successfully: {plan.plan_id}")
            return result

        except Exception as e:
            plan.status = ConsolidationStatus.FAILED
            plan.error_message = str(e)
            self._update_plan_status(plan)

            if self.workflow_config["auto_rollback_on_failure"]:
                self._rollback_consolidation(plan)

            print(f"❌ Consolidation plan failed: {plan.plan_id} - {e}")

            return ConsolidationResult(
                plan_id=plan.plan_id,
                success=False,
                target_guide_path="",
                merged_content_size=0,
                removed_guides=[],
                updated_references=0,
                validation_score=0.0,
                rollback_available=False,
                execution_time_seconds=time.time() - start_time,
                result_timestamp=datetime.now(),
            )

    def _execute_workflow_step(self, plan: ConsolidationPlan, step_config: Dict[str, Any]) -> WorkflowExecution:
        """Execute a single workflow step."""
        step_id = step_config["step_id"]
        step_type = WorkflowStep(step_config["step_type"])

        print(f"  🔄 Executing step: {step_config['description']}")

        execution = WorkflowExecution(
            step_id=step_id,
            plan_id=plan.plan_id,
            step_type=step_type,
            status=ConsolidationStatus.IN_PROGRESS,
            start_time=datetime.now(),
            result_data={},
        )

        try:
            if step_type == WorkflowStep.VALIDATE_OPPORTUNITY:
                execution.result_data = self._validate_opportunity(plan)
            elif step_type == WorkflowStep.CREATE_BACKUP:
                execution.result_data = self._create_backup(plan)
            elif step_type == WorkflowStep.MERGE_CONTENT:
                execution.result_data = self._merge_content(plan)
            elif step_type == WorkflowStep.UPDATE_REFERENCES:
                execution.result_data = self._update_references(plan)
            elif step_type == WorkflowStep.VALIDATE_RESULT:
                execution.result_data = self._validate_result(plan)
            elif step_type == WorkflowStep.COMMIT_CHANGES:
                execution.result_data = self._commit_changes(plan)
            else:
                raise ValueError(f"Unknown workflow step: {step_type}")

            execution.status = ConsolidationStatus.COMPLETED

        except Exception as e:
            execution.status = ConsolidationStatus.FAILED
            execution.error_message = str(e)
            print(f"    ❌ Step failed: {e}")

        execution.end_time = datetime.now()
        execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()

        # Store execution result
        self._store_workflow_execution(execution)

        return execution

    def _validate_opportunity(self, plan: ConsolidationPlan) -> Dict[str, Any]:
        """Validate the consolidation opportunity."""
        result = {
            "source_guides_exist": [],
            "target_guide_exists": False,
            "content_validation": {},
            "risk_assessment": {},
        }

        # Check if source guides exist
        for guide in plan.source_guides:
            guide_path = self.guides_dir / guide
            if guide_path.exists():
                result["source_guides_exist"].append(guide)
            else:
                raise ValueError(f"Source guide not found: {guide}")

        # Check if target guide exists
        target_path = self.guides_dir / plan.target_guide
        result["target_guide_exists"] = target_path.exists()

        # Validate content
        for guide in plan.source_guides:
            guide_path = self.guides_dir / guide
            content = guide_path.read_text(encoding="utf-8")

            result["content_validation"][guide] = {
                "size_bytes": len(content),
                "line_count": len(content.split("\n")),
                "has_content": len(content.strip()) > 0,
                "is_markdown": guide.endswith(".md"),
            }

        # Risk assessment
        result["risk_assessment"] = {
            "risk_level": plan.risk_level,
            "consolidation_type": plan.consolidation_type,
            "merge_strategy": plan.merge_strategy,
            "source_count": len(plan.source_guides),
        }

        return result

    def _create_backup(self, plan: ConsolidationPlan) -> Dict[str, Any]:
        """Create backup of source guides."""
        backup_id = f"backup_{plan.plan_id}_{int(time.time())}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(exist_ok=True)

        backed_up_files = []

        for guide in plan.source_guides:
            source_path = self.guides_dir / guide
            backup_file_path = backup_path / guide

            if source_path.exists():
                shutil.copy2(source_path, backup_file_path)
                backed_up_files.append(guide)

        # Also backup target guide if it exists
        target_path = self.guides_dir / plan.target_guide
        if target_path.exists():
            target_backup_path = backup_path / plan.target_guide
            shutil.copy2(target_path, target_backup_path)
            backed_up_files.append(plan.target_guide)

        return {
            "backup_id": backup_id,
            "backup_path": str(backup_path),
            "backed_up_files": backed_up_files,
            "backup_size_bytes": sum((backup_path / f).stat().st_size for f in backed_up_files),
        }

    def _merge_content(self, plan: ConsolidationPlan) -> Dict[str, Any]:
        """Merge content according to the specified strategy."""
        result = {
            "merged_content": "",
            "merge_strategy_used": plan.merge_strategy,
            "source_contents": {},
            "merge_operations": [],
        }

        # Load source contents
        for guide in plan.source_guides:
            guide_path = self.guides_dir / guide
            content = guide_path.read_text(encoding="utf-8")
            result["source_contents"][guide] = {
                "content": content,
                "size_bytes": len(content),
                "line_count": len(content.split("\n")),
            }

        # Apply merge strategy
        if plan.merge_strategy == "content_replacement":
            # Use the largest source guide as the base
            largest_guide = max(plan.source_guides, key=lambda g: len(result["source_contents"][g]["content"]))
            result["merged_content"] = result["source_contents"][largest_guide]["content"]
            result["merge_operations"].append(f"Used {largest_guide} as base content")

        elif plan.merge_strategy == "content_merging":
            # Merge content from all sources
            merged_content = self._merge_multiple_contents(
                [result["source_contents"][g]["content"] for g in plan.source_guides]
            )
            result["merged_content"] = merged_content
            result["merge_operations"].append("Merged content from all sources")

        elif plan.merge_strategy == "section_consolidation":
            # Consolidate by sections
            merged_content = self._consolidate_by_sections(
                [result["source_contents"][g]["content"] for g in plan.source_guides]
            )
            result["merged_content"] = merged_content
            result["merge_operations"].append("Consolidated content by sections")

        else:
            # Default to content replacement
            largest_guide = max(plan.source_guides, key=lambda g: len(result["source_contents"][g]["content"]))
            result["merged_content"] = result["source_contents"][largest_guide]["content"]
            result["merge_operations"].append(f"Used {largest_guide} as base content (default)")

        return result

    def _merge_multiple_contents(self, contents: List[str]) -> str:
        """Merge multiple content pieces intelligently."""
        if not contents:
            return ""

        if len(contents) == 1:
            return contents[0]

        # Extract headers from all contents
        all_headers = []
        for content in contents:
            headers = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
            all_headers.extend(headers)

        # Find unique headers
        unique_headers = list(set(all_headers))

        # Start with the first content as base
        merged = contents[0]

        # Add unique sections from other contents
        for content in contents[1:]:
            sections = self._extract_sections(content)
            for header, section_content in sections.items():
                if header not in merged:
                    merged += f"\n\n## {header}\n\n{section_content}"

        return merged

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from content based on headers."""
        sections = {}
        lines = content.split("\n")
        current_header = None
        current_content = []

        for line in lines:
            header_match = re.match(r"^#{1,6}\s+(.+)$", line)
            if header_match:
                if current_header:
                    sections[current_header] = "\n".join(current_content).strip()
                current_header = header_match.group(1)
                current_content = []
            elif current_header:
                current_content.append(line)

        if current_header:
            sections[current_header] = "\n".join(current_content).strip()

        return sections

    def _consolidate_by_sections(self, contents: List[str]) -> str:
        """Consolidate content by organizing sections."""
        # Extract all sections from all contents
        all_sections = {}

        for content in contents:
            sections = self._extract_sections(content)
            for header, section_content in sections.items():
                if header not in all_sections:
                    all_sections[header] = []
                all_sections[header].append(section_content)

        # Merge sections
        merged_content = ""
        for header, section_contents in all_sections.items():
            merged_content += f"\n\n## {header}\n\n"
            merged_content += "\n\n".join(section_contents)

        return merged_content.strip()

    def _update_references(self, plan: ConsolidationPlan) -> Dict[str, Any]:
        """Update cross-references to consolidated guides."""
        result = {"files_updated": [], "references_updated": 0, "reference_details": []}

        # Find all markdown files that might reference the source guides
        all_guide_files = list(self.guides_dir.glob("*.md"))

        for guide_file in all_guide_files:
            if guide_file.name in plan.source_guides or guide_file.name == plan.target_guide:
                continue  # Skip the guides being consolidated

            content = guide_file.read_text(encoding="utf-8")
            original_content = content
            references_updated = 0

            # Update references to source guides
            for source_guide in plan.source_guides:
                # Update markdown links
                old_pattern = f"400_guides/{source_guide}"
                new_pattern = f"400_guides/{plan.target_guide}"
                content = content.replace(old_pattern, new_pattern)

                # Update relative links
                old_pattern = f"./{source_guide}"
                new_pattern = f"./{plan.target_guide}"
                content = content.replace(old_pattern, new_pattern)

                # Count updates
                if content != original_content:
                    references_updated += 1

            if references_updated > 0:
                guide_file.write_text(content, encoding="utf-8")
                result["files_updated"].append(guide_file.name)
                result["references_updated"] += references_updated
                result["reference_details"].append({"file": guide_file.name, "references_updated": references_updated})

        return result

    def _validate_result(self, plan: ConsolidationPlan) -> Dict[str, Any]:
        """Validate the consolidation result."""
        result = {
            "target_guide_exists": False,
            "content_validation": {},
            "structure_validation": {},
            "reference_validation": {},
            "overall_score": 0.0,
        }

        # Check if target guide exists
        target_path = self.guides_dir / plan.target_guide
        result["target_guide_exists"] = target_path.exists()

        if result["target_guide_exists"]:
            content = target_path.read_text(encoding="utf-8")

            # Content validation
            result["content_validation"] = {
                "size_bytes": len(content),
                "line_count": len(content.split("\n")),
                "word_count": len(content.split()),
                "has_content": len(content.strip()) > 0,
                "has_headers": bool(re.search(r"^#{1,6}\s+", content, re.MULTILINE)),
            }

            # Structure validation
            headers = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
            result["structure_validation"] = {
                "header_count": len(headers),
                "has_tldr": "TL;DR" in content,
                "has_anchor_key": "ANCHOR_KEY:" in content,
                "has_role_pins": "ROLE_PINS:" in content,
                "structure_score": min(len(headers) / 3, 1.0),  # At least 3 headers
            }

            # Reference validation
            internal_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
            result["reference_validation"] = {
                "internal_links": len(internal_links),
                "valid_links": len([link for _, link in internal_links if not link.startswith("http")]),
            }

            # Calculate overall score
            content_score = 1.0 if result["content_validation"]["has_content"] else 0.0
            structure_score = result["structure_validation"]["structure_score"]
            reference_score = (
                min(result["reference_validation"]["valid_links"] / 5, 1.0)
                if result["reference_validation"]["valid_links"] > 0
                else 0.0
            )

            result["overall_score"] = content_score * 0.4 + structure_score * 0.4 + reference_score * 0.2

        return result

    def _commit_changes(self, plan: ConsolidationPlan) -> Dict[str, Any]:
        """Commit the consolidation changes."""
        result = {"changes_committed": False, "files_removed": [], "target_guide_updated": False}

        # Update target guide with merged content
        target_path = self.guides_dir / plan.target_guide

        # Get merged content from previous step
        merge_execution = self._get_last_execution(plan.plan_id, WorkflowStep.MERGE_CONTENT)
        if merge_execution and merge_execution.result_data:
            merged_content = merge_execution.result_data.get("merged_content", "")

            if merged_content:
                target_path.write_text(merged_content, encoding="utf-8")
                result["target_guide_updated"] = True

        # Remove source guides (except target)
        for guide in plan.source_guides:
            if guide != plan.target_guide:
                guide_path = self.guides_dir / guide
                if guide_path.exists():
                    guide_path.unlink()
                    result["files_removed"].append(guide)

        result["changes_committed"] = True

        return result

    def _rollback_consolidation(self, plan: ConsolidationPlan) -> bool:
        """Rollback a consolidation operation."""
        print(f"🔄 Rolling back consolidation plan: {plan.plan_id}")

        # Find the backup
        backup_execution = self._get_last_execution(plan.plan_id, WorkflowStep.CREATE_BACKUP)
        if not backup_execution or not backup_execution.result_data:
            print("❌ No backup found for rollback")
            return False

        backup_path = Path(backup_execution.result_data.get("backup_path", ""))
        if not backup_path.exists():
            print("❌ Backup directory not found")
            return False

        try:
            # Restore files from backup
            backed_up_files = backup_execution.result_data.get("backed_up_files", [])
            for file_name in backed_up_files:
                backup_file = backup_path / file_name
                target_file = self.guides_dir / file_name

                if backup_file.exists():
                    shutil.copy2(backup_file, target_file)
                    print(f"  ✅ Restored: {file_name}")

            plan.status = ConsolidationStatus.ROLLED_BACK
            self._update_plan_status(plan)

            print(f"✅ Rollback completed successfully: {plan.plan_id}")
            return True

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

    def _get_last_execution(self, plan_id: str, step_type: WorkflowStep) -> Optional[WorkflowExecution]:
        """Get the last execution for a specific step type."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM workflow_executions
                WHERE plan_id = ? AND step_type = ?
                ORDER BY start_time DESC LIMIT 1
            """,
                (plan_id, step_type.value),
            )

            row = cursor.fetchone()
            if row:
                return WorkflowExecution(
                    step_id=row[0],
                    plan_id=row[1],
                    step_type=WorkflowStep(row[2]),
                    status=ConsolidationStatus(row[3]),
                    start_time=datetime.fromisoformat(row[4]),
                    end_time=datetime.fromisoformat(row[5]) if row[5] else None,
                    duration_seconds=row[6],
                    result_data=json.loads(row[7]) if row[7] else {},
                    error_message=row[8],
                )

        return None

    def _store_consolidation_plan(self, plan: ConsolidationPlan):
        """Store consolidation plan in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO consolidation_plans
                (id, opportunity_id, source_guides, target_guide, consolidation_type,
                 merge_strategy, estimated_effort, risk_level, steps, status,
                 created_at, started_at, completed_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    plan.plan_id,
                    plan.opportunity_id,
                    json.dumps(plan.source_guides),
                    plan.target_guide,
                    plan.consolidation_type,
                    plan.merge_strategy,
                    plan.estimated_effort,
                    plan.risk_level,
                    json.dumps(plan.steps),
                    plan.status.value,
                    plan.created_at.isoformat(),
                    plan.started_at.isoformat() if plan.started_at else None,
                    plan.completed_at.isoformat() if plan.completed_at else None,
                    plan.error_message,
                ),
            )

    def _update_plan_status(self, plan: ConsolidationPlan):
        """Update plan status in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE consolidation_plans
                SET status = ?, started_at = ?, completed_at = ?, error_message = ?
                WHERE id = ?
            """,
                (
                    plan.status.value,
                    plan.started_at.isoformat() if plan.started_at else None,
                    plan.completed_at.isoformat() if plan.completed_at else None,
                    plan.error_message,
                    plan.plan_id,
                ),
            )

    def _store_workflow_execution(self, execution: WorkflowExecution):
        """Store workflow execution in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO workflow_executions
                (id, plan_id, step_type, status, start_time, end_time,
                 duration_seconds, result_data, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    execution.step_id,
                    execution.plan_id,
                    execution.step_type.value,
                    execution.status.value,
                    execution.start_time.isoformat(),
                    execution.end_time.isoformat() if execution.end_time else None,
                    execution.duration_seconds,
                    json.dumps(execution.result_data),
                    execution.error_message,
                ),
            )

    def _store_consolidation_result(self, result: ConsolidationResult):
        """Store consolidation result in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO consolidation_results
                (plan_id, success, target_guide_path, merged_content_size,
                 removed_guides, updated_references, validation_score,
                 rollback_available, execution_time_seconds, result_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.plan_id,
                    result.success,
                    result.target_guide_path,
                    result.merged_content_size,
                    json.dumps(result.removed_guides),
                    result.updated_references,
                    result.validation_score,
                    result.rollback_available,
                    result.execution_time_seconds,
                    result.result_timestamp.isoformat(),
                ),
            )

    def _generate_consolidation_result(self, plan: ConsolidationPlan, execution_time: float) -> ConsolidationResult:
        """Generate consolidation result from plan execution."""
        # Get validation result
        validation_execution = self._get_last_execution(plan.plan_id, WorkflowStep.VALIDATE_RESULT)
        validation_score = 0.0
        if validation_execution and validation_execution.result_data:
            validation_score = validation_execution.result_data.get("overall_score", 0.0)

        # Get commit result
        commit_execution = self._get_last_execution(plan.plan_id, WorkflowStep.COMMIT_CHANGES)
        removed_guides = []
        target_guide_path = ""
        merged_content_size = 0

        if commit_execution and commit_execution.result_data:
            removed_guides = commit_execution.result_data.get("files_removed", [])
            target_guide_path = str(self.guides_dir / plan.target_guide)

            # Get content size
            target_path = self.guides_dir / plan.target_guide
            if target_path.exists():
                merged_content_size = target_path.stat().st_size

        # Get reference update result
        reference_execution = self._get_last_execution(plan.plan_id, WorkflowStep.UPDATE_REFERENCES)
        updated_references = 0
        if reference_execution and reference_execution.result_data:
            updated_references = reference_execution.result_data.get("references_updated", 0)

        return ConsolidationResult(
            plan_id=plan.plan_id,
            success=plan.status == ConsolidationStatus.COMPLETED,
            target_guide_path=target_guide_path,
            merged_content_size=merged_content_size,
            removed_guides=removed_guides,
            updated_references=updated_references,
            validation_score=validation_score,
            rollback_available=True,  # Always available if backup was created
            execution_time_seconds=execution_time,
            result_timestamp=datetime.now(),
        )

    def get_consolidation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get consolidation history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT p.*, r.success, r.validation_score, r.execution_time_seconds
                FROM consolidation_plans p
                LEFT JOIN consolidation_results r ON p.id = r.plan_id
                ORDER BY p.created_at DESC
                LIMIT ?
            """,
                (limit,),
            )

            return [
                {
                    "plan_id": row[0],
                    "consolidation_type": row[4],
                    "source_guides": json.loads(row[2]),
                    "target_guide": row[3],
                    "status": row[9],
                    "created_at": row[10],
                    "success": row[14],
                    "validation_score": row[15],
                    "execution_time": row[16],
                }
                for row in cursor.fetchall()
            ]


def main():
    """Main entry point for the automated consolidation workflow."""
    parser = argparse.ArgumentParser(description="Automated consolidation workflow engine")
    parser.add_argument("--guides-dir", default="400_guides", help="Directory containing guides")
    parser.add_argument("--output-dir", default="artifacts/consolidation", help="Output directory for results")
    parser.add_argument("--opportunity-file", help="JSON file with consolidation opportunities")
    parser.add_argument("--execute-plan", help="Execute a specific consolidation plan")
    parser.add_argument("--show-history", action="store_true", help="Show consolidation history")
    parser.add_argument("--rollback-plan", help="Rollback a specific consolidation plan")

    args = parser.parse_args()

    # Initialize workflow engine
    workflow = AutomatedConsolidationWorkflow(args.guides_dir, args.output_dir)

    if args.opportunity_file:
        # Load opportunities and create plans
        with open(args.opportunity_file, "r") as f:
            opportunities = json.load(f)

        for opportunity in opportunities[:3]:  # Limit to 3 for safety
            plan = workflow.create_consolidation_plan(opportunity)
            print(f"📋 Created plan: {plan.plan_id}")

            # Execute plan
            result = workflow.execute_consolidation_plan(plan)
            print(f"🎯 Plan result: {'Success' if result.success else 'Failed'}")

    elif args.execute_plan:
        # Execute specific plan
        print(f"🚀 Executing plan: {args.execute_plan}")
        # This would require loading the plan from database
        print("Plan execution not implemented for specific plan ID")

    elif args.show_history:
        # Show consolidation history
        history = workflow.get_consolidation_history()
        print("📋 Consolidation History:")
        for entry in history:
            print(f"  {entry['plan_id']}: {entry['consolidation_type']} -> {entry['target_guide']} ({entry['status']})")

    elif args.rollback_plan:
        # Rollback specific plan
        print(f"🔄 Rolling back plan: {args.rollback_plan}")
        # This would require loading the plan from database
        print("Plan rollback not implemented for specific plan ID")

    else:
        print("🤖 Automated Consolidation Workflow Engine")
        print("Use --opportunity-file to execute consolidation opportunities")
        print("Use --show-history to view consolidation history")


if __name__ == "__main__":
    main()
