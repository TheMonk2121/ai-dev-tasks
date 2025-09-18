from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import psycopg

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config

#!/usr/bin/env python3
"""
Enable pg_stat_statements extension for database performance monitoring
"""

def check_postgresql_config():
    """Check PostgreSQL configuration location."""
    try:
        # Try to find postgresql.conf
        result = subprocess.run(["psql", "-d", "ai_agency", "-c", "SHOW config_file;"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 3:
                config_file = lines[2].strip()
                return Path(config_file)
    except Exception as e:
        print(f"Error finding config file: {e}")

    # Common locations
    common_paths = [
        Path("/usr/local/var/postgresql.conf"),
        Path("/opt/homebrew/var/postgresql.conf"),
        Path("/usr/local/pgsql/data/postgresql.conf"),
        Path("/var/lib/postgresql/data/postgresql.conf"),
        Path("~/.local/share/postgresql/postgresql.conf").expanduser(),
    ]

    for path in common_paths:
        if path.exists():
            return path

    return None

def enable_pg_stat_statements():
    """Enable pg_stat_statements extension."""
    print("🔧 Enabling pg_stat_statements extension...")

    # Check if already enabled
    try:
        with psycopg.connect("postgresql://danieljacobs@localhost:5432/ai_agency") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM pg_stat_statements LIMIT 1;")
                print("✅ pg_stat_statements is already enabled and working!")
                return True
    except Exception:
        pass  # Not enabled, continue with setup

    # Find PostgreSQL config file
    config_file = check_postgresql_config()
    if not config_file:
        print("❌ Could not find PostgreSQL configuration file")
        print("Please manually add 'pg_stat_statements' to shared_preload_libraries in postgresql.conf")
        print("Then restart PostgreSQL and run: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
        return False

    print(f"📁 Found config file: {config_file}")

    # Read current config
    try:
        with open(config_file) as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False

    # Check if already configured
    if "pg_stat_statements" in content:
        print("✅ pg_stat_statements already in shared_preload_libraries")
        print("🔄 Please restart PostgreSQL and run the script again")
        return False

    # Add pg_stat_statements to shared_preload_libraries
    lines = content.split("\n")
    new_lines = []
    found_shared_preload = False

    for line in lines:
        if line.strip().startswith("shared_preload_libraries"):
            if "pg_stat_statements" not in line:
                # Add pg_stat_statements to existing line
                if line.strip().endswith("="):
                    new_lines.append(f"{line} 'pg_stat_statements'")
                elif line.strip().endswith("''"):
                    new_lines.append(f"{line.replace('', '')} 'pg_stat_statements'")
                else:
                    new_lines.append(f"{line}, 'pg_stat_statements'")
            else:
                new_lines.append(line)
            found_shared_preload = True
        else:
            new_lines.append(line)

    # If shared_preload_libraries not found, add it
    if not found_shared_preload:
        new_lines.append("shared_preload_libraries = 'pg_stat_statements'")

    # Write updated config
    try:
        with open(config_file, "w") as f:
            f.write("\n".join(new_lines))
        print("✅ Updated postgresql.conf with pg_stat_statements")
    except Exception as e:
        print(f"❌ Error writing config file: {e}")
        return False

    print("\n🔄 Next steps:")
    print("1. Restart PostgreSQL:")
    print("   brew services restart postgresql")
    print("   # or")
    print("   sudo systemctl restart postgresql")
    print("2. Run this script again to verify it's working")

    return True

def create_extension():
    """Create the pg_stat_statements extension."""
    try:
        with psycopg.connect("postgresql://danieljacobs@localhost:5432/ai_agency") as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
                conn.commit()
                print("✅ Created pg_stat_statements extension")
                return True
    except Exception as e:
        print(f"❌ Error creating extension: {e}")
        return False

def verify_working():
    """Verify pg_stat_statements is working."""
    try:
        with psycopg.connect("postgresql://danieljacobs@localhost:5432/ai_agency") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM pg_stat_statements;")
                result = cur.fetchone()
                if result is None:
                    print("❌ pg_stat_statements query returned no results")
                    return False
                count = result[0]
                print(f"✅ pg_stat_statements is working! Found {count} statements")
                return True
    except Exception as e:
        print(f"❌ pg_stat_statements not working: {e}")
        return False

def main():
    """Main function."""
    print("🔍 pg_stat_statements Setup")
    print("=" * 50)

    # First check if it's already working
    if verify_working():
        return 0

    # Try to create extension first
    if create_extension():
        if verify_working():
            return 0

    # If not working, try to enable it
    if enable_pg_stat_statements():
        return 0

    print("\n❌ Could not enable pg_stat_statements automatically")
    print("Please manually:")
    print("1. Add 'pg_stat_statements' to shared_preload_libraries in postgresql.conf")
    print("2. Restart PostgreSQL")
    print("3. Run: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")

    return 1

if __name__ == "__main__":
    sys.exit(main())
