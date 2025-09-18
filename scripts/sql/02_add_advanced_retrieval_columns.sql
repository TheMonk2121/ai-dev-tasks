-- 02_add_advanced_retrieval_columns.sql
-- Add advanced retrieval columns to support sophisticated text search and processing

-- Add missing columns to document_chunks table
DO $$
BEGIN
  -- Add short_tsv column for short text search
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='document_chunks' AND column_name='short_tsv'
  ) THEN
    ALTER TABLE document_chunks ADD COLUMN short_tsv tsvector;
    CREATE INDEX idx_chunks_short_tsv_gin ON document_chunks USING GIN (short_tsv);
    RAISE NOTICE 'Added short_tsv column and index';
  END IF;

  -- Add title_tsv column for title text search
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='document_chunks' AND column_name='title_tsv'
  ) THEN
    ALTER TABLE document_chunks ADD COLUMN title_tsv tsvector;
    CREATE INDEX idx_chunks_title_tsv_gin ON document_chunks USING GIN (title_tsv);
    RAISE NOTICE 'Added title_tsv column and index';
  END IF;

  -- Add embedding_text column for processed embedding text
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='document_chunks' AND column_name='embedding_text'
  ) THEN
    ALTER TABLE document_chunks ADD COLUMN embedding_text TEXT;
    RAISE NOTICE 'Added embedding_text column';
  END IF;

  -- Add bm25_text column for BM25 processed text
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='document_chunks' AND column_name='bm25_text'
  ) THEN
    ALTER TABLE document_chunks ADD COLUMN bm25_text TEXT;
    RAISE NOTICE 'Added bm25_text column';
  END IF;

  -- Add path_tsv column to documents table for path-based search
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='documents' AND column_name='path_tsv'
  ) THEN
    ALTER TABLE documents ADD COLUMN path_tsv tsvector;
    CREATE INDEX idx_documents_path_tsv_gin ON documents USING GIN (path_tsv);
    RAISE NOTICE 'Added path_tsv column and index to documents';
  END IF;
END$$;

-- Create trigger function to maintain tsvector columns
CREATE OR REPLACE FUNCTION update_chunk_tsvectors() RETURNS trigger AS $$
BEGIN
  -- Update content_tsv (already exists, but ensure it's maintained)
  NEW.content_tsv := to_tsvector('english', COALESCE(NEW.content, ''));
  
  -- Update short_tsv (first 200 chars for quick matching)
  NEW.short_tsv := to_tsvector('english', LEFT(COALESCE(NEW.content, ''), 200));
  
  -- Update title_tsv (extract title-like content from first line or metadata)
  DECLARE
    title_text TEXT;
  BEGIN
    -- Try to extract title from first line if it looks like a heading
    title_text := CASE 
      WHEN NEW.content ~ '^#+\s+' THEN regexp_replace(NEW.content, '^#+\s+', '', 'g')
      WHEN NEW.content ~ '^[A-Z][^#\n]*$' THEN split_part(NEW.content, E'\n', 1)
      ELSE COALESCE(NEW.metadata->>'title', '')
    END;
    NEW.title_tsv := to_tsvector('english', COALESCE(title_text, ''));
  END;
  
  -- Set embedding_text to content if not already set
  IF NEW.embedding_text IS NULL OR NEW.embedding_text = '' THEN
    NEW.embedding_text := NEW.content;
  END IF;
  
  -- Set bm25_text to content if not already set
  IF NEW.bm25_text IS NULL OR NEW.bm25_text = '' THEN
    NEW.bm25_text := NEW.content;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for document_chunks
DROP TRIGGER IF EXISTS trigger_update_chunk_tsvectors ON document_chunks;
CREATE TRIGGER trigger_update_chunk_tsvectors
  BEFORE INSERT OR UPDATE ON document_chunks
  FOR EACH ROW
  EXECUTE FUNCTION update_chunk_tsvectors();

-- Create trigger function for documents path_tsv
CREATE OR REPLACE FUNCTION update_document_path_tsv() RETURNS trigger AS $$
BEGIN
  NEW.path_tsv := to_tsvector('simple', 
    replace(replace(COALESCE(NEW.file_path, ''), '/', ' '), '_', ' ')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for documents
DROP TRIGGER IF EXISTS trigger_update_document_path_tsv ON documents;
CREATE TRIGGER trigger_update_document_path_tsv
  BEFORE INSERT OR UPDATE ON documents
  FOR EACH ROW
  EXECUTE FUNCTION update_document_path_tsv();

-- Update existing data
UPDATE document_chunks SET 
  short_tsv = to_tsvector('english', LEFT(COALESCE(content, ''), 200)),
  title_tsv = to_tsvector('english', 
    CASE 
      WHEN content ~ '^#+\s+' THEN regexp_replace(content, '^#+\s+', '', 'g')
      WHEN content ~ '^[A-Z][^#\n]*$' THEN split_part(content, E'\n', 1)
      ELSE COALESCE(metadata->>'title', '')
    END
  ),
  embedding_text = COALESCE(embedding_text, content),
  bm25_text = COALESCE(bm25_text, content)
WHERE short_tsv IS NULL OR title_tsv IS NULL OR embedding_text IS NULL OR bm25_text IS NULL;

UPDATE documents SET 
  path_tsv = to_tsvector('simple', 
    replace(replace(COALESCE(file_path, ''), '/', ' '), '_', ' ')
  )
WHERE path_tsv IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN document_chunks.short_tsv IS 'Text search vector for first 200 characters, optimized for quick matching';
COMMENT ON COLUMN document_chunks.title_tsv IS 'Text search vector for title/heading content extracted from chunk';
COMMENT ON COLUMN document_chunks.embedding_text IS 'Processed text used for embedding generation';
COMMENT ON COLUMN document_chunks.bm25_text IS 'Processed text optimized for BM25 scoring';
COMMENT ON COLUMN documents.path_tsv IS 'Text search vector for file path, enabling path-based search';

-- Migration completed successfully
