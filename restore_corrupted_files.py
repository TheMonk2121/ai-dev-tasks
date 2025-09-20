#!/usr/bin/env python3
"""
Restore corrupted files from git history.

This script identifies corrupted files and restores them from a clean commit
before the corruption occurred.
"""

import subprocess
import sys
from pathlib import Path


def get_corrupted_files():
    """Get list of files with syntax errors."""
    try:
        result = subprocess.run(
            ["uv", "run", "ruff", "check", ".", "2>&1"],
            capture_output=True,
            text=True,
            shell=True
        )
        
        corrupted_files = []
        lines = result.stderr.split('\n')
        
        for line in lines:
            if '-->' in line and '.py:' in line:
                # Extract file path
                file_path = line.split('-->')[1].split(':')[0].strip()
                # Remove ANSI escape codes
                file_path = file_path.replace('\x1b[94m', '').replace('\x1b[0m', '')
                if file_path and file_path not in corrupted_files:
                    corrupted_files.append(file_path)
        
        return corrupted_files
    except Exception as e:
        print(f"Error getting corrupted files: {e}")
        return []


def find_clean_commit(file_path):
    """Find a clean commit for a specific file."""
    try:
        # Get commit history for the file
        result = subprocess.run(
            ["git", "log", "--oneline", "--follow", "--", file_path],
            capture_output=True,
            text=True
        )
        
        commits = result.stdout.strip().split('\n')
        
        # Look for commits that don't mention corruption
        for commit in commits:
            if not any(word in commit.lower() for word in ['corrupt', 'fix', 'artifact', 'syntax']):
                commit_hash = commit.split()[0]
                return commit_hash
        
        # Fallback to first commit
        if commits:
            return commits[0].split()[0]
        
        return None
    except Exception as e:
        print(f"Error finding clean commit for {file_path}: {e}")
        return None


def restore_file(file_path, commit_hash):
    """Restore a file from a specific commit."""
    try:
        # Check if file exists in the commit
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:{file_path}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # File exists, restore it
            subprocess.run(
                ["git", "checkout", commit_hash, "--", file_path],
                check=True
            )
            print(f"✅ Restored {file_path} from {commit_hash}")
            return True
        else:
            print(f"❌ File {file_path} not found in commit {commit_hash}")
            return False
    except Exception as e:
        print(f"Error restoring {file_path}: {e}")
        return False


def main():
    """Main restoration process."""
    print("🔍 Finding corrupted files...")
    corrupted_files = get_corrupted_files()
    
    if not corrupted_files:
        print("✅ No corrupted files found!")
        return
    
    print(f"📊 Found {len(corrupted_files)} corrupted files")
    
    # Focus on critical files first
    critical_patterns = [
        "evaluation",
        "scripts",
        "src",
        "tests"
    ]
    
    critical_files = []
    other_files = []
    
    for file_path in corrupted_files:
        if any(pattern in file_path for pattern in critical_patterns):
            critical_files.append(file_path)
        else:
            other_files.append(file_path)
    
    print(f"🎯 Critical files: {len(critical_files)}")
    print(f"📁 Other files: {len(other_files)}")
    
    # Restore critical files first
    restored_count = 0
    for file_path in critical_files[:10]:  # Limit to first 10 for now
        print(f"\n🔧 Restoring {file_path}...")
        commit_hash = find_clean_commit(file_path)
        
        if commit_hash:
            if restore_file(file_path, commit_hash):
                restored_count += 1
        else:
            print(f"❌ No clean commit found for {file_path}")
    
    print(f"\n✅ Restored {restored_count} critical files")
    print("💡 Run 'uv run ruff check .' to verify restoration")


if __name__ == "__main__":
    main()
