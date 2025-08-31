#!/usr/bin/env python3
"""
RAGChecker Evaluation with Integrated Cost Monitoring
Combines RAGChecker evaluation with real-time cost tracking and budget alerts
"""

import os
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bedrock_cost_monitor import BedrockCostMonitor
from ragchecker_official_evaluation import main as run_ragchecker_evaluation


def run_evaluation_with_monitoring():
    """Run RAGChecker evaluation with integrated cost monitoring."""
    print("🧠 RAGChecker Evaluation with Cost Monitoring")
    print("=" * 60)

    # Initialize cost monitor
    monitor = BedrockCostMonitor()

    # Check budget status before evaluation
    print("\n💰 Pre-Evaluation Budget Check:")
    alerts = monitor.check_budget_alerts()

    if alerts:
        print("⚠️  Budget alerts detected:")
        for alert in alerts:
            print(f"   {alert['message']}")

        # Ask user if they want to continue
        if alert["severity"] == "high":
            response = input("\n❓ High budget alert detected. Continue anyway? (y/N): ").strip().lower()
            if response != "y":
                print("🛑 Evaluation cancelled due to budget constraints")
                return 1
    else:
        print("✅ Budget status: OK")

    # Show current usage
    monitor.print_cost_summary("today")

    # Record start time and usage
    start_time = time.time()
    pre_eval_summary = monitor.get_usage_summary("today")

    print("\n🚀 Starting RAGChecker evaluation...")
    print(f"⏰ Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Run the actual evaluation
    try:
        result = run_ragchecker_evaluation()
        evaluation_success = result is not None
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        evaluation_success = False
        result = None

    # Record end time and calculate duration
    end_time = time.time()
    duration = end_time - start_time

    print(f"\n⏰ Evaluation completed in {duration:.1f} seconds")

    # Post-evaluation cost analysis
    print("\n💰 Post-Evaluation Cost Analysis:")
    post_eval_summary = monitor.get_usage_summary("today")

    # Calculate evaluation-specific costs
    eval_requests = post_eval_summary.total_requests - pre_eval_summary.total_requests
    eval_cost = post_eval_summary.total_cost - pre_eval_summary.total_cost
    eval_tokens = (post_eval_summary.total_input_tokens + post_eval_summary.total_output_tokens) - (
        pre_eval_summary.total_input_tokens + pre_eval_summary.total_output_tokens
    )

    print("📊 This Evaluation:")
    print(f"   Requests: {eval_requests}")
    print(f"   Cost: ${eval_cost:.4f}")
    print(f"   Tokens: {eval_tokens:,}")
    print(f"   Duration: {duration:.1f}s")

    if eval_requests > 0:
        print(f"   Cost/Request: ${eval_cost/eval_requests:.6f}")
        print(f"   Tokens/Request: {eval_tokens/eval_requests:.1f}")
        print(f"   Requests/Second: {eval_requests/duration:.2f}")

    # Check for post-evaluation alerts
    post_alerts = monitor.check_budget_alerts()
    new_alerts = [alert for alert in post_alerts if alert not in alerts]

    if new_alerts:
        print("\n⚠️  New budget alerts after evaluation:")
        for alert in new_alerts:
            print(f"   {alert['message']}")

    # Generate recommendations
    recommendations = monitor.get_optimization_recommendations()
    if recommendations:
        print("\n💡 Cost Optimization Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
            print(f"   {i}. {rec['title']}")
            print(f"      {rec['description']}")

    # Offer to generate detailed report
    if eval_cost > 0.01:  # Only for significant costs
        response = input("\n📊 Generate detailed cost report? (y/N): ").strip().lower()
        if response == "y":
            report_file = monitor.export_report("today", "json")
            dashboard_file = monitor.create_usage_dashboard("today")
            print("📄 Reports generated:")
            print(f"   Cost Report: {report_file}")
            print(f"   Dashboard: {dashboard_file}")

    # Summary
    print("\n🎯 Evaluation Summary:")
    if evaluation_success:
        print("   ✅ RAGChecker evaluation completed successfully")
        print(f"   💰 Total cost: ${eval_cost:.4f}")
        print(f"   ⚡ Performance: {eval_requests/duration:.2f} requests/second")
    else:
        print("   ❌ RAGChecker evaluation failed")
        print(f"   💰 Partial cost: ${eval_cost:.4f}")

    return 0 if evaluation_success else 1


def main():
    """Main function with argument parsing."""
    import argparse

    parser = argparse.ArgumentParser(description="RAGChecker Evaluation with Cost Monitoring")
    parser.add_argument("--budget-check-only", action="store_true", help="Only check budget status")
    parser.add_argument("--cost-summary", choices=["today", "week", "month"], help="Show cost summary for period")
    parser.add_argument("--skip-budget-check", action="store_true", help="Skip pre-evaluation budget check")

    args = parser.parse_args()

    monitor = BedrockCostMonitor()

    if args.budget_check_only:
        alerts = monitor.check_budget_alerts()
        if alerts:
            print("⚠️  Budget Alerts:")
            for alert in alerts:
                print(f"   {alert['message']}")
            return 1
        else:
            print("✅ No budget alerts")
            return 0

    elif args.cost_summary:
        monitor.print_cost_summary(args.cost_summary)
        return 0

    else:
        # Set environment variable to skip budget check if requested
        if args.skip_budget_check:
            os.environ["RAGCHECKER_SKIP_BUDGET_CHECK"] = "1"

        return run_evaluation_with_monitoring()


if __name__ == "__main__":
    sys.exit(main())
