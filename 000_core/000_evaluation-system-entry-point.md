# 🎯 Evaluation System Entry Point
<!-- keywords: evals, run the evals, evaluations, ragchecker, benchmark -->

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| **PRIMARY ENTRY POINT** for all evaluation system usage - agents start here | Any agent needs to run evaluations, check performance, or understand the system | Follow the "Quick Start" section below |

## 🚀 **Quick Start (For All Agents)**

### **📋 Standard Evaluation Command (With Lessons Engine)**
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5
```

**This is the ONE command every agent should use for evaluations with automatic lesson learning.**

### **📋 Legacy Evaluation Command (Without Lessons)**
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```

**Use this only if lessons engine is disabled or for baseline comparisons.**

### **💨 Fast Testing Command**
```bash
./scripts/run_ragchecker_smoke_test.sh
```

**Use this for quick iteration and testing changes.**

### 🧭 If you were told to "run the evals"
- **MANDATORY**: Run memory rehydration first: `export POSTGRES_DSN="mock://test" && python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"`
- **ABP‑validated quick sequence**:
  ```bash
  # 1) Update baseline manifest (fresh targets/EMA)
  python3 scripts/update_baseline_manifest.py --profile precision_elevated

  # 2) Run evaluation with lessons (advisory)
  python3 scripts/ragchecker_official_evaluation.py --lessons-mode advisory

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
python3 scripts/ragchecker_official_evaluation.py --lessons-mode advisory --lessons-scope profile --lessons-window 5

# 2. Review decision docket
cat metrics/derived_configs/*_decision_docket.md

# 3. Apply lessons if approved
python3 scripts/ragchecker_official_evaluation.py --lessons-mode apply --lessons-scope profile
```

**Note**: Runner prints one-line summary when apply is blocked and exact "Decision docket:" path.

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
# Attach docket link to backlog comment
# Run quality checks and evolution tracking
python3 scripts/lessons_quality_check.py
python3 scripts/evolution_tracker.py
```

**Example jq snippet**:
```bash
jq '.run_config.lessons' $(ls -t metrics/baseline_evaluations/*.json | head -1)
```

## 📍 **Where to Find Everything**

### **🔧 Configuration Files**
- **`configs/stable_bedrock.env`** - Locked evaluation settings (DO NOT MODIFY)
- **`throttle_free_eval.sh`** - Loads stable configuration
- **`scripts/ragchecker_official_evaluation.py`** - Main evaluation script

### **📊 Results & Documentation**
- **`metrics/baseline_evaluations/`** - All evaluation results
- **`400_guides/400_canonical-evaluation-sop.md`** - Complete SOP documentation
- **`scripts/baseline_version_manager.py`** - Version management tools

### **🚀 Execution Scripts**
- **`throttle_free_eval.sh`** - Load stable config
- **`scripts/run_ragchecker_smoke_test.sh`** - Fast smoke testing
- **`scripts/ragchecker_official_evaluation.py`** - Full evaluation

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
- **`scripts/baseline_version_manager.py --help`** - Version management
- **`scripts/ragchecker_official_evaluation.py --help`** - All options

## 🎯 **Agent Memory Integration**

**For Cursor AI agents, remember:**
- **Entry point**: This file (`000_core/000_evaluation-system-entry-point.md`)
- **Standard command**: Always use `--stable` flag
- **Configuration**: Never modify stable config without versioning
- **Results**: Always check `metrics/baseline_evaluations/`

---

**This is the SINGLE SOURCE OF TRUTH for evaluation system usage.**
**All agents should start here and follow these exact procedures.**
