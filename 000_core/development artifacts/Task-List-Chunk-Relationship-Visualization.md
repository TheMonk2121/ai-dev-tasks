<!-- ANCHOR_KEY: chunk-relationship-visualization -->
<!-- ANCHOR_PRIORITY: 20 -->

<!-- ROLE_PINS: ["coder", "implementer"] -->
# Task List: Chunk Relationship Visualization & /graph-data API (V1)

## Overview

Implement a shared API and dual UI system for visualizing relationships between document chunks in the RAG system. The project includes a GraphDataProvider utility, Flask cluster visualization, NiceGUI network graphs, and comprehensive testing and documentation.

## Implementation Phases

### Phase 1: Core Infrastructure (1-2 days)

#### Task T1: GraphDataProvider + Cache + Feature Flag
**Priority:** Critical
**Estimated Time:** 1 day
**Dependencies:** None

**Description:** Implement the core GraphDataProvider utility class with UMAP caching, database integration, and feature flag protection.

**Acceptance Criteria:**
- [ ] GraphDataProvider class implemented in `src/utils/graph_data_provider.py`
- [ ] `get_graph_data()` method returns V1 schema with nodes/edges/elapsed_ms/v
- [ ] `get_cluster_data()` method computes UMAP 2D coordinates
- [ ] UMAP cache keyed by corpus snapshot (`MAX(documents.updated_at)`)
- [ ] Cache invalidation triggers on document changes
- [ ] Feature flag protection for `/graph-data` endpoin
- [ ] Max nodes limit enforced with `truncated: true` flag
- [ ] Performance: p50 ≤ 200ms, p95 ≤ 500ms

**Testing Requirements:**
- [ ] **Unit Tests**
  - [ ] Test `get_graph_data()` with various query parameters
  - [ ] Test `get_cluster_data()` with UMAP computation
  - [ ] Test cache invalidation on document changes
  - [ ] Test max_nodes limit enforcemen
  - [ ] Test feature flag enablement/disablemen
  - [ ] Test error handling for invalid inputs
  - [ ] Test empty result handling
  - [ ] Test cache miss scenarios

- [ ] **Integration Tests**
  - [ ] Test database integration with real PostgreSQL data
  - [ ] Test UMAP computation with actual embeddings
  - [ ] Test cache integration and invalidation
  - [ ] Test API endpoint integration

- [ ] **Performance Tests**
  - [ ] Benchmark response times with 1k, 2k, 5k chunks
  - [ ] Test UMAP computation time (≤ 5 seconds for 2k chunks)
  - [ ] Test memory usage (≤ 500MB for visualization)
  - [ ] Test cache hit rate (≥ 80% for repeated requests)

- [ ] **Security Tests**
  - [ ] Verify no embedding data in API responses
  - [ ] Test input validation for query parameters
  - [ ] Test max_nodes enforcemen
  - [ ] Test feature flag protection

- [ ] **Resilience Tests**
  - [ ] Test graceful degradation when cache unavailable
  - [ ] Test behavior during database failures
  - [ ] Test resource exhaustion scenarios
  - [ ] Test concurrent access to cache

- [ ] **Edge Case Tests**
  - [ ] Test with 0, 1, max_nodes chunks
  - [ ] Test with Unicode in labels and queries
  - [ ] Test with malformed query parameters
  - [ ] Test race conditions in caching

**Implementation Notes:**
- Use existing database connection patterns from `database_resilience.py`
- Implement UMAP caching with proper invalidation
- Follow type hint standards and Ruff/Pyright compliance
- No inline SQL in views - all DB calls in data layer

**Quality Gates:**
- [ ] **Code Review** - All code has been reviewed
- [ ] **Tests Passing** - All tests pass with 90% coverage
- [ ] **Performance Validated** - Meets response time requirements
- [ ] **Security Reviewed** - No embedding exposure, input validation
- [ ] **Documentation Updated** - Docstrings and type hints added

#### Task T2: API Endpoint Integration
**Priority:** Critical
**Estimated Time:** 0.5 days
**Dependencies:** T1

**Description:** Add `/graph-data` endpoint to existing Flask dashboard with proper routing and error handling.

**Acceptance Criteria:**
- [ ] `/graph-data` endpoint added to `dashboard.py`
- [ ] Endpoint accepts query parameters (q, include_knn, include_entity, min_sim, max_nodes)
- [ ] Returns JSON response with V1 schema
- [ ] Proper error handling and status codes
- [ ] Feature flag protection implemented
- [ ] Input validation and sanitization
- [ ] Performance monitoring hooks added

**Testing Requirements:**
- [ ] **Unit Tests**
  - [ ] Test endpoint with valid query parameters
  - [ ] Test endpoint with invalid parameters
  - [ ] Test feature flag enablement/disablemen
  - [ ] Test error response formats

- [ ] **Integration Tests**
  - [ ] Test endpoint integration with GraphDataProvider
  - [ ] Test with real database data
  - [ ] Test error propagation from data layer

- [ ] **Performance Tests**
  - [ ] Test endpoint response times
  - [ ] Test concurrent request handling

- [ ] **Security Tests**
  - [ ] Test input validation and sanitization
  - [ ] Test feature flag protection
  - [ ] Test rate limiting if implemented

**Implementation Notes:**
- Follow existing Flask route patterns
- Use proper error handling and logging
- Add performance monitoring hooks

**Quality Gates:**
- [ ] **Code Review** - All code has been reviewed
- [ ] **Tests Passing** - All tests pass
- [ ] **Performance Validated** - Meets response time requirements
- [ ] **Security Reviewed** - Input validation and protection
- [ ] **Documentation Updated** - API documentation added

### Phase 2: Flask Cluster Visualization (1-2 days)

#### Task T3: Flask Cluster View (Plotly + UMAP)
**Priority:** High
**Estimated Time:** 1 day
**Dependencies:** T1, T2

**Description:** Add cluster visualization page to existing Flask dashboard with Plotly scatter plots and interactive features.

**Acceptance Criteria:**
- [ ] `/visualize` page added to Flask dashboard
- [ ] 2D scatter plot using UMAP coordinates from API
- [ ] Hover functionality showing file path and line spans
- [ ] Min-sim slider for filtering relationships
- [ ] Debounced API calls for real-time updates
- [ ] Color coding by chunk category or anchor status
- [ ] Responsive design for different screen sizes

**Testing Requirements:**
- [ ] **Unit Tests**
  - [ ] Test route loading and rendering
  - [ ] Test API integration with frontend
  - [ ] Test slider and filter functionality

- [ ] **Integration Tests**
  - [ ] Test end-to-end visualization workflow
  - [ ] Test real-time updates with debouncing
  - [ ] Test interaction with existing dashboard

- [ ] **Performance Tests**
  - [ ] Test page load time
  - [ ] Test plot rendering performance
  - [ ] Test memory usage during visualization

- [ ] **Usability Tests**
  - [ ] Test hover functionality
  - [ ] Test slider interactions
  - [ ] Test responsive design

**Implementation Notes:**
- Use existing Flask template patterns
- Integrate with existing WebSocket infrastructure
- Follow existing CSS/styling patterns

**Quality Gates:**
- [ ] **Code Review** - All code has been reviewed
- [ ] **Tests Passing** - All tests pass
- [ ] **Performance Validated** - Page loads within 2 seconds
- [ ] **Usability Reviewed** - Interface is intuitive and responsive
- [ ] **Documentation Updated** - Usage guide added

### Phase 3: NiceGUI Graph View (1-2 days)

#### Task T4: NiceGUI Graph View (Cytoscape)
**Priority:** High
**Estimated Time:** 1.5 days
**Dependencies:** T1, T2

**Description:** Create NiceGUI application with Cytoscape integration for interactive network graph visualization.

**Acceptance Criteria:**
- [ ] NiceGUI app created with Cytoscape integration
- [ ] Network graph showing chunk relationships
- [ ] Toggle controls for knn/entity edge types
- [ ] Min-sim slider for edge filtering
- [ ] Click functionality showing file/line details
- [ ] Zoom and pan controls for graph navigation
- [ ] Node color coding by type and category

**Testing Requirements:**
- [ ] **Unit Tests**
  - [ ] Test NiceGUI app initialization
  - [ ] Test Cytoscape graph loading
  - [ ] Test toggle and filter functionality

- [ ] **Integration Tests**
  - [ ] Test API integration with NiceGUI
  - [ ] Test graph rendering with real data
  - [ ] Test user interactions and callbacks

- [ ] **Performance Tests**
  - [ ] Test graph rendering performance
  - [ ] Test memory usage with large graphs
  - [ ] Test interaction responsiveness

- [ ] **Usability Tests**
  - [ ] Test graph navigation (zoom, pan)
  - [ ] Test node selection and details
  - [ ] Test edge filtering and toggles

**Implementation Notes:**
- Create separate NiceGUI app in `src/visualization/`
- Use CDN for Cytoscape.js
- Follow existing Python patterns and type hints

**Quality Gates:**
- [ ] **Code Review** - All code has been reviewed
- [ ] **Tests Passing** - All tests pass
- [ ] **Performance Validated** - Graph renders within 3 seconds
- [ ] **Usability Reviewed** - Interface is intuitive and responsive
- [ ] **Documentation Updated** - Usage guide added

### Phase 4: Documentation & Integration (1 day)

#### Task T5: Documentation & Integration
**Priority:** High
**Estimated Time:** 1 day
**Dependencies:** T1, T2, T3, T4

**Description:** Complete comprehensive documentation updates and final integration testing.

**Acceptance Criteria:**
- [ ] Update `400_guides/400_system-overview.md` with visualization components
- [ ] Create `400_guides/400_graph-visualization-guide.md` comprehensive guide
- [ ] Update `100_memory/100_cursor-memory-context.md` with new commands
- [ ] Update `000_core/000_backlog.md` completion status
- [ ] Update `400_guides/400_context-priority-guide.md` with new files
- [ ] Add cross-references and anchor keys
- [ ] Include TL;DR sections and usage examples
- [ ] Final integration testing completed

**Testing Requirements:**
- [ ] **Integration Tests**
  - [ ] Test complete workflow from API to visualization
  - [ ] Test both Flask and NiceGUI UIs
  - [ ] Test feature flag enablement/disablemen

- [ ] **Documentation Tests**
  - [ ] Verify all links and cross-references work
  - [ ] Test code examples and usage instructions
  - [ ] Validate anchor keys and navigation

**Implementation Notes:**
- Follow existing documentation patterns
- Include comprehensive usage examples
- Add proper cross-references

**Quality Gates:**
- [ ] **Code Review** - All documentation has been reviewed
- [ ] **Tests Passing** - All integration tests pass
- [ ] **Documentation Updated** - All relevant docs updated
- [ ] **Cross-references Validated** - All links and anchors work
- [ ] **User Acceptance** - Documentation is clear and complete

## Quality Metrics

- **Test Coverage Target**: 90% for GraphDataProvider
- **Performance Benchmarks**: p50 ≤ 200ms, p95 ≤ 500ms API response
- **Security Requirements**: No embedding exposure, input validation, feature flag protection
- **Reliability Targets**: 99% uptime, graceful degradation on failures

## Risk Mitigation

- **Technical Risks**: UMAP performance mitigated by caching, memory usage limited by max_nodes
- **Timeline Risks**: Phased approach allows early delivery of core functionality
- **Resource Risks**: Comprehensive testing plan ensures quality without over-engineering

## Implementation Status

### Overall Progress

- **Total Tasks:** 0 completed out of 5 total
- **Current Phase:** Planning
- **Estimated Completion:** 4-6 days
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
