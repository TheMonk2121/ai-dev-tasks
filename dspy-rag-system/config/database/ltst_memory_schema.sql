-- LTST Memory System Database Schema
-- This schema extends the existing conversation memory system with ChatGPT-like Long-Term Short-Term memory capabilities

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Enhanced conversation sessions table for session management
CREATE TABLE IF NOT EXISTS conversation_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_name VARCHAR(500),
    session_type VARCHAR(100) DEFAULT 'conversation',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    context_summary TEXT,
    relevance_score FLOAT DEFAULT 0.0,
    session_length INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced conversation messages table for detailed message tracking
CREATE TABLE IF NOT EXISTS conversation_messages (
    message_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    message_type VARCHAR(50) DEFAULT 'message', -- 'message', 'system', 'context', 'preference'
    role VARCHAR(50) NOT NULL, -- 'human', 'ai', 'system'
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    context_hash VARCHAR(64),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(384),
    relevance_score FLOAT DEFAULT 0.0,
    is_context_message BOOLEAN DEFAULT false,
    parent_message_id INTEGER REFERENCES conversation_messages(message_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation context table for context relationships and relevance
CREATE TABLE IF NOT EXISTS conversation_context (
    context_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    context_type VARCHAR(100) NOT NULL, -- 'conversation', 'preference', 'project', 'user_info'
    context_key VARCHAR(255) NOT NULL,
    context_value TEXT NOT NULL,
    relevance_score FLOAT DEFAULT 0.0,
    context_hash VARCHAR(64) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(session_id, context_type, context_key)
);

-- User preferences table for learning and applying user preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    preference_key VARCHAR(255) NOT NULL,
    preference_value TEXT NOT NULL,
    preference_type VARCHAR(100) DEFAULT 'general', -- 'general', 'coding', 'communication', 'project'
    confidence_score FLOAT DEFAULT 0.0,
    source VARCHAR(100) DEFAULT 'learned', -- 'learned', 'explicit', 'inferred'
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

-- Memory retrieval cache for performance optimization
CREATE TABLE IF NOT EXISTS memory_retrieval_cache (
    cache_id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    retrieved_context JSONB NOT NULL,
    relevance_scores JSONB DEFAULT '{}',
    retrieval_time_ms INTEGER,
    cache_hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour')
);

-- Session relationships table for linking related conversations
CREATE TABLE IF NOT EXISTS session_relationships (
    relationship_id SERIAL PRIMARY KEY,
    source_session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    target_session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL, -- 'continuation', 'related', 'fork', 'reference'
    similarity_score FLOAT DEFAULT 0.0,
    relationship_strength FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_session_id, target_session_id, relationship_type)
);

-- Memory performance metrics for monitoring and optimization
CREATE TABLE IF NOT EXISTS memory_performance_metrics (
    metric_id SERIAL PRIMARY KEY,
    operation_type VARCHAR(100) NOT NULL, -- 'retrieval', 'storage', 'merging', 'context_search'
    session_id VARCHAR(255),
    operation_hash VARCHAR(64),
    execution_time_ms INTEGER NOT NULL,
    result_count INTEGER,
    cache_hit BOOLEAN DEFAULT false,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for optimal performance

-- Session indexes
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_last_activity ON conversation_sessions(last_activity);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_relevance_score ON conversation_sessions(relevance_score);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_status ON conversation_sessions(status);

-- Message indexes
CREATE INDEX IF NOT EXISTS idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_timestamp ON conversation_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_role ON conversation_messages(role);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_content_hash ON conversation_messages(content_hash);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_relevance_score ON conversation_messages(relevance_score);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_message_index ON conversation_messages(session_id, message_index);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_embedding ON conversation_messages USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Context indexes
CREATE INDEX IF NOT EXISTS idx_conversation_context_session_id ON conversation_context(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_type ON conversation_context(context_type);
CREATE INDEX IF NOT EXISTS idx_conversation_context_relevance_score ON conversation_context(relevance_score);
CREATE INDEX IF NOT EXISTS idx_conversation_context_expires_at ON conversation_context(expires_at);

-- User preference indexes
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_key ON user_preferences(preference_key);
CREATE INDEX IF NOT EXISTS idx_user_preferences_type ON user_preferences(preference_type);
CREATE INDEX IF NOT EXISTS idx_user_preferences_confidence_score ON user_preferences(confidence_score);
CREATE INDEX IF NOT EXISTS idx_user_preferences_last_used ON user_preferences(last_used);

-- Cache indexes
CREATE INDEX IF NOT EXISTS idx_memory_retrieval_cache_session_id ON memory_retrieval_cache(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_retrieval_cache_query_hash ON memory_retrieval_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_memory_retrieval_cache_expires_at ON memory_retrieval_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_memory_retrieval_cache_last_accessed ON memory_retrieval_cache(last_accessed);

-- Relationship indexes
CREATE INDEX IF NOT EXISTS idx_session_relationships_source ON session_relationships(source_session_id);
CREATE INDEX IF NOT EXISTS idx_session_relationships_target ON session_relationships(target_session_id);
CREATE INDEX IF NOT EXISTS idx_session_relationships_type ON session_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_session_relationships_similarity ON session_relationships(similarity_score);

-- Performance metrics indexes
CREATE INDEX IF NOT EXISTS idx_memory_performance_metrics_operation_type ON memory_performance_metrics(operation_type);
CREATE INDEX IF NOT EXISTS idx_memory_performance_metrics_session_id ON memory_performance_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_performance_metrics_created_at ON memory_performance_metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_memory_performance_metrics_execution_time ON memory_performance_metrics(execution_time_ms);

-- Create triggers for updated_at timestamps
CREATE TRIGGER update_conversation_sessions_updated_at BEFORE UPDATE ON conversation_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_context_updated_at BEFORE UPDATE ON conversation_context
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to update session length
CREATE OR REPLACE FUNCTION update_session_length()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation_sessions
    SET session_length = (
        SELECT COUNT(*)
        FROM conversation_messages
        WHERE session_id = NEW.session_id
    ),
    last_activity = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to update session length when messages are added
CREATE TRIGGER update_session_length_trigger
    AFTER INSERT ON conversation_messages
    FOR EACH ROW EXECUTE FUNCTION update_session_length();

-- Create function to clean expired cache entries
CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM memory_retrieval_cache
    WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ language 'plpgsql';

-- Create function to clean expired context entries
CREATE OR REPLACE FUNCTION clean_expired_context()
RETURNS void AS $$
BEGIN
    DELETE FROM conversation_context
    WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP;
END;
$$ language 'plpgsql';

-- Insert default system preferences
INSERT INTO user_preferences (user_id, preference_key, preference_value, preference_type, source, confidence_score) VALUES
('system', 'memory_retention_days', '30', 'general', 'explicit', 1.0),
('system', 'max_context_length', '10000', 'general', 'explicit', 1.0),
('system', 'relevance_threshold', '0.7', 'general', 'explicit', 1.0),
('system', 'cache_ttl_hours', '1', 'general', 'explicit', 1.0)
ON CONFLICT (user_id, preference_key) DO NOTHING;

-- Create view for session summary
CREATE OR REPLACE VIEW session_summary AS
SELECT
    cs.session_id,
    cs.user_id,
    cs.session_name,
    cs.session_type,
    cs.status,
    cs.created_at,
    cs.last_activity,
    cs.session_length,
    cs.relevance_score,
    COUNT(cm.message_id) as message_count,
    MAX(cm.timestamp) as last_message_time,
    AVG(cm.relevance_score) as avg_message_relevance
FROM conversation_sessions cs
LEFT JOIN conversation_messages cm ON cs.session_id = cm.session_id
GROUP BY cs.session_id, cs.user_id, cs.session_name, cs.session_type, cs.status,
         cs.created_at, cs.last_activity, cs.session_length, cs.relevance_score;

-- Create view for user preference summary
CREATE OR REPLACE VIEW user_preference_summary AS
SELECT
    user_id,
    preference_type,
    COUNT(*) as preference_count,
    AVG(confidence_score) as avg_confidence,
    MAX(last_used) as last_preference_used,
    SUM(usage_count) as total_usage
FROM user_preferences
GROUP BY user_id, preference_type;
