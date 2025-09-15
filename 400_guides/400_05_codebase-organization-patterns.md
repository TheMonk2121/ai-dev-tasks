\n+## 🧪 Testing & Safety Gates (Constitution)
\n+- Enforce tests and rollback plans on risky changes; prefer DSPy assertions for guardrails.
- Use the testing strategy section here for gates; surface violations in CI.
- For destructive edits, require pre‑flight file analysis and explicit approval.
# 💻 Codebase Organization & Patterns

<!-- ANCHOR_KEY: codebase-organization-patterns -->
<!-- ANCHOR_PRIORITY: 6 -->
<!-- ROLE_PINS: ["coder", "implementer"] -->

## 🔍 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete coding standards, patterns, and best practices for codebase development | Writing code, implementing features, optimizing performance, or debugging issues | Apply the patterns and standards to your development work |

- **what this file is**: Comprehensive coding standards, patterns, and best practices for codebase development.

- **read when**: When writing code, implementing features, optimizing performance, or debugging issues.

- **do next**: Apply the patterns and standards to your development work.

## 📋 **Table of Contents**

### **Core Development Patterns**
- [🚀 CODER ROLE SPECIFIC GUIDANCE](#-coder-role-specific-guidance)
- [🔬 RESEARCH & ANALYSIS INTEGRATION PATTERNS](#-research--analysis-integration-patterns)
- [💻 COMPREHENSIVE CODING BEST PRACTICES](#-comprehensive-coding-best-practices)

### **Quality & Testing**
- [🧪 TESTING STRATEGY AND QUALITY GATES](#-testing-strategy-and-quality-gates)
- [⚡ CODE PERFORMANCE OPTIMIZATION](#-code-performance-optimization)
- [🔧 SCRIPT OPTIMIZATION](#-script-optimization)

### **Learning & Examples**
- [🎓 ERROR REDUCTION LESSONS LEARNED](#-error-reduction-lessons-learned)
- [🎯 FEW-SHOT CONTEXT EXAMPLES](#-few-shot-context-examples)

### **Integration Standards**
- [🔧 MCP Module Development Standards](#-mcp-module-development-standards)
- [🤖 AGENT TOOL INTEGRATION STANDARDS](#-agent-tool-integration-standards)

### **Technical Reference**
- [🔧 Technical Artifacts Integration](#-technical-artifacts-integration)
- [🏗️ Architecture & Design Patterns](#️-architecture--design-patterns)
- [📚 References](#-references)

## 🎯 **Current Status**
- **Priority**: 🔥 **HIGH** - Essential for code quality and patterns
- **Phase**: 2 of 4 (Codebase Development)
- **Dependencies**: 04 (Development Workflows & Standards)

## 🎯 **Purpose**

This guide covers comprehensive coding standards and codebase organization patterns including:
- **Coding standards and conventions**
- **Code organization and structure patterns**
- **Performance optimization and efficiency**
- **Error handling and debugging strategies**
- **Testing and quality assurance**
- **Code reuse and pattern libraries**
- **Performance optimization techniques**
- **Module development and integration patterns**

## 📋 When to Use This Guide

- **Writing new code or scripts**
- **Implementing features and modules**
- **Optimizing code performance**
- **Debugging and troubleshooting**
- **Implementing testing strategies**
- **Reducing errors systematically**
- **Optimizing script efficiency**

## 🎯 Expected Outcomes

- **Consistent code quality** across all projects
- **Effective code organization** and structure
- **Optimized performance** and resource usage
- **Reliable error handling** and debugging
- **Comprehensive testing** and quality assurance
- **Systematic error reduction** and prevention
- **High-performance scripts** and systems

## 📋 Policies

### Coding Standards
- **Consistent code style** and formatting
- **Clear naming conventions** and documentation
- **Proper error handling** and logging
- **Performance optimization** and efficiency
- **Security best practices** and validation

### Code Organization Standards
- **Clear and consistent structure** for code organization
- **Pattern-based development** strategies
- **Iterative refinement** of code patterns
- **Quality validation** of code outputs
- **Best practices** in code organization

### Performance Standards
- **Script optimization** for efficiency
- **System performance** monitoring
- **Resource utilization** optimization
- **Scalability** considerations

## 🚀 CODER ROLE SPECIFIC GUIDANCE

### **When functioning as a Coder, ALWAYS start with:**

1. **Virtual Environment Check**: `python3 scripts/venv_manager.py --check` (ensures dependencies are available)
2. **Memory Rehydration**: `./scripts/memory_up.sh -r coder "specific task description"`
3. **Example-First Search**: Search existing codebase for similar patterns before writing new code
4. **Code Reuse Check**: Aim for 70% existing code reuse, 30% new code
5. **Test-First Development**: Write unit tests before implementation (TDD)

## 🔬 RESEARCH & ANALYSIS INTEGRATION PATTERNS

### **Research-First Development Approach**

**Purpose**: Integrate research and analysis into the development workflow to ensure evidence-based decisions and systematic problem-solving.

**Key Principles**:
- **Research before implementation**: Understand the problem domain before coding
- **Evidence-based decisions**: Use data and analysis to guide technical choices
- **Systematic evaluation**: Apply structured evaluation frameworks including RAGChecker for RAG system assessmen
- **Iterative refinement**: Continuously improve based on research findings

### **Implementation Patterns**

#### **1. Research-Driven Development Workflow**
```python
from typing import Dict, Any, Lis
from dataclasses import dataclass
import json

@dataclass
class ResearchContext:
    """Research context for development decisions."""
    problem_domain: str
    current_solutions: List[str]
    evaluation_criteria: List[str]
    success_metrics: Dict[str, Any]
    constraints: List[str]

def research_driven_development(problem: str, context: ResearchContext) -> Dict[str, Any]:
    """Execute research-driven development workflow."""

    # Phase 1: Research and Analysis
    research_findings = conduct_research(problem, context)
    analysis_results = analyze_findings(research_findings)

    # Phase 2: Solution Design
    solution_options = design_solutions(analysis_results)
    evaluation_results = evaluate_solutions(solution_options, context.evaluation_criteria)

    # Phase 3: Implementation Planning
    implementation_plan = create_implementation_plan(evaluation_results)
    risk_assessment = assess_implementation_risks(implementation_plan)

    return {
        "research_findings": research_findings,
        "analysis_results": analysis_results,
        "solution_options": solution_options,
        "evaluation_results": evaluation_results,
        "implementation_plan": implementation_plan,
        "risk_assessment": risk_assessmen
    }
```

#### **2. Systematic Evaluation Framework (Including RAGChecker)**
```python
class EvaluationFramework:
    """Systematic evaluation framework for technical decisions including RAGChecker for RAG system assessment."""

    def __init__(self, criteria: List[str], weights: Dict[str, float]):
        self.criteria = criteria
        self.weights = weights
        self.evaluation_history = []

    def evaluate_solution(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a solution against defined criteria."""
        scores = {}
        total_score = 0.0

        for criterion in self.criteria:
            score = self._evaluate_criterion(solution, criterion)
            scores[criterion] = score
            total_score += score * self.weights.get(criterion, 1.0)

        evaluation_result = {
            "solution": solution,
            "scores": scores,
            "total_score": total_score,
            "timestamp": time.time(),
            "recommendation": self._generate_recommendation(total_score)
        }

        self.evaluation_history.append(evaluation_result)
        return evaluation_resul

    def _evaluate_criterion(self, solution: Dict[str, Any], criterion: str) -> float:
        """Evaluate a specific criterion for a solution."""
        # Implementation specific to each criterion
        evaluators = {
            "performance": self._evaluate_performance,
            "security": self._evaluate_security,
            "maintainability": self._evaluate_maintainability,
            "scalability": self._evaluate_scalability,
            "cost": self._evaluate_cos
        }

        evaluator = evaluators.get(criterion, self._evaluate_generic)
        return evaluator(solution)

    def _generate_recommendation(self, total_score: float) -> str:
        """Generate recommendation based on total score."""
        if total_score >= 8.0:
            return "STRONG_RECOMMEND"
        elif total_score >= 6.0:
            return "RECOMMEND"
        elif total_score >= 4.0:
            return "CONSIDER"
        else:
            return "NOT_RECOMMEND"
```

#### **3. Evidence-Based Decision Making**
```python
class EvidenceBasedDecision:
    """Evidence-based decision making framework."""

    def __init__(self):
        self.evidence_sources = []
        self.decision_log = []

    def collect_evidence(self, sources: List[str]) -> Dict[str, Any]:
        """Collect evidence from multiple sources."""
        evidence = {}

        for source in sources:
            try:
                source_evidence = self._collect_from_source(source)
                evidence[source] = source_evidence
                self.evidence_sources.append({
                    "source": source,
                    "evidence": source_evidence,
                    "timestamp": time.time()
                })
            except Exception as e:
                logger.warning(f"Failed to collect evidence from {source}: {e}")

        return evidence

    def analyze_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected evidence for patterns and insights."""
        analysis = {
            "patterns": self._identify_patterns(evidence),
            "insights": self._extract_insights(evidence),
            "confidence": self._calculate_confidence(evidence),
            "recommendations": self._generate_recommendations(evidence)
        }

        return analysis

    def make_decision(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Make evidence-based decision."""
        decision = {
            "analysis": analysis,
            "context": context,
            "decision": self._evaluate_options(analysis, context),
            "rationale": self._generate_rationale(analysis, context),
            "timestamp": time.time()
        }

        self.decision_log.append(decision)
        return decision
```

### **Integration with Development Workflow**

#### **Research Integration Points**
```python
def integrate_research_into_workflow(backlog_item: Dict[str, Any]) -> Dict[str, Any]:
    """Integrate research into the development workflow."""

    # Check if research is needed
    if backlog_item.get("requires_research", False):
        research_context = create_research_context(backlog_item)
        research_results = research_driven_development(
            backlog_item["description"],
            research_contex
        )

        # Update backlog item with research findings
        backlog_item["research_findings"] = research_results
        backlog_item["implementation_plan"] = research_results["implementation_plan"]

        return backlog_item

    return backlog_item
```

#### **Evaluation Metrics Integration**
```python
def track_research_impact(implementation_results: Dict[str, Any],
                         research_predictions: Dict[str, Any]) -> Dict[str, Any]:
    """Track the impact of research on implementation outcomes."""

    impact_analysis = {
        "predicted_vs_actual": compare_predictions_to_actual(
            research_predictions,
            implementation_results
        ),
        "research_accuracy": calculate_research_accuracy(
            research_predictions,
            implementation_results
        ),
        "lessons_learned": extract_lessons_learned(
            research_predictions,
            implementation_results
        )
    }

    return impact_analysis
```

### Mini Coding Checklist (from Comprehensive Guide)
- Type hints on all functions; clear naming; import order stdlib → third_party → local; no stdlib shadowing
- DSPy assertions for risky code paths; define rollback plans for high‑risk changes
- Treat Tier 1/2 files as zero‑tolerance for F841; enforce in CI

### Auto‑fix Policy (Lessons Learned)
- Safe to auto‑fix in bulk: `RUF001` (Unicode replacement via escapes), `F401` (unused imports), `I001` (import reordering), `F541` (f‑string syntax).
- Dangerous to bulk auto‑fix: `PT009` (unittest asserts), `B007` (unused loop vars), `SIM117` (nested with), `RUF013` (implicit Optional), `SIM102` (nested if), `F841` (unused vars with dependencies).
- Apply safe fixes first; for dangerous categories, require manual review and targeted changes on small subsets before widening scope.

### **For Immediate Issues (10-minute triage):**

1. Run `python scripts/quick_conflict_check.py` for fast conflict detection
2. Check merge markers: `git grep -nE '^(<<<<<<<|=======|>>>>>>>)'`
3. Validate dependencies: `python -m pip check` (Python) or `npm ls --all` (Node.js)
4. **Cursor Git Integration Issue**: If you see "🔍 Quick conflict check" messages during commits, use `git commit --no-verify` or `./scripts/commit_without_cursor.sh "message"` to bypass Cursor's built-in conflict detection

### **For Systematic Problems (Deep audit):**

1. Run comprehensive health check: `python scripts/system_health_check.py --deep`
2. Execute conflict audit: `python scripts/conflict_audit.py --full`
3. Review results and implement fixes

### **For Prevention (Long-term stability):**

1. Set up CI gates using the guardrails in this document
2. Implement automated conflict detection
3. Regular maintenance using the prevention checklis

## 💻 COMPREHENSIVE CODING BEST PRACTICES

### **Code Criticality Map**

#### **Tier 1 Critical (Never Break Without a Plan)**
- **scripts/process_tasks.py**: Task execution engine, core CLI for executing backlog items end-to-end
- **scripts/state_manager.py**: Execution/state persistence, central state tracking across task boundaries
- **src/dspy_modules/cursor_model_router.py**: AI model routing & context engineering, intelligent model selection for Cursor Native AI
- **src/dspy_modules/vector_store.py**: Hybrid vector store, PGVector + text search storage retrieval span-level grounding
- **src/dspy_modules/document_processor.py**: Document ingestion & chunking, document processing validates extracts metadata chunks prepares documents
- **src/utils/memory_rehydrator.py**: Context assembly & role-aware hydration, context building builds role-aware context bundles from Postgres

#### **Tier 2 High (Production Infrastructure)**
- **scripts/doc_coherence_validator.py**: Documentation quality & coherence validation, documentation integrity primary validator
- **src/utils/database_resilience.py**: DB resilience & pooling, database management connection pooling health monitoring retries graceful degradation
- **src/dashboard.py**: Web UI & monitoring integration, Flask dashboard file intake SocketIO updates production monitoring health endpoints
- **src/utils/error_pattern_recognition.py**: Error recovery patterns, error management pattern catalog classification automated recovery hotfix templates
- **src/utils/prompt_sanitizer.py**: Input security guard-rails, security validation validation sanitization queries content foundational safe operations
- **scripts/rollback_doc.sh**: Documentation recovery & rollback system, documentation recovery git snapshot system automated snapshots rollback procedures
- **src/utils/anchor_metadata_parser.py**: Anchor metadata extraction, metadata processing extracts anchor metadata HTML comments maps JSONB memory rehydrator critical context assembly

#### **Tier 3 Supporting (Reliability/Utilities)**
- **src/utils/retry_wrapper.py**: Retry/backoff policies
- **scripts/system_health_check.py**: Health checks diagnostics
- **scripts/performance_benchmark.py**: Performance monitoring optimization
- **src/utils/config_manager.py**: Centralized config handling
- **src/utils/logger.py**: Structured logging helpers
- **scripts/auto_push_prompt.py**: Repository maintenance automation, maintenance automation interactive prompt pushing changes git status checks user confirmation
- **scripts/maintenance_push.sh**: Maintenance push wrapper, maintenance integration shell wrapper auto-push prompt integration maintenance workflows

### **Code Quality Standards**

#### **Tier 1 & 2 Requirements**
- **Pass linter checks**: No F841, E501 errors
- **Comprehensive test coverage**: 80%+ for Tier 1, 70%+ for Tier 2
- **Unused variable best practices**: Proper variable managemen
- **Proper import patterns**: Clear import organization
- **Clear error handling**: Comprehensive error handling and logging

#### **Quality Gates**
- **Pre-commit**: Linter checks pass for Tier 1/2 files
- **CI/CD**: F841 errors cause failures for Tier 1/2 files
- **Code Review**: Unused variable patterns reviewed
- **Test Coverage**: Minimum coverage thresholds enforced

#### **Linting Standards**
- **Tier 1 & 2 files**: Pass all checks
- **Test files**: F841 best practices
- **Ruff configuration**: `--select E,F,I` for comprehensive linting
- **Test-specific linting**: `--select F841` for test files

## 🧪 TESTING STRATEGY AND QUALITY GATES

### **Multi-Role Testing Decision Framework**

**Purpose**: Comprehensive testing strategy and quality gates for the AI development ecosystem.

**Current Status**: Active testing strategy maintained with critical priority and high complexity.

**Testing Approach Migration**:
- **Current Approach**: Marker-based testing with `--tiers` and `--kinds` for test selection, centralized imports with `conftest.py`, pytest with markers
- **Legacy Approach**: Comprehensive test suite, manual sys.path manipulation, file-based test selection (to avoid)

### **Testing Pyramid**

#### **Test Distribution Guidelines**
- **Unit Tests**: 70% - Individual functions/methods, < 1 second execution
- **Integration Tests**: 20% - Component interactions, 1-10 seconds execution
- **E2E Tests**: 10% - Complete user workflows, 10-60 seconds execution

#### **Test Types**

**Unit Tests**:
```python
# Example unit test structure
import unittes
from unittest.mock import Mock, patch

class TestAIModelInterface(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures

    def test_generate_response_success(self):
        # Arrange
        # Ac
        # Assert

    def test_generate_response_failure(self):
        # Test error handling
```

**Integration Tests**:
```python
# Example integration tes
class TestAIIntegration(unittest.TestCase):
    def setUp(self):
        # Set up integration test environmen

    def test_ai_generation_integration(self):
        # Test AI generation with database integration

    def test_workflow_execution_integration(self):
        # Test n8n workflow execution integration
```

**End-to-End Tests**:
```python
# Example E2E tes
from selenium import webdriver

class TestAIEcosystemE2E(unittest.TestCase):
    def setUp(self):
        # Set up E2E test environmen

    def test_complete_ai_workflow(self):
        # Test complete AI workflow from UI to database

    def tearDown(self):
        # Clean up E2E test environmen
```

### **Quality Gates**

#### **Code Quality Gates**
- **Static Code Analysis**: pylint, flake8, mypy
- **Code Coverage Gates**: Minimum 80% coverage, fail under 80%

#### **Test Quality Gates**
- **Unit Tests**: Required timeout 300s, min pass rate 95%
- **Integration Tests**: Required timeout 600s, min pass rate 90%
- **E2E Tests**: Required timeout 1800s, min pass rate 85%

#### **Performance Quality Gates**
- **Performance Test Gates**: Response time < 100ms, throughput > 1000 req/s

#### **Schema Validation Quality Gates**
- **Schema Drift Detection**: Automated schema drift detection for database and Pydantic models
- **Baseline Management**: Version-controlled schema baselines with automated updates
- **Pre-commit Schema Checks**: Schema validation before commits to prevent breaking changes

**Schema Inspection System**:
```bash
# Generate schema snapshots
python3 scripts/validate_config.py --dump-schemas

# Check for schema drif
python3 scripts/system_health_check.py --schema-drif

# Update baseline after intentional changes
./scripts/update_schema_baseline.sh
```

**Schema Coverage**:
- **Pydantic Models**: RAGChecker, DSPy context models, constitution models, error models
- **Pydantic Integration**: Enhanced validation, type safety, and performance optimization for RAGChecker workflows
- **Database Schema**: Tables, columns, indexes, relationships in PostgreSQL
- **Artifacts**: Stored in `dspy-rag-system/config/database/schemas/`

**Integration with CI/CD**:
```yaml
- name: Generate schema snapshots
  run: python3 scripts/validate_config.py --dump-schemas

- name: Schema drift check
  run: python3 scripts/system_health_check.py --schema-drif
```

### **AI Model Testing**

#### **Functionality Testing**
- **Model Response Quality**: Accuracy, relevance, completeness
- **Error Handling**: Graceful failure handling
- **Integration Testing**: Model integration with other components

#### **Performance Testing**
- **Response Time**: < 2 seconds for standard queries
- **Throughput**: > 100 requests per minute
- **Resource Usage**: Memory < 4GB, CPU < 80%

#### **Security Testing**
- **Input Validation**: Prompt injection prevention
- **Output Filtering**: Content filtering and sanitization
- **Access Control**: Model access control and authentication

#### **RAG System Testing with RAGChecker**
- **Official RAGChecker Evaluation**: Industry-standard RAG evaluation framework
- **Evaluation Script**: `python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5`
- **Metrics**: Precision, Recall, F1 Score, Context Utilization, Response Length
- **Quality Gates**:
  - Precision > 0.5, Recall > 0.6, F1 Score > 0.5
  - Context Utilization > 0.7, Response Length > 500 characters
- **Test Cases**: 5 comprehensive ground truth test cases
- **Integration**: Real responses from Unified Memory Orchestrator
- **Status**: ✅ **FULLY OPERATIONAL** - RAGChecker 0.1.9 + spaCy model installed

#### **RAGChecker + Pydantic Integration** ✅ **COMPLETE**
- **Enhanced Data Validation**: Pydantic v2 models for type safety and validation
- **Constitution-Aware Validation**: Integration with constitution validation system
- **Error Taxonomy Mapping**: Structured error classification and reporting
- **Performance Optimization**: Intelligent caching, batching, and optimization strategies
- **Performance Monitoring**: Real-time monitoring, alerting, and metrics expor
- **Error Recovery**: Intelligent error recovery with retry mechanisms and fallback strategies
- **Enhanced Debugging**: Comprehensive debugging context and performance metrics
- **Status**: ✅ **FULLY INTEGRATED** - All phases complete and tested

#### **RAGChecker Testing Commands**

**🚨 NEW: Code-as-SSOT Evaluation System** - Use the standardized evaluation system:

```bash
# Generate evaluation documentation and artifacts
python -m evals_300.tools.gen

# Run specific evaluation passes
python -m evals_300.tools.run --suite 300_core --pass retrieval_only_baseline
python -m evals_300.tools.run --suite 300_core --pass deterministic_few_sho

# Legacy direct execution (still supported)
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# Verify installation
python3 -c "import ragchecker; print('✅ RAGChecker installed successfully!')"

# Check evaluation status
cat metrics/baseline_evaluations/EVALUATION_STATUS.md

# View latest results
ls -la metrics/baseline_evaluations/ragchecker_official_*.json
```

### **Continuous Testing**

#### **CI/CD Integration**
- **Automated Testing Pipeline**: Unit, integration, E2E tests
- **Quality Gates**: Automated quality gate enforcemen
- **Performance Monitoring**: Continuous performance monitoring

#### **Automated Testing Pipeline**
```yaml
# Example CI/CD pipeline
stages:
  - tes
  - quality
  - performance
  - security

test:
  script:
    - pytest tests/unit/
    - pytest tests/integration/
    - pytest tests/e2e/
```

### **Quality Metrics**

#### **Code Quality Metrics**
- **Code Coverage**: 80%+ for critical components
- **Static Analysis**: pylint score ≥ 8.0
- **Test Pass Rate**: 95%+ for all test suites

#### **Performance Metrics**
- **Response Time**: < 100ms average
- **Throughput**: > 1000 requests per second
- **Error Rate**: < 1% error rate

### **Testing Checklist**

#### **Pre-Commit Testing Checklist**
- [ ] Unit tests pass (95% pass rate)
- [ ] Code coverage meets minimum (80%)
- [ ] Static analysis passes (pylint score ≥ 8.0)
- [ ] No security vulnerabilities detected
- [ ] Performance benchmarks pass
- [ ] Documentation updated

#### **Integration Testing Checklist**
- [ ] All API endpoints tested
- [ ] Database integration verified
- [ ] AI model integration tested
- [ ] Workflow execution tested
- [ ] Error handling verified
- [ ] Security integration tested
- [ ] **RAGChecker evaluation run** for RAG system changes (if applicable)

#### **Deployment Testing Checklist**
- [ ] End-to-end tests pass
- [ ] Load tests completed
- [ ] Security tests passed
- [ ] Performance gates me
- [ ] Monitoring configured
- [ ] Rollback plan tested

### **Testing Tools**

#### **Test Automation Tools**
- **Test Runner**: pytest with markers and plugins
- **Coverage**: coverage.py for code coverage
- **Performance**: locust for load testing
- **Security**: Bandit for security testing

#### **Quality Report Generator**
```python
# Example quality report generation
def generate_quality_report():
    # Collect metrics
    # Calculate quality score
    # Generate recommendations
    # Save repor
```

### **Python Style Standards**

#### **Code Structure**
```python
# Example of compliant code structure
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

# Performance optimization section
## ⚡ CODE PERFORMANCE OPTIMIZATION

### **Script Optimization Techniques**

#### **1. Algorithm Optimization**
```python
# Before: O(n²) complexity
def find_duplicates_slow(items):
    duplicates = []
    for i, item in enumerate(items):
        for j, other_item in enumerate(items[i+1:], i+1):
            if item == other_item:
                duplicates.append(item)
    return duplicates

# After: O(n) complexity with se
def find_duplicates_fast(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
```

#### **2. Memory Optimization**
```python
# Memory-efficient data processing
import itertools
from typing import Iterator

def process_large_file_memory_efficient(filename: str) -> Iterator[str]:
    """Process large files without loading entire file into memory."""
    with open(filename, 'r') as file:
        for line in file:
            # Process one line at a time
            processed_line = process_line(line.strip())
            if processed_line:
                yield processed_line

def process_line(line: str) -> Optional[str]:
    """Process individual line with memory optimization."""
    # Use generators for large data transformations
    return line.upper() if line.strip() else None
```

#### **3. Caching and Memoization**
```python
from functools import lru_cache
import time

# Simple caching for expensive operations
@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> int:
    """Expensive calculation with caching."""
    time.sleep(0.1)  # Simulate expensive operation
    return n * n

# Custom caching for complex objects
class ResultCache:
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size

    def get(self, key: str):
        """Get cached result."""
        if key in self.cache:
            # Move to front (LRU)
            result = self.cache.pop(key)
            self.cache[key] = result
            return result
        return None

    def set(self, key: str, value: Any):
        """Set cached result with LRU eviction."""
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            self.cache.pop(oldest_key)
        self.cache[key] = value
```

### **Performance Profiling and Monitoring**

#### **1. Code Profiling**
```python
import cProfile
import pstats
import io
from contextlib import contextmanager

@contextmanager
def profile_code():
    """Context manager for profiling code blocks."""
    pr = cProfile.Profile()
    pr.enable()
    try:
        yield
    finally:
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        print(s.getvalue())

# Usage example
with profile_code():
    result = expensive_calculation(1000)
```

#### **2. Performance Metrics**
```python
import time
from typing import Callable, Any

def measure_performance(func: Callable, *args, **kwargs) -> tuple[Any, float]:
    """Measure function performance and return result with execution time."""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    return result, execution_time

# Performance benchmarking
def benchmark_functions(functions: list[Callable], test_data: Any):
    """Benchmark multiple functions with the same test data."""
    results = {}
    for func in functions:
        result, execution_time = measure_performance(func, test_data)
        results[func.__name__] = {
            'result': result,
            'execution_time': execution_time
        }
    return results
```

### **Development Performance Best Practices**

#### **1. Efficient Data Structures**
```python
# Use appropriate data structures for performance
from collections import defaultdict, Counter, deque

# Fast lookups with defaultdic
word_counts = defaultdict(int)
for word in text.split():
    word_counts[word] += 1

# Efficient counting with Counter
word_frequency = Counter(text.split())

# Fast append/pop with deque
recent_items = deque(maxlen=100)
for item in stream:
    recent_items.append(item)
```

#### **2. Generator Expressions**
```python
# Memory-efficient processing with generators
# Instead of list comprehension for large datasets
def process_large_dataset(items):
    # Memory efficient: processes one item at a time
    return (process_item(item) for item in items if should_process(item))

# vs. list comprehension (loads all into memory)
def process_large_dataset_inefficient(items):
    return [process_item(item) for item in items if should_process(item)]
```

#### **3. Async/Await for I/O Operations**
```python
import asyncio
import aiohttp
from typing import Lis

async def fetch_urls_async(urls: List[str]) -> List[str]:
    """Fetch multiple URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch single URL."""
    async with session.get(url) as response:
        return await response.text()

# Usage
urls = ['http://example.com/1', 'http://example.com/2', 'http://example.com/3']
results = asyncio.run(fetch_urls_async(urls))
```

### **Performance Optimization Checklist**

- [ ] **Algorithm complexity analyzed** and optimized
- [ ] **Memory usage profiled** and optimized
- [ ] **Caching strategies implemented** where appropriate
- [ ] **Data structures optimized** for specific use cases
- [ ] **I/O operations optimized** with async/awai
- [ ] **Performance benchmarks** established and monitored
- [ ] **Code profiling** completed and bottlenecks identified
- [ ] **Memory leaks** identified and resolved
- [ ] **Generator expressions** used for large datasets
- [ ] **Efficient data processing** patterns implemented
```

### **Quality Gates for Solo Development**

| Gate | Purpose | Criteria | Tools |
|------|---------|----------|-------|
|**Code Review**| Ensure code quality | Standards compliance, logic correctness | Self-review |
|**Testing**| Verify functionality | Unit tests, basic integration tests | pytest |
|**Documentation**| Maintain clarity | Documentation completeness | Manual review |
|**Security**| Prevent vulnerabilities | Basic security validation | Manual review |
|**Performance**| Ensure efficiency | Basic performance checks | Manual review |

## 🔧 SCRIPT OPTIMIZATION

### **Top 5 Critical Scripts & Optimization Priorities**

#### **1. `update_cursor_memory.py` - Memory Context Updater**
**Current Issues**: Re-parses entire backlog file, no caching, sequential processing
**Optimization Priority**: 🔥 **HIGH** (run after every change)

##### **Immediate Optimizations**:
```python
# Add caching layer
import hashlib
import pickle
from pathlib import Path

class CachedBacklogParser:
    def __init__(self, cache_dir: Path = Path(".cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def get_backlog_hash(self, file_path: Path) -> str:
        """Get file hash for cache invalidation."""
        return hashlib.md5(file_path.read_bytes()).hexdigest()

    def load_cached_priorities(self, file_path: Path) -> Optional[List[Dict]]:
        """Load cached priorities if valid."""
        cache_file = self.cache_dir / f"backlog_priorities_{file_path.name}.pkl"
        hash_file = self.cache_dir / f"backlog_hash_{file_path.name}.txt"

        if cache_file.exists() and hash_file.exists():
            current_hash = self.get_backlog_hash(file_path)
            cached_hash = hash_file.read_text().strip()

            if current_hash == cached_hash:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)

        return None

    def save_cached_priorities(self, file_path: Path, priorities: List[Dict]):
        """Save priorities to cache."""
        cache_file = self.cache_dir / f"backlog_priorities_{file_path.name}.pkl"
        hash_file = self.cache_dir / f"backlog_hash_{file_path.name}.txt"

        with open(cache_file, 'wb') as f:
            pickle.dump(priorities, f)

        hash_file.write_text(self.get_backlog_hash(file_path))
```

**Performance Targets**:
- **Current**: ~2-3 seconds
- **Target**: <500ms (80% improvement)
- **Memory**: <50MB

#### **2. `quick_conflict_check.py` - Fast Conflict Detection**
**Current Issues**: Sequential checks, no early exit, redundant git calls
**Optimization Priority**: 🔥 **HIGH** (pre-commit hook)

##### **Immediate Optimizations**:
```python
# Parallel execution with early exi
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

class OptimizedConflictChecker:
    def __init__(self):
        self.max_workers = min(8, multiprocessing.cpu_count() + 2)

    def run_parallel_checks(self) -> Dict[str, bool]:
        """Run all checks in parallel with early exit on critical failures."""
        checks = [
            ("merge_markers", self.check_merge_markers),
            ("backup_files", self.check_backup_files),
            ("package_conflicts", self.check_package_conflicts),
        ]

        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_check = {
                executor.submit(check_func): check_name
                for check_name, check_func in checks
            }

            for future in as_completed(future_to_check):
                check_name = future_to_check[future]
                try:
                    results[check_name] = future.result()
                except Exception as e:
                    logger.error(f"Check {check_name} failed: {e}")
                    results[check_name] = False

        return results
```

**Performance Targets**:
- **Current**: ~1-2 seconds
- **Target**: <200ms (85% improvement)
- **Memory**: <25MB

## 🚀 **UV Package Management Migration**

### **🎯 Overview**

**UV Migration** represents a successful transition from pip to UV package management, providing significant performance improvements, better dependency management, and modern tooling integration.

**What**: Complete migration from pip to UV package management across all project phases.

**When**: When setting up development environments, managing dependencies, or using modern Python tooling.

**How**: Use UV commands for all package management tasks, following established patterns and best practices.

### **✅ Migration Phases Completed**

#### **Phase 1: Drop-in Replacement**
- **Installed UV 0.8.15** with Rust performance
- **Created new `.venv` with Python 3.12.11** (upgraded from 3.9.6)
- **Installed all 184 packages** using UV (7.48s resolve + 516ms install)
- **Verified compatibility** with existing pre-commit hooks
- **Tested key dependencies**: DSPy 3.0.1, PyTorch 2.8.0, psycopg2

#### **Phase 2: pyproject.toml Migration**
- **Migrated from `requirements.txt` to `pyproject.toml`** with organized dependency groups
- **Created dependency groups**: `dev`, `test`, `security`, `ml`
- **Generated `uv.lock` file** with 204 packages for deterministic builds
- **Updated installation script** (`install_dependencies.sh`) to use UV workflow
- **Updated README** with comprehensive UV usage guide

#### **Phase 3: CI/CD Integration & Advanced Features**
- **Updated all GitHub Actions workflows** to use UV:
  - Quick Check, Deep Audit, Evaluation Pipeline
  - RAGChecker, Maintenance Validation
- **Added UVX support** for one-off tools (`scripts/uvx_tools.sh`)
- **Created requirements export script** (`scripts/uv_export_requirements.py`)
- **Enhanced pre-commit hooks** with UVX tools check
- **Comprehensive documentation** updates

### **📊 Performance Improvements**

| Metric | Before (pip) | After (UV) | Improvement |
|--------|-------------|------------|-------------|
| **Dependency Resolution** | 30-60s | 1-7s | **10-60x faster** |
| **Package Installation** | 2-5 minutes | 0.5-1s | **100-600x faster** |
| **Lock File Generation** | N/A | 1.13s | **New capability** |
| **Tool Execution** | Global installs | Instant via UVX | **No setup needed** |

### **🔧 Key Benefits Achieved**

#### **🚀 Speed & Performance**
- **Lightning-fast installs**: 10-100x faster than pip
- **Rust-based resolver**: Parallel downloads and caching
- **Deterministic builds**: `uv.lock` ensures reproducible environments

#### **🔧 Developer Experience**
- **One tool**: Replaces pip + virtualenv + pip-tools
- **UVX tools**: Run any Python tool without global installation
- **Better error messages**: Clear dependency conflict resolution
- **Modern Python**: Automatic Python version management

#### **🛡️ Reliability & Security**
- **Deterministic builds**: Lock files ensure reproducible environments
- **Dependency isolation**: Better conflict resolution
- **Security scanning**: Built-in vulnerability detection
- **CI/CD integration**: Consistent environments across all systems

### **📋 UV Usage Patterns**

#### **Basic Commands**
```bash
# Create virtual environment
uv venv

# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Run commands in environment
uv run python script.py

# Run one-off tools
uvx tool-name
```

#### **Advanced Commands**
```bash
# Export requirements
uv export --format requirements-txt > requirements.txt

# Update dependencies
uv sync --upgrade

# Check for outdated packages
uv tree --outdated

# Run with specific Python version
uv run --python 3.12 python script.py
```

#### **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Set up UV
  uses: astral-sh/setup-uv@v4
  with:
    version: "0.8.15"

- name: Install dependencies
  run: uv sync

- name: Run tests
  run: uv run pytest
```

### **🎯 Migration Lessons Learned**

1. **Start with drop-in replacement** - Don't change everything at once
2. **Test thoroughly** - Verify all existing functionality works
3. **Update documentation** - Keep usage guides current
4. **Use dependency groups** - Organize dependencies logically
5. **Leverage UVX** - Use for one-off tools and scripts
6. **Update CI/CD** - Ensure consistent environments everywhere

### **🔄 Ongoing Maintenance**

#### **Regular Tasks**
- **Update UV**: Keep UV version current
- **Sync dependencies**: Regular `uv sync` to update lock file
- **Security scanning**: Use `uv audit` for vulnerability checks
- **Cleanup**: Remove unused dependencies with `uv remove`

#### **Best Practices**
- **Use lock files**: Always commit `uv.lock` for reproducible builds
- **Group dependencies**: Organize by purpose (dev, test, security, ml)
- **Document changes**: Update README when adding new tools
- **Test migrations**: Verify changes work in CI/CD

---

## 🎓 ERROR REDUCTION LESSONS LEARNED

### **Journey Summary**

#### **Starting Point**
- **Goal**: Reduce linter errors systematically across the codebase
- **Initial Approach**: Try auto-fixes broadly and see what works
- **Reality**: Most auto-fixes multiplied errors instead of reducing them

#### **Final Outcome**
- **Successfully Eliminated**: 831 errors (RUF001, F401, I001, F541)
- **Failed Attempts**: Multiple error multiplication disasters
- **Tool Created**: Smart error fix script with decision matrix
- **Documentation**: Comprehensive anti-patterns and prevention strategies

### **Key Discoveries**

#### **1. Auto-Fix Multiplication Effect**
**The Problem**: Most auto-fixes multiply errors instead of reducing them.

**Examples**:
- **PT009**: 127 → 1328 errors (945% increase)
- **B007**: 35 → 206 errors (489% increase)
- **RUF013**: 29 → 213 errors (634% increase)

**Root Cause**: Auto-fixes often introduce new errors while trying to fix existing ones, creating a cascade effect.

#### **2. Error Counting Complexity**
**The Problem**: Simple line counting gives inflated error numbers.

**Discovery**: Ruff outputs multiple lines per error:
- File path and line number
- Error message
- Help text with suggestions
- Code context

**Solution**: Pattern matching to count actual error occurrences, not just lines.

### **Decision Matrix: Safe vs. Dangerous Errors**

#### **✅ SAFE to Auto-Fix (Low Risk)**
- **RUF001**: Unicode character replacement (use escape sequences)
- **F401**: Unused imports (simple deletion)
- **I001**: Import formatting (reordering)
- **F541**: F-string issues (simple syntax fixes)

#### **⚠️ DANGEROUS to Auto-Fix (High Risk)**
- **PT009**: Unittest-style asserts (can break test logic)
- **B007**: Unused loop variables (can break loop logic)
- **SIM117**: Nested with statements (can break context management)
- **RUF013**: Implicit Optional types (can break type safety)
- **SIM102**: Nested if statements (can break control flow)
- **F841**: Unused variables (can break variable dependencies)

### **Systematic Approach**

#### **Phase 1: Safe Error Elimination**
1. **RUF001**: Unicode characters → ASCII equivalents
2. **F401**: Unused imports → Remove completely
3. **I001**: Import formatting → Reorder imports
4. **F541**: F-string issues → Fix syntax

#### **Phase 2: Manual Review for Dangerous Errors**
1. **PT009**: Review each unittest-style assert individually
2. **B007**: Check if loop variables are actually needed
3. **SIM117**: Verify context management logic
4. **RUF013**: Ensure type safety is maintained
5. **SIM102**: Verify control flow logic
6. **F841**: Check variable dependencies

#### **Phase 3: Prevention Strategies**
1. **Pre-commit hooks**: Catch errors before they multiply
2. **Template sanitization**: Clean templates before use
3. **Code review**: Manual review for dangerous patterns
4. **Documentation**: Record anti-patterns and solutions

## 🎯 FEW-SHOT CONTEXT EXAMPLES

### **Documentation Coherence Examples**

#### **1. File Naming Convention Validation**
**Context**: Validating file naming conventions across the project

**Input**:
```markdown
# Check if this file follows naming conventions
filename: "400_guides/400_security-best-practices-guide.md"
```

**Expected Output**:
```json
{
  "valid": true,
  "pattern": "400_*_guide.md",
  "category": "documentation",
  "priority": "HIGH",
  "context_reference": "400_guides/400_context-priority-guide.md",
  "backlog_reference": "000_core/000_backlog.md"
}
```

**Pattern**: `400_` prefix indicates high-priority documentation with context references
**Validation**: Check for required HTML comments and cross-references

#### **2. Cross-Reference Validation**
**Context**: Ensuring documentation files reference each other correctly

**Input**:
```markdown
<!-- BACKLOG_REFERENCE: 000_core/000_backlog.md -->
```

**Expected Output**:
```json
{
  "references_valid": true,
  "context_file_exists": true,
  "backlog_file_exists": true,
  "memory_level": "HIGH",
  "coherence_score": 0.95
}
```

**Pattern**: HTML comments with specific reference patterns
**Validation**: Verify referenced files exist and are accessible

#### **3. Documentation Structure Validation**
**Context**: Validating documentation structure and completeness

**Input**:
```markdown
# Document Title

**Expected Output**:
```json
{
  "structure_valid": true,
  "has_purpose": true,
  "has_toc": true,
  "has_sections": true,
  "has_last_updated": true,
  "completeness_score": 0.9
}
```

**Pattern**: Standard documentation structure with required sections
**Validation**: Check for required sections and formatting

### **AI Prompting Patterns**

#### **1. Context-Aware Prompting**
**Pattern**: Provide relevant context before asking for specific actions

**Example**:
```markdown
## Context
You are working on a Python project with the following structure:
- Main application in `src/`
- Tests in `tests/`
- Documentation in `docs/`
- Configuration in `config/`

## Task
Create a new feature that integrates with the existing authentication system.

## Expected Outpu
- Code implementation following project standards
- Unit tests with 80%+ coverage
- Documentation updates
- Configuration changes if needed
```

#### **2. Iterative Refinement**
**Pattern**: Start with broad prompts and refine based on results

**Example**:
```markdown
## Initial Promp
"Create a user authentication system"

## Refined Promp
"Create a user authentication system using JWT tokens with the following requirements:
- User registration with email validation
- Login with password hashing
- Token-based session managemen
- Password reset functionality
- Rate limiting for security"
```

#### **3. Validation-First Prompting**
**Pattern**: Define validation criteria before requesting output

**Example**:
```markdown
## Task
Generate a Python function for data validation

## Validation Criteria
- Function must accept a dictionary as input
- Must return a boolean indicating validity
- Must log validation errors
- Must handle edge cases (None, empty dict, etc.)
- Must be testable with unit tests

## Expected Outpu
- Function implementation
- Error handling
- Logging statements
- Example usage
```

#### **4. Schema Validation Integration**
**Pattern**: Use schema inspection system for data model validation

**Example**:
```markdown
## Task
Update Pydantic models for new feature

## Schema Validation Steps
1. Generate current schema baseline: `python3 scripts/validate_config.py --dump-schemas`
2. Make model changes
3. Check for schema drift: `python3 scripts/system_health_check.py --schema-drift`
4. Update baseline if intentional: `./scripts/update_schema_baseline.sh`

## Expected Outpu
- Updated Pydantic models
- Schema artifacts in `dspy-rag-system/config/database/schemas/`
- No unintended schema drift detected
```

## 🔧 How-To

### Writing Quality Code
1. **Follow established coding standards** and conventions
2. **Use clear naming** and comprehensive documentation
3. **Implement proper error handling** and logging
4. **Optimize for performance** and resource usage
5. **Write comprehensive tests** for all functionality

### Creating Effective AI Prompts
1. **Define clear objectives** and expected outcomes
2. **Provide relevant context** and background information
3. **Use specific and actionable** language
4. **Iterate and refine** prompts based on results
5. **Validate and verify** AI outputs for quality

### Optimizing Script Performance
1. **Identify performance bottlenecks** through profiling
2. **Implement caching strategies** for repeated operations
3. **Use parallel processing** where appropriate
4. **Optimize I/O operations** and database queries
5. **Monitor resource usage** and memory consumption

### Reducing Errors Systematically
1. **Categorize errors** as safe vs. dangerous
2. **Apply safe auto-fixes** automatically
3. **Review dangerous errors** manually
4. **Implement prevention strategies** for future errors
5. **Document lessons learned** and anti-patterns

## 📋 Checklists

### Code Quality Checklis
- [ ] **Code follows established standards** and conventions
- [ ] **Clear naming and comprehensive documentation**
- [ ] **Proper error handling and logging** implemented
- [ ] **Performance optimization considerations** addressed
- [ ] **Security best practices** followed
- [ ] **Comprehensive tests written and passing**

### AI Prompting Checklis
- [ ] **Clear objectives and expected outcomes** defined
- [ ] **Relevant context and background** provided
- [ ] **Specific and actionable language** used
- [ ] **Prompt iterated and refined** based on results
- [ ] **AI outputs validated and verified** for quality
- [ ] **Ethical considerations** addressed

### Performance Optimization Checklis
- [ ] **Performance bottlenecks identified** through profiling
- [ ] **Caching strategies implemented** for repeated operations
- [ ] **Parallel processing used** where appropriate
- [ ] **I/O operations optimized** and database queries improved
- [ ] **Resource usage monitored** and memory consumption optimized

### Error Reduction Checklis
- [ ] **Errors categorized** as safe vs. dangerous
- [ ] **Safe auto-fixes applied** automatically
- [ ] **Dangerous errors reviewed** manually
- [ ] **Prevention strategies implemented** for future errors
- [ ] **Lessons learned documented** and anti-patterns recorded

## 🔗 Interfaces

### Development Environmen
- **Code Editor**: Cursor, VS Code with AI assistance
- **Version Control**: Git with feature branch workflow
- **Testing Framework**: pytest for unit and integration tests
- **Code Quality**: ruff for linting and formatting
- **Performance Monitoring**: Built-in performance tracking

### AI Integration
- **Prompt Management**: Structured prompt templates and patterns
- **Context Management**: Memory systems for context preservation
- **Output Validation**: Quality checks and validation frameworks
- **Iterative Refinement**: Feedback loops for prompt improvement

### Performance Tools
- **Profiling**: cProfile, line_profiler for performance analysis
- **Caching**: Redis, in-memory caching for optimization
- **Monitoring**: Prometheus, Grafana for performance tracking
- **Optimization**: Parallel processing, async/await for efficiency

## 📚 Examples

### Coding Standards Example
```python
# Good: Clear naming and documentation
def calculate_user_performance_metrics(user_id: str, date_range: tuple) -> dict:
    """
    Calculate performance metrics for a specific user over a date range.

    Args:
        user_id: Unique identifier for the user
        date_range: Tuple of (start_date, end_date) in ISO forma

    Returns:
        Dictionary containing calculated performance metrics

    Raises:
        ValueError: If date_range is invalid
        UserNotFoundError: If user_id doesn'tt exis
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Error calculating metrics for user {user_id}: {e}")
        raise
```

### AI Prompting Example
```markdown
## Effective AI Prompt Structure

### Context
Provide relevant background and context for the AI to understand the task.

### Objective
Clearly state what you want the AI to accomplish.

### Constraints
Specify any limitations or requirements that must be followed.

### Examples
Provide concrete examples of expected input/output patterns.

### Validation
Define how to verify the quality and correctness of the output.
```

### Performance Optimization Example
```python
# Before: Sequential processing
def process_data_sequential(data_list):
    results = []
    for item in data_list:
        result = expensive_operation(item)
        results.append(result)
    return results

# After: Parallel processing with caching
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_operation(item):
    # Cached expensive operation
    pass

def process_data_parallel(data_list):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(expensive_operation, data_list))
    return results
```

### Error Reduction Example
```python
# Smart error fix script with decision matrix
def smart_error_fix(error_code: str, file_path: str) -> bool:
    """Apply safe fixes only, return success status."""

    safe_fixes = {
        'RUF001': fix_unicode_characters,
        'F401': remove_unused_imports,
        'I001': fix_import_formatting,
        'F541': fix_f_string_issues
    }

    dangerous_fixes = {
        'PT009': 'Manual review required - unittest-style asserts',
        'B007': 'Manual review required - loop variables',
        'SIM117': 'Manual review required - nested with statements'
    }

    if error_code in safe_fixes:
        return safe_fixes[error_code](file_path)
    elif error_code in dangerous_fixes:
        logger.warning(f"Dangerous fix required: {dangerous_fixes[error_code]}")
        return False
    else:
        logger.warning(f"Unknown error code: {error_code}")
        return False
```

## 🔧 MCP Module Development Standards

### **MCP Server Development Patterns**

**Purpose**: Standards for developing MCP (Model Context Protocol) servers and modules with enhanced role-specific context integration.

**Core Requirements**:
- **Inherit from Base Server**: All MCP servers must inherit from `MCPServer` base class
- **Configuration Management**: Use `MCPConfig` dataclass for server configuration
- **Error Handling**: Implement proper `MCPError` handling and logging
- **Documentation**: Comprehensive docstrings and type hints
- **Role-Specific Context**: Implement role-aware context for enhanced AI interactions
- **Cursor Integration**: Include Cursor knowledge integration where appropriate

### **MCP Server Orchestration (B-1040)**

**Purpose**: Multi-server tool integration and routing for enhanced MCP capabilities.

**Core Features**:
- **Multi-Server Integration**: Coordinate multiple MCP servers for comprehensive tool coverage
- **Tool Routing**: Intelligent routing of requests to appropriate MCP servers
- **Performance Monitoring**: Real-time monitoring of MCP server health and performance
- **Load Balancing**: Distribute requests across available MCP servers
- **Failover Handling**: Automatic failover to backup servers when primary servers fail

**Implementation Pattern**:
```python
class MCPOrchestrator:
    """Multi-server MCP orchestration system."""
    
    def __init__(self, servers: List[MCPServer]):
        self.servers = servers
        self.health_monitor = MCPHealthMonitor()
        self.load_balancer = MCPLoadBalancer()
    
    def route_request(self, request: MCPRequest) -> MCPResponse:
        """Route request to appropriate MCP server."""
        available_servers = self.health_monitor.get_healthy_servers()
        selected_server = self.load_balancer.select_server(available_servers, request)
        return selected_server.process_request(request)
    
    def monitor_health(self) -> Dict[str, bool]:
        """Monitor health of all MCP servers."""
        return {server.name: self.health_monitor.check_health(server) 
                for server in self.servers}
```

**Server Implementation Pattern**:
```python
from utils.mcp_integration import MCPServer, MCPConfig, MCPError, DocumentMetadata, ProcessedDocumen

class CustomMCPServer(MCPServer):
    """Custom MCP server for specific document processing."""

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.logger = get_logger("custom_mcp_server")

    def can_handle_source(self, document_source: str) -> bool:
        """Check if this server can handle the document source."""
        return document_source.startswith("custom://")

    def process_document(self, document_source: str, processing_config: dict) -> ProcessedDocument:
        """Process document with custom logic."""
        try:
            # Custom processing logic
            content = self._extract_content(document_source)
            metadata = self._extract_metadata(document_source)

            return ProcessedDocument(
                content=content,
                metadata=metadata,
                source=document_source,
                processing_config=processing_config
            )
        except Exception as e:
            raise MCPError(f"Failed to process document: {e}")
```

**DSPy Integration Pattern**:
```python
from dspy_modules.mcp_document_processor import MCPDocumentProcessor

class CustomDocumentProcessor(MCPDocumentProcessor):
    """Custom document processor with MCP integration."""

    def __init__(self, custom_config: dict = None):
        super().__init__(
            mcp_timeout=30,
            max_file_size=100 * 1024 * 1024
        )
        self.custom_config = custom_config or {}

    def process_document(self, document_source: str, processing_config: dict) -> dict:
        """Process document with custom configuration."""
        # Merge custom config with processing config
        merged_config = {**processing_config, **self.custom_config}
        return super().process_document(document_source, merged_config)
```

**Configuration Standards**:
- **Timeout**: Default 30 seconds, configurable per server
- **File Size**: Default 100MB limit, configurable per server
- **Error Handling**: Graceful degradation with detailed error messages
- **Logging**: Structured logging with appropriate log levels

**Testing Requirements**:
- **Unit Tests**: Test individual server methods
- **Integration Tests**: Test server integration with DSPy
- **Error Tests**: Test error handling and edge cases
- **Performance Tests**: Test with large files and high load
- **Role-Specific Tests**: Test role-aware context for each DSPy role
- **Cursor Integration Tests**: Test Cursor knowledge integration

#### **Role-Specific Context Patterns**

**Purpose**: Standards for implementing role-specific context integration with Cursor knowledge.

**Role Context Implementation Pattern**:
```python
class RoleSpecificMCPServer(MCPServer):
    """MCP server with role-specific context integration."""

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.cursor_knowledge = CursorKnowledgeProvider()

    def get_role_context(self, role: str, task: str, **kwargs) -> dict:
        """Get role-specific context with Cursor knowledge."""
        base_context = self._get_base_context(role, task)
        cursor_context = self._get_cursor_context(role, task, **kwargs)

        return {
            "base_context": base_context,
            "cursor_context": cursor_context,
            "role_specific_guidelines": self._get_role_guidelines(role),
            "enhanced_insights": self._get_enhanced_insights(role, task)
        }

    def _get_cursor_context(self, role: str, task: str, **kwargs) -> dict:
        """Get Cursor-specific knowledge for the role."""
        if role == "coder":
            return self._get_coder_cursor_context(task, **kwargs)
        elif role == "planner":
            return self._get_planner_cursor_context(task, **kwargs)
        elif role == "researcher":
            return self._get_researcher_cursor_context(task, **kwargs)
        elif role == "implementer":
            return self._get_implementer_cursor_context(task, **kwargs)
        else:
            return self._get_generic_cursor_context(task, **kwargs)
```

**Role-Specific Context Standards**:
- **Coder Context**: Language patterns, framework best practices, IDE integration
- **Planner Context**: Architecture knowledge, tech stack analysis, performance insights
- **Researcher Context**: Technology context, pattern analysis, methodology support
- **Implementer Context**: Integration patterns, testing frameworks, deployment knowledge

**Cursor Integration Standards**:
- **Language Knowledge**: Include language-specific patterns and best practices
- **Framework Knowledge**: Include framework-specific conventions and patterns
- **IDE Integration**: Include IDE-specific settings and capabilities
- **File Context**: Include current file and import analysis where relevan

## 🤖 AGENT TOOL INTEGRATION STANDARDS

### **Cursor AI Rules System Integration**

**Purpose**: Integration with Cursor AI Rules System for automated governance and tool discovery.

**Core Features**:
- **Rule Organization**: `.cursor/rules/` directory structure for organized rule management
- **Project Rules**: Memory system, RAGChecker baseline, multi-agent patterns
- **Repository Rules**: Code quality, testing standards, CI/CD enforcement
- **Configuration Rules**: Database standards, UV management, environment setup
- **Workflow Rules**: Task management, execution patterns, quality gates

**Rule Structure**:
```yaml
# .cursor/rules/project/memory_system.mdc
---
description: Enforce memory rehydration protocols and LTST integration
globs:
  - '**/*.py'
  - '**/scripts/**/*'
alwaysApply: true
---

# Memory System Rules
- Always run memory rehydration before major tasks
- Use LTST memory system for cross-session continuity
- Update memory with significant decisions
```

**Integration Benefits**:
- **Automated Enforcement**: Rules automatically applied based on file patterns
- **Consistent Behavior**: Standardized AI behavior across all interactions
- **Governance by Code**: Rules enforced through code rather than documentation
- **Role-Specific Context**: Different rules for different agent roles

### **Agent Tool Discovery Standards**

**Purpose**: Standards for implementing agent tool discovery and integration patterns.

**Core Requirements**:
- **MCP Protocol Compliance**: All tools must expose MCP-compatible interfaces
- **Tool Documentation**: Comprehensive tool descriptions and parameter documentation
- **Role-Specific Tools**: Tools should be designed for specific agent roles
- **Fallback Mechanisms**: Always provide fallback tools for reliability
- **Discovery Automation**: Tools should be automatically discoverable by agents

**Tool Discovery Implementation Pattern**:
```python
class AgentToolDiscovery:
    """Agent tool discovery and integration framework"""

    def __init__(self, mcp_server_url: str = "http://localhost:3000"):
        self.mcp_server_url = mcp_server_url
        self.available_tools = {}
        self.role_tool_mappings = {}

    def discover_tools(self) -> dict:
        """Discover available MCP tools"""
        try:
            response = requests.get(f"{self.mcp_server_url}/mcp")
            mcp_info = response.json()

            self.available_tools = {
                tool["name"]: tool for tool in mcp_info["tools"]
            }

            return {
                "server_name": mcp_info["name"],
                "version": mcp_info["version"],
                "available_tools": len(self.available_tools),
                "tools": list(self.available_tools.keys())
            }
        except Exception as e:
            raise Exception(f"Tool discovery failed: {e}")

    def map_tools_to_roles(self) -> dict:
        """Map available tools to agent roles"""
        role_mappings = {
            "coder": ["get_cursor_context", "rehydrate_memory"],
            "planner": ["get_planner_context", "rehydrate_memory"],
            "researcher": ["get_researcher_context", "rehydrate_memory"],
            "implementer": ["get_implementer_context", "rehydrate_memory"]
        }

        self.role_tool_mappings = {}
        for role, tool_names in role_mappings.items():
            available_tools = [
                tool_name for tool_name in tool_names
                if tool_name in self.available_tools
            ]
            self.role_tool_mappings[role] = available_tools

        return self.role_tool_mappings

# Example usage
discovery = AgentToolDiscovery()
tools_info = discovery.discover_tools()
role_mappings = discovery.map_tools_to_roles()
```

### **Agent Decision-Making Standards**

**Purpose**: Standards for implementing agent decision-making and tool selection logic.

**Core Requirements**:
- **Task Analysis**: Agents must analyze tasks before tool selection
- **Role Awareness**: Agents must be aware of their role and capabilities
- **Context Enhancement**: Agents must enhance context before tool execution
- **Error Handling**: Agents must handle tool failures gracefully
- **Performance Monitoring**: Agents must monitor tool usage and performance

**Agent Decision-Making Implementation Pattern**:
```python
class AgentDecisionMaker:
    """Agent decision-making and tool selection framework"""

    def __init__(self, role: str, available_tools: dict):
        self.role = role
        self.available_tools = available_tools
        self.decision_history = []

    def analyze_task(self, task: str) -> dict:
        """Analyze task to determine appropriate tools and approach"""

        # Task analysis patterns
        analysis_patterns = {
            "coder": {
                "keywords": ["code", "implement", "develop", "debug", "test"],
                "primary_tool": "get_cursor_context",
                "context_focus": ["language_patterns", "framework_knowledge"]
            },
            "planner": {
                "keywords": ["plan", "strategy", "architecture", "design"],
                "primary_tool": "get_planner_context",
                "context_focus": ["architecture_knowledge", "tech_stack_analysis"]
            },
            "researcher": {
                "keywords": ["research", "analyze", "investigate", "study"],
                "primary_tool": "get_researcher_context",
                "context_focus": ["technology_context", "pattern_analysis"]
            },
            "implementer": {
                "keywords": ["implement", "integrate", "deploy", "configure"],
                "primary_tool": "get_implementer_context",
                "context_focus": ["integration_patterns", "deployment_knowledge"]
            }
        }

        pattern = analysis_patterns.get(self.role, analysis_patterns["coder"])
        task_lower = task.lower()

        # Analyze task for pattern keywords
        keyword_matches = [
            keyword for keyword in pattern["keywords"]
            if keyword in task_lower
        ]

        # Determine tool selection
        if keyword_matches and pattern["primary_tool"] in self.available_tools:
            selected_tool = pattern["primary_tool"]
            reasoning = f"Task contains keywords: {keyword_matches}"
        else:
            selected_tool = "rehydrate_memory"
            reasoning = "No specific keywords found, using fallback tool"

        decision = {
            "task": task,
            "role": self.role,
            "selected_tool": selected_tool,
            "context_focus": pattern["context_focus"],
            "keyword_matches": keyword_matches,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }

        self.decision_history.append(decision)
        return decision

    def get_decision_history(self) -> list:
        """Get decision history for analysis"""
        return self.decision_history

# Example usage
decision_maker = AgentDecisionMaker("coder", {"get_cursor_context": {}, "rehydrate_memory": {}})
decision = decision_maker.analyze_task("Implement a new feature with proper testing")
```

### **Agent Context Enhancement Standards**

**Purpose**: Standards for implementing agent context enhancement and integration patterns.

**Core Requirements**:
- **Multi-Layer Context**: Implement layered context enhancemen
- **Role-Specific Enhancement**: Enhance context based on agent role
- **Cursor Integration**: Integrate Cursor knowledge where appropriate
- **Performance Optimization**: Optimize context enhancement for speed
- **Quality Validation**: Validate enhanced context quality

**Context Enhancement Implementation Pattern**:
```python
class AgentContextEnhancer:
    """Agent context enhancement and integration framework"""

    def __init__(self, role: str):
        self.role = role
        self.enhancement_layers = self._get_enhancement_layers()

    def _get_enhancement_layers(self) -> list:
        """Get enhancement layers for the role"""
        layer_mappings = {
            "coder": [
                "language_specific_patterns",
                "framework_best_practices",
                "ide_integration_context",
                "file_context_analysis"
            ],
            "planner": [
                "architecture_knowledge",
                "tech_stack_analysis",
                "performance_insights",
                "strategic_context"
            ],
            "researcher": [
                "technology_context",
                "pattern_analysis",
                "methodology_support",
                "research_context"
            ],
            "implementer": [
                "integration_patterns",
                "testing_frameworks",
                "deployment_knowledge",
                "implementation_context"
            ]
        }

        return layer_mappings.get(self.role, layer_mappings["coder"])

    def enhance_context(self, base_context: str, task: str, **kwargs) -> str:
        """Enhance context with role-specific layers"""

        enhanced_context = f"""# Enhanced Context for {self.role.title()} Role

## 🎯 Task Context
{task}

## 📚 Base Context
{base_context}

## 🧠 Enhanced Context Layers
"""

        for layer in self.enhancement_layers:
            layer_content = self._get_layer_content(layer, **kwargs)
            enhanced_context += f"""
### {layer.replace('_', ' ').title()}
{layer_content}
"""

        return enhanced_contex

    def _get_layer_content(self, layer: str, **kwargs) -> str:
        """Get content for a specific enhancement layer"""

        layer_content = {
            "language_specific_patterns": """
- Python: PEP 8, type hints, async/await patterns
- JavaScript: ES6+, modules, async/awai
- TypeScript: Type system, interfaces, generics
- Best practices for each language""",

            "framework_best_practices": """
- DSPy: Signatures, modules, optimizers
- FastAPI: Pydantic, dependencies, async support
- Node.js: Express, middleware, error handling
- Framework-specific conventions and patterns""",

            "ide_integration_context": """
- Cursor AI settings and capabilities
- File context and import analysis
- Development environment configuration
- IDE-specific best practices""",

            "architecture_knowledge": """
- System architecture patterns
- Microservices vs monolith decisions
- Scalability and performance considerations
- Technology stack integration patterns""",

            "tech_stack_analysis": """
- Current technology stack overview
- Framework and library dependencies
- Integration points and APIs
- Technology stack optimization opportunities""",

            "performance_insights": """
- Current performance bottlenecks
- Optimization strategies and techniques
- Monitoring and profiling approaches
- Performance best practices""",

            "integration_patterns": """
- API integration patterns
- Data flow and synchronization
- Error handling and retry logic
- Integration testing strategies""",

            "testing_frameworks": """
- Unit testing frameworks and patterns
- Integration testing approaches
- Test-driven development practices
- Testing best practices and conventions""",

            "deployment_knowledge": """
- Deployment environments and strategies
- CI/CD pipeline configuration
- Environment-specific configurations
- Deployment best practices and rollback strategies"""
        }

        return layer_content.get(layer, f"- Enhanced context for {layer}\n- Role-specific insights and patterns\n- Best practices and guidelines")

# Example usage
enhancer = AgentContextEnhancer("coder")
enhanced_context = enhancer.enhance_context(
    "Basic project context",
    "Implement a new feature",
    language="python",
    framework="dspy"
)
```

### **Agent Error Handling Standards**

**Purpose**: Standards for implementing agent error handling and fallback mechanisms.

**Core Requirements**:
- **Graceful Degradation**: Handle failures without complete system failure
- **Fallback Mechanisms**: Provide alternative approaches when primary methods fail
- **Error Logging**: Comprehensive error logging and monitoring
- **Recovery Strategies**: Implement recovery strategies for different failure types
- **User Communication**: Clear communication about errors and fallbacks

**Error Handling Implementation Pattern**:
```python
class AgentErrorHandler:
    """Agent error handling and fallback framework"""

    def __init__(self, role: str):
        self.role = role
        self.error_history = []

    def handle_tool_discovery_failure(self, task: str, error: str) -> str:
        """Handle tool discovery failures"""

        fallback_context = f"""# Tool Discovery Failure - Fallback Context

## ⚠️ Tool Discovery Error
{error}

## 🎯 Task
{task}

## 📚 Fallback Context
Using basic memory rehydration due to tool discovery failure.

## 💡 Instructions
- Focus on your role as a {self.role}
- Use basic project context and guidelines
- Apply appropriate best practices for your role
- Document any limitations or assumptions made"""

        self.error_history.append({
            "error_type": "tool_discovery_failure",
            "task": task,
            "error": error,
            "fallback_used": True,
            "timestamp": datetime.now().isoformat()
        })

        return fallback_contex

    def handle_memory_rehydration_failure(self, task: str, error: str) -> str:
        """Handle memory rehydration failures"""

        role_fallbacks = {
            "coder": """# Coder Fallback Context
You are a Python developer working on an AI development ecosystem.
Focus on clean, maintainable code with proper testing and documentation.
Use PEP 8 standards and follow project conventions.""",

            "planner": """# Planner Fallback Context
You are a strategic planner for an AI development ecosystem.
Focus on architecture, scalability, and long-term planning.
Consider system design and technology stack decisions.""",

            "researcher": """# Researcher Fallback Context
You are a researcher for an AI development ecosystem.
Focus on evidence-based analysis and systematic evaluation.
Use research methodologies and document findings.""",

            "implementer": """# Implementer Fallback Context
You are a system implementer for an AI development ecosystem.
Focus on robust implementation, integration, and deployment.
Follow implementation best practices and testing strategies."""
        }

        fallback_context = role_fallbacks.get(self.role, role_fallbacks["coder"])

        self.error_history.append({
            "error_type": "memory_rehydration_failure",
            "task": task,
            "error": error,
            "fallback_used": True,
            "timestamp": datetime.now().isoformat()
        })

        return fallback_contex

    def get_error_history(self) -> list:
        """Get error history for analysis"""
        return self.error_history

# Example usage
error_handler = AgentErrorHandler("coder")
fallback_context = error_handler.handle_tool_discovery_failure(
    "Implement a new feature",
    "MCP server connection failed"
)
```

## 🔗 Related Guides

- **Memory System Overview**: `400_guides/400_00_memory-system-overview.md`
- **System Architecture**: `400_guides/400_03_system-overview-and-architecture.md`
- **Development Workflow**: `400_guides/400_04_development-workflow-and-standards.md`
- **Memory Systems**: `400_guides/400_01_memory-system-architecture.md`
?
- **AI Frameworks**: `400_guides/400_09_ai-frameworks-dspy.md` (MCP integration)
- **Integrations**: `400_guides/400_10_integrations-models.md` (MCP servers)

## 🔧 **Technical Artifacts Integration**

### **🚨 CRITICAL: Technical Artifacts Integration is Essential**

**Why This Matters**: Technical artifacts (code components, shell scripts, dashboards, implementation patterns) are the foundation of the system's functionality. Without proper integration into memory context, AI agents cannot provide accurate technical guidance or understand the current system state.

### **Core Technical Artifacts**

#### **1. Critical Scripts & Automation**

**Memory System Scripts**:
```bash
# Core memory orchestration
scripts/unified_memory_orchestrator.py          # Primary memory system orchestrator
scripts/memory_up.sh                            # Static documentation bundling
scripts/ragchecker_evaluation.py                # RAGChecker evaluation framework
scripts/memory_rehydrate.py                     # Memory rehydration utilities

# AWS Bedrock Integration (B-1046)
scripts/bedrock_client.py                       # AWS Bedrock client implementation
scripts/bedrock_cost_monitor.py                 # Cost monitoring and budget managemen
scripts/bedrock_batch_processor.py              # Batch processing for evaluations
scripts/ragchecker_official_evaluation.py       # Official RAGChecker with Bedrock support
scripts/ragchecker_with_monitoring.py           # RAGChecker with cost monitoring
scripts/ragchecker_batch_evaluation.py          # Batch evaluation with Bedrock
scripts/bedrock_connection_test.py              # Bedrock connection testing
scripts/bedrock_setup_guide.py                  # AWS Bedrock setup guide

# MCP Integration
scripts/mcp_memory_server.py                    # LEGACY - MCP memory server implementation (Replaced by Production Framework)
scripts/mcp_orchestrator.py                     # MCP orchestration system
scripts/mcp_security_config.py                  # MCP security configuration
scripts/mcp_advanced_orchestration.py           # Advanced MCP orchestration

# Development Environmen
scripts/venv_manager.py                         # Virtual environment managemen
scripts/system_monitor.py                       # System monitoring and health checks
scripts/update_cursor_memory.py                 # Cursor memory updates
scripts/validate_config.py                      # Configuration validation
```

**Development Workflow Scripts**:
```bash
# Task Managemen
scripts/task_generation_automation.py           # Automated task generation
scripts/task_generator.py                       # Task generation utilities
scripts/task_status_updater.py                  # Task status managemen

# Quality Assurance
scripts/validate_dependencies.py                # Dependency validation
scripts/validate_regen_guide.py                 # Guide regeneration validation
scripts/performance_optimization.py             # Performance optimization utilities

# Documentation Managemen
scripts/add_tldr_sections.py                    # TL;DR section managemen
scripts/fix_duplicate_tldr.py                   # Duplicate TL;DR cleanup
scripts/documentation_usage_analyzer.py         # Documentation usage analysis
```

#### **2. DSPy RAG System Components**

**Core System Files**:
```bash
# Main System
src/dashboard.py                # Main dashboard interface
src/watch_folder.py             # File watching and processing
dspy-rag-system/README.md                       # System documentation

# CLI Components
src/cli/                        # Command-line interface components
src/utils/                      # Utility functions and helpers

# DSPy Modules
src/dspy_modules/               # DSPy framework modules
src/workflows/                  # Workflow implementations
src/monitoring/                 # Monitoring and observability
```

**Go Implementation**:
```bash
# Go Memory Rehydration
src/utils/memory_rehydration.go     # Core Go implementation
```

### **Technical Artifacts Integration Patterns**

#### **Memory Context Integration**
```python
class TechnicalArtifactsIntegrator:
    """Integrates technical artifacts into memory context."""

    def __init__(self):
        self.artifact_registry = {}
        self.integration_patterns = {}
        self.memory_hooks = {}

    def register_artifact(self, artifact_id: str, artifact_info: dict) -> bool:
        """Register a technical artifact for memory integration."""

        # Validate artifact information
        if not self._validate_artifact_info(artifact_info):
            return False

        # Register artifac
        self.artifact_registry[artifact_id] = artifact_info

        # Create memory hooks
        self._create_memory_hooks(artifact_id, artifact_info)

        return True

    def _validate_artifact_info(self, artifact_info: dict) -> bool:
        """Validate technical artifact information."""

        required_fields = ["name", "type", "path", "purpose", "dependencies"]

        for field in required_fields:
            if field not in artifact_info:
                return False

        return True

    def _create_memory_hooks(self, artifact_id: str, artifact_info: dict):
        """Create memory system hooks for the artifact."""

        # Create context hooks
        context_hook = {
            "type": "context_integration",
            "artifact_id": artifact_id,
            "integration_points": ["memory_rehydration", "context_building"],
            "priority": artifact_info.get("priority", "medium")
        }

        self.memory_hooks[f"{artifact_id}_context"] = context_hook

        # Create usage hooks
        usage_hook = {
            "type": "usage_tracking",
            "artifact_id": artifact_id,
            "tracking_points": ["execution", "performance", "errors"],
            "metrics": ["usage_count", "success_rate", "performance_metrics"]
        }

        self.memory_hooks[f"{artifact_id}_usage"] = usage_hook
```

#### **Artifact Discovery & Integration**
```python
class ArtifactDiscoveryEngine:
    """Discovers and integrates technical artifacts automatically."""

    def __init__(self):
        self.discovery_patterns = [
            "scripts/*.py",
            "src/**/*.py",
            "400_guides/*.md",
            "100_memory/*.md"
        ]
        self.integration_rules = {}

    async def discover_artifacts(self) -> List[dict]:
        """Discover technical artifacts in the codebase."""

        discovered_artifacts = []

        for pattern in self.discovery_patterns:
            artifacts = await self._discover_by_pattern(pattern)
            discovered_artifacts.extend(artifacts)

        return discovered_artifacts

    async def _discover_by_pattern(self, pattern: str) -> List[dict]:
        """Discover artifacts matching a specific pattern."""

        # Implementation for pattern-based discovery
        artifacts = []

        # Example discovery logic
        if pattern == "scripts/*.py":
            artifacts = await self._discover_script_artifacts()
        elif pattern == "src/**/*.py":
            artifacts = await self._discover_dspy_artifacts()
        elif pattern == "400_guides/*.md":
            artifacts = await self._discover_guide_artifacts()
        elif pattern == "100_memory/*.md":
            artifacts = await self._discover_memory_artifacts()

        return artifacts

    async def _discover_script_artifacts(self) -> List[dict]:
        """Discover script artifacts in the scripts directory."""

        script_artifacts = []

        # Example script artifacts
        script_artifacts.append({
            "id": "unified_memory_orchestrator",
            "name": "Unified Memory Orchestrator",
            "type": "script",
            "path": "scripts/unified_memory_orchestrator.py",
            "purpose": "Primary memory system orchestrator",
            "dependencies": ["memory_systems", "dspy_framework"],
            "priority": "critical",
            "integration_points": ["memory_rehydration", "context_management"]
        })

        return script_artifacts
```

### **Technical Artifacts Management Commands**

#### **Artifact Discovery & Integration**
```bash
# Discover technical artifacts
python3 scripts/discover_artifacts.py --pattern "scripts/*.py" --output artifacts_discovered.json

# Integrate artifacts into memory context
python3 scripts/integrate_artifacts.py --artifacts artifacts_discovered.json

# Validate artifact integration
python3 scripts/validate_artifact_integration.py --full-check

# Generate artifact documentation
python3 scripts/generate_artifact_docs.py --output technical_artifacts_guide.md
```

#### **Artifact Health Monitoring**
```bash
# Check artifact health
python3 scripts/check_artifact_health.py --all

# Monitor artifact usage
python3 scripts/monitor_artifact_usage.py --timeframe 7d

# Validate artifact dependencies
python3 scripts/validate_artifact_dependencies.py --stric
```

### **Integration Quality Gates**

#### **Artifact Integration Standards**
- **Discovery Coverage**: 100% of technical artifacts must be discovered
- **Memory Integration**: All artifacts must have memory system hooks
- **Documentation Quality**: All artifacts must have clear purpose and usage documentation
- **Dependency Validation**: All artifact dependencies must be validated

#### **Integration Validation Requirements**
- **Context Integration**: Artifacts must integrate with memory context system
- **Usage Tracking**: Artifacts must support usage monitoring and metrics
- **Error Handling**: Artifacts must have proper error handling and recovery
- **Performance Monitoring**: Artifacts must support performance tracking

## 📝 NAMING CONVENTIONS & FILE ORGANIZATION

<!-- ANCHOR_KEY: naming-conventions -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["coder", "implementer"] -->

### **TL;DR**
File and directory naming standards for the project. Apply conventions to new files and update existing ones.

### **🔢 Prefix Category Table**

This table clarifies the buckets for our numeric prefixes, making it easier to categorize and find files.

| Prefix Range | Category Name                 | Purpose                                                                 | Examples                                                              |
| :----------- | :---------------------------- | :---------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| `000-099` | Core Workflow & Planning | Core processes, backlog, PRDs, and high-level project plans. | `000_core/000_backlog.md`, `000_core/001_create-prd.md` |
| `100-199` | Guides & Automation | Memory context, workflow guides, and automation tools. | `100_memory/100_cursor-memory-context.md`, `100_memory/100_backlog-guide.md` |
| `200-299` | Configuration & Setup | Environment setup, naming conventions, and tool configuration. | `200_setup/202_setup-requirements.md`, `400_guides/400_05_codebase-organization-patterns.md` |
| `300-399` | Templates & Examples | Reusable templates, documentation examples, and few-shot prompts. | `300_examples/300_documentation-example.md`, `400_guides/400_few-shot-context-examples.md` |
| `400-499` | System Architecture & Overviews | High-level system design, project overviews, and context guides. | `400_guides/400_system-overview.md`, `400_guides/400_project-overview.md` |
| `500-599` | Research, Testing & Analysis | Research, benchmarks, testing, observability, and completion summaries. | `500_research/500_dspy-research.md`, `500_test-harness-guide.md` |
| `600-999` | Archives & Legacy | Deprecated files, historical archives, and legacy documentation. | `600_archives/`, `docs/legacy/` |

### **🔄 File Generation Workflow**

#### **⭐ CANON RULE: All Guides Go in Root with 400_ Prefix**

**This is absolute canon and non-negotiable:**

- **ALL guides** must use `400_` prefix
- **ALL guides** must be in the **root directory**
- **NO guides** in subdirectories (docs/, processed_documents/, etc.)
- **NO exceptions** - this is enforced by the naming system

**Examples of correct guide placement:**
- ✅ `400_00_memory-system-overview.md` (root)
- ✅ `400_03_system-overview-and-architecture.md` (root)
- ✅ `400_04_development-workflow-and-standards.md` (root)
- ✅ `400_09_ai-frameworks-dspy.md` (root)

**Examples of incorrect guide placement:**
- ❌ `docs/400_guide.md` (subdirectory)
- ❌ `processed_documents/400_guide.md` (subdirectory)
- ❌ `400_guides/400_guide.md` (subdirectory)

#### **Step 1: Determine if a File is Needed**

**Ask these questions:**
- **Is this information that will be referenced multiple times?** (If yes → file)
- **Is this a process or workflow that others/AI will need to follow?** (If yes → file)
- **Is this context that will help with future decisions?** (If yes → file)
- **Is this a one-off note or temporary information?** (If no → don't create file)

#### **Step 2: Choose the Right Prefix Range**

**000-099: Core Planning & Context**
- Backlog, project overview, system overview
- Files that give immediate understanding of the project
- Essential for anyone working on the project

**100-199: Memory & Guides**
- Memory context, backlog guide, automation patterns
- Files that help with ongoing work and decision-making
- Important for regular development activities

**200-299: Configuration & Setup**
- Naming conventions, model config, setup requirements
- Files that help with environment and tool setup
- Important when setting up or configuring

**400-499: Architecture & Overview** ⭐ **CANON RULE**
- System overview, project overview, context priority guide
- **ALL guides go in root directory with 400_ prefix**
- Files that explain the big picture and relationships
- Essential for understanding the system architecture
- **NO guides in subdirectories - this is canon**

**500+: Research & Meta**
- Completion summaries, research notes, benchmarks
- Files that provide historical context and analysis
- Useful for learning from past work

#### **Step 3: Create Descriptive, Self-Documenting Names**

**Follow these naming principles:**
- **Clear purpose**: The name should indicate what the file contains
- **Consistent format**: `prefix_descriptive-name.md`
- **Kebab-case**: Lowercase with hyphens for readability
- **Avoid ambiguity**: Make it clear what the file is for

**Examples of good names:**
- ✅ `100_memory/100_cursor-memory-context.md` (clear purpose)
- ✅ `400_guides/400_system-overview.md` (descriptive)
- ✅ `500_research/500_memory-arch-research.md` (research focus)

**Examples of bad names:**
- ❌ `misc.md` (unclear purpose)
- ❌ `stuff.md` (not descriptive)
- ❌ `temp.md` (temporary feeling)

### **📝 File Naming Rules**

#### **✅ Correct Examples**
- `000_core/000_backlog.md` (three-digit prefix, single underscore, kebab-case)
- `100_memory/100_cursor-memory-context.md` (automation category)
- `400_guides/400_project-overview.md` (documentation category)
- `500_test-harness-guide.md` (testing category)

#### **❌ Incorrect Examples**
- `99_misc.md` (needs three-digit prefix)
- `100_backlog_automation.md` (second underscore disallowed)
- `100-backlog-automation.md` (missing required first underscore)

### **📝 Formatting Standards**

#### **Header Structure Rules**
- **Single h1 per document**: Use filename as the implicit h1 title
- **Main content starts with h2**: `## 🎯 Current Status` or `## 📋 Overview`
- **Consistent emoji usage**: Use emojis for visual hierarchy and AI parsing
- **No h1 in content**: All content headings should be h2 or lower
- **Hierarchical structure**: Use h2 for main sections, h3 for subsections, h4 for details

### **🔐 Core Documentation Invariants**

**Purpose**: Single normative source for core documentation requirements. Validator enforces these invariants.

#### **Required top metadata header (HTML comments)**
- HIGH‑priority docs must include:
  - `<!-- CONTEXT_REFERENCE: <file> -->`
  - `<!-- MEMORY_CONTEXT: <LEVEL> - <description> -->`
- `MODULE_REFERENCE` is required when a closely related implementation module exists.

#### **TL;DR + At‑a‑glance**
- TL;DR section is required in core docs
  - A single explicit anchor is allowed: `{#tldr}`
  - Heading: `## 🔎 TL;DR`
- Immediately after TL;DR, include a 3‑column "At‑a‑glance" table with exact headers:

| what this file is | read when | do next |
|---|---|---|
|_one‑line purpose_|_trigger moments_|_2–3 links/actions_ |

#### **Stable Anchors (kebab‑case)**
- Required anchors per doc type (must exist as section anchors):
  - `100_memory/100_cursor-memory-context.md`: `tldr`, `quick-start`, `quick-links`, `commands`
  - `400_guides/400_project-overview.md`: `tldr`, `quick-start`, `mini-map`
  - `400_guides/400_context-priority-guide.md`: `tldr`, `critical-path`, `ai-file-analysis-strategy`, `documentation-placement-logic`
  - `000_core/000_backlog.md`: `tldr`, `p0-lane`, `ai-executable-queue-003`, `live-backlog`
  - `400_guides/400_05_codebase-organization-patterns.md`: `tldr`, `naming-conventions`, `formatting-standards`, `ai-api-standards`
  - `100_memory/100_backlog-guide.md`: `tldr`, `scoring`, `prd-rule`, `selection-criteria`

#### **Table Usage Mandate**
Markdown tables are the **required standard** for presenting structured data:
- **Status tracking**: Use tables for backlog items, task lists, and progress tracking
- **Decision records**: Structure decisions with clear columns for date, decision, rationale, impact
- **Priority matrices**: Use tables for comparing options or categorizing items
- **Stakeholder information**: Organize roles, responsibilities, and contact information
- **Cross-reference matrices**: Map relationships between files and components

#### **Internal Linking Standards**
- **Primary method**: Use auto-generated heading IDs `[Link Text](#-section-title)`
- **Critical sections**: Allow explicit IDs for stability `[Link Text](#explicit-id)`
- **Cross-file linking**: Use relative paths with anchor links
- **AI-friendly linking**: Include context in link text for better AI parsing
- **Validation**: Ensure all referenced sections exist

### **🤖 AI API Standards**

The HTML comments in our documentation serve as a **formal API for AI consumption**. These comments enable cognitive scaffolding and context rehydration.

#### **Core Comment Types**

| Key | Purpose | Example | Required For |
| :--- | :--- | :--- | :--- |
| CONTEXT_REFERENCE | Links to the main guide for context | `<!-- CONTEXT_REFERENCE: 400_guides/400_system-overview.md -->` | HIGH priority files |
| MODULE_REFERENCE | Links to a related implementation module | `<!-- MODULE_REFERENCE: src/utils/memory_rehydrator.py -->` | MEDIUM priority files |
| MEMORY_CONTEXT | Specifies priority level for AI rehydration | `<!-- MEMORY_CONTEXT: HIGH - Core system overview -->` | All files |
| ESSENTIAL_FILES | Lists files critical for understanding | `<!-- ESSENTIAL_FILES: 400_guides/400_project-overview.md -->` | HIGH priority files |

#### **Usage Patterns**
- **HIGH priority files**: Must include CONTEXT_REFERENCE and MEMORY_CONTEXT
- **MEDIUM priority files**: Should include MODULE_REFERENCE and MEMORY_CONTEXT
- **Cross-references**: Always validate that referenced files exist
- **Consistency**: Use consistent comment patterns across similar file types

### **📋 PRD Lifecycle Management**

#### **PRD Naming Convention**
- **Active PRDs**: `PRD-{BacklogID}-{Descriptive-Name}.md`
  - Example: `PRD-B-084-Research-Based-Schema-Design.md`
  - Location: `000_core/` while project is active
- **Completed PRDs**: Move to `600_archives/prds/` with metadata preservation
  - Keep original filename for traceability
  - Add completion metadata to preserve insights

#### **Doorway Artifacts (Active vs Archive)**
The single doorway system creates standardized artifacts with deterministic naming:

**Active Artifacts** (in `000_core/`)
- **PRDs**: `PRD-{BacklogID}-{Slug}.md`
  - Example: `PRD-B-108-Single-Doorway-System.md`
- **Task Lists**: `TASKS-{BacklogID}-{Slug}.md`
  - Example: `TASKS-B-108-Single-Doorway-System.md`
- **Execution Logs**: `RUN-{BacklogID}-{Slug}.md`
  - Example: `RUN-B-108-Single-Doorway-System.md`

**Versioning for Conflicts**
- If same-day files exist, append `-v2`, `-v3`, etc.
- Example: `PRD-B-108-Single-Doorway-System-v2.md`

**Archive Structure** (in `600_archives/`)
- **PRDs**: `600_archives/prds/PRD-{BacklogID}-{Slug}.md`
- **Task Lists**: `600_archives/tasks/TASKS-{BacklogID}-{Slug}.md`
- **Execution Logs**: `600_archives/runs/RUN-{BacklogID}-{Slug}_{YYYY-MM-DD}.md`

### **🛠️ Implementation Tools**

#### **Collision Detection**
The `scripts/check-number-unique.sh` script runs as a warning-only pre-commit hook to detect duplicate numeric prefixes in HIGH priority files (000-099, 400-499, 500-599).

#### **Memory Hierarchy Display**
Use `python3 scripts/show_memory_hierarchy.py` to display the current memory context hierarchy for human understanding.

#### **Memory Context Updates**
Use `python3 scripts/update_cursor_memory.py` to automatically update memory context based on backlog priorities.

#### **Evaluation Profiles**
**Profiles**: `real`, `gold`, `mock` (single responsibility)
- Env files: `300_evals/configs/profiles/{profile}.env`
- Entry scripts: `scripts/eval_{profile}.sh`
- Orchestrator: `scripts/ragchecker_official_evaluation.py` (uses `--profile`)

**Output folders**:
`metrics/runs/{YYYYMMDD_HHMMSS}__{profile}__driver-{driver}__f1-{f1}__p-{p}__r-{r}/`

**Never** use `mock` for baselines or main branch.

## 📚 References

- **Migration Map**: `migration_map.csv`
- **PRD**: `artifacts/prd/PRD-B-1035-400_guides-Consolidation.md`
- **Original Standards**: Various coding and prompting files (now stubs)
- **Performance Baselines**: System performance benchmarks and targets
- **Error Reduction Tools**: Smart error fix scripts and decision matrices

### **🧪 Testing & Methodology Documentation**

**Testing Infrastructure Guide**: `300_experiments/300_testing-infrastructure-guide.md`
- **Purpose**: Complete guide to testing environment and tools
- **Coverage**: Environment setup, testing workflows, debugging, CI/CD integration

**Testing Methodology Log**: `300_experiments/300_testing-methodology-log.md`
- **Purpose**: Central hub for all testing strategies and methodologies
- **Coverage**: Testing approaches, methodology evolution, key insights, performance tracking

**Code Organization Testing**: `300_experiments/300_integration-testing-results.md`
- **Purpose**: Testing for system integration and cross-component functionality
- **Coverage**: End-to-end workflows, error handling, performance integration

**Comprehensive Testing Coverage**: `300_experiments/300_complete-testing-coverage.md`
- **Purpose**: Complete overview of all testing and methodology coverage
- **Coverage**: Navigation guide, usage instructions, best practices

## 🏗️ **Architecture & Design Patterns**

### **🚨 CRITICAL: Architecture & Design Patterns are Essential**

**Why This Matters**: Architecture and design patterns provide the foundation for building scalable, maintainable, and efficient systems. Without proper architectural patterns, code becomes difficult to understand, maintain, and extend.

### **Architectural Patterns**

#### **Layered Architecture**
```python
class LayeredArchitecture:
    """Implements layered architecture pattern for system organization."""

    def __init__(self):
        self.layers = {
            "presentation": "User interface and interaction layer",
            "business": "Business logic and domain services layer",
            "data": "Data access and persistence layer",
            "infrastructure": "Infrastructure and cross-cutting concerns layer"
        }
        self.layer_dependencies = {}

    def organize_layers(self, system_components: dict) -> dict:
        """Organize system components into appropriate layers."""

        organized_layers = {}

        for layer_name, layer_description in self.layers.items():
            layer_components = self._identify_layer_components(
                system_components, layer_name
            )
            organized_layers[layer_name] = {
                "description": layer_description,
                "components": layer_components,
                "dependencies": self._identify_layer_dependencies(layer_name)
            }

        return organized_layers

    def _identify_layer_components(self, system_components: dict, layer_name: str) -> list:
        """Identify components that belong to a specific layer."""

        # Implementation for component identification
        return [
            component for component, metadata in system_components.items()
            if metadata.get("layer") == layer_name
        ]

    def _identify_layer_dependencies(self, layer_name: str) -> list:
        """Identify dependencies for a specific layer."""

        # Implementation for dependency identification
        if layer_name == "presentation":
            return ["business"]
        elif layer_name == "business":
            return ["data"]
        elif layer_name == "data":
            return ["infrastructure"]
        else:
            return []
```

#### **Microservices Architecture**
```python
class MicroservicesArchitecture:
    """Implements microservices architecture pattern."""

    def __init__(self):
        self.service_patterns = {
            "api_gateway": "Centralized API gateway for service communication",
            "service_discovery": "Service discovery and registration",
            "load_balancing": "Load balancing and routing",
            "circuit_breaker": "Circuit breaker for fault tolerance"
        }
        self.services = {}

    def design_service(self, service_name: str, service_spec: dict) -> dict:
        """Design a microservice according to specifications."""

        # Validate service specification
        if not self._validate_service_spec(service_spec):
            raise ValueError("Invalid service specification")

        # Design service architecture
        service_design = self._create_service_design(service_name, service_spec)

        # Define service boundaries
        service_boundaries = self._define_service_boundaries(service_design)

        # Design service interfaces
        service_interfaces = self._design_service_interfaces(service_design)

        return {
            "service_name": service_name,
            "design": service_design,
            "boundaries": service_boundaries,
            "interfaces": service_interfaces
        }

    def _validate_service_spec(self, service_spec: dict) -> bool:
        """Validate service specification completeness."""

        required_fields = ["responsibilities", "dependencies", "interfaces"]

        for field in required_fields:
            if field not in service_spec:
                return False

        return True
```

### **Design Patterns**

#### **Creational Patterns**
```python
class CreationalPatterns:
    """Implements common creational design patterns."""

    def __init__(self):
        self.patterns = {
            "factory": "Factory pattern for object creation",
            "singleton": "Singleton pattern for single instance",
            "builder": "Builder pattern for complex object construction",
            "prototype": "Prototype pattern for object cloning"
        }

    def apply_factory_pattern(self, product_type: str, product_config: dict) -> object:
        """Apply factory pattern for product creation."""

        # Create factory
        factory = self._create_factory(product_type)

        # Configure factory
        factory.configure(product_config)

        # Create produc
        product = factory.create_product()

        return produc

    def apply_singleton_pattern(self, class_name: str) -> object:
        """Apply singleton pattern for single instance."""

        # Implementation for singleton pattern
        if not hasattr(self, f"_{class_name}_instance"):
            setattr(self, f"_{class_name}_instance", self._create_instance(class_name))

        return getattr(self, f"_{class_name}_instance")
```

### **Architecture Commands**

#### **Architecture Design Commands**
```bash
# Design layered architecture
python3 scripts/design_layered_architecture.py --components system_components.yaml --output architecture_design.md

# Design microservice
python3 scripts/design_microservice.py --service-name "user-service" --spec service_spec.yaml

# Validate architecture
python3 scripts/validate_architecture.py --architecture-file architecture.yaml --full-check

# Generate architecture documentation
python3 scripts/generate_architecture_docs.py --output architecture_documentation.md
```

#### **Pattern Application Commands**
```bash
# Apply design pattern
python3 scripts/apply_design_pattern.py --pattern factory --class-name "ProductFactory"

# Validate pattern implementation
python3 scripts/validate_pattern.py --pattern singleton --class-name "DatabaseConnection"

# Generate pattern documentation
python3 scripts/generate_pattern_docs.py --pattern all --output pattern_documentation.md

# Analyze pattern usage
python3 scripts/analyze_pattern_usage.py --codebase-path src/ --output pattern_analysis.md
```

### **Architecture Quality Gates**

#### **Architecture Standards**
- **Layer Separation**: Clear separation between architectural layers
- **Dependency Management**: Proper dependency direction and managemen
- **Service Boundaries**: Clear and well-defined service boundaries
- **Interface Design**: Clean and consistent interface design

#### **Pattern Requirements**
- **Pattern Appropriateness**: Patterns must be appropriate for the use case
- **Implementation Quality**: Pattern implementation must be correct and efficien
- **Documentation**: All patterns must be properly documented
- **Testing**: Pattern implementations must be thoroughly tested          

## 🛡️ Governance-by-Code Insights

<!-- ANCHOR_KEY: governance-by-code-insights -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

### **TL;DR**
Key insights from transitioning from governance-by-documentation to governance-by-code. Apply these principles to CI/CD implementation and future governance decisions.

### **🎯 Core Governance-by-Code Principles**

#### **1. Single Source of Truth = CI**
- **Principle**: Docs explain; CI enforces
- **Application**: All governance rules must be automated in CI/CD pipelines
- **Avoid**: Manual checklists or documentation-only enforcement

#### **2. Automated Enforcement Over Documentation**
- **Principle**: Code that enforces is more reliable than docs that describe
- **Application**: Implement automated checks for all governance rules
- **Benefits**: Consistent enforcement, reduced human error, scalable governance

#### **3. Progressive Enhancement Strategy**
- **Phase 1**: Start with basic automated checks
- **Phase 2**: Add more sophisticated validation
- **Phase 3**: Implement intelligent governance systems
- **Phase 4**: Full AI-powered governance automation

#### **4. Memory System Evolution**
- **Current**: Static documentation-based governance
- **Target**: Dynamic, context-aware governance systems
- **Implementation**: Use memory systems to track governance compliance over time

### **🚀 Current Implementation Status**

#### **✅ Implemented Governance Systems**
- **Cursor AI Rules System**: `.cursor/rules/` directory with automated rule enforcement
- **RAGChecker Baseline Enforcement**: Automated performance baseline monitoring
- **UV Package Management**: Automated dependency management and environment standards
- **Code Quality Gates**: Automated linting, formatting, and type checking
- **Testing Standards**: Automated test execution and coverage validation

#### **🔄 In Progress**
- **Documentation Governance**: B-1034 documentation governance codification
- **Memory System Integration**: Enhanced memory rehydration with governance context
- **Performance Monitoring**: Real-time governance compliance tracking

#### **📋 Planned**
- **AI-Powered Governance**: Intelligent rule generation and adaptation
- **Predictive Compliance**: Proactive governance enforcement
- **Context-Aware Rules**: Dynamic rule application based on project context

### **🏗️ Technical Implementation Patterns**

#### **CI/CD Integration**
```yaml
# Example: Automated governance checks
governance_checks:
  - name: "Code Quality Enforcement"
    script: "ruff check . && pyright"
    on: [push, pull_request]
  
  - name: "Documentation Compliance"
    script: "python scripts/validate_docs.py"
    on: [push, pull_request]
  
  - name: "Security Scanning"
    script: "bandit -r src/"
    on: [push, pull_request]
```

#### **Automated Rule Enforcement**
```python
# Example: Governance rule implementation
class GovernanceEnforcer:
    def __init__(self):
        self.rules = [
            CodeQualityRule(),
            DocumentationRule(),
            SecurityRule(),
            PerformanceRule()
        ]
    
    def enforce(self, changes):
        violations = []
        for rule in self.rules:
            if not rule.validate(changes):
                violations.append(rule.get_violation())
        return violations
```

### **📊 Industry Best Practices**

#### **AI Company Patterns**
- **OpenAI**: Automated testing and validation pipelines
- **Anthropic**: Constitutional AI with automated compliance
- **Google**: Extensive automated governance in CI/CD
- **Microsoft**: Policy-as-code with automated enforcement

#### **Key Success Factors**
1. **Start Simple**: Begin with basic automated checks
2. **Iterate Rapidly**: Continuously improve governance systems
3. **Measure Everything**: Track governance effectiveness
4. **Human Oversight**: Maintain human review for complex decisions

### **🔄 Implementation Roadmap**

#### **Phase 1: Foundation (Current)**
- ✅ Basic CI/CD pipeline setup
- ✅ Code quality automation
- ✅ Documentation validation
- 🔄 Security scanning integration

#### **Phase 2: Enhancement (Next)**
- **Advanced validation**: Custom governance rules
- **Performance monitoring**: Automated performance checks
- **Compliance tracking**: Governance metrics and reporting
- **Integration testing**: End-to-end governance validation

#### **Phase 3: Intelligence (Future)**
- **AI-powered governance**: Intelligent rule generation
- **Predictive compliance**: Proactive governance enforcement
- **Adaptive systems**: Self-improving governance
- **Context-aware enforcement**: Dynamic rule application

### **⚠️ Risk Mitigation**

#### **Common Pitfalls**
- **Over-automation**: Don't automate everything at once
- **Complexity creep**: Keep governance systems simple
- **False positives**: Ensure rules are accurate and reliable
- **Maintenance burden**: Design for long-term sustainability

#### **Mitigation Strategies**
- **Gradual rollout**: Implement governance incrementally
- **Human fallback**: Maintain manual override capabilities
- **Regular review**: Continuously assess governance effectiveness
- **Community feedback**: Gather input from development team

## 📚 Implementation Patterns Library

<!-- ANCHOR_KEY: implementation-patterns-library -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["coder", "implementer"] -->

### **TL;DR**
Comprehensive library of technical implementation patterns for the AI development ecosystem. Use this library to find appropriate implementation patterns for your current task.

### **🎯 Pattern Library Categories**

#### **1. Memory System Patterns**

##### **Memory Rehydration Pattern**
```python
def memory_rehydration_pattern(query: str, role: str) -> Dict[str, Any]:
    """Standard pattern for memory rehydration."""
    # Set environment
    os.environ["POSTGRES_DSN"] = "mock://test"

    # Execute memory orchestration
    result = subprocess.run([
        "python3", "scripts/unified_memory_orchestrator.py",
        "--systems", "cursor",
        "--role", role,
        query
    ], capture_output=True, text=True)

    return json.loads(result.stdout)
```

##### **Context Integration Pattern**
```python
def context_integration_pattern(base_context: Dict[str, Any],
                               additional_context: Dict[str, Any]) -> Dict[str, Any]:
    """Integrate additional context with base context."""
    integrated_context = base_context.copy()
    
    # Merge additional context
    for key, value in additional_context.items():
        if key in integrated_context:
            if isinstance(integrated_context[key], list):
                integrated_context[key].extend(value)
            else:
                integrated_context[key] = [integrated_context[key], value]
        else:
            integrated_context[key] = value
    
    return integrated_context
```

#### **2. DSPy Integration Patterns**

##### **Model Switcher Pattern**
```python
def model_switcher_pattern(task_type: str, complexity: str) -> str:
    """Select appropriate model based on task characteristics."""
    model_mapping = {
        "coding": {
            "simple": "llama-3.1-8b",
            "moderate": "mistral-7b",
            "complex": "phi-3.5-3.8b"
        },
        "analysis": {
            "simple": "llama-3.1-8b",
            "moderate": "mistral-7b",
            "complex": "phi-3.5-3.8b"
        }
    }
    
    return model_mapping.get(task_type, {}).get(complexity, "llama-3.1-8b")
```

##### **Optimization Pattern**
```python
def optimization_pattern(module, test_data, metric):
    """Standard optimization pattern for DSPy modules."""
    optimizer = LabeledFewShotOptimizer(k=16)
    optimized_module = optimizer.compile(module, trainset=test_data, metric=metric)
    return optimized_module
```

#### **3. Database Patterns**

##### **Connection Management Pattern**
```python
def database_connection_pattern(dsn: str) -> psycopg2.connection:
    """Standard database connection pattern with error handling."""
    try:
        conn = psycopg2.connect(dsn)
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection failed: {e}")
        raise
```

##### **Transaction Pattern**
```python
def transaction_pattern(conn, operations):
    """Standard transaction pattern with rollback."""
    try:
        with conn.cursor() as cur:
            for operation in operations:
                cur.execute(operation)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
```

#### **4. Error Handling Patterns**

##### **Graceful Degradation Pattern**
```python
def graceful_degradation_pattern(primary_function, fallback_function, *args, **kwargs):
    """Try primary function, fallback to secondary if it fails."""
    try:
        return primary_function(*args, **kwargs)
    except Exception as e:
        logging.warning(f"Primary function failed: {e}, using fallback")
        return fallback_function(*args, **kwargs)
```

##### **Retry Pattern**
```python
def retry_pattern(func, max_retries=3, delay=1):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay * (2 ** attempt))
```

#### **5. Testing Patterns**

##### **Mock Pattern**
```python
def mock_pattern(original_function, mock_function):
    """Standard mocking pattern for testing."""
    with patch(original_function, mock_function):
        # Test code here
        pass
```

##### **Fixture Pattern**
```python
@pytest.fixture
def test_database():
    """Standard database fixture for testing."""
    conn = psycopg2.connect("postgresql://test:test@localhost:5432/test")
    yield conn
    conn.close()
```

### **🔄 Pattern Usage Guidelines**

#### **When to Use Patterns**
- **Consistency**: Ensure consistent implementation across the codebase
- **Reusability**: Leverage proven solutions for common problems
- **Maintainability**: Use patterns that are well-documented and tested
- **Performance**: Choose patterns that meet performance requirements

#### **Pattern Selection Criteria**
1. **Appropriateness**: Pattern must fit the specific use case
2. **Quality**: Pattern must be well-implemented and tested
3. **Documentation**: Pattern must be properly documented
4. **Maintenance**: Pattern must be maintainable over time

#### **Pattern Implementation Process**
1. **Identify Need**: Determine what pattern is needed
2. **Search Library**: Look for existing patterns
3. **Adapt Pattern**: Modify pattern for specific use case
4. **Test Implementation**: Ensure pattern works correctly
5. **Document Usage**: Document how pattern is used

## 📋 Changelog

- **2025-08-28**: Created as part of B-1035 consolidation
- **2025-08-28**: Consolidated coding and prompting standards guides
- **2025-08-28**: Merged content from:
  - `400_comprehensive-coding-best-practices.md`
  - `400_script-optimization-guide.md`
  - `400_error-reduction-lessons-learned.md`
  - `400_few-shot-context-examples.md`
  - `400_performance-optimization-guide.md`
- **2025-01-02**: Added MCP Server Orchestration patterns (B-1040)
- **2025-01-02**: Integrated Cursor AI Rules System documentation
- **2025-01-02**: Enhanced governance-by-code section with current implementation status
- **2025-09-15**: Integrated Microsoft Learn Python best practices and Azure SDK patterns
- **2025-09-15**: Enhanced error handling patterns with current industry standards
- **2025-09-15**: Updated docstring standards for better AI code generation

## Model/RAG Interfaces Updated (B-1041)
- `vector_store.py`: retrieval API expanded for hybrid flows; ensure adapters use new methods.
- `model_switcher.py`: selection/forward paths clarified; wrappers aligned.
- Expectations:
  - Add tests when touching wrappers/adapters; see new `test_*` files under `dspy-rag-system/`.
  - Run a smoke: `python3 dspy-rag-system/eval_gold.py` before push.
  - Track KPIs: `python3 dspy-rag-system/scripts/check_retrieval_kpis.py`.
