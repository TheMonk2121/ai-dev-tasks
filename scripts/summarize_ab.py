#!/usr/bin/env python3
"""
A/B Test Metrics Summary Script
-------------------------------
Generate PR-ready Markdown tables for A/B test results.

Usage:
    python scripts/summarize_ab.py BASELINE.json VARIANT.json
"""

from __future__ import annotations

import json
import sys
from typing import Any


def load(path: str) -> dict[str, Any]:
    """Load JSON metrics file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pct(a: float, b: float) -> str:
    """Calculate percentage change."""
    if a == 0:
        return "n/a"
    return f"{((b-a)/a)*100:.1f}%"


def main() -> None:
    """Main function to generate A/B test summary."""
    if len(sys.argv) != 3:
        print("usage: python scripts/summarize_ab.py BASELINE.json VARIANT.json")
        sys.exit(2)

    try:
        base = load(sys.argv[1])
        var = load(sys.argv[2])
    except FileNotFoundError as e:
        print(f"Error: Could not find metrics file: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in metrics file: {e}")
        sys.exit(1)

    print("## A/B Test Results Summary")
    print()
    print("| Metric | Baseline | Variant | Δ |")
    print("|---|---:|---:|---:|")

    metrics = [
        ("recall_at_10", "Recall@10"),
        ("grounding_rate", "Grounding Rate (%)"),
        ("avg_tokens", "Avg Tokens"),
        ("expansion_latency_ms", "Expansion Latency (ms)"),
    ]

    for key, label in metrics:
        b_val = base.get(key, 0.0)
        v_val = var.get(key, 0.0)

        if isinstance(b_val, int | float) and isinstance(v_val, int | float):
            delta = pct(b_val, v_val)
            print(f"| {label} | {b_val:.3f} | {v_val:.3f} | {delta} |")
        else:
            print(f"| {label} | {b_val} | {v_val} | - |")

    print()
    print("### Success Criteria")
    print()
    print("- [ ] Recall@10 ≥ 0.8")
    print("- [ ] Total bundle tokens ≤ 1200")
    print("- [ ] Expansion latency ≤ 200ms p95")
    print("- [ ] ≥ +10% recall improvement on entity-rich queries")
    print()

    # Calculate overall success
    recall_improvement = 0.0
    if base.get("recall_at_10", 0) > 0:
        recall_improvement = (
            (var.get("recall_at_10", 0) - base.get("recall_at_10", 0)) / base.get("recall_at_10", 1)
        ) * 100

    avg_tokens = var.get("avg_tokens", 0)
    expansion_latency = var.get("expansion_latency_ms", 0)

    success_criteria = [
        var.get("recall_at_10", 0) >= 0.8,
        avg_tokens <= 1200,
        expansion_latency <= 200,
        recall_improvement >= 10.0,
    ]

    all_passed = all(success_criteria)

    print(f"### Overall Result: {'✅ PASS' if all_passed else '❌ FAIL'}")
    print()
    print(f"- Recall@10: {var.get('recall_at_10', 0):.3f} {'✅' if var.get('recall_at_10', 0) >= 0.8 else '❌'}")
    print(f"- Avg Tokens: {avg_tokens:.0f} {'✅' if avg_tokens <= 1200 else '❌'}")
    print(f"- Expansion Latency: {expansion_latency:.1f}ms {'✅' if expansion_latency <= 200 else '❌'}")
    print(f"- Recall Improvement: {recall_improvement:.1f}% {'✅' if recall_improvement >= 10.0 else '❌'}")


if __name__ == "__main__":
    main()
