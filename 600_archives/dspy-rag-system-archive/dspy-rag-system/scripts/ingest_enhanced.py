#!/usr/bin/env python3
"""
Enhanced Document Ingestion Script
- Uses enhanced chunking with tokenizer-first approach
- Supports dual-text storage for embedding and BM25
- Includes instrumentation and validation
- A/B testing capabilities
"""

import argparse
import glob
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from tqdm import tqdm

# Use YOUR pool (thread-safe) – single DB layer.
from src.utils.db_pool import get_conn, init_pool
from src.utils.enhanced_chunking import ChunkingConfig, create_enhanced_chunker

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    print("pip install sentence-transformers")
    raise

PdfReader = None  # optional PDF support; requires 'pypdf' to be installed

# ---------- config ----------
MD_TYPES = (".md",)
TEXT_TYPES = (".txt",)
PDF_TYPES = (".pdf",)
EMBED_DIM = 384  # all-MiniLM-L6-v2

# Enhanced DDL with dual-text support
DDL = [
    "CREATE EXTENSION IF NOT EXISTS vector;",
    """
    CREATE TABLE IF NOT EXISTS documents (
      id           SERIAL PRIMARY KEY,
      filename     VARCHAR NOT NULL,
      file_path    TEXT NOT NULL UNIQUE,
      file_type    VARCHAR NOT NULL,
      file_size    BIGINT NOT NULL,
      status       VARCHAR DEFAULT 'completed',
      content_sha  VARCHAR NOT NULL,
      chunk_count  INT DEFAULT 0,
      created_at   TIMESTAMP DEFAULT now(),
      updated_at   TIMESTAMP DEFAULT now(),
      namespace    TEXT GENERATED ALWAYS AS (
        (regexp_match(replace(file_path, '\\', '/'), '(^|/)(\\d{3}_[[:alnum:]_-]+)(/|$)'))[2]
      ) STORED
    );
    """,
    f"""
    CREATE TABLE IF NOT EXISTS document_chunks (
      id           SERIAL PRIMARY KEY,
      document_id  INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
      chunk_index  INT NOT NULL,
      file_path    TEXT,
      line_start   INTEGER,
      line_end     INTEGER,
      content      TEXT NOT NULL,
      embedding_text TEXT,  -- For embedding (with context)
      bm25_text    TEXT,    -- For BM25 (clean)
      embedding    VECTOR({EMBED_DIM}),
      is_anchor    BOOLEAN DEFAULT FALSE,
      anchor_key   TEXT,
      metadata     JSONB DEFAULT '{{}}',
      content_tsv  tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(bm25_text, content))) STORED,
      created_at   TIMESTAMP DEFAULT now(),
      updated_at   TIMESTAMP DEFAULT now(),
      UNIQUE(document_id, chunk_index)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_tsv ON document_chunks USING GIN (content_tsv);",
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_l2_ops);",
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_anchor_key ON document_chunks (anchor_key);",
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_is_anchor ON document_chunks (is_anchor);",
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_file_path ON document_chunks (file_path);",
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_metadata_gin ON document_chunks USING GIN (metadata);",
]

UPSERT_DOCUMENT = """
INSERT INTO documents (filename, file_path, file_type, file_size, status, content_sha, chunk_count, updated_at)
VALUES (%(filename)s, %(file_path)s, %(file_type)s, %(file_size)s, 'completed', %(content_sha)s, %(chunk_count)s, now())
ON CONFLICT (file_path) DO UPDATE SET
  file_type   = EXCLUDED.file_type,
  file_size   = EXCLUDED.file_size,
  status      = 'completed',
  content_sha = EXCLUDED.content_sha,
  chunk_count = EXCLUDED.chunk_count,
  updated_at  = now()
RETURNING id;
"""

SELECT_EXISTING = "SELECT id, content_sha, chunk_count FROM documents WHERE file_path = %s;"
DELETE_DOC_CHUNKS = "DELETE FROM document_chunks WHERE document_id = %s;"

INSERT_CHUNK = """
INSERT INTO document_chunks (document_id, chunk_index, content, embedding_text, bm25_text, embedding, metadata, embedding_token_count, bm25_token_count, chunk_id, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, now())
ON CONFLICT (document_id, chunk_index) DO UPDATE SET
  content                = EXCLUDED.content,
  embedding_text         = EXCLUDED.embedding_text,
  bm25_text             = EXCLUDED.bm25_text,
  embedding             = EXCLUDED.embedding,
  metadata              = EXCLUDED.metadata,
  embedding_token_count = EXCLUDED.embedding_token_count,
  bm25_token_count      = EXCLUDED.bm25_token_count,
  chunk_id              = EXCLUDED.chunk_id,
  updated_at            = now();
"""


def sha256(text: str) -> str:
    """Generate SHA256 hash of text"""
    return hashlib.sha256(text.encode()).hexdigest()


def canonical_file_type(path: Path) -> str:
    """Get canonical file type"""
    return path.suffix.lower().lstrip(".")


def read_text(path: Path) -> str:
    """Read text from file"""
    if path.suffix.lower() in PDF_TYPES:
        global PdfReader
        if PdfReader is None:
            try:
                from pypdf import PdfReader as _PdfReader

                PdfReader = _PdfReader
            except ImportError:
                raise ImportError("pip install pypdf")

        with open(path, "rb") as f:
            reader = PdfReader(f)
            return "\n".join(page.extract_text() for page in reader.pages)
    else:
        with open(path, encoding="utf-8") as f:
            return f.read()


def embed_chunks(model, chunks: list[str], batch: int = 64) -> list[list[float]]:
    """Embed chunks using sentence transformer"""
    if not chunks:
        return []

    vecs = []
    for i in range(0, len(chunks), batch):
        batch_vecs = model.encode(chunks[i : i + batch], show_progress_bar=False, convert_to_numpy=True)
        vecs.extend(batch_vecs.tolist())

    return vecs


def ensure_schema():
    """Ensure database schema exists"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            for stmt in DDL:
                cur.execute(stmt)
        conn.commit()


def fetch_existing(file_path: str) -> dict[str, Any] | None:
    """Fetch existing document info"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SELECT_EXISTING, (file_path,))
            row = cur.fetchone()
            if row:
                return {"id": row[0], "content_sha": row[1], "chunk_count": row[2]}
    return None


def upsert_document(meta: dict[str, Any]) -> int:
    """Upsert document and return ID"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(UPSERT_DOCUMENT, meta)
            doc_id = cur.fetchone()[0]
        conn.commit()
    return doc_id


def clear_doc_chunks(doc_id: int):
    """Clear existing chunks for document"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_DOC_CHUNKS, (doc_id,))
        conn.commit()


def upsert_doc_chunks(
    doc_id: int,
    filename: str,
    chunk_pairs: list[tuple],
    embeddings: list[list[float]],
    metadata: dict[str, Any],
    use_enhanced: bool = False,
):
    """Upsert document chunks with dual-text storage"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            for i, (chunk_data, embedding) in enumerate(zip(chunk_pairs, embeddings)):
                if use_enhanced and len(chunk_data) == 4:
                    # New format: (embedding_text, bm25_text, token_counts, chunk_id)
                    embedding_text, bm25_text, token_counts, chunk_id = chunk_data
                    chunk_metadata = {
                        **metadata,
                        "chunk_index": i,
                        "filename": filename,
                        "chunk_id": chunk_id,
                        "embedding_token_count": token_counts["embedding_token_count"],
                        "bm25_token_count": token_counts["bm25_token_count"],
                        # Add run tracking for evaluations
                        "ingest_run_id": os.getenv("INGEST_RUN_ID"),
                        "chunk_variant": os.getenv("CHUNK_VARIANT"),
                        "chunk_size": metadata.get("chunk_size"),
                        "overlap_ratio": metadata.get("overlap_ratio"),
                    }
                else:
                    # Legacy format: (embedding_text, bm25_text)
                    embedding_text, bm25_text = chunk_data[:2]
                    chunk_metadata = {
                        **metadata,
                        "chunk_index": i,
                        "filename": filename,
                        "embedding_token_count": len(embedding_text.split()),
                        "bm25_token_count": len(bm25_text.split()),
                        # Add run tracking for evaluations
                        "ingest_run_id": os.getenv("INGEST_RUN_ID"),
                        "chunk_variant": os.getenv("CHUNK_VARIANT"),
                        "chunk_size": metadata.get("chunk_size"),
                        "overlap_ratio": metadata.get("overlap_ratio"),
                    }

                cur.execute(
                    INSERT_CHUNK,
                    (
                        doc_id,
                        i,
                        bm25_text,
                        embedding_text,
                        bm25_text,
                        embedding,
                        json.dumps(chunk_metadata),
                        chunk_metadata.get("embedding_token_count"),
                        chunk_metadata.get("bm25_token_count"),
                        chunk_metadata.get("chunk_id"),
                    ),
                )
        conn.commit()


def collect_files(globs_str: str) -> list[Path]:
    """Collect files matching glob patterns"""
    paths = []
    for g in [x.strip() for x in globs_str.split(",") if x.strip()]:
        paths.extend(Path(p) for p in glob.glob(g, recursive=True))

    return sorted(
        [p for p in paths if p.is_file() and p.suffix.lower() in (*MD_TYPES, *TEXT_TYPES, *PDF_TYPES)],
        key=lambda x: str(x),
    )


def log_ingest_metrics(file_path: str, metrics: dict[str, Any], config: ChunkingConfig):
    """Log ingest metrics for analysis"""
    log_entry = {
        "timestamp": time.time(),
        "file_path": file_path,
        "config": {
            "embedder_name": config.embedder_name,
            "chunk_size": config.chunk_size,
            "overlap_ratio": config.overlap_ratio,
            "max_tokens": config.max_tokens,
        },
        "metrics": metrics,
    }

    # Log to file for analysis
    log_file = Path("logs/ingest_metrics.jsonl")
    log_file.parent.mkdir(exist_ok=True)

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def validate_chunking_results(
    chunk_pairs: list[tuple[str, str]] | list[tuple[str, str, dict[str, int], str]], config: ChunkingConfig
) -> dict[str, Any]:
    """Validate chunking results"""
    # Extract bm25_text from either format: (embedding_text, bm25_text) or (embedding_text, bm25_text, token_counts, chunk_id)
    bm25_texts = [pair[1] for pair in chunk_pairs]

    # Simple token counting for validation
    token_counts = [len(text.split()) for text in bm25_texts]

    return {
        "budget_compliance": max(token_counts) <= config.max_tokens if token_counts else True,
        "zero_over_budget": sum(1 for t in token_counts if t > config.max_tokens) == 0,
        "chunk_count": len(chunk_pairs),
        "avg_tokens": sum(token_counts) / len(token_counts) if token_counts else 0,
        "max_tokens": max(token_counts) if token_counts else 0,
        "min_tokens": min(token_counts) if token_counts else 0,
    }


def main():
    """Main ingestion function"""
    load_dotenv()
    parser = argparse.ArgumentParser("Enhanced doc ingester")
    parser.add_argument(
        "--glob", default=os.getenv("INGEST_GLOB", "000_core/**/*.md,100_memory/**/*.md,400_guides/**/*.md")
    )
    parser.add_argument("--embedder", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--overlap-ratio", type=float, default=None)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Re-embed/rewrite even if content_sha unchanged")
    parser.add_argument("--rebuild", action="store_true", help="Clear chunks for changed docs before insert")
    parser.add_argument("--ab-test", action="store_true", help="Run A/B test across chunk sizes")
    parser.add_argument("--log-metrics", action="store_true", help="Log detailed metrics")
    parser.add_argument("--use-enhanced-chunking", action="store_true", help="Use enhanced chunking system")
    parser.add_argument(
        "--shadow-write", action="store_true", help="Write to both old and new chunking systems for A/B"
    )
    args = parser.parse_args()

    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL not set")
        sys.exit(1)

    init_pool()
    ensure_schema()

    print(f"Loading embedding model: {args.embedder}")
    model = SentenceTransformer(args.embedder)

    files = collect_files(args.glob)
    print(f"Found {len(files)} files.")

    # A/B testing mode
    if args.ab_test:
        chunk_sizes = [300, 450, 700, 900]
        print(f"Running A/B test with chunk sizes: {chunk_sizes}")

        for chunk_size in chunk_sizes:
            print(f"\n=== Testing chunk size: {chunk_size} ===")
            config = ChunkingConfig(
                embedder_name=args.embedder,
                chunk_size=chunk_size,
                overlap_ratio=args.overlap_ratio or 0.15,
                max_tokens=args.max_tokens or 512,
            )

            chunker = create_enhanced_chunker(args.embedder)
            chunker.config = config  # Override config for A/B test

            process_files(files, model, chunker, args, config)
    else:
        # Single configuration mode
        config = ChunkingConfig(
            embedder_name=args.embedder,
            chunk_size=args.chunk_size or 400,
            overlap_ratio=args.overlap_ratio or 0.15,
            max_tokens=args.max_tokens or 512,
        )

        chunker = create_enhanced_chunker(args.embedder)
        chunker.config = config  # Override config if specified

        process_files(files, model, chunker, args, config)

    print("✅ Done.")


def process_files(files: list[Path], model, chunker, args, config: ChunkingConfig):
    """Process files with enhanced chunking"""
    for path in tqdm(files, desc="Ingesting"):
        try:
            raw = read_text(path)
        except Exception as e:
            print(f"Read failed: {path} -> {e}")
            continue

        sha = sha256(raw)
        ft = canonical_file_type(path)
        size = path.stat().st_size

        existing = fetch_existing(str(path))
        if existing and existing["content_sha"] == sha and not args.force:
            # unchanged; skip
            continue

        # Enhanced chunking
        result = chunker.chunk_document(path, raw)

        if args.use_enhanced_chunking:
            # New format: (embedding_text, bm25_text, token_counts, chunk_id)
            chunk_pairs = list(
                zip(result["embedding_texts"], result["bm25_texts"], result["token_counts"], result["chunk_ids"])
            )
        else:
            # Legacy format: (embedding_text, bm25_text)
            chunk_pairs = list(zip(result["embedding_texts"], result["bm25_texts"]))

        if not chunk_pairs:
            print(f"WARNING: no chunks for {path.name}; skipping.")
            continue

        # Validate chunking
        validation = validate_chunking_results(chunk_pairs, config)
        if not validation["budget_compliance"]:
            print(f"WARNING: {path.name} has chunks exceeding budget: {validation['max_tokens']} > {config.max_tokens}")

        # Embed chunks
        embedding_texts = [pair[0] for pair in chunk_pairs]
        vecs = embed_chunks(model, embedding_texts)

        # Document metadata
        doc_meta = {
            "filename": path.name,
            "file_path": str(path),
            "file_type": ft,
            "file_size": size,
            "content_sha": sha,
            "chunk_count": len(chunk_pairs),
        }
        doc_id = upsert_document(doc_meta)

        if args.rebuild or not existing or existing["content_sha"] != sha:
            clear_doc_chunks(doc_id)

        # Add chunking configuration to metadata
        chunk_metadata = {
            **result["metadata"],
            "chunk_size": config.chunk_size,
            "overlap_ratio": config.overlap_ratio,
        }
        upsert_doc_chunks(doc_id, path.name, chunk_pairs, vecs, chunk_metadata, args.use_enhanced_chunking)

        # Log metrics if requested
        if args.log_metrics:
            log_ingest_metrics(str(path), result["metrics"], config)


if __name__ == "__main__":
    main()
