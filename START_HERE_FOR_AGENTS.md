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
