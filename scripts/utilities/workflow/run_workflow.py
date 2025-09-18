from __future__ import annotations

import subprocess
import sys
from pathlib import Path

#!/usr/bin/env -S uv run python
"""
Workflow Runner
--------------
Simple wrapper that ensures the virtual environment is active and runs the workflow.
"""

def main() -> Any:
    """Run the workflow with venv management."""

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    if not (project_root / ".venv").exists():
        print("❌ Virtual environment not found at .venv/")
        print("💡 Please create it manually with: uv venv --python 3.12")
        print("💡 Then run: uv sync")
        sys.exit(1)

    # Check venv status
    try:
        result = subprocess.run(
            [sys.executable, "scripts/venv_manager.py", "--check"], capture_output=True, text=True, cwd=project_root
        )

        if result.returncode != 0:
            print("❌ Virtual environment issues:")
            print(result.stdout)
            print(result.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error checking virtual environment: {e}")
        sys.exit(1)

    # Run the single doorway workflow
    try:
        # Pass all arguments to single_doorway.py
        cmd = [sys.executable, "scripts/single_doorway.py"] + sys.argv[1:]
        subprocess.run(cmd, cwd=project_root)

    except KeyboardInterrupt:
        print("\n🛑 Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()