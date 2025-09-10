#!/usr/bin/env bash
set -euo pipefail

# Lightweight DB init for CI to stabilize DB-backed code paths.
# Uses env vars (with sensible defaults) and is safe to run multiple times.

PGHOST=${PGHOST:-localhost}
PGPORT=${PGPORT:-5432}
PGUSER=${PGUSER:-postgres}
PGPASSWORD=${PGPASSWORD:-postgres}
PGDATABASE=${PGDATABASE:-ai_agency}

export PGPASSWORD="$PGPASSWORD"

echo "⏳ Waiting for Postgres at ${PGHOST}:${PGPORT}/${PGDATABASE}..."
for i in {1..30}; do
  if psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT 1" >/dev/null 2>&1; then
    echo "✅ Postgres is ready"
    break
  fi
  sleep 2
  if [[ $i -eq 30 ]]; then
    echo "❌ Postgres did not become ready in time" >&2
    exit 1
  fi
done

echo "🔧 Initializing extensions (best-effort)"
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=0 -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" || true
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=0 -c "CREATE EXTENSION IF NOT EXISTS vector;" || true

echo "🗄️  Ensuring episodic_logs schema exists"
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS episodic_logs (
  id SERIAL PRIMARY KEY,
  user_id TEXT,
  model_type TEXT,
  prompt TEXT,
  response TEXT,
  tokens_used INTEGER,
  cache_hit BOOLEAN DEFAULT FALSE,
  similarity_score DOUBLE PRECISION DEFAULT 0.0,
  last_verified TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
SQL

echo "✅ DB initialization complete"

# Optional performance indexes (idempotent)
echo "⚙️  Ensuring performance indexes"
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=1 <<'SQL'
-- Trigram index for prompt similarity search
CREATE INDEX IF NOT EXISTS idx_episodic_logs_prompt_trgm ON episodic_logs USING gin (prompt gin_trgm_ops);

-- Recency indexes for typical queries
CREATE INDEX IF NOT EXISTS idx_episodic_logs_updated_at ON episodic_logs (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_logs_last_verified ON episodic_logs (last_verified DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_logs_user_updated ON episodic_logs (user_id, updated_at DESC);
SQL

# Optional vector column for future pgvector experiments
echo "🧪 Enabling optional vector column when extension is present (non-fatal)"
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=0 <<'SQL'
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'vector'
  ) THEN
    BEGIN
      ALTER TABLE episodic_logs ADD COLUMN IF NOT EXISTS embedding vector(1536);
    EXCEPTION WHEN OTHERS THEN
      -- ignore failures (type mismatch etc.)
      NULL;
    END;
  END IF;
END$$;
SQL
