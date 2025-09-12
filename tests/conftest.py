from __future__ import annotations

import sys
from pathlib import Path

from tests.mocks import ragchecker_mock  # noqa: F401

"""Test configuration for AI development tasks."""

# Ensure common project paths are importable for all tests
# Do this FIRST before any other imports that might need these paths
project_root = Path(__file__).parent.parent
scripts_dir = project_root / "scripts"
src_dir = project_root / "src"

# Add paths only once to avoid duplicates
paths_to_add = [project_root, scripts_dir, src_dir]
for path in paths_to_add:
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# Import mocks early to prevent Torch/DSPy imports in unit tests
try:
    pass  # No specific imports needed here
except ImportError:
    pass  # Mocks not available, continue normally
