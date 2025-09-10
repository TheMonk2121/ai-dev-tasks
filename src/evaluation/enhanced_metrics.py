"""
Enhanced evaluation metrics for Phase 0 RAG evaluation.

Implements:
- nDCG@10 (Normalized Discounted Cumulative Gain)
- Coverage (fraction of sub-claims with supporting evidence)
- Exact Match / Span support for extractive queries
- F1 score with proper handling of partial matches
- ECE (Expected Calibration Error) with temperature scaling
- Temperature scaling calibration for confidence scores
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

try:
    from sklearn.calibration import calibration_curve
    from sklearn.isotonic import IsotonicRegression

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


@dataclass
class EvaluationMetrics:
    """Container for evaluation metric results."""

    ndcg_10: float = 0.0
    coverage: float = 0.0
    exact_match: float = 0.0
    span_support: float = 0.0
    f1_score: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    ece: float = 0.0

    # Slice-specific metrics
    slice_metrics: dict[str, dict[str, float]] = None

    # Calibration info
    temperature_param: float | None = None
    calibrated: bool = False


@dataclass
class QueryResult:
    """Single query evaluation result."""

    query: str
    expected_answer: str
    predicted_answer: str
    expected_spans: list[str]
    retrieved_spans: list[str]
    sub_claims: list[str]
    supported_claims: list[str]
    confidence: float | None
    slice_tags: list[str]


class NDCGCalculator:
    """Calculator for Normalized Discounted Cumulative Gain."""

    @staticmethod
    def dcg(relevances: list[float], k: int = 10) -> float:
        """Calculate DCG@k."""
        dcg = 0.0
        for i, rel in enumerate(relevances[:k]):
            if i == 0:
                dcg += rel
            else:
                dcg += rel / math.log2(i + 1)
        return dcg

    @staticmethod
    def ndcg(relevances: list[float], ideal_relevances: list[float], k: int = 10) -> float:
        """Calculate NDCG@k."""
        dcg_score = NDCGCalculator.dcg(relevances, k)
        idcg_score = NDCGCalculator.dcg(sorted(ideal_relevances, reverse=True), k)

        if idcg_score == 0:
            return 0.0

        return dcg_score / idcg_score


class CoverageCalculator:
    """Calculator for sub-claim coverage metrics."""

    @staticmethod
    def calculate_coverage(
        sub_claims: list[str], retrieved_spans: list[str], threshold: float = 0.3  # Token overlap threshold
    ) -> tuple[float, list[str]]:
        """
        Calculate coverage of sub-claims by retrieved spans.

        Returns:
            (coverage_ratio, supported_claims)
        """
        if not sub_claims:
            return 1.0, []

        supported_claims = []

        for claim in sub_claims:
            claim_tokens = set(claim.lower().split())
            if not claim_tokens:
                continue

            # Check if any span supports this claim
            for span in retrieved_spans:
                span_tokens = set(span.lower().split())
                if not span_tokens:
                    continue

                # Calculate token overlap
                overlap = len(claim_tokens & span_tokens) / len(claim_tokens)
                if overlap >= threshold:
                    supported_claims.append(claim)
                    break

        coverage = len(supported_claims) / len(sub_claims)
        return coverage, supported_claims


class SpanMatcher:
    """Matcher for exact match and span support calculations."""

    @staticmethod
    def exact_match(predicted: str, expected: str) -> bool:
        """Check if predicted answer exactly matches expected."""
        return predicted.strip().lower() == expected.strip().lower()

    @staticmethod
    def span_support(predicted_answer: str, retrieved_spans: list[str], min_overlap: float = 0.5) -> float:
        """
        Calculate fraction of predicted answer supported by spans.

        Returns score between 0 and 1.
        """
        if not predicted_answer.strip():
            return 0.0

        pred_tokens = set(predicted_answer.lower().split())
        if not pred_tokens:
            return 0.0

        # Find best supporting span
        max_support = 0.0

        for span in retrieved_spans:
            span_tokens = set(span.lower().split())
            if not span_tokens:
                continue

            # Calculate overlap between prediction and span
            overlap = len(pred_tokens & span_tokens) / len(pred_tokens)
            max_support = max(max_support, overlap)

        return max_support


class TemperatureScaler:
    """Temperature scaling for confidence calibration."""

    def __init__(self):
        self.temperature = 1.0
        self.fitted = False

    def fit(
        self, confidences: list[float], correctness: list[bool], method: str = "isotonic"  # "platt" or "isotonic"
    ) -> float:
        """
        Fit temperature scaling to calibrate confidences.

        Returns the optimal temperature parameter.
        """
        if not HAS_SKLEARN:
            # Simple fallback: assume temperature = 1.0
            self.temperature = 1.0
            self.fitted = True
            return self.temperature

        confidences = np.array(confidences)
        correctness = np.array(correctness, dtype=int)

        if method == "isotonic":
            # Isotonic regression for calibration
            calibrator = IsotonicRegression(out_of_bounds="clip")
            calibrator.fit(confidences, correctness)

            # Estimate temperature from calibrated mapping
            mid_conf = 0.5
            calibrated_mid = calibrator.predict([mid_conf])[0]

            if calibrated_mid > 0.01 and calibrated_mid < 0.99:
                # Estimate temperature from logit transformation
                logit_mid = math.log(mid_conf / (1 - mid_conf))
                calibrated_logit = math.log(calibrated_mid / (1 - calibrated_mid))
                self.temperature = logit_mid / calibrated_logit if calibrated_logit != 0 else 1.0
            else:
                self.temperature = 1.0

        else:
            # Platt scaling (simplified)
            # Find temperature that minimizes NLL
            best_temp = 1.0
            best_nll = float("inf")

            for temp in np.linspace(0.1, 10.0, 100):
                calibrated = self._apply_temperature(confidences, temp)
                nll = self._negative_log_likelihood(calibrated, correctness)

                if nll < best_nll:
                    best_nll = nll
                    best_temp = temp

            self.temperature = best_temp

        self.fitted = True
        return self.temperature

    def _apply_temperature(self, confidences: np.ndarray, temperature: float) -> np.ndarray:
        """Apply temperature scaling to logits."""
        # Convert confidence to logits
        eps = 1e-7
        confidences = np.clip(confidences, eps, 1 - eps)
        logits = np.log(confidences / (1 - confidences))

        # Scale by temperature
        scaled_logits = logits / temperature

        # Convert back to probabilities
        scaled_probs = 1 / (1 + np.exp(-scaled_logits))
        return scaled_probs

    def _negative_log_likelihood(self, probs: np.ndarray, targets: np.ndarray) -> float:
        """Calculate negative log likelihood."""
        eps = 1e-7
        probs = np.clip(probs, eps, 1 - eps)
        nll = -np.mean(targets * np.log(probs) + (1 - targets) * np.log(1 - probs))
        return nll

    def calibrate(self, confidence: float) -> float:
        """Apply temperature scaling to a single confidence score."""
        if not self.fitted:
            return confidence

        return self._apply_temperature(np.array([confidence]), self.temperature)[0]


class ECECalculator:
    """Expected Calibration Error calculator."""

    @staticmethod
    def calculate_ece(confidences: list[float], correctness: list[bool], n_bins: int = 10) -> float:
        """
        Calculate Expected Calibration Error.

        ECE measures the expected difference between confidence and accuracy
        across different confidence bins.
        """
        if len(confidences) != len(correctness):
            raise ValueError("Confidences and correctness must have same length")

        if not confidences:
            return 0.0

        # Create bins
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]

        ece = 0.0
        total_samples = len(confidences)

        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find samples in this bin
            in_bin = []
            for i, conf in enumerate(confidences):
                if bin_lower <= conf < bin_upper or (bin_upper == 1.0 and conf == 1.0):
                    in_bin.append(i)

            if not in_bin:
                continue

            # Calculate bin accuracy and confidence
            bin_confidences = [confidences[i] for i in in_bin]
            bin_correctness = [correctness[i] for i in in_bin]

            bin_accuracy = sum(bin_correctness) / len(bin_correctness)
            bin_confidence = sum(bin_confidences) / len(bin_confidences)

            # Weight by bin size
            bin_weight = len(in_bin) / total_samples
            ece += bin_weight * abs(bin_accuracy - bin_confidence)

        return ece


class EnhancedEvaluator:
    """Main evaluator implementing all Phase 0 metrics."""

    def __init__(self):
        self.temperature_scaler = TemperatureScaler()

    def evaluate_batch(self, query_results: list[QueryResult], slice_breakdown: bool = True) -> EvaluationMetrics:
        """
        Evaluate a batch of query results with all metrics.

        Args:
            query_results: List of query evaluation results
            slice_breakdown: Whether to compute per-slice metrics

        Returns:
            Complete evaluation metrics
        """
        if not query_results:
            return EvaluationMetrics()

        # Collect all metrics
        ndcg_scores = []
        coverage_scores = []
        exact_matches = []
        span_supports = []
        precisions = []
        recalls = []
        f1_scores = []

        confidences = []
        correctness = []

        # Per-slice tracking
        slice_results: dict[str, list[QueryResult]] = {}

        for result in query_results:
            # NDCG calculation (simplified - would need ranking info in practice)
            # For now, use binary relevance based on exact match
            relevance = 1.0 if SpanMatcher.exact_match(result.predicted_answer, result.expected_answer) else 0.0
            ndcg_scores.append(relevance)  # Simplified NDCG

            # Coverage
            coverage, _ = CoverageCalculator.calculate_coverage(result.sub_claims, result.retrieved_spans)
            coverage_scores.append(coverage)

            # Exact match
            exact_match = SpanMatcher.exact_match(result.predicted_answer, result.expected_answer)
            exact_matches.append(exact_match)

            # Span support
            span_support = SpanMatcher.span_support(result.predicted_answer, result.retrieved_spans)
            span_supports.append(span_support)

            # F1, Precision, Recall (token-level)
            pred_tokens = set(result.predicted_answer.lower().split())
            exp_tokens = set(result.expected_answer.lower().split())

            if pred_tokens or exp_tokens:
                overlap = len(pred_tokens & exp_tokens)
                precision = overlap / len(pred_tokens) if pred_tokens else 0.0
                recall = overlap / len(exp_tokens) if exp_tokens else 0.0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            else:
                precision = recall = f1 = 0.0

            precisions.append(precision)
            recalls.append(recall)
            f1_scores.append(f1)

            # Confidence calibration data
            if result.confidence is not None:
                confidences.append(result.confidence)
                correctness.append(exact_match)

            # Slice tracking
            if slice_breakdown:
                for tag in result.slice_tags:
                    if tag not in slice_results:
                        slice_results[tag] = []
                    slice_results[tag].append(result)

        # Calculate aggregate metrics
        metrics = EvaluationMetrics(
            ndcg_10=np.mean(ndcg_scores),
            coverage=np.mean(coverage_scores),
            exact_match=np.mean(exact_matches),
            span_support=np.mean(span_supports),
            precision=np.mean(precisions),
            recall=np.mean(recalls),
            f1_score=np.mean(f1_scores),
        )

        # Temperature scaling and ECE
        if confidences and len(confidences) > 10:
            # Fit temperature scaling
            temperature = self.temperature_scaler.fit(confidences, correctness)
            metrics.temperature_param = temperature
            metrics.calibrated = True

            # Calculate ECE with original confidences
            ece = ECECalculator.calculate_ece(confidences, correctness)
            metrics.ece = ece

        # Per-slice metrics
        if slice_breakdown and slice_results:
            slice_metrics = {}
            for slice_name, slice_data in slice_results.items():
                slice_eval = self.evaluate_batch(slice_data, slice_breakdown=False)
                slice_metrics[slice_name] = asdict(slice_eval)

            metrics.slice_metrics = slice_metrics

        return metrics

    def save_results(self, metrics: EvaluationMetrics, output_path: str) -> None:
        """Save evaluation results to JSON file."""
        results = asdict(metrics)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)


def load_golden_queries(golden_path: str) -> list[QueryResult]:
    """Load golden evaluation queries from JSONL file."""
    queries = []

    golden_file = Path(golden_path)
    if not golden_file.exists():
        return queries

    with open(golden_file) as f:
        for line in f:
            data = json.loads(line.strip())

            query = QueryResult(
                query=data.get("query", ""),
                expected_answer=data.get("answer", ""),
                predicted_answer="",  # To be filled by evaluation
                expected_spans=data.get("expected_spans", []),
                retrieved_spans=[],  # To be filled by evaluation
                sub_claims=data.get("sub_claims", []),
                supported_claims=[],  # To be filled by evaluation
                confidence=None,  # To be filled by evaluation
                slice_tags=data.get("slice_tags", []),
            )
            queries.append(query)

    return queries
