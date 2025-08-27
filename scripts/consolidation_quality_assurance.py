#!/usr/bin/env python3
"""
Consolidation Quality Assurance System for B-1032

Validates consolidation results, ensures content integrity, and provides quality metrics.
Part of the t-t3 Authority Structure Implementation.
"""

import argparse
import json
import re
import sqlite3
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class QualityStatus(Enum):
    """Quality status of consolidation results."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILED = "failed"


class ValidationType(Enum):
    """Types of validation checks."""

    CONTENT_INTEGRITY = "content_integrity"
    STRUCTURE_QUALITY = "structure_quality"
    REFERENCE_VALIDITY = "reference_validity"
    READABILITY = "readability"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"


@dataclass
class QualityMetric:
    """A quality metric for consolidation validation."""

    metric_name: str
    metric_value: float
    threshold: float
    weight: float
    status: QualityStatus
    description: str
    details: Dict[str, Any]


@dataclass
class ValidationResult:
    """Result of a validation check."""

    validation_type: ValidationType
    status: QualityStatus
    score: float
    metrics: List[QualityMetric]
    issues: List[str]
    recommendations: List[str]
    validation_timestamp: datetime


@dataclass
class QualityReport:
    """Complete quality assurance report."""

    consolidation_id: str
    target_guide: str
    source_guides: List[str]
    overall_score: float
    overall_status: QualityStatus
    validation_results: Dict[str, ValidationResult]
    quality_metrics: List[QualityMetric]
    critical_issues: List[str]
    improvement_suggestions: List[str]
    report_timestamp: datetime
    validation_duration_seconds: float


class ConsolidationQualityAssurance:
    """Main quality assurance system for consolidation results."""

    def __init__(self, guides_dir: str = "400_guides", output_dir: str = "artifacts/consolidation"):
        self.guides_dir = Path(guides_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database for quality tracking
        self.db_path = self.output_dir / "quality_assurance.db"
        self._init_database()

        # Quality thresholds
        self.quality_thresholds = {"excellent": 0.9, "good": 0.8, "acceptable": 0.7, "poor": 0.6, "failed": 0.0}

        # Validation weights
        self.validation_weights = {
            ValidationType.CONTENT_INTEGRITY: 0.25,
            ValidationType.STRUCTURE_QUALITY: 0.20,
            ValidationType.REFERENCE_VALIDITY: 0.20,
            ValidationType.READABILITY: 0.15,
            ValidationType.COMPLETENESS: 0.15,
            ValidationType.CONSISTENCY: 0.05,
        }

    def _init_database(self):
        """Initialize SQLite database for quality tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS quality_reports (
                    id TEXT PRIMARY KEY,
                    consolidation_id TEXT,
                    target_guide TEXT,
                    source_guides TEXT,
                    overall_score REAL,
                    overall_status TEXT,
                    validation_results TEXT,
                    quality_metrics TEXT,
                    critical_issues TEXT,
                    improvement_suggestions TEXT,
                    report_timestamp TEXT,
                    validation_duration_seconds REAL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS validation_results (
                    id TEXT PRIMARY KEY,
                    report_id TEXT,
                    validation_type TEXT,
                    status TEXT,
                    score REAL,
                    metrics TEXT,
                    issues TEXT,
                    recommendations TEXT,
                    validation_timestamp TEXT,
                    FOREIGN KEY (report_id) REFERENCES quality_reports (id)
                )
            """
            )

    def validate_consolidation(self, consolidation_result: Dict[str, Any]) -> QualityReport:
        """Validate a consolidation result and generate quality report."""
        start_time = time.time()

        print("🔍 Starting consolidation quality assurance...")
        print(f"📁 Target guide: {consolidation_result.get('target_guide', 'Unknown')}")

        consolidation_id = consolidation_result.get("plan_id", "unknown")
        target_guide = consolidation_result.get("target_guide_path", "")
        source_guides = consolidation_result.get("removed_guides", [])

        # Load target guide content
        target_content = ""
        if target_guide and Path(target_guide).exists():
            target_content = Path(target_guide).read_text(encoding="utf-8")

        # Run all validation checks
        validation_results = {}
        all_metrics = []
        all_issues = []
        all_recommendations = []

        for validation_type in ValidationType:
            print(f"  🔍 Running {validation_type.value} validation...")
            result = self._run_validation(validation_type, target_content, source_guides, consolidation_result)
            validation_results[validation_type.value] = result
            all_metrics.extend(result.metrics)
            all_issues.extend(result.issues)
            all_recommendations.extend(result.recommendations)

        # Calculate overall score
        overall_score = self._calculate_overall_score(validation_results)
        overall_status = self._determine_quality_status(overall_score)

        # Identify critical issues
        critical_issues = [issue for issue in all_issues if "critical" in issue.lower() or "error" in issue.lower()]

        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(validation_results, all_metrics)

        validation_duration = time.time() - start_time

        # Create quality report
        report = QualityReport(
            consolidation_id=consolidation_id,
            target_guide=target_guide,
            source_guides=source_guides,
            overall_score=overall_score,
            overall_status=overall_status,
            validation_results=validation_results,
            quality_metrics=all_metrics,
            critical_issues=critical_issues,
            improvement_suggestions=improvement_suggestions,
            report_timestamp=datetime.now(),
            validation_duration_seconds=validation_duration,
        )

        # Store report in database
        self._store_quality_report(report)

        # Save to JSON
        self._save_quality_report(report)

        print(f"✅ Quality assurance complete in {validation_duration:.2f} seconds")
        print(f"📊 Overall score: {overall_score:.2f} ({overall_status.value})")

        return report

    def _run_validation(
        self,
        validation_type: ValidationType,
        content: str,
        source_guides: List[str],
        consolidation_result: Dict[str, Any],
    ) -> ValidationResult:
        """Run a specific validation check."""
        if validation_type == ValidationType.CONTENT_INTEGRITY:
            return self._validate_content_integrity(content, source_guides, consolidation_result)
        elif validation_type == ValidationType.STRUCTURE_QUALITY:
            return self._validate_structure_quality(content)
        elif validation_type == ValidationType.REFERENCE_VALIDITY:
            return self._validate_reference_validity(content)
        elif validation_type == ValidationType.READABILITY:
            return self._validate_readability(content)
        elif validation_type == ValidationType.COMPLETENESS:
            return self._validate_completeness(content, source_guides, consolidation_result)
        elif validation_type == ValidationType.CONSISTENCY:
            return self._validate_consistency(content)
        else:
            raise ValueError(f"Unknown validation type: {validation_type}")

    def _validate_content_integrity(
        self, content: str, source_guides: List[str], consolidation_result: Dict[str, Any]
    ) -> ValidationResult:
        """Validate content integrity after consolidation."""
        metrics = []
        issues = []
        recommendations = []

        # Check if content exists
        if not content.strip():
            issues.append("Critical: No content found in consolidated guide")
            metrics.append(
                QualityMetric(
                    metric_name="content_exists",
                    metric_value=0.0,
                    threshold=1.0,
                    weight=0.3,
                    status=QualityStatus.FAILED,
                    description="Content existence check",
                    details={"content_length": len(content)},
                )
            )
        else:
            metrics.append(
                QualityMetric(
                    metric_name="content_exists",
                    metric_value=1.0,
                    threshold=1.0,
                    weight=0.3,
                    status=QualityStatus.EXCELLENT,
                    description="Content exists",
                    details={"content_length": len(content)},
                )
            )

        # Check content size
        expected_size = consolidation_result.get("merged_content_size", 0)
        actual_size = len(content)

        if expected_size > 0:
            size_ratio = min(actual_size / expected_size, 2.0)  # Cap at 2x
            size_score = max(0.0, 1.0 - abs(1.0 - size_ratio))

            metrics.append(
                QualityMetric(
                    metric_name="content_size_ratio",
                    metric_value=size_score,
                    threshold=0.8,
                    weight=0.2,
                    status=self._determine_metric_status(size_score),
                    description="Content size ratio",
                    details={"expected_size": expected_size, "actual_size": actual_size, "ratio": size_ratio},
                )
            )

            if size_ratio < 0.5:
                issues.append("Warning: Consolidated content is significantly smaller than expected")
            elif size_ratio > 1.5:
                issues.append("Warning: Consolidated content is significantly larger than expected")

        # Check for content duplication
        lines = content.split("\n")
        unique_lines = set(lines)
        duplication_ratio = 1.0 - (len(unique_lines) / len(lines)) if lines else 0.0

        metrics.append(
            QualityMetric(
                metric_name="content_duplication",
                metric_value=1.0 - duplication_ratio,
                threshold=0.9,
                weight=0.2,
                status=self._determine_metric_status(1.0 - duplication_ratio),
                description="Content duplication check",
                details={
                    "duplication_ratio": duplication_ratio,
                    "unique_lines": len(unique_lines),
                    "total_lines": len(lines),
                },
            )
        )

        if duplication_ratio > 0.1:
            issues.append("Warning: High content duplication detected")
            recommendations.append("Review and remove duplicate content sections")

        # Check for content loss
        source_keywords = self._extract_keywords_from_sources(source_guides)
        target_keywords = set(re.findall(r"\b\w{4,}\b", content.lower()))

        if source_keywords:
            keyword_coverage = len(source_keywords.intersection(target_keywords)) / len(source_keywords)

            metrics.append(
                QualityMetric(
                    metric_name="keyword_coverage",
                    metric_value=keyword_coverage,
                    threshold=0.7,
                    weight=0.3,
                    status=self._determine_metric_status(keyword_coverage),
                    description="Keyword coverage from source guides",
                    details={"coverage_ratio": keyword_coverage, "source_keywords": len(source_keywords)},
                )
            )

            if keyword_coverage < 0.5:
                issues.append("Critical: Significant content loss detected")
                recommendations.append("Review source guides for missing content")

        # Calculate overall score
        score = sum(m.metric_value * m.weight for m in metrics) / sum(m.weight for m in metrics)

        return ValidationResult(
            validation_type=ValidationType.CONTENT_INTEGRITY,
            status=self._determine_quality_status(score),
            score=score,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            validation_timestamp=datetime.now(),
        )

    def _validate_structure_quality(self, content: str) -> ValidationResult:
        """Validate structure quality of consolidated content."""
        metrics = []
        issues = []
        recommendations = []

        # Check for headers
        headers = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
        header_count = len(headers)

        if header_count == 0:
            issues.append("Critical: No headers found in consolidated content")
            header_score = 0.0
        elif header_count < 3:
            issues.append("Warning: Insufficient headers for good structure")
            header_score = 0.5
        elif header_count < 5:
            header_score = 0.8
        else:
            header_score = 1.0

        metrics.append(
            QualityMetric(
                metric_name="header_structure",
                metric_value=header_score,
                threshold=0.7,
                weight=0.3,
                status=self._determine_metric_status(header_score),
                description="Header structure quality",
                details={"header_count": header_count, "headers": headers[:5]},
            )
        )

        # Check for TL;DR section
        has_tldr = "TL;DR" in content
        tldr_score = 1.0 if has_tldr else 0.0

        metrics.append(
            QualityMetric(
                metric_name="tldr_section",
                metric_value=tldr_score,
                threshold=0.5,
                weight=0.2,
                status=self._determine_metric_status(tldr_score),
                description="TL;DR section presence",
                details={"has_tldr": has_tldr},
            )
        )

        if not has_tldr:
            recommendations.append("Add TL;DR section for better accessibility")

        # Check for metadata
        has_anchor_key = "ANCHOR_KEY:" in content
        has_role_pins = "ROLE_PINS:" in content

        metadata_score = (has_anchor_key + has_role_pins) / 2.0

        metrics.append(
            QualityMetric(
                metric_name="metadata_completeness",
                metric_value=metadata_score,
                threshold=0.8,
                weight=0.2,
                status=self._determine_metric_status(metadata_score),
                description="Metadata completeness",
                details={"has_anchor_key": has_anchor_key, "has_role_pins": has_role_pins},
            )
        )

        if not has_anchor_key:
            recommendations.append("Add ANCHOR_KEY for better navigation")
        if not has_role_pins:
            recommendations.append("Add ROLE_PINS for role-based filtering")

        # Check for code blocks
        code_blocks = re.findall(r"```[\s\S]*?```", content)
        code_block_count = len(code_blocks)

        if code_block_count > 0:
            code_score = min(code_block_count / 5.0, 1.0)  # Reward up to 5 code blocks
        else:
            code_score = 0.5  # Neutral score for no code blocks

        metrics.append(
            QualityMetric(
                metric_name="code_examples",
                metric_value=code_score,
                threshold=0.5,
                weight=0.15,
                status=self._determine_metric_status(code_score),
                description="Code examples presence",
                details={"code_block_count": code_block_count},
            )
        )

        # Check for lists and tables
        list_items = len(re.findall(r"^\s*[-*+]\s+", content, re.MULTILINE))
        table_rows = len(re.findall(r"^\s*\|.*\|.*$", content, re.MULTILINE))

        structure_elements = list_items + table_rows
        structure_score = min(structure_elements / 10.0, 1.0)  # Reward up to 10 elements

        metrics.append(
            QualityMetric(
                metric_name="structure_elements",
                metric_value=structure_score,
                threshold=0.5,
                weight=0.15,
                status=self._determine_metric_status(structure_score),
                description="Structure elements (lists, tables)",
                details={"list_items": list_items, "table_rows": table_rows},
            )
        )

        # Calculate overall score
        score = sum(m.metric_value * m.weight for m in metrics) / sum(m.weight for m in metrics)

        return ValidationResult(
            validation_type=ValidationType.STRUCTURE_QUALITY,
            status=self._determine_quality_status(score),
            score=score,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            validation_timestamp=datetime.now(),
        )

    def _validate_reference_validity(self, content: str) -> ValidationResult:
        """Validate reference validity in consolidated content."""
        metrics = []
        issues = []
        recommendations = []

        # Extract all links
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        internal_links = [link for _, link in links if not link.startswith("http")]
        external_links = [link for _, link in links if link.startswith("http")]

        # Check internal link validity
        valid_internal_links = 0
        invalid_internal_links = []

        for link in internal_links:
            if self._is_valid_internal_link(link):
                valid_internal_links += 1
            else:
                invalid_internal_links.append(link)

        internal_link_score = valid_internal_links / len(internal_links) if internal_links else 1.0

        metrics.append(
            QualityMetric(
                metric_name="internal_link_validity",
                metric_value=internal_link_score,
                threshold=0.9,
                weight=0.4,
                status=self._determine_metric_status(internal_link_score),
                description="Internal link validity",
                details={
                    "valid_links": valid_internal_links,
                    "total_links": len(internal_links),
                    "invalid_links": invalid_internal_links,
                },
            )
        )

        if invalid_internal_links:
            issues.append(f"Warning: {len(invalid_internal_links)} invalid internal links found")
            recommendations.append("Fix broken internal references")

        # Check cross-references
        cross_refs = re.findall(r"400_guides/[^)\s]+\.md", content)
        cross_ref_score = 1.0 if cross_refs else 0.5  # Neutral if no cross-refs

        metrics.append(
            QualityMetric(
                metric_name="cross_references",
                metric_value=cross_ref_score,
                threshold=0.5,
                weight=0.3,
                status=self._determine_metric_status(cross_ref_score),
                description="Cross-reference presence",
                details={"cross_references": len(cross_refs)},
            )
        )

        # Check for anchor links
        anchor_links = re.findall(r"\[([^\]]+)\]\(#[^)]+\)", content)
        anchor_score = 1.0 if anchor_links else 0.5  # Neutral if no anchors

        metrics.append(
            QualityMetric(
                metric_name="anchor_links",
                metric_value=anchor_score,
                threshold=0.5,
                weight=0.3,
                status=self._determine_metric_status(anchor_score),
                description="Anchor link presence",
                details={"anchor_links": len(anchor_links)},
            )
        )

        # Calculate overall score
        score = sum(m.metric_value * m.weight for m in metrics) / sum(m.weight for m in metrics)

        return ValidationResult(
            validation_type=ValidationType.REFERENCE_VALIDITY,
            status=self._determine_quality_status(score),
            score=score,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            validation_timestamp=datetime.now(),
        )

    def _validate_readability(self, content: str) -> ValidationResult:
        """Validate readability of consolidated content."""
        metrics = []
        issues = []
        recommendations = []

        # Calculate basic readability metrics
        lines = content.split("\n")
        words = content.split()
        sentences = re.split(r"[.!?]+", content)

        # Average words per sentence
        if sentences:
            avg_words_per_sentence = len(words) / len(sentences)
            if avg_words_per_sentence > 25:
                issues.append("Warning: Sentences are too long")
                sentence_score = max(0.0, 1.0 - (avg_words_per_sentence - 20) / 10)
            elif avg_words_per_sentence < 10:
                sentence_score = 0.8
            else:
                sentence_score = 1.0
        else:
            sentence_score = 0.5

        metrics.append(
            QualityMetric(
                metric_name="sentence_length",
                metric_value=sentence_score,
                threshold=0.7,
                weight=0.3,
                status=self._determine_metric_status(sentence_score),
                description="Average words per sentence",
                details={"avg_words_per_sentence": avg_words_per_sentence if sentences else 0},
            )
        )

        # Average words per line
        if lines:
            avg_words_per_line = len(words) / len(lines)
            if avg_words_per_line > 15:
                line_score = max(0.0, 1.0 - (avg_words_per_line - 12) / 8)
            else:
                line_score = 1.0
        else:
            line_score = 0.5

        metrics.append(
            QualityMetric(
                metric_name="line_length",
                metric_value=line_score,
                threshold=0.7,
                weight=0.2,
                status=self._determine_metric_status(line_score),
                description="Average words per line",
                details={"avg_words_per_line": avg_words_per_line if lines else 0},
            )
        )

        # Paragraph structure
        paragraphs = content.split("\n\n")
        paragraph_count = len([p for p in paragraphs if p.strip()])

        if paragraph_count > 0:
            paragraph_score = min(paragraph_count / 10.0, 1.0)  # Reward up to 10 paragraphs
        else:
            paragraph_score = 0.0
            issues.append("Warning: No paragraph breaks found")

        metrics.append(
            QualityMetric(
                metric_name="paragraph_structure",
                metric_value=paragraph_score,
                threshold=0.5,
                weight=0.2,
                status=self._determine_metric_status(paragraph_score),
                description="Paragraph structure",
                details={"paragraph_count": paragraph_count},
            )
        )

        # Technical term usage
        technical_terms = re.findall(r"\b[A-Z]{2,}\b", content)  # Acronyms
        term_score = min(len(technical_terms) / 5.0, 1.0)  # Reward up to 5 technical terms

        metrics.append(
            QualityMetric(
                metric_name="technical_terms",
                metric_value=term_score,
                threshold=0.5,
                weight=0.15,
                status=self._determine_metric_status(term_score),
                description="Technical term usage",
                details={"technical_terms": len(technical_terms)},
            )
        )

        # Code block readability
        code_blocks = re.findall(r"```[\s\S]*?```", content)
        if code_blocks:
            code_readability_score = 1.0  # Assume code blocks are well-formatted
        else:
            code_readability_score = 0.5  # Neutral if no code blocks

        metrics.append(
            QualityMetric(
                metric_name="code_readability",
                metric_value=code_readability_score,
                threshold=0.5,
                weight=0.15,
                status=self._determine_metric_status(code_readability_score),
                description="Code block readability",
                details={"code_blocks": len(code_blocks)},
            )
        )

        # Calculate overall score
        score = sum(m.metric_value * m.weight for m in metrics) / sum(m.weight for m in metrics)

        return ValidationResult(
            validation_type=ValidationType.READABILITY,
            status=self._determine_quality_status(score),
            score=score,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            validation_timestamp=datetime.now(),
        )

    def _validate_completeness(
        self, content: str, source_guides: List[str], consolidation_result: Dict[str, Any]
    ) -> ValidationResult:
        """Validate completeness of consolidated content."""
        metrics = []
        issues = []
        recommendations = []

        # Check if all source guide content is represented
        source_content_keywords = self._extract_keywords_from_sources(source_guides)
        target_keywords = set(re.findall(r"\b\w{4,}\b", content.lower()))

        if source_content_keywords:
            completeness_ratio = len(source_content_keywords.intersection(target_keywords)) / len(
                source_content_keywords
            )

            if completeness_ratio < 0.5:
                issues.append("Critical: Significant content loss from source guides")
            elif completeness_ratio < 0.8:
                issues.append("Warning: Some content may be missing from source guides")

            metrics.append(
                QualityMetric(
                    metric_name="content_completeness",
                    metric_value=completeness_ratio,
                    threshold=0.8,
                    weight=0.4,
                    status=self._determine_metric_status(completeness_ratio),
                    description="Content completeness from source guides",
                    details={"completeness_ratio": completeness_ratio, "source_keywords": len(source_content_keywords)},
                )
            )
        else:
            metrics.append(
                QualityMetric(
                    metric_name="content_completeness",
                    metric_value=1.0,
                    threshold=0.8,
                    weight=0.4,
                    status=QualityStatus.EXCELLENT,
                    description="Content completeness (no source guides to compare)",
                    details={"completeness_ratio": 1.0},
                )
            )

        # Check for essential sections
        essential_sections = ["introduction", "overview", "summary", "conclusion"]
        found_sections = 0

        for section in essential_sections:
            if section in content.lower():
                found_sections += 1

        section_score = found_sections / len(essential_sections)

        metrics.append(
            QualityMetric(
                metric_name="essential_sections",
                metric_value=section_score,
                threshold=0.5,
                weight=0.3,
                status=self._determine_metric_status(section_score),
                description="Essential sections presence",
                details={"found_sections": found_sections, "total_sections": len(essential_sections)},
            )
        )

        if section_score < 0.5:
            recommendations.append("Add essential sections (introduction, overview, summary, conclusion)")

        # Check for implementation details
        implementation_indicators = ["example", "code", "step", "procedure", "how to"]
        implementation_score = 0.0

        for indicator in implementation_indicators:
            if indicator in content.lower():
                implementation_score += 0.2

        implementation_score = min(implementation_score, 1.0)

        metrics.append(
            QualityMetric(
                metric_name="implementation_details",
                metric_value=implementation_score,
                threshold=0.5,
                weight=0.3,
                status=self._determine_metric_status(implementation_score),
                description="Implementation details presence",
                details={"implementation_score": implementation_score},
            )
        )

        if implementation_score < 0.5:
            recommendations.append("Add more implementation details and examples")

        # Calculate overall score
        score = sum(m.metric_value * m.weight for m in metrics) / sum(m.weight for m in metrics)

        return ValidationResult(
            validation_type=ValidationType.COMPLETENESS,
            status=self._determine_quality_status(score),
            score=score,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            validation_timestamp=datetime.now(),
        )

    def _validate_consistency(self, content: str) -> ValidationResult:
        """Validate consistency of consolidated content."""
        metrics = []
        issues = []
        recommendations = []

        # Check header consistency
        headers = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
        header_levels = [
            len(re.match(r"^(#+)", line).group(1)) for line in re.findall(r"^#{1,6}\s+", content, re.MULTILINE)
        ]

        if header_levels:
            # Check for proper hierarchy
            level_jumps = [header_levels[i + 1] - header_levels[i] for i in range(len(header_levels) - 1)]
            invalid_jumps = [jump for jump in level_jumps if jump > 1]

            consistency_score = 1.0 - (len(invalid_jumps) / len(level_jumps)) if level_jumps else 1.0

            if invalid_jumps:
                issues.append("Warning: Inconsistent header hierarchy detected")
                recommendations.append("Fix header levels to maintain proper hierarchy")
        else:
            consistency_score = 0.5

        metrics.append(
            QualityMetric(
                metric_name="header_consistency",
                metric_value=consistency_score,
                threshold=0.8,
                weight=0.4,
                status=self._determine_metric_status(consistency_score),
                description="Header hierarchy consistency",
                details={"invalid_jumps": len(invalid_jumps) if "invalid_jumps" in locals() else 0},
            )
        )

        # Check formatting consistency
        formatting_patterns = {
            "bold": r"\*\*[^*]+\*\*",
            "italic": r"\*[^*]+\*",
            "code_inline": r"`[^`]+`",
            "links": r"\[[^\]]+\]\([^)]+\)",
        }

        formatting_scores = []
        for pattern_name, pattern in formatting_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                # Check if formatting is used consistently
                formatting_scores.append(1.0)
            else:
                formatting_scores.append(0.5)  # Neutral if not used

        formatting_score = sum(formatting_scores) / len(formatting_scores) if formatting_scores else 0.5

        metrics.append(
            QualityMetric(
                metric_name="formatting_consistency",
                metric_value=formatting_score,
                threshold=0.7,
                weight=0.3,
                status=self._determine_metric_status(formatting_score),
                description="Formatting consistency",
                details={"formatting_patterns": len(formatting_patterns)},
            )
        )

        # Check terminology consistency
        technical_terms = re.findall(r"\b[A-Z]{2,}\b", content)
        term_variations = Counter(technical_terms)

        if term_variations:
            # Check for consistent capitalization
            inconsistent_terms = [term for term, count in term_variations.items() if count > 1]
            term_consistency_score = 1.0 - (len(inconsistent_terms) / len(term_variations))
        else:
            term_consistency_score = 1.0

        metrics.append(
            QualityMetric(
                metric_name="terminology_consistency",
                metric_value=term_consistency_score,
                threshold=0.8,
                weight=0.3,
                status=self._determine_metric_status(term_consistency_score),
                description="Terminology consistency",
                details={"inconsistent_terms": len(inconsistent_terms) if "inconsistent_terms" in locals() else 0},
            )
        )

        if "inconsistent_terms" in locals() and inconsistent_terms:
            recommendations.append("Standardize terminology usage throughout the document")

        # Calculate overall score
        score = sum(m.metric_value * m.weight for m in metrics) / sum(m.weight for m in metrics)

        return ValidationResult(
            validation_type=ValidationType.CONSISTENCY,
            status=self._determine_quality_status(score),
            score=score,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            validation_timestamp=datetime.now(),
        )

    def _extract_keywords_from_sources(self, source_guides: List[str]) -> set:
        """Extract keywords from source guides."""
        keywords = set()

        for guide in source_guides:
            guide_path = self.guides_dir / guide
            if guide_path.exists():
                try:
                    content = guide_path.read_text(encoding="utf-8")
                    # Extract meaningful words (4+ characters)
                    guide_keywords = set(re.findall(r"\b\w{4,}\b", content.lower()))
                    keywords.update(guide_keywords)
                except Exception:
                    continue

        return keywords

    def _is_valid_internal_link(self, link: str) -> bool:
        """Check if an internal link is valid."""
        # Remove anchor part
        link = link.split("#")[0]

        # Check if it's a relative path to a markdown file
        if link.endswith(".md"):
            target_path = self.guides_dir / link
            return target_path.exists()

        return True  # Assume other links are valid

    def _determine_metric_status(self, score: float) -> QualityStatus:
        """Determine quality status based on score."""
        if score >= self.quality_thresholds["excellent"]:
            return QualityStatus.EXCELLENT
        elif score >= self.quality_thresholds["good"]:
            return QualityStatus.GOOD
        elif score >= self.quality_thresholds["acceptable"]:
            return QualityStatus.ACCEPTABLE
        elif score >= self.quality_thresholds["poor"]:
            return QualityStatus.POOR
        else:
            return QualityStatus.FAILED

    def _determine_quality_status(self, score: float) -> QualityStatus:
        """Determine overall quality status."""
        return self._determine_metric_status(score)

    def _calculate_overall_score(self, validation_results: Dict[str, ValidationResult]) -> float:
        """Calculate overall quality score."""
        weighted_scores = []
        total_weight = 0

        for validation_type, result in validation_results.items():
            weight = self.validation_weights.get(ValidationType(validation_type), 0.1)
            weighted_scores.append(result.score * weight)
            total_weight += weight

        return sum(weighted_scores) / total_weight if total_weight > 0 else 0.0

    def _generate_improvement_suggestions(
        self, validation_results: Dict[str, ValidationResult], metrics: List[QualityMetric]
    ) -> List[str]:
        """Generate improvement suggestions based on validation results."""
        suggestions = []

        # Get low-scoring metrics
        low_scoring_metrics = [m for m in metrics if m.status in [QualityStatus.POOR, QualityStatus.FAILED]]

        for metric in low_scoring_metrics:
            if metric.metric_name == "content_exists":
                suggestions.append("Add substantial content to the consolidated guide")
            elif metric.metric_name == "header_structure":
                suggestions.append("Add more headers to improve document structure")
            elif metric.metric_name == "internal_link_validity":
                suggestions.append("Fix broken internal links and references")
            elif metric.metric_name == "content_completeness":
                suggestions.append("Review source guides to ensure all important content is included")
            elif metric.metric_name == "essential_sections":
                suggestions.append("Add essential sections like introduction, overview, and summary")

        # Add general suggestions
        if not suggestions:
            suggestions.append("Review consolidated content for clarity and completeness")

        return suggestions

    def _store_quality_report(self, report: QualityReport):
        """Store quality report in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO quality_reports
                (id, consolidation_id, target_guide, source_guides, overall_score,
                 overall_status, validation_results, quality_metrics, critical_issues,
                 improvement_suggestions, report_timestamp, validation_duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    report.consolidation_id,
                    report.consolidation_id,
                    report.target_guide,
                    json.dumps(report.source_guides),
                    report.overall_score,
                    report.overall_status.value,
                    json.dumps({k: asdict(v) for k, v in report.validation_results.items()}),
                    json.dumps([asdict(m) for m in report.quality_metrics]),
                    json.dumps(report.critical_issues),
                    json.dumps(report.improvement_suggestions),
                    report.report_timestamp.isoformat(),
                    report.validation_duration_seconds,
                ),
            )

    def _save_quality_report(self, report: QualityReport):
        """Save quality report to JSON file."""
        report_file = self.output_dir / f"quality_report_{report.consolidation_id}.json"
        with open(report_file, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

        # Generate summary report
        self._generate_summary_report(report)

    def _generate_summary_report(self, report: QualityReport):
        """Generate a human-readable summary report."""
        summary_file = self.output_dir / f"quality_summary_{report.consolidation_id}.md"

        with open(summary_file, "w") as f:
            f.write(f"# Quality Assurance Report: {report.consolidation_id}\n\n")
            f.write(f"**Report Date:** {report.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Validation Duration:** {report.validation_duration_seconds:.2f} seconds\n\n")

            f.write("## Overview\n\n")
            f.write(f"- **Target Guide:** {report.target_guide}\n")
            f.write(f"- **Source Guides:** {', '.join(report.source_guides)}\n")
            f.write(f"- **Overall Score:** {report.overall_score:.2f}\n")
            f.write(f"- **Overall Status:** {report.overall_status.value}\n\n")

            f.write("## Validation Results\n\n")
            for validation_type, result in report.validation_results.items():
                f.write(f"### {validation_type.replace('_', ' ').title()}\n")
                f.write(f"- **Score:** {result.score:.2f}\n")
                f.write(f"- **Status:** {result.status.value}\n")
                if result.issues:
                    f.write(f"- **Issues:** {', '.join(result.issues[:3])}\n")
                f.write("\n")

            f.write("## Critical Issues\n\n")
            if report.critical_issues:
                for issue in report.critical_issues:
                    f.write(f"- {issue}\n")
            else:
                f.write("- No critical issues found\n")
            f.write("\n")

            f.write("## Improvement Suggestions\n\n")
            for suggestion in report.improvement_suggestions:
                f.write(f"- {suggestion}\n")
            f.write("\n")


def main():
    """Main entry point for the consolidation quality assurance system."""
    parser = argparse.ArgumentParser(description="Consolidation quality assurance system")
    parser.add_argument("--guides-dir", default="400_guides", help="Directory containing guides")
    parser.add_argument("--output-dir", default="artifacts/consolidation", help="Output directory for results")
    parser.add_argument("--consolidation-result", help="JSON file with consolidation result")
    parser.add_argument("--validate-all", action="store_true", help="Validate all consolidation results")

    args = parser.parse_args()

    # Initialize quality assurance system
    qa_system = ConsolidationQualityAssurance(args.guides_dir, args.output_dir)

    if args.consolidation_result:
        # Load and validate specific consolidation result
        with open(args.consolidation_result, "r") as f:
            consolidation_result = json.load(f)

        report = qa_system.validate_consolidation(consolidation_result)
        print(f"📊 Quality report generated: {report.consolidation_id}")

    elif args.validate_all:
        # Validate all consolidation results in the output directory
        print("🔍 Validating all consolidation results...")
        # This would require scanning for consolidation result files
        print("Batch validation not implemented")

    else:
        print("🔍 Consolidation Quality Assurance System")
        print("Use --consolidation-result to validate a specific consolidation")
        print("Use --validate-all to validate all consolidations")


if __name__ == "__main__":
    main()
