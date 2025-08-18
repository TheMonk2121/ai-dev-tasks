# Global Bug-Fix Playbook

**TL;DR**: Use ⌘⌥B (macOS) / Ctrl+Alt+B (Windows/Linux) to trigger the "Run Bug-Fix Playbook" preset in Cursor. This injects a structured debugging workflow that ensures CS-level rigor without slowing velocity.

### Quick Reference
- **Preset Name**: "Run Bug-Fix Playbook"
- **Keyboard Shortcut**: ⌘⌥B (macOS) / Ctrl+Alt+B (Windows/Linux)
- **When to Use**: `fix:` commits, `hotfix:` commits, fragile module changes
- **Required Sections**: Problem Snapshot → Dual Review → Resolution Check
- **Test Requirements**: Repro test + Guardrail test
- **Framework Selection**: Based on commit type and module location

### Mini Prompt Template (Copy/Paste)
```
You are a senior debugging assistant. Help me debug this issue following the Global Bug-Fix Playbook structure:

## Problem Snapshot
- Title: [Brief description]
- Context: [Where/when it occurs]
- Observed vs Expected: [What happens vs what should happen]
- Logs/Error: [Relevant error messages]
- Environment: [OS, dependencies, config]
- Dependencies: [Direct/Upstream/Downstream]
- Invariants: [2-5 truths that must hold]

## Dual Review
### 🔴 Red (risks/root causes/questions)
### 🔵 Blue (minimal diff + test strategy)

## Resolution Check
- Chosen Fix: [Description]
- Didn't Touch: [What was left unchanged and why]
- Blast Radius: [Direct/Upstream/Downstream/Public contracts]
- Confidence (0-1): [Confidence level]
- Test Plan: [Repro + Guardrail tests]
- Rollout & Observe: [Optional: flags, logs, metrics]
```

## Purpose

This playbook provides a structured approach to debugging that balances velocity with rigor. It's designed to prevent regressions, ensure proper test coverage, and maintain code quality while keeping development fast.

## Usage

### Quick Start
1. **Trigger Preset**: Use keyboard shortcut ⌘⌥B (macOS) / Ctrl+Alt+B (Windows/Linux) in Cursor
2. **Follow Structure**: Complete all required sections below
3. **Validate**: Ensure tests prove the fix and guard against regressions

### When to Use
- **Bug fixes** (commit prefix: `fix:`)
- **Hot fixes** (commit prefix: `hotfix:`)
- **Critical issues** requiring immediate attention
- **Changes to fragile modules** (validator, vector_store, dashboard, archive)

### Emergency Override
For critical outages requiring immediate fixes:
1. Document the emergency in the PR description
2. Use `--no-verify` if necessary
3. Follow up with proper documentation within 24 hours
4. Schedule post-mortem review

## Core Principles

### 1. Least-Diff Principle
Make the smallest possible change that fixes the issue. Avoid refactoring unrelated code.

### 2. Contracts First
Consider the impact on public contracts, APIs, and interfaces before making changes.

### 3. Tests Prove It
Every bug fix must include:
- **Repro test**: Proves the bug existed
- **Guardrail test**: Prevents regression

## Playbook Structure

### Problem Snapshot
Document the issue clearly to ensure proper understanding and prevent similar bugs.

```markdown
## Problem Snapshot
- **Title**: [Clear, concise description of the issue]
- **Context (where/when)**: [Where and when the issue occurs]
- **Observed vs Expected**: [What happens vs what should happen]
- **Logs / Error**: [Relevant error messages, stack traces, logs]
- **Environment**: [OS, dependencies, configuration]
- **Dependencies**: Direct | Upstream | Downstream
- **Invariants**: [2-5 truths that must hold for the system to work correctly]
```

### Dual Review
Conduct a systematic review to identify risks and plan the fix.

```markdown
## Dual Review

### 🔴 Red (risks / root causes / questions)
- [List potential risks and root causes]
- [Identify questions that need answers]
- [Consider security implications]
- [Evaluate impact on performance]

### 🔵 Blue (minimal viable diff + test strategy)
- [Describe the minimal change needed]
- [Outline test strategy (repro + guardrail)]
- [Plan for rollback if needed]
- [Consider observability requirements]
```

### Resolution Check
Ensure the fix is complete, safe, and properly tested.

```markdown
## Resolution Check
- **Chosen Fix**: [Description of the implemented solution]
- **Didn't Touch**: [What was intentionally left unchanged and why]
- **Blast Radius**: Direct | Upstream | Downstream | Public contracts
- **Confidence (0-1)**: [Confidence level in the fix]
- **Test Plan**: [How to reproduce the bug and prevent regression]
- **Rollout & Observe** (optional): [Feature flags, logging, metrics]
```

## Framework Selection

### Based on Commit Type
- **`fix:`** → Use this playbook (required)
- **`hotfix:`** → Use this playbook (required)
- **`refactor:`** → Consider 005 Feature Refactor Framework
- **`feat:`** → Consider 001-003 governance workflow

### Based on Module
- **`src/validator/**`** → Always use this playbook
- **`src/vector_store/**`** → Always use this playbook
- **`src/dashboard/**`** → Always use this playbook
- **`scripts/archive_*.py`** → Always use this playbook

## Test Requirements

### Minimum Test Coverage
Every bug fix must include:

1. **Repro Test**: Proves the bug existed
   ```python
   def test_bug_reproduction():
       # Test that demonstrates the original bug
       # This should fail before the fix, pass after
   ```

2. **Guardrail Test**: Prevents regression
   ```python
   def test_bug_prevention():
       # Test that ensures the bug cannot recur
       # This should pass before and after the fix
   ```

### Test Naming Convention
- Repro tests: `test_<bug_description>_reproduction`
- Guardrail tests: `test_<bug_description>_prevention`

## PR Template Requirements

When creating a bug fix PR, include these sections:

### Bug Snapshot
- Complete the Problem Snapshot section above
- Include relevant logs and error messages
- Document environment details

### Fix Plan
- Describe the chosen fix
- List what wasn't changed and why
- Document blast radius and confidence level

### Test Plan
- List the repro and guardrail tests added
- Explain how tests prevent regression
- Include any additional test coverage

## Closure Ritual

Before merging a bug fix:

1. **Review Complete**: All sections of the playbook are filled
2. **Tests Pass**: Both repro and guardrail tests are green
3. **Blast Radius Assessed**: Impact on other systems is understood
4. **Confidence High**: Confidence level ≥ 0.8
5. **Documentation Updated**: Any relevant docs are updated

## Integration

### With Existing Workflows
This playbook complements the existing 000→003 governance workflow:
- **000**: Backlog prioritization
- **001**: PRD creation
- **002**: Task generation
- **003**: Task processing
- **004**: Bug fix playbook (this document)
- **005**: Feature refactor framework

### With Cursor IDE
- **Preset**: "Run Bug-Fix Playbook" (⌘⌥B / Ctrl+Alt+B)
- **Rules**: Hot-zone rules for fragile modules
- **Integration**: Works with existing Cursor capabilities

### With CI/CD
- **PR Template**: Automatic application of bug fix sections
- **CI Guard**: Validation of playbook compliance
- **Enforcement**: Automated checks for test coverage

## Troubleshooting

### Common Issues

**Preset not working?**
- Check Cursor version compatibility
- Verify keyboard shortcut configuration
- Try manual copy/paste from quick reference

**Rules not triggering?**
- Ensure you're editing files in protected directories
- Check commit message prefix (fix:, hotfix:)
- Verify Cursor rule configuration

**CI guard failing?**
- Complete all required PR template sections
- Ensure test files are included in the PR
- Check for proper commit message format

### Getting Help
- **Quick Reference**: See the Quick Reference section above in this document
- **Cursor Preset**: See `docs/cursor/presets/debug_playbook_preset.md`
- **CI Configuration**: See `ci/bugfix-guard.sh`

## Version History

- **v1.0**: Initial release with core playbook structure
- **v1.1**: Enhanced test requirements and framework selection
- **v1.2**: Added emergency override procedures
- **v1.3**: Integrated with CI/CD pipeline

---

**Document Version**: 1.3
**Last Updated**: Current Date
**Owner**: Development Team
**Reviewers**: To be assigned
**Approval Status**: Pending
