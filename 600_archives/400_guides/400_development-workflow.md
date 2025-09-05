# 400_development-workflow
> DEPRECATED: Use `400_04_development-workflow-and-standards.md` for the canonical development workflow and standards.
## Auto Memory Rehydration (B-093)

Enable automatic memory rehydration when a Scribe session starts. This is feature-flagged and debounced per backlog ID.

- Environment:
  - `AUTO_REHYDRATE=1` to enable (default is disabled)
  - `REHYDRATE_MINUTES=10` debounce window in minutes
- Entry points:
  - Programmatic: `scripts.rehydration_integration.rehydrate_with_debounce(backlog_id, role, query)`
  - CLI: `python scripts/memory_rehydrate.py --role planner --query "current project status and core documentation"`
- Behavior:
  - Triggered on session registration in `scripts/session_registry.py`
  - Non-fatal on failure; emits metrics and logs
- Metrics:
  - `rehydrate_attempts_total`
  - `rehydrate_duration_seconds_{sum,count}`

<!-- ANCHOR_KEY: development-workflow -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["coder", "implementer", "researcher"] -->

# 🛡️ Development Workflow Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Complete development workflow from coding to testing to quality | Implementing features, debugging issues, or reviewing code | Follow the workflow stages for your specific task |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Development workflow maintained
- **Priority**: 🔥 Critical - Essential for code quality and development efficiency
- **Points**: 8 - High complexity, strategic importance
- **Dependencies**: 400_guides/400_getting-started.md, 400_guides/400_integration-security.md
- **Next Steps**: Follow workflow stages for your specific development task

## 🚀 Quick Start

### **Development Workflow Overview**

1. **Setup & Context**: Environment check and memory rehydration
2. **Planning**: Code analysis and design decisions
3. **Implementation**: Coding with best practices
4. **Testing**: Comprehensive testing strategy
5. **Quality**: Code review and quality gates
6. **Deployment**: Safe deployment practices

### CI Dry‑Run Signal on Pull Requests

Non‑blocking CI runs `ruff`, `pyright`, and `pytest` on `pull_request` to surface issues early without merge friction. See `.github/workflows/dry-run.yml`.

### **For Immediate Development Tasks:**

```bash
# 1. Setup environment
python3 scripts/venv_manager.py --check

# 2. Get context for your task
./scripts/memory_up.sh -q "implement feature description"

# 3. Start development workflow
python3 scripts/single_doorway.py generate "feature"
```

### **For Debugging Issues:**

```bash
# 1. Quick conflict check
python scripts/quick_conflict_check.py

# 2. Check merge markers
git grep -nE '^(<<<<<<<|=======|>>>>>>>)'

# 3. Validate dependencies
python -m pip check
```

## 📋 **Workflow Stages**

### **Stage 1: Setup & Context**

#### **Environment Setup**
```bash
# Check virtual environment
python3 scripts/venv_manager.py --check

# Verify dependencies
python -m pip check

# Check system health
python scripts/system_health_check.py
```

#### **Memory Rehydration**
```bash
# Get context for your specific task
./scripts/memory_up.sh -q "implement authentication system"

# For debugging
./scripts/memory_up.sh -q "debug database connection issue"

# For testing
./scripts/memory_up.sh -q "write tests for user management"
```

#### **Code Analysis**
- **Search existing patterns**: Look for similar implementations
- **Check critical files**: Review Tier 1 files that might be affected
- **Analyze dependencies**: Understand what your changes will impact

### **Stage 2: Planning**

#### **Code Criticality Assessment**
**Tier 1 (Critical) - Never break without a plan:**
- `scripts/venv_manager.py` - Virtual environment management
- `scripts/single_doorway.py` - Core workflow orchestration
- `scripts/process_tasks.py` - Task execution engine
- `scripts/state_manager.py` - State persistence
- `dspy-rag-system/src/dspy_modules/` - Core AI modules
- `dspy-rag-system/src/utils/memory_rehydrator.py` - Context assembly

**Tier 2 (High) - Production infrastructure:**
- `scripts/doc_coherence_validator.py` - Documentation validation
- `scripts/performance_benchmark.py` - Performance monitoring

**Tier 3 (Supporting) - Utilities and automation:**
- `scripts/auto_push_prompt.py` - Maintenance automation

#### **Design Decisions**
- **Function length**: Keep functions ≤ 50 lines
- **Code reuse**: Aim for 70% existing code, 30% new code
- **Test coverage**: Write tests for all new functionality
- **Integration points**: Identify affected components

### **Stage 3: Implementation**

#### **Coding Best Practices**

**Code Structure:**
```python
# ✅ Good: Clear function with single responsibility
def process_user_data(user_data: dict) -> dict:
    """Process user data and return validated result."""
    validated_data = validate_input(user_data)
    processed_result = transform_data(validated_data)
    return processed_result

# ❌ Bad: Function doing too much
def process_user_data(user_data: dict) -> dict:
    # 100+ lines of mixed validation, transformation, and side effects
    pass
```

**Error Handling:**
```python
# ✅ Good: Specific error handling
try:
    result = process_data(data)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    raise
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    # Implement retry logic
    raise

# ❌ Bad: Generic error handling
try:
    result = process_data(data)
except Exception as e:
    print(f"Error: {e}")
    raise
```

**Type Safety:**
```python
# ✅ Good: Type hints and validation
from typing import Dict, List, Optional
from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    email: str
    preferences: Optional[Dict[str, str]] = None

def process_user(user: UserData) -> Dict[str, str]:
    return {"status": "processed", "user_id": user.name}
```

#### **Development Commands**
```bash
# Start development session
python3 scripts/single_doorway.py generate "feature description"

# Check code quality
ruff check .

# Run type checking
pyright .

# Format code
ruff format .
```

### **Stage 4: Testing**

#### **Testing Strategy**

**Test-First Development (TDD):**
```python
# 1. Write test first
def test_user_authentication():
    user = User("test@example.com", "password123")
    assert user.authenticate("password123") == True
    assert user.authenticate("wrongpassword") == False

# 2. Implement functionality
class User:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def authenticate(self, password: str) -> bool:
        return self.password == password

# 3. Run tests
pytest tests/test_user.py -v
```

#### **Test Types**

**Unit Tests:**
```bash
# Run unit tests for specific module
pytest tests/test_user_management.py -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html
```

**Integration Tests:**
```bash
# Run integration tests
pytest tests/integration/ -v

# Test database integration
pytest tests/test_database_integration.py -v
```

**System Tests:**
```bash
# Run full system tests
./run_tests.sh --tiers 1 --kinds smoke

# Test complete workflow
python3 scripts/single_doorway.py test "complete feature workflow"

#### **Testing Commands**
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/ -m "unit" -v
pytest tests/ -m "integration" -v

# Run tests with markers
pytest tests/ --tiers 1 --kinds smoke

# Check test coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### **Stage 5: Quality**

#### **Code Review Checklist**
- [ ] **Function length**: All functions ≤ 50 lines
- [ ] **Type hints**: All functions have proper type annotations
- [ ] **Error handling**: Appropriate exception handling
- [ ] **Documentation**: Docstrings for all public functions
- [ ] **Tests**: Unit tests for all new functionality
- [ ] **Code reuse**: 70% existing patterns, 30% new code
- [ ] **Performance**: No obvious performance issues
- [ ] **Security**: No security vulnerabilities

#### **Quality Gates**
```bash
# Run all quality checks
ruff check . && pyright . && pytest tests/ -v

# Pre-commit validation
git add . && git commit -m "feature: implement user authentication"

# Continuous integration
python scripts/ci_quality_gates.py
```

#### **Performance Validation**
```bash
# Run performance benchmarks
python scripts/performance_benchmark.py

# Check memory usage
python scripts/memory_profiler.py

# Validate database performance
python scripts/database_performance_test.py
```

### **Stage 6: Deployment**

#### **Pre-Deployment Checklist**
- [ ] **All tests pass**: Unit, integration, and system tests
- [ ] **Quality gates pass**: Linting, type checking, security scans
- [ ] **Performance validated**: Benchmarks within acceptable ranges
- [ ] **Documentation updated**: Code comments and documentation current
- [ ] **Dependencies checked**: All dependencies compatible
- [ ] **Backup created**: System state backed up

#### **Deployment Commands**
```bash
# Validate deployment readiness
python scripts/deployment_validator.py

# Create deployment package
python scripts/create_deployment_package.py

# Deploy to staging
python scripts/deploy_staging.py

# Run post-deployment tests
python scripts/post_deployment_tests.py

# Deploy to production
python scripts/deploy_production.py
```

## 🔧 **Development Environment**

### **Required Dependencies**
```bash
# Core dependencies
psycopg2-binary==2.9.9  # Database connectivity
dspy==3.0.1            # Core AI framework
pytest==8.0.0          # Testing framework
ruff==0.3.0            # Code quality and formatting
pyright==1.1.350       # Type checking

# Development tools
pre-commit==3.6.0      # Git hooks
black==24.1.1          # Code formatting (backup)
mypy==1.8.0            # Type checking (backup)
```

### **Environment Setup**
```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

### **IDE Configuration**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

## 🚨 **Troubleshooting**

### **Common Issues**

**Virtual Environment Problems:**
```bash
# Check venv status
python3 scripts/venv_manager.py --check

# Recreate venv if needed
rm -rf venv && python3 -m venv venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Import Errors:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Verify package installation
pip list | grep package_name

# Check for conflicting packages
pip check
```

**Test Failures:**
```bash
# Run tests with verbose output
pytest tests/ -v -s

# Run specific failing test
pytest tests/test_specific.py::test_function -v -s

# Check test environment
python -c "import pytest; print(pytest.__version__)"
```

**Code Quality Issues:**
```bash
# Auto-fix ruff issues
ruff check . --fix

# Format code
ruff format .

# Check specific file
ruff check path/to/file.py
```

### **Performance Issues**
```bash
# Profile code performance
python -m cProfile -o profile.stats script.py

# Analyze memory usage
python scripts/memory_profiler.py

# Check database performance
python scripts/database_performance_test.py
```

## 📚 **Related Guides**

- **Getting Started**: `400_guides/400_getting-started.md`
- **Integration & Security**: `400_guides/400_integration-security.md`
- **Deployment Operations**: `400_guides/400_deployment-operations.md`
- **Testing & Debugging**: `400_guides/400_testing-debugging.md`

## 🔄 **Workflow Integration**

### **With AI Development Ecosystem**
```bash
# Start AI-assisted development
python3 scripts/single_doorway.py generate "feature description"

# Continue interrupted workflow
python3 scripts/single_doorway.py continue B-XXX

# Archive completed work
python3 scripts/single_doorway.py archive B-XXX
```

### **With Scribe Context Capture**
```bash
# Start automatic context capture
python3 scripts/single_doorway.py scribe start

# Add manual notes
python3 scripts/single_doorway.py scribe append "implementation note"

# Generate work summaries
python scripts/worklog_summarizer.py --backlog-id B-XXX
```

## Monitoring & Maintenance

- Run system monitor:

```bash
python3 scripts/system_monitor.py
```

- Health gate for CI (fails non-healthy):

```bash
python3 scripts/health_gate.py
```

- Run maintenance (db analyze + memory validation):

```bash
python3 scripts/maintenance.py
```

- Optional: install daily 3am maintenance via launchd (macOS):

```bash
python3 scripts/create_launchd_maintenance.py
```

See also `dspy-rag-system/src/monitoring/health_endpoints.py` for app endpoints and `scripts/monitoring_dashboard.py` for a simple dashboard.

---

**This guide provides a complete development workflow from initial setup through deployment. Follow the stages sequentially for your specific development task.**
