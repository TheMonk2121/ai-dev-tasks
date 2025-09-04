-- Query Pattern Knowledge Graph Schema Extensions
-- Extends LTST Memory System for comprehensive query pattern analysis
-- Compatible with existing conversation_messages and conversation_sessions tables

-- Enable required extensions if not already present
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Query patterns table for storing detected patterns
CREATE TABLE IF NOT EXISTS query_patterns (
    pattern_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(100) NOT NULL, -- 'sequence', 'topic_evolution', 'context_shift', 'recurring'
    pattern_signature TEXT NOT NULL, -- Semantic signature of the pattern
    queries_in_pattern INTEGER[] NOT NULL, -- Array of message IDs in this pattern
    pattern_embedding VECTOR(384), -- Embedding of the pattern concept
    pattern_strength FLOAT DEFAULT 0.0, -- How strong/consistent this pattern is (0-1)
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    occurrence_count INTEGER DEFAULT 1,
    prediction_accuracy FLOAT DEFAULT 0.0, -- How well this pattern predicts next queries (0-1)
    success_rate FLOAT DEFAULT 0.0, -- How often queries in this pattern lead to resolution
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query relationships and transitions
CREATE TABLE IF NOT EXISTS query_relationships (
    relationship_id SERIAL PRIMARY KEY,
    from_message_id INTEGER NOT NULL REFERENCES conversation_messages(message_id) ON DELETE CASCADE,
    to_message_id INTEGER NOT NULL REFERENCES conversation_messages(message_id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL, -- 'follow_up', 'clarification', 'pivot', 'drill_down', 'zoom_out', 'related'
    transition_embedding VECTOR(384), -- Embedding of the transition concept
    semantic_distance FLOAT NOT NULL, -- Vector distance between queries (0-2, where 0 is identical)
    temporal_distance INTEGER NOT NULL, -- Messages between queries
    context_similarity FLOAT DEFAULT 0.0, -- How similar the contexts were (0-1)
    success_outcome BOOLEAN DEFAULT NULL, -- Whether this transition led to successful resolution
    confidence_score FLOAT DEFAULT 0.0, -- Confidence in this relationship (0-1)
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query intentions and goals
CREATE TABLE IF NOT EXISTS query_intentions (
    intention_id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES conversation_messages(message_id) ON DELETE CASCADE,
    intention_type VARCHAR(100) NOT NULL, -- 'learn', 'debug', 'implement', 'explore', 'optimize', 'clarify'
    intention_embedding VECTOR(384), -- Embedding of the intention
    confidence_score FLOAT DEFAULT 0.0, -- Confidence in intention classification (0-1)
    goal_achieved BOOLEAN DEFAULT NULL, -- Whether the intention was fulfilled
    steps_to_resolution INTEGER DEFAULT NULL, -- How many queries it took to resolve
    resolution_quality FLOAT DEFAULT 0.0, -- Quality of resolution (0-1)
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query clusters for grouping semantically similar queries
CREATE TABLE IF NOT EXISTS query_clusters (
    cluster_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    cluster_name VARCHAR(500), -- Human-readable cluster description
    cluster_centroid VECTOR(384), -- Centroid embedding of the cluster
    message_ids INTEGER[] NOT NULL, -- Array of message IDs in this cluster
    cluster_coherence FLOAT DEFAULT 0.0, -- How coherent the cluster is (0-1)
    cluster_size INTEGER NOT NULL,
    time_span_days INTEGER DEFAULT 0, -- Days between first and last query in cluster
    recurring_frequency FLOAT DEFAULT 0.0, -- How often this type of query recurs
    resolution_success_rate FLOAT DEFAULT 0.0, -- Success rate for queries in this cluster
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query predictions for storing and tracking prediction accuracy
CREATE TABLE IF NOT EXISTS query_predictions (
    prediction_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    current_context_message_id INTEGER REFERENCES conversation_messages(message_id) ON DELETE CASCADE,
    predicted_query_topics TEXT[] NOT NULL, -- Array of predicted query topics
    prediction_embeddings VECTOR(384)[], -- Array of embeddings for predicted queries
    confidence_scores FLOAT[] NOT NULL, -- Confidence for each prediction (0-1)
    prediction_method VARCHAR(100) NOT NULL, -- 'sequence_based', 'topic_evolution', 'recurring_pattern', 'similarity_based'
    actual_next_query_id INTEGER DEFAULT NULL REFERENCES conversation_messages(message_id) ON DELETE SET NULL,
    prediction_accuracy FLOAT DEFAULT NULL, -- How accurate this prediction was (0-1)
    was_helpful BOOLEAN DEFAULT NULL, -- Whether prediction was helpful to user
    metadata JSONB DEFAULT '{}',
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP DEFAULT NULL
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_query_patterns_user_id ON query_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_query_patterns_type_strength ON query_patterns(pattern_type, pattern_strength DESC);
CREATE INDEX IF NOT EXISTS idx_query_patterns_last_seen ON query_patterns(last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_query_patterns_embedding ON query_patterns USING hnsw (pattern_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_query_relationships_from_message ON query_relationships(from_message_id);
CREATE INDEX IF NOT EXISTS idx_query_relationships_to_message ON query_relationships(to_message_id);
CREATE INDEX IF NOT EXISTS idx_query_relationships_type ON query_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_query_relationships_distance ON query_relationships(semantic_distance);
CREATE INDEX IF NOT EXISTS idx_query_relationships_embedding ON query_relationships USING hnsw (transition_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_query_intentions_message_id ON query_intentions(message_id);
CREATE INDEX IF NOT EXISTS idx_query_intentions_type_confidence ON query_intentions(intention_type, confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_query_intentions_embedding ON query_intentions USING hnsw (intention_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_query_clusters_user_id ON query_clusters(user_id);
CREATE INDEX IF NOT EXISTS idx_query_clusters_coherence ON query_clusters(cluster_coherence DESC);
CREATE INDEX IF NOT EXISTS idx_query_clusters_centroid ON query_clusters USING hnsw (cluster_centroid vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_query_predictions_user_id ON query_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_query_predictions_context_message ON query_predictions(current_context_message_id);
CREATE INDEX IF NOT EXISTS idx_query_predictions_method_accuracy ON query_predictions(prediction_method, prediction_accuracy DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_query_predictions_predicted_at ON query_predictions(predicted_at DESC);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_query_patterns_user_type_strength ON query_patterns(user_id, pattern_type, pattern_strength DESC);
CREATE INDEX IF NOT EXISTS idx_query_relationships_messages_type ON query_relationships(from_message_id, to_message_id, relationship_type);
CREATE INDEX IF NOT EXISTS idx_query_clusters_user_size_coherence ON query_clusters(user_id, cluster_size DESC, cluster_coherence DESC);
