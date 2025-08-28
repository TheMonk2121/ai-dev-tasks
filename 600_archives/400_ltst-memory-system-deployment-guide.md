# LTST Memory System Deployment Guide

> DEPRECATED: Content integrated into core guides — see `400_guides/400_06_memory-and-context-systems.md` (LTST/memory rehydration fundamentals), `400_guides/400_11_deployments-ops-and-observability.md` (deployment/runbooks, health checks, monitoring), `400_guides/400_09_automation-and-pipelines.md` (migration/validation scripts, CI steps), `400_guides/400_10_security-compliance-and-access.md` (DB/users/permissions/security), `400_guides/400_08_integrations-editor-and-models.md` (integration touchpoints), and `400_guides/400_00_getting-started-and-index.md` (index). Implementation details live under `dspy-rag-system/` and `scripts/`.

## TL;DR

| what this file is | read when | do next |
|---|---|---|
| Deployment and production setup guide for the LTST Memory System | Setting up production environment or migrating to new system | Follow deployment checklist and run validation tests |

## Overview

This guide provides step-by-step instructions for deploying the LTST Memory System with database integration in production environments. The system includes advanced features like PostgreSQL function integration, session continuity detection, and performance monitoring.

## Prerequisites

### System Requirements

- **Python**: 3.12+
- **PostgreSQL**: 15+ with pgvector extension
- **Memory**: 4GB+ RAM (8GB+ recommended for production)
- **Storage**: 10GB+ available space
- **Network**: Stable database connectivity

### Database Requirements

- **pgvector Extension**: Version 0.5.0+ required
- **PostgreSQL Functions**: Context merging and memory rehydration functions
- **Connection Pooling**: Configured for production load
- **Backup Strategy**: Regular automated backups

## Deployment Checklist

### Phase 1: Environment Setup

- [ ] **Python Environment**
  - [ ] Install Python 3.12+
  - [ ] Create virtual environment
  - [ ] Install dependencies from `requirements.txt`
  - [ ] Verify pgvector support

- [ ] **Database Setup**
  - [ ] Install PostgreSQL 15+
  - [ ] Install pgvector extension
  - [ ] Create database and user
  - [ ] Apply schema migrations
  - [ ] Install PostgreSQL functions

- [ ] **Configuration**
  - [ ] Set environment variables
  - [ ] Configure database connection
  - [ ] Set up logging
  - [ ] Configure monitoring

### Phase 2: Schema Migration

- [ ] **Database Schema**
  - [ ] Apply `schema.sql` for core tables
  - [ ] Apply `context_merging_functions.sql`
  - [ ] Apply `memory_rehydration_functions.sql`
  - [ ] Verify all indexes are created
  - [ ] Test function availability

- [ ] **Data Migration** (if applicable)
  - [ ] Backup existing data
  - [ ] Migrate conversation data
  - [ ] Verify data integrity
  - [ ] Update any references

### Phase 3: System Validation

- [ ] **Integration Tests**
  - [ ] Run core integration tests
  - [ ] Verify database functions
  - [ ] Test performance benchmarks
  - [ ] Validate error handling

- [ ] **Production Readiness**
  - [ ] Load testing
  - [ ] Performance validation
  - [ ] Security review
  - [ ] Monitoring setup

## Detailed Deployment Steps

### 1. Environment Setup

#### Python Environment

```bash
# Install Python 3.12+
python3.12 --version

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify pgvector support
python3 scripts/check_pgvector_version.py
```

#### Database Setup

```bash
# Install PostgreSQL (macOS)
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Install pgvector extension
brew install pgvector

# Create database
createdb ai_agency

# Connect to database and install extension
psql ai_agency -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify pgvector version
psql ai_agency -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
```

#### Configuration

```bash
# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/ai_agency"
export LOG_LEVEL="INFO"
export MAX_CONNECTIONS="10"

# Create configuration file
cat > config/production.env << EOF
DATABASE_URL=postgresql://username:password@localhost:5432/ai_agency
LOG_LEVEL=INFO
MAX_CONNECTIONS=10
ENABLE_MONITORING=true
ENABLE_HEALTH_CHECKS=true
EOF
```

### 2. Schema Migration

#### Apply Core Schema

```bash
# Apply main schema
psql ai_agency -f config/database/schema.sql

# Verify tables created
psql ai_agency -c "\dt conversation_*"
```

#### Install PostgreSQL Functions

```bash
# Apply context merging functions
psql ai_agency -f config/database/context_merging_functions.sql

# Apply memory rehydration functions
psql ai_agency -f config/database/memory_rehydration_functions.sql

# Verify functions installed
psql ai_agency -c "\df merge_contexts_*"
psql ai_agency -c "\df rehydrate_memory_*"
```

#### Verify Indexes

```bash
# Check indexes
psql ai_agency -c "\di idx_conversation_*"

# Expected indexes:
# - idx_conversation_memory_session_id
# - idx_conversation_memory_user_id
# - idx_conversation_memory_embedding (HNSW)
# - idx_conversation_memory_relevance_score
```

### 3. System Validation

#### Run Integration Tests

```bash
# Run core integration tests
python3 tests/test_ltst_integration_core.py

# Expected output: 100% success rate
# Tests Run: 10
# Failures: 0
# Errors: 0
# Success Rate: 100.0%
```

#### Performance Validation

```bash
# Run performance benchmarks
python3 tests/test_ltst_end_to_end.py

# Expected performance:
# - Context Merging: < 50ms
# - Memory Rehydration: < 10ms
# - Session Continuity: < 5ms
```

#### Load Testing

```bash
# Run load tests (if available)
python3 scripts/load_test_ltst.py

# Monitor system resources during testing
# - CPU usage should remain reasonable
# - Memory usage should be stable
# - Database connections should be managed properly
```

## Production Configuration

### Environment Variables

```bash
# Required environment variables
DATABASE_URL=postgresql://username:password@host:port/database
LOG_LEVEL=INFO
MAX_CONNECTIONS=10

# Optional environment variables
ENABLE_MONITORING=true
ENABLE_HEALTH_CHECKS=true
CACHE_TTL=3600
MAX_CONTEXT_LENGTH=10000
RELEVANCE_THRESHOLD=0.7
```

### Database Configuration

#### PostgreSQL Settings

```sql
-- Recommended PostgreSQL settings for production
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

#### Connection Pooling

```python
# Configure connection pooling in your application
import psycopg2
from psycopg2 import pool

# Create connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host="localhost",
    database="ai_agency",
    user="username",
    password="password"
)
```

### Monitoring Setup

#### Health Checks

```python
# Health check endpoint
@app.route('/health')
def health_check():
    try:
        # Test database connection
        ltst_system = LTSTMemorySystem()
        health = ltst_system.get_system_health()

        return {
            'status': 'healthy',
            'database_connected': health.database_connected,
            'error_rate': health.error_rate,
            'total_operations': health.total_operations
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }, 500
```

#### Metrics Collection

```python
# Collect performance metrics
def collect_metrics():
    ltst_system = LTSTMemorySystem()

    # Get context statistics
    context_stats = ltst_system.database_integration.get_context_statistics()

    # Get rehydration statistics
    rehydration_stats = ltst_system.database_integration.get_rehydration_statistics()

    # Log metrics
    logger.info(f"Context stats: {context_stats}")
    logger.info(f"Rehydration stats: {rehydration_stats}")

    return {
        'context_stats': context_stats,
        'rehydration_stats': rehydration_stats
    }
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

**Symptoms**: "Database connection error: 0"

**Solutions**:
1. Verify database is running: `brew services list | grep postgresql`
2. Check connection string format
3. Verify user permissions: `psql ai_agency -c "\du"`
4. Test connection: `psql $DATABASE_URL -c "SELECT 1;"`

#### Function Not Found Errors

**Symptoms**: "function merge_contexts_intelligent does not exist"

**Solutions**:
1. Verify functions are installed: `psql ai_agency -c "\df merge_contexts_*"`
2. Reapply function files if missing
3. Check database schema: `psql ai_agency -c "\dt"`
4. Restart database connection

#### Performance Issues

**Symptoms**: Slow response times

**Solutions**:
1. Check database indexes: `psql ai_agency -c "\di idx_conversation_*"`
2. Monitor query performance: `psql ai_agency -c "EXPLAIN ANALYZE SELECT * FROM conversation_memory LIMIT 1;"`
3. Optimize relevance thresholds
4. Review cache settings

### Debugging Commands

```bash
# Check system status
python3 -c "
from utils.ltst_memory_system import LTSTMemorySystem
ltst = LTSTMemorySystem()
health = ltst.get_system_health()
print(f'Health: {health}')
"

# Test database functions
python3 -c "
from utils.ltst_database_integration import LTSTDatabaseIntegration
db = LTSTDatabaseIntegration()
result = db.test_database_functions()
print(f'Test results: {result}')
"

# Check pgvector version
python3 scripts/check_pgvector_version.py

# Validate schema
psql ai_agency -c "\dt conversation_*"
psql ai_agency -c "\df merge_contexts_*"
psql ai_agency -c "\df rehydrate_memory_*"
```

## Backup and Recovery

### Backup Strategy

```bash
# Create backup script
cat > scripts/backup_ltst.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/ltst"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump ai_agency > $BACKUP_DIR/ltst_backup_$DATE.sql

# Backup configuration
cp -r config $BACKUP_DIR/config_backup_$DATE

# Compress backup
tar -czf $BACKUP_DIR/ltst_backup_$DATE.tar.gz $BACKUP_DIR/ltst_backup_$DATE.sql $BACKUP_DIR/config_backup_$DATE

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "ltst_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/ltst_backup_$DATE.tar.gz"
EOF

chmod +x scripts/backup_ltst.sh
```

### Recovery Process

```bash
# Restore from backup
tar -xzf ltst_backup_YYYYMMDD_HHMMSS.tar.gz

# Restore database
psql ai_agency < ltst_backup_YYYYMMDD_HHMMSS.sql

# Restore configuration
cp -r config_backup_YYYYMMDD_HHMMSS/* config/

# Verify restoration
python3 tests/test_ltst_integration_core.py
```

## Security Considerations

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

## Performance Optimization

### Database Optimization

```sql
-- Analyze table statistics
ANALYZE conversation_memory;

-- Update table statistics
VACUUM ANALYZE conversation_memory;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'conversation_memory';
```

### Application Optimization

```python
# Configure connection pooling
from psycopg2 import pool

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=20,  # Adjust based on load
    host="localhost",
    database="ai_agency",
    user="ltst_user",
    password="secure_password"
)

# Use connection pooling in LTST system
ltst_system = LTSTMemorySystem(db_manager=connection_pool)
```

## Monitoring and Alerting

### Health Monitoring

```python
# Health check script
import time
import requests

def health_check():
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'healthy':
                print("✅ System healthy")
                return True
            else:
                print(f"❌ System unhealthy: {data}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

# Run health check every 5 minutes
while True:
    health_check()
    time.sleep(300)
```

### Performance Monitoring

```python
# Performance monitoring script
import time
from utils.ltst_memory_system import LTSTMemorySystem

def monitor_performance():
    ltst_system = LTSTMemorySystem()

    # Test context merging performance
    start_time = time.time()
    merge_result = ltst_system.merge_contexts_database("test_session")
    merge_time = time.time() - start_time

    # Test memory rehydration performance
    start_time = time.time()
    rehydration_result = ltst_system.rehydrate_memory_database("test_session", "test_user")
    rehydration_time = time.time() - start_time

    # Log performance metrics
    print(f"Context merging: {merge_time:.3f}s")
    print(f"Memory rehydration: {rehydration_time:.3f}s")

    # Alert if performance degrades
    if merge_time > 0.1:  # 100ms threshold
        print("⚠️ Context merging performance degraded")

    if rehydration_time > 0.05:  # 50ms threshold
        print("⚠️ Memory rehydration performance degraded")

# Run performance monitoring every hour
while True:
    monitor_performance()
    time.sleep(3600)
```

## Conclusion

The LTST Memory System deployment provides a robust, scalable solution for conversation memory management. The database integration layer offers significant performance improvements while maintaining full backward compatibility.

Key deployment benefits:
- **Performance**: Optimized database functions for fast execution
- **Scalability**: Connection pooling and efficient indexing
- **Reliability**: Comprehensive error handling and monitoring
- **Security**: Proper access controls and environment variable management
- **Monitoring**: Built-in health checks and performance metrics

For additional support, refer to the [LTST Memory System Integration Guide](./400_ltst-memory-system-integration-guide.md) for detailed API documentation and usage examples.
