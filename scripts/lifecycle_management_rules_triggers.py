#!/usr/bin/env python3
"""
Lifecycle Management Rules and Triggers System for Documentation t-t3 Authority Structure

This module implements automated lifecycle management with rules, triggers, and
workflow automation for documentation governance and maintenance.

Author: AI Assistant
Date: 2025-01-27
"""

import json
import logging
import re
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
import hashlib
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LifecycleStage(Enum):
    """Lifecycle stages for documentation"""
    DRAFT = "draft"
    ACTIVE = "active"
    REVIEW = "review"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DELETED = "deleted"


class TriggerType(Enum):
    """Types of lifecycle triggers"""
    TIME_BASED = "time_based"
    CONTENT_BASED = "content_based"
    AUTHORITY_BASED = "authority_based"
    DEPENDENCY_BASED = "dependency_based"
    MANUAL = "manual"
    SYSTEM = "system"


class ActionType(Enum):
    """Types of lifecycle actions"""
    REVIEW = "review"
    UPDATE = "update"
    DEPRECATE = "deprecate"
    ARCHIVE = "archive"
    DELETE = "delete"
    NOTIFY = "notify"
    ESCALATE = "escalate"
    VALIDATE = "validate"


@dataclass
class LifecycleRule:
    """Lifecycle management rule"""
    rule_id: str
    name: str
    description: str
    authority_level: str
    trigger_type: TriggerType
    trigger_conditions: Dict[str, Any]
    action_type: ActionType
    action_parameters: Dict[str, Any]
    priority: int
    enabled: bool
    created_at: datetime


@dataclass
class LifecycleTrigger:
    """Lifecycle trigger event"""
    trigger_id: str
    rule_id: str
    document_path: str
    trigger_type: TriggerType
    trigger_data: Dict[str, Any]
    timestamp: datetime
    status: str


@dataclass
class LifecycleAction:
    """Lifecycle action execution"""
    action_id: str
    trigger_id: str
    rule_id: str
    document_path: str
    action_type: ActionType
    action_parameters: Dict[str, Any]
    execution_status: str
    execution_result: Dict[str, Any]
    timestamp: datetime


@dataclass
class LifecycleWorkflow:
    """Complete lifecycle workflow"""
    workflow_id: str
    document_path: str
    current_stage: LifecycleStage
    stage_history: List[Dict[str, Any]]
    active_triggers: List[LifecycleTrigger]
    pending_actions: List[LifecycleAction]
    workflow_rules: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class LifecycleAnalysis:
    """Complete lifecycle analysis result"""
    workflows: List[LifecycleWorkflow]
    triggers: List[LifecycleTrigger]
    actions: List[LifecycleAction]
    stage_distribution: Dict[LifecycleStage, int]
    trigger_distribution: Dict[TriggerType, int]
    action_distribution: Dict[ActionType, int]
    recommendations: List[str]
    timestamp: datetime


class LifecycleManagementRulesTriggers:
    """
    Lifecycle Management Rules and Triggers system
    """

    def __init__(self, db_path: str = "lifecycle_management.db"):
        """Initialize the lifecycle management system"""
        self.db_path = db_path
        self.lifecycle_rules = self._load_lifecycle_rules()
        self.trigger_conditions = self._load_trigger_conditions()
        self.action_handlers = self._load_action_handlers()
        self.init_database()

    def _load_lifecycle_rules(self) -> List[LifecycleRule]:
        """Load default lifecycle rules"""
        return [
            LifecycleRule(
                rule_id="review_monthly_critical",
                name="Monthly Review for Critical Documents",
                description="Trigger monthly review for critical authority documents",
                authority_level="critical",
                trigger_type=TriggerType.TIME_BASED,
                trigger_conditions={"interval_days": 30, "last_review_days": 30},
                action_type=ActionType.REVIEW,
                action_parameters={"review_type": "monthly", "notify_roles": ["owner", "reviewer"]},
                priority=1,
                enabled=True,
                created_at=datetime.now()
            ),
            LifecycleRule(
                rule_id="review_quarterly_high",
                name="Quarterly Review for High Authority Documents",
                description="Trigger quarterly review for high authority documents",
                authority_level="high",
                trigger_type=TriggerType.TIME_BASED,
                trigger_conditions={"interval_days": 90, "last_review_days": 90},
                action_type=ActionType.REVIEW,
                action_parameters={"review_type": "quarterly", "notify_roles": ["owner", "reviewer"]},
                priority=2,
                enabled=True,
                created_at=datetime.now()
            ),
            LifecycleRule(
                rule_id="review_annually_medium",
                name="Annual Review for Medium Authority Documents",
                description="Trigger annual review for medium authority documents",
                authority_level="medium",
                trigger_type=TriggerType.TIME_BASED,
                trigger_conditions={"interval_days": 365, "last_review_days": 365},
                action_type=ActionType.REVIEW,
                action_parameters={"review_type": "annual", "notify_roles": ["owner"]},
                priority=3,
                enabled=True,
                created_at=datetime.now()
            ),
            LifecycleRule(
                rule_id="deprecate_old_documents",
                name="Deprecate Old Documents",
                description="Deprecate documents older than 2 years without updates",
                authority_level="all",
                trigger_type=TriggerType.TIME_BASED,
                trigger_conditions={"last_modified_days": 730, "authority_level": ["low", "none"]},
                action_type=ActionType.DEPRECATE,
                action_parameters={"deprecation_notice_days": 30, "notify_roles": ["owner"]},
                priority=4,
                enabled=True,
                created_at=datetime.now()
            ),
            LifecycleRule(
                rule_id="validate_cross_references",
                name="Validate Cross-References",
                description="Validate cross-references when target documents change",
                authority_level="all",
                trigger_type=TriggerType.DEPENDENCY_BASED,
                trigger_conditions={"check_cross_references": True, "validate_targets": True},
                action_type=ActionType.VALIDATE,
                action_parameters={"validation_type": "cross_references", "notify_roles": ["editor"]},
                priority=5,
                enabled=True,
                created_at=datetime.now()
            ),
            LifecycleRule(
                rule_id="escalate_stale_critical",
                name="Escalate Stale Critical Documents",
                description="Escalate critical documents that haven't been reviewed in 6 months",
                authority_level="critical",
                trigger_type=TriggerType.TIME_BASED,
                trigger_conditions={"last_review_days": 180, "escalation_threshold": True},
                action_type=ActionType.ESCALATE,
                action_parameters={"escalation_level": "management", "notify_roles": ["admin", "owner"]},
                priority=1,
                enabled=True,
                created_at=datetime.now()
            )
        ]

    def _load_trigger_conditions(self) -> Dict[str, Dict[str, Any]]:
        """Load trigger condition definitions"""
        return {
            "time_based": {
                "interval_days": "Number of days between triggers",
                "last_review_days": "Days since last review",
                "last_modified_days": "Days since last modification",
                "created_days": "Days since creation"
            },
            "content_based": {
                "content_length": "Document content length",
                "section_count": "Number of sections",
                "cross_reference_count": "Number of cross-references",
                "code_block_count": "Number of code blocks"
            },
            "authority_based": {
                "authority_level": "Authority level of document",
                "authority_scope": "Authority scope",
                "governance_compliance": "Governance compliance status"
            },
            "dependency_based": {
                "check_cross_references": "Check cross-reference validity",
                "validate_targets": "Validate target documents",
                "dependency_changes": "Monitor dependency changes"
            }
        }

    def _load_action_handlers(self) -> Dict[ActionType, Dict[str, Any]]:
        """Load action handler definitions"""
        return {
            ActionType.REVIEW: {
                "description": "Trigger document review process",
                "parameters": ["review_type", "notify_roles", "review_deadline"],
                "handler": "_handle_review_action"
            },
            ActionType.UPDATE: {
                "description": "Update document content or metadata",
                "parameters": ["update_type", "update_source", "notify_roles"],
                "handler": "_handle_update_action"
            },
            ActionType.DEPRECATE: {
                "description": "Deprecate document with notice period",
                "parameters": ["deprecation_notice_days", "notify_roles", "replacement_doc"],
                "handler": "_handle_deprecate_action"
            },
            ActionType.ARCHIVE: {
                "description": "Archive document",
                "parameters": ["archive_reason", "notify_roles", "archive_location"],
                "handler": "_handle_archive_action"
            },
            ActionType.DELETE: {
                "description": "Delete document",
                "parameters": ["delete_reason", "notify_roles", "backup_required"],
                "handler": "_handle_delete_action"
            },
            ActionType.NOTIFY: {
                "description": "Send notifications to roles",
                "parameters": ["notify_roles", "message", "urgency"],
                "handler": "_handle_notify_action"
            },
            ActionType.ESCALATE: {
                "description": "Escalate to higher authority",
                "parameters": ["escalation_level", "notify_roles", "escalation_reason"],
                "handler": "_handle_escalate_action"
            },
            ActionType.VALIDATE: {
                "description": "Validate document content or structure",
                "parameters": ["validation_type", "validation_rules", "notify_roles"],
                "handler": "_handle_validate_action"
            }
        }

    def init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lifecycle_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    authority_level TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    trigger_conditions TEXT,
                    action_type TEXT NOT NULL,
                    action_parameters TEXT,
                    priority INTEGER NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS lifecycle_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_id TEXT UNIQUE NOT NULL,
                    rule_id TEXT NOT NULL,
                    document_path TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    trigger_data TEXT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS lifecycle_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT UNIQUE NOT NULL,
                    trigger_id TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    document_path TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_parameters TEXT,
                    execution_status TEXT NOT NULL,
                    execution_result TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS lifecycle_workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT UNIQUE NOT NULL,
                    document_path TEXT NOT NULL,
                    current_stage TEXT NOT NULL,
                    stage_history TEXT,
                    active_triggers TEXT,
                    pending_actions TEXT,
                    workflow_rules TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_rule_id ON lifecycle_rules(rule_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trigger_id ON lifecycle_triggers(trigger_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_action_id ON lifecycle_actions(action_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_workflow_id ON lifecycle_workflows(workflow_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_document_path ON lifecycle_workflows(document_path)")

    def evaluate_triggers(self, file_path: str, authority_level: str = None) -> List[LifecycleTrigger]:
        """Evaluate triggers for a document"""
        logger.info(f"Evaluating triggers for {file_path}")

        triggers = []

        try:
            # Get document metadata
            doc_metadata = self._get_document_metadata(file_path)

            # Evaluate each rule
            for rule in self.lifecycle_rules:
                if not rule.enabled:
                    continue

                # Check authority level filter
                if rule.authority_level != "all" and authority_level and rule.authority_level != authority_level:
                    continue

                # Check if rule should trigger
                if self._should_trigger_rule(rule, doc_metadata):
                    trigger = self._create_trigger(rule, file_path, doc_metadata)
                    triggers.append(trigger)
                    self._store_trigger(trigger)

        except Exception as e:
            logger.error(f"Error evaluating triggers for {file_path}: {e}")

        return triggers

    def _get_document_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get document metadata for trigger evaluation"""
        try:
            file_stat = Path(file_path).stat()

            metadata = {
                "file_path": file_path,
                "created_time": datetime.fromtimestamp(file_stat.st_ctime),
                "modified_time": datetime.fromtimestamp(file_stat.st_mtime),
                "file_size": file_stat.st_size,
                "last_review_time": None,  # Would be stored in database
                "authority_level": None,   # Would be determined by authority system
                "cross_references": [],
                "dependencies": []
            }

            # Read file content for additional metadata
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                metadata["content_length"] = len(content)
                metadata["section_count"] = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
                metadata["cross_references"] = re.findall(r'@\w+', content)
                metadata["code_block_count"] = len(re.findall(r'```[\s\S]*?```', content))

            return metadata

        except Exception as e:
            logger.error(f"Error getting document metadata for {file_path}: {e}")
            return {}

    def _should_trigger_rule(self, rule: LifecycleRule, metadata: Dict[str, Any]) -> bool:
        """Check if a rule should trigger based on conditions"""
        conditions = rule.trigger_conditions

        if rule.trigger_type == TriggerType.TIME_BASED:
            return self._evaluate_time_based_conditions(conditions, metadata)
        elif rule.trigger_type == TriggerType.CONTENT_BASED:
            return self._evaluate_content_based_conditions(conditions, metadata)
        elif rule.trigger_type == TriggerType.AUTHORITY_BASED:
            return self._evaluate_authority_based_conditions(conditions, metadata)
        elif rule.trigger_type == TriggerType.DEPENDENCY_BASED:
            return self._evaluate_dependency_based_conditions(conditions, metadata)

        return False

    def _evaluate_time_based_conditions(self, conditions: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Evaluate time-based trigger conditions"""
        now = datetime.now()

        # Check interval conditions
        if "interval_days" in conditions:
            if "last_review_time" in metadata and metadata["last_review_time"]:
                days_since_review = (now - metadata["last_review_time"]).days
                if days_since_review >= conditions["interval_days"]:
                    return True

        # Check last modified conditions
        if "last_modified_days" in conditions:
            days_since_modified = (now - metadata["modified_time"]).days
            if days_since_modified >= conditions["last_modified_days"]:
                return True

        # Check creation time conditions
        if "created_days" in conditions:
            days_since_created = (now - metadata["created_time"]).days
            if days_since_created >= conditions["created_days"]:
                return True

        return False

    def _evaluate_content_based_conditions(self, conditions: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Evaluate content-based trigger conditions"""
        # Check content length
        if "content_length" in conditions:
            if metadata.get("content_length", 0) < conditions["content_length"]:
                return True

        # Check section count
        if "section_count" in conditions:
            if metadata.get("section_count", 0) < conditions["section_count"]:
                return True

        # Check cross-reference count
        if "cross_reference_count" in conditions:
            if len(metadata.get("cross_references", [])) < conditions["cross_reference_count"]:
                return True

        return False

    def _evaluate_authority_based_conditions(self, conditions: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Evaluate authority-based trigger conditions"""
        # Check authority level
        if "authority_level" in conditions:
            allowed_levels = conditions["authority_level"]
            if isinstance(allowed_levels, list):
                if metadata.get("authority_level") in allowed_levels:
                    return True
            else:
                if metadata.get("authority_level") == allowed_levels:
                    return True

        return False

    def _evaluate_dependency_based_conditions(self, conditions: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Evaluate dependency-based trigger conditions"""
        # Check cross-references
        if conditions.get("check_cross_references", False):
            cross_refs = metadata.get("cross_references", [])
            if cross_refs:
                # Would validate cross-references here
                return True

        return False

    def _create_trigger(self, rule: LifecycleRule, file_path: str, metadata: Dict[str, Any]) -> LifecycleTrigger:
        """Create a lifecycle trigger"""
        trigger_id = f"trigger_{rule.rule_id}_{int(datetime.now().timestamp())}"

        return LifecycleTrigger(
            trigger_id=trigger_id,
            rule_id=rule.rule_id,
            document_path=file_path,
            trigger_type=rule.trigger_type,
            trigger_data=metadata,
            timestamp=datetime.now(),
            status="pending"
        )

    def _store_trigger(self, trigger: LifecycleTrigger):
        """Store trigger in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO lifecycle_triggers
                    (trigger_id, rule_id, document_path, trigger_type, trigger_data, timestamp, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    trigger.trigger_id,
                    trigger.rule_id,
                    trigger.document_path,
                    trigger.trigger_type.value,
                    json.dumps(trigger.trigger_data),
                    trigger.timestamp.isoformat(),
                    trigger.status
                ))

        except Exception as e:
            logger.error(f"Error storing trigger: {e}")

    def execute_actions(self, triggers: List[LifecycleTrigger]) -> List[LifecycleAction]:
        """Execute actions for triggers"""
        logger.info(f"Executing actions for {len(triggers)} triggers")

        actions = []

        for trigger in triggers:
            try:
                # Get the rule for this trigger
                rule = next((r for r in self.lifecycle_rules if r.rule_id == trigger.rule_id), None)
                if not rule:
                    continue

                # Execute the action
                action = self._execute_action(rule, trigger)
                if action:
                    actions.append(action)
                    self._store_action(action)

                    # Update trigger status
                    trigger.status = "executed"
                    self._update_trigger_status(trigger)

        return actions

    def _execute_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Optional[LifecycleAction]:
        """Execute a single action"""
        action_id = f"action_{rule.rule_id}_{int(datetime.now().timestamp())}"

        # Get action handler
        handler_info = self.action_handlers.get(rule.action_type)
        if not handler_info:
            logger.error(f"No handler found for action type: {rule.action_type}")
            return None

        # Execute the action
        try:
            execution_result = getattr(self, handler_info["handler"])(rule, trigger)

            action = LifecycleAction(
                action_id=action_id,
                trigger_id=trigger.trigger_id,
                rule_id=rule.rule_id,
                document_path=trigger.document_path,
                action_type=rule.action_type,
                action_parameters=rule.action_parameters,
                execution_status="completed",
                execution_result=execution_result,
                timestamp=datetime.now()
            )

            return action

        except Exception as e:
            logger.error(f"Error executing action {rule.action_type}: {e}")

            action = LifecycleAction(
                action_id=action_id,
                trigger_id=trigger.trigger_id,
                rule_id=rule.rule_id,
                document_path=trigger.document_path,
                action_type=rule.action_type,
                action_parameters=rule.action_parameters,
                execution_status="failed",
                execution_result={"error": str(e)},
                timestamp=datetime.now()
            )

            return action

    def _handle_review_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Dict[str, Any]:
        """Handle review action"""
        params = rule.action_parameters
        result = {
            "action": "review",
            "review_type": params.get("review_type", "general"),
            "notified_roles": params.get("notify_roles", []),
            "review_deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "review_requested"
        }

        logger.info(f"Review requested for {trigger.document_path}: {result}")
        return result

    def _handle_update_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Dict[str, Any]:
        """Handle update action"""
        params = rule.action_parameters
        result = {
            "action": "update",
            "update_type": params.get("update_type", "metadata"),
            "update_source": params.get("update_source", "system"),
            "notified_roles": params.get("notify_roles", []),
            "status": "update_initiated"
        }

        logger.info(f"Update initiated for {trigger.document_path}: {result}")
        return result

    def _handle_deprecate_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Dict[str, Any]:
        """Handle deprecate action"""
        params = rule.action_parameters
        result = {
            "action": "deprecate",
            "deprecation_notice_days": params.get("deprecation_notice_days", 30),
            "notified_roles": params.get("notify_roles", []),
            "replacement_doc": params.get("replacement_doc", ""),
            "status": "deprecation_notice_sent"
        }

        logger.info(f"Deprecation notice sent for {trigger.document_path}: {result}")
        return result

    def _handle_archive_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Dict[str, Any]:
        """Handle archive action"""
        params = rule.action_parameters
        result = {
            "action": "archive",
            "archive_reason": params.get("archive_reason", "lifecycle_rule"),
            "notified_roles": params.get("notify_roles", []),
            "archive_location": params.get("archive_location", "archives/"),
            "status": "archived"
        }

        logger.info(f"Document archived: {trigger.document_path}: {result}")
        return result

    def _handle_delete_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Dict[str, Any]:
        """Handle delete action"""
        params = rule.action_parameters
        result = {
            "action": "delete",
            "delete_reason": params.get("delete_reason", "lifecycle_rule"),
            "notified_roles": params.get("notify_roles", []),
            "backup_required": params.get("backup_required", True),
            "status": "deletion_requested"
        }

        logger.info(f"Deletion requested for {trigger.document_path}: {result}")
        return result

    def _handle_notify_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Dict[str, Any]:
        """Handle notify action"""
        params = rule.action_parameters
        result = {
            "action": "notify",
            "notified_roles": params.get("notify_roles", []),
            "message": params.get("message", "Document requires attention"),
            "urgency": params.get("urgency", "normal"),
            "status": "notification_sent"
        }

        logger.info(f"Notification sent for {trigger.document_path}: {result}")
        return result

    def _handle_escalate_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Dict[str, Any]:
        """Handle escalate action"""
        params = rule.action_parameters
        result = {
            "action": "escalate",
            "escalation_level": params.get("escalation_level", "management"),
            "notified_roles": params.get("notify_roles", []),
            "escalation_reason": params.get("escalation_reason", "lifecycle_rule"),
            "status": "escalated"
        }

        logger.info(f"Escalation triggered for {trigger.document_path}: {result}")
        return result

    def _handle_validate_action(self, rule: LifecycleRule, trigger: LifecycleTrigger) -> Dict[str, Any]:
        """Handle validate action"""
        params = rule.action_parameters
        result = {
            "action": "validate",
            "validation_type": params.get("validation_type", "general"),
            "validation_rules": params.get("validation_rules", []),
            "notified_roles": params.get("notify_roles", []),
            "status": "validation_initiated"
        }

        logger.info(f"Validation initiated for {trigger.document_path}: {result}")
        return result

    def _store_action(self, action: LifecycleAction):
        """Store action in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO lifecycle_actions
                    (action_id, trigger_id, rule_id, document_path, action_type,
                     action_parameters, execution_status, execution_result, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    action.action_id,
                    action.trigger_id,
                    action.rule_id,
                    action.document_path,
                    action.action_type.value,
                    json.dumps(action.action_parameters),
                    action.execution_status,
                    json.dumps(action.execution_result),
                    action.timestamp.isoformat()
                ))

        except Exception as e:
            logger.error(f"Error storing action: {e}")

    def _update_trigger_status(self, trigger: LifecycleTrigger):
        """Update trigger status in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE lifecycle_triggers
                    SET status = ?
                    WHERE trigger_id = ?
                """, (trigger.status, trigger.trigger_id))

        except Exception as e:
            logger.error(f"Error updating trigger status: {e}")

    def create_lifecycle_workflow(self, file_path: str) -> LifecycleWorkflow:
        """Create lifecycle workflow for a document"""
        logger.info(f"Creating lifecycle workflow for {file_path}")

        workflow_id = f"workflow_{Path(file_path).stem}_{int(datetime.now().timestamp())}"

        workflow = LifecycleWorkflow(
            workflow_id=workflow_id,
            document_path=file_path,
            current_stage=LifecycleStage.ACTIVE,
            stage_history=[],
            active_triggers=[],
            pending_actions=[],
            workflow_rules=[],
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Store workflow
        self._store_workflow(workflow)

        return workflow

    def _store_workflow(self, workflow: LifecycleWorkflow):
        """Store workflow in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO lifecycle_workflows
                    (workflow_id, document_path, current_stage, stage_history, active_triggers,
                     pending_actions, workflow_rules, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    workflow.workflow_id,
                    workflow.document_path,
                    workflow.current_stage.value,
                    json.dumps(workflow.stage_history),
                    json.dumps([asdict(t) for t in workflow.active_triggers]),
                    json.dumps([asdict(a) for a in workflow.pending_actions]),
                    json.dumps(workflow.workflow_rules),
                    json.dumps(workflow.metadata),
                    workflow.created_at.isoformat(),
                    workflow.updated_at.isoformat()
                ))

        except Exception as e:
            logger.error(f"Error storing workflow: {e}")

    def analyze_directory(self, directory_path: str, file_pattern: str = "*.md") -> LifecycleAnalysis:
        """Analyze directory for lifecycle management"""
        logger.info(f"Analyzing directory for lifecycle management: {directory_path}")

        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        # Find all matching files
        files = list(directory.rglob(file_pattern))
        logger.info(f"Found {len(files)} files to analyze")

        workflows = []
        all_triggers = []
        all_actions = []

        for file_path in files:
            try:
                # Create workflow
                workflow = self.create_lifecycle_workflow(str(file_path))
                workflows.append(workflow)

                # Evaluate triggers
                triggers = self.evaluate_triggers(str(file_path))
                all_triggers.extend(triggers)

                # Execute actions
                actions = self.execute_actions(triggers)
                all_actions.extend(actions)

                # Update workflow
                workflow.active_triggers = triggers
                workflow.pending_actions = actions
                workflow.updated_at = datetime.now()
                self._update_workflow(workflow)

            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")

        # Calculate statistics
        stage_distribution = Counter(w.current_stage for w in workflows)
        trigger_distribution = Counter(t.trigger_type for t in all_triggers)
        action_distribution = Counter(a.action_type for a in all_actions)

        # Generate recommendations
        recommendations = self._generate_lifecycle_recommendations(workflows, all_triggers, all_actions)

        return LifecycleAnalysis(
            workflows=workflows,
            triggers=all_triggers,
            actions=all_actions,
            stage_distribution=dict(stage_distribution),
            trigger_distribution=dict(trigger_distribution),
            action_distribution=dict(action_distribution),
            recommendations=recommendations,
            timestamp=datetime.now()
        )

    def _update_workflow(self, workflow: LifecycleWorkflow):
        """Update workflow in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE lifecycle_workflows
                    SET current_stage = ?, stage_history = ?, active_triggers = ?,
                        pending_actions = ?, workflow_rules = ?, metadata = ?, updated_at = ?
                    WHERE workflow_id = ?
                """, (
                    workflow.current_stage.value,
                    json.dumps(workflow.stage_history),
                    json.dumps([asdict(t) for t in workflow.active_triggers]),
                    json.dumps([asdict(a) for a in workflow.pending_actions]),
                    json.dumps(workflow.workflow_rules),
                    json.dumps(workflow.metadata),
                    workflow.updated_at.isoformat(),
                    workflow.workflow_id
                ))

        except Exception as e:
            logger.error(f"Error updating workflow: {e}")

    def _generate_lifecycle_recommendations(self, workflows: List[LifecycleWorkflow],
                                         triggers: List[LifecycleTrigger],
                                         actions: List[LifecycleAction]) -> List[str]:
        """Generate lifecycle recommendations"""
        recommendations = []

        # Workflow recommendations
        active_count = len([w for w in workflows if w.current_stage == LifecycleStage.ACTIVE])
        if active_count > len(workflows) * 0.8:
            recommendations.append("High proportion of active documents - consider review and deprecation")

        # Trigger recommendations
        pending_triggers = [t for t in triggers if t.status == "pending"]
        if pending_triggers:
            recommendations.append(f"{len(pending_triggers)} pending triggers - review and execute")

        # Action recommendations
        failed_actions = [a for a in actions if a.execution_status == "failed"]
        if failed_actions:
            recommendations.append(f"{len(failed_actions)} failed actions - investigate and retry")

        # Review recommendations
        review_actions = [a for a in actions if a.action_type == ActionType.REVIEW]
        if review_actions:
            recommendations.append(f"{len(review_actions)} review actions initiated - monitor completion")

        return recommendations

    def export_analysis(self, analysis: LifecycleAnalysis,
                       output_dir: str = "artifacts/lifecycle") -> Dict[str, str]:
        """Export analysis results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = analysis.timestamp.strftime("%Y%m%d_%H%M%S")

        # Export detailed results
        results_file = output_path / f"lifecycle_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": analysis.timestamp.isoformat(),
                "stage_distribution": {k.value: v for k, v in analysis.stage_distribution.items()},
                "trigger_distribution": {k.value: v for k, v in analysis.trigger_distribution.items()},
                "action_distribution": {k.value: v for k, v in analysis.action_distribution.items()},
                "recommendations": analysis.recommendations,
                "workflows": [
                    {
                        "workflow_id": w.workflow_id,
                        "document_path": w.document_path,
                        "current_stage": w.current_stage.value,
                        "stage_history": w.stage_history,
                        "active_triggers": len(w.active_triggers),
                        "pending_actions": len(w.pending_actions),
                        "workflow_rules": w.workflow_rules,
                        "metadata": w.metadata,
                        "created_at": w.created_at.isoformat(),
                        "updated_at": w.updated_at.isoformat()
                    }
                    for w in analysis.workflows
                ],
                "triggers": [
                    {
                        "trigger_id": t.trigger_id,
                        "rule_id": t.rule_id,
                        "document_path": t.document_path,
                        "trigger_type": t.trigger_type.value,
                        "trigger_data": t.trigger_data,
                        "timestamp": t.timestamp.isoformat(),
                        "status": t.status
                    }
                    for t in analysis.triggers
                ],
                "actions": [
                    {
                        "action_id": a.action_id,
                        "trigger_id": a.trigger_id,
                        "rule_id": a.rule_id,
                        "document_path": a.document_path,
                        "action_type": a.action_type.value,
                        "action_parameters": a.action_parameters,
                        "execution_status": a.execution_status,
                        "execution_result": a.execution_result,
                        "timestamp": a.timestamp.isoformat()
                    }
                    for a in analysis.actions
                ]
            }, f, indent=2)

        # Export summary report
        summary_file = output_path / f"lifecycle_summary_{timestamp}.md"
        with open(summary_file, 'w') as f:
            f.write(f"# Lifecycle Management Analysis Summary\n\n")
            f.write(f"**Analysis Date:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(f"## Stage Distribution\n\n")
            for stage, count in analysis.stage_distribution.items():
                percentage = (count / len(analysis.workflows)) * 100
                f.write(f"- **{stage.title()}:** {count} documents ({percentage:.1f}%)\n")

            f.write(f"\n## Trigger Distribution\n\n")
            for trigger_type, count in analysis.trigger_distribution.items():
                f.write(f"- **{trigger_type.title()}:** {count} triggers\n")

            f.write(f"\n## Action Distribution\n\n")
            for action_type, count in analysis.action_distribution.items():
                f.write(f"- **{action_type.title()}:** {count} actions\n")

            f.write(f"\n## Recommendations\n\n")
            for i, rec in enumerate(analysis.recommendations, 1):
                f.write(f"{i}. {rec}\n")

            f.write(f"\n## Detailed Results\n\n")
            for workflow in analysis.workflows:
                f.write(f"### {Path(workflow.document_path).name}\n\n")
                f.write(f"- **Stage:** {workflow.current_stage.value.title()}\n")
                f.write(f"- **Active Triggers:** {len(workflow.active_triggers)}\n")
                f.write(f"- **Pending Actions:** {len(workflow.pending_actions)}\n")
                f.write(f"- **Last Updated:** {workflow.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        return {
            "results": str(results_file),
            "summary": str(summary_file)
        }


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Lifecycle Management Rules and Triggers System")
    parser.add_argument("path", help="File or directory path to analyze")
    parser.add_argument("--output", "-o", default="artifacts/lifecycle",
                       help="Output directory for results")
    parser.add_argument("--pattern", "-p", default="*.md",
                       help="File pattern to match (for directories)")

    args = parser.parse_args()

    # Initialize system
    lifecycle_system = LifecycleManagementRulesTriggers()

    path = Path(args.path)

    if path.is_file():
        # Analyze single file
        workflow = lifecycle_system.create_lifecycle_workflow(str(path))
        triggers = lifecycle_system.evaluate_triggers(str(path))
        actions = lifecycle_system.execute_actions(triggers)

        print(f"Lifecycle Analysis Result for {path.name}:")
        print(f"- Workflow ID: {workflow.workflow_id}")
        print(f"- Current Stage: {workflow.current_stage.value.title()}")
        print(f"- Triggers Evaluated: {len(triggers)}")
        print(f"- Actions Executed: {len(actions)}")

        if triggers:
            print(f"- Trigger Types: {', '.join(t.trigger_type.value for t in triggers)}")
        if actions:
            print(f"- Action Types: {', '.join(a.action_type.value for a in actions)}")

    elif path.is_dir():
        # Analyze directory
        analysis = lifecycle_system.analyze_directory(str(path), args.pattern)

        print(f"Lifecycle Management Analysis Complete:")
        print(f"- Workflows created: {len(analysis.workflows)}")
        print(f"- Triggers evaluated: {len(analysis.triggers)}")
        print(f"- Actions executed: {len(analysis.actions)}")
        print(f"- Stage distribution: {analysis.stage_distribution}")
        print(f"- Trigger distribution: {analysis.trigger_distribution}")
        print(f"- Action distribution: {analysis.action_distribution}")
        print(f"- Recommendations: {len(analysis.recommendations)}")

        # Export results
        output_files = lifecycle_system.export_analysis(analysis, args.output)
        print(f"\nResults exported to:")
        for file_type, file_path in output_files.items():
            print(f"- {file_type}: {file_path}")

    else:
        print(f"Error: Path does not exist: {path}")


if __name__ == "__main__":
    main()
