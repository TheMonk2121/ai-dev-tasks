# Virtual Environment Manager

## Overview

The Virtual Environment Manager ensures your project's virtual environment is properly activated and working before running any scripts. This solves the common issue where scripts fail because they can't find required dependencies.

## Files

- `scripts/venv_manager.py` - Core venv management functionality
- `scripts/run_workflow.py` - Simple wrapper for running workflows with venv checks
- Integration in `scripts/cursor_memory_rehydrate.py` and `scripts/single_doorway.py`

## Usage

### Check Venv Status
```bash
python3 scripts/venv_manager.py --check
```

### Activate Venv
```bash
python3 scripts/venv_manager.py --activate
```

### Show Venv Information
```bash
python3 scripts/venv_manager.py --info
```

### Validate Dependencies
```bash
python3 scripts/venv_manager.py --validate
```

### Run Workflow with Venv Check
```bash
# Instead of: python3 scripts/single_doorway.py generate "feature"
python3 scripts/run_workflow.py generate "feature"
```

## Integration

The venv manager is automatically integrated into:

1. **Memory Rehydrator** - Ensures venv is active before importing modules
2. **Single Doorway** - Uses venv Python for all subprocess calls
3. **Workflow Runner** - Checks venv before running any workflow

## Required Dependencies

The venv manager checks for these essential packages:
- `psycopg2` - Database connectivity
- `dspy` - Core AI framework
- `pytest` - Testing framework
- `ruff` - Code quality

## Benefits

1. **Automatic Detection** - No need to manually activate venv
2. **Dependency Validation** - Ensures all required packages are installed
3. **Clear Error Messages** - Tells you exactly what's missing
4. **Seamless Integration** - Works with existing workflow scripts

## Troubleshooting

### Venv Not Found
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Missing Dependencies
```bash
source .venv/bin/activate
pip install psycopg2-binary dspy pytest ruff
```

### Import Errors
The venv manager automatically handles Python path issues and ensures the correct Python executable is used.
