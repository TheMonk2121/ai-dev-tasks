# Product Requirements Document: Complete HNSW Vector Index Migration

> ⚠️**Auto-Skip Note**> This PRD was generated because either `points≥5` or `score_total<3.0`.
> Remove this banner if you manually forced PRD creation.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Database**: PostgreSQL 15+ with pgvector 0.8.0 extension
- **Vector Indexing**: Mixed HNSW and IVFFlat indexes (need to standardize on HNSW)
- **Backend**: Python 3.12, DSPy RAG system, LTST Memory System
- **Development**: Local-first environment, solo developer workflow
- **Infrastructure**: PostgreSQL with vector extensions, local development setup

### Repository Layout
```
dspy-rag-system/
├── config/database/           # Database schema files
│   ├── schema.sql            # Current base schema (IVFFlat)
│   ├── clean_slate_schema.sql # HNSW-optimized schema
│   ├── vector_enhancement_schema.sql # Advanced vector features
│   └── ltst_memory_schema.sql # LTST system with HNSW
├── scripts/                   # Database migration scripts
│   ├── apply_clean_slate_schema.py
│   ├── apply_vector_enhancement.py
│   └── check_pgvector_version.py
├── src/                       # Main application code
│   ├── dspy_modules/         # DSPy vector store modules
│   └── utils/                # Database utilities
└── tests/                    # Database and vector store tests
```

### Development Patterns
- **Database migrations**: Use `scripts/apply_*.py` scripts with dry-run validation
- **Schema changes**: Update `config/database/*.sql` files, test with isolated environment
- **Vector operations**: Use `src/dspy_modules/vector_store.py` for vector operations
- **Performance testing**: Use `scripts/benchmark_vector_store.py` for validation

### Local Development
```bash
# Database setup
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"

# Check pgvector version
psql "$POSTGRES_DSN" -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"

# Apply schema migrations
python3 scripts/apply_clean_slate_schema.py --dry-run
python3 scripts/apply_clean_slate_schema.py

# Test vector operations
python3 scripts/benchmark_vector_store.py
```

### Common Tasks Cheat Sheet
- **Add vector index**: Schema file → Migration script → Dry-run → Apply → Validate
- **Optimize parameters**: Test different HNSW parameters → Benchmark → Document
- **Migrate indexes**: Backup → Drop old → Create new → Validate performance
- **Debug vector issues**: Check pgvector version → Validate indexes → Test queries

## 1. Problem Statement

### What's broken?
The database currently has mixed vector indexing strategies:
- **document_chunks** table: Uses HNSW index (good)
- **conversation_memory** table: Has both HNSW AND IVFFlat indexes (redundant)
- **Inconsistent performance**: IVFFlat provides inferior recall/latency trade-off compared to HNSW
- **Storage overhead**: Redundant indexes consume unnecessary disk space and maintenance overhead

### Why does it matter?
- **Performance impact**: IVFFlat indexes provide slower similarity search for small-to-medium datasets
- **Resource waste**: Redundant indexes consume disk space and slow down write operations
- **Maintenance complexity**: Mixed indexing strategies create confusion and potential for errors
- **Future scalability**: HNSW is the recommended approach for real-time vector search

### What's the opportunity?
- **Performance improvement**: HNSW provides better recall/latency trade-off than IVFFlat
- **Resource optimization**: Remove redundant indexes to save storage and improve write performance
- **Consistency**: Standardize on HNSW across all vector columns for predictable performance
- **Future-proofing**: HNSW is the industry standard for vector similarity search

## 2. Solution Overview

### What are we building?
A complete migration from mixed IVFFlat/HNSW indexing to pure HNSW indexing with optimized parameters across all vector columns in the database.

### How does it work?
1. **Audit current indexes**: Identify all vector indexes and their types
2. **Remove redundant IVFFlat**: Drop the redundant IVFFlat index on conversation_memory
3. **Optimize HNSW parameters**: Ensure all HNSW indexes use optimal parameters (m=16, ef_construction=64)
4. **Validate performance**: Benchmark vector search performance before and after
5. **Document migration**: Create clear documentation of the changes and their impact

### What are the key features?
- **Consistent HNSW indexing**: All vector columns use HNSW with optimal parameters
- **Performance validation**: Before/after benchmarks to quantify improvements
- **Safe migration**: Dry-run validation and rollback procedures
- **Documentation**: Clear migration guide and performance metrics

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] All vector indexes in the database use HNSW type
- [ ] No IVFFlat indexes remain on any vector columns
- [ ] HNSW parameters are optimized (m=16, ef_construction=64) for all indexes
- [ ] Vector search performance is validated with benchmarks
- [ ] Migration is documented with before/after metrics

### What does success look like?
- **Performance**: Vector similarity search queries show improved latency and recall
- **Consistency**: All vector operations use the same indexing strategy
- **Efficiency**: Reduced storage overhead from removed redundant indexes
- **Maintainability**: Clear documentation of the indexing strategy

### What are the quality gates?
- [ ] **Database integrity**: All existing data preserved during migration
- [ ] **Performance validation**: Vector search benchmarks show improvement or no regression
- [ ] **Index verification**: All vector columns have proper HNSW indexes
- [ ] **Documentation**: Migration process and results are documented

## 4. Technical Approach

### What technology?
- **Database**: PostgreSQL 15+ with pgvector 0.8.0 (already supports HNSW)
- **Migration tools**: Existing Python scripts in `scripts/` directory
- **Validation**: SQL queries and Python benchmarks for performance testing
- **Documentation**: Markdown files for migration guide and results

### How does it integrate?
- **Existing schema**: Works with current LTST Memory System schema
- **DSPy integration**: No changes needed to vector store modules
- **Application code**: Transparent to application layer (index changes are internal)
- **Monitoring**: Can use existing health check scripts to validate indexes

### What are the constraints?
- **pgvector version**: Requires pgvector ≥0.5.0 for HNSW support (already satisfied)
- **Data preservation**: Must not lose any existing vector data
- **Downtime**: Migration should be done during low-usage periods
- **Rollback**: Must be able to rollback if performance degrades

## 5. Risks and Mitigation

### What could go wrong?
- **Performance regression**: HNSW might perform worse than IVFFlat in some edge cases
- **Migration failure**: Database operations could fail during index changes
- **Data corruption**: Index recreation could potentially corrupt vector data
- **Application errors**: Code might have hardcoded expectations about index types

### How do we handle it?
- **Performance testing**: Comprehensive benchmarks before and after migration
- **Dry-run validation**: Test all migration steps in isolation first
- **Backup strategy**: Create database backup before any destructive operations
- **Rollback plan**: Document how to restore previous state if needed
- **Gradual migration**: Test on subset of data first if possible

### What are the unknowns?
- **Performance impact**: Exact performance improvement depends on query patterns
- **Index build time**: HNSW index creation time for large datasets
- **Memory usage**: HNSW memory requirements during index building

## 6. Testing Strategy

### What needs testing?
- **Index creation**: Verify HNSW indexes can be created successfully
- **Vector search**: Test similarity search performance and accuracy
- **Data integrity**: Ensure no data loss during index migration
- **Application compatibility**: Verify existing code works with new indexes

### How do we test it?
- **Unit tests**: Test individual migration steps in isolation
- **Integration tests**: Test complete migration workflow
- **Performance benchmarks**: Compare vector search performance before/after
- **Data validation**: Verify all vector data is preserved and accessible

### What's the coverage target?
- **Migration scripts**: 100% test coverage for all migration operations
- **Performance validation**: Benchmark all vector search operations
- **Data integrity**: Validate all existing vector data is preserved

## 7. Implementation Plan

### What are the phases?
1. **Audit and Planning** (0.5 hours): Document current state and plan migration
2. **Migration Execution** (1 hour): Remove redundant indexes and optimize HNSW
3. **Performance Validation** (1.5 hours): Benchmark and validate improvements
4. **Documentation** (1 hour): Document migration process and results

### What are the dependencies?
- **pgvector 0.8.0**: Already satisfied
- **Database access**: Need write permissions for index operations
- **Backup**: Create database backup before migration
- **Low usage period**: Schedule during minimal database activity

### What's the timeline?
- **Total estimated time**: 4 hours
- **Critical path**: Migration execution (1 hour)
- **Risk buffer**: 1 hour for unexpected issues
- **Validation time**: 1.5 hours for thorough performance testing

## 8. Task Breakdown

### Phase 1: Audit and Planning (0.5 hours)
- [ ] Document current vector indexes and their types
- [ ] Identify redundant IVFFlat indexes to remove
- [ ] Plan migration sequence and rollback strategy
- [ ] Create backup of current database state

### Phase 2: Migration Execution (1 hour)
- [ ] Remove redundant IVFFlat index on conversation_memory
- [ ] Verify all remaining indexes are HNSW with optimal parameters
- [ ] Test vector search functionality after migration
- [ ] Validate database integrity and data preservation

### Phase 3: Performance Validation (1.5 hours)
- [ ] Run comprehensive vector search benchmarks
- [ ] Compare performance metrics before and after migration
- [ ] Test edge cases and error conditions
- [ ] Validate application compatibility

### Phase 4: Documentation (1 hour)
- [ ] Document migration process and results
- [ ] Create performance comparison report
- [ ] Update relevant documentation files
- [ ] Create rollback procedures for future reference
