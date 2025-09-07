# 🚀 START HERE FOR AGENTS

This is the one‑stop jump point for stateless agents. For the full path, open:

- 000_core/000_agent-entry-point.md

Quick Evaluation (ABP‑validated)

When asked to “run the evals”, execute exactly these commands:

```bash
# 1) Ensure baseline manifest is fresh for this profile
python3 scripts/update_baseline_manifest.py --profile precision_elevated

# 2) Run evaluation with lessons (advisory mode)
python3 scripts/ragchecker_official_evaluation.py --lessons-mode advisory

# 3) Validate ABP & context sidecars
python3 scripts/abp_validation.py --profile precision_elevated
```

Expected outcome
- ABP written to `metrics/briefings/`
- Context meta sidecar in `metrics/baseline_evaluations/`
- Decision docket path printed; lessons applied/suggested recorded

Helpful references
- Primary evaluation SOP: 000_core/000_evaluation-system-entry-point.md
- Fast smoke test: scripts/run_ragchecker_smoke_test.sh
- Adoption report: `python3 scripts/abp_adoption_report.py --window 20`

Troubleshooting
- If Bedrock creds are missing, run the smoke test and report results
- If validation warns about stale manifest, rerun step (1) above

### ⏩ One-liner (apply → smoke → eval)
```bash
source throttle_free_eval.sh && recall_boost_apply && \
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory
```

To revert quickly after testing:
```bash
source throttle_free_eval.sh && recall_boost_revert
```

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
python3 scripts/ragchecker_official_evaluation.py --bypass-cli --lessons-mode apply --lessons-scope profile
```

**Full details**: See `000_core/000_evaluation-system-entry-point.md` sections 75-137
