# Task List: B-1015 LTST Memory System Database Optimization

## Overview

Implement governance-aligned improvements to the LTST (Long-Term Short-Term) memory system including HNSW semantic search enhancement, DSPy tables promotion to schema.sql, user/session hygiene with nullable user_id, and manual cleanup function for local-first retention policy.

**Backlog ID**: B-1015
**Priority**: High
**Estimated Effort**: 8 hours
**Dependencies**: B-1012 LTST Memory System

## Implementation Phases

### Phase 1: Schema Preparation and Validation (2 hours)

#### Task 1.1: Validate pgvector Version Compatibility
**Priority:** Critical
**Estimated Time:** 0.5 hours
**Dependencies:** None
**Description:** Verify pgvector extension version supports HNSW indexing (≥0.5) and prepare fallback strategy
**Acceptance Criteria:**
- [ ] pgvector version check script created and tested
- [ ] HNSW support validated in current environmen
- [ ] Fallback to IVFFlat strategy documented if HNSW unavailable
- [ ] Version requirements documented in setup guide

**Testing Requirements:**
- [ ] **Unit Tests**: pgvector version detection and validation
- [ ] **Integration Tests**: HNSW index creation test with current pgvector
- [ ] **Edge Case Tests**: Handle missing pgvector extension gracefully
- [ ] **Error Handling Tests**: Proper error messages for version mismatches

**Implementation Notes:** Create utility function to check pgvector version and HNSW support before proceeding with schema changes.

**Quality Gates:**
- [ ] **Code Review**: Version checking logic reviewed
- [ ] **Tests Passing**: All version validation tests pass
- [ ] **Documentation Updated**: pgvector requirements documented

#### Task 1.2: Prepare DDL Statements with Idempotent Patterns
**Priority:** Critical
**Estimated Time:** 1 hour
**Dependencies:** Task 1.1
**Description:** Create all DDL statements using `IF NOT EXISTS` patterns for safe, repeatable execution
**Acceptance Criteria:**
- [ ] All ALTER TABLE statements use `ADD COLUMN IF NOT EXISTS`
- [ ] All CREATE INDEX statements use `CREATE INDEX IF NOT EXISTS`
- [ ] All CREATE TABLE statements use `CREATE TABLE IF NOT EXISTS`
- [ ] All CREATE FUNCTION statements use `CREATE OR REPLACE FUNCTION`
- [ ] DDL statements tested for idempotency

**Testing Requirements:**
- [ ] **Unit Tests**: Each DDL statement tested individually
- [ ] **Integration Tests**: Full schema application multiple times
- [ ] **Edge Case Tests**: Handle existing columns/indexes gracefully
- [ ] **Error Handling Tests**: Proper error messages for constraint violations

**Implementation Notes:** Use PostgreSQL's `IF NOT EXISTS` clauses to ensure safe execution even if objects already exist.

**Quality Gates:**
- [ ] **Code Review**: DDL statements reviewed for safety
- [ ] **Tests Passing**: All idempotency tests pass
- [ ] **Documentation Updated**: Schema migration procedures documented

#### Task 1.3: Test Schema Application in Isolated Environmen
**Priority:** High
**Estimated Time:** 0.5 hours
**Dependencies:** Task 1.2
**Description:** Validate complete schema application in isolated test environmen
**Acceptance Criteria:**
- [ ] Fresh database created for testing
- [ ] All DDL statements applied successfully
- [ ] No errors or warnings during schema creation
- [ ] All new objects (columns, indexes, functions) verified
- [ ] Rollback procedure tested and documented

**Testing Requirements:**
- [ ] **Integration Tests**: Complete schema application workflow
- [ ] **Performance Tests**: Schema creation time measured
- [ ] **Error Handling Tests**: Graceful handling of any failures
- [ ] **Rollback Tests**: Clean rollback procedure verified

**Implementation Notes:** Use Docker or isolated database instance to test schema changes without affecting development environment.

**Quality Gates:**
- [ ] **Code Review**: Schema application process reviewed
- [ ] **Tests Passing**: All schema application tests pass
- [ ] **Documentation Updated**: Test procedures documented

### Phase 2: Core Schema Implementation (3 hours)

#### Task 2.1: Add Embedding Column to conversation_memory
**Priority:** Critical
**Estimated Time:** 0.5 hours
**Dependencies:** Task 1.3
**Description:** Add VECTOR(384) embedding column to conversation_memory table for semantic search
**Acceptance Criteria:**
- [ ] `embedding VECTOR(384)` column added to conversation_memory table
- [ ] Column allows NULL values for existing records
- [ ] No data loss or corruption during migration
- [ ] Column properly indexed for vector operations

**Testing Requirements:**
- [ ] **Unit Tests**: Column creation and data integrity
- [ ] **Integration Tests**: Existing conversation data preserved
- [ ] **Performance Tests**: Column addition doesn'tt impact existing queries
- [ ] **Data Integrity Tests**: Verify no data corruption during migration

**Implementation Notes:** Use `ADD COLUMN IF NOT EXISTS embedding VECTOR(384)` to safely add the column.

**Quality Gates:**
- [ ] **Code Review**: Column addition logic reviewed
- [ ] **Tests Passing**: All data integrity tests pass
- [ ] **Performance Validated**: No performance regression on existing queries

#### Task 2.2: Create HNSW Index with Optimal Parameters
**Priority:** Critical
**Estimated Time:** 1 hour
**Dependencies:** Task 2.1
**Description:** Replace IVFFlat with HNSW index for better recall/latency at small-to-mid scale
**Acceptance Criteria:**
- [ ] HNSW index created on conversation_memory.embedding
- [ ] Index uses vector_cosine_ops for similarity search
- [ ] Parameters optimized: m=16, ef_construction=64
- [ ] Index creation time measured and documented
- [ ] Performance improvement over IVFFlat validated

**Testing Requirements:**
- [ ] **Unit Tests**: Index creation and basic operations
- [ ] **Performance Tests**: HNSW vs IVFFlat benchmark comparison
- [ ] **Integration Tests**: Vector similarity search functionality
- [ ] **Edge Case Tests**: Handle empty embedding vectors gracefully

**Implementation Notes:** Use `CREATE INDEX IF NOT EXISTS idx_cm_embedding_hnsw ON conversation_memory USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)`

**Quality Gates:**
- [ ] **Code Review**: Index creation parameters reviewed
- [ ] **Tests Passing**: All vector search tests pass
- [ ] **Performance Validated**: HNSW outperforms IVFFlat in benchmarks

#### Task 2.3: Promote DSPy Tables to schema.sql
**Priority:** High
**Estimated Time:** 1 hour
**Dependencies:** Task 2.2
**Description:** Move dspy_signatures and dspy_examples tables from Python code to schema.sql for environment reproducibility
**Acceptance Criteria:**
- [ ] dspy_signatures table created in schema.sql with proper structure
- [ ] dspy_examples table created in schema.sql with foreign key to signatures
- [ ] All necessary indexes created (signature_name, signature_id, quality_score)
- [ ] Tables support existing DSPy functionality
- [ ] Environment reproducibility verified (fresh clone + psql -f schema.sql works)

**Testing Requirements:**
- [ ] **Unit Tests**: Table creation and basic CRUD operations
- [ ] **Integration Tests**: DSPy signature and example storage/retrieval
- [ ] **Performance Tests**: Index performance on signature lookups
- [ ] **Data Integrity Tests**: Foreign key constraints and cascading deletes

**Implementation Notes:** Include proper foreign key constraints and indexes for optimal performance.

**Quality Gates:**
- [ ] **Code Review**: Table schemas and relationships reviewed
- [ ] **Tests Passing**: All DSPy integration tests pass
- [ ] **Documentation Updated**: Schema.sql updated with new tables

#### Task 2.4: Add user_id Column for Future Multi-tenant Suppor
**Priority:** Medium
**Estimated Time:** 0.5 hours
**Dependencies:** Task 2.3
**Description:** Add nullable user_id column to conversation_memory for future multi-tenant scenarios
**Acceptance Criteria:**
- [ ] `user_id VARCHAR(255)` column added to conversation_memory
- [ ] Column allows NULL values (single-user current state)
- [ ] No breaking changes to existing functionality
- [ ] Column ready for future indexing when multi-tenant is enabled

**Testing Requirements:**
- [ ] **Unit Tests**: Column addition and data integrity
- [ ] **Integration Tests**: Existing conversation queries still work
- [ ] **Backward Compatibility Tests**: No impact on current single-user functionality
- [ ] **Future Readiness Tests**: Column can be indexed when needed

**Implementation Notes:** Use `ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)` - no index yet to keep it simple.

**Quality Gates:**
- [ ] **Code Review**: Column addition reviewed for future compatibility
- [ ] **Tests Passing**: All backward compatibility tests pass
- [ ] **Documentation Updated**: Multi-tenant readiness documented

### Phase 3: Cleanup and Helper Implementation (2 hours)

#### Task 3.1: Implement Manual Cleanup Function
**Priority:** High
**Estimated Time:** 1 hour
**Dependencies:** Task 2.4
**Description:** Create PostgreSQL function for on-demand conversation cleanup without automated jobs
**Acceptance Criteria:**
- [ ] `cleanup_old_conversation_memory(days_to_keep)` function implemented
- [ ] Function returns count of deleted records
- [ ] Function uses parameterized days_to_keep (default 30)
- [ ] Function handles edge cases (no records to delete, invalid parameters)
- [ ] Function tested with various scenarios

**Testing Requirements:**
- [ ] **Unit Tests**: Function logic and parameter validation
- [ ] **Integration Tests**: Actual cleanup operations with test data
- [ ] **Performance Tests**: Cleanup performance with large datasets
- [ ] **Error Handling Tests**: Invalid parameters and edge cases
- [ ] **Data Integrity Tests**: Verify only intended records are deleted

**Implementation Notes:** Use `CREATE OR REPLACE FUNCTION cleanup_old_conversation_memory(days_to_keep INTEGER DEFAULT 30) RETURNS INTEGER` with proper error handling.

**Quality Gates:**
- [ ] **Code Review**: Cleanup function logic reviewed
- [ ] **Tests Passing**: All cleanup function tests pass
- [ ] **Security Reviewed**: No SQL injection vulnerabilities
- [ ] **Documentation Updated**: Cleanup function usage documented

#### Task 3.2: Create Python Helper for Lazy Embedding Backfill
**Priority:** Medium
**Estimated Time:** 0.5 hours
**Dependencies:** Task 3.1
**Description:** Create ensure_chat_embeddings.py script for on-demand embedding computation
**Acceptance Criteria:**
- [ ] Script computes missing embeddings for conversation_memory records
- [ ] Script processes records incrementally with progress feedback
- [ ] Script handles errors gracefully and provides recovery options
- [ ] Script integrates with existing conversation storage system
- [ ] Script documented with usage examples

**Testing Requirements:**
- [ ] **Unit Tests**: Embedding computation logic
- [ ] **Integration Tests**: Integration with conversation storage
- [ ] **Performance Tests**: Processing speed and memory usage
- [ ] **Error Handling Tests**: Network failures, invalid embeddings
- [ ] **Progress Tracking Tests**: Accurate progress reporting

**Implementation Notes:** Use existing embedding models and conversation storage infrastructure for consistency.

**Quality Gates:**
- [ ] **Code Review**: Embedding computation logic reviewed
- [ ] **Tests Passing**: All embedding helper tests pass
- [ ] **Performance Validated**: Processing speed acceptable for large datasets
- [ ] **Documentation Updated**: Helper script usage documented

#### Task 3.3: Add Comprehensive Error Handling
**Priority:** High
**Estimated Time:** 0.5 hours
**Dependencies:** Task 3.2
**Description:** Implement robust error handling for all new components
**Acceptance Criteria:**
- [ ] All DDL operations have proper error handling
- [ ] Cleanup function handles all error scenarios gracefully
- [ ] Embedding helper provides clear error messages and recovery options
- [ ] Error logging implemented for debugging
- [ ] Rollback procedures documented for all operations

**Testing Requirements:**
- [ ] **Unit Tests**: Error handling for each componen
- [ ] **Integration Tests**: Error propagation between components
- [ ] **Resilience Tests**: System behavior under various failure conditions
- [ ] **Recovery Tests**: Rollback and recovery procedures validated

**Implementation Notes:** Use PostgreSQL exception handling and Python try/catch blocks with meaningful error messages.

**Quality Gates:**
- [ ] **Code Review**: Error handling logic reviewed
- [ ] **Tests Passing**: All error handling tests pass
- [ ] **Documentation Updated**: Error handling and recovery procedures documented

### Phase 4: Testing and Validation (1 hour)

#### Task 4.1: Run Full Test Suite
**Priority:** Critical
**Estimated Time:** 0.5 hours
**Dependencies:** Task 3.3
**Description:** Execute comprehensive test suite covering all new functionality
**Acceptance Criteria:**
- [ ] All unit tests pass (100% coverage of new code)
- [ ] All integration tests pass (end-to-end workflows)
- [ ] All performance tests meet benchmarks
- [ ] All security tests pass (no vulnerabilities)
- [ ] All resilience tests pass (error handling validated)

**Testing Requirements:**
- [ ] **Test Execution**: Automated test suite runs successfully
- [ ] **Coverage Analysis**: Code coverage meets targets
- [ ] **Performance Validation**: All benchmarks me
- [ ] **Security Validation**: No security issues identified
- [ ] **Documentation**: Test results documented

**Implementation Notes:** Use existing test infrastructure and add new tests for all components.

**Quality Gates:**
- [ ] **Tests Passing**: All tests pass with required coverage
- [ ] **Performance Validated**: All performance benchmarks me
- [ ] **Security Reviewed**: No security issues identified

#### Task 4.2: Verify Backward Compatibility
**Priority:** Critical
**Estimated Time:** 0.25 hours
**Dependencies:** Task 4.1
**Description:** Ensure existing conversation data and queries continue working
**Acceptance Criteria:**
- [ ] All existing conversation_memory queries still work
- [ ] No data loss or corruption during migration
- [ ] Existing DSPy functionality unchanged
- [ ] Performance on existing queries not degraded
- [ ] All existing integrations continue working

**Testing Requirements:**
- [ ] **Backward Compatibility Tests**: All existing functionality verified
- [ ] **Data Integrity Tests**: No data loss or corruption
- [ ] **Performance Tests**: No regression on existing operations
- [ ] **Integration Tests**: All existing integrations validated

**Implementation Notes:** Test with real conversation data to ensure no breaking changes.

**Quality Gates:**
- [ ] **Tests Passing**: All backward compatibility tests pass
- [ ] **Performance Validated**: No performance regression
- [ ] **Data Integrity**: No data loss or corruption

#### Task 4.3: Performance Benchmarking
**Priority:** High
**Estimated Time:** 0.25 hours
**Dependencies:** Task 4.2
**Description:** Validate performance improvements and document benchmarks
**Acceptance Criteria:**
- [ ] HNSW vs IVFFlat performance comparison documented
- [ ] Semantic search performance measured and documented
- [ ] Cleanup function performance validated
- [ ] Embedding computation performance measured
- [ ] Performance benchmarks documented for future reference

**Testing Requirements:**
- [ ] **Performance Tests**: Comprehensive benchmarking suite
- [ ] **Comparison Tests**: HNSW vs IVFFlat performance analysis
- [ ] **Load Tests**: Performance under realistic data volumes
- [ ] **Documentation**: Performance results documented

**Implementation Notes:** Use realistic data volumes and document all performance metrics for future optimization.

**Quality Gates:**
- [ ] **Performance Validated**: All performance targets me
- [ ] **Documentation Updated**: Performance benchmarks documented
- [ ] **Results Analyzed**: Performance improvements quantified

## Quality Metrics

- **Test Coverage Target**: 100% for new code
- **Performance Benchmarks**: HNSW provides better recall/latency than IVFFla
- **Security Requirements**: No SQL injection, proper input validation
- **Reliability Targets**: Zero data loss, 100% backward compatibility

## Risk Mitigation

- **Technical Risks**: pgvector version compatibility - mitigated by version checking and fallback
- **Timeline Risks**: Schema complexity - mitigated by phased approach and testing
- **Resource Risks**: Performance impact - mitigated by conservative HNSW parameters and lazy processing

## Implementation Status

### Overall Progress
- **Total Tasks:** 0 completed out of 12 total
- **Current Phase:** Planning
- **Estimated Completion:** 8 hours
- **Blockers:** None

### Quality Gates
- [ ] **Code Review Completed** - All code has been reviewed
- [ ] **Tests Passing** - All unit and integration tests pass
- [ ] **Documentation Updated** - All relevant docs updated
- [ ] **Performance Validated** - Performance meets requirements
- [ ] **Security Reviewed** - Security implications considered
- [ ] **User Acceptance** - Feature validated with users
- [ ] **Resilience Tested** - Error handling and recovery validated
- [ ] **Edge Cases Covered** - Boundary conditions tested

## Success Criteria

- **Semantic search capability**: Can find relevant past conversations using vector similarity
- **Environment reproducibility**: Fresh clone works with just `psql -f schema.sql`
- **Governance compliance**: All changes align with local-first, simple principles
- **Performance improvement**: HNSW provides better recall/latency than IVFFla
- **Future readiness**: User_id column available for multi-tenant scenarios
- **Manual cleanup**: Governance-aligned retention policy implemented
