-- 04_backfill_archives_and_tsv.sql
-- Backfill archives, tsvectors, and metadata

-- A. Mark archives & deprecated
UPDATE documents
SET is_archived = TRUE
WHERE file_path LIKE '600_archives/%' AND is_archived = FALSE;

-- Archive by metadata marker (if you use it)
UPDATE documents
SET is_archived = TRUE
WHERE COALESCE(metadata->>'status','') IN ('deprecated','archived')
  AND is_archived = FALSE;

-- B. Populate missing tsvectors (batch-friendly)
-- Do it in batches to avoid long transactions
WITH cte AS (
  SELECT id FROM document_chunks
  WHERE content_tsv IS NULL
  ORDER BY id
  LIMIT 5000
)
UPDATE document_chunks dc
SET content_tsv = to_tsvector('english', dc.content)
FROM cte
WHERE dc.id = cte.id;

-- C. Record char/token lengths in metadata (optional but useful)
-- Char length
UPDATE document_chunks
SET metadata = jsonb_set(metadata, '{char_len}', to_jsonb(char_length(content)))
WHERE (metadata->>'char_len') IS NULL;

-- D. Stats refresh
ANALYZE documents;
ANALYZE document_chunks;
