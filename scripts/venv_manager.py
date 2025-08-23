#!/usr/bin/env python3
"""
Virtual Environment Manager
---------------------------
Ensures the project virtual environment is properly activated and working.
This module handles venv detection, activation, and dependency validation.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


class VenvManager:
    """Manages virtual environment activation and validation."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.venv_python = self.venv_path / "bin" / "python3"
        self.venv_activate = self.venv_path / "bin" / "activate"

    def is_venv_active(self) -> bool:
        """Check if the project virtual environment is currently active."""
        # Check if VIRTUAL_ENV points to our project venv
        virtual_env = os.environ.get("VIRTUAL_ENV")
        if virtual_env:
            return Path(virtual_env).resolve() == self.venv_path.resolve()

        # Check if sys.prefix points to our project venv
        return Path(sys.prefix).resolve() == self.venv_path.resolve()

    def venv_exists(self) -> bool:
        """Check if the virtual environment exists."""
        return self.venv_path.exists() and self.venv_python.exists()

    def get_venv_python_path(self) -> Optional[Path]:
        """Get the path to the venv Python executable."""
        if self.venv_exists():
            return self.venv_python
        return None

    def validate_dependencies(self) -> Tuple[bool, list[str]]:
        """Validate that required dependencies are installed in the venv."""
        required_packages = ["psycopg2", "dspy", "pytest", "ruff"]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        return len(missing_packages) == 0, missing_packages

    def activate_venv(self) -> bool:
        """Activate the virtual environment in the current process."""
        if not self.venv_exists():
            print(f"❌ Virtual environment not found at {self.venv_path}")
            return False

        if self.is_venv_active():
            print("✅ Virtual environment already active")
            return True

        # Update environment variables to use venv
        os.environ["VIRTUAL_ENV"] = str(self.venv_path)
        os.environ["PATH"] = f"{self.venv_path}/bin:{os.environ.get('PATH', '')}"

        # Update sys.path to include venv site-packages
        venv_site_packages = (
            self.venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        )
        if venv_site_packages.exists():
            sys.path.insert(0, str(venv_site_packages))

        print(f"✅ Activated virtual environment: {self.venv_path}")
        return True

    def run_in_venv(self, command: list[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command using the venv Python."""
        if not self.venv_exists():
            raise RuntimeError(f"Virtual environment not found at {self.venv_path}")

        # Use venv Python for the command
        venv_command = [str(self.venv_python)] + command

        if capture_output:
            return subprocess.run(venv_command, capture_output=True, text=True, cwd=self.project_root)
        else:
            return subprocess.run(venv_command, cwd=self.project_root)

    def ensure_venv_active(self) -> bool:
        """Ensure the virtual environment is active and working."""
        print("🔧 Checking virtual environment...")

        # Check if venv exists
        if not self.venv_exists():
            print(f"❌ Virtual environment not found at {self.venv_path}")
            print("💡 Create it with: python3 -m venv venv")
            return False

        # Try to activate if not already active
        if not self.is_venv_active():
            if not self.activate_venv():
                return False

        # Validate dependencies
        deps_ok, missing = self.validate_dependencies()
        if not deps_ok:
            print(f"❌ Missing dependencies: {', '.join(missing)}")
            print("💡 Install with: source venv/bin/activate && pip install -r requirements.txt")
            return False

        print("✅ Virtual environment is active and ready")
        return True

    def get_venv_info(self) -> dict:
        """Get information about the virtual environment."""
        return {
            "venv_path": str(self.venv_path),
            "venv_exists": self.venv_exists(),
            "is_active": self.is_venv_active(),
            "python_path": str(self.get_venv_python_path()),
            "sys_prefix": sys.prefix,
            "virtual_env": os.environ.get("VIRTUAL_ENV"),
            "dependencies_ok": self.validate_dependencies()[0],
        }


def ensure_venv_for_script() -> bool:
    """Convenience function to ensure venv is active for script execution."""
    manager = VenvManager()
    return manager.ensure_venv_active()


def get_venv_python() -> Optional[str]:
    """Get the path to the venv Python executable."""
    manager = VenvManager()
    python_path = manager.get_venv_python_path()
    return str(python_path) if python_path else None


if __name__ == "__main__":
    # CLI interface for venv management
    import argparse

    parser = argparse.ArgumentParser(description="Virtual Environment Manager")
    parser.add_argument("--check", action="store_true", help="Check venv status")
    parser.add_argument("--activate", action="store_true", help="Activate venv")
    parser.add_argument("--info", action="store_true", help="Show venv information")
    parser.add_argument("--validate", action="store_true", help="Validate dependencies")

    args = parser.parse_args()

    manager = VenvManager()

    if args.check:
        if manager.ensure_venv_active():
            print("✅ Virtual environment is ready")
            sys.exit(0)
        else:
            print("❌ Virtual environment issues found")
            sys.exit(1)

    elif args.activate:
        if manager.activate_venv():
            print("✅ Virtual environment activated")
            sys.exit(0)
        else:
            print("❌ Failed to activate virtual environment")
            sys.exit(1)

    elif args.info:
        info = manager.get_venv_info()
        for key, value in info.items():
            print(f"{key}: {value}")

    elif args.validate:
        deps_ok, missing = manager.validate_dependencies()
        if deps_ok:
            print("✅ All dependencies are available")
            sys.exit(0)
        else:
            print(f"❌ Missing dependencies: {', '.join(missing)}")
            sys.exit(1)

    else:
        parser.print_help()
