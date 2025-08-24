# Archive Content Extraction Plan

## Overview
This document outlines the valuable content that needs to be extracted from archived branches before they can be considered fully archived.

## Archive Branches Analysis

### 1. `archive/cleanup-bracketed-placeholders`
**Status**: 175 valuable commits
**Critical Content to Extract**:

#### A. Error Reduction Patterns (25.9% reduction achieved)
- **Commit**: `9ec5b32d` - eliminate 1121 template-propagating errors
- **Commit**: `258ec3e1` - eliminate 98.4% of import and formatting errors
- **Commit**: `941cbae6` - eliminate final F401 unused import error
- **Commit**: `5d253d0f` - eliminate all UP035 typing import errors

#### B. Unicode Character Safety System
- **Commit**: `452ff2f5` - add critical code copying safety rule to prevent Unicode issues
- **Commit**: `950a8363` - re-apply Unicode character fixes after pattern analysis
- **Commit**: `72cd13ee` - document Unicode character reintroduction pattern
- **Commit**: `fc5fae3d` - add Unicode character and template safety best practices

#### C. Code Quality Governance
- **Commit**: `2724a54c` - integrate code quality into validator as governance aggregator
- **Commit**: `301a5468` - add error reduction governance to cursor rules and governance runbook
- **Commit**: `3ec6aaee` - implement systematic error reduction with lessons learned
- **Commit**: `aa7d2370` - implement efficiency scoring system for bug and feature tests

#### D. Bracketed Placeholder Enforcement
- **Commit**: `bdb8ed1b` - add bracketed placeholder enforcement system
- **Commit**: `68475cf9` - clean up existing bracketed placeholders

#### E. Global Bug-Fix Playbook
- **Commit**: `a7ec0727` - implement B-182 Global Bug-Fix Playbook MVP
- **Commit**: `9b782c6f` - update documentation to include B-182 bug-fix playbook

### 2. `archive/chore-enable-docs-gates`
**Status**: Documentation and governance improvements
**Critical Content to Extract**:

#### A. Backlog Additions
- **Commit**: `315f1fb5` - add B-190 and B-191 to backlog for bracketed placeholder work

#### B. Governance Enhancements
- **Commit**: `4f73f3a0` - add execution-ready items for CODEOWNERS, no-verify policy, ledger expiry, dep pinning/SCA/SAST, and vector-store perf gates

### 3. `archive/feat-docs-relationship-analysis`
**Status**: Documentation improvements
**Content**: Documentation relationship analysis and broken link validation

### 4. `archive/feat-doorway-3cmd`
**Status**: Doorway system enhancements
**Content**: 3-command workflow improvements

### 5. `archive/feat-validator-multirep-xref`
**Status**: Advanced validator features
**Content**: Multi-repo cross-reference capabilities

## Extraction Priority

### Phase 1: Critical Safety & Quality (Immediate)
1. **Unicode Character Safety System** - Prevents critical bugs
2. **Error Reduction Patterns** - 25.9% improvement achieved
3. **Code Quality Governance** - Systematic quality improvements

### Phase 2: Process Improvements (Next Sprint)
1. **Bracketed Placeholder Enforcement** - Code quality system
2. **Global Bug-Fix Playbook** - Systematic debugging approach
3. **Backlog Additions** - B-190, B-191 for future work

### Phase 3: Advanced Features (Future)
1. **Multi-repo Cross-references** - Advanced validator features
2. **Documentation Relationship Analysis** - Enhanced documentation
3. **Doorway System Enhancements** - Workflow improvements

## Implementation Strategy

### Option 1: Cherry-Pick Critical Commits
- Extract specific commits with valuable code changes
- Apply to main branch with conflict resolution
- Preserve commit history and attribution

### Option 2: Manual Implementation
- Read the valuable patterns and implement manually
- Focus on the patterns rather than exact code
- Adapt to current codebase structure

### Option 3: Hybrid Approach
- Cherry-pick simple, non-conflicting improvements
- Manually implement complex patterns
- Document extracted patterns for future reference

## Next Steps

1. **Immediate**: Extract Unicode safety and error reduction patterns
2. **This Week**: Implement code quality governance system
3. **Next Sprint**: Add bracketed placeholder enforcement
4. **Future**: Consider advanced features based on priority

## Risk Assessment

**Low Risk**: Unicode safety, error reduction patterns
**Medium Risk**: Code quality governance (may conflict with current system)
**High Risk**: Advanced validator features (complex integration)

## Success Criteria

- [ ] Unicode character safety system implemented
- [ ] Error reduction patterns documented and applied
- [ ] Code quality governance integrated
- [ ] Bracketed placeholder enforcement working
- [ ] All valuable patterns documented for future reference
