# Deprecated Evaluation System Files

This directory contains files from the legacy RAGChecker evaluation system that have been deprecated in favor of the new clean DSPy evaluator.

## Deprecation Date
September 16, 2025

## Reason for Deprecation
The legacy RAGChecker evaluation system has been replaced by the clean DSPy evaluator (`300_evals/scripts/evaluation/clean_dspy_evaluator.py`) which provides:
- Simplified evaluation workflow
- Better performance metrics
- Cleaner codebase
- More reliable results
- Better integration with DSPy framework

## Directory Structure

### `legacy_evaluation_scripts/`
Contains the main evaluation scripts from the old RAGChecker system:
- `ragchecker_official_evaluation.py` (multiple copies from different locations)
- `health_gated_evaluation.py`
- `evaluation_system_integration.py`
- `production_evaluation.py`
- `nightly_smoke_evaluation.py`
- `test_enhanced_ragchecker.py`
- `run_ragchecker_with_governance.py`
- `ragchecker_performance_optimizer.py`

### `legacy_shell_scripts/`
Contains shell scripts for running legacy evaluations:
- `run_ragchecker_*.sh` - Various RAGChecker execution scripts
- `run_*evaluation*.sh` - Other evaluation execution scripts

### `legacy_tests/`
Contains test files for the legacy system:
- `test_ragchecker_official_evaluation.py`
- `test_health_gated_evaluation.py`

### `legacy_configs/`
Contains configuration files for the legacy system:
- `ragchecker_quality_gates.json`
- `ragchecker-baseline.cursorrules`
- `ragchecker_baseline.mdc`

### `evaluation_drivers/`
Contains additional evaluation driver implementations that were previously deprecated.

### `fix_deprecated_types.py`
A utility script for migrating from deprecated `Optional`/`Union` syntax to modern Python 3.12+ union syntax (`|`). Deprecated on 2025-01-27 because the type migration has been completed and the script is no longer needed.

## Current Evaluation System

The new evaluation system uses:
- **Main Script**: `300_evals/scripts/evaluation/clean_dspy_evaluator.py`
- **Profiles**: `scripts/configs/profiles/` (gold.env, real.env, mock.env)
- **Results**: `300_evals/metrics/dspy_evaluations/`
- **Documentation**: `000_core/000_agent-entry-point.md`

## Migration Notes

- All evaluation results from the legacy system are preserved in `300_evals/metrics/baseline_evaluations/`
- The new system provides equivalent functionality with better performance
- Legacy scripts may still work but are not maintained or supported
- Use the new clean DSPy evaluator for all future evaluations

## Restoration

If any of these files are needed for reference or restoration, they can be found in this directory. However, it is recommended to use the new clean DSPy evaluator system instead.
