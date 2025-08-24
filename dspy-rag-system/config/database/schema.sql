-- DSPy RAG System Database Schema
-- This schema sets up the PostgreSQL database with pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Document chunks table for vector storage
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(384), -- Cursor AI embedding dimension
    metadata JSONB DEFAULT '{}',
    document_id VARCHAR(255),
    chunk_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation memory table
CREATE TABLE IF NOT EXISTS conversation_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    human_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table for tracking uploaded documents
CREATE TABLE IF NOT EXISTS documents (
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

-- DSPy signatures table for storing signature definitions
CREATE TABLE IF NOT EXISTS dspy_signatures (
    id SERIAL PRIMARY KEY,
    signature_name VARCHAR(255) NOT NULL UNIQUE,
    signature_definition TEXT NOT NULL,
    signature_hash VARCHAR(64) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- DSPy examples table for storing signature examples
CREATE TABLE IF NOT EXISTS dspy_examples (
    id SERIAL PRIMARY KEY,
    signature_id INTEGER NOT NULL REFERENCES dspy_signatures(id) ON DELETE CASCADE,
    example_input TEXT NOT NULL,
    example_output TEXT NOT NULL,
    quality_score FLOAT DEFAULT 0.0,
    example_type VARCHAR(50) DEFAULT 'training',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_session_id ON conversation_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_created_at ON conversation_memory(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);

-- DSPy table indexes
CREATE INDEX IF NOT EXISTS idx_dspy_signatures_name ON dspy_signatures(signature_name);
CREATE INDEX IF NOT EXISTS idx_dspy_signatures_hash ON dspy_signatures(signature_hash);
CREATE INDEX IF NOT EXISTS idx_dspy_examples_signature_id ON dspy_examples(signature_id);
CREATE INDEX IF NOT EXISTS idx_dspy_examples_quality_score ON dspy_examples(quality_score);
CREATE INDEX IF NOT EXISTS idx_dspy_examples_type ON dspy_examples(example_type);

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

CREATE TRIGGER update_dspy_signatures_updated_at BEFORE UPDATE ON dspy_signatures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dspy_examples_updated_at BEFORE UPDATE ON dspy_examples
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
