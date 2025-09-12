# Task List: B-1018 Text Analysis & Knowledge Discovery System

## 🎯 Project Overview

**Project**: B-1018 Text Analysis & Knowledge Discovery System: InfraNodus-Style Cognitive Scaffolding
**Implementation Date**: TBD
**Status**: ⏳ PENDING - Ready for implementation
**Priority**: 🔥 Critical (8 points)

## 📋 Implementation Summary

Comprehensive text analysis and knowledge discovery system using existing graph infrastructure, with co-occurrence analysis, gap detection, bridge generation, and market study features to enhance cognitive scaffolding and research capabilities.

## 🎯 Success Criteria

- **Text Analysis**: Co-occurrence graphs generated from text documents
- **Gap Detection**: Structural gaps identified between concept clusters
- **Bridge Generation**: AI-powered bridge questions/ideas created using DSPy
- **Market Study**: Supply/demand analysis capabilities operational
- **Integration**: Seamless integration with existing graph infrastructure
- **Performance**: Analysis completes within 30 seconds for typical documents
- **Evaluation**: Baseline RAGChecker score improves by ≥5 points, context utilization improves by ≥10%

## 📊 Evaluation Strategy

### Before Implementation
- Run baseline RAGChecker evaluation to establish current performance baseline
- Document current context utilization metrics
- Establish gap detection baseline with test documents

### After Implementation
- Re-run baseline RAGChecker evaluation to measure improvements
- Measure context utilization improvements
- Validate gap detection finds ≥3 meaningful gaps in test documents

### Quality Gates
- [ ] Baseline RAGChecker score improves by ≥5 points
- [ ] Context utilization improves by ≥10%
- [ ] Gap detection finds ≥3 meaningful gaps in test documents
- [ ] All existing tests pass
- [ ] Text analysis completes within 30 seconds for typical documents
- [ ] Output format is compatible with GraphDataProvider

---

## 🚀 Phase 1: Baseline Evaluation & Text Analysis Foundation (4 hours)

### Task 1.1: Establish Baseline Evaluation
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **1.1.1**: Run current baseline RAGChecker evaluation
  ```bash
  python3 scripts/ragchecker_official_evaluation.py
  ```
- [ ] **1.1.2**: Document baseline performance metrics
  - Overall RAGChecker score
  - Context utilization metrics
  - Response quality metrics
- [ ] **1.1.3**: Create baseline evaluation repor
  - Save results to `metrics/baseline_evaluations/B-1018_baseline.json`
  - Document current performance state

#### Acceptance Criteria:
- [ ] Baseline evaluation completed successfully
- [ ] Baseline metrics documented and saved
- [ ] Current performance state established

### Task 1.2: Text-to-Co-Occurrence Graph Adapter
**Duration**: 2 hours
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **1.2.1**: Create `src/utils/text_cooc_adapter.py`
  ```python
  class TextCoOccurrenceAdapter:
      def build_graph(self, text: str, window=4, min_freq=2) -> GraphData:
          # Tokenization with nltk.word_tokenize
          # Co-occurrence analysis with sliding window
          # Node metadata: frequency, centrality, community
          # Edge metadata: weight, co_occurrence_coun
          # Return V1 contract compatible forma
  ```
- [ ] **1.2.2**: Implement tokenization and preprocessing
  - NLTK word tokenization
  - Stopword removal
  - Optional lemmatization
- [ ] **1.2.3**: Implement co-occurrence analysis
  - Sliding window (3-5 words)
  - Edge weight calculation
  - Frequency-based filtering

#### Acceptance Criteria:
- [ ] Text-to-graph conversion working
- [ ] Co-occurrence analysis functional
- [ ] V1 API contract compatibility verified
- [ ] Performance: <3s for 10k word documents

### Task 1.3: Graph Metrics Computation
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **1.3.1**: Create `src/utils/graph_metrics.py`
  ```python
  def betweenness_centrality(nodes, edges) -> Dict[str, float]
  def community_labels(nodes, edges) -> Dict[str, int]  # Louvain algorithm
  def influence_ranking(nodes, edges) -> List[str]
  ```
- [ ] **1.3.2**: Integrate with existing UMAP layou
- [ ] **1.3.3**: Performance optimization for large graphs

#### Acceptance Criteria:
- [ ] Graph metrics computation functional
- [ ] UMAP integration working
- [ ] Performance: <2s for 10k word documents

---

## 🔍 Phase 2: Gap Detection System (3 hours)

### Task 2.1: Gap Detection Algorithm
**Duration**: 2 hours
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **2.1.1**: Create `src/utils/gap_detector.py`
  ```python
  def find_structural_gaps(nodes, edges, communities) -> List[GapCandidate]:
      # Gap scoring: few edges between clusters, high centrality near boundary
      # Return: cluster_a, cluster_b, score, exemplar_terms, suggested_bridge
  ```
- [ ] **2.1.2**: Implement gap scoring algorithm
  - Edge density analysis between clusters
  - Centrality analysis near cluster boundaries
  - Gap candidate identification
- [ ] **2.1.3**: Integration with entity-aware memory rehydration

#### Acceptance Criteria:
- [ ] Gap detection algorithm functional
- [ ] Gap scoring working correctly
- [ ] Integration with memory system verified
- [ ] Performance: <1s for typical concept graphs

### Task 2.2: Gap Detection API
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **2.2.1**: Add `/graph-gaps?source=text_cooc` endpoin
- [ ] **2.2.2**: Top N gaps exposure
- [ ] **2.2.3**: Integration with existing Flask infrastructure

#### Acceptance Criteria:
- [ ] Gap detection API functional
- [ ] Top N gaps exposed correctly
- [ ] Integration with Flask verified

---

## 🤖 Phase 3: Bridge Generation (3 hours)

### Task 3.1: DSPy Bridge Generator
**Duration**: 2 hours
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **3.1.1**: Create `src/dspy_modules/bridge_generator.py`
  ```python
  class BridgeQuestionGenerator(dspy.Module):
      def forward(self, gap_candidate: GapCandidate) -> str

  class BridgeIdeaGenerator(dspy.Module):
      def forward(self, gap_candidate: GapCandidate) -> str
  ```
- [ ] **3.1.2**: Integration with existing Reasoning Task pattern
- [ ] **3.1.3**: Entity-aware prompts using LTST memory context

#### Acceptance Criteria:
- [ ] Bridge generation DSPy modules functional
- [ ] Integration with Reasoning Task pattern verified
- [ ] Entity-aware prompts working
- [ ] Performance: <5s per gap using DSPy

### Task 3.2: Bridge Generation Integration
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **3.2.1**: Integration with gap detection system
- [ ] **3.2.2**: Structured questions/ideas saved to notes system
- [ ] **3.2.3**: Integration with existing DSPy infrastructure

#### Acceptance Criteria:
- [ ] Bridge generation integrated with gap detection
- [ ] Structured output saved correctly
- [ ] DSPy integration verified

---

## 📊 Phase 4: Market Study Features (2 hours)

### Task 4.1: Market Study Implementation
**Duration**: 1.5 hours
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **4.1.1**: Create `src/utils/market_study.py`
  ```python
  def related_queries(focus_term: str, locale: str = "en-US") -> List[str]
  def search_results(focus_term: str, locale: str = "en-US", k: int = 40) -> List[Dict]
  ```
- [ ] **4.1.2**: Configurable API keys for local-first approach
- [ ] **4.1.3**: Cache results in `artifacts/market_study/` with TTL

#### Acceptance Criteria:
- [ ] Market study features functional
- [ ] Local-first approach working
- [ ] Caching implemented correctly

### Task 4.2: Supply vs Demand Analysis
**Duration**: 0.5 hours
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **4.2.1**: Supply vs Demand comparison logic
- [ ] **4.2.2**: Highlight terms present in demand but missing in supply
- [ ] **4.2.3**: Integration with existing analysis pipeline

#### Acceptance Criteria:
- [ ] Supply vs demand analysis functional
- [ ] Term highlighting working
- [ ] Integration verified

---

## 🔧 Phase 5: Integration & Optimization (4 hours)

### Task 5.1: GraphDataProvider Extension
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **5.1.1**: Add `get_text_cooc_graph_data(text_id: str, max_nodes: int = None)` method
- [ ] **5.1.2**: Add `get_market_study_graph_data(term: str, study_type: "demand"|"supply")` method
- [ ] **5.1.3**: Maintain V1 API contract compatibility
- [ ] **5.1.4**: Cache text analysis results in `artifacts/text_analysis/`

#### Acceptance Criteria:
- [ ] GraphDataProvider extension functional
- [ ] V1 API contract compatibility maintained
- [ ] Caching implemented correctly
- [ ] Error handling graceful degradation

### Task 5.2: NiceGUI Visualization Enhancements
**Duration**: 1.5 hours
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **5.2.1**: Add "Text Analysis" tab alongside existing RAG/Schema tabs
- [ ] **5.2.2**: Multi-select node hiding with `ui.checkbox_group`
- [ ] **5.2.3**: "Show Latent Topics" button for auto-hiding top frequency nodes
- [ ] **5.2.4**: Gap highlighting with visual indicators
- [ ] **5.2.5**: Bridge suggestions side panel

#### Acceptance Criteria:
- [ ] Text Analysis tab functional
- [ ] Multi-select node hiding working
- [ ] Gap highlighting visible
- [ ] Bridge suggestions displayed correctly

### Task 5.3: Entity Integration
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **5.3.1**: Integration with existing entity extraction system
- [ ] **5.3.2**: Entity-aware concept mapping
- [ ] **5.3.3**: Entity metadata integration with graph nodes

#### Acceptance Criteria:
- [ ] Entity integration functional
- [ ] Entity-aware concept mapping working
- [ ] Entity metadata integrated correctly

### Task 5.4: Performance Optimization
**Duration**: 0.5 hours
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **5.4.1**: Caching layer for co-occurrence analysis results
- [ ] **5.4.2**: Incremental processing for new documents
- [ ] **5.4.3**: Memory-efficient graph construction

#### Acceptance Criteria:
- [ ] Caching implemented correctly
- [ ] Incremental processing functional
- [ ] Memory efficiency verified
- [ ] Performance: <30s for typical documents

---

## 🧪 Phase 6: Testing & Evaluation (2 hours)

### Task 6.1: Comprehensive Testing
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **6.1.1**: Unit tests for all components
  ```bash
  pytest dspy-rag-system/tests/test_text_analysis.py -v
  ```
- [ ] **6.1.2**: Integration tests with existing systems
- [ ] **6.1.3**: Performance benchmarks
- [ ] **6.1.4**: Quality testing for gap detection and bridge generation

#### Acceptance Criteria:
- [ ] All unit tests passing (90% coverage)
- [ ] Integration tests passing
- [ ] Performance benchmarks me
- [ ] Quality metrics achieved

### Task 6.2: Final Evaluation & Improvement Measuremen
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **6.2.1**: Run final baseline RAGChecker evaluation
  ```bash
  python3 scripts/ragchecker_official_evaluation.py
  ```
- [ ] **6.2.2**: Measure improvement metrics
  - Compare baseline vs final RAGChecker score
  - Measure context utilization improvement
  - Validate gap detection performance
- [ ] **6.2.3**: Document final evaluation results
  - Save to `metrics/baseline_evaluations/B-1018_final.json`
  - Create improvement summary repor

#### Acceptance Criteria:
- [ ] Final evaluation completed successfully
- [ ] Improvement metrics measured and documented
- [ ] Quality gates validated:
  - [ ] Baseline RAGChecker score improved by ≥5 points
  - [ ] Context utilization improved by ≥10%
  - [ ] Gap detection finds ≥3 meaningful gaps in test documents
  - [ ] All existing tests pass
  - [ ] Text analysis completes within 30 seconds for typical documents
  - [ ] Output format is compatible with GraphDataProvider

---

## 📚 Phase 7: Documentation & Integration (2 hours)

### Task 7.1: Documentation Updates
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **7.1.1**: Update 00-12 guide system
- [ ] **7.1.2**: Create usage guide for text analysis features
- [ ] **7.1.3**: Update cognitive scaffolding guide
- [ ] **7.1.4**: Integration documentation with existing systems

#### Acceptance Criteria:
- [ ] All documentation updated
- [ ] Usage guide comprehensive and clear
- [ ] Integration documentation complete

### Task 7.2: Scribe Integration
**Duration**: 1 hour
**Priority**: 🔥 Critical

#### Subtasks:
- [ ] **7.2.1**: Create `scripts/scribe_text_analysis.py`
  ```python
  # CLI script for batch text analysis of documents
  # Input: documents/, notes/, transcripts/ directories
  # Output: artifacts/text_analysis/{document_id}_graph.json
  ```
- [ ] **7.2.2**: Integration with Scribe queue (B-1009)
- [ ] **7.2.3**: Mermaid generation for concept maps and gap visualizations

#### Acceptance Criteria:
- [ ] Scribe integration functional
- [ ] Batch processing working correctly
- [ ] Mermaid generation functional

---

## 📊 Quality Gates Summary

### Performance Targets
- [ ] **Text-to-graph conversion**: <3s for 10k word documents
- [ ] **Gap detection**: <1s for typical concept graphs
- [ ] **Bridge generation**: <5s per gap using DSPy
- [ ] **Overall analysis**: <30s for typical documents

### Evaluation Metrics
- [ ] **Baseline RAGChecker score improves by ≥5 points**
- [ ] **Context utilization improves by ≥10%**
- [ ] **Gap detection finds ≥3 meaningful gaps in test documents**
- [ ] **All existing tests pass**
- [ ] **Output format is compatible with GraphDataProvider**

### Integration Requirements
- [ ] **Entity integration works**: Existing entity extraction system integration functional
- [ ] **GraphDataProvider compatibility**: V1 API contract maintained
- [ ] **Memory system integration**: Seamless integration with existing memory systems
- [ ] **DSPy integration**: Bridge generation using existing DSPy infrastructure

---

## 🎯 Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | 4 hours | Baseline evaluation, text analysis foundation |
| **Phase 2** | 3 hours | Gap detection system |
| **Phase 3** | 3 hours | Bridge generation with DSPy |
| **Phase 4** | 2 hours | Market study features |
| **Phase 5** | 4 hours | Integration & optimization |
| **Phase 6** | 2 hours | Testing & evaluation |
| **Phase 7** | 2 hours | Documentation & integration |

**Total Implementation Time**: 20 hours

---

## 🔍 Risk Mitigation

### Technical Risks
- **Performance degradation**: Implement caching and optimization strategies
- **Integration complexity**: Maintain V1 API contract compatibility
- **Quality issues**: Comprehensive testing and evaluation framework

### Evaluation Risks
- **Baseline measurement**: Use existing RAGChecker evaluation system
- **Improvement validation**: Clear quality gates with measurable targets
- **Regression prevention**: Automated testing and quality gates

---

## 📈 Success Metrics

### Primary Metrics
- **Baseline RAGChecker score improvement**: ≥5 points
- **Context utilization improvement**: ≥10%
- **Gap detection accuracy**: ≥3 meaningful gaps in test documents

### Secondary Metrics
- **Performance**: <30s for typical document analysis
- **Integration**: Seamless integration with existing systems
- **Documentation**: Comprehensive usage guides and integration docs

---

*Last updated: [Current Date]*
*Status: Ready for implementation*
