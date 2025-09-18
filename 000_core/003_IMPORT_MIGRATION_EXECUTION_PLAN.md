# Process Task List: Import Migration to Absolute Imports

<!-- ANCHOR_KEY: import-migration-execution -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["implementer", "planner"] -->

## Execution Configuration
- **Auto-Advance**: No (critical infrastructure changes)
- **Pause Points**: After each phase for validation
- **Context Preservation**: LTST integration enabled
- **Smart Pausing**: Pause after each directory for type checking validation

## State Management
- **State File**: `.ai_state.json` (gitignored)
- **Progress Tracking**: Phase-by-phase completion tracking
- **Session Continuity**: Import migration status persisted

## Error Handling
- **HotFix Generation**: Auto-recovery for import resolution failures
- **Retry Logic**: Exponential backoff for type checking failures
- **User Intervention**: Pause on type checking regressions

## Implementation Status
- **Total Tasks**: 4/4 phases
- **Current Phase**: Planning
- **Blockers**: None

## Quality Gates
- [ ] make lint — code quality checks complete
- [ ] make typecheck — type checking complete  
- [ ] make precommit — comprehensive checks complete
- [ ] make test-fast — quick gate tests passing
- [ ] make test-all — full test suite passing (unit/integration)
- [ ] make eval-gold — eval gates met on gold profile
- [ ] make db-status — database readiness verified
- [ ] Documentation updated (400_ governance in effect)
- [ ] Performance validated (import resolution speed)
- [ ] Security reviewed
- [ ] Resilience tested (import fallback mechanisms)
- [ ] Edge cases covered

---

## Phase 1: Critical Core Infrastructure (P0 - Must Complete First)

### 1.1 Database & Configuration Layer
**Priority**: CRITICAL | **Estimate**: 30 minutes | **Dependencies**: None

```bash
# Convert core database and configuration modules
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/common
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/config
```

**Files to Convert**:
- `src/common/db_sync.py` - Database sync operations
- `src/common/db_async.py` - Async database operations  
- `src/common/role_guc_manager.py` - Database role management
- `src/config/__init__.py` - Configuration exports
- `src/config/settings.py` - Pydantic settings

**Validation Commands**:
```bash
make typecheck  # Verify no type errors
make test-fast  # Quick validation
```

**Acceptance Criteria**:
- [ ] All database-related imports use absolute paths
- [ ] Type checking passes without errors
- [ ] Database operations continue to work
- [ ] Configuration loading works correctly

---

## Phase 2: Core Business Logic (P1 - High Priority)

### 2.1 Memory & Validation Systems
**Priority**: HIGH | **Estimate**: 45 minutes | **Dependencies**: Phase 1

```bash
# Convert memory and validation modules
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/memory
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/utils
```

**Files to Convert**:
- `src/memory/guards.py` - Memory system guards
- `src/utils/validator.py` - Input validation
- `src/utils/retry_wrapper.py` - Retry mechanisms
- `src/utils/prompt_sanitizer.py` - Security sanitization

### 2.2 DSPy Modules (Core AI Logic)
**Priority**: HIGH | **Estimate**: 30 minutes | **Dependencies**: Phase 1

```bash
# Convert DSPy modules
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/dspy_modules
```

**Files to Convert**:
- `src/dspy_modules/reader/__init__.py` - Reader exports
- `src/dspy_modules/reader/entrypoint.py` - Reader entry point
- `src/dspy_modules/reader/program.py` - Reader program logic
- `src/dspy_modules/retriever/pg.py` - PostgreSQL retriever

**Validation Commands**:
```bash
make typecheck  # Verify type safety
make test-fast  # Quick validation
uv run python evals/scripts/evaluation/evaluation_graph_integration.py --compare  # Test DiGraph system
```

**Acceptance Criteria**:
- [ ] All memory system imports use absolute paths
- [ ] DSPy modules import correctly
- [ ] Type checking passes
- [ ] DiGraph evaluation system works

---

## Phase 3: Retrieval & Monitoring (P2 - Medium Priority)

### 3.1 Retrieval System
**Priority**: MEDIUM | **Estimate**: 30 minutes | **Dependencies**: Phase 2

```bash
# Convert retrieval and monitoring modules
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/retrieval
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/monitoring
```

**Files to Convert**:
- `src/retrieval/advanced_retriever.py` - Advanced retrieval logic
- `src/retrieval/cross_encoder_client.py` - Cross-encoder client
- `src/monitoring/production_monitor.py` - Production monitoring
- `src/monitoring/__init__.py` - Monitoring exports

### 3.2 Language Processing
**Priority**: MEDIUM | **Estimate**: 15 minutes | **Dependencies**: Phase 2

```bash
# Convert language processing modules
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/llm
```

**Files to Convert**:
- `src/llm/script_aware_tokenizer.py` - Tokenization logic

**Validation Commands**:
```bash
make typecheck  # Verify type safety
make test-fast  # Quick validation
```

**Acceptance Criteria**:
- [ ] Retrieval system imports work correctly
- [ ] Monitoring system functions properly
- [ ] Language processing modules import correctly
- [ ] Type checking passes

---

## Phase 4: Scripts & Evaluation (P3 - Lower Priority)

### 4.1 Utility Scripts
**Priority**: LOW | **Estimate**: 45 minutes | **Dependencies**: Phase 3

```bash
# Convert utility scripts
uv run python scripts/migration/migrate_to_absolute_imports.py --path scripts/utilities
```

**Files to Convert**:
- `scripts/utilities/cursor_realtime_monitor.py` - Cursor monitoring
- `scripts/utilities/cursor_auto_capture.py` - Auto capture
- `scripts/utilities/cursor_file_trigger.py` - File triggers
- `scripts/utilities/cursor_extension_integration.py` - Extension integration
- `scripts/utilities/cursor_unified_integration.py` - Unified integration
- `scripts/utilities/relaxed_validator.py` - Relaxed validation
- `scripts/utilities/cursor_mcp_capture.py` - MCP capture
- `scripts/utilities/tools/cursor_atlas_integration.py` - Atlas integration
- `scripts/utilities/tools/atlas_unified_system.py` - Atlas system
- `scripts/utilities/memory/mcp_memory_server.py` - Memory server

### 4.2 Evaluation System
**Priority**: LOW | **Estimate**: 15 minutes | **Dependencies**: Phase 3

```bash
# Convert evaluation modules
uv run python scripts/migration/migrate_to_absolute_imports.py --path evals
```

**Files to Convert**:
- `evals/stable_build/modules/run.py` - Evaluation runner
- `evals/stable_build/modules/gen.py` - Generation logic
- `evals/stable_build/modules/report.py` - Reporting
- `evals/scripts/evaluation/__init__.py` - Evaluation exports

**Validation Commands**:
```bash
make typecheck  # Verify type safety
make test-all   # Full test suite
make eval-gold  # Gold profile evaluation
```

**Acceptance Criteria**:
- [ ] All utility scripts import correctly
- [ ] Evaluation system functions properly
- [ ] Type checking passes
- [ ] Full test suite passes
- [ ] Gold evaluation works

---

## Execution Commands

### Start Migration
```bash
# Phase 1: Critical Core Infrastructure
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/common
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/config
make typecheck && make test-fast
```

### Continue Migration
```bash
# Phase 2: Core Business Logic
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/memory
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/utils
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/dspy_modules
make typecheck && make test-fast
```

### Complete Migration
```bash
# Phase 3: Retrieval & Monitoring
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/retrieval
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/monitoring
uv run python scripts/migration/migrate_to_absolute_imports.py --path src/llm
make typecheck && make test-fast

# Phase 4: Scripts & Evaluation
uv run python scripts/migration/migrate_to_absolute_imports.py --path scripts/utilities
uv run python scripts/migration/migrate_to_absolute_imports.py --path evals
make typecheck && make test-all && make eval-gold
```

---

## Risk Mitigation

### High-Risk Areas
1. **Database modules** - Core infrastructure, test thoroughly
2. **DSPy modules** - AI logic, verify evaluation system works
3. **Memory system** - Cross-session continuity, test memory rehydration

### Rollback Strategy
```bash
# If issues arise, revert specific files
git checkout HEAD -- src/common/db_sync.py
git checkout HEAD -- src/common/db_async.py
# etc.
```

### Validation Strategy
- **After each phase**: Run `make typecheck` and `make test-fast`
- **After Phase 2**: Test DiGraph evaluation system
- **After Phase 4**: Run full test suite and gold evaluation

---

## Success Metrics

### Quantitative
- **Type checking errors**: 0 (down from current issues)
- **Import resolution time**: < 100ms per module
- **Test coverage**: Maintained or improved
- **Build time**: No significant increase

### Qualitative
- **Code clarity**: Import paths are explicit and clear
- **Maintainability**: Easier to refactor and move files
- **Standards compliance**: Follows PEP 8 and project rules
- **Developer experience**: Better IDE support and type checking

---

## Next Steps

1. **Execute Phase 1** - Critical core infrastructure
2. **Validate** - Run type checking and quick tests
3. **Continue to Phase 2** - Core business logic
4. **Monitor** - Watch for any regressions
5. **Complete** - Finish remaining phases
6. **Document** - Update any affected documentation

**Ready to begin Phase 1?**
