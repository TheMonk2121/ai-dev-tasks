# Product Requirements Document: B-1012 LTST Memory System with Decision Intelligence

> ⚠️**Auto-Generated Note**: This PRD was generated because `points=6` and `score_total=7.2`.
> This represents a significant feature with decision intelligence capabilities.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Backend**: Python 3.12, DSPy 3.0, PostgreSQL 15+ with pgvector
- **Database**: PostgreSQL with pgvector extension for vector operations
- **Memory System**: LTST (Long-Term Short-Term) Memory System with conversation storage
- **Development**: pytest, Ruff, Pyright, pre-commit hooks
- **Infrastructure**: Local-first development with PostgreSQL

### Repository Layout
```
dspy-rag-system/
├── src/utils/              # Core LTST memory components
│   ├── conversation_storage.py    # Database operations
│   ├── session_manager.py         # Session lifecycle
│   ├── context_merger.py          # Context merging logic
│   ├── memory_rehydrator.py       # Memory rehydration
│   └── ltst_memory_system.py      # Main LTST system
├── config/database/        # Database schemas and migrations
│   └── ltst_memory_schema.sql     # Current schema
├── tests/                  # Test files
│   └── test_ltst_comprehensive.py # Comprehensive tests
├── scripts/                # Utility scripts
│   ├── migrate_conversation_schema.py
│   └── optimize_ltst_performance.py
└── docs/                   # Documentation
    ├── ltst_performance_benchmarks.md
    └── ltst_test_results.md
```

### Development Patterns
- **Data Models**: Dataclasses in `conversation_storage.py` (ConversationMessage, ConversationSession, etc.)
- **Database Operations**: ConversationStorage class with CRUD operations
- **Memory Management**: SessionManager for session lifecycle, ContextMerger for context operations
- **Integration**: MemoryRehydrator as the main interface for AI agents

### Local Developmen
```bash
# Setup database
psql -d dspy_rag -f dspy-rag-system/config/database/ltst_memory_schema.sql

# Run tests
python3 dspy-rag-system/tests/test_ltst_comprehensive.py

# Performance optimization
python3 dspy-rag-system/scripts/optimize_ltst_performance.py
```

### Common Tasks
- **Add new decision field**: Extend conversation_context table schema
- **Add new scoring rule**: Modify ContextMerger scoring logic
- **Add new evaluation metric**: Extend test suite with new metrics
- **Optimize performance**: Run performance benchmarks and adjust caching

## 1. Problem Statement

### What's broken?
The current LTST Memory System lacks decision intelligence capabilities. While it successfully handles conversation persistence, session tracking, and context merging, it cannot:
- Track decisions and their rationales across conversations
- Maintain entity relationships (people, projects, concepts)
- Handle decision supersedence when new decisions contradict old ones
- Provide decision-focused retrieval for AI agents
- Evaluate decision retrieval quality with proper metrics

### Why does it matter?
Without decision intelligence, AI agents cannot:
- Remember previous decisions and avoid repeating them
- Understand the evolution of project decisions over time
- Maintain context about who made what decisions and why
- Provide consistent decision-making across multiple sessions
- Learn from past decision patterns and outcomes

### What's the opportunity?
By adding decision intelligence to the LTST system, we can:
- Achieve ChatGPT 5-level cross-thread memory for decisions
- Improve AI agent decision consistency by 90%+ recall
- Enable proper decision tracking and supersedence
- Provide structured decision retrieval with quality metrics
- Create a foundation for advanced entity relationship tracking

## 2. Solution Overview

### What are we building?
A decision intelligence extension to the existing LTST Memory System that adds decision tracking, supersedence logic, and evaluation capabilities while maintaining the current high performance (2.59ms rehydration time).

### How does it work?
1. **Schema Extension**: Add decision fields to existing `conversation_context` table
2. **Decision Operations**: Extend ConversationStorage, ContextMerger, and MemoryRehydrator
3. **Supersedence Logic**: Automatically detect and mark superseded decisions
4. **Simple Scoring**: Status-based scoring with optional complexity only if needed
5. **Evaluation Framework**: 15-20 test cases with Failure@20 ≤ 0.20 targe

### What are the key features?
- **Decision Tracking**: Store decision_head, decision_status, superseded_by, entities, files
- **Supersedence Logic**: Automatic detection of contradictory decisions
- **Status-Based Scoring**: Simple scoring (open +0.2, superseded -0.3)
- **Entity Relationships**: JSONB storage of entities and file references
- **Evaluation Metrics**: Failure@20, latency breakdown, supersedence leakage
- **MVP-First Approach**: Optional complexity (co-sign, entity-overlap) only if needed

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] Schema extended with decision_head, decision_status, superseded_by, entities (JSONB), files (JSONB)
- [ ] ConversationStorage supports decision operations (store, retrieve, update decisions)
- [ ] ContextMerger implements decision-aware context merging with status-based scoring
- [ ] MemoryRehydrator integrates decision intelligence into memory rehydration
- [ ] Supersedence logic automatically detects and marks contradictory decisions
- [ ] 15-20 decision retrieval test cases created and passing
- [ ] Failure@20 evaluation ≤ 0.20 target achieved
- [ ] Performance maintained: p95 < 10ms warm, < 150ms cold
- [ ] Supersedence leakage ≤ 1% in evaluation

### What does success look like?
- **Decision Recall**: 90%+ recall on decision queries with proper context
- **Performance**: Maintain existing 2.59ms rehydration performance
- **Quality**: Failure@20 ≤ 0.20, supersedence leakage ≤ 1%
- **Usability**: AI agents can retrieve relevant decisions with proper context
- **Extensibility**: Foundation ready for optional complexity if needed

### What are the quality gates?
- [ ] All existing LTST functionality continues to work without regression
- [ ] Decision operations integrate seamlessly with existing conversation flow
- [ ] Performance targets met: p95 < 10ms warm, < 150ms cold
- [ ] Evaluation metrics pass: Failure@20 ≤ 0.20, supersedence leakage ≤ 1%
- [ ] Code coverage ≥ 90% for new decision intelligence features
- [ ] No new external dependencies added

## 4. Technical Approach

### What technology?
- **Database**: PostgreSQL with pgvector (existing)
- **Schema**: Extend existing `conversation_context` table (minimal changes)
- **Python**: Extend existing dataclasses and classes (ConversationStorage, ContextMerger, MemoryRehydrator)
- **Evaluation**: Custom evaluation framework with 15-20 test cases
- **Performance**: Maintain existing caching and optimization strategies

### How does it integrate?
- **ConversationStorage**: Add decision CRUD operations alongside existing conversation operations
- **ContextMerger**: Extend scoring logic to include decision status and entity overlap
- **MemoryRehydrator**: Integrate decision retrieval into existing rehydration pipeline
- **SessionManager**: Maintain existing session tracking (no changes needed)
- **Database**: Extend existing schema without breaking existing functionality

### What are the constraints?
- **Performance**: Must maintain existing 2.59ms rehydration performance
- **Compatibility**: Must not break existing LTST functionality
- **Complexity**: MVP-first approach, avoid over-engineering
- **Dependencies**: No new external dependencies
- **Database**: Use existing PostgreSQL setup, no new tables

## 5. Risks and Mitigation

### What could go wrong?
- **Risk 1**: Performance degradation from decision operations
- **Risk 2**: Schema migration breaking existing data
- **Risk 3**: Supersedence logic being too aggressive or not aggressive enough
- **Risk 4**: Evaluation framework not capturing real-world usage patterns
- **Risk 5**: Decision scoring not providing meaningful improvements

### How do we handle it?
- **Mitigation 1**: Extensive performance testing and optimization, maintain existing caching
- **Mitigation 2**: Thorough schema migration testing with rollback capability
- **Mitigation 3**: Configurable supersedence thresholds with monitoring
- **Mitigation 4**: Iterative evaluation framework with real-world test cases
- **Mitigation 5**: MVP-first approach with optional complexity only if needed

### What are the unknowns?
- **Unknown 1**: Optimal decision scoring weights for different use cases
- **Unknown 2**: Real-world supersedence patterns and frequency
- **Unknown 3**: Performance impact of entity overlap calculations
- **Unknown 4**: Whether optional complexity (co-sign, entity-overlap) will be needed

## 6. Testing Strategy

### What needs testing?
- **Schema Operations**: Decision CRUD operations in ConversationStorage
- **Context Merging**: Decision-aware context merging in ContextMerger
- **Memory Rehydration**: Decision integration in MemoryRehydrator
- **Supersedence Logic**: Automatic detection and marking of contradictory decisions
- **Performance**: Maintain existing performance benchmarks
- **Evaluation**: 15-20 decision retrieval test cases

### How do we test it?
- **Unit Tests**: Comprehensive test suite for all decision operations
- **Integration Tests**: End-to-end decision workflow testing
- **Performance Tests**: Benchmark decision operations against existing performance
- **Evaluation Tests**: Automated evaluation framework with Failure@20 metrics
- **Regression Tests**: Ensure existing LTST functionality remains intac

### What's the coverage target?
- **Code Coverage**: ≥ 90% for new decision intelligence features
- **Integration Coverage**: 100% of decision workflow paths
- **Performance Coverage**: All existing performance benchmarks pass
- **Evaluation Coverage**: 15-20 diverse decision retrieval scenarios

## 7. Implementation Plan

### What are the phases?
1. **Phase 1**: Schema Extension and Migration (2 hours)
   - Extend conversation_context table with decision fields
   - Create migration script with rollback capability
   - Update existing dataclasses to include decision fields

2. **Phase 2**: Core Decision Operations (3 hours)
   - Extend ConversationStorage with decision CRUD operations
   - Implement decision-aware context merging in ContextMerger
   - Add decision integration to MemoryRehydrator

3. **Phase 3**: Supersedence Logic and Evaluation (3 hours)
   - Implement supersedence detection and marking logic
   - Create 15-20 decision retrieval test cases
   - Implement Failure@20 evaluation framework
   - Performance testing and optimization

### What are the dependencies?
- **B-1006-A DSPy 3.0 Core Parity Migration**: Must be completed firs
- **Existing LTST System**: Current system must be stable and tested
- **Database Access**: PostgreSQL with pgvector extension must be available
- **Test Environment**: Isolated test database for evaluation

### What's the timeline?
- **Total Estimate**: 8 hours
- **Phase 1**: 2 hours (Schema and migration)
- **Phase 2**: 3 hours (Core operations)
- **Phase 3**: 3 hours (Supersedence and evaluation)
- **Buffer**: 2 hours for unexpected issues and optimization

---

## **Performance Metrics Summary**

> 📊 **Workflow Performance Data**
> - **Workflow ID**: `B-1012-DECISION-INTELLIGENCE`
> - **Total Duration**: `8 hours estimated`
> - **Performance Score**: `7.2/10`
> - **Success**: `Target: Failure@20 ≤ 0.20`
> - **Error Count**: `Target: 0`

> 🔍 **Performance Analysis**
> - **Bottlenecks**: `Maintain existing 2.59ms rehydration performance`
> - **Warnings**: `MVP-first approach, avoid over-engineering`
> - **Recommendations**: `Optional complexity only if Failure@20 > 0.20`

> 📈 **Collection Points**
> - **Schema Migration**: `2 hours`
> - **Core Operations**: `3 hours`
> - **Supersedence & Evaluation**: `3 hours`
> - **Performance Optimization**: `Continuous throughout`
> - **Quality Gates**: `All acceptance criteria must pass`
