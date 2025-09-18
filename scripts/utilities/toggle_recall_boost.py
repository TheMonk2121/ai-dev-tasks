from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Optional, Union

import yaml

#!/usr/bin/env python3
"""
Toggle recall boost settings in config/retrieval.yaml with safety:

- apply: raises recall-oriented params (per Entry Point Recall Playbook)
- revert: restores the exact prior values (from saved state)

Atomicity & provenance:
- Before applying, writes a timestamped backup copy of retrieval.yaml under
  metrics/derived_configs/recall_boost_backups/
- Saves a state file with the previous values to restore later

Usage:
  python3 scripts/toggle_recall_boost.py apply
  python3 scripts/toggle_recall_boost.py revert

After applying, run a smoke test then a full eval:
  ./scripts/run_ragchecker_smoke_test.sh
  source throttle_free_eval.sh && python3 scripts/ragchecker_official_evaluation.py --bypass-cli --stable --lessons-mode advisory
"""

RETRIEVAL_YAML = Path("config/retrieval.yaml")
BACKUP_DIR = Path("metrics/derived_configs/recall_boost_backups")
STATE_FILE = Path("metrics/derived_configs/recall_boost_state.json")

# Target recall boost settings (from Entry Point Recall Playbook)
TARGET = {
    ("candidates", "final_limit"): 80,
    ("rerank", "final_top_n"): 12,
    ("rerank", "alpha"): 0.6,
    ("prefilter", "min_bm25_score"): 0.05,
    ("prefilter", "min_vector_score"): 0.65,
}

def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r") as f:
        return yaml.safe_load(f) or {}

def _dump_yaml(path: Path, data: dict[str, Any]) -> None:
    with path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def _ensure_dirs() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def _backup_file(src: Path) -> Path:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = BACKUP_DIR / f"retrieval_{ts}.yaml"
    dst.write_bytes(src.read_bytes())
    return dst

def _get(d: dict[str, Any], k1: str, k2: str) -> Any:
    return (d.get(k1) or {}).get(k2)

def _set(d: dict[str, Any], k1: str, k2: str, val: Any) -> None:
    if k1 not in d or not isinstance(d[k1], dict):
        d[k1] = {}
    d[k1][k2] = val

def apply() -> None:
    if not RETRIEVAL_YAML.exists():
        raise FileNotFoundError(f"Missing {RETRIEVAL_YAML}")

    _ensure_dirs()
    backup_path = _backup_file(RETRIEVAL_YAML)

    data = _load_yaml(RETRIEVAL_YAML)

    # Capture previous values to state (for precise revert)
    prev: dict[tuple[str, str], Any] = {}
    for (k1, k2), target_val in TARGET.items():
        prev[(k1, k2)] = _get(data, k1, k2)
        _set(data, k1, k2, target_val)

    _dump_yaml(RETRIEVAL_YAML, data)

    # Save state
    state = {
        "backup_path": str(backup_path),
        "previous_values": {f"{k1}.{k2}": v for (k1, k2), v in prev.items()},
        "applied_at": dt.datetime.now().isoformat(),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2))

    print("✅ recall_boost applied.")
    print(f"📝 Backup: {backup_path}")
    print(f"🧭 State:  {STATE_FILE}")
    print("➡️  Next: run smoke test, then full eval.")

def revert() -> None:
    if not STATE_FILE.exists():
        raise FileNotFoundError("No state file found — nothing to revert. Run apply first.")

    state = json.loads(STATE_FILE.read_text())
    prev_values: dict[str, Any] = state.get("previous_values", {})

    data = _load_yaml(RETRIEVAL_YAML)

    # Restore exact prior values (including None → delete key)
    for dotted_key, prev_val in prev_values.items():
        k1, k2 = dotted_key.split(".", 1)
        if prev_val is None:
            # Remove key if it exists now
            if k1 in data and isinstance(data[k1], dict) and k2 in data[k1]:
                del data[k1][k2]
                # Clean empty dicts
                if not data[k1]:
                    del data[k1]
        else:
            _set(data, k1, k2, prev_val)

    _dump_yaml(RETRIEVAL_YAML, data)
    STATE_FILE.unlink(missing_ok=True)

    print("✅ recall_boost reverted to prior values.")
    print("➡️  Next: run smoke test, then full eval.")

def main() -> None:
    p: Any = argparse.ArgumentParser(description="Toggle recall_boost settings safely")
    p.add_argument("action", choices=["apply", "revert"], help="apply or revert recall_boost changes")
    args: Any = p.parse_args()

    if args.action == "apply":
        apply()
    else:
        revert()

if __name__ == "__main__":
    main()
