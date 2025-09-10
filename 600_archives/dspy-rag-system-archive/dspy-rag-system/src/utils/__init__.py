#!/usr/bin/env python3
"""
Utils Package

Lightweight package init for DSPy RAG utils. Avoids importing heavy
submodules at import time to prevent optional dependency failures
in environments without full DB/tooling.
"""

__version__ = "1.0.0"

# Intentionally avoid eager-importing submodules here. Import modules
# explicitly where needed, so optional dependencies (e.g., psycopg2)
# aren't required just to import `utils`.
