-- Materialize path_tsv on documents and add GIN index
ALTER TABLE documents
  ADD COLUMN IF NOT EXISTS path_tsv tsvector GENERATED ALWAYS AS (
    to_tsvector('simple', replace(replace(lower(coalesce(file_path,'')), '/', ' '), '_', ' '))
  ) STORED;

CREATE INDEX IF NOT EXISTS idx_documents_path_tsv ON documents USING GIN (path_tsv);
ANALYZE documents;

