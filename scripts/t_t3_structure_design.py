#!/usr/bin/env python3
"""
t-t3 Structure Design and Implementation System for Documentation Authority Structure

This module implements the core t-t3 authority structure with tier definitions,
validation rules, and structural requirements for documentation governance.

Author: AI Assistant
Date: 2025-01-27
"""

import hashlib
import json
import logging
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TierLevel(Enum):
    """Tier levels for documentation authority structure"""

    TIER_1 = "T1"  # Critical - Core authority documents
    TIER_2 = "T2"  # High - Important supporting documents
    TIER_3 = "T3"  # Supporting - Reference and utility documents


class AuthorityScope(Enum):
    """Authority scopes for documentation"""

    GLOBAL = "global"  # Applies to entire organization
    PROJECT = "project"  # Applies to specific project
    TEAM = "team"  # Applies to specific team
    ROLE = "role"  # Applies to specific role
    CONTEXT = "context"  # Applies to specific context


class ValidationStatus(Enum):
    """Validation status for t-t3 structure"""

    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"


@dataclass
class TierDefinition:
    """Definition of a tier in the t-t3 structure"""

    tier: TierLevel
    name: str
    description: str
    authority_level: int
    required_sections: List[str]
    optional_sections: List[str]
    content_requirements: Dict[str, Any]
    validation_rules: List[str]
    lifecycle_rules: Dict[str, Any]
    dependencies: List[str]


@dataclass
class StructureValidation:
    """Validation result for t-t3 structure"""

    file_path: str
    tier: TierLevel
    status: ValidationStatus
    score: float
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class AuthorityMapping:
    """Mapping of authority to documentation structure"""

    file_path: str
    tier: TierLevel
    authority_scope: AuthorityScope
    authority_indicators: List[str]
    role_pins: List[str]
    cross_references: List[str]
    dependencies: List[str]
    timestamp: datetime


@dataclass
class T3StructureAnalysis:
    """Complete t-t3 structure analysis result"""

    structure_validations: List[StructureValidation]
    authority_mappings: List[AuthorityMapping]
    tier_distribution: Dict[TierLevel, int]
    validation_stats: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime


class T3StructureDesign:
    """
    t-t3 Structure Design and Implementation system
    """

    def __init__(self, db_path: str = "t3_structure.db"):
        """Initialize the t-t3 structure design system"""
        self.db_path = db_path
        self.tier_definitions = self._load_tier_definitions()
        self.validation_rules = self._load_validation_rules()
        self.authority_patterns = self._load_authority_patterns()
        self.init_database()

    def _load_tier_definitions(self) -> Dict[TierLevel, TierDefinition]:
        """Load tier definitions for t-t3 structure"""
        return {
            TierLevel.TIER_1: TierDefinition(
                tier=TierLevel.TIER_1,
                name="Critical Authority",
                description="Core authority documents that define fundamental processes, standards, and governance",
                authority_level=3,
                required_sections=[
                    "TL;DR",
                    "ANCHOR_KEY",
                    "ROLE_PINS",
                    "METADATA",
                    "Purpose",
                    "Scope",
                    "Authority",
                    "Process",
                    "Validation",
                ],
                optional_sections=["Examples", "Troubleshooting", "Related Documents", "Change History"],
                content_requirements={
                    "min_length": 1000,
                    "max_length": 10000,
                    "required_cross_references": 3,
                    "required_code_examples": 2,
                    "required_validation": True,
                    "required_approval": True,
                },
                validation_rules=[
                    "must_have_tldr",
                    "must_have_anchor_key",
                    "must_have_role_pins",
                    "must_have_metadata",
                    "must_have_purpose",
                    "must_have_scope",
                    "must_have_authority_declaration",
                    "must_have_process_definition",
                    "must_have_validation_criteria",
                    "must_have_cross_references",
                    "must_have_code_examples",
                ],
                lifecycle_rules={
                    "review_frequency": "monthly",
                    "approval_required": True,
                    "change_notification": True,
                    "version_control": True,
                    "deprecation_notice": 90,
                },
                dependencies=["T2_validation", "T2_approval_workflow"],
            ),
            TierLevel.TIER_2: TierDefinition(
                tier=TierLevel.TIER_2,
                name="High Authority",
                description="Important supporting documents that implement and extend core authority",
                authority_level=2,
                required_sections=["TL;DR", "ANCHOR_KEY", "Purpose", "Implementation"],
                optional_sections=["ROLE_PINS", "METADATA", "Examples", "Validation", "Related Documents"],
                content_requirements={
                    "min_length": 500,
                    "max_length": 5000,
                    "required_cross_references": 1,
                    "required_code_examples": 1,
                    "required_validation": False,
                    "required_approval": False,
                },
                validation_rules=[
                    "must_have_tldr",
                    "must_have_anchor_key",
                    "must_have_purpose",
                    "must_have_implementation",
                    "should_have_cross_references",
                    "should_have_code_examples",
                ],
                lifecycle_rules={
                    "review_frequency": "quarterly",
                    "approval_required": False,
                    "change_notification": True,
                    "version_control": True,
                    "deprecation_notice": 60,
                },
                dependencies=["T1_core_authority"],
            ),
            TierLevel.TIER_3: TierDefinition(
                tier=TierLevel.TIER_3,
                name="Supporting Authority",
                description="Reference and utility documents that support higher-tier authorities",
                authority_level=1,
                required_sections=["TL;DR"],
                optional_sections=["ANCHOR_KEY", "Purpose", "Usage", "Examples", "Related Documents"],
                content_requirements={
                    "min_length": 100,
                    "max_length": 2000,
                    "required_cross_references": 0,
                    "required_code_examples": 0,
                    "required_validation": False,
                    "required_approval": False,
                },
                validation_rules=["must_have_tldr", "should_have_purpose", "should_have_usage_guidance"],
                lifecycle_rules={
                    "review_frequency": "annually",
                    "approval_required": False,
                    "change_notification": False,
                    "version_control": True,
                    "deprecation_notice": 30,
                },
                dependencies=["T2_implementation_guide"],
            ),
        }

    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load validation rules for t-t3 structure"""
        return {
            "must_have_tldr": {
                "type": "section_required",
                "section": "TL;DR",
                "severity": "error",
                "description": "Document must have a TL;DR section",
            },
            "must_have_anchor_key": {
                "type": "section_required",
                "section": "ANCHOR_KEY",
                "severity": "error",
                "description": "Document must have an ANCHOR_KEY section",
            },
            "must_have_role_pins": {
                "type": "section_required",
                "section": "ROLE_PINS",
                "severity": "error",
                "description": "Document must have a ROLE_PINS section",
            },
            "must_have_metadata": {
                "type": "section_required",
                "section": "METADATA",
                "severity": "error",
                "description": "Document must have a METADATA section",
            },
            "must_have_purpose": {
                "type": "section_required",
                "section": "Purpose",
                "severity": "error",
                "description": "Document must have a Purpose section",
            },
            "must_have_scope": {
                "type": "section_required",
                "section": "Scope",
                "severity": "error",
                "description": "Document must have a Scope section",
            },
            "must_have_authority_declaration": {
                "type": "content_required",
                "pattern": r"authority|authoritative|governance|standard",
                "severity": "error",
                "description": "Document must declare its authority",
            },
            "must_have_process_definition": {
                "type": "section_required",
                "section": "Process",
                "severity": "error",
                "description": "Document must define the process",
            },
            "must_have_validation_criteria": {
                "type": "section_required",
                "section": "Validation",
                "severity": "error",
                "description": "Document must define validation criteria",
            },
            "must_have_cross_references": {
                "type": "content_required",
                "pattern": r"@\w+",
                "min_count": 3,
                "severity": "error",
                "description": "Document must have cross-references",
            },
            "must_have_code_examples": {
                "type": "content_required",
                "pattern": r"```[\s\S]*?```",
                "min_count": 2,
                "severity": "error",
                "description": "Document must have code examples",
            },
            "should_have_cross_references": {
                "type": "content_required",
                "pattern": r"@\w+",
                "min_count": 1,
                "severity": "warning",
                "description": "Document should have cross-references",
            },
            "should_have_code_examples": {
                "type": "content_required",
                "pattern": r"```[\s\S]*?```",
                "min_count": 1,
                "severity": "warning",
                "description": "Document should have code examples",
            },
            "should_have_purpose": {
                "type": "section_required",
                "section": "Purpose",
                "severity": "warning",
                "description": "Document should have a Purpose section",
            },
            "should_have_usage_guidance": {
                "type": "section_required",
                "section": "Usage",
                "severity": "warning",
                "description": "Document should have usage guidance",
            },
        }

    def _load_authority_patterns(self) -> Dict[str, List[str]]:
        """Load authority patterns for content analysis"""
        return {
            "authority_indicators": [
                r"authority|authoritative|governance|standard|mandatory|required",
                r"policy|procedure|protocol|methodology|framework",
                r"best practice|guideline|recommendation|specification",
                r"core|essential|critical|primary|fundamental",
            ],
            "role_indicators": [
                r"developer|coder|programmer|engineer",
                r"admin|administrator|sysadmin|operator",
                r"user|end-user|consumer|stakeholder",
                r"architect|designer|planner|manager",
                r"tester|qa|quality|validator",
            ],
            "scope_indicators": [
                r"global|organization|company|enterprise",
                r"project|team|department|division",
                r"role|position|function|responsibility",
                r"context|domain|area|scope",
            ],
        }

    def init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS structure_validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score REAL NOT NULL,
                    errors TEXT,
                    warnings TEXT,
                    recommendations TEXT,
                    timestamp TEXT NOT NULL,
                    content_hash TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS authority_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    authority_scope TEXT NOT NULL,
                    authority_indicators TEXT,
                    role_pins TEXT,
                    cross_references TEXT,
                    dependencies TEXT,
                    timestamp TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tier_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tier TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    validation_rules TEXT,
                    lifecycle_rules TEXT,
                    created_at TEXT NOT NULL
                )
            """
            )

            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON structure_validations(file_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tier ON structure_validations(tier)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON structure_validations(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON structure_validations(timestamp)")

    def determine_tier(self, file_path: str) -> TierLevel:
        """Determine the appropriate tier for a document"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Analyze content characteristics
            content_length = len(content)
            authority_indicators = self._count_authority_indicators(content)
            cross_references = len(re.findall(r"@\w+", content))
            code_blocks = len(re.findall(r"```[\s\S]*?```", content))
            sections = self._extract_sections(content)

            # Tier determination logic
            if (
                content_length > 2000
                or authority_indicators > 5
                or cross_references > 5
                or code_blocks > 3
                or len(sections) > 8
            ):
                return TierLevel.TIER_1
            elif (
                content_length > 500
                or authority_indicators > 2
                or cross_references > 2
                or code_blocks > 1
                or len(sections) > 4
            ):
                return TierLevel.TIER_2
            else:
                return TierLevel.TIER_3

        except Exception as e:
            logger.error(f"Error determining tier for {file_path}: {e}")
            return TierLevel.TIER_3

    def _count_authority_indicators(self, content: str) -> int:
        """Count authority indicators in content"""
        count = 0
        content_lower = content.lower()

        for pattern in self.authority_patterns["authority_indicators"]:
            count += len(re.findall(pattern, content_lower, re.IGNORECASE))

        return count

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from content"""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split("\n"):
            if line.startswith("#"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line.strip("#").strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def validate_structure(self, file_path: str, tier: Optional[TierLevel] = None) -> StructureValidation:
        """Validate document structure against t-t3 requirements"""
        logger.info(f"Validating structure for {file_path}")

        if tier is None:
            tier = self.determine_tier(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Get tier definition
            tier_def = self.tier_definitions.get(tier)
            if not tier_def:
                raise ValueError(f"Unknown tier: {tier}")

            # Extract sections
            sections = self._extract_sections(content)

            # Validate against tier requirements
            errors = []
            warnings = []
            score = 100.0

            # Validate required sections
            for section in tier_def.required_sections:
                if section not in sections:
                    errors.append(f"Missing required section: {section}")
                    score -= 15.0

            # Validate optional sections
            for section in tier_def.optional_sections:
                if section not in sections:
                    warnings.append(f"Missing optional section: {section}")
                    score -= 5.0

            # Validate content requirements
            content_length = len(content)
            if content_length < tier_def.content_requirements["min_length"]:
                errors.append(
                    f"Content too short: {content_length} chars (min: {tier_def.content_requirements['min_length']})"
                )
                score -= 10.0
            elif content_length > tier_def.content_requirements["max_length"]:
                warnings.append(
                    f"Content too long: {content_length} chars (max: {tier_def.content_requirements['max_length']})"
                )
                score -= 5.0

            # Validate cross-references
            cross_refs = len(re.findall(r"@\w+", content))
            required_refs = tier_def.content_requirements["required_cross_references"]
            if cross_refs < required_refs:
                errors.append(f"Insufficient cross-references: {cross_refs} (required: {required_refs})")
                score -= 10.0

            # Validate code examples
            code_blocks = len(re.findall(r"```[\s\S]*?```", content))
            required_examples = tier_def.content_requirements["required_code_examples"]
            if code_blocks < required_examples:
                errors.append(f"Insufficient code examples: {code_blocks} (required: {required_examples})")
                score -= 10.0

            # Validate specific rules
            for rule_name in tier_def.validation_rules:
                rule = self.validation_rules.get(rule_name)
                if rule:
                    if not self._validate_rule(content, sections, rule):
                        if rule["severity"] == "error":
                            errors.append(rule["description"])
                            score -= 10.0
                        else:
                            warnings.append(rule["description"])
                            score -= 5.0

            # Generate recommendations
            recommendations = self._generate_recommendations(tier_def, sections, content)

            # Determine status
            if errors:
                status = ValidationStatus.INVALID
            elif warnings:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.VALID

            # Ensure score is within bounds
            score = max(0.0, min(100.0, score))

            validation = StructureValidation(
                file_path=file_path,
                tier=tier,
                status=status,
                score=score,
                errors=errors,
                warnings=warnings,
                recommendations=recommendations,
                timestamp=datetime.now(),
            )

            # Store validation result
            self._store_validation_result(validation)

            return validation

        except Exception as e:
            logger.error(f"Error validating structure for {file_path}: {e}")
            return StructureValidation(
                file_path=file_path,
                tier=tier or TierLevel.TIER_3,
                status=ValidationStatus.INVALID,
                score=0.0,
                errors=[f"Validation failed: {e}"],
                warnings=[],
                recommendations=["Fix validation errors and retry"],
                timestamp=datetime.now(),
            )

    def _validate_rule(self, content: str, sections: Dict[str, str], rule: Dict[str, Any]) -> bool:
        """Validate a specific rule"""
        rule_type = rule["type"]

        if rule_type == "section_required":
            return rule["section"] in sections

        elif rule_type == "content_required":
            pattern = rule["pattern"]
            matches = re.findall(pattern, content, re.IGNORECASE)
            min_count = rule.get("min_count", 1)
            return len(matches) >= min_count

        return True

    def _generate_recommendations(self, tier_def: TierDefinition, sections: Dict[str, str], content: str) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []

        # Missing sections
        missing_required = [s for s in tier_def.required_sections if s not in sections]
        if missing_required:
            recommendations.append(f"Add missing required sections: {', '.join(missing_required)}")

        missing_optional = [s for s in tier_def.optional_sections if s not in sections]
        if missing_optional:
            recommendations.append(f"Consider adding optional sections: {', '.join(missing_optional)}")

        # Content quality
        if len(content) < tier_def.content_requirements["min_length"]:
            recommendations.append(
                f"Increase content length to at least {tier_def.content_requirements['min_length']} characters"
            )

        # Cross-references
        cross_refs = len(re.findall(r"@\w+", content))
        if cross_refs < tier_def.content_requirements["required_cross_references"]:
            recommendations.append(
                f"Add more cross-references (current: {cross_refs}, required: {tier_def.content_requirements['required_cross_references']})"
            )

        # Code examples
        code_blocks = len(re.findall(r"```[\s\S]*?```", content))
        if code_blocks < tier_def.content_requirements["required_code_examples"]:
            recommendations.append(
                f"Add more code examples (current: {code_blocks}, required: {tier_def.content_requirements['required_code_examples']})"
            )

        # Authority indicators
        authority_count = self._count_authority_indicators(content)
        if authority_count < 2:
            recommendations.append("Add more authority indicators to clarify document purpose")

        return recommendations

    def _store_validation_result(self, validation: StructureValidation):
        """Store validation result in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO structure_validations
                    (file_path, tier, status, score, errors, warnings, recommendations, timestamp, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        validation.file_path,
                        validation.tier.value,
                        validation.status.value,
                        validation.score,
                        json.dumps(validation.errors),
                        json.dumps(validation.warnings),
                        json.dumps(validation.recommendations),
                        validation.timestamp.isoformat(),
                        self._calculate_content_hash(validation.file_path),
                    ),
                )

        except Exception as e:
            logger.error(f"Error storing validation result: {e}")

    def _calculate_content_hash(self, file_path: str) -> str:
        """Calculate content hash for change detection"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return ""

    def create_authority_mapping(self, file_path: str) -> AuthorityMapping:
        """Create authority mapping for a document"""
        logger.info(f"Creating authority mapping for {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Determine tier
            tier = self.determine_tier(file_path)

            # Extract authority indicators
            authority_indicators = self._extract_authority_indicators(content)

            # Determine authority scope
            authority_scope = self._determine_authority_scope(content)

            # Extract role pins
            role_pins = self._extract_role_pins(content)

            # Extract cross-references
            cross_references = re.findall(r"@\w+", content)

            # Determine dependencies
            dependencies = self._determine_dependencies(content, tier)

            mapping = AuthorityMapping(
                file_path=file_path,
                tier=tier,
                authority_scope=authority_scope,
                authority_indicators=authority_indicators,
                role_pins=role_pins,
                cross_references=cross_references,
                dependencies=dependencies,
                timestamp=datetime.now(),
            )

            # Store mapping
            self._store_authority_mapping(mapping)

            return mapping

        except Exception as e:
            logger.error(f"Error creating authority mapping for {file_path}: {e}")
            return AuthorityMapping(
                file_path=file_path,
                tier=TierLevel.TIER_3,
                authority_scope=AuthorityScope.CONTEXT,
                authority_indicators=[],
                role_pins=[],
                cross_references=[],
                dependencies=[],
                timestamp=datetime.now(),
            )

    def _extract_authority_indicators(self, content: str) -> List[str]:
        """Extract authority indicators from content"""
        indicators = []
        content_lower = content.lower()

        for pattern in self.authority_patterns["authority_indicators"]:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            indicators.extend(matches)

        return list(set(indicators))

    def _determine_authority_scope(self, content: str) -> AuthorityScope:
        """Determine authority scope from content"""
        content_lower = content.lower()

        # Check for global indicators
        if any(re.search(pattern, content_lower) for pattern in [r"global|organization|company|enterprise"]):
            return AuthorityScope.GLOBAL

        # Check for project indicators
        if any(re.search(pattern, content_lower) for pattern in [r"project|team|department|division"]):
            return AuthorityScope.PROJECT

        # Check for role indicators
        if any(re.search(pattern, content_lower) for pattern in [r"role|position|function|responsibility"]):
            return AuthorityScope.ROLE

        # Default to context
        return AuthorityScope.CONTEXT

    def _extract_role_pins(self, content: str) -> List[str]:
        """Extract role pins from content"""
        roles = []
        content_lower = content.lower()

        for pattern in self.authority_patterns["role_indicators"]:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            roles.extend(matches)

        return list(set(roles))

    def _determine_dependencies(self, content: str, tier: TierLevel) -> List[str]:
        """Determine dependencies for a document"""
        dependencies = []

        # Add tier-specific dependencies
        tier_def = self.tier_definitions.get(tier)
        if tier_def:
            dependencies.extend(tier_def.dependencies)

        # Add content-based dependencies
        cross_refs = re.findall(r"@\w+", content)
        dependencies.extend(cross_refs)

        return list(set(dependencies))

    def _store_authority_mapping(self, mapping: AuthorityMapping):
        """Store authority mapping in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO authority_mappings
                    (file_path, tier, authority_scope, authority_indicators, role_pins, cross_references, dependencies, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        mapping.file_path,
                        mapping.tier.value,
                        mapping.authority_scope.value,
                        json.dumps(mapping.authority_indicators),
                        json.dumps(mapping.role_pins),
                        json.dumps(mapping.cross_references),
                        json.dumps(mapping.dependencies),
                        mapping.timestamp.isoformat(),
                    ),
                )

        except Exception as e:
            logger.error(f"Error storing authority mapping: {e}")

    def analyze_directory(self, directory_path: str, file_pattern: str = "*.md") -> T3StructureAnalysis:
        """Analyze directory for t-t3 structure compliance"""
        logger.info(f"Analyzing directory for t-t3 structure: {directory_path}")

        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        # Find all matching files
        files = list(directory.rglob(file_pattern))
        logger.info(f"Found {len(files)} files to analyze")

        structure_validations = []
        authority_mappings = []

        for file_path in files:
            try:
                # Validate structure
                validation = self.validate_structure(str(file_path))
                structure_validations.append(validation)

                # Create authority mapping
                mapping = self.create_authority_mapping(str(file_path))
                authority_mappings.append(mapping)

            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")

        # Calculate statistics
        tier_distribution = Counter(validation.tier for validation in structure_validations)
        validation_scores = [validation.score for validation in structure_validations]

        validation_stats = {
            "average_score": sum(validation_scores) / len(validation_scores) if validation_scores else 0.0,
            "min_score": min(validation_scores) if validation_scores else 0.0,
            "max_score": max(validation_scores) if validation_scores else 0.0,
            "valid_count": len([v for v in structure_validations if v.status == ValidationStatus.VALID]),
            "warning_count": len([v for v in structure_validations if v.status == ValidationStatus.WARNING]),
            "invalid_count": len([v for v in structure_validations if v.status == ValidationStatus.INVALID]),
        }

        # Generate recommendations
        recommendations = self._generate_analysis_recommendations(structure_validations, authority_mappings)

        return T3StructureAnalysis(
            structure_validations=structure_validations,
            authority_mappings=authority_mappings,
            tier_distribution=dict(tier_distribution),
            validation_stats=validation_stats,
            recommendations=recommendations,
            timestamp=datetime.now(),
        )

    def _generate_analysis_recommendations(
        self, validations: List[StructureValidation], mappings: List[AuthorityMapping]
    ) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []

        # Structure validation recommendations
        invalid_docs = [v for v in validations if v.status == ValidationStatus.INVALID]
        if invalid_docs:
            recommendations.append(f"{len(invalid_docs)} documents have invalid structure - review and fix")

        warning_docs = [v for v in validations if v.status == ValidationStatus.WARNING]
        if warning_docs:
            recommendations.append(f"{len(warning_docs)} documents have warnings - consider improvements")

        # Tier distribution recommendations
        tier_counts = Counter(v.tier for v in validations)
        total_docs = len(validations)

        if tier_counts.get(TierLevel.TIER_1, 0) > total_docs * 0.3:
            recommendations.append("High proportion of Tier 1 documents - review if all are truly critical")

        if tier_counts.get(TierLevel.TIER_3, 0) > total_docs * 0.6:
            recommendations.append("High proportion of Tier 3 documents - consider consolidation opportunities")

        # Authority scope recommendations
        scope_counts = Counter(m.authority_scope for m in mappings)
        if scope_counts.get(AuthorityScope.GLOBAL, 0) > 10:
            recommendations.append("Many global authority documents - ensure proper governance")

        return recommendations

    def export_analysis(
        self, analysis: T3StructureAnalysis, output_dir: str = "artifacts/t3_structure"
    ) -> Dict[str, str]:
        """Export analysis results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = analysis.timestamp.strftime("%Y%m%d_%H%M%S")

        # Export detailed results
        results_file = output_path / f"t3_structure_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(
                {
                    "timestamp": analysis.timestamp.isoformat(),
                    "tier_distribution": {k.value: v for k, v in analysis.tier_distribution.items()},
                    "validation_stats": analysis.validation_stats,
                    "recommendations": analysis.recommendations,
                    "structure_validations": [
                        {
                            "file_path": v.file_path,
                            "tier": v.tier.value,
                            "status": v.status.value,
                            "score": v.score,
                            "errors": v.errors,
                            "warnings": v.warnings,
                            "recommendations": v.recommendations,
                            "timestamp": v.timestamp.isoformat(),
                        }
                        for v in analysis.structure_validations
                    ],
                    "authority_mappings": [
                        {
                            "file_path": m.file_path,
                            "tier": m.tier.value,
                            "authority_scope": m.authority_scope.value,
                            "authority_indicators": m.authority_indicators,
                            "role_pins": m.role_pins,
                            "cross_references": m.cross_references,
                            "dependencies": m.dependencies,
                            "timestamp": m.timestamp.isoformat(),
                        }
                        for m in analysis.authority_mappings
                    ],
                },
                f,
                indent=2,
            )

        # Export summary report
        summary_file = output_path / f"t3_structure_summary_{timestamp}.md"
        with open(summary_file, "w") as f:
            f.write("# t-t3 Structure Analysis Summary\n\n")
            f.write(f"**Analysis Date:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Tier Distribution\n\n")
            for tier, count in analysis.tier_distribution.items():
                percentage = (count / len(analysis.structure_validations)) * 100
                f.write(f"- **{tier.value}:** {count} documents ({percentage:.1f}%)\n")

            f.write("\n## Validation Statistics\n\n")
            for stat, value in analysis.validation_stats.items():
                if isinstance(value, float):
                    f.write(f"- **{stat.replace('_', ' ').title()}:** {value:.3f}\n")
                else:
                    f.write(f"- **{stat.replace('_', ' ').title()}:** {value}\n")

            f.write("\n## Recommendations\n\n")
            for i, rec in enumerate(analysis.recommendations, 1):
                f.write(f"{i}. {rec}\n")

            f.write("\n## Detailed Results\n\n")
            for validation in analysis.structure_validations:
                f.write(f"### {Path(validation.file_path).name}\n\n")
                f.write(f"- **Tier:** {validation.tier.value}\n")
                f.write(f"- **Status:** {validation.status.value}\n")
                f.write(f"- **Score:** {validation.score:.1f}\n")
                if validation.errors:
                    f.write(f"- **Errors:** {'; '.join(validation.errors)}\n")
                if validation.warnings:
                    f.write(f"- **Warnings:** {'; '.join(validation.warnings)}\n")
                f.write("\n")

        return {"results": str(results_file), "summary": str(summary_file)}


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="t-t3 Structure Design and Implementation System")
    parser.add_argument("path", help="File or directory path to analyze")
    parser.add_argument("--output", "-o", default="artifacts/t3_structure", help="Output directory for results")
    parser.add_argument("--pattern", "-p", default="*.md", help="File pattern to match (for directories)")
    parser.add_argument("--tier", "-t", help="Specific tier to validate against")

    args = parser.parse_args()

    # Initialize system
    t3_system = T3StructureDesign()

    path = Path(args.path)

    if path.is_file():
        # Analyze single file
        tier = None
        if args.tier:
            tier = TierLevel(args.tier)

        validation = t3_system.validate_structure(str(path), tier)
        mapping = t3_system.create_authority_mapping(str(path))

        print(f"Analysis Result for {path.name}:")
        print(f"- Tier: {validation.tier.value}")
        print(f"- Status: {validation.status.value}")
        print(f"- Score: {validation.score:.1f}")
        print(f"- Authority Scope: {mapping.authority_scope.value}")
        print(f"- Authority Indicators: {', '.join(mapping.authority_indicators)}")
        print(f"- Role Pins: {', '.join(mapping.role_pins)}")

        if validation.errors:
            print(f"- Errors: {'; '.join(validation.errors)}")
        if validation.warnings:
            print(f"- Warnings: {'; '.join(validation.warnings)}")
        if validation.recommendations:
            print(f"- Recommendations: {'; '.join(validation.recommendations)}")

    elif path.is_dir():
        # Analyze directory
        analysis = t3_system.analyze_directory(str(path), args.pattern)

        print("t-t3 Structure Analysis Complete:")
        print(f"- Files analyzed: {len(analysis.structure_validations)}")
        print(f"- Tier distribution: {analysis.tier_distribution}")
        print(f"- Average validation score: {analysis.validation_stats['average_score']:.1f}")
        print(f"- Valid documents: {analysis.validation_stats['valid_count']}")
        print(f"- Documents with warnings: {analysis.validation_stats['warning_count']}")
        print(f"- Invalid documents: {analysis.validation_stats['invalid_count']}")
        print(f"- Recommendations: {len(analysis.recommendations)}")

        # Export results
        output_files = t3_system.export_analysis(analysis, args.output)
        print("\nResults exported to:")
        for file_type, file_path in output_files.items():
            print(f"- {file_type}: {file_path}")

    else:
        print(f"Error: Path does not exist: {path}")


if __name__ == "__main__":
    main()
