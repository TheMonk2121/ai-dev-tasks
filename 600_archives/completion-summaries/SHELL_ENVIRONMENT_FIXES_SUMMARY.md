# 🔧 Shell Environment Fixes - Complete Summary

## 🎯 **Problem Identified**

The **Homebrew migration** and **shell integration setup** were causing global environment conflicts that skewed RAGChecker evaluation runs:

### **Root Causes**
1. **Global env overrides**: `~/.env.ai-dev-tasks` contained conflicting BEDROCK_* and RAGCHECKER_* variables
2. **Multiple shell sourcing**: 4 shell files were sourcing the same environment file
3. **PATH duplicates**: `/opt/homebrew/bin` and Python paths appeared multiple times
4. **Variable naming conflicts**: Different configs used different variable names

## ✅ **Fixes Implemented**

### **1. Cleaned Global Environment**
- **Removed** all BEDROCK_* and RAGCHECKER_* exports from `~/.env.ai-dev-tasks`
- **Kept** only generic PATH and editor settings
- **Created backup**: `~/.env.ai-dev-tasks.backup.YYYYMMDDHHMMSS`

### **2. Single-Source Environment Loading**
- **Removed** sourcing from `.zprofile`, `.bashrc`, `.bash_profile`
- **Kept** sourcing only in `.zshrc` to avoid duplicate loads
- **Created backups** of all modified shell files

### **3. Enhanced Hermetic Runner**
- **Updated** `scripts/run_hermetic_eval.sh` to activate virtual environment
- **Added** support for both `.venv` and `venv` directories
- **Maintains** clean environment with minimal PATH

### **4. PATH Deduplication**
- **Added** `typeset -U path; PATH="${(j/:/)path}"` to `.zshrc`
- **Prevents** duplicate PATH entries in future shell sessions

## 🚀 **Run Options Available**

### **Throttle-Free (Zero Throttling)**
```bash
./scripts/run_hermetic_eval.sh
```
- **Rate**: `BEDROCK_MAX_RPS=0.08`
- **Environment**: Clean, hermetic
- **Use case**: Production runs, CI/CD

### **Stable Baseline (Faster)**
```bash
source configs/stable_bedrock.env
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```
- **Rate**: `BEDROCK_MAX_RPS=0.15`
- **Environment**: Project config
- **Use case**: Development iterations, baseline establishment

### **Direct CLI Runner**
```bash
source throttle_free_eval.sh
python3 scripts/run_bedrock_eval_direct.py
```
- **Rate**: `BEDROCK_MAX_RPS=0.08`
- **Environment**: Throttle-free config
- **Use case**: Direct evaluation runs

## 🔍 **Verification Commands**

### **Check Effective Settings**
```bash
source throttle_free_eval.sh && python3 scripts/ragchecker_official_evaluation.py --use-local-llm --bypass-cli
```

### **Verify Banner Output**
Look for:
- `🧰 Active Bedrock caps: BEDROCK_MAX_RPS=0.08, BEDROCK_MAX_IN_FLIGHT=1`
- `BASE_BACKOFF=2.0, MAX_BACKOFF=16.0`

### **Test Hermetic Environment**
```bash
./scripts/run_hermetic_eval.sh --help
```

## 📊 **Configuration Hierarchy**

### **Stable 1** (`configs/stable_bedrock.env`)
- **Rate**: `BEDROCK_MAX_RPS=0.15`
- **Evidence**: `RAGCHECKER_EVIDENCE_JACCARD=0.07`, `RAGCHECKER_EVIDENCE_COVERAGE=0.20`
- **Use**: Development, baseline establishment

### **Stable 2** (`throttle_free_eval.sh`)
- **Rate**: `BEDROCK_MAX_RPS=0.08` (overrides Stable 1)
- **Evidence**: Same as Stable 1
- **Use**: Production, zero-throttling runs

### **Global Environment** (`~/.env.ai-dev-tasks`)
- **Content**: Generic settings only
- **No**: BEDROCK_* or RAGCHECKER_* variables
- **Purpose**: Shell integration, PATH management

## 🛡️ **Hardening Measures**

### **Environment Isolation**
- **Hermetic runner**: Runs in clean environment
- **Virtual environment**: Automatically activated
- **Minimal PATH**: Only essential directories

### **Configuration Consistency**
- **Variable aliases**: Both legacy and standardized names supported
- **Single source**: Environment loaded from one location
- **Backup strategy**: All changes backed up before modification

### **PATH Management**
- **Deduplication**: Automatic removal of duplicate entries
- **Order preservation**: Maintains correct PATH precedence
- **Homebrew integration**: Proper `/opt/homebrew/bin` handling

## 🎯 **Key Benefits**

1. **Consistent Evaluations**: No more global environment conflicts
2. **Reproducible Results**: Hermetic runs guarantee clean environment
3. **Faster Development**: Stable 1 config for rapid iterations
4. **Production Ready**: Stable 2 config for zero-throttling runs
5. **Maintainable**: Clear separation of concerns between global and project configs

## 📝 **Next Steps**

1. **Use Stable 1** for baseline establishment and development
2. **Use Stable 2** for production runs and final evaluations
3. **Monitor** for any remaining environment conflicts
4. **Update** documentation as needed for team members

---

**Status**: ✅ **COMPLETE** - All shell environment conflicts resolved
**Date**: $(date)
**Backup Location**: `~/.env.ai-dev-tasks.backup.*` and shell file backups
