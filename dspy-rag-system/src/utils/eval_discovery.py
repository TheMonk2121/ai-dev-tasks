#!/usr/bin/env python3
"""
Evaluation Discovery Helpers

Lightweight, filesystem-based discovery of the repository's evaluation entry points
so agents can return actionable commands even when RAG/DB retrieval is unavailable
or the schema is mismatched.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[3]


def _exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def discover_evaluation_commands() -> Dict[str, List[Dict[str, str]]]:
    """Discover eval entry points and recommended commands in the repo.

    Returns a dict with two lists:
    - commands: ordered, actionable commands (primary first)
    - files: key files that document or wrap eval flows
    """
    files: List[Dict[str, str]] = []
    commands: List[Dict[str, str]] = []

    # Primary entry points
    if _exists("RUN_THE_EVALS_START_HERE.md"):
        files.append({
            "path": "RUN_THE_EVALS_START_HERE.md",
            "reason": "Top-level, discoverable instructions for running evals",
        })

    if _exists("000_core/000_evaluation-system-entry-point.md"):
        files.append({
            "path": "000_core/000_evaluation-system-entry-point.md",
            "reason": "Primary SOP for the evaluation system",
        })

    if _exists("run_evals.sh"):
        files.append({
            "path": "run_evals.sh",
            "reason": "Canonical wrapper script to run the evals",
        })

    # Core scripts
    if _exists("throttle_free_eval.sh"):
        files.append({
            "path": "throttle_free_eval.sh",
            "reason": "Loads stable evaluation environment",
        })

    if _exists("scripts/ragchecker_official_evaluation.py"):
        files.append({
            "path": "scripts/ragchecker_official_evaluation.py",
            "reason": "Main evaluation driver",
        })

    if _exists("scripts/run_ragchecker_smoke_test.sh"):
        files.append({
            "path": "scripts/run_ragchecker_smoke_test.sh",
            "reason": "Fast smoke test wrapper",
        })

    # Construct recommended commands (prefer Bedrock when available)
    if _exists("scripts/ragchecker_official_evaluation.py") and _exists("throttle_free_eval.sh"):
        commands.append({
            "label": "Primary (stable, Bedrock-preferred)",
            "cmd": "source throttle_free_eval.sh && python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable",
        })
        commands.append({
            "label": "Primary (stable, local-LLM fallback)",
            "cmd": "source throttle_free_eval.sh && python3 scripts/ragchecker_official_evaluation.py --use-local-llm --bypass-cli --stable",
        })

    if _exists("scripts/run_ragchecker_smoke_test.sh"):
        commands.append({
            "label": "Fast smoke test",
            "cmd": "./scripts/run_ragchecker_smoke_test.sh",
        })

    if _exists("run_evals.sh"):
        commands.append({
            "label": "Canonical wrapper",
            "cmd": "./run_evals.sh",
        })

    return {"commands": commands, "files": files}

