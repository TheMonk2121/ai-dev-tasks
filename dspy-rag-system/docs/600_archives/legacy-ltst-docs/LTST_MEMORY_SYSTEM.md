# LTST Memory System Documentation

## Overview

The LTST (Long-Term Short-Term) Memory System provides ChatGPT-like conversation memory capabilities for the DSPy RAG System. It enables persistent conversation storage, session tracking, context merging, and semantic search across conversation history.

## Architecture

### Core Components

1. **Conversation Sessions** - Manage conversation continuity and user interactions
2. **Conversation Messages** - Store individual messages with metadata and embeddings
3. **Conversation Context** - Maintain context and preferences across sessions
4. **User Preferences** - Store user-specific settings and preferences
5. **Session Relationships** - Link related conversation sessions
6. **Session Summary** - Track session statistics and summaries

### Database Schema

The system uses PostgreSQL with pgvector extension for vector storage and semantic search capabilities.

#### Tables

- `conversation_sessions` - Session management
- `conversation_messages` - Individual messages with embeddings
- `conversation_context` - Context storage
- `user_preferences` - User preference storage
- `session_relationships` - Session linking
- `session_summary` - Session statistics

#### Key Features

- **Vector Embeddings** - Semantic search using pgvector
- **JSONB Metadata** - Flexible metadata storage
- **Automatic Triggers** - Session activity and summary updates
- **Foreign Key Constraints** - Data integrity
- **Performance Indexes** - Optimized query performance

## Installation

### Prerequisites

- PostgreSQL 12+ with pgvector extension
- Python 3.8+ with required dependencies

### Database Setup

1. **Run the migration script:**
   ```bash
   psql -d your_database -f dspy-rag-system/config/database/ltst_schema_migration.sql
   ```

2. **Verify installation:**
   ```bash
   python -m pytest dspy-rag-system/tests/test_ltst_schema.py
   ```

### Python Dependencies

The system requires the following Python packages:
- `psycopg2-binary` - PostgreSQL adapter
- `pgvector` - Vector operations
- `numpy` - Numerical operations

## Usage

### Basic Usage

```python
from dspy_rag_system.src.utils.conversation_storage import ConversationStorage, ConversationSession, ConversationMessage

# Initialize storage
storage = ConversationStorage()

# Create a session
session = ConversationSession(
    session_id="session_123",
    user_id="user_456",
    session_name="Development Discussion"
)
storage.create_session(session)

# Store a message
message = ConversationMessage(
    session_id="session_123",
    role="human",
    content="How do I implement the LTST memory system?",
    message_type="message"
)
storage.store_message(message)
```

### Advanced Features

#### Semantic Search

```python
# Search for similar messages
results = storage.search_messages(
    query="memory system implementation",
    session_id="session_123",
    limit=10,
    threshold=0.7
)

for message, similarity in results:
    print(f"Similarity: {similarity}, Content: {message.content}")
```

#### Context Management

```python
from dspy_rag_system.src.utils.conversation_storage import ConversationContext

# Store context
context = ConversationContext(
    session_id="session_123",
    context_type="project",
    context_key="current_task",
    context_value="LTST Memory System Implementation",
    relevance_score=0.9
)
storage.store_context(context)

# Retrieve context
contexts = storage.get_context("session_123", context_type="project")
```

#### Session Management

```python
# Get user sessions
sessions = storage.get_user_sessions("user_456", limit=50)

# Update session activity
storage.update_session_activity("session_123")

# Get session summary
summary = storage.get_session_summary("session_123")
```

## API Reference

### ConversationStorage

Main class for conversation storage and retrieval.

#### Methods

- `create_session(session)` - Create a new conversation session
- `get_session(session_id)` - Retrieve a conversation session
- `store_message(message)` - Store a conversation message
- `get_messages(session_id, limit, offset)` - Retrieve messages for a session
- `search_messages(query, session_id, limit, threshold)` - Search messages using semantic similarity
- `store_context(context)` - Store conversation context
- `get_context(session_id, context_type)` - Retrieve conversation context
- `update_session_activity(session_id)` - Update session last activity timestamp
- `get_user_sessions(user_id, limit)` - Get sessions for a user
- `delete_session(session_id)` - Delete a conversation session and all associated data
- `get_session_summary(session_id)` - Get session summary statistics
- `cleanup_expired_data()` - Clean up expired context and cache entries

### Data Classes

#### ConversationSession

Represents a conversation session.

**Attributes:**
- `session_id` - Unique session identifier
- `user_id` - User identifier
- `session_name` - Human-readable session name
- `session_type` - Type of session (default: 'conversation')
- `status` - Session status (default: 'active')
- `metadata` - Additional metadata
- `context_summary` - Session context summary
- `relevance_score` - Session relevance score
- `created_at` - Creation timestamp
- `last_activity` - Last activity timestamp

#### ConversationMessage

Represents a conversation message.

**Attributes:**
- `session_id` - Session identifier
- `role` - Message role ('human', 'ai', 'system')
- `content` - Message content
- `message_type` - Type of message (default: 'message')
- `message_index` - Message index within session
- `parent_message_id` - Parent message identifier
- `metadata` - Additional metadata
- `embedding` - Vector embedding for semantic search
- `relevance_score` - Message relevance score
- `is_context_message` - Whether this is a context message
- `timestamp` - Message timestamp

#### ConversationContext

Represents conversation context.

**Attributes:**
- `session_id` - Session identifier
- `context_type` - Type of context ('conversation', 'preference', 'project', 'user_info')
- `context_key` - Context key
- `context_value` - Context value
- `relevance_score` - Context relevance score
- `metadata` - Additional metadata
- `expires_at` - Expiration timestamp

## Performance

### Benchmarks

- **Memory rehydration**: <5 seconds
- **Conversation retrieval**: <2 seconds
- **Context merging**: <1 second
- **Session creation**: <500ms
- **Message storage**: <200ms

### Optimization

#### Indexing Strategy

- Primary indexes on foreign keys for join performance
- Composite indexes for common query patterns
- Vector indexes for semantic search using pgvector
- Hash indexes for exact content matching

#### Caching

- In-memory caching for frequently accessed data
- Cache TTL of 1 hour for session data
- Automatic cache invalidation on updates

## Security

### Data Protection

- Input validation for all user content
- Content sanitization for stored messages
- Access control based on user_id
- Data encryption for sensitive preferences

### Privacy

- Session isolation between users
- Data retention policies
- Anonymization for analytics

## Monitoring

### Metrics

- Query performance tracking
- Index usage analysis
- Cache hit rates monitoring
- Storage growth tracking

### Logging

The system uses structured logging with the following levels:
- `INFO` - Normal operations
- `WARNING` - Non-critical issues
- `ERROR` - Critical errors
- `DEBUG` - Detailed debugging information

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify DATABASE_URL environment variable
   - Check PostgreSQL service status
   - Validate connection credentials

2. **Performance Issues**
   - Check index usage with `EXPLAIN ANALYZE`
   - Monitor query execution times
   - Verify pgvector extension is enabled

3. **Schema Migration Issues**
   - Run schema validation tests
   - Check for conflicting table names
   - Verify PostgreSQL version compatibility

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger('dspy_rag_system.src.utils.conversation_storage').setLevel(logging.DEBUG)
```

## Migration

### From Previous Versions

1. **Backup existing data**
2. **Run migration script**
3. **Verify data integrity**
4. **Update application code**
5. **Test functionality**

### Rollback

The migration script uses `IF NOT EXISTS` clauses, making it safe to run multiple times. To rollback:

1. **Drop new tables** (if needed)
2. **Restore from backup**
3. **Revert application code**

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
