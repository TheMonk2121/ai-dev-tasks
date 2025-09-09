# Evaluation Profiles Guide

<!-- ANCHOR_KEY: evaluation-profiles-guide -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["researcher", "implementer", "coder"] -->

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete guide to the evaluation profile system that prevents "accidentally-synthetic" baselines | Need to run evaluations, understand profile system, or troubleshoot evaluation issues | Use the appropriate profile for your use case and follow the quick start commands |

## 🎯 **Evaluation Profiles Overview**

The evaluation profile system provides **deterministic configuration** with **preflight checks** to prevent "accidentally-synthetic" baselines. This eliminates the confusion between real and mock evaluations.

### **📋 Available Profiles**

| Profile | Purpose | Use Case | Driver | Database |
|---------|---------|----------|--------|----------|
| `real` | Baseline/tuning on real RAG | Production baselines, performance tuning | `dspy_rag` | Real PostgreSQL |
| `gold` | Real RAG + gold cases | Validation with known good answers | `dspy_rag` | Real PostgreSQL |
| `mock` | Infra-only, synthetic | CI smoke tests, infrastructure validation | `synthetic` | Mock database |

## 🚀 **Quick Start**

### **Baseline (real data):**
```bash
./scripts/eval_real.sh --concurrency 8
```

### **Gold validation (real + gold cases):**
```bash
./scripts/eval_gold.sh
```

### **Infra smoke (mock, fast):**
```bash
./scripts/eval_mock.sh --concurrency 3
```

### **Using Makefile:**
```bash
make eval-real    # Baseline/tuning on real RAG
make eval-gold    # Real RAG + gold cases
make eval-mock    # Infra-only smoke
```

## 🔧 **Configuration System**

### **Profile Files**
Each profile has a dedicated configuration file:

- `configs/profiles/real.env` - Real evaluations
- `configs/profiles/gold.env` - Real evaluations with gold cases
- `configs/profiles/mock.env` - Mock evaluations

### **Configuration Resolution Order**
1. **CLI flags** (highest precedence)
2. **Profile file** configs
3. **Process env** (for CI secrets only)
4. **Hardcoded safe defaults**

### **Preflight Checks**
The system **refuses to run** if:
- `real`/`gold` profile with `EVAL_DRIVER=synthetic`
- `real`/`gold` profile with `POSTGRES_DSN=mock://*`
- No profile specified

## 📊 **Output Structure**

### **Profile-Aware Output Directories**
Results are saved to:
```
metrics/runs/{YYYYMMDD_HHMMSS}__{profile}__driver-{driver}__f1-{f1}__p-{p}__r-{r}/
```

### **Artifacts**
Each run creates:
- `summary.json` - Profile and environment information
- `evaluation_results.json` - Full evaluation results
- `provenance.json` - Configuration and metadata

## 🛡️ **Safety Features**

### **Branch Protection**
- **Mock profile blocked on main branch** - Prevents accidental synthetic baselines
- **Real profile required for baselines** - Ensures production-quality evaluations

### **Configuration Validation**
- **Preflight checks** before evaluation starts
- **Clear error messages** for invalid configurations
- **Banner display** showing resolved configuration

## 🔄 **CI Integration**

### **PR Workflow** (Fast)
```yaml
# .github/workflows/ci-pr-quick.yml
- name: Eval (mock, low concurrency)
  run: ./scripts/eval_mock.sh --concurrency 3
```

### **Nightly Baseline** (Real)
```yaml
# .github/workflows/ci-nightly-baseline.yml
- name: Eval (real, higher concurrency)
  env:
    POSTGRES_DSN: ${{ secrets.POSTGRES_DSN }}
  run: ./scripts/eval_real.sh --concurrency 12
```

## 🧪 **Testing Profiles**

### **Test Profile Configuration**
```bash
make test-profiles
```

### **Manual Testing**
```bash
# Test each profile
python3 scripts/lib/config_loader.py --profile real
python3 scripts/lib/config_loader.py --profile gold
python3 scripts/lib/config_loader.py --profile mock
```

## 🚨 **Common Issues & Solutions**

### **"No profile selected" Error**
```bash
❌ No profile selected.
   Use one of:
     --profile real   (baseline/tuning on real RAG)
     --profile gold   (real RAG + gold cases)
     --profile mock   (infra tests only)
```
**Solution**: Always specify a profile: `--profile real`

### **"Real/gold require EVAL_DRIVER=dspy_rag" Error**
```bash
❌ Real/gold require EVAL_DRIVER=dspy_rag (synthetic refused).
```
**Solution**: Use real profile, not mock: `--profile real`

### **"Real/gold require a real POSTGRES_DSN" Error**
```bash
❌ Real/gold require a real POSTGRES_DSN (not mock://).
```
**Solution**: Set real database connection in profile file

### **"Refusing to run mock profile on main branch" Error**
```bash
❌ Refusing to run mock profile on main branch.
```
**Solution**: Use real profile for main branch: `--profile real`

## 📝 **Environment Variables**

### **Profile-Specific Variables**
| Variable | real | gold | mock | Description |
|----------|------|------|------|-------------|
| `EVAL_DRIVER` | `dspy_rag` | `dspy_rag` | `synthetic` | Evaluation driver |
| `RAGCHECKER_USE_REAL_RAG` | `1` | `1` | `0` | Use real RAG system |
| `POSTGRES_DSN` | Real DB | Real DB | `mock://test` | Database connection |
| `EVAL_CONCURRENCY` | `8` | `8` | `3` | Worker concurrency |

### **CI Secrets** (Flow through automatically)
- `POSTGRES_DSN`
- `OPENAI_API_KEY`
- `BEDROCK_REGION`
- `BEDROCK_ACCESS_KEY`
- `BEDROCK_SECRET_KEY`

## 🎯 **Best Practices**

### **For Baselines**
- ✅ Always use `--profile real`
- ✅ Use higher concurrency (8-12 workers)
- ✅ Run on real database
- ❌ Never use mock profile

### **For Development**
- ✅ Use `--profile mock` for fast iteration
- ✅ Use lower concurrency (3 workers)
- ✅ Test infrastructure changes
- ❌ Don't use for performance measurements

### **For Validation**
- ✅ Use `--profile gold` with known test cases
- ✅ Compare against expected results
- ✅ Validate system behavior

## 🔍 **Troubleshooting**

### **Check Current Configuration**
```bash
python3 scripts/lib/config_loader.py --profile real
```

### **Validate Profile Files**
```bash
# Check if profile files exist
ls -la configs/profiles/
```

### **Test Profile System**
```bash
# Test all profiles
make test-profiles
```

## 🔧 **Pydantic Array Fields for Evaluation Data**

### **Array Field Guidelines**

The evaluation system uses strongly-typed NumPy arrays in Pydantic models for feature data:

```python
from dspy_modules.retriever.feature_schema import Vector384, FusionFeatures

# Use the correct dimension for your embedding model
feature = FusionFeatures(
    s_bm25=0.3, s_vec=0.5, s_title=0.1, s_short=0.2,
    r_bm25=0.1, r_vec=0.2, len_norm=0.9,
    q_vec=[0.1] * 384,  # 384-dim for all-MiniLM-L6-v2
    d_vec=[0.2] * 384
)
```

### **Environment Control**

```bash
# Strict validation (CI/Production)
export EVAL_STRICT_ARRAYS=1

# Permissive mode (Development)
export EVAL_STRICT_ARRAYS=0
```

### **JSONL Persistence**

```python
from train.feature_io import write_feature, read_feature

# Write validated features
jsonl_line = write_feature(feature)

# Read with validation
feature = read_feature(jsonl_line)
```

### **Available Vector Types**

- `Vector384` - all-MiniLM-L6-v2 (your default)
- `Vector768` - all-mpnet-base-v2, all-distilroberta-v1
- `Vector1024` - intfloat/e5-large-v2
- `Vector1536` - text-embedding-ada-002

## 📚 **Related Documentation**

- [Naming Conventions](200_setup/200_naming-conventions.md) - File naming standards
- [System Overview](400_guides/400_03_system-overview-and-architecture.md) - Overall system architecture
- [Testing Methodology](300_experiments/300_testing-methodology-log.md) - Testing approaches

---

**Profile System Status**: ✅ **IMPLEMENTED** - Prevents accidentally-synthetic baselines
**Array Fields Status**: ✅ **IMPLEMENTED** - Strongly-typed NumPy arrays with JSON serialization
**Last Updated**: 2025-09-08
**Next Review**: 2025-02-07
