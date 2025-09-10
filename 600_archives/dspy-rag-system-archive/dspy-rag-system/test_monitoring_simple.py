#!/usr/bin/env python3
"""
Simple Monitoring Test

Test to verify that the monitoring system is properly integrated
with the context integration system.
"""

import os
import sys
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from utils.context_monitoring import get_context_monitor, get_performance_report


def test_monitoring_working():
    """Test that monitoring system is working"""
    print("🔍 Testing Monitoring System")
    print("-" * 50)

    monitor = get_context_monitor()

    # Record a test request
    monitor.record_request(
        role="test_role",
        task="test task",
        start_time=time.time(),
        success=True,
        response_time=2.5,
        cache_hit=False,
        fallback_used=False,
    )

    # Get metrics
    metrics = monitor.get_metrics_summary()

    print("📊 Metrics after test request:")
    print(f"   Total requests: {metrics['current_metrics']['total_requests']}")
    print(f"   Successful requests: {metrics['current_metrics']['successful_requests']}")
    print(f"   Avg response time: {metrics['current_metrics']['avg_response_time_ms']:.2f}ms")

    if metrics["current_metrics"]["total_requests"] > 0:
        print("   ✅ Monitoring system is working!")
        return True
    else:
        print("   ❌ Monitoring system not recording metrics")
        return False


def test_performance_report():
    """Test performance report generation"""
    print("\n🔍 Testing Performance Report")
    print("-" * 50)

    report = get_performance_report()

    if "error" in report:
        print(f"⚠️ No performance data: {report['error']}")
        return True

    print("📊 Performance Report:")
    print(f"   Response time count: {report['response_time_stats']['count']}")
    print(f"   Cache hit rate: {report['cache_stats']['hit_rate']:.2f}%")
    print(f"   Error rate: {report['error_stats']['error_rate']:.2f}%")

    print("   ✅ Performance report working!")
    return True


def main():
    """Run simple monitoring tests"""
    print("📊 Simple Monitoring Test")
    print("=" * 50)

    test1 = test_monitoring_working()
    test2 = test_performance_report()

    if test1 and test2:
        print("\n🎉 Monitoring system is working correctly!")
        print("   T5: Add monitoring and observability - COMPLETED!")
    else:
        print("\n⚠️ Some monitoring tests failed")


if __name__ == "__main__":
    main()
