-- 01_documents_chunks_ddl.sql
-- Idempotent DDL migration for documents and chunks

-- Create documents table if not exists
CREATE TABLE IF NOT EXISTS documents (
  id              BIGSERIAL PRIMARY KEY,
  file_path       TEXT NOT NULL,
  file_name       TEXT NOT NULL,
  content_sha     TEXT NOT NULL,
  content_type    TEXT NOT NULL,
  is_archived     BOOLEAN NOT NULL DEFAULT FALSE,
  metadata        JSONB NOT NULL DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create document_chunks table if not exists
CREATE TABLE IF NOT EXISTS document_chunks (
  id              BIGSERIAL PRIMARY KEY,
  document_id     BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index     INT NOT NULL,
  content         TEXT NOT NULL,
  content_tsv     tsvector,
  embedding       vector(384) NOT NULL,
  metadata        JSONB NOT NULL DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Columns (idempotent)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='documents' AND column_name='is_archived'
  ) THEN
    ALTER TABLE documents ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT FALSE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='documents' AND column_name='metadata'
  ) THEN
    ALTER TABLE documents ADD COLUMN metadata JSONB NOT NULL DEFAULT '{}';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='document_chunks' AND column_name='content_tsv'
  ) THEN
    ALTER TABLE document_chunks ADD COLUMN content_tsv tsvector;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='document_chunks' AND column_name='metadata'
  ) THEN
    ALTER TABLE document_chunks ADD COLUMN metadata JSONB NOT NULL DEFAULT '{}';
  END IF;
END$$;

-- Constraints (idempotent)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='documents_path_sha_uniq'
  ) THEN
    ALTER TABLE documents
    ADD CONSTRAINT documents_path_sha_uniq UNIQUE (file_path, content_sha);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='document_chunks_doc_idx_uniq'
  ) THEN
    ALTER TABLE document_chunks
    ADD CONSTRAINT document_chunks_doc_idx_uniq UNIQUE (document_id, chunk_index);
  END IF;
END$$;

-- TSV trigger to auto-maintain content_tsv
CREATE OR REPLACE FUNCTION chunks_tsv_update() RETURNS trigger AS $$
BEGIN
  NEW.content_tsv := to_tsvector('english', NEW.content);
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname='trg_chunks_tsv'
  ) THEN
    CREATE TRIGGER trg_chunks_tsv
    BEFORE INSERT OR UPDATE ON document_chunks
    FOR EACH ROW EXECUTE FUNCTION chunks_tsv_update();
  END IF;
END$$;

-- Provenance tracking function
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
