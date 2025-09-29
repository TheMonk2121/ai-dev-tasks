# 🎯 Evaluation System Entry Point
<!-- keywords: evals, run the evals, evaluations, ragchecker, benchmark -->

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| **Primary entry point** for running or validating evaluations | Before executing any evaluation or updating baselines | Follow the Quick Start checklist, then choose the workflow below |

## 🚀 Quick Start Checklist

1. **Rehydrate memory context** so you inherit the latest evaluation decisions.
   ```bash
   export POSTGRES_DSN="mock://test"
   UV_PROJECT_ENVIRONMENT=.venv uv run python scripts/utilities/unified_memory_orchestrator.py \
     --systems ltst cursor go_cli prime --role planner "current project status and core documentation"
   ```
2. **Prime your shell** for repo-relative imports.
   ```bash
   export PYTHONPATH=$PWD
   export UV_PROJECT_ENVIRONMENT=.venv
   ```
3. **Run smoke checks** to confirm the stack is healthy.
   ```bash
   PYTHONPATH=$PWD uv run python evals/scripts/evaluation/test_governance_simple.py
   PYTHONPATH=$PWD uv run python -m pytest tests/evaluation/test_canonical_evaluator.py
   ```
   Both commands must pass before you run the full evaluations.
4. **Pick an evaluation profile** (`make eval-gold`, `make eval-real`, or `make eval-mock`) and monitor the output. Detailed workflows are below.

## 🧪 Smoke Tests (required before full runs)

| command | why it matters |
|---|---|
| `PYTHONPATH=$PWD uv run python evals/scripts/evaluation/test_governance_simple.py` | Exercises the governance pipeline and confirms the optimized configuration loads successfully. |
| `PYTHONPATH=$PWD uv run python -m pytest tests/evaluation/test_canonical_evaluator.py` | Validates the canonical evaluator interface and catches missing imports or environment drift. |

If either command fails, stop and fix the issue before attempting a full evaluation.

## 🏃 Standard Evaluation Workflows

### Preferred: Makefile targets
Use these targets for consistent environment setup and logging.

```bash
# Gold profile (baseline comparisons)
make eval-gold

# Real profile (production parity)
make eval-real

# Mock profile (infra-only smoke)
make eval-mock
```

Each target prints the active command. Logs land in `metrics/baseline_evaluations/` just like the direct invocation.

### Direct invocation (when you need custom flags)

```bash
PYTHONPATH=$PWD UV_PROJECT_ENVIRONMENT=.venv \
uv run python scripts/ragchecker_official_evaluation.py --profile gold \
  --lessons-mode advisory --limit 10
```

Key flags:
- `--profile {gold|real|mock}` – chooses dataset + infrastructure profile.
- `--limit N` – optional subset for quick iteration.
- `--lessons-mode {off|advisory|apply}` – integrate lessons engine output. Stay on `advisory` unless the decision docket tells you to apply.

## 📂 Where results live

- **Metrics JSON**: `metrics/baseline_evaluations/*.json`
- **Decision dockets & derived configs**: `metrics/derived_configs/`
- **Lessons**: `metrics/lessons/lessons.jsonl`
- **Logs**: `mcp_server.log` (for MCP) and stdout from the commands above

Use `jq` or `python -m json.tool` to inspect the latest metrics file:

```bash
LATEST=$(ls -t metrics/baseline_evaluations/*.json | head -1)
jq '.overall_metrics' "$LATEST"
```

## ✅ Post-run checklist

- [ ] Did the command finish without stack traces?
- [ ] Are `precision`, `recall`, and `f1_score` within expected guard rails?
- [ ] Were new lessons written (`metrics/lessons/lessons.jsonl`)?
- [ ] If lessons were produced, review the decision docket before applying changes.
- [ ] Record the metrics path in the backlog or execution log if the run was official.

## 📊 Guard rails & remediation

| metric | production guard rail | remediation hint |
|---|---|---|
| Precision | ≥ 0.20 | Reintroduce precision-focused lessons, tighten reranker top‑k |
| Recall | ≥ 0.45 | Apply recall improvements, but keep precision ≥ 0.149 while iterating |
| F1 | ≥ 0.22 | Balance both knobs; rerun smoke test after each change |

If a run drops below a guard rail:
1. Re-run with `--lessons-mode advisory` and inspect the docket.
2. Apply adjustments manually or rerun with `--lessons-mode apply` only after verifying the docket gates.
3. Re-run the smoke tests, then the full evaluation profile.

## 🧭 Useful companion commands

```bash
# Check MCP memory server
make mcp-status

# Tail latest evaluation metrics summary
PYTHONPATH=$PWD uv run python scripts/evaluation/metrics_guard.py

# Generate lessons from a run (writes to episodic memory automatically)
PYTHONPATH=$PWD uv run python scripts/utilities/lessons_extractor.py \
  metrics/baseline_evaluations/<run>.json
```

## 🛠 Troubleshooting quick reference

| symptom | fix |
|---|---|
| `ModuleNotFoundError: src...` | Ensure `export PYTHONPATH=$PWD` and rerun command with `uv run`. |
| Governance smoke fails to import pipeline module | Run `git status` to confirm repo sync; the loader now reads from `evals/stable_build/modules/`. |
| Evaluator complains about Bedrock credentials | Use `aws configure` or run the mock profile until credentials are restored. |
| Lessons file missing | Re-run `lessons_extractor.py`; the script now writes to episodic memory automatically. |

## 🔗 Reference material

- `400_guides/400_11_performance-optimization.md` – performance tuning patterns.
- `400_guides/400_12_advanced-configurations.md` – advanced configuration scenarios.
- `scripts/utilities/memory/mcp_memory_server.py --help` – MCP memory endpoints.
- `Makefile` – authoritative list of supported eval targets.

---
**All agents should start here before touching the evaluation stack. Keep this document up to date whenever workflows change.**
