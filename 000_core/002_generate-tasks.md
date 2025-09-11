<!-- ANCHOR_KEY: generate-tasks -->
<!-- ANCHOR_PRIORITY: 25 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

# Generate Tasks

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Enhanced task generation workflow that embeds tasks directly in PRDs with MoSCoW prioritization, solo developer optimizations, and industry standards | When you need to convert a PRD or backlog item into actionable tasks embedded in the PRD | 1) Parse PRD/backlog item; 2) Use enhanced task template; 3) Add MoSCoW prioritization; 4) Include solo optimizations |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Enhanced task generation workflow with MoSCoW prioritization
- **Priority**: 🔥 Critical - Essential for project execution
- **Points**: 4 - Moderate complexity, high importance
- **Dependencies**: 400_guides/400_context-priority-guide.md, 000_core/001_create-prd.md
- **Next Steps**: Enhanced task templates with embedded approach and solo optimizations

<!-- ANCHOR: workflow -->
{#workflow}

## Enhanced Workflow

### 🤖 **Automated Task Generation (Recommended)**

For consistent, high-quality task generation with embedded approach:

```bash
# Generate tasks embedded in PRD
python3 scripts/task_generation_automation.py --prd <prd_file> --embed --preview

# Generate tasks from backlog item (embedded in PRD)
python3 scripts/task_generation_automation.py --backlog-id <backlog_id> --embed --preview

# Generate complete embedded task lis
python3 scripts/task_generation_automation.py --prd <prd_file> --embed --output-file prd_with_tasks.md
```

### Backlog Integration {#backlog-integration}

- **Input**: Backlog item ID (e.g., B-1007, B-1009) or PRD file
- **Output**: Tasks embedded directly in PRD (Section 8: Task Breakdown)
- **Cross-reference**: `000_core/000_backlog.md` for item details and metadata
- **B-1009**: AsyncIO Scribe Enhancement - Task generation completed
- **B-1010**: NiceGUI Scribe Dashboard - Task generation completed

The automation system provides:
- **Embedded task templates** with MoSCoW prioritization
- **Solo developer optimizations** with one-command workflows
- **Industry-standard testing requirements** based on task type and complexity
- **Priority-based quality gates** with appropriate review levels
- **Dependency analysis** and task relationships
- **Streamlined output** - tasks embedded in PRD, no separate Task-List file

### 📝 **Manual Process (Fallback)**

- Parse PRD or `000_core/000_backlog.md` row to derive tasks
- Embed tasks directly in PRD Section 8: Task Breakdown
- Enforce quality gates and acceptance criteria per task

### PRD-less path

- If PRD is skipped per rule (points < 5 AND score_total ≥ 3.0), parse `000_core/000_backlog.md` directly
- Use backlog metadata (scores, deps) to size/schedule tasks
- Log that PRD was skipped; proceed with standard task format and gates

<!-- ANCHOR: template -->
{#template}

## Enhanced Task Format Requirements

### Task Name
**Priority**: [Critical/High/Medium/Low]
**MoSCoW**: [🔥 Must/🎯 Should/⚡ Could/⏸️ Won't]
**Estimated Time**: [X hours/days]
**Dependencies**: [List of prerequisite tasks]
**Solo Optimization**: [🚀 One-command/🔄 Auto-advance/⏸️ Smart pause]

**Description**: [Clear, actionable description]

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

**Implementation Notes**: [Technical details, considerations, or warnings]

**Quality Gates**:
- [ ] **Code Review** - All code has been reviewed
- [ ] **Tests Passing** - All tests pass with required coverage
- [ ] **Performance Validated** - Meets performance requirements
- [ ] **Security Reviewed** - Security implications considered
- [ ] **Documentation Updated** - Relevant docs updated

## MoSCoW Prioritization Integration

### Priority Mapping:
- **🔥 Must**: Critical tasks that block the entire project
- **🎯 Should**: Important tasks that should be completed if possible
- **⚡ Could**: Nice-to-have tasks that can be deferred
- **⏸️ Won't**: Tasks explicitly deferred to future iterations

### Solo Developer Optimization Features:
- **🚀 One-command**: Tasks that can be executed with a single command
- **🔄 Auto-advance**: Tasks that automatically advance to the next step
- **⏸️ Smart pause**: Tasks that require user input or external dependencies

## Enhanced Automated Task Generation

### Commands:
```bash
# Generate embedded tasks in PRD
python3 scripts/task_generation_automation.py --prd <prd_file> --embed

# Generate tasks with MoSCoW prioritization
python3 scripts/task_generation_automation.py --prd <prd_file> --moscow --embed

# Generate tasks with solo optimizations
python3 scripts/task_generation_automation.py --prd <prd_file> --solo-optimized --embed

# Generate complete embedded workflow
python3 scripts/task_generation_automation.py --prd <prd_file> --complete --embed
```

### Enhanced Testing Methodology

#### Comprehensive Test Coverage Requirements:

##### **1. Unit Tests**
- **Purpose**: Test individual components in isolation
- **Coverage**: All public methods and critical private methods
- **Requirements**:
  - Mock external dependencies
  - Test edge cases and error conditions
  - Validate input/output contracts
  - Test configuration variations

##### **2. Integration Tests**
- **Purpose**: Test component interactions and workflows
- **Coverage**: End-to-end workflows and data flows
- **Requirements**:
  - Test with real external services (when safe)
  - Validate data transformation and persistence
  - Test error propagation between components
  - Verify API contracts and interfaces

##### **3. Performance Tests**
- **Purpose**: Validate performance under load and stress
- **Coverage**: Response times, throughput, resource usage
- **Requirements**:
  - Benchmark against defined thresholds
  - Test with realistic data volumes
  - Measure memory usage and cleanup
  - Test concurrent request handling

##### **4. Security Tests**
- **Purpose**: Validate security controls and vulnerability prevention
- **Coverage**: Input validation, access control, data protection
- **Requirements**:
  - Test injection attacks (SQL, XSS, prompt injection)
  - Validate authentication and authorization
  - Test data sanitization and validation
  - Verify secure communication protocols

##### **5. Resilience Tests**
- **Purpose**: Test system behavior under failure conditions
- **Coverage**: Error handling, recovery, graceful degradation
- **Requirements**:
  - Test network failures and timeouts
  - Validate error recovery mechanisms
  - Test resource exhaustion scenarios
  - Verify logging and monitoring under stress

##### **6. Edge Case Tests**
- **Purpose**: Test boundary conditions and unusual scenarios
- **Coverage**: Large inputs, special characters, malformed data
- **Requirements**:
  - Test with maximum/minimum values
  - Validate Unicode and special character handling
  - Test concurrent access and race conditions
  - Verify behavior with corrupted or incomplete data

### Test Implementation Standards:

#### **Test Structure:**
```python
def test_component_functionality():
    """Test description with clear purpose"""

    # Setup - Prepare test data and mocks

    # Execute - Call the function under tes

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

## Enhanced Quality Gates Integration

### Implementation Status Tracking:
```markdown
## Implementation Status

### Overall Progress
- **Total Tasks:** [X] completed out of [Y] total
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

## Enhanced Output Forma

Generate tasks embedded directly in the PRD with the following structure:

```markdown
## 8. Task Breakdown

### Phase 1: [Phase Name]
#### Task 1.1: [Task Name]
**Priority**: [Critical/High/Medium/Low]
**MoSCoW**: [🔥 Must/🎯 Should/⚡ Could/⏸️ Won't]
**Estimated Time**: [X hours]
**Dependencies**: [List of prerequisite tasks]
**Solo Optimization**: [🚀 One-command/🔄 Auto-advance/⏸️ Smart pause]

**Description**: [Clear, actionable description]

**Acceptance Criteria**:
- [ ] [Specific, testable criteria]
- [ ] [Another criterion]

**Testing Requirements**:
- [ ] **Unit Tests** - [Specific test scenarios]
- [ ] **Integration Tests** - [Component interaction tests]
- [ ] **Performance Tests** - [Benchmarks and thresholds]

**Implementation Notes**: [Technical details, considerations, or warnings]

**Quality Gates**:
- [ ] **Code Review** - All code has been reviewed
- [ ] **Tests Passing** - All tests pass with required coverage
- [ ] **Documentation Updated** - Relevant docs updated

#### Task 1.2: [Task Name]
[Same structure as above]

### Phase 2: [Phase Name]
#### Task 2.1: [Task Name]
[Same structure as above]

[Continue for all phases and tasks]
```

## **Enhanced Special Instructions**

### Implementation Focus (Enhanced):
1. **Always include comprehensive testing requirements** for every task
2. **Specify performance benchmarks** where applicable
3. **Include security considerations** for all user-facing features
4. **Add resilience testing** for critical system components
5. **Consider edge cases** and boundary conditions
6. **Define quality gates** for each major milestone
7. **Include monitoring and observability** requirements
8. **Specify error handling** and recovery procedures
9. **Align with backlog priorities** when planning task dependencies and effor
10. **Consider impact estimates** from backlog to ensure appropriate task scope
11. **Parse backlog table format** when provided with backlog ID
12. **Use points-based estimation** for task effort planning
13. **Track backlog status updates** as tasks are completed
14. **Consider backlog scoring** for task prioritization when available
15. **Use scoring metadata** to inform task sizing and dependencies
16. **Parse scoring comments** (`<!--score: {bv:X, tc:X, rr:X, le:X, effort:X}-->`) for context
17. **Embed tasks in PRD** - No separate Task-List file generation
18. **Include MoSCoW prioritization** - Must/Should/Could/Won't categorization
19. **Add solo developer optimizations** - One-command workflows and auto-advance
20. **Consider industry standards** - Best practices for maintainability and scalability

This enhanced approach ensures that every task includes thorough testing requirements, quality gates, MoSCoW prioritization, and solo developer optimizations, leading to more robust and reliable implementations with streamlined file management.
