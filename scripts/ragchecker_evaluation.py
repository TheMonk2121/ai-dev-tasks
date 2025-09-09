#!/usr/bin/env python3
"""
RAGChecker Evaluation System

This module implements RAGChecker evaluation as a replacement for RAGAS.
RAGChecker is a peer-reviewed, industry-tested framework that provides
fine-grained diagnostic metrics for RAG systems with strong correlation
to human judgments.

Reference: https://arxiv.org/abs/2408.08067
"""

import json
import subprocess
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

# Import RAGChecker components with type ignore for missing stubs
from ragchecker.container import RetrievedDoc  # type: ignore
from ragchecker.evaluator import RAGChecker, RAGResult, RAGResults  # type: ignore

from scripts.ragchecker_constitution_validator import create_ragchecker_validator
from scripts.ragchecker_debug_manager import create_ragchecker_debug_manager
from scripts.ragchecker_error_recovery import RAGCheckerErrorRecovery, with_error_recovery
from scripts.ragchecker_official_evaluation import OfficialRAGCheckerEvaluator
from scripts.ragchecker_performance_monitor import create_performance_monitor
from scripts.ragchecker_performance_optimizer import create_validation_optimizer, optimize_validation

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
        self.official_evaluator = OfficialRAGCheckerEvaluator()

        # Initialize constitution-aware validator
        self.constitution_validator = create_ragchecker_validator()

        # Initialize enhanced debugging manager
        self.debug_manager = create_ragchecker_debug_manager()

        # Initialize error recovery manager
        self.error_recovery = RAGCheckerErrorRecovery()

        # Initialize performance optimizer
        self.validation_optimizer = create_validation_optimizer(enable_caching=True, enable_batching=True)

        # Initialize performance monitor
        self.performance_monitor = create_performance_monitor(
            enable_alerting=True, enable_logging=True, enable_metrics_export=True
        )

        # Initialize RAGChecker with default settings
        # Note: RAGChecker requires LLM access for claim extraction and checking
        # We'll use it in a limited capacity for metrics that don't require LLM
        self.ragchecker = RAGChecker()

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
            response_data = json.loads(response["output"])
            generated_response = response_data.get("formatted_output", "")

            # Extract retrieved context
            context_sources: list[str] = []
            if "ltst_memory" in response_data:
                context_sources.append(str(response_data["ltst_memory"]))
            if "cursor_memory" in response_data:
                context_sources.append(str(response_data["cursor_memory"]))
            if "go_cli_memory" in response_data:
                context_sources.append(str(response_data["go_cli_memory"]))
            if "prime_memory" in response_data:
                context_sources.append(str(response_data["prime_memory"]))

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
            results = self.ragchecker.evaluate(rag_results, metrics="faithfulness")  # type: ignore

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
        metrics["response_length"] = min(response_length / 1000, 1.0)  # Normalize to 0-1

        # Context utilization (if we have retrieved context)
        if rag_result.retrieved_context:
            context_length = sum(len(doc.text) for doc in rag_result.retrieved_context)
            metrics["context_utilization"] = min(context_length / 1000, 1.0)
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

    @optimize_validation("constitution_validation")
    @with_error_recovery("constitution_validation")
    def validate_with_constitution(self, evaluation_data: dict[str, Any]) -> dict[str, Any]:
        """Validate RAGChecker evaluation data with constitution awareness."""
        import time

        # Create debug context for validation
        evaluation_id = f"eval_{int(time.time())}"
        debug_context = self.debug_manager.capture_ragchecker_context(
            evaluation_id=evaluation_id, evaluation_type="constitution_validation", validation_stage="start"
        )

        validation_results = {
            "input_validation": None,
            "metrics_validation": None,
            "result_validation": None,
            "overall_compliance": True,
            "total_violations": 0,
            "total_warnings": 0,
        }

        try:
            # Update debug context
            debug_context.validation_stage = "input_validation"

            # Validate input data if present
            if "input" in evaluation_data:
                start_time = time.time()
                input_validation = self.constitution_validator.validate_ragchecker_input(evaluation_data["input"])
                validation_time = time.time() - start_time

                validation_results["input_validation"] = input_validation
                if not input_validation["valid"]:
                    validation_results["overall_compliance"] = False
                    validation_results["total_violations"] += len(input_validation["errors"])
                validation_results["total_warnings"] += len(input_validation.get("warnings", []))

                # Log input validation with debug manager
                self.debug_manager.log_constitution_validation(
                    context=debug_context,
                    validation_result=input_validation,
                    compliance_score=self._extract_compliance_score(input_validation),
                )

                # Log performance metrics
                self.debug_manager.log_performance_metrics(
                    context=debug_context, metrics={"input_validation_time": validation_time}
                )

                # Record operation in performance monitor
                self.performance_monitor.record_operation(
                    operation_name="input_validation",
                    execution_time=validation_time,
                    success=True,
                    metadata={
                        "evaluation_id": evaluation_id,
                        "validation_type": "input_validation",
                        "compliance_score": self._extract_compliance_score(input_validation),
                    },
                )

            # Update debug context
            debug_context.validation_stage = "metrics_validation"

            # Validate metrics data if present
            if "metrics" in evaluation_data:
                start_time = time.time()
                metrics_validation = self.constitution_validator.validate_ragchecker_metrics(evaluation_data["metrics"])
                validation_time = time.time() - start_time

                validation_results["metrics_validation"] = metrics_validation
                if not metrics_validation["valid"]:
                    validation_results["overall_compliance"] = False
                    validation_results["total_violations"] += len(metrics_validation["errors"])
                validation_results["total_warnings"] += len(metrics_validation.get("warnings", []))

                # Log metrics validation with debug manager
                self.debug_manager.log_constitution_validation(
                    context=debug_context,
                    validation_result=metrics_validation,
                    compliance_score=self._extract_compliance_score(metrics_validation),
                )

                # Log performance metrics
                self.debug_manager.log_performance_metrics(
                    context=debug_context, metrics={"metrics_validation_time": validation_time}
                )

                # Record operation in performance monitor
                self.performance_monitor.record_operation(
                    operation_name="metrics_validation",
                    execution_time=validation_time,
                    success=True,
                    metadata={
                        "evaluation_id": evaluation_id,
                        "validation_type": "metrics_validation",
                        "compliance_score": self._extract_compliance_score(metrics_validation),
                    },
                )

            # Update debug context
            debug_context.validation_stage = "result_validation"

            # Validate result data if present
            if "result" in evaluation_data:
                start_time = time.time()
                result_validation = self.constitution_validator.validate_ragchecker_result(evaluation_data["result"])
                validation_time = time.time() - start_time

                validation_results["result_validation"] = result_validation
                if not result_validation["valid"]:
                    validation_results["overall_compliance"] = False
                    validation_results["total_violations"] += len(result_validation["errors"])
                validation_results["total_warnings"] += len(result_validation.get("warnings", []))

                # Log result validation with debug manager
                self.debug_manager.log_constitution_validation(
                    context=debug_context,
                    validation_result=result_validation,
                    compliance_score=self._extract_compliance_score(result_validation),
                )

                # Log performance metrics
                self.debug_manager.log_performance_metrics(
                    context=debug_context, metrics={"result_validation_time": validation_time}
                )

                # Record operation in performance monitor
                self.performance_monitor.record_operation(
                    operation_name="result_validation",
                    execution_time=validation_time,
                    success=True,
                    metadata={
                        "evaluation_id": evaluation_id,
                        "validation_type": "result_validation",
                        "compliance_score": self._extract_compliance_score(result_validation),
                    },
                )

            # Update debug context
            debug_context.validation_stage = "compliance_summary"

            # Add constitution compliance summary
            validation_results["constitution_summary"] = {
                "is_compliant": validation_results["overall_compliance"],
                "compliance_score": 1.0 if validation_results["overall_compliance"] else 0.3,
                "total_violations": validation_results["total_violations"],
                "total_warnings": validation_results["total_warnings"],
                "recommendations": self._extract_recommendations(validation_results),
            }

            # Log final compliance summary
            self.debug_manager.log_constitution_validation(
                context=debug_context,
                validation_result=validation_results["constitution_summary"],
                compliance_score=validation_results["constitution_summary"]["compliance_score"],
            )

            # Update performance monitor with cache hit rate from optimizer
            optimizer_summary = self.validation_optimizer.get_performance_summary()
            if "cache_hit_rate" in optimizer_summary:
                self.performance_monitor.update_metrics({"cache_hit_rate": optimizer_summary["cache_hit_rate"]})

        except Exception as e:
            validation_results["overall_compliance"] = False
            validation_results["error"] = f"Constitution validation failed: {str(e)}"

            # Calculate total execution time
            total_execution_time = time.time() - start_time

            # Log error with debug manager
            self.debug_manager.log_validation_error(
                context=debug_context,
                error=e,
                error_type="constitution_validation_failure",
                error_details={"error_message": str(e)},
            )

            # Record error in performance monitor
            self.performance_monitor.record_operation(
                operation_name="constitution_validation",
                execution_time=total_execution_time,
                success=False,
                error_type="constitution_validation_failure",
                metadata={
                    "evaluation_id": evaluation_id,
                    "error_message": str(e),
                    "validation_stage": debug_context.validation_stage,
                },
            )

            print(f"Constitution validation error: {e}")

        return validation_results

    def validate_with_constitution_and_taxonomy(self, evaluation_data: dict[str, Any]) -> dict[str, Any]:
        """Validate RAGChecker evaluation data with constitution awareness and error taxonomy."""
        # First, perform constitution validation
        validation_results = self.validate_with_constitution(evaluation_data)

        # Then, enhance with error taxonomy
        enhanced_results = self.constitution_validator.enhance_validation_with_taxonomy(validation_results)

        return enhanced_results

    def _extract_compliance_score(self, validation_result: dict[str, Any]) -> float:
        """Extract compliance score from validation result safely."""
        try:
            if validation_result.get("compliance"):
                compliance = validation_result["compliance"]
                if hasattr(compliance, "compliance_score"):
                    return compliance.compliance_score
                elif isinstance(compliance, dict):
                    return compliance.get("compliance_score", 0.0)
            return 0.0
        except Exception:
            return 0.0

    def _extract_recommendations(self, validation_results: dict[str, Any]) -> list[str]:
        """Extract recommendations from validation results."""
        recommendations = []

        for validation_type in ["input_validation", "metrics_validation", "result_validation"]:
            if validation_results[validation_type]:
                validation = validation_results[validation_type]
                for error in validation.get("errors", []):
                    if "recommendation" in error:
                        recommendations.append(error["recommendation"])

        return list(set(recommendations))  # Remove duplicates

    def get_debugging_summary(self) -> dict[str, Any]:
        """Get debugging summary for RAGChecker evaluation workflows"""
        return self.debug_manager.get_debugging_summary()

    def get_debug_context(self, evaluation_id: str) -> Any | None:
        """Get debug context for a specific evaluation"""
        # This would need to be implemented based on how we store contexts
        # For now, return the debug manager summary
        return self.debug_manager.get_debugging_summary()

    def get_error_recovery_statistics(self) -> dict[str, Any]:
        """Get error recovery statistics and performance metrics"""
        return self.error_recovery.get_recovery_statistics()

    def recover_from_validation_error(
        self, error: Exception, error_type: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Recover from a validation error using the error recovery system"""
        return self.error_recovery.recover_from_error(error=error, error_type=error_type, context=context)

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance optimization summary"""
        return self.validation_optimizer.get_performance_summary()

    def update_optimization_config(self, **config_updates) -> None:
        """Update performance optimization configuration"""
        self.validation_optimizer.update_optimization_config(**config_updates)

    def clear_performance_history(self) -> None:
        """Clear performance history"""
        self.validation_optimizer.clear_performance_history()

    def batch_validate_with_constitution(
        self, evaluation_data_batch: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], Any]:
        """Batch validate multiple evaluation data items with constitution awareness"""
        return self.validation_optimizer.batch_validate(
            self.constitution_validator.validate_ragchecker_input, evaluation_data_batch, "constitution_validation"
        )

    # Performance Monitoring Methods
    def get_performance_monitoring_summary(self) -> dict[str, Any]:
        """Get comprehensive performance monitoring summary."""
        return self.performance_monitor.get_performance_summary()

    def get_performance_history(
        self, start_time: datetime | None = None, end_time: datetime | None = None, max_points: int = 100
    ) -> list[dict[str, Any]]:
        """Get performance history within a time range."""
        return self.performance_monitor.get_performance_history(start_time, end_time, max_points)

    def export_performance_metrics(self, filepath: str, format_type: str = "json") -> bool:
        """Export performance metrics to file."""
        return self.performance_monitor.export_metrics_to_file(filepath, format_type)

    def update_performance_thresholds(self, **threshold_updates) -> None:
        """Update performance monitoring thresholds."""
        self.performance_monitor.update_thresholds(**threshold_updates)

    def add_performance_alert_callback(self, callback) -> None:
        """Add a callback function for performance alerts."""
        self.performance_monitor.add_alert_callback(callback)

    def acknowledge_performance_alert(self, alert_id: str) -> bool:
        """Acknowledge a performance alert."""
        return self.performance_monitor.acknowledge_alert(alert_id)

    def resolve_performance_alert(self, alert_id: str) -> None:
        """Resolve a performance alert."""
        self.performance_monitor.resolve_alert(alert_id)

    def set_performance_snapshot_interval(self, interval: float) -> None:
        """Set performance snapshot interval in seconds."""
        self.performance_monitor.set_snapshot_interval(interval)

    def enable_performance_monitoring(self, enabled: bool = True) -> None:
        """Enable or disable performance monitoring."""
        self.performance_monitor.enable_monitoring(enabled)

    def clear_performance_monitoring_history(self) -> None:
        """Clear performance monitoring history."""
        self.performance_monitor.clear_history()

    def stop_performance_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.performance_monitor.stop_monitoring()

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
            weight = weights.get(metric, 0.1)  # Default weight
            total_score += score * weight
            total_weight += weight

        # Convert to 0-100 scale
        if total_weight > 0:
            return (total_score / total_weight) * 100
        else:
            return 0.0

    def compare_evaluations(self, custom_score: float, ragchecker_overall: float) -> dict[str, Any]:
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

        return {
            "difference": difference,
            "percentage_diff": percentage_diff,
            "agreement": agreement,
            "recommendation": recommendation,
        }

    def evaluate_test_case(self, case_name: str, query: str, role: str = "planner") -> RAGCheckerResult:
        """Evaluate a single test case using both custom and RAGChecker evaluation."""

        # Run memory query
        response = self.run_memory_query(query, role)

        if not response["success"]:
            return RAGCheckerResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                ragchecker_scores={},
                ragchecker_overall=0.0,
                comparison={"error": response["error"], "agreement": "Query Failed", "recommendation": "Query failed"},
                recommendation="Query failed",
            )

        # Find the case by query_id
        baseline_cases = self.official_evaluator.create_official_test_cases()
        case = None
        for c in baseline_cases:
            if c.query_id == case_name:
                case = c
                break

        if case is None:
            return RAGCheckerResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                ragchecker_scores={},
                ragchecker_overall=0.0,
                comparison={
                    "error": "Case not found",
                    "agreement": "Case Not Found",
                    "recommendation": "Case not found",
                },
                recommendation="Case not found",
            )

        # Run custom evaluation using fallback method
        try:
            fallback_data: list[dict[str, Any]] = [
                {"query": case.query, "response": response, "gt_answer": case.gt_answer, "retrieved_context": []}
            ]
            custom_result = self.official_evaluator.create_fallback_evaluation(fallback_data)
            custom_score = float(custom_result["overall_metrics"]["f1_score"])
        except Exception as e:
            print(f"Custom evaluation failed: {e}")
            custom_score = 0.0

        # Extract RAGChecker data
        rag_result = self.extract_ragchecker_data(response, query)

        # Run RAGChecker evaluation
        ragchecker_scores = self.run_ragchecker_evaluation(rag_result)
        ragchecker_overall = self.calculate_ragchecker_overall(ragchecker_scores)

        # Compare evaluations
        comparison = self.compare_evaluations(custom_score, ragchecker_overall)

        return RAGCheckerResult(
            test_case_name=case_name,
            query=query,
            custom_score=custom_score,
            ragchecker_scores=ragchecker_scores,
            ragchecker_overall=ragchecker_overall,
            comparison=comparison,
            recommendation=comparison["recommendation"],
        )

    def run_ragchecker_evaluation_suite(self) -> dict[str, Any]:
        """Run RAGChecker evaluation on all baseline test cases."""

        print("🧠 Starting RAGChecker Evaluation")
        print("📊 Industry-Standard RAG Evaluation (Peer-Reviewed)")
        print("=" * 60)

        # Get baseline test cases
        baseline_cases = self.official_evaluator.create_official_test_cases()

        results: list[RAGCheckerResult] = []
        custom_total = 0.0
        ragchecker_total = 0.0

        for i, case in enumerate(baseline_cases, 1):
            print(f"\n🔍 Test {i}/{len(baseline_cases)}: {case.query_id}")
            print(f"   Query: {case.query}")

            # Run RAGChecker evaluation
            result = self.evaluate_test_case(case.query_id, case.query, "default")

            results.append(result)
            custom_total += result.custom_score
            ragchecker_total += result.ragchecker_overall

            # Print results
            print(f"   Custom Score: {result.custom_score:.1f}/100")
            print(f"   RAGChecker Score: {result.ragchecker_overall:.1f}/100")
            print(f"   Agreement: {result.comparison['agreement']}")
            print(f"   Recommendation: {result.recommendation}")

        # Calculate averages
        custom_avg = custom_total / len(baseline_cases) if baseline_cases else 0.0
        ragchecker_avg = ragchecker_total / len(baseline_cases) if baseline_cases else 0.0

        # Overall comparison
        overall_comparison = self.compare_evaluations(custom_avg, ragchecker_avg)

        print("\n" + "=" * 60)
        print("📊 RAGCHECKER EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Custom Average: {custom_avg:.1f}/100")
        print(f"🎯 RAGChecker Average: {ragchecker_avg:.1f}/100")
        print(f"📈 Difference: {overall_comparison['difference']:.1f} points")
        print(f"📊 Agreement: {overall_comparison['agreement']}")
        print(f"💡 Recommendation: {overall_comparison['recommendation']}")

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
    print(f"Based on the comparison between custom evaluation ({results['custom_average']:.1f}/100)")
    print(f"and RAGChecker evaluation ({results['ragchecker_average']:.1f}/100):")
    print(f"→ {results['overall_comparison']['recommendation']}")

    print("\n📚 RAGChecker Reference:")
    print("Paper: https://arxiv.org/abs/2408.08067")
    print("Features: Peer-reviewed, industry-tested, correlates with human judgments")
    print("\n⚠️  Note: This evaluation uses basic metrics due to LLM access requirements.")
    print("   For full RAGChecker capabilities, configure LLM access (OpenAI, Bedrock, etc.)")


if __name__ == "__main__":
    main()
