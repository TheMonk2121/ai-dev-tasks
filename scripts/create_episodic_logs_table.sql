-- Create episodic_logs table for generation cache implementation
-- This script creates the base table structure before adding cache columns

-- Drop table if it exists (for development/testing)
DROP TABLE IF EXISTS episodic_logs CASCADE;

-- Create episodic_logs table with basic structure
CREATE TABLE episodic_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id VARCHAR(255),
    model_type VARCHAR(100),
    prompt TEXT,
    response TEXT,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for basic performance
CREATE INDEX idx_episodic_logs_timestamp ON episodic_logs (timestamp);
CREATE INDEX idx_episodic_logs_user_id ON episodic_logs (user_id);
CREATE INDEX idx_episodic_logs_model_type ON episodic_logs (model_type);

-- Insert some sample data for testing
INSERT INTO episodic_logs (user_id, model_type, prompt, response, tokens_used) VALUES
    ('user1', 'gpt-4', 'What is machine learning?', 'Machine learning is a subset of artificial intelligence...', 150),
    ('user2', 'claude-3', 'Explain neural networks', 'Neural networks are computing systems inspired by biological neurons...', 200),
    ('user1', 'gpt-4', 'How to implement caching?', 'Caching involves storing frequently accessed data...', 180);

-- Verify table creation
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'episodic_logs'
ORDER BY ordinal_position;

-- Show table size
SELECT
    pg_size_pretty(pg_total_relation_size('episodic_logs')) as table_size,
    pg_size_pretty(pg_relation_size('episodic_logs')) as data_size,
    pg_size_pretty(pg_total_relation_size('episodic_logs') - pg_relation_size('episodic_logs')) as index_size;
