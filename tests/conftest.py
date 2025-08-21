"""Test configuration for AI development tasks."""

import sys
from pathlib import Path

# Add scripts directory to Python path for all tests
scripts_dir = Path(__file__).parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
