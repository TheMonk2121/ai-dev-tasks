# Task List: B-1006 DSPy 3.0 Migration (Simplified)

## Overview

Simple migration from DSPy 2.6.27 to DSPy 3.0.1. Replace custom assertion framework with native `dspy.Assert` support where beneficial. **Schema compatibility confirmed** - existing signatures work identically in DSPy 3.0.

## Implementation Tasks

### Task 1: Upgrade DSPy Version
**Priority:** Critical
**Estimated Time:** 1 hour
**Dependencies:** None

**Do:**
1. Update `requirements.txt` to pin DSPy 3.0.1
2. Update `requirements-constraints.txt` if needed
3. Test installation in virtual environmen

**Done when:**
- [ ] DSPy 3.0.1 successfully installed
- [ ] Basic import and configuration works
- [ ] No dependency conflicts

### Task 2: Test Compatibility
**Priority:** Critical
**Estimated Time:** 2 hours
**Dependencies:** Task 1

**Do:**
1. Run existing tests to ensure nothing breaks
2. Test core DSPy functionality (model switching, orchestration)
3. Verify assertion framework still works
4. Check memory rehydration system

**Done when:**
- [ ] All existing tests pass
- [ ] Core functionality unchanged
- [ ] No breaking changes identified

### Task 3: Replace Custom Assertions (Optional)
**Priority:** Medium
**Estimated Time:** 2 hours
**Dependencies:** Task 2

**Do:**
1. Identify where native `dspy.Assert` can replace custom assertions
2. Replace simple cases firs
3. Test to ensure functionality preserved
4. Keep custom framework for complex cases

**Done when:**
- [ ] Native assertions used where beneficial
- [ ] Custom framework preserved for complex cases
- [ ] All tests still pass

### Task 4: Final Validation
**Priority:** Critical
**Estimated Time:** 1 hour
**Dependencies:** Task 3

**Do:**
1. Run full test suite
2. Test enhanced workflow integration
3. Verify memory systems work
4. Document any changes made

**Done when:**
- [ ] All tests pass
- [ ] System functionality verified
- [ ] Changes documented
