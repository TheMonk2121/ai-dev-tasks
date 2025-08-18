# B-103 Implementation Plan: Repo Layout Normalization

## 🎯 **Status**: 🚀 **READY FOR EXECUTION** - Phased Implementation

**Date**: 2025-08-16
**Priority**: P0 (Governance/Non-Negotiable)
**Constitutional Authority**: Article V - Governance & Repository Management

## 📋 **Implementation Strategy: Phased Commits with Rollback Safety**

### **Phase 1: Test Directory Consolidation**
**Commit**: `feat: consolidate test directories (B-103 Phase 1)`

**Scope:**
- OK Move `dspy-rag-system/tests/` → `tests/` (main directory)
- OK Update all test imports to use unified location
- OK Remove duplicate test directories
- OK Update pytest configuration to point to unified location

**Rollback Safety:**
- OK Git commit checkpoint after each directory move
- OK Test validation after each import update
- OK Backup of original test structure

**Validation:**
```bash
pytest tests/ --collect-only  # Verify all tests found
pytest tests/ -v              # Run all tests successfully
```

### **Phase 2: Configuration File Consolidation**
**Commit**: `feat: consolidate pyproject.toml configs (B-103 Phase 2)`

**Scope:**
- OK Audit all `pyproject.toml` files in repository
- OK Merge configurations into single authoritative file
- OK Remove duplicate/conflicting configurations
- OK Update all references to point to unified config

**Rollback Safety:**
- OK Backup all existing config files
- OK Validate configuration after merge
- OK Test all tools that depend on config (ruff, pytest, etc.)

**Validation:**
```bash
ruff check .                    # Verify linting works
pytest tests/                   # Verify testing works
python -m build                 # Verify build works
```

### **Phase 3: Import Resolution Strategy Unification**
**Commit**: `feat: unify import resolution strategy (B-103 Phase 3)`

**Scope:**
- OK Audit all import strategies across codebase
- OK Remove dead/archived import strategies (sys.path.append, redundant helpers)
- OK Enforce single-source `setup_imports.py` or `PYTHONPATH` config
- OK Update all files to use unified import approach

**Rollback Safety:**
- OK Backup all import-related files
- OK Test each module after import changes
- OK Validate all scripts and tools still work

**Validation:**
```bash
python -c "import sys; print('Python path:', sys.path)"  # Verify path setup
python scripts/process_tasks.py --help                   # Test core scripts
python dspy-rag-system/add_document.py --help           # Test dspy scripts
```

### **Phase 4: Governance Documentation & Validation**
**Commit**: `feat: add governance validation rules (B-103 Phase 4)`

**Scope:**
- OK Update `000_backlog.md` with `<!-- auto: governance -->` tags
- OK Add validator rule to enforce no duplicate configs
- OK Add validator rule to enforce no orphan test dirs
- OK Create governance compliance checker

**Rollback Safety:**
- OK Backup original backlog file
- OK Test validator rules before deployment
- OK Validate governance compliance

**Validation:**
```bash
python scripts/doc_coherence_validator.py --check governance
python scripts/validate_repo_layout.py
```

## 🎯 **Success Criteria**

### **Technical Success:**
- OK Single unified test directory (`tests/`)
- OK Single authoritative `pyproject.toml`
- OK Unified import resolution strategy
- OK All tests pass in consolidated structure
- OK All tools work with unified configuration

### **Governance Success:**
- OK Constitutional rule enforced
- OK Automatic P0 classification working
- OK Governance validation rules active
- OK No duplicate configs or orphan directories
- OK Self-documenting governance tags in backlog

## 🚨 **Risk Mitigation**

### **Rollback Strategy:**
- OK Each phase is a separate commit
- OK Git tags for each phase completion
- OK Backup of all original files
- OK Validation checkpoints after each phase

### **Testing Strategy:**
- OK Comprehensive test suite validation
- OK Import resolution testing
- OK Configuration validation
- OK Governance rule testing

## 📊 **Implementation Timeline**

**Phase 1**: Test Directory Consolidation (2 hours)
**Phase 2**: Configuration Consolidation (1.5 hours)
**Phase 3**: Import Strategy Unification (2.5 hours)
**Phase 4**: Governance Documentation (1 hour)

**Total Estimated Time**: 7 hours
**Risk Level**: Low (phased approach with rollback safety)

## 🚀 **Ready to Execute**

**Status**: OK **Implementation plan complete** - ready to begin Phase 1

**Next Action**: Execute Phase 1 - Test Directory Consolidation

---

**Constitutional Authority**: Article V - Governance & Repository Management
**Priority**: P0 (Non-negotiable prerequisite for feature work)
**Dependencies**: None (P0 items block others, not vice versa)
