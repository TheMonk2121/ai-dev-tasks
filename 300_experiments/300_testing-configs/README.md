# ⚙️ Testing Configurations Directory

**Location**: `300_experiments/300_testing-configs/`
**Purpose**: Centralized location for all testing environment configurations

## 📋 **Available Test Configurations**

### **🔒 Baseline Configurations**
- **`baseline_v1.1.env`** - Current locked baseline configuration (precision ≥ 0.159, recall ≥ 0.166, F1 ≥ 0.159)
- **`phase2_baseline_v1.1.sh`** - Phase-2 exact configuration script for baseline validation
- **`rollback_phase2_baseline.sh`** - Rollback configuration to restore stable Phase-2 baseline

### **🧪 Phase-Based Testing Configurations**
- **`phase1_ragchecker_flags.sh`** - Phase 1 RAGChecker enhancement flags for testing

### **🧪 Performance Testing Configurations**
- **`performance_testing.env`** - Configuration for performance benchmarking and optimization testing
- **`memory_testing.env`** - Configuration for memory system performance testing

### **🔌 Integration Testing Configurations**
- **`integration_testing.env`** - Configuration for system integration and end-to-end testing

## 🎯 **Configuration Usage**

#### **Load Baseline Configuration**
```bash
cd 300_experiments/300_testing-configs/
source baseline_v1.1.env
```

#### **Load Phase-2 Baseline Script**
```bash
cd 300_experiments/300_testing-configs/
source phase2_baseline_v1.1.sh
```

#### **Load Phase 1 RAGChecker Flags**
```bash
cd 300_experiments/300_testing-configs/
source phase1_ragchecker_flags.sh
```

#### **Run Tests with Specific Config**
```bash
cd 300_experiments/300_testing-scripts/
export $(cat ../300_testing-configs/baseline_v1.1.env | xargs)
python3 ragchecker_official_evaluation.py --use-bedrock --bypass-cli
```

## 🔧 **Configuration Management**

**Environment Variables**: All test configurations use environment variables for easy switching
**Version Control**: Configurations are versioned and tracked in git
**CI Integration**: Automated testing uses these configurations for consistent test environments

## 📊 **Baseline Configuration Details**

**Current Baseline v1.1**:
- **Precision**: 0.159 (target: ≥0.20)
- **Recall**: 0.166 (target: ≥0.45)
- **F1 Score**: 0.159 (target: ≥0.22)
- **Faithfulness**: Reporting only (target: ≥0.60 with gating)

**Key Features**:
- Dynamic-K evidence selection (weak:3, base:5, strong:9)
- Blended scoring (Jaccard:0.20, ROUGE:0.30, Cosine:0.50)
- Claim binding with soft-drop policy
- Bedrock reliability with retry logic and caching

## 🚀 **Adding New Configurations**

1. **Create Config**: Add new `.env` file with appropriate variables
2. **Update README**: Document the configuration's purpose and parameters
3. **Test Integration**: Verify the configuration works with testing scripts
4. **Version Control**: Commit and tag the new configuration

## 📚 **Related Documentation**

- **[300_testing-scripts/](../300_testing-scripts/)** - Testing scripts that use these configurations
- **[300_testing-methodology-log.md](../300_testing-methodology-log.md)** - Testing strategies and methodologies
- **[300_complete-testing-coverage.md](../300_complete-testing-coverage.md)** - Complete testing coverage overview
