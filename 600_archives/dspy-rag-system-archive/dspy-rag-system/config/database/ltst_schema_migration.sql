-- LTST Memory System Database Migration
-- This script creates the complete schema for the LTST Memory System
-- Run this script to set up the database for conversation memory functionality

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Create conversation_sessions table
CREATE TABLE IF NOT EXISTS conversation_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_name VARCHAR(500),
    session_type VARCHAR(100) DEFAULT 'conversation',
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    context_summary TEXT,
    relevance_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create conversation_messages table
CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    message_type VARCHAR(50) DEFAULT 'message',
    role VARCHAR(50) NOT NULL, -- 'human', 'ai', 'system'
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    context_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(384), -- For semantic search
    relevance_score FLOAT DEFAULT 0.0,
    is_context_message BOOLEAN DEFAULT FALSE,
    parent_message_id INTEGER REFERENCES conversation_messages(id),
    UNIQUE(session_id, message_index)
);

-- 3. Create conversation_context table
CREATE TABLE IF NOT EXISTS conversation_context (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    context_type VARCHAR(100) NOT NULL, -- 'conversation', 'preference', 'project', 'user_info'
    context_key VARCHAR(255) NOT NULL,
    context_value TEXT NOT NULL,
    relevance_score FLOAT DEFAULT 0.0,
    context_hash VARCHAR(64) NOT NULL,
    metadata JSONB DEFAULT '{}',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, context_type, context_key)
);

-- 4. Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    preference_key VARCHAR(255) NOT NULL,
    preference_value TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

-- 5. Create session_relationships table
CREATE TABLE IF NOT EXISTS session_relationships (
    id SERIAL PRIMARY KEY,
    source_session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    target_session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL, -- 'continuation', 'reference', 'similar'
    relationship_score FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_session_id, target_session_id, relationship_type)
);

-- 6. Create session_summary table
CREATE TABLE IF NOT EXISTS session_summary (
    session_id VARCHAR(255) PRIMARY KEY REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    message_count INTEGER DEFAULT 0,
    human_message_count INTEGER DEFAULT 0,
    ai_message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    average_message_length INTEGER DEFAULT 0,
    session_duration INTERVAL,
    context_count INTEGER DEFAULT 0,
    last_summary_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Enhance existing conversation_memory table
ALTER TABLE conversation_memory
ADD COLUMN IF NOT EXISTS message_type VARCHAR(50) DEFAULT 'message',
ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64),
ADD COLUMN IF NOT EXISTS context_hash VARCHAR(64),
ADD COLUMN IF NOT EXISTS message_index INTEGER,
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS embedding VECTOR(384),
ADD COLUMN IF NOT EXISTS relevance_score FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS is_context_message BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS parent_message_id INTEGER;

-- Create indexes for performance optimization

-- conversation_sessions indexes
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_last_activity ON conversation_sessions(last_activity);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_status ON conversation_sessions(status);

-- conversation_messages indexes
CREATE INDEX IF NOT EXISTS idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_timestamp ON conversation_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_role ON conversation_messages(role);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_content_hash ON conversation_messages(content_hash);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_embedding ON conversation_messages USING ivfflat (embedding vector_cosine_ops);

-- conversation_context indexes
CREATE INDEX IF NOT EXISTS idx_conversation_context_session_id ON conversation_context(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_type ON conversation_context(context_type);
CREATE INDEX IF NOT EXISTS idx_conversation_context_expires ON conversation_context(expires_at);

-- user_preferences indexes
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_key ON user_preferences(preference_key);

-- session_relationships indexes
CREATE INDEX IF NOT EXISTS idx_session_relationships_source ON session_relationships(source_session_id);
CREATE INDEX IF NOT EXISTS idx_session_relationships_target ON session_relationships(target_session_id);
CREATE INDEX IF NOT EXISTS idx_session_relationships_type ON session_relationships(relationship_type);

-- Enhanced conversation_memory indexes
CREATE INDEX IF NOT EXISTS idx_conversation_memory_content_hash ON conversation_memory(content_hash);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding ON conversation_memory USING ivfflat (embedding vector_cosine_ops);

-- Create helper functions

-- Function to update session last_activity
CREATE OR REPLACE FUNCTION update_session_activity(session_id_param VARCHAR(255))
RETURNS VOID AS $$
BEGIN
    UPDATE conversation_sessions
    SET last_activity = CURRENT_TIMESTAMP
    WHERE session_id = session_id_param;
END;
$$ LANGUAGE plpgsql;

-- Function to clean expired context
CREATE OR REPLACE FUNCTION clean_expired_context()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM conversation_context
    WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to update session summary
CREATE OR REPLACE FUNCTION update_session_summary(session_id_param VARCHAR(255))
RETURNS VOID AS $$
DECLARE
    msg_count INTEGER;
    human_count INTEGER;
    ai_count INTEGER;
    context_count INTEGER;
    session_start TIMESTAMP;
    session_end TIMESTAMP;
BEGIN
    -- Get message counts
    SELECT COUNT(*),
           COUNT(*) FILTER (WHERE role = 'human'),
           COUNT(*) FILTER (WHERE role = 'ai')
    INTO msg_count, human_count, ai_count
    FROM conversation_messages
    WHERE session_id = session_id_param;

    -- Get context count
    SELECT COUNT(*) INTO context_count
    FROM conversation_context
    WHERE session_id = session_id_param;

    -- Get session duration
    SELECT MIN(timestamp), MAX(timestamp)
    INTO session_start, session_end
    FROM conversation_messages
    WHERE session_id = session_id_param;

    -- Insert or update summary
    INSERT INTO session_summary (
        session_id, message_count, human_message_count, ai_message_count,
        context_count, session_duration, last_summary_update
    ) VALUES (
        session_id_param, msg_count, human_count, ai_count,
        context_count,
        CASE WHEN session_start IS NOT NULL AND session_end IS NOT NULL
             THEN session_end - session_start
             ELSE NULL
        END,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (session_id) DO UPDATE SET
        message_count = EXCLUDED.message_count,
        human_message_count = EXCLUDED.human_message_count,
        ai_message_count = EXCLUDED.ai_message_count,
        context_count = EXCLUDED.context_count,
        session_duration = EXCLUDED.session_duration,
        last_summary_update = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic updates

-- Trigger to update session activity when messages are added
CREATE OR REPLACE FUNCTION trigger_update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_session_activity(NEW.session_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_conversation_messages_activity
    AFTER INSERT OR UPDATE ON conversation_messages
    FOR EACH ROW EXECUTE FUNCTION trigger_update_session_activity();

-- Trigger to update session summary when messages are added/modified
CREATE OR REPLACE FUNCTION trigger_update_session_summary()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_session_summary(NEW.session_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_conversation_messages_summary
    AFTER INSERT OR UPDATE OR DELETE ON conversation_messages
    FOR EACH ROW EXECUTE FUNCTION trigger_update_session_summary();

-- Add comments for documentation
COMMENT ON TABLE conversation_sessions IS 'Stores conversation sessions and user interactions';
COMMENT ON TABLE conversation_messages IS 'Stores individual conversation messages with metadata and embeddings';
COMMENT ON TABLE conversation_context IS 'Stores conversation context and preferences';
COMMENT ON TABLE user_preferences IS 'Stores user preferences and settings';
COMMENT ON TABLE session_relationships IS 'Links related conversation sessions';
COMMENT ON TABLE session_summary IS 'Stores session statistics and summaries';

-- Migration complete
SELECT 'LTST Memory System schema migration completed successfully' as status;
