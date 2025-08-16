# dspy-rag-system/tests/conftest.py
import sys
from pathlib import Path


def _boost_sys_path():
    tests_dir = Path(__file__).resolve().parent
    dspy_root = tests_dir.parent  # dspy-rag-system/
    src = dspy_root / "src"  # dspy-rag-system/src

    # Add dspy-rag-system/src so `dspy_modules` and `utils` resolve
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

    # Optional: also add repo root if you keep cross-repo imports in some tests
    repo_root = dspy_root.parent
    if str(repo_root) not in sys.path:
        sys.path.append(str(repo_root))


# Always boost the path for both pytest and static analysis
# This ensures tests can import utils.* and dspy_modules.* consistently
_boost_sys_path()
