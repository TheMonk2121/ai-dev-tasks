# Product Requirements Document: 5-Layer Memory System with Hybrid Rankers and Pruner

> ⚠️**Auto-Skip Note**> This PRD was generated because `points≥5` (18 days effort).
> Remove this banner if you manually forced PRD creation.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Backend**: Python 3.12, DSPy, PostgreSQL 15+ with pgvector extension
- **AI/ML**: Ollama (local models), sentence-transformers for embeddings
- **Database**: PostgreSQL with HNSW indexes, tsvector for BM25 search
- **Development**: Poetry, pytest, pre-commit, Ruff, Pyright
- **Infrastructure**: Local-first development, Docker for database
- **Memory System**: LTST (Long-Term Short-Term) with existing conversation_memory table

### Repository Layout
```
ai-dev-tasks/
├── dspy-rag-system/           # Main DSPy RAG system
│   ├── src/
│   │   ├── dspy_modules/      # DSPy components (model_switcher.py)
│   │   ├── utils/             # Utilities (memory_rehydrator.py, ltst_database_integration.py)
│   │   ├── monitoring/        # Health and metrics
│   │   └── cli/               # Command line tools
│   ├── config/database/       # SQL schemas and functions
│   ├── tests/                 # Test files
│   └── scripts/               # Development scripts
├── scripts/                   # Project-wide scripts (memory_up.sh, memory_rehydrate.py)
├── 000_core/                  # Core documentation and workflows
├── 100_memory/                # Memory system documentation
└── 400_guides/                # Implementation guides
```

### Development Patterns
- **Add database table**: `dspy-rag-system/config/database/` → add DDL → add migration script
- **Add DSPy module**: `dspy-rag-system/src/dspy_modules/` → add module → add tests
- **Add utility function**: `dspy-rag-system/src/utils/` → add function → add tests
- **Add SQL function**: `dspy-rag-system/config/database/` → add function → add tests
- **Update memory system**: `dspy-rag-system/src/utils/` → modify memory_rehydrator.py → update tests

### Local Development
```bash
# Setup
cd dspy-rag-system
poetry install
poetry run pre-commit install

# Database setup
docker-compose up -d postgres
poetry run python scripts/apply_clean_slate_schema.py

# Run tests
poetry run pytest tests/
poetry run python -m pytest tests/test_memory_system.py -v

# Quality gates
poetry run ruff check .        # Lint code
poetry run pyright .           # Type check
poetry run pytest --cov=src   # Test coverage
```

### Common Tasks Cheat Sheet
- **Add new memory layer**: Database table → SQL functions → Python integration → Tests
- **Modify ranking algorithm**: Update SQL function → Update Python wrapper → Test performance
- **Add new DSPy component**: Module → Integration → Tests → Documentation
- **Database migration**: DDL script → Apply → Test → Update documentation
- **Performance optimization**: Profile → Optimize → Benchmark → Document

## 1. Problem Statement

### What's broken?
Our current LTST memory system uses a simple ranking formula (`priority_score = (relevance_score * 0.7) + (recency_score * 0.3)`) that doesn't leverage the full potential of modern retrieval techniques. The system lacks:
- **Sophisticated ranking**: No BM25 lexical search or hybrid ranking
- **Intelligent pruning**: No audit trails or usage-based eviction
- **Entity management**: No versioning or contradiction handling for facts
- **Multi-layer architecture**: Single memory layer instead of specialized layers

### Why does it matter?
The current system limits our AI development ecosystem's ability to:
- Provide contextually relevant information from conversation history
- Maintain high-quality, non-contradictory entity facts
- Scale efficiently with intelligent memory management
- Leverage different types of memory for different use cases

### What's the opportunity?
Implementing a 5-layer memory system with hybrid rankers will:
- **Improve context relevance** by 40-60% through hybrid ranking (cosine + BM25 + recency)
- **Reduce memory bloat** by 70% through intelligent pruning with audit trails
- **Enhance entity accuracy** through versioning and contradiction detection
- **Enable specialized memory layers** for different types of information

## 2. Solution Overview

### What are we building?
A sophisticated 5-layer memory system that enhances our existing LTST memory with:
1. **Turn Buffer** (FIFO) - Short-term memory for recent interactions
2. **Rolling Summary** - Compact, continually updated conversation summaries
3. **Entity/Fact Store** - Structured key-value records with versioning
4. **Episodic Memory** - Sparse log of important events and decisions
5. **Semantic Index** - Chunks with embeddings for long-term recall

### How does it work?
The system uses hybrid ranking combining:
- **Cosine similarity** (55%) - Semantic similarity via embeddings
- **BM25 lexical search** (25%) - Keyword matching via PostgreSQL tsvector
- **Recency weighting** (20%) - Time-based decay with 14-day half-life

Intelligent pruning removes low-value content based on:
- **Hard expiration** - Respects explicit expiration dates
- **Age-based eviction** - Removes old, low-usage, low-salience content
- **Audit trails** - Complete history of what was pruned and why

### What are the key features?
- **Hybrid ranking** with configurable weights and thresholds
- **Intelligent pruning** with audit logs and usage tracking
- **Entity fact versioning** with contradiction detection
- **Diversity filtering** to avoid redundant context
- **Token capping** to respect model context limits
- **Performance monitoring** with query timing and hit rates

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] All 5 database tables created with proper indexes
- [ ] Hybrid ranking function returns results in < 500ms
- [ ] Pruner removes 70% of low-value content while preserving important items
- [ ] UPSERT helpers handle entity fact versioning correctly
- [ ] `build_context()` function integrates with existing LTST system
- [ ] Performance within acceptable limits (< 2s total context retrieval)

### What does success look like?
- **Context relevance improvement**: 40-60% better retrieval accuracy
- **Memory efficiency**: 70% reduction in storage bloat
- **Entity accuracy**: 95%+ consistency in fact management
- **Performance**: < 2s context retrieval time
- **Integration**: Seamless operation with existing DSPy components

### What are the quality gates?
- **Test coverage**: > 90% for all new components
- **Performance**: Hybrid ranking < 500ms, total context < 2s
- **Database**: All indexes created, functions working
- **Integration**: Existing memory system continues to function
- **Documentation**: Complete API documentation and usage examples

## 4. Technical Approach

### What technology?
- **Database**: PostgreSQL 15+ with pgvector extension for HNSW indexes
- **Search**: PostgreSQL tsvector for BM25 lexical search
- **Embeddings**: sentence-transformers (384-dimensional vectors)
- **Python**: Async/await for database operations
- **Integration**: Extend existing LTST memory system

### How does it integrate?
- **Extends LTST**: Builds on existing `conversation_memory` table
- **DSPy integration**: Updates `memory_rehydrator.py` and `model_switcher.py`
- **Database layer**: New tables alongside existing schema
- **Performance layer**: Integrates with existing caching and optimization

### What are the constraints?
- **Backward compatibility**: Must not break existing LTST functionality
- **Performance**: Must maintain < 2s context retrieval time
- **Storage**: Must fit within existing database constraints
- **Local-first**: Must work in local development environment
- **DSPy compatibility**: Must integrate with existing DSPy modules

## 5. Risks and Mitigation

### What could go wrong?
- **Performance degradation**: New hybrid ranking could be slower
- **Data inconsistency**: Complex UPSERT operations could corrupt data
- **Integration complexity**: Changes to existing memory system could break functionality
- **Storage bloat**: New tables could grow too large
- **Ranking quality**: Hybrid weights might not work well for our use case

### How do we handle it?
- **Performance**: Extensive benchmarking and optimization
- **Data consistency**: Transaction-based operations with rollback capability
- **Integration**: Gradual rollout with feature flags
- **Storage**: Intelligent pruning with configurable thresholds
- **Ranking quality**: A/B testing with different weight configurations

### What are the unknowns?
- **Optimal hybrid weights**: May need tuning based on actual usage
- **Pruning thresholds**: Best values for age, access count, and salience
- **Diversity filtering**: Optimal cosine similarity threshold
- **Token distribution**: How to best allocate tokens across 5 layers

## 6. Testing Strategy

### What needs testing?
- **Database functions**: All SQL functions with various input scenarios
- **Hybrid ranking**: Accuracy and performance across different query types
- **Pruning logic**: Correct eviction of low-value content
- **Entity versioning**: Proper handling of fact updates and contradictions
- **Integration**: End-to-end context retrieval workflow
- **Performance**: Query timing and resource usage

### How do we test it?
- **Unit tests**: Individual components with mocked dependencies
- **Integration tests**: Database operations with test data
- **Performance tests**: Load testing with realistic query patterns
- **A/B tests**: Compare new vs. old ranking accuracy
- **End-to-end tests**: Full context retrieval workflow

### What's the coverage target?
- **Code coverage**: > 90% for all new Python code
- **Function coverage**: 100% for all SQL functions
- **Integration coverage**: All major workflow paths
- **Performance coverage**: All critical performance scenarios

## 7. Implementation Plan

### What are the phases?
1. **Phase 1: Database Schema** (2 days) - Create all tables and indexes
2. **Phase 2: Hybrid Ranking** (4 days) - Implement ranking functions
3. **Phase 3: Pruner** (4 days) - Build intelligent eviction system
4. **Phase 4: UPSERT Helpers** (2 days) - Entity fact management
5. **Phase 5: Python Integration** (4 days) - `build_context()` function
6. **Phase 6: Integration & Testing** (6 days) - Full system integration

### What are the dependencies?
- **Phase 1**: No dependencies, can start immediately
- **Phase 2**: Requires Phase 1 database schema
- **Phase 3**: Requires Phase 2 ranking functions
- **Phase 4**: Can run in parallel with Phase 3
- **Phase 5**: Requires Phases 2-4 to be complete
- **Phase 6**: Requires all previous phases

### What's the timeline?
- **Total duration**: 18 days
- **Critical path**: Phases 1 → 2 → 5 → 6 (16 days)
- **Parallel work**: Phases 3 and 4 can run concurrently
- **Testing**: Integrated throughout all phases
- **Documentation**: Updated continuously

### Success Metrics
- **Technical**: All acceptance criteria met
- **Performance**: < 2s context retrieval, < 500ms ranking
- **Quality**: > 90% test coverage, no regressions
- **Integration**: Seamless operation with existing system
- **User experience**: Improved context relevance and system responsiveness
