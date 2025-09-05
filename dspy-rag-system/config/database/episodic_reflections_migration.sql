-- Episodic Reflections Migration
-- Adds episodic memory capabilities to the existing LTST Memory System
-- Run this after the main LTST schema migration

-- Ensure pgvector extension is available
CREATE EXTENSION IF NOT EXISTS vector;

-- Create episodic_reflections table
CREATE TABLE IF NOT EXISTS episodic_reflections (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent VARCHAR(100) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    summary TEXT NOT NULL,
    what_worked JSONB NOT NULL DEFAULT '[]',
    what_to_avoid JSONB NOT NULL DEFAULT '[]',
    outcome_metrics JSONB NOT NULL DEFAULT '{}',
    source_refs JSONB NOT NULL DEFAULT '{}',
    span_hash VARCHAR(64) NOT NULL,
    embedding VECTOR(384),
    search_vector TSVECTOR
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_episodic_reflections_agent ON episodic_reflections(agent);
CREATE INDEX IF NOT EXISTS idx_episodic_reflections_task_type ON episodic_reflections(task_type);
CREATE INDEX IF NOT EXISTS idx_episodic_reflections_span_hash ON episodic_reflections(span_hash);
CREATE INDEX IF NOT EXISTS idx_episodic_reflections_created_at ON episodic_reflections(created_at);

-- Vector similarity index using HNSW (same as your existing LTST system)
CREATE INDEX IF NOT EXISTS idx_episodic_reflections_embedding
ON episodic_reflections USING hnsw (embedding vector_cosine_ops);

-- Full-text search index using GIN (same as your existing LTST system)
CREATE INDEX IF NOT EXISTS idx_episodic_reflections_search_vector
ON episodic_reflections USING gin (search_vector);

-- Add comments for documentation
COMMENT ON TABLE episodic_reflections IS 'Stores episodic reflections for learning from past work';
COMMENT ON COLUMN episodic_reflections.agent IS 'AI agent that performed the task (e.g., cursor_ai, dspy_agent)';
COMMENT ON COLUMN episodic_reflections.task_type IS 'Type of task performed (e.g., coding, analysis, planning)';
COMMENT ON COLUMN episodic_reflections.summary IS 'Brief summary of the task and outcome';
COMMENT ON COLUMN episodic_reflections.what_worked IS 'JSON array of what worked well in this task';
COMMENT ON COLUMN episodic_reflections.what_to_avoid IS 'JSON array of what to avoid in similar tasks';
COMMENT ON COLUMN episodic_reflections.outcome_metrics IS 'JSON object with task outcome metrics';
COMMENT ON COLUMN episodic_reflections.source_refs IS 'JSON object with references to source files, commits, etc.';
COMMENT ON COLUMN episodic_reflections.span_hash IS 'Stable hash of input/output for deduplication';
COMMENT ON COLUMN episodic_reflections.embedding IS 'Vector embedding for semantic similarity search';
COMMENT ON COLUMN episodic_reflections.search_vector IS 'Full-text search vector for keyword matching';

-- Verify the table was created
SELECT 'episodic_reflections table created successfully' as status;
