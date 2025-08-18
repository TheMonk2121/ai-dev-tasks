#!/usr/bin/env python3.12.123.11
"""
Tests for slugify function correctness (PR B)
"""

import pytest

from scripts.markdown_utils import slugify_heading


@pytest.mark.tier1
@pytest.mark.kind_unit
class TestSlugifyHeading:
    """Test GitHub-style heading slugification."""

    def test_basic_slugification(self):
        """Test basic heading slugification."""
        assert slugify_heading("Hello World") == "hello-world"
        assert slugify_heading("API Reference") == "api-reference"
        assert slugify_heading("Getting Started") == "getting-started"

    def test_special_characters(self):
        """Test handling of special characters."""
        assert slugify_heading("Hello & World") == "hello--world"
        assert slugify_heading("API Reference & Examples") == "api-reference--examples"
        assert slugify_heading("What's New?") == "whats-new"

    def test_numbers(self):
        """Test handling of numbers."""
        assert slugify_heading("Version 2.0") == "version-20"
        assert slugify_heading("API v1.2.3") == "api-v123"

    def test_underscores_and_hyphens(self):
        """Test handling of underscores and hyphens."""
        assert slugify_heading("Hello_World") == "hello-world"
        assert slugify_heading("API-Reference") == "api-reference"
        assert slugify_heading("Hello_World-Test") == "hello-world-test"

    def test_multiple_spaces(self):
        """Test handling of multiple spaces."""
        assert slugify_heading("Hello   World") == "hello-world"
        assert slugify_heading("  API Reference  ") == "api-reference"

    def test_empty_and_edge_cases(self):
        """Test empty and edge cases."""
        assert slugify_heading("") == ""
        assert slugify_heading("   ") == ""
        assert slugify_heading("###") == ""
        assert slugify_heading("123") == "123"

    def test_unicode_normalization(self):
        """Test Unicode normalization."""
        # Test combining characters
        assert slugify_heading("café") == "cafe"
        assert slugify_heading("naïve") == "naive"

    def test_chinese_characters(self):
        """Test Chinese character handling."""
        # Chinese characters should be converted to Unicode code points
        result = slugify_heading("你好世界")
        assert "-" in result
        assert all(part.isdigit() or part == "-" for part in result.split("-") if part)

    def test_html_tags(self):
        """Test HTML tag removal."""
        assert slugify_heading("<strong>Hello</strong> World") == "hello-world"
        assert slugify_heading("API <code>Reference</code>") == "api-reference"

    def test_github_compatibility(self):
        """Test compatibility with GitHub's slugification."""
        # These should match GitHub's behavior
        assert slugify_heading("Vector Store Contract") == "vector-store-contract"
        assert slugify_heading("API Reference & Examples") == "api-reference--examples"
        assert slugify_heading("Getting Started!") == "getting-started"

    def test_emoji_heading_slug(self):
        """Emoji in headings should be ignored for slug creation, preserving words."""
        assert slugify_heading("⚡ Quick reference") == "quick-reference"

    def test_case_insensitivity(self):
        """Test case insensitivity."""
        assert slugify_heading("Hello World") == slugify_heading("hello world")
        assert slugify_heading("API Reference") == slugify_heading("api reference")

    def test_trailing_punctuation(self):
        """Test removal of trailing punctuation."""
        assert slugify_heading("Hello World!") == "hello-world"
        assert slugify_heading("API Reference?") == "api-reference"
        assert slugify_heading("Getting Started.") == "getting-started"
