#!/usr/bin/env python3
"""
Precision Push Final Configuration
Apply risk-aware precision optimizations to push past 0.20 while maintaining recall.
"""

import logging
import os
from typing import Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrecisionPushFinalConfig:
    """Final precision push configuration for RAGAS leadership."""

    def __init__(self):
        self.config_sections = {
            "faithfulness_fix": self._get_faithfulness_fix_config(),
            "precision_push": self._get_precision_push_config(),
            "recall_retention": self._get_recall_retention_config(),
            "unsupported_fix": self._get_unsupported_fix_config(),
        }

    def _get_faithfulness_fix_config(self) -> Dict[str, str]:
        """Fix faithfulness wiring bug."""
        return {
            "RAGCHECKER_ENABLE_FUSED_SCORER": "1",
            "RAGCHECKER_JSON_PROMPTS": "1",
        }

    def _get_precision_push_config(self) -> Dict[str, str]:
        """Risk-aware precision push configuration."""
        return {
            # Risk-aware gates (keep non-risky unchanged)
            "RAGCHECKER_SUPPORT_TWO_OF_THREE": "1",
            "RAGCHECKER_RISKY_REQUIRE_ALL": "1",
            "RAGCHECKER_NUMERIC_MUST_MATCH": "1",
            "RAGCHECKER_ENTITY_MUST_MATCH": "1",
            "RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC": "2",
            "RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY": "2",
            # NLI bump on borderlines
            "RAGCHECKER_NLI_ENABLE": "1",
            "RAGCHECKER_NLI_ON_BORDERLINE": "1",
            "RAGCHECKER_BORDERLINE_BAND": "0.02",
            "RAGCHECKER_NLI_P_THRESHOLD": "0.65",  # 0.60→0.65
            # CE weight bump
            "RAGCHECKER_CE_RERANK_ENABLE": "1",
            "RAGCHECKER_CE_RERANK_TOPN": "80",
            "RAGCHECKER_CE_WEIGHT": "0.16",  # 0.12–0.14 → 0.16
            # Keep floors modest so recall holds
            "RAGCHECKER_EVIDENCE_JACCARD": "0.07",
            "RAGCHECKER_EVIDENCE_COVERAGE": "0.20",
            "ROUGE_FLOOR": "0.20",
            "COS_FLOOR": "0.58",
        }

    def _get_recall_retention_config(self) -> Dict[str, str]:
        """Fusion bias toward anchored docs (recall-safe)."""
        return {
            "RAGCHECKER_RRF_K": "50",
            "RAGCHECKER_BM25_BOOST_ANCHORS": "1.9",  # 1.8 → 1.9
            "RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR": "0.72",  # 0.75 → 0.72
            "RAGCHECKER_PER_DOC_LINE_CAP": "8",
            "RAGCHECKER_LONG_TAIL_SLOT": "1",
            # Tiny redundancy trim
            "RAGCHECKER_REDUNDANCY_TRIGRAM_MAX": "0.38",  # from 0.40
            # Facet breadth — selective, not blanket
            "RAGCHECKER_REWRITE_YIELD_MIN": "1.8",  # 1.5 → 1.8
            # Adaptive TOPK only when facets agree
            "RAGCHECKER_REWRITE_AGREE_STRONG": "0.50",
            "RAGCHECKER_CONTEXT_TOPK_MIN": "16",
            "RAGCHECKER_CONTEXT_TOPK_MAX": "22",
        }

    def _get_unsupported_fix_config(self) -> Dict[str, str]:
        """Fix unsupported claims calculation."""
        return {
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING": "160",
            "RAGCHECKER_DROP_UNSUPPORTED": "0",  # Keep soft-drop
        }

    def apply_all_configs(self) -> Dict[str, Dict[str, str]]:
        """Apply all precision push configurations."""
        applied_configs = {}

        for section_name, config in self.config_sections.items():
            logger.info(f"🔧 Applying {section_name} configuration...")

            # Apply to environment
            for key, value in config.items():
                os.environ[key] = str(value)

            applied_configs[section_name] = config.copy()
            logger.info(f"✅ Applied {section_name}: {len(config)} parameters")

        return applied_configs

    def merged_env(self) -> Dict[str, str]:
        """Return a single dict of all env keys we manage (union of sections)."""
        merged: Dict[str, str] = {}
        for _name, cfg in self.config_sections.items():
            merged.update(cfg)
        return merged

    def emit_exports(self) -> str:
        """Render all managed env keys as shell export commands."""
        lines = []
        for k, v in self.merged_env().items():
            # Quote values conservatively
            vq = str(v).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'export {k}="{vq}"')
        return "\n".join(lines) + "\n"

    def print_effective_config(self):
        """Print effective configuration values."""
        print("\n🔧 Precision Push Final Configuration")
        print("=" * 60)

        for section_name, config in self.config_sections.items():
            print(f"\n📊 {section_name.upper()}:")
            for key, value in config.items():
                actual_value = os.getenv(key, "NOT_SET")
                status = "✅" if str(actual_value) == str(value) else "❌"
                print(f"  {status} {key}: {actual_value}")

        print("\n" + "=" * 60)

    def get_telemetry_config(self) -> Dict[str, str]:
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
            "RAGCHECKER_LOG_REWRITE_AGREEMENT": "1",
        }

    def get_ragas_targets(self) -> Dict[str, float]:
        """Get RAGAS target metrics."""
        return {
            "precision": 0.20,
            "recall_at_20": 0.28,  # Conservative target to start
            "f1_score": 0.225,
            "unsupported_percent": 0.18,
            "faithfulness": 0.60,
        }


def main():
    """Main function for precision push final configuration."""
    import argparse

    parser = argparse.ArgumentParser(description="Precision Push Final Configuration")
    parser.add_argument("--apply", action="store_true", help="Apply precision push configuration")
    parser.add_argument("--print-config", action="store_true", help="Print effective configuration")
    parser.add_argument("--telemetry", action="store_true", help="Enable telemetry")
    parser.add_argument("--emit-exports", action="store_true", help="Print shell export commands for this config")
    parser.add_argument("--write-env", type=str, default=None, help="Write KEY=VALUE lines to the given env file")

    args = parser.parse_args()

    config_manager = PrecisionPushFinalConfig()

    if args.apply:
        applied_configs = config_manager.apply_all_configs()
        print(
            f"✅ Applied precision push configuration: {sum(len(config) for config in applied_configs.values())} parameters"
        )

    if args.print_config:
        config_manager.print_effective_config()

    if args.telemetry:
        telemetry_config = config_manager.get_telemetry_config()
        for key, value in telemetry_config.items():
            os.environ[key] = value
        print("📊 Telemetry enabled")

    if args.emit_exports:
        print(config_manager.emit_exports(), end="")

    if args.write_env:
        path = args.write_env
        try:
            with open(path, "w") as f:
                for k, v in config_manager.merged_env().items():
                    f.write(f"{k}={v}\n")
            print(f"💾 Wrote env to {path}")
        except Exception as e:
            print(f"❌ Failed to write env file {path}: {e}")


if __name__ == "__main__":
    main()
