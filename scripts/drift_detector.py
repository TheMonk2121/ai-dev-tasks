#!/usr/bin/env python3
import os, json, sys, datetime as dt

RETR_LATEST = "evals/latest_retrieval_metrics.json"
RETR_BASE   = "evals/baseline_metrics.json"
READ_LATEST = "evals/latest_reader_metrics.json"
READ_BASE   = "evals/baseline_reader_metrics.json"

MAX_RETR_DRIFT = float(os.getenv("MAX_RETR_WEEKLY_DRIFT", "0.02"))
MAX_READ_DRIFT = float(os.getenv("MAX_READ_WEEKLY_DRIFT", "0.03"))

def load(path):
    return json.load(open(path,"r",encoding="utf-8")) if os.path.exists(path) else None

def drift(latest, base):
    if not latest or not base: return None
    return latest.get("micro",0.0) - base.get("micro",0.0)

if __name__ == "__main__":
    retr_d = drift(load(RETR_LATEST), load(RETR_BASE))
    read_d = drift(load(READ_LATEST), load(READ_BASE))
    report = {
        "timestamp": dt.datetime.utcnow().isoformat()+"Z",
        "retrieval_drift": retr_d,
        "reader_drift": read_d,
        "limits": {"retrieval": MAX_RETR_DRIFT, "reader": MAX_READ_DRIFT}
    }
    print(json.dumps(report, indent=2))
    bad = False
    if retr_d is not None and retr_d < -MAX_RETR_DRIFT:
        print(f"ALERT: retrieval drift {retr_d:.3f} below limit {-MAX_RETR_DRIFT:.3f}"); bad=True
    if read_d is not None and read_d < -MAX_READ_DRIFT:
        print(f"ALERT: reader drift {read_d:.3f} below limit {-MAX_READ_DRIFT:.3f}"); bad=True
    sys.exit(1 if bad else 0)
