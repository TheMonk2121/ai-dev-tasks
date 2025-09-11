
# Core Evaluation Suite

> SSOT: `300_core` • Generated 2025-09-11T00:02:22.874226+00:00 • Commit: 6a21056ced7f3a6ef389ae5de3cf2d3a1dc91644 (main)
>
> Suite created: 2025-09-08T19:57:59-05:00 • updated: 2025-09-08T19:57:59-05:00


---
## 1. Retrieval-Only Baseline
**ID:** `retrieval_only_baseline` • **Version:** 3.0.0 • **Tags:** retrieval, baseline

**Purpose**  
Confirms retrieval/rerank/chunk config (450/10%/J=0.8/prefix-A).

**Run Spec**  
- Kind: `ragchecker`  
- Script: `scripts/_ragchecker_eval_impl.py`  
- CLI Args: `(none)`  

**Config Layers**: base + stable

**Config (effective)**:
```json
{
  "FEW_SHOT_K": 0,
  "FEW_SHOT_SELECTOR": "none",
  "FEW_SHOT_SEED": 42,
  "EVAL_COT": 0,
  "EVAL_DISABLE_CACHE": 1,
  "DSPY_TELEPROMPT_CACHE": "false",
  "TEMPERATURE": 0.0,
  "MAX_WORKERS": 3,
  "RATE_LIMIT_PROFILE": "stable"
}
```

**Timestamps**
- **Created**: 2025-09-08T23:07:29.017097
- **Updated**: 2025-09-09T00:55:48.551858+00:00
- **Last run**: 2025-09-09T02:51:26


**Gates**

| Metric | Target | Direction |
|--------|--------|-----------|
| f1 | 0.500 | >= |
| faithfulness | 0.800 | >= |



**Reproduce**
```bash
python -m evals_300.tools.run --suite 300_core --pass retrieval_only_baseline
```

**Latest Results**
```json
{'precision': 0.0, 'recall': 0.0, 'f1': 0.0, 'faithfulness': 0.0032499751352009095, 'artifact_path': 'metrics/history/retrieval_only_baseline_1757404273/ragchecker_clean_evaluation_20250909_025126.json', 'timestamp': '2025-09-09T02:51:26'}
```


---
## 2. Deterministic Few-Shot (k=5, knn, seed=42)
**ID:** `deterministic_few_shot` • **Version:** 3.0.0 • **Tags:** reader, fewshot

**Purpose**  
Records prompt_audit.few_shot_ids, prompt_hash, CoT disabled.

**Run Spec**  
- Kind: `ragchecker`  
- Script: `scripts/_ragchecker_eval_impl.py`  
- CLI Args: `(none)`  

**Config Layers**: base + stable + delta_fewshot

**Config (effective)**:
```json
{
  "FEW_SHOT_K": 5,
  "FEW_SHOT_SELECTOR": "knn",
  "FEW_SHOT_SEED": 42,
  "EVAL_COT": 0,
  "EVAL_DISABLE_CACHE": 1,
  "DSPY_TELEPROMPT_CACHE": "false",
  "TEMPERATURE": 0.0,
  "MAX_WORKERS": 3,
  "RATE_LIMIT_PROFILE": "stable"
}
```

**Timestamps**
- **Created**: 2025-09-08T23:07:29.017142
- **Updated**: 2025-09-09T00:55:48.552045+00:00
- **Last run**: never


**Gates**

| Metric | Target | Direction |
|--------|--------|-----------|
| f1 | 0.600 | >= |



**Reproduce**
```bash
python -m evals_300.tools.run --suite 300_core --pass deterministic_few_shot
```

**Latest Results**
```json
{}
```


---
## 3. Calibrate Answerable Thresholds
**ID:** `calibrate_thresholds` • **Version:** 2.0.0 • **Tags:** calibration

**Purpose**  
Runs calibration; writes metrics/calibration/thresholds.json.

**Run Spec**  
- Kind: `calibrate`  
- Script: `scripts/calibrate_answerable_threshold.py`  
- CLI Args: `(none)`  

**Config Layers**: base + stable

**Config (effective)**:
```json
{
  "FEW_SHOT_K": 0,
  "FEW_SHOT_SELECTOR": "none",
  "FEW_SHOT_SEED": 42,
  "EVAL_COT": 0,
  "EVAL_DISABLE_CACHE": 1,
  "DSPY_TELEPROMPT_CACHE": "false",
  "TEMPERATURE": 0.0,
  "MAX_WORKERS": 3,
  "RATE_LIMIT_PROFILE": "stable"
}
```

**Timestamps**
- **Created**: 2025-09-08T23:07:29.017163
- **Updated**: 2025-09-08T23:07:29.017161
- **Last run**: never



**Reproduce**
```bash
python -m evals_300.tools.run --suite 300_core --pass calibrate_thresholds
```

**Latest Results**
```json
{}
```


---
## 4. Reader Debug A/B
**ID:** `reader_debug_ab` • **Version:** 2.0.0 • **Tags:** debug, reader

**Purpose**  
Debug parity between teleprompt configs. See reader_debug outputs.

**Run Spec**  
- Kind: `reader_debug`  
- Script: `scripts/reader_debug_ab.py`  
- CLI Args: `(none)`  

**Config Layers**: base + stable

**Config (effective)**:
```json
{
  "FEW_SHOT_K": 0,
  "FEW_SHOT_SELECTOR": "none",
  "FEW_SHOT_SEED": 42,
  "EVAL_COT": 0,
  "EVAL_DISABLE_CACHE": 1,
  "DSPY_TELEPROMPT_CACHE": "false",
  "TEMPERATURE": 0.0,
  "MAX_WORKERS": 3,
  "RATE_LIMIT_PROFILE": "stable"
}
```

**Timestamps**
- **Created**: 2025-09-08T23:07:29.017178
- **Updated**: 2025-09-08T23:07:29.017177
- **Last run**: never



**Reproduce**
```bash
python -m evals_300.tools.run --suite 300_core --pass reader_debug_ab
```

**Latest Results**
```json
{}
```


---
## 5. Reranker Ablation (OFF)
**ID:** `reranker_ablation_off` • **Version:** 3.0.0 • **Tags:** retrieval, reranker, ablation

**Purpose**  
Retrieval with reranker disabled to establish baseline for uplift.

**Run Spec**  
- Kind: `ragchecker`  
- Script: `scripts/_ragchecker_eval_impl.py`  
- CLI Args: `(none)`  

**Config Layers**: base + stable + reranker_off

**Config (effective)**:
```json
{
  "FEW_SHOT_K": 0,
  "FEW_SHOT_SELECTOR": "none",
  "FEW_SHOT_SEED": 42,
  "EVAL_COT": 0,
  "EVAL_DISABLE_CACHE": 1,
  "DSPY_TELEPROMPT_CACHE": "false",
  "TEMPERATURE": 0.0,
  "MAX_WORKERS": 3,
  "RATE_LIMIT_PROFILE": "stable"
}
```

**Timestamps**
- **Created**: 2025-09-08T23:41:23.566608+00:00
- **Updated**: 2025-09-09T00:55:48.552085+00:00
- **Last run**: 2025-09-10T19:02:20


**Gates**

| Metric | Target | Direction |
|--------|--------|-----------|
| f1 | 0.500 | >= |
| faithfulness | 0.800 | >= |



**Reproduce**
```bash
python -m evals_300.tools.run --suite 300_core --pass reranker_ablation_off
```

**Latest Results**
```json
{'precision': 0.09648873348208598, 'recall': 0.0627661633300274, 'f1': 0.06312759563341493, 'faithfulness': 0.22948172101814165, 'artifact_path': 'metrics/history/reranker_ablation_off_1757548938/ragchecker_clean_evaluation_20250910_190219.json', 'timestamp': '2025-09-10T19:02:20'}
```


---
## 6. Reranker Ablation (ON)
**ID:** `reranker_ablation_on` • **Version:** 3.0.0 • **Tags:** retrieval, reranker, ablation

**Purpose**  
Retrieval with cross-encoder reranker enabled to measure uplift.

**Run Spec**  
- Kind: `ragchecker`  
- Script: `scripts/_ragchecker_eval_impl.py`  
- CLI Args: `(none)`  

**Config Layers**: base + stable + reranker_on

**Config (effective)**:
```json
{
  "FEW_SHOT_K": 0,
  "FEW_SHOT_SELECTOR": "none",
  "FEW_SHOT_SEED": 42,
  "EVAL_COT": 0,
  "EVAL_DISABLE_CACHE": 1,
  "DSPY_TELEPROMPT_CACHE": "false",
  "TEMPERATURE": 0.0,
  "MAX_WORKERS": 3,
  "RATE_LIMIT_PROFILE": "stable"
}
```

**Timestamps**
- **Created**: 2025-09-08T23:41:23.566632+00:00
- **Updated**: 2025-09-09T00:55:48.552102+00:00
- **Last run**: 2025-09-10T19:02:22


**Gates**

| Metric | Target | Direction |
|--------|--------|-----------|
| f1 | 0.500 | >= |
| faithfulness | 0.800 | >= |



**Reproduce**
```bash
python -m evals_300.tools.run --suite 300_core --pass reranker_ablation_on
```

**Latest Results**
```json
{'precision': 0.09648873348208598, 'recall': 0.0627661633300274, 'f1': 0.06312759563341493, 'faithfulness': 0.22948172101814165, 'artifact_path': 'metrics/history/reranker_ablation_on_1757548940/ragchecker_clean_evaluation_20250910_190222.json', 'timestamp': '2025-09-10T19:02:22'}
```

