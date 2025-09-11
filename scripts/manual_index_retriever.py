#!/usr/bin/env python3
"""
Manually index the retriever files that the documentation_indexer can't handle.
"""
import hashlib
import os
import sys
from pathlib import Path
from typing import Any, cast

import psycopg2
from psycopg2.extras import RealDictCursor


def get_file_content(file_path):
    """Read file content"""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def split_python_content(content, max_chunk_size=900):
    """Split Python content into function/class-aware chunks"""
    chunks = []
    lines = content.splitlines()
    current_chunk = []
    current_size = 0

    for i, line in enumerate(lines):
        current_chunk.append(line)
        current_size += len(line) + 1

        # Split on function/class definitions or size limit
        if (line.strip().startswith(("def ", "class ")) and current_size > 100) or current_size >= max_chunk_size:
            if current_chunk:
                chunk_content = "\n".join(current_chunk).strip()
                if len(chunk_content) > 50:
                    chunks.append({"content": chunk_content, "start_line": i - len(current_chunk) + 1, "end_line": i})
                current_chunk = []
                current_size = 0

    # Add remaining content
    if current_chunk:
        chunk_content = "\n".join(current_chunk).strip()
        if len(chunk_content) > 50:
            chunks.append(
                {"content": chunk_content, "start_line": len(lines) - len(current_chunk) + 1, "end_line": len(lines)}
            )

    return chunks or [{"content": content, "start_line": 1, "end_line": len(lines)}]


def index_file(file_path, dsn):
    """Index a single file"""
    content = get_file_content(file_path)
    if not content:
        return False

    file_path_str = str(file_path)
    filename = file_path.name
    file_type = file_path.suffix[1:] if file_path.suffix else "txt"
    file_size = len(content)
    content_sha = hashlib.sha256(content.encode()).hexdigest()

    # Split content into chunks
    chunks = split_python_content(content)

    try:
        with psycopg2.connect(dsn, cursor_factory=RealDictCursor) as conn:
            with conn.cursor() as cur:
                # Insert document
                cur.execute(
                    """
                    INSERT INTO documents (filename, file_path, file_type, file_size, chunk_count, status, content_sha)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (filename, file_path_str, file_type, file_size, len(chunks), "indexed", content_sha),
                )

                result_raw = cur.fetchone()
                document_id: int
                if result_raw is not None:
                    row_dict = cast(dict[str, Any], result_raw)
                    if "id" in row_dict:
                        document_id = int(row_dict["id"])  # RealDictCursor returns a dict-like row
                    else:
                        # Get existing document ID
                        cur.execute("SELECT id FROM documents WHERE content_sha = %s", (content_sha,))
                        row2_raw = cur.fetchone()
                        if row2_raw is None:
                            raise RuntimeError("Failed to retrieve document id after insert/select")
                        row2 = cast(dict[str, Any], row2_raw)
                        document_id = int(row2["id"])  # type: ignore[reportUnknownArgumentType]
                else:
                    # Get existing document ID
                    cur.execute("SELECT id FROM documents WHERE content_sha = %s", (content_sha,))
                    row3_raw = cur.fetchone()
                    if row3_raw is None:
                        raise RuntimeError("Failed to retrieve document id after insert/select")
                    row3 = cast(dict[str, Any], row3_raw)
                    document_id = int(row3["id"])  # type: ignore[reportUnknownArgumentType]

                # Insert chunks
                for i, chunk in enumerate(chunks):
                    chunk_content = chunk["content"]
                    cur.execute(
                        """
                        INSERT INTO document_chunks (
                            document_id, chunk_index, file_path, line_start, line_end, content,
                            embedding_text, bm25_text, chunk_id, filename
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s
                        )
                    """,
                        (
                            document_id,
                            i,
                            file_path_str,
                            chunk["start_line"],
                            chunk["end_line"],
                            chunk_content,
                            chunk_content,
                            chunk_content,
                            f"{filename[:10]}_{i}",
                            filename,
                        ),
                    )

                conn.commit()
                print(f"✅ Indexed {filename} with {len(chunks)} chunks")
                return True

    except Exception as e:
        print(f"❌ Error indexing {file_path}: {e}")
        return False


def main():
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    retriever_dir = Path("src/dspy_modules/retriever")

    if not retriever_dir.exists():
        print(f"❌ Directory {retriever_dir} does not exist")
        return

    files_to_index = ["query_rewrite.py", "rerank.py", "pg.py", "limits.py", "weights.py"]

    success_count = 0
    for filename in files_to_index:
        file_path = retriever_dir / filename
        if file_path.exists():
            if index_file(file_path, dsn):
                success_count += 1
        else:
            print(f"⚠️ File {file_path} does not exist")

    print(f"\n🎯 Successfully indexed {success_count}/{len(files_to_index)} files")


if __name__ == "__main__":
    main()
