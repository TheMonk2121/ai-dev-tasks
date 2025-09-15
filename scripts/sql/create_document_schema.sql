-- Document and Chunk Schema for AI Dev Tasks
-- Comprehensive schema design with provenance, archiving, and retrieval hygiene

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Documents Table
CREATE TABLE documents (
  id              BIGSERIAL PRIMARY KEY,
  file_path       TEXT NOT NULL,                         -- e.g., repo path or URI
  file_name       TEXT NOT NULL,
  content_sha     TEXT NOT NULL,                         -- SHA-256 of raw text
  content_type    TEXT NOT NULL,                         -- 'md','pdf','html',etc
  metadata        JSONB NOT NULL DEFAULT '{}',
  is_archived     BOOLEAN NOT NULL DEFAULT FALSE,        -- mirrors 600_archives
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (file_path, content_sha)
);

-- Document Chunks Table
CREATE TABLE document_chunks (
  id              BIGSERIAL PRIMARY KEY,
  document_id     BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index     INT NOT NULL,
  content         TEXT NOT NULL,
  content_tsv     tsvector,                               -- maintained via trigger
  embedding       vector(384) NOT NULL,                   -- normalized; cosine
  metadata        JSONB NOT NULL DEFAULT '{}',            -- {char_len, token_len, chunk_variant, ingest_run_id, embedder_name, embedder_ver}
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (document_id, chunk_index)
);

-- Indexes
CREATE INDEX idx_documents_path ON documents(file_path);
CREATE INDEX idx_documents_metadata_gin ON documents USING GIN (metadata);
CREATE INDEX idx_chunks_doc ON document_chunks(document_id, chunk_index);
CREATE INDEX idx_chunks_tsv_gin ON document_chunks USING GIN (content_tsv);
CREATE INDEX idx_chunks_embed_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- Trigger Function to Maintain tsvector
CREATE OR REPLACE FUNCTION chunks_tsv_update() RETURNS trigger AS $$
BEGIN
  NEW.content_tsv := to_tsvector('english', NEW.content);
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

-- Trigger to Automatically Update tsvector
CREATE TRIGGER trg_chunks_tsv 
BEFORE INSERT OR UPDATE ON document_chunks 
FOR EACH ROW EXECUTE FUNCTION chunks_tsv_update();

-- Active Chunks View (Retrieval Hygiene)
CREATE OR REPLACE VIEW vw_active_chunks AS
SELECT dc.*
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id
WHERE d.is_archived = FALSE
  AND char_length(dc.content) >= 140;

-- Optional: Provenance Tracking Function
CREATE OR REPLACE FUNCTION track_document_provenance(
  p_file_path TEXT, 
  p_file_name TEXT, 
  p_content_sha TEXT, 
  p_content_type TEXT, 
  p_metadata JSONB DEFAULT '{}'
) RETURNS BIGINT AS $$
DECLARE
  v_document_id BIGINT;
BEGIN
  -- Upsert documents with unique (file_path, content_sha)
  INSERT INTO documents (
    file_path, file_name, content_sha, content_type, metadata, updated_at
  ) VALUES (
    p_file_path, p_file_name, p_content_sha, p_content_type, 
    p_metadata, NOW()
  )
  ON CONFLICT (file_path, content_sha) 
  DO UPDATE SET 
    metadata = COALESCE(documents.metadata, '{}') || EXCLUDED.metadata,
    updated_at = NOW()
  RETURNING id INTO v_document_id;

  RETURN v_document_id;
END;
$$ LANGUAGE plpgsql;

-- Sanity Check View
CREATE OR REPLACE VIEW document_chunk_stats AS
SELECT 
  COUNT(*) AS total_chunks,
  AVG(char_length(content)) AS avg_chunk_length,
  MIN(char_length(content)) AS min_chunk_length,
  MAX(char_length(content)) AS max_chunk_length,
  COUNT(CASE WHEN char_length(content) < 140 THEN 1 END) AS small_chunks_count,
  COUNT(DISTINCT document_id) AS unique_documents
FROM document_chunks;
