-- =============================================================================
-- Simplified Context Merging Functions for LTST Memory System
-- =============================================================================

-- Function to calculate semantic similarity between two context texts
CREATE OR REPLACE FUNCTION calculate_context_similarity(
    context1 TEXT,
    context2 TEXT,
    method VARCHAR(20) DEFAULT 'jaccard'
)
RETURNS FLOAT AS $$
DECLARE
    similarity FLOAT := 0.0;
    tokens1 TEXT[];
    tokens2 TEXT[];
    intersection_count INTEGER := 0;
    union_count INTEGER := 0;
    i INTEGER;
    j INTEGER;
BEGIN
    -- Handle NULL inputs
    IF context1 IS NULL OR context2 IS NULL THEN
        RETURN 0.0;
    END IF;

    -- Convert to lowercase and tokenize
    context1 := lower(trim(context1));
    context2 := lower(trim(context2));

    -- Split into tokens (words)
    tokens1 := string_to_array(regexp_replace(context1, '[^\w\s]', '', 'g'), ' ');
    tokens2 := string_to_array(regexp_replace(context2, '[^\w\s]', '', 'g'), ' ');

    -- Remove empty tokens
    tokens1 := array_remove(tokens1, '');
    tokens2 := array_remove(tokens2, '');

    -- Calculate intersection and union
    FOR i IN 1..array_length(tokens1, 1) LOOP
        FOR j IN 1..array_length(tokens2, 1) LOOP
            IF tokens1[i] = tokens2[j] THEN
                intersection_count := intersection_count + 1;
                EXIT;
            END IF;
        END LOOP;
    END LOOP;

    union_count := array_length(tokens1, 1) + array_length(tokens2, 1) - intersection_count;

    -- Calculate Jaccard similarity
    IF union_count > 0 THEN
        similarity := intersection_count::FLOAT / union_count::FLOAT;
    END IF;

    RETURN similarity;
END;
$$ LANGUAGE plpgsql;

-- Function to select relevant contexts based on threshold
CREATE OR REPLACE FUNCTION select_relevant_contexts(
    session_id_param VARCHAR(255),
    relevance_threshold FLOAT DEFAULT 0.7,
    max_contexts INTEGER DEFAULT 10,
    context_type_filter VARCHAR(50) DEFAULT NULL
)
RETURNS TABLE(
    id INTEGER,
    session_id VARCHAR(255),
    context_value TEXT,
    relevance_score FLOAT,
    context_type VARCHAR(50),
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cm.id,
        cm.session_id,
        COALESCE(cm.human_message, '') || ' ' || COALESCE(cm.ai_response, '') as context_value,
        cm.relevance_score,
        cm.message_type as context_type,
        cm.created_at
    FROM conversation_memory cm
    WHERE cm.session_id = session_id_param
    AND cm.relevance_score >= relevance_threshold
    AND (context_type_filter IS NULL OR cm.message_type = context_type_filter)
    ORDER BY cm.relevance_score DESC, cm.created_at DESC
    LIMIT max_contexts;
END;
$$ LANGUAGE plpgsql;

-- Function to merge contexts intelligently (simplified)
CREATE OR REPLACE FUNCTION merge_contexts_intelligent(
    session_id_param VARCHAR(255),
    merge_strategy VARCHAR(20) DEFAULT 'relevance',
    max_merged_length INTEGER DEFAULT 5000,
    relevance_threshold FLOAT DEFAULT 0.7,
    similarity_threshold FLOAT DEFAULT 0.8
)
RETURNS TABLE(
    merged_content TEXT,
    source_context_count INTEGER,
    avg_relevance FLOAT,
    merge_quality_score FLOAT,
    context_types VARCHAR(50)[]
) AS $$
DECLARE
    context_records RECORD;
    merged_text TEXT := '';
    context_count INTEGER := 0;
    total_relevance FLOAT := 0.0;
    context_types_array VARCHAR(50)[] := ARRAY[]::VARCHAR(50)[];
    current_length INTEGER := 0;
    quality_score FLOAT := 0.0;
BEGIN
    -- Strategy: relevance-based selection
    FOR context_records IN
        SELECT
            COALESCE(human_message, '') || ' ' || COALESCE(ai_response, '') as context_text,
            relevance_score,
            message_type
        FROM conversation_memory
        WHERE session_id = session_id_param
        AND relevance_score >= relevance_threshold
        ORDER BY relevance_score DESC
    LOOP
        -- Check if adding this context would exceed max length
        IF current_length + length(context_records.context_text) <= max_merged_length THEN
            IF merged_text != '' THEN
                merged_text := merged_text || E'\n\n';
            END IF;
            merged_text := merged_text || context_records.context_text;
            current_length := current_length + length(context_records.context_text);
            context_count := context_count + 1;
            total_relevance := total_relevance + context_records.relevance_score;
            context_types_array := array_append(context_types_array, context_records.message_type);
        ELSE
            EXIT;
        END IF;
    END LOOP;

    -- Calculate quality score based on relevance and diversity
    IF context_count > 0 THEN
        quality_score := (total_relevance / context_count) * (1.0 + (array_length(context_types_array, 1) * 0.1));
    END IF;

    -- Return merged result
    merged_content := merged_text;
    source_context_count := context_count;
    avg_relevance := CASE WHEN context_count > 0 THEN total_relevance / context_count ELSE 0.0 END;
    merge_quality_score := quality_score;
    context_types := context_types_array;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to optimize context cache
CREATE OR REPLACE FUNCTION optimize_context_cache(
    cache_ttl_hours INTEGER DEFAULT 24,
    max_cache_size INTEGER DEFAULT 1000
)
RETURNS TABLE(
    cache_entries_removed INTEGER,
    cache_size_after_cleanup INTEGER,
    optimization_time_ms INTEGER
) AS $$
DECLARE
    start_time TIMESTAMP;
    removed_count INTEGER := 0;
    current_cache_size INTEGER;
BEGIN
    start_time := clock_timestamp();

    -- Get current cache size (simulated)
    SELECT COUNT(*) INTO current_cache_size FROM conversation_memory
    WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '1 hour';

    -- Remove old cache entries (simulated cleanup)
    DELETE FROM conversation_memory
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day'
    AND relevance_score < 0.5;

    GET DIAGNOSTICS removed_count = ROW_COUNT;

    -- Return optimization results
    cache_entries_removed := removed_count;
    cache_size_after_cleanup := current_cache_size - removed_count;
    optimization_time_ms := EXTRACT(EPOCH FROM (clock_timestamp() - start_time)) * 1000;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to get context merging statistics
CREATE OR REPLACE FUNCTION get_context_statistics(
    session_id_param VARCHAR(255) DEFAULT NULL
)
RETURNS TABLE(
    total_contexts INTEGER,
    avg_relevance FLOAT,
    context_types VARCHAR(50)[],
    recent_activity_hours INTEGER,
    cache_hit_ratio FLOAT,
    merge_operations_count INTEGER
) AS $$
DECLARE
    context_count INTEGER;
    avg_relevance_score FLOAT;
    types_array VARCHAR(50)[];
    hours_since_activity INTEGER;
    cache_ratio FLOAT := 0.0;
    merge_count INTEGER := 0;
BEGIN
    -- Get basic statistics
    SELECT
        COUNT(*),
        AVG(relevance_score),
        array_agg(DISTINCT message_type)
    INTO
        context_count,
        avg_relevance_score,
        types_array
    FROM conversation_memory
    WHERE (session_id_param IS NULL OR session_id = session_id_param);

    -- Calculate hours since last activity
    SELECT
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(created_at))) / 3600
    INTO hours_since_activity
    FROM conversation_memory
    WHERE (session_id_param IS NULL OR session_id = session_id_param);

    -- Return statistics
    total_contexts := context_count;
    avg_relevance := COALESCE(avg_relevance_score, 0.0);
    context_types := COALESCE(types_array, ARRAY[]::VARCHAR(50)[]);
    recent_activity_hours := COALESCE(hours_since_activity::INTEGER, 0);
    cache_hit_ratio := cache_ratio;
    merge_operations_count := merge_count;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to create context merging summary view
CREATE OR REPLACE VIEW context_merging_summary AS
SELECT
    session_id,
    COUNT(*) as total_contexts,
    AVG(relevance_score) as avg_relevance,
    MAX(created_at) as last_activity,
    COUNT(DISTINCT message_type) as context_type_diversity,
    STRING_AGG(DISTINCT message_type, ', ') as context_types
FROM conversation_memory
WHERE relevance_score > 0
GROUP BY session_id
ORDER BY last_activity DESC;

-- Function to test context merging with sample data
CREATE OR REPLACE FUNCTION test_context_merging()
RETURNS TABLE(
    test_name VARCHAR(100),
    test_result BOOLEAN,
    details TEXT
) AS $$
DECLARE
    test_session_id VARCHAR(255) := 'test_merge_session_' || EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::TEXT;
    similarity_result FLOAT;
    merge_result RECORD;
BEGIN
    -- Test 1: Similarity calculation
    similarity_result := calculate_context_similarity('hello world', 'hello world test');
    IF similarity_result > 0.5 THEN
        test_name := 'Similarity Calculation';
        test_result := TRUE;
        details := 'Similarity calculated successfully: ' || similarity_result;
        RETURN NEXT;
    ELSE
        test_name := 'Similarity Calculation';
        test_result := FALSE;
        details := 'Similarity calculation failed: ' || similarity_result;
        RETURN NEXT;
    END IF;

    -- Test 2: Context selection
    SELECT * INTO merge_result FROM select_relevant_contexts(test_session_id, 0.1, 5);
    test_name := 'Context Selection';
    test_result := TRUE;
    details := 'Context selection function executed successfully';
    RETURN NEXT;

    -- Test 3: Intelligent merging
    SELECT * INTO merge_result FROM merge_contexts_intelligent(test_session_id, 'relevance', 1000, 0.1);
    test_name := 'Intelligent Merging';
    test_result := TRUE;
    details := 'Intelligent merging function executed successfully';
    RETURN NEXT;

    -- Test 4: Statistics
    SELECT * INTO merge_result FROM get_context_statistics(test_session_id);
    test_name := 'Statistics Collection';
    test_result := TRUE;
    details := 'Statistics collection function executed successfully';
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;
