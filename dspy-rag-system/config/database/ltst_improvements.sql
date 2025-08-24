-- LTST Memory System Improvements
-- Governance-aligned enhancements for conversation memory
-- Add to schema.sql or run as standalone patch

-- Phase 1: Essential improvements (local-first, simple)

-- 1) Add embedding column for semantic chat recall
ALTER TABLE conversation_memory
  ADD COLUMN IF NOT EXISTS embedding VECTOR(384);

-- 2) HNSW index for better recall/latency at small-mid scale
CREATE INDEX IF NOT EXISTS idx_cm_embedding_hnsw
  ON conversation_memory
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- 3) Promote DSPy tables to schema for reproducibility
CREATE TABLE IF NOT EXISTS dspy_signatures (
  id SERIAL PRIMARY KEY,
  signature_name VARCHAR(255) UNIQUE NOT NULL,
  prompt_structure TEXT NOT NULL,
  success_rate DOUBLE PRECISION DEFAULT 0,
  usage_count BIGINT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dspy_examples (
  id SERIAL PRIMARY KEY,
  signature_id INT NOT NULL REFERENCES dspy_signatures(id) ON DELETE CASCADE,
  input_data JSONB NOT NULL,
  output_data JSONB NOT NULL,
  quality_score DOUBLE PRECISION DEFAULT 0,
  context JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DSPy table indexes
CREATE INDEX IF NOT EXISTS idx_signatures_name ON dspy_signatures(signature_name);
CREATE INDEX IF NOT EXISTS idx_examples_signature ON dspy_examples(signature_id);
CREATE INDEX IF NOT EXISTS idx_examples_quality ON dspy_examples(quality_score);

-- 4) User/Session hygiene (future-proof without overbuilding)
ALTER TABLE conversation_memory
  ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- Phase 2: Simple manual cleanup (governance-friendly)
CREATE OR REPLACE FUNCTION cleanup_old_conversation_memory(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM conversation_memory
  WHERE created_at < CURRENT_TIMESTAMP - (INTERVAL '1 day' * days_to_keep);
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Usage: SELECT cleanup_old_conversation_memory(30);
