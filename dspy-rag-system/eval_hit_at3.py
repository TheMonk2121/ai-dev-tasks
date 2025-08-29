#!/usr/bin/env python3
"""
Quick hit@3 before/after evaluation.

Before: naive top-3 from retriever.
After: enforce per-document cap (<=2) when selecting top-3.

Prints a simple table of query, expected, hit@3 before, hit@3 after.
"""

import os
import sys
from typing import Dict, List, Tuple

from dotenv import load_dotenv

sys.path.append("src")
from dspy_modules.hit_adapter import adapt_rows
from dspy_modules.vector_store import HybridVectorStore


def select_top3_with_cap(hits, max_per_doc: int = 2):
    selected = []
    per_doc: Dict[str, int] = {}
    for h in hits:
        doc_id = str(h.metadata.get("document_id"))
        cnt = per_doc.get(doc_id, 0)
        if cnt >= max_per_doc:
            continue
        selected.append(h)
        per_doc[doc_id] = cnt + 1
        if len(selected) == 3:
            break
    return selected


def hit_at3(filenames: List[str], expected_sub: str) -> bool:
    exp = expected_sub.lower()
    return any((f or "").lower().find(exp) != -1 for f in filenames)


def main() -> int:
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        return 1

    retriever = HybridVectorStore(db_url)

    # 15 queries with expected filename substring (editable ground truth)
    cases: List[Tuple[str, str]] = [
        ("What is DSPy according to 400_07_ai-frameworks-dspy.md?", "400_07_ai-frameworks-dspy.md"),
        ("List the core workflow guides in 000_core.", "000_core"),
        ("What is the CONTEXT_INDEX?", "100_cursor-memory-context.md"),
        ("Where are coding and prompting standards documented?", "400_05_coding-and-prompting-standards.md"),
        ("Where is the governance and AI constitution guide?", "400_02_governance-and-ai-constitution.md"),
        ("Describe the memory and context systems.", "400_06_memory-and-context-systems.md"),
        ("Show the development workflow and standards.", "400_04_development-workflow-and-standards.md"),
        ("What is in the backlog?", "000_backlog.md"),
        ("Where is the system overview and architecture?", "400_03_system-overview-and-architecture.md"),
        ("What's the project overview?", "400_project-overview.md"),
        ("Where is the context priority guide?", "400_context-priority-guide.md"),
        ("Which guides are included in the getting started index?", "400_00_getting-started-and-index.md"),
        ("Where is memory context workflow documented?", "103_memory-context-workflow.md"),
        ("Where are dspy development details?", "104_dspy-development-context.md"),
        ("Where is the codebase index discussed?", "CONTEXT_INDEX"),
    ]

    print("Query | Expected | Hit@3 Before | Hit@3 After")
    print("----- | -------- | ------------ | -----------")

    before_hits = 0
    after_hits = 0

    for q, expected in cases:
        result = retriever.forward("search", query=q, limit=12)
        if result.get("status") != "success":
            print(f"{q} | {expected} | error | error")
            continue
        rows = result.get("results", [])
        hits = adapt_rows(rows)

        # Before: naive top-3
        top3_before = hits[:3]
        before_files = [h.metadata.get("filename") for h in top3_before]
        before_ok = hit_at3(before_files, expected)

        # After: with doc cap
        top3_after = select_top3_with_cap(hits, max_per_doc=2)
        after_files = [h.metadata.get("filename") for h in top3_after]
        after_ok = hit_at3(after_files, expected)

        before_hits += int(before_ok)
        after_hits += int(after_ok)

        print(f"{q[:40]}... | {expected} | {'✔' if before_ok else '✖'} | {'✔' if after_ok else '✖'}")

    total = len(cases)
    print("\nSummary")
    print(f"Before: {before_hits}/{total} hit@3")
    print(f"After:  {after_hits}/{total} hit@3")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
