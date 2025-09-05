-- Quick migration to add content_tsv and GIN index to legacy document_chunks
-- Safe to run multiple times due to IF NOT EXISTS guards

-- Add tsvector column if missing
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'document_chunks' AND column_name = 'content_tsv'
  ) THEN
    ALTER TABLE document_chunks ADD COLUMN content_tsv TSVECTOR;
  END IF;
END$$;

-- Backfill content_tsv from content
UPDATE document_chunks
SET content_tsv = to_tsvector('english', content)
WHERE content_tsv IS NULL;

-- Create GIN index if missing
CREATE INDEX IF NOT EXISTS idx_document_chunks_content_tsv
ON document_chunks USING gin (content_tsv);

