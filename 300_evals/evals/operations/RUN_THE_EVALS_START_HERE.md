# 🧪 Run the Evals — Start Here

If you were told "run the evals", do this:

```bash
# Quick health check (for stateless agents)
python3 scripts/healthcheck_db.py
source throttle_free_eval.sh
echo "🔒 Environment loaded. Check banner shows 'lock=True'"

# Run evaluation with consistent flags
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# Verify results (for stateless agents)
echo "✅ Evaluation complete. Checking results..."
ls -la metrics/baseline_evaluations/ | tail -5
```

- SOP and details: `000_core/000_evaluation-system-entry-point.md`
- No Bedrock? Run: `./scripts/run_ragchecker_smoke_test.sh`

This file exists to be discoverable by simple code search for the phrase "run the evals".

