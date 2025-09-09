#!/usr/bin/env python3
# pyright: reportMissingImports=false
# scripts/ingest_integrated.py
# Minimal, pool-integrated doc ingester: .md/.txt/.pdf -> Postgres (pgvector + FTS)

import argparse
import glob
import hashlib
import os
import re
import sys
from pathlib import Path


import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from tqdm import tqdm

# Use YOUR pool (thread-safe) – single DB layer.
from src.utils.db_pool import get_conn, init_pool

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
      updated_at   TIMESTAMP DEFAULT now()
    );
    """,
    f"""
    CREATE TABLE IF NOT EXISTS document_chunks (
      id           SERIAL PRIMARY KEY,
      document_id  INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
      chunk_index  INT NOT NULL,
      content      TEXT NOT NULL,
      embedding    VECTOR({EMBED_DIM}),
      content_tsv  tsvector,
      metadata     JSONB DEFAULT '{{}}'::jsonb,
      created_at   TIMESTAMP DEFAULT now(),
      updated_at   TIMESTAMP DEFAULT now(),
      UNIQUE(document_id, chunk_index)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_tsv ON document_chunks USING GIN (content_tsv);",
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_l2_ops);",
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
INSERT INTO document_chunks (document_id, chunk_index, content, embedding, metadata, updated_at)
VALUES (%s, %s, %s, %s, %s::jsonb, now())
ON CONFLICT (document_id, chunk_index) DO UPDATE SET
  content     = EXCLUDED.content,
  embedding   = EXCLUDED.embedding,
  metadata    = EXCLUDED.metadata,
  updated_at  = now();
"""

# ---------- io / hashing ----------


def read_text(p: Path) -> str:
    suf = p.suffix.lower()
    if suf in MD_TYPES or suf in TEXT_TYPES:
        return p.read_text(encoding="utf-8", errors="ignore")
    if suf in PDF_TYPES:
        if not PdfReader:
            raise RuntimeError("pypdf not installed (pip install pypdf)")
        out = []
        with open(p, "rb") as f:
            r = PdfReader(f)
            for pg in r.pages:
                out.append(pg.extract_text() or "")
        return "\n".join(out)
    # default: try text
    return p.read_text(encoding="utf-8", errors="ignore")


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def canonical_file_type(p: Path) -> str:
    return "markdown" if p.suffix.lower() in MD_TYPES else p.suffix.lower().lstrip(".")


# ---------- chunking (simple, section-aware for md) ----------


def approx_tokens(s: str) -> int:
    return max(1, len(s.split()))


def pack_with_overlap(parts: list[str], target: int, overlap: int) -> list[str]:
    chunks, cur, cur_tok = [], [], 0
    for part in parts:
        t = approx_tokens(part)
        if cur and cur_tok + t > target:
            chunks.append("\n\n".join(cur).strip())
            if overlap > 0:
                tail = " ".join(" ".join(cur).split()[-overlap:])
                cur = [tail] if tail else []
                cur_tok = approx_tokens(tail) if tail else 0
            else:
                cur, cur_tok = [], 0
        cur.append(part)
        cur_tok += t
    if cur:
        chunks.append("\n\n".join(cur).strip())
    return [c for c in chunks if approx_tokens(c) > 30]


def split_markdown(text: str, target=900, overlap=120) -> list[str]:
    # keep fenced code intact; then split on headings
    blocks = re.split(r"(\n```.*?\n```)", text, flags=re.DOTALL)
    sections: list[str] = []
    for i, blk in enumerate(blocks):
        if i % 2 == 1:
            sections.append(blk)
        else:
            parts = re.split(r"(?=^#{1,6}\s)", blk, flags=re.MULTILINE)
            sections.extend([p for p in parts if p.strip()])
    return pack_with_overlap(sections, target, overlap)


def split_text(text: str, target=900, overlap=120) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return pack_with_overlap(paras, target, overlap)


def chunk_for(p: Path, text: str, target=900, overlap=120) -> list[str]:
    return split_markdown(text, target, overlap) if p.suffix.lower() in MD_TYPES else split_text(text, target, overlap)


# ---------- embeddings ----------


def embed_chunks(model, chunks: list[str], batch: int = 64):
    if not chunks:
        return []
    vecs = []
    for i in range(0, len(chunks), batch):
        batch_vecs = model.encode(chunks[i : i + batch], show_progress_bar=False, convert_to_numpy=True)
        vecs.extend(batch_vecs)
    return vecs


# ---------- db ops (via your pool) ----------


def ensure_schema():
    with get_conn() as conn:
        with conn.cursor() as cur:
            for stmt in DDL:
                cur.execute(stmt)
        conn.commit()


def upsert_document(meta: dict) -> int:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(UPSERT_DOCUMENT, meta)
            row = cur.fetchone()
        conn.commit()
    return int(row["id"])


def clear_doc_chunks(doc_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_DOC_CHUNKS, (doc_id,))
        conn.commit()


def upsert_doc_chunks(doc_id: int, filename: str, chunks: list[str], embeddings):
    rows = []
    for idx, (c, e) in enumerate(zip(chunks, embeddings)):
        meta = psycopg2.extras.Json({"filename": filename})
        # Convert numpy array to list for pgvector
        if hasattr(e, "tolist"):
            e = e.tolist()
        rows.append((doc_id, idx, c, e, meta))
    with get_conn() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, INSERT_CHUNK, rows, page_size=200)
        conn.commit()


def fetch_existing(file_path: str):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(SELECT_EXISTING, (file_path,))
            return cur.fetchone()


# ---------- main ----------


def discover(globs_str: str) -> list[Path]:
    paths = []
    for g in [x.strip() for x in globs_str.split(",") if x.strip()]:
        paths.extend(Path(p) for p in glob.glob(g, recursive=True))
    return sorted(
        [p for p in paths if p.is_file() and p.suffix.lower() in (*MD_TYPES, *TEXT_TYPES, *PDF_TYPES)],
        key=lambda x: str(x),
    )


def main():
    load_dotenv()
    parser = argparse.ArgumentParser("Ingest docs (pool-integrated)")
    parser.add_argument(
        "--glob", default=os.getenv("INGEST_GLOB", "000_core/**/*.md,100_memory/**/*.md,400_guides/**/*.md")
    )
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--overlap", type=int, default=120)
    parser.add_argument("--force", action="store_true", help="Re-embed/rewrite even if content_sha unchanged")
    parser.add_argument("--rebuild", action="store_true", help="Clear chunks for changed docs before insert")
    args = parser.parse_args()

    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL not set")
        sys.exit(1)

    init_pool()
    ensure_schema()

    print("Loading embedding model: all-MiniLM-L6-v2")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    files = discover(args.glob)
    print(f"Found {len(files)} files.")

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

        chunks = chunk_for(path, raw, args.chunk_size, args.overlap)
        if not chunks:
            print(f"WARNING: no chunks for {path.name}; skipping.")
            continue
        vecs = embed_chunks(model, chunks)

        doc_meta = {
            "filename": path.name,
            "file_path": str(path),
            "file_type": ft,
            "file_size": size,
            "content_sha": sha,
            "chunk_count": len(chunks),
        }
        doc_id = upsert_document(doc_meta)

        if args.rebuild or not existing or existing["content_sha"] != sha:
            clear_doc_chunks(doc_id)
        upsert_doc_chunks(doc_id, path.name, chunks, vecs)

    print("✅ Done.")


if __name__ == "__main__":
    main()
