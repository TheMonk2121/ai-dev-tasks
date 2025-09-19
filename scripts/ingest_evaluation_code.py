#!/usr/bin/env python3
"""
Evaluation Code Ingester

Uses the manifest-driven approach to ingest only the evaluation system files
that are actually needed, without breaking existing imports or moving files around.
"""

from __future__ import annotations

import hashlib
import subprocess

# Add repo root to import path
import sys
import tempfile
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.evals.export import export_evaluation_bundle  # type: ignore
from src.common.db_dsn import resolve_dsn  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


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


def ingest_evaluation_bundle(bundle_dir: Path, dsn: str, commit: str, ctime: str | None) -> tuple[int, int, int]:
    """Ingest all Python files from the evaluation bundle."""
    inserted_files = 0
    inserted_symbols = 0
    inserted_chunks = 0

    # Find all Python files in the bundle
    python_files = list(bundle_dir.rglob("*.py"))

    with psycopg.connect(dsn) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            for fp in python_files:
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception as e:
                    print(f"skip {fp}: read error {e}")
                    continue

                # Calculate relative path from bundle root
                rel = str(fp.relative_to(bundle_dir))
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
                if not file_result:
                    continue
                file_id = file_result["id"]
                inserted_files += 1

                # Enhanced symbol extraction (functions and classes with proper body detection)
                symbols = []
                lines = text.split("\n")

                def find_function_end(start_line: int) -> int:
                    """Find the end line of a function by tracking indentation."""
                    if start_line >= len(lines):
                        return start_line

                    # Get the indentation of the function definition
                    def_line = lines[start_line - 1]
                    def_indent = len(def_line) - len(def_line.lstrip())

                    # Look for the next line with same or less indentation (not empty/comment)
                    for i in range(start_line, len(lines)):
                        line = lines[i]
                        if not line.strip() or line.strip().startswith("#"):
                            continue
                        line_indent = len(line) - len(line.lstrip())
                        if line_indent <= def_indent:
                            return i
                    return len(lines)

                def find_class_end(start_line: int) -> int:
                    """Find the end line of a class by tracking indentation."""
                    if start_line >= len(lines):
                        return start_line

                    # Get the indentation of the class definition
                    class_line = lines[start_line - 1]
                    class_indent = len(class_line) - len(class_line.lstrip())

                    # Look for the next line with same or less indentation (not empty/comment)
                    for i in range(start_line, len(lines)):
                        line = lines[i]
                        if not line.strip() or line.strip().startswith("#"):
                            continue
                        line_indent = len(line) - len(line.lstrip())
                        if line_indent <= class_indent:
                            return i
                    return len(lines)

                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if line.startswith("def ") and "(" in line:
                        name = line.split("(")[0].replace("def ", "").strip()
                        end_line = find_function_end(i)
                        symbols.append(("function", name, i, end_line))
                    elif line.startswith("class ") and ":" in line:
                        name = line.split(":")[0].replace("class ", "").strip()
                        end_line = find_class_end(i)
                        symbols.append(("class", name, i, end_line))

                # Insert symbols
                for symbol_type, symbol_name, start_line, end_line in symbols:
                    _ = cur.execute(
                        """
                        INSERT INTO code_symbols (file_id, symbol_type, symbol_name, span_start, span_end, meta)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (file_id, symbol_type, symbol_name, start_line, end_line, "{}"),
                    )
                    symbol_result = cur.fetchone()
                    if symbol_result:
                        symbol_id = symbol_result["id"]
                        inserted_symbols += 1

                        # Enhanced chunking (split by functions/classes with full body)
                        chunk_content = f"{symbol_type} {symbol_name}\n" + "\n".join(lines[start_line - 1 : end_line])

                        _ = cur.execute(
                            """
                            INSERT INTO code_chunks (file_id, symbol_id, chunk_index, content, token_count, 
                                                    content_hash, embedding, model_name, normalized, meta)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                file_id,
                                symbol_id,
                                0,  # chunk_index
                                chunk_content,
                                len(chunk_content.split()),  # rough token count
                                sha256_bytes(chunk_content.encode("utf-8")),
                                None,  # embedding - will be filled by separate process
                                "BAAI/bge-small-en-v1.5",
                                True,
                                "{}",
                            ),
                        )
                        inserted_chunks += 1

    return inserted_files, inserted_symbols, inserted_chunks


def main() -> int:
    """Main entry point."""
    dsn = resolve_dsn(strict=True)
    commit = current_commit()
    ctime = current_commit_time()

    # Create temporary directory for bundle
    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_dir = Path(temp_dir) / "evaluation_bundle"

        # Export evaluation bundle using manifest
        manifest_path = PROJECT_ROOT / "evals" / "manifest.yml"
        export_evaluation_bundle(manifest_path, bundle_dir, "clean_dspy")

        print(f"📦 Exported evaluation bundle to {bundle_dir}")
        print(f"📁 Bundle contains {len(list(bundle_dir.rglob('*.py')))} Python files")

        # Ingest the bundle
        inserted_files, inserted_symbols, inserted_chunks = ingest_evaluation_bundle(bundle_dir, dsn, commit, ctime)

        print(f"Ingest complete: files={inserted_files}, symbols={inserted_symbols}, chunks={inserted_chunks}")

        return 0


if __name__ == "__main__":
    exit(main())
