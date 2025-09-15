#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import subprocess

# Add repo root to import path
import sys
from collections.abc import Iterable
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common.db_dsn import resolve_dsn  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def iter_python_files() -> Iterable[Path]:
    for base in (PROJECT_ROOT / "src", PROJECT_ROOT / "scripts"):
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            # Skip venvs, caches, and node_modules
            s = str(p)
            if any(seg in s for seg in ("/.venv/", "/venv/", "__pycache__", ".pytest_cache", "node_modules")):
                continue
            yield p


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

    files = list(iter_python_files())
    if not files:
        print("No Python files found to ingest.")
        return 0

    inserted_files = 0
    inserted_symbols = 0
    inserted_chunks = 0

    with psycopg2.connect(dsn, cursor_factory=RealDictCursor) as conn:
        with conn.cursor() as cur:
            for fp in files:
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception as e:
                    print(f"skip {fp}: read error {e}")
                    continue

                rel = str(fp.relative_to(PROJECT_ROOT))
                fhash = sha256_bytes(text.encode("utf-8"))

                # Upsert code_files (unique by (repo_rel_path, git_commit))
                cur.execute(
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
                        psycopg2.Binary(fhash),
                        rel.startswith("tests/") or Path(rel).name.startswith("test_"),
                        False,
                        False,
                        "ok",
                        "{}",
                    ),
                )
                file_id = int(cur.fetchone()["id"])  # type: ignore[index]
                inserted_files += 1

                # Insert a module-level symbol row (simple first slice)
                cur.execute(
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
                symbol_id = int(cur.fetchone()["id"])  # type: ignore[index]
                inserted_symbols += 1

                # Create a single chunk for now (embedding left NULL; will be backfilled)
                chunk_hash = sha256_bytes(text.encode("utf-8"))
                cur.execute(
                    """
                    INSERT INTO code_chunks (file_id, symbol_id, chunk_index, content, docstring,
                                              token_count, content_hash, embedding, model_name, model_version, normalized, meta)
                    VALUES (%s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        file_id,
                        symbol_id,
                        0,
                        text,
                        None,
                        max(1, len(text) // 4),
                        psycopg2.Binary(chunk_hash),
                        None,  # embedding to be backfilled
                        None,
                        None,
                        False,
                        "{}",
                    ),
                )
                inserted_chunks += 1

        conn.commit()

    print(f"Ingest complete: files={inserted_files}, symbols={inserted_symbols}, chunks={inserted_chunks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
