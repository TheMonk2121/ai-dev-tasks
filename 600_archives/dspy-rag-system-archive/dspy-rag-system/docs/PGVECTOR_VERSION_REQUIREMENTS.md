# pgvector Version Requirements and Fallback Strategy

## Overview

This document outlines the pgvector version requirements for the LTST Memory System database optimization and provides a fallback strategy for environments with limited pgvector support.

## Version Requirements

### Minimum Requirements
- **pgvector**: 0.5.0+ (for HNSW support)
- **PostgreSQL**: 12+ (for pgvector compatibility)
- **Python**: 3.8+ (for psycopg2-binary)

### Recommended Requirements
- **pgvector**: 0.7.0+ (for optimal HNSW performance)
- **PostgreSQL**: 14+ (for better performance)
- **Python**: 3.9+ (for latest features)

## Feature Support Matrix

| pgvector Version | HNSW Indexes | IVFFlat Indexes | Vector Operations | Notes |
|------------------|--------------|-----------------|-------------------|-------|
| 0.8.0+ | ✅ Full | ✅ Full | ✅ Full | **Recommended** |
| 0.7.0+ | ✅ Full | ✅ Full | ✅ Full | **Recommended** |
| 0.6.0+ | ✅ Full | ✅ Full | ✅ Full | Good |
| 0.5.0+ | ✅ Basic | ✅ Full | ✅ Full | Minimum for HNSW |
| 0.4.x | ❌ No | ✅ Full | ✅ Full | IVFFlat only |
| < 0.4.0 | ❌ No | ❌ No | ✅ Basic | Limited support |

## Fallback Strategy

### Primary Strategy: HNSW Indexes
When pgvector 0.5.0+ is available, the system will use HNSW indexes for optimal semantic search performance:

```sql
-- HNSW index with optimal parameters
CREATE INDEX idx_conversation_memory_embedding_hnsw
ON conversation_memory
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Advantages:**
- Better recall/latency trade-off than IVFFlat
- Faster similarity search for small-to-medium datasets
- More accurate nearest neighbor results

### Fallback Strategy: IVFFlat Indexes
When HNSW is not available (pgvector < 0.5.0), the system falls back to IVFFlat indexes:

```sql
-- IVFFlat index as fallback
CREATE INDEX idx_conversation_memory_embedding_ivfflat
ON conversation_memory
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Advantages:**
- Compatible with older pgvector versions
- Good performance for large datasets
- Stable and well-tested

### No Vector Support
When pgvector is not available, the system will:
1. Log warnings about missing vector support
2. Continue operation without semantic search
3. Use text-based search as fallback
4. Provide clear upgrade instructions

## Version Detection

The system automatically detects pgvector version and capabilities using the `check_pgvector_version.py` script:

```bash
# Check version and capabilities
python3 scripts/check_pgvector_version.py --db-url "postgresql://user@host/db"

# Output example:
# ✅ pgvector available: 0.8.0
# 📈 HNSW support: ✅ Yes
# 🎯 Meets minimum: ✅ Yes
# ⭐ Meets recommended: ✅ Yes
```

## Installation Instructions

### Ubuntu/Debian
```bash
# Install PostgreSQL and pgvector
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install pgvector extension
sudo apt install postgresql-14-pgvector  # Adjust version as needed

# Or build from source for latest version
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### macOS (Homebrew)
```bash
# Install PostgreSQL with pgvector
brew install postgresql
brew install pgvector

# Or install pgvector extension separately
brew install pgvector
```

### Docker
```dockerfile
# Use official pgvector image
FROM pgvector/pgvector:pg15

# Or add to existing PostgreSQL image
RUN apt-get update && apt-get install -y postgresql-15-pgvector
```

## Configuration

### PostgreSQL Configuration
Add to `postgresql.conf`:
```conf
# Enable pgvector extension
shared_preload_libraries = 'vector'

# Optional: Tune for vector operations
work_mem = 256MB
maintenance_work_mem = 1GB
```

### Database Setup
```sql
-- Create extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

## Performance Tuning

### HNSW Parameters
- **m**: Number of connections per layer (default: 16)
- **ef_construction**: Search depth during construction (default: 64)
- **ef**: Search depth during queries (default: 40)

### IVFFlat Parameters
- **lists**: Number of inverted lists (default: 100)
- **probes**: Number of lists to search (default: 1)

### Memory Configuration
```conf
# For vector operations
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 256MB
maintenance_work_mem = 1GB
```

## Troubleshooting

### Common Issues

1. **Extension not found**
   ```bash
   # Check if pgvector is installed
   psql -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
   ```

2. **Version too old**
   ```bash
   # Check current version
   psql -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
   ```

3. **Permission denied**
   ```sql
   -- Grant necessary permissions
   GRANT CREATE ON DATABASE your_database TO your_user;
   ```

### Upgrade Instructions

1. **Backup database**
   ```bash
   pg_dump your_database > backup.sql
   ```

2. **Install new pgvector version**
   ```bash
   # Follow installation instructions above
   ```

3. **Update extension**
   ```sql
   ALTER EXTENSION vector UPDATE TO '0.8.0';
   ```

4. **Verify upgrade**
   ```bash
   python3 scripts/check_pgvector_version.py
   ```

## Testing

Run the compatibility test suite:
```bash
# Test version detection
python3 scripts/check_pgvector_version.py

# Test index creation
python3 -m pytest tests/test_ltst_schema.py

# Test performance
python3 -m pytest tests/test_ltst_integration.py
```

## Migration Strategy

### From IVFFlat to HNSW
When upgrading from pgvector < 0.5.0 to 0.5.0+:

1. **Backup existing indexes**
   ```sql
   -- Note existing index names
   SELECT indexname FROM pg_indexes WHERE tablename = 'conversation_memory';
   ```

2. **Create HNSW indexes**
   ```sql
   -- New HNSW indexes will be created automatically
   -- Old IVFFlat indexes can be dropped after verification
   ```

3. **Verify performance**
   ```sql
   -- Compare query performance
   EXPLAIN ANALYZE SELECT * FROM conversation_memory
   ORDER BY embedding <=> '[0.1,0.2,...]'::vector LIMIT 10;
   ```

## Support

For issues with pgvector:
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [pgvector Documentation](https://github.com/pgvector/pgvector#readme)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

For LTST Memory System issues:
- Check the project documentation
- Review the troubleshooting guide
- Open an issue on the project repository
