from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional, Union

#!/usr/bin/env python3
"""
Lightweight helper to capture Hypothesis counter-examples into tests/data/edge_cases.jsonl
so we can add deterministic regression tests.
"""




def _edge_cases_path() -> Path:
    # tests/test_property_regressions.py loads from tests/data/edge_cases.jsonl
    root = Path(__file__).resolve().parents[1]
    p = root / "data" / "edge_cases.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def record_case(test_name: str, payload: dict[str, Any]) -> None:
    """Append a regression case to the shared edge_cases.jsonl file.

    Args:
        test_name: Identifier to route the reproduction (e.g., "test_query_rewrite_regex")
        payload: JSON-serializable dict with inputs and optional expected values
    """
    try:
        row = {"test": test_name, **payload}
        p = _edge_cases_path()
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        # Never fail the test because of capture issues
        pass

