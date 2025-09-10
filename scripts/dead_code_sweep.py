#!/usr/bin/env python3
"""
Dead code sweeper using vulture to identify unreferenced code.

Combines with coverage data to flag dead code for potential removal.
"""

import argparse
import datetime
import json
import pathlib
import subprocess
import sys


def run(cmd):
    """Run command and return result"""
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def main():
    ap = argparse.ArgumentParser(description="Find dead code using vulture")
    ap.add_argument("--paths", nargs="+", default=["src", "src"])
    ap.add_argument("--min-confidence", type=int, default=80)
    ap.add_argument("--out", default="metrics/dead_code.jsonl")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # vulture output: "path:line: message (confidence)"
    cmd = ["vulture", *args.paths, f"--min-confidence={args.min_confidence}"]
    res = run(cmd)
    lines = [ln for ln in res.stdout.splitlines() if ":" in ln and "(" in ln]
    now = datetime.datetime.utcnow().isoformat()

    with out.open("w") as fh:
        for ln in lines:
            # naive parse
            try:
                path, rest = ln.split(":", 1)
                line, rest2 = rest.split(":", 1)
                msg, conf = rest2.rsplit("(", 1)
                conf = conf.strip(")% \n")
                item = {
                    "ts": now,
                    "file": path.strip(),
                    "line": int(line.strip()),
                    "message": msg.strip(),
                    "confidence": int(conf),
                }
                fh.write(json.dumps(item) + "\n")
            except Exception:
                continue
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
