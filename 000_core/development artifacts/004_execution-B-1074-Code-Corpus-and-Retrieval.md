# Prioritized Execution — B-1074 Code Corpus & Retrieval

## Execution Configuration
- Auto-Advance: yes
- Pause Points: DB schema apply (T-1), hook install (T-3)
- Context Preservation: LTST (PRD refs, decisions)
- Smart Pausing: stop on schema errors or CI gate failures

## 0) Bootstrap
```bash
export UV_PROJECT_ENVIRONMENT=.venv
uv sync --extra dev
export SEED=42 MAX_WORKERS=3
```

## 1) Prerequisites
- Run readiness checks (extensions, profiles)
```bash
uv run python scripts/db_readiness_check.py | cat || true
uv run python scripts/ci_verify_profiles.py | cat || true
```

## 2) Prioritized Steps

### P1 — Ship schema safely (Must)
- Goal: Create isolated code corpus tables + indexes (idempotent)
- Command:
```bash
psql "$POSTGRES_DSN" -v ON_ERROR_STOP=1 <<'SQL'
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- code_files / code_symbols / code_chunks per PRD B-1074
-- HNSW (vector_cosine_ops), trigram, comments_tsv GIN, helper indexes
SQL
```
- Gates:
  - [ ] DDL re-runnable without errors
  - [ ] Indexes present (HNSW, trigram, comments GIN)

### P1 — Ingest Python code (Must)
- Goal: Symbol-aware chunks + embeddings (768-dim, normalized)
- Command:
```bash
PG_DSN="$POSTGRES_DSN" OLLAMA_URL="http://localhost:11434" EMBED_MODEL="bge-code-v1" \
uv run python scripts/ingest_code.py
```
- Gates:
  - [ ] Rows in code_files/symbols/chunks
  - [ ] Embeddings 768-dim, normalized=true

### P1 — Change-only pre-push sync (Must)
- Goal: Re-embed changed files only; soft-archive deletes
- Command:
```bash
./scripts/install_pre_push_code_sync.sh
```
- Gates:
  - [ ] Hook executes on push; small diffs < 5s
  - [ ] Unchanged files skipped via content_hash

### P2 — Sanity queries & isolation (Should)
- Goal: Validate hybrid search and no eval interference
- Commands:
```bash
psql "$POSTGRES_DSN" -v ON_ERROR_STOP=1 <<'SQL'
SET LOCAL hnsw.ef_search = 100;
-- dense
SELECT id FROM code_chunks ORDER BY embedding <=> (SELECT embedding FROM code_chunks LIMIT 1) LIMIT 5;
-- trigram
SELECT id FROM code_chunks WHERE content ILIKE '%ErrInvalidState%' ORDER BY similarity(content,'ErrInvalidState') DESC LIMIT 5;
-- comments FTS
SELECT id FROM code_chunks, to_tsquery('english','retry & backoff') q WHERE comments_tsv @@ q ORDER BY ts_rank_cd(comments_tsv,q) DESC LIMIT 5;
SQL
```
- Gates:
  - [ ] Results sensible for each mode
  - [ ] No changes to eval tables/retrievers

### P2 — CI gates (Should)
```bash
uv run ruff check .
uv run black --check .
uv run basedpyright || uv run pyright
uv run pytest -q
```
- Gates:
  - [ ] All pass locally and in PR

### P3 — Docs anchors (Could)
- Goal: Update 400_ anchors with brief notes (no new guides)
- Command:
```bash
true  # perform minimal anchor edits in 400_ docs
```
- Gates:
  - [ ] Anchors updated; TOC maintained

## 3) Quality Gates (roll-up)
- [ ] Code review complete
- [ ] Tests passing (unit/integration)
- [ ] Performance validated (hook < 5s on small diffs)
- [ ] Security reviewed (exclude vendor/generated/secrets)
- [ ] Eval unaffected (no retrieval regressions)

## 4) Output & Provenance
- State: `.ai_state.json` (git-ignored)
- Logs: structured stdout; store brief run notes in `metrics/` if applicable
- Record: `model_name`, `model_version`, `normalized`, `vector_dim=768`

## 5) Recovery Ladder
1) Re-run with `--json` logging; increase verbosity
2) Verify extensions; reduce `MAX_WORKERS=1`
3) Rebuild indexes after batch loads
4) Soft-archive conflicting rows; re-ingest file subset
5) Open HotFix task if gates fail; minimal change then refactor
