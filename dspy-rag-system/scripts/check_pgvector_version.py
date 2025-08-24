#!/usr/bin/env python3
"""
pgvector Version Compatibility Checker

This script checks the pgvector version and validates HNSW support
for the LTST Memory System database optimization.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.database_resilience import DatabaseResilienceManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PgvectorVersionChecker:
    """Check pgvector version and HNSW support."""

    def __init__(self, db_url: str = None):
        """Initialize the checker."""
        self.db_url = db_url or os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
        self.db_manager = DatabaseResilienceManager(self.db_url)

        # Version requirements
        self.min_pgvector_version = "0.5.0"  # Minimum version for HNSW support
        self.recommended_pgvector_version = "0.7.0"  # Recommended version

        # HNSW parameters for testing
        self.test_m = 16
        self.test_ef_construction = 64

    def check_pgvector_version(self) -> dict:
        """Check pgvector version and return detailed information."""
        try:
            import psycopg2

            conn = psycopg2.connect(self.db_url)
            with conn.cursor() as cursor:
                # Check if pgvector extension is available
                cursor.execute(
                    """
                    SELECT extname, extversion
                    FROM pg_extension
                    WHERE extname = 'vector'
                """
                )
                result = cursor.fetchone()

                if not result:
                    return {"available": False, "version": None, "error": "pgvector extension not installed"}

                extname, extversion = result

                # Handle case where extversion might be None or empty
                if not extversion:
                    return {
                        "available": True,
                        "version": "unknown",
                        "major": 0,
                        "minor": 0,
                        "patch": 0,
                        "supports_hnsw": False,
                        "meets_minimum": False,
                        "meets_recommended": False,
                        "error": "Version information not available",
                    }

                # Parse version
                version_parts = extversion.split(".")
                major = int(version_parts[0]) if len(version_parts) > 0 else 0
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                patch = int(version_parts[2]) if len(version_parts) > 2 else 0

                # Check if version supports HNSW
                supports_hnsw = self._version_supports_hnsw(major, minor, patch)

                return {
                    "available": True,
                    "version": extversion,
                    "major": major,
                    "minor": minor,
                    "patch": patch,
                    "supports_hnsw": supports_hnsw,
                    "meets_minimum": self._version_meets_minimum(major, minor, patch),
                    "meets_recommended": self._version_meets_recommended(major, minor, patch),
                }

        except Exception as e:
            logger.error(f"Error checking pgvector version: {e}")
            return {"available": False, "version": None, "error": str(e)}
        finally:
            if "conn" in locals():
                conn.close()

    def _version_supports_hnsw(self, major: int, minor: int, patch: int) -> bool:
        """Check if version supports HNSW indexes."""
        # HNSW support was added in pgvector 0.5.0
        if major > 0:
            return True
        if major == 0 and minor >= 5:
            return True
        return False

    def _version_meets_minimum(self, major: int, minor: int, patch: int) -> bool:
        """Check if version meets minimum requirements."""
        min_parts = self.min_pgvector_version.split(".")
        min_major = int(min_parts[0])
        min_minor = int(min_parts[1])
        min_patch = int(min_parts[2])

        if major > min_major:
            return True
        if major == min_major and minor > min_minor:
            return True
        if major == min_major and minor == min_minor and patch >= min_patch:
            return True
        return False

    def _version_meets_recommended(self, major: int, minor: int, patch: int) -> bool:
        """Check if version meets recommended requirements."""
        rec_parts = self.recommended_pgvector_version.split(".")
        rec_major = int(rec_parts[0])
        rec_minor = int(rec_parts[1])
        rec_patch = int(rec_parts[2])

        if major > rec_major:
            return True
        if major == rec_major and minor > rec_minor:
            return True
        if major == rec_major and minor == rec_minor and patch >= rec_patch:
            return True
        return False

    def test_hnsw_index_creation(self) -> dict:
        """Test HNSW index creation capability."""
        try:
            import psycopg2

            conn = psycopg2.connect(self.db_url)
            with conn.cursor() as cursor:
                # Create a test table with vector column
                cursor.execute(
                    """
                        CREATE TABLE IF NOT EXISTS test_hnsw_support (
                            id SERIAL PRIMARY KEY,
                            embedding VECTOR(384)
                        )
                    """
                )

                # Insert a test record with 384-dimensional vector
                test_vector = "[" + ",".join(["0.1"] * 384) + "]"
                cursor.execute(
                    f"""
                        INSERT INTO test_hnsw_support (embedding)
                        VALUES ('{test_vector}'::vector)
                        ON CONFLICT DO NOTHING
                    """
                )

                # Try to create HNSW index
                try:
                    cursor.execute(
                        f"""
                            CREATE INDEX IF NOT EXISTS test_hnsw_index
                            ON test_hnsw_support
                            USING hnsw (embedding vector_cosine_ops)
                            WITH (m = {self.test_m}, ef_construction = {self.test_ef_construction})
                        """
                    )

                    # Test basic similarity search
                    test_vector = "[" + ",".join(["0.1"] * 384) + "]"
                    cursor.execute(
                        f"""
                            SELECT id, embedding <=> '{test_vector}'::vector as distance
                            FROM test_hnsw_support
                            ORDER BY embedding <=> '{test_vector}'::vector
                            LIMIT 1
                        """
                    )

                    result = cursor.fetchone()

                    # Clean up test table
                    cursor.execute("DROP TABLE IF EXISTS test_hnsw_support")

                    return {
                        "success": True,
                        "index_created": True,
                        "similarity_search_works": True,
                        "test_distance": result[1] if result else None,
                    }

                except Exception as index_error:
                    # Clean up test table
                    cursor.execute("DROP TABLE IF EXISTS test_hnsw_support")

                    return {
                        "success": False,
                        "index_created": False,
                        "error": str(index_error),
                        "fallback_available": True,
                    }

        except Exception as e:
            logger.error(f"Error testing HNSW index creation: {e}")
            return {"success": False, "index_created": False, "error": str(e), "fallback_available": False}

    def test_ivfflat_fallback(self) -> dict:
        """Test IVFFlat index creation as fallback."""
        try:
            import psycopg2

            conn = psycopg2.connect(self.db_url)
            with conn.cursor() as cursor:
                # Create a test table with vector column
                cursor.execute(
                    """
                        CREATE TABLE IF NOT EXISTS test_ivfflat_support (
                            id SERIAL PRIMARY KEY,
                            embedding VECTOR(384)
                        )
                    """
                )

                # Insert a test record with 384-dimensional vector
                test_vector = "[" + ",".join(["0.1"] * 384) + "]"
                cursor.execute(
                    f"""
                        INSERT INTO test_ivfflat_support (embedding)
                        VALUES ('{test_vector}'::vector)
                        ON CONFLICT DO NOTHING
                    """
                )

                # Try to create IVFFlat index
                try:
                    cursor.execute(
                        """
                            CREATE INDEX IF NOT EXISTS test_ivfflat_index
                            ON test_ivfflat_support
                            USING ivfflat (embedding vector_cosine_ops)
                            WITH (lists = 100)
                        """
                    )

                    # Test basic similarity search
                    test_vector = "[" + ",".join(["0.1"] * 384) + "]"
                    cursor.execute(
                        f"""
                            SELECT id, embedding <=> '{test_vector}'::vector as distance
                            FROM test_ivfflat_support
                            ORDER BY embedding <=> '{test_vector}'::vector
                            LIMIT 1
                        """
                    )

                    result = cursor.fetchone()

                    # Clean up test table
                    cursor.execute("DROP TABLE IF EXISTS test_ivfflat_support")

                    return {
                        "success": True,
                        "index_created": True,
                        "similarity_search_works": True,
                        "test_distance": result[1] if result else None,
                    }

                except Exception as index_error:
                    # Clean up test table
                    cursor.execute("DROP TABLE IF EXISTS test_ivfflat_support")

                    return {"success": False, "index_created": False, "error": str(index_error)}

        except Exception as e:
            logger.error(f"Error testing IVFFlat index creation: {e}")
            return {"success": False, "index_created": False, "error": str(e)}

    def generate_report(self) -> dict:
        """Generate comprehensive compatibility report."""
        logger.info("Checking pgvector version compatibility...")

        # Check version
        version_info = self.check_pgvector_version()

        # Test HNSW support
        hnsw_test = None
        if version_info.get("supports_hnsw", False):
            logger.info("Testing HNSW index creation...")
            hnsw_test = self.test_hnsw_index_creation()

        # Test IVFFlat fallback
        logger.info("Testing IVFFlat fallback...")
        ivfflat_test = self.test_ivfflat_fallback()

        # Generate recommendations
        recommendations = self._generate_recommendations(version_info, hnsw_test, ivfflat_test)

        return {
            "version_info": version_info,
            "hnsw_test": hnsw_test,
            "ivfflat_test": ivfflat_test,
            "recommendations": recommendations,
            "timestamp": str(Path(__file__).stat().st_mtime),
        }

    def _generate_recommendations(self, version_info: dict, hnsw_test: dict, ivfflat_test: dict) -> list:
        """Generate recommendations based on test results."""
        recommendations = []

        if not version_info.get("available", False):
            recommendations.append(
                {
                    "type": "error",
                    "message": "pgvector extension not available",
                    "action": "Install pgvector extension before proceeding",
                }
            )
            return recommendations

        if not version_info.get("meets_minimum", False):
            recommendations.append(
                {
                    "type": "warning",
                    "message": f"pgvector version {version_info['version']} is below minimum {self.min_pgvector_version}",
                    "action": "Upgrade pgvector to at least version 0.5.0 for HNSW support",
                }
            )

        if not version_info.get("meets_recommended", False):
            recommendations.append(
                {
                    "type": "info",
                    "message": f"pgvector version {version_info['version']} is below recommended {self.recommended_pgvector_version}",
                    "action": "Consider upgrading to pgvector 0.7.0+ for optimal performance",
                }
            )

        if hnsw_test and hnsw_test.get("success", False):
            recommendations.append(
                {
                    "type": "success",
                    "message": "HNSW indexes are supported and working",
                    "action": "Proceed with HNSW implementation",
                }
            )
        elif hnsw_test and not hnsw_test.get("success", False):
            recommendations.append(
                {
                    "type": "warning",
                    "message": "HNSW index creation failed, but IVFFlat fallback is available",
                    "action": "Use IVFFlat indexes as fallback",
                }
            )

        if ivfflat_test.get("success", False):
            recommendations.append(
                {
                    "type": "success",
                    "message": "IVFFlat indexes are supported and working",
                    "action": "IVFFlat can be used as fallback if HNSW fails",
                }
            )
        else:
            recommendations.append(
                {
                    "type": "error",
                    "message": "Neither HNSW nor IVFFlat indexes are working",
                    "action": "Check pgvector installation and PostgreSQL configuration",
                }
            )

        return recommendations

    def print_report(self, report: dict):
        """Print formatted compatibility report."""
        print("\n" + "=" * 60)
        print("pgvector Version Compatibility Report")
        print("=" * 60)

        # Version information
        version_info = report["version_info"]
        print("\n📊 Version Information:")
        if version_info["available"]:
            print(f"   ✅ pgvector available: {version_info['version']}")
            print(f"   📈 HNSW support: {'✅ Yes' if version_info['supports_hnsw'] else '❌ No'}")
            print(f"   🎯 Meets minimum: {'✅ Yes' if version_info['meets_minimum'] else '❌ No'}")
            print(f"   ⭐ Meets recommended: {'✅ Yes' if version_info['meets_recommended'] else '❌ No'}")
        else:
            print(f"   ❌ pgvector not available: {version_info.get('error', 'Unknown error')}")

        # HNSW test results
        hnsw_test = report["hnsw_test"]
        print("\n🔍 HNSW Index Test:")
        if hnsw_test:
            if hnsw_test["success"]:
                print("   ✅ HNSW index creation: Success")
                print("   ✅ Similarity search: Working")
                if hnsw_test.get("test_distance"):
                    print(f"   📏 Test distance: {hnsw_test['test_distance']:.6f}")
            else:
                print("   ❌ HNSW index creation: Failed")
                print(f"   ⚠️  Error: {hnsw_test.get('error', 'Unknown error')}")
                print(f"   🔄 Fallback available: {'Yes' if hnsw_test.get('fallback_available') else 'No'}")
        else:
            print("   ⚠️  HNSW test skipped (not supported)")

        # IVFFlat test results
        ivfflat_test = report["ivfflat_test"]
        print("\n🔄 IVFFlat Index Test:")
        if ivfflat_test["success"]:
            print("   ✅ IVFFlat index creation: Success")
            print("   ✅ Similarity search: Working")
            if ivfflat_test.get("test_distance"):
                print(f"   📏 Test distance: {ivfflat_test['test_distance']:.6f}")
        else:
            print("   ❌ IVFFlat index creation: Failed")
            print(f"   ⚠️  Error: {ivfflat_test.get('error', 'Unknown error')}")

        # Recommendations
        recommendations = report["recommendations"]
        print("\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️", "success": "✅"}.get(rec["type"], "•")
            print(f"   {icon} {rec['message']}")
            print(f"      Action: {rec['action']}")

        print("\n" + "=" * 60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check pgvector version and HNSW support")
    parser.add_argument("--db-url", help="Database connection URL")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create checker
    checker = PgvectorVersionChecker(args.db_url)

    # Generate report
    report = checker.generate_report()

    # Output results
    if args.json:
        import json

        print(json.dumps(report, indent=2))
    else:
        checker.print_report(report)

    # Exit with appropriate code
    version_info = report["version_info"]
    if not version_info.get("available", False):
        sys.exit(1)

    hnsw_test = report.get("hnsw_test")
    ivfflat_test = report.get("ivfflat_test")

    if hnsw_test and hnsw_test.get("success", False):
        sys.exit(0)  # HNSW works
    elif ivfflat_test and ivfflat_test.get("success", False):
        sys.exit(2)  # Only IVFFlat works
    else:
        sys.exit(1)  # Neither works


if __name__ == "__main__":
    main()
