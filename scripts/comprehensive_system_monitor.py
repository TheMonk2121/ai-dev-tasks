#!/usr/bin/env python3
"""
Comprehensive System Monitor - Industry Standards Compliance
Implements Grafana-style monitoring, database health metrics, and automated alerts
Based on industry best practices from web research
"""

import logging
import os
import queue
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

import psutil
import psycopg2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseMetrics:
    """Database health metrics based on industry standards"""

    connection_count: int
    connection_time_ms: float
    connection_errors: int
    query_response_time_ms: float
    active_queries: int
    cache_hit_ratio: float
    timestamp: datetime


@dataclass
class PipelineMetrics:
    """Pipeline performance metrics"""

    throughput_requests_per_second: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime


@dataclass
class SystemHealth:
    """Overall system health status"""

    status: str  # healthy, warning, critical
    score: float  # 0.0 to 1.0
    issues: List[str]
    recommendations: List[str]
    timestamp: datetime


class DatabaseHealthMonitor:
    """Database health monitoring based on industry best practices"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.metrics_history = deque(maxlen=1000)
        self.connection_pool = []
        self.max_connections = 20

    def get_connection_metrics(self) -> DatabaseMetrics:
        """Get comprehensive database connection metrics"""
        start_time = time.time()

        try:
            # Test connection establishment time
            conn = psycopg2.connect(self.database_url)
            connection_time = (time.time() - start_time) * 1000

            # Get connection count
            with conn.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
                _row = cursor.fetchone()
                active_connections = _row[0] if _row else 0

                # Get cache hit ratio
                cursor.execute(
                    """
                    SELECT
                        CASE
                            WHEN sum(heap_blks_hit) + sum(heap_blks_read) = 0 THEN 0
                            ELSE sum(heap_blks_hit)::float / (sum(heap_blks_hit) + sum(heap_blks_read))::float
                        END as cache_hit_ratio
                    FROM pg_statio_user_tables
                """
                )
                _row = cursor.fetchone()
                cache_hit_ratio = (_row[0] if _row else 0.0) or 0.0

                # Get active queries
                cursor.execute(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND query NOT LIKE '%pg_stat_activity%'"
                )
                _row = cursor.fetchone()
                active_queries = _row[0] if _row else 0

            conn.close()

            # Test query response time
            query_start = time.time()
            conn = psycopg2.connect(self.database_url)
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            query_time = (time.time() - query_start) * 1000
            conn.close()

            return DatabaseMetrics(
                connection_count=active_connections,
                connection_time_ms=connection_time,
                connection_errors=0,  # Will be tracked over time
                query_response_time_ms=query_time,
                active_queries=active_queries,
                cache_hit_ratio=cache_hit_ratio,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return DatabaseMetrics(
                connection_count=0,
                connection_time_ms=0,
                connection_errors=1,
                query_response_time_ms=0,
                active_queries=0,
                cache_hit_ratio=0.0,
                timestamp=datetime.now(),
            )


class PipelinePerformanceMonitor:
    """Pipeline performance monitoring with industry-standard metrics"""

    def __init__(self):
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.throughput_window = deque(maxlen=60)  # 1 minute window

    def record_request(self, response_time_ms: float, success: bool = True):
        """Record a request for performance analysis"""
        self.request_times.append(response_time_ms)
        self.throughput_window.append(time.time())

        if not success:
            self.error_counts[datetime.now().strftime("%Y-%m-%d %H:%M")] += 1

    def get_performance_metrics(self) -> PipelineMetrics:
        """Calculate comprehensive performance metrics"""
        if not self.request_times:
            return PipelineMetrics(
                throughput_requests_per_second=0.0,
                latency_p50_ms=0.0,
                latency_p95_ms=0.0,
                latency_p99_ms=0.0,
                error_rate=0.0,
                memory_usage_mb=psutil.virtual_memory().used / 1024 / 1024,
                cpu_usage_percent=psutil.cpu_percent(),
                timestamp=datetime.now(),
            )

        # Calculate throughput (requests per second in last minute)
        now = time.time()
        recent_requests = [t for t in self.throughput_window if now - t <= 60]
        throughput = len(recent_requests) / 60.0

        # Calculate latency percentiles
        sorted_times = sorted(self.request_times)
        p50_idx = int(len(sorted_times) * 0.5)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)

        # Calculate error rate
        total_requests = len(self.request_times)
        total_errors = sum(self.error_counts.values())
        error_rate = total_errors / total_requests if total_requests > 0 else 0.0

        return PipelineMetrics(
            throughput_requests_per_second=throughput,
            latency_p50_ms=sorted_times[p50_idx] if p50_idx < len(sorted_times) else 0.0,
            latency_p95_ms=sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0.0,
            latency_p99_ms=sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0.0,
            error_rate=error_rate,
            memory_usage_mb=psutil.virtual_memory().used / 1024 / 1024,
            cpu_usage_percent=psutil.cpu_percent(),
            timestamp=datetime.now(),
        )


class SystemHealthAnalyzer:
    """System health analysis with industry-standard scoring"""

    def __init__(self, db_monitor: DatabaseHealthMonitor, pipeline_monitor: PipelinePerformanceMonitor):
        self.db_monitor = db_monitor
        self.pipeline_monitor = pipeline_monitor
        self.health_history = deque(maxlen=100)

    def analyze_system_health(self) -> SystemHealth:
        """Analyze overall system health with industry-standard metrics"""
        db_metrics = self.db_monitor.get_connection_metrics()
        pipeline_metrics = self.pipeline_monitor.get_performance_metrics()

        issues = []
        recommendations = []
        score = 1.0

        # Database Health Analysis
        if db_metrics.connection_time_ms > 100:
            issues.append(f"High database connection time: {db_metrics.connection_time_ms:.1f}ms")
            score -= 0.2
            recommendations.append("Optimize database connection pooling")

        if db_metrics.cache_hit_ratio < 0.8:
            issues.append(f"Low cache hit ratio: {db_metrics.cache_hit_ratio:.1%}")
            score -= 0.15
            recommendations.append("Review and optimize database queries")

        if db_metrics.connection_errors > 0:
            issues.append(f"Database connection errors: {db_metrics.connection_errors}")
            score -= 0.3
            recommendations.append("Investigate database connectivity issues")

        # Pipeline Performance Analysis
        if pipeline_metrics.latency_p95_ms > 1000:
            issues.append(f"High 95th percentile latency: {pipeline_metrics.latency_p95_ms:.1f}ms")
            score -= 0.2
            recommendations.append("Optimize pipeline processing and caching")

        if pipeline_metrics.error_rate > 0.05:
            issues.append(f"High error rate: {pipeline_metrics.error_rate:.1%}")
            score -= 0.25
            recommendations.append("Investigate error patterns and implement fixes")

        if pipeline_metrics.memory_usage_mb > 1000:
            issues.append(f"High memory usage: {pipeline_metrics.memory_usage_mb:.1f}MB")
            score -= 0.1
            recommendations.append("Review memory usage patterns and optimize")

        # Determine overall status
        if score >= 0.9:
            status = "healthy"
        elif score >= 0.7:
            status = "warning"
        else:
            status = "critical"

        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))

        health = SystemHealth(
            status=status, score=score, issues=issues, recommendations=recommendations, timestamp=datetime.now()
        )

        self.health_history.append(health)
        return health


class MonitoringDashboard:
    """Real-time monitoring dashboard with industry-standard visualizations"""

    def __init__(self):
        self.db_monitor = DatabaseHealthMonitor(
            os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")
        )
        self.pipeline_monitor = PipelinePerformanceMonitor()
        self.health_analyzer = SystemHealthAnalyzer(self.db_monitor, self.pipeline_monitor)
        self.monitoring_active = False
        self.metrics_queue = queue.Queue()

    def start_monitoring(self):
        """Start continuous monitoring"""
        self.monitoring_active = True
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
        logger.info("🔄 Comprehensive system monitoring started")

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("⏹️ System monitoring stopped")

    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                db_metrics = self.db_monitor.get_connection_metrics()
                pipeline_metrics = self.pipeline_monitor.get_performance_metrics()
                health = self.health_analyzer.analyze_system_health()

                # Store in queue for dashboard access
                self.metrics_queue.put(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "database": asdict(db_metrics),
                        "pipeline": asdict(pipeline_metrics),
                        "health": asdict(health),
                    }
                )

                # Log critical issues
                if health.status == "critical":
                    logger.critical(f"🚨 CRITICAL SYSTEM ISSUES: {health.issues}")
                elif health.status == "warning":
                    logger.warning(f"⚠️ SYSTEM WARNINGS: {health.issues}")

                time.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics for dashboard display"""
        try:
            # Get latest metrics from queue
            latest_metrics = None
            while not self.metrics_queue.empty():
                latest_metrics = self.metrics_queue.get_nowait()

            if latest_metrics is not None:
                return latest_metrics

            # If no recent metrics, generate current ones
            db_metrics = self.db_monitor.get_connection_metrics()
            pipeline_metrics = self.pipeline_monitor.get_performance_metrics()
            health = self.health_analyzer.analyze_system_health()

            metrics_now = {
                "timestamp": datetime.now().isoformat(),
                "database": asdict(db_metrics),
                "pipeline": asdict(pipeline_metrics),
                "health": asdict(health),
            }
            return metrics_now

        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {"error": str(e)}

    def generate_health_report(self) -> str:
        """Generate comprehensive health report"""
        metrics = self.get_current_metrics()

        if "error" in metrics:
            return f"❌ Error generating report: {metrics['error']}"

        health = metrics.get("health", {})
        db = metrics.get("database", {})
        pipeline = metrics.get("pipeline", {})

        report = f"""
🏥 COMPREHENSIVE SYSTEM HEALTH REPORT
{'='*50}
📊 OVERALL STATUS: {health['status'].upper()}
🎯 HEALTH SCORE: {health['score']:.1%}
⏰ TIMESTAMP: {health['timestamp']}

🔍 DATABASE HEALTH:
  • Active Connections: {db['connection_count']}
  • Connection Time: {db['connection_time_ms']:.1f}ms
  • Cache Hit Ratio: {db['cache_hit_ratio']:.1%}
  • Active Queries: {db['active_queries']}
  • Connection Errors: {db['connection_errors']}

⚡ PIPELINE PERFORMANCE:
  • Throughput: {pipeline['throughput_requests_per_second']:.1f} req/s
  • P50 Latency: {pipeline['latency_p50_ms']:.1f}ms
  • P95 Latency: {pipeline['latency_p95_ms']:.1f}ms
  • P99 Latency: {pipeline['latency_p99_ms']:.1f}ms
  • Error Rate: {pipeline['error_rate']:.1%}
  • Memory Usage: {pipeline['memory_usage_mb']:.1f}MB
  • CPU Usage: {pipeline['cpu_usage_percent']:.1f}%

🚨 ISSUES IDENTIFIED:
"""

        if health["issues"]:
            for issue in health["issues"]:
                report += f"  • {issue}\n"
        else:
            report += "  • No issues detected ✅\n"

        if health["recommendations"]:
            report += "\n💡 RECOMMENDATIONS:\n"
            for rec in health["recommendations"]:
                report += f"  • {rec}\n"

        return report


def main():
    """Main monitoring application"""
    print("🚀 Starting Comprehensive System Monitor...")

    # Initialize dashboard
    dashboard = MonitoringDashboard()

    try:
        # Start monitoring
        dashboard.start_monitoring()

        # Wait a moment for initial metrics
        time.sleep(10)

        # Generate and display health report
        report = dashboard.generate_health_report()
        print(report)

        # Keep running for continuous monitoring
        print("\n🔄 Continuous monitoring active. Press Ctrl+C to stop...")
        while True:
            time.sleep(30)
            report = dashboard.generate_health_report()
            print("\n" + "=" * 50)
            print(report)

    except KeyboardInterrupt:
        print("\n⏹️ Stopping monitoring...")
        dashboard.stop_monitoring()
        print("✅ Monitoring stopped successfully")


if __name__ == "__main__":
    main()
