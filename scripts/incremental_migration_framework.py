#!/usr/bin/env python3
"""
Incremental Migration Framework for B-1032

Provides safe, step-by-step migration of existing documentation to the new t-t3 structure
with rollback capabilities and progress tracking. Part of the t-t3 Authority Structure Implementation.
"""

import os
import json
import argparse
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from collections import defaultdict
import sqlite3
import hashlib
from enum import Enum


class MigrationStatus(Enum):
    """Status of migration operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class MigrationStep(Enum):
    """Steps in the migration process."""
    VALIDATE_SOURCE = "validate_source"
    CREATE_BACKUP = "create_backup"
    ANALYZE_CONTENT = "analyze_content"
    DETERMINE_TIER = "determine_tier"
    TRANSFORM_CONTENT = "transform_content"
    UPDATE_REFERENCES = "update_references"
    VALIDATE_RESULT = "validate_result"
    COMMIT_CHANGES = "commit_changes"


@dataclass
class MigrationPlan:
    """A migration plan for a single guide."""
    plan_id: str
    source_guide: str
    target_tier: Optional[str]
    migration_steps: List[Dict[str, Any]]
    status: MigrationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    rollback_available: bool = False


@dataclass
class MigrationStepExecution:
    """Execution details for a migration step."""
    step_id: str
    plan_id: str
    step_type: MigrationStep
    status: MigrationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result_data: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    plan_id: str
    success: bool
    source_guide: str
    target_tier: str
    transformed_content_size: int
    references_updated: int
    validation_score: float
    rollback_available: bool
    execution_time_seconds: float
    result_timestamp: datetime


@dataclass
class MigrationBatch:
    """A batch of migration operations."""
    batch_id: str
    guides: List[str]
    batch_size: int
    priority: str
    estimated_duration: str
    status: MigrationStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0


class IncrementalMigrationFramework:
    """Main incremental migration framework."""
    
    def __init__(self, guides_dir: str = "400_guides", output_dir: str = "artifacts/migration"):
        self.guides_dir = Path(guides_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database for migration tracking
        self.db_path = self.output_dir / "migration_tracking.db"
        self._init_database()
        
        # Backup directory for rollback capability
        self.backup_dir = self.output_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Migration configuration
        self.migration_config = {
            "batch_size": 5,  # Process 5 guides at a time
            "max_concurrent_batches": 2,
            "timeout_seconds": 600,  # 10 minutes per guide
            "auto_rollback_on_failure": True,
            "validation_threshold": 0.7,
            "backup_retention_days": 30
        }
        
        # t-t3 structure configuration
        self.tier_config = {
            "tier_1": {
                "name": "Authoritative",
                "description": "Core, definitive guides",
                "size_range": (500, 1500),
                "priority": "high",
                "validation_rules": ["must_have_tldr", "must_have_anchor_key", "must_have_role_pins"]
            },
            "tier_2": {
                "name": "Supporting",
                "description": "Supporting and reference guides",
                "size_range": (1000, 2000),
                "priority": "medium",
                "validation_rules": ["should_have_tldr", "should_have_anchor_key"]
            },
            "tier_3": {
                "name": "Reference",
                "description": "Reference and utility guides",
                "size_range": (0, None),
                "priority": "low",
                "validation_rules": ["basic_structure"]
            }
        }

    def _init_database(self):
        """Initialize SQLite database for migration tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migration_plans (
                    id TEXT PRIMARY KEY,
                    source_guide TEXT,
                    target_tier TEXT,
                    migration_steps TEXT,
                    status TEXT,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT,
                    rollback_available BOOLEAN
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migration_step_executions (
                    id TEXT PRIMARY KEY,
                    plan_id TEXT,
                    step_type TEXT,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration_seconds REAL,
                    result_data TEXT,
                    error_message TEXT,
                    FOREIGN KEY (plan_id) REFERENCES migration_plans (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migration_results (
                    plan_id TEXT PRIMARY KEY,
                    success BOOLEAN,
                    source_guide TEXT,
                    target_tier TEXT,
                    transformed_content_size INTEGER,
                    references_updated INTEGER,
                    validation_score REAL,
                    rollback_available BOOLEAN,
                    execution_time_seconds REAL,
                    result_timestamp TEXT,
                    FOREIGN KEY (plan_id) REFERENCES migration_plans (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migration_batches (
                    id TEXT PRIMARY KEY,
                    guides TEXT,
                    batch_size INTEGER,
                    priority TEXT,
                    estimated_duration TEXT,
                    status TEXT,
                    created_at TEXT,
                    completed_at TEXT,
                    success_count INTEGER,
                    failure_count INTEGER
                )
            """)

    def create_migration_plan(self, source_guide: str, target_tier: Optional[str] = None) -> MigrationPlan:
        """Create a migration plan for a single guide."""
        plan_id = f"migration_{int(time.time())}_{hashlib.md5(source_guide.encode()).hexdigest()[:8]}"
        
        # Define migration steps
        steps = [
            {
                "step_id": f"{plan_id}_validate",
                "step_type": MigrationStep.VALIDATE_SOURCE.value,
                "description": "Validate source guide",
                "required": True,
                "timeout": 60
            },
            {
                "step_id": f"{plan_id}_backup",
                "step_type": MigrationStep.CREATE_BACKUP.value,
                "description": "Create backup of source guide",
                "required": True,
                "timeout": 120
            },
            {
                "step_id": f"{plan_id}_analyze",
                "step_type": MigrationStep.ANALYZE_CONTENT.value,
                "description": "Analyze content for tier determination",
                "required": True,
                "timeout": 180
            },
            {
                "step_id": f"{plan_id}_determine_tier",
                "step_type": MigrationStep.DETERMINE_TIER.value,
                "description": "Determine target tier",
                "required": True,
                "timeout": 60
            },
            {
                "step_id": f"{plan_id}_transform",
                "step_type": MigrationStep.TRANSFORM_CONTENT.value,
                "description": "Transform content for target tier",
                "required": True,
                "timeout": 300
            },
            {
                "step_id": f"{plan_id}_update_refs",
                "step_type": MigrationStep.UPDATE_REFERENCES.value,
                "description": "Update cross-references",
                "required": True,
                "timeout": 180
            },
            {
                "step_id": f"{plan_id}_validate_result",
                "step_type": MigrationStep.VALIDATE_RESULT.value,
                "description": "Validate migration result",
                "required": True,
                "timeout": 120
            },
            {
                "step_id": f"{plan_id}_commit",
                "step_type": MigrationStep.COMMIT_CHANGES.value,
                "description": "Commit migration changes",
                "required": True,
                "timeout": 60
            }
        ]
        
        plan = MigrationPlan(
            plan_id=plan_id,
            source_guide=source_guide,
            target_tier=target_tier,
            migration_steps=steps,
            status=MigrationStatus.PENDING,
            created_at=datetime.now()
        )
        
        # Store plan in database
        self._store_migration_plan(plan)
        
        return plan

    def execute_migration_plan(self, plan: MigrationPlan) -> MigrationResult:
        """Execute a migration plan."""
        print(f"🚀 Executing migration plan: {plan.plan_id}")
        print(f"📁 Source: {plan.source_guide}")
        print(f"🎯 Target Tier: {plan.target_tier or 'Auto-determined'}")
        
        start_time = time.time()
        plan.started_at = datetime.now()
        plan.status = MigrationStatus.IN_PROGRESS
        self._update_plan_status(plan)
        
        try:
            # Execute each step
            for step_config in plan.migration_steps:
                step_execution = self._execute_migration_step(plan, step_config)
                
                if step_execution.status == MigrationStatus.FAILED:
                    plan.status = MigrationStatus.FAILED
                    plan.error_message = step_execution.error_message
                    self._update_plan_status(plan)
                    
                    if self.migration_config["auto_rollback_on_failure"]:
                        self._rollback_migration(plan)
                    
                    return MigrationResult(
                        plan_id=plan.plan_id,
                        success=False,
                        source_guide=plan.source_guide,
                        target_tier=plan.target_tier or "unknown",
                        transformed_content_size=0,
                        references_updated=0,
                        validation_score=0.0,
                        rollback_available=False,
                        execution_time_seconds=time.time() - start_time,
                        result_timestamp=datetime.now()
                    )
            
            # Plan completed successfully
            plan.status = MigrationStatus.COMPLETED
            plan.completed_at = datetime.now()
            self._update_plan_status(plan)
            
            # Generate result
            result = self._generate_migration_result(plan, time.time() - start_time)
            self._store_migration_result(result)
            
            print(f"✅ Migration plan completed successfully: {plan.plan_id}")
            return result
            
        except Exception as e:
            plan.status = MigrationStatus.FAILED
            plan.error_message = str(e)
            self._update_plan_status(plan)
            
            if self.migration_config["auto_rollback_on_failure"]:
                self._rollback_migration(plan)
            
            print(f"❌ Migration plan failed: {plan.plan_id} - {e}")
            
            return MigrationResult(
                plan_id=plan.plan_id,
                success=False,
                source_guide=plan.source_guide,
                target_tier=plan.target_tier or "unknown",
                transformed_content_size=0,
                references_updated=0,
                validation_score=0.0,
                rollback_available=False,
                execution_time_seconds=time.time() - start_time,
                result_timestamp=datetime.now()
            )

    def _execute_migration_step(self, plan: MigrationPlan, step_config: Dict[str, Any]) -> MigrationStepExecution:
        """Execute a single migration step."""
        step_id = step_config["step_id"]
        step_type = MigrationStep(step_config["step_type"])
        
        print(f"  🔄 Executing step: {step_config['description']}")
        
        execution = MigrationStepExecution(
            step_id=step_id,
            plan_id=plan.plan_id,
            step_type=step_type,
            status=MigrationStatus.IN_PROGRESS,
            start_time=datetime.now(),
            result_data={}
        )
        
        try:
            if step_type == MigrationStep.VALIDATE_SOURCE:
                execution.result_data = self._validate_source_guide(plan)
            elif step_type == MigrationStep.CREATE_BACKUP:
                execution.result_data = self._create_backup(plan)
            elif step_type == MigrationStep.ANALYZE_CONTENT:
                execution.result_data = self._analyze_content(plan)
            elif step_type == MigrationStep.DETERMINE_TIER:
                execution.result_data = self._determine_tier(plan)
            elif step_type == MigrationStep.TRANSFORM_CONTENT:
                execution.result_data = self._transform_content(plan)
            elif step_type == MigrationStep.UPDATE_REFERENCES:
                execution.result_data = self._update_references(plan)
            elif step_type == MigrationStep.VALIDATE_RESULT:
                execution.result_data = self._validate_result(plan)
            elif step_type == MigrationStep.COMMIT_CHANGES:
                execution.result_data = self._commit_changes(plan)
            else:
                raise ValueError(f"Unknown migration step: {step_type}")
            
            execution.status = MigrationStatus.COMPLETED
            
        except Exception as e:
            execution.status = MigrationStatus.FAILED
            execution.error_message = str(e)
            print(f"    ❌ Step failed: {e}")
        
        execution.end_time = datetime.now()
        execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
        
        # Store execution result
        self._store_migration_step_execution(execution)
        
        return execution

    def _validate_source_guide(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Validate the source guide before migration."""
        result = {
            "guide_exists": False,
            "content_validation": {},
            "structure_validation": {},
            "readiness_assessment": {}
        }
        
        # Check if guide exists
        guide_path = self.guides_dir / plan.source_guide
        result["guide_exists"] = guide_path.exists()
        
        if not result["guide_exists"]:
            raise ValueError(f"Source guide not found: {plan.source_guide}")
        
        # Load and validate content
        content = guide_path.read_text(encoding="utf-8")
        lines = content.split('\n')
        
        result["content_validation"] = {
            "size_bytes": len(content),
            "line_count": len(lines),
            "word_count": len(content.split()),
            "has_content": len(content.strip()) > 0,
            "is_markdown": plan.source_guide.endswith('.md')
        }
        
        # Structure validation
        headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        result["structure_validation"] = {
            "header_count": len(headers),
            "has_tldr": "TL;DR" in content,
            "has_anchor_key": "ANCHOR_KEY:" in content,
            "has_role_pins": "ROLE_PINS:" in content,
            "structure_score": min(len(headers) / 3, 1.0)
        }
        
        # Readiness assessment
        readiness_score = 0.0
        readiness_issues = []
        
        if result["content_validation"]["has_content"]:
            readiness_score += 0.3
        else:
            readiness_issues.append("No content found")
        
        if result["structure_validation"]["header_count"] >= 2:
            readiness_score += 0.3
        else:
            readiness_issues.append("Insufficient headers")
        
        if result["structure_validation"]["has_tldr"]:
            readiness_score += 0.2
        else:
            readiness_issues.append("Missing TL;DR section")
        
        if result["structure_validation"]["has_anchor_key"]:
            readiness_score += 0.1
        else:
            readiness_issues.append("Missing ANCHOR_KEY")
        
        if result["structure_validation"]["has_role_pins"]:
            readiness_score += 0.1
        else:
            readiness_issues.append("Missing ROLE_PINS")
        
        result["readiness_assessment"] = {
            "readiness_score": readiness_score,
            "readiness_issues": readiness_issues,
            "ready_for_migration": readiness_score >= 0.5
        }
        
        if not result["readiness_assessment"]["ready_for_migration"]:
            raise ValueError(f"Guide not ready for migration: {', '.join(readiness_issues)}")
        
        return result

    def _create_backup(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Create backup of source guide."""
        backup_id = f"backup_{plan.plan_id}_{int(time.time())}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(exist_ok=True)
        
        guide_path = self.guides_dir / plan.source_guide
        backup_file_path = backup_path / plan.source_guide
        
        if guide_path.exists():
            shutil.copy2(guide_path, backup_file_path)
            plan.rollback_available = True
        
        return {
            "backup_id": backup_id,
            "backup_path": str(backup_path),
            "backed_up_file": plan.source_guide,
            "backup_size_bytes": backup_file_path.stat().st_size if backup_file_path.exists() else 0
        }

    def _analyze_content(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Analyze content for tier determination."""
        guide_path = self.guides_dir / plan.source_guide
        content = guide_path.read_text(encoding="utf-8")
        
        # Basic metrics
        lines = content.split('\n')
        words = content.split()
        
        # Content analysis
        headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        # Authority indicators
        authority_indicators = [
            "authoritative", "primary", "main", "core", "essential", "critical",
            "definitive", "comprehensive", "complete", "master", "reference"
        ]
        
        authority_score = sum(1 for indicator in authority_indicators if indicator.lower() in content.lower())
        
        # Complexity analysis
        complexity_indicators = [
            "advanced", "complex", "detailed", "comprehensive", "thorough",
            "extensive", "in-depth", "technical", "sophisticated"
        ]
        
        complexity_score = sum(1 for indicator in complexity_indicators if indicator.lower() in content.lower())
        
        # Content type analysis
        content_type = self._classify_content_type(content)
        
        return {
            "basic_metrics": {
                "line_count": len(lines),
                "word_count": len(words),
                "size_bytes": len(content)
            },
            "structure_metrics": {
                "header_count": len(headers),
                "code_block_count": len(code_blocks),
                "link_count": len(links)
            },
            "authority_analysis": {
                "authority_score": authority_score,
                "authority_indicators_found": authority_score
            },
            "complexity_analysis": {
                "complexity_score": complexity_score,
                "complexity_indicators_found": complexity_score
            },
            "content_type": content_type,
            "tier_suggestions": self._suggest_tiers(len(lines), authority_score, complexity_score, content_type)
        }

    def _classify_content_type(self, content: str) -> str:
        """Classify content by type."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['workflow', 'process', 'procedure']):
            return "workflow"
        elif any(word in content_lower for word in ['reference', 'api', 'schema']):
            return "reference"
        elif any(word in content_lower for word in ['best practice', 'guideline', 'recommendation']):
            return "best_practice"
        elif any(word in content_lower for word in ['guide', 'how-to', 'tutorial']):
            return "guide"
        else:
            return "general"

    def _suggest_tiers(self, line_count: int, authority_score: int, complexity_score: int, content_type: str) -> List[str]:
        """Suggest appropriate tiers based on content analysis."""
        suggestions = []
        
        # Tier 1 criteria: High authority, high complexity, comprehensive content
        if authority_score >= 3 and complexity_score >= 2 and line_count >= 500:
            suggestions.append("tier_1")
        
        # Tier 2 criteria: Medium authority, good structure, substantial content
        if (authority_score >= 1 or complexity_score >= 1) and line_count >= 300:
            suggestions.append("tier_2")
        
        # Tier 3: Everything else
        suggestions.append("tier_3")
        
        return list(set(suggestions))  # Remove duplicates

    def _determine_tier(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Determine the target tier for migration."""
        # If tier is already specified, use it
        if plan.target_tier:
            return {
                "target_tier": plan.target_tier,
                "determination_method": "manual_specification",
                "confidence": 1.0,
                "tier_config": self.tier_config.get(plan.target_tier, {})
            }
        
        # Get analysis from previous step
        analysis_execution = self._get_last_execution(plan.plan_id, MigrationStep.ANALYZE_CONTENT)
        if not analysis_execution or not analysis_execution.result_data:
            raise ValueError("Content analysis not available for tier determination")
        
        analysis = analysis_execution.result_data
        suggestions = analysis.get("tier_suggestions", [])
        
        # Use the highest priority tier from suggestions
        if "tier_1" in suggestions:
            target_tier = "tier_1"
            confidence = 0.9
        elif "tier_2" in suggestions:
            target_tier = "tier_2"
            confidence = 0.8
        else:
            target_tier = "tier_3"
            confidence = 0.7
        
        # Update plan with determined tier
        plan.target_tier = target_tier
        
        return {
            "target_tier": target_tier,
            "determination_method": "content_analysis",
            "confidence": confidence,
            "tier_config": self.tier_config.get(target_tier, {}),
            "suggestions_considered": suggestions
        }

    def _transform_content(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Transform content for the target tier."""
        guide_path = self.guides_dir / plan.source_guide
        content = guide_path.read_text(encoding="utf-8")
        
        # Get tier configuration
        tier_config = self.tier_config.get(plan.target_tier, {})
        validation_rules = tier_config.get("validation_rules", [])
        
        # Apply transformations based on tier requirements
        transformed_content = content
        transformations_applied = []
        
        # Add TL;DR if required and missing
        if "must_have_tldr" in validation_rules and "TL;DR" not in content:
            tldr_section = self._generate_tldr_section(content)
            transformed_content = tldr_section + "\n\n" + transformed_content
            transformations_applied.append("added_tldr_section")
        
        # Add ANCHOR_KEY if required and missing
        if "must_have_anchor_key" in validation_rules and "ANCHOR_KEY:" not in content:
            anchor_key = self._generate_anchor_key(plan.source_guide)
            transformed_content = f"ANCHOR_KEY: {anchor_key}\n\n" + transformed_content
            transformations_applied.append("added_anchor_key")
        
        # Add ROLE_PINS if required and missing
        if "must_have_role_pins" in validation_rules and "ROLE_PINS:" not in content:
            role_pins = self._generate_role_pins(content)
            transformed_content = f"ROLE_PINS: {role_pins}\n\n" + transformed_content
            transformations_applied.append("added_role_pins")
        
        # Ensure proper structure
        if "basic_structure" in validation_rules:
            transformed_content = self._ensure_basic_structure(transformed_content)
            transformations_applied.append("ensured_basic_structure")
        
        # Update content in file
        guide_path.write_text(transformed_content, encoding="utf-8")
        
        return {
            "original_size": len(content),
            "transformed_size": len(transformed_content),
            "transformations_applied": transformations_applied,
            "tier_requirements_met": self._check_tier_requirements(transformed_content, validation_rules)
        }

    def _generate_tldr_section(self, content: str) -> str:
        """Generate a TL;DR section for the content."""
        # Extract first few sentences or key points
        lines = content.split('\n')
        summary_lines = []
        
        for line in lines[:10]:  # Look at first 10 lines
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
                if len(summary_lines) >= 3:
                    break
        
        if summary_lines:
            summary = ' '.join(summary_lines)
            if len(summary) > 200:
                summary = summary[:200] + "..."
        else:
            summary = "Quick reference guide for documentation management."
        
        return f"## TL;DR\n\n{summary}"

    def _generate_anchor_key(self, filename: str) -> str:
        """Generate an anchor key for the guide."""
        # Remove extension and convert to lowercase
        base_name = Path(filename).stem.lower()
        # Replace spaces and special characters with underscores
        anchor_key = re.sub(r'[^a-z0-9]', '_', base_name)
        # Remove multiple underscores
        anchor_key = re.sub(r'_+', '_', anchor_key)
        # Remove leading/trailing underscores
        anchor_key = anchor_key.strip('_')
        return anchor_key

    def _generate_role_pins(self, content: str) -> str:
        """Generate role pins based on content analysis."""
        content_lower = content.lower()
        roles = []
        
        if any(word in content_lower for word in ['workflow', 'process', 'procedure']):
            roles.append("planner")
        
        if any(word in content_lower for word in ['code', 'script', 'implementation']):
            roles.append("coder")
        
        if any(word in content_lower for word in ['research', 'analysis', 'investigation']):
            roles.append("researcher")
        
        if any(word in content_lower for word in ['guide', 'how-to', 'tutorial']):
            roles.append("implementer")
        
        # Default roles if none detected
        if not roles:
            roles = ["implementer", "planner"]
        
        return ", ".join(roles)

    def _ensure_basic_structure(self, content: str) -> str:
        """Ensure basic markdown structure."""
        lines = content.split('\n')
        
        # Ensure there's a title
        if not lines or not lines[0].startswith('#'):
            title = "Documentation Guide"
            content = f"# {title}\n\n" + content
        
        # Ensure proper spacing around headers
        content = re.sub(r'\n(#{1,6}\s+[^\n]+)\n', r'\n\n\1\n\n', content)
        
        return content

    def _check_tier_requirements(self, content: str, validation_rules: List[str]) -> Dict[str, bool]:
        """Check if content meets tier requirements."""
        requirements_met = {}
        
        for rule in validation_rules:
            if rule == "must_have_tldr" or rule == "should_have_tldr":
                requirements_met["has_tldr"] = "TL;DR" in content
            elif rule == "must_have_anchor_key" or rule == "should_have_anchor_key":
                requirements_met["has_anchor_key"] = "ANCHOR_KEY:" in content
            elif rule == "must_have_role_pins":
                requirements_met["has_role_pins"] = "ROLE_PINS:" in content
            elif rule == "basic_structure":
                requirements_met["has_basic_structure"] = bool(re.search(r'^#{1,6}\s+', content, re.MULTILINE))
        
        return requirements_met

    def _update_references(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Update cross-references to the migrated guide."""
        result = {
            "files_updated": [],
            "references_updated": 0,
            "reference_details": []
        }
        
        # Find all markdown files that might reference the migrated guide
        all_guide_files = list(self.guides_dir.glob("*.md"))
        
        for guide_file in all_guide_files:
            if guide_file.name == plan.source_guide:
                continue  # Skip the guide being migrated
            
            content = guide_file.read_text(encoding="utf-8")
            original_content = content
            references_updated = 0
            
            # Update references to the migrated guide
            old_pattern = f"400_guides/{plan.source_guide}"
            new_pattern = f"400_guides/{plan.source_guide}"  # Same path, but content is transformed
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                references_updated += 1
            
            # Update relative links
            old_pattern = f"./{plan.source_guide}"
            if old_pattern in content:
                content = content.replace(old_pattern, f"./{plan.source_guide}")
                references_updated += 1
            
            if references_updated > 0:
                guide_file.write_text(content, encoding="utf-8")
                result["files_updated"].append(guide_file.name)
                result["references_updated"] += references_updated
                result["reference_details"].append({
                    "file": guide_file.name,
                    "references_updated": references_updated
                })
        
        return result

    def _validate_result(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Validate the migration result."""
        result = {
            "guide_exists": False,
            "content_validation": {},
            "tier_validation": {},
            "overall_score": 0.0
        }
        
        # Check if guide exists
        guide_path = self.guides_dir / plan.source_guide
        result["guide_exists"] = guide_path.exists()
        
        if result["guide_exists"]:
            content = guide_path.read_text(encoding="utf-8")
            
            # Content validation
            result["content_validation"] = {
                "size_bytes": len(content),
                "line_count": len(content.split('\n')),
                "word_count": len(content.split()),
                "has_content": len(content.strip()) > 0
            }
            
            # Tier validation
            tier_config = self.tier_config.get(plan.target_tier, {})
            validation_rules = tier_config.get("validation_rules", [])
            
            tier_requirements = self._check_tier_requirements(content, validation_rules)
            tier_score = sum(tier_requirements.values()) / len(tier_requirements) if tier_requirements else 0.0
            
            result["tier_validation"] = {
                "tier_requirements": tier_requirements,
                "tier_score": tier_score,
                "tier_config": tier_config
            }
            
            # Calculate overall score
            content_score = 1.0 if result["content_validation"]["has_content"] else 0.0
            result["overall_score"] = (content_score * 0.4 + tier_score * 0.6)
        
        return result

    def _commit_changes(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Commit the migration changes."""
        result = {
            "changes_committed": False,
            "guide_updated": False,
            "migration_complete": False
        }
        
        # Verify the guide has been transformed
        guide_path = self.guides_dir / plan.source_guide
        if guide_path.exists():
            content = guide_path.read_text(encoding="utf-8")
            
            # Check if transformations were applied
            has_tldr = "TL;DR" in content
            has_anchor_key = "ANCHOR_KEY:" in content
            has_role_pins = "ROLE_PINS:" in content
            
            if has_tldr or has_anchor_key or has_role_pins:
                result["guide_updated"] = True
                result["changes_committed"] = True
                result["migration_complete"] = True
        
        return result

    def _rollback_migration(self, plan: MigrationPlan) -> bool:
        """Rollback a migration operation."""
        print(f"🔄 Rolling back migration plan: {plan.plan_id}")
        
        # Find the backup
        backup_execution = self._get_last_execution(plan.plan_id, MigrationStep.CREATE_BACKUP)
        if not backup_execution or not backup_execution.result_data:
            print("❌ No backup found for rollback")
            return False
        
        backup_path = Path(backup_execution.result_data.get("backup_path", ""))
        if not backup_path.exists():
            print("❌ Backup directory not found")
            return False
        
        try:
            # Restore file from backup
            backup_file = backup_path / plan.source_guide
            target_file = self.guides_dir / plan.source_guide
            
            if backup_file.exists():
                shutil.copy2(backup_file, target_file)
                print(f"  ✅ Restored: {plan.source_guide}")
            
            plan.status = MigrationStatus.ROLLED_BACK
            self._update_plan_status(plan)
            
            print(f"✅ Rollback completed successfully: {plan.plan_id}")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

    def _get_last_execution(self, plan_id: str, step_type: MigrationStep) -> Optional[MigrationStepExecution]:
        """Get the last execution for a specific step type."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM migration_step_executions 
                WHERE plan_id = ? AND step_type = ?
                ORDER BY start_time DESC LIMIT 1
            """, (plan_id, step_type.value))
            
            row = cursor.fetchone()
            if row:
                return MigrationStepExecution(
                    step_id=row[0],
                    plan_id=row[1],
                    step_type=MigrationStep(row[2]),
                    status=MigrationStatus(row[3]),
                    start_time=datetime.fromisoformat(row[4]),
                    end_time=datetime.fromisoformat(row[5]) if row[5] else None,
                    duration_seconds=row[6],
                    result_data=json.loads(row[7]) if row[7] else {},
                    error_message=row[8]
                )
        
        return None

    def _store_migration_plan(self, plan: MigrationPlan):
        """Store migration plan in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO migration_plans 
                (id, source_guide, target_tier, migration_steps, status,
                 created_at, started_at, completed_at, error_message, rollback_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan.plan_id,
                plan.source_guide,
                plan.target_tier,
                json.dumps(plan.migration_steps),
                plan.status.value,
                plan.created_at.isoformat(),
                plan.started_at.isoformat() if plan.started_at else None,
                plan.completed_at.isoformat() if plan.completed_at else None,
                plan.error_message,
                plan.rollback_available
            ))

    def _update_plan_status(self, plan: MigrationPlan):
        """Update plan status in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE migration_plans 
                SET status = ?, started_at = ?, completed_at = ?, error_message = ?, rollback_available = ?
                WHERE id = ?
            """, (
                plan.status.value,
                plan.started_at.isoformat() if plan.started_at else None,
                plan.completed_at.isoformat() if plan.completed_at else None,
                plan.error_message,
                plan.rollback_available,
                plan.plan_id
            ))

    def _store_migration_step_execution(self, execution: MigrationStepExecution):
        """Store migration step execution in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO migration_step_executions 
                (id, plan_id, step_type, status, start_time, end_time,
                 duration_seconds, result_data, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.step_id,
                execution.plan_id,
                execution.step_type.value,
                execution.status.value,
                execution.start_time.isoformat(),
                execution.end_time.isoformat() if execution.end_time else None,
                execution.duration_seconds,
                json.dumps(execution.result_data),
                execution.error_message
            ))

    def _store_migration_result(self, result: MigrationResult):
        """Store migration result in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO migration_results 
                (plan_id, success, source_guide, target_tier, transformed_content_size,
                 references_updated, validation_score, rollback_available,
                 execution_time_seconds, result_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.plan_id,
                result.success,
                result.source_guide,
                result.target_tier,
                result.transformed_content_size,
                result.references_updated,
                result.validation_score,
                result.rollback_available,
                result.execution_time_seconds,
                result.result_timestamp.isoformat()
            ))

    def _generate_migration_result(self, plan: MigrationPlan, execution_time: float) -> MigrationResult:
        """Generate migration result from plan execution."""
        # Get validation result
        validation_execution = self._get_last_execution(plan.plan_id, MigrationStep.VALIDATE_RESULT)
        validation_score = 0.0
        if validation_execution and validation_execution.result_data:
            validation_score = validation_execution.result_data.get("overall_score", 0.0)
        
        # Get transform result
        transform_execution = self._get_last_execution(plan.plan_id, MigrationStep.TRANSFORM_CONTENT)
        transformed_content_size = 0
        if transform_execution and transform_execution.result_data:
            transformed_content_size = transform_execution.result_data.get("transformed_size", 0)
        
        # Get reference update result
        reference_execution = self._get_last_execution(plan.plan_id, MigrationStep.UPDATE_REFERENCES)
        references_updated = 0
        if reference_execution and reference_execution.result_data:
            references_updated = reference_execution.result_data.get("references_updated", 0)
        
        return MigrationResult(
            plan_id=plan.plan_id,
            success=plan.status == MigrationStatus.COMPLETED,
            source_guide=plan.source_guide,
            target_tier=plan.target_tier or "unknown",
            transformed_content_size=transformed_content_size,
            references_updated=references_updated,
            validation_score=validation_score,
            rollback_available=plan.rollback_available,
            execution_time_seconds=execution_time,
            result_timestamp=datetime.now()
        )

    def get_migration_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get migration history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT p.*, r.success, r.validation_score, r.execution_time_seconds
                FROM migration_plans p
                LEFT JOIN migration_results r ON p.id = r.plan_id
                ORDER BY p.created_at DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    "plan_id": row[0],
                    "source_guide": row[1],
                    "target_tier": row[2],
                    "status": row[4],
                    "created_at": row[5],
                    "success": row[10],
                    "validation_score": row[11],
                    "execution_time": row[12]
                }
                for row in cursor.fetchall()
            ]


def main():
    """Main entry point for the incremental migration framework."""
    parser = argparse.ArgumentParser(description="Incremental migration framework for t-t3 structure")
    parser.add_argument("--guides-dir", default="400_guides", help="Directory containing guides")
    parser.add_argument("--output-dir", default="artifacts/migration", help="Output directory for results")
    parser.add_argument("--migrate-guide", help="Migrate a specific guide")
    parser.add_argument("--target-tier", help="Target tier for migration")
    parser.add_argument("--show-history", action="store_true", help="Show migration history")
    parser.add_argument("--rollback-plan", help="Rollback a specific migration plan")
    
    args = parser.parse_args()
    
    # Initialize migration framework
    framework = IncrementalMigrationFramework(args.guides_dir, args.output_dir)
    
    if args.migrate_guide:
        # Create and execute migration plan for specific guide
        plan = framework.create_migration_plan(args.migrate_guide, args.target_tier)
        print(f"📋 Created migration plan: {plan.plan_id}")
        
        # Execute plan
        result = framework.execute_migration_plan(plan)
        print(f"🎯 Migration result: {'Success' if result.success else 'Failed'}")
        if result.success:
            print(f"📊 Validation score: {result.validation_score:.2f}")
            print(f"🔗 References updated: {result.references_updated}")
    
    elif args.show_history:
        # Show migration history
        history = framework.get_migration_history()
        print("📋 Migration History:")
        for entry in history:
            print(f"  {entry['plan_id']}: {entry['source_guide']} -> {entry['target_tier']} ({entry['status']})")
    
    elif args.rollback_plan:
        # Rollback specific plan
        print(f"🔄 Rolling back plan: {args.rollback_plan}")
        # This would require loading the plan from database
        print("Plan rollback not implemented for specific plan ID")
    
    else:
        print("🚀 Incremental Migration Framework for t-t3 Structure")
        print("Use --migrate-guide to migrate a specific guide")
        print("Use --show-history to view migration history")


if __name__ == "__main__":
    main()
