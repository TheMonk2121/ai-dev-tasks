<!-- ANCHOR_KEY: quick-reference -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

# ⚡ Quick Reference Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Quick commands and shortcuts for common tasks | Need a quick command reference or looking for shortcuts | Use the command that matches your task |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Quick reference maintained
- **Priority**: 🔥 Critical - Essential for productivity
- **Points**: 2 - Low complexity, high importance
- **Dependencies**: All 400_guides files
- **Next Steps**: Use commands for your specific task

## 🚀 **Essential Commands**

### **Environment Setup**
```bash
# Check virtual environment
python3 scripts/venv_manager.py --check

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python3 scripts/venv_manager.py --check
```

### **Memory Rehydration**
```bash
# Get context for any task
./scripts/memory_up.sh -q "your specific task description"

# Role-specific context
./scripts/memory_up.sh -r coder "implement authentication"
./scripts/memory_up.sh -r planner "project planning"
./scripts/memory_up.sh -r implementer "deployment strategy"
./scripts/memory_up.sh -r researcher "performance analysis"

# JSON output for programmatic access
./scripts/memory_up.sh -f json
```

### **Development Workflow**
```bash
# Start new feature
python3 scripts/single_doorway.py generate "feature description"

# Continue interrupted work
python3 scripts/single_doorway.py continue B-XXX

# Archive completed work
python3 scripts/single_doorway.py archive B-XXX

# Test workflow
python3 scripts/single_doorway.py test "test description"
```

### **Code Quality**
```bash
# Check code quality
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .

# Type checking
pyright .

# Run all quality checks
ruff check . && pyright . && pytest tests/ -v
```

### **Testing**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_specific.py -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run tests with markers
pytest tests/ -m "unit" -v
pytest tests/ -m "integration" -v
```

### **Database Operations**
```bash
# Check database sync
python3 scripts/database_sync_check.py

# Auto-update database
python3 scripts/database_sync_check.py --auto-update

# Apply database schema
python3 dspy-rag-system/scripts/apply_clean_slate_schema.py

# Check database health
python3 scripts/database_health_check.py
```

### **DSPy System**
```bash
# Start DSPy dashboard
python3 dspy-rag-system/src/dashboard.py

# Run DSPy tests
./dspy-rag-system/run_tests.sh

# Test DSPy integration
python3 dspy-rag-system/test_cursor_context_engineering.py
```

### **Context Management**
```bash
# Start context capture
python3 scripts/single_doorway.py scribe start

# Add manual notes
python3 scripts/single_doorway.py scribe append "note"

# Check scribe status
python3 scripts/single_doorway.py scribe status

# Generate summaries
python scripts/worklog_summarizer.py --backlog-id B-XXX
```

## 🔧 **Troubleshooting Commands**

### **Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv && python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Verify package installation
pip list | grep package_name

# Check for conflicts
python -m pip check
```

### **Database Issues**
```bash
# Check database connection
python3 scripts/database_sync_check.py

# Reset database
python3 dspy-rag-system/scripts/apply_clean_slate_schema.py

# Check database logs
python3 scripts/database_logs.py
```

### **Memory System Issues**
```bash
# Test memory rehydration
./scripts/memory_up.sh -q "test memory system"

# Check system health
python3 scripts/system_health_check.py

# Debug memory issues
python3 scripts/debug_memory_system.py
```

### **Code Issues**
```bash
# Check for merge conflicts
git grep -nE '^(<<<<<<<|=======|>>>>>>>)'

# Quick conflict check
python scripts/quick_conflict_check.py

# System health check
python scripts/system_health_check.py --deep
```

## 📊 **Monitoring Commands**

### **System Monitoring**
```bash
# Check system status
python3 scripts/system_status.py

# Monitor performance
python3 scripts/performance_monitor.py

# Check logs
python3 scripts/log_monitor.py

# Health check
python3 scripts/health_check.py
```

### **Deployment Monitoring**
```bash
# Check deployment status
python3 scripts/deployment_status.py

# Monitor deployment health
python3 scripts/monitor_deployment_health.py

# Check deployment logs
python3 scripts/deployment_logs.py
```

## 🛡️ **Security Commands**

### **Security Validation**
```bash
# Security scan
python3 scripts/security_scan.py --env production

# Vulnerability check
python3 scripts/vulnerability_check.py

# Security audit
python3 scripts/security_audit.py

# Test authentication
python3 scripts/test_authentication.py
```

### **Access Control**
```bash
# Generate JWT token
python3 scripts/generate_jwt.py --user user_123 --role developer

# Validate JWT token
python3 scripts/validate_jwt.py --token your-jwt-token

# Check permissions
python3 scripts/check_permissions.py --user user_123 --resource /api/v1/ai/generate
```

## 📈 **Performance Commands**

### **Performance Analysis**
```bash
# Performance benchmark
python3 scripts/performance_benchmark.py

# Memory profiler
python3 scripts/memory_profiler.py

# Database performance test
python3 scripts/database_performance_test.py

# Profile code performance
python -m cProfile -o profile.stats script.py
```

### **Optimization**
```bash
# Performance optimization
python3 scripts/performance_optimize.py

# Memory optimization
python3 scripts/memory_optimize.py

# Database optimization
python3 scripts/database_optimize.py
```

## 🔄 **Git Commands**

### **Basic Git Operations**
```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "descriptive message"

# Push changes
git push

# Pull latest changes
git pull
```

### **Git Workflow**
```bash
# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

## 📚 **Documentation Commands**

### **Documentation Management**
```bash
# Update memory context
python3 scripts/update_cursor_memory.py

# Generate documentation
python3 scripts/generate_docs.py

# Validate documentation
python3 scripts/validate_docs.py

# Check broken links
python3 scripts/check_broken_links.py
```

## 🎯 **Task-Specific Shortcuts**

### **I need to...**

#### **Start working on a feature**
```bash
./scripts/memory_up.sh -q "implement feature description"
python3 scripts/single_doorway.py generate "feature description"
```

#### **Debug an issue**
```bash
./scripts/memory_up.sh -q "debug specific issue"
python3 scripts/system_health_check.py
python3 scripts/debug_memory_system.py
```

#### **Deploy changes**
```bash
ruff check . && pyright . && pytest tests/ -v
python3 scripts/deploy_staging.py
python3 scripts/deploy_production.py
```

#### **Check system health**
```bash
python3 scripts/venv_manager.py --check
python3 scripts/database_sync_check.py
python3 scripts/system_health_check.py
```

#### **Get project context**
```bash
./scripts/memory_up.sh -q "current project status"
cat 000_core/000_backlog.md | head -50
```

## 📚 **Related Guides**

- **Getting Started**: `400_guides/400_getting-started.md`
- **Development Workflow**: `400_guides/400_development-workflow.md`
- **Deployment Operations**: `400_guides/400_deployment-operations.md`
- **Integration & Security**: `400_guides/400_integration-security.md`
- **Performance Optimization**: `400_guides/400_performance-optimization.md`

## 💡 **Pro Tips**

### **Command Aliases**
Add these to your shell profile for faster access:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias mem='./scripts/memory_up.sh'
alias dev='python3 scripts/single_doorway.py'
alias test='pytest tests/ -v'
alias quality='ruff check . && pyright .'
alias deploy='python3 scripts/deploy_staging.py'
```

### **Quick Context**
```bash
# Get context for any task in one command
mem -q "your task" && dev generate "your task"
```

### **Quality Gates**
```bash
# Run all quality checks before committing
quality && test && git add . && git commit -m "your message"
```

---

**This guide provides quick access to all essential commands. Use the task-specific shortcuts for common workflows.**
