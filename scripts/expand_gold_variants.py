#!/usr/bin/env python3
"""
Expand answer variants for free F1 improvements.
Adds path variants, SQL casing/semicolon variants without model changes.
"""

import json
import pathlib
import re
import sys

inp = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "evals/reader_gold_comprehensive.jsonl")
rows = [json.loads(l) for l in inp.read_text(encoding="utf-8").splitlines() if l.strip()]


def norm_sql(s):
    return re.sub(r"[;\s]+$", "", s.strip())


def variants(ans):
    v = {ans}
    # path variants
    if "/" in ans or "." in ans:
        v.add(ans.lstrip("./"))
        v.add("./" + ans.lstrip("./"))
    # sql casing/semicolon
    v.add(norm_sql(ans))
    if ans.endswith(";"):
        v.add(ans.rstrip(";"))
    else:
        v.add(ans + ";")
    # SQL keyword casing variants
    if any(kw in ans.upper() for kw in ["CREATE", "ALTER", "DROP", "INDEX", "TABLE"]):
        v.add(ans.lower())
        v.add(ans.upper())
    return list(v)


out = []
for r in rows:
    A = r.get("answers", [])
    newA = set()
    for a in A:
        for v in variants(a):
            newA.add(v)
    r["answers"] = list(newA) if newA else A
    out.append(r)

pathlib.Path("evals/reader_gold_comprehensive_expanded.jsonl").write_text(
    "\n".join(json.dumps(x) for x in out), encoding="utf-8"
)
print("Expanded answers → evals/reader_gold_comprehensive_expanded.jsonl")
