#!/usr/bin/env python3
"""
Simple Validation System for B-1032

Enforces basic quality gates for documentation size, freshness, and cross-reference integrity.
Part of the t-t3 Authority Structure Implementation.
"""

import argparse
import json
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects and other non-serializable types."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, tuple):
            return list(obj)
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


# Validation rules configuration
VALIDATION_RULES = {
    "tier_limits": {
        "tier_1": {"min_lines": 500, "max_lines": 1500},
        "tier_2": {"min_lines": 1000, "max_lines": 2000},
        "tier_3": {"min_lines": 0, "max_lines": None},  # Flexible
    },
    "freshness_threshold": 90,  # days
    "cross_reference_validation": True,
    "tldr_requirement": True,
    "anchor_key_requirement": True,
    "role_pins_requirement": True,
}


@dataclass
class ValidationResult:
    """Result of validation for a single guide."""

    file_path: str
    file_name: str
    tier: Optional[str]
    size_validation: Dict[str, Any]
    freshness_validation: Dict[str, Any]
    cross_reference_validation: Dict[str, Any]
    structure_validation: Dict[str, Any]
    overall_valid: bool
    validation_score: float
    recommendations: List[str]


@dataclass
class ValidationSummary:
    """Summary of validation results for all guides."""

    total_guides: int
    valid_guides: int
    invalid_guides: int
    average_score: float
    tier_distribution: Dict[str, int]
    validation_errors: Dict[str, List[str]]
    recommendations: List[str]
    validation_timestamp: datetime
    validation_duration_seconds: float


class DocumentationValidator:
    """Main validator class for documentation quality gates."""

    def __init__(self, guides_dir: str = "400_guides", output_dir: str = "artifacts/validation"):
        self.guides_dir = Path(guides_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database for validation history
        self.db_path = self.output_dir / "validation_history.db"
        self._init_database()

        # Load validation rules
        self.rules = VALIDATION_RULES

    def _init_database(self):
        """Initialize SQLite database for validation history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS validation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_guides INTEGER,
                    valid_guides INTEGER,
                    invalid_guides INTEGER,
                    average_score REAL,
                    validation_duration REAL,
                    results_json TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guide_validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    file_path TEXT,
                    file_name TEXT,
                    tier TEXT,
                    overall_valid BOOLEAN,
                    validation_score REAL,
                    size_validation TEXT,
                    freshness_validation TEXT,
                    cross_reference_validation TEXT,
                    structure_validation TEXT,
                    recommendations TEXT,
                    FOREIGN KEY (run_id) REFERENCES validation_runs (id)
                )
            """
            )

    def validate_all_guides(self) -> ValidationSummary:
        """Validate all guides in the 400_guides directory."""
        start_time = time.time()

        print("🔍 Starting documentation validation...")
        print(f"📁 Validating guides in: {self.guides_dir}")

        # Get all markdown files
        guide_files = list(self.guides_dir.glob("*.md"))
        print(f"📄 Found {len(guide_files)} guide files")

        # Validate each guide
        validation_results = []
        for file_path in guide_files:
            try:
                result = self._validate_single_guide(file_path)
                validation_results.append(result)
                status = "✅" if result.overall_valid else "❌"
                print(f"{status} Validated: {file_path.name} (Score: {result.validation_score:.2f})")
            except Exception as e:
                print(f"❌ Error validating {file_path.name}: {e}")

        # Generate validation summary
        validation_summary = self._generate_validation_summary(validation_results, start_time)

        # Store results in database
        self._store_validation_results(validation_summary, validation_results)

        # Save to JSON
        self._save_validation_results(validation_summary, validation_results)

        print(f"🎯 Validation complete in {validation_summary.validation_duration_seconds:.2f} seconds")
        print(f"📊 Results saved to: {self.output_dir}")

        return validation_summary

    def _validate_single_guide(self, file_path: Path) -> ValidationResult:
        """Validate a single guide file."""
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Basic metrics
        line_count = len(lines)

        # File metadata
        stat = file_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        days_since_modified = (datetime.now() - last_modified).days

        # Determine tier (placeholder - will be enhanced in Task 2.1)
        tier = self._determine_tier(line_count, content)

        # Run validations
        size_validation = self._validate_size(line_count, tier)
        freshness_validation = self._validate_freshness(days_since_modified)
        cross_reference_validation = self._validate_cross_references(content, file_path)
        structure_validation = self._validate_structure(content, lines)

        # Calculate overall validation score
        validation_score = self._calculate_validation_score(
            size_validation, freshness_validation, cross_reference_validation, structure_validation
        )

        # Determine if overall valid
        overall_valid = validation_score >= 0.7  # 70% threshold

        # Generate recommendations
        recommendations = self._generate_recommendations(
            size_validation, freshness_validation, cross_reference_validation, structure_validation
        )

        return ValidationResult(
            file_path=str(file_path),
            file_name=file_path.name,
            tier=tier,
            size_validation=size_validation,
            freshness_validation=freshness_validation,
            cross_reference_validation=cross_reference_validation,
            structure_validation=structure_validation,
            overall_valid=overall_valid,
            validation_score=validation_score,
            recommendations=recommendations,
        )

    def _determine_tier(self, line_count: int, content: str) -> Optional[str]:
        """Determine the tier of a guide based on size and content."""
        # This is a placeholder implementation - will be enhanced in Task 2.1
        if line_count < 200:
            return "tier_3"
        elif line_count < 500:
            return "tier_2"
        elif line_count < 1500:
            return "tier_1"
        else:
            return "tier_1"  # Very large guides default to tier 1

    def _validate_size(self, line_count: int, tier: Optional[str]) -> Dict[str, Any]:
        """Validate guide size against tier limits."""
        if not tier or tier not in self.rules["tier_limits"]:
            return {"valid": False, "error": "Unknown tier", "line_count": line_count, "tier": tier}

        limits = self.rules["tier_limits"][tier]
        min_lines = limits["min_lines"]
        max_lines = limits["max_lines"]

        valid = True
        error = None

        if line_count < min_lines:
            valid = False
            error = f"Too small: {line_count} lines (minimum {min_lines})"
        elif max_lines and line_count > max_lines:
            valid = False
            error = f"Too large: {line_count} lines (maximum {max_lines})"

        return {
            "valid": valid,
            "error": error,
            "line_count": line_count,
            "tier": tier,
            "min_lines": min_lines,
            "max_lines": max_lines,
        }

    def _validate_freshness(self, days_since_modified: int) -> Dict[str, Any]:
        """Validate guide freshness."""
        threshold = self.rules["freshness_threshold"]
        valid = days_since_modified <= threshold

        return {
            "valid": valid,
            "days_since_modified": days_since_modified,
            "threshold": threshold,
            "error": None if valid else f"Stale content: {days_since_modified} days old",
        }

    def _validate_cross_references(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Validate cross-references in the guide."""
        if not self.rules["cross_reference_validation"]:
            return {"valid": True, "error": None, "references": []}

        # Extract cross-references
        cross_refs = re.findall(r"400_guides/[^)\s]+\.md", content)

        # Check if referenced files exist
        valid_refs = []
        invalid_refs = []

        for ref in cross_refs:
            ref_path = self.guides_dir / Path(ref).name
            if ref_path.exists():
                valid_refs.append(ref)
            else:
                invalid_refs.append(ref)

        valid = len(invalid_refs) == 0

        return {
            "valid": valid,
            "error": None if valid else f"Invalid references: {invalid_refs}",
            "total_references": len(cross_refs),
            "valid_references": len(valid_refs),
            "invalid_references": len(invalid_refs),
            "invalid_refs": invalid_refs,
        }

    def _validate_structure(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """Validate guide structure and required elements."""
        structure_errors = []

        # Check for TL;DR section
        if self.rules["tldr_requirement"] and not any("TL;DR" in line for line in lines):
            structure_errors.append("Missing TL;DR section")

        # Check for anchor key
        if self.rules["anchor_key_requirement"] and not any("ANCHOR_KEY:" in line for line in lines):
            structure_errors.append("Missing ANCHOR_KEY")

        # Check for role pins
        if self.rules["role_pins_requirement"] and not any("ROLE_PINS:" in line for line in lines):
            structure_errors.append("Missing ROLE_PINS")

        # Check for headings
        headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
        if len(headings) < 2:
            structure_errors.append("Insufficient headings (minimum 2)")

        valid = len(structure_errors) == 0

        return {
            "valid": valid,
            "errors": structure_errors,
            "has_tldr": any("TL;DR" in line for line in lines),
            "has_anchor_key": any("ANCHOR_KEY:" in line for line in lines),
            "has_role_pins": any("ROLE_PINS:" in line for line in lines),
            "heading_count": len(headings),
        }

    def _calculate_validation_score(
        self,
        size_validation: Dict[str, Any],
        freshness_validation: Dict[str, Any],
        cross_reference_validation: Dict[str, Any],
        structure_validation: Dict[str, Any],
    ) -> float:
        """Calculate overall validation score."""
        score = 0.0
        total_weight = 0.0

        # Size validation (30% weight)
        weight = 0.3
        total_weight += weight
        if size_validation["valid"]:
            score += weight

        # Freshness validation (20% weight)
        weight = 0.2
        total_weight += weight
        if freshness_validation["valid"]:
            score += weight

        # Cross-reference validation (25% weight)
        weight = 0.25
        total_weight += weight
        if cross_reference_validation["valid"]:
            score += weight

        # Structure validation (25% weight)
        weight = 0.25
        total_weight += weight
        if structure_validation["valid"]:
            score += weight

        return score / total_weight if total_weight > 0 else 0.0

    def _generate_recommendations(
        self,
        size_validation: Dict[str, Any],
        freshness_validation: Dict[str, Any],
        cross_reference_validation: Dict[str, Any],
        structure_validation: Dict[str, Any],
    ) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        # Size recommendations
        if not size_validation["valid"]:
            if size_validation["error"] and "Too small" in size_validation["error"]:
                recommendations.append("Expand content to meet minimum size requirement")
            elif size_validation["error"] and "Too large" in size_validation["error"]:
                recommendations.append("Consider breaking down into smaller, focused guides")

        # Freshness recommendations
        if not freshness_validation["valid"]:
            recommendations.append("Update content to ensure freshness")

        # Cross-reference recommendations
        if not cross_reference_validation["valid"]:
            recommendations.append("Fix invalid cross-references")

        # Structure recommendations
        if not structure_validation["valid"]:
            for error in structure_validation["errors"]:
                recommendations.append(f"Add {error.lower()}")

        return recommendations

    def _generate_validation_summary(
        self, validation_results: List[ValidationResult], start_time: float
    ) -> ValidationSummary:
        """Generate validation summary for all guides."""
        total_guides = len(validation_results)
        valid_guides = sum(1 for r in validation_results if r.overall_valid)
        invalid_guides = total_guides - valid_guides

        # Calculate average score
        total_score = sum(r.validation_score for r in validation_results)
        average_score = total_score / total_guides if total_guides > 0 else 0.0

        # Tier distribution
        tier_distribution = defaultdict(int)
        for result in validation_results:
            tier = result.tier or "unknown"
            tier_distribution[tier] += 1

        # Collect validation errors by type
        validation_errors = defaultdict(list)
        for result in validation_results:
            if not result.size_validation["valid"]:
                validation_errors["size"].append(result.file_name)
            if not result.freshness_validation["valid"]:
                validation_errors["freshness"].append(result.file_name)
            if not result.cross_reference_validation["valid"]:
                validation_errors["cross_references"].append(result.file_name)
            if not result.structure_validation["valid"]:
                validation_errors["structure"].append(result.file_name)

        # Generate overall recommendations
        recommendations = []
        if validation_errors["size"]:
            recommendations.append(f"Fix size issues in {len(validation_errors['size'])} guides")
        if validation_errors["freshness"]:
            recommendations.append(f"Update {len(validation_errors['freshness'])} stale guides")
        if validation_errors["cross_references"]:
            recommendations.append(f"Fix cross-references in {len(validation_errors['cross_references'])} guides")
        if validation_errors["structure"]:
            recommendations.append(f"Improve structure in {len(validation_errors['structure'])} guides")

        validation_duration = time.time() - start_time

        return ValidationSummary(
            total_guides=total_guides,
            valid_guides=valid_guides,
            invalid_guides=invalid_guides,
            average_score=average_score,
            tier_distribution=dict(tier_distribution),
            validation_errors=dict(validation_errors),
            recommendations=recommendations,
            validation_timestamp=datetime.now(),
            validation_duration_seconds=validation_duration,
        )

    def _store_validation_results(
        self, validation_summary: ValidationSummary, validation_results: List[ValidationResult]
    ):
        """Store validation results in SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            # Store main validation run
            cursor = conn.execute(
                """
                INSERT INTO validation_runs
                (timestamp, total_guides, valid_guides, invalid_guides, average_score, validation_duration, results_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    validation_summary.validation_timestamp.isoformat(),
                    validation_summary.total_guides,
                    validation_summary.valid_guides,
                    validation_summary.invalid_guides,
                    validation_summary.average_score,
                    validation_summary.validation_duration_seconds,
                    json.dumps(asdict(validation_summary), cls=CustomJSONEncoder),
                ),
            )
            run_id = cursor.lastrowid  # cspell:ignore lastrowid

            # Store individual guide validations
            for result in validation_results:
                conn.execute(
                    """
                    INSERT INTO guide_validations
                    (run_id, file_path, file_name, tier, overall_valid, validation_score,
                     size_validation, freshness_validation, cross_reference_validation,
                     structure_validation, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        run_id,
                        result.file_path,
                        result.file_name,
                        result.tier,
                        result.overall_valid,
                        result.validation_score,
                        json.dumps(result.size_validation),
                        json.dumps(result.freshness_validation),
                        json.dumps(result.cross_reference_validation),
                        json.dumps(result.structure_validation),
                        json.dumps(result.recommendations),
                    ),
                )

    def _save_validation_results(
        self, validation_summary: ValidationSummary, validation_results: List[ValidationResult]
    ):
        """Save validation results to JSON files."""
        # Save main validation summary
        summary_file = self.output_dir / "validation_summary.json"
        with open(summary_file, "w") as f:
            json.dump(asdict(validation_summary), f, indent=2, cls=CustomJSONEncoder)

        # Save individual validation results
        results_file = self.output_dir / "validation_results.json"
        with open(results_file, "w") as f:
            json.dump([asdict(result) for result in validation_results], f, indent=2, cls=CustomJSONEncoder)

        # Generate summary report
        self._generate_summary_report(validation_summary, validation_results)

    def _generate_summary_report(
        self, validation_summary: ValidationSummary, validation_results: List[ValidationResult]
    ):
        """Generate a human-readable summary report."""
        report_file = self.output_dir / "validation_summary.md"

        with open(report_file, "w") as f:
            f.write("# Documentation Validation Summary\n\n")
            f.write(f"**Validation Date:** {validation_summary.validation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Validation Duration:** {validation_summary.validation_duration_seconds:.2f} seconds\n\n")

            f.write("## Overview\n\n")
            f.write(f"- **Total Guides:** {validation_summary.total_guides}\n")
            f.write(f"- **Valid Guides:** {validation_summary.valid_guides}\n")
            f.write(f"- **Invalid Guides:** {validation_summary.invalid_guides}\n")
            f.write(
                f"- **Success Rate:** {(validation_summary.valid_guides/validation_summary.total_guides*100):.1f}%\n"
            )
            f.write(f"- **Average Score:** {validation_summary.average_score:.2f}\n\n")

            f.write("## Tier Distribution\n\n")
            for tier, count in validation_summary.tier_distribution.items():
                f.write(f"- **{tier}:** {count} guides\n")
            f.write("\n")

            f.write("## Validation Errors by Type\n\n")
            for error_type, files in validation_summary.validation_errors.items():
                f.write(f"- **{error_type.title()}:** {len(files)} guides\n")
                for file in files[:5]:  # Show first 5 files
                    f.write(f"  - {file}\n")
                if len(files) > 5:
                    f.write(f"  - ... and {len(files) - 5} more\n")
                f.write("\n")

            f.write("## Recommendations\n\n")
            for i, recommendation in enumerate(validation_summary.recommendations, 1):
                f.write(f"{i}. {recommendation}\n")
            f.write("\n")

            f.write("## Top Issues\n\n")
            # Show guides with lowest scores
            sorted_results = sorted(validation_results, key=lambda x: x.validation_score)
            f.write("**Guides with lowest validation scores:**\n")
            for result in sorted_results[:10]:
                f.write(f"- {result.file_name}: {result.validation_score:.2f}\n")
                for rec in result.recommendations[:2]:  # Show first 2 recommendations
                    f.write(f"  - {rec}\n")

    def validate_single_guide(self, file_path: str) -> ValidationResult:
        """Validate a single guide file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Guide file not found: {file_path}")

        return self._validate_single_guide(path)

    def get_validation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get validation history from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT timestamp, total_guides, valid_guides, invalid_guides,
                       average_score, validation_duration
                FROM validation_runs
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

            return [
                {
                    "timestamp": row[0],
                    "total_guides": row[1],
                    "valid_guides": row[2],
                    "invalid_guides": row[3],
                    "average_score": row[4],
                    "validation_duration": row[5],
                }
                for row in cursor.fetchall()
            ]


def main():
    """Main entry point for the documentation validator."""
    parser = argparse.ArgumentParser(description="Validate documentation quality")
    parser.add_argument("--guides-dir", default="400_guides", help="Directory containing guides")
    parser.add_argument("--output-dir", default="artifacts/validation", help="Output directory for results")
    parser.add_argument("--validate-all", action="store_true", help="Run full validation")
    parser.add_argument("--validate-file", help="Validate a single file")
    parser.add_argument("--show-history", action="store_true", help="Show validation history")
    parser.add_argument("--history-limit", type=int, default=10, help="Number of history entries to show")

    args = parser.parse_args()

    # Initialize validator
    validator = DocumentationValidator(args.guides_dir, args.output_dir)

    if args.validate_all:
        print("🚀 Starting comprehensive documentation validation...")
        result = validator.validate_all_guides()
        print(f"📊 Validation results saved to: {validator.output_dir}")
        return result

    elif args.validate_file:
        print(f"🔍 Validating single file: {args.validate_file}")
        result = validator.validate_single_guide(args.validate_file)
        print(f"✅ Validation complete for {args.validate_file}")
        print(f"Score: {result.validation_score:.2f}")
        print(f"Valid: {result.overall_valid}")
        return result

    elif args.show_history:
        print("📋 Validation History:")
        history = validator.get_validation_history(args.history_limit)
        for entry in history:
            print(
                f"  {entry['timestamp']}: {entry['valid_guides']}/{entry['total_guides']} valid (Score: {entry['average_score']:.2f})"
            )
        return history

    else:
        print("🔍 Running quick validation...")
        result = validator.validate_all_guides()
        return result


if __name__ == "__main__":
    main()
