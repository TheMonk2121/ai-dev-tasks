

<!-- ANCHOR_KEY: hydration-system -->
<!-- ANCHOR_PRIORITY: 40 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

# 🔗 Hydration System Guide

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete guide to memory rehydration system including integration, testing, and role-specific strategies | Setting up hydration system, testing, or using role-specific context | Configure system, run tests, and use role-appropriate context assembly |

- **what this file is**: Complete guide to memory rehydration system including integration, testing, and role-specific strategies.
- **read when**: Setting up hydration system, testing, or using role-specific context.
- **do next**: Configure system, run tests, and use role-appropriate context assembly.
- **anchors**: `integration-architecture`, `testing-framework`, `role-specific-strategies`, `n8n-workflow-integration`, `dashboard-monitoring`, `automation-patterns`, `alert-system`, `configuration-management`, `performance-optimization`, `testing-integration`, `troubleshooting`, `quality-gates`

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Comprehensive hydration system guide
- **Priority**: 🔥 Critical - Essential for AI context management
- **Points**: 5 - High complexity, system-critical importance
- **Dependencies**: dspy-rag-system/src/utils/memory_rehydrator.py, dspy-rag-system/src/utils/memory_rehydration.go, dspy-rag-system/src/n8n_workflows/hydration_monitor.py
- **Next Steps**: Configure system, run tests, and validate performance

## 📋 Table of Contents

1. [🔧 Integration Architecture](#-integration-architecture)
2. [🧪 Testing Framework](#-testing-framework)
3. [🎯 Role-Specific Strategies](#-role-specific-strategies)
4. [🚀 n8n Workflow Integration](#-n8n-workflow-integration)
5. [📊 Dashboard & Monitoring](#-dashboard--monitoring)
6. [🔄 Automation Patterns](#-automation-patterns)
7. [🚨 Alert System](#-alert-system)
8. [🔧 Configuration Management](#-configuration-management)
9. [📈 Performance Optimization](#-performance-optimization)
10. [🧪 Testing Integration](#-testing-integration)
11. [🔍 Troubleshooting](#-troubleshooting)
12. [🎯 Quality Gates](#-quality-gates)

---

<!-- ANCHOR: integration-architecture -->

## 🔧 Integration Architecture

### **System Components**

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   n8n Workflow  │    │  Hydration      │    │  Performance    │
│   Monitor       │◄──►│  Dashboard      │◄──►│  Benchmark      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Alert System  │    │  Metrics Store  │    │  Quality Tests  │
│   (Slack/Email) │    │  (JSON/DB)      │    │  (Automated)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Flow**

1. **Monitoring**: Continuous health checks every 30 seconds
2. **Metrics Collection**: Performance, quality, and system health data
3. **Alert Generation**: Automatic alerts for degradation or failures
4. **Dashboard Updates**: Real-time visualization of system status
5. **Integration**: n8n workflows for automation and notifications

---

<!-- ANCHOR: testing-framework -->

## 🧪 Testing Framework

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

### **Basic Functionality Tests**

#### **1. Role-Based Testing**

```bash
# Test planner role
python3 -m src.utils.memory_rehydrator --role planner --task "test planning context" --limit 5

# Test implementer role
python3 -m src.utils.memory_rehydrator --role implementer --task "test implementation context" --limit 5

# Test with JSON output
python3 -m src.utils.memory_rehydrator --role planner --task "test" --json
```

#### **2. Smoke Test Suite**

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

#### **3. Anchor Metadata Validation**

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

### **Performance Benchmarks**

#### **1. Bundle Creation Performance**

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

#### **2. Memory Usage Benchmarks**

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

### **Context Quality Validation**

#### **1. Content Relevance Testing**

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

#### **2. Role-Specific Validation**

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

#### **3. Anchor Content Validation**

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

---

<!-- ANCHOR: role-specific-strategies -->

## 🎯 Role-Specific Strategies

### **Planner Role Strategy**

#### **Planner Pinned Anchors (Always Loaded - ~400 tokens)**

1. **TL;DR** (priority 0) - Quick overview and current state
   - From: `100_memory/100_cursor-memory-context.md`
   - Purpose: Instant project understanding

2. **Backlog P0 Lane** (priority 5) - Current priorities
   - From: `000_core/000_backlog.md`
   - Purpose: Strategic priorities and urgent items

3. **System Overview** (priority 15) - Architecture context
   - From: `400_guides/400_system-overview.md`
   - Purpose: Technical landscape understanding

#### **Planner Task-Scoped Retrieval (~800 tokens)**

**Strategic Planning Content:**

- Priority assessment guides
- System architecture references
- Development roadmap documents
- Risk assessment materials

**Planning-Specific Patterns:**

- Backlog analysis and prioritization
- Dependency mapping and blocking issues
- Resource allocation considerations
- Timeline and milestone planning

#### **Planner Use Cases**

```python
# Strategic Planning Sessions
bundle = build_hydration_bundle(
    role="planner",
    task="strategic planning for Q4 development",
    token_budget=1200
)

# Priority Assessment
bundle = build_hydration_bundle(
    role="planner",
    task="assess backlog priorities and dependencies",
    token_budget=1200
)

# System Architecture Decisions
bundle = build_hydration_bundle(
    role="planner",
    task="evaluate system architecture for scalability",
    token_budget=1200
)
```

### **Implementer Role Strategy**

#### **Implementer Pinned Anchors (Always Loaded - ~400 tokens)**

1. **TL;DR** (priority 0) - Quick overview and current state
   - From: `100_memory/100_cursor-memory-context.md`
   - Purpose: Instant project understanding

2. **DSPy Development Context** (priority 10) - Technical foundation
   - From: `100_memory/104_dspy-development-context.md`
   - Purpose: Implementation patterns and technical context

3. **System Architecture** (priority 20) - Technical context
   - From: `400_guides/400_system-overview.md`
   - Purpose: Component relationships and integration patterns

#### **Implementer Task-Scoped Retrieval (~800 tokens)**

**Technical Implementation Content:**

- Code examples and patterns
- Technical implementation guides
- Testing strategies and frameworks
- Performance optimization techniques

**Implementation-Specific Patterns:**

- DSPy module development
- Vector store integration
- Database schema and queries
- API design and implementation
- Error handling and resilience

#### **Implementer Use Cases**

```python
# Code Implementation
bundle = build_hydration_bundle(
    role="implementer",
    task="implement new DSPy module for context assembly",
    token_budget=1200
)

# Technical Debugging
bundle = build_hydration_bundle(
    role="implementer",
    task="debug vector store performance issues",
    token_budget=1200
)

# System Integration
bundle = build_hydration_bundle(
    role="implementer",
    task="integrate new component with existing system",
    token_budget=1200
)
```

### **Token Budget Allocation**

- **Pinned anchors**: ~400 tokens (stable backbone)
- **Task-scoped content**: ~800 tokens (dynamic retrieval)
- **Total budget**: ~1200 tokens (default)

---

<!-- ANCHOR: n8n-workflow-integration -->

## 🚀 n8n Workflow Integration

### **1. Health Monitoring Workflow**

```python
# dspy-rag-system/src/n8n_workflows/hydration_monitor.py
from src.n8n_workflows.hydration_monitor import HydrationMonitor, create_n8n_webhook_payload

# Initialize monitor
monitor = HydrationMonitor()
health_report = monitor.generate_health_report()

# Create webhook payload for n8n
webhook_payload = create_n8n_webhook_payload(health_report)
```

**n8n Workflow Configuration:**

```json
{
  "name": "Hydration Health Monitor",
  "nodes": [
    {
      "type": "webhook",
      "name": "Health Check Trigger",
      "url": "/hydration-health-check",
      "method": "POST"
    },
    {
      "type": "python",
      "name": "Run Health Check",
      "script": "python3 src/n8n_workflows/hydration_monitor.py"
    },
    {
      "type": "condition",
      "name": "Check Health Status",
      "conditions": {
        "status": "equals",
        "value": "unhealthy"
      }
    },
    {
      "type": "slack",
      "name": "Send Alert",
      "channel": "#alerts",
      "message": "Hydration system health check failed"
    }
  ]
}
```

### **2. Performance Monitoring Workflow**

```python
# Performance monitoring with alerts
def monitor_performance():
    """Monitor performance metrics and trigger alerts"""
    dashboard = HydrationDashboard()
    dashboard_data = dashboard.get_dashboard_data()

    # Check for performance alerts
    alerts = dashboard_data["alerts"]

    for alert in alerts:
        if alert["severity"] == "critical":
            # Send immediate notification
            send_critical_alert(alert)
        elif alert["severity"] == "warning":
            # Log warning
            logger.warning(f"Performance warning: {alert['message']}")

    return dashboard_data
```

### **3. Quality Assurance Workflow**

```python
# Automated quality testing
def run_quality_tests():
    """Run automated quality tests"""
    import subprocess

    # Run hydration quality tests
    result = subprocess.run([
        "python3", "tests/test_hydration_quality.py"
    ], capture_output=True, text=True)

    # Parse results
    if result.returncode == 0:
        logger.info("Quality tests passed")
        return {"status": "passed", "output": result.stdout}
    else:
        logger.error("Quality tests failed")
        return {"status": "failed", "output": result.stderr}
```

---

<!-- ANCHOR: dashboard-monitoring -->

## 📊 Dashboard & Monitoring

### **1. Real-Time Dashboard**

```python
# Start dashboard monitoring
from src.mission_dashboard.hydration_dashboard import HydrationDashboard

dashboard = HydrationDashboard()
dashboard.start_monitoring(interval_seconds=30)

# Get current data
dashboard_data = dashboard.get_dashboard_data()
```

**Dashboard Features:**

- **Real-time metrics**: Bundle creation time, quality scores, memory usage
- **Performance trends**: Improving/degrading indicators
- **Alert system**: Warning and critical alerts
- **Auto-refresh**: Updates every 30 seconds
- **Historical data**: 24-hour performance summary

### **2. Dashboard API Endpoints**

```python
# Flask API for dashboard data
from flask import Flask, jsonify
from src.mission_dashboard.hydration_dashboard import HydrationDashboard

app = Flask(__name__)
dashboard = HydrationDashboard()

@app.route('/api/hydration/status')
def get_status():
    """Get current hydration system status"""
    return jsonify(dashboard.get_dashboard_data())

@app.route('/api/hydration/metrics')
def get_metrics():
    """Get performance metrics"""
    data = dashboard.get_dashboard_data()
    return jsonify(data["current_metrics"])

@app.route('/api/hydration/alerts')
def get_alerts():
    """Get current alerts"""
    data = dashboard.get_dashboard_data()
    return jsonify(data["alerts"])
```

---

<!-- ANCHOR: automation-patterns -->

## 🔄 Automation Patterns

### **1. Scheduled Health Checks**

```bash
#!/bin/bash
# scripts/hydration_health_check.sh

# Run health check every 5 minutes
while true; do
    cd /path/to/dspy-rag-system
    python3 src/n8n_workflows/hydration_monitor.py

    # Wait 5 minutes
    sleep 300
done
```

**Cron Configuration:**

```bash
# Add to crontab
*/5 * * * * /path/to/scripts/hydration_health_check.sh
```

### **2. Performance Benchmarking**

```bash
#!/bin/bash
# scripts/hydration_benchmark.sh

# Run benchmarks daily at 2 AM
cd /path/to/dspy-rag-system
python3 scripts/hydration_benchmark.py > benchmark_results.json

# Send results to monitoring system
curl -X POST http://localhost:5000/api/hydration/benchmark \
  -H "Content-Type: application/json" \
  -d @benchmark_results.json
```

### **3. Quality Testing Automation**

```python
# Automated quality testing pipeline
def quality_testing_pipeline():
    """Run comprehensive quality testing"""
    tests = [
        "test_hydration_quality.py",
        "test_memory_rehydrator_smoke.py",
        "test_anchor_metadata.py"
    ]

    results = {}
    for test in tests:
        result = subprocess.run([
            "python3", f"tests/{test}"
        ], capture_output=True, text=True)

        results[test] = {
            "passed": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }

    return results
```

---

<!-- ANCHOR: alert-system -->

## 🚨 Alert System

### **1. Alert Configuration**

```python
# Alert configuration
ALERT_CONFIG = {
    "performance": {
        "bundle_creation_time": {
            "warning": 5.0,  # seconds
            "critical": 10.0  # seconds
        },
        "memory_usage": {
            "warning": 1000,  # MB
            "critical": 2000  # MB
        }
    },
    "quality": {
        "overall_score": {
            "warning": 0.7,  # 70%
            "critical": 0.5  # 50%
        }
    },
    "system": {
        "health_check": {
            "critical": False  # Any failure is critical
        }
    }
}
```

### **2. Alert Channels**

```python
# Multiple alert channels
def send_alert(alert):
    """Send alert through multiple channels"""

    # Slack notification
    if alert["severity"] in ["warning", "critical"]:
        send_slack_alert(alert)

    # Email notification
    if alert["severity"] == "critical":
        send_email_alert(alert)

    # Log alert
    logger.warning(f"Alert: {alert['type']} - {alert['message']}")

    # Store in database
    store_alert_in_database(alert)
```

### **3. Alert Escalation**

```python
# Alert escalation logic
def escalate_alert(alert):
    """Escalate alerts based on severity and frequency"""

    # Check if this is a repeated alert
    recent_alerts = get_recent_alerts(alert["type"], minutes=30)

    if len(recent_alerts) >= 3:
        # Escalate to critical
        alert["severity"] = "critical"
        send_escalation_notification(alert)

    return alert
```

---

<!-- ANCHOR: configuration-management -->

## 🔧 Configuration Management

### **1. Environment Configuration**

```bash
# .env file for hydration system
HYDRATION_MONITORING_ENABLED=true
HYDRATION_CHECK_INTERVAL=30
HYDRATION_ALERT_ENABLED=true
HYDRATION_DASHBOARD_PORT=5000
HYDRATION_N8N_WEBHOOK_URL=http://localhost:5678/webhook/hydration
```

### **2. Configuration Validation**

```python
# Configuration validation
def validate_config():
    """Validate hydration system configuration"""
    required_vars = [
        "POSTGRES_DSN",
        "HYDRATION_MONITORING_ENABLED",
        "HYDRATION_CHECK_INTERVAL"
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")

    return True
```

---

<!-- ANCHOR: performance-optimization -->

## 📈 Performance Optimization

### **1. Caching Strategy**

```python
# Bundle caching for performance
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_bundle(role: str, task: str, token_budget: int):
    """Cache frequently requested bundles"""
    return build_hydration_bundle(role=role, task=task, token_budget=token_budget)
```

### **2. Connection Pooling**

```python
# Database connection pooling optimization
def optimize_connection_pool():
    """Optimize database connection pool for concurrent access"""
    pool_config = {
        "min_size": 5,
        "max_size": 20,
        "max_queries": 50000,
        "max_inactive_connection_lifetime": 300.0
    }

    return pool_config
```

### **3. Load Balancing**

```python
# Load balancing for high concurrent access
def distribute_load():
    """Distribute load across multiple instances"""
    instances = [
        "http://localhost:5001",
        "http://localhost:5002",
        "http://localhost:5003"
    ]

    # Round-robin load balancing
    current_instance = instances[load_balancer.get_next()]
    return current_instance
```

---

<!-- ANCHOR: testing-integration -->

## 🧪 Testing Integration

### **1. Integration Test Suite**

```python
# Integration tests for hydration system
def test_integration_workflow():
    """Test complete integration workflow"""

    # 1. Start monitoring
    monitor = HydrationMonitor()
    health_report = monitor.generate_health_report()

    # 2. Verify health check
    assert health_report["status"] == "healthy"

    # 3. Start dashboard
    dashboard = HydrationDashboard()
    dashboard_data = dashboard.get_dashboard_data()

    # 4. Verify dashboard data
    assert "current_metrics" in dashboard_data
    assert "alerts" in dashboard_data

    # 5. Test n8n webhook
    webhook_payload = create_n8n_webhook_payload(health_report)
    assert webhook_payload["webhook_type"] == "hydration_health_check"

    return True
```

### **2. Performance Testing**

```python
# Performance testing under load
def test_performance_under_load():
    """Test system performance under concurrent load"""

    import threading
    import time

    results = []
    errors = []

    def create_bundle_worker():
        try:
            start_time = time.time()
            bundle = build_hydration_bundle(
                role="planner",
                task="load test",
                token_budget=1200
            )
            end_time = time.time()

            results.append(end_time - start_time)
        except Exception as e:
            errors.append(str(e))

    # Create 50 concurrent threads
    threads = []
    for i in range(50):
        thread = threading.Thread(target=create_bundle_worker)
        threads.append(thread)
        thread.start()

    # Wait for completion
    for thread in threads:
        thread.join()

    # Analyze results
    avg_time = sum(results) / len(results) if results else 0
    success_rate = len(results) / 50

    return {
        "avg_time": avg_time,
        "success_rate": success_rate,
        "errors": errors
    }
```

### **3. Workflow Integration Tests**

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

### **4. Implementation Workflow Tests**

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

---

<!-- ANCHOR: troubleshooting -->

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

#### **4. Context Quality Issues**

```python
# Validate context quality
def diagnose_context_quality(bundle):
    """Diagnose context quality issues"""
    text = bundle.text.lower()

    # Check for essential content
    issues = []

    if "tl;" not in text and "tldr" not in text:
        issues.append("Missing TL;DR content")

    if bundle.meta.get("sections", 0) < 3:
        issues.append("Too few sections")

    if bundle.meta.get("tokens_est", 0) < 200:
        issues.append("Context too short")

    return {
        "has_issues": len(issues) > 0,
        "issues": issues,
        "sections": bundle.meta.get("sections", 0),
        "tokens": bundle.meta.get("tokens_est", 0)
    }
```

---

<!-- ANCHOR: quality-gates -->

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

### **Quality Validation Functions**

```python
def validate_planner_context(bundle) -> bool:
    """Validate planner role context quality"""
    text = bundle.text.lower()

    # Check for essential planning content
    has_tldr = "tl;" in text or "tldr" in text
    has_priorities = "p0" in text or "priority" in text
    has_system = "system" in text or "architecture" in text
    has_backlog = "backlog" in text or "lane" in text

    return has_tldr and has_priorities and has_system and has_backlog

def validate_implementer_context(bundle) -> bool:
    """Validate implementer role context quality"""
    text = bundle.text.lower()

    # Check for essential implementation content
    has_tldr = "tl;" in text or "tldr" in text
    has_dspy = "dspy" in text or "development" in text
    has_system = "system" in text or "architecture" in text
    has_technical = "implementation" in text or "code" in text

    return has_tldr and has_dspy and has_system and has_technical
```

---

## 🔗 Related Documentation

- **Memory Rehydrator**: `dspy-rag-system/src/utils/memory_rehydrator.py` (Python implementation)
- **Memory Rehydrator**: `dspy-rag-system/src/utils/memory_rehydration.go` (Go implementation)
- **Health Monitor**: `dspy-rag-system/src/n8n_workflows/hydration_monitor.py` (n8n integration)
- **Performance Dashboard**: `dspy-rag-system/src/mission_dashboard/hydration_dashboard.py` (Real-time monitoring)
- **Smoke Tests**: `dspy-rag-system/tests/test_memory_rehydrator_smoke.py` (Basic tests)
- **Anchor Parser**: `dspy-rag-system/src/utils/anchor_metadata_parser.py` (Metadata testing)
- **Memory Context**: `100_memory/100_cursor-memory-context.md` (Primary scaffold)
- **DSPy Context**: `100_memory/104_dspy-development-context.md` (Technical foundation)
- **System Overview**: `400_guides/400_system-overview.md` (Architecture context)
- **Context Priority**: `400_guides/400_context-priority-guide.md` (Reading order)

## 🗒️ Change Log

- v2.0: Consolidated all hydration guides into comprehensive system guide
- v1.0: Created individual hydration guides (archived)

---

## 📋 Quick Reference

### **Essential Commands**

```bash
# Test hydration system (Python)
python3 -m src.utils.memory_rehydrator --role planner --task "test" --limit 5

# Test hydration system (Go)
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "test query"

# Run smoke tests
PYTHONPATH=. python3 tests/test_memory_rehydrator_smoke.py

# Start monitoring
python3 src/n8n_workflows/hydration_monitor.py

# Check performance
python3 scripts/hydration_benchmark.py
```

### **Role-Specific Usage**

```python
# Planner context
bundle = build_hydration_bundle(role="planner", task="strategic planning", token_budget=1200)

# Implementer context
bundle = build_hydration_bundle(role="implementer", task="code implementation", token_budget=1200)
```

### **Performance Targets**

- Bundle creation: < 5s
- Memory usage: < 100MB for 10 bundles
- Success rate: > 95%
- Token efficiency: > 80%

---

## 🏷️ Session Registry Integration

The Session Registry provides enhanced context for memory rehydration by tracking active Scribe sessions and their rich metadata.

### **Session Context Enhancement**

Session registry data is automatically integrated into memory rehydration bundles:

```python
# Enhanced memory context with session data
def build_enhanced_hydration_bundle(role, task, token_budget=1200):
    """Build hydration bundle with session registry integration"""

    # Get base bundle
    base_bundle = build_hydration_bundle(role, task, token_budget)

    # Integrate session registry data
    from scripts.session_context_integration import SessionContextIntegrator
    integrator = SessionContextIntegrator()

    session_context = integrator.get_active_sessions_context()
    session_summary = integrator.get_session_summary()

    # Enhance bundle with session data
    enhanced_bundle = base_bundle.copy()
    enhanced_bundle.session_registry = session_context
    enhanced_bundle.session_summary = session_summary

    return enhanced_bundle
```

### **Session Discovery Integration**

Find sessions by context tags during memory rehydration:

```python
# Find sessions by context tags
def find_related_sessions(tags):
    """Find sessions related to current task"""
    from scripts.session_context_integration import SessionContextIntegrator

    integrator = SessionContextIntegrator()
    matching_sessions = integrator.get_sessions_by_context(tags)

    return matching_sessions
```

### **Enhanced Context Examples**

#### **Planner Role with Session Context**

```python
# Planner bundle with active session awareness
bundle = build_enhanced_hydration_bundle(
    role="planner",
    task="strategic planning for Q4 development",
    token_budget=1200
)

# Bundle now includes:
# - Active Scribe sessions
# - Session context tags
# - Related session information
# - Session summary for quick overview
```

#### **Implementer Role with Session Context**

```python
# Implementer bundle with technical session context
bundle = build_enhanced_hydration_bundle(
    role="implementer",
    task="debug DSPy integration issues",
    token_budget=1200
)

# Bundle includes:
# - Active debugging sessions
# - Implementation session context
# - Related technical sessions
# - Session priority and type information
```

### **Session Registry CLI Integration**

Direct integration with memory rehydration commands:

```bash
# Get session context with memory rehydration
python scripts/session_context_integration.py integrate

# Find sessions by context tags
python scripts/session_context_integration.py context --tags dspy testing

# Get active sessions summary
python scripts/session_context_integration.py summary
```

### **Integration Benefits**

- **🎯 Enhanced Context**: Rich session metadata for better AI understanding
- **🔍 Session Discovery**: Find related sessions by context tags
- **📊 Active Session Awareness**: Know what sessions are currently running
- **🏷️ Context Tagging**: Rich metadata for session categorization
- **⚡ Real-time Updates**: Live session status and context information
