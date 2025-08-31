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
- **Systematic evaluation**: Apply structured evaluation frameworks including RAGChecker for RAG system assessment
- **Iterative refinement**: Continuously improve based on research findings

### **Implementation Patterns**

#### **1. Research-Driven Development Workflow**
```python
from typing import Dict, Any, List
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
        "risk_assessment": risk_assessment
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
        return evaluation_result

    def _evaluate_criterion(self, solution: Dict[str, Any], criterion: str) -> float:
        """Evaluate a specific criterion for a solution."""
        # Implementation specific to each criterion
        evaluators = {
            "performance": self._evaluate_performance,
            "security": self._evaluate_security,
            "maintainability": self._evaluate_maintainability,
            "scalability": self._evaluate_scalability,
            "cost": self._evaluate_cost
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
            research_context
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
3. Regular maintenance using the prevention checklist

## 💻 COMPREHENSIVE CODING BEST PRACTICES

### **Code Criticality Map**

#### **Tier 1 Critical (Never Break Without a Plan)**
- **scripts/process_tasks.py**: Task execution engine, core CLI for executing backlog items end-to-end
- **scripts/state_manager.py**: Execution/state persistence, central state tracking across task boundaries
- **dspy-rag-system/src/dspy_modules/cursor_model_router.py**: AI model routing & context engineering, intelligent model selection for Cursor Native AI
- **dspy-rag-system/src/dspy_modules/vector_store.py**: Hybrid vector store, PGVector + text search storage retrieval span-level grounding
- **dspy-rag-system/src/dspy_modules/document_processor.py**: Document ingestion & chunking, document processing validates extracts metadata chunks prepares documents
- **dspy-rag-system/src/utils/memory_rehydrator.py**: Context assembly & role-aware hydration, context building builds role-aware context bundles from Postgres

#### **Tier 2 High (Production Infrastructure)**
- **scripts/doc_coherence_validator.py**: Documentation quality & coherence validation, documentation integrity primary validator
- **dspy-rag-system/src/utils/database_resilience.py**: DB resilience & pooling, database management connection pooling health monitoring retries graceful degradation
- **dspy-rag-system/src/dashboard.py**: Web UI & monitoring integration, Flask dashboard file intake SocketIO updates production monitoring health endpoints
- **dspy-rag-system/src/utils/error_pattern_recognition.py**: Error recovery patterns, error management pattern catalog classification automated recovery hotfix templates
- **dspy-rag-system/src/utils/prompt_sanitizer.py**: Input security guard-rails, security validation validation sanitization queries content foundational safe operations
- **scripts/rollback_doc.sh**: Documentation recovery & rollback system, documentation recovery git snapshot system automated snapshots rollback procedures
- **dspy-rag-system/src/utils/anchor_metadata_parser.py**: Anchor metadata extraction, metadata processing extracts anchor metadata HTML comments maps JSONB memory rehydrator critical context assembly

#### **Tier 3 Supporting (Reliability/Utilities)**
- **dspy-rag-system/src/utils/retry_wrapper.py**: Retry/backoff policies
- **scripts/system_health_check.py**: Health checks diagnostics
- **scripts/performance_benchmark.py**: Performance monitoring optimization
- **dspy-rag-system/src/utils/config_manager.py**: Centralized config handling
- **dspy-rag-system/src/utils/logger.py**: Structured logging helpers
- **scripts/auto_push_prompt.py**: Repository maintenance automation, maintenance automation interactive prompt pushing changes git status checks user confirmation
- **scripts/maintenance_push.sh**: Maintenance push wrapper, maintenance integration shell wrapper auto-push prompt integration maintenance workflows

### **Code Quality Standards**

#### **Tier 1 & 2 Requirements**
- **Pass linter checks**: No F841, E501 errors
- **Comprehensive test coverage**: 80%+ for Tier 1, 70%+ for Tier 2
- **Unused variable best practices**: Proper variable management
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
import unittest
from unittest.mock import Mock, patch

class TestAIModelInterface(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures

    def test_generate_response_success(self):
        # Arrange
        # Act
        # Assert

    def test_generate_response_failure(self):
        # Test error handling
```

**Integration Tests**:
```python
# Example integration test
class TestAIIntegration(unittest.TestCase):
    def setUp(self):
        # Set up integration test environment

    def test_ai_generation_integration(self):
        # Test AI generation with database integration

    def test_workflow_execution_integration(self):
        # Test n8n workflow execution integration
```

**End-to-End Tests**:
```python
# Example E2E test
from selenium import webdriver

class TestAIEcosystemE2E(unittest.TestCase):
    def setUp(self):
        # Set up E2E test environment

    def test_complete_ai_workflow(self):
        # Test complete AI workflow from UI to database

    def tearDown(self):
        # Clean up E2E test environment
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

# Check for schema drift
python3 scripts/system_health_check.py --schema-drift

# Update baseline after intentional changes
./scripts/update_schema_baseline.sh
```

**Schema Coverage**:
- **Pydantic Models**: RAGChecker, DSPy context models, constitution models, error models
- **Database Schema**: Tables, columns, indexes, relationships in PostgreSQL
- **Artifacts**: Stored in `dspy-rag-system/config/database/schemas/`

**Integration with CI/CD**:
```yaml
- name: Generate schema snapshots
  run: python3 scripts/validate_config.py --dump-schemas

- name: Schema drift check
  run: python3 scripts/system_health_check.py --schema-drift
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
- **Evaluation Script**: `python3 scripts/ragchecker_official_evaluation.py`
- **Metrics**: Precision, Recall, F1 Score, Context Utilization, Response Length
- **Quality Gates**:
  - Precision > 0.5, Recall > 0.6, F1 Score > 0.5
  - Context Utilization > 0.7, Response Length > 500 characters
- **Test Cases**: 5 comprehensive ground truth test cases
- **Integration**: Real responses from Unified Memory Orchestrator
- **Status**: ✅ **FULLY OPERATIONAL** - RAGChecker 0.1.9 + spaCy model installed

#### **RAGChecker Testing Commands**
```bash
# Run Official RAGChecker evaluation
python3 scripts/ragchecker_official_evaluation.py

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
- **Quality Gates**: Automated quality gate enforcement
- **Performance Monitoring**: Continuous performance monitoring

#### **Automated Testing Pipeline**
```yaml
# Example CI/CD pipeline
stages:
  - test
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
- [ ] Performance gates met
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
    # Save report
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

# After: O(n) complexity with set
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

# Fast lookups with defaultdict
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
from typing import List

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
- [ ] **I/O operations optimized** with async/await
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

## ⚡ PERFORMANCE OPTIMIZATION

### **System Architecture Optimization**

#### **Performance-Optimized Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                Performance Layers                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Load Balancing (Request Distribution)                  │
│ 2. Caching Layer (Redis/Memory Cache)                    │
│ 3. Application Layer (Optimized Code)                     │
│ 4. Database Layer (PostgreSQL + Indexing)                │
│ 5. Storage Layer (SSD + RAID)                            │
│ 6. Network Layer (High Bandwidth)                        │
└─────────────────────────────────────────────────────────────┘
```

#### **Component Performance Characteristics**

##### **AI Model Performance**
```python
# Model performance configuration
MODEL_PERFORMANCE_CONFIG = {
    "cursor-native-ai": {
        "max_tokens": 2048,
        "temperature": 0.7,
        "response_time_target": 3.0,
        "memory_usage": "n/a",
        "concurrent_requests": 4
    }
}
```

##### **Database Performance**
```sql
-- Performance-optimized database configuration
-- PostgreSQL performance settings
SET shared_buffers = '256MB';
SET effective_cache_size = '1GB';
SET work_mem = '4MB';
SET maintenance_work_mem = '64MB';
SET checkpoint_completion_target = 0.9;
SET wal_buffers = '16MB';
```

### **Performance Baselines**

| Metric | Baseline | Target | Critical |
|--------|----------|--------|----------|
|**AI Response Time**| < 5 seconds | < 3 seconds | > 10 seconds |
|**Database Query Time**| < 100ms | < 50ms | > 500ms |
|**Dashboard Load Time**| < 2 seconds | < 1 second | > 5 seconds |

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
# Parallel execution with early exit
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

## Purpose
Brief description

## Table of Contents
1. [Section 1](#section-1)
2. [Section 2](#section-2)

## Section 1
Content here

---
*Last Updated: 2025-08-31*
```

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

## Expected Output
- Code implementation following project standards
- Unit tests with 80%+ coverage
- Documentation updates
- Configuration changes if needed
```

#### **2. Iterative Refinement**
**Pattern**: Start with broad prompts and refine based on results

**Example**:
```markdown
## Initial Prompt
"Create a user authentication system"

## Refined Prompt
"Create a user authentication system using JWT tokens with the following requirements:
- User registration with email validation
- Login with password hashing
- Token-based session management
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

## Expected Output
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

## Expected Output
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

### Code Quality Checklist
- [ ] **Code follows established standards** and conventions
- [ ] **Clear naming and comprehensive documentation**
- [ ] **Proper error handling and logging** implemented
- [ ] **Performance optimization considerations** addressed
- [ ] **Security best practices** followed
- [ ] **Comprehensive tests written and passing**

### AI Prompting Checklist
- [ ] **Clear objectives and expected outcomes** defined
- [ ] **Relevant context and background** provided
- [ ] **Specific and actionable language** used
- [ ] **Prompt iterated and refined** based on results
- [ ] **AI outputs validated and verified** for quality
- [ ] **Ethical considerations** addressed

### Performance Optimization Checklist
- [ ] **Performance bottlenecks identified** through profiling
- [ ] **Caching strategies implemented** for repeated operations
- [ ] **Parallel processing used** where appropriate
- [ ] **I/O operations optimized** and database queries improved
- [ ] **Resource usage monitored** and memory consumption optimized

### Error Reduction Checklist
- [ ] **Errors categorized** as safe vs. dangerous
- [ ] **Safe auto-fixes applied** automatically
- [ ] **Dangerous errors reviewed** manually
- [ ] **Prevention strategies implemented** for future errors
- [ ] **Lessons learned documented** and anti-patterns recorded

## 🔗 Interfaces

### Development Environment
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
        date_range: Tuple of (start_date, end_date) in ISO format

    Returns:
        Dictionary containing calculated performance metrics

    Raises:
        ValueError: If date_range is invalid
        UserNotFoundError: If user_id doesn't exist
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

**Server Implementation Pattern**:
```python
from utils.mcp_integration import MCPServer, MCPConfig, MCPError, DocumentMetadata, ProcessedDocument

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
- **File Context**: Include current file and import analysis where relevant

## 🤖 AGENT TOOL INTEGRATION STANDARDS

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
- **Multi-Layer Context**: Implement layered context enhancement
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

        return enhanced_context

    def _get_layer_content(self, layer: str, **kwargs) -> str:
        """Get content for a specific enhancement layer"""

        layer_content = {
            "language_specific_patterns": """
- Python: PEP 8, type hints, async/await patterns
- JavaScript: ES6+, modules, async/await
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

        return fallback_context

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

        return fallback_context

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
- **AI Frameworks**: `400_guides/400_07_ai-frameworks-dspy.md` (MCP integration)
- **Integrations**: `400_guides/400_08_integrations-editor-and-models.md` (MCP servers)

## 📚 References

- **Migration Map**: `migration_map.csv`
- **PRD**: `artifacts/prd/PRD-B-1035-400_guides-Consolidation.md`
- **Original Standards**: Various coding and prompting files (now stubs)
- **Performance Baselines**: System performance benchmarks and targets
- **Error Reduction Tools**: Smart error fix scripts and decision matrices

## 📋 Changelog

- **2025-08-28**: Created as part of B-1035 consolidation
- **2025-08-28**: Consolidated coding and prompting standards guides
- **2025-08-28**: Merged content from:
  - `400_comprehensive-coding-best-practices.md`
  - `400_script-optimization-guide.md`
  - `400_error-reduction-lessons-learned.md`
  - `400_few-shot-context-examples.md`
  - `400_performance-optimization-guide.md`


## Model/RAG Interfaces Updated (B-1041)
- `vector_store.py`: retrieval API expanded for hybrid flows; ensure adapters use new methods.
- `model_switcher.py`: selection/forward paths clarified; wrappers aligned.
- Expectations:
  - Add tests when touching wrappers/adapters; see new `test_*` files under `dspy-rag-system/`.
  - Run a smoke: `python3 dspy-rag-system/eval_gold.py` before push.
  - Track KPIs: `python3 dspy-rag-system/scripts/check_retrieval_kpis.py`.
