# Testing Infrastructure Guide

<!-- ANCHOR_KEY: testing-infrastructure-guide -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["researcher", "implementer", "coder"] -->

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete guide to testing environment setup, tools, dependencies, and configuration for reproducible testing | Need to set up testing environment, reproduce tests, or understand testing infrastructure | Follow setup instructions, install required tools, or update infrastructure documentation |

## 🎯 **Overview**

This guide provides complete instructions for setting up and maintaining the testing infrastructure for the AI development ecosystem. It ensures all tests can be reproduced consistently and new team members can quickly establish working testing environments.

## 🏗️ **Testing Infrastructure Architecture**

### **Core Components**
- **Testing Environment**: Python 3.12 virtual environment with all dependencies
- **Database**: PostgreSQL with pgvector extension for vector operations
- **Evaluation Framework**: RAGChecker with AWS Bedrock integration
- **Memory Systems**: LTST memory system with database backend
- **Integration Tools**: MCP server, Cursor integration, and testing utilities

### **Infrastructure Layers**
```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Applications                     │
├─────────────────────────────────────────────────────────────┤
│                    Testing Framework                       │
├─────────────────────────────────────────────────────────────┤
│                    Core Dependencies                       │
├─────────────────────────────────────────────────────────────┤
│                    System Infrastructure                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Environment Setup**

### **Prerequisites**

#### **System Requirements**
- **Operating System**: macOS 12.0+, Windows 10+, or Linux Ubuntu 20.04+
- **Python**: Python 3.12 (required)
- **Memory**: Minimum 8GB RAM, recommended 16GB+
- **Storage**: Minimum 10GB free space
- **Network**: Internet access for package installation and AWS services

#### **Required Software**
- **Python 3.12**: [Download from python.org](https://python.org)
- **PostgreSQL 14+**: [Download from postgresql.org](https://postgresql.org)
- **Git**: [Download from git-scm.com](https://git-scm.com)
- **VS Code/Cursor**: [Download from cursor.sh](https://cursor.sh)

### **Step-by-Step Setup**

#### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/ai-dev-tasks.git
cd ai-dev-tasks
```

#### **2. Create Virtual Environment**
```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### **3. Install Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

#### **4. Database Setup**
```bash
# Install PostgreSQL (if not already installed)
# macOS with Homebrew:
brew install postgresql
brew services start postgresql

# Create database
createdb ai_agency

# Install pgvector extension
psql -d ai_agency -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

#### **5. Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
# Set your database connection, AWS credentials, etc.
```

## 🛠️ **Testing Tools & Dependencies**

### **Core Testing Framework**

#### **Python Testing Stack**
- **pytest**: Primary testing framework
- **pytest-asyncio**: Async testing support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking and patching

#### **Code Quality Tools**
- **Ruff**: Fast Python linter and formatter
- **Pyright**: Static type checking
- **Bandit**: Security linting
- **Pre-commit**: Git hooks for code quality

#### **Performance Testing**
- **pytest-benchmark**: Performance benchmarking
- **memory-profiler**: Memory usage profiling
- **cProfile**: Python profiling

### **AI Development Tools**

#### **DSPy Framework**
- **dspy-ai**: Core DSPy framework
- **dspy-ai[all]**: Full DSPy with all dependencies
- **dspy-ai[bedrock]**: AWS Bedrock integration

#### **Vector Operations**
- **pgvector**: PostgreSQL vector extension
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning utilities

#### **Evaluation & Monitoring**
- **ragchecker**: RAG evaluation framework
- **boto3**: AWS SDK for Python
- **psycopg2**: PostgreSQL adapter

### **Integration Testing Tools**

#### **MCP Server Testing**
- **mcp**: Model Context Protocol server
- **httpx**: Async HTTP client for testing
- **websockets**: WebSocket testing support

#### **Cursor Integration Testing**
- **vsce**: VS Code extension packaging
- **@types/vscode**: VS Code extension types
- **jest**: JavaScript testing framework

## 🔧 **Configuration Management**

### **Environment Variables**

#### **Required Environment Variables**
```bash
# Database Configuration
POSTGRES_DSN=postgresql://username:password@localhost:5432/ai_agency
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_agency
POSTGRES_USER=username
POSTGRES_PASSWORD=password

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Testing Configuration
TESTING_MODE=true
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/ai_agency_test
LOG_LEVEL=DEBUG
```

#### **Optional Environment Variables**
```bash
# Performance Testing
BENCHMARK_ITERATIONS=1000
PERFORMANCE_THRESHOLD=0.1

# Integration Testing
INTEGRATION_TEST_TIMEOUT=300
MOCK_EXTERNAL_SERVICES=true

# Debugging
ENABLE_TRACING=true
TRACE_LEVEL=VERBOSE
```

### **Configuration Files**

#### **pyproject.toml**
```toml
[tool.pytest.ini_options]
testpaths = ["tests", "src"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--import-mode=importlib --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "performance: marks tests as performance tests",
    "memory: marks tests as memory system tests",
    "retrieval: marks tests as retrieval system tests"
]

[tool.ruff]
target-version = "py312"
line-length = 88
select = ["E", "F", "I", "N", "W", "B", "A", "C4", "UP", "PL", "RUF"]
ignore = ["E501", "B008", "C901"]
extend-select = ["RUF001", "RUF002", "RUF003", "PLE2502"]

[tool.pyright]
pythonVersion = "3.12"
pythonPlatform = "Darwin"
typeCheckingMode = "strict"
useLibraryCodeForTypes = true
reportMissingImports = true
reportMissingTypeStubs = false
```

#### **pytest.ini**
```ini
[tool:pytest]
testpaths = tests src
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    --import-mode=importlib
    --strict-markers
    --verbose
    --tb=short
    --strict-config
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    performance: marks tests as performance tests
    memory: marks tests as memory system tests
    retrieval: marks tests as retrieval system tests
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

## 🧪 **Testing Workflows**

### **Test Execution Commands**

#### **Basic Testing**
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x
```

#### **Specific Test Categories**
```bash
# Run only unit tests
pytest -m "not integration and not performance"

# Run only integration tests
pytest -m integration

# Run only performance tests
pytest -m performance

# Run only memory system tests
pytest -m memory

# Run only retrieval system tests
pytest -m retrieval
```

#### **Performance Testing**
```bash
# Run performance benchmarks
pytest --benchmark-only

# Run performance tests with profiling
pytest -m performance --profile

# Run memory profiling
pytest -m performance --memray
```

### **Test Organization**

#### **Test Directory Structure**
```
tests/
├── unit/                    # Unit tests
│   ├── test_memory/        # Memory system unit tests
│   ├── test_retrieval/     # Retrieval system unit tests
│   └── test_integration/   # Integration unit tests
├── integration/             # Integration tests
│   ├── test_end_to_end/    # End-to-end workflow tests
│   ├── test_cross_system/  # Cross-system integration tests
│   └── test_performance/   # Performance integration tests
├── performance/             # Performance tests
│   ├── test_benchmarks/    # Performance benchmarks
│   ├── test_load/          # Load testing
│   └── test_stress/        # Stress testing
└── fixtures/                # Test fixtures and data
    ├── test_data/          # Test datasets
    ├── mock_services/      # Mock external services
    └── test_configs/       # Test configurations
```

#### **Test File Naming Convention**
- **Unit Tests**: `test_<module_name>.py`
- **Integration Tests**: `test_integration_<feature>.py`
- **Performance Tests**: `test_performance_<metric>.py`
- **Memory Tests**: `test_memory_<component>.py`
- **Retrieval Tests**: `test_retrieval_<component>.py`

## 📊 **Testing Data Management**

### **Test Datasets**

#### **Required Test Data**
- **Sample Conversations**: Representative conversation data for memory testing
- **Test Queries**: Diverse query types for retrieval testing
- **Performance Baselines**: Historical performance data for comparison
- **Integration Scenarios**: Real-world integration test cases

#### **Test Data Sources**
- **Synthetic Data**: Generated test data for controlled testing
- **Anonymized Real Data**: Real data with privacy protection
- **Public Datasets**: Open-source datasets for validation
- **Mock Data**: Simulated data for isolated testing

### **Data Management Commands**

#### **Test Data Setup**
```bash
# Generate synthetic test data
python scripts/generate_test_data.py

# Load test datasets
python scripts/load_test_data.py

# Validate test data integrity
python scripts/validate_test_data.py

# Clean test data
python scripts/clean_test_data.py
```

#### **Test Data Validation**
```bash
# Check data format consistency
python scripts/check_data_format.py

# Validate data relationships
python scripts/validate_data_relationships.py

# Check data quality metrics
python scripts/check_data_quality.py
```

## 🔍 **Debugging & Troubleshooting**

### **Common Issues & Solutions**

#### **Database Connection Issues**
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Restart PostgreSQL
brew services restart postgresql

# Check database connectivity
psql -h localhost -U username -d ai_agency -c "SELECT 1;"

# Reset database
dropdb ai_agency && createdb ai_agency
```

#### **Python Environment Issues**
```bash
# Check Python version
python --version

# Verify virtual environment
which python

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Check for conflicts
pip check
```

#### **Testing Framework Issues**
```bash
# Clear pytest cache
pytest --cache-clear

# Run with debug output
pytest -v --tb=long

# Check test discovery
pytest --collect-only

# Run single test file
pytest tests/unit/test_memory.py -v
```

### **Debugging Tools**

#### **Python Debugging**
```python
# Add debug breakpoints
import pdb; pdb.set_trace()

# Use ipdb for better debugging
import ipdb; ipdb.set_trace()

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### **Performance Debugging**
```bash
# Profile specific functions
python -m cProfile -o profile.stats script.py

# Analyze profile results
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Memory profiling
python -m memory_profiler script.py
```

## 📈 **Monitoring & Reporting**

### **Test Execution Monitoring**

#### **Real-time Monitoring**
```bash
# Run tests with live output
pytest -v --tb=short

# Monitor test progress
pytest --durations=10

# Track test execution time
pytest --durations=0
```

#### **Test Results Reporting**
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Generate XML coverage report
pytest --cov=src --cov-report=xml

# Generate performance report
pytest --benchmark-only --benchmark-json=benchmark_results.json
```

### **Performance Monitoring**

#### **Performance Metrics**
- **Test Execution Time**: Total time for test suite execution
- **Memory Usage**: Peak memory consumption during testing
- **CPU Utilization**: CPU usage during test execution
- **Database Performance**: Query execution times and throughput

#### **Performance Thresholds**
```bash
# Set performance thresholds
pytest --benchmark-min-rounds=100 --benchmark-warmup=on

# Fail tests below performance threshold
pytest --benchmark-fail=0.1
```

## 🔄 **Continuous Integration**

### **CI/CD Pipeline Integration**

#### **GitHub Actions Configuration**
```yaml
name: Testing Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

#### **Pre-commit Hooks**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

## 🚀 **Advanced Testing Features**

### **Parallel Test Execution**

#### **Multi-process Testing**
```bash
# Run tests in parallel
pytest -n auto

# Specify number of processes
pytest -n 4

# Use specific worker type
pytest -n 4 --dist=worksteal
```

#### **Test Sharding**
```bash
# Split tests across shards
pytest --dist=loadfile --tx 4*popen//python=python3.12

# Run specific shard
pytest --dist=loadfile --tx 4*popen//python=python3.12 --dist=loadfile --tx 2*popen//python=python3.12
```

### **Custom Test Markers**

#### **Defining Custom Markers**
```python
# In conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
```

#### **Using Custom Markers**
```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    # This test will be marked as slow
    pass

@pytest.mark.integration
def test_integration_feature():
    # This test will be marked as integration
    pass

@pytest.mark.performance
def test_performance_metric():
    # This test will be marked as performance
    pass
```

## 📚 **Related Documentation**

### **Testing Logs**
- **[300_testing-methodology-log.md](300_testing-methodology-log.md)** - Testing strategies and methodologies
- **[300_retrieval-testing-results.md](300_retrieval-testing-results.md)** - Retrieval system testing
- **[300_memory-system-testing.md](300_memory-system-testing.md)** - Memory system testing
- **[300_integration-testing-results.md](300_integration-testing-results.md)** - Integration testing

### **Related Guides**
- **[400_06_memory-and-context-systems.md](../400_guides/400_06_memory-and-context-systems.md)** - Memory system architecture
- **[400_08_integrations-editor-and-models.md](../400_guides/400_08_integrations-editor-and-models.md)** - Integration patterns

## 🔄 **Maintenance & Updates**

### **Update Frequency**
- **Infrastructure Changes**: Update immediately when infrastructure changes
- **Tool Updates**: Update when tools or dependencies are updated
- **Configuration Changes**: Update when configuration files change
- **Process Changes**: Update when testing processes evolve

### **Quality Gates**
- **Accuracy**: All setup instructions must be tested and verified
- **Completeness**: No critical setup steps should be missing
- **Reproducibility**: All instructions must lead to working environments
- **Maintenance**: Instructions must be kept current with system changes

---

**Last Updated**: [Date]
**Next Review**: [Date + 1 month]
**Infrastructure Version**: [Current version]
**Maintainer**: [Your name/team]
