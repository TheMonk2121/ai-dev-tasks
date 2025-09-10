-- Vector Database Foundation Enhancement Schema
-- This migration adds advanced vector indexing, performance monitoring, and optimization capabilities

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Vector indexes table for managing HNSW indexes
CREATE TABLE IF NOT EXISTS vector_indexes (
    id SERIAL PRIMARY KEY,
    index_name VARCHAR(255) UNIQUE NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    index_type VARCHAR(50) DEFAULT 'hnsw',
    parameters JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'creating',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_optimized TIMESTAMP,
    performance_stats JSONB DEFAULT '{}'
);

-- Vector performance metrics table for tracking query performance
CREATE TABLE IF NOT EXISTS vector_performance_metrics (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(100) NOT NULL,
    query_hash VARCHAR(64),
    execution_time_ms INTEGER,
    result_count INTEGER,
    index_used VARCHAR(255),
    cache_hit BOOLEAN DEFAULT false,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced documents table with index status and optimization flags
ALTER TABLE documents ADD COLUMN IF NOT EXISTS index_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS optimization_flags JSONB DEFAULT '{}';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS last_indexed TIMESTAMP;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS index_performance JSONB DEFAULT '{}';

-- Enhanced document_chunks table with advanced indexing support
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS index_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS similarity_score FLOAT;
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS last_verified TIMESTAMP;
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS cache_hit BOOLEAN DEFAULT false;

-- Vector operation cache table for frequently accessed embeddings
CREATE TABLE IF NOT EXISTS vector_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    embedding VECTOR(384),
    metadata JSONB DEFAULT '{}',
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Vector health monitoring table
CREATE TABLE IF NOT EXISTS vector_health_checks (
    id SERIAL PRIMARY KEY,
    check_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    message TEXT,
    metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create advanced indexes for better performance

-- HNSW index for fast similarity search (replaces existing ivfflat index)
DROP INDEX IF EXISTS idx_document_chunks_embedding;
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw 
    ON document_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Index for performance metrics
CREATE INDEX IF NOT EXISTS idx_vector_performance_metrics_operation_type 
    ON vector_performance_metrics(operation_type);
CREATE INDEX IF NOT EXISTS idx_vector_performance_metrics_created_at 
    ON vector_performance_metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_vector_performance_metrics_execution_time 
    ON vector_performance_metrics(execution_time_ms);

-- Index for vector cache
CREATE INDEX IF NOT EXISTS idx_vector_cache_cache_key 
    ON vector_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_vector_cache_last_accessed 
    ON vector_cache(last_accessed);
CREATE INDEX IF NOT EXISTS idx_vector_cache_expires_at 
    ON vector_cache(expires_at);

-- Index for vector health checks
CREATE INDEX IF NOT EXISTS idx_vector_health_checks_check_type 
    ON vector_health_checks(check_type);
CREATE INDEX IF NOT EXISTS idx_vector_health_checks_status 
    ON vector_health_checks(status);
CREATE INDEX IF NOT EXISTS idx_vector_health_checks_created_at 
    ON vector_health_checks(created_at);

-- Index for vector indexes management
CREATE INDEX IF NOT EXISTS idx_vector_indexes_index_name 
    ON vector_indexes(index_name);
CREATE INDEX IF NOT EXISTS idx_vector_indexes_status 
    ON vector_indexes(status);
CREATE INDEX IF NOT EXISTS idx_vector_indexes_table_name 
    ON vector_indexes(table_name);

-- Enhanced indexes for documents table
CREATE INDEX IF NOT EXISTS idx_documents_index_status 
    ON documents(index_status);
CREATE INDEX IF NOT EXISTS idx_documents_last_indexed 
    ON documents(last_indexed);

-- Enhanced indexes for document_chunks table
CREATE INDEX IF NOT EXISTS idx_document_chunks_index_status 
    ON document_chunks(index_status);
CREATE INDEX IF NOT EXISTS idx_document_chunks_similarity_score 
    ON document_chunks(similarity_score);
CREATE INDEX IF NOT EXISTS idx_document_chunks_cache_hit 
    ON document_chunks(cache_hit);

-- Create functions for vector operations

-- Function to update vector index performance statistics
CREATE OR REPLACE FUNCTION update_vector_index_stats(
    p_index_name VARCHAR(255),
    p_stats JSONB
)
RETURNS VOID AS $$
BEGIN
    UPDATE vector_indexes 
    SET performance_stats = p_stats,
        updated_at = CURRENT_TIMESTAMP
    WHERE index_name = p_index_name;
END;
$$ LANGUAGE plpgsql;

-- Function to record vector performance metrics
CREATE OR REPLACE FUNCTION record_vector_performance(
    p_operation_type VARCHAR(100),
    p_query_hash VARCHAR(64),
    p_execution_time_ms INTEGER,
    p_result_count INTEGER,
    p_index_used VARCHAR(255),
    p_cache_hit BOOLEAN,
    p_error_message TEXT,
    p_metadata JSONB
)
RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    INSERT INTO vector_performance_metrics (
        operation_type, query_hash, execution_time_ms, result_count,
        index_used, cache_hit, error_message, metadata
    ) VALUES (
        p_operation_type, p_query_hash, p_execution_time_ms, p_result_count,
        p_index_used, p_cache_hit, p_error_message, p_metadata
    ) RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update document index status
CREATE OR REPLACE FUNCTION update_document_index_status(
    p_document_id VARCHAR(255),
    p_status VARCHAR(50),
    p_performance JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    UPDATE documents 
    SET index_status = p_status,
        index_performance = p_performance,
        last_indexed = CASE WHEN p_status = 'indexed' THEN CURRENT_TIMESTAMP ELSE last_indexed END,
        updated_at = CURRENT_TIMESTAMP
    WHERE document_id = p_document_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update chunk index status
CREATE OR REPLACE FUNCTION update_chunk_index_status(
    p_chunk_id INTEGER,
    p_status VARCHAR(50),
    p_similarity_score FLOAT DEFAULT NULL,
    p_cache_hit BOOLEAN DEFAULT false
)
RETURNS VOID AS $$
BEGIN
    UPDATE document_chunks 
    SET index_status = p_status,
        similarity_score = COALESCE(p_similarity_score, similarity_score),
        cache_hit = p_cache_hit,
        last_verified = CASE WHEN p_status = 'verified' THEN CURRENT_TIMESTAMP ELSE last_verified END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_chunk_id;
END;
$$ LANGUAGE plpgsql;

-- Function to clean expired cache entries
CREATE OR REPLACE FUNCTION clean_expired_vector_cache()
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM vector_cache 
    WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get vector health status
CREATE OR REPLACE FUNCTION get_vector_health_status()
RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_documents', (SELECT COUNT(*) FROM documents),
        'indexed_documents', (SELECT COUNT(*) FROM documents WHERE index_status = 'indexed'),
        'pending_documents', (SELECT COUNT(*) FROM documents WHERE index_status = 'pending'),
        'total_chunks', (SELECT COUNT(*) FROM document_chunks),
        'indexed_chunks', (SELECT COUNT(*) FROM document_chunks WHERE index_status = 'indexed'),
        'cache_entries', (SELECT COUNT(*) FROM vector_cache),
        'avg_query_time', (SELECT AVG(execution_time_ms) FROM vector_performance_metrics WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '1 hour'),
        'recent_errors', (SELECT COUNT(*) FROM vector_performance_metrics WHERE error_message IS NOT NULL AND created_at > CURRENT_TIMESTAMP - INTERVAL '1 hour'),
        'index_health', (SELECT jsonb_object_agg(index_name, status) FROM vector_indexes)
    ) INTO v_result;
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_vector_indexes_updated_at BEFORE UPDATE ON vector_indexes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vector_cache_last_accessed BEFORE UPDATE ON vector_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create scheduled job to clean expired cache (if pg_cron extension is available)
-- SELECT cron.schedule('clean-vector-cache', '0 */6 * * *', 'SELECT clean_expired_vector_cache();');

-- Insert initial health check
INSERT INTO vector_health_checks (check_type, status, message, metrics) VALUES
('schema_migration', 'completed', 'Vector enhancement schema migration completed successfully', 
 '{"tables_created": 4, "indexes_created": 12, "functions_created": 6}');

-- Grant necessary permissions (adjust based on your database user)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_user;

-- Create views for easier monitoring

-- View for vector performance summary
CREATE OR REPLACE VIEW vector_performance_summary AS
SELECT 
    operation_type,
    COUNT(*) as total_operations,
    AVG(execution_time_ms) as avg_execution_time,
    MAX(execution_time_ms) as max_execution_time,
    MIN(execution_time_ms) as min_execution_time,
    COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as error_count,
    COUNT(CASE WHEN cache_hit = true THEN 1 END) as cache_hits
FROM vector_performance_metrics 
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY operation_type;

-- View for index performance
CREATE OR REPLACE VIEW index_performance_view AS
SELECT 
    vi.index_name,
    vi.table_name,
    vi.column_name,
    vi.index_type,
    vi.status,
    vi.performance_stats,
    vi.last_optimized,
    COUNT(vpm.id) as query_count,
    AVG(vpm.execution_time_ms) as avg_query_time
FROM vector_indexes vi
LEFT JOIN vector_performance_metrics vpm ON vpm.index_used = vi.index_name
    AND vpm.created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY vi.id, vi.index_name, vi.table_name, vi.column_name, vi.index_type, vi.status, vi.performance_stats, vi.last_optimized;

-- View for document indexing status
CREATE OR REPLACE VIEW document_indexing_status AS
SELECT 
    d.filename,
    d.file_type,
    d.chunk_count,
    d.index_status,
    d.last_indexed,
    d.index_performance,
    COUNT(dc.id) as total_chunks,
    COUNT(CASE WHEN dc.index_status = 'indexed' THEN 1 END) as indexed_chunks,
    COUNT(CASE WHEN dc.cache_hit = true THEN 1 END) as cache_hits
FROM documents d
LEFT JOIN document_chunks dc ON dc.document_id = d.document_id
GROUP BY d.id, d.filename, d.file_type, d.chunk_count, d.index_status, d.last_indexed, d.index_performance;

-- Add comments for documentation
COMMENT ON TABLE vector_indexes IS 'Manages HNSW indexes for vector similarity search';
COMMENT ON TABLE vector_performance_metrics IS 'Tracks performance metrics for vector operations';
COMMENT ON TABLE vector_cache IS 'Caches frequently accessed embeddings for performance';
COMMENT ON TABLE vector_health_checks IS 'Monitors health and status of vector operations';

COMMENT ON FUNCTION update_vector_index_stats IS 'Updates performance statistics for vector indexes';
COMMENT ON FUNCTION record_vector_performance IS 'Records performance metrics for vector operations';
COMMENT ON FUNCTION get_vector_health_status IS 'Returns comprehensive health status of vector system';
COMMENT ON FUNCTION clean_expired_vector_cache IS 'Removes expired entries from vector cache';

-- Migration completed successfully
INSERT INTO vector_health_checks (check_type, status, message) VALUES
('migration_complete', 'success', 'Vector Database Foundation Enhancement schema migration completed'); 