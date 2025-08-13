<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 000_core/000_backlog.md -->
<!-- MODULE_REFERENCE: 400_guides/400_testing-strategy-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MEMORY_CONTEXT: HIGH - Task generation workflow and planning -->

# Generate Tasks

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Task generation workflow that breaks down PRDs or backlog items into executable tasks with testing, quality gates, and acceptance criteria | When you need to convert a PRD or backlog item into actionable tasks | 1) Parse PRD/backlog item; 2) Use task template; 3) Add testing requirements; 4) Set quality gates |

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Task generation workflow maintained

- **Priority**: 🔥 Critical - Essential for project execution

- **Points**: 4 - Moderate complexity, high importance

- **Dependencies**: 400_guides/400_context-priority-guide.md, 000_core/001_create-prd.md

- **Next Steps**: Enhance task templates and automation

<!-- ANCHOR: workflow -->
{#workflow}

## Workflow

- Parse PRD or `000_core/000_backlog.md` row to derive tasks
- Enforce quality gates and acceptance criteria per task

### PRD-less path

- If PRD is skipped per rule (points < 5 AND score_total ≥ 3.0), parse `000_core/000_backlog.md` directly

- Use backlog metadata (scores, deps) to size/schedule tasks

- Log that PRD was skipped; proceed with standard task format and gates

- **Integration & Testing**- Component integration and validation

- **Performance & Security**- Optimization and hardening

- **Documentation & Deployment**- Final preparation and launch

<!-- ANCHOR: template -->
{#template}

### 3.**Task Format Requirements** Each task must include

```markdown

### Task Name**Priority:**[Critical/High/Medium/Low]**Estimated Time:**[X hours/days]**Dependencies:**[List of prerequisite tasks]**Description:**[Clear, actionable description]**Acceptance Criteria:**- [ ] [Specific, testable criteria]

- [ ] [Another criterion]

- [ ] [Performance benchmarks if applicable]**Testing Requirements:**- [ ]**Unit Tests**- [Specific test scenarios]

- [ ]**Integration Tests**- [Component interaction tests]

- [ ]**Performance Tests**- [Benchmarks and thresholds]

- [ ]**Security Tests**- [Vulnerability and validation tests]

- [ ]**Resilience Tests**- [Error handling and failure scenarios]

- [ ]**Edge Case Tests**- [Boundary conditions and unusual inputs]**Implementation Notes:**[Technical details, considerations, or warnings]**Quality Gates:**- [ ]**Code Review**- All code has been reviewed

- [ ]**Tests Passing**- All tests pass with required coverage

- [ ]**Performance Validated**- Meets performance requirements

- [ ]**Security Reviewed**- Security implications considered

- [ ]**Documentation Updated**- Relevant docs updated

```yaml

## **Enhanced Testing Methodology**###**Comprehensive Test Coverage Requirements:**####**1. Unit Tests**-**Purpose**: Test individual components in isolation

- **Coverage**: All public methods and critical private methods

- **Requirements**:
  - Mock external dependencies
  - Test edge cases and error conditions
  - Validate input/output contracts
  - Test configuration variations

#### **2. Integration Tests**-**Purpose**: Test component interactions and workflows

- **Coverage**: End-to-end workflows and data flows

- **Requirements**:
  - Test with real external services (when safe)
  - Validate data transformation and persistence
  - Test error propagation between components
  - Verify API contracts and interfaces

#### **3. Performance Tests**-**Purpose**: Validate performance under load and stress

- **Coverage**: Response times, throughput, resource usage

- **Requirements**:
  - Benchmark against defined thresholds
  - Test with realistic data volumes
  - Measure memory usage and cleanup
  - Test concurrent request handling

#### **4. Security Tests**-**Purpose**: Validate security controls and vulnerability prevention

- **Coverage**: Input validation, access control, data protection

- **Requirements**:
  - Test injection attacks (SQL, XSS, prompt injection)
  - Validate authentication and authorization
  - Test data sanitization and validation
  - Verify secure communication protocols

#### **5. Resilience Tests**-**Purpose**: Test system behavior under failure conditions

- **Coverage**: Error handling, recovery, graceful degradation

- **Requirements**:
  - Test network failures and timeouts
  - Validate error recovery mechanisms
  - Test resource exhaustion scenarios
  - Verify logging and monitoring under stress

#### **6. Edge Case Tests**-**Purpose**: Test boundary conditions and unusual scenarios

- **Coverage**: Large inputs, special characters, malformed data

- **Requirements**:
  - Test with maximum/minimum values
  - Validate Unicode and special character handling
  - Test concurrent access and race conditions
  - Verify behavior with corrupted or incomplete data

### **Test Implementation Standards:**####**Test Structure:**```python
def test_component_functionality():
    """Test description with clear purpose"""

    # Setup - Prepare test data and mocks

    # Execute - Call the function under test

    # Assert - Verify expected outcomes

    # Cleanup - Restore state if needed

```bash

#### **Test Quality Requirements:**-**Isolation**: Tests should not depend on each other

- **Deterministic**: Tests should produce consistent results

- **Fast**: Unit tests should complete in milliseconds

- **Clear**: Test names and assertions should be self-documenting

- **Comprehensive**: Cover happy path, error cases, and edge cases

#### **Performance Benchmarks:**-**Response Time**: Define acceptable latency thresholds

- **Throughput**: Specify requests per second requirements

- **Resource Usage**: Set memory and CPU limits

- **Scalability**: Test with increasing load levels

## **Quality Gates Integration**###**Implementation Status Tracking:**```markdown

## Implementation Status

### Overall Progress

- **Total Tasks:**[X] completed out of [Y] total

- **Current Phase:**[Planning/Implementation/Testing/Deployment]

- **Estimated Completion:**[Date or percentage]

- **Blockers:**[List any current blockers]

### Quality Gates

- [ ]**Code Review Completed**- All code has been reviewed

- [ ]**Tests Passing**- All unit and integration tests pass

- [ ]**Documentation Updated**- All relevant docs updated

- [ ]**Performance Validated**- Performance meets requirements

- [ ]**Security Reviewed**- Security implications considered

- [ ]**User Acceptance**- Feature validated with users

- [ ]**Resilience Tested**- Error handling and recovery validated

- [ ]**Edge Cases Covered**- Boundary conditions tested

```bash

### **Testing Checklist for Each Task:**

- [ ] **Unit Tests Written** - All public methods tested

- [ ]**Integration Tests Created**- Component interactions tested

- [ ]**Performance Tests Implemented**- Benchmarks and thresholds defined

- [ ]**Security Tests Added**- Vulnerability checks implemented

- [ ]**Resilience Tests Included**- Error scenarios covered

- [ ]**Edge Case Tests Written**- Boundary conditions tested

- [ ]**Test Documentation Updated**- Test procedures documented

- [ ]**CI/CD Integration**- Tests run automatically

## **Output Format**Generate a comprehensive task list with the following structure:

```markdown

# Task List: [Project Name]

## Overview

[Brief description of the project and its goals]

## Implementation Phases

### Phase 1: Environment Setup

[Tasks for infrastructure and dependencies]

### Phase 2: Core Implementation

[Tasks for main functionality development]

### Phase 3: Integration & Testing

[Tasks for component integration and validation]

### Phase 4: Performance & Security

[Tasks for optimization and hardening]

### Phase 5: Documentation & Deployment

[Tasks for final preparation and launch]

## Quality Metrics

- **Test Coverage Target**: [X]%

- **Performance Benchmarks**: [Specific metrics]

- **Security Requirements**: [Security standards]

- **Reliability Targets**: [Uptime and error rates]

## Risk Mitigation

- **Technical Risks**: [Identified risks and mitigation strategies]

- **Timeline Risks**: [Schedule risks and contingency plans]

- **Resource Risks**: [Resource constraints and solutions]

```

## **Special Instructions**

1.**Always include comprehensive testing requirements** for every task
2.**Specify performance benchmarks** where applicable
3.**Include security considerations** for all user-facing features
4.**Add resilience testing** for critical system components
5.**Consider edge cases** and boundary conditions
6.**Define quality gates** for each major milestone
7.**Include monitoring and observability** requirements
8.**Specify error handling** and recovery procedures
9.**Align with backlog priorities** when planning task dependencies and effort
10.**Consider impact estimates** from backlog to ensure appropriate task scope
11.**Parse backlog table format** when provided with backlog ID
12.**Use points-based estimation** for task effort planning
13.**Track backlog status updates** as tasks are completed
14.**Consider backlog scoring** for task prioritization when available
15.**Use scoring metadata** to inform task sizing and dependencies
16.**Parse scoring comments** (`<!--score: {bv:X, tc:X, rr:X, le:X, effort:X}-->`) for context

This enhanced approach ensures that every task includes thorough testing requirements and quality gates, leading to more
robust and reliable implementations.
