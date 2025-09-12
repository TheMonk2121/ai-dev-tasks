from __future__ import annotations
import json
from pathlib import Path
#!/usr/bin/env python3

p = Path("evals/gold/v1/gold_cases.jsonl")
seen = set()
out = []
for line in p.read_text().splitlines():
    if not line.strip():
        continue
    obj = json.loads(line)
    # Handle both "id" and "case_id" fields
    k = obj.get("id") or obj.get("case_id")
    if not k:
        print(f"Warning: No ID field in {obj}")
        continue
    if k in seen:
        continue
    seen.add(k)
    out.append(obj)
p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n")
print(f"Kept {len(out)} unique cases.")