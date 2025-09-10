# DSPy-RAG-System Deprecation Notice

## Overview
This directory contains the archived `dspy-rag-system` that was previously located at the project root.

## Archive Date
September 9, 2025

## Reason for Deprecation
The `dspy-rag-system` directory has been deprecated and archived because:

1. **Broken Imports**: Module imports were failing (`No module named 'dspy_rag_system'`)
2. **Legacy Architecture**: Built for DSPy 2.6.27, incompatible with current DSPy 3.0.1
3. **Redundant Functionality**: Main project has modern equivalents with better integration
4. **Pydantic Ecosystem**: Not compatible with current PydanticAI, Pydantic Evals, Logfire stack

## What's in Main Project Now
- **Database Resilience**: `src/common/db_dsn.py`, `src/utils/retry_wrapper.py`
- **Model Handling**: `src/agents/ollama_qa.py`, `src/agents/qa.py`
- **Quality Gates**: `src/retrieval/quality_gates.py`
- **Modern DSPy**: Integrated with PydanticAI, Pydantic Evals, Logfire
- **Better Architecture**: Cleaner separation of concerns

## Migration Guide
If you need functionality from this archive:

1. **Database Operations**: Use `src/common/db_dsn.py` and `src/utils/retry_wrapper.py`
2. **Model Handling**: Use `src/agents/ollama_qa.py` and `src/agents/qa.py`
3. **Quality Validation**: Use `src/retrieval/quality_gates.py`
4. **DSPy Integration**: Use the modern PydanticAI + DSPy 3.0.1 integration

## Files Archived
- `dspy-rag-system/src/` - All source modules
- `dspy-rag-system/` - Configuration and setup files
- All Python modules and utilities

## Recovery
If you need to recover specific functionality, check the main project's equivalent modules first. If not available, you can extract specific files from this archive and adapt them to the current architecture.

---
*This archive was created as part of the DSPy venv consolidation and Pydantic ecosystem upgrade.*
