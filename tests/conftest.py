"""Pytest configuration for memory consolidation tests."""

import os
import sys
from pathlib import Path

# Set environment variable before any imports
os.environ["APP_USE_MEMORY_GRAPH"] = "true"

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
