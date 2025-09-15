-- 02_indexes_online.sql
-- Online index creation (no table locks)

-- Documents
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_path
  ON documents(file_path);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_metadata_gin
  ON documents USING GIN (metadata);

-- Chunks
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunks_doc
  ON document_chunks(document_id, chunk_index);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunks_tsv_gin
  ON document_chunks USING GIN (content_tsv);

-- HNSW on normalized 384-d embeddings (cosine)
-- Run this separately outside of a transaction
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunks_embed_hnsw
  ON document_chunks USING hnsw (embedding vector_cosine_ops);
