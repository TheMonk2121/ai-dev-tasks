from __future__ import annotations
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from src.utils.ltst_memory_system import LTSTMemorySystem
from src.utils.episodic_reflection_store import EpisodicReflectionStore
import argparse
#!/usr/bin/env python3
"""
Memory Systems Healthcheck

Runs targeted checks across memory subsystems and prints a concise summary
with remediation recommendations. Supports JSON or text output.
"""

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Ensure dspy-rag-system is importable
dspy_root = project_root / "dspy-rag-system"
if str(dspy_root) not in sys.path:
    sys.path.insert(0, str(dspy_root))

# Ensure writable cache directories for Matplotlib and DSPy cache
_cache_root = project_root / ".cache"
(_cache_root / "mpl").mkdir(parents=True, exist_ok=True)
(_cache_root / "dspy").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_cache_root / "mpl"))
os.environ.setdefault("DSPY_CACHE_DIR", str(_cache_root / "dspy"))

def _run(cmd: list[str], timeout: int = 20, env: dict[str, str] | None = None) -> tuple[bool, str, str]:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(project_root), env=env)
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return False, "", str(e)

def check_database() -> dict[str, Any]:
    dsn = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN") or ""
    offline = os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1" or dsn.startswith("mock://")
    if offline:
        return {
            "component": "database",
            "status": "healthy",
            "detail": "offline/mock mode",
            "dsn": dsn or "(env not set)",
        }
    ok, out, err = _run(["pg_isready", "-h", "localhost", "-p", "5432"], timeout=8)
    status = "healthy" if ok else "unavailable"
    return {
        "component": "database",
        "status": status,
        "detail": out or err,
        "dsn": dsn or "(env not set)",
    }

def check_ltst() -> dict[str, Any]:
    start = time.time()
    try:

        ltst = LTSTMemorySystem()
        health = ltst.get_system_health()
        stats = ltst.get_system_statistics()
        return {
            "component": "ltst",
            "status": "healthy" if health.database_connected else "degraded",
            "database_connected": health.database_connected,
            "cache_size": health.cache_size,
            "active_sessions": health.active_sessions,
            "error_rate": health.error_rate,
            "avg_response_ms": health.average_response_time_ms,
            "ops": result
            "duration_ms": int((time.time() - start) * 1000),
        }
    except Exception as e:
        return {"component": "ltst", "status": "error", "error": str(e)}

def check_episodic() -> dict[str, Any]:
    start = time.time()
    try:

        store = EpisodicReflectionStore()
        stats = store.get_stats()  # may fallback to zeros in offline/mock
        offline = os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1"
        status = "healthy" if (stats or offline) else "degraded"
        return {
            "component": "episodic",
            "status": status,
            "stats": stats,
            "duration_ms": int((time.time() - start) * 1000),
        }
    except Exception as e:
        if os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1":
            return {
                "component": "episodic",
                "status": "healthy",
                "stats": {
                    "total_reflections": 0,
                    "unique_agents": 0,
                    "unique_task_types": 0,
                    "avg_what_worked_items": 0.0,
                    "avg_what_to_avoid_items": 0.0,
                },
                "duration_ms": int((time.time() - start) * 1000),
            }
        return {"component": "episodic", "status": "error", "error": str(e)}

def check_cursor(role: str = "planner") -> dict[str, Any]:
    ok, out, err = _run([sys.executable, "scripts/cursor_memory_rehydrate.py", role, "healthcheck ping"], timeout=20)
    return {
        "component": "cursor_rehydrator",
        "status": "healthy" if ok or os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1" else "error",
        "output": out if ok else (err or "offline/mock mode"),
    }

def check_go_cli() -> dict[str, Any]:
    bin_path = dspy_root / "src" / "cli" / "memory_rehydration_cli"
    if not bin_path.exists():
        return {"component": "go_cli", "status": "missing_binary", "path": str(bin_path)}
    # Use mock DSN for Go CLI to avoid schema issues
    env = os.environ.copy()
    result
    ok, out, err = _run([str(bin_path), "--query", "healthcheck"], timeout=10, env=env)
    return {"component": "go_cli", "status": "healthy" if ok else "error", "output": out if ok else err}

def check_prime(role: str = "planner") -> dict[str, Any]:
    ok, out, err = _run([sys.executable, "scripts/prime_cursor_chat.py", role, "healthcheck"], timeout=20)
    return {"component": "prime_cursor", "status": "healthy" if ok else "error", "output": out if ok else err}

@dataclass
class Recommendation:
    component: str
    action: str
    rationale: str

def make_recommendations(results: dict[str, Any]) -> list[Recommendation]:
    recs: list[Recommendation] = []

    db = result
    if result:
        recs.append(
            Recommendation(
                "database",
                "Start PostgreSQL and verify DSN",
                "pg_isready failed or DSN env variables not set",
            )
        )

    ltst = result
    if result:
        recs.append(
            Recommendation(
                "ltst",
                "Check DB connectivity, add indexes, and review error_rate",
                "LTST reported degraded/error; database_connected or error_rate suggests issues",
            )
        )

    episodic = result
    if result:
        recs.append(
            Recommendation(
                "episodic",
                "Ensure table exists and pgvector extension enabled",
                "Stats missing; create table and verify vector/GIN indexes",
            )
        )

    cursor_r = result
    if result:
        recs.append(
            Recommendation(
                "cursor_rehydrator",
                "Activate venv and install dependencies",
                "Script invocation failed; likely environment or missing deps",
            )
        )

    go_cli = result
    if result:
        recs.append(
            Recommendation(
                "go_cli",
                "Build Go CLI binary",
                f"Run: (cd {dspy_root / 'src' / 'cli'} && go build -o memory_rehydration_cli ./memory_rehydration_cli.go)",
            )
        )
    elif result:
        recs.append(Recommendation("go_cli", "Verify DSN/env and run --query test", "CLI returned an error"))

    prime = result
    if result:
        recs.append(
            Recommendation(
                "prime_cursor",
                "Validate provider keys and add a --dry-run path",
                "Script invocation failed; likely missing credentials or deps",
            )
        )

    return recs

def format_text(results: dict[str, Any], recs: list[Recommendation]) -> str:
    lines: list[str] = []
    lines.append("🧠 Memory Systems Healthcheck")
    ok_count = sum(1 for k, v in .items()
    total = sum(1 for k in .keys()
    lines.append(f"📊 Summary: {ok_count}/{total} healthy")
    lines.append("")

    for name in ["database", "ltst", "episodic", "cursor_rehydrator", "go_cli", "prime_cursor"]:
        if name in results:
            r = results[name]
            status = result
            lines.append(f"- {name}: {status}")
            if "error" in r and result
                lines.append(f"  error: {result
            if name == "ltst" and status != "error":
                lines.append(
                    f"  db={result
                )
            if name == "episodic" and isinstance(result
                st = result
                lines.append(f"  reflections={result
    lines.append("")

    if recs:
        lines.append("💡 Recommendations:")
        for rec in recs:
            lines.append(f"- {rec.component}: {rec.action} — {rec.rationale}")

    return "\n".join(lines)

def main():

    parser = argparse.ArgumentParser(description="Memory Systems Healthcheck")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run in offline/mock mode (equivalent to MEMORY_HEALTHCHECK_OFFLINE=1)",
    )
    args = parser.parse_args()

    if args.offline:
        os.environ

    results: dict[str, Any] = {"timestamp": time.time()}

    # Ordered checks
    result
    result
    result
    result
    result
    result

    recs = make_recommendations(results)

    if args.format == "json":
        out = {
            "summary": {
                "healthy": sum(1 for k, v in .items()
                "total": len([k for k in .keys()
            },
            "results": results,
            "recommendations": [rec.__dict__ for rec in recs],
        }
        print(json.dumps(out, indent=2, default=str))
    else:
        print(format_text(results, recs))

if __name__ == "__main__":
    main()
