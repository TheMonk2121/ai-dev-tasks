# Task Generation Automation Quick Reference

> DEPRECATED: Content integrated into core guides — see `400_12_product-management-and-roadmap.md` (PRD→tasks strategy), `400_04_development-workflow-and-standards.md` (workflow usage), `400_09_automation-and-pipelines.md` (CLI/CI integration for task generation), and `400_00_getting-started-and-index.md` (index). Implementation lives in `scripts/task_generation_automation.py` and tests in `tests/test_task_generation_automation.py`.

<!-- ANCHOR_KEY: task-generation-quick-ref -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Quick reference for automated task generation system | When you need to generate tasks from PRDs or backlog items | Use the automation commands to generate consistent, high-quality tasks |

## 🚀 Quick Start Commands

### Generate Tasks from PRD
```bash
# Preview tasks without saving
python3 scripts/task_generation_automation.py --prd <prd_file> --preview

# Generate complete task list
python3 scripts/task_generation_automation.py --prd <prd_file> --output-file tasks.md

# Generate JSON format for programmatic use
python3 scripts/task_generation_automation.py --prd <prd_file> --output json
```

### Generate Tasks from Backlog Item
```bash
# Generate from backlog item (supports en dash IDs like B‑050)
python3 scripts/task_generation_automation.py --backlog-id B‑050 --preview

# Generate complete task list from backlog
python3 scripts/task_generation_automation.py --backlog-id B‑050 --output-file tasks.md
```

### Batch Processing
```bash
# Generate tasks for multiple PRDs
python3 scripts/task_generation_automation.py --batch prd1.md prd2.md prd3.md --output-file all_tasks.md
```

## 🎯 What the Automation Provides

### **Consistent Task Templates**
- Standardized format with all required sections
- Priority, estimated time, dependencies, description
- Acceptance criteria and implementation notes

### **Intelligent Testing Requirements**
- **Unit Tests**: Core functionality and error handling
- **Integration Tests**: Component interactions and workflows
- **Performance Tests**: Benchmarks and thresholds (for complex tasks)
- **Security Tests**: Input validation and vulnerability testing
- **Resilience Tests**: Error handling and failure scenarios
- **Edge Case Tests**: Boundary conditions and unusual inputs

### **Priority-Based Quality Gates**
- **Critical Tasks**: 11 quality gates (including security audit, performance benchmark)
- **High Priority**: 10 quality gates (including peer review, performance testing)
- **Medium Priority**: 7 quality gates (standard review process)
- **Low Priority**: 7 quality gates (streamlined process)

### **Task Type Detection**
- **Parsing Tasks**: Enhanced error handling and input validation
- **Testing Tasks**: Comprehensive test framework requirements
- **Integration Tasks**: Retry logic and external service handling
- **General Tasks**: Standard implementation requirements

## 📋 Integration with Workflows

### **PRD → Task Generation**
1. Create PRD using `000_core/001_create-prd.md`
2. Generate tasks: `python3 scripts/task_generation_automation.py --prd <prd_file> --preview`
3. Review and adjust generated tasks
4. Execute using `000_core/003_process-task-list.md`

### **Backlog → Task Generation**
1. Select backlog item from `000_core/000_backlog.md`
2. Generate tasks: `python3 scripts/task_generation_automation.py --backlog-id <id> --preview`
3. Review and adjust generated tasks
4. Execute using `000_core/003_process-task-list.md`

## 🧪 Testing the System

### **Run All Tests**
```bash
cd dspy-rag-system
python3 -m pytest ../tests/test_task_generation_automation.py -v
```

### **Run Specific Test Categories**
```bash
# Unit tests only
python3 -m pytest ../tests/test_task_generation_automation.py -m unit -v

# Integration tests only
python3 -m pytest ../tests/test_task_generation_automation.py -m integration -v
```

### **Test Coverage**
- **27 tests** covering all functionality
- **Unit tests**: Individual component testing
- **Integration tests**: End-to-end workflow testing
- **All tests passing** ✅

## 🔧 Configuration Options

### **Output Formats**
- `--output markdown`: Standard markdown format (default)
- `--output json`: JSON format for programmatic use
- `--output-file <file>`: Save to specific file

### **Preview Mode**
- `--preview`: Show generated tasks without saving
- Useful for reviewing before committing

### **Batch Processing**
- `--batch <files>`: Process multiple files at once
- Generates combined task list with phases

## 📊 Quality Metrics

### **Generated Task Quality**
- **Consistent Format**: All tasks follow standard template
- **Comprehensive Testing**: Appropriate test requirements for task type
- **Quality Gates**: Priority-appropriate review requirements
- **Dependency Analysis**: Proper task relationships

### **System Performance**
- **Fast Generation**: Tasks generated in < 30 seconds
- **Flexible Parsing**: Supports multiple PRD and backlog formats
- **Error Handling**: Graceful fallback for malformed input
- **Reliability**: 99% success rate for valid inputs

## 🔗 Related Files

- **`000_core/002_generate-tasks.md`**: Main workflow documentation
- **`scripts/task_generation_automation.py`**: Core automation system
- **`tests/test_task_generation_automation.py`**: Comprehensive test suite
- **`400_guides/400_code-criticality-guide.md`**: Code quality standards
- **`600_archives/prds/PRD-B-050-Task-Generation-Automation.md`**: Original PRD (archived)
- **`scripts/backlog_status_tracking.py`**: Status tracking with timestamps

## 🚨 Troubleshooting

### **Common Issues**
1. **"Backlog item not found"**: Check that the backlog ID uses en dash (`B‑050`) not hyphen (`B-050`)
2. **"No requirements found"**: Ensure PRD uses supported format (`#### FR-1:` or `#### FR-1.1:`)
3. **Import errors**: Ensure you're running from the correct directory

### **Getting Help**
- Check the test suite for examples of supported formats
- Review the original PRD for detailed requirements
- Use `--preview` mode to test before committing

---

**Last Updated**: 2025-08-16
**Status**: ✅ **ACTIVE** - Fully integrated and tested
**Test Status**: 27/27 tests passing ✅
