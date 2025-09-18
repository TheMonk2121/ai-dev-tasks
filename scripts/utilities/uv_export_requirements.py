from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
UV Export Requirements Script

This script exports dependencies from pyproject.toml to requirements.txt format
for backward compatibility with tools that still expect requirements.txt files.
"""

def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        result: Any = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def export_requirements(output_file: str = "requirements.txt", dev: bool = False) -> None:
    """Export requirements from pyproject.toml to requirements.txt format."""

    # Check if UV is available
    try:
        run_command(["uv", "--version"])
    except FileNotFoundError:
        print("❌ UV not found. Please install UV first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    # Check if pyproject.toml exists
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found in current directory")
        sys.exit(1)

    print(f"📦 Exporting requirements to {output_file}")
    if dev:
        print("📦 Including development dependencies")

    # Build the export command
    cmd = ["uv", "export", "--format", "requirements-txt"]
    if dev:
        cmd.extend(["--extra", "dev"])

    # Run the export command
    result = run_command(cmd)

    # Write to file
    with open(output_file, "w") as f:
        f.write(result.stdout)

    print(f"✅ Requirements exported to {output_file}")

    # Show summary
    lines = result.stdout.strip().split("\n")
    print(f"📊 Exported {len(lines)} dependencies")

    # Show first few lines as preview
    print("\n📋 Preview (first 10 lines):")
    for i, line in enumerate(lines[:10]):
        print(f"  {line}")

    if len(lines) > 10:
        print(f"  ... and {len(lines) - 10} more lines")

def export_lock_to_requirements(output_file: str = "requirements-lock.txt") -> None:
    """Export locked dependencies from uv.lock to requirements.txt format."""

    if not Path("uv.lock").exists():
        print("❌ uv.lock not found. Run 'uv lock' first to generate lock file")
        sys.exit(1)

    print(f"🔒 Exporting locked requirements to {output_file}")

    # Export from lock file
    cmd = ["uv", "export", "--format", "requirements-txt", "--locked"]
    result = run_command(cmd)

    # Write to file
    with open(output_file, "w") as f:
        f.write(result.stdout)

    print(f"✅ Locked requirements exported to {output_file}")

def main() -> Any:
    """Main function."""
    parser: Any = argparse.ArgumentParser(description="Export dependencies from pyproject.toml to requirements.txt format")
    parser.add_argument(
        "--output", "-o", default="requirements.txt", help="Output file name (default: requirements.txt)"
    )
    parser.add_argument("--dev", "-d", action="store_true", help="Include development dependencies")
    parser.add_argument("--lock", "-l", action="store_true", help="Export from uv.lock (locked versions)")
    parser.add_argument("--preview", "-p", action="store_true", help="Show preview without writing file")

    args: Any = parser.parse_args()

    if args.preview:
        print("📋 Preview mode - showing what would be exported:")
        if args.lock:
            cmd = ["uv", "export", "--format", "requirements-txt", "--locked"]
        else:
            cmd = ["uv", "export", "--format", "requirements-txt"]
            if args.dev:
                cmd.extend(["--extra", "dev"])

        result = run_command(cmd)
        print(result.stdout)
        return

    if args.lock:
        export_lock_to_requirements(args.output)
    else:
        export_requirements(args.output, args.dev)

if __name__ == "__main__":
    main()