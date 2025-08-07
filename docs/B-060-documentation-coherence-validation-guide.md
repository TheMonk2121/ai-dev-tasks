# 📋 B-060 Documentation Coherence Validation System Guide

## 🎯 Overview

The Documentation Coherence Validation System (B-060) implements lightweight doc-linter with Cursor AI semantic checking for the AI development ecosystem. This system ensures documentation coherence through automated validation, cross-reference checking, and AI-enhanced semantic analysis.

## 🏗️ System Architecture

### **Core Components**

1. **Main Validator** (`scripts/doc_coherence_validator.py`)
   - Primary validation engine
   - Cross-reference validation
   - File naming convention checking
   - Backlog reference validation
   - Memory context coherence checking
   - Cursor AI semantic validation

2. **Pre-commit Hook** (`scripts/pre_commit_doc_validation.sh`)
   - Automatic validation before commits
   - Critical file change detection
   - Integration with git workflow

3. **Test Suite** (`tests/test_doc_coherence_validator.py`)
   - Comprehensive unit tests
   - Integration tests
   - Edge case coverage

### **Validation Tasks**

| Task | Purpose | Dependencies |
|------|---------|--------------|
| Cross-reference validation | Validates `<!-- --><!-- MODULE_REFERENCE: 400_few-shot-context-examples_memory_context_examples.md -->
<!-- MODULE_REFERENCE: 400_performance-optimization-guide_performance_metrics.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: 400_system-overview_system_architecture_macro_view.md -->
<!-- MODULE_REFERENCE: 400_system-overview_core_components_detailed_view.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
` comment patterns | None |
| File naming conventions | Checks three-digit prefix system | None |
| Backlog reference validation | Ensures backlog item references exist | `000_backlog.md` |
| Memory context coherence | Validates memory context consistency | `100_cursor-memory-context.md` |
| Cursor AI semantic validation | AI-enhanced coherence checking | Cursor AI availability |
| Validation report generation | Creates comprehensive reports | All previous tasks |

## 🚀 Quick Start

### **Basic Usage**

```bash
# Run validation in dry-run mode (default)
python scripts/doc_coherence_validator.py

# Run validation and make changes
python scripts/doc_coherence_validator.py --no-dry-run

# Check specific file only
python scripts/doc_coherence_validator.py --file 100_cursor-memory-context.md

# Check all files (not just priority files)
python scripts/doc_coherence_validator.py --check-all
```

### **Pre-commit Hook Setup**

```bash
# Install pre-commit hook
./scripts/pre_commit_doc_validation.sh --install

# Uninstall pre-commit hook
./scripts/pre_commit_doc_validation.sh --uninstall

# Manual pre-commit validation
./scripts/pre_commit_doc_validation.sh
```

### **Running Tests**

```bash
# Run all tests
python -m pytest tests/test_doc_coherence_validator.py -v

# Run specific test class
python -m pytest tests/test_doc_coherence_validator.py::TestDocCoherenceValidator -v

# Run with coverage
python -m pytest tests/test_doc_coherence_validator.py --cov=scripts.doc_coherence_validator
```

## 📋 Configuration

### **Priority Files**

The system validates these priority files by default:

```python
priority_files = {
    'memory_context': ['100_cursor-memory-context.md'],
    'system_overview': ['400_system-overview_advanced_features.md'],
    'backlog': ['000_backlog.md'],
    'project_overview': ['400_project-overview.md'],
    'context_priority': ['400_context-priority-guide.md']
}
```

### **Exclude Patterns**

Files matching these patterns are excluded from validation:

```python
exclude_patterns = [
    'venv/',
    'node_modules/',
    'docs/legacy/',
    '__pycache__/',
    '.git/',
    '999_repo-maintenance.md',
    'REPO_MAINTENANCE_SUMMARY.md',
    '600_archives/'
]
```

### **Validation Patterns**

The system uses these regex patterns for validation:

```python
# Cross-reference pattern: <!-- TYPE: target -->
cross_reference_pattern = re.compile(r'<!--\s*([A-Z_]+):\s*([^>]+)\s*-->')

# File reference pattern: `filename.md`
file_reference_pattern = re.compile(r'`([^`]+\.md)`')

# Backlog reference pattern: B‑XXX
backlog_reference_pattern = re.compile(r'B‑\d+')
```

## 🔧 Validation Tasks

### **Task 1: Cross-Reference Validation**

Validates all `<!-- -->` comment patterns in documentation files.

**Checks:**
- File existence for referenced targets
- Markdown file references
- Cross-reference syntax

**Example:**
```markdown
<!-- CONTEXT_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- BACKLOG_REFERENCE: 000_backlog.md -->
```

### **Task 2: File Naming Conventions**

Validates the three-digit prefix naming system.

**Rules:**
- Files must have three-digit prefix (e.g., `100_`, `400_`)
- Exceptions: `README.md`, `LICENSE.md`
- Descriptive names after prefix

**Valid Examples:**
- `100_cursor-memory-context.md`
- `400_system-overview_advanced_features.md`
- `000_backlog.md`

**Invalid Examples:**
- `invalid_file.md` (no prefix)
- `100.md` (no descriptive name)

### **Task 3: Backlog Reference Validation**

Ensures all backlog item references exist in the backlog file.

**Checks:**
- References to `B‑XXX` items
- Validates against `000_backlog.md`
- Reports invalid references

### **Task 4: Memory Context Coherence**

Validates memory context consistency with other documentation.

**Checks:**
- Current sprint references exist in backlog
- Architectural consistency with system overview
- Terminology consistency

### **Task 5: Cursor AI Semantic Validation**

Uses Cursor AI for semantic coherence checking.

**Features:**
- Internal consistency analysis
- Cross-reference validation
- Terminology consistency
- Completeness checking
- Clarity assessment

**Requirements:**
- Cursor AI must be available (`cursor` command)
- Falls back to basic validation if unavailable

### **Task 6: Validation Report Generation**

Creates comprehensive validation reports.

**Output:**
- JSON report in `docs/validation_report.json`
- Timestamp and validation results
- Errors and warnings summary
- Changes made during validation

## 🛠️ Advanced Usage

### **Custom Validation Rules**

You can extend the validator with custom rules:

```python
class CustomDocValidator(DocCoherenceValidator):
    def task_7_custom_validation(self) -> bool:
        """Custom validation task."""
        # Your custom validation logic
        return True
```

### **Integration with CI/CD**

Add to your CI pipeline:

```yaml
# .github/workflows/doc-validation.yml
name: Documentation Validation
on: [push, pull_request]
jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Run documentation validation
        run: python scripts/doc_coherence_validator.py --no-dry-run
```

### **Pre-commit Integration**

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: doc-coherence-validation
        name: Documentation Coherence Validation
        entry: python scripts/doc_coherence_validator.py --dry-run
        language: system
        files: \.md$
```

## 🔍 Troubleshooting

### **Common Issues**

#### **Cursor AI Not Available**
```
[WARNING] Cursor AI not available - using basic validation only
```

**Solution:** Install Cursor AI or run without semantic validation.

#### **Broken Cross-References**
```
[WARNING] Found 2 broken cross-references:
  100_cursor-memory-context.md -> 400_system-overview_advanced_features.md (File not found)
```

**Solution:** Fix the cross-reference or create the missing file.

#### **Naming Convention Issues**
```
[WARNING] Found 1 naming convention issues:
  invalid_file.md: Missing three-digit prefix
```

**Solution:** Rename file to follow three-digit prefix convention.

#### **Invalid Backlog References**
```
[WARNING] Found 1 invalid backlog references:
  memory_context.md: B-999 (Invalid backlog item reference)
```

**Solution:** Remove invalid reference or add item to backlog.

### **Debug Mode**

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

validator = DocCoherenceValidator(dry_run=True)
validator.run_all_validations()
```

### **Validation Report Analysis**

Check the validation report for detailed information:

```bash
# View validation report
cat docs/validation_report.json | jq '.'

# Check specific validation results
cat docs/validation_report.json | jq '.validation_results'
```

## 📊 Performance Considerations

### **Optimization Tips**

1. **Use `--file` for single file validation**
2. **Run in dry-run mode for testing**
3. **Exclude large directories in exclude_patterns**
4. **Use pre-commit hooks for automatic validation**

### **Memory Usage**

- **Small projects**: < 50MB memory usage
- **Large projects**: ~100MB memory usage
- **Cursor AI calls**: Additional memory per file

### **Execution Time**

- **Basic validation**: 1-5 seconds
- **Full validation**: 10-30 seconds
- **With Cursor AI**: 30-60 seconds per file

## 🔄 Maintenance

### **Regular Validation**

Run validation regularly to maintain coherence:

```bash
# Daily validation (add to cron)
0 9 * * * cd /path/to/project && python scripts/doc_coherence_validator.py --dry-run

# Pre-commit validation (automatic)
# Install pre-commit hook for automatic validation
```

### **Updating Validation Rules**

To add new validation rules:

1. Add new task method to `DocCoherenceValidator`
2. Update `run_all_validations()` method
3. Add corresponding tests
4. Update documentation

### **Monitoring Validation Health**

Track validation success over time:

```bash
# Check validation history
ls -la docs/validation_report.json

# Analyze validation trends
python -c "
import json
with open('docs/validation_report.json') as f:
    data = json.load(f)
    print(f'Files checked: {data[\"files_checked\"]}')
    print(f'Errors: {len(data[\"errors\"])}')
    print(f'Warnings: {len(data[\"warnings\"])}')
"
```

## 📚 Related Documentation

- **B-052-a**: Safety & Lint Tests (dependency)
- **B-061**: Memory Context Auto-Update Helper (dependent)
- **B-062**: Context Priority Guide Auto-Generation (dependent)
- **B-063**: Documentation Recovery & Rollback System (dependent)
- **B-064**: Naming Convention Category Table (dependent)

## 🎯 Success Metrics

### **Validation Coverage**
- ✅ All priority files validated
- ✅ Cross-references checked
- ✅ Naming conventions enforced
- ✅ Backlog references validated
- ✅ Memory context coherence maintained

### **Performance Metrics**
- ⚡ Validation completes in < 30 seconds
- 📊 < 5% false positive rate
- 🔧 < 10% false negative rate
- 💾 < 100MB memory usage

### **Integration Metrics**
- 🔗 Pre-commit hooks working
- 🧪 Test suite passing
- 📋 Documentation complete
- 🛠️ Maintenance procedures established

---

**Implementation Status**: ✅ Complete  
**Last Updated**: 2024-08-07  
**Next Review**: Monthly review cycle
