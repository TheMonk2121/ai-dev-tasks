# DSPy RAG System Tests

This directory contains all test files for the DSPy RAG system.

## Test Files

- `test_document_processor.py` - Tests for document processing and chunking
- `test_enhanced_rag_system.py` - Tests for the enhanced RAG system with DSPy integration
- `test_fast_path.py` - Tests for fast-path bypass functionality
- `test_logger.py` - Tests for logging functionality
- `test_metadata_extractor.py` - Tests for metadata extraction and categorization
- `test_rag_system.py` - Tests for the basic RAG system
- `test_retry_policy.py` - Tests for retry wrapper and error handling (C-2 completed)
- `test_timeout_config.py` - Tests for global timeout configuration (C-3 completed)
- `test_tokenizer.py` - Tests for token-aware text chunking
- `test_vector_store.py` - Tests for vector storage and search
- `test_watch_folder.py` - Tests for file watching and processing

## Running Tests

### Run All Tests
```bash
# From the dspy-rag-system directory
python -m pytest tests/

# Or with more detail
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Files
```bash
# Test just the RAG system
python -m pytest tests/test_rag_system.py -v

# Test just the enhanced RAG system
python -m pytest tests/test_enhanced_rag_system.py -v

# Test just the document processor
python -m pytest tests/test_document_processor.py -v
```

### Run Tests with Database
```bash
# Tests that require PostgreSQL
python -m pytest tests/test_vector_store.py -v

# Tests that require Ollama/Mistral
python -m pytest tests/test_enhanced_rag_system.py -v
```

## Test Categories

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

## Test Requirements

- **pytest** - Test framework
- **PostgreSQL** - For vector store tests
- **Ollama/Mistral** - For RAG system tests
- **pytest-cov** - For coverage reporting (the execution engine)

## Notes

- Some tests require external services (PostgreSQL, Ollama)
- Tests are designed to be run from the `dspy-rag-system` directory
- All tests use relative imports to access the `src` module 