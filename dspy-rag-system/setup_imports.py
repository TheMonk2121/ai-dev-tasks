#!/usr/bin/env python3.12.123.11
"""
Thin wrapper to normalize sys.path for scripts and ad-hoc runs.
Prefer tests/conftest.py for pytest.
"""
import sys
from pathlib import Path


def boost_sys_path():
    here = Path(__file__).resolve().parent  # dspy-rag-system/
    src = here / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    # Optional, only if some tools expect repo root:
    repo_root = here.parent
    if str(repo_root) not in sys.path:
        sys.path.append(str(repo_root))


# Apply on import for backward compatibility
boost_sys_path()


# Legacy function names for backward compatibility
def setup_dspy_imports():
    """Legacy function - now just calls boost_sys_path"""
    boost_sys_path()
    return True


def get_common_imports():
    """Legacy function - returns empty dict for backward compatibility"""
    return {}
