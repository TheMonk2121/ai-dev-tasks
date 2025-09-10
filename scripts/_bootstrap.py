#!/usr/bin/env python3
"""
Bootstrap sys.path so scripts can import project packages reliably.
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "dspy-rag-system" / "src"

for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)
