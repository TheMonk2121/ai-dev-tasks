# 🎯 Agent Entry Point (Discovery ➜ Execution)

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Canonical start-to-finish path for stateless agents | You need the shortest path from zero context to results | Follow the Quick Path below |

## 🚀 Quick Path (All Agents)

### 0) Environment Setup (UV)
```bash
# Install UV (once)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Team onboarding / checks
python3 scripts/uv_team_onboarding.py

# Helpful aliases (optional)
source uv_aliases.sh   # uvd, uvt, uvs, etc.
```

### 1) Load Context (Memory Rehydration)
```bash
# Start memory systems
./scripts/memory_up.sh

# Verify memory systems are running
python3 scripts/healthcheck_db.py

# Pull core context for this session
python3 scripts/unified_memory_orchestrator.py
  --systems ltst cursor go_cli prime
  --role planner "current project status and core documentation"

# Verify context loaded successfully
echo "✅ Memory rehydration complete. Check output above for any errors."
```
- Memory quick start: `400_guides/400_01_memory-system-architecture.md`
- Daily usage: `400_guides/400_02_memory-rehydration-context-management.md`

### 2) Validate with Evaluations (Single Source of Truth)
```bash
# Load evaluation environment
source throttle_free_eval.sh

# Verify environment is configured
echo "🔒 Environment loaded. Check banner shows 'lock=True'"

# Run evaluation with consistent flags
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# Verify evaluation completed successfully
echo "✅ Evaluation complete. Check metrics/baseline_evaluations/ for results."
```
- Evaluation SOP: `000_core/000_evaluation-system-entry-point.md`
- Fast smoke: `./scripts/run_ragchecker_smoke_test.sh`

#### 🔁 "Run the evals" (ABP‑validated quick path)
```bash
# 1) Ensure baseline manifest is fresh for this profile
python3 scripts/update_baseline_manifest.py --profile precision_elevated

# 2) Run evaluation with lessons (advisory mode) - consistent flags
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# 3) Validate ABP & context sidecars
python3 scripts/abp_validation.py --profile precision_elevated

# 4) Verify all steps completed successfully
echo "✅ ABP-validated evaluation complete. Check metrics/briefings/ and metrics/baseline_evaluations/"
```
Expected:
- ABP in `metrics/briefings/` and context meta sidecar in `metrics/baseline_evaluations/`
- Decision docket path printed; lessons applied/suggested recorded

### 3) Execute by Role (Choose One)
```bash
# Planner – plan next steps
auth='plan next steps for <topic>'
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor --role planner "$auth"

# Implementer – design implementation
impl='design implementation for <feature>'
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli --role implementer "$impl"

# Researcher – analyze best practices
res='analyze best practices for <area>'
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor prime --role researcher "$res"

# Coder – implement with tests
code='implement <task> with tests'
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli --role coder "$code"
```
- AI frameworks: `400_guides/400_09_ai-frameworks-dspy.md`
- Integrations & models: `400_guides/400_10_integrations-models.md`

### 4) Iterate & Persis
- Results: `metrics/baseline_evaluations/`
- Baselines: `metrics/baseline_evaluations/BASELINE_LOCKED_20250901.md`, `metrics/baseline_evaluations/TUNED_BASELINE_20250902.md`
- Versioning: `scripts/baseline_version_manager.py`

### 5) Quick Status Check (Before Troubleshooting)
```bash
# Check system health
python3 scripts/healthcheck_db.py
python3 scripts/metrics_guard.py

# Verify recent evaluation results
ls -la metrics/baseline_evaluations/ | head -5

# Check memory system status
python3 scripts/unified_memory_orchestrator.py --systems ltst --role planner "system status check" --dry-run
```

### 6) Error Recovery & Validation
```bash
# If memory rehydration failed
./scripts/memory_up.sh
python3 scripts/healthcheck_db.py

# If evaluation failed
source throttle_free_eval.sh
./scripts/run_ragchecker_smoke_test.sh

# If role execution failed
python3 scripts/unified_memory_orchestrator.py --systems ltst --role planner "diagnose system issues"

# Verify all systems are working
python3 scripts/metrics_guard.py
```

### 7) Troubleshoot (Common)
- Agent patterns: `000_core/005_troubleshooting-patterns.md`
- DB/connection: `dspy-rag-system/test_db_connection.py`, `scripts/healthcheck_db.py`
- Metrics guard: `scripts/metrics_guard.py`
- Fast smoke test: `./scripts/run_ragchecker_smoke_test.sh`

#### **Evaluation-Specific Troubleshooting**
- **If Bedrock creds are missing**: Run the smoke test and report results
- **If validation warns about stale manifest**: Rerun step (1) in the evaluation workflow above
- **Primary evaluation SOP**: `000_core/000_evaluation-system-entry-point.md`
- **Adoption report**: `python3 scripts/abp_adoption_report.py --window 20`

## 🚨 Current Status: RED LINE BASELINE ENFORCEMENT

**Current Performance** (2025-09-06): Precision: 0.129, Recall: 0.157, F1: 0.137
**Targets**: Precision ≥0.20, Recall ≥0.45, F1 ≥0.22
**Status**: All metrics below targets - NO NEW FEATURES until baseline restored

### Quick Recall Boost (keep precision ≥0.149)
```bash
# 1. Increase breadth in config/retrieval.yaml:
candidates.final_limit: 50 → 80
rerank.final_top_n: 8 → 12
rerank.alpha: 0.7 → 0.6

# 2. Loosen filters:
prefilter.min_bm25_score: 0.10 → 0.05
prefilter.min_vector_score: 0.70 → 0.65

# 3. Test incrementally:
./scripts/run_ragchecker_smoke_test.sh
# Abort if precision < 0.149 and recall gain < +0.03
```

### Apply Lessons (when safe)
```bash
# Review docket first, then:
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode apply --lessons-scope profile
```

### ⏩ One-liner Commands
```bash
# Quick apply → smoke → eval
source throttle_free_eval.sh && recall_boost_apply && \
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# Revert quickly after testing
source throttle_free_eval.sh && recall_boost_revert
```

**Full details**: See `000_core/000_evaluation-system-entry-point.md` sections 75-137

## 🧭 Also See
- Memory overview: `400_guides/400_00_memory-system-overview.md`
- System overview: `400_guides/400_03_system-overview-and-architecture.md`
