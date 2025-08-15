<!-- ANCHOR_KEY: hydration-integration -->
<!-- ANCHOR_PRIORITY: 40 -->
<!-- ROLE_PINS: ["implementer"] -->

# 🔗 Hydration Integration Guide

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Integration patterns and automation for hydration system | Setting up monitoring or automation | Configure n8n workflows and start dashboard |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Integration framework implemented
- **Priority**: 🔥 High - Essential for production deployment
- **Points**: 5 - High complexity, critical importance
- **Dependencies**: dspy-rag-system/src/n8n_workflows/hydration_monitor.py, dspy-rag-system/src/mission_dashboard/hydration_dashboard.py
- **Next Steps**: Configure n8n workflows and start monitoring

## 🔧 Integration Architecture

### **System Components**

```
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

## 📊 Dashboard Integration

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

## 🔗 Related Documentation

- **Health Monitor**: `dspy-rag-system/src/n8n_workflows/hydration_monitor.py` (n8n integration)
- **Performance Dashboard**: `dspy-rag-system/src/mission_dashboard/hydration_dashboard.py` (Real-time monitoring)
- **Testing Guide**: `400_guides/400_hydration-testing-guide.md` (Testing framework)
- **Planner Guide**: `400_guides/400_planner-hydration-guide.md` (Planner integration)
- **Implementer Guide**: `400_guides/400_implementer-hydration-guide.md` (Implementer integration)

## 🗒️ Change Log

- v1.0 (initial): Created comprehensive hydration integration guide
