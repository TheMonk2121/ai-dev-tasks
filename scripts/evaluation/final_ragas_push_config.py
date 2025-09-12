from __future__ import annotations
import logging
import os
    import argparse
#!/usr/bin/env python3
"""
Final RAGAS Push Configuration

Implements the three-move strategy to push precision past 0.20 while maintaining recall ≥0.60
and driving unsupported ≤15%. Based on proven RAGAS-competitive strategies.

Target Metrics:
- Precision ≥ 0.20
- Recall@20 ≥ 0.65
- F1 ≥ 0.175
- Unsupported ≤ 15%
- Faithfulness ≥ 0.60
"""

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FinalRAGASPushConfig:
    """Final precision push configuration for RAGAS competitiveness."""

    def __init__(self):
        self.move_configs = {
            "move1": self._get_move1_config(),
            "move2": self._get_move2_config(),
            "move3": self._get_move3_config(),
            "recall_health": self._get_recall_health_config(),
        }

    def _get_move1_config(self) -> dict[str, str]:
        """Move 1: Risk-aware 3-of-3 (risky only) + multi-evidence."""
        return {
            # Risk-aware support rules
            "RAGCHECKER_SUPPORT_TWO_OF_THREE": "1",  # 2-of-3 for normal sentences
            "RAGCHECKER_RISKY_REQUIRE_ALL": "1",  # 3-of-3 for risky sentences
            # Evidence thresholds
            "RAGCHECKER_EVIDENCE_JACCARD": "0.07",
            "RAGCHECKER_EVIDENCE_COVERAGE": "0.20",
            "ROUGE_FLOOR": "0.20",
            "COS_FLOOR": "0.58",
            # Multi-evidence for risky content
            "RAGCHECKER_NUMERIC_MUST_MATCH": "1",
            "RAGCHECKER_ENTITY_MUST_MATCH": "1",
            "RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC": "2",
            "RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY": "2",
            # Expected: +0.01–0.02 precision, Unsupported ↓, recall ≈ flat
        }

    def _get_move2_config(self) -> dict[str, str]:
        """Move 2: Lightweight cross-encoder rerank with decisive blending."""
        return {
            # Cross-encoder configuration
            "RAGCHECKER_CROSS_ENCODER_ENABLED": "1",
            "RAGCHECKER_CE_RERANK_ENABLE": "1",
            "RAGCHECKER_CE_RERANK_TOPN": "80",
            "RAGCHECKER_CE_WEIGHT": "0.12",  # Nudged up from 0.10
            # Redundancy controls (if needed)
            "RAGCHECKER_PER_CHUNK_CAP": "2",  # Strict if flooding
            "RAGCHECKER_REDUNDANCY_TRIGRAM_MAX": "0.40",
            # Expected: +0.02–0.04 precision, minimal recall hit
        }

    def _get_move3_config(self) -> dict[str, str]:
        """Move 3: Borderline NLI gate for unsupported reduction."""
        return {
            # NLI configuration
            "RAGCHECKER_NLI_ENABLE": "1",
            "RAGCHECKER_NLI_ON_BORDERLINE": "1",
            "RAGCHECKER_BORDERLINE_BAND": "0.02",
            "RAGCHECKER_NLI_P_THRESHOLD": "0.60",
            # Expected: Unsupported → ≤15–18%, precision +~0.01, tiny recall cost
        }

    def _get_recall_health_config(self) -> dict[str, str]:
        """Recall health maintenance configuration."""
        return {
            # Anchor-biased fusion (retain)
            "RAGCHECKER_RRF_K": "50",
            "RAGCHECKER_BM25_BOOST_ANCHORS": "1.8",
            "RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR": "0.75",
            "RAGCHECKER_PER_DOC_LINE_CAP": "8",
            "RAGCHECKER_LONG_TAIL_SLOT": "1",
            # Facet yield (selective)
            "RAGCHECKER_REWRITE_YIELD_MIN": "1.5",  # Global default
            "RAGCHECKER_REWRITE_YIELD_MIN_SPARSE": "1.2",  # For sparse cases
            # Claim binding
            "RAGCHECKER_CLAIM_TOPK": "2",
            "RAGCHECKER_CLAIM_TOPK_STRONG": "3",
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING": "160",
            "RAGCHECKER_DROP_UNSUPPORTED": "0",  # Keep soft-drop
            # Dynamic-K
            "RAGCHECKER_EVIDENCE_KEEP_MODE": "target_k",
            "RAGCHECKER_TARGET_K_WEAK": "3",
            "RAGCHECKER_TARGET_K_BASE": "5",
            "RAGCHECKER_TARGET_K_STRONG": "9",
        }

    def apply_move(self, move_name: str) -> dict[str, str]:
        """Apply a specific move configuration."""
        if move_name not in self.move_configs:
            raise ValueError(f"Unknown move: {move_name}")

        config = self.move_configs[move_name].copy()

        # Apply to environment
        for key, value in config.items():
            os.environ[key] = str(value)

        logger.info(f"✅ Applied {move_name} configuration: {len(config)} parameters")
        return config

    def apply_all_moves(self) -> dict[str, dict[str, str]]:
        """Apply all moves in sequence."""
        applied_configs = {}

        # Apply recall health first (foundation)
        logger.info("🏗️ Applying recall health foundation...")
        applied_configs["recall_health"] = self.apply_move("recall_health")

        # Apply moves in sequence
        for move in ["move1", "move2", "move3"]:
            logger.info(f"🎯 Applying {move}...")
            applied_configs[move] = self.apply_move(move)

        return applied_configs

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

    def get_fallback_configs(self) -> dict[str, dict[str, str]]:
        """Get fallback configurations if targets not met."""
        return {
            "precision_low": {
                "RAGCHECKER_TARGET_K_STRONG": "8",  # Drop by 1
                "RAGCHECKER_EVIDENCE_COVERAGE_RISKY": "0.22",  # Raise for risky only
            },
            "recall_low": {
                "RAGCHECKER_CONTEXT_TOPK": "18",  # Raise only when REWRITE_AGREE_STRONG ≥ 0.50
            },
        }

    def validate_targets(self, results: dict[str, float]) -> dict[str, bool]:
        """Validate if results meet RAGAS targets."""
        targets = self.get_ragas_targets()
        validation = {}

        for metric, target in targets.items():
            if metric in results:
                validation[metric] = results[metric] >= target
            else:
                validation[metric] = False

        return validation

    def get_next_actions(self, validation: dict[str, bool]) -> list[str]:
        """Get recommended next actions based on validation results."""
        actions = []

        if not validation.get("precision", False):
            actions.append(
                "Apply precision fallback: Drop TARGET_K_STRONG by 1 or raise EVIDENCE_COVERAGE to 0.22 for risky sentences"
            )

        if not validation.get("recall_at_20", False):
            actions.append("Apply recall fallback: Raise CONTEXT_TOPK to 18 only when REWRITE_AGREE_STRONG ≥ 0.50")

        if all(validation.values()):
            actions.append("🎉 SUCCESS: All RAGAS targets met! Repeat once (two-run rule) and raise Haiku floors")

        return actions

def main():
    """Main function for final RAGAS push configuration."""

    parser = argparse.ArgumentParser(description="Final RAGAS Push Configuration")
    parser.add_argument(
        "--move", choices=["move1", "move2", "move3", "recall_health"], help="Apply specific move configuration"
    )
    parser.add_argument("--all-moves", action="store_true", help="Apply all moves in sequence")
    parser.add_argument("--telemetry", action="store_true", help="Enable telemetry configuration")
    parser.add_argument("--targets", action="store_true", help="Show RAGAS target metrics")
    parser.add_argument("--fallbacks", action="store_true", help="Show fallback configurations")

    args = parser.parse_args()

    config_manager = FinalRAGASPushConfig()

    if args.targets:
        targets = config_manager.get_ragas_targets()
        print("🎯 RAGAS Target Metrics:")
        for metric, target in targets.items():
            print(f"  {metric}: {target}")
        return

    if args.fallbacks:
        fallbacks = config_manager.get_fallback_configs()
        print("🔄 Fallback Configurations:")
        for scenario, config in fallbacks.items():
            print(f"  {scenario}: {config}")
        return

    if args.telemetry:
        telemetry_config = config_manager.get_telemetry_config()
        for key, value in telemetry_config.items():
            os.environ[key] = value
        print("📊 Telemetry configuration enabled")

    if args.move:
        config = config_manager.apply_move(args.move)
        print(f"✅ Applied {args.move} configuration")
        print(f"📊 Configuration: {len(config)} parameters set")

    elif args.all_moves:
        applied_configs = config_manager.apply_all_moves()
        print("✅ Applied all moves configuration")
        total_params = sum(len(config) for config in applied_configs.values())
        print(f"📊 Total parameters set: {total_params}")

        # Enable telemetry
        telemetry_config = config_manager.get_telemetry_config()
        for key, value in telemetry_config.items():
            os.environ[key] = value
        print("📊 Telemetry enabled")

    else:
        print("Use --help for usage information")

if __name__ == "__main__":
    main()