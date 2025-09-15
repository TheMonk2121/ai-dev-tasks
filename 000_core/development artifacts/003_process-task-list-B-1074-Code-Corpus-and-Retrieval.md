# Process Task List: B-1074 Code Corpus & Retrieval

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Executable task list to ship a separate code corpus without touching eval docs | You approved PRD B-1074 and want CI-ready tasks | Run tasks top-to-bottom; pause only at gates noted |

**Backlog ID**: B-1074  
**Priority**: High  
**Auto-Advance**: yes (schema and hooks require a short pause)  
**Scope guard**: Eval corpus and retrievers must remain unchanged

---

## 1) Environment and Protocol

```bash
export UV_PROJECT_ENVIRONMENT=.venv
uv sync --extra dev
# required extensions verified by readiness step below
```

Use DSN resolver for DB code; do not read DSN directly.

---

## 2) Tasks (CI-ready)

### T-1: Add Code Corpus Schema (idempotent DDL)
**Priority**: Critical  
**MoSCoW**: Must  
**Estimate**: 1h  
**Dependencies**: none  
**Profile(s)**: n/a  
**Commands**:
```bash
# Verify extensions and critical tables (readiness)
uv run python scripts/db_readiness_check.py | cat || true

# Apply DDL (create tables/indexes if not exist)
psql "$POSTGRES_DSN" -v ON_ERROR_STOP=1 <<'SQL'
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS code_files (
  id BIGSERIAL PRIMARY KEY,
  repo_rel_path  TEXT NOT NULL,
  language       TEXT NOT NULL,
  git_commit     TEXT NOT NULL,
  commit_time    TIMESTAMPTZ,
  content_hash   BYTEA,
  is_test        BOOLEAN DEFAULT FALSE,
  is_vendor      BOOLEAN DEFAULT FALSE,
  is_generated   BOOLEAN DEFAULT FALSE,
  parse_status   TEXT,
  license        TEXT,
  meta           JSONB DEFAULT '{}'::jsonb,
  created_at     TIMESTAMPTZ DEFAULT now(),
  UNIQUE (repo_rel_path, git_commit)
);

CREATE TABLE IF NOT EXISTS code_symbols (
  id BIGSERIAL PRIMARY KEY,
  file_id      BIGINT REFERENCES code_files(id) ON DELETE CASCADE,
  symbol_type  TEXT NOT NULL,
  symbol_name  TEXT NOT NULL,
  span_start   INTEGER,
  span_end     INTEGER,
  signature    TEXT,
  docstring    TEXT,
  doc_hash     BYTEA,
  meta         JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS code_chunks (
  id             BIGSERIAL PRIMARY KEY,
  file_id        BIGINT  REFERENCES code_files(id)   ON DELETE CASCADE,
  symbol_id      BIGINT  REFERENCES code_symbols(id) ON DELETE SET NULL,
  chunk_index    INTEGER NOT NULL,
  content        TEXT    NOT NULL,
  docstring      TEXT,
  token_count    INTEGER,
  content_hash   BYTEA,
  embedding      VECTOR(768),
  model_name     TEXT,
  model_version  TEXT,
  normalized     BOOLEAN,
  is_archived    BOOLEAN DEFAULT FALSE,
  meta           JSONB   DEFAULT '{}'::jsonb,
  created_at     TIMESTAMPTZ DEFAULT now(),
  comments_tsv   TSVECTOR GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(docstring, ''))
  ) STORED
);

CREATE INDEX IF NOT EXISTS code_chunks_hnsw
  ON code_chunks USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS code_chunks_trgm
  ON code_chunks USING GIN (content gin_trgm_ops);

CREATE INDEX IF NOT EXISTS code_chunks_comments_gin
  ON code_chunks USING GIN (comments_tsv);

CREATE INDEX IF NOT EXISTS code_chunks_file_idx ON code_chunks (file_id, chunk_index);
CREATE INDEX IF NOT EXISTS code_symbols_lookup ON code_symbols (symbol_type, symbol_name);
CREATE INDEX IF NOT EXISTS code_files_lang_idx ON code_files (language);
SQL
```
**Acceptance Criteria**
- [ ] DDL is idempotent; re-run produces no errors
- [ ] HNSW, trigram, and comments_tsv indexes exist
- [ ] Readiness step confirms `vector` and `pg_trgm`

**CI Gates**: ruff, black, pyright, pytest (schema smoke) pass

---

### T-2: Implement Python-Only Code Ingester (LibCST)
**Priority**: Critical  
**MoSCoW**: Must  
**Estimate**: 2h  
**Dependencies**: T-1  
**Profile(s)**: n/a  
**Commands**:
```bash
# Ingest .py under src/ and scripts/
PG_DSN="$POSTGRES_DSN" OLLAMA_URL="http://localhost:11434" EMBED_MODEL="bge-code-v1" \
uv run python scripts/ingest_code.py
```
**Description**  
- Symbol-scoped chunks (function/class; fallback module-level) with small context
- L2-normalize vectors; set model fields and `normalized=true`

**Acceptance Criteria**
- [ ] Inserts into `code_files`, `code_symbols`, `code_chunks`
- [ ] Embeddings dimension 768; cosine similarity sane on sample query
- [ ] `parse_status` recorded for fallbacks

**CI Gates**: unit tests for chunking; minimal DB integration test

---

### T-3: Pre-Push Change-Only Sync (soft-archive deletes)
**Priority**: High  
**MoSCoW**: Must  
**Estimate**: 1h  
**Dependencies**: T-2  
**Commands**:
```bash
# Install pre-push hook
./scripts/install_pre_push_code_sync.sh || true
```
**Acceptance Criteria**
- [ ] Modified/added `.py` re-embedded only; unchanged skipped by `content_hash`
- [ ] Deleted paths marked `is_archived=true`
- [ ] Hook runs < 5s for small diffs on local

**CI Gates**: lint/type/tests for hook installer

---

### T-4: Sanity Queries & Isolation Check
**Priority**: High  
**MoSCoW**: Must  
**Estimate**: 0.5h  
**Dependencies**: T-1..T-3  
**Commands**:
```bash
psql "$POSTGRES_DSN" -v ON_ERROR_STOP=1 <<'SQL'
SET LOCAL hnsw.ef_search = 100;
-- dense
SELECT id, file_id, symbol_id FROM code_chunks ORDER BY embedding <=> (SELECT embedding FROM code_chunks LIMIT 1) LIMIT 5;
-- trigram
SELECT id FROM code_chunks WHERE content ILIKE '%ErrInvalidState%' ORDER BY similarity(content,'ErrInvalidState') DESC LIMIT 5;
-- fts on comments/docstrings
SELECT id FROM code_chunks, to_tsquery('english','retry & backoff') q WHERE comments_tsv @@ q ORDER BY ts_rank_cd(comments_tsv,q) DESC LIMIT 5;
SQL
```
**Acceptance Criteria**
- [ ] All three query modes return sensible rows
- [ ] No queries against `documents/document_chunks` added or modified
- [ ] Eval retrieval behavior unchanged (spot-check pass)

---

### T-5: Tests and CI Wiring
**Priority**: High  
**MoSCoW**: Should  
**Estimate**: 1h  
**Dependencies**: T-2..T-4  
**Commands**:
```bash
uv run ruff check .
uv run black --check .
uv run basedpyright || uv run pyright
uv run pytest -q
```
**Acceptance Criteria**
- [ ] Lint/format/types/tests all green
- [ ] Minimal integration tests cover ingest + sample queries

---

### T-6: Docs & Anchors (400_ governance)
**Priority**: Medium  
**MoSCoW**: Should  
**Estimate**: 0.5h  
**Dependencies**: T-1..T-5  
**Commands**:
```bash
# no-op placeholder; edits to 400_ docs via anchors
true
```
**Acceptance Criteria**
- [ ] Add concise notes to existing 400_ guide anchors (no new guide files)
- [ ] Cross-references updated; TOC maintained

---

## 3) Quality Gates (roll-up)
- [ ] Code review complete
- [ ] Tests passing (unit/integration)
- [ ] Performance validated (pre-push < 5s on small diffs)
- [ ] Security reviewed (no secrets; vendor/generated excluded)
- [ ] Eval gates unaffected (no regressions)

---

## 4) Notes
- Keep workers small (INGEST_WORKERS=3) to avoid local thrash.
- Lock vector dim (768) and store model metadata to prevent drift.
- Future work: multi-language via tree-sitter; reranker; half-precision vectors.
