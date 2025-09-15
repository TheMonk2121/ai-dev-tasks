#!/usr/bin/env python3
"""Test script to verify DSN resolver integration with LTST memory system."""

import os
import sys
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_dsn_resolver():
    """Test the DSN resolver directly."""
    print("🔍 Testing DSN Resolver...")

    try:
        from src.common.db_dsn import resolve_dsn

        # Test with current environment
        dsn = resolve_dsn(strict=False)
        print(f"✅ DSN Resolver returned: {dsn}")

        # Check environment variables
        print(f"📋 DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")
        print(f"📋 POSTGRES_DSN: {os.getenv('POSTGRES_DSN', 'NOT SET')}")

        return dsn
    except Exception as e:
        print(f"❌ DSN Resolver failed: {e}")
        return None

def test_ltst_import():
    """Test importing LTST memory system."""
    print("\n🔍 Testing LTST Memory System Import...")

    try:
        # Import the current LTST integration layer
        from scripts.ltst_memory_integration import LTSTMemoryIntegration

        print("✅ LTST Memory Integration imported successfully")

        # Try to create an instance
        print("🔍 Creating LTST Memory Integration instance...")
        ltst = LTSTMemoryIntegration()
        print("✅ LTST Memory System instance created successfully")

        # Check what connection string it's using
        if hasattr(ltst, "db_manager") and hasattr(ltst.db_manager, "connection_string"):
            print(f"🔗 Database connection: {ltst.db_manager.connection_string}")
        else:
            print("⚠️  Could not determine database connection string")

        return ltst
    except Exception as e:
        print(f"❌ LTST Memory Integration failed: {e}")
        return None

def main():
    """Run all tests."""
    print("🧪 Testing DSN Resolver Integration")
    print("=" * 50)

    # Test 1: DSN Resolver
    dsn = test_dsn_resolver()

    # Test 2: LTST Import
    ltst = test_ltst_import()

    print("\n" + "=" * 50)
    if dsn and ltst:
        print("🎉 All tests passed! DSN integration working.")
    else:
        print("❌ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
