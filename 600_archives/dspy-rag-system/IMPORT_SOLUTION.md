# Import Error Solution for DSPy RAG System

> DEPRECATED: Content integrated into core guides — see `400_guides/400_04_development-workflow-and-standards.md` (project structure, import patterns), `400_guides/400_05_coding-and-prompting-standards.md` (linters/type-checking conventions), `400_guides/400_09_automation-and-pipelines.md` (CI config for Pyright/Ruff), and `400_guides/400_00_getting-started-and-index.md` (index). Implementation remains in `dspy-rag-system/` (e.g., `setup_imports.py`).

## 🎯 **Problem Summary**

The DSPy RAG system was experiencing consistent import errors (`reportmissingimports`) across multiple scripts, particularly when trying to import modules from the `src/utils` directory.

### **Root Causes Identified:**

1. **Inconsistent Path Resolution**: Different scripts used different approaches to add the `src` directory to `sys.path`
2. **Missing Package Structure**: The `src` directory wasn't properly configured as a Python package
3. **Linter Configuration**: PyRight/Ruff couldn't resolve relative imports properly
4. **Runtime vs Development Imports**: Scripts worked at runtime but failed during development/linting

## 🛠️ **Solution Implemented**

### **1. Centralized Import Utility (`setup_imports.py`)**

Created a centralized utility that handles all import path resolution:

```python
# Key Features:
- Automatic project root detection
- Consistent path resolution across all scripts
- Error handling and validation
- Common import caching
```

### **2. Updated Script Pattern**

All scripts now follow this consistent pattern:

```python
#!/usr/bin/env python3

import sys
# Import the centralized import utility
try:
    from setup_imports import setup_dspy_imports, get_common_imports
except ImportError:
    # Fallback: try to import directly
    sys.path.insert(0, "src")
    from setup_imports import setup_dspy_imports, get_common_imports

# Setup imports
if not setup_dspy_imports():
    print("❌ Error: Could not setup DSPy import paths")
    sys.exit(1)

# Get common imports
try:
    imports = get_common_imports()
    extract_anchor_metadata = imports['extract_anchor_metadata']
    extract_anchor_metadata_from_file = imports['extract_anchor_metadata_from_file']
except KeyError as e:
    print(f"❌ Error: Missing required import: {e}")
    sys.exit(1)
```

### **3. Updated Linter Configuration**

Enhanced `pyproject.toml` with proper linter settings:

```toml
[tool.pyright]
pythonVersion = "3.12"
pythonPlatform = "Darwin"
venvPath = ".."
venv = "venv"
extraPaths = ["src", "../.venv/lib/python3.*/site-packages"]
include = ["src", "*.py"]
exclude = ["venv", "600_archives", "**/__pycache__", ".pytest_cache", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]  # Line too long - handled by black

[tool.ruff.lint.per-file-ignores]
"setup_imports.py" = ["E501"]
"add_chunks_to_existing.py" = ["E501"]
```

## 📋 **Files Updated**

### **New Files:**
- `setup_imports.py` - Centralized import utility
- `IMPORT_SOLUTION.md` - This documentation

### **Updated Files:**
- `add_chunks_to_existing.py` - Updated to use new import pattern
- `pyproject.toml` - Enhanced linter configuration

## 🧪 **Testing the Solution**

### **1. Test Import Setup:**
```bash
cd dspy-rag-system
python3 setup_imports.py
```

**Expected Output:**
```
🧪 Testing DSPy RAG System Import Setup
✅ Import paths setup successful
✅ All required imports available
✅ Common imports loaded: ['extract_anchor_metadata', 'extract_anchor_metadata_from_file', 'get_database_manager', 'setup_logger', 'get_logger']
```

### **2. Test Script Execution:**
```bash
python3 add_chunks_to_existing.py
```

**Expected Output:**
```
🚀 Starting Chunk Addition to Existing Documents
📄 Processing: ../100_memory/100_cursor-memory-context.md
   Found anchor metadata: {'anchor_key': 'tldr', 'anchor_priority': 0, 'role_pins': ['planner', 'implementer', 'researcher']}
   ...
🎉 Summary: 4/4 documents updated successfully
```

## 🔧 **How to Apply to Other Scripts**

### **Step 1: Update Import Section**
Replace the existing import section with:

```python
# Import the centralized import utility
try:
    from setup_imports import setup_dspy_imports, get_common_imports
except ImportError:
    # Fallback: try to import directly
    sys.path.insert(0, "src")
    from setup_imports import setup_dspy_imports, get_common_imports

# Setup imports
if not setup_dspy_imports():
    print("❌ Error: Could not setup DSPy import paths")
    sys.exit(1)
```

### **Step 2: Get Required Imports**
```python
# Get common imports
try:
    imports = get_common_imports()
    # Extract the functions you need
    function_name = imports['function_name']
except KeyError as e:
    print(f"❌ Error: Missing required import: {e}")
    sys.exit(1)
```

### **Step 3: Add to Linter Ignores (if needed)**
If the script has long lines, add to `pyproject.toml`:

```toml
[tool.ruff.lint.per-file-ignores]
"your_script.py" = ["E501"]
```

## 🎉 **Benefits Achieved**

1. **✅ Consistent Imports**: All scripts now use the same import pattern
2. **✅ Error Handling**: Proper error messages when imports fail
3. **✅ Linter Compatibility**: PyRight and Ruff can now resolve imports
4. **✅ Runtime Reliability**: Scripts work consistently across different environments
5. **✅ Maintainability**: Centralized import logic is easy to update
6. **✅ Fallback Support**: Graceful degradation if import utility fails

## 🚀 **Next Steps**

1. **Apply to All Scripts**: Update remaining scripts to use the new import pattern
2. **Add to CI/CD**: Include import validation in automated testing
3. **Documentation**: Update all script documentation to reflect new import pattern
4. **Training**: Ensure team members understand the new import approach

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"Could not setup DSPy import paths"**
   - Ensure you're running from the `dspy-rag-system` directory
   - Check that `src/utils/anchor_metadata_parser.py` exists

2. **"Missing required import"**
   - Check that the function exists in `get_common_imports()`
   - Verify the module is properly installed

3. **Linter still shows errors**
   - Restart your IDE/editor
   - Check that `pyproject.toml` is properly configured
   - Ensure you're using the correct Python interpreter

### **Debug Mode:**
```python
# Add to any script for debugging
import sys
print("Python path:", sys.path)
print("Current directory:", os.getcwd())
```

This solution provides a robust, maintainable approach to handling imports across the entire DSPy RAG system while ensuring compatibility with both development tools and runtime execution.
