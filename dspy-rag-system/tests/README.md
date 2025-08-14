<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MEMORY_CONTEXT: MEDIUM - Testing setup and execution guide -->
# Test Setup and Execution Guide

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Testing infrastructure setup and execution guide for DSPy RAG System | Setting up test environment or running comprehensive test suite | Install dependencies with `./install_test_dependencies.sh` then run `python tests/comprehensive_test_suite.py` |

## 🎯 Current Status

- **Status**: ✅ **ACTIVE** - Maintained and current
- **Priority**: 🔥 High - Testing infrastructure
- **Points**: 2 - Medium complexity, high importance
- **Dependencies**: `install_test_dependencies.sh`, `comprehensive_test_suite.py`
- **Next Steps**: Update when new test categories or dependencies are added

## 📋 Test Categories

### Unit Tests

- `test_fast_path.py` - Unit tests for fast-path detection and routing
- `test_logger.py` - Pure unit tests, no external dependencies
- `test_retry_policy.py` - Unit tests for retry wrapper and error handling (C-2 completed)
- `test_tokenizer.py` - Unit tests for text processing
- `test_metadata_extractor.py` - Unit tests for metadata extraction

### Integration Tests

- `test_document_processor.py` - Tests document processing pipeline
- `test_rag_system.py` - Tests RAG system integration
- `test_enhanced_rag_system.py` - Tests enhanced DSPy RAG system
- `test_vector_store.py` - Tests database integration
- `test_watch_folder.py` - Tests file system integration

## 🚀 Quick Setup

### Automated Installation

```bash
# From the dspy-rag-system directory
./install_test_dependencies.sh
```

### Manual Installation

```bash
pip install psutil>=5.9.0 coverage pytest pytest-cov pytest-mock bandit
```

## 📊 Test Requirements

| Dependency | Purpose | Version |
|---|---|---|
| **pytest** | Test framework | 7.4.3+ |
| **PostgreSQL** | Vector store tests | Latest |
| **psutil** | System metrics in performance tests | 5.9.0+ |
| **pytest-cov** | Coverage reporting | 4.1.0+ |
| **bandit** | Security scanning | 1.7.5+ |

## 🔧 Comprehensive Test Suite

The comprehensive test suite (`comprehensive_test_suite.py`) provides advanced testing capabilities:

| Category | Purpose | Examples |
|---|---|---|
| **Unit Tests** | Fast, isolated tests | `test_logger.py`, `test_tokenizer.py` |
| **Integration Tests** | System component integration | `test_rag_system.py`, `test_vector_store.py` |
| **E2E Tests** | End-to-end workflow tests | `test_mission_dashboard.py` |
| **Performance Tests** | System performance benchmarks | Response time, memory usage, CPU metrics |
| **Security Tests** | Security scanning and validation | Bandit scans, input validation |

### Execution Commands

```bash
# Run complete test suite
python tests/comprehensive_test_suite.py

# Run specific categories
python tests/comprehensive_test_suite.py --categories unit integration

# Run with custom configuration
python tests/comprehensive_test_suite.py --workers 8 --timeout 600
```

## 📝 Important Notes

- **External Services**: Some tests require PostgreSQL for vector store functionality
- **Working Directory**: Tests are designed to be run from the `dspy-rag-system` directory
- **Import Strategy**: All tests use relative imports to access the `src` module
- **Performance**: Performance tests may take several minutes to complete
- **Security**: Security scans require network access for vulnerability databases

## 🔗 Related Files

- **Installation Script**: `install_test_dependencies.sh` - Automated dependency installation
- **Comprehensive Suite**: `comprehensive_test_suite.py` - Advanced testing framework
- **Test Configuration**: `pytest.ini` - Pytest configuration and settings
- **Coverage Reports**: `htmlcov/` - Generated coverage reports

## 🗒️ Change Log

- **v1.1**: Added comprehensive test suite documentation and dependency management
- **v1.0**: Initial test categories and basic setup instructions
