-- B-1015 LTST Memory System Database Optimization DDL
-- Idempotent schema changes for HNSW semantic search, DSPy tables, and user hygiene
--
-- This script can be run multiple times safely without errors
-- All statements use IF NOT EXISTS or CREATE OR REPLACE patterns

-- =============================================================================
-- 1. ENHANCE EXISTING conversation_memory TABLE
-- =============================================================================

-- Add embedding column for semantic search (HNSW/IVFFlat indexes)
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS embedding VECTOR(384);

-- Add user_id column for future multi-tenant support (nullable for current single-user state)
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- Add message_type column for better message categorization
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS message_type VARCHAR(50) DEFAULT 'message';

-- Add content_hash for deduplication and integrity
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);

-- Add context_hash for context tracking
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS context_hash VARCHAR(64);

-- Add message_index for ordering within sessions
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS message_index INTEGER;

-- Add metadata column for flexible additional data
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Add relevance_score for semantic search ranking
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS relevance_score FLOAT DEFAULT 0.0;

-- Add is_context_message flag for context vs conversation messages
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS is_context_message BOOLEAN DEFAULT FALSE;

-- Add parent_message_id for message threading
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS parent_message_id INTEGER;

-- =============================================================================
-- 2. CREATE DSPy TABLES (PROMOTED FROM CODE TO SCHEMA)
-- =============================================================================

-- DSPy signatures table for storing signature definitions
CREATE TABLE IF NOT EXISTS dspy_signatures (
    id SERIAL PRIMARY KEY,
    signature_name VARCHAR(255) NOT NULL UNIQUE,
    signature_definition TEXT NOT NULL,
    signature_hash VARCHAR(64) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- DSPy examples table for storing signature examples
CREATE TABLE IF NOT EXISTS dspy_examples (
    id SERIAL PRIMARY KEY,
    signature_id INTEGER NOT NULL REFERENCES dspy_signatures(id) ON DELETE CASCADE,
    example_input TEXT NOT NULL,
    example_output TEXT NOT NULL,
    quality_score FLOAT DEFAULT 0.0,
    example_type VARCHAR(50) DEFAULT 'training',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- =============================================================================
-- 3. CREATE INDEXES FOR PERFORMANCE
-- =============================================================================

-- HNSW index for semantic search (primary strategy)
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding_hnsw
ON conversation_memory
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- IVFFlat index as fallback (if HNSW not available)
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding_ivfflat
ON conversation_memory
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Indexes for conversation_memory enhancements
CREATE INDEX IF NOT EXISTS idx_conversation_memory_content_hash
ON conversation_memory(content_hash);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_context_hash
ON conversation_memory(context_hash);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_user_id
ON conversation_memory(user_id);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_message_type
ON conversation_memory(message_type);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_relevance_score
ON conversation_memory(relevance_score);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_is_context_message
ON conversation_memory(is_context_message);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_parent_message_id
ON conversation_memory(parent_message_id);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_conversation_memory_session_user
ON conversation_memory(session_id, user_id);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_session_created
ON conversation_memory(session_id, created_at);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_user_created
ON conversation_memory(user_id, created_at);

-- DSPy table indexes
CREATE INDEX IF NOT EXISTS idx_dspy_signatures_name
ON dspy_signatures(signature_name);

CREATE INDEX IF NOT EXISTS idx_dspy_signatures_hash
ON dspy_signatures(signature_hash);

CREATE INDEX IF NOT EXISTS idx_dspy_examples_signature_id
ON dspy_examples(signature_id);

CREATE INDEX IF NOT EXISTS idx_dspy_examples_quality_score
ON dspy_examples(quality_score);

CREATE INDEX IF NOT EXISTS idx_dspy_examples_type
ON dspy_examples(example_type);

-- =============================================================================
-- 4. CREATE HELPER FUNCTIONS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to generate content hash
CREATE OR REPLACE FUNCTION generate_content_hash(content TEXT)
RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(sha256(content::bytea), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to generate context hash
CREATE OR REPLACE FUNCTION generate_context_hash(context JSONB)
RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(sha256(context::text::bytea), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to cleanup old conversation memory (governance-aligned retention)
CREATE OR REPLACE FUNCTION cleanup_old_conversation_memory(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete old conversation memory records
    DELETE FROM conversation_memory
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep
    AND is_context_message = FALSE;  -- Keep context messages longer

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Log cleanup operation
    INSERT INTO conversation_memory (
        session_id,
        human_message,
        ai_response,
        message_type,
        content_hash,
        metadata
    ) VALUES (
        'system',
        'Cleanup operation',
        format('Deleted %s old conversation records (older than %s days)', deleted_count, days_to_keep),
        'system',
        generate_content_hash(format('cleanup_%s_%s', deleted_count, days_to_keep)),
        jsonb_build_object('operation', 'cleanup', 'deleted_count', deleted_count, 'days_to_keep', days_to_keep)
    );

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get conversation statistics
CREATE OR REPLACE FUNCTION get_conversation_statistics(session_id_param VARCHAR(255) DEFAULT NULL)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_messages', COUNT(*),
        'human_messages', COUNT(*) FILTER (WHERE human_message IS NOT NULL),
        'ai_messages', COUNT(*) FILTER (WHERE ai_response IS NOT NULL),
        'context_messages', COUNT(*) FILTER (WHERE is_context_message = TRUE),
        'unique_sessions', COUNT(DISTINCT session_id),
        'date_range', jsonb_build_object(
            'earliest', MIN(created_at),
            'latest', MAX(created_at)
        ),
        'avg_relevance_score', AVG(relevance_score),
        'messages_with_embeddings', COUNT(*) FILTER (WHERE embedding IS NOT NULL)
    ) INTO result
    FROM conversation_memory
    WHERE (session_id_param IS NULL OR session_id = session_id_param);

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to search conversations by semantic similarity
CREATE OR REPLACE FUNCTION search_conversations_semantic(
    query_embedding VECTOR(384),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 10,
    session_filter VARCHAR(255) DEFAULT NULL
)
RETURNS TABLE(
    id INTEGER,
    session_id VARCHAR(255),
    human_message TEXT,
    ai_response TEXT,
    similarity_score FLOAT,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cm.id,
        cm.session_id,
        cm.human_message,
        cm.ai_response,
        1 - (cm.embedding <=> query_embedding) as similarity_score,
        cm.created_at
    FROM conversation_memory cm
    WHERE cm.embedding IS NOT NULL
    AND (session_filter IS NULL OR cm.session_id = session_filter)
    AND 1 - (cm.embedding <=> query_embedding) >= similarity_threshold
    ORDER BY cm.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 5. CREATE TRIGGERS
-- =============================================================================

-- Trigger to update updated_at timestamp on conversation_memory
DROP TRIGGER IF EXISTS update_conversation_memory_updated_at ON conversation_memory;
CREATE TRIGGER update_conversation_memory_updated_at
    BEFORE UPDATE ON conversation_memory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at timestamp on dspy_signatures
DROP TRIGGER IF EXISTS update_dspy_signatures_updated_at ON dspy_signatures;
CREATE TRIGGER update_dspy_signatures_updated_at
    BEFORE UPDATE ON dspy_signatures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at timestamp on dspy_examples
DROP TRIGGER IF EXISTS update_dspy_examples_updated_at ON dspy_examples;
CREATE TRIGGER update_dspy_examples_updated_at
    BEFORE UPDATE ON dspy_examples
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-generate content_hash for new conversation_memory records
CREATE OR REPLACE FUNCTION auto_generate_content_hash()
RETURNS TRIGGER AS $$
BEGIN
    -- Generate content hash from human_message and ai_response
    NEW.content_hash = generate_content_hash(
        COALESCE(NEW.human_message, '') || '|' || COALESCE(NEW.ai_response, '')
    );

    -- Generate context hash from context JSONB
    IF NEW.context IS NOT NULL THEN
        NEW.context_hash = generate_context_hash(NEW.context);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS auto_generate_content_hash_trigger ON conversation_memory;
CREATE TRIGGER auto_generate_content_hash_trigger
    BEFORE INSERT OR UPDATE ON conversation_memory
    FOR EACH ROW EXECUTE FUNCTION auto_generate_content_hash();

-- =============================================================================
-- 6. CREATE VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View for active conversation sessions
CREATE OR REPLACE VIEW active_conversation_sessions AS
SELECT
    session_id,
    user_id,
    COUNT(*) as message_count,
    MAX(created_at) as last_activity,
    MIN(created_at) as first_activity,
    AVG(relevance_score) as avg_relevance,
    COUNT(*) FILTER (WHERE is_context_message = TRUE) as context_message_count
FROM conversation_memory
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY session_id, user_id
ORDER BY last_activity DESC;

-- View for conversation summaries
CREATE OR REPLACE VIEW conversation_summaries AS
SELECT
    session_id,
    user_id,
    COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE human_message IS NOT NULL) as human_messages,
    COUNT(*) FILTER (WHERE ai_response IS NOT NULL) as ai_messages,
    COUNT(*) FILTER (WHERE is_context_message = TRUE) as context_messages,
    MIN(created_at) as session_start,
    MAX(created_at) as session_end,
    AVG(relevance_score) as avg_relevance_score,
    COUNT(*) FILTER (WHERE embedding IS NOT NULL) as messages_with_embeddings
FROM conversation_memory
GROUP BY session_id, user_id
ORDER BY session_end DESC;

-- =============================================================================
-- 7. INSERT INITIAL DATA (IF NEEDED)
-- =============================================================================

-- Insert system message to mark schema initialization
INSERT INTO conversation_memory (
    session_id,
    human_message,
    ai_response,
    message_type,
    content_hash,
    metadata
) VALUES (
    'system',
    'Schema initialization',
    'B-1015 database optimization schema applied successfully',
    'system',
    generate_content_hash('b1015_schema_init'),
    jsonb_build_object(
        'operation', 'schema_init',
        'version', '1.0',
        'features', jsonb_build_array(
            'hnsw_semantic_search',
            'dspy_tables_promotion',
            'user_session_hygiene',
            'manual_cleanup_function'
        ),
        'timestamp', CURRENT_TIMESTAMP
    )
) ON CONFLICT DO NOTHING;

-- =============================================================================
-- 8. VERIFICATION QUERIES
-- =============================================================================

-- Verify all new columns exist
DO $$
DECLARE
    missing_columns TEXT[] := ARRAY[]::TEXT[];
    col_name TEXT;
BEGIN
    -- Check for required columns
    FOR col_name IN
        SELECT unnest(ARRAY[
            'embedding', 'user_id', 'message_type', 'content_hash',
            'context_hash', 'message_index', 'metadata', 'relevance_score',
            'is_context_message', 'parent_message_id'
        ])
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'conversation_memory'
            AND column_name = col_name
        ) THEN
            missing_columns := array_append(missing_columns, col_name);
        END IF;
    END LOOP;

    IF array_length(missing_columns, 1) > 0 THEN
        RAISE EXCEPTION 'Missing columns: %', array_to_string(missing_columns, ', ');
    END IF;

    RAISE NOTICE 'All required columns verified successfully';
END $$;

-- Verify indexes exist
DO $$
DECLARE
    missing_indexes TEXT[] := ARRAY[]::TEXT[];
    idx_name TEXT;
BEGIN
    -- Check for required indexes
    FOR idx_name IN
        SELECT unnest(ARRAY[
            'idx_conversation_memory_embedding_hnsw',
            'idx_conversation_memory_embedding_ivfflat',
            'idx_conversation_memory_content_hash',
            'idx_conversation_memory_context_hash',
            'idx_conversation_memory_user_id',
            'idx_dspy_signatures_name',
            'idx_dspy_examples_signature_id'
        ])
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE indexname = idx_name
        ) THEN
            missing_indexes := array_append(missing_indexes, idx_name);
        END IF;
    END LOOP;

    IF array_length(missing_indexes, 1) > 0 THEN
        RAISE EXCEPTION 'Missing indexes: %', array_to_string(missing_indexes, ', ');
    END IF;

    RAISE NOTICE 'All required indexes verified successfully';
END $$;

-- Verify functions exist
DO $$
DECLARE
    missing_functions TEXT[] := ARRAY[]::TEXT[];
    func_name TEXT;
BEGIN
    -- Check for required functions
    FOR func_name IN
        SELECT unnest(ARRAY[
            'update_updated_at_column',
            'generate_content_hash',
            'generate_context_hash',
            'cleanup_old_conversation_memory',
            'get_conversation_statistics',
            'search_conversations_semantic',
            'auto_generate_content_hash'
        ])
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public' AND p.proname = func_name
        ) THEN
            missing_functions := array_append(missing_functions, func_name);
        END IF;
    END LOOP;

    IF array_length(missing_functions, 1) > 0 THEN
        RAISE EXCEPTION 'Missing functions: %', array_to_string(missing_functions, ', ');
    END IF;

    RAISE NOTICE 'All required functions verified successfully';
END $$;

-- Final verification message
DO $$
BEGIN
    RAISE NOTICE 'B-1015 database optimization schema applied successfully!';
    RAISE NOTICE 'Features enabled: HNSW semantic search, DSPy tables, user hygiene, manual cleanup';
    RAISE NOTICE 'All DDL statements are idempotent and can be run multiple times safely';
END $$;
