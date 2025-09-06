# Baseline RAGChecker Evaluation System

## Overview

This directory contains baseline RAGChecker evaluation results using **fixed, version-controlled criteria** that don't change over time. This ensures reliable progress measurement of the memory system.

## Why Baseline Evaluations?

**Problem**: Our original RAGChecker evaluations evolved during development, making progress measurement unreliable:
- Score progression: 70.0 → 65.6 → 76.7 → 74.7 → 77.2 → 77.2 → 78.9 → 80.6 → **85.0** → 83.4
- Evaluation criteria changed over time (scoring system, bonus points, partial credit)
- Impossible to determine if score changes were due to system improvements or evaluation changes

**Solution**: Fixed baseline evaluations with consistent criteria that never change.

## Baseline Evaluation Framework

### Version Control
- **Baseline V1.0**: Fixed evaluation criteria established 2025-08-30
- **Configuration**: `config/baseline_evaluations/baseline_v1.0.json`
- **Evaluator**: `scripts/baseline_ragchecker_evaluation.py`

### 🎯 **NEW MILESTONE: Production-Ready RAG System**
- **Date Established**: 2025-08-31
- **Documentation**: `NEW_BASELINE_MILESTONE_2025.md`
- **Target**: Transform from Development Phase to Industry Standard Production Ready
- **Priority**: 🔥 **HIGHEST** - Industry Standard Production Metrics
- **🚨 RED LINE RULE**: Once achieved, NEVER go below - NO new features until restored

### Fixed Criteria (Never Changes)
- **Scoring**: Sources (40pts), Content (40pts), Workflow (20pts), Commands (20pts)
- **Pass Threshold**: 65/100
- **Bonus Points**: None (fixed)
- **Partial Credit**: None (fixed)
- **Strict Matching**: Yes (fixed)

### Evaluation Cases (Fixed)
1. **Memory Hierarchy** (3 tests)
   - Current Project Status Query
   - PRD Creation Workflow
   - DSPy Integration Patterns

2. **Workflow Chain** (2 tests)
   - Complete Development Workflow
   - Interrupted Session Continuation

3. **Role-Specific** (4 tests)
   - Planner Role - Development Priorities
   - Implementer Role - DSPy Implementation
   - Researcher Role - Memory System Analysis
   - Coder Role - Codebase Structure

## Usage

### Run Baseline Evaluation
```bash
# Run baseline evaluation v1.0
python3 scripts/baseline_ragchecker_evaluation.py

# Run with specific version
python3 scripts/baseline_ragchecker_evaluation.py --version 1.0

# Save to specific file
python3 scripts/baseline_ragchecker_evaluation.py --output my_baseline_results.json
```

### View Results
```bash
# List all baseline evaluations
ls -la metrics/baseline_evaluations/

# View latest baseline result
cat metrics/baseline_evaluations/baseline_ragchecker_v1.0_YYYYMMDD_HHMMSS.json | jq '.average_score'
```

## File Naming Convention

Results are saved as: `baseline_ragchecker_v{VERSION}_{TIMESTAMP}.json`

Example: `baseline_ragchecker_v1.0_20250830_150000.json`

## Progress Tracking

### Baseline Score History
| Date | Version | Score | Level | Pass Rate | Notes |
|------|---------|-------|-------|-----------|-------|
| 2025-08-30 | 1.0 | **73.3/100** | **📊 FAIR** | **88.9% (8/9)** | **Initial baseline established** |

### RAGChecker Levels (Baseline)
- **🥇 EXCELLENT**: 85-100 RAGChecker
- **🥈 VERY GOOD**: 80-84 RAGChecker
- **🥉 GOOD**: 75-79 RAGChecker
- **📊 FAIR**: 70-74 RAGChecker
- **⚠️ NEEDS WORK**: <70 RAGChecker

## Benefits

1. **Consistent Measurement**: Same criteria every time
2. **Reliable Progress**: Real improvement vs. evaluation changes
3. **Version Control**: Multiple baseline versions for different purposes
4. **Quality Assurance**: Automated validation of baseline stability

## Comparison with Original RAGChecker

| Aspect | Original RAGChecker | Baseline RAGChecker |
|--------|----------------|----------------|
| **Criteria** | Evolved over time | Fixed, never changes |
| **Scoring** | Variable (bonus, partial credit) | Consistent (strict matching) |
| **Progress** | Unreliable (mixed improvements + criteria changes) | Reliable (pure system improvements) |
| **Versioning** | Single evolving system | Multiple versioned baselines |
| **Measurement** | Relative to changing criteria | Absolute against fixed baseline |

## Next Steps

1. **Establish Baseline**: Run initial baseline evaluation to establish reference point
2. **Regular Monitoring**: Weekly/monthly baseline evaluations
3. **Progress Tracking**: Measure improvements against fixed baseline
4. **Version Evolution**: Create new baseline versions for major system changes

---

*This baseline evaluation system ensures reliable progress measurement of the memory system over time.*

## ABP Validation & CI Gates

To ensure stateless agents always have reliable context, the pipeline validates the Agent Briefing Pack (ABP) and Baseline Manifest.

Tools
- `scripts/update_baseline_manifest.py` — builds `config/baselines/<profile>.json` (targets, EMA, gates)
- `scripts/abp_packer.py` — generates `metrics/briefings/<ts>_<profile>_ABP.md`
- `scripts/abp_validation.py` — validates freshness/presence; supports CI warnings and strict mode
- `scripts/abp_adoption_report.py` — reports ABP carry‑over and usage across recent runs

Local usage
```bash
# Update manifest for a profile
python3 scripts/update_baseline_manifest.py --profile precision_elevated

# Validate (local)
python3 scripts/abp_validation.py --profile precision_elevated --max-age-days 2

# Strict (fail on stale/missing)
python3 scripts/abp_validation.py --profile precision_elevated --max-age-days 2 --strict

# Adoption report (last 20 runs)
python3 scripts/abp_adoption_report.py --window 20
```

CI integration
- Quick checks (soft warnings): `.github/workflows/quick-check.yml`
  - `uv run python scripts/abp_validation.py --profile precision_elevated --max-age-days 2 --ci-mode`
- Evaluation pipeline (soft warnings + release hard gate): `.github/workflows/ragchecker-evaluation.yml`
  - Soft validation (all branches): same as above
  - Hard gate for release/*: `uv run python scripts/abp_validation.py --profile precision_elevated --max-age-days 2 --strict`

Artifacts
- ABP: `metrics/briefings/<ts>_<profile>_ABP.md`
- Context meta sidecar: `metrics/baseline_evaluations/*_context_meta.json` (records ABP path, lessons applied/suggested, carry‑over)

This validation stack provides soft guidance during development and enforces freshness on release branches.
