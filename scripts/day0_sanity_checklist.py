#!/usr/bin/env python3
"""
Day-0 Sanity Checklist
2-minute checklist to ensure production readiness before go-live.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class Day0SanityChecklist:
    """Day-0 sanity checklist for production go-live."""

    def __init__(self):
        self.checklist_results = {"timestamp": datetime.now().isoformat(), "checks": {}, "overall_status": "unknown"}

    def run_day0_sanity_checklist(self) -> Dict[str, Any]:
        """Run complete Day-0 sanity checklist."""
        print("🔍 DAY-0 SANITY CHECKLIST")
        print("=" * 50)
        print("⏰ 2-minute production readiness check")
        print()

        # Check 1: Secrets loaded & scoped
        print("🔐 Check 1: Secrets loaded & scoped...")
        secrets_check = self._check_secrets_loaded()
        self.checklist_results["checks"]["secrets_loaded"] = secrets_check

        # Check 2: Active pointer / run-id
        print("📍 Check 2: Active pointer / run-id...")
        pointer_check = self._check_active_pointer()
        self.checklist_results["checks"]["active_pointer"] = pointer_check

        # Check 3: Cache stance
        print("💾 Check 3: Cache stance...")
        cache_check = self._check_cache_stance()
        self.checklist_results["checks"]["cache_stance"] = cache_check

        # Check 4: Reranker prewarm
        print("🔥 Check 4: Reranker prewarm...")
        reranker_check = self._check_reranker_prewarm()
        self.checklist_results["checks"]["reranker_prewarm"] = reranker_check

        # Check 5: Kill switch
        print("🚨 Check 5: Kill switch...")
        killswitch_check = self._check_kill_switch()
        self.checklist_results["checks"]["kill_switch"] = killswitch_check

        # Determine overall status
        all_checks_passed = all(check["passed"] for check in self.checklist_results["checks"].values())
        self.checklist_results["overall_status"] = "passed" if all_checks_passed else "failed"

        # Print summary
        print("\n📊 Day-0 Sanity Checklist Summary:")
        for check_name, check_result in self.checklist_results["checks"].items():
            status_emoji = "✅" if check_result["passed"] else "❌"
            print(f"  {status_emoji} {check_name}: {check_result['message']}")

        if all_checks_passed:
            print("\n🎉 All checks passed - Ready for production go-live!")
        else:
            print("\n⚠️ Some checks failed - Address issues before go-live")

        return self.checklist_results

    def _check_secrets_loaded(self) -> Dict[str, Any]:
        """Check secrets loaded & scoped."""
        required_secrets = {
            "POSTGRES_DSN": "Database connection string",
            "OPENAI_API_KEY": "OpenAI API key",
            "AWS_REGION": "AWS region for Bedrock",
        }

        missing_secrets = []
        present_secrets = []

        for secret, description in required_secrets.items():
            if os.getenv(secret):
                present_secrets.append(secret)
            else:
                missing_secrets.append(secret)

        # Check for least-privilege DB user
        postgres_dsn = os.getenv("POSTGRES_DSN", "")
        is_least_priv = "eval_user" in postgres_dsn or "readonly" in postgres_dsn

        passed = len(missing_secrets) == 0 and is_least_priv

        return {
            "passed": passed,
            "present_secrets": present_secrets,
            "missing_secrets": missing_secrets,
            "is_least_priv_db": is_least_priv,
            "message": f"Secrets: {len(present_secrets)}/{len(required_secrets)} present, DB user: {'least-priv' if is_least_priv else 'full-priv'}",
        }

    def _check_active_pointer(self) -> Dict[str, Any]:
        """Check active pointer / run-id logging."""
        ingest_run_id = os.getenv("INGEST_RUN_ID")
        config_hash = os.getenv("CONFIG_HASH")

        # Check if active pointer file exists
        active_pointer_file = Path("configs/canary/active_pointer.json")
        pointer_exists = active_pointer_file.exists()

        # Check if run-id and config-hash are set
        run_id_set = bool(ingest_run_id)
        config_hash_set = bool(config_hash)

        passed = pointer_exists and run_id_set and config_hash_set

        return {
            "passed": passed,
            "ingest_run_id": ingest_run_id,
            "config_hash": config_hash,
            "pointer_exists": pointer_exists,
            "message": f"Run ID: {ingest_run_id or 'missing'}, Config: {config_hash or 'missing'}, Pointer: {'exists' if pointer_exists else 'missing'}",
        }

    def _check_cache_stance(self) -> Dict[str, Any]:
        """Check cache stance configuration."""
        eval_disable_cache = os.getenv("EVAL_DISABLE_CACHE", "0")
        cache_enabled_prod = os.getenv("CACHE_ENABLED_PROD", "1")

        # Eval cache should be disabled
        eval_cache_disabled = eval_disable_cache == "1"
        # Prod cache should be enabled
        prod_cache_enabled = cache_enabled_prod == "1"

        passed = eval_cache_disabled and prod_cache_enabled

        return {
            "passed": passed,
            "eval_disable_cache": eval_disable_cache,
            "cache_enabled_prod": cache_enabled_prod,
            "message": f"Eval cache: {'disabled' if eval_cache_disabled else 'enabled'}, Prod cache: {'enabled' if prod_cache_enabled else 'disabled'}",
        }

    def _check_reranker_prewarm(self) -> Dict[str, Any]:
        """Check reranker prewarm configuration."""
        reranker_prewarm = os.getenv("RERANKER_PREWARM", "0")
        reranker_model = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")

        # Check if prewarm is enabled
        prewarm_enabled = reranker_prewarm == "1"

        # Check if model is specified
        model_specified = bool(reranker_model)

        passed = prewarm_enabled and model_specified

        return {
            "passed": passed,
            "prewarm_enabled": prewarm_enabled,
            "reranker_model": reranker_model,
            "message": f"Prewarm: {'enabled' if prewarm_enabled else 'disabled'}, Model: {reranker_model or 'missing'}",
        }

    def _check_kill_switch(self) -> Dict[str, Any]:
        """Check kill switch configuration."""
        deploy_disable = os.getenv("DEPLOY_DISABLE_NEW_CONFIG", "0")
        kill_switch_doc = Path("docs/kill_switch.md")

        # Check if kill switch is available
        kill_switch_available = deploy_disable == "1" or kill_switch_doc.exists()

        # Check if ops doc exists
        ops_doc = Path("docs/ops_procedures.md")
        ops_doc_exists = ops_doc.exists()

        passed = kill_switch_available and ops_doc_exists

        return {
            "passed": passed,
            "deploy_disable": deploy_disable,
            "kill_switch_doc": kill_switch_doc.exists(),
            "ops_doc": ops_doc_exists,
            "message": f"Kill switch: {'available' if kill_switch_available else 'missing'}, Ops doc: {'exists' if ops_doc_exists else 'missing'}",
        }

    def print_verification_commands(self):
        """Print verification commands for manual checks."""
        print("\n🔍 Manual Verification Commands:")
        print("=" * 50)

        print("1. Check secrets in runner:")
        print(
            "   echo $POSTGRES_DSN | grep -q 'eval_user' && echo '✅ Least-priv DB user' || echo '❌ Full-priv DB user'"
        )

        print("\n2. Check active pointer logging:")
        print("   python3 scripts/check_active_pointer_logging.py")

        print("\n3. Verify cache stance:")
        print("   echo 'Eval cache disabled:' $EVAL_DISABLE_CACHE")
        print("   echo 'Prod cache enabled:' $CACHE_ENABLED_PROD")

        print("\n4. Test reranker prewarm:")
        print("   python3 scripts/test_reranker_prewarm.py")

        print("\n5. Test kill switch:")
        print("   export DEPLOY_DISABLE_NEW_CONFIG=1")
        print("   python3 scripts/test_kill_switch.py")


def main():
    """Main entry point for Day-0 sanity checklist."""
    checklist = Day0SanityChecklist()
    result = checklist.run_day0_sanity_checklist()

    # Print verification commands
    checklist.print_verification_commands()

    # Exit with appropriate code
    if result["overall_status"] == "passed":
        print("\n🎉 Day-0 sanity checklist passed - Ready for go-live!")
        sys.exit(0)
    else:
        print("\n⚠️ Day-0 sanity checklist failed - Address issues before go-live")
        sys.exit(1)


if __name__ == "__main__":
    main()
