<!-- ANCHOR_KEY: prd-b-1015-ltst-memory-system-database-optimization -->
<!-- ANCHOR_PRIORITY: 35 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->
<!-- Backlog ID: B-1015 -->
<!-- Status: todo -->
<!-- Priority: High -->
<!-- Dependencies: B-1012 -->
<!-- Version: 1.0 -->
<!-- Date: 2025-01-23 -->

# Product Requirements Document: B-1015 LTST Memory System Database Optimization

> ⚠️**Auto-Skip Note**> This PRD was generated because either `points≥5` or `score_total<3.0`.
> Remove this banner if you manually forced PRD creation.

## 1. Problem Statement

### What's broken?
The current LTST (Long-Term Short-Term) memory system lacks several critical capabilities that limit its effectiveness and scalability:

1. **No semantic search**: Conversation memory isn't semantically searchable, making it difficult to find relevant past conversations
2. **Schema fragmentation**: DSPy tables (`dspy_signatures`, `dspy_examples`) are created in Python code rather than the canonical `schema.sql`, breaking environment reproducibility
3. **Missing user/session hygiene**: Only has `session_id` without `user_id`, limiting future multi-tenant support
4. **No retention policy**: LTST can bloat over time without any cleanup mechanism
5. **Suboptimal indexing**: Uses IVFFlat instead of HNSW for vector search, limiting recall/latency performance

### Why does it matter?
- **Context loss**: AI agents can't semantically recall relevant past conversations
- **Environment drift**: New environments require running Python first to get proper schema
- **Scalability limits**: No path to multi-tenant support without breaking changes
- **Performance degradation**: System slows down as conversation history grows
- **Governance violation**: Current approach doesn'tt align with "local-first, simple" principles

### What's the opportunity?
Implement governance-aligned improvements that enhance semantic search capabilities, ensure environment reproducibility, future-proof for multi-tenant support, and provide manual cleanup options while maintaining the project's "local-first, simple" philosophy.

## 2. Solution Overview

### What are we building?
A comprehensive database optimization for the LTST memory system that enhances semantic search, promotes schema reproducibility, adds user/session hygiene, and implements governance-aligned retention policies.

### How does it work?
1. **HNSW Semantic Search**: Replace IVFFlat with HNSW index for better recall/latency at small-to-mid scale
2. **Schema Promotion**: Move DSPy tables from Python code to `schema.sql` for environment reproducibility
3. **User/Session Hygiene**: Add nullable `user_id` column for future multi-tenant support
4. **Manual Cleanup**: Implement PostgreSQL function for on-demand conversation cleanup

### What are the key features?
- **Semantic conversation recall**: HNSW index enables finding relevant past conversations
- **Reproducible environments**: Fresh clone + `psql -f schema.sql` is sufficien
- **Future-proof architecture**: User_id column ready for multi-tenant scenarios
- **Governance-aligned retention**: Manual cleanup function, no automated jobs

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] HNSW index replaces IVFFlat on `conversation_memory.embedding` with vector_cosine_ops
- [ ] DSPy tables (`dspy_signatures`, `dspy_examples`) exist in `schema.sql` with proper indexes
- [ ] `user_id VARCHAR(255)` column added to `conversation_memory` table
- [ ] `cleanup_old_conversation_memory(days_to_keep)` function implemented and tested
- [ ] All changes applied to `dspy-rag-system/config/database/schema.sql`
- [ ] Python helper `ensure_chat_embeddings.py` created for lazy embedding backfill

### What does success look like?
- **Semantic search**: Can find relevant past conversations using vector similarity
- **Environment reproducibility**: New environments work with just `psql -f schema.sql`
- **Future readiness**: User_id column available for multi-tenant scenarios
- **Governance compliance**: Manual cleanup available, no automated jobs
- **Performance**: HNSW provides better recall/latency than IVFFla

### What are the quality gates?
- [ ] All SQL migrations are idempotent (use `IF NOT EXISTS`)
- [ ] No breaking changes to existing conversation_memory data
- [ ] Manual cleanup function works without side effects
- [ ] Lazy embedding backfill doesn'tt impact performance
- [ ] All changes align with local-first, simple governance principles

## 4. Technical Approach

### What technology?
- **Database**: PostgreSQL with pgvector extension (≥0.5 for HNSW support)
- **Vector indexing**: HNSW with m=16, ef_construction=64 parameters
- **Schema management**: DDL statements in `schema.sql`
- **Python integration**: Helper script for lazy embedding computation

### How does it integrate?
- **Schema.sql**: All DDL statements added to canonical schema file
- **Conversation storage**: Existing `conversation_storage.py` updated for new columns
- **Memory rehydrator**: Enhanced with semantic search capabilities
- **DSPy integration**: Tables available for signature and example storage

### What are the constraints?
- **pgvector version**: Requires ≥0.5 for HNSW support
- **Backward compatibility**: Must not break existing conversation data
- **Local-first**: No automated jobs, manual cleanup only
- **Simple approach**: Minimal surface area, no over-engineering

## 5. Risks and Mitigation

### What could go wrong?
- **pgvector version mismatch**: HNSW requires pgvector ≥0.5
  - **Mitigation**: Check version in setup and provide fallback to IVFFla
- **Performance regression**: HNSW construction might be slower
  - **Mitigation**: Use conservative parameters (m=16, ef_construction=64)
- **Data migration issues**: Adding columns to existing table
  - **Mitigation**: Use `ADD COLUMN IF NOT EXISTS` for idempotency
- **Embedding computation overhead**: Lazy backfill might be slow
  - **Mitigation**: Process only when needed, provide progress feedback

### How do we handle it?
- **Version checking**: Validate pgvector version before HNSW creation
- **Graceful degradation**: Fall back to IVFFlat if HNSW unavailable
- **Idempotent migrations**: All DDL uses `IF NOT EXISTS` patterns
- **Incremental processing**: Lazy embedding computation with progress tracking

### What are the unknowns?
- **HNSW performance**: Actual recall/latency improvement in our data
- **Embedding quality**: How well conversation embeddings capture semantic meaning
- **Cleanup frequency**: How often manual cleanup will be needed
- **Multi-tenant timeline**: When user_id will actually be used

## 6. Testing Strategy

### What needs testing?
- **Schema migrations**: All DDL statements work correctly
- **HNSW indexing**: Vector search performance and accuracy
- **DSPy table integration**: Signature and example storage/retrieval
- **Cleanup function**: Manual cleanup works without data loss
- **Backward compatibility**: Existing data remains accessible

### How do we test it?
- **Unit tests**: Test each migration statement individually
- **Integration tests**: Full schema application and verification
- **Performance tests**: Compare HNSW vs IVFFlat recall/latency
- **Data integrity tests**: Verify cleanup function preserves data integrity
- **Backward compatibility tests**: Ensure existing queries still work

### What's the coverage target?
- **Schema coverage**: 100% of new DDL statements tested
- **Function coverage**: 100% of cleanup function code paths
- **Integration coverage**: Full end-to-end schema application
- **Performance coverage**: HNSW vs IVFFlat benchmark comparison

## 7. Implementation Plan

### What are the phases?
1. **Phase 1**: Schema preparation and validation (2 hours)
   - Validate pgvector version compatibility
   - Prepare all DDL statements with idempotent patterns
   - Test schema application in isolated environmen

2. **Phase 2**: Core schema implementation (3 hours)
   - Add embedding column to conversation_memory
   - Create HNSW index with optimal parameters
   - Promote DSPy tables to schema.sql
   - Add user_id column for future support

3. **Phase 3**: Cleanup and helper implementation (2 hours)
   - Implement manual cleanup function
   - Create Python helper for lazy embedding backfill
   - Add comprehensive error handling

4. **Phase 4**: Testing and validation (1 hour)
   - Run full test suite
   - Verify backward compatibility
   - Performance benchmarking

### What are the dependencies?
- **B-1012**: LTST Memory System (foundation)
- **pgvector ≥0.5**: Required for HNSW support
- **Existing schema.sql**: Target for DDL additions
- **conversation_storage.py**: Integration point for new columns

### What's the timeline?
- **Total effort**: 8 hours (matches backlog estimate)
- **Phase 1**: Day 1 (2 hours)
- **Phase 2**: Day 1-2 (3 hours)
- **Phase 3**: Day 2 (2 hours)
- **Phase 4**: Day 2 (1 hour)
- **Risk buffer**: 2 hours for unexpected issues

## 8. Governance Alignmen

### Local-First Principles
- **Manual cleanup**: No automated jobs, user controls when to clean
- **Simple approach**: Minimal surface area, no over-engineering
- **Reproducible**: Environment setup requires only schema.sql
- **Future-proof**: User_id ready for multi-tenant without breaking changes

### Technical Constraints
- **No new dependencies**: Uses existing pgvector and PostgreSQL
- **Backward compatible**: Existing data and queries continue working
- **Idempotent migrations**: Safe to run multiple times
- **Performance conscious**: HNSW parameters optimized for small-to-mid scale

### Success Metrics
- **Semantic search capability**: Can find relevant past conversations
- **Environment reproducibility**: Fresh clone works with just schema.sql
- **Governance compliance**: All changes align with local-first, simple principles
- **Performance improvement**: HNSW provides better recall/latency than IVFFla
