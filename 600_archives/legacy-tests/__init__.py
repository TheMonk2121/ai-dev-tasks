# DSPy RAG System Tests Package
# This package contains all test files for the DSPy RAG system

# Set up path for static analysis tools (Pyright, etc.)
import sys
from pathlib import Path

# Add src directory to path for import resolution
tests_dir = Path(__file__).resolve().parent
src_dir = tests_dir.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
