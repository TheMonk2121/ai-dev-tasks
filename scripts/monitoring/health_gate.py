from __future__ import annotations

import json
import sys
from subprocess import run

#!/usr/bin/env python3
"""
Health Gate for CI/Automation

Exits with non-zero status if overall health is not healthy.
"""

def main() -> int:
    result = run(
        ["uv", "run", "python", "scripts/system_monitor.py", "--format", "json"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("health_gate: system_monitor failed", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        return 2

    try:
        stdout = result.stdout
        # Scan for all JSON objects and pick the one containing \"system_health\"
        candidates = []
        for start_idx, ch in enumerate(stdout):
            if ch != "{":
                continue
            depth = 0
            end_idx = None
            i = start_idx
            while i < len(stdout):
                c = stdout[i]
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break
                i += 1
            if end_idx is None:
                continue
            snippet = stdout[start_idx : end_idx + 1]
            if '"system_health"' in snippet:
                candidates.append(snippet)
        if not candidates:
            raise ValueError("no JSON payload with system_health found")
        payload = candidates[-1]
        report = json.loads(payload)
    except Exception as e:
        print(f"health_gate: failed to parse JSON: {e}", file=sys.stderr)
        return 3

    status = report.get("system_health", {}).get("overall_status", "unknown")
    if status != "healthy":
        print(f"❌ Health gate failed: overall_status={status}")
        # Print brief dependency summary
        deps = report.get("system_health", {}).get("dependencies", {})
        for name, dep in deps.items():
            print(f" - {name}: {dep.get('status')} ({dep.get('response_time', 0):.3f}s)")
        return 1

    print("✅ Health gate passed: overall_status=healthy")
    return 0

if __name__ == "__main__":
    sys.exit(main())