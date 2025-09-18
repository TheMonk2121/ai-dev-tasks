# DEPRECATED EVALUATION DRIVERS

This directory contains deprecated evaluation drivers that have been moved from 300_evals/scripts/evaluation/.

## Deprecated Drivers:
- All RAGChecker variant evaluations (enhanced, precision, recovery, etc.)
- Legacy evaluation system integration files
- Health-gated evaluation systems
- Agent evaluation onboarding systems

## Current Active Driver:
- **clean_dspy_evaluator.py** - The PRIMARY active evaluation driver
- Uses gold profile configuration with real RAG system
- Located in: 300_evals/scripts/evaluation/clean_dspy_evaluator.py
- Status: ✅ **ACTIVE** - Primary evaluation system

## Migration:
All evaluation scripts now use the clean DSPy evaluator as the PRIMARY evaluation system.
The clean DSPy evaluator uses gold profile configuration with real RAG system integration.

**Current Status (September 6, 2025):**
- ✅ **Clean DSPy Evaluator**: PRIMARY active evaluation system
- ⚠️ **RAGChecker**: Deprecated but kept for legacy reference
- ❌ **RAGUS/RAGAS**: Completely removed

For more information, see:
- 000_core/000_evaluation-system-entry-point.md
- 300_evals/metrics/baseline_evaluations/EVALUATION_STATUS.md
- scripts/shell/deployment/run_evals.sh
- scripts/configs/profiles/gold.env
