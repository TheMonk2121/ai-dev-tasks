-- Clean content tables for fresh re-ingestion
-- This script clears all content-related tables while preserving evaluation data

-- Disable foreign key checks temporarily for faster cleanup
SET session_replication_role = replica;

-- Clear content tables in dependency order
TRUNCATE TABLE document_chunks CASCADE;
TRUNCATE TABLE documents CASCADE;
TRUNCATE TABLE atlas_edge CASCADE;
TRUNCATE TABLE atlas_node CASCADE;

-- Reset sequences to start from 1
ALTER SEQUENCE documents_id_seq RESTART WITH 1;
ALTER SEQUENCE document_chunks_id_seq RESTART WITH 1;
ALTER SEQUENCE atlas_edge_edge_id_seq RESTART WITH 1;

-- Re-enable foreign key checks
SET session_replication_role = DEFAULT;

-- Verify cleanup
SELECT 
    'documents' as table_name, COUNT(*) as remaining_rows FROM documents
UNION ALL
SELECT 
    'document_chunks' as table_name, COUNT(*) as remaining_rows FROM document_chunks
UNION ALL
SELECT 
    'atlas_node' as table_name, COUNT(*) as remaining_rows FROM atlas_node
UNION ALL
SELECT 
    'atlas_edge' as table_name, COUNT(*) as remaining_rows FROM atlas_edge;

-- Show that evaluation data is preserved
SELECT 
    'eval_event' as table_name, COUNT(*) as remaining_rows FROM eval_event
UNION ALL
SELECT 
    'eval_run' as table_name, COUNT(*) as remaining_rows FROM eval_run;
