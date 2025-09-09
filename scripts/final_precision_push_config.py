#!/usr/bin/env python3
"""
Final Precision Push Configuration
Aggressive precision tightening to achieve P ≥ 0.135 target with minimal recall loss.
"""

from typing import Any

from precision_lift_pack_config import PrecisionLiftPackConfig


class FinalPrecisionPushConfig(PrecisionLiftPackConfig):
    """Final precision push with aggressive tightening for P ≥ 0.135 target."""

    def _get_enhanced_config(self) -> dict[str, Any]:
        """Get enhanced configuration with final precision push."""
        # Start with precision lift pack configuration
        base_config = super()._get_enhanced_config()

        # Apply final precision push modifications
        final_config = {
            **base_config,
            # Aggressive precision tightening (one more click)
            "RAGCHECKER_REDUNDANCY_TRIGRAM_MAX": "0.40",  # 0.45 → 0.40 (stricter)
            "RAGCHECKER_PER_CHUNK_CAP": "1",  # 2 → 1 (strict)
            "RAGCHECKER_EVIDENCE_JACCARD": "0.07",  # 0.06 → 0.07 (tighter)
            "RAGCHECKER_EVIDENCE_COVERAGE": "0.20",  # 0.18 → 0.20 (stricter)
            "RAGCHECKER_PENALTY_NUM_MISMATCH": "0.15",  # 0.12 → 0.15 (harsher)
            "RAGCHECKER_CLAIM_TOPK": "2",  # 3 → 2 (global, stricter)
            "RAGCHECKER_CLAIM_TOPK_STRONG": "3",  # 4 → 3 (strong cases)
            "RAGCHECKER_MIN_WORDS_AFTER_BINDING": "160",  # 140 → 160 (more selective)
            "RAGCHECKER_REWRITE_YIELD_MIN": "1.5",  # 1.2 → 1.5 (only high-yield facets)
            "RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR": "0.80",  # 0.85 → 0.80 (more aggressive)
            "RAGCHECKER_RRF_K": "60",  # 80 → 60 (stronger rank penalty)
            "RAGCHECKER_BM25_BOOST_ANCHORS": "1.6",  # 1.5 → 1.6 (stronger anchor boost)
            # Additional precision gates
            "RAGCHECKER_STRICT_SEMANTIC_MATCH": "1",  # Enable strict semantic matching
            "RAGCHECKER_REQUIRE_QUERY_ANCHORS": "1",  # Require query terms in retrieved docs
            "RAGCHECKER_PENALTY_WEAK_SUPPORT": "0.10",  # Penalty for weak support
            "RAGCHECKER_MAX_SENTENCE_LENGTH": "200",  # Cap sentence length for precision
            # Keep recall guardrails but tighten slightly
            "RAGCHECKER_TARGET_K_STRONG": "7",  # 8 → 7 (slightly tighter)
            "RAGCHECKER_LONG_TAIL_SLOT": "1",  # Keep 1 reserved slot
            "RAGCHECKER_CONTEXT_TOPK": "14",  # 16 → 14 (tighter)
            # Final precision reporting
            "RAGCHECKER_FINAL_PRECISION_PUSH": "1",  # Flag for final push
            "RAGCHECKER_AGGRESSIVE_MODE": "1",  # Enable aggressive mode
        }

        return final_config

    def get_final_precision_push_summary(self) -> dict[str, Any]:
        """Get summary of final precision push changes."""
        return {
            "final_precision_push": {
                "aggressive_tightening": {
                    "redundancy_trigram_max": "0.45 → 0.40",
                    "per_chunk_cap": "2 → 1",
                    "evidence_jaccard": "0.06 → 0.07",
                    "evidence_coverage": "0.18 → 0.20",
                    "penalty_num_mismatch": "0.12 → 0.15",
                },
                "claim_binding_tightening": {
                    "claim_topk": "3 → 2 (global)",
                    "claim_topk_strong": "4 → 3 (strong)",
                    "min_words_after_binding": "140 → 160",
                },
                "facet_influence_tightening": {
                    "rewrite_yield_min": "1.2 → 1.5",
                    "facet_downweight_no_anchor": "0.85 → 0.80",
                    "rrf_k": "80 → 60",
                    "bm25_boost_anchors": "1.5 → 1.6",
                },
                "additional_precision_gates": {
                    "strict_semantic_match": "enabled",
                    "require_query_anchors": "enabled",
                    "penalty_weak_support": "0.10",
                    "max_sentence_length": "200",
                },
                "recall_guardrail_adjustments": {
                    "target_k_strong": "8 → 7",
                    "context_topk": "16 → 14",
                    "long_tail_slot": "1 (maintained)",
                },
            },
            "expected_impact": {
                "precision_gain": "+0.016 to +0.025 (target: ≥0.135)",
                "recall_loss": "≤0.02 (maintain ≥0.20)",
                "f1_improvement": "+0.005 to +0.015",
                "target_precision": "≥0.135",
                "target_recall": "≥0.20",
                "target_f1": "≥0.155",
            },
            "risk_assessment": {
                "precision_risk": "Low - aggressive but controlled",
                "recall_risk": "Low - guardrails maintained",
                "f1_risk": "Low - balanced approach",
                "fallback_plan": "If recall drops >0.02, relax EVIDENCE_COVERAGE to 0.19",
            },
        }


def apply_final_precision_push() -> FinalPrecisionPushConfig:
    """Apply final precision push configuration."""
    config = FinalPrecisionPushConfig()
    config.apply_environment()
    return config


if __name__ == "__main__":
    config = apply_final_precision_push()

    print("\n🎯 Final Precision Push Configuration Applied")
    print("=" * 50)

    summary = config.get_final_precision_push_summary()

    print("\n📊 Final Precision Push Changes:")
    for category, changes in summary["final_precision_push"].items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for key, value in changes.items():
            print(f"   {key}: {value}")

    print("\n🎯 Expected Impact:")
    for key, value in summary["expected_impact"].items():
        print(f"   {key}: {value}")

    print("\n⚠️ Risk Assessment:")
    for key, value in summary["risk_assessment"].items():
        print(f"   {key}: {value}")

    print("\n✅ Ready for final precision push evaluation!")
