#!/usr/bin/env python3
"""
Tests for the HotFix Template Generation System
"""

import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated

from utils.hotfix_templates import HotFixGenerator, generate_hotfix_template, list_hotfix_templates, HotFixTemplate
from utils.error_pattern_recognition import ErrorAnalysis, ErrorPattern, analyze_error_pattern


class TestHotFixTemplates:
    """Test cases for HotFix template generation"""

    def test_hotfix_generator_initialization(self):
        """Test that the HotFix generator initializes correctly"""
        generator = HotFixGenerator()
        assert generator is not None
        assert len(generator.templates) > 0
        assert isinstance(generator.template_stats, dict)

    def test_database_error_hotfix_generation(self):
        """Test HotFix generation for database errors"""
        error_message = "Database connection timeout after 30 seconds"
        analysis = analyze_error_pattern(error_message, "ConnectionError")

        hotfix = generate_hotfix_template(analysis)
        assert hotfix is not None
        assert hotfix.category == "database"
        assert "timeout" in hotfix.name.lower()
        assert len(hotfix.variables) > 0
        assert hotfix.estimated_time is not None

    def test_llm_error_hotfix_generation(self):
        """Test HotFix generation for LLM errors"""
        error_message = "Rate limit exceeded: too many requests (429)"
        analysis = analyze_error_pattern(error_message, "HTTPError")

        hotfix = generate_hotfix_template(analysis)
        assert hotfix is not None
        assert hotfix.category == "llm"
        assert "rate limit" in hotfix.name.lower()
        assert len(hotfix.variables) > 0

    def test_security_error_hotfix_generation(self):
        """Test HotFix generation for security errors"""
        error_message = "Security violation: blocked pattern detected"
        analysis = analyze_error_pattern(error_message, "SecurityError")

        hotfix = generate_hotfix_template(analysis)
        assert hotfix is not None
        assert hotfix.category == "security"
        assert "security" in hotfix.name.lower()
        assert hotfix.severity == "critical"

    def test_no_hotfix_for_unknown_error(self):
        """Test that no HotFix is generated for unknown errors"""
        error_message = "Some completely unrelated error message"
        analysis = analyze_error_pattern(error_message, "Exception")

        hotfix = generate_hotfix_template(analysis)
        assert hotfix is None

    def test_hotfix_template_content(self):
        """Test that HotFix templates have proper content"""
        templates = list_hotfix_templates()
        assert len(templates) > 0

        for template in templates:
            assert template.template_id is not None
            assert template.name is not None
            assert template.description is not None
            assert template.category is not None
            assert template.severity is not None
            assert template.template_content is not None
            assert len(template.variables) >= 0
            assert len(template.prerequisites) >= 0
            assert template.estimated_time is not None

    def test_hotfix_template_variables(self):
        """Test that HotFix templates have proper variable definitions"""
        templates = list_hotfix_templates()

        for template in templates:
            # Check that variables mentioned in template content are in variables list
            for variable in template.variables:
                assert (
                    f"{{{variable}}}" in template.template_content
                ), f"Variable {variable} not found in template content"

    def test_hotfix_template_categories(self):
        """Test that HotFix templates cover expected categories"""
        templates = list_hotfix_templates()
        categories = set(template.category for template in templates)

        expected_categories = {"database", "llm", "security"}

        # Check that we have templates in expected categories
        for category in expected_categories:
            assert any(
                template.category == category for template in templates
            ), f"Missing HotFix templates for category: {category}"

    def test_hotfix_template_severity_levels(self):
        """Test that HotFix templates have appropriate severity levels"""
        templates = list_hotfix_templates()

        for template in templates:
            assert template.severity in [
                "low",
                "medium",
                "high",
                "critical",
            ], f"Invalid severity level: {template.severity}"

            # Security violations should be critical
            if template.category == "security":
                assert template.severity == "critical"

    def test_hotfix_template_estimated_times(self):
        """Test that HotFix templates have reasonable estimated times"""
        templates = list_hotfix_templates()

        for template in templates:
            assert template.estimated_time is not None
            assert len(template.estimated_time) > 0
            # Should contain time format like "15-30 minutes"
            assert "minute" in template.estimated_time.lower()

    def test_hotfix_template_prerequisites(self):
        """Test that HotFix templates have appropriate prerequisites"""
        templates = list_hotfix_templates()

        for template in templates:
            assert len(template.prerequisites) > 0, f"Template {template.name} has no prerequisites"

            # Database templates should have database-related prerequisites
            if template.category == "database":
                assert any("database" in prereq.lower() for prereq in template.prerequisites)

            # Security templates should have security-related prerequisites
            if template.category == "security":
                assert any("security" in prereq.lower() for prereq in template.prerequisites)

    def test_hotfix_template_generation_with_context(self):
        """Test HotFix generation with context information"""
        error_message = "Database connection timeout"
        context = {"db_host": "localhost", "db_port": "5432"}
        analysis = analyze_error_pattern(error_message, "ConnectionError", context)

        hotfix = generate_hotfix_template(analysis, context)
        assert hotfix is not None
        assert hotfix.category == "database"

    def test_hotfix_template_statistics(self):
        """Test that HotFix template statistics are tracked"""
        generator = HotFixGenerator()

        # Generate some HotFixes to update statistics
        error_message = "Database connection timeout"
        analysis = analyze_error_pattern(error_message, "ConnectionError")
        generator.generate_hotfix(analysis)

        # Check that statistics are updated
        assert len(generator.template_stats) > 0


if __name__ == "__main__":
    pytest.main([__file__])
