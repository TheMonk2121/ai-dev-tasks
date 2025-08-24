# LTST Memory System Database Schema Design

## Overview

This document defines the complete database schema for the LTST (Long-Term Short-Term) Memory System, providing ChatGPT-like conversation memory with session tracking, context management, and semantic search capabilities.

## Existing Schema Integration

The LTST system builds upon the existing DSPy RAG system schema:
- `document_chunks` - Vector storage for document embeddings
- `documents` - Document tracking and metadata
- `conversation_memory` - Basic conversation storage (to be enhanced)

## New Tables Design

### 1. conversation_sessions
**Purpose:** Manage conversation sessions and user interactions

```sql
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
```

**Indexes:**
- `idx_conversation_sessions_user_id` on `user_id`
- `idx_conversation_sessions_last_activity` on `last_activity`
- `idx_conversation_sessions_status` on `status`

### 2. conversation_messages
**Purpose:** Store individual conversation messages with metadata

```sql
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
```

**Indexes:**
- `idx_conversation_messages_session_id` on `session_id`
- `idx_conversation_messages_timestamp` on `timestamp`
- `idx_conversation_messages_role` on `role`
- `idx_conversation_messages_embedding` on `embedding` USING ivfflat (embedding vector_cosine_ops)
- `idx_conversation_messages_content_hash` on `content_hash`

### 3. conversation_context
**Purpose:** Store conversation context and preferences

```sql
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
```

**Indexes:**
- `idx_conversation_context_session_id` on `session_id`
- `idx_conversation_context_type` on `context_type`
- `idx_conversation_context_expires` on `expires_at`

### 4. user_preferences
**Purpose:** Store user preferences and settings

```sql
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    preference_key VARCHAR(255) NOT NULL,
    preference_value TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);
```

**Indexes:**
- `idx_user_preferences_user_id` on `user_id`
- `idx_user_preferences_key` on `preference_key`

### 5. session_relationships
**Purpose:** Link related conversation sessions

```sql
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
```

**Indexes:**
- `idx_session_relationships_source` on `source_session_id`
- `idx_session_relationships_target` on `target_session_id`
- `idx_session_relationships_type` on `relationship_type`

### 6. session_summary
**Purpose:** Store session statistics and summaries

```sql
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
```

## Enhanced Existing Tables

### Enhanced conversation_memory
**Purpose:** Maintain backward compatibility while adding new features

```sql
-- Add new columns to existing table
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

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_conversation_memory_content_hash ON conversation_memory(content_hash);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding ON conversation_memory USING ivfflat (embedding vector_cosine_ops);
```

## Performance Optimization

### Indexing Strategy
- **Primary indexes** on foreign keys for join performance
- **Composite indexes** for common query patterns
- **Vector indexes** for semantic search using pgvector
- **Hash indexes** for exact content matching

### Query Optimization
- **Partitioning** by session_id for large datasets
- **Materialized views** for session summaries
- **Caching** for frequently accessed data

## Integration Points

### With Existing Schema
- **document_chunks**: Link conversation context to relevant documents
- **documents**: Reference documents in conversation metadata
- **conversation_memory**: Maintain backward compatibility

### With pgvector
- **Embedding storage** for semantic search
- **Similarity queries** for context matching
- **Vector operations** for relevance scoring

## Security Considerations

### Data Protection
- **Input validation** for all user content
- **Content sanitization** for stored messages
- **Access control** based on user_id
- **Data encryption** for sensitive preferences

### Privacy
- **Session isolation** between users
- **Data retention** policies
- **Anonymization** for analytics

## Migration Strategy

### Phase 1: Schema Creation
1. Create new tables with IF NOT EXISTS
2. Add indexes for performance
3. Create helper functions

### Phase 2: Data Migration
1. Migrate existing conversation_memory data
2. Generate missing metadata
3. Create session relationships

### Phase 3: Validation
1. Verify data integrity
2. Test performance benchmarks
3. Validate backward compatibility

## Performance Benchmarks

### Target Metrics
- **Memory rehydration**: <5 seconds
- **Conversation retrieval**: <2 seconds
- **Context merging**: <1 second
- **Session creation**: <500ms
- **Message storage**: <200ms

### Monitoring
- **Query performance** tracking
- **Index usage** analysis
- **Cache hit rates** monitoring
- **Storage growth** tracking
