#!/usr/bin/env python3
"""
Agent Evaluation System Onboarding
Quick setup and verification for new agents
"""

import subprocess
from pathlib import Path


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"🎯 {title}")
    print(f"{'=' * 60}")


def check_evaluation_system():
    """Check if evaluation system is properly set up."""
    print_header("Evaluation System Check")

    # Check critical files
    critical_files = [
        "000_core/000_evaluation-system-entry-point.md",
        "configs/stable_bedrock.env",
        "throttle_free_eval.sh",
        "scripts/ragchecker_official_evaluation.py",
        "scripts/run_ragchecker_smoke_test.sh",
    ]

    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")

    if missing_files:
        print("\n❌ Missing critical files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False

    print("\n✅ All critical files present")
    return True


def check_aws_credentials():
    """Check AWS credentials configuration."""
    print_header("AWS Credentials Check")

    try:
        subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, text=True, check=True)
        print("✅ AWS credentials configured")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ AWS credentials not configured")
        print("💡 Run: aws configure")
        return False


def show_standard_commands():
    """Show standard evaluation commands."""
    print_header("Standard Evaluation Commands")

    print("🔒 Standard Evaluation (run every time):")
    print("   source throttle_free_eval.sh")
    print("   python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable")

    print("\n💨 Fast Testing:")
    print("   ./scripts/run_ragchecker_smoke_test.sh")

    print("\n🔧 Version New Baseline:")
    print("   python3 scripts/baseline_version_manager.py --full-setup")


def show_verification_checklist():
    """Show verification checklist."""
    print_header("Verification Checklist")

    checklist = [
        "configs/stable_bedrock.env exists",
        "Using --stable flag",
        "Banner shows lock status",
        "No throttling in previous runs",
        "AWS credentials configured",
    ]

    for item in checklist:
        print(f"□ {item}")


def show_troubleshooting():
    """Show common troubleshooting steps."""
    print_header("Troubleshooting")

    print("❌ 'Stable config not found':")
    print("   cp configs/stable_bedrock.env.template configs/stable_bedrock.env")

    print("\n❌ Throttling errors:")
    print("   # Edit configs/stable_bedrock.env")
    print("   export BEDROCK_MAX_RPS=0.06  # Reduce from 0.15")
    print("   export BEDROCK_COOLDOWN_SEC=45  # Increase from 30")

    print("\n❌ AWS credentials issues:")
    print("   aws configure  # Set up credentials")
    print("   python3 scripts/bedrock_connection_test.py  # Test connection")


def main():
    """Main onboarding function."""
    print("🤖 Agent Evaluation System Onboarding")
    print("=====================================")

    # Check system
    system_ok = check_evaluation_system()
    aws_ok = check_aws_credentials()

    # Show commands and guidance
    show_standard_commands()
    show_verification_checklist()
    show_troubleshooting()

    # Summary
    print_header("Onboarding Summary")

    if system_ok and aws_ok:
        print("🎉 Evaluation system ready!")
        print("📋 Next steps:")
        print("   1. Run standard evaluation command")
        print("   2. Verify banner shows lock status")
        print("   3. Check results in metrics/baseline_evaluations/")
    else:
        print("⚠️  Setup required:")
        if not system_ok:
            print("   - Fix missing files")
        if not aws_ok:
            print("   - Configure AWS credentials")

    print("\n📚 Documentation:")
    print("   - Entry Point: 000_core/000_evaluation-system-entry-point.md")
    print("   - Complete SOP: 400_guides/400_canonical-evaluation-sop.md")
    print("   - Memory Context: 100_memory/100_cursor-memory-context.md")


if __name__ == "__main__":
    main()
