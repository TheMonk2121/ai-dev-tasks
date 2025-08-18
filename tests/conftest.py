"""
B-103 Phase 3: Test configuration for unified import resolution.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to Python path for tests
project_root = Path(__file__).parent.parent
scripts_path = project_root / "scripts"
dspy_src_path = project_root / "dspy-rag-system" / "src"

if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

if str(dspy_src_path) not in sys.path:
    sys.path.insert(0, str(dspy_src_path))


def pytest_configure(config):
    """Configure pytest with import path validation."""
    # Validate that all test imports use unified configuration
    # This prevents per-file sys.path hacks in test files
    pass


def pytest_collection_modifyitems(config, items):
    """Validate import paths for collected test items."""

    for item in items:
        # Check if test file has direct sys.path manipulation
        test_file = Path(item.fspath)
        if test_file.exists():
            with open(test_file) as f:
                content = f.read()
                if "sys.path.insert" in content and "conftest.py" not in str(test_file):
                    pytest.fail(
                        f"Test file {test_file} contains direct sys.path manipulation. "
                        f"Use unified import configuration in conftest.py instead."
                    )
