from __future__ import annotations
import json
import os
import random
import re
import sys
from pathlib import Path
from typing import Any
    from utils.database_resilience import get_database_manager
    from utils.database_resilience import get_database_manager
    import argparse
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
DEPRECATED: Repo-Gold dataset bootstrapper.

Use evals/gold/v1/gold_cases.jsonl with src/utils/gold_loader instead.
This script remains for archival reference only.
"""

# Add DSPy RAG system to path
# sys.path.insert(0, "src")  # DSPy modules now in main src directory

# Import database utilities directly to avoid PyTorch issues
try:
except ImportError:
    # Fallback for when running from outside src directory
    # sys.path.insert(0, "src")  # DSPy modules now in main src directory

class RepoGoldDatasetBootstrap:
    """Bootstrap repo-gold dataset from existing documentation."""

    def __init__(self, db_connection_string: str = "postgresql://danieljacobs@localhost:5432/ai_agency"):
        self.db_connection = db_connection_string
        self.db_manager = get_database_manager()

        # Coverage categories as specified
        self.coverage_categories = {
            "ops_health": 6,
            "db_workflows": 6,
            "rag_qa_single": 6,
            "rag_qa_multi": 6,
            "meta_ops": 3,
            "negatives": 3,
        }

        # Total target: 30 items
        self.total_target = sum(self.coverage_categories.values())

    def sample_representative_chunks(self, target_count: int = 40) -> list[dict[str, Any]]:
        """Sample representative chunks across docs, favoring top-linked/long docs."""
        print(f"🔍 Sampling {target_count} representative chunks...")

        # Get document statistics
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM documents")
                    total_docs = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM document_chunks")
                    total_chunks = cur.fetchone()[0]
                    print(f"📊 Total documents: {total_docs}")
                    print(f"📊 Total chunks: {total_chunks}")
        except Exception as e:
            print(f"⚠️ Could not get stats: {e}")
            total_docs = total_chunks = 0

        # Sample chunks with preference for longer content and important files
        sampled_chunks = []

        try:
            # Query for chunks with good content length and metadata
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 
                            dc.id,
                            dc.document_id,
                            dc.chunk_index,
                            dc.content,
                            dc.file_path,
                            dc.metadata,
                            d.filename,
                            LENGTH(dc.content) as content_length
                        FROM document_chunks dc
                        JOIN documents d ON dc.document_id = d.id
                        WHERE dc.content IS NOT NULL 
                        AND LENGTH(dc.content) > 100
                        AND dc.metadata->>'ingest_run_id' = get_active_chunk_config()
                        ORDER BY 
                            LENGTH(dc.content) DESC,
                            CASE 
                                WHEN d.filename LIKE '%README%' THEN 1
                                WHEN d.filename LIKE '%000_core%' THEN 2
                                WHEN d.filename LIKE '%400_guides%' THEN 3
                                WHEN d.filename LIKE '%scripts%' THEN 4
                                ELSE 5
                            END,
                            d.filename,
                            dc.chunk_index
                        LIMIT %s
                    """,
                        (target_count * 2,),
                    )  # Get 2x to allow for filtering

                    rows = cur.fetchall()

                    # Filter and select diverse chunks
                    selected = []
                    seen_files = set()

                    for row in rows:
                        if len(selected) >= target_count:
                            break

                        file_path = row[4] or row[6] or "unknown"
                        content = row[3]

                        # Skip if we already have too many from this file
                        file_count = sum(1 for s in selected if (s.get("file_path") or s.get("filename")) == file_path)
                        if file_count >= 3:  # Max 3 chunks per file
                            continue

                        # Skip very short or very long chunks
                        if len(content) < 150 or len(content) > 2000:
                            continue

                        selected.append(
                            {
                                "id": row[0],
                                "document_id": row[1],
                                "chunk_index": row[2],
                                "content": content,
                                "file_path": file_path,
                                "filename": row[6],
                                "metadata": row[5] if row[5] else {},
                                "content_length": row[7],
                            }
                        )

                        seen_files.add(file_path)

                    sampled_chunks = selected

        except Exception as e:
            print(f"⚠️ Database sampling failed: {e}")
            # Fallback: create synthetic examples based on known important files
            sampled_chunks = self._create_fallback_chunks(target_count)

        print(
            f"✅ Sampled {len(sampled_chunks)} chunks from {len(set(c.get('file_path', '') for c in sampled_chunks))} files"
        )
        return sampled_chunks

    def _create_fallback_chunks(self, target_count: int) -> list[dict[str, Any]]:
        """Create fallback chunks when database sampling fails."""
        fallback_files = [
            "README.md",
            "000_core/000_backlog.md",
            "000_core/001_create-prd.md",
            "400_guides/400_system-overview.md",
            "scripts/ragchecker_official_evaluation.py",
            "src/dspy_modules/rag_pipeline.py",
        ]

        chunks = []
        for i, filename in enumerate(fallback_files[:target_count]):
            chunks.append(
                {
                    "id": f"fallback_{i}",
                    "document_id": f"doc_{i}",
                    "chunk_index": 0,
                    "content": f"Sample content from {filename} - this is a fallback chunk for dataset creation.",
                    "file_path": filename,
                    "filename": filename,
                    "metadata": {},
                    "content_length": 200,
                }
            )

        return chunks

    def extract_authoritative_sentence(self, content: str) -> str:
        """Extract a short authoritative sentence from chunk content."""
        # Look for sentences that contain actionable information
        sentences = re.split(r"[.!?]+", content)

        # Score sentences by importance indicators
        scored_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 200:
                continue

            score = 0
            # Boost for imperative verbs (commands)
            if re.search(r"\b(run|execute|create|build|install|configure|set|use|add|remove)\b", sentence.lower()):
                score += 3
            # Boost for technical terms
            if re.search(r"\b(config|script|command|file|database|index|vector|embedding)\b", sentence.lower()):
                score += 2
            # Boost for specific instructions
            if re.search(r"\b(how to|steps|procedure|process)\b", sentence.lower()):
                score += 2
            # Boost for file paths or commands
            if re.search(r"[a-zA-Z0-9_/.-]+\.(py|sh|sql|md|yaml|json)", sentence):
                score += 2

            if score > 0:
                scored_sentences.append((sentence, score))

        if scored_sentences:
            # Return highest scoring sentence
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            return scored_sentences[0][0]

        # Fallback: return first substantial sentence
        for sentence in sentences:
            sentence = sentence.strip()
            if 30 <= len(sentence) <= 150:
                return sentence

        return content[:100] + "..." if len(content) > 100 else content

    def draft_query_from_content(self, content: str, filename: str) -> str:
        """Draft a question that a competent dev/ops person would ask."""
        # Extract key concepts from content
        words = re.findall(r"\b[a-zA-Z]{3,}\b", content.lower())

        # Common question patterns
        question_templates = [
            "How do I {action}?",
            "What is {concept}?",
            "How does {concept} work?",
            "Where is {concept} configured?",
            "How to {action} {concept}?",
            "What are the steps to {action}?",
            "How do we {action}?",
            "Where can I find {concept}?",
            "How to set up {concept}?",
            "What is the process for {action}?",
        ]

        # Extract potential actions and concepts
        actions = []
        concepts = []

        for word in words:
            if word in [
                "run",
                "execute",
                "create",
                "build",
                "install",
                "configure",
                "set",
                "use",
                "add",
                "remove",
                "start",
                "stop",
                "restart",
            ]:
                actions.append(word)
            elif word in [
                "config",
                "script",
                "command",
                "file",
                "database",
                "index",
                "vector",
                "embedding",
                "evaluation",
                "rag",
                "dspy",
            ]:
                concepts.append(word)

        # Try to create a natural question
        if actions and concepts:
            action = random.choice(actions)
            concept = random.choice(concepts)
            template = random.choice(question_templates)
            query = template.format(action=action, concept=concept)
        elif concepts:
            concept = random.choice(concepts)
            query = f"How do I work with {concept}?"
        elif "script" in filename.lower():
            query = "How do I run this script?"
        elif "config" in filename.lower():
            query = "How do I configure this system?"
        else:
            query = "How do I use this feature?"

        return query

    def categorize_chunk(self, chunk: dict[str, Any]) -> str:
        """Categorize chunk into coverage categories."""
        content = chunk.get("content", "").lower()
        filename = chunk.get("filename", "").lower()
        file_path = chunk.get("file_path", "").lower()

        # Ops/Health (6)
        if any(
            term in content or term in filename
            for term in ["env", "environment", "prefix", "cache", "rollback", "canary"]
        ):
            return "ops_health"

        # DB workflows (6)
        if any(
            term in content or term in filename
            for term in ["sql", "database", "vector", "fts", "gin", "pgvector", "ann"]
        ):
            return "db_workflows"

        # Meta-ops (3)
        if any(term in content or term in filename for term in ["runbook", "manifest", "deploy", "gate", "ci"]):
            return "meta_ops"

        # RAG QA - single hop (6)
        if any(term in content for term in ["retrieval", "embedding", "chunk", "document"]) and "multi" not in content:
            return "rag_qa_single"

        # RAG QA - multi hop (6)
        if any(term in content for term in ["multi", "fusion", "rerank", "cross-encoder"]):
            return "rag_qa_multi"

        # Default to single hop RAG QA
        return "rag_qa_single"

    def create_negative_examples(self) -> list[dict[str, Any]]:
        """Create 3 negative examples for not found behavior."""
        negatives = [
            {
                "query": "How do I configure the quantum entanglement module?",
                "gt_answer": "Not in context.",
                "expected_files": [],
                "tags": ["negative", "quantum", "entanglement"],
                "category": "negatives",
            },
            {
                "query": "What is the API key for the Mars colony database?",
                "gt_answer": "Not in context.",
                "expected_files": [],
                "tags": ["negative", "mars", "api-key"],
                "category": "negatives",
            },
            {
                "query": "How do I install the time travel dependencies?",
                "gt_answer": "Not in context.",
                "expected_files": [],
                "tags": ["negative", "time-travel", "dependencies"],
                "category": "negatives",
            },
        ]
        return negatives

    def create_gold_records(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Create gold records from sampled chunks."""
        print("📝 Creating gold records...")

        gold_records = []
        category_counts = {cat: 0 for cat in self.coverage_categories.keys()}

        for chunk in chunks:
            category = self.categorize_chunk(chunk)

            # Skip if we have enough of this category
            if category_counts[category] >= self.coverage_categories[category]:
                continue

            # Extract authoritative sentence
            gt_answer = self.extract_authoritative_sentence(chunk["content"])

            # Draft query
            query = self.draft_query_from_content(chunk["content"], chunk["filename"])

            # Determine expected files
            expected_files = [chunk["filename"]] if chunk["filename"] else []

            # Create tags based on content and category
            tags = [category]
            if "script" in chunk["filename"].lower():
                tags.append("script")
            if "config" in chunk["filename"].lower():
                tags.append("config")
            if "db" in chunk["filename"].lower() or "sql" in chunk["filename"].lower():
                tags.append("db")

            gold_record = {
                "query": query,
                "gt_answer": gt_answer,
                "expected_files": expected_files,
                "tags": tags,
                "category": category,
                "source_chunk_id": chunk["id"],
                "source_file": chunk["filename"],
            }

            gold_records.append(gold_record)
            category_counts[category] += 1

            print(f"  ✅ {category}: {query[:50]}...")

        # Add negative examples
        negatives = self.create_negative_examples()
        gold_records.extend(negatives)

        print(f"📊 Created {len(gold_records)} gold records:")
        for cat, count in category_counts.items():
            print(f"  • {cat}: {count}")
        print(f"  • negatives: {len(negatives)}")

        return gold_records

    def save_dataset(self, gold_records: list[dict[str, Any]], output_path: str = "datasets/dev_gold.jsonl"):
        """Save gold records to JSONL file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            for record in gold_records:
                f.write(json.dumps(record) + "\n")

        print(f"💾 Saved {len(gold_records)} gold records to {output_path}")

        # Create review sheet
        self._create_review_sheet(gold_records, output_path.replace(".jsonl", "_review.md"))

    def _create_review_sheet(self, gold_records: list[dict[str, Any]], review_path: str):
        """Create a review sheet for manual validation."""
        with open(review_path, "w") as f:
            f.write("# Repo-Gold Dataset Review Sheet\n\n")
            f.write("Review each record and accept/revise as needed.\n\n")

            for i, record in enumerate(gold_records, 1):
                f.write(f"## Record {i}: {record['category']}\n\n")
                f.write(f"**Query:** {record['query']}\n\n")
                f.write(f"**Ground Truth:** {record['gt_answer']}\n\n")
                f.write(f"**Expected Files:** {', '.join(record['expected_files'])}\n\n")
                f.write(f"**Tags:** {', '.join(record['tags'])}\n\n")
                f.write(f"**Source:** {record.get('source_file', 'N/A')}\n\n")
                f.write("**Review:** [ ] Accept [ ] Revise\n\n")
                f.write("---\n\n")

        print(f"📋 Created review sheet: {review_path}")

    def bootstrap_dataset(self, output_path: str = "datasets/dev_gold.jsonl"):
        """Main bootstrap process."""
        print("🚀 Bootstrapping Repo-Gold Dataset")
        print("=" * 50)

        # Sample representative chunks
        chunks = self.sample_representative_chunks(self.total_target)

        # Create gold records
        gold_records = self.create_gold_records(chunks)

        # Save dataset
        self.save_dataset(gold_records, output_path)

        print("\n✅ Bootstrap complete!")
        print(f"📁 Dataset: {output_path}")
        print(f"📋 Review sheet: {output_path.replace('.jsonl', '_review.md')}")
        print("\nNext steps:")
        print("1. Review the generated dataset")
        print("2. Accept/revise records as needed")
        print("3. Set DATASET_HAS_GOLD=1 in evaluation config")
        print("4. Re-enable strict oracle gates")

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="Bootstrap repo-gold dataset")
    parser.add_argument("--output", default="datasets/dev_gold.jsonl", help="Output path for dataset")
    parser.add_argument(
        "--db", default="postgresql://danieljacobs@localhost:5432/ai_agency", help="Database connection string"
    )

    args = parser.parse_args()

    bootstrap = RepoGoldDatasetBootstrap(args.db)
    bootstrap.bootstrap_dataset(args.output)

if __name__ == "__main__":
    main()
