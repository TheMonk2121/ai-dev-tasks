# 🎯 Evaluation System Entry Point
<!-- keywords: evals, run the evals, evaluations, ragchecker, benchmark -->

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| **PRIMARY ENTRY POINT** for all evaluation system usage - agents start here | Any agent needs to run evaluations, check performance, or understand the system | Follow the "Quick Start" section below |

## 🚀 **Quick Start (For All Agents)**

### **📋 Standard Evaluation Command**
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```

**This is the ONE command every agent should use for evaluations.**

### **💨 Fast Testing Command**
```bash
./scripts/run_ragchecker_smoke_test.sh
```

**Use this for quick iteration and testing changes.**

### 🧭 If you were told to "run the evals"
- Do exactly the two commands above.
- If Bedrock credentials are missing, run `./scripts/run_ragchecker_smoke_test.sh` and report results.

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
