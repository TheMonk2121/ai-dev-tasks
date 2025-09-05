#!/usr/bin/env python3
"""
Daily UV Maintenance Script

Automated daily maintenance tasks for UV environment.
"""

import subprocess
import sys
from datetime import datetime

def run_daily_maintenance():
    """Run daily maintenance tasks."""
    print(f"🔧 Daily UV Maintenance - {datetime.now().strftime('%Y-%m-%d')}")
    
    tasks = [
        ("Check for outdated packages", ["uv", "pip", "list", "--outdated"]),
        ("Update lock file", ["uv", "lock"]),
        ("Run security scan", ["python", "scripts/uv_dependency_manager.py", "--security"]),
        ("Performance check", ["python", "scripts/uv_performance_monitor.py"])
    ]
    
    for task_name, cmd in tasks:
        print(f"\n📋 {task_name}...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ {task_name} completed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ {task_name} failed: {e}")

if __name__ == "__main__":
    run_daily_maintenance()
