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
    files = data.get("files", {})
    for fpath, entry in files.items():
        contexts = entry.get("contexts", {})
        for line_str, tests in contexts.items():
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
    for fpath, items in blob.items():
        vals = [it.get("complexity", 1) for it in items]
        cc_by_file[fpath] = stats.mean(vals) if vals else 1.0
    return cc_by_file

def parse_junit_fail_rate():
    if not JUNIT_XML.exists():
        return {}
    root = ET.fromstring(JUNIT_XML.read_text())
    fr = {}
    for case in root.iter("testcase"):
        cls = case.get("classname", "")
        name = case.get("name", "")
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
    for test_name, failures in flake_rates.items():
        if failures:
            result[test_name] = sum(failures) / len(failures)

    return result

def normalize(vals: dict):
    if not vals:
        return {}
    mx = max(vals.values()) or 1.0
    return {k: (v / mx) for k, v in vals.items()}

def main():
    by_test, by_line = parse_coverage()
    dur = parse_durations()
    churn = parse_churn()
    cc = parse_complexity()
    fail_rate = parse_junit_fail_rate()
    flake_rate = parse_flake_rates()

    unique_counts = {}
    weighted_unique = {}
    for tid, lines in by_test.items():
        uniq = 0
        wuniq = 0.0
        for line in lines:
            if len(by_line[line]) == 1:
                uniq += 1
                f = line.split(":")[0]
                w = (churn.get(f, 1)) * (cc.get(f, 1.0))
                wuniq += w
        unique_counts[tid] = uniq
        weighted_unique[tid] = wuniq

    # Optional redundancy clustering if datasketch is available
    cluster_rep = {}
    if MinHash and MinHashLSH:
        lsh = MinHashLSH(threshold=0.85, num_perm=64)
        mh_map = {}
        for tid, lines in by_test.items():
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
            rep = max(near, key=lambda t: weighted_unique.get(t, 0.0))
            for x in near:
                cluster_rep[x] = rep

    # Runtime percentiles
    all_durs = [v for v in dur.values() if v > 0]
    p90 = stats.quantiles(all_durs, n=10)[-1] if all_durs else 0
    runtime_pct = {t: (min(1.0, dur.get(t, 0) / p90) if p90 else 0.0) for t in by_test}

    # Change coupling
    avg_churn = {}
    for tid, lines in by_test.items():
        files = {l.split(":")[0] for l in lines}
        val = stats.mean([churn.get(f, 0) for f in files]) if files else 0
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
            W_UC * N_wuniq.get(tid, 0)
            + W_FR * N_fr.get(tid, 0)
            + W_CC * N_ccoup.get(tid, 0)
            + W_MUT * mutation_score.get(tid, 0)
            + W_COST * N_cost.get(tid, 0)
            + W_FLAKE * flake_rate.get(tid, 0)
        )

    rows = []
    for tid in by_test:
        s = score(tid)
        uniq = unique_counts.get(tid, 0)
        rep = int(cluster_rep.get(tid, tid) == tid) if cluster_rep else 0
        decision = "keep" if (s >= 0.6 or uniq > 0) else ("quarantine" if s >= 0.3 else "retire")
        rows.append(
            {
                "test_id": tid,
                "score": round(s, 4),
                "unique_lines": uniq,
                "weighted_unique": round(weighted_unique.get(tid, 0), 2),
                "runtime_sec": round(dur.get(tid, 0.0), 3),
                "fail_rate": N_fr.get(tid, 0.0),
                "flake_rate": flake_rate.get(tid, 0.0),
                "avg_churn": round(avg_churn.get(tid, 0), 2),
                "cluster_rep": rep,
                "decision": decision,
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (-r["score"], r["test_id"])))
    print(f"Wrote {OUT_CSV} with {len(rows)} rows")

if __name__ == "__main__":
    main()
