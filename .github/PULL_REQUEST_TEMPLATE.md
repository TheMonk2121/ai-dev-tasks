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
