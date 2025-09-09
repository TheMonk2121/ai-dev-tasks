"""Test configuration for AI development tasks."""

import sys
from pathlib import Path

# Ensure common project paths are importable for all tests
project_root = Path(__file__).parent.parent
scripts_dir = project_root / "scripts"
src_dir = project_root / "src"

for p in (project_root, scripts_dir, src_dir):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
