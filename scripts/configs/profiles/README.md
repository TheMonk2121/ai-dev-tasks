# Evaluation Profiles - Optimized Configuration

This directory contains optimized evaluation profiles for different use cases in the AI Dev Tasks project.

## 📊 Profile Overview

| **Profile** | **Purpose** | **Use Case** | **Speed** | **Reliability** | **Status** |
|-------------|-------------|--------------|-----------|-----------------|------------|
| **Gold** | Production Baselines & CI Gates | Curated test cases for reliable performance tracking | 🟡 Medium | ✅ High | ✅ **OPTIMIZED** |
| **Real** | Development & Tuning | Full system testing with project data | 🟡 Medium | ⚠️ Variable | ✅ **OPTIMIZED** |
| **Mock** | Infrastructure Testing | Fast plumbing tests without external dependencies | ⚡ Fast | ✅ High | ✅ **OPTIMIZED** |

## 🎯 Profile Details

### **Gold Profile** (`gold.env`)
- **Purpose**: Curated test cases for reliable performance tracking
- **Use Case**: CI gates, baseline enforcement, regression detection
- **Key Features**:
  - Conservative retrieval settings (60/60/10) for stability
  - Baseline enforcement with red-line protection
  - Curated gold test cases from `evals/data/gold/v1/gold_cases.jsonl`
  - Production-ready Bedrock settings
  - Comprehensive logging and metrics

### **Real Profile** (`real.env`)
- **Purpose**: Full system testing with project data for development
- **Use Case**: Development, tuning, full pipeline validation
- **Key Features**:
  - Aggressive retrieval settings (140/140/18) for maximum recall
  - Development-focused Bedrock settings with higher concurrency
  - Experimental features enabled for testing
  - Tuning mode for parameter optimization
  - Enhanced performance monitoring

### **Mock Profile** (`mock.env`)
- **Purpose**: Fast plumbing tests without external dependencies
- **Use Case**: CI infrastructure, unit tests, development setup
- **Key Features**:
  - Synthetic evaluation driver for speed
  - Mock database connection (`mock://test`)
  - All RAG components disabled for infrastructure testing
  - CI-optimized settings for fast iteration
  - Minimal logging and metrics

## 🚀 Usage

### **Command Line**
```bash
# Gold Profile (Production Baselines)
make eval-gold

# Real Profile (Development & Tuning)
make eval-real

# Mock Profile (Infrastructure Testing)
make eval-mock
```

### **Direct Scripts**
```bash
# Gold Profile
./scripts/shell/deployment/run_evals_gold.sh

# Real Profile
./scripts/shell/deployment/run_evals_real.sh

# Mock Profile
./scripts/shell/deployment/run_evals_mock.sh
```

### **Environment Variables**
```bash
# Load specific profile
export RAGCHECKER_ENV_FILE=scripts/configs/profiles/gold.env
source scripts/configs/profiles/gold.env

# Run evaluation
uv run python scripts/ragchecker_official_evaluation.py
```

## 🔧 Configuration Sections

Each profile is organized into logical sections:

1. **Core Evaluation Settings** - Basic profile configuration
2. **Test Configuration** - Test case and concurrency settings
3. **Retrieval Settings** - Vector search and BM25 parameters
4. **Reranking Settings** - Reranking model and pool configuration
5. **Reader Configuration** - Answer generation and quality control settings
6. **Bedrock Settings** - AWS Bedrock API configuration
7. **Metrics & Logging** - Evaluation output and progress tracking
8. **Database Configuration** - PostgreSQL connection settings
9. **Profile-Specific Features** - Unique features for each profile

## 📈 Performance Characteristics

### **Gold Profile**
- **Retrieval**: Conservative (60/60/10) for consistent results
- **Reranking**: Conservative (40/10) for baseline stability
- **Concurrency**: 8 workers for balanced performance
- **Bedrock**: Conservative rate limiting (0.12 RPS)
- **Use Case**: Production evaluation, CI gates

### **Real Profile**
- **Retrieval**: Aggressive (140/140/18) for maximum recall
- **Reranking**: Aggressive (60/18) for comprehensive testing
- **Concurrency**: 12 workers for development speed
- **Bedrock**: Higher rate limiting (0.15 RPS) for flexibility
- **Use Case**: Development, tuning, full system testing

### **Mock Profile**
- **Retrieval**: Disabled (0/0/0) for infrastructure testing
- **Reranking**: Disabled (0/0) for speed
- **Concurrency**: 3 workers for fast iteration
- **Bedrock**: Mock mode (0 RPS) for infrastructure testing
- **Use Case**: CI infrastructure, unit tests

## 🧠 Reader Configuration

All profiles use optimized reader settings for better answer generation:

### **Reader Settings**
- **`READER_ENFORCE_SPAN=0`** - Disabled span enforcement for better answer generation
- **`READER_PRECHECK=1`** - Enabled precheck for quality control (10% token overlap)
- **`READER_ABSTAIN=1`** - Enabled abstention gate to prevent hallucination
- **`READER_PRECHECK_MIN_OVERLAP=0.10`** - 10% minimum token overlap threshold

### **Why These Settings?**
- **Span enforcement disabled**: Prevents overly strict filtering that was causing "I don't know" responses
- **Precheck enabled**: Ensures questions have sufficient context overlap before processing
- **Abstention enabled**: Prevents the system from making up answers when information isn't clearly present
- **Consistent across profiles**: All profiles use the same reader configuration for predictable behavior

## 🛠️ Customization

### **Adding New Settings**
1. Add the setting to the appropriate section in the profile file
2. Document the setting in this README
3. Update the profile-specific script if needed
4. Test the setting with the appropriate profile

### **Profile-Specific Scripts**
Each profile has a dedicated script in `scripts/shell/deployment/`:
- `run_evals_gold.sh` - Gold profile evaluation
- `run_evals_real.sh` - Real profile evaluation
- `run_evals_mock.sh` - Mock profile evaluation

### **Makefile Integration**
The Makefile includes optimized targets for each profile:
- `make eval-gold` - Run gold profile evaluation
- `make eval-real` - Run real profile evaluation
- `make eval-mock` - Run mock profile evaluation

## 🔍 Troubleshooting

### **Common Issues**
1. **Profile not found**: Check that the profile file exists in `scripts/configs/profiles/`
2. **Database connection failed**: Verify `POSTGRES_DSN` is set correctly
3. **Bedrock API errors**: Check AWS credentials and rate limiting settings
4. **Test cases not found**: Verify `GOLD_FILE` path is correct

### **Debug Mode**
Enable debug mode for detailed logging:
```bash
export RAGCHECKER_DEBUG_MODE=1
export RAGCHECKER_VERBOSE_LOGGING=1
```

### **Profile Validation**
Test profile configuration:
```bash
make test-profiles
```

## 📚 Related Documentation

- [Evaluation System Entry Point](../000_core/000_evaluation-system-entry-point.md)
- [Execution Template](../000_core/003_EXECUTION_TEMPLATE.md)
- [Task List Template](../000_core/002_TASK-LIST_TEMPLATE.md)
- [PRD Template](../000_core/001_PRD_TEMPLATE.md)
