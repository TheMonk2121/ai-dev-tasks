<!-- ANCHOR_KEY: multi-tenant-indexing-strategy -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["coder", "implementer"] -->
<!-- CONTEXT_REFERENCE: 400_guides/400_system-overview.md -->
<!-- MEMORY_CONTEXT: MEDIUM - Multi-tenant database indexing strategy for future scalability -->

<!-- markdownlint-disable MD041 -->

# Multi-Tenant Indexing Strategy

> DEPRECATED: Content integrated into core guides — see `400_guides/400_11_deployments-ops-and-observability.md` (DB performance/monitoring), `400_guides/400_10_security-compliance-and-access.md` (data isolation, RLS, auth), `400_guides/400_06_memory-and-context-systems.md` (schema touchpoints for memory/rehydration), `400_guides/400_09_automation-and-pipelines.md` (migration/index validation in CI), and `400_guides/400_00_getting-started-and-index.md` (index). Implementation lives under `dspy-rag-system/config/database/`.

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Database indexing strategy for multi-tenant support | Planning database scaling or implementing user isolation | Review current indexes and implement tenant-aware queries |

## 📋 Overview

This document outlines the indexing strategy for supporting multi-tenant scenarios in the DSPy RAG system. The current single-user setup includes `user_id` columns that are ready for future multi-tenant expansion.

## 🏗️ Current Multi-Tenant Infrastructure

### Existing User-Aware Columns

The following tables already include `user_id` columns for future multi-tenant support:

- **conversation_memory**: `user_id VARCHAR(255)` (nullable)
- **conversation_sessions**: `user_id VARCHAR(255)` (nullable)
- **conversation_messages**: `user_id VARCHAR(255)` (nullable)
- **user_preferences**: `user_id VARCHAR(255)` (primary key)

### Existing Indexes

Current indexes that support multi-tenant queries:

```sql
-- User-specific indexes
idx_conversation_memory_user_id ON conversation_memory(user_id)
idx_conversation_memory_session_user ON conversation_memory(session_id, user_id)
idx_conversation_memory_user_created ON conversation_memory(user_id, created_at)

-- Session-specific indexes
idx_conversation_sessions_user_id ON conversation_sessions(user_id)
idx_conversation_sessions_user_created ON conversation_sessions(user_id, created_at)

-- Message-specific indexes
idx_conversation_messages_user_id ON conversation_messages(user_id)
idx_conversation_messages_user_created ON conversation_messages(user_id, created_at)
```

## 🎯 Multi-Tenant Indexing Strategy

### Phase 1: Tenant Isolation (Current State)

**Status**: ✅ **Implemented**

- All user-related tables include `user_id` columns
- Basic indexes on `user_id` for tenant isolation
- Composite indexes for common query patterns
- Nullable `user_id` supports current single-user mode

### Phase 2: Performance Optimization (Future)

**Status**: 🔄 **Planned**

#### Additional Indexes Needed

```sql
-- Enhanced user isolation indexes
CREATE INDEX IF NOT EXISTS idx_conversation_memory_user_session_type
ON conversation_memory(user_id, session_id, message_type);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_user_relevance
ON conversation_memory(user_id, relevance_score DESC);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_user_context
ON conversation_memory(user_id, is_context_message, created_at);

-- DSPy multi-tenant indexes
CREATE INDEX IF NOT EXISTS idx_dspy_signatures_user_version
ON dspy_signatures(user_id, version, created_at);

CREATE INDEX IF NOT EXISTS idx_dspy_examples_user_quality
ON dspy_examples(signature_id, user_id, quality_score DESC);
```

#### Query Optimization Patterns

```sql
-- Tenant-aware conversation retrieval
SELECT * FROM conversation_memory
WHERE user_id = $1
ORDER BY created_at DESC
LIMIT 50;

-- Tenant-aware semantic search
SELECT * FROM search_conversations_semantic(
    $1::vector(384),
    0.5,
    10
) WHERE user_id = $2;

-- Tenant-aware DSPy signature lookup
SELECT * FROM dspy_signatures
WHERE user_id = $1
AND signature_name = $2;
```

### Phase 3: Advanced Multi-Tenant Features (Future)

**Status**: 📋 **Planned**

#### Row-Level Security (RLS)

```sql
-- Enable RLS on user tables
ALTER TABLE conversation_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY user_isolation_policy ON conversation_memory
    FOR ALL USING (user_id = current_setting('app.current_user_id'));

CREATE POLICY user_isolation_policy ON conversation_sessions
    FOR ALL USING (user_id = current_setting('app.current_user_id'));
```

#### Tenant-Specific Views

```sql
-- Create tenant-aware views
CREATE OR REPLACE VIEW user_conversation_summary AS
SELECT
    user_id,
    session_id,
    COUNT(*) as message_count,
    MAX(created_at) as last_activity,
    AVG(relevance_score) as avg_relevance
FROM conversation_memory
WHERE user_id IS NOT NULL
GROUP BY user_id, session_id;

-- Tenant-specific statistics
CREATE OR REPLACE VIEW user_statistics AS
SELECT
    user_id,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(*) as total_messages,
    AVG(relevance_score) as avg_relevance,
    MAX(created_at) as last_activity
FROM conversation_memory
WHERE user_id IS NOT NULL
GROUP BY user_id;
```

## 🔧 Implementation Guidelines

### Current Best Practices

1. **Always include user_id in queries** when filtering user data
2. **Use composite indexes** for common query patterns
3. **Maintain nullable user_id** for backward compatibility
4. **Test tenant isolation** with multiple user scenarios

### Performance Considerations

#### Index Maintenance

- **Monitor index usage** with `pg_stat_user_indexes`
- **Analyze query performance** with `EXPLAIN ANALYZE`
- **Consider partial indexes** for active users only
- **Regular index maintenance** for optimal performance

#### Query Optimization

```sql
-- Efficient tenant-aware queries
-- ✅ Good: Use indexed columns in WHERE clause
SELECT * FROM conversation_memory
WHERE user_id = $1 AND created_at > $2;

-- ❌ Avoid: Full table scans
SELECT * FROM conversation_memory
WHERE LOWER(human_message) LIKE '%search%';
```

### Security Considerations

1. **Input validation**: Always validate user_id parameters
2. **SQL injection prevention**: Use parameterized queries
3. **Access control**: Implement proper authentication/authorization
4. **Data isolation**: Ensure no cross-tenant data leakage

## 📊 Monitoring and Metrics

### Key Performance Indicators

- **Query response time** for tenant-specific queries
- **Index hit ratio** for user-related indexes
- **Storage usage** per tenant
- **Concurrent user sessions** per tenant

### Monitoring Queries

```sql
-- Index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname LIKE '%user%';

-- Tenant data distribution
SELECT
    user_id,
    COUNT(*) as message_count,
    COUNT(DISTINCT session_id) as session_count
FROM conversation_memory
WHERE user_id IS NOT NULL
GROUP BY user_id
ORDER BY message_count DESC;
```

## 🚀 Migration Strategy

### From Single-User to Multi-Tenant

1. **Phase 1**: Add user_id columns (✅ Complete)
2. **Phase 2**: Create tenant-aware indexes
3. **Phase 3**: Implement RLS policies
4. **Phase 4**: Add tenant-specific views
5. **Phase 5**: Performance optimization

### Backward Compatibility

- **Maintain nullable user_id** for existing single-user data
- **Default user_id** for legacy applications
- **Gradual migration** to tenant-aware queries
- **Comprehensive testing** of isolation boundaries

## 🔗 Related Files

<!-- ESSENTIAL_FILES: 400_guides/400_system-overview.md -->
<!-- MODULE_REFERENCE: dspy-rag-system/config/database/schema.sql -->

- **Database Schema**: `dspy-rag-system/config/database/schema.sql`
- **System Overview**: `400_guides/400_system-overview.md`
- **Performance Guide**: `400_guides/400_database-performance-guide.md`

## 📝 Change Log

| Date | Change | Author | Impact |
|------|--------|--------|--------|
| 2025-01-27 | Initial multi-tenant indexing strategy | System | New feature planning |

<!-- markdownlint-enable MD041 -->
