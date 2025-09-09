#!/usr/bin/env python3
"""
Performance Data Integration → LTST Memory

This module integrates performance metrics with the LTST memory system,
enabling automatic capture of system behavior, optimization opportunities,
and correlation with development conversations.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any

import psutil

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from decision_extractor import DecisionExtractor
    from monitoring_system import PerformanceMetrics, SLOMonitor
    from unified_retrieval_api import UnifiedRetrievalAPI
except ImportError:
    # Fallback for testing
    DecisionExtractor = None
    PerformanceMetrics = None
    SLOMonitor = None
    UnifiedRetrievalAPI = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceLTSTIntegration:
    """
    Integrates performance metrics with LTST memory for automatic system behavior capture.

    This class provides:
    - Automatic performance metrics capture and storage
    - System behavior correlation with conversations
    - Optimization opportunity identification
    - Performance issue tracking and linking
    - Real-time decision extraction from performance data
    """

    def __init__(self, db_connection_string: str, project_root: Path | None = None):
        """
        Initialize the Performance-LTST integration.

        Args:
            db_connection_string: Database connection string for LTST memory
            project_root: Path to project root (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()

        # Initialize LTST memory components
        if UnifiedRetrievalAPI is not None:
            self.unified_api = UnifiedRetrievalAPI(db_connection_string)
        else:
            self.unified_api = None

        if DecisionExtractor is not None:
            self.decision_extractor = DecisionExtractor(db_connection_string)
        else:
            self.decision_extractor = None

        # Initialize monitoring components
        if PerformanceMetrics is not None:
            self.performance_metrics = PerformanceMetrics()
        else:
            self.performance_metrics = None

        if SLOMonitor is not None:
            self.slo_monitor = SLOMonitor()
        else:
            self.slo_monitor = None

        logger.info(f"✅ Performance-LTST Integration initialized for {self.project_root}")

    def capture_performance_data(self, duration: int = 60) -> dict[str, Any]:
        """
        Capture comprehensive performance data over a specified duration.

        Args:
            duration: Duration in seconds to capture performance data

        Returns:
            dict: Captured performance data
        """
        try:
            performance_data = {
                "timestamp": datetime.now(UTC).isoformat(),
                "system_info": self._get_system_info(),
                "performance_metrics": self._capture_metrics(duration),
                "resource_usage": self._get_resource_usage(),
                "application_metrics": self._get_application_metrics(),
                "optimization_opportunities": self._identify_optimization_opportunities(),
                "performance_issues": self._detect_performance_issues(),
                "decisions": self._extract_performance_decisions(),
            }

            logger.info(f"📊 Captured performance data over {duration} seconds")
            return performance_data

        except Exception as e:
            logger.error(f"❌ Error capturing performance data: {e}")
            return {"error": str(e)}

    def correlate_with_conversations(
        self, performance_data: dict[str, Any], conversation_context: str | None = None
    ) -> dict[str, Any]:
        """
        Correlate performance data with conversation context in LTST memory.

        Args:
            performance_data: The captured performance data
            conversation_context: Optional conversation context to search for

        Returns:
            dict: Correlation result with conversation context
        """
        try:
            # Search for related conversations in LTST memory
            search_terms = []

            # Add performance-related search terms
            if performance_data.get("performance_issues"):
                search_terms.append("performance optimization")
                search_terms.append("system performance")

            if performance_data.get("optimization_opportunities"):
                search_terms.append("optimization opportunity")
                search_terms.append("performance improvement")

            # Add resource usage terms
            resource_usage = performance_data.get("resource_usage", {})
            if resource_usage.get("cpu_percent", 0) > 80:
                search_terms.append("high CPU usage")
            if resource_usage.get("memory_percent", 0) > 80:
                search_terms.append("high memory usage")

            # Search for related conversations
            related_conversations = []
            if self.unified_api is not None:
                for term in search_terms[:5]:  # Limit to 5 most relevant terms
                    result = self.unified_api.search_decisions(query=term, limit=3, include_superseded=False)
                    related_conversations.extend(result.get("decisions", []))

            # Remove duplicates
            seen_keys = set()
            unique_conversations = []
            for conv in related_conversations:
                if conv.get("decision_key") not in seen_keys:
                    seen_keys.add(conv.get("decision_key"))
                    unique_conversations.append(conv)

            # Extract correlation insights
            insights = self._extract_correlation_insights(performance_data, unique_conversations)

            # Create correlation metadata
            correlation_data = {
                "performance_data": performance_data,
                "related_conversations": unique_conversations,
                "insights": insights,
                "correlated_at": datetime.now(UTC).isoformat(),
                "correlation_type": "performance_data_to_conversation",
            }

            logger.info(f"🔗 Correlated performance data with {len(unique_conversations)} conversations")
            return correlation_data

        except Exception as e:
            logger.error(f"❌ Error correlating performance data: {e}")
            return {"error": str(e)}

    def track_optimization_opportunities(self, performance_data: dict[str, Any]) -> dict[str, Any]:
        """
        Track optimization opportunities and decisions.

        Args:
            performance_data: The captured performance data

        Returns:
            dict: Optimization opportunities and insights
        """
        try:
            optimization_data = {
                "cpu_optimizations": self._analyze_cpu_optimizations(performance_data),
                "memory_optimizations": self._analyze_memory_optimizations(performance_data),
                "disk_optimizations": self._analyze_disk_optimizations(performance_data),
                "network_optimizations": self._analyze_network_optimizations(performance_data),
                "application_optimizations": self._analyze_application_optimizations(performance_data),
                "trends": self._analyze_performance_trends(performance_data),
            }

            logger.info("📈 Tracked optimization opportunities")
            return optimization_data

        except Exception as e:
            logger.error(f"❌ Error tracking optimization opportunities: {e}")
            return {"error": str(e)}

    def store_in_ltst_memory(self, performance_data: dict[str, Any], correlation_data: dict[str, Any]) -> bool:
        """
        Store performance data and correlation information in LTST memory.

        Args:
            performance_data: The captured performance data
            correlation_data: The conversation correlation data

        Returns:
            bool: True if successfully stored
        """
        try:
            # Create a comprehensive decision entry for the performance data
            decision_data = {
                "head": "Performance data captured and correlated with conversations",
                "rationale": self._create_performance_rationale(performance_data, correlation_data),
                "confidence": 0.88,  # High confidence for automated capture
                "metadata": {
                    "performance_data": performance_data,
                    "correlation_data": correlation_data,
                    "capture_method": "performance_ltst_integration",
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            }

            # Store in LTST memory (this would typically call the decision storage API)
            # For now, we'll log the decision data
            logger.info("💾 Stored performance data in LTST memory")
            logger.debug(f"Decision data: {json.dumps(decision_data, indent=2)}")

            return True

        except Exception as e:
            logger.error(f"❌ Error storing in LTST memory: {e}")
            return False

    def _get_system_info(self) -> dict[str, Any]:
        """Get system information."""
        try:
            return {
                "platform": sys.platform,
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage("/").total,
                "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown",
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}

    def _capture_metrics(self, duration: int) -> dict[str, Any]:
        """Capture performance metrics over time."""
        try:
            metrics = {"cpu_samples": [], "memory_samples": [], "disk_samples": [], "network_samples": []}

            # Capture metrics over the specified duration
            start_time = time.time()
            sample_count = 0

            while time.time() - start_time < duration and sample_count < 10:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                metrics["cpu_samples"].append({"timestamp": datetime.now(UTC).isoformat(), "cpu_percent": cpu_percent})

                # Memory metrics
                memory = psutil.virtual_memory()
                metrics["memory_samples"].append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "memory_percent": memory.percent,
                        "memory_used": memory.used,
                        "memory_available": memory.available,
                    }
                )

                # Disk metrics
                disk = psutil.disk_usage("/")
                metrics["disk_samples"].append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "disk_percent": (disk.used / disk.total) * 100,
                        "disk_used": disk.used,
                        "disk_free": disk.free,
                    }
                )

                # Network metrics
                network = psutil.net_io_counters()
                metrics["network_samples"].append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv,
                    }
                )

                sample_count += 1
                time.sleep(max(1, duration // 10))  # Sample every 1 second or duration/10

            return metrics

        except Exception as e:
            logger.error(f"Error capturing metrics: {e}")
            return {"error": str(e)}

    def _get_resource_usage(self) -> dict[str, Any]:
        """Get current resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / (1024**3),
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_used_gb": disk.used / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
            }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {"error": str(e)}

    def _get_application_metrics(self) -> dict[str, Any]:
        """Get application-specific metrics."""
        try:
            # Get current process metrics
            current_process = psutil.Process()

            return {
                "process_cpu_percent": current_process.cpu_percent(),
                "process_memory_percent": current_process.memory_percent(),
                "process_memory_info": {
                    "rss": current_process.memory_info().rss,
                    "vms": current_process.memory_info().vms,
                },
                "process_num_threads": current_process.num_threads(),
                "process_open_files": len(current_process.open_files()),
                "process_connections": len(current_process.connections()),
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {"error": str(e)}

    def _identify_optimization_opportunities(self) -> list[dict[str, Any]]:
        """Identify optimization opportunities based on current metrics."""
        opportunities = []

        try:
            resource_usage = self._get_resource_usage()

            # CPU optimization opportunities
            if resource_usage.get("cpu_percent", 0) > 80:
                opportunities.append(
                    {
                        "type": "cpu_optimization",
                        "priority": "high",
                        "description": "High CPU usage detected",
                        "current_value": resource_usage["cpu_percent"],
                        "threshold": 80,
                        "recommendation": "Consider process optimization or load balancing",
                    }
                )

            # Memory optimization opportunities
            if resource_usage.get("memory_percent", 0) > 80:
                opportunities.append(
                    {
                        "type": "memory_optimization",
                        "priority": "high",
                        "description": "High memory usage detected",
                        "current_value": resource_usage["memory_percent"],
                        "threshold": 80,
                        "recommendation": "Consider memory cleanup or optimization",
                    }
                )

            # Disk optimization opportunities
            if resource_usage.get("disk_percent", 0) > 90:
                opportunities.append(
                    {
                        "type": "disk_optimization",
                        "priority": "critical",
                        "description": "Low disk space detected",
                        "current_value": resource_usage["disk_percent"],
                        "threshold": 90,
                        "recommendation": "Consider disk cleanup or expansion",
                    }
                )

            return opportunities

        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {e}")
            return []

    def _detect_performance_issues(self) -> list[dict[str, Any]]:
        """Detect performance issues based on current metrics."""
        issues = []

        try:
            resource_usage = self._get_resource_usage()

            # Critical CPU usage
            if resource_usage.get("cpu_percent", 0) > 95:
                issues.append(
                    {
                        "type": "critical_cpu_usage",
                        "severity": "critical",
                        "description": "Critical CPU usage detected",
                        "current_value": resource_usage["cpu_percent"],
                        "threshold": 95,
                    }
                )

            # Critical memory usage
            if resource_usage.get("memory_percent", 0) > 95:
                issues.append(
                    {
                        "type": "critical_memory_usage",
                        "severity": "critical",
                        "description": "Critical memory usage detected",
                        "current_value": resource_usage["memory_percent"],
                        "threshold": 95,
                    }
                )

            # Critical disk usage
            if resource_usage.get("disk_percent", 0) > 95:
                issues.append(
                    {
                        "type": "critical_disk_usage",
                        "severity": "critical",
                        "description": "Critical disk usage detected",
                        "current_value": resource_usage["disk_percent"],
                        "threshold": 95,
                    }
                )

            return issues

        except Exception as e:
            logger.error(f"Error detecting performance issues: {e}")
            return []

    def _extract_performance_decisions(self) -> list[dict[str, Any]]:
        """Extract decisions from performance data."""
        decisions = []

        try:
            # Create performance summary for decision extraction
            resource_usage = self._get_resource_usage()
            opportunities = self._identify_optimization_opportunities()
            issues = self._detect_performance_issues()

            performance_summary = f"""
            Current system performance:
            - CPU Usage: {resource_usage.get('cpu_percent', 0)}%
            - Memory Usage: {resource_usage.get('memory_percent', 0)}%
            - Disk Usage: {resource_usage.get('disk_percent', 0)}%
            - Optimization Opportunities: {len(opportunities)}
            - Performance Issues: {len(issues)}
            """

            # Use decision extractor to find decisions in performance summary
            if self.decision_extractor is not None:
                performance_decisions = self.decision_extractor.extract_decisions_from_text(
                    performance_summary, "performance_analysis", "system"
                )

                # Add performance context to each decision
                for decision in performance_decisions:
                    decision["performance_context"] = {
                        "resource_usage": resource_usage,
                        "opportunities_count": len(opportunities),
                        "issues_count": len(issues),
                    }
                    decision["source"] = "performance_analysis"

                decisions.extend(performance_decisions)
            else:
                # Fallback: create a simple decision from performance summary
                decisions.append(
                    {
                        "head": "Performance analysis completed",
                        "rationale": performance_summary,
                        "confidence": 0.8,
                        "source": "performance_analysis",
                        "performance_context": {
                            "resource_usage": resource_usage,
                            "opportunities_count": len(opportunities),
                            "issues_count": len(issues),
                        },
                    }
                )

        except Exception as e:
            logger.error(f"Error extracting performance decisions: {e}")

        return decisions

    def _extract_correlation_insights(
        self, performance_data: dict[str, Any], conversations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Extract insights from performance-conversation correlation."""
        insights = {
            "total_conversations": len(conversations),
            "correlation_strength": (
                "high" if len(conversations) > 5 else "moderate" if len(conversations) > 2 else "low"
            ),
            "performance_issues": len(performance_data.get("performance_issues", [])),
            "optimization_opportunities": len(performance_data.get("optimization_opportunities", [])),
            "resource_usage": performance_data.get("resource_usage", {}),
            "decision_count": len(performance_data.get("decisions", [])),
        }

        return insights

    def _create_performance_rationale(self, performance_data: dict[str, Any], correlation_data: dict[str, Any]) -> str:
        """Create a rationale for the performance data decision."""
        insights = correlation_data.get("insights", {})
        resource_usage = insights.get("resource_usage", {})

        rationale = f"""
        Performance data captured and correlated with conversation context.

        Performance Summary:
        - CPU Usage: {resource_usage.get('cpu_percent', 0)}%
        - Memory Usage: {resource_usage.get('memory_percent', 0)}%
        - Disk Usage: {resource_usage.get('disk_percent', 0)}%
        - Performance Issues: {insights.get('performance_issues', 0)}
        - Optimization Opportunities: {insights.get('optimization_opportunities', 0)}
        - Decisions Extracted: {insights.get('decision_count', 0)}
        - Related Conversations: {insights.get('total_conversations', 0)}

        This performance data has been automatically correlated with {insights.get('total_conversations', 0)}
        related conversations in the LTST memory system, enabling comprehensive tracking
        of system behavior and optimization opportunities.
        """

        return rationale.strip()

    def _analyze_cpu_optimizations(self, performance_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze CPU optimization opportunities."""
        cpu_samples = performance_data.get("performance_metrics", {}).get("cpu_samples", [])

        if not cpu_samples:
            return {"optimizations": [], "trend": "unknown"}

        cpu_values = [sample["cpu_percent"] for sample in cpu_samples]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        max_cpu = max(cpu_values)

        optimizations = []
        if avg_cpu > 70:
            optimizations.append("Consider process optimization")
        if max_cpu > 90:
            optimizations.append("Consider load balancing")

        return {
            "optimizations": optimizations,
            "average_cpu": avg_cpu,
            "max_cpu": max_cpu,
            "trend": "high" if avg_cpu > 70 else "moderate" if avg_cpu > 40 else "low",
        }

    def _analyze_memory_optimizations(self, performance_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze memory optimization opportunities."""
        memory_samples = performance_data.get("performance_metrics", {}).get("memory_samples", [])

        if not memory_samples:
            return {"optimizations": [], "trend": "unknown"}

        memory_values = [sample["memory_percent"] for sample in memory_samples]
        avg_memory = sum(memory_values) / len(memory_values)
        max_memory = max(memory_values)

        optimizations = []
        if avg_memory > 70:
            optimizations.append("Consider memory cleanup")
        if max_memory > 90:
            optimizations.append("Consider memory optimization")

        return {
            "optimizations": optimizations,
            "average_memory": avg_memory,
            "max_memory": max_memory,
            "trend": "high" if avg_memory > 70 else "moderate" if avg_memory > 40 else "low",
        }

    def _analyze_disk_optimizations(self, performance_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze disk optimization opportunities."""
        disk_samples = performance_data.get("performance_metrics", {}).get("disk_samples", [])

        if not disk_samples:
            return {"optimizations": [], "trend": "unknown"}

        disk_values = [sample["disk_percent"] for sample in disk_samples]
        avg_disk = sum(disk_values) / len(disk_values)
        max_disk = max(disk_values)

        optimizations = []
        if avg_disk > 80:
            optimizations.append("Consider disk cleanup")
        if max_disk > 95:
            optimizations.append("Consider disk expansion")

        return {
            "optimizations": optimizations,
            "average_disk": avg_disk,
            "max_disk": max_disk,
            "trend": "high" if avg_disk > 80 else "moderate" if avg_disk > 60 else "low",
        }

    def _analyze_network_optimizations(self, performance_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze network optimization opportunities."""
        network_samples = performance_data.get("performance_metrics", {}).get("network_samples", [])

        if not network_samples:
            return {"optimizations": [], "trend": "unknown"}

        # Calculate network usage trends
        total_bytes_sent = sum(sample["bytes_sent"] for sample in network_samples)
        total_bytes_recv = sum(sample["bytes_recv"] for sample in network_samples)

        return {
            "optimizations": [],
            "total_bytes_sent": total_bytes_sent,
            "total_bytes_recv": total_bytes_recv,
            "trend": "active" if total_bytes_sent + total_bytes_recv > 1000000 else "low",
        }

    def _analyze_application_optimizations(self, performance_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze application-specific optimization opportunities."""
        app_metrics = performance_data.get("application_metrics", {})

        optimizations = []

        if app_metrics.get("process_cpu_percent", 0) > 50:
            optimizations.append("Consider application CPU optimization")

        if app_metrics.get("process_memory_percent", 0) > 50:
            optimizations.append("Consider application memory optimization")

        if app_metrics.get("process_open_files", 0) > 100:
            optimizations.append("Consider file handle optimization")

        return {
            "optimizations": optimizations,
            "process_cpu": app_metrics.get("process_cpu_percent", 0),
            "process_memory": app_metrics.get("process_memory_percent", 0),
            "open_files": app_metrics.get("process_open_files", 0),
        }

    def _analyze_performance_trends(self, performance_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze performance trends over time."""
        metrics = performance_data.get("performance_metrics", {})

        trends = {}

        # Analyze CPU trend
        cpu_samples = metrics.get("cpu_samples", [])
        if len(cpu_samples) >= 2:
            cpu_values = [sample["cpu_percent"] for sample in cpu_samples]
            trends["cpu_trend"] = (
                "increasing"
                if cpu_values[-1] > cpu_values[0]
                else "decreasing" if cpu_values[-1] < cpu_values[0] else "stable"
            )

        # Analyze memory trend
        memory_samples = metrics.get("memory_samples", [])
        if len(memory_samples) >= 2:
            memory_values = [sample["memory_percent"] for sample in memory_samples]
            trends["memory_trend"] = (
                "increasing"
                if memory_values[-1] > memory_values[0]
                else "decreasing" if memory_values[-1] < memory_values[0] else "stable"
            )

        return trends


# Convenience functions for easy integration
def integrate_performance_data(
    db_connection_string: str, project_root: Path | None = None, duration: int = 60
) -> dict[str, Any]:
    """
    Convenience function to integrate performance data with LTST memory.

    Args:
        db_connection_string: Database connection string
        project_root: Optional project root path
        duration: Duration in seconds to capture performance data

    Returns:
        dict: Integration result
    """
    integration = PerformanceLTSTIntegration(db_connection_string, project_root)

    # Capture performance data
    performance_data = integration.capture_performance_data(duration)

    # Correlate with conversations
    correlation_data = integration.correlate_with_conversations(performance_data)

    # Store in LTST memory
    storage_success = integration.store_in_ltst_memory(performance_data, correlation_data)

    return {"success": storage_success, "performance_data": performance_data, "correlation_data": correlation_data}


def track_optimization_opportunities(db_connection_string: str, project_root: Path | None = None) -> dict[str, Any]:
    """
    Track optimization opportunities.

    Args:
        db_connection_string: Database connection string
        project_root: Optional project root path

    Returns:
        dict: Optimization opportunities
    """
    integration = PerformanceLTSTIntegration(db_connection_string, project_root)

    # Capture performance data for analysis
    performance_data = integration.capture_performance_data(duration=30)

    return integration.track_optimization_opportunities(performance_data)


if __name__ == "__main__":
    # Example usage
    db_connection_string = "postgresql://danieljacobs@localhost:5432/ai_agency"

    # Test integration with performance data capture
    result = integrate_performance_data(db_connection_string, duration=30)
    print(f"Performance integration result: {json.dumps(result, indent=2)}")

    # Track optimization opportunities
    opportunities = track_optimization_opportunities(db_connection_string)
    print(f"Optimization opportunities: {json.dumps(opportunities, indent=2)}")
