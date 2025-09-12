# Process Task List: Simplify Overengineered Quality Gates

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Execution engine for simplifying overengineered quality gates | When running the quality gates simplification workflow | 1) Start with T-1; 2) Remove dead code; 3) Add missing gates; 4) Optimize performance |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Quality gates simplification workflow
- **Priority**: 🔥 Critical - Essential for development velocity
- **Points**: 6 - Moderate complexity, high impact
- **Dependencies**: None
- **Next Steps**: Execute T-1 to remove dead database sync check

## Run Loop

### T-1 Remove Dead Database Sync Check
- **Priority:** Critical
- **Auto-Advance:** yes
- **🛑 Pause After:** no

**Do:**
1. Remove database sync check from `.pre-commit-config.yaml`
2. Archive `scripts/database_sync_check.py` to `600_archives/`
3. Test pre-commit hook installation
4. Verify no errors in pre-commit workflow

**Done when:**
- [ ] Database sync check removed from .pre-commit-config.yaml
- [ ] scripts/database_sync_check.py archived
- [ ] Pre-commit hooks install without errors
- [ ] Pre-commit workflow runs successfully

### T-2 Simplify Conflict Detection Script
- **Priority:** Critical
- **Auto-Advance:** yes
- **🛑 Pause After:** no
- **Depends on:** T-1

**Do:**
1. Replace complex conflict check with simple bash command
2. Update `.pre-commit-config.yaml` with new conflict check
3. Test conflict detection with known merge markers
4. Benchmark execution time

**Done when:**
- [x] Conflict check reduced to simple git grep command
- [x] No caching, threading, or complex logic
- [x] Execution time <1 second (0.059s measured)
- [x] Same detection capability as original

### T-3 Add Type Checking Gate
- **Priority:** High
- **Auto-Advance:** yes
- **🛑 Pause After:** no
- **Depends on:** T-2

**Do:**
1. Add Pyright type checking to `.pre-commit-config.yaml`
2. Configure to run on Python files only
3. Test with known type errors
4. Verify execution time <2 seconds

**Done when:**
- [x] Pyright type checking added to .pre-commit-config.yaml
- [x] Type checking runs on Python files only
- [x] Clear error messages for type issues
- [x] Execution time <2 seconds

### T-4 Add Security Scanning Gate
- **Priority:** High
- **Auto-Advance:** yes
- **🛑 Pause After:** no
- **Depends on:** T-3

**Do:**
1. Install bandit security scanner
2. Add bandit to `.pre-commit-config.yaml`
3. Configure medium severity threshold
4. Test with known vulnerabilities

**Done when:**
- [x] Bandit security scanning added to pre-commit hooks
- [x] Scans Python files for common vulnerabilities
- [x] Configurable severity levels
- [x] Execution time <2 seconds (0.102s measured)

### T-5 Optimize Documentation Validation
- **Priority:** Medium
- **Auto-Advance:** yes
- **🛑 Pause After:** no
- **Depends on:** T-4

**Do:**
1. Simplify `scripts/pre_commit_doc_validation.sh`
2. Remove complex caching and worker pools
3. Focus on essential checks only
4. Test with known documentation issues

**Done when:**
- [x] Documentation validation simplified to core checks
- [x] Remove complex caching and worker pools
- [x] Focus on broken links and basic structure
- [x] Execution time <1 second (0.030s measured)

### T-6 Final Performance Validation
- **Priority:** Medium
- **Auto-Advance:** no
- **🛑 Pause After:** yes
- **Depends on:** T-5
- **When Ready Prompt:** "Quality gates simplified! Total execution time: X seconds. Ready to commit changes?"

**Do:**
1. Run complete pre-commit workflow
2. Measure total execution time
3. Test with various file types and sizes
4. Validate all gates work correctly
5. Update quality gates documentation

**Done when:**
- [x] All gates complete in <5 seconds total (4.491s measured)
- [x] No complex caching or parallel processing
- [x] Simple, reliable operation
- [x] Clear error messages when gates fail

## HotFix Task Template

### T-HotFix-`<n>` Fix `<short description>`
- **Priority:** Critical
- **Time:** 1-2 hours
- **Depends on:** `[failed_task_id]`

**Do:**
1. Reproduce the error
2. Fix the issue
3. Add regression test
4. Re-run failing validation

**Done when:**
- Original task's "Done when" criteria pass
- New regression test passes

**Auto-Advance:** no
**🛑 Pause After:** yes
**When Ready Prompt:** "HotFix complete - retry original task?"

## State Management

### .ai_state.json Structure
```json
{
  "last_commit": "abc123",
  "file_list": [".pre-commit-config.yaml", "scripts/"],
  "test_results": {"passed": 0, "failed": 0},
  "current_task": "T-1",
  "completed_tasks": [],
  "performance_metrics": {
    "total_execution_time": 0,
    "individual_gates": {}
  }
}
```

## Error Handling

### Safety Rules
- **Pre-commit Changes**: Always test installation before committing
- **Script Removal**: Archive files, don't delete permanently
- **Consecutive Failures**: Stop after 2 consecutive failures
- **Performance Regression**: Revert if execution time increases

### Recovery Process
1. Generate HotFix task with error details
2. Execute HotFix task
3. Retry original task
4. Continue normal execution

## Progress Tracking

### Simple Progress
- Count completed tasks: `[x]` vs total tasks (6)
- Update progress in task list header
- Track blocked tasks: `[!]`

### Completion Validation
- All tasks marked `[x]` or `[!]`
- No tasks with status `[ ]`
- All "Done when" criteria validated
- Performance targets met

## Human Checkpoints

### When to Pause
- T-6 Final Performance Validation (always pause)
- HotFix completions
- Performance regression detected
- User explicitly requests pause

### Checkpoint Process
1. Display "When Ready Prompt"
2. Wait for user input
3. Continue execution on user approval
4. Handle user feedback if provided

## File Maintenance

### Required Files
- Task list markdown file
- `.ai_state.json` (auto-generated, gitignored)
- `.pre-commit-config.yaml`
- Modified scripts

### Git Operations
- Commit after each completed task
- Use conventional commit messages
- Never commit `.ai_state.json`

## Success Criteria

This approach ensures:
- **Fast execution** - All gates complete in <5 seconds
- **Simple debugging** - Clear error messages and no complex logic
- **Reliable operation** - No flaky failures or complex dependencies
- **Actual value** - Gates catch real issues that improve code quality
- **Developer satisfaction** - Gates are boring and reliable, not bypassed

## 🔄 Execution Flow

1. **Parse Task List**: Extract tasks and dependencies
2. **Validate State**: Check `.ai_state.json` for current context
3. **Execute Tasks**: Run tasks in priority order
4. **Update State**: Record progress in `.ai_state.json`
5. **Test Performance**: Validate <5 second total execution time
6. **Generate Report**: Create completion summary with performance metrics
