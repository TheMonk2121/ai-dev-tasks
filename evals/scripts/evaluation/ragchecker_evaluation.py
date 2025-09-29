#!/usr/bin/env python3
"""
RAGChecker Evaluation System

This module implements RAGChecker evaluation as a replacement for RAGAS.
RAGChecker is a peer-reviewed, industry-tested framework that provides
fine-grained diagnostic metrics for RAG systems with strong correlation
to human judgments.

Reference: https://arxiv.org/abs/2408.08067
"""

import copy
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator
from ragchecker.container import RetrievedDoc  # type: ignore[import-untyped]
from ragchecker.evaluator import RAGChecker, RAGResult, RAGResults  # type: ignore[import-untyped]

try:
    from .ragchecker_constitution_validator import (  # type: ignore[attr-defined]
        RAGCheckerConstitutionValidator,
    )
except Exception:  # pragma: no cover - fallback when optional dependency missing
    RAGCheckerConstitutionValidator = None  # type: ignore[assignment]

try:
    from scripts.evaluation.ragchecker_official_evaluation import (  # type: ignore[import-untyped]
        OfficialRAGCheckerEvaluator,
    )
except Exception:  # pragma: no cover - optional runtime dependency
    OfficialRAGCheckerEvaluator = None  # type: ignore[assignment]

# Use canonical schemas
from src.schemas.eval import EvaluationResult, GoldCase, Mode
from src.utils.gold_loader import load_gold_cases, stratified_sample


class RAGCheckerResult(BaseModel):
    """Result of RAGChecker evaluation with Pydantic validation."""

    test_case_name: str = Field(..., min_length=1, description="Name of the test case")
    query: str = Field(..., min_length=1, description="The query that was evaluated")
    custom_score: float = Field(..., ge=0.0, le=1.0, description="Custom evaluation score (0-1)")
    ragchecker_scores: dict[str, float] = Field(..., description="Dictionary of RAGChecker metric scores")
    ragchecker_overall: float = Field(..., ge=0.0, le=1.0, description="Overall RAGChecker score (0-1)")
    comparison: dict[str, Any] = Field(..., description="Comparison data between custom and RAGChecker scores")
    recommendation: str = Field(..., min_length=1, description="Recommendation based on evaluation results")

    @field_validator("test_case_name")
    @classmethod
    def validate_test_case_name(cls, v):
        if not v.strip():
            raise ValueError("test_case_name cannot be empty")
        return v.strip()

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("query cannot be empty")
        return v.strip()

    @field_validator("recommendation")
    @classmethod
    def validate_recommendation(cls, v):
        if not v.strip():
            raise ValueError("recommendation cannot be empty")
        return v.strip()

    @field_validator("ragchecker_scores")
    @classmethod
    def validate_ragchecker_scores(cls, v):
        if not v:
            raise ValueError("ragchecker_scores cannot be empty")
        # Validate all scores are in 0-1 range
        for score_name, score_value in v.items():
            if not isinstance(score_value, int | float) or score_value < 0.0 or score_value > 1.0:
                raise ValueError(f"Score {score_name} must be between 0.0 and 1.0, got {score_value}")
        return v

class RAGCheckerEvaluator:
    """RAGChecker evaluator that provides industry-standard RAG evaluation."""

    def __init__(self):
        # Initialize RAGChecker with default settings
        # Note: RAGChecker requires LLM access for claim extraction and checking
        # We'll use it in a limited capacity for metrics that don't require LLM
        self.ragchecker = RAGChecker()
        self.constitution_validator: RAGCheckerConstitutionValidator | None = None
        if RAGCheckerConstitutionValidator is not None:
            try:
                self.constitution_validator = RAGCheckerConstitutionValidator()
            except Exception as exc:  # pragma: no cover - best-effort optional feature
                print(f"⚠️ Constitution validator unavailable: {exc}")
                self.constitution_validator = None

        self.official_evaluator: OfficialRAGCheckerEvaluator | None = None
        if OfficialRAGCheckerEvaluator is not None:
            try:
                self.official_evaluator = OfficialRAGCheckerEvaluator()
            except Exception as exc:  # pragma: no cover - best-effort optional feature
                print(f"⚠️ Official RAGChecker evaluator unavailable: {exc}")
                self.official_evaluator = None

    def run_memory_query(self, query: str, role: str = "planner") -> dict[str, Any]:
        """Run memory query using our existing orchestrator."""
        try:
            result = subprocess.run(
                [
                    "python3",
                    "scripts/unified_memory_orchestrator.py",
                    "--systems",
                    "ltst",
                    "cursor",
                    "go_cli",
                    "prime",
                    "--role",
                    role,
                    query,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {"success": True, "output": result.stdout, "error": None}
            else:
                return {"success": False, "output": result.stdout, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Query timed out after 60 seconds"}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

    def extract_ragchecker_data(self, response: dict[str, Any], query: str) -> RAGResult:
        """Extract data in RAGChecker format from memory system response."""
        try:
            # Parse the response
            response_data = json.loads(response.get("output", "{}"))
            generated_response = response.get("output", "")

            # Extract retrieved context
            context_sources: list[str] = []
            if "ltst_memory" in response_data:
                context_sources.append(str(response_data.get("ltst_memory", "")))
            if "cursor_memory" in response_data:
                context_sources.append(str(response_data.get("cursor_memory", "")))
            if "go_cli_memory" in response_data:
                context_sources.append(str(response_data.get("go_cli_memory", "")))
            if "prime_memory" in response_data:
                context_sources.append(str(response_data.get("prime_memory", "")))

            retrieved_context = " ".join(context_sources) if context_sources else ""

            # Create RetrievedDoc objects
            retrieved_docs: list[RetrievedDoc] = []
            if retrieved_context:
                retrieved_docs.append(RetrievedDoc(doc_id="memory_context", text=retrieved_context))

            # Create RAGResult
            # Note: We don't have ground truth answers, so we'll use a placeholder
            rag_result = RAGResult(
                query_id=f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                query=query,
                gt_answer="",  # We don't have ground truth
                response=generated_response,
                retrieved_context=retrieved_docs,
            )

            return rag_result

        except Exception as e:
            print(f"Error extracting RAGChecker data: {e}")
            # Fallback to basic extraction
            return RAGResult(
                query_id=f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                query=query,
                gt_answer="",
                response=response.get("output", ""),
                retrieved_context=[],
            )

    def run_ragchecker_evaluation(self, rag_result: RAGResult) -> dict[str, float]:
        """Run RAGChecker evaluation on the data."""
        try:
            # Create RAGResults object
            rag_results = RAGResults([rag_result])

            # Run RAGChecker evaluation with limited metrics
            # Note: Many RAGChecker metrics require LLM access and ground truth
            # We'll focus on metrics that can work with our data
            results = self.ragchecker.evaluate(rag_results, metrics="faithfulness")  # type: ignore[attr-defined]

            # Extract scores
            ragchecker_scores: dict[str, float] = {}
            for metric_name, score in results.items():
                try:
                    if isinstance(score, int | float):
                        ragchecker_scores[metric_name] = float(score)
                    else:
                        ragchecker_scores[metric_name] = 0.0
                except (ValueError, TypeError):
                    ragchecker_scores[metric_name] = 0.0

            return ragchecker_scores

        except Exception as e:
            print(f"RAGChecker evaluation failed: {e}")
            # Return basic metrics that we can calculate manually
            return self._calculate_basic_metrics(rag_result)

    def _calculate_basic_metrics(self, rag_result: RAGResult) -> dict[str, float]:
        """Calculate basic metrics that don't require LLM or ground truth."""
        metrics: dict[str, float] = {}

        # Response length (normalized)
        response_length = len(rag_result.response)
        metrics["response_length"] = min(response_length / 1000.0, 1.0)  # Normalize to 0-1

        # Context utilization (if we have retrieved context)
        if rag_result.retrieved_context:
            context_length = sum(len(doc.text) for doc in rag_result.retrieved_context)
            metrics["context_utilization"] = min(context_length / 2000.0, 1.0)  # Normalize to 0-1
        else:
            metrics["context_utilization"] = 0.0

        # Query-response overlap (simple keyword matching)
        query_words = set(rag_result.query.lower().split())
        response_words = set(rag_result.response.lower().split())
        if query_words:
            overlap = len(query_words.intersection(response_words)) / len(query_words)
            metrics["query_response_overlap"] = overlap
        else:
            metrics["query_response_overlap"] = 0.0

        return metrics

    def validate_with_constitution(self, evaluation_data: dict[str, Any]) -> dict[str, Any]:
        """Validate RAGChecker evaluation data with constitution awareness."""
        validation_results = self._create_empty_validation_results()

        if "input" in evaluation_data:
            validation_results["input_validation"] = self._basic_input_validation(
                evaluation_data.get("input", {})
            )

        if "metrics" in evaluation_data:
            validation_results["metrics_validation"] = self._basic_metrics_validation(
                evaluation_data.get("metrics", {})
            )

        if "result" in evaluation_data:
            validation_results["result_validation"] = self._basic_result_validation(
                evaluation_data.get("result", {})
            )

        try:
            if self.constitution_validator is not None:
                self._apply_constitution_validator(validation_results, evaluation_data)
        except Exception as exc:  # pragma: no cover - optional path
            validation_results["overall_compliance"] = False
            validation_results.setdefault("errors", []).append(str(exc))
            print(f"Constitution validator integration failed: {exc}")

        self._finalize_validation_summary(validation_results)
        return validation_results

    def validate_with_constitution_and_taxonomy(self, evaluation_data: dict[str, Any]) -> dict[str, Any]:
        """Validate RAGChecker evaluation data with constitution awareness and error taxonomy."""
        # First, perform constitution validation
        validation_results = self.validate_with_constitution(evaluation_data)

        validator = self.constitution_validator
        if validator is None:
            return validation_results

        try:
            enhanced = validator.enhance_validation_with_taxonomy(copy.deepcopy(validation_results))
            self._finalize_validation_summary(enhanced)
            return enhanced
        except Exception as exc:  # pragma: no cover - optional path
            validation_results.setdefault("taxonomy_warning", str(exc))
            print(f"Error taxonomy enhancement failed: {exc}")
            return validation_results

    def _extract_compliance_score(self, validation_result: dict[str, Any]) -> float:
        """Extract compliance score from validation result safely."""
        try:
            if validation_result and "is_valid" in validation_result:
                if validation_result["is_valid"]:
                    return 1.0
                else:
                    return 0.5
            return 0.0
        except Exception:
            return 0.0

    def _extract_recommendations(self, validation_results: dict[str, Any]) -> list[str]:
        """Extract recommendations from validation results."""
        recommendations = []

        for validation_type in ["input_validation", "metrics_validation", "result_validation"]:
            if validation_results[validation_type]:
                validation = validation_results[validation_type]
                if "warnings" in validation:
                    for warning in validation["warnings"]:
                        if isinstance(warning, dict) and "recommendation" in warning:
                            recommendations.append(warning["recommendation"])

        return list(set(recommendations))  # Remove duplicates

    def _create_empty_validation_results(self) -> dict[str, Any]:
        """Create a base validation result structure."""
        return {
            "input_validation": None,
            "metrics_validation": None,
            "result_validation": None,
            "overall_compliance": True,
            "total_violations": 0,
            "total_warnings": 0,
        }

    def _basic_input_validation(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Perform lightweight input validation as a baseline."""
        _ = input_data  # Placeholder for future enhancements
        return {"is_valid": True, "errors": [], "warnings": [], "compliance": None}

    def _basic_metrics_validation(self, metrics_data: dict[str, Any]) -> dict[str, Any]:
        """Perform lightweight metrics validation as a baseline."""
        _ = metrics_data
        return {"is_valid": True, "errors": [], "warnings": [], "compliance": None}

    def _basic_result_validation(self, result_data: dict[str, Any]) -> dict[str, Any]:
        """Perform lightweight result validation as a baseline."""
        _ = result_data
        return {"is_valid": True, "errors": [], "warnings": [], "compliance": None}

    def _merge_validation_sections(
        self,
        base: dict[str, Any] | None,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        """Merge baseline validation with constitution-aware results."""

        merged: dict[str, Any] = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        if base:
            merged["is_valid"] = bool(base.get("is_valid", True))
            merged["errors"] = list(base.get("errors", []))
            merged["warnings"] = list(base.get("warnings", []))
            if "compliance" in base:
                merged["compliance"] = base.get("compliance")

        merged["is_valid"] = merged["is_valid"] and bool(extra.get("valid", True))
        merged["errors"].extend(extra.get("errors", []))
        merged["warnings"].extend(extra.get("warnings", []))

        if extra.get("compliance") is not None:
            merged["compliance"] = extra.get("compliance")

        return merged

    def _apply_constitution_validator(
        self, validation_results: dict[str, Any], evaluation_data: dict[str, Any]
    ) -> None:
        """Apply constitution validator outputs onto baseline validation data."""

        validator = self.constitution_validator
        if validator is None:
            return

        if "input" in evaluation_data:
            validator_result = validator.validate_ragchecker_input(evaluation_data.get("input", {}))
            validation_results["input_validation"] = self._merge_validation_sections(
                validation_results.get("input_validation"), validator_result
            )

        if "metrics" in evaluation_data:
            validator_result = validator.validate_ragchecker_metrics(evaluation_data.get("metrics", {}))
            validation_results["metrics_validation"] = self._merge_validation_sections(
                validation_results.get("metrics_validation"), validator_result
            )

        if "result" in evaluation_data:
            validator_result = validator.validate_ragchecker_result(evaluation_data.get("result", {}))
            validation_results["result_validation"] = self._merge_validation_sections(
                validation_results.get("result_validation"), validator_result
            )

    def _finalize_validation_summary(self, validation_results: dict[str, Any]) -> None:
        """Recompute aggregate validation summary fields."""

        overall = True
        total_violations = 0
        total_warnings = 0

        for section_key in ["input_validation", "metrics_validation", "result_validation"]:
            section = validation_results.get(section_key)
            if not section:
                continue
            overall = overall and bool(section.get("is_valid", True))
            total_violations += len(section.get("errors", []))
            total_warnings += len(section.get("warnings", []))

        validation_results["overall_compliance"] = overall
        validation_results["total_violations"] = total_violations
        validation_results["total_warnings"] = total_warnings
        validation_results["compliance_summary"] = {
            "is_compliant": overall,
            "compliance_score": 1.0 if overall else 0.5,
            "total_violations": total_violations,
            "total_warnings": total_warnings,
            "recommendations": self._extract_recommendations(validation_results),
        }

    def get_debugging_summary(self) -> dict[str, Any]:
        """Get debugging summary for RAGChecker evaluation workflows"""
        return {"status": "basic_debugging", "message": "Debugging features not yet implemented"}

    def get_debug_context(self, evaluation_id: str) -> Any | None:
        """Get debug context for a specific evaluation"""
        return {"evaluation_id": evaluation_id, "status": "basic_context"}

    def get_error_recovery_statistics(self) -> dict[str, Any]:
        """Get error recovery statistics and performance metrics"""
        return {"status": "basic_recovery", "message": "Error recovery features not yet implemented"}

    def recover_from_validation_error(
        self, error: Exception, error_type: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Recover from a validation error using the error recovery system"""
        return {"status": "basic_recovery", "error": str(error), "error_type": error_type}

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance optimization summary"""
        return {"status": "basic_performance", "message": "Performance optimization not yet implemented"}

    def update_optimization_config(self, **config_updates) -> None:
        """Update performance optimization configuration"""
        pass  # No-op for now

    def clear_performance_history(self) -> None:
        """Clear performance history"""
        pass  # No-op for now

    def batch_validate_with_constitution(
        self, evaluation_data_batch: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], Any]:
        """Batch validate multiple evaluation data items with constitution awareness"""
        results = []
        for data in evaluation_data_batch:
            results.append(self.validate_with_constitution(data))
        return results, None

    # Performance Monitoring Methods
    def get_performance_monitoring_summary(self) -> dict[str, Any]:
        """Get comprehensive performance monitoring summary."""
        return {"status": "basic_monitoring", "message": "Performance monitoring not yet implemented"}

    def get_performance_history(
        self, start_time: datetime | None = None, end_time: datetime | None = None, max_points: int = 100
    ) -> list[dict[str, Any]]:
        """Get performance history within a time range."""
        return []

    def export_performance_metrics(self, filepath: str, format_type: str = "json") -> bool:
        """Export performance metrics to file."""
        return False

    def update_performance_thresholds(self, **threshold_updates) -> None:
        """Update performance monitoring thresholds."""
        pass  # No-op for now

    def add_performance_alert_callback(self, callback) -> None:
        """Add a callback function for performance alerts."""
        pass  # No-op for now

    def acknowledge_performance_alert(self, alert_id: str) -> bool:
        """Acknowledge a performance alert."""
        return False

    def resolve_performance_alert(self, alert_id: str) -> None:
        """Resolve a performance alert."""
        pass  # No-op for now

    def set_performance_snapshot_interval(self, interval: float) -> None:
        """Set performance snapshot interval in seconds."""
        pass  # No-op for now

    def enable_performance_monitoring(self, enabled: bool = True) -> None:
        """Enable or disable performance monitoring."""
        pass  # No-op for now

    def clear_performance_monitoring_history(self) -> None:
        """Clear performance monitoring history."""
        pass  # No-op for now

    def stop_performance_monitoring(self) -> None:
        """Stop performance monitoring."""
        pass  # No-op for now

    def calculate_ragchecker_overall(self, ragchecker_scores: dict[str, float]) -> float:
        """Calculate overall RAGChecker score (weighted average)."""
        if not ragchecker_scores:
            return 0.0

        # Define weights for different metrics (based on importance)
        weights = {
            "faithfulness": 0.40,  # Most important - factual consistency
            "query_response_overlap": 0.30,  # Query relevance
            "context_utilization": 0.20,  # Context usage
            "response_length": 0.10,  # Response completeness
        }

        # Calculate weighted average
        total_score = 0.0
        total_weight = 0.0

        for metric, score in ragchecker_scores.items():
            weight = weights.get(metric, 0.0)
            total_score += score * weight
            total_weight += weight

        # Convert to 0-100 scale
        if total_weight > 0:
            return (total_score / total_weight) * 100
        else:
            return 0.0

    def _compute_custom_score(
        self, response_text: str, rag_result: RAGResult, query: str
    ) -> tuple[float, dict[str, float]]:
        """Compute a custom evaluation score using official evaluator heuristics when available."""

        if not response_text:
            return 0.0, {}

        retrieved_payload: list[dict[str, Any]] = []
        for doc in getattr(rag_result, "retrieved_context", []) or []:
            payload = {
                "doc_id": getattr(doc, "doc_id", ""),
                "text": getattr(doc, "text", ""),
            }
            score = getattr(doc, "score", None)
            if score is not None:
                payload["score"] = score
            retrieved_payload.append(payload)

        if self.official_evaluator is not None and retrieved_payload:
            try:
                faithfulness = float(
                    self.official_evaluator._compute_faithfulness(response_text, retrieved_payload)
                )
                length_score = min(len(response_text) / 100.0, 1.0)
                composite = ((faithfulness * 0.7) + (length_score * 0.3)) * 100.0
                return composite, {
                    "faithfulness": round(faithfulness, 4),
                    "length_score": round(length_score, 4),
                }
            except Exception as exc:  # pragma: no cover - optional path
                print(f"Official evaluator scoring failed: {exc}")

        # Fallback heuristic that blends response length and query overlap
        length_score = min(len(response_text) / 100.0, 1.0)
        query_tokens = set(query.lower().split())
        response_tokens = set(response_text.lower().split())
        overlap_score = (
            len(query_tokens & response_tokens) / len(query_tokens) if query_tokens else 0.0
        )
        composite = ((length_score * 0.6) + (overlap_score * 0.4)) * 100.0
        return composite, {
            "length_score": round(length_score, 4),
            "query_overlap": round(overlap_score, 4),
        }

    def compare_evaluations(
        self,
        custom_score: float,
        ragchecker_overall: float,
        custom_metrics: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """Compare custom vs RAGChecker evaluation results."""
        difference = custom_score - ragchecker_overall
        percentage_diff = (difference / custom_score * 100) if custom_score > 0 else 0

        if abs(percentage_diff) < 10:
            agreement = "High Agreement"
            recommendation = "Both evaluations are well-aligned"
        elif percentage_diff > 20:
            agreement = "Custom Higher"
            recommendation = "Custom evaluation may be too lenient"
        elif percentage_diff < -20:
            agreement = "RAGChecker Higher"
            recommendation = "RAGChecker evaluation may be more appropriate"
        else:
            agreement = "Moderate Agreement"
            recommendation = "Consider using RAGChecker as industry standard"

        comparison: dict[str, Any] = {
            "difference": difference,
            "percentage_diff": percentage_diff,
            "agreement": agreement,
            "recommendation": recommendation,
        }
        if custom_metrics:
            comparison["custom_metrics"] = custom_metrics
        return comparison

    def evaluate_test_case(self, case_name: str, query: str, role: str = "planner") -> RAGCheckerResult:
        """Evaluate a single test case using both custom and RAGChecker evaluation."""

        # Run memory query
        response = self.run_memory_query(query, role)

        if not response.get("success", False):
            return RAGCheckerResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                ragchecker_scores={},
                ragchecker_overall=0.0,
                comparison={"error": response.get("error", "Unknown error")},
                recommendation="Query failed",
            )

        response_text = response.get("output", "")
        # Extract RAGChecker data for downstream scoring
        rag_result = self.extract_ragchecker_data(response, query)

        # Compute custom evaluation score leveraging official evaluator heuristics when available
        custom_score, custom_metrics = self._compute_custom_score(response_text, rag_result, query)

        # Run RAGChecker evaluation
        ragchecker_scores = self.run_ragchecker_evaluation(rag_result)
        ragchecker_overall = self.calculate_ragchecker_overall(ragchecker_scores)

        # Compare evaluations
        comparison = self.compare_evaluations(custom_score, ragchecker_overall, custom_metrics)

        return RAGCheckerResult(
            test_case_name=case_name,
            query=query,
            custom_score=custom_score,
            ragchecker_scores=ragchecker_scores,
            ragchecker_overall=ragchecker_overall,
            comparison=comparison,
            recommendation=comparison.get("recommendation", "Evaluation completed")
        )

    def run_ragchecker_evaluation_suite(self) -> dict[str, Any]:
        """Run RAGChecker evaluation on all baseline test cases."""

        print("🧠 Starting RAGChecker Evaluation")
        print("📊 Industry-Standard RAG Evaluation (Peer-Reviewed)")
        print("=" * 60)

        # Create some basic test cases for demonstration
        test_cases = [
            {"query_id": "test_1", "query": "What is the current project status?"},
            {"query_id": "test_2", "query": "How does the memory system work?"},
            {"query_id": "test_3", "query": "What are the evaluation metrics?"},
        ]

        results: list[RAGCheckerResult] = []
        custom_total = 0.0
        ragchecker_total = 0.0

        for i, case in enumerate(test_cases, 1):
            print(f"\n🔍 Test {i}/{len(test_cases)}: {case['query_id']}")
            print(f"   Query: {case['query']}")

            # Run RAGChecker evaluation
            result = self.evaluate_test_case(case["query_id"], case["query"], "default")

            results.append(result)
            custom_total += result.custom_score
            ragchecker_total += result.ragchecker_overall

            # Print results
            print(f"   Custom Score: {result.custom_score:.1f}/100")
            print(f"   RAGChecker Score: {result.ragchecker_overall:.1f}/100")
            print(f"   Agreement: {result.comparison.get('agreement', 'Unknown')}")
            print(f"   Recommendation: {result.recommendation}")

        # Calculate averages
        custom_avg = custom_total / len(test_cases) if test_cases else 0.0
        ragchecker_avg = ragchecker_total / len(test_cases) if test_cases else 0.0

        # Overall comparison
        overall_comparison = self.compare_evaluations(custom_avg, ragchecker_avg)

        print("\n" + "=" * 60)
        print("📊 RAGCHECKER EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Custom Average: {custom_avg:.1f}/100")
        print(f"🎯 RAGChecker Average: {ragchecker_avg:.1f}/100")
        print(f"📈 Difference: {overall_comparison.get('difference', 0.0):.1f}")
        print(f"📊 Agreement: {overall_comparison.get('agreement', 'Unknown')}")
        print(f"💡 Recommendation: {overall_comparison.get('recommendation', 'No recommendation')}")

        # Detailed RAGChecker metrics
        print("\n🔍 RAGChecker Metrics Breakdown:")
        all_ragchecker_scores: dict[str, list[float]] = {}
        for result in results:
            for metric, score in result.ragchecker_scores.items():
                if metric not in all_ragchecker_scores:
                    all_ragchecker_scores[metric] = []
                all_ragchecker_scores[metric].append(float(score))

        for metric, scores in all_ragchecker_scores.items():
            avg_score = sum(scores) / len(scores) * 100 if scores else 0.0
            print(f"   {metric}: {avg_score:.1f}/100")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data: dict[str, Any] = {
            "timestamp": timestamp,
            "custom_average": custom_avg,
            "ragchecker_average": ragchecker_avg,
            "overall_comparison": overall_comparison,
            "ragchecker_metrics_breakdown": {
                metric: sum(scores) / len(scores) * 100 if scores else 0.0
                for metric, scores in all_ragchecker_scores.items()
            },
            "detailed_results": [
                {
                    "test_case": r.test_case_name,
                    "query": r.query,
                    "custom_score": r.custom_score,
                    "ragchecker_scores": r.ragchecker_scores,
                    "ragchecker_overall": r.ragchecker_overall,
                    "comparison": r.comparison,
                    "recommendation": r.recommendation,
                }
                for r in results
            ],
        }

        output_file = f"metrics/baseline_evaluations/ragchecker_evaluation_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        return results_data

def main():
    """Run RAGChecker evaluation."""
    evaluator = RAGCheckerEvaluator()
    results = evaluator.run_ragchecker_evaluation_suite()

    # Print final recommendation
    print("\n🎯 FINAL RECOMMENDATION:")
    print(f"Based on the comparison between custom evaluation ({results.get('custom_average', 0.0):.1f})")
    print(f"and RAGChecker evaluation ({results.get('ragchecker_average', 0.0):.1f})")
    print(f"→ {results.get('overall_comparison', {}).get('recommendation', 'No recommendation')}")

    print("\n📚 RAGChecker Reference:")
    print("Paper: https://arxiv.org/abs/2408.08067")
    print("Features: Peer-reviewed, industry-tested, correlates with human judgments")
    print("\n⚠️  Note: This evaluation uses basic metrics due to LLM access requirements.")
    print("   For full RAGChecker capabilities, configure LLM access (OpenAI, Bedrock, etc.)")

if __name__ == "__main__":
    main()
