#!/usr/bin/env python3
"""
CI guard for retrieval KPIs.
Runs eval_gold metrics and enforces thresholds:
- scoped intent@3 >= 0.80
- hit@3 >= 0.69
- mrr@10 >= 0.67
- dup_rate@3 <= 0.33
- p95 latency <= budget (default 0.250s, overridable via KPI_P95_BUDGET_SEC)

Exit non-zero on failure so CI can block.
"""

from __future__ import annotations

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

from dspy_modules.vector_store import HybridVectorStore
from eval_gold import ADDITIONAL_GOLD, GOLD, evaluate, make_search_fn


def run_eval() -> dict:
    # Mimic eval_gold main but return metrics dict
    load_dotenv()
    os.environ.setdefault("HYBRID_USE_WRAPPER", "1")
    os.environ.setdefault("NS_RESERVED", "2")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        sys.exit(1)

    store = HybridVectorStore(db_url)
    search_fn = make_search_fn(store)
    GOLD.update(ADDITIONAL_GOLD)
    metrics = evaluate(search_fn, GOLD, top_k=10, at_k=3)
    print(metrics)
    return metrics


def main() -> int:
    metrics = run_eval()

    # Thresholds
    intent = float(metrics.get("intent@3", 0.0))
    scoped_n = int(metrics.get("scoped_n", 0))
    hit3 = float(metrics.get("hit@3", 0.0))
    mrr10 = float(metrics.get("mrr@10", 0.0))
    dup = float(metrics.get("dup_rate@3", 1.0))
    p95 = float(metrics.get("p95_latency_s", 10.0))

    intent_min = float(os.getenv("KPI_INTENT3_MIN", "0.80"))
    hit3_min = float(os.getenv("KPI_HIT3_MIN", "0.69"))
    mrr_min = float(os.getenv("KPI_MRR10_MIN", "0.67"))
    dup_max = float(os.getenv("KPI_DUP3_MAX", "0.33"))
    p95_max = float(os.getenv("KPI_P95_BUDGET_SEC", "0.250"))

    failures = []
    if scoped_n > 0 and intent < intent_min:
        failures.append(f"intent@3 {intent:.2f} < {intent_min:.2f}")
    if hit3 < hit3_min:
        failures.append(f"hit@3 {hit3:.2f} < {hit3_min:.2f}")
    if mrr10 < mrr_min:
        failures.append(f"mrr@10 {mrr10:.2f} < {mrr_min:.2f}")
    if dup > dup_max:
        failures.append(f"dup_rate@3 {dup:.2f} > {dup_max:.2f}")
    if p95 > p95_max:
        failures.append(f"p95_latency_s {p95:.3f} > {p95_max:.3f}")

    if failures:
        print("❌ KPI check failed:\n - " + "\n - ".join(failures))
        return 2
    print("✅ KPI check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
