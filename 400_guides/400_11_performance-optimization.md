# ⚡ Performance & Optimization

<!-- ANCHOR_KEY: performance-optimization -->
<!-- ANCHOR_PRIORITY: 12 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

## 🔍 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete performance optimization and monitoring guide | Optimizing system performance, monitoring metrics, or improving efficiency | Read 12 (Advanced Configurations) then apply optimization techniques |

- **what this file is**: Comprehensive performance optimization and monitoring guide.

- **read when**: When optimizing system performance, monitoring metrics, or improving efficiency.

- **do next**: Read 12 (Advanced Configurations) then apply the optimization techniques to your systems.

## 🎯 **Current Status**
- **Priority**: 🔥 **HIGH** - Essential for system performance
- **Phase**: 4 of 4 (Advanced Topics)
- **Dependencies**: 09-10 (AI Frameworks & Integrations)

## 🎯 **Purpose**

This guide covers comprehensive performance optimization and monitoring including:
- **Performance monitoring and metrics collection**
- **System optimization and resource management**
- **Caching strategies and optimization**
- **Database performance and optimization**
- **AI model performance optimization**
- **Memory and CPU optimization**
- **Network and I/O optimization**

## 📋 When to Use This Guide

- **Optimizing system performance**
- **Monitoring performance metrics**
- **Improving resource efficiency**
- **Optimizing database queries**
- **Improving AI model performance**
- **Reducing latency and response times**
- **Scaling system capacity**

## 🎯 Expected Outcomes

- **Optimized system performance** with improved efficiency
- **Comprehensive performance monitoring** and alerting
- **Efficient resource utilization** and cost optimization
- **Fast response times** and low latency
- **Scalable architecture** for growth
- **Proactive performance management**
- **Data-driven optimization decisions**

## 📋 Policies

### Performance Monitoring
- **Real-time monitoring**: Monitor performance metrics in real-time
- **Proactive alerting**: Alert on performance issues before they impact users
- **Historical analysis**: Maintain historical data for trend analysis
- **Baseline establishment**: Establish performance baselines for comparison

### Optimization Strategies
- **Data-driven decisions**: Make optimization decisions based on metrics
- **Incremental improvements**: Implement optimizations incrementally
- **Testing and validation**: Test all optimizations before deployment
- **Rollback procedures**: Maintain ability to rollback optimizations

### Resource Management
- **Efficient resource utilization**: Optimize resource usage and costs
- **Capacity planning**: Plan for future capacity needs
- **Cost optimization**: Optimize costs while maintaining performance
- **Resource monitoring**: Monitor resource usage and trends

## 📊 **Performance Monitoring Framework**

### **Comprehensive Metrics Collection**

#### **System Performance Metrics**
```python
from typing import Dict, Any, List, Optional
import psutil
import time
import statistics
from dataclasses import dataclass

@dataclass
class SystemMetrics:
    """System performance metrics collection."""

    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    process_count: int
    load_average: List[float]

class PerformanceMonitor:
    """Comprehensive performance monitoring system."""

    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {}
        self.performance_baselines = {}

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics."""

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent

        # Network metrics
        network_io = psutil.net_io_counters()
        network_metrics = {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv
        }

        # Process metrics
        process_count = len(psutil.pids())

        # Load average (Unix-like systems)
        try:
            load_average = psutil.getloadavg()
        except AttributeError:
            load_average = [0.0, 0.0, 0.0]

        metrics = SystemMetrics(
            timestamp=time.isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_usage_percent,
            network_io=network_metrics,
            process_count=process_count,
            load_average=list(load_average)
        )

        self.metrics_history.append(metrics)
        return metrics

    def set_alert_threshold(self, metric_name: str, threshold: float, operator: str = ">"):
        """Set alert threshold for a metric."""
        self.alert_thresholds[metric_name] = {
            "threshold": threshold,
            "operator": operator
        }

    def check_alerts(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """Check metrics against alert thresholds."""
        alerts = []

        for metric_name, threshold_config in self.alert_thresholds.items():
            current_value = getattr(metrics, metric_name, None)

            if current_value is not None:
                threshold = threshold_config["threshold"]
                operator = threshold_config["operator"]

                is_alert = False
                if operator == ">":
                    is_alert = current_value > threshold
                elif operator == "<":
                    is_alert = current_value < threshold
                elif operator == ">=":
                    is_alert = current_value >= threshold
                elif operator == "<=":
                    is_alert = current_value <= threshold

                if is_alert:
                    alerts.append({
                        "metric": metric_name,
                        "current_value": current_value,
                        "threshold": threshold,
                        "operator": operator,
                        "timestamp": metrics.timestamp
                    })

        return alerts

    def get_performance_summary(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the specified time window."""

        cutoff_time = time.time() - (time_window_hours * 3600)
        recent_metrics = [
            m for m in self.metrics_history
            if time.mktime(time.strptime(m.timestamp, "%Y-%m-%dT%H:%M:%S")) > cutoff_time
        ]

        if not recent_metrics:
            return {"error": "No metrics available for time window"}

        # Calculate statistics
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        disk_values = [m.disk_usage_percent for m in recent_metrics]

        return {
            "time_window_hours": time_window_hours,
            "metrics_count": len(recent_metrics),
            "cpu": {
                "average": statistics.mean(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
                "p95": statistics.quantiles(cpu_values, n=20)[18] if len(cpu_values) >= 20 else 0
            },
            "memory": {
                "average": statistics.mean(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
                "p95": statistics.quantiles(memory_values, n=20)[18] if len(memory_values) >= 20 else 0
            },
            "disk": {
                "average": statistics.mean(disk_values),
                "max": max(disk_values),
                "min": min(disk_values),
                "p95": statistics.quantiles(disk_values, n=20)[18] if len(disk_values) >= 20 else 0
            }
        }
```

### **Application Performance Monitoring**

#### **APM Framework**
```python
import time
import functools
from typing import Dict, Any, Optional, Callable
import threading

class APMMonitor:
    """Application Performance Monitoring framework."""

    def __init__(self):
        self.traces = []
        self.spans = {}
        self.performance_data = {}
        self.lock = threading.Lock()

    def start_trace(self, trace_id: str, operation_name: str) -> str:
        """Start a new trace."""
        with self.lock:
            trace = {
                "trace_id": trace_id,
                "operation_name": operation_name,
                "start_time": time.time(),
                "spans": [],
                "status": "active"
            }
            self.traces.append(trace)
            return trace_id

    def end_trace(self, trace_id: str, status: str = "success"):
        """End a trace."""
        with self.lock:
            for trace in self.traces:
                if trace["trace_id"] == trace_id:
                    trace["end_time"] = time.time()
                    trace["duration"] = trace["end_time"] - trace["start_time"]
                    trace["status"] = status
                    break

    def start_span(self, trace_id: str, span_name: str) -> str:
        """Start a span within a trace."""
        span_id = f"{trace_id}_{span_name}_{int(time.time() * 1000)}"

        with self.lock:
            span = {
                "span_id": span_id,
                "trace_id": trace_id,
                "name": span_name,
                "start_time": time.time(),
                "status": "active"
            }
            self.spans[span_id] = span

            # Add to trace
            for trace in self.traces:
                if trace["trace_id"] == trace_id:
                    trace["spans"].append(span_id)
                    break

        return span_id

    def end_span(self, span_id: str, status: str = "success"):
        """End a span."""
        with self.lock:
            if span_id in self.spans:
                span = self.spans[span_id]
                span["end_time"] = time.time()
                span["duration"] = span["end_time"] - span["start_time"]
                span["status"] = status

    def add_span_attribute(self, span_id: str, key: str, value: Any):
        """Add attribute to a span."""
        with self.lock:
            if span_id in self.spans:
                if "attributes" not in self.spans[span_id]:
                    self.spans[span_id]["attributes"] = {}
                self.spans[span_id]["attributes"][key] = value

    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of a trace."""
        with self.lock:
            for trace in self.traces:
                if trace["trace_id"] == trace_id:
                    spans = [self.spans.get(span_id, {}) for span_id in trace["spans"]]
                    return {
                        "trace_id": trace_id,
                        "operation_name": trace["operation_name"],
                        "duration": trace.get("duration", 0),
                        "status": trace["status"],
                        "span_count": len(spans),
                        "spans": spans
                    }
        return None

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics."""
        with self.lock:
            completed_traces = [t for t in self.traces if "duration" in t]

            if not completed_traces:
                return {"error": "No completed traces available"}

            durations = [t["duration"] for t in completed_traces]
            success_count = len([t for t in completed_traces if t["status"] == "success"])

            return {
                "total_traces": len(completed_traces),
                "success_rate": success_count / len(completed_traces),
                "average_duration": statistics.mean(durations),
                "max_duration": max(durations),
                "min_duration": min(durations),
                "p95_duration": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else 0
            }

def apm_trace(operation_name: str):
    """Decorator for APM tracing."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get APM monitor instance (you'd need to make this available globally)
            apm = get_apm_monitor()

            trace_id = f"{func.__name__}_{int(time.time() * 1000)}"
            apm.start_trace(trace_id, operation_name)

            try:
                result = func(*args, **kwargs)
                apm.end_trace(trace_id, "success")
                return result
            except Exception as e:
                apm.end_trace(trace_id, "error")
                raise

        return wrapper
    return decorator

def get_apm_monitor() -> APMMonitor:
    """Get global APM monitor instance."""
    # Implementation to get global APM monitor
    return APMMonitor()
```

## 🔧 **System Optimization**

### **Resource Optimization**

#### **Memory Optimization**
```python
import gc
import sys
import psutil
from typing import Dict, Any, List

class MemoryOptimizer:
    """Memory optimization and management."""

    def __init__(self):
        self.memory_threshold = 80.0  # 80% memory usage threshold
        self.optimization_history = []

    def check_memory_usage(self) -> Dict[str, Any]:
        """Check current memory usage."""
        memory = psutil.virtual_memory()

        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "is_critical": memory.percent > self.memory_threshold
        }

    def optimize_memory(self) -> List[str]:
        """Perform memory optimization."""
        optimizations = []

        # Check if optimization is needed
        memory_info = self.check_memory_usage()
        if not memory_info["is_critical"]:
            return ["Memory usage is within normal limits"]

        # Force garbage collection
        collected = gc.collect()
        optimizations.append(f"Garbage collection freed {collected} objects")

        # Clear Python cache
        if hasattr(sys, 'getsizeof'):
            cache_size_before = sum(sys.getsizeof(obj) for obj in gc.get_objects())
            gc.collect()
            cache_size_after = sum(sys.getsizeof(obj) for obj in gc.get_objects())
            freed = cache_size_before - cache_size_after
            optimizations.append(f"Cache optimization freed {freed} bytes")

        # Record optimization
        self.optimization_history.append({
            "timestamp": time.isoformat(),
            "memory_before": memory_info["percent"],
            "optimizations": optimizations
        })

        return optimizations

    def get_memory_usage_by_process(self) -> List[Dict[str, Any]]:
        """Get memory usage by process."""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "memory_percent": proc.info['memory_percent'],
                    "memory_rss": proc.info['memory_info'].rss if proc.info['memory_info'] else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by memory usage
        processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
        return processes[:10]  # Top 10 processes
```

#### **CPU Optimization**
```python
class CPUOptimizer:
    """CPU optimization and management."""

    def __init__(self):
        self.cpu_threshold = 80.0  # 80% CPU usage threshold
        self.optimization_history = []

    def check_cpu_usage(self) -> Dict[str, Any]:
        """Check current CPU usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        return {
            "usage_percent": cpu_percent,
            "cpu_count": cpu_count,
            "frequency": cpu_freq.current if cpu_freq else None,
            "is_critical": cpu_percent > self.cpu_threshold
        }

    def get_cpu_usage_by_process(self) -> List[Dict[str, Any]]:
        """Get CPU usage by process."""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc.info['cpu_percent'] = proc.cpu_percent()
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes[:10]  # Top 10 processes

    def optimize_cpu_usage(self) -> List[str]:
        """Perform CPU optimization."""
        optimizations = []

        # Check if optimization is needed
        cpu_info = self.check_cpu_usage()
        if not cpu_info["is_critical"]:
            return ["CPU usage is within normal limits"]

        # Get high CPU processes
        high_cpu_processes = [
            p for p in self.get_cpu_usage_by_process()
            if p['cpu_percent'] and p['cpu_percent'] > 10
        ]

        for process in high_cpu_processes:
            optimizations.append(f"High CPU process: {process['name']} (PID: {process['pid']}) - {process['cpu_percent']:.1f}%")

        # Record optimization
        self.optimization_history.append({
            "timestamp": time.isoformat(),
            "cpu_before": cpu_info["usage_percent"],
            "optimizations": optimizations
        })

        return optimizations
```

### **Database Performance Optimization**

#### **Database Performance Monitor**
```python
import sqlite3
import psycopg2
from typing import Dict, Any, List, Optional

class DatabasePerformanceMonitor:
    """Database performance monitoring and optimization."""

    def __init__(self, db_type: str, connection_string: str):
        self.db_type = db_type
        self.connection_string = connection_string
        self.performance_history = []

    def get_connection(self):
        """Get database connection."""
        if self.db_type == "sqlite":
            return sqlite3.connect(self.connection_string)
        elif self.db_type == "postgresql":
            return psycopg2.connect(self.connection_string)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def execute_query_with_timing(self, query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """Execute query and measure performance."""
        start_time = time.time()

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    result = None
                    conn.commit()

                duration = time.time() - start_time

                performance_data = {
                    "query": query,
                    "duration": duration,
                    "success": True,
                    "timestamp": time.isoformat(),
                    "row_count": len(result) if result else 0
                }

                self.performance_history.append(performance_data)
                return performance_data

        except Exception as e:
            duration = time.time() - start_time

            performance_data = {
                "query": query,
                "duration": duration,
                "success": False,
                "error": str(e),
                "timestamp": time.isoformat()
            }

            self.performance_history.append(performance_data)
            return performance_data

    def get_slow_queries(self, threshold_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """Get queries that exceed the time threshold."""
        return [
            query for query in self.performance_history
            if query["success"] and query["duration"] > threshold_seconds
        ]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get database performance summary."""
        if not self.performance_history:
            return {"error": "No performance data available"}

        successful_queries = [q for q in self.performance_history if q["success"]]

        if not successful_queries:
            return {"error": "No successful queries found"}

        durations = [q["duration"] for q in successful_queries]

        return {
            "total_queries": len(self.performance_history),
            "successful_queries": len(successful_queries),
            "success_rate": len(successful_queries) / len(self.performance_history),
            "average_duration": statistics.mean(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "p95_duration": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else 0,
            "slow_queries_count": len(self.get_slow_queries())
        }

    def optimize_queries(self) -> List[str]:
        """Generate query optimization recommendations."""
        recommendations = []

        # Analyze slow queries
        slow_queries = self.get_slow_queries()

        for query_data in slow_queries:
            query = query_data["query"]

            # Check for common optimization opportunities
            if "SELECT *" in query.upper():
                recommendations.append(f"Consider selecting specific columns instead of SELECT * in: {query[:100]}...")

            if "ORDER BY" in query.upper() and "LIMIT" not in query.upper():
                recommendations.append(f"Consider adding LIMIT clause to ORDER BY query: {query[:100]}...")

            if "WHERE" not in query.upper() and query.strip().upper().startswith('SELECT'):
                recommendations.append(f"Consider adding WHERE clause to filter data: {query[:100]}...")

        return recommendations
```

## 🚀 **Caching Strategies**

### **Multi-Level Caching System**

#### **Intelligent Caching Framework**
```python
from typing import Dict, Any, Optional, Callable
import hashlib
import json
import time
from functools import wraps

class CacheLevel:
    """Cache level configuration."""

    def __init__(self, name: str, max_size: int, ttl_seconds: int):
        self.name = name
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            self.miss_count += 1
            return None

        # Check TTL
        if time.time() - self.access_times[key] > self.ttl_seconds:
            self._remove(key)
            self.miss_count += 1
            return None

        # Update access time
        self.access_times[key] = time.time()
        self.hit_count += 1
        return self.cache[key]

    def set(self, key: str, value: Any):
        """Set value in cache."""
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = value
        self.access_times[key] = time.time()

    def _remove(self, key: str):
        """Remove key from cache."""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]

    def _evict_oldest(self):
        """Evict oldest cache entries."""
        if not self.access_times:
            return

        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove(oldest_key)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0

        return {
            "name": self.name,
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }

class MultiLevelCache:
    """Multi-level caching system."""

    def __init__(self):
        self.levels = {}
        self.key_generators = {}

    def add_level(self, name: str, max_size: int, ttl_seconds: int):
        """Add a cache level."""
        self.levels[name] = CacheLevel(name, max_size, ttl_seconds)

    def add_key_generator(self, name: str, generator_func: Callable):
        """Add a key generator function."""
        self.key_generators[name] = generator_func

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, checking all levels."""
        for level_name, level in self.levels.items():
            value = level.get(key)
            if value is not None:
                # Promote to higher levels if applicable
                self._promote_to_higher_levels(key, value, level_name)
                return value

        return None

    def set(self, key: str, value: Any, level_name: Optional[str] = None):
        """Set value in cache."""
        if level_name:
            # Set in specific level
            if level_name in self.levels:
                self.levels[level_name].set(key, value)
        else:
            # Set in all levels
            for level in self.levels.values():
                level.set(key, value)

    def _promote_to_higher_levels(self, key: str, value: Any, current_level: str):
        """Promote value to higher cache levels."""
        level_names = list(self.levels.keys())
        current_index = level_names.index(current_level)

        # Promote to higher levels (lower indices)
        for i in range(current_index - 1, -1, -1):
            level_name = level_names[i]
            self.levels[level_name].set(key, value)

    def generate_key(self, generator_name: str, *args, **kwargs) -> str:
        """Generate cache key using specified generator."""
        if generator_name not in self.key_generators:
            raise ValueError(f"Key generator '{generator_name}' not found")

        key_data = self.key_generators[generator_name](*args, **kwargs)
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all cache levels."""
        stats = {}
        for level_name, level in self.levels.items():
            stats[level_name] = level.get_stats()
        return stats

def cache_result(cache: MultiLevelCache, key_generator: str, level_name: Optional[str] = None):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache.generate_key(key_generator, *args, **kwargs)

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, level_name)

            return result

        return wrapper
    return decorator
```

## 📋 **Checklists**

### **Performance Monitoring Checklist**
- [ ] **Real-time monitoring** implemented and active
- [ ] **Performance baselines** established
- [ ] **Alert thresholds** configured and tested
- [ ] **Historical data** collection working
- [ ] **Performance dashboards** created and accessible
- [ ] **Alert notifications** configured and tested
- [ ] **Performance reports** automated

### **System Optimization Checklist**
- [ ] **Memory optimization** implemented and tested
- [ ] **CPU optimization** implemented and tested
- [ ] **Database optimization** implemented and tested
- [ ] **Caching strategies** implemented and working
- [ ] **Resource monitoring** active and alerting
- [ ] **Optimization procedures** documented
- [ ] **Performance improvements** measured and validated

### **Resource Management Checklist**
- [ ] **Resource utilization** optimized
- [ ] **Capacity planning** implemented
- [ ] **Cost optimization** strategies in place
- [ ] **Resource monitoring** comprehensive
- [ ] **Scaling procedures** documented
- [ ] **Resource allocation** optimized
- [ ] **Performance budgets** established

## 🔗 **Interfaces**

### **Performance Monitoring**
- **System Metrics**: Real-time system performance monitoring
- **Application Metrics**: Application performance monitoring
- **Database Metrics**: Database performance monitoring
- **Custom Metrics**: Custom performance metrics collection

### **Optimization Systems**
- **Memory Optimization**: Memory usage optimization and management
- **CPU Optimization**: CPU usage optimization and management
- **Database Optimization**: Database performance optimization
- **Caching Systems**: Multi-level caching and optimization

### **Resource Management**
- **Resource Monitoring**: Comprehensive resource monitoring
- **Capacity Planning**: Capacity planning and scaling
- **Cost Optimization**: Cost optimization and management
- **Performance Analysis**: Performance analysis and reporting

## 📚 **Examples**

### **Performance Monitoring Example**
```python
# Initialize performance monitor
performance_monitor = PerformanceMonitor()

# Set alert thresholds
performance_monitor.set_alert_threshold("cpu_percent", 80.0, ">")
performance_monitor.set_alert_threshold("memory_percent", 85.0, ">")

# Collect metrics
metrics = performance_monitor.collect_system_metrics()

# Check for alerts
alerts = performance_monitor.check_alerts(metrics)
for alert in alerts:
    print(f"Alert: {alert['metric']} = {alert['current_value']} {alert['operator']} {alert['threshold']}")

# Get performance summary
summary = performance_monitor.get_performance_summary(24)  # 24 hours
print(f"CPU Average: {summary['cpu']['average']:.1f}%")
print(f"Memory Average: {summary['memory']['average']:.1f}%")
```

### **APM Tracing Example**
```python
# Initialize APM monitor
apm = APMMonitor()

# Start trace
trace_id = apm.start_trace("user_request", "Process user request")

# Start span
span_id = apm.start_span(trace_id, "database_query")
apm.add_span_attribute(span_id, "query", "SELECT * FROM users")

# Simulate work
time.sleep(0.1)

# End span
apm.end_span(span_id, "success")

# End trace
apm.end_trace(trace_id, "success")

# Get trace summary
summary = apm.get_trace_summary(trace_id)
print(f"Trace duration: {summary['duration']:.3f}s")
print(f"Span count: {summary['span_count']}")
```

### **Caching Example**
```python
# Initialize multi-level cache
cache = MultiLevelCache()

# Add cache levels
cache.add_level("L1", max_size=1000, ttl_seconds=300)  # 5 minutes
cache.add_level("L2", max_size=10000, ttl_seconds=3600)  # 1 hour

# Add key generator
def function_key_generator(func_name, *args, **kwargs):
    return {
        "function": func_name,
        "args": args,
        "kwargs": kwargs
    }

cache.add_key_generator("function", function_key_generator)

# Use caching decorator
@cache_result(cache, "function", "L1")
def expensive_calculation(x, y):
    time.sleep(1)  # Simulate expensive operation
    return x * y

# First call - cache miss
result1 = expensive_calculation(5, 10)  # Takes 1 second

# Second call - cache hit
result2 = expensive_calculation(5, 10)  # Instant

# Get cache stats
stats = cache.get_stats()
for level_name, level_stats in stats.items():
    print(f"{level_name}: Hit rate = {level_stats['hit_rate']:.2%}")
```

## 🔗 **Related Guides**

- **Memory System Overview**: `400_guides/400_00_memory-system-overview.md`
- **AI Frameworks & DSPy**: `400_guides/400_09_ai-frameworks-dspy.md`
- **Integrations & Models**: `400_guides/400_10_integrations-models.md`
- **Advanced Configurations**: `400_guides/400_12_advanced-configurations.md`

## 📚 **References**

- **Performance Monitoring**: `scripts/performance_monitor.py`
- **APM Framework**: `scripts/apm_monitor.py`
- **Database Optimization**: `scripts/db_optimizer.py`
- **Caching System**: `scripts/cache_manager.py`

## 📋 **Changelog**

- **2025-01-XX**: Created as part of Phase 4 documentation restructuring
- **2025-01-XX**: Extracted from `400_guides/400_11_deployments-ops-and-observability.md`
- **2025-01-XX**: Integrated with AI frameworks and system optimization
- **2025-01-XX**: Added comprehensive performance monitoring and optimization frameworks

---

*This file provides comprehensive guidance for performance optimization and monitoring, ensuring high-performance, efficient, and scalable systems.*
