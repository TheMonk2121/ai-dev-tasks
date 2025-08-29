# LTST Memory System Schema Documentation

## Overview

The LTST (Long-Term Short-Term) Memory System provides ChatGPT-like conversation memory with session tracking, context management, and semantic search capabilities. This schema extends the existing DSPy RAG system with advanced conversation memory features.

## Schema Architecture

### Core Tables

#### 1. conversation_sessions
**Purpose:** Manage conversation sessions and user interactions

**Key Features:**
- Session lifecycle management
- User association and metadata
- Activity tracking and relevance scoring
- Context summarization

**Schema:**
```sql
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
```

**Indexes:**
- `idx_conversation_sessions_user_id` - User session lookup
- `idx_conversation_sessions_last_activity` - Recent activity queries
- `idx_conversation_sessions_relevance_score` - Relevance-based retrieval
- `idx_conversation_sessions_status` - Status filtering

#### 2. conversation_messages
**Purpose:** Store individual conversation messages with metadata and embeddings

**Key Features:**
- Message content and metadata storage
- Vector embeddings for semantic search
- Message threading and relationships
- Context message identification

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS conversation_messages (
    message_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    message_type VARCHAR(50) DEFAULT 'message',
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
```

**Indexes:**
- `idx_conversation_messages_session_id` - Session message lookup
- `idx_conversation_messages_timestamp` - Chronological queries
- `idx_conversation_messages_role` - Role-based filtering
- `idx_conversation_messages_content_hash` - Content deduplication
- `idx_conversation_messages_relevance_score` - Relevance-based retrieval
- `idx_conversation_messages_message_index` - Ordered message access
- `idx_conversation_messages_embedding` - Semantic search (HNSW)

#### 3. conversation_context
**Purpose:** Store conversation context and relationships

**Key Features:**
- Context type categorization
- Relevance scoring
- Expiration management
- Metadata storage

**Schema:**
```sql
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
```

**Indexes:**
- `idx_conversation_context_session_id` - Session context lookup
- `idx_conversation_context_type` - Context type filtering
- `idx_conversation_context_relevance_score` - Relevance-based retrieval
- `idx_conversation_context_expires_at` - Expiration management

#### 4. user_preferences
**Purpose:** Store user preferences and learning patterns

**Key Features:**
- Preference categorization
- Confidence scoring
- Usage tracking
- Source attribution

**Schema:**
```sql
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
```

**Indexes:**
- `idx_user_preferences_user_id` - User preference lookup
- `idx_user_preferences_key` - Preference key filtering
- `idx_user_preferences_type` - Type-based filtering
- `idx_user_preferences_confidence_score` - Confidence-based retrieval
- `idx_user_preferences_last_used` - Usage tracking

### Performance Tables

#### 5. memory_retrieval_cache
**Purpose:** Cache memory retrieval results for performance optimization

**Key Features:**
- Query result caching
- Hit count tracking
- Automatic expiration
- Performance monitoring

**Schema:**
```sql
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
```

**Indexes:**
- `idx_memory_retrieval_cache_session_id` - Session cache lookup
- `idx_memory_retrieval_cache_query_hash` - Query-based retrieval
- `idx_memory_retrieval_cache_expires_at` - Expiration management
- `idx_memory_retrieval_cache_last_accessed` - Access pattern analysis

#### 6. session_relationships
**Purpose:** Link related conversation sessions

**Key Features:**
- Session relationship mapping
- Similarity scoring
- Relationship strength tracking
- Metadata storage

**Schema:**
```sql
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
```

**Indexes:**
- `idx_session_relationships_source` - Source session lookup
- `idx_session_relationships_target` - Target session lookup
- `idx_session_relationships_type` - Relationship type filtering
- `idx_session_relationships_similarity` - Similarity-based queries

#### 7. memory_performance_metrics
**Purpose:** Monitor and optimize memory system performance

**Key Features:**
- Operation timing tracking
- Error monitoring
- Cache performance analysis
- Performance trend analysis

**Schema:**
```sql
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
```

**Indexes:**
- `idx_memory_performance_metrics_operation_type` - Operation type filtering
- `idx_memory_performance_metrics_session_id` - Session performance analysis
- `idx_memory_performance_metrics_created_at` - Time-based analysis
- `idx_memory_performance_metrics_execution_time` - Performance monitoring

## Integration with Existing Schema

### Existing Tables Enhanced
- **conversation_memory**: Basic conversation storage (backward compatibility)
- **document_chunks**: Vector storage for document embeddings
- **documents**: Document tracking and metadata

### Integration Points
1. **Vector Operations**: Shared pgvector extension for embeddings
2. **Session Context**: Link conversations to relevant documents
3. **Metadata Consistency**: Unified JSONB metadata structure
4. **Performance Monitoring**: Integrated metrics collection

## Performance Optimization

### Indexing Strategy
- **Primary indexes** on foreign keys for join performance
- **Composite indexes** for common query patterns
- **Vector indexes** for semantic search using HNSW
- **Hash indexes** for exact content matching
- **Partial indexes** for active sessions and recent data

### Query Optimization
- **Partitioning** by session_id for large datasets
- **Materialized views** for session summaries
- **Caching** for frequently accessed data
- **Connection pooling** for concurrent access

### Performance Benchmarks
- **Memory rehydration**: <5 seconds
- **Conversation retrieval**: <2 seconds
- **Context merging**: <1 second
- **Session creation**: <500ms
- **Message storage**: <200ms

## Security and Privacy

### Data Protection
- **Input validation** for all user content
- **Content sanitization** for stored messages
- **Access control** based on user_id
- **Data encryption** for sensitive preferences

### Privacy Features
- **Session isolation** between users
- **Data retention** policies with automatic cleanup
- **Anonymization** for analytics
- **User consent** tracking for data usage

## Maintenance and Operations

### Automated Cleanup
- **Expired cache entries** (1 hour TTL)
- **Expired context entries** (configurable TTL)
- **Old performance metrics** (30 days retention)
- **Inactive sessions** (configurable cleanup)

### Monitoring
- **Query performance** tracking
- **Index usage** analysis
- **Cache hit rates** monitoring
- **Storage growth** tracking
- **Error rate** monitoring

## Migration and Compatibility

### Backward Compatibility
- **Existing conversation_memory** table preserved
- **Gradual migration** of data to new schema
- **API compatibility** maintained during transition
- **Rollback capability** for safe deployment

### Migration Strategy
1. **Schema creation** with IF NOT EXISTS
2. **Data migration** from existing tables
3. **Index creation** for performance
4. **Validation** of data integrity
5. **Performance testing** against benchmarks
