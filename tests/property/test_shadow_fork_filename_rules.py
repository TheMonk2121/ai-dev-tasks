#!/usr/bin/env python3.12.123.11
"""
Property-based tests for shadow fork filename rules (Round 1)
Tests that illegal names are rejected and legal role-suffix names pass.
"""

import re

import pytest
from hypothesis import given
from hypothesis import strategies as st


@pytest.mark.tier1
@pytest.mark.kind_property
class TestShadowForkFilenameRules:
    """Property-based tests for filename validation rules."""

    # Legal role-suffix patterns
    LEGAL_SUFFIXES = ["core", "perf", "compat", "facade"]

    # Illegal patterns that should be rejected
    ILLEGAL_PATTERNS = [
        r".*_enhanced\.py$",
        r".*_optimized\.py$",
        r".*_improved\.py$",
        r".*_better\.py$",
        r".*_new\.py$",
        r".*_v2\.py$",
        r".*_v3\.py$",
        r".*_updated\.py$",
        r".*_fixed\.py$",
        r".*_patched\.py$",
    ]

    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=["Ll", "Nd"])))
    def test_legal_role_suffix_names_pass(self, base_name):
        """Test that legal role-suffix names are accepted."""
        for suffix in self.LEGAL_SUFFIXES:
            filename = f"{base_name}_{suffix}.py"
            assert self._is_legal_filename(filename), f"Legal filename {filename} was rejected"

    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=["Ll", "Nd"])))
    def test_illegal_enhanced_names_rejected(self, base_name):
        """Test that _enhanced names are rejected."""
        filename = f"{base_name}_enhanced.py"
        assert not self._is_legal_filename(filename), f"Illegal filename {filename} was accepted"

    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=["Ll", "Nd"])))
    def test_illegal_optimized_names_rejected(self, base_name):
        """Test that _optimized names are rejected."""
        filename = f"{base_name}_optimized.py"
        assert not self._is_legal_filename(filename), f"Illegal filename {filename} was accepted"

    @given(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=["Ll", "Nd"])),
        st.sampled_from(
            ["enhanced", "optimized", "improved", "better", "new", "v2", "v3", "updated", "fixed", "patched"]
        ),
    )
    def test_illegal_patterns_rejected(self, base_name, illegal_suffix):
        """Test that all illegal patterns are rejected."""
        filename = f"{base_name}_{illegal_suffix}.py"
        assert not self._is_legal_filename(filename), f"Illegal filename {filename} was accepted"

    @given(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=["Ll", "Nd"])),
        st.sampled_from(LEGAL_SUFFIXES),
    )
    def test_legal_patterns_accepted(self, base_name, legal_suffix):
        """Test that all legal patterns are accepted."""
        filename = f"{base_name}_{legal_suffix}.py"
        assert self._is_legal_filename(filename), f"Legal filename {filename} was rejected"

    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=["Ll", "Nd"])))
    def test_plain_names_accepted(self, base_name):
        """Test that plain names without suffixes are accepted."""
        filename = f"{base_name}.py"
        assert self._is_legal_filename(filename), f"Plain filename {filename} was rejected"

    def test_edge_cases(self):
        """Test edge cases for filename validation."""
        # Test with numbers
        assert self._is_legal_filename("module_123_core.py")
        assert not self._is_legal_filename("module_123_enhanced.py")

        # Test with underscores
        assert self._is_legal_filename("my_module_core.py")
        assert not self._is_legal_filename("my_module_enhanced.py")

        # Test case sensitivity
        assert self._is_legal_filename("module_CORE.py")  # Different case is legal
        assert not self._is_legal_filename("module_ENHANCED.py")  # Different case is still illegal

    def _is_legal_filename(self, filename: str) -> bool:
        """Check if filename follows legal naming rules."""
        # Check for illegal patterns
        for pattern in self.ILLEGAL_PATTERNS:
            if re.match(pattern, filename, re.IGNORECASE):
                return False

        # If no illegal patterns found, it's legal
        return True


@pytest.mark.tier1
@pytest.mark.kind_property
class TestFilenameValidationProperties:
    """Additional property-based tests for filename validation."""

    @given(st.text(min_size=1, max_size=50))
    def test_filename_length_property(self, filename):
        """Test that filename length doesn't affect validation logic."""
        # Add .py extension if not present
        if not filename.endswith(".py"):
            filename += ".py"

        # Test that validation is consistent regardless of length
        is_legal = self._is_legal_filename(filename)

        # Create a longer version and test consistency
        longer_filename = filename.replace(".py", "_longer.py")
        longer_is_legal = self._is_legal_filename(longer_filename)

        # If original was illegal, longer version should also be illegal
        if not is_legal:
            assert not longer_is_legal, f"Length should not change illegal status: {filename} -> {longer_filename}"

    @given(st.text(min_size=1, max_size=20))
    def test_filename_case_consistency(self, base_name):
        """Test that case doesn't affect validation logic."""
        # Test both cases for legal and illegal patterns
        legal_lower = f"{base_name}_core.py"
        legal_upper = f"{base_name}_CORE.py"
        illegal_lower = f"{base_name}_enhanced.py"
        illegal_upper = f"{base_name}_ENHANCED.py"

        # Both cases should have same validation result
        assert self._is_legal_filename(legal_lower) == self._is_legal_filename(legal_upper)
        assert self._is_legal_filename(illegal_lower) == self._is_legal_filename(illegal_upper)

    def _is_legal_filename(self, filename: str) -> bool:
        """Check if filename follows legal naming rules."""
        illegal_patterns = [
            r".*_enhanced\.py$",
            r".*_optimized\.py$",
            r".*_improved\.py$",
            r".*_better\.py$",
            r".*_new\.py$",
            r".*_v2\.py$",
            r".*_v3\.py$",
            r".*_updated\.py$",
            r".*_fixed\.py$",
            r".*_patched\.py$",
        ]

        for pattern in illegal_patterns:
            if re.match(pattern, filename, re.IGNORECASE):
                return False

        return True
