<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->

python -m pytest tests/test_enhanced_rag_system.py -v

```

## Test Categories

<a id="tldr"></a>

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of Test Categories.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.


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

- **Optional local model runner** - For legacy/local RAG system tests (see archives)

- **pytest-cov** - For coverage reporting (the execution engine)

## Notes

- Some tests require external services (e.g., PostgreSQL)

- Tests are designed to be run from the `dspy-rag-system` directory

- All tests use relative imports to access the `src` module
