-- 06_sanity_checks.sql
-- Sanity and performance check queries

-- How many chunks would the view exclude?
SELECT
  COUNT(*) AS total_chunks,
  SUM( (char_length(dc.content) < 140)::int ) AS too_short,
  SUM( (d.is_archived)::int ) AS archived
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id;

-- Confirm view works & uses indexes
EXPLAIN ANALYZE
SELECT id FROM vw_active_chunks
WHERE content_tsv @@ to_tsquery('english', 'retrieval & pipeline')
ORDER BY embedding <=> ARRAY[0.0, 0.0]::vector  -- placeholder, just to see plan
LIMIT 10;

-- Quick archive quality check
SELECT is_archived, COUNT(*) FROM documents GROUP BY 1 ORDER BY 1;

-- Chunk length distribution
SELECT 
  MIN(char_length(content)) AS min_length,
  MAX(char_length(content)) AS max_length,
  AVG(char_length(content)) AS avg_length,
  COUNT(*) AS total_chunks,
  SUM(CASE WHEN char_length(content) < 140 THEN 1 ELSE 0 END) AS chunks_below_140
FROM document_chunks;

-- Embedding dimension check
SELECT 
  MIN(vector_dims(embedding)) AS min_embedding_dim,
  MAX(vector_dims(embedding)) AS max_embedding_dim,
  COUNT(DISTINCT vector_dims(embedding)) AS unique_embedding_dims
FROM document_chunks;
