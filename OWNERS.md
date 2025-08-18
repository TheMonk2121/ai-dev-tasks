# Repository Owners

This file maps top-level directories to their owners for accountability and governance.

## Directory Ownership

### Core Infrastructure
- `000_core/` - @ai-dev-team
- `100_memory/` - @ai-dev-team
- `200_setup/` - @ai-dev-team
- `400_guides/` - @ai-dev-team

### Research & Reference
- `500_research/` - @ai-dev-team
- `500_reference-cards.md` - @ai-dev-team

### Implementation
- `dspy-rag-system/` - @ai-dev-team
- `scripts/` - @ai-dev-team
- `tests/` - @ai-dev-team

### Documentation
- `docs/` - @ai-dev-team
- `dashboard/` - @ai-dev-team

### Data & Configuration
- `data/` - @ai-dev-team
- `config/` - @ai-dev-team
- `schemas/` - @ai-dev-team

### Archives
- `600_archives/` - @ai-dev-team (immutable)

### Root Files
- `*.md` - @ai-dev-team
- `*.yml` - @ai-dev-team
- `*.yaml` - @ai-dev-team
- `*.json` - @ai-dev-team
- `*.py` - @ai-dev-team
- `*.sh` - @ai-dev-team

## Owner Responsibilities

### Primary Owner (@ai-dev-team)
- **Governance**: Ensure validator compliance across all directories
- **Maintenance**: Keep documentation and code up to date
- **Review**: Review PRs and ensure quality standards
- **Escalation**: Handle governance violations and exceptions

### Specific Responsibilities
1. **Validator Compliance**: Ensure all files pass validator checks
2. **Exception Management**: Review and approve ledger exceptions
3. **Schema Changes**: Approve validator schema migrations
4. **Flip Management**: Monitor and manage category flips
5. **Rollback Coordination**: Handle rollbacks when needed

## Contact Information

- **Primary**: AI Development Team
- **Escalation**: Repository maintainers
- **Emergency**: Check GitHub notifications for governance alerts

## Governance Integration

This ownership mapping is used by:
- **Weekly Summary**: `scripts/weekly_metrics_with_owners.py` suggests owners for violations
- **Governance CI**: Validates owner assignments
- **Exception Approval**: Owners approve exceptions for their directories
- **Accountability**: Clear ownership for governance violations
