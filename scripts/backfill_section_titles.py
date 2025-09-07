#!/usr/bin/env python3
"""
Backfill section_title/section_path for document_chunks using existing text.

Steps:
- Ensure optional canonical filename column exists and populate from documents.file_path
- Derive section_title/section_path per chunk from bm25_text
- Create section_ts index and ANALYZE

Requires POSTGRES_DSN in env.
"""
import os
import re
import sys
from typing import Tuple

import psycopg2
import psycopg2.extras

MD = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
PY = re.compile(r"^(?:@[\w\.]+\(.*\)\s*\n)*\s*(class|def)\s+([A-Za-z_]\w*)", re.MULTILINE)
JS = re.compile(r"^(?:export\s+)?(class|function|const)\s+([A-Za-z_]\w*)", re.MULTILINE)
SQL = re.compile(r"(?is)\b(CREATE|ALTER)\s+(INDEX|TABLE|VIEW)\s+(\"?[\w\.]+\"?)")


def derive_section_title(filename: str | None, text: str) -> Tuple[str, str]:
    fp = (filename or "").lower()
    # Markdown
    if fp.endswith(".md"):
        m = MD.search(text)
        if m:
            t = m.group(2).strip()
            return (t, t)
    # Python
    if fp.endswith(".py"):
        m = PY.search(text)
        if m:
            return (f"{m.group(1).title()}: {m.group(2)}", m.group(2))
    # JS/TS
    if fp.endswith((".js", ".ts", ".tsx", ".jsx")):
        m = JS.search(text)
        if m:
            return (f"{m.group(1).title() if m.group(1) else 'Symbol'}: {m.group(2)}", m.group(2))
    # SQL
    if fp.endswith(".sql"):
        m = SQL.search(text)
        if m:
            return (f"{m.group(2).title()}: {m.group(3)}", m.group(3).strip('"'))
    # YAML/TOML/ENV
    if fp.endswith((".yml", ".yaml", ".toml")) or os.path.basename(fp) in (".env", "config"):
        for ln in text.splitlines():
            if ":" in ln and not ln.strip().startswith(("#", "-")):
                k = ln.split(":", 1)[0].strip()
                if k:
                    return (f"Key: {k}", k)
                break
    # Fallbacks
    base = os.path.basename(filename) if filename else ""
    if base:
        return (base, base)
    for ln in text.splitlines():
        ln = ln.strip()
        if ln:
            return (ln[:80], ln[:80])
    return ("", "")


def main() -> int:
    dsn = os.environ.get("POSTGRES_DSN")
    if not dsn:
        print("❌ POSTGRES_DSN not set", file=sys.stderr)
        return 1

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    cur = conn.cursor()

    # Optional: add canonical filename and populate from documents.file_path
    cur.execute(
        """
        ALTER TABLE document_chunks
          ADD COLUMN IF NOT EXISTS filename text;
        """
    )
    conn.commit()

    # Populate filename from documents.file_path when possible
    cur.execute(
        """
        UPDATE document_chunks dc
        SET    filename = d.file_path
        FROM   documents d
        WHERE  dc.document_id = d.id
          AND  (dc.filename IS NULL OR dc.filename = '')
        """
    )
    conn.commit()

    # Create index for filename if missing
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chunks_filename ON document_chunks (filename);
        """
    )
    conn.commit()

    # Ensure section_title/section_path columns exist
    cur.execute(
        """
        ALTER TABLE document_chunks
          ADD COLUMN IF NOT EXISTS section_title text,
          ADD COLUMN IF NOT EXISTS section_path  text;
        """
    )
    conn.commit()

    # Batch process rows lacking section_title
    BATCH = 1000
    while True:
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute(
            """
            SELECT id, filename, bm25_text
            FROM document_chunks
            WHERE (section_title IS NULL OR section_title = '')
            ORDER BY id
            LIMIT %s
            """,
            (BATCH,),
        )
        rows = dict_cur.fetchall()
        if not rows:
            break

        updates = []
        for r in rows:
            _id = r["id"]
            fn = r["filename"]
            txt = r["bm25_text"] or ""
            title, path = derive_section_title(fn, txt)
            if title:
                updates.append((title, path, _id))

        if updates:
            psycopg2.extras.execute_batch(
                conn.cursor(),
                """
                UPDATE document_chunks
                SET section_title = %s, section_path = %s
                WHERE id = %s
                """,
                updates,
            )
        conn.commit()

    # Add tsvector and index, then analyze
    cur.execute(
        """
        ALTER TABLE document_chunks
          ADD COLUMN IF NOT EXISTS section_ts tsvector
            GENERATED ALWAYS AS (to_tsvector('simple', coalesce(section_title,''))) STORED;
        CREATE INDEX IF NOT EXISTS idx_chunks_section_ts ON document_chunks USING GIN (section_ts);
        ANALYZE document_chunks;
        """
    )
    conn.commit()
    conn.close()
    print("Backfill complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
