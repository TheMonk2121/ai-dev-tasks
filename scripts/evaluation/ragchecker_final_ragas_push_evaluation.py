from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Final RAGAS Push Evaluation Script

Implements the three-move strategy to push precision past 0.20 while maintaining recall ≥0.60
and driving unsupported ≤15%. Uses Haiku judge for final validation.

Target Metrics:
- Precision ≥ 0.20
- Recall@20 ≥ 0.65
- F1 ≥ 0.175
- Unsupported ≤ 15%
- Faithfulness ≥ 0.60
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Add the precision climb config - use absolute path and check for duplicates
scripts_path = Path(__file__).parent.resolve()
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# Import existing evaluation infrastructure
try:
    from ragchecker_official_evaluation import (
        EvalItem,
        OfficialRAGCheckerEvaluator,
        evidence_filter,
        normalize_item,
        sentence_supported,
    )
except ImportError:
    print("⚠️ Could not import base RAGChecker evaluation - some features may be limited")
    OfficialRAGCheckerEvaluator = None

# Import cross-encoder reranker
try:
    from cross_encoder_reranker import CrossEncoderReranker, EnhancedEvidenceFilter

    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    print("⚠️ Could not import cross-encoder reranker - cross-encoder features disabled")
    CROSS_ENCODER_AVAILABLE = False
    CrossEncoderReranker = None
    EnhancedEvidenceFilter = None

# Import NLI borderline gate
try:
    from nli_borderline_gate import BorderlineNLIGate, EnhancedEvidenceFilterWithNLI

    NLI_AVAILABLE = True
except ImportError:
    print("⚠️ Could not import NLI borderline gate - NLI features disabled")
    NLI_AVAILABLE = False
    BorderlineNLIGate = None
    EnhancedEvidenceFilterWithNLI = None

# Import final RAGAS push config
try:
    from final_ragas_push_config import FinalRAGASPushConfig

    FINAL_CONFIG_AVAILABLE = True
except ImportError:
    print("⚠️ Could not import final RAGAS push config - using fallback")
    FINAL_CONFIG_AVAILABLE = False
    FinalRAGASPushConfig = None

class FinalRAGASPushEvaluator:
    """Final RAGAS push evaluator with three-move strategy."""

    def __init__(self):
        self.config_manager = FinalRAGASPushConfig() if FINAL_CONFIG_AVAILABLE else None
        self.telemetry_data = defaultdict(list)
        self.case_metrics = {}

        # Initialize cross-encoder if available
        self.cross_encoder = None
        self.enhanced_filter = None
        if CROSS_ENCODER_AVAILABLE:
            self.cross_encoder = CrossEncoderReranker()
            self.enhanced_filter = EnhancedEvidenceFilter()

        # Initialize NLI gate if available
        self.nli_gate = None
        self.nli_enhanced_filter = None
        if NLI_AVAILABLE:
            self.nli_gate = BorderlineNLIGate()
            self.nli_enhanced_filter = EnhancedEvidenceFilterWithNLI()

    def detect_risky_sentences(self, sentence: str) -> bool:
        """Detect if a sentence contains risky content (numbers/units or proper nouns)."""
        # Numbers and units pattern
        numeric_pattern = r"\b\d+(?:\.\d+)?\s*(?:%|percent|kg|lb|m|cm|mm|km|ft|in|°|degrees?|years?|months?|days?|hours?|minutes?|seconds?|USD|\$|€|£|¥)\b"

        # Proper nouns pattern (capitalized words, acronyms)
        proper_noun_pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b|\b[A-Z]{2,}\b"

        # Check for risky patterns
        has_numeric = bool(re.search(numeric_pattern, sentence, re.IGNORECASE))
        has_proper_nouns = bool(re.search(proper_noun_pattern, sentence))

        return has_numeric or has_proper_nouns

    def calculate_sentence_support_signals(self, sentence: str, contexts: list[str]) -> dict[str, float]:
        """Calculate all support signals for a sentence."""

        def _tokens(s: str) -> list[str]:
            return re.findall(r"[a-z0-9]+", s.lower())

        def _jaccard(a: set[str], b: set[str]) -> float:
            return (len(a & b) / len(a | b)) if (a or b) else 0.0

        def _lcs_len(a: list[str], b: list[str]) -> int:
            m, n = len(a), len(b)
            dp = [0] * (n + 1)
            for i in range(1, m + 1):
                prev = 0
                ai = a[i - 1]
                for j in range(1, n + 1):
                    tmp = dp[j]
                    dp[j] = prev + 1 if ai == b[j - 1] else max(dp[j], dp[j - 1])
                    prev = tmp
            return dp[n]

        def _rouge_l_f1(a: str, b: str) -> float:
            ta, tb = _tokens(a), _tokens(b)
            if not ta or not tb:
                return 0.0
            lcs = _lcs_len(ta, tb)
            p = lcs / len(tb)
            r = lcs / len(ta)
            return (2 * p * r / (p + r)) if (p + r) else 0.0

        sentence_tokens = set(_tokens(sentence))
        all_context = " ".join(contexts)
        all_context_tokens = set(_tokens(all_context))

        # Calculate signals
        jaccard_score = max([_jaccard(sentence_tokens, set(_tokens(ctx))) for ctx in contexts] + [0.0])
        rouge_score = max([_rouge_l_f1(sentence, ctx) for ctx in contexts] + [0.0])
        cosine_score = _jaccard(sentence_tokens, all_context_tokens)

        return {"jaccard": jaccard_score, "rouge": rouge_score, "cosine": cosine_score}

    def risk_aware_sentence_filter(self, sentence: str, contexts: list[str]) -> bool:
        """Apply risk-aware sentence filtering (3-of-3 for risky, 2-of-3 for non-risky)."""
        is_risky = self.detect_risky_sentences(sentence)
        signals = self.calculate_sentence_support_signals(sentence, contexts)

        # Get thresholds from environment
        jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))

        # Count passing signals
        jaccard_pass = signals["jaccard"] >= jaccard_threshold
        rouge_pass = signals["rouge"] >= rouge_threshold
        cosine_pass = signals["cosine"] >= cosine_threshold

        passing_signals = sum([jaccard_pass, rouge_pass, cosine_pass])

        if is_risky:
            # Risky sentences: require 3-of-3 signals
            required_signals = 3
            self.telemetry_data["risky_sentences_total"].append(1)
            if passing_signals >= required_signals:
                self.telemetry_data["risky_sentences_passed"].append(1)
                return True
            else:
                self.telemetry_data["risky_sentences_failed"].append(1)
                return False
        else:
            # Non-risky sentences: require 2-of-3 signals
            required_signals = 2
            self.telemetry_data["non_risky_sentences_total"].append(1)
            if passing_signals >= required_signals:
                self.telemetry_data["non_risky_sentences_passed"].append(1)
                return True
            else:
                self.telemetry_data["non_risky_sentences_failed"].append(1)
                return False

    def enhanced_evidence_filter(self, answer: str, contexts: list[str], query: str = "") -> str:
        """Enhanced evidence filter with all three moves."""
        # Check if NLI gate is enabled and available
        if os.getenv("RAGCHECKER_NLI_ENABLE", "0") == "1" and self.nli_enhanced_filter and self.nli_gate:
            print("🔄 Using NLI-enhanced filtering")
            return self.nli_enhanced_filter.filter_with_nli_gate(answer, contexts)

        # Check if cross-encoder is enabled and available
        if os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0") == "1" and self.enhanced_filter and self.cross_encoder:
            print("🔄 Using cross-encoder enhanced filtering")
            return self.enhanced_filter.filter_with_cross_encoder(answer, contexts, query)

        # Fall back to risk-aware filtering with robust sentence splitting
        main_answer = answer.split("Sources:", 1)[0].strip()
        bullet_or_num = r"(?m)^\s*(?:[-*•–—]|\d+[\.)])\s+"
        sents = re.split(rf"{bullet_or_num}|(?<=[.!?\]])\s+|\n+", main_answer)
        sents = [s for s in sents if s and s.strip()]
        if len(sents) <= 1:
            sents = re.split(r"\s*[;—–•·]\s*", main_answer)
            sents = [s for s in sents if s.strip()]
        if len(sents) <= 1:
            sents = re.split(r"\s{2,}", main_answer)
            sents = [s for s in sents if s.strip()]
        if not sents:
            return answer

        filtered_sentences = []
        for sent in sents:
            if not sent.strip():
                continue

            # Apply risk-aware filtering
            if self.risk_aware_sentence_filter(sent, contexts):
                filtered_sentences.append(sent)

        # Apply additional filtering from base evidence_filter
        filtered_answer = " ".join(filtered_sentences)

        # Use the base evidence filter for additional processing
        if "evidence_filter" in globals():
            filtered_answer = evidence_filter(filtered_answer, contexts)

        return filtered_answer

    def run_final_ragas_push_evaluation(self) -> dict[str, Any]:
        """Run final RAGAS push evaluation with all three moves."""
        print("🚀 Starting Final RAGAS Push Evaluation")
        print("🎯 Target: Precision ≥ 0.20, Recall@20 ≥ 0.65, F1 ≥ 0.175, Unsupported ≤ 15%")

        # Apply all moves configuration
        if self.config_manager:
            applied_configs = self.config_manager.apply_all_moves()
            print(f"📊 Applied all moves: {sum(len(config) for config in applied_configs.values())} parameters")

            # Enable telemetry
            telemetry_config = self.config_manager.get_telemetry_config()
            for key, value in telemetry_config.items():
                os.environ[key] = value
            print("📊 Telemetry enabled")

        # Run base evaluation if available
        if OfficialRAGCheckerEvaluator:
            base_evaluator = OfficialRAGCheckerEvaluator()
            results = base_evaluator.run_official_evaluation(use_local_llm=True, local_api_base=None, use_bedrock=False)
        else:
            # Fallback to basic evaluation
            results = self._run_basic_evaluation()

        # Add final RAGAS push specific metrics
        results["final_ragas_metrics"] = self._calculate_final_ragas_metrics()
        results["telemetry_summary"] = self._get_telemetry_summary()

        # Validate against RAGAS targets
        if self.config_manager:
            validation = self.config_manager.validate_targets(results.get("overall_metrics", {}))
            results["ragas_validation"] = validation
            results["next_actions"] = self.config_manager.get_next_actions(validation)

        return results

    def _run_basic_evaluation(self) -> dict[str, Any]:
        """Fallback basic evaluation if base evaluator is not available."""
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "faithfulness": 0.0,
            "unsupported_percent": 0.0,
            "evaluation_mode": "basic_fallback",
        }

    def _calculate_final_ragas_metrics(self) -> dict[str, Any]:
        """Calculate final RAGAS push specific metrics."""
        metrics = {}

        # Risk-aware metrics
        risky_total = len(self.telemetry_data.get("risky_sentences_total", []))
        risky_passed = len(self.telemetry_data.get("risky_sentences_passed", []))
        risky_pass_rate = risky_passed / risky_total if risky_total > 0 else 0.0

        non_risky_total = len(self.telemetry_data.get("non_risky_sentences_total", []))
        non_risky_passed = len(self.telemetry_data.get("non_risky_sentences_passed", []))
        non_risky_pass_rate = non_risky_passed / non_risky_total if non_risky_total > 0 else 0.0

        metrics["risky_pass_rate"] = risky_pass_rate
        metrics["non_risky_pass_rate"] = non_risky_pass_rate
        metrics["overall_pass_rate"] = (
            (risky_passed + non_risky_passed) / (risky_total + non_risky_total)
            if (risky_total + non_risky_total) > 0
            else 0.0
        )

        # Cross-encoder metrics
        if self.cross_encoder:
            ce_stats = self.cross_encoder.get_cache_stats()
            metrics["cross_encoder_enabled"] = ce_stats.get("model_loaded", False)
            metrics["cross_encoder_cache_size"] = ce_stats.get("cache_size", 0)
            metrics["cross_encoder_weight"] = ce_stats.get("weight", 0.0)
        else:
            metrics["cross_encoder_enabled"] = False
            metrics["cross_encoder_cache_size"] = 0
            metrics["cross_encoder_weight"] = 0.0

        # NLI gate metrics
        if self.nli_gate:
            nli_stats = self.nli_gate.get_cache_stats()
            metrics["nli_gate_enabled"] = nli_stats.get("model_loaded", False)
            metrics["nli_gate_cache_size"] = nli_stats.get("cache_size", 0)
            metrics["nli_threshold"] = nli_stats.get("nli_threshold", 0.0)
        else:
            metrics["nli_gate_enabled"] = False
            metrics["nli_gate_cache_size"] = 0
            metrics["nli_threshold"] = 0.0

        return metrics

    def _get_telemetry_summary(self) -> dict[str, Any]:
        """Get summary of telemetry data."""
        summary = {}
        for key, values in self.telemetry_data.items():
            if values:
                summary[key] = {
                    "count": len(values),
                    "total": sum(values) if isinstance(values[0], int | float) else len(values),
                }
        return summary

def main():
    """Main function for final RAGAS push evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Final RAGAS Push Evaluation")
    parser.add_argument("--output", type=str, default="final_ragas_push_results.json", help="Output file for results")
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate configuration without running evaluation"
    )

    args = parser.parse_args()

    evaluator = FinalRAGASPushEvaluator()

    if args.validate_only:
        print("🔍 Validating Final RAGAS Push Configuration...")

        # Check component availability
        components = {
            "Base RAGChecker": OfficialRAGCheckerEvaluator is not None,
            "Cross-Encoder": CROSS_ENCODER_AVAILABLE,
            "NLI Gate": NLI_AVAILABLE,
            "Final Config": FINAL_CONFIG_AVAILABLE,
        }

        print("📊 Component Availability:")
        for component, available in components.items():
            status = "✅ Available" if available else "❌ Not Available"
            print(f"  {component}: {status}")

        if all(components.values()):
            print("🎉 All components available - ready for final RAGAS push!")
        else:
            print("⚠️ Some components missing - evaluation may use fallbacks")

        return

    # Run evaluation
    results = evaluator.run_final_ragas_push_evaluation()

    # Save results
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"📊 Results saved to {args.output}")

    # Print summary
    if "overall_metrics" in results:
        metrics = results["overall_metrics"]
        print("\n📈 Final RAGAS Push Results:")
        print(f"  Precision: {metrics.get('precision', 0):.3f}")
        print(f"  Recall: {metrics.get('recall', 0):.3f}")
        print(f"  F1 Score: {metrics.get('f1_score', 0):.3f}")
        print(f"  Faithfulness: {metrics.get('faithfulness', 0):.3f}")
        print(f"  Unsupported: {metrics.get('unsupported_percent', 0):.1f}%")

        # Show RAGAS validation
        if "ragas_validation" in results:
            validation = results["ragas_validation"]
            print("\n🎯 RAGAS Target Validation:")
            for metric, passed in validation.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {metric}: {status}")

            # Show next actions
            if "next_actions" in results:
                actions = results["next_actions"]
                if actions:
                    print("\n🔄 Next Actions:")
                    for action in actions:
                        print(f"  • {action}")

if __name__ == "__main__":
    main()
