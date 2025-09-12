# 🎯 Gold Cases Excellence Plan - Prioritized Execution

**Date**: September 11, 2025  
**Status**: Ready for Execution  
**Goal**: Transform gold cases from current state to "Excellent" status

## 📊 Current State Analysis

- **Total Cases**: 121
- **Critical Issues**: 38 cases with unclear phrasing
- **File Accuracy**: 100% (all files exist and are properly referenced)
- **Content Relevance**: 85% (some cases need better file targeting)

## 🚀 Prioritized Execution Plan

### **Phase 1: Critical Fixes (P0 - Immediate)**
**Time**: 1-2 hours | **Impact**: High | **Effort**: Low

#### 1.1 Fix Unclear Phrasing (30 minutes)
- **Target**: 38 cases with grammar issues
- **Script**: `scripts/gold_cases_improvement/fix_unclear_phrasing.py`
- **Examples**:
  - `"What show the dspy development context tl;dr.?"` → `"Show me the DSPy development context TL;DR"`
  - `"What give the high-level getting started index.?"` → `"Give me the high-level getting started index"`
  - `"What point me to memory-related guides..."` → `"Point me to memory-related guides..."`

#### 1.2 Fix Short Queries (15 minutes)
- **Target**: Cases with queries < 10 characters
- **Script**: `scripts/gold_cases_improvement/fix_short_queries.py`
- **Examples**:
  - `"DSPy"` → `"What is DSPy and how is it used in this project?"`

**Phase 1 Success Criteria**: 0 unclear phrasing issues, 0 short queries

---

### **Phase 2: Quality Improvements (P1 - High Priority)**
**Time**: 2-3 hours | **Impact**: High | **Effort**: Medium

#### 2.1 Diversify Query Patterns (1 hour)
- **Target**: 20+ repetitive "What is the main purpose of..." queries
- **Script**: `scripts/gold_cases_improvement/diversify_query_patterns.py`
- **Examples**:
  - `"What is the main purpose of 400_09_ai-frameworks-dspy.md?"` → `"How do I integrate DSPy into my project?"`
  - `"What is the main purpose of 000_backlog.md?"` → `"How do I manage project priorities and backlog items?"`
  - `"What is the main purpose of 400_11_performance-optimization.md?"` → `"What are the RAGChecker performance metrics and how do I optimize them?"`

#### 2.2 Improve Content Relevance (45 minutes)
- **Target**: Cases with overly broad glob patterns
- **Script**: `scripts/gold_cases_improvement/improve_content_relevance.py`
- **Examples**:
  - Add specific file references for database queries
  - Add MCP-specific files for MCP tool queries
  - Add memory-specific files for memory queries

#### 2.3 Refine Glob Patterns (30 minutes)
- **Target**: Cases using `**/*.md` pattern
- **Script**: `scripts/gold_cases_improvement/refine_glob_patterns.py`
- **Examples**:
  - `**/*.md` → `400_guides/*.md` (for guide queries)
  - `**/*.md` → `100_memory/*.md` (for memory queries)
  - `**/*.md` → `000_core/*.md` (for core workflow queries)

**Phase 2 Success Criteria**: Varied query patterns, specific file references, targeted glob patterns

---

### **Phase 3: Enhancement & Optimization (P2 - Medium Priority)**
**Time**: 3-4 hours | **Impact**: Medium | **Effort**: High

#### 3.1 Add Missing File References (1 hour)
- **Target**: Cases 100-121 using only glob patterns
- **Script**: `scripts/gold_cases_improvement/add_specific_file_references.py`
- **Examples**:
  - Database queries → Add specific SQL files
  - Script queries → Add specific Python files
  - Configuration queries → Add specific config files

#### 3.2 Improve Query Specificity (1.5 hours)
- **Target**: Generic queries that could be more specific
- **Script**: `scripts/gold_cases_improvement/improve_query_specificity.py`
- **Examples**:
  - `"How does the database schema work?"` → `"How do I create and manage database tables with pgvector?"`
  - `"What MCP tools are available?"` → `"How do I use the MCP server tools for project context and evaluation?"`
  - `"How do I run the evals?"` → `"How do I run the RAGChecker evaluation system with proper configuration?"`

#### 3.3 Add Negative Test Cases (30 minutes)
- **Target**: Cases 66-68 (negative test cases)
- **Script**: `scripts/gold_cases_improvement/validate_negative_cases.py`
- **Examples**:
  - Verify "Not in context" answers are properly configured
  - Ensure negative cases test appropriate scenarios

**Phase 3 Success Criteria**: Specific file references, actionable queries, proper negative testing

---

### **Phase 4: Excellence & Polish (P3 - Low Priority)**
**Time**: 2-3 hours | **Impact**: Low | **Effort**: Medium

#### 4.1 Add Comprehensive Test Coverage (1 hour)
- **Target**: Ensure all major system components are covered
- **Script**: `scripts/gold_cases_improvement/add_comprehensive_coverage.py`
- **Examples**:
  - Add cases for new features
  - Add edge cases for complex workflows
  - Add integration test cases

#### 4.2 Optimize Query Distribution (45 minutes)
- **Target**: Balance query types across modes and categories
- **Script**: `scripts/gold_cases_improvement/optimize_query_distribution.py`
- **Examples**:
  - Ensure good distribution of retrieval vs reader vs decision cases
  - Balance technical vs operational queries
  - Add more specific category tags

#### 4.3 Add Metadata and Documentation (30 minutes)
- **Target**: Add comprehensive metadata
- **Script**: `scripts/gold_cases_improvement/add_metadata_documentation.py`
- **Examples**:
  - Add difficulty levels (Easy, Medium, Hard)
  - Add expected response time
  - Add category tags
  - Add dependency information

**Phase 4 Success Criteria**: Comprehensive coverage, balanced distribution, rich metadata

---

## 🎯 Success Metrics

### **Phase 1 Success Criteria**
- ✅ 0 unclear phrasing issues
- ✅ 0 short queries
- ✅ All queries are grammatically correct

### **Phase 2 Success Criteria**
- ✅ < 5 repetitive query patterns
- ✅ 90%+ cases have specific file references
- ✅ < 10 cases using `**/*.md` pattern

### **Phase 3 Success Criteria**
- ✅ 100% cases have specific file references
- ✅ 95%+ queries are actionable and specific
- ✅ All negative test cases properly configured

### **Phase 4 Success Criteria**
- ✅ 100% system component coverage
- ✅ Balanced query distribution across modes
- ✅ Rich metadata for all cases

## 🚀 Execution Commands

### **Phase 1: Critical Fixes**
```bash
# Fix unclear phrasing
python3 scripts/gold_cases_improvement/fix_unclear_phrasing.py

# Fix short queries
python3 scripts/gold_cases_improvement/fix_short_queries.py

# Verify fixes
python3 scripts/verify_gold_cases_detailed.py
```

### **Phase 2: Quality Improvements**
```bash
# Diversify query patterns
python3 scripts/gold_cases_improvement/diversify_query_patterns.py

# Improve content relevance
python3 scripts/gold_cases_improvement/improve_content_relevance.py

# Refine glob patterns
python3 scripts/gold_cases_improvement/refine_glob_patterns.py

# Verify improvements
python3 scripts/verify_gold_cases_detailed.py
```

### **Phase 3: Enhancement**
```bash
# Add specific file references
python3 scripts/gold_cases_improvement/add_specific_file_references.py

# Improve query specificity
python3 scripts/gold_cases_improvement/improve_query_specificity.py

# Validate negative cases
python3 scripts/gold_cases_improvement/validate_negative_cases.py

# Verify enhancements
python3 scripts/verify_gold_cases_detailed.py
```

### **Phase 4: Excellence**
```bash
# Add comprehensive coverage
python3 scripts/gold_cases_improvement/add_comprehensive_coverage.py

# Optimize query distribution
python3 scripts/gold_cases_improvement/optimize_query_distribution.py

# Add metadata and documentation
python3 scripts/gold_cases_improvement/add_metadata_documentation.py

# Final verification
python3 scripts/verify_gold_cases_detailed.py
```

## 📊 Expected Outcomes

### **After Phase 1**
- **Clarity**: 100% grammatically correct queries
- **Readability**: Natural, conversational language
- **User Experience**: Easy to understand what each case tests

### **After Phase 2**
- **Variety**: Diverse query patterns and styles
- **Precision**: Specific file references instead of broad patterns
- **Relevance**: Files directly match query intent

### **After Phase 3**
- **Specificity**: Actionable, detailed queries
- **Coverage**: Comprehensive file reference coverage
- **Testing**: Proper negative test case validation

### **After Phase 4**
- **Excellence**: Comprehensive test coverage
- **Balance**: Well-distributed query types
- **Richness**: Detailed metadata and documentation

## 🎉 Final Excellence Criteria

When all phases are complete, the gold cases will achieve "Excellent" status with:

1. **100% Grammatical Accuracy** - All queries are clear and natural
2. **100% File Accuracy** - All referenced files exist and are relevant
3. **90%+ Query Specificity** - Most queries are actionable and detailed
4. **100% Coverage** - All major system components are tested
5. **Balanced Distribution** - Good mix of query types and difficulty levels
6. **Rich Metadata** - Comprehensive documentation and categorization

**Total Estimated Time**: 8-12 hours  
**Expected Completion**: 2-3 days (working in phases)  
**Success Rate**: 95%+ cases achieving excellence criteria
