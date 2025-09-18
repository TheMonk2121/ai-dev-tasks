from __future__ import annotations

import os
import subprocess
import sys
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config

#!/usr/bin/env python3
"""
Simple script to enable pg_stat_statements extension
"""

def check_and_enable() -> bool:
    """Check if pg_stat_statements is working, if not provide instructions."""
    print("🔍 Checking pg_stat_statements status...")

    # First check if it's already working
    try:
        with Psycopg3Config.get_cursor("default") as cur:
            _ = cur.execute("SELECT COUNT(*) FROM pg_stat_statements LIMIT 1;")
            initial_result: Any = cur.fetchone()
            if initial_result is not None:
                count = initial_result[0]
                print(f"✅ pg_stat_statements is already working! Found {count} statements")
                return True
            else:
                print("❌ No results from pg_stat_statements query")
    except Exception as e:
        print(f"❌ pg_stat_statements not working: {e}")

    # Try to create extension
    print("🔧 Attempting to create extension...")
    try:
        with Psycopg3Config.get_cursor("default") as cur:
            _ = cur.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
            # Get connection from cursor to commit
            conn = cur.connection
            conn.commit()
            print("✅ Created pg_stat_statements extension")

            # Test again
            _ = cur.execute("SELECT COUNT(*) FROM pg_stat_statements LIMIT 1;")
            test_result: Any = cur.fetchone()
            if test_result is not None:
                count = test_result[0]
                print(f"✅ pg_stat_statements is now working! Found {count} statements")
                return True
            else:
                print("❌ No results from pg_stat_statements query after creation")
    except Exception as e:
        print(f"❌ Error creating extension: {e}")

    # Get PostgreSQL config file location
    print("🔍 Finding PostgreSQL configuration...")
    try:
        config_result: Any = subprocess.run(["psql", "-d", "ai_agency", "-c", "SHOW config_file;"], capture_output=True, text=True)
        if config_result.returncode == 0:
            config_file = config_result.stdout.strip().split("\n")[2].strip()
            print(f"📁 Config file: {config_file}")
        else:
            print("❌ Could not find config file")
    except Exception as e:
        print(f"❌ Error finding config: {e}")

    print("\n🔧 Manual setup required:")
    print("1. Edit postgresql.conf and add to shared_preload_libraries:")
    print("   shared_preload_libraries = 'pg_stat_statements'")
    print("2. Restart PostgreSQL:")
    print("   brew services restart postgresql")
    print("3. Run this script again")

    return False

def main() -> int:
    """Main function."""
    print("🔍 pg_stat_statements Setup")
    print("=" * 50)

    if check_and_enable():
        print("\n🎉 pg_stat_statements is ready for performance monitoring!")
        return 0
    else:
        print("\n❌ Manual setup required")
        return 1

if __name__ == "__main__":
    sys.exit(main())
