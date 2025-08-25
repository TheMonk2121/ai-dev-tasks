<!-- ANCHOR_KEY: generate-tasks -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

# Generate Tasks

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Enhanced task generation workflow with MoSCoW prioritization and solo developer optimizations | When you need to convert a PRD or backlog item into actionable tasks | 1) Parse PRD/backlog item; 2) Use enhanced task template; 3) Add MoSCoW prioritization; 4) Set solo optimization features |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Enhanced task generation workflow
- **Priority**: 🔥 Critical - Essential for project execution
- **Points**: 6 - Enhanced complexity, high importance
- **Dependencies**: 400_guides/400_context-priority-guide.md, 000_core/001_create-prd.md
- **Next Steps**: Use enhanced templates with MoSCoW prioritization

<!-- ANCHOR: workflow -->
{#workflow}

## Workflow

### 🤖 **Enhanced Automated Task Generation (Recommended)**

For consistent, high-quality task generation with industry standards:

```bash
# Generate tasks from PRD with MoSCoW prioritization
python3 scripts/task_generation_automation.py --prd <prd_file> --moscow --preview

# Generate tasks from backlog item with solo optimizations
python3 scripts/task_generation_automation.py --backlog-id <backlog_id> --solo-optimized --preview

# Generate complete task list with enhanced features
python3 scripts/task_generation_automation.py --prd <prd_file> --output-file tasks.md --moscow --solo-optimized
```

### Enhanced Backlog Integration {#backlog-integration}

- **Input**: Backlog item ID (e.g., B-1007, B-1009) or PRD file
- **Output**: Task list with MoSCoW prioritization and solo optimizations
- **Cross-reference**: `000_core/000_backlog.md` for item details and metadata
- **MoSCoW Support**: Must/Should/Could/Won't prioritization throughout
- **Solo Optimization**: Auto-advance, context preservation, one-command workflows

The enhanced automation system provides:
- **MoSCoW Prioritization** with visual indicators (🔥 Must, 🎯 Should, ⚡ Could, ⏸️ Won't)
- **Solo Developer Optimizations** with auto-advance and context preservation
- **Enhanced Task Templates** with implementation guidance from PRD Section 0
- **Intelligent Testing Requirements** based on task type and complexity
- **Priority-based Quality Gates** with appropriate review levels
- **Dependency Analysis** and task relationships with MoSCoW consideration
- **Multiple Output Formats** (markdown, JSON, task lists) with enhanced metadata

### 📝 **Enhanced Manual Process (Fallback)**

- Parse PRD Section 0 for implementation context
- Apply MoSCoW prioritization to task ordering
- Include solo optimization features in task templates
- Enforce enhanced quality gates and acceptance criteria per task

### PRD-less path

- If PRD is skipped per rule (points < 5 AND score_total ≥ 3.0), parse `000_core/000_backlog.md` directly
- Use backlog metadata (scores, deps, MoSCoW priority) to size/schedule tasks
- Apply solo optimization features based on backlog item complexity
- Log that PRD was skipped; proceed with enhanced task format and gates

<!-- ANCHOR: template -->
{#template}

## Enhanced Task Format Requirements

Each task must include MoSCoW prioritization and solo optimization features:

```markdown
### Task Name
**Priority**: [Critical/High/Medium/Low]
**MoSCoW**: [🔥 Must/🎯 Should/⚡ Could/⏸️ Won't]
**Estimated Time**: [X hours/days]
**Dependencies**: [List of prerequisite tasks]
**Solo Optimization**: [Auto-advance: yes/no, Context preservation: yes/no]

**Description**: [Clear, actionable description with implementation guidance]

**Acceptance Criteria**:
- [ ] [Specific, testable criteria]
- [ ] [Another criterion]
- [ ] [Performance benchmarks if applicable]

**Testing Requirements**:
- [ ] **Unit Tests** - [Specific test scenarios]
- [ ] **Integration Tests** - [Component interaction tests]
- [ ] **Performance Tests** - [Benchmarks and thresholds]
- [ ] **Security Tests** - [Vulnerability and validation tests]
- [ ] **Resilience Tests** - [Error handling and failure scenarios]
- [ ] **Edge Case Tests** - [Boundary conditions and unusual inputs]

**Implementation Notes**: [Technical details, considerations, or warnings from PRD Section 0]

**Quality Gates**:
- [ ] **Code Review** - All code has been reviewed
- [ ] **Tests Passing** - All tests pass with required coverage
- [ ] **Performance Validated** - Meets performance requirements
- [ ] **Security Reviewed** - Security implications considered
- [ ] **Documentation Updated** - Relevant docs updated

**Solo Workflow Integration**:
- **Auto-Advance**: [yes/no] - Will task auto-advance to next?
- **Context Preservation**: [yes/no] - Does task preserve context for next session?
- **One-Command**: [yes/no] - Can task be executed with single command?
- **Smart Pause**: [yes/no] - Should task pause for user input?
```

## **Enhanced Testing Methodology**

### **Comprehensive Test Coverage Requirements:**

#### **1. Unit Tests**
- **Purpose**: Test individual components in isolation
- **Coverage**: All public methods and critical private methods
- **Requirements**:
  - Mock external dependencies
  - Test edge cases and error conditions
  - Validate input/output contracts
  - Test configuration variations

#### **2. Integration Tests**
- **Purpose**: Test component interactions and workflows
- **Coverage**: End-to-end workflows and data flows
- **Requirements**:
  - Test with real external services (when safe)
  - Validate data transformation and persistence
  - Test error propagation between components
  - Verify API contracts and interfaces

#### **3. Performance Tests**
- **Purpose**: Validate performance under load and stress
- **Coverage**: Response times, throughput, resource usage
- **Requirements**:
  - Benchmark against defined thresholds
  - Test with realistic data volumes
  - Measure memory usage and cleanup
  - Test concurrent request handling

#### **4. Security Tests**
- **Purpose**: Validate security controls and vulnerability prevention
- **Coverage**: Input validation, access control, data protection
- **Requirements**:
  - Test injection attacks (SQL, XSS, prompt injection)
  - Validate authentication and authorization
  - Test data sanitization and validation
  - Verify secure communication protocols

#### **5. Resilience Tests**
- **Purpose**: Test system behavior under failure conditions
- **Coverage**: Error handling, recovery, graceful degradation
- **Requirements**:
  - Test network failures and timeouts
  - Validate error recovery mechanisms
  - Test resource exhaustion scenarios
  - Verify logging and monitoring under stress

#### **6. Edge Case Tests**
- **Purpose**: Test boundary conditions and unusual scenarios
- **Coverage**: Large inputs, special characters, malformed data
- **Requirements**:
  - Test with maximum/minimum values
  - Validate Unicode and special character handling
  - Test concurrent access and race conditions
  - Verify behavior with corrupted or incomplete data

### **Test Implementation Standards:**

#### **Test Structure:**
```python
def test_component_functionality():
    """Test description with clear purpose"""

    # Setup - Prepare test data and mocks

    # Execute - Call the function under test

    # Assert - Verify expected outcomes

    # Cleanup - Restore state if needed
```

#### **Test Quality Requirements:**
- **Isolation**: Tests should not depend on each other
- **Deterministic**: Tests should produce consistent results
- **Fast**: Unit tests should complete in milliseconds
- **Clear**: Test names and assertions should be self-documenting
- **Comprehensive**: Cover happy path, error cases, and edge cases

#### **Performance Benchmarks:**
- **Response Time**: Define acceptable latency thresholds
- **Throughput**: Specify requests per second requirements
- **Resource Usage**: Set memory and CPU limits
- **Scalability**: Test with increasing load levels

## **MoSCoW Prioritization Integration**

### **Priority Mapping:**
- **🔥 Must**: Critical tasks that block the entire project
- **🎯 Should**: Important tasks that add significant value
- **⚡ Could**: Nice-to-have tasks that improve the experience
- **⏸️ Won't**: Tasks deferred to future iterations

### **Task Selection Logic:**
1. **Must tasks** are always executed first
2. **Should tasks** are executed when Must tasks are complete
3. **Could tasks** are executed if time permits
4. **Won't tasks** are documented but not executed

### **Dynamic Reprioritization:**
- AI-driven priority adjustments based on completion patterns
- Context-aware task selection using LTST memory
- Dependency-based reordering with MoSCoW consideration

## **Solo Developer Optimization Features**

### **Auto-Advance Configuration:**
- **Auto-Advance: yes** for Medium and Low priority tasks
- **Auto-Advance: no** for Critical tasks, deployment changes, database migrations
- **Smart Pausing**: Automatic detection of blocking conditions

### **Context Preservation:**
- **LTST Memory Integration**: Maintains context across sessions
- **Session State Management**: Preserves progress and decisions
- **Cross-Session Continuity**: Links related work sessions

### **One-Command Workflows:**
- **Solo Workflow CLI**: `python3 scripts/solo_workflow.py start/continue/ship`
- **Task Bundling**: Group related tasks for single execution
- **Smart Dependencies**: Automatic dependency resolution

## **Enhanced Quality Gates Integration**

### **Implementation Status Tracking:**
```markdown
## Implementation Status

### Overall Progress
- **Total Tasks:** [X] completed out of [Y] total
- **MoSCoW Progress:** 🔥 Must: [X/Y], 🎯 Should: [X/Y], ⚡ Could: [X/Y]
- **Current Phase:** [Planning/Implementation/Testing/Deployment]
- **Estimated Completion:** [Date or percentage]
- **Blockers:** [List any current blockers]

### Quality Gates
- [ ] **Code Review Completed** - All code has been reviewed
- [ ] **Tests Passing** - All unit and integration tests pass
- [ ] **Documentation Updated** - All relevant docs updated
- [ ] **Performance Validated** - Performance meets requirements
- [ ] **Security Reviewed** - Security implications considered
- [ ] **User Acceptance** - Feature validated with users
- [ ] **Resilience Tested** - Error handling and recovery validated
- [ ] **Edge Cases Covered** - Boundary conditions tested
- [ ] **MoSCoW Validated** - Priority alignment confirmed
- [ ] **Solo Optimization** - Auto-advance and context preservation working
```

### **Testing Checklist for Each Task:**
- [ ] **Unit Tests Written** - All public methods tested
- [ ] **Integration Tests Created** - Component interactions tested
- [ ] **Performance Tests Implemented** - Benchmarks and thresholds defined
- [ ] **Security Tests Added** - Vulnerability checks implemented
- [ ] **Resilience Tests Included** - Error scenarios covered
- [ ] **Edge Case Tests Written** - Boundary conditions tested
- [ ] **Test Documentation Updated** - Test procedures documented
- [ ] **CI/CD Integration** - Tests run automatically
- [ ] **MoSCoW Alignment** - Task priority matches project goals
- [ ] **Solo Optimization** - Auto-advance and context features tested

## **Enhanced Output Format**

Generate a comprehensive task list with the following structure:

```markdown
# Task List: [Project Name]

## Overview
[Brief description of the project and its goals with MoSCoW context]

## MoSCoW Prioritization Summary
- **🔥 Must Have**: [X] tasks - Critical path items
- **🎯 Should Have**: [X] tasks - Important value-add items
- **⚡ Could Have**: [X] tasks - Nice-to-have improvements
- **⏸️ Won't Have**: [X] tasks - Deferred to future iterations

## Solo Developer Quick Start
```bash
# Start everything with enhanced workflow
python3 scripts/solo_workflow.py start "description"

# Continue where you left off
python3 scripts/solo_workflow.py continue

# Ship when done
python3 scripts/solo_workflow.py ship
```

## Implementation Phases

### Phase 1: Environment Setup
[Tasks for infrastructure and dependencies with MoSCoW indicators]

### Phase 2: Core Implementation
[Tasks for main functionality development with solo optimizations]

### Phase 3: Integration & Testing
[Tasks for component integration and validation with enhanced testing]

### Phase 4: Performance & Security
[Tasks for optimization and hardening with quality gates]

### Phase 5: Documentation & Deployment
[Tasks for final preparation and launch with solo workflow integration]

## Quality Metrics
- **Test Coverage Target**: [X]%
- **Performance Benchmarks**: [Specific metrics]
- **Security Requirements**: [Security standards]
- **Reliability Targets**: [Uptime and error rates]
- **MoSCoW Alignment**: [Priority distribution metrics]
- **Solo Optimization**: [Auto-advance and context preservation metrics]

## Risk Mitigation
- **Technical Risks**: [Identified risks and mitigation strategies]
- **Timeline Risks**: [Schedule risks and contingency plans]
- **Resource Risks**: [Resource constraints and solutions]
- **Priority Risks**: [MoSCoW alignment risks and adjustments]
```

## **Special Instructions**

1. **Always include MoSCoW prioritization** for every task
2. **Include solo optimization features** (auto-advance, context preservation)
3. **Always include comprehensive testing requirements** for every task
4. **Specify performance benchmarks** where applicable
5. **Include security considerations** for all user-facing features
6. **Add resilience testing** for critical system components
7. **Consider edge cases** and boundary conditions
8. **Define quality gates** for each major milestone
9. **Include monitoring and observability** requirements
10. **Specify error handling** and recovery procedures
11. **Align with backlog priorities** when planning task dependencies and effort
12. **Consider impact estimates** from backlog to ensure appropriate task scope
13. **Parse backlog table format** when provided with backlog ID
14. **Use points-based estimation** for task effort planning
15. **Track backlog status updates** as tasks are completed
16. **Consider backlog scoring** for task prioritization when available
17. **Use scoring metadata** to inform task sizing and dependencies
18. **Parse scoring comments** (`<!--score: {bv:X, tc:X, rr:X, le:X, effort:X}-->`) for context
19. **Extract implementation guidance** from PRD Section 0 when available
20. **Apply solo developer optimizations** based on task complexity and dependencies

This enhanced approach ensures that every task includes MoSCoW prioritization, solo developer optimizations, thorough testing requirements, and quality gates, leading to more robust, prioritized, and solo-developer-friendly implementations.
