#!/usr/bin/env python3
"""
Production Monitoring Demo

Demonstrates the production monitoring system with security alerts,
health checks, and system metrics collection.
"""

import sys
import time

# Add src to path
sys.path.append('src')

from monitoring.health_endpoints import HealthEndpointManager, initialize_health_endpoints
from monitoring.production_monitor import ProductionMonitor, initialize_production_monitoring


def demo_security_events():
    """Demonstrate security event recording"""
    print("🔐 Security Events Demo")
    print("=" * 50)
    
    monitor = ProductionMonitor(
        service_name="demo-service",
        service_version="0.1.0",
        environment="demo"
    )
    
    # Record some security events
    events = [
        ("file_upload", "low", "user_upload", "User uploaded document.pdf"),
        ("authentication", "medium", "auth_system", "Failed login attempt from 192.168.1.100"),
        ("system_alert", "high", "system_monitor", "CPU usage exceeded 90%"),
        ("security_scan", "critical", "security_scanner", "Critical vulnerability detected in dependency")
    ]
    
    for event_type, severity, source, description in events:
        monitor._record_security_event(event_type, severity, source, description)
        print(f"📝 Recorded {severity.upper()} event: {event_type} - {description}")
        time.sleep(0.5)
    
    # Get recent events
    recent_events = monitor.get_security_events(hours=1)
    print(f"\n📊 Recent security events: {len(recent_events)}")
    for event in recent_events:
        print(f"  • {event['severity'].upper()}: {event['event_type']} - {event['description']}")
    
    print()

def demo_health_checks():
    """Demonstrate health check functionality"""
    print("🏥 Health Checks Demo")
    print("=" * 50)
    
    health_manager = HealthEndpointManager()
    
    # Run health checks
    print("Running health checks...")
    dependency_results = health_manager.run_dependency_checks()
    
    for name, result in dependency_results.items():
        status_emoji = "✅" if result.status == "healthy" else "⚠️" if result.status == "degraded" else "❌"
        print(f"  {status_emoji} {name}: {result.status} ({result.response_time:.3f}s)")
    
    # Get overall health status
    health_status = health_manager.get_health_status()
    print(f"\n📊 Overall Health Status: {health_status['status'].upper()}")
    print(f"  • Unhealthy dependencies: {health_status['unhealthy_dependencies']}")
    print(f"  • Degraded dependencies: {health_status['degraded_dependencies']}")
    print(f"  • Total dependencies: {health_status['total_dependencies']}")
    
    # Get readiness status
    ready_status = health_manager.get_ready_status()
    ready_emoji = "✅" if ready_status["ready"] else "❌"
    print(f"\n🚀 Kubernetes Ready: {ready_emoji} {ready_status['ready']}")
    
    print()

def demo_system_metrics():
    """Demonstrate system metrics collection"""
    print("📊 System Metrics Demo")
    print("=" * 50)
    
    monitor = ProductionMonitor(
        service_name="demo-service",
        service_version="0.1.0",
        environment="demo"
    )
    
    # Collect metrics for a few cycles
    print("Collecting system metrics...")
    for i in range(3):
        monitor._collect_system_metrics()
        print(f"  Cycle {i+1}: Collected system metrics")
        time.sleep(1)
    
    # Get recent metrics
    recent_metrics = monitor.get_system_metrics(minutes=5)
    print(f"\n📈 Recent system metrics: {len(recent_metrics)}")
    
    if recent_metrics:
        latest = recent_metrics[-1]
        print(f"  • CPU Usage: {latest['cpu_percent']:.1f}%")
        print(f"  • Memory Usage: {latest['memory_percent']:.1f}%")
        print(f"  • Disk Usage: {latest['disk_usage_percent']:.1f}%")
        print(f"  • Active Connections: {latest['active_connections']}")
    
    print()

def demo_monitoring_integration():
    """Demonstrate full monitoring integration"""
    print("🔗 Full Monitoring Integration Demo")
    print("=" * 50)
    
    # Initialize production monitoring
    monitor = initialize_production_monitoring(
        service_name="demo-service",
        service_version="0.1.0",
        environment="demo"
    )
    
    # Initialize health endpoints
    health_manager = initialize_health_endpoints(monitor)
    
    # Start monitoring
    print("Starting production monitoring...")
    monitor.start_monitoring(interval_seconds=5)
    
    # Let it run for a few cycles
    print("Monitoring for 15 seconds...")
    time.sleep(15)
    
    # Stop monitoring
    monitor.stop_monitoring()
    print("Monitoring stopped.")
    
    # Get comprehensive status
    print("\n📊 Comprehensive Status Report")
    print("-" * 30)
    
    health_status = health_manager.get_health_status()
    security_events = monitor.get_security_events(hours=1)
    system_metrics = monitor.get_system_metrics(minutes=5)
    
    print(f"Overall Status: {health_status['status'].upper()}")
    print(f"Security Events: {len(security_events)}")
    print(f"System Metrics: {len(system_metrics)}")
    
    if security_events:
        print("\nRecent Security Events:")
        for event in security_events[-3:]:  # Last 3 events
            print(f"  • {event['severity'].upper()}: {event['event_type']}")
    
    if system_metrics:
        latest_metrics = system_metrics[-1]
        print("\nLatest System Metrics:")
        print(f"  • CPU: {latest_metrics['cpu_percent']:.1f}%")
        print(f"  • Memory: {latest_metrics['memory_percent']:.1f}%")
        print(f"  • Disk: {latest_metrics['disk_usage_percent']:.1f}%")
    
    print()

def demo_alert_callbacks():
    """Demonstrate alert callback functionality"""
    print("🚨 Alert Callbacks Demo")
    print("=" * 50)
    
    alert_events = []
    
    def alert_callback(event):
        alert_events.append(event)
        print(f"🚨 ALERT: {event.severity.upper()} - {event.event_type}: {event.description}")
    
    monitor = ProductionMonitor(
        service_name="demo-service",
        service_version="0.1.0",
        environment="demo"
    )
    
    # Register alert callback
    monitor.register_alert_callback(alert_callback)
    
    # Trigger some events
    events = [
        ("high_cpu", "high", "system", "CPU usage at 95%"),
        ("memory_warning", "medium", "system", "Memory usage at 85%"),
        ("security_breach", "critical", "security", "Unauthorized access attempt"),
    ]
    
    for event_type, severity, source, description in events:
        monitor._record_security_event(event_type, severity, source, description)
        time.sleep(0.5)
    
    print(f"\n📊 Total alerts triggered: {len(alert_events)}")
    print()

def main():
    """Run all demos"""
    print("🎯 Production Monitoring System Demo")
    print("=" * 60)
    print()
    
    try:
        demo_security_events()
        demo_health_checks()
        demo_system_metrics()
        demo_alert_callbacks()
        demo_monitoring_integration()
        
        print("✅ All demos completed successfully!")
        print("\n🎉 Production monitoring system is ready for deployment!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 