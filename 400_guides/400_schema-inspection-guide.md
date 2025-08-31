# 🔍 Schema Inspection & Drift Detection Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Guide for using the repo-native schema inspection system | When working with database schemas or Pydantic models | Use the commands below to generate snapshots and check for drift |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Schema inspection system operational
- **Priority**: 🔧 Tool - Essential for schema management
- **Points**: 3 - Medium complexity, high value
- **Dependencies**: B-1053 Schema Inspection & Drift Detection
- **Next Steps**: Integrate into CI workflows

## 🚀 Quick Start

### Generate Schema Snapshots
```bash
# Generate both Pydantic and database schema snapshots
python3 scripts/validate_config.py --dump-schemas
```

### Check for Schema Drift
```bash
# Check if current schema differs from baseline
python3 scripts/system_health_check.py --schema-drift
```

### Update Baseline (After Intentional Changes)
```bash
# Update baseline with current schema
./scripts/update_schema_baseline.sh
```

## 📁 Schema Artifacts

All schema artifacts are stored in `dspy-rag-system/config/database/schemas/`:

- **`db_schema.snapshot.json`** - Current database schema snapshot
- **`db_schema.baseline.json`** - Baseline database schema (committed to git)
- **`pydantic_components.json`** - Combined Pydantic model schemas
- **`model_*.schema.json`** - Individual Pydantic model schemas

## 🔧 How It Works

### Schema Dumping
The system dumps schemas from two sources:

1. **Pydantic Models**: All models from `ragchecker_pydantic_models.py` and DSPy modules
2. **Database Schema**: Live PostgreSQL schema via SQLAlchemy introspection

### Drift Detection
Compares current snapshot against baseline using normalized JSON comparison:

```bash
# Drift detected
❌ Schema drift detected vs baseline. If intentional, update baseline.
   To update baseline: cp dspy-rag-system/config/database/schemas/db_schema.snapshot.json dspy-rag-system/config/database/schemas/db_schema.baseline.json

# No drift
✅ No schema drift detected.
```

## 🛠️ Integration with Existing Workflows

### Local Development
```bash
# Before committing schema changes
python3 scripts/validate_config.py --dump-schemas
python3 scripts/system_health_check.py --schema-drift

# If drift is intentional
./scripts/update_schema_baseline.sh
git add dspy-rag-system/config/database/schemas/db_schema.baseline.json
git commit -m "Update schema baseline"
```

### CI Integration
Add to existing GitHub Actions workflows:

```yaml
- name: Generate schema snapshots
  run: python3 scripts/validate_config.py --dump-schemas

- name: Schema drift check
  run: python3 scripts/system_health_check.py --schema-drift
```

## 🎯 Use Cases

### 1. Database Migration Safety
- Generate baseline before migration
- Run drift check after migration
- Catch unintended schema changes

### 2. Pydantic Model Validation
- Track model schema changes
- Ensure backward compatibility
- Validate RAGChecker inputs/outputs

### 3. RAG System Stability
- Prevent breaking changes to retrieval
- Maintain evaluation consistency
- Track vector store schema evolution

## 🔍 Troubleshooting

### Missing Baseline
```bash
ℹ️  Schema baseline or snapshot missing; run validate_config.py --dump-schemas to generate.
```

**Solution**: Generate initial baseline:
```bash
python3 scripts/validate_config.py --dump-schemas
cp dspy-rag-system/config/database/schemas/db_schema.snapshot.json dspy-rag-system/config/database/schemas/db_schema.baseline.json
```

### Import Errors
If you get import errors, ensure virtual environment is activated:
```bash
source venv/bin/activate
python3 scripts/validate_config.py --dump-schemas
```

### Database Connection Issues
Check PostgreSQL is running and environment variables are set:
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Verify connection
psql -d postgres -c "SELECT version();"
```

## 📊 Schema Coverage

### Pydantic Models Tracked
- **RAGChecker Models**: `RAGCheckerInput`, `RAGCheckerMetrics`, `RAGCheckerResult`
- **DSPy Context Models**: `BaseContext`, `PlannerContext`, `CoderContext`, `ResearcherContext`, `ImplementerContext`
- **Constitution Models**: `ConstitutionCompliance`, `ProgramOutput`
- **Error Models**: `PydanticError`, `ValidationError`

### Database Schema Tracked
- **Tables**: All tables in `public` schema
- **Columns**: Data types, nullability, primary/foreign keys
- **Indexes**: Index names, uniqueness, column lists
- **Relationships**: Foreign key references

## 🔗 Related Documentation

- [B-1054 Schema Inspection & Drift Detection](../000_core/000_backlog.md#p1-lane)
- [Database Troubleshooting Patterns](../100_memory/100_database-troubleshooting-patterns.md)
- [Development Workflow Guide](400_04_development-workflow-and-standards.md)
- [Quality Gates Guide](400_05_codebase-organization-patterns.md)

## 🎯 Success Metrics

- ✅ Schema snapshots generated successfully
- ✅ Drift detection catches intentional and unintentional changes
- ✅ Baseline management script works correctly
- ✅ Integration with existing CI workflows
- ✅ No new infrastructure dependencies added
