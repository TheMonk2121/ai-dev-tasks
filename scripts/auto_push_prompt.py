#!/usr/bin/env python3
"""
Auto-Push Prompt for Repo Maintenance (B-052-e)

Interactive prompt to push changes to GitHub after maintenance operations.
Provides git status check, user confirmation, and safety checks.

Usage:
    python3 scripts/auto_push_prompt.py [--force] [--message "custom message"]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_git_command(args: list[str], capture_output: bool = True) -> tuple[int, str, str]:
    """Run a git command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(["git"] + args, capture_output=capture_output, text=True, cwd=Path.cwd())
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def check_git_status() -> tuple[bool, str]:
    """Check git status and return if there are changes to commit"""
    exit_code, stdout, stderr = run_git_command(["status", "--porcelain"])

    if exit_code != 0:
        return False, f"Error checking git status: {stderr}"

    # Check if there are any changes
    changes = [line for line in stdout.split("\n") if line.strip()]

    if not changes:
        return False, "No changes to commit"

    return True, stdout


def get_staged_files() -> list[str]:
    """Get list of staged files"""
    exit_code, stdout, stderr = run_git_command(["diff", "--cached", "--name-only"])

    if exit_code != 0:
        return []

    return [line.strip() for line in stdout.split("\n") if line.strip()]


def get_unstaged_files() -> list[str]:
    """Get list of unstaged files"""
    exit_code, stdout, stderr = run_git_command(["diff", "--name-only"])

    if exit_code != 0:
        return []

    return [line.strip() for line in stdout.split("\n") if line.strip()]


def get_untracked_files() -> list[str]:
    """Get list of untracked files"""
    exit_code, stdout, stderr = run_git_command(["ls-files", "--others", "--exclude-standard"])

    if exit_code != 0:
        return []

    return [line.strip() for line in stdout.split("\n") if line.strip()]


def stage_all_changes() -> bool:
    """Stage all changes (modified, deleted, untracked files)"""
    print("📦 Staging all changes...")

    # Add all changes
    exit_code, stdout, stderr = run_git_command(["add", "."])
    if exit_code != 0:
        print(f"❌ Error staging changes: {stderr}")
        return False

    return True


def commit_changes(message: str) -> bool:
    """Commit staged changes with the given message"""
    print(f"💾 Committing changes: {message}")

    exit_code, stdout, stderr = run_git_command(["commit", "-m", message])
    if exit_code != 0:
        print(f"❌ Error committing changes: {stderr}")
        return False

    print("✅ Changes committed successfully")
    return True


def push_changes() -> bool:
    """Push changes to remote repository"""
    print("🚀 Pushing changes to remote...")

    # Get current branch
    exit_code, stdout, stderr = run_git_command(["branch", "--show-current"])
    if exit_code != 0:
        print(f"❌ Error getting current branch: {stderr}")
        return False

    current_branch = stdout.strip()

    # Push to remote
    exit_code, stdout, stderr = run_git_command(["push", "origin", current_branch])
    if exit_code != 0:
        print(f"❌ Error pushing changes: {stderr}")
        return False

    print(f"✅ Changes pushed to {current_branch}")
    return True


def get_commit_message() -> str:
    """Get commit message from user or use default"""
    print("\n📝 Enter commit message (or press Enter for default):")
    print("   Default: 'Auto-push: Maintenance updates'")

    message = input("   Message: ").strip()

    if not message:
        message = "Auto-push: Maintenance updates"

    return message


def confirm_push(changes_summary: str) -> bool:
    """Get user confirmation to push changes"""
    print("\n" + "=" * 60)
    print("🚀 AUTO-PUSH CONFIRMATION")
    print("=" * 60)
    print(changes_summary)
    print("=" * 60)

    while True:
        response = input("\n❓ Push these changes to GitHub? (y/N): ").strip().lower()

        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no", ""]:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")


def display_changes_summary() -> str:
    """Display a summary of changes to be committed"""
    staged = get_staged_files()
    unstaged = get_unstaged_files()
    untracked = get_untracked_files()

    summary = []
    summary.append("📋 CHANGES TO BE COMMITTED:")
    summary.append("")

    if staged:
        summary.append("✅ Staged files:")
        for file in staged[:10]:  # Show first 10
            summary.append(f"   + {file}")
        if len(staged) > 10:
            summary.append(f"   ... and {len(staged) - 10} more")
        summary.append("")

    if unstaged:
        summary.append("📝 Modified files (will be staged):")
        for file in unstaged[:10]:  # Show first 10
            summary.append(f"   ~ {file}")
        if len(unstaged) > 10:
            summary.append(f"   ... and {len(unstaged) - 10} more")
        summary.append("")

    if untracked:
        summary.append("🆕 New files (will be staged):")
        for file in untracked[:10]:  # Show first 10
            summary.append(f"   + {file}")
        if len(untracked) > 10:
            summary.append(f"   ... and {len(untracked) - 10} more")
        summary.append("")

    if not staged and not unstaged and not untracked:
        summary.append("ℹ️  No changes detected")

    return "\n".join(summary)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Auto-Push Prompt for Repo Maintenance")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--message", type=str, help="Custom commit message")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")

    args = parser.parse_args()

    print("🔍 Auto-Push Prompt for Repo Maintenance")
    print("=" * 50)

    # Check if we're in a git repository
    exit_code, stdout, stderr = run_git_command(["rev-parse", "--git-dir"])
    if exit_code != 0:
        print("❌ Not in a git repository")
        sys.exit(1)

    # Check git status
    has_changes, status_output = check_git_status()

    if not has_changes:
        print("✅ No changes to commit")
        return

    # Display changes summary
    changes_summary = display_changes_summary()
    print(changes_summary)

    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        return

    # Get commit message
    commit_message = args.message if args.message else get_commit_message()

    # Stage all changes
    if not stage_all_changes():
        sys.exit(1)

    # Get updated summary after staging
    changes_summary = display_changes_summary()

    # Confirm push (unless --force)
    if not args.force:
        if not confirm_push(changes_summary):
            print("❌ Push cancelled by user")
            sys.exit(0)

    # Commit changes
    if not commit_changes(commit_message):
        sys.exit(1)

    # Push changes
    if not push_changes():
        sys.exit(1)

    print("\n🎉 Auto-push completed successfully!")
    print("✅ Changes have been committed and pushed to GitHub")


if __name__ == "__main__":
    main()
