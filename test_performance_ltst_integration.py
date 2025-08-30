#!/usr/bin/env python3
"""
Test Script for Performance-LTST Integration (Task 10)

This script tests the integration between performance metrics and LTST memory system.
"""

import sys
from pathlib import Path

# Add the dspy-rag-system utils to the path
sys.path.insert(0, str(Path(__file__).parent / "dspy-rag-system" / "src" / "utils"))

from performance_ltst_integration import (
    PerformanceLTSTIntegration,
    integrate_performance_data,
    track_optimization_opportunities,
)


def test_performance_ltst_integration():
    """Test the complete Performance-LTST integration workflow."""

    print("🧪 Testing Performance-LTST Integration (Task 10)")
    print("=" * 50)

    # Database connection string
    db_connection_string = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("\n📊 Testing performance data integration")
    print("-" * 40)

    # Test 1: Complete integration workflow
    print("1. Testing complete integration workflow...")
    result = integrate_performance_data(db_connection_string, duration=30)

    if result["success"]:
        print("✅ Integration workflow completed successfully")

        # Display key metrics
        performance_data = result["performance_data"]
        correlation_data = result["correlation_data"]

        resource_usage = performance_data.get("resource_usage", {})
        insights = correlation_data.get("insights", {})

        print(f"   💻 CPU Usage: {resource_usage.get('cpu_percent', 0)}%")
        print(f"   🧠 Memory Usage: {resource_usage.get('memory_percent', 0)}%")
        print(f"   💾 Disk Usage: {resource_usage.get('disk_percent', 0)}%")
        print(f"   ⚠️ Performance Issues: {insights.get('performance_issues', 0)}")
        print(f"   🎯 Optimization Opportunities: {insights.get('optimization_opportunities', 0)}")
        print(f"   🔗 Related Conversations: {insights.get('total_conversations', 0)}")

    else:
        print("❌ Integration workflow failed")
        return False

    # Test 2: Optimization opportunity tracking
    print("\n2. Testing optimization opportunity tracking...")
    opportunities = track_optimization_opportunities(db_connection_string)

    if opportunities and not opportunities.get("error"):
        print("✅ Optimization opportunity tracking successful")

        cpu_opt = opportunities.get("cpu_optimizations", {})
        memory_opt = opportunities.get("memory_optimizations", {})
        disk_opt = opportunities.get("disk_optimizations", {})
        app_opt = opportunities.get("application_optimizations", {})
        trends = opportunities.get("trends", {})

        print(f"   📈 CPU Trend: {cpu_opt.get('trend', 'Unknown')} (avg: {cpu_opt.get('average_cpu', 0):.1f}%)")
        print(
            f"   🧠 Memory Trend: {memory_opt.get('trend', 'Unknown')} (avg: {memory_opt.get('average_memory', 0):.1f}%)"
        )
        print(f"   💾 Disk Trend: {disk_opt.get('trend', 'Unknown')} (avg: {disk_opt.get('average_disk', 0):.1f}%)")
        print(f"   🎯 App CPU: {app_opt.get('process_cpu', 0):.1f}%")
        print(f"   📁 Open Files: {app_opt.get('open_files', 0)}")
        print(f"   📊 CPU Trend: {trends.get('cpu_trend', 'Unknown')}")
        print(f"   📊 Memory Trend: {trends.get('memory_trend', 'Unknown')}")

    else:
        print("❌ Optimization opportunity tracking failed")
        return False

    # Test 3: Direct integration class usage
    print("\n3. Testing direct integration class...")
    integration = PerformanceLTSTIntegration(db_connection_string)

    # Test performance data capture
    performance_data = integration.capture_performance_data(duration=15)
    if performance_data and not performance_data.get("error"):
        print("✅ Performance data capture successful")

        # Test correlation
        correlation_data = integration.correlate_with_conversations(performance_data)
        if correlation_data and not correlation_data.get("error"):
            print("✅ Conversation correlation successful")

            # Test storage
            storage_success = integration.store_in_ltst_memory(performance_data, correlation_data)
            if storage_success:
                print("✅ LTST memory storage successful")
            else:
                print("❌ LTST memory storage failed")
                return False
        else:
            print("❌ Conversation correlation failed")
            return False
    else:
        print("❌ Performance data capture failed")
        return False

    # Test 4: Quality gates verification
    print("\n4. Verifying quality gates...")

    # Quality Gate 1: Metrics Capture
    metrics_capture_ok = (
        performance_data.get("performance_metrics") is not None
        and performance_data.get("resource_usage") is not None
        and performance_data.get("application_metrics") is not None
        and len(performance_data.get("performance_metrics", {}).get("cpu_samples", [])) > 0
    )
    print(f"   📊 Metrics Capture: {'✅ PASS' if metrics_capture_ok else '❌ FAIL'}")

    # Quality Gate 2: Behavior Correlation
    behavior_correlation_ok = (
        correlation_data.get("correlation_type") == "performance_data_to_conversation"
        and correlation_data.get("insights") is not None
    )
    print(f"   🔗 Behavior Correlation: {'✅ PASS' if behavior_correlation_ok else '❌ FAIL'}")

    # Quality Gate 3: Optimization Tracking
    optimization_tracking_ok = (
        opportunities.get("cpu_optimizations") is not None
        and opportunities.get("memory_optimizations") is not None
        and opportunities.get("application_optimizations") is not None
    )
    print(f"   📈 Optimization Tracking: {'✅ PASS' if optimization_tracking_ok else '❌ FAIL'}")

    all_gates_passed = metrics_capture_ok and behavior_correlation_ok and optimization_tracking_ok

    print(f"\n🎯 Quality Gates Summary: {'✅ ALL PASSED' if all_gates_passed else '❌ SOME FAILED'}")

    # Test 5: System information
    print("\n5. Testing system information capture...")
    system_info = performance_data.get("system_info", {})
    if system_info and not system_info.get("error"):
        print("✅ System information captured")
        print(f"   💻 Platform: {system_info.get('platform', 'Unknown')}")
        print(f"   🐍 Python Version: {system_info.get('python_version', 'Unknown').split()[0]}")
        print(f"   🔢 CPU Count: {system_info.get('cpu_count', 'Unknown')}")
        print(f"   🧠 Memory Total: {system_info.get('memory_total', 0) / (1024**3):.1f} GB")
        print(f"   💾 Disk Total: {system_info.get('disk_total', 0) / (1024**3):.1f} GB")
    else:
        print("❌ System information capture failed")

    # Test 6: Performance issues detection
    print("\n6. Testing performance issues detection...")
    performance_issues = performance_data.get("performance_issues", [])
    optimization_opportunities = performance_data.get("optimization_opportunities", [])

    if performance_issues:
        print(f"⚠️ Detected {len(performance_issues)} performance issues:")
        for issue in performance_issues:
            print(f"   - {issue.get('description', 'Unknown')} (severity: {issue.get('severity', 'Unknown')})")
    else:
        print("✅ No critical performance issues detected")

    if optimization_opportunities:
        print(f"🎯 Found {len(optimization_opportunities)} optimization opportunities:")
        for opp in optimization_opportunities:
            print(f"   - {opp.get('description', 'Unknown')} (priority: {opp.get('priority', 'Unknown')})")
    else:
        print("✅ No optimization opportunities identified (system running optimally)")

    print("\n" + "=" * 50)
    print("🧪 Performance-LTST Integration Test Complete")

    if all_gates_passed:
        print("✅ Task 10: Performance Data Integration → LTST Memory - COMPLETED")
        return True
    else:
        print("❌ Task 10: Some quality gates failed")
        return False


if __name__ == "__main__":
    success = test_performance_ltst_integration()
    sys.exit(0 if success else 1)
