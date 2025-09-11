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

# Pull core context for this session
python3 scripts/unified_memory_orchestrator.py
  --systems ltst cursor go_cli prime
  --role planner "current project status and core documentation"
```
- Memory quick start: `400_guides/400_01_memory-system-architecture.md`
- Daily usage: `400_guides/400_02_memory-rehydration-context-management.md`

### 2) Validate with Evaluations (Single Source of Truth)
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```
- Evaluation SOP: `000_core/000_evaluation-system-entry-point.md`
- Fast smoke: `./scripts/run_ragchecker_smoke_test.sh`

#### 🔁 “Run the evals” (ABP‑validated quick path)
```bash
# 1) Ensure baseline manifest is fresh for this profile
python3 scripts/update_baseline_manifest.py --profile precision_elevated

# 2) Run evaluation with lessons (advisory mode)
python3 scripts/ragchecker_official_evaluation.py --lessons-mode advisory

# 3) Validate ABP & context sidecars
python3 scripts/abp_validation.py --profile precision_elevated
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

### 5) Troubleshoot (Common)
- Agent patterns: `100_memory/100_agent-troubleshooting-patterns.md`
- DB/connection: `dspy-rag-system/test_db_connection.py`, `scripts/healthcheck_db.py`
- Metrics guard: `scripts/metrics_guard.py`

## 🧭 Also See
- Root quick launcher: `START_HERE_FOR_AGENTS.md`
- Memory overview: `400_guides/400_00_memory-system-overview.md`
- System overview: `400_guides/400_03_system-overview-and-architecture.md`
