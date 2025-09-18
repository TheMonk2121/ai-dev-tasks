from __future__ import annotations
from typing import Any
import argparse
import logging
import os
import sys

#!/usr/bin/env python3
"""
Precision-Climb v2 Configuration Script

Implements the precision-focused optimization plan to achieve P≥0.20 while maintaining R≥0.60.
Based on the comprehensive analysis and proven RAGAS-competitive strategies.

Layer 0: Wire-through sanity (configuration validation)
Layer 1: Risk-aware sentence-level gates
Layer 2: Fusion tweaks favoring truly relevant docs
Layer 3: Claim binding optimization
Optional: Cross-encoder rerank for top-N candidates
"""

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PrecisionClimbV2Config:
    """Precision-focused configuration manager for RAGChecker optimization."""

    def __init__(self):
        self.config_layers = {
            "layer0": self._get_layer0_config(),
            "layer1": self._get_layer1_config(),
            "layer2": self._get_layer2_config(),
            "layer3": self._get_layer3_config(),
            "cross_encoder": self._get_cross_encoder_config(),
        }

    def _get_layer0_config(self) -> dict[str, Any]:
        """Layer 0: Wire-through sanity - Ensure all knobs actually apply."""
        return {
            # Router configuration
            "RAGCHECKER_ROUTE_BM25_MARGIN": "0.20",
            "RAGCHECKER_REWRITE_AGREE_STRONG": "0.50",
            # Fusion configuration
            "RAGCHECKER_RRF_K": "50",
            "RAGCHECKER_BM25_BOOST_ANCHORS": "1.8",
            "RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR": "0.75",
            "RAGCHECKER_PER_DOC_LINE_CAP": "8",
            # Facets configuration
            "RAGCHECKER_REWRITE_K": "3",
            "RAGCHECKER_REWRITE_KEEP": "1",
            "RAGCHECKER_REWRITE_YIELD_MIN": "1.5",
            # Selection gates
            "RAGCHECKER_EVIDENCE_JACCARD": "0.07",
            "RAGCHECKER_EVIDENCE_COVERAGE": "0.20",
            "RAGCHECKER_SUPPORT_TWO_OF_THREE": "1",
            # Binding configuration
            "RAGCHECKER_CLAIM_TOPK": "2",
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING": "160",
            "RAGCHECKER_DROP_UNSUPPORTED": "0",
            # Dynamic-K (target-K only, no percentile)
            "RAGCHECKER_EVIDENCE_KEEP_MODE": "target_k",
            "RAGCHECKER_TARGET_K_WEAK": "3",
            "RAGCHECKER_TARGET_K_BASE": "5",
            "RAGCHECKER_TARGET_K_STRONG": "9",
        }

    def _get_layer1_config(self) -> dict[str, Any]:
        """Layer 1: Risk-aware sentence-level gates that raise P without killing R."""
        return {
            # Risk-aware support rules
            "RAGCHECKER_RISKY_REQUIRE_ALL": "1",  # 3-of-3 for risky sentences
            "RAGCHECKER_SUPPORT_TWO_OF_THREE": "1",  # 2-of-3 for non-risky
            # Evidence thresholds
            "RAGCHECKER_EVIDENCE_JACCARD": "0.07",
            "RAGCHECKER_EVIDENCE_COVERAGE": "0.20",
            "COS_FLOOR": "0.58",  # Normalized cosine threshold
            "ROUGE_FLOOR": "0.20",
            # Multi-evidence for risky content
            "RAGCHECKER_NUMERIC_MUST_MATCH": "1",
            "RAGCHECKER_ENTITY_MUST_MATCH": "1",
            "RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC": "2",
            "RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY": "2",
            # Redundancy and novelty controls
            "RAGCHECKER_REDUNDANCY_TRIGRAM_MAX": "0.40",  # 0.45 → 0.40
            "RAGCHECKER_PER_CHUNK_CAP": "1",  # Global cap
            "RAGCHECKER_UNIQUE_ANCHOR_MIN": "1",  # Each sentence must add new anchor
        }

    def _get_layer2_config(self) -> dict[str, Any]:
        """Layer 2: Fusion tweaks that favor truly relevant docs."""
        return {
            # Anchor-biased fusion (stronger)
            "RAGCHECKER_RRF_K": "50",  # Stronger rank discount for deep items
            "RAGCHECKER_BM25_BOOST_ANCHORS": "1.8",
            "RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR": "0.75",
            "RAGCHECKER_PER_DOC_LINE_CAP": "8",
            # Selective facet yield (adaptive)
            "RAGCHECKER_REWRITE_YIELD_MIN": "1.5",  # Global default
            "RAGCHECKER_REWRITE_YIELD_MIN_SPARSE": "1.2",  # For sparse cases
            "RAGCHECKER_FUSION_GAIN_THRESHOLD": "2",  # Threshold for sparse case detection
        }

    def _get_layer3_config(self) -> dict[str, Any]:
        """Layer 3: Claim binding that reduces Unsupported Claims without starving R."""
        return {
            # Soft-drop configuration
            "RAGCHECKER_DROP_UNSUPPORTED": "0",  # Keep soft-drop
            # Claim binding parameters
            "RAGCHECKER_CLAIM_TOPK": "2",  # Global
            "RAGCHECKER_CLAIM_TOPK_STRONG": "3",  # For strong cases
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING": "160",
            # Per-claim confidence scoring
            "RAGCHECKER_CLAIM_CONFIDENCE_ENABLED": "1",
            "RAGCHECKER_CLAIM_CONFIDENCE_WEIGHTS": "0.4,0.3,0.3",  # cosine, anchor, spans
        }

    def _get_cross_encoder_config(self) -> dict[str, Any]:
        """Optional: Lightweight cross-encoder rerank for top-N candidates."""
        return {
            "RAGCHECKER_CROSS_ENCODER_ENABLED": "0",  # Disabled by default
            "RAGCHECKER_CROSS_ENCODER_MODEL": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "RAGCHECKER_CROSS_ENCODER_TOP_N": "50",  # Top 50-100 candidates
            "RAGCHECKER_CROSS_ENCODER_WEIGHT": "0.15",  # Weight in blended score
            "RAGCHECKER_CROSS_ENCODER_CACHE": "1",  # Cache embeddings
        }

    def apply_layer(self, layer_name: str, enable_cross_encoder: bool = False) -> dict[str, str]:
        """Apply configuration for a specific layer."""
        if layer_name not in self.config_layers:
            raise ValueError(f"Unknown layer: {layer_name}")

        config = self.config_layers[layer_name].copy()

        # Add cross-encoder config if requested
        if enable_cross_encoder and layer_name in ["layer2", "layer3"]:
            ce_config = self.result.get("key", "")
            result.get("key", "")
            config.update(ce_config)

        # Apply to environment
        for key, value in \1.items()
            os.environ[key] = str(value)

        return config

    def get_layer_config(self, layer_name: str, enable_cross_encoder: bool = False) -> dict[str, str]:
        """Get configuration for a specific layer without applying to environment."""
        if layer_name not in self.config_layers:
            raise ValueError(f"Unknown layer: {layer_name}")

        config = self.config_layers[layer_name].copy()

        # Add cross-encoder config if requested
        if enable_cross_encoder and layer_name in ["layer2", "layer3"]:
            ce_config = self.result.get("key", "")
            result.get("key", "")
            config.update(ce_config)

        return config

    def apply_progressive_config(
        self, layers: list[str], enable_cross_encoder: bool = False
    ) -> dict[str, dict[str, str]]:
        """Apply multiple layers progressively."""
        applied_configs = {}

        for layer in layers:
            logger.info(f"Applying {layer} configuration...")
            config = self.apply_layer(layer, enable_cross_encoder and layer in ["layer2", "layer3"])
            applied_configs[layer] = config

            # Log effective configuration
            self._log_effective_config(layer, config)

        return applied_configs

    def _log_effective_config(self, layer_name: str, config: dict[str, str]) -> None:
        """Log the effective configuration for debugging."""
        logger.info(f"📊 Effective {layer_name} configuration:")
        for key, value in sorted(\1.items()
            logger.info(f"  {key}={value}")

    def validate_configuration(self) -> bool:
        """Validate that all critical configuration parameters are set."""
        critical_params = [
            "RAGCHECKER_EVIDENCE_JACCARD",
            "RAGCHECKER_EVIDENCE_COVERAGE",
            "RAGCHECKER_SUPPORT_TWO_OF_THREE",
            "RAGCHECKER_CLAIM_TOPK",
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING",
        ]

        missing_params = []
        for param in critical_params:
            if param not in os.environ:
                missing_params.append(param)

        if missing_params:
            logger.error(f"Missing critical parameters: {missing_params}")
            return False

        logger.info("✅ Configuration validation passed")
        return True

    def get_rollout_sequence(self) -> list[dict[str, Any]]:
        """Get the recommended rollout sequence with expected improvements."""
        return [
            {
                "layer": "layer1",
                "description": "Risk-aware 3-of-3 + multi-evidence for risky",
                "expected_improvement": "P +0.01–0.02, R ~flat",
                "validation_target": "P ≥ 0.13",
            },
            {
                "layer": "layer2",
                "description": "Anchor-biased fusion",
                "expected_improvement": "P +0.005–0.01",
                "validation_target": "P ≥ 0.14",
            },
            {
                "layer": "layer3",
                "description": "Selective facet yield",
                "expected_improvement": "P +0.005, R ~flat/up",
                "validation_target": "P ≥ 0.15",
            },
            {
                "layer": "cross_encoder",
                "description": "Claim binding confidence order",
                "expected_improvement": "Unsupported ↓, P +0.005",
                "validation_target": "P ≥ 0.16",
            },
            {
                "layer": "final",
                "description": "Cross-encoder rerank (if needed)",
                "expected_improvement": "P +0.02–0.05",
                "validation_target": "P ≥ 0.20",
            },
        ]

    def generate_telemetry_config(self) -> dict[str, str]:
        """Generate telemetry configuration for monitoring."""
        return {
            "RAGCHECKER_TELEMETRY_ENABLED": "1",
            "RAGCHECKER_LOG_RISKY_PASS_RATE": "1",
            "RAGCHECKER_LOG_UNSUPPORTED_PERCENT": "1",
            "RAGCHECKER_LOG_FUSION_GAIN": "1",
            "RAGCHECKER_LOG_ANCHOR_COVERAGE": "1",
            "RAGCHECKER_LOG_NUMERIC_MATCH_RATE": "1",
            "RAGCHECKER_LOG_ENTITY_MATCH_RATE": "1",
            "RAGCHECKER_LOG_CE_RERANK_USED": "1",
        }

    def get_promotion_gate_criteria(self) -> dict[str, float]:
        """Get the RAGAS-competitive promotion gate criteria."""
        return {
            "recall_at_20": 0.65,
            "precision": 0.20,
            "f1_score": 0.175,
            "faithfulness": 0.60,
            "unsupported_percent": 0.15,
        }


def main():
    """Main function for configuration management."""

    parser = argparse.ArgumentParser(description="Precision-Climb v2 Configuration Manager")
    parser.add_argument(
        "--layer",
        choices=["layer0", "layer1", "layer2", "layer3", "cross_encoder"],
        help="Apply specific layer configuration",
    )
    parser.add_argument(
        "--progressive",
        nargs="+",
        choices=["layer0", "layer1", "layer2", "layer3", "cross_encoder"],
        help="Apply multiple layers progressively",
    )
    parser.add_argument("--enable-cross-encoder", action="store_true", help="Enable cross-encoder reranking")
    parser.add_argument("--validate", action="store_true", help="Validate current configuration")
    parser.add_argument("--rollout-sequence", action="store_true", help="Show recommended rollout sequence")
    parser.add_argument("--telemetry", action="store_true", help="Enable telemetry configuration")

    args = parser.parse_args()

    config_manager = PrecisionClimbV2Config()

    if args.validate:
        if config_manager.validate_configuration():
            print("✅ Configuration validation passed")
            sys.exit(0)
        else:
            print("❌ Configuration validation failed")
            sys.exit(1)

    if args.rollout_sequence:
        sequence = config_manager.get_rollout_sequence()
        print("📋 Recommended Rollout Sequence:")
        for i, step in enumerate(sequence, 1):
            print(f"{i}. {result.get("key", "")
            print(f"   Expected: {result.get("key", "")
            print(f"   Target: {result.get("key", "")
            print()
        sys.exit(0)

    if args.telemetry:
        telemetry_config = config_manager.generate_telemetry_config()
        for key, value in \1.items()
            os.environ[key] = value
        print("📊 Telemetry configuration enabled")

    if args.layer:
        config = config_manager.apply_layer(args.layer, args.enable_cross_encoder)
        print(f"✅ Applied {args.layer} configuration")
        print(f"📊 Configuration: {len(config)} parameters set")

    elif args.progressive:
        applied_configs = config_manager.apply_progressive_config(args.progressive, args.enable_cross_encoder)
        print(f"✅ Applied progressive configuration: {args.progressive}")
        total_params = sum(len(config) for config in \1.values()
        print(f"📊 Total parameters set: {total_params}")

    else:
        print("Use --help for usage information")


if __name__ == "__main__":
    main()
