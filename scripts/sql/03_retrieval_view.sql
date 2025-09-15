-- 03_retrieval_view.sql
-- Retrieval hygiene view with archive and min-length filters

CREATE OR REPLACE VIEW vw_active_chunks AS
SELECT
  dc.id, dc.document_id, dc.chunk_index, dc.content, dc.content_tsv,
  dc.embedding, dc.metadata, dc.created_at,
  d.file_path, d.file_name, d.content_type, d.metadata AS doc_metadata
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id
WHERE d.is_archived = FALSE
  AND d.file_path NOT LIKE '600_archives/%'
  AND char_length(dc.content) >= 140;
