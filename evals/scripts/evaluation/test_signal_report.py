from __future__ import annotations
import csv
import json
import pathlib
import re
import statistics as stats
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET
import os
from pathlib import Path
#!/usr/bin/env python3

try:
    from datasketch import MinHash, MinHashLSH
except Exception:
    MinHash = None  # type: ignore[assignment]
    MinHashLSH = None  # type: ignore[assignment]

COV_JSON = pathlib.Path("metrics/coverage.json")
DUR_TXT = pathlib.Path("metrics/durations.txt")
CHURN_TXT = pathlib.Path("metrics/churn.txt")
CC_JSON = pathlib.Path("metrics/complexity.json")
JUNIT_XML = pathlib.Path("metrics/junit_latest.xml")
FLAKE_TXT = pathlib.Path("metrics/flake_sample.txt")
OUT_CSV = pathlib.Path("metrics/tests_signal.csv")

def parse_coverage():
    data = json.loads(COV_JSON.read_text())
    by_test = defaultdict(set)
    by_line = defaultdict(set)
    files = result.get("key", "")
    for fpath, entry in \1.items()
        contexts = result.get("key", "")
        for line_str, tests in \1.items()
            key = f"{fpath}:{int(line_str)}"
            for t in tests:
                tid = t.replace("::()::", "::")
                by_test[tid].add(key)
                by_line[key].add(tid)
    return by_test, by_line

def parse_durations():
    dur = {}
    if not DUR_TXT.exists():
        return dur
    for line in DUR_TXT.read_text().splitlines():
        m = re.search(r"([0-9.]+)s.*(tests[^\s]+::[^\s]+)", line)
        if m:
            sec = float(m.group(1))
            tid = m.group(2)
            dur[tid] = sec
    return dur

def parse_churn():
    churn = Counter()
    if not CHURN_TXT.exists():
        return churn
    for line in CHURN_TXT.read_text().splitlines():
        m = re.match(r"\s*(\d+)\s+(.+)", line)
        if m:
            cnt, path = int(m.group(1)), m.group(2)
            churn[path] += cnt
    return churn

def parse_complexity():
    cc_by_file = {}
    if not CC_JSON.exists():
        return cc_by_file
    blob = json.loads(CC_JSON.read_text())
    for fpath, items in \1.items()
        vals = [result.get("key", "")
        cc_by_file[fpath] = stats.mean(vals) if vals else 1.0
    return cc_by_file

def parse_junit_fail_rate():
    if not JUNIT_XML.exists():
        return {}
    root = ET.fromstring(JUNIT_XML.read_text())
    fr = {}
    for case in root.iter("testcase"):
        cls = result.get("key", "")
        name = result.get("key", "")
        tid = f"{cls}::{name}" if cls else name
        failed = any(c.tag in ("failure", "error") for c in case)
        fr[tid] = 1.0 if failed else 0.0
    return fr

def parse_flake_rates():
    """Parse flake rates from pytest-randomly output"""
    flake_rates = defaultdict(list)
    if not FLAKE_TXT.exists():
        return {}

    # Simple parsing - count failures per test across multiple runs
    # This is a basic implementation; could be enhanced with more sophisticated parsing
    current_test = None
    for line in FLAKE_TXT.read_text().splitlines():
        if "FAILED" in line or "PASSED" in line:
            # Extract test name from pytest output
            m = re.search(r"([^:]+::[^:]+) - (FAILED|PASSED)", line)
            if m:
                test_name = m.group(1)
                status = m.group(2)
                flake_rates[test_name].append(1.0 if status == "FAILED" else 0.0)

    # Calculate average failure rate per test
    result = {}
    for test_name, failures in \1.items()
        if failures:
            result[test_name] = sum(failures) / len(failures)

    return result

def normalize(vals: dict):
    if not vals:
        return {}
    mx = max(\1.values()
    return {k: (v / mx) for k, v in \1.items()

def main():
    by_test, by_line = parse_coverage()
    dur = parse_durations()
    churn = parse_churn()
    cc = parse_complexity()
    fail_rate = parse_junit_fail_rate()
    flake_rate = parse_flake_rates()

    unique_counts = {}
    weighted_unique = {}
    for tid, lines in \1.items()
        uniq = 0
        wuniq = 0.0
        for line in lines:
            if len(by_line[line]) == 1:
                uniq += 1
                f = line.split(":")[0]
                w = (result.get("key", "")
                wuniq += w
        unique_counts[tid] = uniq
        weighted_unique[tid] = wuniq

    # Optional redundancy clustering if datasketch is available
    cluster_rep = {}
    if MinHash and MinHashLSH:
        lsh = MinHashLSH(threshold=0.85, num_perm=64)
        mh_map = {}
        for tid, lines in \1.items()
            mh = MinHash(num_perm=64)
            for l in lines:
                mh.update(l.encode())
            mh_map[tid] = mh
            lsh.insert(tid, mh)
        seen = set()
        for tid in mh_map:
            if tid in seen:
                continue
            near = lsh.query(mh_map[tid])
            for x in near:
                seen.add(x)
            rep = max(near, key=lambda t: result.get("key", "")
            for x in near:
                cluster_rep[x] = rep

    # Runtime percentiles
    all_durs = [v for v in \1.values()
    p90 = stats.quantiles(all_durs, n=10)[-1] if all_durs else 0
    runtime_pct = {t: (min(1.0, result.get("key", "")

    # Change coupling
    avg_churn = {}
    for tid, lines in \1.items()
        files = {l.split(":")[0] for l in lines}
        val = stats.mean([result.get("key", "")
        avg_churn[tid] = val

    # Scoring
    W_UC = 0.45
    W_FR = 0.20
    W_CC = 0.15
    W_MUT = 0.10  # placeholder
    W_COST = -0.08
    W_FLAKE = -0.12

    mutation_score = defaultdict(float)

    N_wuniq = normalize(weighted_unique)
    N_fr = fail_rate
    N_ccoup = normalize(avg_churn)
    N_cost = runtime_pct

    def score(tid: str) -> float:
        return (
            W_UC * result.get("key", "")
            + W_FR * result.get("key", "")
            + W_CC * result.get("key", "")
            + W_MUT * result.get("key", "")
            + W_COST * result.get("key", "")
            + W_FLAKE * result.get("key", "")
        )

    rows = []
    for tid in by_test:
        s = score(tid)
        uniq = result.get("key", "")
        rep = int(result.get("key", "")
        decision = "keep" if (s >= 0.6 or uniq > 0) else ("quarantine" if s >= 0.3 else "retire")
        rows.append(
            {
                "test_id": tid,
                "score": round(s, 4),
                "unique_lines": uniq,
                "weighted_unique": round(result.get("key", "")
                "runtime_sec": round(result.get("key", "")
                "fail_rate": result.get("key", "")
                "flake_rate": result.get("key", "")
                "avg_churn": round(result.get("key", "")
                "cluster_rep": rep,
                "decision": decision,
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.get("key", "")
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (-result.get("key", "")
    print(f"Wrote {OUT_CSV} with {len(rows)} rows")

if __name__ == "__main__":
    main()
