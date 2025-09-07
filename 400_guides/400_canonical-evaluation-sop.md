# Canonical Evaluation Standard Operating Procedure
> Agents: start at `000_core/000_evaluation-system-entry-point.md` or run `./run_evals.sh`.

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Standard Operating Procedure for canonical, locked evaluation system with regression tracking | Setting up evaluation system, running evaluations, or managing baselines | Follow the SOP for consistent, comparable evaluation results |

## 🎯 **Overview**

This SOP establishes a **canonical, locked evaluation system** for regression tracking and performance monitoring. The system ensures **apples-to-apples comparisons** across all evaluation runs.

## 🔒 **Core Principles**

1. **One canonical, locked "stable" eval** for regression tracking
2. **Versioned baselines** when intentionally changing weights/pipeline
3. **Small smoke tests** for fast iteration between big runs
4. **Audit trail** with git commits and configuration provenance

## 📋 **Standard Evaluation Flow**

### **🔄 Daily Regression Testing**

**Command (run every time):**
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```

**What this does:**
- ✅ Loads locked stable configuration
- ✅ Uses proven throttle-free settings
- ✅ Runs all 15 test cases
- ✅ Generates comparable results

**Verify banner shows:**
```
🔒 Loaded env from configs/stable_bedrock.env … lock=True
ASYNC_MAX_CONCURRENCY=1, BEDROCK_MAX_CONCURRENCY=1, BEDROCK_MAX_RPS=0.15, MODEL_ID=anthropic.claude-3-haiku-20240307-v1
```

### **💨 Fast Iteration (Smoke Tests)**

**For quick testing between changes:**
```bash
./scripts/run_ragchecker_smoke_test.sh
```

**What this does:**
- ✅ Uses subset of representative test cases
- ✅ Fast mode enabled
- ✅ Same locked configuration
- ✅ Quick feedback loop

## 🔧 **Configuration Management**

### **📁 Stable Configuration**

**File**: `configs/stable_bedrock.env`
- **Purpose**: Locked configuration for regression tracking
- **Status**: DO NOT MODIFY without versioning
- **Contains**: Proven throttle-free settings

### **🔄 Versioning New Baselines**

**When to version:**
- Intentionally changing weights/config
- Want to reset expectations
- New model or significant changes

**Steps:**
1. **Create versioned config:**
   ```bash
   cp configs/stable_bedrock.env configs/stable_bedrock_YYYYMMDD.env
   ```

2. **Update default (optional):**
   ```bash
   # Edit throttle_free_eval.sh to point to new config
   export RAGCHECKER_ENV_FILE=configs/stable_bedrock_YYYYMMDD.env
   ```

3. **Run baseline setup:**
   ```bash
   python3 scripts/baseline_version_manager.py --full-setup
   ```

4. **Run stable eval and promote:**
   ```bash
   source throttle_free_eval.sh
   python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
   ```

## 📊 **Results Management**

### **📁 Results Storage**

**Location**: `metrics/baseline_evaluations/`
- **Format**: `ragchecker_official_evaluation_YYYYMMDD_HHMMSS.json`
- **Contains**: Full evaluation results with provenance

### **📋 Baseline Documents**

**Created by version manager:**
- `NEW_BASELINE_MILESTONE_YYYYMMDD.md` - New target baseline
- `BASELINE_LOCKED_YYYYMMDD.md` - Locked configuration audit
- `stable_bedrock_YYYYMMDD.env` - Versioned configuration

## 🚨 **Red Line Enforcement**

### **🔴 Build Freeze Triggers**

**When ANY baseline metric falls below target:**
- **Recall@20** < 0.65 → **BUILD FREEZE**
- **Precision@k** < 0.20 → **BUILD FREEZE**
- **Faithfulness** < 0.60 → **BUILD FREEZE**

### **✅ Build Resume Conditions**

**ALL baseline metrics must be restored above targets before:**
- New feature development
- Major system changes
- Performance-impacting updates

## 🛠️ **Troubleshooting**

### **🚫 Throttling Issues**

**If throttled at all:**
1. **Reduce rate limit:**
   ```bash
   # Edit configs/stable_bedrock.env
   export BEDROCK_MAX_RPS=0.06  # or 0.04
   ```

2. **Increase cooldown:**
   ```bash
   export BEDROCK_COOLDOWN_SEC=45  # or 60
   ```

3. **Re-run and lock:**
   ```bash
   source throttle_free_eval.sh
   python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
   ```

### **❌ Configuration Issues**

**Missing stable config:**
```bash
cp configs/stable_bedrock.env.template configs/stable_bedrock.env
```

**Wrong environment:**
```bash
# Verify banner shows correct settings
# Check configs/stable_bedrock.env exists
# Ensure RAGCHECKER_LOCK_ENV=1
```

## 📈 **Performance Monitoring**

### **📊 Key Metrics to Track**

**Retrieval Quality:**
- Recall@20 (target: ≥0.65)
- Precision@k (target: ≥0.20)
- F1 Score (target: ≥0.22)

**Answer Quality:**
- Faithfulness (target: ≥0.60)
- Unsupported Claims (target: ≤15%)
- Context Utilization (target: ≥60%)

### **📋 Reporting**

**Weekly baseline reports:**
- Compare against locked baseline
- Track regression trends
- Identify performance gaps
- Document configuration changes

## 🎯 **Best Practices**

### **✅ Do**

- **Always use stable configuration** for regression testing
- **Version baselines** when making intentional changes
- **Run smoke tests** for fast iteration
- **Document configuration changes** with git commits
- **Lock successful configurations** immediately

### **❌ Don't**

- **Modify stable config** without versioning
- **Run evaluations** without locked configuration
- **Ignore throttling** - fix configuration instead
- **Skip smoke tests** for major changes
- **Deploy without baseline validation**

## ⚙️ Quick Recall Boost (Safe Toggle)

When under RED LINE enforcement and recall needs improvement while guarding precision, use the safe toggle and aliases:

```bash
# Apply recall tuning, run smoke test, then evaluate
source throttle_free_eval.sh && recall_boost_apply && \
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory

# Revert tuning and re-check quickly
source throttle_free_eval.sh && recall_boost_revert
```

Details:
- Script: `scripts/toggle_recall_boost.py` (apply/revert atomically; backups under `metrics/derived_configs/recall_boost_backups/`)
- Targets set: `candidates.final_limit=80`, `rerank.final_top_n=12`, `rerank.alpha=0.6`, `prefilter.min_bm25_score=0.05`, `prefilter.min_vector_score=0.65`
- Guard: Abort changes if precision drops below your interim floor (e.g., ≥0.149) without ≥+0.03 recall gain.

See also: `000_core/000_evaluation-system-entry-point.md` — Recall Improvement Playbook and Lessons Application.

## 🔄 **Automation Opportunities**

### **🤖 Cursor Tasks**

**Add to evaluation script:**
- `--stable` flag with automatic config loading
- Post-run queue stats and provenance tracking
- Automatic baseline versioning on config changes

### **📅 Scheduled Runs**

**Nightly regression testing:**
- Source stable config
- Run full evaluation
- Compare against baseline
- Alert on regressions

**PR validation:**
- Run smoke test on every PR
- Full evaluation on performance labels
- Baseline comparison required

---

**Generated**: 2025-09-04
**Status**: ✅ **CANONICAL EVALUATION SOP ESTABLISHED**
**Next Review**: 2025-09-11
