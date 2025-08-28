# LTST Memory System Integration Guide

> DEPRECATED: Content integrated into core guides — see `400_guides/400_06_memory-and-context-systems.md` (LTST/memory rehydration architecture and APIs), `400_guides/400_11_deployments-ops-and-observability.md` (monitoring/health/metrics), `400_guides/400_09_automation-and-pipelines.md` (CLI/CI wiring and validation), `400_guides/400_10_security-compliance-and-access.md` (DB/users/permissions/security), `400_guides/400_08_integrations-editor-and-models.md` (integration touchpoints), and `400_guides/400_00_getting-started-and-index.md` (index). Implementation lives under `dspy-rag-system/` and `scripts/`.

## TL;DR

The LTST Memory System now includes a powerful database integration layer that leverages PostgreSQL functions for enhanced performance and functionality. This integration provides:

- **Database-powered context merging** with intelligent relevance scoring
- **Automatic memory rehydration** with session continuity detection
- **Real-time performance monitoring** and statistics
- **Dual API support** - both Python and database methods available
- **Comprehensive error handling** and resilience

## Overview

The LTST Memory System has been enhanced with a sophisticated database integration layer that bridges Python functionality with PostgreSQL functions. This integration provides significant performance improvements and advanced features while maintaining backward compatibility.

### Key Features

- **Context Merging**: Intelligent merging of conversation contexts using PostgreSQL functions
- **Memory Rehydration**: Automatic restoration of conversation state with continuity detection
- **Session Management**: Real-time session tracking and continuity scoring
- **Performance Monitoring**: Built-in statistics and health monitoring
- **Error Resilience**: Comprehensive error handling and recovery mechanisms

## Architecture

### Integration Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    LTST Memory System                       │
├─────────────────────────────────────────────────────────────┤
│  Python API Layer (Backward Compatible)                    │
│  ├── merge_contexts()                                      │
│  ├── rehydrate_memory()                                    │
│  └── store_conversation_message()                          │
├─────────────────────────────────────────────────────────────┤
│  Database Integration Layer (New)                          │
│  ├── merge_contexts_database()                             │
│  ├── rehydrate_memory_database()                           │
│  └── database_integration.*                                │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL Functions Layer                                │
│  ├── merge_contexts_intelligent()                          │
│  ├── rehydrate_memory_automatic()                          │
│  └── detect_session_continuity()                           │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **LTSTMemorySystem**: Main integration class with dual API support
2. **LTSTDatabaseIntegration**: Direct PostgreSQL function access layer
3. **DatabaseMergeResult**: Structured results from context merging
4. **DatabaseRehydrationResult**: Structured results from memory rehydration

## Quick Start

### Basic Usage

```python
from utils.ltst_memory_system import LTSTMemorySystem

# Initialize the system
ltst_system = LTSTMemorySystem()

# Store conversation messages
ltst_system.store_conversation_message(
    session_id="my_session",
    user_id="user123",
    role="human",
    content="Hello, how are you?"
)

# Use database-powered context merging
merge_result = ltst_system.merge_contexts_database(
    session_id="my_session",
    relevance_threshold=0.7
)

print(f"Merged {merge_result.source_context_count} contexts")
print(f"Quality score: {merge_result.merge_quality_score:.3f}")

# Use database-powered memory rehydration
rehydration_result = ltst_system.rehydrate_memory_database(
    session_id="my_session",
    user_id="user123"
)

print(f"Continuity score: {rehydration_result.continuity_score:.3f}")
print(f"Rehydrated context: {rehydration_result.rehydrated_context}")
```

### Advanced Usage

```python
# Get session continuity information
continuity_info = ltst_system.database_integration.get_session_continuity(
    session_id="my_session"
)

print(f"Session is continuous: {continuity_info['is_continuous']}")
print(f"Message count: {continuity_info['message_count']}")

# Get system statistics
context_stats = ltst_system.database_integration.get_context_statistics()
rehydration_stats = ltst_system.database_integration.get_rehydration_statistics()

print(f"Total contexts: {context_stats['total_contexts']}")
print(f"Total sessions: {rehydration_stats['total_sessions']}")

# Optimize caches
optimization_results = ltst_system.database_integration.optimize_caches()
```

## API Reference

### LTSTMemorySystem Class

#### Database Integration Methods

##### `merge_contexts_database()`

Merges contexts using PostgreSQL functions for enhanced performance.

```python
def merge_contexts_database(
    self,
    session_id: str,
    merge_strategy: str = "relevance",
    max_merged_length: int = 5000,
    relevance_threshold: float = 0.7,
    similarity_threshold: float = 0.8
) -> DatabaseMergeResult:
```

**Parameters:**
- `session_id`: Session identifier
- `merge_strategy`: Merging strategy ('relevance' or 'similarity')
- `max_merged_length`: Maximum length of merged content
- `relevance_threshold`: Minimum relevance score
- `similarity_threshold`: Minimum similarity threshold

**Returns:** `DatabaseMergeResult` with merged content and metadata

##### `rehydrate_memory_database()`

Rehydrates memory using PostgreSQL functions with continuity detection.

```python
def rehydrate_memory_database(
    self,
    session_id: str,
    user_id: str,
    max_context_length: int = 10000,
    include_history: bool = True,
    history_limit: int = 20
) -> DatabaseRehydrationResult:
```

**Parameters:**
- `session_id`: Session identifier
- `user_id`: User identifier
- `max_context_length`: Maximum context length
- `include_history`: Whether to include conversation history
- `history_limit`: Maximum number of history messages

**Returns:** `DatabaseRehydrationResult` with rehydrated content

### LTSTDatabaseIntegration Class

#### Session Management

##### `get_session_continuity()`

Detects session continuity and provides scoring.

```python
def get_session_continuity(
    self,
    session_id: str,
    continuity_window_hours: int = 24
) -> Dict[str, Any]:
```

**Returns:** Dictionary with continuity information including:
- `continuity_score`: Continuity score (0.0 to 1.0)
- `message_count`: Number of messages in session
- `is_continuous`: Whether session is considered continuous
- `last_activity`: Timestamp of last activity
- `hours_since_last_activity`: Hours since last activity

#### Statistics and Monitoring

##### `get_context_statistics()`

Retrieves context merging statistics.

```python
def get_context_statistics(
    self,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
```

**Returns:** Dictionary with context statistics including:
- `total_contexts`: Total number of contexts
- `avg_relevance`: Average relevance score
- `context_types`: List of context types
- `cache_hit_ratio`: Cache hit ratio
- `merge_operations_count`: Number of merge operations

##### `get_rehydration_statistics()`

Retrieves memory rehydration statistics.

```python
def get_rehydration_statistics(
    self,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
```

**Returns:** Dictionary with rehydration statistics including:
- `total_sessions`: Total number of sessions
- `active_sessions`: Number of active sessions
- `avg_continuity_score`: Average continuity score
- `avg_rehydration_quality`: Average rehydration quality
- `cache_hit_ratio`: Cache hit ratio

##### `optimize_caches()`

Optimizes both context and rehydration caches.

```python
def optimize_caches(self) -> Dict[str, Any]:
```

**Returns:** Dictionary with optimization results for both caches.

### Result Classes

#### DatabaseMergeResult

```python
@dataclass
class DatabaseMergeResult:
    merged_content: str              # Merged context content
    source_context_count: int        # Number of source contexts
    avg_relevance: float             # Average relevance score
    merge_quality_score: float       # Overall merge quality (0.0-1.0)
    context_types: List[str]         # Types of contexts merged
```

#### DatabaseRehydrationResult

```python
@dataclass
class DatabaseRehydrationResult:
    session_id: str                  # Session identifier
    user_id: str                     # User identifier
    rehydrated_context: str          # Rehydrated context content
    conversation_history: str        # Conversation history
    user_preferences: str            # User preferences (JSON)
    continuity_score: float          # Session continuity score (0.0-1.0)
    context_count: int               # Number of contexts used
    rehydration_quality_score: float # Rehydration quality (0.0-1.0)
    cache_hit: bool                  # Whether result was from cache
```

## Performance Characteristics

### Benchmarks

Based on testing with existing data:

- **Context Merging**: ~16ms average execution time
- **Memory Rehydration**: ~2.7ms average execution time
- **Session Continuity**: ~1ms average execution time
- **Statistics Retrieval**: ~5ms average execution time

### Scalability

The database integration layer is designed for scalability:

- **Connection Pooling**: Automatic connection management
- **Query Optimization**: Optimized PostgreSQL functions
- **Caching**: Built-in caching for frequently accessed data
- **Indexing**: Optimized database indexes for fast queries

### Quality Metrics

The system provides comprehensive quality metrics:

- **Merge Quality Score**: 0.0-1.0 scale based on context diversity and relevance
- **Rehydration Quality Score**: 0.0-1.0 scale based on context completeness and continuity
- **Continuity Score**: 0.0-1.0 scale based on session activity patterns

## Error Handling

### Graceful Degradation

The system handles errors gracefully:

- **Invalid Session IDs**: Returns empty results without exceptions
- **Invalid User IDs**: Returns empty results without exceptions
- **Database Errors**: Logs errors and provides fallback behavior
- **Network Issues**: Automatic retry with exponential backoff

### Error Recovery

```python
try:
    merge_result = ltst_system.merge_contexts_database("invalid_session")
    # Returns empty result instead of raising exception
    assert merge_result.source_context_count == 0
except Exception as e:
    # Should not reach here for invalid inputs
    print(f"Unexpected error: {e}")
```

## Migration Guide

### From Python-Only to Database Integration

The integration is backward compatible. Existing code continues to work:

```python
# Old way (still works)
merge_result = ltst_system.merge_contexts(session_id)

# New way (recommended)
merge_result = ltst_system.merge_contexts_database(session_id)
```

### Database Schema Requirements

Ensure your database has the required schema:

```sql
-- Required tables (already included in schema.sql)
CREATE TABLE IF NOT EXISTS conversation_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),
    relevance_score FLOAT DEFAULT 0.0,
    context_type VARCHAR(100),
    context_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Required indexes
CREATE INDEX IF NOT EXISTS idx_conversation_memory_session_id ON conversation_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_user_id ON conversation_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding ON conversation_memory USING hnsw(embedding vector_cosine_ops);
```

### PostgreSQL Functions

The integration requires PostgreSQL functions to be installed:

```sql
-- Apply the function files
\i config/database/context_merging_functions.sql
\i config/database/memory_rehydration_functions.sql
```

## Best Practices

### Performance Optimization

1. **Use Appropriate Thresholds**: Set relevance thresholds based on your use case
2. **Monitor Statistics**: Regularly check system statistics for optimization opportunities
3. **Optimize Caches**: Run cache optimization periodically
4. **Connection Pooling**: Use connection pooling for high-traffic applications

### Error Handling

1. **Always Check Results**: Verify result objects before using their data
2. **Handle Empty Results**: Account for cases where no data is found
3. **Monitor Error Rates**: Track error rates using system health monitoring
4. **Implement Fallbacks**: Provide fallback behavior for critical operations

### Data Management

1. **Regular Cleanup**: Implement regular cleanup of old conversation data
2. **Monitor Storage**: Track database storage usage and growth
3. **Backup Strategy**: Implement regular backups of conversation data
4. **Data Retention**: Establish clear data retention policies

## Troubleshooting

### Common Issues

#### Database Connection Errors

**Symptoms:** "Database connection error: 0"

**Solutions:**
1. Verify database is running and accessible
2. Check connection string format
3. Ensure database user has required permissions
4. Verify network connectivity

#### Function Not Found Errors

**Symptoms:** "function merge_contexts_intelligent does not exist"

**Solutions:**
1. Ensure PostgreSQL functions are installed
2. Check function file application
3. Verify database schema is up to date
4. Restart database connection

#### Performance Issues

**Symptoms:** Slow response times

**Solutions:**
1. Check database indexes
2. Monitor query performance
3. Optimize relevance thresholds
4. Review cache settings

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check system health:

```python
health = ltst_system.get_system_health()
print(f"Database connected: {health.database_connected}")
print(f"Error rate: {health.error_rate:.3f}")
```

## Examples

### Complete Integration Example

```python
from utils.ltst_memory_system import LTSTMemorySystem

# Initialize system
ltst_system = LTSTMemorySystem()

# Store conversation
session_id = "example_session"
user_id = "example_user"

ltst_system.store_conversation_message(
    session_id=session_id,
    user_id=user_id,
    role="human",
    content="I need help with Python programming"
)

ltst_system.store_conversation_message(
    session_id=session_id,
    user_id=user_id,
    role="ai",
    content="I'd be happy to help with Python programming!"
)

# Store context
ltst_system.store_context(
    session_id=session_id,
    context_type="user_preference",
    context_key="programming_language",
    context_value="Python",
    relevance=0.9
)

# Merge contexts using database integration
merge_result = ltst_system.merge_contexts_database(
    session_id=session_id,
    relevance_threshold=0.7
)

print(f"Context merging completed:")
print(f"  Contexts merged: {merge_result.source_context_count}")
print(f"  Quality score: {merge_result.merge_quality_score:.3f}")
print(f"  Content length: {len(merge_result.merged_content)}")

# Rehydrate memory
rehydration_result = ltst_system.rehydrate_memory_database(
    session_id=session_id,
    user_id=user_id
)

print(f"Memory rehydration completed:")
print(f"  Continuity score: {rehydration_result.continuity_score:.3f}")
print(f"  Quality score: {rehydration_result.rehydration_quality_score:.3f}")
print(f"  Context count: {rehydration_result.context_count}")

# Check session continuity
continuity_info = ltst_system.database_integration.get_session_continuity(session_id)
print(f"Session continuity: {continuity_info['is_continuous']}")

# Get statistics
context_stats = ltst_system.database_integration.get_context_statistics()
print(f"Total contexts in system: {context_stats['total_contexts']}")
```

### Advanced Usage Example

```python
# Custom merge strategy with specific parameters
merge_result = ltst_system.merge_contexts_database(
    session_id="advanced_session",
    merge_strategy="relevance",
    max_merged_length=8000,
    relevance_threshold=0.8,
    similarity_threshold=0.9
)

# Memory rehydration with custom parameters
rehydration_result = ltst_system.rehydrate_memory_database(
    session_id="advanced_session",
    user_id="advanced_user",
    max_context_length=15000,
    include_history=True,
    history_limit=30
)

# Session-specific statistics
session_context_stats = ltst_system.database_integration.get_context_statistics("advanced_session")
session_rehydration_stats = ltst_system.database_integration.get_rehydration_statistics("advanced_session")

# Cache optimization
optimization_results = ltst_system.database_integration.optimize_caches()
print(f"Context cache optimized: {optimization_results['context_cache']}")
print(f"Rehydration cache optimized: {optimization_results['rehydration_cache']}")
```

## Security Considerations

### Data Protection

- **Input Validation**: All user content is validated before storage
- **Content Sanitization**: Messages are sanitized to prevent injection attacks
- **Access Control**: Session isolation based on user_id
- **Data Encryption**: Sensitive preferences are encrypted at rest

### Privacy Features

- **Session Isolation**: Complete separation between users
- **Data Retention**: Configurable retention policies
- **Anonymization**: Analytics data is anonymized
- **Audit Trail**: Comprehensive timestamp tracking

### Database Security

```sql
-- Create dedicated user with limited permissions
CREATE USER ltst_user WITH PASSWORD 'secure_password';

-- Grant necessary permissions
GRANT CONNECT ON DATABASE ai_agency TO ltst_user;
GRANT USAGE ON SCHEMA public TO ltst_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ltst_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ltst_user;

-- Revoke unnecessary permissions
REVOKE CREATE ON SCHEMA public FROM ltst_user;
REVOKE DROP ON SCHEMA public FROM ltst_user;
```

### Application Security

```python
# Use environment variables for sensitive data
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Validate database URL format
if not DATABASE_URL.startswith('postgresql://'):
    raise ValueError("Invalid DATABASE_URL format")
```

## Database Schema Details

### Core Tables

#### conversation_sessions
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

#### conversation_messages
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

#### conversation_context
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

#### user_preferences
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

### Database Functions

#### update_session_length()
**Purpose:** Automatically updates session length when messages are added.
**Trigger:** `update_session_length_trigger` on conversation_messages INSERT

#### clean_expired_cache()
**Purpose:** Removes expired cache entries.
**Usage:** Can be called manually or via scheduled job

#### clean_expired_context()
**Purpose:** Removes expired context entries.
**Usage:** Can be called manually or via scheduled job

### Database Views

#### session_summary
**Purpose:** Provides aggregated session information.
**Key Fields:**
- Session metadata (id, user, name, type, status)
- Message count and timing
- Average message relevance

#### user_preference_summary
**Purpose:** Provides aggregated user preference information.
**Key Fields:**
- Preference counts by type
- Average confidence scores
- Usage statistics

## Contributing

### Development Setup

1. **Clone the repository**
2. **Install dependencies**
3. **Set up test database**
4. **Run tests**

### Testing

```bash
# Run all tests
python -m pytest dspy-rag-system/tests/

# Run schema tests only
python -m pytest dspy-rag-system/tests/test_ltst_schema.py

# Run with coverage
python -m pytest --cov=dspy_rag_system dspy-rag-system/tests/
```

### Code Style

Follow the project's coding standards:
- Use type hints
- Add docstrings
- Follow PEP 8
- Write unit tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Conclusion

The LTST Memory System database integration provides significant performance improvements and advanced features while maintaining full backward compatibility. The integration layer successfully bridges Python functionality with PostgreSQL functions, offering the best of both worlds.

Key benefits:
- **Performance**: Faster execution through database optimization
- **Scalability**: Better handling of large datasets
- **Features**: Advanced continuity detection and quality scoring
- **Reliability**: Comprehensive error handling and recovery
- **Compatibility**: Full backward compatibility with existing code

For questions or issues, refer to the troubleshooting section or check the system health monitoring for diagnostic information.
