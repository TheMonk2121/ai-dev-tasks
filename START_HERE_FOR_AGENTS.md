# 🚦 Start Here for Agents (Zero‑Context)

Primary SOP: `000_core/000_agent-entry-point.md`

Follow these exact steps to get the right context fast.

## 1) Load Working Context (Memory)

```bash
# Start memory systems
./scripts/memory_up.sh

# Verify & pull core context into the session
python3 scripts/unified_memory_orchestrator.py \
  --systems ltst cursor go_cli prime \
  --role planner "current project status and core documentation"
```

- Read next (5 min): `400_guides/400_01_memory-system-architecture.md`
- Daily use: `400_guides/400_02_memory-rehydration-context-management.md`

## 2) Run Evaluations (Single Source of Truth)

```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```

- Evaluation SOP: `000_core/000_evaluation-system-entry-point.md`

## 3) Team/Env Onboarding (UV)

```bash
python3 scripts/uv_team_onboarding.py
# or
python3 scripts/uv_team_onboarding.py --check-only
```

- Dependency + workflow tools: `scripts/uv_dependency_manager.py`, `scripts/uv_workflow_optimizer.py`

## 4) Quick Links (Choose Your Path)

- Memory overview: `400_guides/400_00_memory-system-overview.md`
- AI frameworks + DSPy quick start: `400_guides/400_09_ai-frameworks-dspy.md`
- Integrations & models: `400_guides/400_10_integrations-models.md`
- Performance & optimization: `400_guides/400_11_performance-optimization.md`

If in doubt, re-run step 1 to rehydrate context, then step 2 for verification.
