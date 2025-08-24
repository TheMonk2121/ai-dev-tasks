# Process Task List: B-1015 LTST Memory System Database Optimization

## Overview

Execute governance-aligned improvements to the LTST (Long-Term Short-Term) memory system including HNSW semantic search enhancement, DSPy tables promotion to schema.sql, user/session hygiene with nullable user_id, and manual cleanup function for local-first retention policy.

**Backlog ID**: B-1015
**Priority**: High
**Estimated Effort**: 8 hours
**Dependencies**: B-1012 LTST Memory System
**Auto-Advance**: no (Critical database changes require human review)

## Implementation Phases

### Phase 1: Schema Preparation and Validation (2 hours)

#### Task 1.1: Validate pgvector Version Compatibility
**Priority**: Critical
**Time**: 0.5 hours
**Depends on**: None
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Create utility script to check pgvector version and HNSW support
2. Test pgvector version detection in current environment
3. Validate HNSW index creation capability
4. Document fallback strategy to IVFFlat if HNSW unavailable
5. Update setup documentation with version requirements

**Done when**:
- [ ] pgvector version check script created and tested
- [ ] HNSW support validated in current environment
- [ ] Fallback to IVFFlat strategy documented if HNSW unavailable
- [ ] Version requirements documented in setup guide

**When Ready Prompt**: "pgvector version validation complete - proceed to DDL preparation?"

#### Task 1.2: Prepare DDL Statements with Idempotent Patterns
**Priority**: Critical
**Time**: 1 hour
**Depends on**: Task 1.1
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Create all ALTER TABLE statements using `ADD COLUMN IF NOT EXISTS`
2. Create all CREATE INDEX statements using `CREATE INDEX IF NOT EXISTS`
3. Create all CREATE TABLE statements using `CREATE TABLE IF NOT EXISTS`
4. Create all CREATE FUNCTION statements using `CREATE OR REPLACE FUNCTION`
5. Test DDL statements for idempotency in isolated environment

**Done when**:
- [ ] All ALTER TABLE statements use `ADD COLUMN IF NOT EXISTS`
- [ ] All CREATE INDEX statements use `CREATE INDEX IF NOT EXISTS`
- [ ] All CREATE TABLE statements use `CREATE TABLE IF NOT EXISTS`
- [ ] All CREATE FUNCTION statements use `CREATE OR REPLACE FUNCTION`
- [ ] DDL statements tested for idempotency

**When Ready Prompt**: "DDL statements prepared with idempotent patterns - proceed to schema testing?"

#### Task 1.3: Test Schema Application in Isolated Environment
**Priority**: High
**Time**: 0.5 hours
**Depends on**: Task 1.2
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Create fresh database instance for testing
2. Apply all DDL statements to test database
3. Verify all new objects (columns, indexes, functions) created successfully
4. Test rollback procedure if needed
5. Document any errors or warnings encountered

**Done when**:
- [ ] Fresh database created for testing
- [ ] All DDL statements applied successfully
- [ ] No errors or warnings during schema creation
- [ ] All new objects (columns, indexes, functions) verified
- [ ] Rollback procedure tested and documented

**When Ready Prompt**: "Schema application tested successfully - proceed to core implementation?"

### Phase 2: Core Schema Implementation (3 hours)

#### Task 2.1: Add Embedding Column to conversation_memory
**Priority**: Critical
**Time**: 0.5 hours
**Depends on**: Task 1.3
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Execute `ALTER TABLE conversation_memory ADD COLUMN IF NOT EXISTS embedding VECTOR(384)`
2. Verify column added successfully with proper data type
3. Confirm existing data remains intact
4. Test that column allows NULL values for existing records
5. Verify column is ready for vector operations

**Done when**:
- [ ] `embedding VECTOR(384)` column added to conversation_memory table
- [ ] Column allows NULL values for existing records
- [ ] No data loss or corruption during migration
- [ ] Column properly indexed for vector operations

**When Ready Prompt**: "Embedding column added successfully - proceed to HNSW index creation?"

#### Task 2.2: Create HNSW Index with Optimal Parameters
**Priority**: Critical
**Time**: 1 hour
**Depends on**: Task 2.1
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Execute HNSW index creation with optimal parameters
2. Monitor index creation progress and time
3. Verify index created successfully with vector_cosine_ops
4. Test basic vector similarity search functionality
5. Benchmark performance against IVFFlat if available

**Done when**:
- [ ] HNSW index created on conversation_memory.embedding
- [ ] Index uses vector_cosine_ops for similarity search
- [ ] Parameters optimized: m=16, ef_construction=64
- [ ] Index creation time measured and documented
- [ ] Performance improvement over IVFFlat validated

**When Ready Prompt**: "HNSW index created successfully - proceed to DSPy tables promotion?"

#### Task 2.3: Promote DSPy Tables to schema.sql
**Priority**: High
**Time**: 1 hour
**Depends on**: Task 2.2
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Add dspy_signatures table definition to schema.sql
2. Add dspy_examples table definition with foreign key to signatures
3. Create necessary indexes (signature_name, signature_id, quality_score)
4. Test table creation and basic CRUD operations
5. Verify environment reproducibility (fresh clone + psql -f schema.sql)

**Done when**:
- [ ] dspy_signatures table created in schema.sql with proper structure
- [ ] dspy_examples table created in schema.sql with foreign key to signatures
- [ ] All necessary indexes created (signature_name, signature_id, quality_score)
- [ ] Tables support existing DSPy functionality
- [ ] Environment reproducibility verified (fresh clone + psql -f schema.sql works)

**When Ready Prompt**: "DSPy tables promoted to schema.sql - proceed to user_id column addition?"

#### Task 2.4: Add user_id Column for Future Multi-tenant Support
**Priority**: Medium
**Time**: 0.5 hours
**Depends on**: Task 2.3
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Execute `ALTER TABLE conversation_memory ADD COLUMN IF NOT EXISTS user_id VARCHAR(255)`
2. Verify column added successfully with proper data type
3. Confirm column allows NULL values for current single-user state
4. Test that existing functionality continues working
5. Document future indexing strategy for multi-tenant scenarios

**Done when**:
- [ ] `user_id VARCHAR(255)` column added to conversation_memory
- [ ] Column allows NULL values (single-user current state)
- [ ] No breaking changes to existing functionality
- [ ] Column ready for future indexing when multi-tenant is enabled

**When Ready Prompt**: "user_id column added successfully - proceed to cleanup function implementation?"

### Phase 3: Cleanup and Helper Implementation (2 hours)

#### Task 3.1: Implement Manual Cleanup Function
**Priority**: High
**Time**: 1 hour
**Depends on**: Task 2.4
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Create PostgreSQL function `cleanup_old_conversation_memory(days_to_keep INTEGER DEFAULT 30)`
2. Implement function logic with proper error handling
3. Test function with various scenarios (no records, invalid parameters)
4. Verify function returns count of deleted records
5. Document function usage and examples

**Done when**:
- [ ] `cleanup_old_conversation_memory(days_to_keep)` function implemented
- [ ] Function returns count of deleted records
- [ ] Function uses parameterized days_to_keep (default 30)
- [ ] Function handles edge cases (no records to delete, invalid parameters)
- [ ] Function tested with various scenarios

**When Ready Prompt**: "Cleanup function implemented successfully - proceed to embedding helper creation?"

#### Task 3.2: Create Python Helper for Lazy Embedding Backfill
**Priority**: Medium
**Time**: 0.5 hours
**Depends on**: Task 3.1
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Create `ensure_chat_embeddings.py` script
2. Implement incremental processing with progress feedback
3. Integrate with existing conversation storage system
4. Add error handling and recovery options
5. Document script usage with examples

**Done when**:
- [ ] Script computes missing embeddings for conversation_memory records
- [ ] Script processes records incrementally with progress feedback
- [ ] Script handles errors gracefully and provides recovery options
- [ ] Script integrates with existing conversation storage system
- [ ] Script documented with usage examples

**When Ready Prompt**: "Embedding helper script created successfully - proceed to error handling implementation?"

#### Task 3.3: Add Comprehensive Error Handling
**Priority**: High
**Time**: 0.5 hours
**Depends on**: Task 3.2
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Add error handling to all DDL operations
2. Enhance cleanup function with comprehensive error handling
3. Improve embedding helper error messages and recovery options
4. Implement error logging for debugging
5. Document rollback procedures for all operations

**Done when**:
- [ ] All DDL operations have proper error handling
- [ ] Cleanup function handles all error scenarios gracefully
- [ ] Embedding helper provides clear error messages and recovery options
- [ ] Error logging implemented for debugging
- [ ] Rollback procedures documented for all operations

**When Ready Prompt**: "Error handling implemented successfully - proceed to testing and validation?"

### Phase 4: Testing and Validation (1 hour)

#### Task 4.1: Run Full Test Suite
**Priority**: Critical
**Time**: 0.5 hours
**Depends on**: Task 3.3
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Execute all unit tests for new components
2. Run integration tests for end-to-end workflows
3. Perform performance tests against benchmarks
4. Execute security tests for vulnerabilities
5. Run resilience tests for error handling validation

**Done when**:
- [ ] All unit tests pass (100% coverage of new code)
- [ ] All integration tests pass (end-to-end workflows)
- [ ] All performance tests meet benchmarks
- [ ] All security tests pass (no vulnerabilities)
- [ ] All resilience tests pass (error handling validated)

**When Ready Prompt**: "Full test suite passed successfully - proceed to backward compatibility verification?"

#### Task 4.2: Verify Backward Compatibility
**Priority**: Critical
**Time**: 0.25 hours
**Depends on**: Task 4.1
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Test all existing conversation_memory queries
2. Verify no data loss or corruption during migration
3. Confirm existing DSPy functionality unchanged
4. Test performance on existing queries for regression
5. Validate all existing integrations continue working

**Done when**:
- [ ] All existing conversation_memory queries still work
- [ ] No data loss or corruption during migration
- [ ] Existing DSPy functionality unchanged
- [ ] Performance on existing queries not degraded
- [ ] All existing integrations continue working

**When Ready Prompt**: "Backward compatibility verified successfully - proceed to performance benchmarking?"

#### Task 4.3: Performance Benchmarking
**Priority**: High
**Time**: 0.25 hours
**Depends on**: Task 4.2
**Auto-Advance**: no
**🛑 Pause After**: yes

**Do**:
1. Compare HNSW vs IVFFlat performance
2. Measure semantic search performance
3. Benchmark cleanup function performance
4. Test embedding computation performance
5. Document all performance metrics for future reference

**Done when**:
- [ ] HNSW vs IVFFlat performance comparison documented
- [ ] Semantic search performance measured and documented
- [ ] Cleanup function performance validated
- [ ] Embedding computation performance measured
- [ ] Performance benchmarks documented for future reference

**When Ready Prompt**: "Performance benchmarking completed successfully - B-1015 implementation complete!"

## Quality Gates

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
- **Performance improvement**: HNSW provides better recall/latency than IVFFlat
- **Future readiness**: User_id column available for multi-tenant scenarios
- **Manual cleanup**: Governance-aligned retention policy implemented

## Implementation Status

### Overall Progress
- **Total Tasks:** 0 completed out of 12 total
- **Current Phase:** Planning
- **Estimated Completion:** 8 hours
- **Blockers:** None

### Current State
- **Last Commit**: None
- **File List**: []
- **Test Results**: {"passed": 0, "failed": 0}
- **Current Task**: None
- **Completed Tasks**: []

## HotFix Tasks

*No HotFix tasks created yet*

## Notes

- All database changes require human review before proceeding
- Each phase includes comprehensive testing and validation
- Error handling and rollback procedures are critical for database operations
- Performance benchmarking is essential for validating improvements
