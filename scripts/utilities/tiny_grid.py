from __future__ import annotations
import argparse
import itertools
import os
import shutil
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import yaml
from _bootstrap import ROOT, SRC
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.weights import load_weights
from evals.gold import gold_hit
from scripts.migrate_to_pydantic_evals import load_eval_cases
            from dspy_modules.retriever.rerank import per_file_cap as _cap
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Tiny weight grid sweep for stability - 30-second sweep to lock in best combo per-tag.
"""

# bootstrap
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
src_dir = os.path.join(repo_root, "src")
sys.path.insert(0, repo_root)
sys.path.insert(0, src_dir)

GRID = {
    "w_path": [2.0, 2.2, 2.4],
    "w_short": [1.8, 2.0, 2.2],
    "w_title": [1.4, 1.6],
    "w_bm25": [1.0, 1.1],
    "w_vec": [1.1, 1.2],
    "adjacency_db": [0, 1],
    "per_file_cap": [4, 5],
}

def eval_combo(ws: dict[str, float], cases: list[Any]) -> tuple[int, dict[str, int], dict[str, int]]:
    """Evaluate a weight combination and return hits, tag_hits, tag_total."""
    hits = 0
    tag_hits = defaultdict(int)
    tag_total = defaultdict(int)

    for case in cases:
        try:
            # Support both legacy 'tag' and newer 'tags' fields
            tag = getattr(case, "tag", None)
            if tag is None:
                tags_list = getattr(case, "tags", []) or []
                tag = tags_list[0] if tags_list else ""
            qs = build_channel_queries(case.query, tag)
            rows = run_fused_query(
                qs["short"],
                qs["title"],
                qs["bm25"],
                getattr(case, "qvec", None),
                k=25,
                use_mmr=True,
                weights={k: v for k, v in ws.items() if k.startswith("w_")},
                tag=tag,
                fname_regex=qs.get("fname_regex"),
                adjacency_db=bool(ws.get("adjacency_db", 0)),
                cold_start=bool(qs.get("cold_start", False)),
            )

            rows = _cap(rows, cap=int(ws.get("per_file_cap", 5)))
            hit = int(gold_hit(case.id, rows))
            hits += hit
            tag_total[tag] += 1
            tag_hits[tag] += hit
        except Exception as e:
            print(f"Error evaluating case {getattr(case,'id',None) or case.get('id')}: {e}")
            tag_total[tag] += 1  # Count as miss

    return hits, dict(tag_hits), dict(tag_total)

def apply_best_weights(
    best_weights: dict[str, float], min_delta: int = 0, baseline_hits: int = 0, best_hits: int = 0
) -> bool:
    """Apply best weights to retriever_weights.yaml with safety rails."""
    if (best_hits - baseline_hits) < min_delta:
        print(f"[skip] Improvement {best_hits - baseline_hits} < min_delta {min_delta}")
        return False

    cfg_path = os.getenv("RETRIEVER_WEIGHTS_FILE", "configs/retriever_weights.yaml")
    bak = f"{cfg_path}.{time.strftime('%Y%m%d_%H%M%S')}.bak"

    # Backup existing file
    if os.path.exists(cfg_path):
        shutil.copyfile(cfg_path, bak)
        print(f"[backup] Created {bak}")

    # Load existing config
    data = {}
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            data = yaml.safe_load(f) or {}

    # Update default block only, preserve per-tag overrides
    data.setdefault("default", {}).update(best_weights)

    # Ensure directory exists
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)

    # Write updated config
    with open(cfg_path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    print(f"[applied] Updated {cfg_path} (backup: {bak})")
    return True

def print_tag_metrics(tag_hits: dict[str, int], tag_total: dict[str, int], k: int = 25):
    """Print per-tag hit@K metrics with macro/micro averages."""
    print("\n📊 Per-Tag Performance:")
    print("-" * 40)

    for tag in sorted(tag_total.keys()):
        hits = tag_hits.get(tag, 0)
        total = tag_total[tag]
        hit_rate = hits / total if total > 0 else 0.0
        print(f"[tag] {tag}: {hits}/{total} hit@{k} ({hit_rate:.3f})")

    # Calculate macro and micro averages
    if tag_total:
        macro_avg = sum(tag_hits.get(tag, 0) / tag_total[tag] for tag in tag_total) / len(tag_total)
        micro_avg = sum(tag_hits.values()) / sum(tag_total.values())
        print(f"[macro] {macro_avg:.3f}  [micro] {micro_avg:.3f}")

def main():
    """Run tiny weight grid sweep."""
    parser = argparse.ArgumentParser(description="Tiny weight grid sweep for stability")
    parser.add_argument("--apply-best", action="store_true", help="Apply best weights to retriever_weights.yaml")
    parser.add_argument(
        "--min-delta", type=int, default=0, help="Minimum improvement required to apply weights (default: 0)"
    )
    parser.add_argument(
        "--min-tag-hit", type=float, default=0.0, help="Fail fast if any tag hit rate below threshold (default: 0.0)"
    )
    parser.add_argument("--tag-filter", type=str, default=None, help="Filter cases to specific tag only")

    args = parser.parse_args()

    print("🔍 Running tiny weight grid sweep for stability...")
    print("=" * 50)

    cases = load_eval_cases("gold_standard")

    # Filter cases by tag if specified
    if args.tag_filter:
        filtered = []
        for case in cases:
            tag = getattr(case, "tag", None)
            if tag is None:
                tags_list = getattr(case, "tags", []) or []
                tag = tags_list[0] if tags_list else ""
            if tag == args.tag_filter:
                filtered.append(case)
        cases = filtered
        print(f"Filtered to {len(cases)} cases for tag: {args.tag_filter}")
    else:
        print(f"Loaded {len(cases)} evaluation cases")

    # Baseline using current defaults
    baseline_ws = load_weights(tag="")
    baseline_hits, base_tag_hits, base_tag_total = eval_combo(baseline_ws, cases)

    best = None
    best_tag_hits = {}
    best_tag_total = {}
    combos = list(itertools.product(*GRID.values()))
    keys = list(GRID.keys())
    total_combos = len(combos)
    print(f"Testing {total_combos} weight combinations...")

    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = []
        for vals in combos:
            ws = dict(zip(keys, vals))
            futures.append(ex.submit(eval_combo, ws, cases))

        for i, (ws, fut) in enumerate(zip((dict(zip(keys, v)) for v in combos), futures)):
            score, tag_hits, tag_total = fut.result()

            # Check tag hit thresholds
            if args.min_tag_hit > 0:
                min_tag_rate = min(
                    tag_hits.get(tag, 0) / tag_total.get(tag, 1) for tag in tag_total if tag_total[tag] > 0
                )
                if min_tag_rate < args.min_tag_hit:
                    print(f"[skip] Tag hit rate {min_tag_rate:.3f} < threshold {args.min_tag_hit}")
                    continue

            if not best or score > best[1]:
                best = (ws, score)
                best_tag_hits = tag_hits
                best_tag_total = tag_total

            current_best_score = best[1] if best else 0
            print(f"Progress: {i+1}/{total_combos} - Current best: {current_best_score}/{len(cases)}")

    print("=" * 50)
    print("Baseline hits:", baseline_hits, "/", len(cases))

    if best is None:
        print("No valid weight combinations found!")
        return None

    print("Best weights:", best[0])
    print("Prefilter hits:", best[1], "/", len(cases), f"(+{best[1]-baseline_hits})")

    # Print per-tag metrics
    print_tag_metrics(best_tag_hits, best_tag_total)

    # Save best weights to YAML
    with open("best_weights.yaml", "w") as f:
        yaml.dump(best[0], f)
    print("Saved best weights to best_weights.yaml")

    # Apply best weights if requested
    if args.apply_best:
        apply_best_weights(best[0], args.min_delta, baseline_hits, best[1])

    return best

if __name__ == "__main__":
    main()
