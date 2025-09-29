"""Pytest configuration for memory consolidation tests."""

import os
import sys
from pathlib import Path

import pytest

# Set environment variable before any imports
os.environ["APP_USE_MEMORY_GRAPH"] = "true"

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def clean_environment():
    """Ensure clean environment variables for all tests."""
    # Store original values
    original_dsn = os.environ.get("POSTGRES_DSN")
    original_db_url = os.environ.get("DATABASE_URL")
    
    # Clear DSN variables to prevent conflicts
    if "POSTGRES_DSN" in os.environ:
        del os.environ["POSTGRES_DSN"]
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    
    yield
    
    # Restore original values
    if original_dsn is not None:
        os.environ["POSTGRES_DSN"] = original_dsn
    if original_db_url is not None:
        os.environ["DATABASE_URL"] = original_db_url
