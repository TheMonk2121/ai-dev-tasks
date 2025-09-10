# LTST Memory System Database Schema Documentation

## Overview

The LTST Memory System extends the existing conversation memory infrastructure with ChatGPT-like Long-Term Short-Term memory capabilities. This schema provides conversation persistence, session tracking, context merging, and user preference learning.

## Schema Tables

### 1. conversation_sessions

**Purpose:** Manages conversation sessions and their metadata.

**Key Fields:**
- `session_id` (VARCHAR(255), PRIMARY KEY): Unique session identifier
- `user_id` (VARCHAR(255)): User identifier for session ownership
- `session_name` (VARCHAR(500)): Human-readable session name
- `session_type` (VARCHAR(100)): Type of session (conversation, project, etc.)
- `status` (VARCHAR(50)): Session status (active, archived, etc.)
- `context_summary` (TEXT): AI-generated summary of session context
- `relevance_score` (FLOAT): Overall session relevance score
- `session_length` (INTEGER): Number of messages in session

**Indexes:**
- `idx_conversation_sessions_user_id`: Fast user session lookup
- `idx_conversation_sessions_last_activity`: Recent activity queries
- `idx_conversation_sessions_relevance_score`: Relevance-based sorting

### 2. conversation_messages

**Purpose:** Stores individual conversation messages with metadata and embeddings.

**Key Fields:**
- `message_id` (SERIAL, PRIMARY KEY): Unique message identifier
- `session_id` (VARCHAR(255)): Foreign key to conversation_sessions
- `message_type` (VARCHAR(50)): Message type (message, system, context, preference)
- `role` (VARCHAR(50)): Message role (human, ai, system)
- `content` (TEXT): Message content
- `content_hash` (VARCHAR(64)): Hash for content deduplication
- `context_hash` (VARCHAR(64)): Hash for context relationships
- `message_index` (INTEGER): Sequential message order within session
- `embedding` (VECTOR(384)): Message embedding for semantic search
- `relevance_score` (FLOAT): Message relevance score
- `parent_message_id` (INTEGER): Reference to parent message for threading

**Indexes:**
- `idx_conversation_messages_session_id`: Session message lookup
- `idx_conversation_messages_embedding`: HNSW index for semantic search
- `idx_conversation_messages_message_index`: Sequential message ordering

### 3. conversation_context

**Purpose:** Stores context relationships and metadata for conversations.

**Key Fields:**
- `context_id` (SERIAL, PRIMARY KEY): Unique context identifier
- `session_id` (VARCHAR(255)): Foreign key to conversation_sessions
- `context_type` (VARCHAR(100)): Context type (conversation, preference, project, user_info)
- `context_key` (VARCHAR(255)): Context key for categorization
- `context_value` (TEXT): Context value
- `relevance_score` (FLOAT): Context relevance score
- `context_hash` (VARCHAR(64)): Hash for context deduplication
- `expires_at` (TIMESTAMP): Context expiration time

**Indexes:**
- `idx_conversation_context_session_id`: Session context lookup
- `idx_conversation_context_type`: Context type filtering
- `idx_conversation_context_relevance_score`: Relevance-based sorting

### 4. user_preferences

**Purpose:** Learns and stores user preferences for personalized interactions.

**Key Fields:**
- `preference_id` (SERIAL, PRIMARY KEY): Unique preference identifier
- `user_id` (VARCHAR(255)): User identifier
- `preference_key` (VARCHAR(255)): Preference key
- `preference_value` (TEXT): Preference value
- `preference_type` (VARCHAR(100)): Preference category (general, coding, communication, project)
- `confidence_score` (FLOAT): Confidence in preference accuracy
- `source` (VARCHAR(100)): Preference source (learned, explicit, inferred)
- `usage_count` (INTEGER): Number of times preference was used
- `last_used` (TIMESTAMP): Last time preference was applied

**Indexes:**
- `idx_user_preferences_user_id`: User preference lookup
- `idx_user_preferences_key`: Preference key lookup
- `idx_user_preferences_confidence_score`: Confidence-based sorting

### 5. memory_retrieval_cache

**Purpose:** Caches memory retrieval results for performance optimization.

**Key Fields:**
- `cache_id` (SERIAL, PRIMARY KEY): Unique cache entry identifier
- `cache_key` (VARCHAR(255), UNIQUE): Cache key for lookup
- `session_id` (VARCHAR(255)): Associated session
- `query_hash` (VARCHAR(64)): Hash of the query that generated this cache
- `retrieved_context` (JSONB): Cached context data
- `relevance_scores` (JSONB): Cached relevance scores
- `retrieval_time_ms` (INTEGER): Original retrieval time
- `cache_hit_count` (INTEGER): Number of cache hits
- `expires_at` (TIMESTAMP): Cache expiration time

**Indexes:**
- `idx_memory_retrieval_cache_session_id`: Session cache lookup
- `idx_memory_retrieval_cache_expires_at`: Expiration-based cleanup

### 6. session_relationships

**Purpose:** Links related conversations for context continuity.

**Key Fields:**
- `relationship_id` (SERIAL, PRIMARY KEY): Unique relationship identifier
- `source_session_id` (VARCHAR(255)): Source session
- `target_session_id` (VARCHAR(255)): Target session
- `relationship_type` (VARCHAR(100)): Relationship type (continuation, related, fork, reference)
- `similarity_score` (FLOAT): Similarity between sessions
- `relationship_strength` (FLOAT): Strength of relationship

**Indexes:**
- `idx_session_relationships_source`: Source session relationships
- `idx_session_relationships_target`: Target session relationships
- `idx_session_relationships_similarity`: Similarity-based sorting

### 7. memory_performance_metrics

**Purpose:** Tracks performance metrics for optimization and monitoring.

**Key Fields:**
- `metric_id` (SERIAL, PRIMARY KEY): Unique metric identifier
- `operation_type` (VARCHAR(100)): Operation type (retrieval, storage, merging, context_search)
- `session_id` (VARCHAR(255)): Associated session
- `operation_hash` (VARCHAR(64)): Hash of operation parameters
- `execution_time_ms` (INTEGER): Operation execution time
- `result_count` (INTEGER): Number of results returned
- `cache_hit` (BOOLEAN): Whether cache was hit
- `error_message` (TEXT): Error message if operation failed

**Indexes:**
- `idx_memory_performance_metrics_operation_type`: Operation type filtering
- `idx_memory_performance_metrics_execution_time`: Performance analysis

## Database Functions

### 1. update_session_length()

**Purpose:** Automatically updates session length when messages are added.

**Trigger:** `update_session_length_trigger` on conversation_messages INSERT

### 2. clean_expired_cache()

**Purpose:** Removes expired cache entries.

**Usage:** Can be called manually or via scheduled job

### 3. clean_expired_context()

**Purpose:** Removes expired context entries.

**Usage:** Can be called manually or via scheduled job

## Database Views

### 1. session_summary

**Purpose:** Provides aggregated session information.

**Key Fields:**
- Session metadata (id, user, name, type, status)
- Message count and timing
- Average message relevance

### 2. user_preference_summary

**Purpose:** Provides aggregated user preference information.

**Key Fields:**
- Preference counts by type
- Average confidence scores
- Usage statistics

## Integration Points

### Existing Schema Integration

The LTST Memory System integrates with existing tables:

1. **document_chunks**: Leverages existing vector infrastructure
2. **conversation_memory**: Extends existing conversation storage
3. **documents**: References for project context
4. **event_ledger**: Integration with n8n workflows

### Performance Considerations

1. **HNSW Indexes**: Optimized for semantic search with 384-dimensional embeddings
2. **Caching**: Memory retrieval cache with 1-hour TTL
3. **Indexing**: Comprehensive indexing for all query patterns
4. **Cleanup**: Automatic cleanup of expired data

### Security Features

1. **Content Hashing**: Prevents duplicate storage
2. **Session Isolation**: User-based session separation
3. **Access Control**: User_id based filtering
4. **Audit Trail**: Comprehensive timestamp tracking

## Migration Strategy

### Phase 1: Schema Creation
1. Create new tables with IF NOT EXISTS
2. Add indexes for performance
3. Create functions and triggers
4. Insert default system preferences

### Phase 2: Data Migration
1. Migrate existing conversation_memory data
2. Create session records for existing conversations
3. Generate embeddings for existing messages
4. Validate data integrity

### Phase 3: Integration
1. Update application code to use new schema
2. Implement backward compatibility layer
3. Performance testing and optimization
4. Gradual rollout with feature flags

## Monitoring and Maintenance

### Performance Monitoring
- Track execution times via memory_performance_metrics
- Monitor cache hit rates
- Alert on slow queries (>5s)

### Data Maintenance
- Regular cleanup of expired cache entries
- Archive old sessions based on retention policy
- Optimize indexes based on usage patterns

### Health Checks
- Verify schema integrity
- Check index performance
- Monitor storage growth
- Validate trigger functions
