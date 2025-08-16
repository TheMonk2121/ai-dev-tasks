# Product Requirements Document: Chunk Relationship Visualization & /graph-data API (V1)

> ⚠️ **Auto-Skip Note**: This PRD was generated because this is a multi-component feature introducing a new contract (points≥5 equivalent complexity).

## 1. Executive Summary

**Project**: Chunk Relationship Visualization & /graph-data API (V1)
**Timeline**: 4-6 days (4 phases)
**Stakeholders**: AI development team, system administrators
**Success Metrics**: API response p50 ≤ 200ms, p95 ≤ 500ms, comprehensive visualization of chunk relationships

**Overview**: Implement a shared API and dual UI system for visualizing relationships between document chunks in the RAG system, enabling better understanding of semantic clusters, search neighborhoods, entity expansion, and anchor relationships.

## 2. Problem Statement

**Current State**: The RAG system has 1,939 chunks from 20 core documents but lacks visualization tools to understand chunk relationships, making it difficult to:
- Debug search result relevance
- Understand entity expansion effectiveness
- Analyze semantic clustering patterns
- Optimize anchor relationships

**Pain Points**:
- No visual representation of chunk similarity relationships
- Difficulty understanding why certain chunks are retrieved together
- Limited insight into entity expansion performance
- No way to explore the semantic space of documents

**Opportunity**: Add comprehensive chunk relationship visualization to improve system understanding and debugging capabilities.

**Impact**: Better system comprehension, improved debugging, enhanced optimization opportunities.

## 3. Solution Overview

**High-Level Solution**: Implement a shared `/graph-data` API with dual UI approach - Flask for cluster visualization and NiceGUI for network graphs.

**Key Features**:
- Shared API contract (V1) for chunk relationship data
- UMAP-based 2D clustering visualization in Flask
- Interactive network graphs in NiceGUI with Cytoscape
- Entity expansion relationship visualization
- Anchor relationship network analysis
- Real-time search result neighborhood exploration

**Technical Approach**:
- GraphDataProvider utility class in `src/utils/`
- UMAP for 2D embedding reduction (cached per corpus snapshot)
- Flask + Plotly for cluster visualization
- NiceGUI + Cytoscape for network graphs
- Feature flag protection for API endpoint

**Integration Points**:
- Existing PostgreSQL database with pgvector
- Current Flask dashboard infrastructure
- Entity overlay system for expansion visualization
- Memory rehydrator for search result analysis

## 4. Functional Requirements

**User Stories**:
- As a developer, I want to see semantic clusters of chunks to understand document organization
- As a developer, I want to visualize search result neighborhoods to debug relevance
- As a developer, I want to explore entity expansion relationships to optimize performance
- As a developer, I want to analyze anchor relationships to improve system design

**Feature Specifications**:
- API endpoint `/graph-data` with query parameters for filtering
- 2D scatter plot visualization of chunk clusters
- Interactive network graph showing chunk relationships
- Toggle controls for different relationship types (knn, entity)
- Click-to-detail functionality showing file paths and line spans
- Real-time search result visualization

**Data Requirements**:
- Chunk metadata (id, label, anchor, category)
- 2D coordinates from UMAP reduction
- Relationship edges with weights and types
- Performance metrics (elapsed_ms)

**API Requirements**:
- RESTful endpoint with query parameters
- JSON response with nodes, edges, metadata
- Error handling and truncation indicators
- Feature flag protection

## 5. Non-Functional Requirements

**Performance Requirements**:
- API response p50 ≤ 200ms, p95 ≤ 500ms
- Support for up to 2,000 nodes in visualization
- UMAP computation cached per corpus snapshot
- Debounced API calls for real-time updates

**Security Requirements**:
- No embedding data exposed in API responses
- Max nodes limit enforced to prevent DoS
- Feature flag protection for API endpoint
- Input validation and sanitization

**Reliability Requirements**:
- Graceful degradation when cache misses
- Error handling for malformed requests
- Automatic cache invalidation on document changes
- Fallback to basic visualization on failures

**Usability Requirements**:
- Intuitive controls for relationship type toggles
- Clear visual distinction between different node types
- Responsive design for different screen sizes
- Consistent interaction patterns across UIs

## 6. Testing Strategy

**Test Coverage Goals**:
- Unit tests: 90% coverage for GraphDataProvider
- Integration tests: API contract validation
- Performance tests: Response time validation
- Security tests: Input validation and access control

**Testing Phases**:
- Unit testing of GraphDataProvider class
- Integration testing of API endpoints
- Performance testing with realistic data loads
- Security testing of input validation

**Automation Requirements**:
- Automated unit and integration tests
- Performance regression testing
- Security vulnerability scanning
- Manual testing for UI interactions

**Test Environment Requirements**:
- Isolated test database with sample chunks
- Performance testing environment
- Security testing environment

## 7. Quality Assurance Requirements

**Code Quality Standards**:
- Full type hints throughout codebase
- Ruff-clean code with no linting errors
- Pyright-clean with no type errors
- Sorted imports and consistent formatting
- No inline SQL in views (DB calls in data layer)

**Performance Benchmarks**:
- API response time: p50 ≤ 200ms, p95 ≤ 500ms
- UMAP computation: ≤ 5 seconds for 2k chunks
- Memory usage: ≤ 500MB for visualization
- Cache hit rate: ≥ 80% for repeated requests

**Security Validation**:
- No embedding data leakage in API responses
- Input validation for all query parameters
- Rate limiting on API endpoints
- Feature flag protection

**User Acceptance Criteria**:
- Developers can successfully visualize chunk clusters
- Search result neighborhoods are clearly displayed
- Entity expansion relationships are understandable
- Anchor relationships are effectively communicated

## 8. Implementation Quality Gates

**Development Phase Gates**:
- [ ] **Requirements Review** - PRD approved and requirements clear
- [ ] **Design Review** - API contract and architecture approved
- [ ] **Code Review** - All code reviewed and approved
- [ ] **Testing Complete** - All tests pass with required coverage
- [ ] **Performance Validated** - Response times meet requirements
- [ ] **Security Reviewed** - Security implications addressed
- [ ] **Documentation Updated** - All relevant documentation current
- [ ] **User Acceptance** - Feature validated with developers

## 9. Testing Requirements by Component

**Unit Testing Requirements**:
- **Coverage Target**: 90% for GraphDataProvider
- **Test Scope**: All public methods and cache logic
- **Test Quality**: Isolated, deterministic, fast
- **Mock Requirements**: Database and UMAP dependencies mocked
- **Edge Cases**: Empty results, cache misses, invalid inputs

**Integration Testing Requirements**:
- **API Contract Testing**: Validate response schema and types
- **Database Integration**: Test with real PostgreSQL data
- **Cache Integration**: Test UMAP caching and invalidation
- **Error Propagation**: Test error handling across components

**Performance Testing Requirements**:
- **Response Time**: p50 ≤ 200ms, p95 ≤ 500ms
- **Throughput**: 10 requests/second sustained
- **Resource Usage**: ≤ 500MB memory, ≤ 2 CPU cores
- **Scalability**: Test with 1k, 2k, 5k chunks
- **Concurrent Users**: 5 concurrent users

**Security Testing Requirements**:
- **Input Validation**: Test for injection attacks
- **Data Protection**: Verify no embedding exposure
- **Access Control**: Test feature flag protection
- **Rate Limiting**: Test max_nodes enforcement
- **Vulnerability Scanning**: Regular security scans

**Resilience Testing Requirements**:
- **Error Handling**: Test graceful degradation
- **Cache Failures**: Test behavior when cache unavailable
- **Database Failures**: Test behavior during DB issues
- **Resource Exhaustion**: Test under high memory/CPU load
- **Network Failures**: Test during network interruptions

**Edge Case Testing Requirements**:
- **Boundary Conditions**: Test with 0, 1, max_nodes chunks
- **Special Characters**: Test Unicode in labels and queries
- **Large Data Sets**: Test with realistic chunk volumes
- **Concurrent Access**: Test race conditions in caching
- **Malformed Input**: Test with invalid query parameters

## 10. Monitoring and Observability

**Logging Requirements**:
- Structured logging for API requests and responses
- Performance metrics logging (response times, cache hits)
- Error logging with appropriate levels
- Security event logging

**Metrics Collection**:
- API response time percentiles
- Cache hit/miss rates
- UMAP computation times
- Error rates by type

**Alerting**:
- High response time alerts (>500ms p95)
- High error rate alerts (>5%)
- Cache miss rate alerts (>20%)
- Security violation alerts

**Dashboard Requirements**:
- Real-time API performance dashboard
- Cache performance monitoring
- Error rate tracking
- Security event monitoring

**Troubleshooting**:
- Detailed error messages with context
- Performance profiling tools
- Cache debugging utilities
- Database query analysis tools

## 11. Deployment and Release Requirements

**Environment Setup**:
- Development environment with test data
- Staging environment for integration testing
- Production environment with feature flags

**Deployment Process**:
- Automated deployment with rollback capability
- Feature flag controlled rollout
- Database migration procedures
- Configuration management

**Configuration Management**:
- Environment-specific API configurations
- Feature flag settings
- Performance tuning parameters
- Security settings

**Database Migrations**:
- No schema changes required (uses existing tables)
- Data migration procedures if needed
- Index optimization for performance

**Feature Flags**:
- `/graph-data` endpoint behind feature flag
- Gradual rollout capability
- Easy disable mechanism for issues

## 12. Risk Assessment and Mitigation

**Technical Risks**:
- **UMAP Performance**: Risk of slow computation for large datasets
  - *Mitigation*: Implement caching with corpus snapshot invalidation
- **Memory Usage**: Risk of high memory consumption
  - *Mitigation*: Enforce max_nodes limit and monitor usage
- **API Complexity**: Risk of complex API contract
  - *Mitigation*: Version API and maintain backward compatibility

**Timeline Risks**:
- **UI Complexity**: Risk of complex visualization implementation
  - *Mitigation*: Start with simple Flask implementation, add NiceGUI later
- **Integration Issues**: Risk of integration problems with existing systems
  - *Mitigation*: Thorough testing and gradual rollout

**Resource Risks**:
- **Development Time**: Risk of underestimating effort
  - *Mitigation*: Break into smaller phases with clear deliverables
- **Testing Complexity**: Risk of insufficient testing
  - *Mitigation*: Comprehensive test plan with automation

## 13. Success Criteria

**Measurable Success Criteria**:
- API response time: p50 ≤ 200ms, p95 ≤ 500ms
- Test coverage: ≥ 90% for GraphDataProvider
- Code quality: Ruff-clean, Pyright-clean, full type hints
- Documentation: All relevant guides updated with cross-references

**Acceptance Criteria**:
- `/graph-data` API returns V1 schema with correct data types
- Flask cluster visualization displays 2D scatter plots with UMAP coordinates
- NiceGUI graph visualization shows interactive network relationships
- Feature flag protection works correctly
- Cache invalidation triggers on document changes
- All tests pass with required coverage
- Documentation updated with usage examples and cross-references

**API Contract V1**:
```json
{
  "nodes": [
    {
      "id": "chunk_123",
      "label": "file.md:45-67",
      "anchor": "tldr",
      "coords": [0.12, -0.87],
      "category": "code"
    }
  ],
  "edges": [
    {
      "source": "chunk_123",
      "target": "chunk_456",
      "type": "knn",
      "weight": 0.85
    }
  ],
  "elapsed_ms": 145,
  "v": 1,
  "truncated": false
}
```

**Cache Semantics**:
- UMAP cache keyed by corpus snapshot (`MAX(documents.updated_at)`)
- Invalidates on new/updated documents
- Cache miss triggers recomputation

**Security Requirements**:
- No embedding data in API responses
- Max nodes limit enforced
- Feature flag protection
- Input validation and sanitization
