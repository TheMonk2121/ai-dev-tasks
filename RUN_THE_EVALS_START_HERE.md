# 🧪 Run the Evals — Start Here

If you were told "run the evals", do this:

```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```

- SOP and details: `000_core/000_evaluation-system-entry-point.md`
- No Bedrock? Run: `./scripts/run_ragchecker_smoke_test.sh`

This file exists to be discoverable by simple code search for the phrase "run the evals".

