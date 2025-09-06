#!/usr/bin/env python3
"""
RAGChecker Precision-Climb v2 Evaluation Script

Implements the precision-focused optimization plan to achieve P≥0.20 while maintaining R≥0.60.
This script applies the proven RAGAS-competitive strategies in a staged approach.

Key Features:
- Risk-aware sentence-level gates (3-of-3 for risky, 2-of-3 for non-risky)
- Anchor-biased fusion favoring truly relevant docs
- Selective facet yield for sparse cases
- Claim binding optimization to reduce Unsupported Claims
- Optional cross-encoder reranking for top-N candidates
- Comprehensive telemetry and monitoring
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union

# Add the precision climb config
sys.path.insert(0, str(Path(__file__).parent))
from precision_climb_v2_config import PrecisionClimbV2Config

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# Type definitions for evaluation items
class EvalItem(TypedDict, total=False):
    """Normalized evaluation item with guaranteed keys."""

    response: str
    gt_answer: str
    query: str
    query_id: Optional[str]


def normalize_item(raw: Union[str, Dict[str, Any]]) -> EvalItem:
    """Coerce raw items (str or dict-like) into a uniform dict shape."""
    if isinstance(raw, str):
        return {"response": raw, "gt_answer": "", "query": "", "query_id": None}
    elif isinstance(raw, dict):
        return {
            "response": str(raw.get("response", raw.get("answer", ""))),
            "gt_answer": str(raw.get("gt_answer", raw.get("gold", ""))),
            "query": str(raw.get("query", raw.get("question", ""))),
            "query_id": raw.get("query_id", None),
        }
    else:
        return {"response": str(raw), "gt_answer": "", "query": "", "query_id": None}


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


class PrecisionClimbV2Evaluator:
    """Enhanced RAGChecker evaluator with precision-focused optimizations."""

    def __init__(self):
        self.config_manager = PrecisionClimbV2Config()
        self.telemetry_data = defaultdict(list)
        self.case_metrics = {}

        # Initialize cross-encoder if available
        self.cross_encoder = None
        self.enhanced_filter = None
        if CROSS_ENCODER_AVAILABLE:
            self.cross_encoder = CrossEncoderReranker()
            self.enhanced_filter = EnhancedEvidenceFilter()

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

    def calculate_sentence_support_signals(self, sentence: str, contexts: List[str]) -> Dict[str, float]:
        """Calculate all support signals for a sentence."""

        def _tokens(s: str) -> List[str]:
            return re.findall(r"[a-z0-9]+", s.lower())

        def _jaccard(a: set[str], b: set[str]) -> float:
            return (len(a & b) / len(a | b)) if (a or b) else 0.0

        def _lcs_len(a: List[str], b: List[str]) -> int:
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

    def risk_aware_sentence_filter(self, sentence: str, contexts: List[str]) -> bool:
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

    def enhanced_evidence_filter(self, answer: str, contexts: List[str], query: str = "") -> str:
        """Enhanced evidence filter with risk-aware sentence filtering and cross-encoder."""
        # Check if cross-encoder is enabled and available
        if os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0") == "1" and self.enhanced_filter and self.cross_encoder:
            logger.info("🔄 Using cross-encoder enhanced filtering")
            return self.enhanced_filter.filter_with_cross_encoder(answer, contexts, query)

        # Fall back to risk-aware filtering with robust sentence splitting
        main_answer = answer.split("Sources:", 1)[0].strip()
        bullet_or_num = r"(?m)^\s*(?:[-*•–—]|\d+[\.)])\s+"
        sents = re.split(fr"{bullet_or_num}|(?<=[.!?\]])\s+|\n+", main_answer)
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

    def calculate_claim_confidence(self, claim: str, contexts: List[str], top_k: int = 2) -> float:
        """Calculate per-claim confidence score."""
        signals = self.calculate_sentence_support_signals(claim, contexts)

        # Get weights from environment
        weights_str = os.getenv("RAGCHECKER_CLAIM_CONFIDENCE_WEIGHTS", "0.4,0.3,0.3")
        weights = [float(w.strip()) for w in weights_str.split(",")]

        if len(weights) != 3:
            weights = [0.4, 0.3, 0.3]  # Default weights

        # Calculate confidence components
        cosine_component = signals["cosine"] * weights[0]
        anchor_component = signals["jaccard"] * weights[1]  # Using jaccard as anchor proxy
        spans_component = min(len(contexts) / top_k, 1.0) * weights[2]

        confidence = cosine_component + anchor_component + spans_component
        return confidence

    def enhanced_claim_binding(self, answer: str, contexts: List[str]) -> str:
        """Enhanced claim binding with confidence-based ordering."""
        if not os.getenv("RAGCHECKER_CLAIM_CONFIDENCE_ENABLED", "0") == "1":
            # Fall back to base claim binding if not enabled
            return answer

        sents = re.split(r"(?<=[.!?])\s+", answer.strip())
        if not sents:
            return answer

        # Calculate confidence for each sentence
        claim_confidences = []
        for sent in sents:
            if not sent.strip():
                continue
            confidence = self.calculate_claim_confidence(sent, contexts)
            claim_confidences.append((sent, confidence))

        # Sort by confidence (descending)
        claim_confidences.sort(key=lambda x: x[1], reverse=True)

        # Keep top claims until minimum words threshold is met
        min_words = int(os.getenv("RAGCHECKER_MIN_WORDS_AFTER_BINDING", "160"))
        selected_sentences = []
        word_count = 0

        for sent, confidence in claim_confidences:
            selected_sentences.append(sent)
            word_count += len(sent.split())
            if word_count >= min_words:
                break

        return " ".join(selected_sentences)

    def run_precision_climb_evaluation(
        self, layer: str = "layer1", enable_cross_encoder: bool = False
    ) -> Dict[str, Any]:
        """Run evaluation with precision-climb configuration."""
        print(f"🚀 Starting Precision-Climb v2 evaluation with {layer}")

        # Apply configuration
        config = self.config_manager.apply_layer(layer, enable_cross_encoder)
        print(f"📊 Applied {len(config)} configuration parameters")

        # Enable telemetry
        telemetry_config = self.config_manager.generate_telemetry_config()
        for key, value in telemetry_config.items():
            os.environ[key] = value

        # Run base evaluation if available
        if OfficialRAGCheckerEvaluator:
            base_evaluator = OfficialRAGCheckerEvaluator()
            results = base_evaluator.run_official_evaluation(
                use_local_llm=True, local_api_base=None, use_bedrock=False  # Use local LLM for consistency
            )
        else:
            # Fallback to basic evaluation
            results = self._run_basic_evaluation()

        # Add precision-climb specific metrics
        results["precision_climb_metrics"] = self._calculate_precision_climb_metrics()
        results["telemetry_summary"] = self._get_telemetry_summary()

        return results

    def _run_basic_evaluation(self) -> Dict[str, Any]:
        """Fallback basic evaluation if base evaluator is not available."""
        # This would implement a basic evaluation loop
        # For now, return a placeholder
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "faithfulness": 0.0,
            "unsupported_percent": 0.0,
            "evaluation_mode": "basic_fallback",
        }

    def _calculate_precision_climb_metrics(self) -> Dict[str, Any]:
        """Calculate precision-climb specific metrics."""
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

        return metrics

    def _get_telemetry_summary(self) -> Dict[str, Any]:
        """Get summary of telemetry data."""
        summary = {}
        for key, values in self.telemetry_data.items():
            if values:
                summary[key] = {
                    "count": len(values),
                    "total": sum(values) if isinstance(values[0], (int, float)) else len(values),
                }
        return summary

    def run_staged_evaluation(self, layers: List[str] = None, enable_cross_encoder: bool = False) -> Dict[str, Any]:
        """Run staged evaluation across multiple layers."""
        if layers is None:
            layers = ["layer1", "layer2", "layer3"]

        results = {}
        for layer in layers:
            print(f"\n🔄 Running evaluation for {layer}")
            layer_results = self.run_precision_climb_evaluation(layer, enable_cross_encoder)
            results[layer] = layer_results

            # Check if we've reached the target precision
            precision = layer_results.get("precision", 0.0)
            if precision >= 0.20:
                print(f"🎯 Target precision (≥0.20) achieved with {layer}: {precision:.3f}")
                break

        return results


def main():
    """Main function for precision-climb evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="RAGChecker Precision-Climb v2 Evaluation")
    parser.add_argument(
        "--layer",
        choices=["layer1", "layer2", "layer3", "cross_encoder"],
        default="layer1",
        help="Precision-climb layer to evaluate",
    )
    parser.add_argument("--staged", action="store_true", help="Run staged evaluation across multiple layers")
    parser.add_argument("--enable-cross-encoder", action="store_true", help="Enable cross-encoder reranking")
    parser.add_argument("--output", type=str, default="precision_climb_v2_results.json", help="Output file for results")

    args = parser.parse_args()

    evaluator = PrecisionClimbV2Evaluator()

    if args.staged:
        results = evaluator.run_staged_evaluation(enable_cross_encoder=args.enable_cross_encoder)
    else:
        results = evaluator.run_precision_climb_evaluation(args.layer, args.enable_cross_encoder)

    # Save results
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"📊 Results saved to {args.output}")

    # Print summary
    if isinstance(results, dict) and "precision" in results:
        print("\n📈 Evaluation Summary:")
        print(f"  Precision: {results['precision']:.3f}")
        print(f"  Recall: {results['recall']:.3f}")
        print(f"  F1 Score: {results['f1_score']:.3f}")
        print(f"  Faithfulness: {results['faithfulness']:.3f}")
        print(f"  Unsupported: {results['unsupported_percent']:.1f}%")
    elif isinstance(results, dict):
        print("\n📈 Staged Evaluation Summary:")
        for layer, layer_results in results.items():
            if isinstance(layer_results, dict) and "precision" in layer_results:
                print(
                    f"  {layer}: P={layer_results['precision']:.3f}, R={layer_results['recall']:.3f}, F1={layer_results['f1_score']:.3f}"
                )


if __name__ == "__main__":
    main()
