# Governance Rails Archive

This directory contains archived governance workflows and components from the transition to steady-state operations.

## Archived Components

### Transitional Workflows
- `validator.yml` - Original validator workflow (replaced by governance.yml)
- `nightly.yml` - Original nightly workflow (replaced by governance.yml)
- `archive-flip.yml` - Archive flip workflow (automated)
- `shadow-flip.yml` - Shadow flip workflow (automated)
- `xref-flip.yml` - XRef flip workflow (automated)
- `readme-flip.yml` - README flip workflow (automated)
- `archive-zeroization.yml` - Archive zeroization workflow (completed)
- `shadow-fix.yml` - Shadow fix workflow (completed)
- `xref-proof.yml` - XRef proof workflow (completed)
- `readme-batch-2.yml` - README batch workflow (completed)

## Archive Date
**Date**: 2025-08-17
**Reason**: Transition to steady-state governance operations
**Status**: Immutable snapshot

## Current State
- **Active Workflow**: `.github/workflows/governance.yml` (consolidated)
- **Active Workflow**: `.github/workflows/nightly.yml` (scheduled)
- **Active Workflow**: `.github/workflows/governance-drill.yml` (on-demand)

## Migration Notes
- All transitional workflows have been consolidated into governance.yml
- Flip automation is now handled by the flip manager
- Proof workflows are no longer needed (steady-state achieved)
- Archive and shadow fixes are complete (0 violations)

## Reference
- **Consensus Log**: `401_consensus-log.md`
- **Flip Log**: `402_validator-flip-log.md`
- **Runbook**: `400_guides/400_governance-runbook.md`
