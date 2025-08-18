#!/usr/bin/env python3.12.123.11
"""Validator flip manager - automated FAIL mode transitions"""

import datetime
import json
import os
import subprocess
import sys

TARGETS = {"archive": 3, "shadow_fork": 7, "multirep": 5, "readme": 14}
COUNTERS_PATH = "data/validator_counters.json"  # machine state
FLIP_LOG_MD = "402_validator-flip-log.md"


def load(path, default):
    """Load JSON file with default fallback"""
    try:
        return json.load(open(path))
    except:
        return default


def save(path, obj):
    """Save JSON file with directory creation"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w"), indent=2, sort_keys=True)


def load_counters_from_state():
    """Load counters from state branch if available"""
    try:
        subprocess.run(
            ["git", "fetch", "origin", "bot/validator-state:bot/validator-state"], capture_output=True, check=False
        )

        result = subprocess.run(
            ["git", "show", "bot/validator-state:data/validator_counters.json"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass

    return load(COUNTERS_PATH, dict.fromkeys(TARGETS, 0))


def is_fail_flag_enabled(category):
    """Check if category is already in FAIL mode"""
    flag_map = {
        "archive": "VALIDATOR_ARCHIVE_FAIL",
        "shadow_fork": "VALIDATOR_SHADOW_FAIL",
        "readme": "VALIDATOR_README_FAIL",
        "multirep": "VALIDATOR_MULTIREP_FAIL",
    }
    return os.getenv(flag_map.get(category, ""), "0") == "1"


def bump_flags(flips):
    """Update environment flags for flipped categories"""
    # This would update the workflow file or environment
    # For now, just print what would be updated
    print(f"Would update flags for: {', '.join(flips)}")
    for flip in flips:
        flag_name = f"VALIDATOR_{flip.upper()}_FAIL"
        print(f"  {flag_name} = 1")


def append_flip_log(log_path, flips, today, counters):
    """Append flip entry to immutable log"""
    entry = f"\n## {today} - Auto-flip\n"
    entry += f"Categories flipped: {', '.join(flips)}\n"
    entry += f"Counters: {json.dumps(counters)}\n"
    with open(log_path, "a") as f:
        f.write(entry)


def create_flip_pr(flips, today, counters):
    """Create flip PR with GH CLI or action fallback"""
    # Get recent metrics trend
    trend_data = get_recent_metrics_trend()

    # Build enriched PR body
    pr_body = f"""# Validator Flip: {', '.join(flips)}

Automated flip of validators to FAIL mode based on clean day counters.

## Recent Trend (Last 7 Runs)
{format_metrics_trend(trend_data)}

## Current Counters
{format_counters_table(counters)}

## Details
- Categories: {', '.join(flips)}
- Date: {today}

## Changes
"""
    for flip in flips:
        pr_body += f"- Set `VALIDATOR_{flip.upper()}_FAIL=1` in CI environment\n"

    pr_body += """
## Checklist
- [ ] Review flip criteria and recent trend
- [ ] Test for false positives
- [ ] Approve deployment

## Rollback
If >5% false positives in 48h, revert with consensus note in logs.
"""

    branch = f"auto/validator-flip-{today}"
    subprocess.check_call(["git", "checkout", "-b", branch])
    bump_flags(flips)
    append_flip_log(FLIP_LOG_MD, flips, today, counters)
    subprocess.check_call(["git", "commit", "-am", f"Flip validators to FAIL: {', '.join(flips)}"])

    # Try GH CLI first, fallback to action
    try:
        subprocess.check_call(["gh", "pr", "create", "--fill"])
        print(f"Created flip PR via GH CLI: {', '.join(flips)}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: create PR via action
        with open(".github/pull_request_template_flip.md", "w") as f:
            f.write(pr_body)

        print("Created flip PR template: .github/pull_request_template_flip.md")
        print("Manual PR creation required via GitHub UI or action")


def get_recent_metrics_trend():
    """Get last 7 versions of metrics from bot/validator-state."""
    try:
        # Get last 7 commits that touched metrics file
        result = subprocess.run(
            ["git", "log", "--oneline", "-7", "--format=%H", "bot/validator-state:metrics/validator_counts.json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return []

        commits = result.stdout.strip().split("\n")
        trend_data = []

        for commit in commits:
            if commit:
                try:
                    # Get metrics for this commit
                    metrics_result = subprocess.run(
                        ["git", "show", f"{commit}:metrics/validator_counts.json"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if metrics_result.returncode == 0:
                        metrics = json.loads(metrics_result.stdout)
                        trend_data.append(
                            {"date": metrics.get("generated_at", "unknown"), "counts": metrics.get("counts", {})}
                        )
                except Exception:
                    continue

        return trend_data
    except Exception:
        return []


def format_metrics_trend(trend_data):
    """Format metrics trend as markdown table."""
    if not trend_data:
        return "No recent trend data available"

    lines = ["| Date | readme | multirep |", "|---|---:|---:|"]

    for entry in trend_data[-7:]:  # Last 7 entries
        date = entry["date"][:10] if len(entry["date"]) >= 10 else entry["date"]
        readme = entry["counts"].get("readme", 0)
        multirep = entry["counts"].get("multirep", 0)
        lines.append(f"| {date} | {readme} | {multirep} |")

    return "\n".join(lines)


def format_counters_table(counters):
    """Format counters as markdown table."""
    targets = {"archive": 3, "shadow_fork": 7, "multirep": 5, "readme": 14}

    lines = ["| Category | Days | Target |", "|---|---:|---:|"]
    for category, days in counters.items():
        target = targets.get(category, "-")
        lines.append(f"| {category} | {days} | {target} |")

    return "\n".join(lines)


def main(report_path):
    """Main flip manager logic"""
    r = json.load(open(report_path))
    counters = load_counters_from_state()
    today = datetime.date.today().isoformat()

    for cat, info in r["categories"].items():
        if info["violations"] == 0:
            counters[cat] = counters.get(cat, 0) + 1
        else:
            counters[cat] = 0  # reset on any violation

    save(COUNTERS_PATH, counters)

    flips = [c for c, days in counters.items() if days >= TARGETS[c] and not is_fail_flag_enabled(c)]
    if flips:
        create_flip_pr(flips, today, counters)


if __name__ == "__main__":
    main(sys.argv[1])
