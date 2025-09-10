-- Clean Slate Schema for Lean Hybrid Memory Rehydration System
-- This drops existing tables and recreates them with the perfect schema

-- Drop existing tables (if they exist)
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Documents table for tracking uploaded documents
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

-- Document chunks table with all first-class columns for Lean Hybrid
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255),
    chunk_index INTEGER,
    file_path TEXT,                    -- First-class column for hot path
    line_start INTEGER,                -- Span tracking for citations
    line_end INTEGER,                  -- Span tracking for citations
    content TEXT NOT NULL,
    embedding VECTOR(384),             -- Cursor AI embedding dimension
    is_anchor BOOLEAN DEFAULT FALSE,   -- First-class column for fast filtering
    anchor_key TEXT,                   -- First-class column for fast filtering
    metadata JSONB DEFAULT '{}',       -- Additional metadata
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create all indexes for optimal performance
-- FTS index for BM25 search
CREATE INDEX IF NOT EXISTS idx_document_chunks_content_tsv
    ON document_chunks USING GIN (content_tsv);

-- Hot-path helper indexes
CREATE INDEX IF NOT EXISTS idx_document_chunks_anchor_key
    ON document_chunks (anchor_key);
CREATE INDEX IF NOT EXISTS idx_document_chunks_file_path
    ON document_chunks (file_path);

-- HNSW index for fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw
    ON document_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m=16, ef_construction=64);

-- Uniqueness constraint for document/chunk combinations
CREATE UNIQUE INDEX IF NOT EXISTS ux_document_chunks_doc_chunk
    ON document_chunks (document_id, chunk_index);

-- Additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
    ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_is_anchor
    ON document_chunks (is_anchor);

-- JSONB index for metadata queries
CREATE INDEX IF NOT EXISTS idx_document_chunks_metadata_gin
    ON document_chunks USING GIN (metadata);

-- Timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_document_chunks_updated_at
    BEFORE UPDATE ON document_chunks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
