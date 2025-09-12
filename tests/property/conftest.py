from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, List, Optional, Union

from hypothesis import HealthCheck, Phase, settings

from ._regression_capture import record_case

"""
Pytest conftest for Hypothesis property-based tests.
Defines a 'ci' profile for controlled execution in CI environments.
Also captures counter-examples from unexpected failures across all property
tests in this folder into tests/data/edge_cases.jsonl for regression replay.
"""


# Register CI profile for property tests
settings.register_profile(
    "ci",
    max_examples=25,  # Limit examples for faster CI runs
    deadline=50,  # 50ms deadline per test function
    suppress_health_check=[HealthCheck.too_slow],  # Suppress if tests are slow
    phases=(Phase.generate, Phase.shrink),  # Only generate and shrink, no explore/filter
)

# Load CI profile by default
settings.load_profile("ci")


def _jsonish(v: Any) -> Any:
    """Best-effort conversion of local variables to a JSON-friendly summary."""
    try:

        if v is None or isinstance(v, (bool, int, float, str)):
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                return str(v)
            return v
        if isinstance(v, (list, tuple)):
            if len(v) <= 10:
                return [_jsonish(x) for x in v]
            return {"_type": type(v).__name__, "len": len(v)}
        if isinstance(v, dict):
            if len(v) <= 10:
                return {str(k): _jsonish(v[k]) for k in list(v.keys())[:10]}
            return {"_type": "dict", "len": len(v), "keys": [str(k) for k in list(v.keys())[:10]]}
        s = str(v)
        return s[:200]
    except Exception:
        return "<unserializable>"


def pytest_exception_interact(node, call, report):  # type: ignore[override]
    """Capture locals for failed property tests under tests/property/"""
    try:
        fspath = str(getattr(node, "fspath", ""))
        if "/tests/property/" not in fspath.replace("\\", "/"):
            return
        if not report.failed:
            return
        # Walk traceback to find the first frame within tests/property
        tb = call.excinfo.tb  # type: ignore[attr-defined]
        sel = None
        while tb:
            fn = str(tb.tb_frame.f_code.co_filename)
            if "/tests/property/" in fn.replace("\\", "/"):
                sel = tb.tb_frame.f_locals
                break
            tb = tb.tb_next
        payload = {
            "nodeid": getattr(node, "nodeid", ""),
            "file": fspath,
            "error": str(call.excinfo.value),
        }
        if sel:
            # Sample up to 12 locals
            locals_summary = {}
            for i, (k, v) in enumerate(sel.items()):
                if i >= 12:
                    break
                locals_summary[str(k)] = _jsonish(v)
            payload["locals"] = locals_summary
        record_case(f"auto_property_failure::{getattr(node, 'name', '')}", payload)
    except Exception:
        # Never disrupt pytest on capture errors
        pass
