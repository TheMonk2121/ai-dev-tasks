#!/usr/bin/env python3
"""
Evaluation Code Embedder

Generates embeddings for all code chunks in the evaluation system using BAAI/bge-small-en-v1.5.
Completes the pipeline after scripts/ingest_evaluation_code.py.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import psycopg
from psycopg.rows import dict_row
from sentence_transformers import SentenceTransformer

# Add repo root to import path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common.db_dsn import resolve_dsn  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_db_connection() -> psycopg.Connection[dict[str, Any]]:
    """Get database connection using Psycopg3Config."""
    return psycopg.connect(resolve_dsn(strict=True))


def get_embedding_model() -> SentenceTransformer:
    """Get or create the embedding model."""
    model_name = "BAAI/bge-small-en-v1.5"
    print(f"🤖 Loading embedding model: {model_name}")

    model = SentenceTransformer(model_name)
    model.max_seq_length = 512  # Safe for BGE small

    print(f"✅ Model loaded: {model_name} (dim={model.get_sentence_embedding_dimension()})")
    return model


def generate_embeddings_batch(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    if not texts:
        return []

    # Generate embeddings
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    # Convert to list of lists
    return [embedding.tolist() for embedding in embeddings]


def embed_evaluation_code() -> int:
    """Generate embeddings for all evaluation code chunks."""
    model = get_embedding_model()
    expected_dim = model.get_sentence_embedding_dimension()

    print(f"📊 Expected embedding dimension: {expected_dim}")

    with get_db_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Get all chunks that need embeddings
            cur.execute(
                """
                SELECT cc.id, cc.content, cf.repo_rel_path
                FROM code_chunks cc
                JOIN code_files cf ON cc.file_id = cf.id
                WHERE cc.embedding IS NULL
                AND cc.is_archived = false
                ORDER BY cc.id
                """
            )
            chunks = cur.fetchall()

            if not chunks:
                print("✅ No chunks need embedding - all done!")
                return 0

            print(f"📦 Found {len(chunks)} chunks to embed")

            # Process in batches
            batch_size = 32
            total_embedded = 0

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i : i + batch_size]
                batch_texts = [chunk["content"] for chunk in batch]
                batch_ids = [chunk["id"] for chunk in batch]

                print(
                    f"🔄 Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size} "
                    f"({len(batch)} chunks)"
                )

                try:
                    # Generate embeddings
                    embeddings = generate_embeddings_batch(model, batch_texts)

                    # Update database
                    for chunk_id, embedding in zip(batch_ids, embeddings):
                        if len(embedding) != expected_dim:
                            print(
                                f"⚠️  Warning: chunk {chunk_id} has wrong dimension {len(embedding)} != {expected_dim}"
                            )
                            continue

                        cur.execute(
                            """
                            UPDATE code_chunks 
                            SET embedding = %s, model_name = %s, normalized = %s
                            WHERE id = %s
                            """,
                            (embedding, "BAAI/bge-small-en-v1.5", True, chunk_id),
                        )
                        total_embedded += 1

                    # Commit batch
                    conn.commit()

                except Exception as e:
                    print(f"❌ Error processing batch: {e}")
                    conn.rollback()
                    continue

            print(f"✅ Embedding complete: {total_embedded} chunks embedded")

            # Verify results
            cur.execute(
                """
                SELECT 
                    COUNT(*) as total_chunks,
                    COUNT(embedding) as embedded_chunks,
                    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embeddings
                FROM code_chunks 
                WHERE is_archived = false
                """
            )
            stats = cur.fetchone()

            print("📊 Final stats:")
            print(f"   Total chunks: {stats['total_chunks']}")
            print(f"   With embeddings: {stats['with_embeddings']}")
            print(f"   Embedding rate: {stats['with_embeddings']/stats['total_chunks']*100:.1f}%")

            return 0


def main() -> int:
    """Main entry point."""
    try:
        return embed_evaluation_code()
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
