#!/usr/bin/env python3
"""
Virtual Environment Mapping Verification

This script verifies that all UV tools and scripts properly map to the new .venv environment.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[bool, str, str]:
    """Run a command and return success, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def verify_environment():
    """Verify the virtual environment is properly configured."""
    print("🔍 Verifying Virtual Environment Configuration...")

    # Check VIRTUAL_ENV
    venv_path = os.environ.get("VIRTUAL_ENV")
    if not venv_path:
        print("❌ VIRTUAL_ENV not set")
        return False

    if not venv_path.endswith(".venv"):
        print(f"❌ VIRTUAL_ENV doesn't point to .venv: {venv_path}")
        return False

    print(f"✅ VIRTUAL_ENV correctly set to: {venv_path}")

    # Check Python executable
    python_path = sys.executable
    if not python_path.startswith(venv_path):
        print(f"❌ Python not in virtual environment: {python_path}")
        return False

    print(f"✅ Python executable in venv: {python_path}")

    # Check UV installation
    success, stdout, stderr = run_command(["uv", "--version"])
    if not success:
        print(f"❌ UV not available: {stderr}")
        return False

    print(f"✅ UV available: {stdout.strip()}")

    return True


def verify_uv_commands():
    """Verify UV commands work correctly with the virtual environment."""
    print("\n🔍 Verifying UV Commands...")

    # Test uv run
    success, stdout, stderr = run_command(["uv", "run", "python", "-c", "import sys; print(sys.executable)"])
    if not success:
        print(f"❌ uv run failed: {stderr}")
        return False

    python_path = stdout.strip()
    if not python_path.endswith(".venv/bin/python3"):
        print(f"❌ uv run not using .venv: {python_path}")
        return False

    print(f"✅ uv run uses correct Python: {python_path}")

    # Test uv sync
    success, stdout, stderr = run_command(["uv", "sync", "--dry-run"])
    if not success:
        print(f"❌ uv sync failed: {stderr}")
        return False

    print("✅ uv sync works correctly")

    return True


def verify_scripts():
    """Verify all generated scripts work correctly."""
    print("\n🔍 Verifying Generated Scripts...")

    scripts_to_test = [
        "scripts/uv_performance_monitor.py",
        "scripts/uv_dependency_manager.py",
        "scripts/uv_workflow_optimizer.py",
        "scripts/uv_team_onboarding.py",
        "scripts/uv_export_requirements.py",
    ]

    for script in scripts_to_test:
        if not Path(script).exists():
            print(f"❌ Script not found: {script}")
            continue

        # Test script with --help
        success, _, stderr = run_command(["python", script, "--help"])
        if not success:
            print(f"❌ Script {script} failed: {stderr}")
            continue

        print(f"✅ Script {script} works correctly")

    return True


def verify_shell_aliases():
    """Verify shell aliases are properly configured."""
    print("\n🔍 Verifying Shell Aliases...")

    aliases_file = Path("uv_aliases.sh")
    if not aliases_file.exists():
        print("❌ uv_aliases.sh not found")
        return False

    print("✅ uv_aliases.sh exists")

    # Check alias content
    content = aliases_file.read_text()
    expected_aliases = ["uvd", "uvt", "uvl", "uvf", "uvs", "uvp"]

    for alias in expected_aliases:
        if f"alias {alias}=" not in content:
            print(f"❌ Alias {alias} not found in uv_aliases.sh")
            return False

    print("✅ All expected aliases found in uv_aliases.sh")

    return True


def verify_generated_scripts():
    """Verify generated workflow scripts."""
    print("\n🔍 Verifying Generated Workflow Scripts...")

    scripts_to_check = [
        "scripts/dev_setup.sh",
        "scripts/quick_test.sh",
        "scripts/perf_check.sh",
        "scripts/daily_maintenance.py",
        "scripts/weekly_optimization.py",
    ]

    for script in scripts_to_check:
        if not Path(script).exists():
            print(f"❌ Generated script not found: {script}")
            continue

        if not os.access(script, os.X_OK):
            print(f"❌ Generated script not executable: {script}")
            continue

        print(f"✅ Generated script {script} exists and is executable")

    return True


def verify_dependencies():
    """Verify key dependencies are available in the virtual environment."""
    print("\n🔍 Verifying Key Dependencies...")

    key_packages = ["dspy", "torch", "psycopg", "pytest", "black", "ruff"]

    for package in key_packages:
        success, _, stderr = run_command(
            ["uv", "run", "python", "-c", f"import {package}; print('{package} available')"]
        )
        if not success:
            print(f"❌ Package {package} not available: {stderr}")
            continue

        print(f"✅ Package {package} available")

    return True


def main():
    """Main verification function."""
    print("🚀 UV Virtual Environment Mapping Verification")
    print("=" * 60)

    checks = [
        ("Environment Configuration", verify_environment),
        ("UV Commands", verify_uv_commands),
        ("Scripts", verify_scripts),
        ("Shell Aliases", verify_shell_aliases),
        ("Generated Scripts", verify_generated_scripts),
        ("Dependencies", verify_dependencies),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1

    print(f"\n🎯 Results: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All checks passed! Virtual environment mapping is correct.")
        return 0
    else:
        print("⚠️ Some checks failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
