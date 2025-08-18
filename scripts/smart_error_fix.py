#!/usr/bin/env python3.12
"""
Smart Error Fix Script - Implements refined auto-fix strategy based on testing.

This script uses our decision matrix to safely apply auto-fixes only to proven-safe error types.
"""

import subprocess
import sys

# Decision matrix based on our testing
SAFE_AUTO_FIXES = {
    "F401": "Unused imports - Safe to auto-fix",
    "I001": "Import formatting - Safe to auto-fix",
    "F541": "F-string issues - Safe to auto-fix",
    "RUF001": "Unicode characters - Use custom script",
}

DANGEROUS_AUTO_FIXES = {
    "PT009": "Unittest assertions - Manual inspection required",
    "B007": "Loop variables - Manual inspection required",
    "RUF013": "Implicit Optional - Manual inspection required",
    "F841": "Unused variables - Manual inspection required",
    "RUF010": "F-string conversion - Manual inspection required",
    "SIM117": "Nested with statements - Auto-fix doesn't work",
    "SIM102": "Nested if statements - Auto-fix doesn't work",
}


def run_ruff_check(
    target_paths: list[str], select: str | None = None
) -> tuple[int, str]:
    """Run ruff check and return error count and output."""
    cmd = ["ruff", "check"]
    if select:
        cmd.extend(["--select", select])
    cmd.extend(target_paths)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        # Count actual errors by looking for error codes in output
        if result.stdout.strip():
            # Count lines that contain error codes (e.g., "F401", "PT009")
            # Look for lines that contain ":ERROR_CODE " pattern
            error_count = 0
            for line in result.stdout.split("\n"):
                for error_type in SAFE_AUTO_FIXES | DANGEROUS_AUTO_FIXES:
                    if f":{error_type} " in line or f" {error_type} " in line:
                        error_count += 1
                        break  # Only count each line once
        else:
            error_count = 0
        return error_count, result.stdout
    except Exception as e:
        print(f"Error running ruff check: {e}")
        return 0, ""


def get_error_counts(target_paths: list[str]) -> dict[str, int]:
    """Get error counts for all error types."""
    error_counts = {}

    # Check safe auto-fixes
    for error_type in SAFE_AUTO_FIXES:
        count, _ = run_ruff_check(target_paths, error_type)
        if count > 0:
            error_counts[error_type] = count

    # Check dangerous auto-fixes
    for error_type in DANGEROUS_AUTO_FIXES:
        count, _ = run_ruff_check(target_paths, error_type)
        if count > 0:
            error_counts[error_type] = count

    return error_counts


def apply_safe_auto_fixes(target_paths: list[str], error_type: str) -> bool:
    """Apply auto-fix for a safe error type."""
    print(f"🔧 Applying safe auto-fix for {error_type}...")

    cmd = ["ruff", "check", "--select", error_type, "--fix"]
    if error_type in ["B007", "RUF013", "F841"]:
        cmd.append("--unsafe-fixes")
    cmd.extend(target_paths)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"OK Successfully applied auto-fix for {error_type}")
            return True
        else:
            print(f"X Auto-fix failed for {error_type}: {result.stderr}")
            return False
    except Exception as e:
        print(f"X Error applying auto-fix for {error_type}: {e}")
        return False


def apply_unicode_fix(target_paths: list[str]) -> bool:
    """Apply custom Unicode fix script."""
    print("🔧 Applying custom Unicode fix...")

    try:
        result = subprocess.run(
            ["python3.12", "scripts/fix_unicode_characters.py"] + target_paths,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print("OK Successfully applied Unicode fix")
            return True
        else:
            print(f"X Unicode fix failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"X Error applying Unicode fix: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3.12 scripts/smart_error_fix.py <target_paths...>")
        print(
            "Example: python3.12 scripts/smart_error_fix.py scripts/ dspy-rag-system/ tests/"
        )
        sys.exit(1)

    target_paths = sys.argv[1:]

    print("🔍 Smart Error Fix - Using Refined Strategy")
    print("=" * 50)

    # Get current error counts
    print("📊 Analyzing current error counts...")
    error_counts = get_error_counts(target_paths)

    if not error_counts:
        print("OK No errors found!")
        return

    print("\n📈 Current Error Counts:")
    for error_type, count in sorted(
        error_counts.items(), key=lambda x: x[1], reverse=True
    ):
        status = "OK SAFE" if error_type in SAFE_AUTO_FIXES else "X DANGEROUS"
        print(f"  {error_type}: {count} errors ({status})")

    # Apply safe auto-fixes
    print("\n🔧 Applying Safe Auto-Fixes:")
    safe_fixes_applied = 0

    for error_type in SAFE_AUTO_FIXES:
        if error_type in error_counts:
            if error_type == "RUF001":
                if apply_unicode_fix(target_paths):
                    safe_fixes_applied += 1
            else:
                if apply_safe_auto_fixes(target_paths, error_type):
                    safe_fixes_applied += 1

    # Report dangerous errors
    dangerous_errors = {
        k: v for k, v in error_counts.items() if k in DANGEROUS_AUTO_FIXES
    }
    if dangerous_errors:
        print("\n!️  Dangerous Errors (Manual Inspection Required):")
        for error_type, count in dangerous_errors.items():
            print(
                f"  {error_type}: {count} errors - {DANGEROUS_AUTO_FIXES[error_type]}"
            )

    # Final summary
    print("\n🎉 Summary:")
    print(f"  Safe fixes applied: {safe_fixes_applied}")
    print(f"  Dangerous errors remaining: {len(dangerous_errors)}")

    if dangerous_errors:
        print("\n💡 Next Steps:")
        print("  - Manual inspection required for dangerous error types")
        print("  - Consider if these errors are actually problematic")
        print("  - Focus on high-impact errors first")


if __name__ == "__main__":
    main()
