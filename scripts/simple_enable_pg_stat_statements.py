#!/usr/bin/env python3
"""
Simple script to enable pg_stat_statements extension
"""

import subprocess
import sys

import psycopg2


def check_and_enable():
    """Check if pg_stat_statements is working, if not provide instructions."""
    print("🔍 Checking pg_stat_statements status...")

    # First check if it's already working
    try:
        with psycopg2.connect("postgresql://danieljacobs@localhost:5432/ai_agency") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM pg_stat_statements LIMIT 1;")
                count = cur.fetchone()[0]
                print(f"✅ pg_stat_statements is already working! Found {count} statements")
                return True
    except Exception as e:
        print(f"❌ pg_stat_statements not working: {e}")

    # Try to create extension
    print("🔧 Attempting to create extension...")
    try:
        with psycopg2.connect("postgresql://danieljacobs@localhost:5432/ai_agency") as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
                conn.commit()
                print("✅ Created pg_stat_statements extension")

                # Test again
                cur.execute("SELECT COUNT(*) FROM pg_stat_statements LIMIT 1;")
                count = cur.fetchone()[0]
                print(f"✅ pg_stat_statements is now working! Found {count} statements")
                return True
    except Exception as e:
        print(f"❌ Error creating extension: {e}")

    # Get PostgreSQL config file location
    print("🔍 Finding PostgreSQL configuration...")
    try:
        result = subprocess.run(["psql", "-d", "ai_agency", "-c", "SHOW config_file;"], capture_output=True, text=True)
        if result.returncode == 0:
            config_file = result.stdout.strip().split("\n")[2].strip()
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


def main():
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
