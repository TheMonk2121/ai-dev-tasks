#!/usr/bin/env python3
"""
Lightweight wrapper to trigger the project's memory rehydration.

Provides both:
- a callable function: rehydrate_memory(role, query, output_format)
- a CLI: python scripts/memory_rehydrate.py --role planner --query "..."

This delegates to ./scripts/memory_up.sh using supported flags (-q, -r, -f).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Literal

OutputFormat = Literal["cursor", "json"]


def rehydrate_memory(
    role: str = "planner",
    query: str = "current project status and core documentation",
    output_format: OutputFormat = "cursor",
) -> bool:
    """Invoke the memory rehydration script and stream output to stdout.

    Returns True on success (exit code 0), False otherwise.
    """
    cmd = [
        "./scripts/memory_up.sh",
        "-q",
        query,
        "-r",
        role,
    ]

    if output_format == "json":
        cmd.extend(["-f", "json"])

    try:
        # Stream output directly so users see the formatted bundle
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: ./scripts/memory_up.sh not found", file=sys.stderr)
        return False
    except Exception as exc:  # noqa: BLE001 - top-level CLI guard
        print(f"Error running memory rehydrator: {exc}", file=sys.stderr)
        return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger memory rehydration bundle generation")
    parser.add_argument(
        "--role",
        default="planner",
        help="Role context to generate (planner, implementer, researcher, coder)",
    )
    parser.add_argument(
        "--query",
        default="current project status and core documentation",
        help="Query/topic focus for the memory bundle",
    )
    parser.add_argument(
        "--format",
        choices=("cursor", "json"),
        default="cursor",
        help="Output format (rendered for chat or machine-readable JSON)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ok = rehydrate_memory(role=args.role, query=args.query, output_format=args.format)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
