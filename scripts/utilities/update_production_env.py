from __future__ import annotations

import os
import sys
from pathlib import Path

from src.common.db_dsn import resolve_dsn

#!/usr/bin/env python3
"""
Update Environment for Production Database
Updates environment variables to use real database instead of mock.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def update_environment_for_production() -> Any:
    """Update environment variables for production database use."""
    print("⚙️  Updating environment for production database...")

    # Get the current database DSN
    dsn = resolve_dsn(strict=True)
    if not dsn:
        print("❌ No database DSN configured")
        return 1

    print(f"📡 Using database: {dsn[:30]}...")

    # Update environment variables
    os.environ["POSTGRES_DSN"] = dsn
    os.environ["DATABASE_URL"] = dsn
    os.environ["EVAL_DRIVER"] = "dspy_rag"  # Use real RAG instead of synthetic
    os.environ["RAGCHECKER_USE_REAL_RAG"] = "1"  # Enable real RAG evaluation
    os.environ["EVAL_PROFILE"] = "gold"  # Use gold profile for production

    print("   ✅ Environment variables updated:")
    print(f"      - POSTGRES_DSN: {dsn[:30]}...")
    print(f"      - EVAL_DRIVER: {os.environ['EVAL_DRIVER']}")
    print(f"      - RAGCHECKER_USE_REAL_RAG: {os.environ['RAGCHECKER_USE_REAL_RAG']}")
    print(f"      - EVAL_PROFILE: {os.environ['EVAL_PROFILE']}")

    # Create production environment file
    env_file = project_root / "configs" / "production.env"
    env_file.parent.mkdir(exist_ok=True)

    with open(env_file, "w") as f:
        f.write("# Production Environment Configuration\n")
        f.write(f"POSTGRES_DSN={dsn}\n")
        f.write(f"DATABASE_URL={dsn}\n")
        f.write("EVAL_DRIVER=dspy_rag\n")
        f.write("RAGCHECKER_USE_REAL_RAG=1\n")
        f.write("EVAL_PROFILE=gold\n")
        f.write("EVAL_CONCURRENCY=8\n")
        f.write("RETR_TOPK_VEC=50\n")
        f.write("RETR_TOPK_BM25=50\n")
        f.write("RERANK_ENABLE=0\n")
        f.write("DSPY_RAG_PATH=src\n")

    print(f"   📝 Production environment saved to: {env_file}")

    return 0

def main() -> Any:
    """Main entry point."""
    return update_environment_for_production()

if __name__ == "__main__":
    sys.exit(main())