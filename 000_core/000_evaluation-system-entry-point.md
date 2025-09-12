# 🎯 Evaluation System Entry Poin
<!-- keywords: evals, run the evals, evaluations, ragchecker, benchmark -->

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| **PRIMARY ENTRY POINT** for all evaluation system usage - agents start here | Any agent needs to run evaluations, check performance, or understand the system | Follow the "Quick Start" section below |

## 🚀 **Quick Start (For All Agents)**

### **🚨 NEW: Pydantic Evals Framework (Recommended)**
```bash
# Run Pydantic Evals integration demo
python3 scripts/pydantic_evals_integration.py

# Run retrieval evaluation with Pydantic Evals
python3 300_evals/retrieval_eval.py

# Run legacy compatibility tes
python3 -c "from scripts.migrate_to_pydantic_evals import load_eval_cases; print(f'Loaded {len(load_eval_cases(\"gold\"))} cases')"
```

**This is the NEW Pydantic Evals framework with type-safe evaluation, Logfire observability, and full legacy compatibility.**

### **📋 Legacy Evaluation System (Deprecated)**
```bash
# Generate evaluation documentation and artifacts
python -m evals_300.tools.gen

# Run specific evaluation passes
python -m evals_300.tools.run --suite 300_core --pass retrieval_only_baseline
python -m evals_300.tools.run --suite 300_core --pass deterministic_few_sho

# View generated documentation
cat evals_300/_generated/300_core.md
```

**This is the legacy evaluation system. Use Pydantic Evals framework for new development.**

### **📋 Standard Evaluation Command (With Lessons Engine)**
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5
```

**This is the legacy command for evaluations with automatic lesson learning.**

### **📋 Legacy Evaluation Command (Without Lessons)**
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5
```

**Use this only if lessons engine is disabled or for baseline comparisons.**

### **💨 Fast Testing Command**
```bash
./scripts/run_ragchecker_smoke_test.sh
```

**Use this for quick iteration and testing changes.**

### **🔍 Quick Status Check (For Stateless Agents)**
```bash
# Check system health before running evaluations
python3 scripts/healthcheck_db.py

# Verify evaluation environment
source throttle_free_eval.sh
echo "🔒 Environment loaded. Check banner shows 'lock=True'"

# Check recent evaluation results
ls -la metrics/baseline_evaluations/ | head -5

# Verify baseline manifest exists
ls -la metrics/baseline_evaluations/BASELINE_*.md
```

**Use this to verify system status before running evaluations.**

### **🔧 Environment Setup Command**
```bash
# Set up all required environment variables for evaluation system
source scripts/setup_evaluation_env.sh

# Verify environment is configured
uv run python scripts/health_gated_evaluation.py --check-only
```

**Use this to configure the evaluation system environment and verify all components are working.**

### ✅ Standard Evaluation Sequence
1) `python3 scripts/update_baseline_manifest.py --profile precision_elevated`
2) `python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5`
3) `python3 scripts/abp_validation.py --profile precision_elevated`

Use this 3‑step flow for any official evaluation run. Step 2 supports Bedrock/stable flags via your sourced env (see Quick Start).

### **✅ Post-Evaluation Validation (For Stateless Agents)**
```bash
# Verify evaluation completed successfully
echo "✅ Evaluation complete. Checking results..."

# Check results were generated
ls -la metrics/baseline_evaluations/ | tail -5

# Verify ABP files were created
ls -la metrics/briefings/ | tail -3

# Check for any error indicators
grep -i "error\|failed\|exception" metrics/baseline_evaluations/*.json | head -5

# Display latest metrics summary
python3 scripts/metrics_guard.py
```

**Use this to verify evaluation completed successfully and results are valid.**

### 🧭 If you were told to "run the evals"
- **MANDATORY**: Run memory rehydration first: `export POSTGRES_DSN="mock://test" && python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"`
- **ABP‑validated quick sequence**:
  ```bash
  # 1) Update baseline manifest (fresh targets/EMA)
  python3 scripts/update_baseline_manifest.py --profile precision_elevated

  # 2) Run evaluation with lessons (advisory)
  python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

  # 3) Validate ABP generation and context sidecars
  python3 scripts/abp_validation.py --profile precision_elevated
  ```
- **Review the decision docket** printed in the output
- **Document results** in `000_core/000_backlog.md`
- If Bedrock credentials are missing, run `./scripts/run_ragchecker_smoke_test.sh` and report results

### 🧠 **Lessons Engine Integration**

#### **Advisory-First Approach**
```bash
# 1. Run with lessons in advisory mode (recommended)
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# 2. Review decision docke
cat metrics/derived_configs/*_decision_docket.md

# 3. Apply lessons if approved
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode apply --lessons-scope profile
```

**Note**: Runner prints one-line summary when apply is blocked and exact "Decision docket:" path.

#### **When To Use `--lessons-mode apply`**
- Use apply only after reviewing the docket and confirming:
  - No hard gates will be violated (see Baseline Targets below)
  - Precision stays above your current guard rail during recall pushes (e.g., ≥ 0.149 interim)
  - The change is configuration-only and reversible
- Command: `python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode apply --lessons-scope profile`
- If the script prints "apply_blocked: true", keep using advisory and apply changes manually in `config/retrieval.yaml`.

#### **Interpret Output**
- **Decision docket path**: Printed in output, contains lesson details and parameter changes
- **Apply blocked**: If quality gates prevent apply, review docket for warnings
- **Generated files**: Check `metrics/derived_configs/` for candidate configs and dockets
- **New lessons**: Check `metrics/lessons/lessons.jsonl` for lessons learned

#### **Minimal Resume Checklist**
```bash
# Get latest eval → parse .run_config.lessons → if docket present, open; if apply_blocked, keep base env
LATEST_RESULTS=$(ls -t metrics/baseline_evaluations/*.json | head -1)
jq '.run_config.lessons' "$LATEST_RESULTS"

# If docket present, open and follow next steps
# If apply_blocked == true, review gates and fix before applying
# Attach docket link to backlog commen
# Run quality checks and evolution tracking
python3 scripts/lessons_quality_check.py
python3 scripts/evolution_tracker.py
```

**Example jq snippet**:
```bash
jq '.run_config.lessons' $(ls -t metrics/baseline_evaluations/*.json | head -1)
```

### 🎯 Baseline Targets (Production)
- Precision: ≥ 0.20
- Recall: ≥ 0.45
- F1 Score: ≥ 0.22

Reference: `metrics/baseline_evaluations/TUNED_BASELINE_20250902.md` and `metrics/baseline_evaluations/RED_LINE_ENFORCEMENT_RULES.md`.

### 🛠 When Metrics Are Below Targe
- Run with lessons advisory: `python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5`
- Review decision docket in `metrics/derived_configs/` and apply if gates allow: `--lessons-mode apply`
- Re‑run smoke test for quick iteration: `./scripts/run_ragchecker_smoke_test.sh`
- Validate baselines and context: `python3 scripts/abp_validation.py --profile precision_elevated`
- If still below, check retrieval settings and quality gates per `400_guides/400_canonical-evaluation-sop.md`

#### 📈 Recall Improvement Playbook (keep precision ≥ 0.149)
- Increase breadth, then prune:
  - In `config/retrieval.yaml` → `candidates.final_limit`: raise from 50 → 80
  - `rerank.final_top_n`: raise from 8 → 12
  - `rerank.alpha`: lower from 0.7 → 0.6 (let fused recall influence more)
- Loosen early filters slightly:
  - `prefilter.min_bm25_score`: 0.10 → 0.05
  - `prefilter.min_vector_score`: 0.70 → 0.65
- Favor semantic coverage when query is conceptual:
  - Switch fusion profile to `semantic_heavy` or increase `fusion.lambda_sem` (+0.1) for those runs
- Add diversity for multi-facet queries:
  - `packing.mmr_lambda`: 0.7 → 0.6 (slightly more diversity)
- Iterate fast:
  - Run: `./scripts/run_ragchecker_smoke_test.sh` then full eval
  - Abort/revert if precision < 0.149 while recall gain < +0.03

Tip: capture each change as a lesson note in the docket or commit message for provenance.

## 📍 **Where to Find Everything**

### **🔧 Configuration Files**
- **`configs/stable_bedrock.env`** - Locked evaluation settings (DO NOT MODIFY)
- **`throttle_free_eval.sh`** - Loads stable configuration
- **`scripts/ragchecker_official_evaluation.py`** - Main evaluation script
- **`scripts/setup_evaluation_env.sh`** - Environment variables setup for evaluation system
- **`src/`** - DSPy RAG system components for evaluation

### **📊 Results & Documentation**
- **`metrics/baseline_evaluations/`** - All evaluation results
- **`400_guides/400_canonical-evaluation-sop.md`** - Complete SOP documentation
- **`scripts/baseline_version_manager.py`** - Version management tools

### **🚀 Execution Scripts**
- **`throttle_free_eval.sh`** - Load stable config
- **`scripts/run_ragchecker_smoke_test.sh`** - Fast smoke testing
- **`scripts/ragchecker_official_evaluation.py`** - Full evaluation
- **`scripts/setup_evaluation_env.sh`** - Environment setup
- **`src/rag_system.py`** - DSPy RAG system interface

### **🤖 DSPy RAG System Components**
- **`src/rag_system.py`** - Main RAG system interface
- **`src/dspy_modules/`** - DSPy-specific modules and programs
- **`src/rag/`** - RAG pipeline components
- **`src/schemas/`** - Pydantic data models
- **`src/common/`** - Common utilities and database connections

## 🎯 **Agent Workflow**

### **🔄 Daily Regression Testing**
1. **Run standard command** (see Quick Start above)
2. **Verify banner shows**: `🔒 Loaded env from configs/stable_bedrock.env … lock=True`
3. **Check results** in `metrics/baseline_evaluations/`

### **💨 Fast Iteration**
1. **Make changes** to system
2. **Run smoke test**: `./scripts/run_ragchecker_smoke_test.sh`
3. **Iterate quickly** until satisfied
4. **Run full evaluation** when ready

### **🔒 Version New Baseline**
1. **When intentionally changing** weights/config
2. **Run**: `python3 scripts/baseline_version_manager.py --full-setup`
3. **Follow prompts** to create new versioned baseline

## 🚨 **Critical Rules**

### **✅ Always Do**
- **Use `--stable` flag** for all evaluations
- **Source `throttle_free_eval.sh`** before running
- **Verify lock status** in banner output
- **Check for throttling** - if any, reduce rate limits

### **❌ Never Do**
- **Modify `configs/stable_bedrock.env`** without versioning
- **Run evaluations** without stable configuration
- **Ignore throttling** - fix configuration instead
- **Skip smoke tests** for major changes

## 📋 **Verification Checklist**

**Before running any evaluation, verify:**
- [ ] `configs/stable_bedrock.env` exists
- [ ] Using `--stable` flag
- [ ] Banner shows lock status
- [ ] No throttling in previous runs
- [ ] AWS credentials configured

**After running evaluation, check:**
- [ ] Results saved to `metrics/baseline_evaluations/`
- [ ] No throttling errors
- [ ] Performance metrics within baseline
- [ ] Configuration provenance recorded

## 🔍 **Troubleshooting**

### **❌ "Stable config not found"**
```bash
cp configs/stable_bedrock.env.template configs/stable_bedrock.env
```

### **❌ Throttling errors**
```bash
# Edit configs/stable_bedrock.env
export BEDROCK_MAX_RPS=0.06  # Reduce from 0.15
export BEDROCK_COOLDOWN_SEC=45  # Increase from 30
```

### **❌ AWS credentials issues**
```bash
aws configure  # Set up credentials
python3 scripts/bedrock_connection_test.py  # Test connection
```

## 📚 **Further Reading**

- **`400_guides/400_canonical-evaluation-sop.md`** - Complete SOP
- **`scripts/baseline_version_manager.py --help`** - Version managemen
- **`scripts/ragchecker_official_evaluation.py --help`** - All options

## 🎯 **Agent Memory Integration**

**For Cursor AI agents, remember:**
- **Entry point**: This file (`000_core/000_evaluation-system-entry-point.md`)
- **Standard command**: Always use `--stable` flag
- **Configuration**: Never modify stable config without versioning
- **Results**: Always check `metrics/baseline_evaluations/`

### 📊 Current RAGChecker Baseline (2025-09-06)
- Precision: 0.129 (Target ≥ 0.20) — Needs +0.071
- Recall: 0.157 (Target ≥ 0.45) — Needs +0.293
- F1 Score: 0.137 (Target ≥ 0.22) — Needs +0.083

Source: latest `metrics/baseline_evaluations/ragchecker_official_evaluation_*.json` overall_metrics.

### 🔄 Baseline Restoration Plan
- Lock env: `source throttle_free_eval.sh` and verify banner `lock=True`
- Run Standard Evaluation Sequence (above) with lessons in advisory
- Apply the Recall Improvement Playbook (small, reversible steps)
- Gate checks:
  - Don’t accept any change that drops precision below 0.149 (interim guard)
  - Prefer changes that add ≥ +0.03 recall per step
- Validate: `python3 scripts/abp_validation.py --profile precision_elevated`
- When all production targets are met (P≥0.20, R≥0.45, F1≥0.22):
  - Version baseline: `python3 scripts/baseline_version_manager.py --full-setup`
  - Update manifest: `python3 scripts/update_baseline_manifest.py --profile precision_elevated`
  - Record snapshot in backlog with the result JSON path

---

**This is the SINGLE SOURCE OF TRUTH for evaluation system usage.**
**All agents should start here and follow these exact procedures.**
