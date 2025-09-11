<!-- ANCHOR_KEY: process-task-list -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["implementer", "planner"] -->

# Process Task Lis

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Enhanced task execution workflow with solo developer optimizations, auto-advance, and context preservation | Ready to execute tasks from PRD | Run solo workflow CLI to start automated execution with smart pausing |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Enhanced execution workflow with solo optimizations
- **Priority**: 🔥 Critical - Essential for project execution
- **Points**: 4 - Moderate complexity, high importance
- **Dependencies**: 000_core/001_create-prd.md, 000_core/002_generate-tasks.md
- **Next Steps**: Solo workflow CLI with auto-advance and context preservation

## When to use {#when-to-use}

- Use when you have a PRD with embedded tasks (Section 8: Task Breakdown)
- Use for automated execution with smart pausing and context preservation
- Use for solo developer workflows with one-command operations
- **B-1008**: Enhanced Backlog System - Ready for execution
- **B-1009**: AsyncIO Scribe Enhancement - Ready for execution

### Execution Skip Rule {#execution-skip-rule}

- Skip automated execution when: tasks require extensive user input or external dependencies
- Otherwise, use solo workflow CLI for automated execution with smart pausing

### Backlog Integration {#backlog-integration}

- **Input**: PRD file with embedded tasks (Section 8: Task Breakdown)
- **Output**: Execution configuration and state managemen
- **Cross-reference**: `000_core/000_backlog.md` for item details and metadata

## Enhanced Workflow {#workflow}

### 🚀 **Solo Developer Quick Start (Recommended)**

For streamlined, automated execution with solo developer optimizations:

```bash
# Start everything (backlog intake → PRD → tasks → execution)
python3 scripts/solo_workflow.py start "Enhanced backlog system with industry standards"

# Continue where you left off
python3 scripts/solo_workflow.py continue

# Ship when done
python3 scripts/solo_workflow.py ship
```

### Context Preservation
- **LTST Memory**: Maintains context across sessions
- **Auto-Advance**: Tasks auto-advance unless you pause
- **Smart Pausing**: Pause only for critical decisions or external dependencies

### 🧠 **Memory System Commands**

**Unified Memory Orchestrator**: Single command access to all memory systems
```bash
# Refresh all memory layers
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status"

# Specific system access
python3 scripts/unified_memory_orchestrator.py --systems ltst --role coder "DSPy integration task"

# JSON output for programmatic access
python3 scripts/unified_memory_orchestrator.py --systems cursor prime --role researcher "performance analysis" --format json
```

**Database Auto-Startup**: Automatically starts PostgreSQL if not running
- **Health Check**: Uses `pg_isready` to verify database connectivity
- **Auto-Startup**: Runs `brew services start postgresql@14` if database is down
- **Progress Monitoring**: Real-time progress indicators during startup
- **Graceful Degradation**: Continues with other systems if database startup is slow

**Virtual Environment Auto-Activation**: Automatically activates venv and sets up dependencies
- **Environment Check**: Verifies venv is active and dependencies are available
- **Auto-Activation**: Activates venv if not already active
- **Dependency Setup**: Ensures all required packages are installed

### 🤖 **Automated Execution Engine**

For consistent, high-quality task execution:

```bash
# Execute tasks from PRD with auto-advance
python3 scripts/solo_workflow.py execute --prd <prd_file> --auto-advance

# Execute with smart pausing
python3 scripts/solo_workflow.py execute --prd <prd_file> --smart-pause

# Execute with context preservation
python3 scripts/solo_workflow.py execute --prd <prd_file> --context-preserve
```

### 📝 **Manual Process (Fallback)**

- Parse PRD Section 8: Task Breakdown for task lis
- Execute tasks manually with state tracking
- Update progress in `.ai_state.json`

## Enhanced Execution Configuration {#configuration}

### Execution Configuration Structure

```markdown
# Process Task List: [Project Name]

## Execution Configuration
- **Auto-Advance**: yes/no
- **Pause Points**: [Critical decisions, deployments, user input]
- **Context Preservation**: LTST memory integration
- **Smart Pausing**: Automatic detection of blocking conditions

## State Managemen
- **State File**: `.ai_state.json` (auto-generated, gitignored)
- **Progress Tracking**: Task completion status
- **Session Continuity**: LTST memory for context preservation

## Error Handling
- **HotFix Generation**: Automatic error recovery
- **Retry Logic**: Smart retry with exponential backoff
- **User Intervention**: When to pause for manual fixes

## Execution Commands
```bash
# Start execution
python3 scripts/solo_workflow.py start "description"

# Continue execution
python3 scripts/solo_workflow.py continue

# Complete and archive
python3 scripts/solo_workflow.py ship
```

## Task Execution
[Reference tasks from PRD Section 8 - no duplication]
```

## Enhanced Task Execution Engine {#execution-engine}

### Auto-Advance Configuration

#### **Auto-Advance Rules:**
- **🚀 One-command tasks**: Automatically advance to next task
- **🔄 Auto-advance tasks**: Continue without user input
- **⏸️ Smart pause tasks**: Pause for user input or external dependencies

#### **Smart Pausing Logic:**
- **Critical decisions**: Pause for architectural or design decisions
- **External dependencies**: Pause for API keys, credentials, or external services
- **User validation**: Pause for user acceptance or testing
- **Error conditions**: Pause for manual error resolution

### Context Preservation

#### **LTST Memory Integration:**
- **Session state**: Maintain task progress across sessions
- **Context bundle**: Preserve project context and decisions
- **Knowledge mining**: Extract insights from completed work
- **Scribe integration**: Automated worklog generation

#### **State Management:**
```json
{
  "project": "B-1008: Enhanced Backlog System",
  "current_phase": "Phase 1: Core Structured Data",
  "current_task": "Task 1.1: Enhanced JSON Schema",
  "completed_tasks": ["Task 1.1", "Task 1.2"],
  "pending_tasks": ["Task 1.3", "Task 1.4"],
  "blockers": [],
  "context": {
    "tech_stack": ["Python 3.12", "PostgreSQL", "NiceGUI"],
    "dependencies": ["B-1006-A", "B-1007"],
    "decisions": ["Use JSON Schema for validation", "MoSCoW prioritization"]
  }
}
```

### Error Handling and Recovery

#### **HotFix Task Generation:**
- **Automatic detection**: Identify failed tasks and root causes
- **Recovery tasks**: Generate tasks to fix issues
- **Retry logic**: Smart retry with exponential backoff
- **User intervention**: Pause for manual fixes when needed

#### **Error Recovery Workflow:**
1. **Detect failure**: Identify task failure and root cause
2. **Generate HotFix**: Create recovery task with clear steps
3. **Execute recovery**: Run recovery task with retry logic
4. **Validate fix**: Confirm issue is resolved
5. **Continue execution**: Resume normal task flow

## Enhanced Quality Gates {#quality-gates}

### Implementation Status Tracking

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

### **Quality Gate Checklist for Each Task:**
- [ ] **Code Review** - All code has been reviewed
- [ ] **Tests Passing** - All tests pass with required coverage
- [ ] **Performance Validated** - Meets performance requirements
- [ ] **Security Reviewed** - Security implications considered
- [ ] **Documentation Updated** - Relevant docs updated
- [ ] **Integration Tested** - Component interactions validated
- [ ] **Error Handling** - Error scenarios covered
- [ ] **Edge Cases** - Boundary conditions tested

## Enhanced Output Format {#output-format}

Generate execution configuration with the following structure:

```markdown
# Process Task List: [Project Name]

## Execution Configuration
- **Auto-Advance**: [yes/no]
- **Pause Points**: [List of critical decision points]
- **Context Preservation**: [LTST memory integration details]
- **Smart Pausing**: [Automatic detection rules]

## State Managemen
- **State File**: `.ai_state.json` (auto-generated)
- **Progress Tracking**: [Task completion status]
- **Session Continuity**: [LTST memory for context preservation]

## Error Handling
- **HotFix Generation**: [Automatic error recovery]
- **Retry Logic**: [Smart retry with exponential backoff]
- **User Intervention**: [When to pause for manual fixes]

## Execution Commands
```bash
# Start execution
python3 scripts/solo_workflow.py start "description"

# Continue execution
python3 scripts/solo_workflow.py continue

# Complete and archive
python3 scripts/solo_workflow.py ship
```

## Task Execution
[Reference tasks from PRD Section 8 - no duplication]
```

## **Enhanced Special Instructions**

### Implementation Focus (Enhanced):
1. **Use solo workflow CLI** - One-command operations for common tasks
2. **Enable auto-advance** - Tasks auto-advance unless explicitly paused
3. **Preserve context** - Use LTST memory for session continuity
4. **Implement smart pausing** - Pause only for critical decisions
5. **Generate HotFix tasks** - Automatic error recovery and retry
6. **Track progress** - Maintain state in `.ai_state.json`
7. **Validate quality gates** - Ensure all requirements are me
8. **Handle errors gracefully** - Provide clear error messages and recovery steps
9. **Integrate with LTST memory** - Preserve context across sessions
10. **Use Scribe integration** - Automated worklog generation
11. **Support one-command workflows** - Minimize context switching
12. **Implement retry logic** - Smart retry with exponential backoff
13. **Provide user intervention points** - Clear pause and resume functionality
14. **Track task dependencies** - Ensure proper execution order
15. **Validate acceptance criteria** - Confirm tasks meet requirements
16. **Generate execution reports** - Provide progress and status updates
17. **Support archive operations** - Complete and archive finished work
18. **Integrate with mission dashboard** - Real-time status updates
19. **Provide rollback capabilities** - Ability to revert changes if needed
20. **Ensure backward compatibility** - Work with existing workflow systems

This enhanced approach ensures streamlined task execution with solo developer optimizations, automated error recovery, context preservation, and smart pausing for critical decisions.
