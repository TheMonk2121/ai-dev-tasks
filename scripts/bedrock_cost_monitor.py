#!/usr/bin/env python3
"""
AWS Bedrock Cost Monitoring and Analytics Dashboard
Provides real-time usage tracking, budget alerts, and cost analytics for RAGChecker evaluations
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# Optional imports for visualization
try:
    import matplotlib.pyplot as plt  # type: ignore
    import pandas as pd  # type: ignore

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("⚠️ matplotlib/pandas not available - visualization features disabled")


@dataclass
class CostAlert:
    """Cost alert configuration and status."""

    threshold: float
    period: str  # "daily", "weekly", "monthly"
    alert_type: str  # "budget", "spike", "trend"
    enabled: bool = True
    last_triggered: str | None = None


@dataclass
class UsageSummary:
    """Usage summary for a time period."""

    period: str
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    avg_cost_per_request: float
    avg_tokens_per_request: float
    peak_usage_hour: str | None = None


class BedrockCostMonitor:
    """
    AWS Bedrock cost monitoring and analytics system.

    Features:
    - Real-time usage tracking and cost calculation
    - Budget alerts and threshold monitoring
    - Usage analytics and trend analysis
    - Cost optimization recommendations
    - Export capabilities for reporting
    """

    def __init__(
        self, usage_log_file: str = "metrics/bedrock_usage.json", config_file: str = "config/bedrock_cost_config.json"
    ):
        """
        Initialize cost monitor.

        Args:
            usage_log_file: Path to Bedrock usage log file
            config_file: Path to cost monitoring configuration
        """
        self.usage_log_file = Path(usage_log_file)
        self.config_file = Path(config_file)
        self.reports_dir = Path("metrics/cost_reports")

        # Ensure directories exist
        self.usage_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Claude 3.5 Sonnet pricing (as of 2024)
        self.INPUT_TOKEN_COST = 3.00 / 1_000_000  # $3.00 per 1M input tokens
        self.OUTPUT_TOKEN_COST = 15.00 / 1_000_000  # $15.00 per 1M output tokens

    def _load_config(self) -> dict[str, Any]:
        """Load cost monitoring configuration."""
        default_config = {
            "budget_alerts": {
                "daily_budget": 5.00,
                "weekly_budget": 25.00,
                "monthly_budget": 100.00,
                "spike_threshold": 2.0,  # 2x average cost
            },
            "notifications": {
                "email_enabled": False,
                "email_address": "",
                "slack_webhook": "",
            },
            "optimization": {
                "auto_suggest": True,
                "cost_efficiency_threshold": 0.001,  # $0.001 per request
            },
        }

        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"⚠️ Failed to load config, using defaults: {e}")

        # Save default config
        with open(self.config_file, "w") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def load_usage_data(self) -> list[dict[str, Any]]:
        """Load usage data from log file."""
        if not self.usage_log_file.exists():
            return []

        try:
            with open(self.usage_log_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load usage data: {e}")
            return []

    def get_usage_summary(self, period: str = "today") -> UsageSummary:
        """
        Get usage summary for specified period.

        Args:
            period: "today", "week", "month", or "all"

        Returns:
            UsageSummary object with aggregated metrics
        """
        usage_data = self.load_usage_data()

        if not usage_data:
            return UsageSummary(
                period=period,
                total_requests=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_cost=0.0,
                avg_cost_per_request=0.0,
                avg_tokens_per_request=0.0,
            )

        # Filter by period
        now = datetime.now()
        filtered_data = []

        for entry in usage_data:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])

                if period == "today":
                    if entry_time.date() == now.date():
                        filtered_data.append(entry)
                elif period == "week":
                    week_start = now - timedelta(days=7)
                    if entry_time >= week_start:
                        filtered_data.append(entry)
                elif period == "month":
                    month_start = now - timedelta(days=30)
                    if entry_time >= month_start:
                        filtered_data.append(entry)
                else:  # "all"
                    filtered_data.append(entry)

            except (ValueError, KeyError):
                continue

        if not filtered_data:
            return UsageSummary(
                period=period,
                total_requests=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_cost=0.0,
                avg_cost_per_request=0.0,
                avg_tokens_per_request=0.0,
            )

        # Calculate aggregates
        total_requests = sum(entry.get("request_count", 0) for entry in filtered_data)
        total_input_tokens = sum(entry.get("input_tokens", 0) for entry in filtered_data)
        total_output_tokens = sum(entry.get("output_tokens", 0) for entry in filtered_data)
        total_cost = sum(entry.get("total_cost", 0.0) for entry in filtered_data)

        avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0.0
        avg_tokens_per_request = (
            (total_input_tokens + total_output_tokens) / total_requests if total_requests > 0 else 0.0
        )

        # Find peak usage hour
        peak_usage_hour = None
        if filtered_data:
            hourly_usage: dict[str, float] = {}
            for entry in filtered_data:
                try:
                    hour = datetime.fromisoformat(entry["timestamp"]).strftime("%H:00")
                    hourly_usage[hour] = hourly_usage.get(hour, 0.0) + entry.get("total_cost", 0.0)
                except (ValueError, KeyError):
                    continue

            if hourly_usage:
                peak_usage_hour = max(hourly_usage.keys(), key=lambda k: hourly_usage[k])

        return UsageSummary(
            period=period,
            total_requests=total_requests,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cost=total_cost,
            avg_cost_per_request=avg_cost_per_request,
            avg_tokens_per_request=avg_tokens_per_request,
            peak_usage_hour=peak_usage_hour,
        )

    def check_budget_alerts(self) -> list[dict[str, Any]]:
        """Check for budget threshold violations and return alerts."""
        alerts = []

        # Check daily budget
        today_summary = self.get_usage_summary("today")
        daily_budget = self.config["budget_alerts"]["daily_budget"]

        if today_summary.total_cost > daily_budget:
            alerts.append(
                {
                    "type": "budget_exceeded",
                    "period": "daily",
                    "current": today_summary.total_cost,
                    "budget": daily_budget,
                    "severity": "high" if today_summary.total_cost > daily_budget * 1.5 else "medium",
                    "message": f"Daily budget exceeded: ${today_summary.total_cost:.4f} / ${daily_budget:.2f}",
                }
            )

        # Check weekly budget
        week_summary = self.get_usage_summary("week")
        weekly_budget = self.config["budget_alerts"]["weekly_budget"]

        if week_summary.total_cost > weekly_budget:
            alerts.append(
                {
                    "type": "budget_exceeded",
                    "period": "weekly",
                    "current": week_summary.total_cost,
                    "budget": weekly_budget,
                    "severity": "high" if week_summary.total_cost > weekly_budget * 1.2 else "medium",
                    "message": f"Weekly budget exceeded: ${week_summary.total_cost:.4f} / ${weekly_budget:.2f}",
                }
            )

        # Check for cost spikes
        spike_threshold = self.config["budget_alerts"]["spike_threshold"]
        if today_summary.avg_cost_per_request > 0:
            week_avg = week_summary.avg_cost_per_request
            if week_avg > 0 and today_summary.avg_cost_per_request > week_avg * spike_threshold:
                alerts.append(
                    {
                        "type": "cost_spike",
                        "period": "today",
                        "current": today_summary.avg_cost_per_request,
                        "baseline": week_avg,
                        "severity": "medium",
                        "message": f"Cost spike detected: ${today_summary.avg_cost_per_request:.6f} vs ${week_avg:.6f} avg",
                    }
                )

        return alerts

    def generate_cost_report(self, period: str = "week") -> dict[str, Any]:
        """Generate comprehensive cost report."""
        summary = self.get_usage_summary(period)
        alerts = self.check_budget_alerts()
        recommendations = self.get_optimization_recommendations()

        report = {
            "report_date": datetime.now().isoformat(),
            "period": period,
            "summary": {
                "total_requests": summary.total_requests,
                "total_cost": summary.total_cost,
                "avg_cost_per_request": summary.avg_cost_per_request,
                "total_tokens": summary.total_input_tokens + summary.total_output_tokens,
                "avg_tokens_per_request": summary.avg_tokens_per_request,
                "peak_usage_hour": summary.peak_usage_hour,
            },
            "budget_status": {
                "daily_usage": self.get_usage_summary("today").total_cost,
                "daily_budget": self.config["budget_alerts"]["daily_budget"],
                "weekly_usage": self.get_usage_summary("week").total_cost,
                "weekly_budget": self.config["budget_alerts"]["weekly_budget"],
                "monthly_usage": self.get_usage_summary("month").total_cost,
                "monthly_budget": self.config["budget_alerts"]["monthly_budget"],
            },
            "alerts": alerts,
            "recommendations": recommendations,
            "cost_breakdown": self._get_cost_breakdown(period),
        }

        return report

    def _get_cost_breakdown(self, period: str) -> dict[str, Any]:
        """Get detailed cost breakdown by component."""
        usage_data = self.load_usage_data()

        if not usage_data:
            return {"input_tokens": 0.0, "output_tokens": 0.0, "total": 0.0}

        # Filter by period (reuse logic from get_usage_summary)
        summary = self.get_usage_summary(period)

        input_cost = summary.total_input_tokens * self.INPUT_TOKEN_COST
        output_cost = summary.total_output_tokens * self.OUTPUT_TOKEN_COST

        return {
            "input_tokens": {
                "count": summary.total_input_tokens,
                "cost": input_cost,
                "rate": self.INPUT_TOKEN_COST * 1_000_000,  # per 1M tokens
            },
            "output_tokens": {
                "count": summary.total_output_tokens,
                "cost": output_cost,
                "rate": self.OUTPUT_TOKEN_COST * 1_000_000,  # per 1M tokens
            },
            "total": summary.total_cost,
        }

    def get_optimization_recommendations(self) -> list[dict[str, Any]]:
        """Generate cost optimization recommendations."""
        recommendations = []

        summary = self.get_usage_summary("week")

        if summary.total_requests == 0:
            return recommendations

        # Check cost efficiency
        efficiency_threshold = self.config["optimization"]["cost_efficiency_threshold"]
        if summary.avg_cost_per_request > efficiency_threshold:
            recommendations.append(
                {
                    "type": "cost_efficiency",
                    "priority": "medium",
                    "title": "High cost per request detected",
                    "description": f"Average cost per request (${summary.avg_cost_per_request:.6f}) exceeds threshold (${efficiency_threshold:.6f})",
                    "suggestions": [
                        "Consider using shorter prompts to reduce input tokens",
                        "Optimize response length with RAGCHECKER_MAX_WORDS",
                        "Use batch processing for multiple evaluations",
                        "Enable fast mode for development testing",
                    ],
                }
            )

        # Check token usage patterns
        if summary.avg_tokens_per_request > 2000:
            recommendations.append(
                {
                    "type": "token_optimization",
                    "priority": "low",
                    "title": "High token usage per request",
                    "description": f"Average tokens per request ({summary.avg_tokens_per_request:.0f}) is high",
                    "suggestions": [
                        "Review prompt engineering for conciseness",
                        "Use context ranking to limit relevant chunks",
                        "Consider response length limits",
                    ],
                }
            )

        # Check usage patterns
        if summary.peak_usage_hour:
            recommendations.append(
                {
                    "type": "usage_pattern",
                    "priority": "info",
                    "title": "Peak usage optimization",
                    "description": f"Peak usage occurs at {summary.peak_usage_hour}",
                    "suggestions": [
                        "Consider spreading evaluations across different hours",
                        "Use local LLM for development during peak hours",
                        "Batch non-urgent evaluations for off-peak processing",
                    ],
                }
            )

        return recommendations

    def create_usage_dashboard(self, period: str = "week") -> str:
        """Create visual usage dashboard and save as image."""
        if not VISUALIZATION_AVAILABLE:
            print("❌ Visualization not available - install matplotlib and pandas")
            return ""

        usage_data = self.load_usage_data()

        if not usage_data:
            print("⚠️ No usage data available for dashboard")
            return ""

        # Prepare data for visualization
        df = pd.DataFrame(usage_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["date"] = df["timestamp"].dt.date

        # Filter by period
        now = datetime.now()
        if period == "today":
            df = df[df["date"] == now.date()]
        elif period == "week":
            week_start = now - timedelta(days=7)
            df = df[df["timestamp"] >= week_start]
        elif period == "month":
            month_start = now - timedelta(days=30)
            df = df[df["timestamp"] >= month_start]

        if df.empty:
            print(f"⚠️ No usage data for period: {period}")
            return ""

        # Create dashboard
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"AWS Bedrock Usage Dashboard - {period.title()}", fontsize=16)

        # Cost over time
        daily_cost = df.groupby("date")["total_cost"].sum()
        axes[0, 0].plot(daily_cost.index, daily_cost.values, marker="o")
        axes[0, 0].set_title("Daily Cost Trend")
        axes[0, 0].set_ylabel("Cost ($)")
        axes[0, 0].tick_params(axis="x", rotation=45)

        # Token usage distribution
        axes[0, 1].hist(
            [df["input_tokens"], df["output_tokens"]], label=["Input Tokens", "Output Tokens"], alpha=0.7, bins=20
        )
        axes[0, 1].set_title("Token Usage Distribution")
        axes[0, 1].set_xlabel("Tokens")
        axes[0, 1].set_ylabel("Frequency")
        axes[0, 1].legend()

        # Hourly usage pattern
        hourly_usage = df.groupby("hour")["total_cost"].sum()
        axes[1, 0].bar(hourly_usage.index, hourly_usage.values)
        axes[1, 0].set_title("Usage by Hour of Day")
        axes[1, 0].set_xlabel("Hour")
        axes[1, 0].set_ylabel("Total Cost ($)")

        # Cost per request trend
        df["cost_per_request"] = df["total_cost"] / df["request_count"]
        daily_cpr = df.groupby("date")["cost_per_request"].mean()
        axes[1, 1].plot(daily_cpr.index, daily_cpr.values, marker="s", color="orange")
        axes[1, 1].set_title("Cost per Request Trend")
        axes[1, 1].set_ylabel("Cost per Request ($)")
        axes[1, 1].tick_params(axis="x", rotation=45)

        plt.tight_layout()

        # Save dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_file = self.reports_dir / f"bedrock_dashboard_{period}_{timestamp}.png"
        plt.savefig(dashboard_file, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"📊 Dashboard saved: {dashboard_file}")
        return str(dashboard_file)

    def export_report(self, period: str = "week", format: str = "json") -> str:
        """Export cost report in specified format."""
        report = self.generate_cost_report(period)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format.lower() == "json":
            report_file = self.reports_dir / f"bedrock_cost_report_{period}_{timestamp}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

        elif format.lower() == "csv":
            # Export usage data as CSV
            if not VISUALIZATION_AVAILABLE:
                print("❌ CSV export requires pandas - install pandas")
                return ""

            usage_data = self.load_usage_data()
            if usage_data:
                df = pd.DataFrame(usage_data)
                report_file = self.reports_dir / f"bedrock_usage_data_{period}_{timestamp}.csv"
                df.to_csv(report_file, index=False)
            else:
                print("⚠️ No usage data to export")
                return ""

        else:
            print(f"❌ Unsupported format: {format}")
            return ""

        print(f"📄 Report exported: {report_file}")
        return str(report_file)

    def print_cost_summary(self, period: str = "today"):
        """Print formatted cost summary to console."""
        summary = self.get_usage_summary(period)
        alerts = self.check_budget_alerts()

        print(f"\n💰 AWS Bedrock Cost Summary - {period.title()}")
        print("=" * 50)

        print("📊 Usage Metrics:")
        print(f"   Total Requests: {summary.total_requests}")
        print(f"   Total Cost: ${summary.total_cost:.4f}")
        print(f"   Avg Cost/Request: ${summary.avg_cost_per_request:.6f}")
        print(f"   Total Tokens: {summary.total_input_tokens + summary.total_output_tokens:,}")
        print(f"   Avg Tokens/Request: {summary.avg_tokens_per_request:.1f}")

        if summary.peak_usage_hour:
            print(f"   Peak Usage Hour: {summary.peak_usage_hour}")

        # Budget status
        print("\n💳 Budget Status:")
        daily_summary = self.get_usage_summary("today")
        weekly_summary = self.get_usage_summary("week")
        monthly_summary = self.get_usage_summary("month")

        daily_budget = self.config["budget_alerts"]["daily_budget"]
        weekly_budget = self.config["budget_alerts"]["weekly_budget"]
        monthly_budget = self.config["budget_alerts"]["monthly_budget"]

        daily_pct = (daily_summary.total_cost / daily_budget * 100) if daily_budget > 0 else 0
        weekly_pct = (weekly_summary.total_cost / weekly_budget * 100) if weekly_budget > 0 else 0
        monthly_pct = (monthly_summary.total_cost / monthly_budget * 100) if monthly_budget > 0 else 0

        print(f"   Daily: ${daily_summary.total_cost:.4f} / ${daily_budget:.2f} ({daily_pct:.1f}%)")
        print(f"   Weekly: ${weekly_summary.total_cost:.4f} / ${weekly_budget:.2f} ({weekly_pct:.1f}%)")
        print(f"   Monthly: ${monthly_summary.total_cost:.4f} / ${monthly_budget:.2f} ({monthly_pct:.1f}%)")

        # Alerts
        if alerts:
            print(f"\n⚠️  Active Alerts ({len(alerts)}):")
            for alert in alerts:
                severity_icon = "🔴" if alert["severity"] == "high" else "🟡"
                print(f"   {severity_icon} {alert['message']}")
        else:
            print("\n✅ No budget alerts")

        # Quick recommendations
        recommendations = self.get_optimization_recommendations()
        if recommendations:
            print("\n💡 Top Recommendations:")
            for rec in recommendations[:2]:  # Show top 2
                print(f"   • {rec['title']}")


def main():
    """Main function for cost monitoring CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="AWS Bedrock Cost Monitoring Dashboard")
    parser.add_argument(
        "--period", choices=["today", "week", "month", "all"], default="today", help="Time period for analysis"
    )
    parser.add_argument("--dashboard", action="store_true", help="Generate visual dashboard")
    parser.add_argument("--export", choices=["json", "csv"], help="Export report in specified format")
    parser.add_argument("--alerts", action="store_true", help="Check budget alerts only")

    args = parser.parse_args()

    monitor = BedrockCostMonitor()

    if args.alerts:
        alerts = monitor.check_budget_alerts()
        if alerts:
            print("⚠️  Budget Alerts:")
            for alert in alerts:
                print(f"   {alert['message']}")
        else:
            print("✅ No budget alerts")
    elif args.dashboard:
        dashboard_file = monitor.create_usage_dashboard(args.period)
        if dashboard_file:
            print(f"📊 Dashboard created: {dashboard_file}")
    elif args.export:
        report_file = monitor.export_report(args.period, args.export)
        if report_file:
            print(f"📄 Report exported: {report_file}")
    else:
        monitor.print_cost_summary(args.period)


if __name__ == "__main__":
    main()
