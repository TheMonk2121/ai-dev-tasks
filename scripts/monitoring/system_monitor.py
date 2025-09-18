from __future__ import annotations
import json
import os
import psycopg
import sys
import time
from datetime import datetime
from typing import Any
    from monitoring.health_endpoints import HealthEndpointManager
    from monitoring.metrics import get_metrics
    from monitoring.production_monitor import ProductionMonitor
# Add project paths
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config
import subprocess
import argparse
from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
System Monitor for AI Development Tasks

Provides comprehensive monitoring of:
- Database health and performance
- Memory system status
- DSPy RAG system metrics
- System resource usage
- Error tracking and alerts
"""

# Add src directory to Python path for monitoring modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
except ImportError as e:
    print(f"❌ Monitoring modules not available: {e}")
    sys.exit(1)

class SystemMonitor:
    """Comprehensive system monitoring for AI development tasks"""

    def __init__(self):
        self.health_manager = HealthEndpointManager()
        self.production_monitor = ProductionMonitor()
        self.start_time = datetime.now()

    def get_system_health(self) -> dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            health_status = self.health_manager.get_health_status()
            return {
                "timestamp": datetime.now().isoformat(),
                "uptime": str(datetime.now() - self.start_time),
                "overall_status": health_status["status"],
                "dependencies": health_status["dependencies"],
                "unhealthy_count": health_status["unhealthy_dependencies"],
                "degraded_count": health_status["degraded_dependencies"],
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": f"Health check failed: {e}",
                "overall_status": "unhealthy",
            }

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get system performance metrics"""
        try:
            metrics = get_metrics()
            return {
                "timestamp": datetime.now().isoformat(),
                "request_total": metrics.get("request_total", 0),
                "request_latency_avg": self._calculate_avg_latency(metrics),
                "memory_usage_bytes": metrics.get("memory_usage_bytes", 0),
                "error_total": metrics.get("error_total", 0),
                "token_total": metrics.get("token_total", 0),
            }
        except Exception as e:
            return {"timestamp": datetime.now().isoformat(), "error": f"Metrics collection failed: {e}"}

    def get_database_status(self) -> dict[str, Any]:
        """Get detailed database status"""
        try:

            start_time = time.time()

            with psycopg.connect("postgresql://danieljacobs@localhost:5432/ai_agency") as conn:
                with conn.cursor() as cursor:
                    # Get basic counts
                    cursor.execute("SELECT COUNT(*) FROM documents")
                    row = cursor.fetchone()
                    doc_count = int(row[0]) if row else 0

                    cursor.execute("SELECT COUNT(*) FROM document_chunks")
                    row = cursor.fetchone()
                    chunk_count = int(row[0]) if row else 0

                    cursor.execute("SELECT COUNT(*) FROM conversation_memory")
                    row = cursor.fetchone()
                    memory_count = int(row[0]) if row else 0

                    # Check vector extension
                    cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
                    vector_ext = cursor.fetchone()

                    # Get connection info
                    cursor.execute("SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'dspy_rag'")
                    row = cursor.fetchone()
                    active_connections = int(row[0]) if row else 0

            response_time = time.time() - start_time

            return {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "response_time": response_time,
                "documents": doc_count,
                "chunks": chunk_count,
                "memory_entries": memory_count,
                "vector_extension": bool(vector_ext),
                "active_connections": active_connections,
            }
        except Exception as e:
            return {"timestamp": datetime.now().isoformat(), "status": "unhealthy", "error": str(e)}

    def get_memory_system_status(self) -> dict[str, Any]:
        """Get memory system status"""
        try:
            # Test memory rehydration
            start_time = time.time()

            result = subprocess.run(
                ["./scripts/memory_up.sh", "-r", "planner", "-q", "status check"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            response_time = time.time() - start_time

            return {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy" if result.returncode == 0 else "unhealthy",
                "response_time": response_time,
                "return_code": result.returncode,
                "output_length": len(result.stdout),
                "error_length": len(result.stderr),
            }
        except Exception as e:
            return {"timestamp": datetime.now().isoformat(), "status": "unhealthy", "error": str(e)}

    def _calculate_avg_latency(self, metrics: dict[str, Any]) -> float:
        """Calculate average request latency"""
        try:
            total = metrics.get("request_latency_seconds_sum", 0)
            count = metrics.get("request_latency_seconds_count", 0)
            return total / count if count > 0 else 0.0
        except:
            return 0.0

    def generate_report(self, format: str = "text") -> str:
        """Generate comprehensive system report"""
        health = self.get_system_health()
        metrics = self.get_performance_metrics()
        db_status = self.get_database_status()
        memory_status = self.get_memory_system_status()

        report = {
            "system_health": health,
            "performance_metrics": metrics,
            "database_status": db_status,
            "memory_system_status": memory_status,
        }

        if format == "json":
            return json.dumps(report, indent=2, default=str)
        else:
            return self._format_text_report(report)

    def _format_text_report(self, report: dict[str, Any]) -> str:
        """Format report as human-readable text"""
        lines = []
        lines.append("=" * 60)
        lines.append("🤖 AI DEVELOPMENT TASKS - SYSTEM MONITOR")
        lines.append("=" * 60)
        health = report.get("system_health", {})
        lines.append(f"Timestamp: {health.get('timestamp', datetime.now().isoformat())}")
        lines.append(f"Uptime: {health.get('uptime', 'unknown')}")
        lines.append("")

        # Overall Status
        lines.append("📊 OVERALL STATUS")
        lines.append("-" * 20)
        overall = str(health.get("overall_status", "unknown")).upper()
        lines.append(f"Status: {overall}")
        lines.append(f"Unhealthy Dependencies: {health.get('unhealthy_count', 0)}")
        lines.append(f"Degraded Dependencies: {health.get('degraded_count', 0)}")
        lines.append("")

        # Database Status
        lines.append("🗄️ DATABASE STATUS")
        lines.append("-" * 20)
        db = report["database_status"]
        lines.append(f"Status: {db['status'].upper()}")
        if "error" not in db:
            lines.append(f"Response Time: {db['response_time']:.3f}s")
            lines.append(f"Documents: {db['documents']}")
            lines.append(f"Chunks: {db['chunks']}")
            lines.append(f"Memory Entries: {db['memory_entries']}")
            lines.append(f"Vector Extension: {'✅' if db['vector_extension'] else '❌'}")
            lines.append(f"Active Connections: {db['active_connections']}")
        else:
            lines.append(f"Error: {db['error']}")
        lines.append("")

        # Memory System Status
        lines.append("🧠 MEMORY SYSTEM STATUS")
        lines.append("-" * 25)
        mem = report["memory_system_status"]
        lines.append(f"Status: {mem['status'].upper()}")
        if "error" not in mem:
            lines.append(f"Response Time: {mem['response_time']:.3f}s")
            lines.append(f"Return Code: {mem['return_code']}")
            lines.append(f"Output Size: {mem['output_length']} chars")
        else:
            lines.append(f"Error: {mem['error']}")
        lines.append("")

        # Performance Metrics
        lines.append("⚡ PERFORMANCE METRICS")
        lines.append("-" * 22)
        perf = report["performance_metrics"]
        if "error" not in perf:
            lines.append(f"Total Requests: {perf['request_total']}")
            lines.append(f"Avg Latency: {perf['request_latency_avg']:.3f}s")
            lines.append(f"Memory Usage: {perf['memory_usage_bytes']:,} bytes")
            lines.append(f"Total Errors: {perf['error_total']}")
            lines.append(f"Total Tokens: {perf['token_total']}")
        else:
            lines.append(f"Error: {perf['error']}")
        lines.append("")

        # Dependencies
        lines.append("🔗 DEPENDENCIES")
        lines.append("-" * 12)
        deps = health.get("dependencies", {}) or {}
        if isinstance(deps, dict):
            for name, dep in deps.items():
                status = dep.get("status", "unknown") if isinstance(dep, dict) else str(dep)
                rt = dep.get("response_time", 0.0) if isinstance(dep, dict) else 0.0
                status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                lines.append(f"{status_icon} {name}: {status} ({float(rt):.3f}s)")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

def main():
    """Main monitoring function"""

    parser = argparse.ArgumentParser(description="System Monitor for AI Development Tasks")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--watch", action="store_true", help="Watch mode - continuously monitor system")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in seconds (default: 30)")

    args = parser.parse_args()

    monitor = SystemMonitor()

    if args.watch:
        print("🔍 Starting continuous monitoring... (Press Ctrl+C to stop)")
        try:
            while True:
                os.system("clear" if os.name == "posix" else "cls")
                print(monitor.generate_report(args.format))
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    else:
        print(monitor.generate_report(args.format))

if __name__ == "__main__":
    main()
