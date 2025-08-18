#!/usr/bin/env python3.12.123.11
"""
Weekly Metrics with Owners

Generates weekly validator metrics summary with suggested owners for top impacted files.
"""

import json
import os
from datetime import UTC, datetime


def load_codeowners() -> dict[str, str]:
    """Load CODEOWNERS file to map paths to owners."""
    owners = {}

    codeowners_path = ".github/CODEOWNERS"
    if not os.path.exists(codeowners_path):
        return owners

    with open(codeowners_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    path_pattern = parts[0]
                    owner = parts[1]
                    owners[path_pattern] = owner

    return owners


def find_owner_for_file(file_path: str, owners: dict[str, str]) -> str | None:
    """Find the owner for a given file path."""
    # Convert to relative path if needed
    if file_path.startswith("/"):
        cwd = os.getcwd()
        if file_path.startswith(cwd):
            file_path = file_path[len(cwd) :].lstrip("/")

    # Find the most specific match
    best_match = None
    best_owner = None

    for pattern, owner in owners.items():
        if pattern == "*":
            if not best_match:
                best_match = pattern
                best_owner = owner
        elif pattern.endswith("/"):
            if file_path.startswith(pattern):
                if not best_match or len(pattern) > len(best_match):
                    best_match = pattern
                    best_owner = owner
        elif file_path == pattern:
            best_match = pattern
            best_owner = owner
            break

    return best_owner


def load_metrics() -> dict:
    """Load current validator metrics."""
    metrics_path = "metrics/validator_counts.json"
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            return json.load(f)
    return {}


def load_historical_metrics(days: int = 7) -> list[dict]:
    """Load historical metrics from bot/validator-state."""
    historical = []

    try:
        import subprocess

        # Get list of recent commits in bot/validator-state
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", str(days), "bot/validator-state"],
            capture_output=True,
            text=True,
            check=True,
        )

        for line in result.stdout.strip().split("\n"):
            if line:
                commit_hash = line.split()[0]
                try:
                    # Get metrics from this commit
                    metrics_result = subprocess.run(
                        ["git", "show", f"{commit_hash}:metrics/validator_counts.json"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    metrics = json.loads(metrics_result.stdout)
                    historical.append(metrics)
                except Exception:
                    continue

    except Exception:
        pass

    return historical


def generate_trend_arrow(current: int, previous: int) -> str:
    """Generate trend arrow for metrics."""
    if current > previous:
        return "📈"
    elif current < previous:
        return "📉"
    else:
        return "➡️"


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate weekly metrics with owners")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Load data
    current_metrics = load_metrics()
    historical_metrics = load_historical_metrics(args.days)
    owners = load_codeowners()

    print("## Weekly Validator Metrics Summary")
    print(f"**Generated**: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"**Period**: Last {args.days} days")
    print()

    # Current counts
    print("### Current Violation Counts")
    print("| Category | Count | Trend |")
    print("|----------|-------|-------|")

    counts = current_metrics.get("counts", {})
    for category in ["archive", "shadow_fork", "readme", "multirep"]:
        current = counts.get(category, 0)

        # Find trend
        trend = "➡️"
        if historical_metrics:
            previous = historical_metrics[-1].get("counts", {}).get(category, 0)
            trend = generate_trend_arrow(current, previous)

        print(f"| {category} | {current} | {trend} |")

    print()

    # Top impacted files with owners
    print("### Top Impacted Files (with suggested owners)")

    impacted_files = current_metrics.get("top_impacted", {})
    for category, files in impacted_files.items():
        if files:
            print(f"\n**{category}:**")
            for file_path in files[:10]:  # Top 10
                owner = find_owner_for_file(file_path, owners)
                owner_info = f" (@{owner})" if owner else ""
                print(f"- `{file_path}`{owner_info}")

    print()

    # Near-expiry exceptions
    print("### Near-Expiry Exceptions (≤7 days)")

    try:
        with open("data/validator_exceptions.json") as f:
            ledger = json.load(f)

        near_expiry = []
        now = datetime.now(UTC)

        for file_path, entries in ledger.get("exceptions", {}).items():
            for entry in entries:
                expires = entry.get("expires")
                if expires:
                    try:
                        if len(expires) == 10 and expires[4] == "-" and expires[7] == "-":
                            expiry_date = datetime.fromisoformat(expires).replace(
                                hour=23, minute=59, second=59, tzinfo=UTC
                            )
                        else:
                            expiry_date = datetime.fromisoformat(expires.replace("Z", "+00:00"))

                        days_remaining = (expiry_date - now).days
                        if days_remaining <= 7:
                            near_expiry.append(
                                {
                                    "file": file_path,
                                    "key": entry.get("key", "unknown"),
                                    "expires": expires,
                                    "days_remaining": days_remaining,
                                    "reason": entry.get("reason", ""),
                                }
                            )
                    except Exception:
                        continue

        if near_expiry:
            # Sort by days remaining
            near_expiry.sort(key=lambda x: x["days_remaining"])

            print("| File | Key | Expires | Days Left | Reason |")
            print("|------|-----|---------|-----------|--------|")
            for item in near_expiry:
                print(
                    f"| {item['file']} | {item['key']} | {item['expires']} | {item['days_remaining']} | {item['reason'][:50]}... |"
                )
        else:
            print("OK No near-expiry exceptions found")

    except Exception as e:
        print(f"!️  Could not load exceptions: {e}")

    print()

    # JSON output
    if args.json:
        result = {
            "generated_at": datetime.now(UTC).isoformat() + "Z",
            "period_days": args.days,
            "current_counts": counts,
            "historical_metrics": historical_metrics,
            "top_impacted_with_owners": {},
        }

        for category, files in impacted_files.items():
            result["top_impacted_with_owners"][category] = [
                {"file": file_path, "suggested_owner": find_owner_for_file(file_path, owners)}
                for file_path in files[:10]
            ]

        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
