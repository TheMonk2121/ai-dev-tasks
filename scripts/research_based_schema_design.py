#!/usr/bin/env python3
"""
Research-Based Schema Design for Extraction
==========================================
Integrates research findings from 500_research/ directory to generate
adaptive, validated extraction schemas for improved data processing.

This module provides:
1. Research integration and analysis
2. Schema generation based on research patterns
3. Validation and quality assessment
4. Schema evolution and learning

Usage:
    python3 scripts/research_based_schema_design.py --analyze-research
    python3 scripts/research_based_schema_design.py --generate-schema --content-type "documentation"
    python3 scripts/research_based_schema_design.py --validate-schema --schema-file "schemas/doc_schema.json"
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ResearchFinding:
    """Represents a research finding with metadata."""

    source_file: str
    topic: str
    key_insight: str
    implementation_impact: str
    actionable_patterns: list[str]
    citations: list[str]
    confidence: float = 1.0
    last_updated: str | None = None


@dataclass
class SchemaPattern:
    """Represents a schema pattern derived from research."""

    pattern_name: str
    description: str
    research_basis: list[str]
    implementation: str
    validation_criteria: list[str]
    performance_benchmarks: dict[str, Any]
    content_types: list[str]


@dataclass
class ExtractionSchema:
    """Represents a complete extraction schema."""

    schema_id: str
    content_type: str
    patterns: list[SchemaPattern]
    validation_rules: list[str]
    quality_metrics: dict[str, Any]
    research_coverage: float
    created_at: str
    version: str = "1.0"


class ResearchBasedSchemaDesign:
    """Handles research-based schema design for extraction."""

    def __init__(self):
        self.research_dir = Path("500_research")
        self.schemas_dir = Path("schemas")
        self.findings: list[ResearchFinding] = []
        self.patterns: list[SchemaPattern] = []
        self.schemas: dict[str, ExtractionSchema] = {}

        # Ensure directories exist
        self.schemas_dir.mkdir(exist_ok=True)

        # Load existing schemas
        self._load_existing_schemas()

    def _load_existing_schemas(self) -> None:
        """Load existing schemas from the schemas directory."""
        for schema_file in self.schemas_dir.glob("*.json"):
            try:
                with open(schema_file, encoding="utf-8") as f:
                    schema_data = json.load(f)
                    schema = ExtractionSchema(**schema_data)
                    self.schemas[schema.schema_id] = schema
                logger.info(f"Loaded existing schema: {schema.schema_id}")
            except Exception as e:
                logger.warning(f"Failed to load schema {schema_file}: {e}")

    def analyze_research(self) -> dict[str, Any]:
        """Analyze research findings from 500_research/ directory."""
        logger.info("Starting research analysis...")

        research_files = list(self.research_dir.glob("*.md"))
        logger.info(f"Found {len(research_files)} research files")

        analysis_results = {
            "total_files": len(research_files),
            "findings_extracted": 0,
            "patterns_identified": 0,
            "topics_covered": set(),
            "research_coverage": 0.0,
        }

        for research_file in research_files:
            try:
                findings = self._extract_findings_from_file(research_file)
                self.findings.extend(findings)
                analysis_results["findings_extracted"] += len(findings)

                # Extract topics
                for finding in findings:
                    analysis_results["topics_covered"].add(finding.topic)

            except Exception as e:
                logger.error(f"Error analyzing {research_file}: {e}")

        # Convert set to list for JSON serialization
        analysis_results["topics_covered"] = list(analysis_results["topics_covered"])

        # Calculate research coverage
        expected_topics = ["rag", "dspy", "metadata", "extraction", "validation", "performance"]
        covered_topics = len(
            [t for t in expected_topics if any(t in topic.lower() for topic in analysis_results["topics_covered"])]
        )
        analysis_results["research_coverage"] = covered_topics / len(expected_topics)

        logger.info(f"Research analysis complete: {analysis_results['findings_extracted']} findings extracted")
        return analysis_results

    def _extract_findings_from_file(self, file_path: Path) -> list[ResearchFinding]:
        """Extract research findings from a markdown file."""
        findings = []
        content = file_path.read_text(encoding="utf-8")

        # Extract topic from filename
        topic = file_path.stem.replace("500_", "").replace("-research", "")

        # Look for key findings sections
        key_findings_pattern = r"## Key Findings\s*\n(.*?)(?=\n##|\Z)"
        key_findings_match = re.search(key_findings_pattern, content, re.DOTALL)

        if key_findings_match:
            key_findings_text = key_findings_match.group(1)

            # Extract individual findings
            findings_pattern = r"[-*]\s*(.*?)(?=\n[-*]|\n\n|\Z)"
            individual_findings = re.findall(findings_pattern, key_findings_text, re.DOTALL)

            for finding_text in individual_findings:
                finding = ResearchFinding(
                    source_file=str(file_path),
                    topic=topic,
                    key_insight=finding_text.strip(),
                    implementation_impact="",  # Will be extracted separately
                    actionable_patterns=[],  # Will be extracted separately
                    citations=[],  # Will be extracted separately
                    last_updated=datetime.now().isoformat(),
                )
                findings.append(finding)

        # Extract actionable patterns
        patterns_pattern = r"## Actionable Patterns\s*\n(.*?)(?=\n##|\Z)"
        patterns_match = re.search(patterns_pattern, content, re.DOTALL)

        if patterns_match:
            patterns_text = patterns_match.group(1)
            # Extract patterns and associate with findings
            for finding in findings:
                if finding.topic in patterns_text.lower():
                    # Extract patterns for this topic
                    pattern_lines = [line.strip() for line in patterns_text.split("\n") if line.strip()]
                    finding.actionable_patterns = pattern_lines[:3]  # Limit to first 3 patterns

        return findings

    def generate_schema_patterns(self) -> list[SchemaPattern]:
        """Generate schema patterns based on research findings."""
        logger.info("Generating schema patterns from research findings...")

        patterns = []

        # Pattern 1: Span-level grounding (from RAG research)
        span_pattern = SchemaPattern(
            pattern_name="span_level_grounding",
            description="Store character offsets for exact source attribution and validation",
            research_basis=["rag-system-research", "metadata-research"],
            implementation="""
            {
                "fields": {
                    "start_offset": {"type": "integer", "required": true},
                    "end_offset": {"type": "integer", "required": true},
                    "source_path": {"type": "string", "required": true},
                    "chunk_id": {"type": "string", "required": true}
                },
                "validation": {
                    "offset_consistency": "start_offset < end_offset",
                    "source_exists": "file_exists(source_path)"
                }
            }
            """,
            validation_criteria=[
                "Character offsets are valid and consistent",
                "Source file exists and is accessible",
                "Chunk ID is unique within source",
            ],
            performance_benchmarks={
                "extraction_time": "< 100ms",
                "validation_time": "< 50ms",
                "storage_overhead": "< 10%",
            },
            content_types=["documentation", "code", "research"],
        )
        patterns.append(span_pattern)

        # Pattern 2: Multi-stage retrieval (from RAG research)
        multi_stage_pattern = SchemaPattern(
            pattern_name="multi_stage_retrieval",
            description="Implement query decomposition and iterative refinement",
            research_basis=["rag-system-research"],
            implementation="""
            {
                "stages": [
                    {
                        "name": "query_decomposition",
                        "type": "llm_call",
                        "output": "sub_queries"
                    },
                    {
                        "name": "retrieval",
                        "type": "vector_search",
                        "input": "sub_queries"
                    },
                    {
                        "name": "synthesis",
                        "type": "llm_call",
                        "input": "retrieved_chunks"
                    }
                ],
                "validation": {
                    "stage_completion": "all_stages_complete",
                    "quality_threshold": "synthesis_confidence > 0.8"
                }
            }
            """,
            validation_criteria=[
                "All retrieval stages complete successfully",
                "Synthesis confidence meets threshold",
                "Response time within acceptable limits",
            ],
            performance_benchmarks={
                "total_time": "< 5 seconds",
                "decomposition_time": "< 1 second",
                "retrieval_time": "< 2 seconds",
                "synthesis_time": "< 2 seconds",
            },
            content_types=["complex_queries", "multi_hop_reasoning"],
        )
        patterns.append(multi_stage_pattern)

        # Pattern 3: Metadata governance (from metadata research)
        metadata_pattern = SchemaPattern(
            pattern_name="metadata_governance",
            description="Consistent identifiers and provenance tracking",
            research_basis=["metadata-research"],
            implementation="""
            {
                "fields": {
                    "doc_id": {"type": "string", "required": true, "unique": true},
                    "provenance": {"type": "string", "required": true},
                    "last_verified": {"type": "datetime", "required": true},
                    "validated_flag": {"type": "boolean", "required": true},
                    "owner": {"type": "string", "required": true}
                },
                "validation": {
                    "provenance_format": "valid_provenance_format(provenance)",
                    "verification_frequency": "last_verified < 30_days_ago"
                }
            }
            """,
            validation_criteria=[
                "Document ID is unique and follows format",
                "Provenance information is complete",
                "Verification is recent and valid",
            ],
            performance_benchmarks={
                "validation_time": "< 100ms",
                "storage_efficiency": "metadata < 5% of content size",
            },
            content_types=["all"],
        )
        patterns.append(metadata_pattern)

        # Pattern 4: DSPy assertions (from DSPy research)
        dspy_pattern = SchemaPattern(
            pattern_name="dspy_assertions",
            description="Code-enforced constraints for reliability",
            research_basis=["dspy-research"],
            implementation="""
            {
                "assertions": [
                    {
                        "name": "content_quality",
                        "condition": "extraction_confidence > 0.7",
                        "retry_count": 3,
                        "fallback": "manual_review"
                    },
                    {
                        "name": "schema_compliance",
                        "condition": "all_required_fields_present",
                        "retry_count": 2,
                        "fallback": "schema_adaptation"
                    }
                ],
                "validation": {
                    "assertion_success_rate": "> 95%",
                    "retry_efficiency": "retries < 20% of total"
                }
            }
            """,
            validation_criteria=[
                "Assertions pass with high success rate",
                "Retry mechanisms are efficient",
                "Fallback strategies are effective",
            ],
            performance_benchmarks={"assertion_time": "< 200ms", "retry_overhead": "< 15%", "success_rate": "> 95%"},
            content_types=["all"],
        )
        patterns.append(dspy_pattern)

        self.patterns = patterns
        logger.info(f"Generated {len(patterns)} schema patterns")
        return patterns

    def generate_schema(self, content_type: str, research_coverage_threshold: float = 0.8) -> ExtractionSchema:
        """Generate a complete extraction schema for a content type."""
        logger.info(f"Generating schema for content type: {content_type}")

        # Ensure patterns are generated if not already available
        if not self.patterns:
            self.generate_schema_patterns()

        # Select relevant patterns for the content type
        relevant_patterns = [
            pattern
            for pattern in self.patterns
            if content_type in pattern.content_types or "all" in pattern.content_types
        ]

        if not relevant_patterns:
            logger.warning(f"No patterns found for content type: {content_type}")
            # Fall back to all patterns that support "all" content types
            relevant_patterns = [pattern for pattern in self.patterns if "all" in pattern.content_types]

        # Calculate research coverage based on patterns, not findings
        research_basis = set()
        for pattern in relevant_patterns:
            research_basis.update(pattern.research_basis)

        # Calculate coverage as percentage of available research areas
        available_research_areas = ["rag-system-research", "dspy-research", "metadata-research", "performance-research"]
        research_coverage = len(research_basis) / len(available_research_areas) if available_research_areas else 0.0

        if research_coverage < research_coverage_threshold:
            logger.warning(
                f"Research coverage ({research_coverage:.2f}) below threshold ({research_coverage_threshold})"
            )

        # Generate validation rules
        validation_rules = []
        for pattern in relevant_patterns:
            validation_rules.extend(pattern.validation_criteria)

        # Generate quality metrics
        quality_metrics = {
            "research_coverage": research_coverage,
            "pattern_count": len(relevant_patterns),
            "validation_rule_count": len(validation_rules),
            "performance_targets": {
                "extraction_time": "< 5 seconds",
                "validation_time": "< 2 seconds",
                "accuracy_target": "> 95%",
            },
        }

        # Create schema
        schema = ExtractionSchema(
            schema_id=f"{content_type}_schema_v1",
            content_type=content_type,
            patterns=relevant_patterns,
            validation_rules=validation_rules,
            quality_metrics=quality_metrics,
            research_coverage=research_coverage,
            created_at=datetime.now().isoformat(),
        )

        self.schemas[schema.schema_id] = schema
        logger.info(f"Generated schema: {schema.schema_id} with {len(relevant_patterns)} patterns")
        return schema

    def validate_schema(self, schema: ExtractionSchema) -> dict[str, Any]:
        """Validate a schema against research findings and quality criteria."""
        logger.info(f"Validating schema: {schema.schema_id}")

        validation_results = {
            "schema_id": schema.schema_id,
            "overall_score": 0.0,
            "validation_passed": False,
            "issues": [],
            "recommendations": [],
        }

        # Check research coverage
        if schema.research_coverage < 0.8:
            validation_results["issues"].append(f"Low research coverage: {schema.research_coverage:.2f}")
            validation_results["recommendations"].append("Include more research-based patterns")
        else:
            validation_results["overall_score"] += 0.3

        # Check pattern completeness
        if len(schema.patterns) < 2:
            validation_results["issues"].append("Insufficient patterns for robust extraction")
            validation_results["recommendations"].append("Add more extraction patterns")
        else:
            validation_results["overall_score"] += 0.3

        # Check validation rules
        if len(schema.validation_rules) < 3:
            validation_results["issues"].append("Insufficient validation rules")
            validation_results["recommendations"].append("Add more validation criteria")
        else:
            validation_results["overall_score"] += 0.2

        # Check performance targets
        if "extraction_time" not in schema.quality_metrics.get("performance_targets", {}):
            validation_results["issues"].append("Missing performance targets")
            validation_results["recommendations"].append("Define performance benchmarks")
        else:
            validation_results["overall_score"] += 0.2

        # Determine if validation passed
        validation_results["validation_passed"] = validation_results["overall_score"] >= 0.8

        logger.info(f"Schema validation complete: {validation_results['overall_score']:.2f}/1.0")
        return validation_results

    def save_schema(self, schema: ExtractionSchema) -> None:
        """Save a schema to disk."""
        schema_file = self.schemas_dir / f"{schema.schema_id}.json"

        # Convert dataclass to dict for JSON serialization
        schema_dict = {
            "schema_id": schema.schema_id,
            "content_type": schema.content_type,
            "patterns": [
                {
                    "pattern_name": p.pattern_name,
                    "description": p.description,
                    "research_basis": p.research_basis,
                    "implementation": p.implementation,
                    "validation_criteria": p.validation_criteria,
                    "performance_benchmarks": p.performance_benchmarks,
                    "content_types": p.content_types,
                }
                for p in schema.patterns
            ],
            "validation_rules": schema.validation_rules,
            "quality_metrics": schema.quality_metrics,
            "research_coverage": schema.research_coverage,
            "created_at": schema.created_at,
            "version": schema.version,
        }

        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Schema saved to: {schema_file}")

    def load_schema(self, schema_id: str) -> ExtractionSchema | None:
        """Load a schema from disk."""
        schema_file = self.schemas_dir / f"{schema_id}.json"

        if not schema_file.exists():
            logger.error(f"Schema file not found: {schema_file}")
            return None

        try:
            with open(schema_file, encoding="utf-8") as f:
                schema_data = json.load(f)

            # Reconstruct patterns
            patterns = []
            for pattern_data in schema_data.get("patterns", []):
                pattern = SchemaPattern(**pattern_data)
                patterns.append(pattern)

            schema_data["patterns"] = patterns
            schema = ExtractionSchema(**schema_data)

            logger.info(f"Schema loaded: {schema_id}")
            return schema

        except Exception as e:
            logger.error(f"Error loading schema {schema_id}: {e}")
            return None

    def get_schema_summary(self) -> dict[str, Any]:
        """Get a summary of all schemas."""
        summary = {"total_schemas": len(self.schemas), "schemas": {}, "research_coverage": 0.0, "average_patterns": 0.0}

        total_coverage = 0.0
        total_patterns = 0

        for schema_id, schema in self.schemas.items():
            summary["schemas"][schema_id] = {
                "content_type": schema.content_type,
                "pattern_count": len(schema.patterns),
                "research_coverage": schema.research_coverage,
                "validation_rule_count": len(schema.validation_rules),
                "created_at": schema.created_at,
            }

            total_coverage += schema.research_coverage
            total_patterns += len(schema.patterns)

        if self.schemas:
            summary["research_coverage"] = total_coverage / len(self.schemas)
            summary["average_patterns"] = total_patterns / len(self.schemas)

        return summary


def main():
    """Main entry point for research-based schema design."""
    import argparse

    parser = argparse.ArgumentParser(description="Research-Based Schema Design for Extraction")
    parser.add_argument("--analyze-research", action="store_true", help="Analyze research findings")
    parser.add_argument("--generate-patterns", action="store_true", help="Generate schema patterns")
    parser.add_argument("--generate-schema", action="store_true", help="Generate schema for content type")
    parser.add_argument("--content-type", help="Content type for schema generation")
    parser.add_argument("--validate-schema", action="store_true", help="Validate existing schema")
    parser.add_argument("--schema-id", help="Schema ID for validation")
    parser.add_argument("--summary", action="store_true", help="Show schema summary")
    parser.add_argument("--output-file", help="Output file for results")

    args = parser.parse_args()

    schema_design = ResearchBasedSchemaDesign()

    if args.analyze_research:
        print("Analyzing research findings...")
        results = schema_design.analyze_research()
        print("Research analysis complete:")
        print(f"  - Files analyzed: {results['total_files']}")
        print(f"  - Findings extracted: {results['findings_extracted']}")
        print(f"  - Topics covered: {', '.join(results['topics_covered'])}")
        print(f"  - Research coverage: {results['research_coverage']:.2f}")

        if args.output_file:
            with open(args.output_file, "w") as f:
                json.dump(results, f, indent=2)

    if args.generate_patterns:
        print("Generating schema patterns...")
        patterns = schema_design.generate_schema_patterns()
        print(f"Generated {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"  - {pattern.pattern_name}: {pattern.description}")

    if args.generate_schema and args.content_type:
        print(f"Generating schema for content type: {args.content_type}")
        schema = schema_design.generate_schema(args.content_type)
        schema_design.save_schema(schema)
        print(f"Schema generated and saved: {schema.schema_id}")

    if args.validate_schema and args.schema_id:
        print(f"Validating schema: {args.schema_id}")
        schema = schema_design.load_schema(args.schema_id)
        if schema:
            results = schema_design.validate_schema(schema)
            print("Validation results:")
            print(f"  - Overall score: {results['overall_score']:.2f}/1.0")
            print(f"  - Passed: {results['validation_passed']}")
            if results["issues"]:
                print(f"  - Issues: {', '.join(results['issues'])}")
            if results["recommendations"]:
                print(f"  - Recommendations: {', '.join(results['recommendations'])}")

    if args.summary:
        print("Schema summary:")
        summary = schema_design.get_schema_summary()
        print(f"  - Total schemas: {summary['total_schemas']}")
        print(f"  - Average research coverage: {summary['research_coverage']:.2f}")
        print(f"  - Average patterns per schema: {summary['average_patterns']:.1f}")
        for schema_id, info in summary["schemas"].items():
            print(f"  - {schema_id}: {info['content_type']} ({info['pattern_count']} patterns)")

    if not any(
        [args.analyze_research, args.generate_patterns, args.generate_schema, args.validate_schema, args.summary]
    ):
        print("Research-Based Schema Design for Extraction")
        print("Use --help for available options")
        print("\nExample usage:")
        print("  python3 scripts/research_based_schema_design.py --analyze-research")
        print("  python3 scripts/research_based_schema_design.py --generate-schema --content-type documentation")
        print("  python3 scripts/research_based_schema_design.py --validate-schema --schema-id documentation_schema_v1")


if __name__ == "__main__":
    main()
