# DSPy Venv Archive

## Overview
This directory contains the archived DSPy virtual environment that was previously located at `dspy-rag-system/.venv`.

## Archive Date
September 9, 2025

## Reason for Archive
The DSPy venv has been deprecated and consolidated into the main project environment because:

1. **Outdated versions**: DSPy 2.6.27 vs 3.0.1 in main project
2. **Incompatible PyTorch**: 2.8.0 vs 2.3.1 compatibility issues
3. **Missing Pydantic ecosystem**: No PydanticAI, Pydantic Evals, Logfire
4. **Redundant**: Main project has everything needed

## What's in Main Project Now
- **DSPy**: 3.0.1 (newer version)
- **PyTorch**: 2.3.1 (stable, compatible version)
- **Transformers**: 4.56.1 (newer version)
- **Pydantic Ecosystem**: Full modern stack (PydanticAI, Pydantic Evals, Logfire)

## Usage
All DSPy work now uses the main project environment (`.venv`). The hybrid integration script handles environment detection and uses the appropriate DSPy imports from the main project.

## Recovery
If needed, this venv can be restored by moving it back to `dspy-rag-system/.venv`, but it's recommended to use the main project environment instead.
