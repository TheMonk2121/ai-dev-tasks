#!/usr/bin/env python3
"""
Extracts hardcoded GOLD sets and writes them into evals/gold/v1/gold_cases.jsonl
Run once, then delete the hardcoded dicts.
"""
import json
import re
from pathlib import Path

out = Path("evals/gold/v1/gold_cases.jsonl")
out.parent.mkdir(parents=True, exist_ok=True)

lines = []

# 1) Extract from dspy-rag-system/eval_gold.py
try:
    with open("dspy-rag-system/eval_gold.py", "r") as f:
        content = f.read()

    # Extract GOLD dict
    gold_match = re.search(r"GOLD:\s*Dict\[str,\s*Dict\[str,\s*Any\]\]\s*=\s*\{([^}]+)\}", content, re.DOTALL)
    if gold_match:
        gold_content = gold_match.group(1)
        # Simple parsing for the 2 GOLD entries
        if '"What is DSPy according to 400_07_ai-frameworks-dspy.md?"' in gold_content:
            lines.append(
                {
                    "id": "EVAL_GOLD_0001",
                    "mode": "retrieval",
                    "query": "What is DSPy according to 400_07_ai-frameworks-dspy.md?",
                    "tags": ["rag_qa_single"],
                    "expected_files": ["400_07_ai-frameworks-dspy.md"],
                    "notes": "Ported from dspy-rag-system/eval_gold.py GOLD",
                }
            )
        if '"List the core workflow guides in 000_core."' in gold_content:
            lines.append(
                {
                    "id": "EVAL_GOLD_0002",
                    "mode": "retrieval",
                    "query": "List the core workflow guides in 000_core.",
                    "tags": ["rag_qa_single"],
                    "globs": ["000_core/*.md"],
                    "notes": "Ported from dspy-rag-system/eval_gold.py GOLD",
                }
            )

    # Extract ADDITIONAL_GOLD dict entries
    additional_entries = [
        (
            "According to 400_06_memory-and-context-systems.md, what is the memory system in this project?",
            "400_06_memory-and-context-systems.md",
            "EVAL_GOLD_ADD_0001",
        ),
        (
            "Where are the model configuration settings defined?",
            "200_setup/201_model-configuration.md",
            "EVAL_GOLD_ADD_0002",
        ),
        (
            "What are the naming conventions used in this repo (see 200_setup)?",
            "200_setup/200_naming-conventions.md",
            "EVAL_GOLD_ADD_0003",
        ),
        ("Show the DSPy development context TL;DR.", "104_dspy-development-context.md", "EVAL_GOLD_ADD_0004"),
        ("Which file summarizes backlog and priorities?", "000_backlog.md", "EVAL_GOLD_ADD_0005"),
        (
            "Which file defines the governance and AI constitution?",
            "400_02_governance-and-ai-constitution.md",
            "EVAL_GOLD_ADD_0006",
        ),
        (
            "Where are database troubleshooting patterns documented?",
            "100_memory/100_database-troubleshooting-patterns.md",
            "EVAL_GOLD_ADD_0007",
        ),
        ("Which file describes the memory/context workflow?", "103_memory-context-workflow.md", "EVAL_GOLD_ADD_0008"),
        ("Give the high-level getting started index.", "400_00_getting-started-and-index.md", "EVAL_GOLD_ADD_0009"),
    ]

    for query, file_path, case_id in additional_entries:
        lines.append(
            {
                "id": case_id,
                "mode": "retrieval",
                "query": query,
                "tags": ["rag_qa_single"],
                "expected_files": [file_path],
                "notes": "Ported from dspy-rag-system/eval_gold.py ADDITIONAL_GOLD",
            }
        )

    # Add namespace queries
    lines.append(
        {
            "id": "EVAL_GOLD_ADD_0010",
            "mode": "retrieval",
            "query": "Show me the setup docs under 200_setup.",
            "tags": ["rag_qa_single"],
            "globs": ["200_setup/*.md"],
            "notes": "Ported from dspy-rag-system/eval_gold.py ADDITIONAL_GOLD (namespace)",
        }
    )

    lines.append(
        {
            "id": "EVAL_GOLD_ADD_0011",
            "mode": "retrieval",
            "query": "Point me to memory-related guides under 100_memory.",
            "tags": ["rag_qa_single"],
            "globs": ["100_memory/*.md"],
            "notes": "Ported from dspy-rag-system/eval_gold.py ADDITIONAL_GOLD (namespace)",
        }
    )

    print(f"✅ Exported {len([l for l in lines if l['id'].startswith('EVAL_GOLD_')])} eval_gold cases")

except Exception as e:
    print(f"⚠️ eval_gold extraction failed: {e}")

# 2) Extract decision cases from evaluation_harness.py
decision_queries = [
    (
        "postgresql",
        ["use_postgresql_with_e586cb3c2389", "postgresql_with_pgvector_5931f6780a53"],
        "Database technology choice",
    ),
    (
        "hybrid search",
        ["implement_a_hybrid_bdfdbadd8cc2", "a_hybrid_search_417c35cf99d5"],
        "Search system architecture",
    ),
    (
        "vector search",
        ["use_postgresql_with_e586cb3c2389", "postgresql_with_pgvector_5931f6780a53"],
        "Vector search implementation",
    ),
    ("database choice", ["use_postgresql_with_e586cb3c2389"], "Database selection decision"),
    ("search optimization", ["implement_a_hybrid_bdfdbadd8cc2"], "Search performance optimization"),
    (
        "pgvector",
        ["use_postgresql_with_e586cb3c2389", "postgresql_with_pgvector_5931f6780a53"],
        "Vector extension choice",
    ),
    ("BM25", ["implement_a_hybrid_bdfdbadd8cc2"], "Text search algorithm"),
    ("memory system", [], "Memory system architecture (no decisions yet)"),
    ("API design", [], "API design decisions (no decisions yet)"),
]

for i, (query, decisions, description) in enumerate(decision_queries, 1):
    lines.append(
        {
            "id": f"DECISION_{i:03d}",
            "mode": "decision",
            "query": query,
            "tags": ["meta_ops"],
            "expected_decisions": decisions,
            "notes": f"Ported from evaluation_harness.create_gold_set() - {description}",
        }
    )

print(f"✅ Exported {len(decision_queries)} decision cases")

# Write to file
with out.open("w") as f:
    for row in lines:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"📝 Wrote {len(lines)} total cases to {out}")
print("🎯 Next: Delete hardcoded dicts and update evaluation scripts")
