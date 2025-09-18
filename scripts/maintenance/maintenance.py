from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config

#!/usr/bin/env python3
"""
System Maintenance for AI Development Tasks
"""

def run_health_check() -> Any:
    """Run system health check"""
    print("🔍 Running health check...")
    try:
        result: Any = subprocess.run(["./scripts/system_monitor.py"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def run_database_maintenance() -> Any:
    """Run database maintenance"""
    print("🗄️ Running database maintenance...")
    try:

        with Psycopg3Config.get_cursor("default") as cursor:
            cursor.execute("ANALYZE documents")
            cursor.execute("ANALYZE document_chunks")
            cursor.execute("ANALYZE conversation_memory")
        print("✅ Database maintenance completed")
        return True
    except Exception as e:
        print(f"❌ Database maintenance error: {e}")
        return False

def run_memory_validation() -> Any:
    """Validate memory system"""
    print("🧠 Validating memory system...")
    try:
        result = subprocess.run(
            ["./scripts/memory_up.sh", "-r", "planner", "-q", "maintenance"], capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            print("✅ Memory system validation passed")
            return True
        else:
            print("❌ Memory system validation failed")
            return False
    except Exception as e:
        print(f"❌ Memory validation error: {e}")
        return False

def main() -> Any:
    """Main maintenance function"""
    print("🔧 AI Development Tasks - System Maintenance")
    print("=" * 50)
    print(f"Started: {datetime.now()}")
    print()

    tasks = [
        ("Health Check", run_health_check),
        ("Database Maintenance", run_database_maintenance),
        ("Memory Validation", run_memory_validation),
    ]

    passed = 0
    total = len(tasks)

    for task_name, task_func in tasks:
        if task_func():
            passed += 1

    print()
    print("=" * 50)
    print(f"Maintenance completed: {passed}/{total} tasks passed")
    print(f"Finished: {datetime.now()}")

if __name__ == "__main__":
    main()
