#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess

# Add repo root to import path
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import psycopg
import torch
from psycopg.rows import dict_row
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, PreTrainedTokenizerBase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common.db_dsn import resolve_dsn  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EMBEDDER_NAME = "BAAI/bge-small-en-v1.5"
CODE_CHUNK_TOKENS = int(os.getenv("CODE_CHUNK_SIZE_TOKENS", "256"))
CODE_CHUNK_OVERLAP = int(os.getenv("CODE_CHUNK_OVERLAP_TOKENS", "64"))


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def iter_python_files() -> Iterable[Path]:
    for base in (PROJECT_ROOT / "src", PROJECT_ROOT / "scripts", PROJECT_ROOT / "evals"):
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            # Skip venvs, caches, and node_modules
            s = str(p)
            if any(seg in s for seg in ("/.venv/", "/venv/", "__pycache__", ".pytest_cache", "node_modules")):
                continue
            yield p


def chunk_code_by_tokens(
    text: str,
    tokenizer: PreTrainedTokenizerBase,
    max_tokens: int = CODE_CHUNK_TOKENS,
    overlap_tokens: int = CODE_CHUNK_OVERLAP,
) -> list[str]:
    """Split code into overlapping token windows to improve retrieval granularity."""

    if not text.strip():
        return []

    token_ids = tokenizer.encode(text, add_special_tokens=False)
    if not token_ids:
        return []

    windows: list[str] = []
    step = max(1, max_tokens - overlap_tokens)

    for start in range(0, len(token_ids), step):
        window_ids = token_ids[start : start + max_tokens]
        if not window_ids:
            break
        window_text = tokenizer.decode(window_ids)
        snippet = window_text.strip()
        if snippet:
            windows.append(snippet)

    return windows


def current_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=str(PROJECT_ROOT)).strip()
    except Exception:
        return "unknown"


def current_commit_time() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "show", "-s", "--format=%cI", "HEAD"], text=True, cwd=str(PROJECT_ROOT)
        ).strip()
    except Exception:
        return None


def main() -> int:
    dsn = resolve_dsn(strict=True)
    commit = current_commit()
    ctime = current_commit_time()

    # Initialize embedder and tokenizer
    print(f"Loading embedder: {EMBEDDER_NAME}")
    embedder = SentenceTransformer(EMBEDDER_NAME, device="cuda" if torch.cuda.is_available() else "cpu")
    embedder.max_seq_length = 512
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDER_NAME)
    chunk_variant = f"code_t{CODE_CHUNK_TOKENS}_o{CODE_CHUNK_OVERLAP}"
    ingest_run_id = os.getenv("INGEST_RUN_ID", f"ing-{os.getpid()}")

    files = list(iter_python_files())
    if not files:
        print("No Python files found to ingest.")
        return 0

    inserted_files = 0
    inserted_symbols = 0
    inserted_chunks = 0

    with psycopg.connect(dsn) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            for fp in files:
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception as e:
                    print(f"skip {fp}: read error {e}")
                    continue

                rel = str(fp.relative_to(PROJECT_ROOT))
                fhash = sha256_bytes(text.encode("utf-8"))

                # Upsert code_files (unique by (repo_rel_path, git_commit))
                _ = cur.execute(
                    """
                    INSERT INTO code_files (repo_rel_path, language, git_commit, commit_time, content_hash,
                                            is_test, is_vendor, is_generated, parse_status, meta)
                    VALUES (%s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s)
                    ON CONFLICT (repo_rel_path, git_commit)
                    DO UPDATE SET content_hash = EXCLUDED.content_hash,
                                  commit_time  = EXCLUDED.commit_time,
                                  parse_status = EXCLUDED.parse_status
                    RETURNING id
                    """,
                    (
                        rel,
                        "python",
                        commit,
                        ctime,
                        fhash,
                        rel.startswith("tests/") or Path(rel).name.startswith("test_"),
                        False,
                        False,
                        "ok",
                        "{}",
                    ),
                )
                file_result = cur.fetchone()
                if file_result is None:
                    raise RuntimeError("Failed to insert file record")
                file_id = int(file_result["id"])
                inserted_files += 1

                # Insert a module-level symbol row (simple first slice)
                _ = cur.execute(
                    """
                    INSERT INTO code_symbols (file_id, symbol_type, symbol_name, span_start, span_end, signature, docstring, doc_hash, meta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        file_id,
                        "module",
                        Path(rel).stem,
                        1,
                        len(text.splitlines()) or 1,
                        f"module {Path(rel).stem}",
                        None,
                        None,
                        "{}",
                    ),
                )
                symbol_result = cur.fetchone()
                if symbol_result is None:
                    raise RuntimeError("Failed to insert symbol record")
                symbol_id = int(symbol_result["id"])
                inserted_symbols += 1

                # Replace any previous chunks for this file to keep indexes consistent
                cur.execute("DELETE FROM code_chunks WHERE file_id = %s", (file_id,))

                windows = chunk_code_by_tokens(text, tokenizer, CODE_CHUNK_TOKENS, CODE_CHUNK_OVERLAP)
                if not windows:
                    continue

                embeddings = embedder.encode(
                    windows,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                )
                for idx, snippet in enumerate(windows):
                    tokens = tokenizer.encode(snippet, add_special_tokens=False)
                    metadata = json.dumps(
                        {
                            "chunk_variant": chunk_variant,
                            "source_path": rel,
                            "ingest_run_id": ingest_run_id,
                        }
                    )
                    vector = embeddings[idx].tolist() if hasattr(embeddings[idx], "tolist") else list(embeddings[idx])
                    _ = cur.execute(
                        """
                        INSERT INTO code_chunks (file_id, symbol_id, chunk_index, content, docstring,
                                                  token_count, content_hash, embedding, model_name, model_version, normalized, meta)
                        VALUES (%s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            file_id,
                            symbol_id,
                            idx,
                            snippet,
                            None,
                            max(1, len(tokens)),
                            sha256_bytes(snippet.encode("utf-8")),
                            vector,
                            EMBEDDER_NAME,
                            "v1.5",
                            True,
                            metadata,
                        ),
                    )
                    inserted_chunks += 1

        conn.commit()

    print(f"Ingest complete: files={inserted_files}, symbols={inserted_symbols}, chunks={inserted_chunks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
