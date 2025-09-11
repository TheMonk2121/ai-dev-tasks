# Database Troubleshooting Patterns

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Codified database troubleshooting patterns and recovery procedures | When encountering database connection or DSPy system issues | Apply these patterns systematically; update based on new insights |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Database troubleshooting patterns maintained

- **Priority**: 🔥 Critical - Essential for system reliability

- **Points**: 5 - High importance for system stability

- **Dependencies**: 100_memory/100_cursor-memory-context.md

- **Next Steps**: Update based on successful troubleshooting patterns

## 🚨 **Recurring Database Issues Pattern**

### **1. PostgreSQL Service Issues**
**Pattern**: `postgresql@14 error` in brew services
**Symptoms**:
- `Error: failed to perform vector probe: pq: invalid input syntax for type vector`
- `Database connection error: 0`
- `No module named 'dspy_rag_system'`

**Recovery Steps**:
```bash
# 1. Check PostgreSQL status
brew services list | grep postgresql

# 2. Restart PostgreSQL service
brew services restart postgresql@14

# 3. Verify connection
psql -d postgres -c "SELECT version();"
```

### **2. Database Schema Issues**
**Pattern**: Missing required columns or tables
**Symptoms**:
- `Database schema issue: Requires 'start_char' column that doesn'tt exist`
- `Table doesn'tt exist yet`

**Recovery Steps**:
```bash
# 1. Apply clean slate schema
psql -d postgres -f dspy-rag-system/config/database/clean_slate_schema.sql

# 2. Add missing columns
psql -d postgres -c "ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS start_char INTEGER;"

# 3. Verify schema
psql -d postgres -c "\d document_chunks"
```

### **3. Vector Extension Issues**
**Pattern**: pgvector extension not properly installed
**Symptoms**:
- `pq: invalid input syntax for type vector`
- Vector operations failing

**Recovery Steps**:
```bash
# 1. Install vector extension
psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 2. Verify extension
psql -d postgres -c "\dx vector"
```

### **4. Python Path Issues**
**Pattern**: Module import failures
**Symptoms**:
- `No module named 'dspy_rag_system'`
- Import errors in system health checks

**Recovery Steps**:
```bash
# 1. Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/dspy-rag-system/src"

# 2. Verify imports
python3 -c "import dspy_rag_system; print('Import successful')"
```

### **5. Database Connection Configuration**
**Pattern**: Missing or incorrect connection strings
**Symptoms**:
- `Database connection error: 0`
- Connection timeouts

**Recovery Steps**:
```bash
# 1. Set connection string
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/postgres"

# 2. Test connection
psql -d postgres -c "SELECT 1;"
```

## 🔧 **Systematic Recovery Procedure**

### **Phase 1: Service Health Check**
```bash
# Check all services
brew services list | grep postgresql
psql -d postgres -c "SELECT version();"
```

### **Phase 2: Schema Validation**
```bash
# Apply schema
psql -d postgres -f dspy-rag-system/config/database/clean_slate_schema.sql

# Verify tables
psql -d postgres -c "\dt"
psql -d postgres -c "\d document_chunks"
```

### **Phase 3: Extension Verification**
```bash
# Install extensions
psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify extensions
psql -d postgres -c "\dx"
```

### **Phase 4: Environment Configuration**
```bash
# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/dspy-rag-system/src"
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/postgres"

# Test configuration
python3 -c "import dspy_rag_system; print('Configuration successful')"
```

### **Phase 5: Data Population**
```bash
# Populate database
cd dspy-rag-system && python3 bulk_add_core_documents.py

# Verify data
psql -d postgres -c "SELECT COUNT(*) FROM document_chunks;"
```

## 📊 **Success Metrics**

### **Recovery Effectiveness**
- **Service Status**: PostgreSQL running without errors
- **Schema Compliance**: All required tables and columns exis
- **Extension Status**: Vector extension properly installed
- **Connection Success**: Database queries execute without errors
- **Data Availability**: Document chunks populated in database

### **Troubleshooting Efficiency**
- **Time to Resolution**: <5 minutes for common issues
- **Pattern Recognition**: Identify issue type within 30 seconds
- **Recovery Success Rate**: >90% for documented patterns
- **Prevention**: Proactive monitoring prevents recurrence

## 🔄 **Prevention Strategies**

### **1. Automated Health Checks**
```bash
# Daily health check script
python3 scripts/system_health_check.py

# Pre-commit database validation
python3 scripts/database_sync_check.py
```

### **2. Environment Validation**
```bash
# Startup validation
python3 scripts/venv_manager.py --check
python3 -c "import dspy_rag_system; print('Environment OK')"
```

### **3. Configuration Management**
```bash
# Environment variable validation
echo $POSTGRES_DSN
echo $PYTHONPATH

# Configuration backup
cp dspy-rag-system/config/database/clean_slate_schema.sql backup/
```

## 🎯 **Application Guidelines**

### **When to Apply**
- **Database connection failures**
- **DSPy system startup issues**
- **Vector probe errors**
- **Module import failures**
- **Schema validation errors**

### **How to Apply**
1. **Identify pattern** from symptoms
2. **Follow recovery steps** systematically
3. **Verify resolution** with success metrics
4. **Update patterns** with new insights
5. **Document prevention** strategies

### **What to Avoid**
- **Guessing at solutions** without pattern recognition
- **Skipping verification steps** in recovery procedure
- **Ignoring prevention** after successful recovery
- **Not updating patterns** with new insights

## 📋 **Quick Reference**

### **Common Commands**
```bash
# Service managemen
brew services restart postgresql@14

# Schema managemen
psql -d postgres -f dspy-rag-system/config/database/clean_slate_schema.sql

# Environment setup
export PYTHONPATH="${PYTHONPATH}:$(pwd)/dspy-rag-system/src"
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/postgres"

# Health verification
psql -d postgres -c "SELECT COUNT(*) FROM document_chunks;"
```

### **Error Patterns**
- `pq: invalid input syntax for type vector` → Vector extension issue
- `Database connection error: 0` → Connection configuration issue
- `No module named 'dspy_rag_system'` → Python path issue
- `Table doesn'tt exist yet` → Schema issue

---

<!-- ANCHOR_KEY: database-troubleshooting -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->
<!-- LESSONS_APPLIED: ["100_memory/105_lessons-learned-context.md#database-reliability"] -->
<!-- REFERENCE_CARDS: ["500_reference-cards.md#database-troubleshooting"] -->
<!-- TECH_FOOTPRINT: Database Troubleshooting + PostgreSQL + Vector Extensions + Python Path + Environment Configuration -->
<!-- PROBLEM: Recurring database connection and DSPy system issues requiring systematic troubleshooting -->
<!-- OUTCOME: Comprehensive database troubleshooting patterns with systematic recovery procedures and prevention strategies -->
