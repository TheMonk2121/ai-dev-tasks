<!-- ANCHOR_KEY: prd-b-1006-dspy-3-0-migration -->
<!-- ANCHOR_PRIORITY: 35 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->
<!-- Backlog ID: B-1006 -->
<!-- Status: todo -->
<!-- Priority: High -->
<!-- Dependencies: B-1003 -->
<!-- Version: 1.0 -->
<!-- Date: 2025-01-23 -->

# Product Requirements Document: B-1006 - DSPy 3.0 Migration

> ⚠️**Auto-Skip Note**: This PRD was generated because either `points≥5` or `score_total<3.0`.
> Remove this banner if you manually forced PRD creation.

## 1. Problem Statement

**What's broken?** The current system uses DSPy 2.6.27 with a sophisticated custom assertion framework and optimization components. While this implementation is advanced, it's missing native DSPy 3.0 features, constitution-aware testing, GEPA optimizer migration, performance budgets, safety mechanisms, and surgical asyncio integration for I/O operations needed for production deployment.

**Why does it matter?** DSPy 3.0 introduces native assertion support (`dspy.Assert`, `@dspy.assert_transform_module`), enhanced optimization capabilities, MLflow integration, and improved fine-tuning support. Additionally, we need constitution-aware testing, GEPA optimizer migration with performance budgets, feature flags for gradual rollout, HITL safety mechanisms, and surgical asyncio integration for 60% I/O performance improvement for production readiness.

**What's the opportunity?** By migrating to DSPy 3.0 with enhanced requirements, we can:
- Replace custom assertion framework with native `dspy.Assert` support
- Implement constitution-aware regression suite with context preservation, workflow chain, and error recovery checks
- Migrate Coder/Planner pipelines to GEPA with performance budgets (latency ≤ +20%, tokens ≤ +25%)
- Add feature flags (OPTIMIZE_PLANNER, OPTIMIZE_CODER) for gradual rollout
- Implement HITL fallback for safety when scores fall below thresholds
- Implement surgical asyncio integration for 60% I/O performance improvement
- Achieve ≥15% improvement on seeded bugs with 0 dependency violations
- Integrate MLflow for comprehensive experiment tracking and CoT/ReAct traces
- Future-proof the system with the latest framework capabilities
- **Schema compatibility confirmed** - existing signatures and field definitions work identically in DSPy 3.0

## 2. Solution Overview

**What are we building?** A comprehensive migration from DSPy 2.6.27 to DSPy 3.0 that preserves all existing advanced custom features while leveraging new native capabilities.

**How does it work?** The migration will follow a phased approach:
1. **Environment & Compatibility**: Pin DSPy 3.0.1 in constraints.txt, run regression tests + lint + doc-coherence validator, add baseline metrics → eval/baseline.json
2. **Constitution-Aware Testing Integration**: Integrate constitution-aware testing with existing test infrastructure, implement constitution compliance validation
3. **Assertion Migration**: Replace custom validators with DSPy 3.0 assertions, add constitution-aware regression suite with context preservation, workflow chain, and error recovery checks, re-tier modules in 400_code-criticality-guide.md
4. **Optimizer Refit**: Migrate Coder/Planner pipelines to GEPA with performance budgets (latency ≤ +20%, tokens ≤ +25%), add optimizer_budget.yaml caps per role
5. **Surgical AsyncIO Integration**: Implement AsyncMemoryRehydrator in existing memory_rehydrator.py with asyncio.to_thread() for 40-60% I/O performance improvement, optional SQLite STM, background flusher, and bounded concurrency
6. **Observability**: MLflow integration for optimizer runs, capture CoT/ReAct traces and artifact diffs in eval_report.json
7. **Rollout & Safety**: Feature flags (OPTIMIZE_PLANNER, OPTIMIZE_CODER), HITL fallback for <threshold scores
8. **Production Deployment**: Gradual rollout with rollback capabilities

**What are the key features?**
- Native assertion support replacing custom framework
- Constitution-aware regression suite with context preservation, workflow chain, and error recovery checks
- GEPA optimizer migration with performance budgets (latency ≤ +20%, tokens ≤ +25%)
- Feature flags (OPTIMIZE_PLANNER, OPTIMIZE_CODER) for gradual rollout
- HITL fallback for safety when scores fall below thresholds
- Constitution-aware testing integrated with existing test infrastructure
- Optimizer budget enforcement with constitution compliance validation
- Surgical asyncio integration with AsyncMemoryRehydrator in existing memory_rehydrator.py
- Optional SQLite STM (local-first) with asyncio.to_thread() for existing DB calls
- Background flusher with bounded concurrency (semaphores) for predictable performance
- Zero new external dependencies (uses existing psycopg2/sqlite3)
- MLflow integration for comprehensive experiment tracking and CoT/ReAct traces
- Performance baseline establishment and improvement tracking
- Backward compatibility with existing custom components

## 3. Acceptance Criteria

**How do we know it's done?**
- All existing DSPy modules work with DSPy 3.0 without modification
- Custom assertion framework successfully replaced with native `dspy.Assert`
- Constitution-aware regression suite passes all checks (context preservation, workflow chain, error recovery)
- GEPA optimizer migration completed with performance budgets (latency ≤ +20%, tokens ≤ +25%)
- Feature flags (OPTIMIZE_PLANNER, OPTIMIZE_CODER) implemented and functional
- HITL fallback mechanism operational for <threshold scores
- MLflow integration provides comprehensive experiment tracking and CoT/ReAct traces
- Performance metrics show ≥15% improvement on seeded bugs with 0 dependency violations
- All tests pass with DSPy 3.0

**What does success look like?**
- System successfully migrates to DSPy 3.0 with zero downtime
- Native assertion support reduces code complexity by 30%
- Constitution test suite green with all articles validated
- GEPA optimization improves performance by 15-25% within budget constraints
- Feature flags enable gradual rollout with safety controls
- HITL fallback provides safety net for low-scoring operations
- Surgical asyncio integration (AsyncMemoryRehydrator) provides 40-60% I/O performance improvement
- Optional SQLite STM provides local-first memory without external dependencies
- Background flusher with bounded concurrency maintains Tier-1 performance discipline
- MLflow integration provides comprehensive experiment tracking and artifact diffs
- Constitution-aware testing integrated with existing test infrastructure
- Optimizer budget enforcement with constitution compliance validation operational
- All existing advanced features remain functional
- Tier 1 modules stable post-migration

**What are the quality gates?**
- All existing tests must pass with DSPy 3.0
- Constitution test suite must be green with all articles validated
- Performance benchmarks must show ≥15% improvement on seeded bugs with 0 dependency violations
- GEPA optimizer must operate within performance budgets (latency ≤ +20%, tokens ≤ +25%)
- Feature flags must be functional for gradual rollout
- HITL fallback must be operational for <threshold scores
- Custom assertion framework must be fully replaced with native DSPy 3.0 assertions
- Surgical asyncio integration (AsyncMemoryRehydrator) must provide 40-60% I/O performance improvement
- Optional SQLite STM must function without external dependencies
- Background flusher with bounded concurrency must maintain Tier-1 performance discipline
- MLflow integration must be functional with CoT/ReAct traces
- Constitution-aware testing integrated with existing test infrastructure
- Optimizer budget enforcement with constitution compliance validation operational
- Rollback capability must be tested and verified
- Tier 1 modules must be stable post-migration

## 4. Technical Approach

**What technology?**
- DSPy 3.0.1 (pinned version upgrade from 2.6.27)
- MLflow for experiment tracking and CoT/ReAct traces
- GEPA optimizer with performance budgets
- Constitution-aware testing framework
- Feature flags for gradual rollout
- HITL fallback mechanisms
- Native assertion framework
- Surgical asyncio integration (asyncio.to_thread(), built-in asyncio, optional SQLite)
- AsyncMemoryRehydrator in existing memory_rehydrator.py
- Background flusher with bounded concurrency (asyncio.Semaphore)
- Performance baseline metrics
- Existing custom components (preserved)
- Zero new external dependencies

**How does it integrate?**
- Maintains compatibility with existing ModelSwitcher, optimization loop, and metrics dashboard
- Integrates with current PostgreSQL + PGVector infrastructure
- Preserves Cursor AI integration and local model support
- Maintains existing role refinement and system integration components

**What are the constraints?**
- Must maintain backward compatibility with existing custom features
- Hardware constraints (M4 Mac, 128GB RAM) remain unchanged
- Local model integration (Ollama) must continue working
- Zero downtime migration requirement
- **Schema compatibility** - existing signatures and field definitions are fully compatible with DSPy 3.0

## 5. Risks and Mitigation

**What could go wrong?**
- Breaking changes in DSPy 3.0 API that affect existing modules
- Performance regression with GEPA optimizer migration
- Constitution-aware testing complexity and overhead
- Feature flag implementation complexity
- HITL fallback mechanism reliability
- Performance budget constraints not met
- MLflow integration complexity and overhead
- Custom assertion framework replacement complexity
- **Schema compatibility risk** - Minimal risk confirmed through analysis of existing signatures

**How do we handle it?**
- Comprehensive testing in isolated environment before production
- Gradual migration with rollback capabilities at each phase
- Performance benchmarking at each step with baseline metrics
- Constitution-aware testing to ensure compliance
- Feature flags for gradual rollout with safety controls
- HITL fallback for safety when scores fall below thresholds
- Performance budget monitoring and enforcement
- Maintain custom assertion framework as fallback during transition

**What are the unknowns?**
- Exact DSPy 3.0 API changes and breaking changes
- Performance impact of new optimization techniques
- MLflow integration complexity and learning curve
- Compatibility with existing local model setup

## 6. Testing Strategy

**What needs testing?**
- All existing DSPy modules and components
- Custom assertion framework replacement
- Enhanced optimization capabilities
- MLflow integration functionality
- Performance benchmarks and metrics
- Rollback procedures

**How do we test it?**
- Comprehensive test suite with DSPy 3.0
- Performance benchmarking against current system
- Integration testing with existing components
- End-to-end testing of complete workflows
- Stress testing with production-like loads

**What's the coverage target?**
- 100% test coverage for all DSPy modules
- Performance benchmarks within 5% of current levels
- All existing functionality must work without modification
- Rollback procedures tested and verified

## 7. Implementation Plan

**What are the phases?**
1. **Phase 1: Test Environment** (2 hours)
   - Set up isolated DSPy 3.0 test environment
   - Install and configure DSPy 3.0
   - Validate basic functionality

2. **Phase 2: Compatibility Testing** (4 hours)
   - Test all existing modules with DSPy 3.0
   - Identify and resolve compatibility issues
   - Validate performance benchmarks

3. **Phase 3: Native Feature Integration** (6 hours)
   - Replace custom assertions with native DSPy 3.0 assertions
   - Integrate enhanced optimization capabilities
   - Test and validate new features

4. **Phase 4: MLflow Integration** (4 hours)
   - Set up MLflow integration
   - Configure experiment tracking
   - Test and validate tracking capabilities

5. **Phase 5: Production Deployment** (2 hours)
   - Gradual rollout to production
   - Monitor performance and stability
   - Verify all functionality

**What are the dependencies?**
- DSPy 3.0 availability and stability
- Existing B-1003 DSPy Multi-Agent System Implementation (completed)
- Test environment setup and configuration
- Performance benchmarking tools

**What's the timeline?**
- Total estimated time: 18 hours
- Phase 1-2: 6 hours (compatibility validation)
- Phase 3-4: 10 hours (feature integration)
- Phase 5: 2 hours (deployment)
- Buffer time: 2 hours for unexpected issues
