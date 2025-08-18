# Pull Request

## Description
<!-- Describe the changes made in this PR -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement
- [ ] Other (please describe)

## Bug-Fix Documentation (Required for bug fixes)
<!-- Complete this section for all bug fixes (fix: and hotfix: commits) -->

### Problem Snapshot
- **Title**: Clear, concise description of the issue
- **Context (where/when)**: Where and when the issue occurs
- **Observed vs Expected**: What happens vs what should happen
- **Logs / Error**: Relevant error messages, stack traces, logs
- **Environment**: OS, dependencies, configuration
- **Dependencies**: Direct | Upstream | Downstream
- **Invariants**: 2-5 truths that must hold for the system to work correctly

### Fix Plan
- **Chosen Fix**: Description of the implemented solution
- **Didn't Touch**: What was intentionally left unchanged and why
- **Blast Radius**: Direct | Upstream | Downstream | Public contracts
- **Confidence (0-1)**: Confidence level in the fix

### Test Plan
- **Repro Test**: Test that demonstrates the original bug - should fail before fix, pass after
- **Guardrail Test**: Test that prevents regression - should pass before and after fix
- **Additional Tests**: Any other test coverage added
- **Test Files Modified**: List test files that were changed

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass (if applicable)
- [ ] Manual testing completed

## Validator Compliance
- [ ] Ran: `python3 scripts/doc_coherence_validator.py --ci --json` (attach or paste summary)
- [ ] If backlog item created, include `backlog_items/{B-xxx}/status.json` and validator summary
- [ ] No new violations introduced in FAIL mode categories
- [ ] Documentation updated if needed

## Flip PR Checklist (if applicable)
- [ ] Clean-day counters ≥ target for category
- [ ] Last 7 snapshots shown in PR body
- [ ] Changed-files gating mode confirmed (XRef/README: changed-files, Archive/Shadow: repo-wide)
- [ ] No regressions in nightly for 48h post-merge (or rollback engaged)
- [ ] Near-expiry exceptions < threshold and trending down (XRef/README only)

## Backlog Item (if applicable)
- **ID**:
- **Title**:
- **Status**:
- **Files Created/Modified**:

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes introduced
- [ ] Constitutional compliance maintained (archive immutability, no shadow-fork names, role-suffix naming)

## Bug-Fix Checklist (Required for bug fixes)
- [ ] Problem Snapshot is complete and clear
- [ ] Fix Plan documents what was changed and what wasn't
- [ ] Blast radius is assessed and documented
- [ ] Confidence level is ≥ 0.8
- [ ] Repro test demonstrates the original bug
- [ ] Guardrail test prevents regression
- [ ] Test files are included in the PR
- [ ] Emergency override documented (if applicable)

## Additional Notes
<!-- Any additional information or context -->

## Validator Summary
<!-- Paste validator output here or attach validator_report.json -->

```
Validator Report:
- Archive violations: X
- Shadow fork violations: X
- README violations: X
- Multi-rep violations: X
```

## Related Issues
<!-- Link to related issues or backlog items -->

## 📚 README / Docs Governance
- [ ] This PR does not add nonstandard README names (only `README.md` / `README-dev.md`)
- [ ] If adding/updating a README, it includes: Purpose, Usage/Integration, Owner, Last reviewed
- [ ] New README meets Creation Criteria (public surface / runbook / config contract / topical hub)
- [ ] If touching public-surface directories (e.g., `dspy-rag-system/src/vector_store/`), updated at least one of:
  - `400_guides/400_system-overview.md`
  - `500_reference-cards.md`
  - `401_consensus-log.md`
  - Local README (`dspy-rag-system/src/vector_store/README.md` or `dspy-rag-system/README.md`)
- [ ] If no docs were touched, explanation is provided for why there is no documentation impact
 - [ ] Header/footer context tags reviewed and updated (e.g., `CONTEXT_REFERENCE`, `MODULE_REFERENCE`, `MEMORY_CONTEXT`, `DOCUMENTATION_MASTER`)
