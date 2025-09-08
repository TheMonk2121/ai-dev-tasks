# Gold Dataset v1 (Single Source of Truth)

## Record Schema (JSON Lines)
Each line is one case. Fields are optional depending on `mode`.

- id (string, required, stable)
- mode (enum: retrieval | reader | decision, required)
- query (string, required)
- tags (array[string], required)  # e.g. ["ops_health","rag_qa_single"]
- category (string, optional)
- gt_answer (string, optional)          # reader mode
- expected_files (array[string], opt.)  # retrieval/decision
- globs (array[string], optional)       # retrieval/decision
- expected_decisions (array[string], optional) # decision mode
- notes (string, optional)

### Invariants
- Exactly one `mode`.
- At least one of {expected_files | globs | gt_answer | expected_decisions}.
- `id` is globally unique and stable across versions.

## Example lines for all three modes:

```json
{"id":"OPS_RUN_EVALS_001","mode":"reader","query":"How do I run the evals?","tags":["ops_health"],"category":"ops","gt_answer":"Use scripts/ragchecker_official_evaluation.py with --gold-profile ops_smoke ..."}
{"id":"DSPY_GUIDES_000_CORE_002","mode":"retrieval","query":"List the core workflow guides in 000_core.","tags":["rag_qa_single"],"category":"arch","expected_files":["000_core/001_create-prd.md","000_core/002_generate-tasks.md"],"globs":["000_core/*.md"]}
{"id":"DECISION_DB_CHOICE_003","mode":"decision","query":"database choice","tags":["meta_ops"],"expected_decisions":["postgres","pgvector","gin+ivfflat"],"notes":"Ported from evaluation_harness.create_gold_set()"}
```

## Usage

Load cases using the unified loader:
```python
from src.utils.gold_loader import load_gold_cases, stratified_sample

# Load all cases
cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")

# Use a profile from manifest.json
cases = stratified_sample(cases, strata=view["strata"], size=view["size"], seed=view["seed"])
```

## Profiles/Views

See `manifest.json` for predefined evaluation profiles that provide deterministic sampling and tag balance.
