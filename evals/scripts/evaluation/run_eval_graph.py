from __future__ import annotations

import argparse
import json
from pathlib import Path

from graphs.persistence_graph import PgStatePersistence
from src.graphs.eval_graph import build_graph

#!/usr/bin/env python3


def main() -> None:
    ap = argparse.ArgumentParser(description="Run eval graph with Postgres persistence")
    _ = ap.add_argument("--run-id", default=None, help="Run id; defaults to timestamp-based")
    _ = ap.add_argument("--gold-file", default="evals/gold/v1/gold_cases.jsonl")
    _ = ap.add_argument("--out", default="metrics/graph_runs", help="Output directory for snapshot log JSON")
    args = ap.parse_args()

    run_id = args.run_id or f"run_{int(__import__('time').time())}"
    persist = PgStatePersistence(run_id)
    g = build_graph()

    # Minimal execution: load cases, retrieve for the first case, score
    cases = g.nodes[0].run(args.gold_file)  # type: ignore[attr-defined]
    if not cases:
        raise SystemExit("No cases loaded")
    first = cases[0]

    sid = persist.snapshot_node({"stage": "retrieve", "query": first.get("query")}, {"node": "Retrieve"})
    with persist.record_run(sid):
        cands = g.nodes[1].run(first.get("query", ""))  # type: ignore[attr-defined]

    sid2 = persist.snapshot_node({"stage": "score", "case_id": first.get("id")}, {"node": "Score"})
    with persist.record_run(sid2):
        result = g.nodes[2].run(  # type: ignore[attr-defined]
            case_id=str(first.get("id")),
            mode=str(first.get("mode")),
            tags=list(first.get("tags") or []),
            query=str(first.get("query")),
            candidates=cands,
        )
    _ = persist.snapshot_end({"stage": "done"}, {"ok": True})

    # Write snapshot log
    out_dir = Path(args.out)
    _ = out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / f"{run_id}.json"
    log = {"run_id": run_id, "snapshots": persist.load_all(), "result": json.loads(result.model_dump_json())}
    _ = log_path.write_text(json.dumps(log, indent=2))
    print(f"✅ Graph run complete → {log_path}")


if __name__ == "__main__":
    main()
