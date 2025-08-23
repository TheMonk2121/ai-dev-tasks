#!/usr/bin/env python3
"""
Test suite for Research-Based Schema Design for Extraction
=========================================================
Comprehensive tests for the research-based schema design system.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.research_based_schema_design import (
    ExtractionSchema,
    ResearchBasedSchemaDesign,
    ResearchFinding,
    SchemaPattern,
)


class TestResearchBasedSchemaDesign:
    """Test cases for the ResearchBasedSchemaDesign class."""

    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.research_dir = Path(self.temp_dir) / "500_research"
        self.schemas_dir = Path(self.temp_dir) / "schemas"

        self.research_dir.mkdir()
        self.schemas_dir.mkdir()

        # Create sample research files
        self._create_sample_research_files()

        # Initialize the schema design system
        with patch.object(ResearchBasedSchemaDesign, "__init__", return_value=None):
            self.schema_design = ResearchBasedSchemaDesign()
            self.schema_design.research_dir = self.research_dir
            self.schema_design.schemas_dir = self.schemas_dir
            self.schema_design.findings = []
            self.schema_design.patterns = []
            self.schema_design.schemas = {}

        yield

        # Clean up test fixtures
        shutil.rmtree(self.temp_dir)

    def _create_sample_research_files(self):
        """Create sample research files for testing."""
        # Sample RAG research file
        rag_research = """
# RAG System Research

## Key Findings
- Hybrid dense+sparse significantly improves recall/precision over pure vector search
- Smaller, semantically coherent chunks (≈100–300 words/tokens) outperform large blocks
- Span-level grounding (character offsets) increases trust and enables automatic faithfulness checks

## Actionable Patterns
- Implement span-level grounding for all extracted content
- Use hybrid retrieval for improved accuracy
- Store character offsets for validation
"""
        (self.research_dir / "500_rag-system-research.md").write_text(rag_research)

        # Sample DSPy research file
        dspy_research = """
# DSPy Research

## Key Findings
- Assertions move reliability from ad-hoc guardrails to code-enforced constraints
- Teleprompter compiles programs with example selection against a metric
- DSPy modules provide clean composition for multi-hop retrieval

## Actionable Patterns
- Implement DSPy assertions for validation
- Use teleprompter for prompt optimization
- Structure workflows as DSPy modules
"""
        (self.research_dir / "500_dspy-research.md").write_text(dspy_research)

        # Sample metadata research file
        metadata_research = """
# Metadata Research

## Key Findings
- Consistent identifiers (doc_id, chunk_id) and span offsets enable grounding
- Provenance and last_verified fields are essential for trust
- Governance requires PII classification and redaction policies

## Actionable Patterns
- Implement consistent identifier scheme
- Track provenance for all content
- Validate metadata completeness
"""
        (self.research_dir / "500_metadata-research.md").write_text(metadata_research)

    def test_analyze_research(self):
        """Test research analysis functionality."""
        results = self.schema_design.analyze_research()

        assert isinstance(results, dict)
        assert "total_files" in results
        assert "findings_extracted" in results
        assert "topics_covered" in results
        assert "research_coverage" in results

        assert results["total_files"] == 3
        assert results["findings_extracted"] > 0
        assert len(results["topics_covered"]) > 0
        assert results["research_coverage"] > 0.0

    def test_extract_findings_from_file(self):
        """Test extraction of findings from research files."""
        rag_file = self.research_dir / "500_rag-system-research.md"
        findings = self.schema_design._extract_findings_from_file(rag_file)

        assert isinstance(findings, list)
        assert len(findings) > 0

        for finding in findings:
            assert isinstance(finding, ResearchFinding)
            assert finding.source_file == str(rag_file)
            assert finding.topic == "rag-system"
            assert isinstance(finding.key_insight, str)
            assert len(finding.key_insight) > 0

    def test_generate_schema_patterns(self):
        """Test schema pattern generation."""
        patterns = self.schema_design.generate_schema_patterns()

        assert isinstance(patterns, list)
        assert len(patterns) > 0

        for pattern in patterns:
            assert isinstance(pattern, SchemaPattern)
            assert isinstance(pattern.pattern_name, str)
            assert isinstance(pattern.description, str)
            assert isinstance(pattern.research_basis, list)
            assert isinstance(pattern.validation_criteria, list)
            assert isinstance(pattern.performance_benchmarks, dict)
            assert isinstance(pattern.content_types, list)

    def test_generate_schema(self):
        """Test schema generation for a content type."""
        # First generate patterns
        self.schema_design.generate_schema_patterns()

        # Generate schema for documentation
        schema = self.schema_design.generate_schema("documentation")

        assert isinstance(schema, ExtractionSchema)
        assert schema.content_type == "documentation"
        assert len(schema.patterns) > 0
        assert len(schema.validation_rules) > 0
        assert isinstance(schema.quality_metrics, dict)
        assert schema.research_coverage > 0.0

    def test_validate_schema(self):
        """Test schema validation."""
        # Generate a schema first
        self.schema_design.generate_schema_patterns()
        schema = self.schema_design.generate_schema("documentation")

        # Validate the schema
        validation_results = self.schema_design.validate_schema(schema)

        assert isinstance(validation_results, dict)
        assert "schema_id" in validation_results
        assert "overall_score" in validation_results
        assert "validation_passed" in validation_results
        assert "issues" in validation_results
        assert "recommendations" in validation_results

        assert isinstance(validation_results["overall_score"], float)
        assert isinstance(validation_results["validation_passed"], bool)
        assert isinstance(validation_results["issues"], list)
        assert isinstance(validation_results["recommendations"], list)

    def test_save_and_load_schema(self):
        """Test schema saving and loading."""
        # Generate a schema
        self.schema_design.generate_schema_patterns()
        schema = self.schema_design.generate_schema("test_content")

        # Save the schema
        self.schema_design.save_schema(schema)

        # Verify the file was created
        schema_file = self.schemas_dir / f"{schema.schema_id}.json"
        assert schema_file.exists()

        # Load the schema
        loaded_schema = self.schema_design.load_schema(schema.schema_id)

        assert loaded_schema is not None
        assert loaded_schema.schema_id == schema.schema_id
        assert loaded_schema.content_type == schema.content_type
        assert len(loaded_schema.patterns) == len(schema.patterns)
        assert len(loaded_schema.validation_rules) == len(schema.validation_rules)

    def test_get_schema_summary(self):
        """Test schema summary generation."""
        # Generate multiple schemas
        self.schema_design.generate_schema_patterns()
        self.schema_design.generate_schema("documentation")
        self.schema_design.generate_schema("code")
        self.schema_design.generate_schema("research")

        # Get summary
        summary = self.schema_design.get_schema_summary()

        assert isinstance(summary, dict)
        assert "total_schemas" in summary
        assert "schemas" in summary
        assert "research_coverage" in summary
        assert "average_patterns" in summary

        assert summary["total_schemas"] == 3
        assert summary["research_coverage"] > 0.0
        assert summary["average_patterns"] > 0.0

    def test_content_type_matching(self):
        """Test content type matching logic."""
        self.schema_design.generate_schema_patterns()

        # Test documentation content type
        doc_schema = self.schema_design.generate_schema("documentation")
        assert len(doc_schema.patterns) > 0

        # Test code content type
        code_schema = self.schema_design.generate_schema("code")
        assert len(code_schema.patterns) > 0

        # Test research content type
        research_schema = self.schema_design.generate_schema("research")
        assert len(research_schema.patterns) > 0

    def test_research_coverage_calculation(self):
        """Test research coverage calculation."""
        self.schema_design.generate_schema_patterns()

        # Generate schema and check coverage
        schema = self.schema_design.generate_schema("documentation")

        assert schema.research_coverage > 0.0
        assert schema.research_coverage <= 1.0

        # Coverage should be based on research areas covered by patterns
        research_areas = set()
        for pattern in schema.patterns:
            research_areas.update(pattern.research_basis)

        expected_coverage = len(research_areas) / 4.0  # 4 available research areas
        assert abs(schema.research_coverage - expected_coverage) < 0.01

    def test_validation_criteria_generation(self):
        """Test validation criteria generation from patterns."""
        self.schema_design.generate_schema_patterns()
        schema = self.schema_design.generate_schema("documentation")

        # Validation rules should be aggregated from all patterns
        expected_rules = []
        for pattern in schema.patterns:
            expected_rules.extend(pattern.validation_criteria)

        assert len(schema.validation_rules) == len(expected_rules)
        assert set(schema.validation_rules) == set(expected_rules)

    def test_quality_metrics_generation(self):
        """Test quality metrics generation."""
        self.schema_design.generate_schema_patterns()
        schema = self.schema_design.generate_schema("documentation")

        metrics = schema.quality_metrics

        assert "research_coverage" in metrics
        assert "pattern_count" in metrics
        assert "validation_rule_count" in metrics
        assert "performance_targets" in metrics

        assert metrics["pattern_count"] == len(schema.patterns)
        assert metrics["validation_rule_count"] == len(schema.validation_rules)
        assert isinstance(metrics["performance_targets"], dict)

class TestDataClasses:
    """Test cases for data classes."""

    def test_research_finding(self):
        """Test ResearchFinding data class."""
        finding = ResearchFinding(
            source_file="test.md",
            topic="test",
            key_insight="Test insight",
            implementation_impact="Test impact",
            actionable_patterns=["pattern1", "pattern2"],
            citations=["citation1"],
            confidence=0.9,
            last_updated="2025-08-16T00:00:00",
        )

        assert finding.source_file == "test.md"
        assert finding.topic == "test"
        assert finding.key_insight == "Test insight"
        assert finding.confidence == 0.9

    def test_schema_pattern(self):
        """Test SchemaPattern data class."""
        pattern = SchemaPattern(
            pattern_name="test_pattern",
            description="Test pattern",
            research_basis=["research1"],
            implementation="{}",
            validation_criteria=["criteria1"],
            performance_benchmarks={"time": "< 1s"},
            content_types=["all"],
        )

        assert pattern.pattern_name == "test_pattern"
        assert pattern.description == "Test pattern"
        assert len(pattern.research_basis) == 1
        assert len(pattern.validation_criteria) == 1
        assert len(pattern.content_types) == 1

    def test_extraction_schema(self):
        """Test ExtractionSchema data class."""
        schema = ExtractionSchema(
            schema_id="test_schema",
            content_type="test",
            patterns=[],
            validation_rules=[],
            quality_metrics={},
            research_coverage=0.8,
            created_at="2025-08-16T00:00:00",
        )

        assert schema.schema_id == "test_schema"
        assert schema.content_type == "test"
        assert schema.research_coverage == 0.8
        assert schema.version == "1.0"

if __name__ == "__main__":
    pytest.main([__file__])
