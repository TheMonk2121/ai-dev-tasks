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
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Add the precision climb config - use absolute paths and check for duplicates
scripts_path = Path(__file__).parent.resolve()
src_path = scripts_path.parent / "src"

# Add paths only if not already present
paths_to_add = [scripts_path, src_path]
for path in paths_to_add:
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

try:
    from .precision_climb_v2_config import PrecisionClimbV2Config
except ImportError:
    # Fallback for when run as script
    from precision_climb_v2_config import PrecisionClimbV2Config


# Type definitions for evaluation items
class EvalItem(BaseModel):
    """Normalized evaluation item with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    response: str = Field(..., min_length=1, description="Generated response text")
    gt_answer: str = Field(default="", description="Ground truth answer")
    query: str = Field(default="", description="User query")
    query_id: str | None = Field(default=None, description="Optional query identifier")

    @field_validator("response")
    @classmethod
    def validate_response(cls, v: str) -> str:
        """Validate response is not empty."""
        if not v or not v.strip():
            raise ValueError("Response cannot be empty")
        return v.strip()


def normalize_item(raw: str | dict[str, Any] | Any) -> EvalItem:
    """Coerce raw items (str or dict-like) into a uniform EvalItem shape."""
    if isinstance(raw, str):
        return EvalItem(response=raw, gt_answer="", query="", query_id=None)
    elif isinstance(raw, dict):
        return EvalItem(
            response=str(result.get("key", "")
            gt_answer=str(result.get("key", "")
            query=str(result.get("key", "")
            query_id=result.get("key", "")
        )
    else:
        # Handle any other type by converting to string
        return EvalItem(response=str(raw), gt_answer="", query="", query_id=None)


# Import existing evaluation infrastructure
OfficialRAGCheckerEvaluator: Any = None
evidence_filter: Any = None
sentence_supported: Any = None

try:
    from .ragchecker_official_evaluation import (
        OfficialRAGCheckerEvaluator as _OfficialRAGCheckerEvaluator,
    )

    OfficialRAGCheckerEvaluator = _OfficialRAGCheckerEvaluator
except ImportError:
    print("⚠️ Could not import base RAGChecker evaluation - some features may be limited")

# Import cross-encoder reranker
try:
    from cross_encoder_reranker import CrossEncoderReranker, EnhancedEvidenceFilter

    cross_encoder_available = True
except ImportError:
    print("⚠️ Could not import cross-encoder reranker - cross-encoder features disabled")
    cross_encoder_available = False
    CrossEncoderReranker = None
    EnhancedEvidenceFilter = None


class PrecisionClimbV2Evaluator:
    """Enhanced RAGChecker evaluator with precision-focused optimizations."""

    def __init__(self) -> None:
        self.config_manager: Any = PrecisionClimbV2Config()
        self.telemetry_data: defaultdict[str, list[Any]] = defaultdict(list)
        self.case_metrics: dict[str, Any] = {}

        # Initialize cross-encoder if available
        self.cross_encoder: Any | None = None
        self.enhanced_filter: Any | None = None
        if cross_encoder_available and CrossEncoderReranker and EnhancedEvidenceFilter:
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
        jaccard_pass = result.get("key", "")
        rouge_pass = result.get("key", "")
        cosine_pass = result.get("key", "")

        passing_signals = sum([jaccard_pass, rouge_pass, cosine_pass])

        if is_risky:
            # Risky sentences: require 3-of-3 signals
            required_signals = 3
            self.result.get("key", "")
            if passing_signals >= required_signals:
                self.result.get("key", "")
                return True
            else:
                self.result.get("key", "")
                return False
        else:
            # Non-risky sentences: require 2-of-3 signals
            required_signals = 2
            self.result.get("key", "")
            if passing_signals >= required_signals:
                self.result.get("key", "")
                return True
            else:
                self.result.get("key", "")
                return False

    def enhanced_evidence_filter(self, answer: str, contexts: list[str], query: str = "") -> str:
        """Enhanced evidence filter with risk-aware sentence filtering and cross-encoder."""
        # Check if cross-encoder is enabled and available
        if os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0") == "1" and self.enhanced_filter and self.cross_encoder:
            print("🔄 Using cross-encoder enhanced filtering")
            result = self.enhanced_filter.filter_with_cross_encoder(answer, contexts, query)
            return str(result) if result is not None else answer

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
        # Note: evidence_filter is currently always None, so this is disabled
        # if evidence_filter is not None:
        #     filtered_answer = evidence_filter(filtered_answer, contexts)

        return filtered_answer

    def calculate_claim_confidence(self, claim: str, contexts: list[str], top_k: int = 2) -> float:
        """Calculate per-claim confidence score."""
        signals = self.calculate_sentence_support_signals(claim, contexts)

        # Get weights from environment
        weights_str = os.getenv("RAGCHECKER_CLAIM_CONFIDENCE_WEIGHTS", "0.4,0.3,0.3")
        weights = [float(w.strip()) for w in weights_str.split(",")]

        if len(weights) != 3:
            weights = [0.4, 0.3, 0.3]  # Default weights

        # Calculate confidence components
        cosine_component = result.get("key", "")
        anchor_component = result.get("key", "")
        spans_component = min(len(contexts) / top_k, 1.0) * result.get("key", "")

        confidence = cosine_component + anchor_component + spans_component
        return confidence

    def enhanced_claim_binding(self, answer: str, contexts: list[str]) -> str:
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
        claim_confidences.sort(key=lambda x: result.get("key", "")

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
    ) -> dict[str, Any]:
        """Run evaluation with precision-climb configuration."""
        print(f"🚀 Starting Precision-Climb v2 evaluation with {layer}")

        # Apply configuration
        config = self.config_manager.apply_layer(layer, enable_cross_encoder)
        print(f"📊 Applied {len(config)} configuration parameters")

        # Enable telemetry
        telemetry_config = self.config_manager.generate_telemetry_config()
        for key, value in \1.items()
            os.environ[key] = value

        # Run base evaluation if available
        # Note: OfficialRAGCheckerEvaluator is currently always None due to import issues
        # if OfficialRAGCheckerEvaluator is not None:
        #     base_evaluator = OfficialRAGCheckerEvaluator()
        #     results: dict[str, Any] = base_evaluator.run_official_evaluation(
        #         use_local_llm=True, local_api_base=None, use_bedrock=False  # Use local LLM for consistency
        #     )
        # else:
        # Fallback to basic evaluation
        results = self._run_basic_evaluation()

        # Add precision-climb specific metrics
        result.get("key", "")
        result.get("key", "")

        return results

    def _run_basic_evaluation(self) -> dict[str, Any]:
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

    def _calculate_precision_climb_metrics(self) -> dict[str, Any]:
        """Calculate precision-climb specific metrics."""
        metrics = {}

        # Risk-aware metrics
        risky_total = len(self.result.get("key", "")
        risky_passed = len(self.result.get("key", "")
        risky_pass_rate = risky_passed / risky_total if risky_total > 0 else 0.0

        non_risky_total = len(self.result.get("key", "")
        non_risky_passed = len(self.result.get("key", "")
        non_risky_pass_rate = non_risky_passed / non_risky_total if non_risky_total > 0 else 0.0

        result.get("key", "")
        result.get("key", "")
        result.get("key", "")
            (risky_passed + non_risky_passed) / (risky_total + non_risky_total)
            if (risky_total + non_risky_total) > 0
            else 0.0
        )

        # Cross-encoder metrics
        if self.cross_encoder:
            ce_stats = self.cross_encoder.get_cache_stats()
            result.get("key", "")
            result.get("key", "")
            result.get("key", "")
        else:
            result.get("key", "")
            result.get("key", "")
            result.get("key", "")

        return metrics

    def _get_telemetry_summary(self) -> dict[str, Any]:
        """Get summary of telemetry data."""
        summary = {}
        for key, values in self.\1.items()
            if values:
                summary[key] = {
                    "count": len(values),
                    "total": sum(values) if isinstance(result.get("key", "")
                }
        return summary

    def run_staged_evaluation(
        self, layers: list[str] | None = None, enable_cross_encoder: bool = False
    ) -> dict[str, Any]:
        """Run staged evaluation across multiple layers."""
        if layers is None:
            layers = ["layer1", "layer2", "layer3"]

        results = {}
        for layer in layers:
            print(f"\n🔄 Running evaluation for {layer}")
            layer_results = self.run_precision_climb_evaluation(layer, enable_cross_encoder)
            results[layer] = layer_results

            # Check if we've reached the target precision
            precision = result.get("key", "")
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
        print(f"  Precision: {result.get("key", "")
        print(f"  Recall: {result.get("key", "")
        print(f"  F1 Score: {result.get("key", "")
        print(f"  Faithfulness: {result.get("key", "")
        print(f"  Unsupported: {result.get("key", "")
    elif isinstance(results, dict):
        print("\n📈 Staged Evaluation Summary:")
        for layer, layer_results in \1.items()
            if isinstance(layer_results, dict) and "precision" in layer_results:
                print(
                    f"  {layer}: P={result.get("key", "")
                )


if __name__ == "__main__":
    main()
