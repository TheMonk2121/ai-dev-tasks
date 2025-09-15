# 300_phase2_baseline_config_legacy

## ⚠️ Legacy Configuration - Do Not Use

This file contains **legacy Phase-2 baseline configuration** that is no longer current with project standards.

### 📁 Contents

- `300_phase2_baseline_config_legacy.env` - Phase-2 exact configuration with rollback audit

### 🚫 Status: Legacy

This configuration file is **outdated** and contains references to completed development phases:

#### **Issues:**
- **Phase References**: References "Phase-2" which is a completed development phase
- **Outdated Commands**: Uses `python3 scripts/` instead of `uv run python scripts/`
- **Historical Metrics**: Contains Phase-2 baseline metrics (`P≥0.159, R≥0.166, F1≥0.159`)
- **Rollback Config**: This is a rollback and audit configuration from a completed phase

#### **Phase-2 References:**
- **Target Metrics**: `P≥0.159, R≥0.166, F1≥0.159` (Phase-2 baseline)
- **Configuration Focus**: Heavy RAGChecker tuning parameters (30 environment variables)
- **Purpose**: Rollback and audit configuration to restore Phase-2 stable floor

#### **Current Standards:**
- **Python Execution**: `uv run python scripts/`
- **Package Management**: `uv sync --extra dev`
- **Testing**: `uv run pytest -q`

### 🔒 Archive Status

This configuration is **archived** and should not be used for active development. The configuration is preserved for historical reference only.

### 📅 Archived: September 2025

**Reason**: Legacy Phase-2 configuration with outdated commands and historical baseline metrics.
