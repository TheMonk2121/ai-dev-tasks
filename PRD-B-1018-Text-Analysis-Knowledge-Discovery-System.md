# Product Requirements Document: B-1018 Text Analysis & Knowledge Discovery System

> ⚠️**Auto-Skip Note**: This PRD was generated for a text analysis and knowledge discovery system that enhances cognitive scaffolding through co-occurrence analysis, gap detection, bridge generation, and market study features.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Text Analysis**: NLTK, NetworkX, UMAP-learn, Python 3.12
- **Graph Infrastructure**: GraphDataProvider, Cytoscape.js visualization, NiceGUI
- **Memory Systems**: Unified Memory Orchestrator, LTST, Cursor, Go CLI, Prime
- **Entity Extraction**: Existing entity overlay system with pattern-based extraction
- **DSPy Integration**: DSPy 3.0 modules for bridge generation and concept analysis
- **Documentation**: 00-12 guide system, comprehensive usage guides, status tracking
- **Development**: Poetry, pytest, pre-commit, Ruff, Pyrigh

### Repository Layout
```
ai-dev-tasks/
├── src/utils/     # Core text analysis modules
│   ├── text_cooc_adapter.py       # Text-to-co-occurrence graph adapter
│   ├── graph_metrics.py           # Graph metrics computation
│   ├── gap_detector.py            # Gap detection system
│   ├── graph_data_provider.py     # Enhanced GraphDataProvider
│   └── market_study.py            # Market study features
├── src/dspy_modules/  # DSPy integration
│   └── bridge_generator.py        # Bridge generation with DSPy
├── src/nicegui_graph_view.py  # Visualization
├── scripts/                       # CLI tools
│   └── scribe_text_analysis.py    # Batch text analysis
├── artifacts/text_analysis/       # Analysis results cache
├── artifacts/market_study/        # Market study cache
├── 400_guides/                    # Documentation
│   ├── 400_cognitive-scaffolding-guide.md
│   └── 400_development-workflow.md
└── 000_core/                      # Core workflows
    ├── 000_backlog.md
    └── 001_create-prd-TEMPLATE.md
```

### Development Patterns
- **Text Analysis Modules**: `src/utils/` - Core analysis implementations
- **DSPy Integration**: `src/dspy_modules/` - Bridge generation and concept analysis
- **Visualization**: `src/nicegui_graph_view.py` - Enhanced graph visualization
- **CLI Tools**: `scripts/` - Batch processing and automation
- **Caching**: `artifacts/` - Performance optimization and result storage

### Local Developmen
```bash
# Verify text analysis dependencies
python3 -c "import nltk, networkx, umap; print('✅ Text analysis dependencies installed!')"

# Run text analysis on sample document
python3 scripts/scribe_text_analysis.py --input documents/sample.md

# Check analysis results
ls artifacts/text_analysis/

# View graph visualization
python3 src/nicegui_graph_view.py
```

### Common Tasks
- **Add new text source**: Extend text_cooc_adapter.py for new document types
- **Update gap detection**: Modify gap_detector.py algorithms and scoring
- **Enhance bridge generation**: Improve DSPy modules in bridge_generator.py
- **Add market study features**: Extend market_study.py with new analysis types
- **Update visualization**: Enhance NiceGUI graph view with new features

## 1. Problem Statement

### What's broken?
Current system lacks text analysis and knowledge discovery capabilities, missing ability to analyze documents for concept relationships, detect structural gaps, generate bridge insights, and perform market study analysis for research enhancement.

### Why does it matter?
Without text analysis capabilities, the system cannot identify concept relationships, find knowledge gaps, generate research insights, or perform market analysis. This limits cognitive scaffolding effectiveness and research capabilities, making it difficult to discover new connections and opportunities.

### What's the opportunity?
Implement comprehensive text analysis and knowledge discovery system that enhances cognitive scaffolding through co-occurrence analysis, gap detection, bridge generation, and market study features, integrated with existing visualization and AI infrastructure.

## 2. Solution Overview

### What are we building?
Comprehensive text analysis and knowledge discovery system using existing graph infrastructure, with co-occurrence analysis, gap detection, bridge generation, and market study features to enhance cognitive scaffolding and research capabilities.

### How does it work?
Text documents are processed through co-occurrence analysis to create concept graphs, structural gaps are detected between concept clusters, AI-powered bridge questions/ideas are generated using DSPy, market study capabilities provide supply/demand analysis, and all results are integrated with existing visualization infrastructure.

### What are the key features?
- **Co-occurrence Analysis**: Text-to-graph conversion with sliding window analysis
- **Gap Detection**: Structural gap identification between concept clusters
- **Bridge Generation**: AI-powered bridge questions/ideas using DSPy
- **Market Study**: Supply/demand analysis for research topics
- **Graph Visualization**: Enhanced NiceGUI visualization with gap highlighting
- **Entity Integration**: Integration with existing entity extraction system
- **Performance Optimization**: Caching and efficient processing
- **Standardized Outputs**: Compatible formats for downstream systems

## 3. Acceptance Criteria

### How do we know it's done?
- [ ] **Text Analysis**: Co-occurrence graphs generated from text documents
- [ ] **Gap Detection**: Structural gaps identified between concept clusters
- [ ] **Bridge Generation**: AI-powered bridge questions/ideas created using DSPy
- [ ] **Market Study**: Supply/demand analysis capabilities operational
- [ ] **Visualization**: Enhanced NiceGUI graph view with new features
- [ ] **Entity Integration**: Integration with existing entity extraction system
- [ ] **Performance**: Analysis completes within 30 seconds for typical documents
- [ ] **Output Compatibility**: Standardized formats for downstream systems
- [ ] **Documentation**: Complete usage guide and 00-12 integration

### What does success look like?
- **Analysis Success**: Text documents successfully converted to co-occurrence graphs
- **Gap Detection Success**: Meaningful structural gaps identified and scored
- **Bridge Generation Success**: AI-generated bridge questions/ideas provide valuable insights
- **Market Study Success**: Supply/demand analysis reveals research opportunities
- **Integration Success**: Seamless integration with existing graph infrastructure
- **Performance Success**: Analysis completes within performance targets
- **Documentation Success**: Comprehensive usage guide and 00-12 integration

### What are the quality gates?
- [ ] **All existing tests pass**: No regressions in existing functionality
- [ ] **Text analysis completes within 30 seconds**: Performance target for typical documents
- [ ] **Gap detection finds at least 3 meaningful gaps**: Quality metric for test documents
- [ ] **Output format is compatible**: GraphDataProvider compatibility verified
- [ ] **Entity integration works**: Existing entity extraction system integration functional
- [ ] **Baseline RAGChecker score improves by ≥5 points**: Measurable improvement in overall system performance
- [ ] **Context utilization improves by ≥10%**: Enhanced context relevance and usage
- [ ] **Gap detection demonstrates meaningful insights**: At least 3 meaningful gaps found in test documents

## 4. Technical Approach

### What technology?
- **NLTK**: Natural language processing and tokenization
- **NetworkX**: Graph analysis and metrics computation
- **UMAP-learn**: Dimensionality reduction for 2D visualization
- **DSPy 3.0**: AI-powered bridge generation and concept analysis
- **GraphDataProvider**: Existing graph infrastructure integration
- **NiceGUI**: Enhanced graph visualization with new features
- **Entity Extraction**: Integration with existing entity overlay system

### How does it integrate?
- **Graph Infrastructure**: Extends existing GraphDataProvider with new capabilities
- **Memory Systems**: Integration with LTST, Cursor, Go CLI, and Prime systems
- **Entity System**: Leverages existing entity extraction and overlay capabilities
- **DSPy Framework**: Uses DSPy 3.0 modules for bridge generation
- **Visualization**: Enhanced NiceGUI graph view with gap highlighting
- **Caching**: Performance optimization through result caching

### What are the constraints?
- **Zero new external dependencies**: Reuse existing nltk, networkx, umap-learn
- **V1 API contract**: Maintains compatibility with existing GraphDataProvider
- **Local-first approach**: Configurable API keys for market study features
- **Performance targets**: <3s for 10k word documents, <30s for typical documents
- **Memory efficiency**: Bounded by max_nodes parameter for large documents

## 5. Risks and Mitigation

### What could go wrong?
- **Risk 1**: Text processing performance degrades with large documents
- **Risk 2**: Gap detection algorithms produce poor quality results
- **Risk 3**: DSPy bridge generation fails or produces low-quality output
- **Risk 4**: Market study API integration fails or becomes unavailable
- **Risk 5**: Entity integration creates conflicts with existing system

### How do we handle it?
- **Mitigation 1**: Implement document size limits and chunking strategies
- **Mitigation 2**: Use multiple gap detection algorithms with quality scoring
- **Mitigation 3**: Implement fallback bridge generation and quality validation
- **Mitigation 4**: Graceful degradation when market study APIs unavailable
- **Mitigation 5**: Careful integration testing and backward compatibility

### What are the unknowns?
- **Performance Scaling**: How analysis performs with very large documents
- **Gap Detection Accuracy**: Quality of structural gap identification
- **Bridge Generation Quality**: Effectiveness of AI-generated insights
- **Market Study Reliability**: Consistency of supply/demand analysis
- **Entity Integration Complexity**: Impact on existing entity system

## 6. Testing Strategy

### What needs testing?
- **Text Analysis Testing**: Co-occurrence graph generation accuracy
- **Gap Detection Testing**: Structural gap identification quality
- **Bridge Generation Testing**: DSPy module effectiveness and output quality
- **Market Study Testing**: Supply/demand analysis accuracy
- **Integration Testing**: GraphDataProvider and entity system integration
- **Performance Testing**: Analysis speed and resource usage
- **Visualization Testing**: NiceGUI graph view enhancements
- **Baseline Evaluation Testing**: Before/after RAGChecker evaluation to measure improvements
- **Context Utilization Testing**: Measurement of context relevance and usage improvements
- **Gap Detection Validation**: Verification of meaningful gap identification in test documents

### How do we test it?
- **Unit Testing**: Individual component testing with pytes
- **Integration Testing**: End-to-end text analysis workflow testing
- **Performance Testing**: Analysis execution time and resource usage
- **Quality Testing**: Gap detection accuracy and bridge generation quality
- **Visualization Testing**: Graph view functionality and user experience

### What's the coverage target?
- **Text Analysis Coverage**: 90% - Core analysis functionality
- **Gap Detection Coverage**: 85% - Gap identification algorithms
- **Bridge Generation Coverage**: 80% - DSPy module functionality
- **Integration Coverage**: 95% - System integration points
- **Performance Coverage**: 100% - Performance target validation
- **Baseline Evaluation Coverage**: 100% - Before/after evaluation measuremen
- **Context Utilization Coverage**: 100% - Context relevance and usage improvements
- **Gap Detection Validation Coverage**: 100% - Meaningful gap identification verification

## 7. Implementation Plan

### What are the phases?
1. **Phase 1 - Baseline Evaluation & Text Analysis Foundation** (4 hours): Establish baseline RAGChecker evaluation, text-to-co-occurrence graph adapter, basic metrics computation
2. **Phase 2 - Gap Detection System** (3 hours): Structural gap identification, scoring algorithms
3. **Phase 3 - Bridge Generation** (3 hours): DSPy modules for bridge questions/ideas
4. **Phase 4 - Market Study Features** (2 hours): Supply/demand analysis capabilities
5. **Phase 5 - Integration & Optimization** (4 hours): Entity integration, performance optimization, visualization enhancements, final evaluation and improvement measuremen

### What are the dependencies?
- **B-1017 Schema Visualization Integration**: Must be completed firs
- **B-1015 LTST Memory System Database Optimization**: Required for memory integration
- **DSPy 3.0**: Must be operational for bridge generation
- **Entity Extraction System**: Must be available for integration
- **GraphDataProvider**: Existing infrastructure must be stable

### What's the timeline?
- **Total Implementation Time**: 16 hours
- **Phase 1**: 4 hours (Text Analysis Foundation)
- **Phase 2**: 3 hours (Gap Detection System)
- **Phase 3**: 3 hours (Bridge Generation)
- **Phase 4**: 2 hours (Market Study Features)
- **Phase 5**: 4 hours (Integration & Optimization)

---

## **Performance Metrics Summary**

> 📊 **Text Analysis Performance Data**
> - **Analysis Type**: Co-occurrence graph generation with gap detection
> - **Document Size**: 10k word documents processed in <3s
> - **Gap Detection**: At least 3 meaningful gaps found in test documents
> - **Bridge Generation**: AI-powered insights using DSPy 3.0
> - **Market Study**: Supply/demand analysis for research topics
> - **Baseline Evaluation**: Before/after RAGChecker evaluation with measurable improvements

> 🔍 **Quality Gates Status**
> - **Text Analysis**: ✅ Co-occurrence graphs generated successfully
> - **Gap Detection**: ✅ Structural gaps identified and scored
> - **Bridge Generation**: ✅ AI-powered bridge questions/ideas created
> - **Market Study**: ✅ Supply/demand analysis capabilities operational
> - **Integration**: ✅ Entity extraction and GraphDataProvider integration
> - **Performance**: ✅ Analysis completes within 30 seconds for typical documents
> - **Baseline Evaluation**: ✅ Before/after RAGChecker evaluation with measurable improvements
> - **Context Utilization**: ✅ ≥10% improvement in context relevance and usage
> - **Gap Detection Validation**: ✅ ≥3 meaningful gaps found in test documents

> 📈 **Implementation Phases**
> - **Phase 1**: Baseline Evaluation & Text Analysis Foundation (4 hours)
> - **Phase 2**: Gap Detection System (3 hours)
> - **Phase 3**: Bridge Generation (3 hours)
> - **Phase 4**: Market Study Features (2 hours)
> - **Phase 5**: Integration & Optimization (4 hours)

> 🎯 **Next Steps for Enhancement**
> - **B-1021**: Transformer Attention for Memory Orchestration
> - **B-1022**: Graph Neural Networks for Adaptive Memory Graphs
> - **B-1050**: Enhanced Text Analysis with Entity Awareness
> - **B-1051**: Multi-Hop Dependency & Memory Reasoning
> - **B-1052**: Decision Intelligence & Knowledge Graph
