#!/usr/bin/env python3
"""
Command-aware scoring utilities for evaluation.
"""

import re
import shlex
from typing import Any


def _norm_cmd(s: str) -> set[str]:
    """Normalize command strings for order-insensitive comparison."""
    s = re.sub(r"\s+", " ", s.strip())
    toks = shlex.split(s)
    # split '--flag=value' into two tokens for order-insensitive compare
    norm = []
    for t in toks:
        if t.startswith("--") and "=" in t:
            k, v = t.split("=", 1)
            norm += [k, v]
        else:
            norm.append(t)
    return set(norm)


def cmd_f1(pred: str, gold: str) -> float:
    """Calculate F1 score for commands with order-insensitive comparison."""
    P, G = _norm_cmd(pred), _norm_cmd(gold)
    if not P or not G:
        return 0.0
    inter = len(P & G)
    prec = inter / len(P)
    rec = inter / len(G)
    return 0.0 if (prec == 0 or rec == 0) else 2 * prec * rec / (prec + rec)


def is_command_gold(gold: str) -> bool:
    """Check if gold answer looks like a command."""
    gold_lower = gold.lower()
    return any(k in gold_lower for k in ("uv run", "--profile", "python", "make", "env -u"))


def smart_f1(pred: str, gold: str) -> float:
    """Use command-aware F1 if gold looks like a command, otherwise use regular F1."""
    if is_command_gold(gold):
        return cmd_f1(pred, gold)
    else:
        # Regular F1 calculation
        pred_words = set(pred.lower().split())
        gold_words = set(gold.lower().split())
        if not pred_words or not gold_words:
            return 0.0
        inter = len(pred_words & gold_words)
        prec = inter / len(pred_words)
        rec = inter / len(gold_words)
        return 0.0 if (prec == 0 or rec == 0) else 2 * prec * rec / (prec + rec)
