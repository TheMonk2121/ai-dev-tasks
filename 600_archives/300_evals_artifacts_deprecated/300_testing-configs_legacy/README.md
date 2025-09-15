# 300_testing-configs_legacy

## ⚠️ Legacy Directory - Do Not Use

This directory contains **legacy Phase-2 testing configurations** that are no longer current with project standards.

### 📁 Contents

- `phase1_ragchecker_flags.sh` - Phase 1 RAGChecker enhancement flags
- `phase2_baseline_v1.1.sh` - Phase-2 exact configuration with rollback audit
- `rollback_phase2_baseline.sh` - Phase-2 rollback configuration to restore stable floor

### 🚫 Status: Legacy

These configuration files are **outdated** and contain references to completed development phases:

#### **Issues:**
- **Phase References**: All files reference "Phase-2" which is a completed development phase
- **Outdated Commands**: Uses `python3 scripts/` instead of `uv run python scripts/`
- **Historical Metrics**: Contains Phase-2 baseline metrics that are no longer current
- **Rollback Configs**: These are rollback and audit configurations from a completed phase

#### **Phase-2 References:**
- **Target Metrics**: `P≥0.159, R≥0.166, F1≥0.159` (Phase-2 baseline)
- **Configuration Focus**: Heavy RAGChecker tuning parameters (59 environment variables)
- **Purpose**: Rollback and audit configurations to restore Phase-2 stable floor

#### **Current Standards:**
- **Python Execution**: `uv run python scripts/`
- **Package Management**: `uv sync --extra dev`
- **Testing**: `uv run pytest -q`

### 🔒 Archive Status

This directory is **archived** and should not be used for active development. The configurations are preserved for historical reference only.

### 📅 Archived: September 2025

**Reason**: Legacy Phase-2 configurations with outdated commands and historical baseline metrics.
