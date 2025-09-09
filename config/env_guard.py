#!/usr/bin/env python3
"""
Environment Guard - Hard-fail early for missing required environment variables.
Importing this module will immediately check for required environment variables.
"""

import os
import sys


# Required environment variables for production
REQUIRED_ENV_VARS = ["POSTGRES_DSN", "OPENAI_API_KEY", "AWS_REGION"]

# Optional but recommended environment variables
RECOMMENDED_ENV_VARS = ["INGEST_RUN_ID", "CHUNK_VARIANT", "CHUNK_SIZE", "OVERLAP_RATIO", "EVAL_DISABLE_CACHE"]


def check_required_env_vars() -> None:
    """Check for required environment variables and fail fast if missing."""
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

    if missing_vars:
        print("❌ CRITICAL: Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n💡 Set them with:")
        print("   export POSTGRES_DSN='postgresql://user:pass@host:5432/dbname'")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   export AWS_REGION='us-east-1'")
        print("\n🚨 Exiting due to missing environment variables.")
        sys.exit(1)


def check_recommended_env_vars() -> list[str]:
    """Check for recommended environment variables and warn if missing."""
    missing_vars = [var for var in RECOMMENDED_ENV_VARS if not os.getenv(var)]

    if missing_vars:
        print("⚠️  WARNING: Missing recommended environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("   These are optional but recommended for optimal performance.")

    return missing_vars


def get_env_summary() -> dict:
    """Get a summary of environment variable status."""
    return {
        "required": {
            "present": [var for var in REQUIRED_ENV_VARS if os.getenv(var)],
            "missing": [var for var in REQUIRED_ENV_VARS if not os.getenv(var)],
        },
        "recommended": {
            "present": [var for var in RECOMMENDED_ENV_VARS if os.getenv(var)],
            "missing": [var for var in RECOMMENDED_ENV_VARS if not os.getenv(var)],
        },
    }


# Auto-check on import (this is the key behavior)
check_required_env_vars()

# Optional: warn about recommended vars (non-fatal)
check_recommended_env_vars()

if __name__ == "__main__":
    # Allow running as a standalone script for testing
    print("✅ Environment check passed!")
    summary = get_env_summary()
    print(f"Required vars present: {len(summary['required']['present'])}/{len(REQUIRED_ENV_VARS)}")
    print(f"Recommended vars present: {len(summary['recommended']['present'])}/{len(RECOMMENDED_ENV_VARS)}")
