#!/usr/bin/env python3
"""
Production Monitoring System

Provides comprehensive monitoring, security alerts, and health checks
for production deployment of the DSPy RAG system.
"""

import logging
import os
import sys
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import psutil

# OpenTelemetry imports

# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.enhanced_file_validator import EnhancedFileValidator
from utils.logger import get_logger
from utils.opentelemetry_config import OpenTelemetryConfig, add_span_attribute, trace_operation
from utils.security import SecurityScanner

logger = get_logger("production_monitor")


@dataclass
class SecurityEvent:
    """Security event data structure"""

    timestamp: datetime
    event_type: str
    severity: str  # low, medium, high, critical
    source: str
    description: str
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class HealthCheck:
    """Health check result"""

    name: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """System performance metrics"""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    active_connections: int
    queue_depth: int


class ProductionMonitor:
    """Production monitoring system with security alerts and health checks"""

    def __init__(
        self,
        service_name: str = "ai-dev-tasks",
        service_version: str = "0.3.1",
        environment: str = "production",
        otlp_endpoint: Optional[str] = None,
    ):
        """
        Initialize the production monitor.

        Args:
            service_name: Name of the service
            service_version: Version of the service
            environment: Environment (development, staging, production)
            otlp_endpoint: OTLP endpoint for telemetry export
        """
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.otlp_endpoint = otlp_endpoint

        # Initialize components
        self.security_scanner = SecurityScanner()
        self.file_validator = EnhancedFileValidator()
        self.ot_config = OpenTelemetryConfig()

        # Event storage
        self.security_events: deque = deque(maxlen=1000)
        self.health_checks: Dict[str, HealthCheck] = {}
        self.system_metrics: deque = deque(maxlen=100)

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_callbacks: List[Callable] = []

        # Initialize OpenTelemetry
        self._initialize_telemetry()

        # Register health checks
        self._register_default_health_checks()

    def _initialize_telemetry(self) -> None:
        """Initialize OpenTelemetry with production configuration"""
        try:
            self.ot_config.initialize(
                service_name=self.service_name,
                service_version=self.service_version,
                environment=self.environment,
                otlp_endpoint=self.otlp_endpoint,
                enable_console_exporter=self.environment != "production",
                enable_requests_instrumentation=True,
                enable_flask_instrumentation=True,
                enable_logging_instrumentation=True,
            )
            logger.info("OpenTelemetry initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}")

    def _register_default_health_checks(self) -> None:
        """Register default health checks"""
        self.register_health_check("system", self._check_system_health)
        self.register_health_check("database", self._check_database_health)
        self.register_health_check("security", self._check_security_health)
        self.register_health_check("file_validation", self._check_file_validation_health)

    def register_health_check(self, name: str, check_func: Callable[[], HealthCheck]) -> None:
        """Register a health check function"""
        self.health_checks[name] = HealthCheck(
            name=name, status="unknown", response_time=0.0, last_check=datetime.now()
        )
        setattr(self, f"_check_{name}_health", check_func)

    def register_alert_callback(self, callback: Callable[[SecurityEvent], None]) -> None:
        """Register a callback for security alerts"""
        self.alert_callbacks.append(callback)

    def start_monitoring(self, interval_seconds: int = 30) -> None:
        """Start the monitoring system"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(interval_seconds,), daemon=True)
        self.monitoring_thread.start()
        logger.info(f"Production monitoring started (interval: {interval_seconds}s)")

    def stop_monitoring(self) -> None:
        """Stop the monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Production monitoring stopped")

    def _monitoring_loop(self, interval_seconds: int) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                with trace_operation("production_monitoring_cycle"):
                    # Collect system metrics
                    self._collect_system_metrics()

                    # Run health checks
                    self._run_health_checks()

                    # Security monitoring
                    self._security_monitoring_cycle()

                    # Check for alerts
                    self._check_alerts()

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self._record_security_event(
                    "monitoring_error", "high", "production_monitor", f"Monitoring loop error: {e}"
                )

            time.sleep(interval_seconds)

    def _collect_system_metrics(self) -> None:
        """Collect system performance metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage("/")

            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            }

            # Active connections (approximate)
            active_connections = len(psutil.net_connections())

            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io=network_io,
                active_connections=active_connections,
                queue_depth=0,  # TODO: Implement queue monitoring
            )

            self.system_metrics.append(metrics)

            # Add OpenTelemetry attributes
            add_span_attribute("system.cpu_percent", cpu_percent)
            add_span_attribute("system.memory_percent", memory.percent)
            add_span_attribute("system.disk_percent", disk.percent)
            add_span_attribute("system.active_connections", active_connections)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def _run_health_checks(self) -> None:
        """Run all registered health checks"""
        for name, health_check in self.health_checks.items():
            try:
                check_func = getattr(self, f"_check_{name}_health")
                start_time = time.time()

                result = check_func()
                response_time = time.time() - start_time

                # Update health check result
                health_check.status = result.status
                health_check.response_time = response_time
                health_check.last_check = datetime.now()
                health_check.error_message = result.error_message
                health_check.metadata = result.metadata

                # Log health check result
                if result.status != "healthy":
                    logger.warning(f"Health check '{name}' status: {result.status}")

            except Exception as e:
                logger.error(f"Error running health check '{name}': {e}")
                health_check.status = "unhealthy"
                health_check.error_message = str(e)
                health_check.last_check = datetime.now()

    def _check_system_health(self) -> HealthCheck:
        """Check system health (CPU, memory, disk)"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Determine status based on thresholds
            status = "healthy"
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = "degraded"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = "unhealthy"

            return HealthCheck(
                name="system",
                status=status,
                response_time=0.0,
                last_check=datetime.now(),
                metadata={"cpu_percent": cpu_percent, "memory_percent": memory.percent, "disk_percent": disk.percent},
            )
        except Exception as e:
            return HealthCheck(
                name="system", status="unhealthy", response_time=0.0, last_check=datetime.now(), error_message=str(e)
            )

    def _check_database_health(self) -> HealthCheck:
        """Check database connectivity"""
        try:
            # TODO: Implement actual database health check
            # For now, return healthy status
            return HealthCheck(name="database", status="healthy", response_time=0.0, last_check=datetime.now())
        except Exception as e:
            return HealthCheck(
                name="database", status="unhealthy", response_time=0.0, last_check=datetime.now(), error_message=str(e)
            )

    # Removed legacy local model health check; Cursor native AI requires no local HTTP service

    def _check_security_health(self) -> HealthCheck:
        """Check security system health"""
        try:
            # Run security scan
            security_report = self.security_scanner.generate_security_report()

            # Determine status based on vulnerabilities
            vulnerabilities = security_report.get("vulnerabilities", [])
            critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
            high_vulns = [v for v in vulnerabilities if v.get("severity") == "high"]

            status = "healthy"
            if critical_vulns:
                status = "unhealthy"
            elif high_vulns:
                status = "degraded"

            return HealthCheck(
                name="security",
                status=status,
                response_time=0.0,
                last_check=datetime.now(),
                metadata={
                    "total_vulnerabilities": len(vulnerabilities),
                    "critical_vulnerabilities": len(critical_vulns),
                    "high_vulnerabilities": len(high_vulns),
                },
            )
        except Exception as e:
            return HealthCheck(
                name="security", status="unhealthy", response_time=0.0, last_check=datetime.now(), error_message=str(e)
            )

    def _check_file_validation_health(self) -> HealthCheck:
        """Check file validation system health"""
        try:
            # Check quarantine status
            quarantine_status = self.file_validator.get_quarantine_status()

            quarantined_files = quarantine_status.get("quarantined_files", [])

            status = "healthy"
            if len(quarantined_files) > 10:  # Threshold for quarantined files
                status = "degraded"

            return HealthCheck(
                name="file_validation",
                status=status,
                response_time=0.0,
                last_check=datetime.now(),
                metadata={
                    "quarantined_files": len(quarantined_files),
                    "quarantine_directory": quarantine_status.get("quarantine_directory"),
                },
            )
        except Exception as e:
            return HealthCheck(
                name="file_validation",
                status="unhealthy",
                response_time=0.0,
                last_check=datetime.now(),
                error_message=str(e),
            )

    def _security_monitoring_cycle(self) -> None:
        """Run security monitoring checks"""
        try:
            # Check for recent security events
            recent_events = [
                event for event in self.security_events if event.timestamp > datetime.now() - timedelta(minutes=5)
            ]

            # Check for critical events
            critical_events = [event for event in recent_events if event.severity in ["high", "critical"]]

            if critical_events:
                logger.warning(f"Found {len(critical_events)} critical security events")

        except Exception as e:
            logger.error(f"Error in security monitoring cycle: {e}")

    def _check_alerts(self) -> None:
        """Check for conditions that require alerts"""
        try:
            # Check system metrics for alerts
            if self.system_metrics:
                latest_metrics = self.system_metrics[-1]

                # CPU alert
                if latest_metrics.cpu_percent > 90:
                    self._record_security_event(
                        "high_cpu_usage", "medium", "system_monitor", f"CPU usage is {latest_metrics.cpu_percent}%"
                    )

                # Memory alert
                if latest_metrics.memory_percent > 90:
                    self._record_security_event(
                        "high_memory_usage",
                        "medium",
                        "system_monitor",
                        f"Memory usage is {latest_metrics.memory_percent}%",
                    )

                # Disk alert
                if latest_metrics.disk_usage_percent > 90:
                    self._record_security_event(
                        "high_disk_usage",
                        "medium",
                        "system_monitor",
                        f"Disk usage is {latest_metrics.disk_usage_percent}%",
                    )

            # Check health checks for alerts
            for name, health_check in self.health_checks.items():
                if health_check.status == "unhealthy":
                    self._record_security_event(
                        "health_check_failed",
                        "high",
                        "health_monitor",
                        f"Health check '{name}' is unhealthy: {health_check.error_message}",
                    )

        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    def _record_security_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        description: str,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a security event"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            source=source,
            description=description,
            correlation_id=correlation_id,
            metadata=metadata,
        )

        self.security_events.append(event)

        # Log the event
        log_level = logging.ERROR if severity in ["high", "critical"] else logging.WARNING
        logger.log(log_level, f"Security event: {event_type} - {description}")

        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        health_checks = {name: asdict(check) for name, check in self.health_checks.items()}

        # Determine overall status
        unhealthy_count = sum(1 for check in self.health_checks.values() if check.status == "unhealthy")
        degraded_count = sum(1 for check in self.health_checks.values() if check.status == "degraded")

        if unhealthy_count > 0:
            overall_status = "unhealthy"
        elif degraded_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "health_checks": health_checks,
            "unhealthy_count": unhealthy_count,
            "degraded_count": degraded_count,
        }

    def get_security_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get security events from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [event for event in self.security_events if event.timestamp > cutoff_time]

        return [asdict(event) for event in recent_events]

    def get_system_metrics(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get system metrics from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [metrics for metrics in self.system_metrics if metrics.timestamp > cutoff_time]

        return [asdict(metrics) for metrics in recent_metrics]

    def shutdown(self) -> None:
        """Shutdown the production monitor"""
        self.stop_monitoring()
        self.ot_config.shutdown()
        logger.info("Production monitor shutdown complete")


# Global instance
_production_monitor: Optional[ProductionMonitor] = None


def get_production_monitor() -> ProductionMonitor:
    """Get the global production monitor instance"""
    global _production_monitor
    if _production_monitor is None:
        _production_monitor = ProductionMonitor()
    return _production_monitor


def initialize_production_monitoring(
    service_name: str = "ai-dev-tasks",
    service_version: str = "0.3.1",
    environment: str = "production",
    otlp_endpoint: Optional[str] = None,
) -> ProductionMonitor:
    """Initialize production monitoring"""
    global _production_monitor
    _production_monitor = ProductionMonitor(
        service_name=service_name, service_version=service_version, environment=environment, otlp_endpoint=otlp_endpoint
    )
    return _production_monitor
