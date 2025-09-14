from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
UV Team Onboarding Automation

This script automates the UV setup process for new team members,
including installation, environment setup, and verification.
"""

class UVTeamOnboarding:
    """Automate UV setup for new team members."""

    def __init__(self):
        self.system_info = self._get_system_info()
        self.setup_log = []

    def _get_system_info(self) -> dict:
        """Get system information for platform-specific setup."""
        return {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "shell": self._detect_shell(),
        }

    def _detect_shell(self) -> str:
        """Detect the user's shell."""
        shell = Path.cwd() / "SHELL"
        if shell.exists():
            return shell.read_text().strip()

        # Fallback detection

        return os.environ.get("SHELL", "bash")

    def _log_step(self, step: str, success: bool, details: str = ""):
        """Log a setup step."""
        self.setup_log.append(
            {
                "step": step,
                "success": success,
                "details": details,
                "timestamp": subprocess.run(["date"], capture_output=True, text=True).stdout.strip(),
            }
        )

        status = "✅" if success else "❌"
        print(f"{status} {step}")
        if details:
            print(f"   {details}")

    def check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        print("🔍 Checking prerequisites...")

        # Check Python version
        python_version = self.system_info["python_version"]
        major, minor = map(int, python_version.split(".")[:2])

        if major < 3 or (major == 3 and minor < 8):
            self._log_step("Python version check", False, f"Python {python_version} detected. UV requires Python 3.8+")
            return False
        else:
            self._log_step("Python version check", True, f"Python {python_version} is compatible")

        # Check if UV is already installed
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
            self._log_step("UV installation check", True, f"UV already installed: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._log_step("UV installation check", False, "UV not found, will install")
            return False

    def install_uv(self) -> bool:
        """Install UV package manager."""
        print("📦 Installing UV...")

        try:
            # Use the official UV installer

            # For Windows, we'd need a different approach
            if self.system_info["platform"] == "Windows":
                self._log_step(
                    "UV installation", False, "Windows installation not automated. Please install UV manually."
                )
                return False

            # Run the installer
            subprocess.run(
                "curl -LsSf https://astral.sh/uv/install.sh | sh",
                shell=True,
                capture_output=True,
                text=True,
                check=True,
            )

            self._log_step("UV installation", True, "UV installed successfully")

            # Add UV to PATH
            self._setup_path()

            return True

        except subprocess.CalledProcessError as e:
            self._log_step("UV installation", False, f"Installation failed: {e.stderr}")
            return False

    def _setup_path(self):
        """Setup PATH for UV."""
        print("🔧 Setting up PATH...")

        shell = self.system_info["shell"]
        uv_path = Path.home() / ".local" / "bin"

        if "bash" in shell:
            profile_file = Path.home() / ".bashrc"
        elif "zsh" in shell:
            profile_file = Path.home() / ".zshrc"
        else:
            profile_file = Path.home() / ".profile"

        # Check if UV path is already in profile
        if profile_file.exists():
            content = profile_file.read_text()
            if str(uv_path) not in content:
                # Add UV to PATH
                path_line = f'\nexport PATH="{uv_path}:$PATH"\n'
                profile_file.write_text(content + path_line)

                self._log_step("PATH setup", True, f"Added UV to PATH in {profile_file.name}")
            else:
                self._log_step("PATH setup", True, "UV already in PATH")
        else:
            self._log_step("PATH setup", False, f"Profile file {profile_file} not found")

    def setup_project_environment(self) -> bool:
        """Setup the project environment."""
        print("🏗️ Setting up project environment...")

        try:
            # Check if we're in the right directory
            if not Path("pyproject.toml").exists():
                self._log_step(
                    "Project directory check", False, "pyproject.toml not found. Please run from project root."
                )
                return False

            self._log_step("Project directory check", True, "Found pyproject.toml")

            # Create virtual environment
            subprocess.run(["uv", "venv", "--python", "3.12"], capture_output=True, text=True, check=True)

            self._log_step("Virtual environment creation", True, "Created .venv with Python 3.12")

            # Install dependencies
            subprocess.run(["uv", "sync", "--extra", "dev"], capture_output=True, text=True, check=True)

            self._log_step("Dependency installation", True, "Installed all dependencies with dev extras")

            return True

        except subprocess.CalledProcessError as e:
            self._log_step("Project environment setup", False, f"Setup failed: {e.stderr}")
            return False

    def verify_setup(self) -> bool:
        """Verify the setup is working correctly."""
        print("✅ Verifying setup...")

        try:
            # Test UV commands
            commands = [
                (["uv", "--version"], "UV version check"),
                (["uv", "run", "python", "--version"], "Python in UV environment"),
                (["uv", "run", "python", "-c", "import dspy; print('DSPy:', dspy.__version__)"], "DSPy import test"),
                (
                    ["uv", "run", "python", "-c", "import torch; print('PyTorch:', torch.__version__)"],
                    "PyTorch import test",
                ),
                (["uv", "run", "pre-commit", "--version"], "Pre-commit test"),
            ]

            all_passed = True
            for cmd, description in commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    self._log_step(description, True, result.stdout.strip())
                except subprocess.CalledProcessError as e:
                    self._log_step(description, False, f"Failed: {e.stderr}")
                    all_passed = False

            return all_passed

        except Exception as e:
            self._log_step("Setup verification", False, f"Verification failed: {e}")
            return False

    def create_development_guide(self):
        """Create a development guide for the team member."""
        print("📚 Creating development guide...")

        guide_content = f"""# 🚀 Development Setup Guide

## System Information
- **Platform**: {self.system_info['platform']}
- **Architecture**: {self.system_info['architecture']}
- **Python Version**: {self.system_info['python_version']}
- **Shell**: {self.system_info['shell']}

## UV Commands Quick Reference

### Basic Commands
```bash
# Activate environment
source .venv/bin/activate

# Install dependencies
uv sync --extra dev

# Run commands in environment
uv run python scripts/system_health_check.py
uv run pytest
uv run pre-commit run --all-files
```

### Development Workflow
```bash
# Add new dependencies
uv add package-name
uv add --dev package-name

# Update lock file
uv lock

# Run one-off tools
uvx black .
uvx ruff check .
uvx pytest tests/
```

### Performance Monitoring
```bash
# Monitor UV performance
python scripts/uv_performance_monitor.py

# Check available UVX tools
bash scripts/uvx_tools.sh

# Export requirements
python scripts/uv_export_requirements.py
```

## Troubleshooting

### Common Issues
1. **UV not found**: Run `source ~/.bashrc` or restart terminal
2. **Permission denied**: Check UV installation path permissions
3. **Dependency conflicts**: Run `uv lock` to update lock file

### Getting Help
- UV Documentation: https://docs.astral.sh/uv/
- Project README: README.md
- Performance Monitor: scripts/uv_performance_monitor.py

## Setup Log
"""

        # Add setup log to guide
        for entry in self.setup_log:
            status = "✅" if entry["success"] else "❌"
            guide_content += f"- {status} {entry['step']}\n"
            if entry["details"]:
                guide_content += f"  - {entry['details']}\n"

        # Write guide
        guide_file = Path("DEVELOPMENT_SETUP_GUIDE.md")
        guide_file.write_text(guide_content)

        self._log_step("Development guide creation", True, f"Created {guide_file}")

    def run_full_onboarding(self) -> bool:
        """Run the complete onboarding process."""
        print("🎯 Starting UV Team Onboarding...")
        print("=" * 50)

        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites check failed. Please resolve issues and try again.")
            return False

        # Install UV if needed
        try:
            subprocess.run(["uv", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            if not self.install_uv():
                print("\n❌ UV installation failed.")
                return False

        # Setup project environment
        if not self.setup_project_environment():
            print("\n❌ Project environment setup failed.")
            return False

        # Verify setup
        if not self.verify_setup():
            print("\n⚠️ Setup verification had issues. Check the log above.")

        # Create development guide
        self.create_development_guide()

        # Print summary
        print("\n" + "=" * 50)
        print("🎉 ONBOARDING COMPLETE!")
        print("=" * 50)

        successful_steps = sum(1 for entry in self.setup_log if entry["success"])
        total_steps = len(self.setup_log)

        print(f"✅ Successful steps: {successful_steps}/{total_steps}")
        print("📚 Development guide: DEVELOPMENT_SETUP_GUIDE.md")
        print("🔧 Next steps:")
        print("   1. Restart your terminal or run: source ~/.bashrc")
        print("   2. Activate environment: source .venv/bin/activate")
        print("   3. Run tests: uv run pytest")
        print("   4. Check performance: python scripts/uv_performance_monitor.py")

        return successful_steps == total_steps

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Automate UV setup for new team members")
    parser.add_argument("--check-only", action="store_true", help="Only check prerequisites")
    parser.add_argument("--install-only", action="store_true", help="Only install UV")
    parser.add_argument("--setup-only", action="store_true", help="Only setup project environment")
    parser.add_argument("--verify-only", action="store_true", help="Only verify setup")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    onboarding = UVTeamOnboarding()

    if args.check_only:
        success = onboarding.check_prerequisites()
        if args.json:
            print(json.dumps({"prerequisites_check": success, "system_info": onboarding.system_info}))
        sys.exit(0 if success else 1)

    elif args.install_only:
        success = onboarding.install_uv()
        if args.json:
            print(json.dumps({"uv_installation": success}))
        sys.exit(0 if success else 1)

    elif args.setup_only:
        success = onboarding.setup_project_environment()
        if args.json:
            print(json.dumps({"project_setup": success}))
        sys.exit(0 if success else 1)

    elif args.verify_only:
        success = onboarding.verify_setup()
        if args.json:
            print(json.dumps({"setup_verification": success}))
        sys.exit(0 if success else 1)

    else:
        # Full onboarding
        success = onboarding.run_full_onboarding()

        if args.json:
            print(
                json.dumps(
                    {
                        "onboarding_success": success,
                        "setup_log": onboarding.setup_log,
                        "system_info": onboarding.system_info,
                    }
                )
            )

        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()