# Process Task List - AI-Optimized Execution

Guidelines for executing task lists generated from PRDs using AI agents (Mistral 7B Instruct + Yi-Coder-9B-Chat-Q6_K).

<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- WORKFLOW_FILES: 001_create-prd.md, 002_generate-tasks.md -->
<!-- BACKLOG_FILES: 000_backlog.md, 100_backlog-guide.md -->
<!-- MEMORY_CONTEXT: MEDIUM - Core workflow for AI task execution -->
<!-- SYSTEM_FILES: 400_system-overview_advanced_features.md -->

<!-- MODULE_REFERENCE: 400_deployment-environment-guide_additional_resources.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide_ai_model_upgrade_procedures.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide_database_migration_procedures.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->
### **AI Development Ecosystem Context**
This task execution process is part of a comprehensive AI-powered development ecosystem that transforms ideas into working software using AI agents (Mistral 7B Instruct + Yi-Coder-9B-Chat-Q6_K). The ecosystem provides structured workflows, automated task processing, and intelligent error recovery to make AI-assisted development efficient and reliable.

**Key Components:**
- **Planning Layer**: PRD Creation, Task Generation, Process Management
- **AI Execution Layer**: Mistral 7B Instruct (Planning), Yi-Coder-9B-Chat-Q6_K (Implementation)
- **Core Systems**: DSPy RAG System, N8N Workflows, Dashboard, Testing Framework
- **Supporting Infrastructure**: PostgreSQL + PGVector, File Watching, Notification System

---

## 1. Execution Loop

### Core Process
1. **Load Context**
   - Read task list from markdown file
   - Load `.ai_state.json` if present (file list, commit hash, test results)
   - Consider backlog priorities for task selection when multiple tasks are available
   - Parse backlog table for status and dependency information
   - **Parse backlog scoring** when available (`<!--score_total: X.X-->` comments)
   - **Use scores for task prioritization** - higher scores indicate higher priority
   - **Fall back to human priority tags** when scores are missing

2. **Select Next Task**
   - Find task with status `[ ]` where all dependencies are `[x]`
   - Skip tasks marked `[!]` (blocked)
   - Prioritize tasks based on backlog impact estimates when possible
   - Check backlog dependencies before starting tasks
   - **Consider backlog scores** for task selection when available
   - **Prioritize high-scoring items** when multiple tasks are ready

3. **Execute Task**
   - Follow steps in "Do:" section
   - Use Yi-Coder-9B-Chat-Q6_K for code implementation
   - Use Mistral 7B Instruct for reasoning and planning

4. **Validate Completion**
   - Run all "Done when:" criteria
   - If any fail → mark task `[!]` and create HotFix task
   - If all pass → mark task `[x]`

5. **Update State**
   - Write/update `.ai_state.json` with current state
   - Update progress tracking

6. **Check for Pause**
   - If `🛑 Pause After: yes` AND `Auto-Advance: no` → wait for human input
   - Otherwise continue to next task

7. **Update Backlog** (the execution engine)
   - Mark completed features in backlog as implemented
   - **Move completed items to "Completed Items" section** in backlog
   - Update status from "todo" to "✅ done" in backlog table
   - Add completion date and implementation notes
   - Add new discoveries or requirements to backlog
   - Update effort estimates based on actual implementation time
   - Execute AI-BACKLOG-META commands for automated updates
   - **Update scoring metadata** if effort estimates change significantly
   - **Re-calculate scores** if business value or priorities shift
   - **Update timestamp**: Change *Last Updated: YYYY-MM-DD HH:MM* to current time
   - **Add history**: Move current *Last Updated* to *Previously Updated* line

---

## 2. Task Status Tracking

| Status | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[x]` | Completed successfully |
| `[!]` | Blocked/needs fix |

---

## 3. Auto-Advance Configuration

### Task Template Addition
```markdown
**Auto-Advance**: yes | no
```

### Default Rules
- **Auto-Advance: yes** for Medium and Low priority tasks
- **Auto-Advance: no** for Critical tasks, deployment changes, database migrations
- **Auto-Advance: no** when `🛑 Pause After: yes`

---

## 4. State Management

### .ai_state.json Structure
```json
{
  "last_commit": "abc123",
  "file_list": ["src/main.py", "tests/test_main.py"],
  "test_results": {"passed": 15, "failed": 0},
  "current_task": "T-5",
  "completed_tasks": ["T-1", "T-2", "T-3", "T-4"]
}
```

### State Operations
- **Load**: Read state at start of execution
- **Save**: Update after each task completion
- **Ignore**: Add to .gitignore (never commit)

---

## 5. HotFix Task Generation

### When to Create HotFix
- Any "Done when:" criteria fails
- Uncaught exception during execution
- Test suite failure

### HotFix Task Template
```markdown
### T-HotFix-<n> Fix <short description>
**Priority**: Critical
**Time**: 1-2 hours
**Depends on**: [failed_task_id]

**Do**:
1. Reproduce the error
2. Fix the issue
3. Add regression test
4. Re-run failing validation

**Done when**:
- Original task's "Done when" criteria pass
- New regression test passes

**Auto-Advance**: no
**🛑 Pause After**: yes
**When Ready Prompt**: "HotFix complete - retry original task?"
```

---

## 6. Error Handling

### Safety Rules
- **Database Changes**: Always pause for human review
- **Deployment Scripts**: Always pause for human review
- **Consecutive Failures**: Stop execution after 2 consecutive failures
- **Uncaught Exceptions**: Generate HotFix task and pause

### Recovery Process
1. Generate HotFix task with error details
2. Execute HotFix task
3. Retry original task
4. Continue normal execution

---

## 7. Progress Tracking

### Simple Progress
- Count completed tasks: `[x]` vs total tasks
- Update progress in task list header
- Track blocked tasks: `[!]`

### Completion Validation
- All tasks marked `[x]` or `[!]`
- No tasks with status `[ ]`
- All "Done when" criteria validated

---

## 8. Human Checkpoints

### When to Pause
- Critical priority tasks
- Database migrations
- Deployment changes
- HotFix completions
- User explicitly requests pause

### Checkpoint Process
1. Display "When Ready Prompt"
2. Wait for user input
3. Continue execution on user approval
4. Handle user feedback if provided

---

## 9. File Maintenance

### Required Files
- Task list markdown file
- `.ai_state.json` (auto-generated, gitignored)
- Source code files
- Test files

### Git Operations
- Commit after each completed task
- Use conventional commit messages
- Never commit `.ai_state.json`

---

This approach ensures:
- **Efficient AI execution** with state caching
- **Automatic error recovery** with HotFix tasks
- **Minimal human intervention** with smart pausing
- **Clear progress tracking** for oversight
- **Safe execution** with appropriate checkpoints