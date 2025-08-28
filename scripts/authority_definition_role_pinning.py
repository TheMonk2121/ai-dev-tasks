#!/usr/bin/env python3
"""
Authority Definition and Role Pinning System for Documentation t-t3 Authority Structure

This module implements sophisticated authority detection, role assignment, and
pinning mechanisms for documentation governance and access control.

Author: AI Assistant
Date: 2025-01-27
"""

import json
import logging
import re
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthorityLevel(Enum):
    """Authority levels for documentation"""

    CRITICAL = "critical"  # Highest authority - core governance
    HIGH = "high"  # High authority - important decisions
    MEDIUM = "medium"  # Medium authority - implementation guidance
    LOW = "low"  # Low authority - reference and utility
    NONE = "none"  # No authority - informational only


class RoleType(Enum):
    """Role types for documentation access and governance"""

    OWNER = "owner"  # Document owner with full control
    EDITOR = "editor"  # Can edit and modify content
    REVIEWER = "reviewer"  # Can review and approve changes
    CONSUMER = "consumer"  # Can read and use content
    ADMIN = "admin"  # Administrative access
    GUEST = "guest"  # Limited read access


class PinStatus(Enum):
    """Status of role pinning"""

    ACTIVE = "active"  # Role is actively pinned
    INACTIVE = "inactive"  # Role is not pinned
    PENDING = "pending"  # Role pinning is pending
    EXPIRED = "expired"  # Role pinning has expired


@dataclass
class AuthorityDefinition:
    """Definition of authority for a document"""

    document_path: str
    authority_level: AuthorityLevel
    authority_scope: str
    authority_indicators: List[str]
    authority_declaration: str
    governance_rules: Dict[str, Any]
    approval_workflow: List[str]
    timestamp: datetime


@dataclass
class RolePin:
    """Role pin for a document"""

    document_path: str
    role_type: RoleType
    role_name: str
    role_description: str
    permissions: List[str]
    pin_status: PinStatus
    pin_date: datetime
    expiry_date: Optional[datetime]
    pinned_by: str
    metadata: Dict[str, Any]


@dataclass
class AuthorityRoleMapping:
    """Mapping of authority to roles for a document"""

    document_path: str
    authority_definition: AuthorityDefinition
    role_pins: List[RolePin]
    access_control: Dict[str, List[str]]
    governance_hierarchy: List[str]
    timestamp: datetime


@dataclass
class AuthorityAnalysis:
    """Complete authority and role analysis result"""

    authority_definitions: List[AuthorityDefinition]
    role_pins: List[RolePin]
    authority_role_mappings: List[AuthorityRoleMapping]
    authority_distribution: Dict[AuthorityLevel, int]
    role_distribution: Dict[RoleType, int]
    pin_status_distribution: Dict[PinStatus, int]
    recommendations: List[str]
    timestamp: datetime


class AuthorityDefinitionRolePinning:
    """
    Authority Definition and Role Pinning system
    """

    def __init__(self, db_path: str = "authority_role_pinning.db"):
        """Initialize the authority definition and role pinning system"""
        self.db_path = db_path
        self.authority_patterns = self._load_authority_patterns()
        self.role_patterns = self._load_role_patterns()
        self.governance_rules = self._load_governance_rules()
        self.permission_matrix = self._load_permission_matrix()
        self.init_database()

    def _load_authority_patterns(self) -> Dict[str, List[str]]:
        """Load authority detection patterns"""
        return {
            "critical_authority": [
                r"critical|essential|mandatory|required|must|shall",
                r"governance|policy|standard|regulation|compliance",
                r"core|fundamental|primary|principal|central",
                r"authority|authoritative|official|formal|binding",
            ],
            "high_authority": [
                r"important|significant|major|key|primary",
                r"best practice|guideline|recommendation|specification",
                r"process|procedure|workflow|methodology|framework",
                r"decision|approval|validation|verification",
            ],
            "medium_authority": [
                r"standard|convention|pattern|approach|method",
                r"implementation|execution|operation|maintenance",
                r"guidance|direction|instruction|tutorial|guide",
                r"reference|documentation|specification|interface",
            ],
            "low_authority": [
                r"optional|suggested|recommended|preferred",
                r"utility|tool|helper|assistant|support",
                r"example|sample|template|boilerplate",
                r"informational|educational|tutorial|learning",
            ],
            "no_authority": [
                r"informational|educational|tutorial|learning",
                r"example|sample|template|boilerplate",
                r"archive|legacy|deprecated|outdated",
                r"draft|proposal|suggestion|idea",
            ],
        }

    def _load_role_patterns(self) -> Dict[str, List[str]]:
        """Load role detection patterns"""
        return {
            "owner": [
                r"owner|creator|author|maintainer|steward",
                r"responsible|accountable|liable|answerable",
                r"lead|principal|chief|head|director",
            ],
            "editor": [
                r"editor|writer|contributor|developer|coder",
                r"modify|change|update|revise|edit",
                r"implement|build|create|develop|code",
            ],
            "reviewer": [
                r"reviewer|approver|validator|verifier|checker",
                r"review|approve|validate|verify|check",
                r"quality|assurance|testing|validation",
            ],
            "consumer": [
                r"user|consumer|reader|viewer|audience",
                r"use|consume|read|view|access",
                r"follow|implement|apply|adopt|use",
            ],
            "admin": [
                r"admin|administrator|manager|supervisor|coordinator",
                r"manage|coordinate|organize|oversee|supervise",
                r"system|infrastructure|platform|environment",
            ],
            "guest": [
                r"guest|visitor|observer|spectator|onlooker",
                r"view|observe|watch|monitor|track",
                r"public|open|accessible|available",
            ],
        }

    def _load_governance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load governance rules for different authority levels"""
        return {
            "critical": {
                "approval_required": True,
                "review_frequency": "monthly",
                "change_notification": True,
                "version_control": True,
                "audit_trail": True,
                "rollback_required": True,
                "stakeholder_approval": True,
            },
            "high": {
                "approval_required": True,
                "review_frequency": "quarterly",
                "change_notification": True,
                "version_control": True,
                "audit_trail": True,
                "rollback_required": False,
                "stakeholder_approval": False,
            },
            "medium": {
                "approval_required": False,
                "review_frequency": "semi_annually",
                "change_notification": True,
                "version_control": True,
                "audit_trail": False,
                "rollback_required": False,
                "stakeholder_approval": False,
            },
            "low": {
                "approval_required": False,
                "review_frequency": "annually",
                "change_notification": False,
                "version_control": True,
                "audit_trail": False,
                "rollback_required": False,
                "stakeholder_approval": False,
            },
            "none": {
                "approval_required": False,
                "review_frequency": "never",
                "change_notification": False,
                "version_control": False,
                "audit_trail": False,
                "rollback_required": False,
                "stakeholder_approval": False,
            },
        }

    def _load_permission_matrix(self) -> Dict[RoleType, List[str]]:
        """Load permission matrix for different roles"""
        return {
            RoleType.OWNER: [
                "read",
                "write",
                "delete",
                "approve",
                "review",
                "pin_roles",
                "change_authority",
                "modify_governance",
                "manage_permissions",
            ],
            RoleType.EDITOR: ["read", "write", "review", "suggest_changes", "update_metadata"],
            RoleType.REVIEWER: ["read", "review", "approve", "reject", "comment", "suggest_improvements"],
            RoleType.CONSUMER: ["read", "comment", "suggest_improvements", "report_issues"],
            RoleType.ADMIN: [
                "read",
                "write",
                "delete",
                "approve",
                "review",
                "pin_roles",
                "manage_permissions",
                "system_administration",
            ],
            RoleType.GUEST: ["read", "comment"],
        }

    def init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS authority_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_path TEXT NOT NULL,
                    authority_level TEXT NOT NULL,
                    authority_scope TEXT NOT NULL,
                    authority_indicators TEXT,
                    authority_declaration TEXT,
                    governance_rules TEXT,
                    approval_workflow TEXT,
                    timestamp TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS role_pins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_path TEXT NOT NULL,
                    role_type TEXT NOT NULL,
                    role_name TEXT NOT NULL,
                    role_description TEXT,
                    permissions TEXT,
                    pin_status TEXT NOT NULL,
                    pin_date TEXT NOT NULL,
                    expiry_date TEXT,
                    pinned_by TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS authority_role_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_path TEXT NOT NULL,
                    authority_definition_id INTEGER,
                    role_pins TEXT,
                    access_control TEXT,
                    governance_hierarchy TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (authority_definition_id) REFERENCES authority_definitions (id)
                )
            """
            )

            conn.execute("CREATE INDEX IF NOT EXISTS idx_document_path ON authority_definitions(document_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_authority_level ON authority_definitions(authority_level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_role_type ON role_pins(role_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pin_status ON role_pins(pin_status)")

    def detect_authority(self, file_path: str) -> AuthorityDefinition:
        """Detect authority level and definition for a document"""
        logger.info(f"Detecting authority for {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Analyze content for authority indicators
            authority_scores = self._calculate_authority_scores(content)
            authority_level = self._determine_authority_level(authority_scores)
            authority_scope = self._determine_authority_scope(content)
            authority_indicators = self._extract_authority_indicators(content)
            authority_declaration = self._extract_authority_declaration(content)

            # Get governance rules for authority level
            governance_rules = self.governance_rules.get(authority_level.value, {})

            # Determine approval workflow
            approval_workflow = self._determine_approval_workflow(authority_level, content)

            authority_def = AuthorityDefinition(
                document_path=file_path,
                authority_level=authority_level,
                authority_scope=authority_scope,
                authority_indicators=authority_indicators,
                authority_declaration=authority_declaration,
                governance_rules=governance_rules,
                approval_workflow=approval_workflow,
                timestamp=datetime.now(),
            )

            # Store authority definition
            self._store_authority_definition(authority_def)

            return authority_def

        except Exception as e:
            logger.error(f"Error detecting authority for {file_path}: {e}")
            return AuthorityDefinition(
                document_path=file_path,
                authority_level=AuthorityLevel.NONE,
                authority_scope="unknown",
                authority_indicators=[],
                authority_declaration="",
                governance_rules={},
                approval_workflow=[],
                timestamp=datetime.now(),
            )

    def _calculate_authority_scores(self, content: str) -> Dict[str, float]:
        """Calculate authority scores for different levels"""
        scores = {}
        content_lower = content.lower()

        for level, patterns in self.authority_patterns.items():
            score = 0.0
            total_matches = 0

            for pattern in patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                total_matches += len(matches)
                score += len(matches) * 0.1  # Weight each match

            # Normalize score
            scores[level] = min(1.0, score)

        return scores

    def _determine_authority_level(self, scores: Dict[str, float]) -> AuthorityLevel:
        """Determine authority level based on scores"""
        # Find the highest scoring level
        max_score = 0.0
        best_level = AuthorityLevel.NONE

        for level_name, score in scores.items():
            if score > max_score:
                max_score = score
                if level_name == "critical_authority":
                    best_level = AuthorityLevel.CRITICAL
                elif level_name == "high_authority":
                    best_level = AuthorityLevel.HIGH
                elif level_name == "medium_authority":
                    best_level = AuthorityLevel.MEDIUM
                elif level_name == "low_authority":
                    best_level = AuthorityLevel.LOW
                elif level_name == "no_authority":
                    best_level = AuthorityLevel.NONE

        return best_level

    def _determine_authority_scope(self, content: str) -> str:
        """Determine authority scope from content"""
        content_lower = content.lower()

        # Check for global scope indicators
        if any(re.search(pattern, content_lower) for pattern in [r"global|organization|company|enterprise|all"]):
            return "global"

        # Check for project scope indicators
        if any(re.search(pattern, content_lower) for pattern in [r"project|team|department|division|specific"]):
            return "project"

        # Check for role scope indicators
        if any(re.search(pattern, content_lower) for pattern in [r"role|position|function|responsibility|individual"]):
            return "role"

        # Default to context scope
        return "context"

    def _extract_authority_indicators(self, content: str) -> List[str]:
        """Extract authority indicators from content"""
        indicators = []
        content_lower = content.lower()

        for level, patterns in self.authority_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                indicators.extend(matches)

        return list(set(indicators))

    def _extract_authority_declaration(self, content: str) -> str:
        """Extract authority declaration from content"""
        # Look for explicit authority declarations
        authority_patterns = [
            r"This document has (?:the |an |)(?:authority|authoritative|governance|standard)",
            r"This (?:is |represents |constitutes |)(?:authority|authoritative|governance|standard)",
            r"Authority: (.*?)(?:\n|\.)",
            r"Governance: (.*?)(?:\n|\.)",
            r"Standard: (.*?)(?:\n|\.)",
        ]

        for pattern in authority_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        return ""

    def _determine_approval_workflow(self, authority_level: AuthorityLevel, content: str) -> List[str]:
        """Determine approval workflow based on authority level"""
        workflows = []

        if authority_level == AuthorityLevel.CRITICAL:
            workflows = ["stakeholder_review", "technical_review", "legal_review", "executive_approval"]
        elif authority_level == AuthorityLevel.HIGH:
            workflows = ["technical_review", "peer_review", "manager_approval"]
        elif authority_level == AuthorityLevel.MEDIUM:
            workflows = ["peer_review", "team_lead_approval"]
        elif authority_level == AuthorityLevel.LOW:
            workflows = ["self_review"]
        else:
            workflows = []

        return workflows

    def _store_authority_definition(self, authority_def: AuthorityDefinition):
        """Store authority definition in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO authority_definitions
                    (document_path, authority_level, authority_scope, authority_indicators,
                     authority_declaration, governance_rules, approval_workflow, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        authority_def.document_path,
                        authority_def.authority_level.value,
                        authority_def.authority_scope,
                        json.dumps(authority_def.authority_indicators),
                        authority_def.authority_declaration,
                        json.dumps(authority_def.governance_rules),
                        json.dumps(authority_def.approval_workflow),
                        authority_def.timestamp.isoformat(),
                    ),
                )

        except Exception as e:
            logger.error(f"Error storing authority definition: {e}")

    def detect_roles(self, file_path: str) -> List[RolePin]:
        """Detect roles for a document"""
        logger.info(f"Detecting roles for {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            roles = []

            # Detect roles based on content patterns
            for role_type, patterns in self.role_patterns.items():
                role_score = self._calculate_role_score(content, patterns)

                if role_score > 0.3:  # Threshold for role detection
                    role_pin = self._create_role_pin(file_path, RoleType(role_type), role_score, content)
                    roles.append(role_pin)

            # Add default roles based on authority level
            authority_def = self.detect_authority(file_path)
            default_roles = self._get_default_roles(authority_def.authority_level)

            for role_type in default_roles:
                if not any(r.role_type == role_type for r in roles):
                    role_pin = self._create_default_role_pin(file_path, role_type)
                    roles.append(role_pin)

            # Store role pins
            for role_pin in roles:
                self._store_role_pin(role_pin)

            return roles

        except Exception as e:
            logger.error(f"Error detecting roles for {file_path}: {e}")
            return []

    def _calculate_role_score(self, content: str, patterns: List[str]) -> float:
        """Calculate role score based on pattern matches"""
        score = 0.0
        content_lower = content.lower()

        for pattern in patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            score += len(matches) * 0.1

        return min(1.0, score)

    def _create_role_pin(self, file_path: str, role_type: RoleType, score: float, content: str) -> RolePin:
        """Create a role pin based on detection"""
        role_name = role_type.value.title()
        role_description = self._generate_role_description(role_type, content)
        permissions = self.permission_matrix.get(role_type, [])

        return RolePin(
            document_path=file_path,
            role_type=role_type,
            role_name=role_name,
            role_description=role_description,
            permissions=permissions,
            pin_status=PinStatus.ACTIVE,
            pin_date=datetime.now(),
            expiry_date=None,
            pinned_by="auto_detection",
            metadata={"detection_score": score, "detection_method": "pattern_matching"},
            timestamp=datetime.now(),
        )

    def _create_default_role_pin(self, file_path: str, role_type: RoleType) -> RolePin:
        """Create a default role pin"""
        role_name = role_type.value.title()
        role_description = f"Default {role_name} role for document"
        permissions = self.permission_matrix.get(role_type, [])

        return RolePin(
            document_path=file_path,
            role_type=role_type,
            role_name=role_name,
            role_description=role_description,
            permissions=permissions,
            pin_status=PinStatus.ACTIVE,
            pin_date=datetime.now(),
            expiry_date=None,
            pinned_by="system_default",
            metadata={"detection_method": "default_assignment"},
            timestamp=datetime.now(),
        )

    def _generate_role_description(self, role_type: RoleType, content: str) -> str:
        """Generate role description based on content"""
        descriptions = {
            RoleType.OWNER: "Document owner with full control and responsibility",
            RoleType.EDITOR: "Can edit and modify document content",
            RoleType.REVIEWER: "Can review and approve document changes",
            RoleType.CONSUMER: "Can read and use document content",
            RoleType.ADMIN: "Administrative access to document",
            RoleType.GUEST: "Limited read access to document",
        }

        return descriptions.get(role_type, "Document role")

    def _get_default_roles(self, authority_level: AuthorityLevel) -> List[RoleType]:
        """Get default roles based on authority level"""
        if authority_level == AuthorityLevel.CRITICAL:
            return [RoleType.OWNER, RoleType.REVIEWER, RoleType.CONSUMER, RoleType.ADMIN]
        elif authority_level == AuthorityLevel.HIGH:
            return [RoleType.OWNER, RoleType.EDITOR, RoleType.REVIEWER, RoleType.CONSUMER]
        elif authority_level == AuthorityLevel.MEDIUM:
            return [RoleType.EDITOR, RoleType.REVIEWER, RoleType.CONSUMER]
        elif authority_level == AuthorityLevel.LOW:
            return [RoleType.EDITOR, RoleType.CONSUMER]
        else:
            return [RoleType.CONSUMER]

    def _store_role_pin(self, role_pin: RolePin):
        """Store role pin in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO role_pins
                    (document_path, role_type, role_name, role_description, permissions,
                     pin_status, pin_date, expiry_date, pinned_by, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        role_pin.document_path,
                        role_pin.role_type.value,
                        role_pin.role_name,
                        role_pin.role_description,
                        json.dumps(role_pin.permissions),
                        role_pin.pin_status.value,
                        role_pin.pin_date.isoformat(),
                        role_pin.expiry_date.isoformat() if role_pin.expiry_date else None,
                        role_pin.pinned_by,
                        json.dumps(role_pin.metadata),
                        role_pin.timestamp.isoformat(),
                    ),
                )

        except Exception as e:
            logger.error(f"Error storing role pin: {e}")

    def create_authority_role_mapping(self, file_path: str) -> AuthorityRoleMapping:
        """Create authority-role mapping for a document"""
        logger.info(f"Creating authority-role mapping for {file_path}")

        # Detect authority and roles
        authority_def = self.detect_authority(file_path)
        role_pins = self.detect_roles(file_path)

        # Create access control matrix
        access_control = self._create_access_control(role_pins)

        # Create governance hierarchy
        governance_hierarchy = self._create_governance_hierarchy(authority_def, role_pins)

        mapping = AuthorityRoleMapping(
            document_path=file_path,
            authority_definition=authority_def,
            role_pins=role_pins,
            access_control=access_control,
            governance_hierarchy=governance_hierarchy,
            timestamp=datetime.now(),
        )

        # Store mapping
        self._store_authority_role_mapping(mapping)

        return mapping

    def _create_access_control(self, role_pins: List[RolePin]) -> Dict[str, List[str]]:
        """Create access control matrix from role pins"""
        access_control = {}

        for role_pin in role_pins:
            if role_pin.pin_status == PinStatus.ACTIVE:
                access_control[role_pin.role_type.value] = role_pin.permissions

        return access_control

    def _create_governance_hierarchy(self, authority_def: AuthorityDefinition, role_pins: List[RolePin]) -> List[str]:
        """Create governance hierarchy based on authority and roles"""
        hierarchy = []

        # Add authority level
        hierarchy.append(f"authority:{authority_def.authority_level.value}")

        # Add approval workflow
        for step in authority_def.approval_workflow:
            hierarchy.append(f"approval:{step}")

        # Add role hierarchy
        role_hierarchy = [
            RoleType.OWNER,
            RoleType.ADMIN,
            RoleType.EDITOR,
            RoleType.REVIEWER,
            RoleType.CONSUMER,
            RoleType.GUEST,
        ]

        for role_type in role_hierarchy:
            if any(r.role_type == role_type for r in role_pins):
                hierarchy.append(f"role:{role_type.value}")

        return hierarchy

    def _store_authority_role_mapping(self, mapping: AuthorityRoleMapping):
        """Store authority-role mapping in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # First, get the authority definition ID
                cursor = conn.execute(
                    """
                    SELECT id FROM authority_definitions
                    WHERE document_path = ?
                    ORDER BY timestamp DESC LIMIT 1
                """,
                    (mapping.document_path,),
                )

                authority_def_id = cursor.fetchone()
                authority_def_id = authority_def_id[0] if authority_def_id else None

                conn.execute(
                    """
                    INSERT INTO authority_role_mappings
                    (document_path, authority_definition_id, role_pins, access_control,
                     governance_hierarchy, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        mapping.document_path,
                        authority_def_id,
                        json.dumps([asdict(rp) for rp in mapping.role_pins]),
                        json.dumps(mapping.access_control),
                        json.dumps(mapping.governance_hierarchy),
                        mapping.timestamp.isoformat(),
                    ),
                )

        except Exception as e:
            logger.error(f"Error storing authority-role mapping: {e}")

    def analyze_directory(self, directory_path: str, file_pattern: str = "*.md") -> AuthorityAnalysis:
        """Analyze directory for authority and role patterns"""
        logger.info(f"Analyzing directory for authority and roles: {directory_path}")

        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        # Find all matching files
        files = list(directory.rglob(file_pattern))
        logger.info(f"Found {len(files)} files to analyze")

        authority_definitions = []
        role_pins = []
        authority_role_mappings = []

        for file_path in files:
            try:
                # Create authority-role mapping
                mapping = self.create_authority_role_mapping(str(file_path))
                authority_role_mappings.append(mapping)
                authority_definitions.append(mapping.authority_definition)
                role_pins.extend(mapping.role_pins)

            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")

        # Calculate statistics
        authority_distribution = Counter(def_.authority_level for def_ in authority_definitions)
        role_distribution = Counter(pin.role_type for pin in role_pins)
        pin_status_distribution = Counter(pin.pin_status for pin in role_pins)

        # Generate recommendations
        recommendations = self._generate_authority_recommendations(
            authority_definitions, role_pins, authority_role_mappings
        )

        return AuthorityAnalysis(
            authority_definitions=authority_definitions,
            role_pins=role_pins,
            authority_role_mappings=authority_role_mappings,
            authority_distribution=dict(authority_distribution),
            role_distribution=dict(role_distribution),
            pin_status_distribution=dict(pin_status_distribution),
            recommendations=recommendations,
            timestamp=datetime.now(),
        )

    def _generate_authority_recommendations(
        self,
        authority_definitions: List[AuthorityDefinition],
        role_pins: List[RolePin],
        mappings: List[AuthorityRoleMapping],
    ) -> List[str]:
        """Generate recommendations based on authority and role analysis"""
        recommendations = []

        # Authority level recommendations
        critical_count = len([d for d in authority_definitions if d.authority_level == AuthorityLevel.CRITICAL])
        if critical_count > len(authority_definitions) * 0.2:
            recommendations.append("High proportion of critical authority documents - review if all are truly critical")

        none_count = len([d for d in authority_definitions if d.authority_level == AuthorityLevel.NONE])
        if none_count > len(authority_definitions) * 0.5:
            recommendations.append(
                "High proportion of documents with no authority - consider assigning appropriate authority levels"
            )

        # Role distribution recommendations
        owner_count = len([p for p in role_pins if p.role_type == RoleType.OWNER])
        if owner_count < len(authority_definitions) * 0.8:
            recommendations.append("Many documents lack clear ownership - assign document owners")

        reviewer_count = len([p for p in role_pins if p.role_type == RoleType.REVIEWER])
        if reviewer_count < len(authority_definitions) * 0.6:
            recommendations.append("Many documents lack reviewers - assign review responsibilities")

        # Governance recommendations
        for mapping in mappings:
            if mapping.authority_definition.authority_level in [AuthorityLevel.CRITICAL, AuthorityLevel.HIGH]:
                if not any(p.role_type == RoleType.REVIEWER for p in mapping.role_pins):
                    recommendations.append(f"High authority document {mapping.document_path} lacks reviewers")

        return recommendations

    def export_analysis(
        self, analysis: AuthorityAnalysis, output_dir: str = "artifacts/authority_roles"
    ) -> Dict[str, str]:
        """Export analysis results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = analysis.timestamp.strftime("%Y%m%d_%H%M%S")

        # Export detailed results
        results_file = output_path / f"authority_role_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(
                {
                    "timestamp": analysis.timestamp.isoformat(),
                    "authority_distribution": {k.value: v for k, v in analysis.authority_distribution.items()},
                    "role_distribution": {k.value: v for k, v in analysis.role_distribution.items()},
                    "pin_status_distribution": {k.value: v for k, v in analysis.pin_status_distribution.items()},
                    "recommendations": analysis.recommendations,
                    "authority_definitions": [
                        {
                            "document_path": d.document_path,
                            "authority_level": d.authority_level.value,
                            "authority_scope": d.authority_scope,
                            "authority_indicators": d.authority_indicators,
                            "authority_declaration": d.authority_declaration,
                            "governance_rules": d.governance_rules,
                            "approval_workflow": d.approval_workflow,
                            "timestamp": d.timestamp.isoformat(),
                        }
                        for d in analysis.authority_definitions
                    ],
                    "role_pins": [
                        {
                            "document_path": p.document_path,
                            "role_type": p.role_type.value,
                            "role_name": p.role_name,
                            "role_description": p.role_description,
                            "permissions": p.permissions,
                            "pin_status": p.pin_status.value,
                            "pin_date": p.pin_date.isoformat(),
                            "expiry_date": p.expiry_date.isoformat() if p.expiry_date else None,
                            "pinned_by": p.pinned_by,
                            "metadata": p.metadata,
                            "timestamp": p.timestamp.isoformat(),
                        }
                        for p in analysis.role_pins
                    ],
                },
                f,
                indent=2,
            )

        # Export summary report
        summary_file = output_path / f"authority_role_summary_{timestamp}.md"
        with open(summary_file, "w") as f:
            f.write("# Authority and Role Analysis Summary\n\n")
            f.write(f"**Analysis Date:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Authority Distribution\n\n")
            for level, count in analysis.authority_distribution.items():
                percentage = (count / len(analysis.authority_definitions)) * 100
                f.write(f"- **{level.title()}:** {count} documents ({percentage:.1f}%)\n")

            f.write("\n## Role Distribution\n\n")
            for role, count in analysis.role_distribution.items():
                f.write(f"- **{role.title()}:** {count} pins\n")

            f.write("\n## Pin Status Distribution\n\n")
            for status, count in analysis.pin_status_distribution.items():
                f.write(f"- **{status.title()}:** {count} pins\n")

            f.write("\n## Recommendations\n\n")
            for i, rec in enumerate(analysis.recommendations, 1):
                f.write(f"{i}. {rec}\n")

            f.write("\n## Detailed Results\n\n")
            for mapping in analysis.authority_role_mappings:
                f.write(f"### {Path(mapping.document_path).name}\n\n")
                f.write(f"- **Authority Level:** {mapping.authority_definition.authority_level.value.title()}\n")
                f.write(f"- **Authority Scope:** {mapping.authority_definition.authority_scope.title()}\n")
                f.write(f"- **Roles:** {', '.join(p.role_type.value for p in mapping.role_pins)}\n")
                f.write(f"- **Governance Hierarchy:** {' → '.join(mapping.governance_hierarchy)}\n\n")

        return {"results": str(results_file), "summary": str(summary_file)}


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Authority Definition and Role Pinning System")
    parser.add_argument("path", help="File or directory path to analyze")
    parser.add_argument("--output", "-o", default="artifacts/authority_roles", help="Output directory for results")
    parser.add_argument("--pattern", "-p", default="*.md", help="File pattern to match (for directories)")

    args = parser.parse_args()

    # Initialize system
    authority_system = AuthorityDefinitionRolePinning()

    path = Path(args.path)

    if path.is_file():
        # Analyze single file
        mapping = authority_system.create_authority_role_mapping(str(path))

        print(f"Analysis Result for {path.name}:")
        print(f"- Authority Level: {mapping.authority_definition.authority_level.value.title()}")
        print(f"- Authority Scope: {mapping.authority_definition.authority_scope.title()}")
        print(f"- Authority Indicators: {', '.join(mapping.authority_definition.authority_indicators[:5])}")
        print(f"- Roles: {', '.join(p.role_type.value for p in mapping.role_pins)}")
        print(f"- Governance Hierarchy: {' → '.join(mapping.governance_hierarchy)}")

        if mapping.authority_definition.approval_workflow:
            print(f"- Approval Workflow: {' → '.join(mapping.authority_definition.approval_workflow)}")

    elif path.is_dir():
        # Analyze directory
        analysis = authority_system.analyze_directory(str(path), args.pattern)

        print("Authority and Role Analysis Complete:")
        print(f"- Files analyzed: {len(analysis.authority_definitions)}")
        print(f"- Authority distribution: {analysis.authority_distribution}")
        print(f"- Role distribution: {analysis.role_distribution}")
        print(f"- Pin status distribution: {analysis.pin_status_distribution}")
        print(f"- Recommendations: {len(analysis.recommendations)}")

        # Export results
        output_files = authority_system.export_analysis(analysis, args.output)
        print("\nResults exported to:")
        for file_type, file_path in output_files.items():
            print(f"- {file_type}: {file_path}")

    else:
        print(f"Error: Path does not exist: {path}")


if __name__ == "__main__":
    main()
