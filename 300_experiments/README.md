# 🧪 300_experiments - Testing & Experimental Infrastructure

**Purpose**: Centralized location for all testing, experimentation, methodology, and results

## 📁 **Directory Structure**

### **🧪 Testing Scripts & Tools**
- **[300_testing-scripts/](300_testing-scripts/)** - All testing, evaluation, and benchmarking scripts
  - RAGChecker testing and evaluation
  - Performance benchmarking
  - Memory system testing
  - Integration testing

### **⚙️ Testing Configurations**
- **[300_testing-configs/](300_testing-configs/)** - Test environment configurations and parameters
  - Baseline configurations (v1.1 locked)
  - Performance testing configs
  - Integration testing configs

### **📊 Testing Results & Analysis**
- **[300_testing-results/](300_testing-results/)** - Test outputs, results, and analysis
  - Baseline validation results
  - Performance test results
  - Integration test results
  - System health audits

### **📚 Testing Documentation & Methodology**
- **[300_testing-methodology-log.md](300_testing-methodology-log.md)** - Testing strategies, methodologies, and lessons learned
- **[300_complete-testing-coverage.md](300_complete-testing-coverage.md)** - Complete testing coverage overview and analysis
- **[300_testing-methodology-log.md](300_testing-methodology-log.md)** - Testing infrastructure setup and configuration
- **[300_historical-testing-archive.md](300_historical-testing-archive.md)** - Historical testing results and learnings

### **🔍 Specialized Testing Results**
- **[300_retrieval-testing-results.md](300_retrieval-testing-results.md)** - Retrieval system testing (B-1065-B-1068)
- **[300_memory-system-testing.md](300_memory-system-testing.md)** - Memory system testing and validation
- **[300_integration-testing-results.md](300_integration-testing-results.md)** - System integration testing results
- **[300_testing-coverage-analysis.md](300_testing-coverage-analysis.md)** - Testing coverage analysis and gaps

### **🎭 Demo & Example Scripts**
- **[300_dspy-v2-demo-scripts/](300_dspy-v2-demo-scripts/)** - DSPy framework demonstration and example scripts

## 🎯 **Quick Start Guide**

### **Run RAGChecker Baseline Validation**
```bash
cd 300_experiments/300_testing-scripts/
python3 ragchecker_official_evaluation.py --use-bedrock --bypass-cli
```

### **Load Testing Configuration**
```bash
cd 300_experiments/300_testing-configs/
source baseline_v1.1.env
```

### **View Testing Results**
```bash
cd 300_experiments/300_testing-results/
ls -la baseline_results/
```

## 🔧 **Testing Infrastructure Overview**

### **Current Status**
- **Baseline v1.1**: LOCKED (precision ≥ 0.159, recall ≥ 0.166, F1 ≥ 0.159)
- **Testing Coverage**: 100% for all recent breakthroughs (B-1045, B-1048, B-1054, B-1059, B-1009)
- **Infrastructure**: Complete testing scripts, configs, and results organization

### **Key Testing Capabilities**
- **Automated Baseline Validation**: CI-integrated baseline compliance testing
- **Performance Benchmarking**: Comprehensive performance testing and optimization
- **Integration Testing**: End-to-end system integration validation
- **Regression Detection**: Automated performance regression prevention
- **Quality Gates**: Comprehensive testing quality assurance

### **Testing Methodologies**
- **Dev Slice Testing**: 8-case stratified testing for development
- **Full Validation**: 15-case testing with two-run requirement
- **Baseline Optimization**: Systematic precision/recall improvement testing
- **Integration Validation**: Cross-component compatibility testing

## 🚀 **Adding New Testing Content**

### **New Testing Scripts**
1. Add to `300_testing-scripts/`
2. Update `300_testing-scripts/README.md`
3. Reference in `300_testing-methodology-log.md`

### **New Test Configurations**
1. Add to `300_testing-configs/`
2. Update `300_testing-configs/README.md`
3. Document in testing methodology

### **New Test Results**
1. Organize in appropriate `300_testing-results/` subdirectory
2. Update relevant testing documentation
3. Reference in methodology and coverage analysis

## 📚 **Related Documentation**

- **[400_guides/](../400_guides/)** - Core system documentation and guides
- **[000_core/](../000_core/)** - Core workflows and backlog management
- **[scripts/](../scripts/)** - General utility scripts and tools

## 🔍 **Testing Discovery**

**Current Testing Status**: Check `300_testing-methodology-log.md`
**Testing Coverage**: Review `300_complete-testing-coverage.md`
**Testing Infrastructure**: See `300_testing-methodology-log.md`
**Historical Results**: Browse `300_historical-testing-archive.md`

---

**Last Updated**: September 2, 2025
**Maintainer**: Daniel Jacobs
**Testing Infrastructure**: Complete and organized
