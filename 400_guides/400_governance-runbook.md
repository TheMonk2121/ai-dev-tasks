# Governance Runbook

This runbook provides operational guidance for the AI Development
Governance System v1.0.

## 🔎 TL;DR

| what this file is | read when | do next |
|----|----|----|
| Operational guidance for governance system | When dealing with governance violations or system issues | Follow the appropriate playbook for the specific issue |

## 🎯 **Current Status**

- **Status**: OK **ACTIVE** - Governance runbook operational and current

- **Priority**: 🔥 Critical - Essential for governance operations

- **Points**: 4 - Moderate complexity, operational importance

- **Dependencies**: 400_guides/400_cursor-context-engineering-guide.md,
  000_core/000_backlog.md

- **Next Steps**: Maintain operational procedures and update as system
  evolves

## Quick Reference

### SLOs (Service Level Objectives)

- **PR path time**: ≤5 min p95 (governance workflow)
- **Nightly duration**: ≤15 min p95
- **False positives**: \<1% per week; automatic rollback within 48h if
  \>5%
- **Waiver discipline**: zero renewals; near-expiry waivers resolved ≤7
  days
- **Time-to-flip**: ≤48h after a category reaches 0 violations and clean
  window completes

### Emergency Contacts

- **Primary**: AI Development Team
- **Escalation**: Repository maintainers
- **On-call**: Check GitHub notifications for governance alerts

## PR Triage Flow

### Normal PR Processing

1.  **Governance CI** runs automatically on all PRs
2.  **Validator** checks for violations in all categories
3.  **Ratchet** prevents increases in readme/multirep for changed files
4.  **Ledger check** ensures new exceptions have approval + ≤7d expiry
5.  **Schema guard** prevents unauthorized schema changes

### PR Failure Scenarios

#### Violations in FAIL Mode Categories

**Symptom**: PR fails with “FAIL: {category} has {N} violations in FAIL
mode”

**Action**: 1. Check which files are causing violations 2. Fix
violations or add appropriate exceptions 3. Re-run governance CI

#### Ratchet Failure

**Symptom**: PR fails with ratchet violation message

**Action**: 1. Identify which files increased readme/multirep violations
2. Fix the violations or justify the increase 3. Re-run governance CI

#### Ledger Addition Without Approval

**Symptom**: PR fails with “Invalid ledger additions detected”

**Action**: 1. Add ‘exception-approved’ label to PR 2. Ensure new
exceptions have ≤7d expiry 3. Re-run governance CI

#### Schema Change Without Migration

**Symptom**: PR fails with “Schema change detected without proper
documentation”

**Action**: 1. Update `docs/VALIDATOR_SCHEMA_MIGRATION.md` 2. Add
‘schema-migration’ label to PR 3. Re-run governance CI

## Flip/Rollback Playbook

### Automatic Flips

Flips happen automatically when clean-day counters reach targets: -
**Archive**: 3 days clean → FAIL mode - **Shadow**: 7 days clean → FAIL
mode - **XRef**: 5 days clean → FAIL mode - **README**: 14 days clean →
FAIL mode

### Manual Flip Override

If automatic flip is needed: 1. Run governance drill with rollback
scenario 2. Verify all systems are stable 3. Manually trigger flip via
flip manager

### Rollback Procedure

**Trigger**: \>5% false positives within 48h of flip

**Automatic Rollback**: 1. Flip manager detects high violation count 2.
Creates rollback PR automatically 3. Reverts category to WARN mode 4.
Notifies maintainers

**Manual Rollback**: 1. Run governance drill with rollback scenario 2.
Manually revert category to WARN mode 3. Update flip log with rollback
reason 4. Investigate root cause

## Ledger Policy

### Exception Management

- **No renewals**: Expired exceptions cannot be renewed without content
  changes
- **Short expiry**: All exceptions must have ≤7d expiry
- **Approval required**: New exceptions need ‘exception-approved’ label
- **Owner accountability**: Weekly summary shows suggested owners for
  violations

### Ledger Cleanup

- **Weekly review**: Check near-expiry exceptions (≤7 days)
- **Owner notification**: Weekly summary includes owner suggestions
- **Automatic cleanup**: Expired exceptions are automatically removed

## Monitoring & Alerts

### Daily Monitoring

- **Governance CI**: Check for PR failures and violations
- **Clean-day counters**: Monitor progress toward flip targets
- **Exception expiry**: Review near-expiry exceptions

### Weekly Monitoring

- **Weekly summary**: Review violation trends and owner suggestions
- **SLO compliance**: Check PR path times and nightly durations
- **Exception trends**: Monitor waiver usage and expiry patterns

### Monthly Monitoring

- **Governance drill**: Run chaos test scenarios
- **Schema review**: Check for unauthorized schema changes
- **Performance review**: Analyze SLO compliance trends

## Troubleshooting

### Common Issues

#### High PR Path Times

**Symptom**: Governance CI takes \>5 minutes

**Investigation**: 1. Check Python dependency cache 2. Review validator
performance 3. Analyze changed files scope

**Resolution**: 1. Optimize validator logic 2. Improve caching strategy
3. Reduce changed files scope if needed

#### False Positive Spikes

**Symptom**: Sudden increase in violations without code changes

**Investigation**: 1. Check validator logic changes 2. Review exception
ledger 3. Analyze recent commits

**Resolution**: 1. Fix validator logic if needed 2. Add appropriate
exceptions 3. Consider rollback if \>5% false positives

#### Flip Failures

**Symptom**: Automatic flips not happening when expected

**Investigation**: 1. Check clean-day counters 2. Verify flip manager is
running 3. Review flip log for errors

**Resolution**: 1. Fix counter calculation if needed 2. Restart flip
manager 3. Manually trigger flip if necessary

### Emergency Procedures

#### Complete System Failure

**Symptom**: Governance CI completely broken

**Action**: 1. Disable governance CI temporarily 2. Investigate root
cause 3. Fix and re-enable 4. Run governance drill to verify

#### Data Corruption

**Symptom**: Validator state or metrics corrupted

**Action**: 1. Restore from bot/validator-state backup 2. Re-run
governance CI 3. Verify data integrity 4. Update documentation

## Error Reduction Governance

### Error Reduction Lessons Learned Organization

**Standard**: All error reduction lessons learned must be organized by error code in `400_guides/400_comprehensive-coding-best-practices.md`

**Requirements**:
- **Error Code Organization**: Group all information (problem, bad fix, good fix, result, tool) by specific Ruff error code
- **Decision Matrix**: Include auto-fix safety classification (Safe vs. Dangerous)
- **Anti-Patterns**: Document what NOT to do with specific examples
- **Success Metrics**: Include error reduction statistics (before/after counts)

**Update Procedures**:
- New error reduction lessons must be added to the appropriate error code section
- All lessons must include problem description, bad fix example, good fix example, and results
- Anti-patterns must include the specific command that caused the problem

**Quality Gates**:
- Lessons must include actual error counts (before/after)
- Anti-patterns must include the specific command that failed
- All examples must be tested and verified

### Auto-Fix Decision Matrix

**Safe Auto-Fixes** (Tested and Proven):
- **RUF001**: Unicode character replacement (31 → 0 errors)
- **F401**: Unused imports (434 → 0 errors)
- **I001**: Import formatting (222 → 0 errors)
- **F541**: F-string issues (84 → 0 errors)

**Dangerous Auto-Fixes** (Tested and Failed):
- **PT009**: Unittest assertions (127 → 1328 errors)
- **B007**: Loop variables (35 → 206 errors)
- **RUF013**: Implicit Optional (29 → 213 errors)
- **F841**: Unused variables (24 → 41 errors)
- **RUF010**: F-string conversion (12 → 24 errors)

### Error Reduction Tools

**Required Tools**:
- `scripts/fix_unicode_characters.py` - For RUF001 Unicode character fixes
- `scripts/smart_error_fix.py` - For safe auto-fix application
- `ruff check --select <ERROR_CODE> --fix` - For standard safe fixes

**Validation Commands**:
- `ruff check --select RUF001` - Verify Unicode fixes
- `ruff check --select F401,I001,F541` - Verify import and f-string fixes
- `python3.12 scripts/smart_error_fix.py <target_paths>` - Apply safe fixes only

## Maintenance Tasks

### Quarterly Tasks

- **Action updates**: Update pinned action versions
- **Dependency updates**: Update Python dependencies
- **Drill execution**: Run comprehensive governance drill
- **Documentation review**: Update runbook and migration docs

### Annual Tasks

- **Schema review**: Evaluate schema version freeze
- **SLO review**: Update SLOs based on performance data
- **Process review**: Evaluate governance effectiveness
- **Training**: Update team on governance procedures

## References

- **Validator Schema**: `docs/VALIDATOR_SCHEMA_MIGRATION.md`
- **Consensus Log**: `401_consensus-log.md`
- **Flip Log**: `402_validator-flip-log.md`
- **Governance CI**: `.github/workflows/governance.yml`
- **Chaos Test**: `scripts/validator_chaos_test.py`
- **Weekly Summary**: `scripts/weekly_metrics_with_owners.py`

<!-- README_AUTOFIX_START -->

## Auto-generated sections for 400_governance-runbook.md

## Generated: 2025-08-18T08:03:22.746480

## Missing sections to add:

## Last Reviewed

2025-08-18

## Owner

Documentation Team

## Purpose

Describe the purpose and scope of this document

## Usage

Describe how to use this document or system

<!-- README_AUTOFIX_END -->
