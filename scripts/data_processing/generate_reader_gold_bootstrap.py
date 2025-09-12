from __future__ import annotations
import json
import os
import random
import re
import psycopg2
from psycopg2.extras import DictCursor
#!/usr/bin/env python3
"""
Bootstrap Q/A from Postgres content -> JSONL you will CURATE.
Env:
  - DATABASE_URL=postgresql://user:pass@host:port/db (or POSTGRES_DSN)
  - OUT_FILE=300_evals/data/reader_gold_bootstrap.jsonl (optional)
  - MAX_PER_TAG=60 (optional)
  - SEED=42 (optional)
"""

DSN = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN")
OUT = os.getenv("OUT_FILE", "300_evals/data/reader_gold_bootstrap.jsonl")
MAX_PER_TAG = int(os.getenv("MAX_PER_TAG", "60"))
SEED = int(os.getenv("SEED", "42"))

TAG_RULES = [
    ("db_workflows", re.compile(r"(^|/)(db|database|migrations?|sql)(/|$)|\.(sql)$", re.I)),
    ("ops_health", re.compile(r"(^|/)(ops|scripts|shell|setup)(/|$)|\.(sh|bash|zsh)$", re.I)),
    ("meta_ops", re.compile(r"(^|/)(meta|deploy|canary|checks?)(/|$)", re.I)),
    ("rag_qa_single", re.compile(r".", re.I)),  # catch-all
]

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

def guess_tag(path: str) -> str:
    lp = (path or "").lower()
    for tag, rx in TAG_RULES:
        if rx.search(lp):
            return tag
    return "rag_qa_single"

def first_sentence(text: str) -> str:
    if not text:
        return ""
    sents = SENT_SPLIT.split(text.strip())
    return (sents[0] if sents else text).strip()

def mk_question(path: str, section: str | None) -> str:
    base = (path or "").split("/")[-1]
    if section:
        return f"What does {base} explain about '{section}'?"
    return f"What is the main purpose of {base}?"

def main():
    assert DSN, "Set DATABASE_URL or POSTGRES_DSN"
    random.seed(SEED)
    conn = psycopg2.connect(DSN)
    cur = conn.cursor(cursor_factory=DictCursor)

    # Pull representative chunks with filenames, paths; section_title may not exist, so NULL
    cur.execute(
        """
        SELECT 
            COALESCE(dc.chunk_id::text, dc.id::text) AS chunk_id,
            COALESCE(dc.embedding_text, dc.content) AS embedding_text,
            NULL::text AS section_title,
            dc.filename,
            d.file_path
        FROM document_chunks dc
        LEFT JOIN documents d ON d.id = dc.document_id
        WHERE COALESCE(dc.embedding_text, dc.content) IS NOT NULL
          AND length(COALESCE(dc.embedding_text, dc.content)) > 120
        LIMIT 5000
        """
    )
    rows = cur.fetchall()
    conn.close()

    buckets: dict[str, list[dict]] = {"db_workflows": [], "ops_health": [], "meta_ops": [], "rag_qa_single": []}
    for r in rows:
        path = r["file_path"] or r["filename"] or ""
        tag = guess_tag(path)
        q = mk_question(path, r["section_title"])
        a = first_sentence(r["embedding_text"])[:180]
        if len(a) < 40:
            continue  # skip flimsy answers
        case_id = q  # align id with query for bootstrap
        item = {"case_id": case_id, "query": q, "answers": [a], "tag": tag, "file_path": path}
        buckets[tag].append(item)

    for tag in list(buckets.keys()):
        random.shuffle(buckets[tag])

    out: list[dict] = []
    for tag, items in buckets.items():
        out.extend(items[:MAX_PER_TAG])

    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for row in out:
            f.write(json.dumps(row) + "\n")
    print(f"Wrote {len(out)} bootstrap Q/A to {OUT}. CURATE before using in gates.")

if __name__ == "__main__":
    main()