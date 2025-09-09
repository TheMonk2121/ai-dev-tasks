#!/usr/bin/env python3
"""
Precision Lift Pack Configuration
Surgical tightenings for +0.01-0.03 precision with minimal recall loss.
"""

from typing import Any

from limit_inspired_precision_recovery import LimitInspiredPrecisionRecovery


class PrecisionLiftPackConfig(LimitInspiredPrecisionRecovery):
    """Precision lift pack with surgical tightenings for precision improvement."""

    def _get_enhanced_config(self) -> dict[str, Any]:
        """Get enhanced configuration with precision lift pack."""
        # Start with base LIMIT configuration
        base_config = super()._get_enhanced_config()

        # Apply precision lift pack modifications
        precision_config = {
            **base_config,
            # A) Tighten sentence-level support (two-of-three rule)
            "RAGCHECKER_EVIDENCE_JACCARD": "0.06",  # 0.05 → 0.06
            "RAGCHECKER_EVIDENCE_COVERAGE": "0.18",  # 0.16 → 0.18
            "RAGCHECKER_SUPPORT_TWO_OF_THREE": "1",  # Enable two-of-three gate
            # B) Hard gates for numbers & entities
            "RAGCHECKER_NUMERIC_MUST_MATCH": "1",  # Numbers must appear in retrieved spans
            "RAGCHECKER_ENTITY_MUST_MATCH": "1",  # Entities must appear in retrieved spans
            "RAGCHECKER_PENALTY_NUM_MISMATCH": "0.12",  # Raise from 0.08
            "RAGCHECKER_PENALTY_UNBACKED_NEG": "0.08",  # Keep negation alignment strict
            # C) Reduce local redundancy and clumping
            "RAGCHECKER_REDUNDANCY_TRIGRAM_MAX": "0.45",  # 0.50 → 0.45 (already set)
            "RAGCHECKER_PER_CHUNK_CAP": "2",  # 3 → 2 (already set)
            "RAGCHECKER_UNIQUE_ANCHOR_MIN": "1",  # Require new anchor per kept sentence
            # D) Calibrate claim binding breadth (don't starve recall)
            "RAGCHECKER_CLAIM_TOPK": "3",  # Keep at 3 globally
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING": "140",  # 120 → 140 (already set)
            "RAGCHECKER_CLAIM_TOPK_STRONG": "4",  # 4 only on strong cases
            "RAGCHECKER_DROP_UNSUPPORTED": "0",  # Keep soft-drop
            # E) Soften facet influence in fusion (just a hair)
            "RAGCHECKER_RRF_K": "80",  # Smaller K → stronger rank penalty
            "RAGCHECKER_BM25_BOOST_ANCHORS": "1.5",  # 1.4 → 1.5
            "RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR": "0.85",  # Down-weight facet-only docs
            "RAGCHECKER_REWRITE_YIELD_MIN": "1.2",  # 1.0 → 1.2 (keep only higher-yield facets)
            # Keep recall guardrails in place
            "RAGCHECKER_TARGET_K_STRONG": "8",  # Keep dynamic-K strong
            "RAGCHECKER_LONG_TAIL_SLOT": "1",  # Keep 1 reserved slot
            "RAGCHECKER_FAITHFULNESS_REPORTING": "1",  # Keep faithfulness ON (reporting)
        }

        return precision_config

    def get_precision_lift_summary(self) -> dict[str, Any]:
        """Get summary of precision lift pack changes."""
        return {
            "precision_lift_pack": {
                "sentence_level_support": {
                    "evidence_jaccard": "0.05 → 0.06",
                    "evidence_coverage": "0.16 → 0.18",
                    "two_of_three_gate": "enabled",
                },
                "hard_gates": {
                    "numeric_must_match": "enabled",
                    "entity_must_match": "enabled",
                    "penalty_num_mismatch": "0.08 → 0.12",
                },
                "redundancy_reduction": {
                    "trigram_max": "0.50 → 0.45",
                    "per_chunk_cap": "3 → 2",
                    "unique_anchor_min": "enabled",
                },
                "claim_binding": {
                    "claim_topk": "3 (global), 4 (strong)",
                    "min_words_after_binding": "120 → 140",
                    "drop_unsupported": "soft (0)",
                },
                "facet_influence": {
                    "rrf_k": "80 (smaller K)",
                    "bm25_boost_anchors": "1.4 → 1.5",
                    "facet_downweight_no_anchor": "0.85",
                    "rewrite_yield_min": "1.0 → 1.2",
                },
            },
            "recall_guardrails": {
                "target_k_strong": "8 (keep dynamic-K)",
                "long_tail_slot": "1 (reserved)",
                "faithfulness_reporting": "ON",
            },
            "expected_impact": {
                "precision_gain": "+0.01 to +0.03",
                "recall_loss": "≤0.01",
                "target_precision": "≥0.135",
                "target_recall": "≥0.20-0.26",
                "target_f1": "≥0.155",
            },
        }


def apply_precision_lift_pack() -> PrecisionLiftPackConfig:
    """Apply precision lift pack configuration."""
    config = PrecisionLiftPackConfig()
    config.apply_environment()
    return config


if __name__ == "__main__":
    config = apply_precision_lift_pack()

    print("\n🎯 Precision Lift Pack Configuration Applied")
    print("=" * 50)

    summary = config.get_precision_lift_summary()

    print("\n📊 Precision Lift Pack Changes:")
    for category, changes in summary["precision_lift_pack"].items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for key, value in changes.items():
            print(f"   {key}: {value}")

    print("\n🛡️ Recall Guardrails:")
    for key, value in summary["recall_guardrails"].items():
        print(f"   {key}: {value}")

    print("\n🎯 Expected Impact:")
    for key, value in summary["expected_impact"].items():
        print(f"   {key}: {value}")

    print("\n✅ Ready for precision lift evaluation!")
