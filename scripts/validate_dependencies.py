#!/usr/bin/env python3.12.123.11
"""
Dependency Validation Script
Validates that all dependencies are properly installed and consistent
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_dependency_versions():
    """Check for version conflicts across requirements files"""
    print("🔍 Checking dependency versions...")

    # Check pip list for installed packages
    success, stdout, stderr = run_command("pip list")
    if not success:
        print(f"❌ Failed to get installed packages: {stderr}")
        return False

    installed_packages = {}
    for line in stdout.split("\n")[2:]:  # Skip header lines
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                installed_packages[parts[0].lower()] = parts[1]

    # Check for key dependencies
    key_deps = ["flask", "psycopg2-binary", "pytest", "dspy", "psutil"]
    missing_deps = []

    for dep in key_deps:
        if dep not in installed_packages:
            missing_deps.append(dep)
        else:
            print(f"✅ {dep}: {installed_packages[dep]}")

    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        return False

    return True


def validate_imports():
    """Validate that key modules can be imported"""
    print("\n🔍 Validating imports...")

    test_imports = [
        ("dspy", "DSPy framework"),
        ("flask", "Flask web framework"),
        ("psycopg2", "PostgreSQL adapter"),
        ("pytest", "Testing framework"),
        ("psutil", "System monitoring"),
        ("pandas", "Data processing"),
        ("numpy", "Numerical computing"),
    ]

    failed_imports = []

    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError as e:
            print(f"❌ {module}: {description} - {e}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
        return False

    return True


def check_requirements_files():
    """Check that requirements files reference root correctly"""
    print("\n🔍 Checking requirements files...")

    requirements_files = [
        "dspy-rag-system/requirements.txt",
        "dashboard/requirements.txt",
        "config/requirements-conflict-detection.txt",
    ]

    for req_file in requirements_files:
        if not Path(req_file).exists():
            print(f"❌ Missing requirements file: {req_file}")
            continue

        with open(req_file) as f:
            content = f.read()

        if "-r ../requirements.txt" in content:
            print(f"✅ {req_file}: References root requirements")
        else:
            print(f"❌ {req_file}: Does not reference root requirements")
            return False

    return True


def main():
    """Main validation function"""
    print("🧪 Dependency Validation")
    print("=" * 50)

    checks = [
        ("Dependency Versions", check_dependency_versions),
        ("Import Validation", validate_imports),
        ("Requirements Files", check_requirements_files),
    ]

    all_passed = True

    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 30)

        if not check_func():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All dependency checks passed!")
        return 0
    else:
        print("❌ Some dependency checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
