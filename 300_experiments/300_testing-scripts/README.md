# 🧪 Testing Scripts Directory

**Location**: `300_experiments/300_testing-scripts/`
**Purpose**: Centralized location for all testing, evaluation, and benchmarking scripts

## 📋 **Available Testing Scripts**

### **🔍 RAGChecker Testing**
- **`ragchecker_official_evaluation.py`** - Official RAGChecker baseline validation and evaluation
- **`ragchecker_performance_monitor.py`** - Real-time RAGChecker performance monitoring

### **⚡ Performance Testing**
- **`performance_benchmark.py`** - System-wide performance benchmarking and optimization testing
- **`memory_benchmark.py`** - Memory system performance and optimization testing

### **🔌 Integration Testing**
- **`bedrock_test.py`** - AWS Bedrock integration testing and validation
- **`evaluation_approach_discussion.py`** - DSPy agent evaluation approach discussion and testing

### **🎯 Usage Examples**

#### **RAGChecker Baseline Validation**
```bash
cd 300_experiments/300_testing-scripts/
python3 ragchecker_official_evaluation.py --use-bedrock --bypass-cli
```

#### **Performance Benchmarking**
```bash
cd 300_experiments/300_testing-scripts/
python3 performance_benchmark.py --system memory --duration 300
```

#### **Memory System Testing**
```bash
cd 300_experiments/300_testing-scripts/
python3 memory_benchmark.py --test-type overflow --iterations 1000
```

#### **AWS Bedrock Integration Testing**
```bash
cd 300_experiments/300_testing-scripts/
python3 bedrock_test.py
```

#### **DSPy Evaluation Approach Testing**
```bash
cd 300_experiments/300_testing-scripts/
python3 evaluation_approach_discussion.py
```

## 🔧 **Configuration**

**Test Configs**: Located in `../300_testing-configs/`
**Test Results**: Output to `../300_testing-results/`

## 📊 **Integration with Testing Infrastructure**

- **Baseline Testing**: Automated baseline validation with CI integration
- **Performance Monitoring**: Continuous performance tracking and alerting
- **Regression Detection**: Automatic detection of performance degradation
- **Quality Gates**: Integration with testing methodology and quality gates

## 🚀 **Adding New Testing Scripts**

1. **Place Script**: Add new testing scripts to this directory
2. **Update README**: Document the script's purpose and usage
3. **Update Methodology**: Reference in `300_testing-methodology-log.md`
4. **CI Integration**: Add to automated testing pipeline if applicable

## 📚 **Related Documentation**

- **[300_testing-methodology-log.md](../300_testing-methodology-log.md)** - Testing strategies and methodologies
- **[300_complete-testing-coverage.md](../300_complete-testing-coverage.md)** - Complete testing coverage overview
- **[300_testing-infrastructure-guide.md](../300_testing-infrastructure-guide.md)** - Testing infrastructure setup and configuration
