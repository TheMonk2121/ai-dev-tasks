# evals/load_cases.py
"""
Lightweight loader shim for evaluation cases used by various scripts.
Prefer src.utils.gold_loader in new code; this module provides a stable
interface for older scripts that import load_eval_cases.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from src.schemas.eval import GoldCase as Case  # legacy import path


def load_eval_cases(profile: str | Path = "gold") -> list[Case]:
    """Load evaluation cases based on a simple profile or explicit path.

    - If `profile` is "gold" or startswith "gold", load from env CASES_FILE or default 'evals/gold_cases.json'.
    - If `profile` is a path, load that file.
    - The file is expected to be JSON array of objects compatible with Case.
    """
    # Resolve path
    if isinstance(profile, str | Path) and str(profile).startswith("gold"):
        path = os.getenv("CASES_FILE", "evals/gold_cases.json")
    else:
        path = str(profile)

    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize iterable to list
    if isinstance(data, dict):
        data = [data]

    # Build models with Pydantic normalizations for legacy fields
    return [Case.parse_obj(obj) for obj in data]
