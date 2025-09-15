# 300_testing-scripts_legacy

## ⚠️ Legacy Directory - Do Not Use

This directory contains **legacy testing scripts** that are no longer current with project standards.

### 📁 Contents

- `bedrock_test.py` - AWS Bedrock integration test
- `evaluation_approach_discussion.py` - DSPy evaluation approach discussion
- `memory_benchmark.py` - Memory context system benchmark
- `performance_benchmark.py` - Performance benchmark for critical scripts
- `ragchecker_official_evaluation.py` - Official RAGChecker evaluation script
- `ragchecker_performance_monitor.py` - RAGChecker performance monitoring

### 🚫 Status: Legacy

These scripts were created during development but **contain outdated commands** that don't align with current project standards:

#### **Issues:**
- **Python Commands**: Uses `python3` instead of `uv run python`
- **Package Installation**: References `pip install` instead of `uv sync`
- **Command Standards**: Not aligned with current UV package management

#### **Current Standards:**
- **Python Execution**: `uv run python scripts/`
- **Package Management**: `uv sync --extra dev`
- **Testing**: `uv run pytest -q`

### 🔒 Archive Status

This directory is **archived** and should not be used for active development. The scripts are preserved for historical reference only.

### 📅 Archived: September 2025

**Reason**: Outdated command usage not aligned with current UV package management standards.
