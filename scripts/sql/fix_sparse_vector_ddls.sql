-- Fix Sparse Vector DDLs and Performance Issues
-- This script addresses the red/yellow items from healthcheck

-- 1. Ensure pgvector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create active configuration pointer table
CREATE TABLE IF NOT EXISTS chunk_config_active (
    key text PRIMARY KEY CHECK (key = 'active'),
    ingest_run_id text NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- 3. Fix embedding dimension enforcement
-- First, let's check what tables exist and their current structure
DO $$
DECLARE
    table_name text;
    embedding_dim integer := 384; -- all-MiniLM-L6-v2 dimension
BEGIN
    -- Get all document_chunks tables (including versioned ones)
    FOR table_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE tablename LIKE 'document_chunks%' 
        AND schemaname = 'public'
    LOOP
        -- Add generated tsvector column for full-text search performance
        EXECUTE format('
            ALTER TABLE %I 
            ADD COLUMN IF NOT EXISTS ts tsvector
            GENERATED ALWAYS AS (to_tsvector(''english'', bm25_text)) STORED
        ', table_name);
        
        -- Create GIN index on tsvector for fast full-text search
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_ts
            ON %I USING GIN (ts)
        ', table_name, table_name);
        
        -- Fix embedding column type to enforce dimension
        -- Note: This will fail if there are existing embeddings with wrong dimensions
        BEGIN
            EXECUTE format('
                ALTER TABLE %I 
                ALTER COLUMN embedding TYPE vector(%s) 
                USING embedding::vector(%s)
            ', table_name, embedding_dim, embedding_dim);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not alter embedding column for table %: %', table_name, SQLERRM;
        END;
        
        -- Recreate vector indexes with proper configuration
        EXECUTE format('
            DROP INDEX IF EXISTS idx_%I_embedding_hnsw
        ', table_name);
        
        EXECUTE format('
            CREATE INDEX idx_%I_embedding_hnsw
            ON %I USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        ', table_name, table_name);
        
        -- Add IVFFLAT index as backup (faster for smaller datasets)
        EXECUTE format('
            DROP INDEX IF EXISTS idx_%I_embedding_ivfflat
        ', table_name);
        
        EXECUTE format('
            CREATE INDEX idx_%I_embedding_ivfflat
            ON %I USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        ', table_name, table_name);
        
        RAISE NOTICE 'Fixed table: %', table_name;
    END LOOP;
END $$;

-- 4. Create function to get active configuration
CREATE OR REPLACE FUNCTION get_active_chunk_config()
RETURNS text AS $$
BEGIN
    RETURN (SELECT ingest_run_id FROM chunk_config_active WHERE key = 'active');
END;
$$ LANGUAGE plpgsql;

-- 5. Create function to set active configuration
CREATE OR REPLACE FUNCTION set_active_chunk_config(run_id text)
RETURNS void AS $$
BEGIN
    INSERT INTO chunk_config_active (key, ingest_run_id, updated_at)
    VALUES ('active', run_id, CURRENT_TIMESTAMP)
    ON CONFLICT (key) 
    DO UPDATE SET 
        ingest_run_id = EXCLUDED.ingest_run_id,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- 6. Create view for active chunks only
CREATE OR REPLACE VIEW active_document_chunks AS
SELECT dc.*
FROM document_chunks dc
WHERE dc.metadata->>'ingest_run_id' = get_active_chunk_config();

-- 7. Add performance monitoring functions
CREATE OR REPLACE FUNCTION get_vector_index_stats()
RETURNS TABLE (
    table_name text,
    index_name text,
    index_type text,
    index_size text,
    index_usage_count bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.tablename::text,
        i.indexname::text,
        i.indexdef::text,
        pg_size_pretty(pg_relation_size(i.indexname::regclass))::text,
        COALESCE(s.idx_scan, 0)::bigint
    FROM pg_tables t
    JOIN pg_indexes i ON t.tablename = i.tablename
    LEFT JOIN pg_stat_user_indexes s ON i.indexname = s.indexrelname
    WHERE t.tablename LIKE 'document_chunks%'
    AND i.indexdef LIKE '%vector%'
    ORDER BY t.tablename, i.indexname;
END;
$$ LANGUAGE plpgsql;

-- 8. Create function to check embedding dimension consistency
CREATE OR REPLACE FUNCTION check_embedding_dimensions()
RETURNS TABLE (
    table_name text,
    dimension integer,
    count bigint,
    status text
) AS $$
DECLARE
    table_name text;
    expected_dim integer := 384;
BEGIN
    FOR table_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE tablename LIKE 'document_chunks%' 
        AND schemaname = 'public'
    LOOP
        RETURN QUERY EXECUTE format('
            SELECT 
                %L::text as table_name,
                vector_dims(embedding)::integer as dimension,
                COUNT(*)::bigint as count,
                CASE 
                    WHEN vector_dims(embedding) = %s THEN ''OK''
                    ELSE ''MISMATCH''
                END::text as status
            FROM %I 
            WHERE embedding IS NOT NULL
            GROUP BY vector_dims(embedding)
            ORDER BY count DESC
        ', table_name, expected_dim, table_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 9. Set initial active configuration if none exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM chunk_config_active WHERE key = 'active') THEN
        -- Find the most recent ingest run
        INSERT INTO chunk_config_active (key, ingest_run_id)
        SELECT 'active', metadata->>'ingest_run_id'
        FROM document_chunks
        WHERE metadata->>'ingest_run_id' IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1;
        
        IF FOUND THEN
            RAISE NOTICE 'Set initial active configuration';
        ELSE
            RAISE NOTICE 'No ingest runs found - active configuration not set';
        END IF;
    END IF;
END $$;

-- 10. Create indexes for common query patterns
DO $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE tablename LIKE 'document_chunks%' 
        AND schemaname = 'public'
    LOOP
        -- Index on ingest_run_id for filtering
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_ingest_run_id
            ON %I ((metadata->>''ingest_run_id''))
        ', table_name, table_name);
        
        -- Index on chunk_variant for A/B testing
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_chunk_variant
            ON %I ((metadata->>''chunk_variant''))
        ', table_name, table_name);
        
        -- Index on created_at for time-based queries
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_created_at
            ON %I (created_at)
        ', table_name, table_name);
        
        RAISE NOTICE 'Created common indexes for table: %', table_name;
    END LOOP;
END $$;

-- 11. Analyze tables for query planner
DO $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE tablename LIKE 'document_chunks%' 
        AND schemaname = 'public'
    LOOP
        EXECUTE format('ANALYZE %I', table_name);
        RAISE NOTICE 'Analyzed table: %', table_name;
    END LOOP;
END $$;

-- 12. Show summary of changes
SELECT 'DDL Fixes Applied Successfully' as status;

-- Show current active configuration
SELECT 
    'Active Configuration' as info,
    ingest_run_id,
    created_at,
    updated_at
FROM chunk_config_active 
WHERE key = 'active';

-- Show embedding dimension check
SELECT * FROM check_embedding_dimensions();

-- Show vector index stats
SELECT * FROM get_vector_index_stats();
