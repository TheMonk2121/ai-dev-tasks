from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.utils.gold_loader import load_gold_cases

#!/usr/bin/env python3

sys.path.append(".")

PATH = "evals/gold/v1/gold_cases.jsonl"


def main() -> Any:
    cases = load_gold_cases(PATH)
    by_mode = Counter(c.mode for c in cases)
    by_tag = Counter(t for c in cases for t in c.tags)
    print(f"Total cases: {len(cases)}")
    print("Modes:", dict(by_mode))
    print("Top tags:", by_tag.most_common())

    # sanity: each record has supervision target
    bad = []
    for c in cases:
        if not any([c.gt_answer, c.expected_files, c.globs, c.expected_decisions]):
            bad.append(c.id)
    if bad:
        print("⚠️ No supervision in:", bad[:20])

    # simple category counts
    cats = Counter(c.category or "uncat" for c in cases)
    print("Categories:", dict(cats))

    # tag → ids (to spot dominance)
    tag2ids = defaultdict(list)
    for c in cases:
        for t in c.tags:
            tag2ids[t].append(c.id)
    print("\nTag coverage (showing up to 5 IDs/tag):")
    for t, ids in by_tag.most_common():
        print(f" - {t}: {len(tag2ids[t])} eg: {tag2ids[t][:5]}")


if __name__ == "__main__":
    main()
