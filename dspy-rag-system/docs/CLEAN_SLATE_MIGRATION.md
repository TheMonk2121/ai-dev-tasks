# Clean Slate Database Migration

## Overview

This migration implements ChatGPT's recommendations for a deterministic, performant database schema with proper relational integrity and optimized indexes.

## Key Improvements

### 1. **Relational Integrity**
- `document_id` as `INTEGER REFERENCES documents(id) ON DELETE CASCADE`
- Proper foreign key constraints prevent data drift
- CASCADE deletes maintain referential integrity

### 2. **Span Validation**
- `CHECK (line_end >= line_start)` constraint prevents bad ranges
- Null-tolerant logic allows missing spans
- Protects path#line deduplication logic

### 3. **Optimized Indexes**
- HNSW vector index for fast ANN search
- Partial index on `is_anchor = TRUE` for anchor queries
- GIN index on `content_tsv` for full-text search
- Unique constraint on `(document_id, chunk_index)`

### 4. **Stable Ordering**
- Vector search: `ORDER BY distance ASC, file_path NULLS LAST, chunk_index NULLS LAST, id ASC`
- BM25 search: `ORDER BY bm25 DESC, file_path NULLS LAST, chunk_index NULLS LAST, id ASC`
- Deterministic results across runs

### 5. **Improved Canonicalizer**
- Soft-fail by default for solo-dev ergonomics
- Strict mode toggle: `REHYDRATE_STRICT_IDS=1`
- Enforces real PK `id` from store
- Deterministic path generation: spans → chunk → file

## Migration Steps

### 1. **Dry Run (Recommended)**
```bash
cd dspy-rag-system
python3 scripts/apply_clean_slate_schema.py --dry-run
```

### 2. **Apply Migration**
```bash
# With backup (recommended)
python3 scripts/apply_clean_slate_schema.py --backup

# Without backup (if you're sure)
python3 scripts/apply_clean_slate_schema.py
```

### 3. **Re-ingest Documents**
```bash
./start_watch_folder.sh
```

### 4. **Test the System**
```bash
# Test rehydrator
python3 scripts/cursor_memory_rehydrate.py planner "test query"

# Verify deterministic results
python3 scripts/cursor_memory_rehydrate.py planner "same query"  # Should return identical results
```

## Schema Changes

### Before (Legacy)
```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(384),
    metadata JSONB DEFAULT '{}',
    document_id VARCHAR(255),  -- String, no FK
    chunk_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### After (Clean Slate)
```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    content TEXT NOT NULL,
    embedding VECTOR(384),
    is_anchor BOOLEAN DEFAULT FALSE,
    anchor_key TEXT,
    metadata JSONB DEFAULT '{}',
    content_tsv tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(content, ''))
    ) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_span_valid CHECK (
        line_start IS NULL OR line_end IS NULL OR line_end >= line_start
    )
);
```

## Search Queries

### Vector Search (Cosine Distance)
```sql
SELECT
  id, document_id, chunk_index, file_path, line_start, line_end,
  content, is_anchor, anchor_key, metadata,
  (embedding <=> %s::vector) AS distance
FROM document_chunks
WHERE embedding IS NOT NULL
ORDER BY embedding <=> %s::vector ASC,
         file_path NULLS LAST,
         chunk_index NULLS LAST,
         id ASC
LIMIT %s;
```

### BM25 Search (Full-Text)
```sql
SELECT
  id, document_id, chunk_index, file_path, line_start, line_end,
  content, is_anchor, anchor_key, metadata,
  ts_rank_cd(content_tsv, websearch_to_tsquery('english', %s)) AS bm25
FROM document_chunks
WHERE content_tsv @@ websearch_to_tsquery('english', %s)
ORDER BY bm25 DESC,
         file_path NULLS LAST,
         chunk_index NULLS LAST,
         id ASC
LIMIT %s;
```

## Configuration

### Environment Variables
- `REHYDRATE_STRICT_IDS=1` - Enable strict ID validation
- `POSTGRES_DSN` - Database connection string

### Kill-Switches
- `--no-rrf` - Disable BM25+RRF fusion (pure vector)
- `--dedupe file` - File-level deduplication only
- `--expand-query off` - Disable query expansion

## Benefits

1. **Determinism** - Same query always returns same results
2. **Performance** - Optimized indexes and stable ordering
3. **Integrity** - Foreign keys prevent data corruption
4. **Maintainability** - Clean schema with proper constraints
5. **Solo-Dev Friendly** - Soft-fail defaults with strict mode option

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the right directory
   cd dspy-rag-system
   python3 scripts/apply_clean_slate_schema.py --dry-run
   ```

2. **Database Connection**
   ```bash
   # Check environment variable
   echo $POSTGRES_DSN

   # Test connection
   psql "$POSTGRES_DSN" -c "SELECT version();"
   ```

3. **Permission Issues**
   ```bash
   # Ensure PostgreSQL user has CREATE/DROP privileges
   psql "$POSTGRES_DSN" -c "GRANT ALL ON DATABASE your_db TO your_user;"
   ```

### Rollback

If you created a backup, you can rollback:
```sql
-- Drop new tables
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

-- Restore from backup
CREATE TABLE document_chunks AS SELECT * FROM document_chunks_backup;
CREATE TABLE documents AS SELECT * FROM documents_backup;
```

## Validation

After migration, verify:

1. **Deterministic Results**
   ```bash
   # Run same query multiple times
   python3 scripts/cursor_memory_rehydrate.py planner "test"
   python3 scripts/cursor_memory_rehydrate.py planner "test"
   # Results should be identical
   ```

2. **Performance**
   ```bash
   # Check query performance
   python3 scripts/cursor_memory_rehydrate.py planner "complex query" --debug
   ```

3. **Kill-Switches**
   ```bash
   # Test different modes
   python3 scripts/cursor_memory_rehydrate.py planner "test" --no-rrf
   python3 scripts/cursor_memory_rehydrate.py planner "test" --dedupe file
   ```

## Credits

This migration is based on ChatGPT's recommendations for:
- Clean-slate approach over migration gymnastics
- Proper relational integrity with foreign keys
- Span validation constraints
- Optimized indexes for performance
- Deterministic ordering for consistent results
- Solo-developer ergonomics with strict mode toggle

<!-- README_AUTOFIX_START -->
# Auto-generated sections for CLEAN_SLATE_MIGRATION.md
# Generated: 2025-08-17T21:49:49.325519

## Missing sections to add:

## Last Reviewed

2025-08-17

## Owner

[Document owner/maintainer information]

## Usage

[Describe how to use this document or system]

<!-- README_AUTOFIX_END -->
