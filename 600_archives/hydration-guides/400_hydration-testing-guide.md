<!-- ANCHOR_KEY: hydration-testing -->
<!-- ANCHOR_PRIORITY: 35 -->
<!-- ROLE_PINS: ["implementer"] -->

# 🧪 Hydration Testing Guide

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Test memory rehydrator and context assembly | Implementing or debugging hydration | Run smoke tests and validate context quality |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Hydration testing framework documented
- **Priority**: 🔥 High - Essential for system reliability
- **Points**: 4 - Moderate complexity, high importance
- **Dependencies**: dspy-rag-system/src/utils/memory_rehydrator.py, 400_guides/400_planner-hydration-guide.md
- **Next Steps**: Run comprehensive tests and validate performance

## 🧪 Testing Strategy

### **Test Categories**

1. **Functional Tests** - Verify core functionality
2. **Performance Tests** - Measure speed and efficiency
3. **Quality Tests** - Validate context relevance
4. **Integration Tests** - Test with real workflows
5. **Stress Tests** - Test under load and edge cases

### **Test Environment Setup**

```bash
# Set up test environment
cd dspy-rag-system
export PYTHONPATH=.
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"

# Install test dependencies
pip install pytest pytest-benchmark pytest-cov psutil

# Optional: For enhanced memory benchmarking
pip install psutil
```

## 🔧 Basic Functionality Tests

### **1. Role-Based Testing**

```bash
# Test planner role
python3 -m src.utils.memory_rehydrator --role planner --task "test planning context" --limit 5

# Test implementer role
python3 -m src.utils.memory_rehydrator --role implementer --task "test implementation context" --limit 5

# Test with JSON output
python3 -m src.utils.memory_rehydrator --role planner --task "test" --json
```

### **2. Smoke Test Suite**

```bash
# Run comprehensive smoke tests
cd dspy-rag-system
PYTHONPATH=. python3 tests/test_memory_rehydrator_smoke.py
```

**Expected Results:**
- ✅ Planner bundle: 8-12 sections, 400-600 tokens
- ✅ Implementer bundle: 6-10 sections, 350-550 tokens
- ✅ TL;DR content found in both roles
- ✅ Role-specific content included

### **3. Anchor Metadata Validation**

```python
from src.utils.anchor_metadata_parser import extract_anchor_metadata, validate_anchor_metadata

def test_anchor_extraction():
    """Test anchor metadata extraction from core files"""
    core_files = [
        "100_memory/100_cursor-memory-context.md",
        "000_core/000_backlog.md",
        "400_guides/400_system-overview.md"
    ]

    for file_path in core_files:
        metadata = extract_anchor_metadata_from_file(file_path)
        errors = validate_anchor_metadata(metadata)
        assert len(errors) == 0, f"Validation errors in {file_path}: {errors}"
```

## 📊 Performance Benchmarks

### **1. Bundle Creation Performance**

```python
import time
from src.utils.memory_rehydrator import build_hydration_bundle

def benchmark_bundle_creation():
    """Benchmark bundle creation performance"""
    test_cases = [
        ("planner", "strategic planning", 1200),
        ("implementer", "code implementation", 1200),
        ("planner", "priority assessment", 800),
        ("implementer", "debugging", 1000)
    ]

    results = {}
    for role, task, budget in test_cases:
        start_time = time.time()
        bundle = build_hydration_bundle(role=role, task=task, token_budget=budget)
        end_time = time.time()

        results[f"{role}_{task}"] = {
            "creation_time": end_time - start_time,
            "sections": bundle.meta.get("sections", 0),
            "tokens": bundle.meta.get("tokens_est", 0),
            "budget": budget
        }

    return results
```

**Performance Targets:**
- **Bundle creation**: < 5s (EXCELLENT), < 10s (GOOD)
- **Token efficiency**: ≤ 1200 tokens for standard bundles
- **Section count**: 3-12 sections typical

### **2. Memory Usage Benchmarks**

```python
import psutil
import os

def benchmark_memory_usage():
    """Benchmark memory usage during bundle creation"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Create multiple bundles
    bundles = []
    for i in range(10):
        bundle = build_hydration_bundle(
            role="planner" if i % 2 == 0 else "implementer",
            task=f"test task {i}",
            token_budget=1200
        )
        bundles.append(bundle)

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    return {
        "initial_memory_mb": initial_memory,
        "final_memory_mb": final_memory,
        "memory_increase_mb": memory_increase,
        "bundles_created": len(bundles)
    }
```

## 🎯 Context Quality Validation

### **1. Content Relevance Testing**

```python
def validate_context_relevance(bundle, expected_keywords):
    """Validate that context contains relevant content"""
    text = bundle.text.lower()
    found_keywords = []

    for keyword in expected_keywords:
        if keyword.lower() in text:
            found_keywords.append(keyword)

    relevance_score = len(found_keywords) / len(expected_keywords)
    return {
        "relevance_score": relevance_score,
        "found_keywords": found_keywords,
        "missing_keywords": [k for k in expected_keywords if k.lower() not in text]
    }
```

### **2. Role-Specific Validation**

```python
def validate_planner_context(bundle):
    """Validate planner role context quality"""
    expected_keywords = ["backlog", "priority", "system", "overview", "planning"]
    return validate_context_relevance(bundle, expected_keywords)

def validate_implementer_context(bundle):
    """Validate implementer role context quality"""
    expected_keywords = ["dspy", "development", "implementation", "code", "technical"]
    return validate_context_relevance(bundle, expected_keywords)
```

### **3. Anchor Content Validation**

```python
def validate_anchor_content(bundle):
    """Validate that pinned anchors are present"""
    text = bundle.text.lower()

    # Check for essential anchors
    anchor_checks = {
        "tldr": "tl;" in text or "tldr" in text,
        "quick_start": "quick-start" in text or "quick start" in text,
        "commands": "commands" in text,
        "role_specific": any(role in text for role in ["planner", "implementer", "researcher"])
    }

    return {
        "anchor_checks": anchor_checks,
        "all_anchors_present": all(anchor_checks.values()),
        "missing_anchors": [k for k, v in anchor_checks.items() if not v]
    }
```

## 🔄 Integration Testing

### **1. Workflow Integration Tests**

```python
def test_planning_workflow():
    """Test hydration integration with planning workflow"""
    # Step 1: Initial assessment
    assessment_bundle = build_hydration_bundle(
        role="planner",
        task="assess current project state",
        token_budget=1200
    )

    # Step 2: Priority review
    priority_bundle = build_hydration_bundle(
        role="planner",
        task="review backlog priorities",
        token_budget=1000
    )

    # Step 3: Strategic decision
    decision_bundle = build_hydration_bundle(
        role="planner",
        task="make strategic architecture decision",
        token_budget=1200
    )

    # Validate each step
    assert assessment_bundle.meta["sections"] > 0
    assert priority_bundle.meta["sections"] > 0
    assert decision_bundle.meta["sections"] > 0

    return {
        "assessment_sections": assessment_bundle.meta["sections"],
        "priority_sections": priority_bundle.meta["sections"],
        "decision_sections": decision_bundle.meta["sections"]
    }
```

### **2. Implementation Workflow Tests**

```python
def test_implementation_workflow():
    """Test hydration integration with implementation workflow"""
    # Step 1: Code review
    review_bundle = build_hydration_bundle(
        role="implementer",
        task="review code implementation",
        token_budget=1200
    )

    # Step 2: Technical design
    design_bundle = build_hydration_bundle(
        role="implementer",
        task="design technical solution",
        token_budget=1000
    )

    # Step 3: Debugging
    debug_bundle = build_hydration_bundle(
        role="implementer",
        task="debug technical issues",
        token_budget=1200
    )

    # Validate each step
    assert review_bundle.meta["sections"] > 0
    assert design_bundle.meta["sections"] > 0
    assert debug_bundle.meta["sections"] > 0

    return {
        "review_sections": review_bundle.meta["sections"],
        "design_sections": design_bundle.meta["sections"],
        "debug_sections": debug_bundle.meta["sections"]
    }
```

## 🚀 Stress Testing

### **1. High Load Testing**

```python
def stress_test_concurrent_bundles():
    """Test system under concurrent load"""
    import threading
    import time

    results = []
    errors = []

    def create_bundle(role, task_id):
        try:
            start_time = time.time()
            bundle = build_hydration_bundle(
                role=role,
                task=f"stress test task {task_id}",
                token_budget=1200
            )
            end_time = time.time()

            results.append({
                "task_id": task_id,
                "role": role,
                "creation_time": end_time - start_time,
                "sections": bundle.meta.get("sections", 0),
                "success": True
            })
        except Exception as e:
            errors.append({
                "task_id": task_id,
                "role": role,
                "error": str(e),
                "success": False
            })

    # Create 20 concurrent threads
    threads = []
    for i in range(20):
        role = "planner" if i % 2 == 0 else "implementer"
        thread = threading.Thread(target=create_bundle, args=(role, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return {
        "total_requests": 20,
        "successful_requests": len(results),
        "failed_requests": len(errors),
        "average_creation_time": sum(r["creation_time"] for r in results) / len(results) if results else 0,
        "errors": errors
    }
```

### **2. Token Budget Stress Testing**

```python
def stress_test_token_budgets():
    """Test system with various token budgets"""
    test_budgets = [100, 500, 1000, 1200, 2000, 5000]
    results = {}

    for budget in test_budgets:
        try:
            bundle = build_hydration_bundle(
                role="planner",
                task="token budget stress test",
                token_budget=budget
            )

            results[budget] = {
                "success": True,
                "sections": bundle.meta.get("sections", 0),
                "tokens_used": bundle.meta.get("tokens_est", 0),
                "budget_efficiency": bundle.meta.get("tokens_est", 0) / budget
            }
        except Exception as e:
            results[budget] = {
                "success": False,
                "error": str(e)
            }

    return results
```

## 📈 Performance Monitoring

### **1. Real-Time Metrics**

```python
def collect_performance_metrics():
    """Collect real-time performance metrics"""
    import psutil
    import time

    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent

    # Bundle creation metrics
    start_time = time.time()
    bundle = build_hydration_bundle(
        role="planner",
        task="performance monitoring test",
        token_budget=1200
    )
    creation_time = time.time() - start_time

    return {
        "timestamp": time.time(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "bundle_creation_time": creation_time,
        "bundle_sections": bundle.meta.get("sections", 0),
        "bundle_tokens": bundle.meta.get("tokens_est", 0)
    }
```

### **2. Performance Dashboard**

```python
def generate_performance_report():
    """Generate comprehensive performance report"""
    # Run all benchmarks
    bundle_performance = benchmark_bundle_creation()
    memory_usage = benchmark_memory_usage()
    stress_results = stress_test_concurrent_bundles()

    return {
        "bundle_performance": bundle_performance,
        "memory_usage": memory_usage,
        "stress_test": stress_results,
        "summary": {
            "total_tests": len(bundle_performance) + 1 + 1,
            "average_creation_time": sum(bundle_performance.values()) / len(bundle_performance),
            "memory_efficiency": memory_usage["memory_increase_mb"] / memory_usage["bundles_created"],
            "stress_test_success_rate": stress_results["successful_requests"] / stress_results["total_requests"]
        }
    }
```

## 🔍 Troubleshooting

### **Common Issues and Solutions**

#### **1. Database Connection Errors**
```bash
# Check database connectivity
psql $POSTGRES_DSN -c "SELECT 1;"

# Verify environment variables
echo $POSTGRES_DSN
echo $PYTHONPATH
```

#### **2. Import Errors**
```bash
# Fix Python path
export PYTHONPATH=dspy-rag-system/src

# Check module availability
python3 -c "import src.utils.memory_rehydrator; print('Import successful')"
```

#### **3. Performance Issues**
```python
# Check database performance
def check_database_performance():
    import psycopg2
    import time

    conn = psycopg2.connect(os.getenv("POSTGRES_DSN"))
    cursor = conn.cursor()

    start_time = time.time()
    cursor.execute("SELECT COUNT(*) FROM document_chunks")
    count = cursor.fetchone()[0]
    query_time = time.time() - start_time

    return {
        "document_chunks": count,
        "query_time": query_time,
        "performance_status": "GOOD" if query_time < 1.0 else "SLOW"
    }
```

## 🎯 Quality Gates

### **Success Criteria**

#### **Functional Quality Gates**
- ✅ All role-based tests pass
- ✅ Anchor metadata extraction works
- ✅ Context bundles contain expected content
- ✅ Token budgeting functions correctly

#### **Performance Quality Gates**
- ✅ Bundle creation < 5s (EXCELLENT)
- ✅ Memory usage < 100MB for 10 bundles
- ✅ Stress test success rate > 95%
- ✅ Token efficiency > 80%

#### **Integration Quality Gates**
- ✅ Workflow integration tests pass
- ✅ Real-world task scenarios work
- ✅ Error handling functions correctly
- ✅ Monitoring metrics available

## 🔗 Related Documentation

- **Memory Rehydrator**: `dspy-rag-system/src/utils/memory_rehydrator.py` (Core implementation)
- **Planner Guide**: `400_guides/400_planner-hydration-guide.md` (Planner testing)
- **Implementer Guide**: `400_guides/400_implementer-hydration-guide.md` (Implementer testing)
- **Smoke Tests**: `dspy-rag-system/tests/test_memory_rehydrator_smoke.py` (Basic tests)
- **Anchor Parser**: `dspy-rag-system/src/utils/anchor_metadata_parser.py` (Metadata testing)

## 🗒️ Change Log

- v1.0 (initial): Created comprehensive hydration testing guide
