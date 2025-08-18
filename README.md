# AI Development Tasks

AI-powered development ecosystem with comprehensive governance and automation.

## Purpose

This project provides a comprehensive AI development ecosystem with automated governance, testing frameworks, and development workflows. It serves as a foundation for AI-powered development with built-in quality controls and operational excellence.

## Usage

The project provides:
- **Governance System**: Automated validation and compliance checking
- **Testing Framework**: Comprehensive test suites with marker-based execution
- **Development Workflows**: Backlog management, PRD creation, and task execution
- **Documentation**: Extensive guides and runbooks for operational excellence

## Owner

AI Development Team - Core Infrastructure

## Last Reviewed

2025-08-17

## Governance Status

| Category | Violations | Status |
|----------|------------|--------|
| archive | 0 | OK Clean |
| shadow_fork | 0 | OK Clean |
| readme | 0 | OK Clean |
| multirep | 0 | OK Clean |

*Last updated: 2025-08-17 18:30 UTC*

📊 [Weekly Summary](/.github/workflows/nightly.yml) | 📋 [Governance Runbook](400_guides/400_governance-runbook.md)

## Quick Start

```bash
# Install dependencies
./install_dependencies.sh

# Run governance check
python3 scripts/doc_coherence_validator.py --ci --json

# Run tests
python3 -m pytest tests/ -m "tier_1 and unit"

# Generate status badge
python3 scripts/generate_status_badge.py
```

## Project Structure

- **`000_core/`** - Core workflows and backlog management
- **`100_memory/`** - Memory context and development state
- **`200_setup/`** - Environment setup and configuration
- **`400_guides/`** - Development guides and runbooks
- **`500_research/`** - Research and reference materials
- **`dspy-rag-system/`** - DSPy RAG system implementation
- **`scripts/`** - Automation and utility scripts
- **`tests/`** - Test suite and validation

## Governance System

This project uses a comprehensive governance system with:

- **Validator**: Checks for violations across all categories
- **Ratchet**: Prevents regression in readme/multirep violations
- **Flip Automation**: Automatically flips categories to FAIL mode when clean
- **Rollback Protection**: Automatic rollback for >5% false positives
- **Schema Guard**: Prevents unauthorized schema changes
- **Owner Accountability**: Suggested owners for violations

### SLOs (Service Level Objectives)
- **PR path time**: ≤5 min p95
- **Nightly duration**: ≤15 min p95
- **False positives**: <1% per week
- **Time-to-flip**: ≤48h after clean window completion

## Development Workflow

1. **Backlog Management**: Use `000_core/000_backlog.md` for prioritization
2. **PR Creation**: Follow templates in `.github/PULL_REQUEST_TEMPLATE.md`
3. **Governance Check**: All PRs must pass governance CI
4. **Testing**: Run comprehensive test suite before merging
5. **Documentation**: Update relevant guides and runbooks

## Key Commands

```bash
# Governance
make gov/validate          # Run validator
make gov/status           # Show current status
make gov/counters         # Show clean-day counters

# Development
make test/unit            # Run unit tests
make test/integration     # Run integration tests
make test/e2e             # Run end-to-end tests

# Utilities
python3 scripts/backlog_cli.py create-backlog-item  # Create backlog item
python3 scripts/weekly_metrics_with_owners.py       # Generate weekly summary
```

## Documentation

- **[Governance Runbook](400_guides/400_governance-runbook.md)** - Operational guidance
- **[System Overview](400_guides/400_system-overview.md)** - Technical architecture
- **[Consensus Log](401_consensus-log.md)** - Major decisions and changes
- **[Flip Log](402_validator-flip-log.md)** - Category transition history
- **[Reference Cards](500_reference-cards.md)** - Quick reference guides

## Contributing

1. Follow the governance system and pass all checks
2. Update documentation for any changes
3. Run tests before submitting PRs
4. Follow the consensus framework for major decisions

## License

This project is part of the AI Development Ecosystem.
