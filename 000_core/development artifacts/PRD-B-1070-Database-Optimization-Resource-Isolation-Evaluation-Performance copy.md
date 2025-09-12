# Product Requirements Document: Database Optimization & Resource Isolation for Evaluation Performance

> ⚠️**B-1070 Implementation**: This PRD defines the comprehensive database optimization and resource isolation strategy to eliminate evaluation/LTST workload contention and enable sub-5-minute RAGChecker evaluations with strict baseline protection.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Database**: PostgreSQL 14.18 (Homebrew), pgvector 0.8.0, 128GB RAM Mac M4
- **RAG Evaluation**: RAGChecker with AWS Bedrock, Phase-2 retrieval (coverage=0.152)
- **Memory Systems**: LTST Memory System, Unified Memory Orchestrator, conversation storage
- **Baselines**: Red-line protection (precision ≥ 0.159, recall ≥ 0.166, F1 ≥ 0.159)
- **Caching**: Separate `.ragcache_eval` vs `.ragcache_ltst` directories
- **Development**: Python 3.12, asyncpg, SQLAlchemy, Pyright, Ruff

### Repository Layout
```
ai-dev-tasks/
├── scripts/                           # Database utilities and evaluation
│   ├── ragchecker_official_evaluation.py
│   ├── unified_memory_orchestrator.py
│   └── pg_settings_snapshot.py
├── dspy-rag-system/                   # LTST core system
│   ├── src/utils/ltst_memory_system.py
│   ├── src/utils/conversation_storage.py
│   └── config/database/ltst_memory_schema.sql
├── metrics/                           # Performance artifacts
│   ├── baseline_evaluations/          # RAGChecker results
│   └── system_diagnostics/            # DB snapshots
├── src/common/                        # Shared utilities
│   └── db_dsn.py                      # DSN resolution
└── 000_core/000_backlog.md           # B-1070 tracking
```

### Development Patterns
- **DSN Resolution**: Unified `DATABASE_URL` with `POSTGRES_DSN` fallback
- **Connection Management**: Per-role GUCs, limited concurrency (2-3 workers)
- **Observability**: pg_stat_statements, query timing, resource monitoring
- **Safety**: Incremental tuning with rollback gates, baseline protection

### Local Developmen
```bash
# Environment setup
export DATABASE_URL="postgresql://danieljacobs@localhost:5432/ai_agency"

# Database health check
python3 scripts/healthcheck_db.py

# Take system snapsho
python3 scripts/pg_settings_snapshot.py
python3 scripts/vector_index_inventory.py

# Run baseline evaluation
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli
```

### Common Tasks
- **DSN Audit**: Scan repo for DATABASE_URL/POSTGRES_DSN usage patterns
- **Performance Tuning**: Incremental postgresql.conf optimization with rollback
- **Index Optimization**: pgvector HNSW parameter tuning and query-time controls
- **Workload Isolation**: Per-role GUCs and resource scheduling
- **Monitoring**: pg_stat_statements analysis and performance views

## 1. Problem Statement

### What's broken?
**Resource Contention Crisis**: LTST background jobs (memory rehydration, compaction, embeddings) are competing directly with $0.30 RAGChecker evaluations on a severely under-tuned PostgreSQL instance. Current state:
- PostgreSQL using <1% of 128GB RAM (shared_buffers=128MB, effective_cache_size=4GB)
- Mixed DSN usage across codebase (DATABASE_URL vs POSTGRES_DSN) causing connection fragmentation
- HNSW vector indexes using defaults (no m/ef_construction tuning for 384-dim embeddings)
- No workload isolation between LTST operations and evaluation queries
- No query performance monitoring (pg_stat_statements not enabled)

### Why does it matter?
**Evaluation Performance & Reliability Impact**:
- RAGChecker evaluations taking >5 minutes due to resource contention
- Baseline metrics at risk: precision 0.159, recall 0.166, F1 0.159 (near red-line floors)
- LTST memory operations causing unpredictable evaluation timing
- Under-utilized hardware (128GB RAM, SSD) leading to excessive disk I/O
- No visibility into query performance bottlenecks or resource usage patterns

### What's the opportunity?
**Performance & Isolation Transformation**:
- Achieve <5-minute evaluation target with zero workload interference
- Utilize 128GB RAM effectively (20-25% for shared_buffers, 75% for OS cache)
- Implement proper pgvector optimization for 384-dimensional embeddings
- Establish workload isolation without requiring separate database clusters
- Enable comprehensive performance monitoring and tuning capabilities
- Maintain strict baseline protection while improving system responsiveness

## 2. Solution Overview

### What are we building?
**Comprehensive Database Optimization & Resource Isolation System** with five progressive phases:
1. **DSN Unification & Observability**: Single connection standard + monitoring
2. **Connection Standardization**: Unified DSN resolver + startup health checks
3. **PostgreSQL Optimization**: Mac M4 + 128GB RAM tuning + pgvector optimization
4. **Workload Isolation**: Per-role GUCs + resource scheduling + cache separation
5. **Performance Monitoring**: Query tracking + resource monitoring + evaluation timing

### How does it work?
**Multi-Layered Optimization Strategy**:
- **DSN Resolution Layer**: Central resolver enforcing DATABASE_URL canonical with POSTGRES_DSN fallback
- **Connection Management**: Per-role database users (ltst_app, eval_app) with tailored GUCs
- **Memory Optimization**: Graduated tuning (8GB → 16GB → 24GB shared_buffers) with regression gates
- **Vector Performance**: Query-time hnsw.ef_search scaling + iterative_scan for 384-dim embeddings
- **Resource Isolation**: Separate cache directories + controlled LTST concurrency during evaluations
- **Monitoring & Safety**: pg_stat_statements + auto-snapshots + strict baseline protection

### What are the key features?
**Core Capabilities**:
- **Unified DSN Management**: Single source of truth for database connections across all components
- **Incremental Memory Tuning**: Safe progression with rollback gates and regression protection
- **pgvector Query Optimization**: Dynamic ef_search scaling and iterative_scan for filtered searches
- **Workload Role Isolation**: Per-role GUCs without requiring PgBouncer or separate clusters
- **Performance Visibility**: pg_stat_statements + custom monitoring views + timing instrumentation
- **Baseline Protection**: Automated red-line validation (precision/recall/F1) after each change
- **Cache Separation**: Dedicated `.ragcache_eval` vs `.ragcache_ltst` to prevent interference
- **Evidence-Driven Indexing**: Add JSONB/BTREE indexes only after pg_stat_statements confirms patterns

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] **DSN Unification Complete**: All components use unified resolver; no direct env reads
- [ ] **PostgreSQL Optimized**: Incremental tuning applied (Stage A/B/C) with snapshots
- [ ] **pgvector Enhanced**: Query-time controls implemented; HNSW parameters documented
- [ ] **Workload Isolation Active**: Per-role GUCs functional; cache separation enforced
- [ ] **Monitoring Operational**: pg_stat_statements + custom views + timing instrumentation
- [ ] **Baseline Protection Verified**: All red-line metrics maintained through optimization
- [ ] **Performance Target Met**: RAGChecker evaluations consistently <5 minutes
- [ ] **Documentation Complete**: All changes documented with rollback procedures

### What does success look like?
**Measurable Performance Outcomes**:
- **Evaluation Speed**: RAGChecker runs complete in <5 minutes (vs current >5 minutes)
- **Memory Utilization**: PostgreSQL using 20-30% of 128GB RAM effectively
- **Vector Performance**: HNSW queries <200ms p95 at K=16 with proper ef_search scaling
- **Workload Isolation**: Zero LTST interference during evaluations (measured via pg_stat_activity)
- **Baseline Compliance**: precision ≥ 0.159, recall ≥ 0.166, F1 ≥ 0.159 maintained throughou
- **Resource Monitoring**: pg_stat_statements providing actionable query performance insights

### What are the quality gates?
- [ ] **DSN Audit Clean**: `python3 scripts/dsn_repo_audit.py` shows unified usage
- [ ] **Health Check Passing**: `python3 scripts/healthcheck_db.py` validates configuration
- [ ] **Baseline Protection**: No regression in precision/recall/F1 after each tuning stage
- [ ] **Performance Monitoring**: pg_stat_statements capturing >90% query activity
- [ ] **Vector Optimization**: EXPLAIN ANALYZE showing improved HNSW performance
- [ ] **Isolation Verification**: No backend conflicts during concurrent LTST/eval operations

## 4. Technical Approach

### What technology?
**Stack and Core Components**:
- **PostgreSQL 14.18**: Core database with memory/WAL optimization for 128GB RAM
- **pgvector 0.8.0**: Vector similarity with HNSW optimization + iterative_scan
- **Python 3.12**: Application layer with asyncpg connection managemen
- **pg_stat_statements**: Query performance monitoring and optimization guidance
- **DSN Resolver**: Unified connection string management across all components
- **Per-Role GUCs**: Workload isolation via ALTER ROLE settings (work_mem, timeouts)

### How does it integrate?
**Integration Architecture**:
- **LTST Memory System**: Enhanced with unified DSN resolver + role-based connections
- **RAGChecker Integration**: Separate eval_app role + dedicated cache directory
- **Memory Orchestrator**: Maintains compatibility while using optimized connections
- **Development Workflow**: Health checks integrated into evaluation startup sequence
- **Monitoring Dashboard**: pg_stat_statements views accessible via existing tools
- **Baseline Protection**: Automated validation integrated into evaluation pipeline

### What are the constraints?
**Technical Limitations and Requirements**:
- **macOS Compatibility**: effective_io_concurrency=0, no huge_pages, LZ4 detection required
- **Homebrew PostgreSQL**: Config path `/opt/homebrew/var/postgres/postgresql.conf`
- **Memory Limits**: Incremental tuning to avoid overwhelming 128GB system
- **Baseline Red-Line**: Zero tolerance for precision/recall/F1 regression
- **Local-First**: No external dependencies (PgBouncer deferred until needed)
- **Rollback Requirement**: Every change must have documented 1-line rollback

## 5. Risks and Mitigation

### What could go wrong?
- **Risk 1**: Aggressive memory tuning causes macOS/Homebrew PostgreSQL instability
- **Risk 2**: pgvector optimization regresses recall below 0.166 red-line threshold
- **Risk 3**: DSN unification breaks existing LTST/evaluation workflows
- **Risk 4**: Role-based isolation insufficient without PgBouncer connection pooling
- **Risk 5**: pg_stat_statements overhead impacts evaluation performance

### How do we handle it?
- **Mitigation 1**: Incremental tuning (Stage A→B→C) with postgresql.conf.bak + restart rollback
- **Mitigation 2**: Baseline validation after every change; automatic revert on regression
- **Mitigation 3**: Phased DSN adoption starting with scripts; maintain fallback during transition
- **Mitigation 4**: Monitor pg_stat_activity for backend pressure; add PgBouncer if needed
- **Mitigation 5**: Measure pg_stat_statements overhead; disable if >2% performance impac

### What are the unknowns?
**Areas of Uncertainty**:
- **macOS Memory Limits**: How aggressive shared_buffers tuning can be on Homebrew builds
- **Vector Workload Patterns**: Actual ef_search requirements for filtered 384-dim queries
- **LTST Background Load**: Peak resource usage during memory rehydration/compaction
- **Cache Performance**: Impact of separate cache directories on SSD I/O patterns
- **Role Isolation Effectiveness**: Whether per-role GUCs provide sufficient workload separation

## 6. Testing Strategy

### What needs testing?
**Critical Testing Scenarios**:
- **DSN Resolution Testing**: All components correctly resolve unified DSN with fallback
- **Memory Tuning Validation**: Each postgresql.conf stage maintains baseline compliance
- **Vector Performance Testing**: HNSW queries with various ef_search values and filter patterns
- **Workload Isolation Testing**: Concurrent LTST operations + RAGChecker evaluations
- **Monitoring Accuracy Testing**: pg_stat_statements capturing representative query patterns
- **Rollback Testing**: Quick recovery from any optimization that causes regression

### How do we test it?
**Testing Methodology**:
- **Unit Testing**: DSN resolver, health check script, snapshot utilities with pytes
- **Integration Testing**: End-to-end evaluation runs with concurrent LTST operations
- **Performance Testing**: EXPLAIN ANALYZE on vector queries; pg_stat_statements analysis
- **Baseline Testing**: Automated precision/recall/F1 validation after each change
- **Load Testing**: Concurrent LTST memory operations during RAGChecker evaluation
- **Rollback Testing**: Verify postgresql.conf.bak restoration + service restar

### What's the coverage target?
**Testing Coverage Requirements**:
- **DSN Resolution**: 100% - All env combinations and fallback scenarios
- **Baseline Protection**: 100% - Every tuning change validated against red-line
- **Performance Monitoring**: 95% - pg_stat_statements capturing core query patterns
- **Vector Optimization**: 100% - All ef_search scaling scenarios tested
- **Workload Isolation**: 90% - Representative concurrent operation patterns
- **Rollback Procedures**: 100% - All changes tested for complete reversion

## 7. Implementation Plan

### What are the phases?
1. **Phase 1 - Discovery & Assessment** (4 hours): DSN audit, pg_settings snapshot, workload profiling, performance baseline measuremen
2. **Phase 2 - Connection Standardization** (3 hours): DSN resolver implementation, startup health check, connection unification
3. **Phase 3 - PostgreSQL Optimization** (6 hours): Incremental memory/WAL tuning (Stage A→B→C), pgvector query controls
4. **Phase 4 - Workload Isolation** (4 hours): Per-role GUCs, cache separation, resource scheduling
5. **Phase 5 - Performance Monitoring** (3 hours): pg_stat_statements, custom views, evaluation timing instrumentation

### What are the dependencies?
**Sequential Requirements**:
- **Phase 1 Prerequisites**: PostgreSQL operational, pgvector installed, baseline evaluation metrics
- **Phase 2 Prerequisites**: DSN audit complete, all connection points identified
- **Phase 3 Prerequisites**: Unified DSN resolver operational, health checks passing
- **Phase 4 Prerequisites**: PostgreSQL optimization stable, baseline metrics protected
- **Phase 5 Prerequisites**: Workload isolation functional, monitoring needs identified

### What's the timeline?
**Realistic Implementation Schedule**:
- **Total Implementation Time**: 20 hours across 5 phases
- **Phase 1**: 4 hours (Discovery & Assessment)
- **Phase 2**: 3 hours (Connection Standardization)
- **Phase 3**: 6 hours (PostgreSQL Optimization)
- **Phase 4**: 4 hours (Workload Isolation)
- **Phase 5**: 3 hours (Performance Monitoring)

**Daily Breakdown**:
- **Day 1**: Phase 1 complete + Phase 2 start (DSN audit, snapshots, resolver implementation)
- **Day 2**: Phase 2 complete + Phase 3 start (health checks, Stage A tuning)
- **Day 3**: Phase 3 complete (Stage B/C tuning, pgvector optimization)
- **Day 4**: Phase 4 complete (role isolation, cache separation)
- **Day 5**: Phase 5 complete + validation (monitoring, final testing)

---

## **Discovery & Baseline Summary**

> 📊 **Current System State (Phase 1 Discovery)**
> - **PostgreSQL**: 14.18 (Homebrew), shared_buffers=128MB, effective_cache_size=4GB
> - **Extensions**: vector 0.8.0, pg_trgm 1.6 (pg_stat_statements not installed)
> - **Vector Indexes**: HNSW on document_chunks (defaults), IVFFlat on conversation/doc chunks
> - **DSN Usage**: Mixed DATABASE_URL/POSTGRES_DSN across 15+ files
> - **Current Baseline**: precision 0.159, recall 0.166, F1 0.159 (at red-line floors)

> 🔍 **Implementation Decisions**
> - **DSN Standard**: DATABASE_URL canonical, POSTGRES_DSN temporary fallback
> - **Memory Strategy**: Incremental tuning (8GB→16GB→24GB) with regression gates
> - **Vector Optimization**: Query-time ef_search scaling, iterative_scan on 0.8.0
> - **Isolation Method**: Per-role GUCs (defer PgBouncer until backend pressure)
> - **Safety Protocol**: postgresql.conf.bak + baseline validation + rollback procedures

> 📈 **Target Performance Metrics**
> - **Evaluation Time**: <5 minutes (from current >5 minutes)
> - **Memory Utilization**: 20-30% of 128GB RAM (from current <1%)
> - **Vector Performance**: <200ms p95 for HNSW queries at K=16
> - **Baseline Protection**: precision ≥ 0.159, recall ≥ 0.166, F1 ≥ 0.159
> - **Workload Isolation**: Zero LTST interference during evaluations

> 🎯 **Success Criteria**
> - **DSN Unification**: All components using unified resolver
> - **Performance Optimization**: PostgreSQL utilizing available RAM effectively
> - **Vector Enhancement**: HNSW queries optimized with proper ef_search scaling
> - **Workload Separation**: LTST and evaluation operations properly isolated
> - **Monitoring Active**: pg_stat_statements providing actionable performance insights

> 🛡️ **Risk Mitigation**
> - **Incremental Tuning**: Stage A→B→C progression with rollback gates
> - **Baseline Protection**: Automated validation after every change
> - **Rollback Procedures**: postgresql.conf.bak + 1-line reversion for each change
> - **Local-First**: No external dependencies until proven necessary
> - **Evidence-Driven**: Add indexes only after pg_stat_statements confirms patterns
