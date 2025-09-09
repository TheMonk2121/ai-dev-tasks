#!/usr/bin/env python3
"""
Production RAGAS Configuration - Tight, No-Drama Rollout

Implements the focused plan to convert three moves into production wins:
- Wire-through & go-live checklist
- Precision climb with tightened screws (risky only)
- Retain recall while tightening precision
- Claim binding that slashes Unsupported ≤ 15%
- Tiny knobs for final precision push
"""

import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ProductionRAGASConfig:
    """Production RAGAS configuration for tight, no-drama rollout."""

    def __init__(self):
        self.config_sections = {
            "router": self._get_router_config(),
            "fusion": self._get_fusion_config(),
            "facets": self._get_facets_config(),
            "selection": self._get_selection_config(),
            "binding": self._get_binding_config(),
            "ce_nli": self._get_ce_nli_config(),
            "dynamic_k": self._get_dynamic_k_config(),
        }

    def _get_router_config(self) -> dict[str, str]:
        """Router configuration."""
        return {
            "RAGCHECKER_ROUTE_BM25_MARGIN": "0.1",
            "RAGCHECKER_REWRITE_AGREE_STRONG": "0.5",
        }

    def _get_fusion_config(self) -> dict[str, str]:
        """Fusion configuration."""
        return {
            "RAGCHECKER_RRF_K": "50",
            "RAGCHECKER_BM25_BOOST_ANCHORS": "1.8",
            "RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR": "0.75",
            "RAGCHECKER_PER_DOC_LINE_CAP": "8",
        }

    def _get_facets_config(self) -> dict[str, str]:
        """Facets configuration."""
        return {
            "RAGCHECKER_REWRITE_K": "10",
            "RAGCHECKER_REWRITE_KEEP": "0.8",
            "RAGCHECKER_REWRITE_YIELD_MIN": "1.5",
        }

    def _get_selection_config(self) -> dict[str, str]:
        """Selection gates configuration."""
        return {
            "RAGCHECKER_EVIDENCE_JACCARD": "0.07",
            "RAGCHECKER_EVIDENCE_COVERAGE": "0.20",
            "RAGCHECKER_SUPPORT_TWO_OF_THREE": "1",
            "RAGCHECKER_RISKY_REQUIRE_ALL": "1",
            "ROUGE_FLOOR": "0.20",
            "COS_FLOOR": "0.58",
        }

    def _get_binding_config(self) -> dict[str, str]:
        """Claim binding configuration."""
        return {
            "RAGCHECKER_CLAIM_TOPK": "2",
            "RAGCHECKER_CLAIM_TOPK_STRONG": "3",
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING": "160",
            "RAGCHECKER_DROP_UNSUPPORTED": "0",
        }

    def _get_ce_nli_config(self) -> dict[str, str]:
        """Cross-encoder and NLI configuration."""
        return {
            "RAGCHECKER_CE_RERANK_ENABLE": "1",
            "RAGCHECKER_CE_RERANK_TOPN": "80",
            "RAGCHECKER_CE_WEIGHT": "0.14",
            "RAGCHECKER_NLI_ENABLE": "1",
            "RAGCHECKER_NLI_ON_BORDERLINE": "1",
            "RAGCHECKER_BORDERLINE_BAND": "0.02",
            "RAGCHECKER_NLI_P_THRESHOLD": "0.62",
        }

    def _get_dynamic_k_config(self) -> dict[str, str]:
        """Dynamic-K configuration."""
        return {
            "RAGCHECKER_EVIDENCE_KEEP_MODE": "target_k",
            "RAGCHECKER_TARGET_K_WEAK": "3",
            "RAGCHECKER_TARGET_K_BASE": "5",
            "RAGCHECKER_TARGET_K_STRONG": "9",
        }

    def apply_production_config(self) -> dict[str, dict[str, str]]:
        """Apply production configuration and return applied configs."""
        applied_configs = {}

        for section_name, config in self.config_sections.items():
            logger.info(f"🔧 Applying {section_name} configuration...")

            # Apply to environment only if not already set
            for key, value in config.items():
                if key not in os.environ:
                    os.environ[key] = str(value)
                    logger.info(f"  ✅ Set {key}={value}")
                else:
                    existing_value = os.environ[key]
                    logger.info(f"  🔒 Preserved {key}={existing_value} (already set)")

            applied_configs[section_name] = config.copy()
            logger.info(f"✅ Applied {section_name}: {len(config)} parameters")

        return applied_configs

    def print_effective_config(self, case_id: str = "case_start"):
        """Print effective configuration values at case start."""
        print(f"\n🔧 Effective Configuration for {case_id}")
        print("=" * 60)

        for section_name, config in self.config_sections.items():
            print(f"\n📊 {section_name.upper()}:")
            for key, value in config.items():
                # Get actual environment value
                actual_value = os.getenv(key, "NOT_SET")
                status = "✅" if str(actual_value) == str(value) else "❌"
                print(f"  {status} {key}: {actual_value}")

        print("\n" + "=" * 60)

    def validate_config(self) -> dict[str, bool]:
        """Validate that all configuration values are properly set."""
        validation = {}

        for section_name, config in self.config_sections.items():
            section_valid = True
            for key, expected_value in config.items():
                actual_value = os.getenv(key)
                if str(actual_value) != str(expected_value):
                    section_valid = False
                    logger.warning(f"❌ Config mismatch: {key} = {actual_value}, expected {expected_value}")

            validation[section_name] = section_valid

        return validation

    def get_precision_knobs(self) -> dict[str, dict[str, str]]:
        """Get precision tuning knobs for fine-tuning."""
        return {
            "ce_weight_boost": {
                "RAGCHECKER_CE_WEIGHT": "0.16",  # 0.14 → 0.16
            },
            "risky_coverage_boost": {
                "RAGCHECKER_EVIDENCE_COVERAGE": "0.22",  # 0.20 → 0.22 (risky only)
            },
            "redundancy_tighten": {
                "RAGCHECKER_REDUNDANCY_TRIGRAM_MAX": "0.38",  # 0.40 → 0.38
            },
            "target_k_reduce": {
                "RAGCHECKER_TARGET_K_STRONG": "8",  # 9 → 8 (strong cases only)
            },
        }

    def get_recall_knobs(self) -> dict[str, dict[str, str]]:
        """Get recall tuning knobs for maintaining R@20 ≥ 0.65."""
        return {
            "adaptive_topk": {
                "RAGCHECKER_CONTEXT_TOPK": "20",  # Adaptive based on rewrite_agreement
            },
            "long_tail_slot": {
                "RAGCHECKER_LONG_TAIL_SLOT": "1",  # Always preserve one novel doc
            },
        }

    def get_telemetry_config(self) -> dict[str, str]:
        """Get comprehensive telemetry configuration."""
        return {
            "RAGCHECKER_TELEMETRY_ENABLED": "1",
            "RAGCHECKER_LOG_RISKY_PASS_RATE": "1",
            "RAGCHECKER_LOG_CE_USED_PERCENT": "1",
            "RAGCHECKER_LOG_NLI_USED_PERCENT": "1",
            "RAGCHECKER_LOG_UNSUPPORTED_PERCENT": "1",
            "RAGCHECKER_LOG_FUSION_GAIN": "1",
            "RAGCHECKER_LOG_ANCHOR_COVERAGE": "1",
            "RAGCHECKER_LOG_KEPT_SENTENCES": "1",
            "RAGCHECKER_LOG_CLAIMS_EXTRACTED_KEPT": "1",
        }

    def get_ragas_targets(self) -> dict[str, float]:
        """Get RAGAS target metrics."""
        return {
            "precision": 0.20,
            "recall_at_20": 0.65,
            "f1_score": 0.175,
            "unsupported_percent": 0.15,
            "faithfulness": 0.60,
        }

    def apply_precision_knob(self, knob_name: str) -> dict[str, str]:
        """Apply a specific precision tuning knob."""
        knobs = self.get_precision_knobs()
        if knob_name not in knobs:
            raise ValueError(f"Unknown precision knob: {knob_name}")

        config = knobs[knob_name]
        for key, value in config.items():
            os.environ[key] = str(value)

        logger.info(f"🎯 Applied precision knob '{knob_name}': {config}")
        return config

    def apply_recall_knob(self, knob_name: str) -> dict[str, str]:
        """Apply a specific recall tuning knob."""
        knobs = self.get_recall_knobs()
        if knob_name not in knobs:
            raise ValueError(f"Unknown recall knob: {knob_name}")

        config = knobs[knob_name]
        for key, value in config.items():
            os.environ[key] = str(value)

        logger.info(f"📈 Applied recall knob '{knob_name}': {config}")
        return config


def main():
    """Main function for production RAGAS configuration."""
    import argparse

    parser = argparse.ArgumentParser(description="Production RAGAS Configuration")
    parser.add_argument("--apply", action="store_true", help="Apply production configuration")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--print-config", action="store_true", help="Print effective configuration")
    parser.add_argument("--precision-knob", type=str, help="Apply precision tuning knob")
    parser.add_argument("--recall-knob", type=str, help="Apply recall tuning knob")
    parser.add_argument("--telemetry", action="store_true", help="Enable telemetry")

    args = parser.parse_args()

    config_manager = ProductionRAGASConfig()

    if args.apply:
        applied_configs = config_manager.apply_production_config()
        print(
            f"✅ Applied production configuration: {sum(len(config) for config in applied_configs.values())} parameters"
        )

    if args.validate:
        validation = config_manager.validate_config()
        print("📊 Configuration Validation:")
        for section, valid in validation.items():
            status = "✅ VALID" if valid else "❌ INVALID"
            print(f"  {section}: {status}")

    if args.print_config:
        config_manager.print_effective_config()

    if args.precision_knob:
        config = config_manager.apply_precision_knob(args.precision_knob)
        print(f"🎯 Applied precision knob: {config}")

    if args.recall_knob:
        config = config_manager.apply_recall_knob(args.recall_knob)
        print(f"📈 Applied recall knob: {config}")

    if args.telemetry:
        telemetry_config = config_manager.get_telemetry_config()
        for key, value in telemetry_config.items():
            os.environ[key] = value
        print("📊 Telemetry configuration enabled")


if __name__ == "__main__":
    main()
