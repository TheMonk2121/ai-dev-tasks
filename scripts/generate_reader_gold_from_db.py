#!/usr/bin/env python3
"""
Generate comprehensive reader gold cases from existing database.
Uses the chunked data from 100_ to 500_ directories already in the database.
"""

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor

# Add project paths (repo root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from _bootstrap import ROOT, SRC  # noqa: F401

sys.path.insert(0, str(SRC))

from dspy_modules.reader.sentence_select import select_sentences
from dspy_modules.retriever.query_rewrite import PHRASE_HINTS

from common.case_id import canonical_case_id


def get_db_connection():
    """Get database connection from environment or default."""
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    # Handle mock DSN for testing
    if dsn.startswith("mock://"):
        dsn = "postgresql://danieljacobs@localhost:5432/ai_agency"
    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)


def generate_reader_gold_cases(target_count: int = 20) -> List[Dict[str, Any]]:
    """Generate reader gold cases from database chunks."""
    cases = []

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get diverse chunks from different directories
            cur.execute(
                """
                SELECT 
                    dc.id AS chunk_id,
                    COALESCE(dc.embedding_text, dc.content) AS content_text,
                    d.file_path,
                    d.filename,
                    LENGTH(COALESCE(dc.embedding_text, dc.content)) as content_length
                FROM document_chunks dc
                LEFT JOIN documents d ON d.id = dc.document_id
                WHERE COALESCE(dc.embedding_text, dc.content) IS NOT NULL 
                  AND LENGTH(COALESCE(dc.embedding_text, dc.content)) BETWEEN 200 AND 2000
                  AND (LOWER(d.file_path) LIKE '100_%' OR LOWER(d.file_path) LIKE '200_%' 
                       OR LOWER(d.file_path) LIKE '300_%' OR LOWER(d.file_path) LIKE '400_%' 
                       OR LOWER(d.file_path) LIKE '500_%')
                ORDER BY RANDOM()
                LIMIT 120
            """
            )  # oversample to allow filtering

            rows = cur.fetchall()

            # Generate questions and answers for each chunk
            for i, row in enumerate(rows):
                # Type cast to help the type checker understand this is a dict-like object
                row_dict: Dict[str, Any] = row  # type: ignore
                content = row_dict.get("content_text") or ""
                file_path = row_dict.get("file_path") or ""
                filename = row_dict.get("filename") or ""

                # Skip if content is too short or too long
                if len(content) < 100 or len(content) > 1500:
                    continue

                # Generate different types of questions based on content
                case = generate_question_answer_pair(content, file_path, filename, i)
                if case:
                    cases.append(case)

                if len(cases) >= target_count:
                    break

    return cases


def _guess_tag(file_path: str) -> str:
    fp = (file_path or "").lower()
    if any(key in fp for key in ["/db/", ".sql", "migrations", "ivfflat", "index.sql"]):
        return "db_workflows"
    if any(key in fp for key in ["/ops/", "zsh", "shell", "health", "canary", "deploy"]):
        return "meta_ops" if ("canary" in fp or "deploy" in fp) else "ops_health"
    return "rag_qa_single"


def generate_question_answer_pair(content: str, file_path: str, filename: str, index: int) -> Dict[str, Any]:
    """Generate a question-answer pair from content."""

    # Extract key information from content
    lines = content.split("\n")
    title = None
    key_concepts = []

    # Find title (first # heading)
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Extract key concepts (words in backticks, bold, or capitalized)
    import re

    concepts = re.findall(r"`([^`]+)`", content)
    concepts.extend(re.findall(r"\*\*([^*]+)\*\*", content))
    concepts.extend(re.findall(r"\b([A-Z][A-Z_]+)\b", content))

    # Filter and clean concepts
    key_concepts = [c for c in concepts if len(c) > 2 and len(c) < 30][:5]

    # Generate question based on content type
    if "DSPy" in content:
        question = f"What is DSPy according to {filename}?"
        answers = [
            "a framework for declarative optimization of prompts and programs",
            "declarative optimization framework for LLM prompts/programs",
        ]
    elif "memory" in content.lower() and "system" in content.lower():
        question = f"What is the memory system described in {filename}?"
        answers = [
            "a sophisticated memory context system to maintain state across AI sessions",
            "memory context system for maintaining state across sessions",
        ]
    elif "workflow" in content.lower() and "template" in content.lower():
        question = f"What workflow templates are mentioned in {filename}?"
        answers = [
            "evaluation system entry point, PRD creation template, task generation template, and task processing template",
            "core workflow guides include evaluation system entry point, PRD creation template, task generation template, and task processing template",
        ]
    elif title and len(title) > 10:
        question = f"What is {title} according to {filename}?"
        # Extract first sentence as answer
        first_sentence = content.split(".")[0] + "."
        if len(first_sentence) > 200:
            first_sentence = first_sentence[:200] + "..."
        answers = [first_sentence]
    elif key_concepts:
        concept = key_concepts[0]
        question = f"What is {concept} according to {filename}?"
        # Find sentence containing the concept
        sentences = content.split(".")
        for sentence in sentences:
            if concept.lower() in sentence.lower():
                answer = sentence.strip() + "."
                if len(answer) > 200:
                    answer = answer[:200] + "..."
                answers = [answer]
                break
        else:
            answers = [f"{concept} is mentioned in {filename}"]
    else:
        # Generic question
        question = f"What is the main topic discussed in {filename}?"
        first_sentence = content.split(".")[0] + "."
        if len(first_sentence) > 200:
            first_sentence = first_sentence[:200] + "..."
        answers = [first_sentence]

    # Use sentence selection to refine the answer to a grounded sentence
    try:
        tag = _guess_tag(file_path)
        phrase_hints = PHRASE_HINTS.get(tag, [])
        rows = [
            {
                "file_path": file_path,
                "filename": filename,
                "embedding_text": content,
                "chunk_id": index,
                "score": 1.0,
            }
        ]
        compact, chosen = select_sentences(rows, question, tag, phrase_hints, per_chunk=2, total=1)
        if chosen:
            answers = [chosen[0]["sentence"]]
    except Exception:
        pass

    source_path = file_path or ""
    case_id = canonical_case_id(question, source_path)
    return {
        "id": case_id,
        "query": question,
        "source_path": source_path,
        "answers": answers,
        "tag": _guess_tag(file_path),
        "source": "database_generated",
        "meta": {"dataset_version": datetime.utcnow().strftime("v%Y-%m-%d")},
    }


def main():
    """Generate comprehensive reader gold cases."""
    print("🔍 Generating reader gold cases from database...")

    # Generate cases
    cases = generate_reader_gold_cases(target_count=30)

    print(f"Generated {len(cases)} reader gold cases")

    # Create dev/test splits (70/30)
    random.seed(42)
    random.shuffle(cases)
    k = int(0.7 * len(cases))
    dev_cases = cases[:k]
    test_cases = cases[k:]

    # Ensure directories exist
    Path("evals/dspy").mkdir(parents=True, exist_ok=True)

    # Save splits
    with open("evals/dspy/dev.jsonl", "w", encoding="utf-8") as f:
        for case in dev_cases:
            f.write(json.dumps(case) + "\n")

    with open("evals/dspy/test.jsonl", "w", encoding="utf-8") as f:
        for case in test_cases:
            f.write(json.dumps(case) + "\n")

    # Also save combined for reference
    with open("evals/reader_gold_comprehensive.jsonl", "w", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")

    print(f"✅ Saved {len(dev_cases)} dev cases and {len(test_cases)} test cases")
    print("📁 Files created:")
    print(f"   - evals/dspy/dev.jsonl ({len(dev_cases)} cases)")
    print(f"   - evals/dspy/test.jsonl ({len(test_cases)} cases)")
    print(f"   - evals/reader_gold_comprehensive.jsonl ({len(cases)} cases)")

    # Show sample cases
    print("\n📋 Sample dev cases:")
    for i, case in enumerate(dev_cases[:3]):
        print(f"   {i+1}. {case['query']}")
        print(f"      Answer: {case['answers'][0][:100]}...")

    print("\n📋 Sample test cases:")
    for i, case in enumerate(test_cases[:2]):
        print(f"   {i+1}. {case['query']}")
        print(f"      Answer: {case['answers'][0][:100]}...")


if __name__ == "__main__":
    main()
