-- DSPy RAG System - Clean Slate Schema
-- Based on ChatGPT's recommendations for deterministic, performant storage
-- Run this as a single transaction for atomic migration

BEGIN;

-- Required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Drop old tables (CASCADE ensures clean slate)
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS conversation_memory CASCADE;

-- Documents table (source of truth)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks table (first-class hot-path columns)
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    content TEXT NOT NULL,
    embedding VECTOR(384),  -- Cursor AI embedding dimension
    is_anchor BOOLEAN DEFAULT FALSE,
    anchor_key TEXT,
    metadata JSONB DEFAULT '{}',
    content_tsv tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(content, ''))
    ) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Span sanity check (nulls allowed; if present, enforce order)
    CONSTRAINT chk_span_valid CHECK (
        line_start IS NULL OR line_end IS NULL OR line_end >= line_start
    )
);

-- Conversation memory table (preserved from original)
CREATE TABLE conversation_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    human_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Helpful uniqueness & hot-path indexes
CREATE UNIQUE INDEX ux_document_chunks_doc_chunk
    ON document_chunks (document_id, chunk_index);

CREATE INDEX idx_document_chunks_content_tsv
    ON document_chunks USING GIN (content_tsv);

CREATE INDEX idx_document_chunks_file_path
    ON document_chunks (file_path);

CREATE INDEX idx_document_chunks_anchor_key
    ON document_chunks (anchor_key);

-- Fast anchor filter (partial index)
CREATE INDEX idx_document_chunks_is_anchor_true
    ON document_chunks (id)
    WHERE is_anchor = TRUE;

-- ANN vector index (HNSW for better performance)
CREATE INDEX idx_document_chunks_embedding_hnsw
    ON document_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m=16, ef_construction=64);

-- Preserve existing indexes for conversation_memory
CREATE INDEX idx_conversation_memory_session_id ON conversation_memory(session_id);
CREATE INDEX idx_conversation_memory_created_at ON conversation_memory(created_at);
CREATE INDEX idx_documents_status ON documents(status);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_document_chunks_updated_at BEFORE UPDATE ON document_chunks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
