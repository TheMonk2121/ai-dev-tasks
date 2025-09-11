#!/usr/bin/env python3
"""
Production Database Setup for Evaluation System
Complete setup including schema creation and real data ingestion.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.common.db_dsn import resolve_dsn


def main():
    """Main setup process."""
    print("🚀 Production Database Setup for Evaluation System")
    print("=" * 60)

    # Check if database DSN is configured
    dsn = resolve_dsn(strict=False)

    # If using mock database, prompt for real database
    if not dsn or dsn == "mock://test":
        print("❌ No real database DSN configured")
        print("   Please provide your PostgreSQL database connection string")
        print("   Example: postgresql://user:pass@localhost:5432/db")

        dsn = input("\nEnter your PostgreSQL DSN: ").strip()
        if not dsn:
            print("❌ No DSN provided, exiting")
            return 1

        # Set environment variables for this session
        os.environ["POSTGRES_DSN"] = dsn
        os.environ["DATABASE_URL"] = dsn
        print(f"✅ Using database: {dsn[:30]}...")
    else:
        print(f"📡 Using database: {dsn[:30]}...")

    # Step 1: Set up database schema
    print("\n🔧 Step 1: Setting up database schema...")
    schema_result = os.system("uv run python scripts/setup_database_schema.py")
    if schema_result != 0:
        print("❌ Database schema setup failed")
        return 1

    # Step 2: Ingest real data
    print("\n📚 Step 2: Ingesting real project data...")
    ingest_result = os.system("uv run python scripts/ingest_real_data.py")
    if ingest_result != 0:
        print("❌ Data ingestion failed")
        return 1

    # Step 3: Update environment for production
    print("\n⚙️  Step 3: Updating environment for production...")
    update_env_result = os.system("uv run python scripts/update_production_env.py")
    if update_env_result != 0:
        print("⚠️  Environment update failed, but continuing...")

    # Step 4: Verify everything is working
    print("\n🔍 Step 4: Verifying production setup...")
    verify_result = os.system("uv run python scripts/health_gated_evaluation.py --check-only")
    if verify_result != 0:
        print("❌ Health check failed")
        return 1

    print("\n✅ Production database setup completed successfully!")
    print("🎉 Your evaluation system is now ready for production use")
    print("\n📋 Next steps:")
    print("   1. Run evaluations: uv run python scripts/ragchecker_official_evaluation.py --profile gold")
    print("   2. Test with real data: uv run python scripts/nightly_smoke_evaluation.py")
    print("   3. Monitor performance: uv run python scripts/health_gated_evaluation.py --check-only")

    return 0


if __name__ == "__main__":
    sys.exit(main())
