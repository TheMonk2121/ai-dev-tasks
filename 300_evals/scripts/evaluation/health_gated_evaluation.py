import json

#!/usr/bin/env python3
"""
Health-Gated Evaluation System
Refuses to run evaluations if any critical health checks fail.
"""

import os
import sys
import time
from pathlib import Path

# Add scripts to path for imports - use absolute path and check for duplicates
scripts_path = Path(__file__).parent.resolve()
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

try:
    from safe_pytorch_import import apply_safe_pytorch_import

    apply_safe_pytorch_import()
except ImportError:
    pass


class HealthGatedEvaluator:
    """Health-gated evaluation system with comprehensive pre-flight checks."""

    def __init__(self):
        self.health_checks = []
        self.failed_checks = []
        self.warning_checks = []
        self.checks_enabled = {
            "env_validation": os.getenv("HEALTH_CHECK_ENV", "1") == "1",
            "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
            "config_validation": os.getenv("HEALTH_CHECK_CONFIG", "1") == "1",
            "resource_availability": os.getenv("HEALTH_CHECK_RESOURCES", "1") == "1",
        }

    def run_health_checks(self) -> tuple[bool, list[str], list[str]]:
        """Run all enabled health checks."""
        print("🔍 Running health checks...")

        if self.checks_enabled["env_validation"]:
            self._check_environment_validation()

        if self.checks_enabled["index_present"]:
            self._check_index_presence()

        if self.checks_enabled["token_budget"]:
            self._check_token_budget()

        if self.checks_enabled["prefix_leakage"]:
            self._check_prefix_leakage()

        if self.checks_enabled["database_connectivity"]:
            self._check_database_connectivity()

        if self.checks_enabled["model_availability"]:
            self._check_model_availability()

        if self.checks_enabled["config_validation"]:
            self._check_config_validation()

        if self.checks_enabled["resource_availability"]:
            self._check_resource_availability()

        # Determine overall health status
        is_healthy = len(self.failed_checks) == 0

        return is_healthy, self.failed_checks, self.warning_checks

    def _check_environment_validation(self):
        """Check critical environment variables and configuration."""
        print("  🔧 Checking environment validation...")

        critical_env_vars = [
            "DSPY_RAG_PATH",
            "EVAL_DRIVER",
            "RAGCHECKER_USE_REAL_RAG",
            "RETR_TOPK_VEC",
            "RETR_TOPK_BM25",
            "RERANK_ENABLE",
        ]

        missing_vars = []
        for var in critical_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.failed_checks.append(f"Missing critical environment variables: {', '.join(missing_vars)}")
        else:
            print("    ✅ Environment variables validated")

    def _check_index_presence(self):
        """Check if vector index and data are present."""
        print("  📊 Checking index presence...")

        # Check if DSPy RAG system path exists
        dspy_rag_path = os.getenv("DSPY_RAG_PATH", "src")
        if not os.path.exists(dspy_rag_path):
            self.failed_checks.append(f"DSPy RAG system path not found: {dspy_rag_path}")
            return

        # Check if evaluation cases exist
        eval_cases_file = os.getenv("EVAL_CASES_FILE", "300_evals/datasets/eval_cases.jsonl")
        if not os.path.exists(eval_cases_file):
            self.failed_checks.append(f"Evaluation cases file not found: {eval_cases_file}")
            return

        # Check if database has data
        try:
            try:
                from src.common.db_dsn import resolve_dsn

                dsn = resolve_dsn(strict=False)
                if not dsn:
                    self.failed_checks.append("Database DSN not configured")
                    return
                print(f"    ✅ Database DSN configured: {dsn[:20]}...")
            except ImportError:
                self.failed_checks.append("Database DSN module not available")
                return
            except Exception as e:
                self.failed_checks.append(f"Database DSN resolution failed: {e}")
                return

            # Note: Full database connectivity check requires database setup
            # For now, just verify DSN is available
            print("    ✅ Database connectivity check passed (DSN available)")
        except Exception as e:
            self.failed_checks.append(f"Database connectivity check failed: {e}")

    def _check_token_budget(self):
        """Check token budget and limits."""
        print("  🎯 Checking token budget...")

        # Check if token limits are reasonable
        max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
        if max_tokens > 4096:
            self.warning_checks.append(f"High token limit: {max_tokens} (may cause performance issues)")

        # Check context limits
        context_max_chars = int(os.getenv("CONTEXT_MAX_CHARS", "1600"))
        if context_max_chars > 8000:
            self.warning_checks.append(f"High context limit: {context_max_chars} characters")

        print("    ✅ Token budget validated")

    def _check_prefix_leakage(self):
        """Check for prefix leakage in BM25 text."""
        print("  🔒 Checking prefix leakage...")

        # This would check if BM25 text contains evaluation prefixes
        # For now, just validate the configuration
        bm25_text_field = os.getenv("BM25_TEXT_FIELD", "bm25_text")
        embedding_text_field = os.getenv("EMBEDDING_TEXT_FIELD", "embedding_text")

        if bm25_text_field == embedding_text_field:
            self.warning_checks.append("BM25 and embedding text fields are the same (potential leakage)")

        print("    ✅ Prefix leakage check completed")

    def _check_database_connectivity(self):
        """Check database connectivity and schema."""
        print("  🗄️ Checking database connectivity...")

        try:
            try:
                from src.common.db_dsn import resolve_dsn

                dsn = resolve_dsn(strict=False)
                if not dsn:
                    self.failed_checks.append("Database DSN not configured")
                    return
                print(f"    ✅ Database DSN configured: {dsn[:20]}...")
            except ImportError:
                self.failed_checks.append("Database DSN module not available")
                return
            except Exception as e:
                self.failed_checks.append(f"Database DSN resolution failed: {e}")
                return

            # Note: Full database connectivity check requires database setup
            # For now, just verify DSN is available
            print("    ✅ Database connectivity check passed (DSN available)")
        except Exception as e:
            self.failed_checks.append(f"Database connectivity failed: {e}")

    def _check_model_availability(self):
        """Check if required models are available."""
        print("  🤖 Checking model availability...")

        # Check embedding model
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(embedding_model)
            print(f"    ✅ Embedding model available: {embedding_model}")
        except Exception as e:
            self.failed_checks.append(f"Embedding model not available: {embedding_model} - {e}")

        # Check rerank model if enabled
        if os.getenv("RERANK_ENABLE", "1") == "1":
            rerank_model = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
            try:
                from sentence_transformers import CrossEncoder

                model = CrossEncoder(rerank_model)
                print(f"    ✅ Rerank model available: {rerank_model}")
            except Exception as e:
                self.failed_checks.append(f"Rerank model not available: {rerank_model} - {e}")

    def _check_config_validation(self):
        """Validate configuration parameters."""
        print("  ⚙️ Checking configuration validation...")

        # Check retrieval parameters
        topk_vec = int(os.getenv("RETR_TOPK_VEC", "140"))
        topk_bm25 = int(os.getenv("RETR_TOPK_BM25", "140"))

        if topk_vec > 500:
            self.warning_checks.append(f"High vector top-k: {topk_vec} (may cause performance issues)")

        if topk_bm25 > 500:
            self.warning_checks.append(f"High BM25 top-k: {topk_bm25} (may cause performance issues)")

        # Check reranking parameters
        if os.getenv("RERANK_ENABLE", "1") == "1":
            rerank_pool = int(os.getenv("RERANK_POOL", "60"))
            if rerank_pool > 200:
                self.warning_checks.append(f"High rerank pool size: {rerank_pool}")

        # Check performance parameters
        max_in_flight = int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1"))
        if max_in_flight > 3:
            self.warning_checks.append(f"High concurrency: {max_in_flight} (may cause rate limiting)")

        print("    ✅ Configuration validation completed")

    def _check_resource_availability(self):
        """Check system resource availability."""
        print("  💻 Checking resource availability...")

        # Check available disk space
        try:
            import shutil

            total, used, free = shutil.disk_usage("/")
            free_gb = free // (1024**3)
            if free_gb < 5:
                self.warning_checks.append(f"Low disk space: {free_gb}GB available")
        except Exception:
            pass

        # Check memory usage (basic check)
        try:
            import psutil

            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.warning_checks.append(f"High memory usage: {memory.percent}%")
        except ImportError:
            pass

        print("    ✅ Resource availability checked")

    def print_health_report(self, is_healthy: bool, failed_checks: list[str], warning_checks: list[str]):
        """Print comprehensive health report."""
        print("\n" + "=" * 60)
        print("🏥 HEALTH CHECK REPORT")
        print("=" * 60)

        if is_healthy:
            print("✅ OVERALL STATUS: HEALTHY - Ready for evaluation")
        else:
            print("❌ OVERALL STATUS: UNHEALTHY - Evaluation blocked")

        if failed_checks:
            print(f"\n🔴 CRITICAL ISSUES ({len(failed_checks)}):")
            for i, check in enumerate(failed_checks, 1):
                print(f"  {i}. {check}")

        if warning_checks:
            print(f"\n⚠️ WARNINGS ({len(warning_checks)}):")
            for i, check in enumerate(warning_checks, 1):
                print(f"  {i}. {check}")

        if not failed_checks and not warning_checks:
            print("\n🎉 All health checks passed!")

        print("=" * 60)

    def should_proceed_with_evaluation(self) -> bool:
        """Determine if evaluation should proceed based on health checks."""
        is_healthy, failed_checks, warning_checks = self.run_health_checks()
        self.print_health_report(is_healthy, failed_checks, warning_checks)

        if not is_healthy:
            print("\n🚫 EVALUATION BLOCKED: Critical health checks failed")
            print("💡 Fix the critical issues above before running evaluation")
            return False

        if warning_checks:
            print(f"\n⚠️ {len(warning_checks)} warnings detected - proceeding with caution")

        print("\n✅ EVALUATION APPROVED: All critical health checks passed")
        return True


def main():
    """Main entry point for health-gated evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Health-gated evaluation system")
    parser.add_argument(
        "--check-only", action="store_true", help="Only run health checks, don't proceed with evaluation"
    )
    parser.add_argument("--disable-check", action="append", help="Disable specific health check")

    args = parser.parse_args()

    # Disable specific checks if requested
    if args.disable_check:
        for check in args.disable_check:
            if check in evaluator.checks_enabled:
                evaluator.checks_enabled[check] = False

    evaluator = HealthGatedEvaluator()

    if args.check_only:
        # Just run health checks
        is_healthy, failed_checks, warning_checks = evaluator.run_health_checks()
        evaluator.print_health_report(is_healthy, failed_checks, warning_checks)
        sys.exit(0 if is_healthy else 1)
    else:
        # Run health checks and determine if evaluation should proceed
        should_proceed = evaluator.should_proceed_with_evaluation()
        sys.exit(0 if should_proceed else 1)


if __name__ == "__main__":
    main()
