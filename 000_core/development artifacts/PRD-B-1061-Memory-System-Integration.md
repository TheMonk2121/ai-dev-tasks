# Product Requirements Document: Memory System Integration - Heuristic Extractor + Multi-Signal Guard for Overflow Compaction & Knowledge Graph Enhancemen

> ⚠️**Auto-Skip Note**: This PRD builds naturally on B-1060's academic citation quality gates foundation.
> Use this template for memory system optimization and knowledge graph enhancement projects.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Academic Citation System**: B-1060's quality gates and validation framework
- **RAG Evaluation**: RAGChecker 0.1.9, spaCy en_core_web_sm, Python 3.12
- **Memory Systems**: Unified Memory Orchestrator, LTST, Cursor, Go CLI, Prime
- **Heuristic Extractor**: Existing Bedrock texting extraction system
- **Multi-Signal Guard**: Proven precision controls and quality validation
- **Development**: Poetry, pytest, pre-commit, Ruff, Pyrigh

### Repository Layout
```
ai-dev-tasks/
├── scripts/                    # Memory system and extraction scripts
│   ├── memory_overflow_detector.py
│   ├── heuristic_extractor_integration.py
│   └── knowledge_graph_enhancer.py
├── src/                        # Core implementation
│   ├── memory/                # Memory overflow and compaction
│   ├── extraction/            # Heuristic extractor integration
│   ├── validation/            # Multi-signal guard for facts
│   └── knowledge_graph/       # KG enhancement and fact normalization
├── tests/                      # Test suite
│   ├── test_memory_overflow.py
│   ├── test_heuristic_extraction.py
│   └── test_knowledge_graph.py
├── 400_guides/                # Documentation
│   ├── 400_memory-system-guide.md
│   ├── 400_overflow-compaction-guide.md
│   └── 400_knowledge-graph-guide.md
└── 000_core/                  # Core workflows
    ├── 000_backlog.md
    └── 001_create-prd-TEMPLATE.md
```

### Development Patterns
- **Memory System Scripts**: `scripts/` - Overflow detection and compaction
- **Core Implementation**: `src/` - Modular memory, extraction, and KG systems
- **Documentation**: `400_guides/` - Comprehensive usage guides and integration
- **Natural Integration**: Builds on B-1060's quality gates without complex hooks

### Local Developmen
```bash
# Verify memory overflow detection
python3 -c "from src.memory.overflow_detector import MemoryOverflowDetector; print('✅ Memory overflow detection ready!')"

# Verify heuristic extractor integration
python3 -c "from src.extraction.heuristic_integration import HeuristicExtractorIntegration; print('✅ Heuristic extractor integration ready!')"

# Run memory system tests
python3 -m pytest tests/test_memory_overflow.py -v

# Check memory system status
python3 scripts/memory_overflow_detector.py --status
```

### Common Tasks
- **Add new extraction patterns**: Create in `src/extraction/` with existing heuristic logic
- **Update overflow thresholds**: Modify detection criteria in memory overflow detector
- **Enhance knowledge graph**: Add new fact normalization patterns
- **Update documentation**: Maintain 00-12 guide system integration

## 1. Problem Statement

### What's broken?
LTST memory system lacks overflow compaction, leading to context budget explosions in long sessions. No systematic fact extraction or knowledge graph enhancement, and memory rehydration lacks structured fact retrieval. This impacts system performance and knowledge retention.

### Why does it matter?
Memory overflow degrades system performance and user experience. Lack of fact extraction means valuable information is lost, and poor knowledge graph structure limits memory rehydration quality. This affects the overall effectiveness of the memory system.

### What's the opportunity?
Integrate existing heuristic extractor + multi-signal guard for intelligent memory overflow compaction, systematic fact extraction with academic provenance, and enhanced knowledge graph for better memory rehydration and fact retrieval.

## 2. Solution Overview

### What are we building?
Memory system integration that uses heuristic extractor + multi-signal guard for overflow compaction, knowledge graph fact normalization with academic provenance, and unified quality gates that build on B-1060's academic citation foundation.

### How does it work?
Memory overflow detection triggers heuristic extraction, multi-signal guard validates extracted facts, knowledge graph stores normalized facts with academic provenance, and memory rehydration combines session summaries with KG facts for optimal context.

### What are the key features?
- **Memory Overflow Detection**: Soft alarm (85% budget) and hard alarm (100% budget)
- **Heuristic Extraction**: Existing extractor for overflow compaction
- **Multi-Signal Guard**: Proven precision controls for fact validation
- **Knowledge Graph Enhancement**: Triple schema with academic provenance
- **Memory Rehydration**: Session summaries + KG facts for optimal context
- **Natural Integration**: Uses B-1060's quality gates as input

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] **Memory Overflow Detection**: Automatic detection at 85% and 100% budget thresholds
- [ ] **Heuristic Extractor Integration**: Existing extractor wired into memory system
- [ ] **Multi-Signal Guard**: Fact validation using proven precision controls
- [ ] **Knowledge Graph Enhancement**: Triple schema with academic provenance
- [ ] **Memory Rehydration**: Session summaries + KG facts for optimal context
- [ ] **Natural Integration**: Seamless integration with B-1060's quality gates
- [ ] **Performance Metrics**: 150-250 tokens per 1k compacted, 0% baseline degradation
- [ ] **Quality Assurance**: 100% fact provenance tracking, multi-signal validation

### What does success look like?
- **Overflow Prevention**: No more context budget explosions
- **Fact Retention**: Systematic extraction and storage of valuable information
- **Memory Quality**: Enhanced rehydration with structured facts and provenance
- **Performance**: Efficient memory management without quality degradation
- **Integration**: Natural extension of B-1060's academic foundation

### What are the quality gates?
- [ ] **Memory Overflow Detection**: Automatic triggering at budget thresholds
- [ ] **Fact Extraction Quality**: Multi-signal guard validation of extracted facts
- [ ] **Knowledge Graph Integrity**: Proper triple schema and academic provenance
- [ ] **Memory Rehydration Quality**: Optimal context combination without degradation
- [ ] **Baseline Protection**: 0% degradation of RAGChecker baseline metrics

## 4. Technical Approach

### What technology?
- **Python 3.12**: Runtime environment with dependency managemen
- **Heuristic Extractor**: Existing Bedrock texting extraction system
- **Multi-Signal Guard**: Proven precision controls and quality validation
- **Knowledge Graph**: Enhanced triple schema with academic provenance
- **Memory System**: Integration with existing LTST memory orchestrator
- **Natural Integration**: Simple data flow from B-1060's quality gates

### How does it integrate?
- **B-1060 Integration**: Uses academic citation quality gates as input
- **Memory System**: Integrates with existing LTST memory orchestrator
- **Heuristic Extractor**: Wires existing extraction system into memory flow
- **Multi-Signal Guard**: Applies proven validation to extracted facts
- **Knowledge Graph**: Enhances existing KG with academic provenance
- **Simple Interfaces**: Clean data flow without complex preparation hooks

### What are the constraints?
- **Baseline Protection**: Must maintain RAGChecker baseline (0% degradation)
- **Performance**: Overflow compaction must not significantly slow system
- **Integration Complexity**: Must work with existing memory and extraction systems
- **Data Consistency**: Fact extraction must maintain academic provenance integrity
- **Memory Budget**: Must respect existing context budget constraints

## 5. Risks and Mitigation

### What could go wrong?
- **Risk 1**: Heuristic extraction reduces fact quality below acceptable thresholds
- **Risk 2**: Memory overflow detection becomes too aggressive, compacting too early
- **Risk 3**: Knowledge graph enhancement causes performance degradation
- **Risk 4**: Integration with B-1060 creates complex dependencies
- **Risk 5**: Multi-signal guard becomes too restrictive for fact validation

### How do we handle it?
- **Mitigation 1**: Use existing multi-signal guard with proven precision controls
- **Mitigation 2**: Configurable thresholds with gradual enforcement and monitoring
- **Mitigation 3**: Optimize KG operations and implement caching strategies
- **Mitigation 4**: Keep integration simple - natural data flow without complex hooks
- **Mitigation 5**: Use existing guard thresholds that are already proven effective

### What are the unknowns?
- **Performance Impact**: Effect of overflow compaction on system performance
- **Fact Quality**: Correlation between extraction quality and memory rehydration
- **Integration Complexity**: How well existing systems integrate with new memory features
- **Scalability**: How memory system performs with larger knowledge graphs

## 6. Testing Strategy

### What needs testing?
- **Memory Overflow Detection**: Automatic triggering at budget thresholds
- **Heuristic Extraction**: Quality and performance of fact extraction
- **Multi-Signal Guard**: Validation accuracy and performance
- **Knowledge Graph Enhancement**: Triple schema and academic provenance
- **Memory Rehydration**: Context quality and performance
- **Integration Testing**: End-to-end memory system workflow
- **Baseline Protection**: RAGChecker metrics maintenance

### How do we test it?
- **Unit Testing**: Individual component testing with pytes
- **Integration Testing**: End-to-end memory system workflow testing
- **Performance Testing**: Overflow compaction and memory rehydration performance
- **Quality Testing**: Fact extraction quality and multi-signal validation
- **Baseline Testing**: RAGChecker metrics validation to ensure no degradation

### What's the coverage target?
- **Memory Overflow Coverage**: 100% - All detection scenarios tested
- **Extraction Coverage**: 100% - All extraction patterns tested
- **Validation Coverage**: 100% - All multi-signal guard scenarios tested
- **KG Enhancement Coverage**: 100% - All triple schema scenarios tested
- **Integration Coverage**: 100% - All integration points tested
- **Baseline Coverage**: 100% - All RAGChecker metrics validated

## 7. Implementation Plan

### What are the phases?
1. **Phase 1 - Memory Overflow Detection** (1 week): Automatic detection at budget thresholds, integration with existing memory system
2. **Phase 2 - Heuristic Extractor Integration** (1 week): Wire existing extractor into memory flow, implement overflow compaction
3. **Phase 3 - Multi-Signal Guard & Knowledge Graph** (1 week): Fact validation, triple schema enhancement, academic provenance
4. **Phase 4 - Memory Rehydration & Integration** (1 week): Session summaries, KG fact retrieval, B-1060 integration

### What are the dependencies?
- **B-1060**: Academic Citation Quality Gates must be operational
- **B-1045**: RAG Evaluation System for baseline protection
- **Heuristic Extractor**: Existing Bedrock texting extraction system
- **Multi-Signal Guard**: Existing precision controls and validation
- **Memory System**: LTST memory orchestrator must be operational

### What's the timeline?
- **Total Implementation Time**: 4 weeks
- **Phase 1**: 1 week (Memory Overflow Detection)
- **Phase 2**: 1 week (Heuristic Extractor Integration)
- **Phase 3**: 1 week (Multi-Signal Guard & Knowledge Graph)
- **Phase 4**: 1 week (Memory Rehydration & Integration)

---

## **Performance Metrics Summary**

> 📊 **Memory System Integration Data**
> - **Current State**: No overflow compaction, limited fact extraction, basic knowledge graph
> - **Target State**: Intelligent overflow management, systematic fact extraction, enhanced KG with academic provenance
> - **Baseline Protection**: 0% degradation of RAGChecker metrics (Precision: 0.149, Recall: 0.099, F1: 0.112)
> - **Status**: Ready for memory system integration with B-1060 foundation

> 🔍 **Integration Status**
> - **B-1060 Foundation**: 🆕 New - Academic citation quality gates
> - **Memory Overflow**: 🆕 New - Automatic detection and compaction
> - **Heuristic Extraction**: 🆕 New - Integration with existing extractor
> - **Knowledge Graph**: 🆕 New - Enhanced triple schema with provenance
> - **Natural Integration**: 🆕 New - Simple data flow from B-1060

> 📈 **Implementation Phases**
> - **Phase 1**: 🆕 Memory Overflow Detection (1 week)
> - **Phase 2**: 🆕 Heuristic Extractor Integration (1 week)
> - **Phase 3**: 🆕 Multi-Signal Guard & Knowledge Graph (1 week)
> - **Phase 4**: 🆕 Memory Rehydration & Integration (1 week)

> 🎯 **Next Steps for Implementation**
> - **Complete B-1060**: Establish academic citation quality gates foundation
> - **Memory Overflow**: Implement automatic detection and triggering
> - **Heuristic Integration**: Wire existing extractor into memory system
> - **Knowledge Enhancement**: Build enhanced triple schema with academic provenance
> - **Natural Integration**: Simple data flow from B-1060's quality gates
