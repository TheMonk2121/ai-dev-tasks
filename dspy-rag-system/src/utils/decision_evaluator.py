"""
Decision Intelligence Evaluation Framework

This module provides comprehensive evaluation capabilities for decision retrieval quality,
including Failure@20, latency measurements, and supersedence leakage detection.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .context_merger import ContextMerger
from .conversation_storage import ConversationContext, ConversationStorage


@dataclass
class EvaluationResult:
    """Results from a decision evaluation run"""

    test_name: str
    timestamp: datetime
    total_queries: int
    failure_at_20: float
    recall_at_10: float
    precision_at_10: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    supersedence_leakage: float
    execution_time: float
    details: dict[str, Any]


@dataclass
class TestCase:
    """A test case for decision evaluation"""

    query: str
    expected_decisions: list[str]
    expected_entities: list[str] | None = None
    complexity: str = "medium"  # low, medium, high
    category: str = "general"  # decision, entity, supersedence, performance


class DecisionEvaluator:
    """
    Evaluates decision retrieval quality using industry-standard metrics.

    Implements:
    - Failure@20 calculation
    - Latency breakdown (p50/p95/p99)
    - Supersedence leakage detection
    - Comprehensive evaluation reporting
    """

    def __init__(self, storage: ConversationStorage, merger: ContextMerger):
        self.storage = storage
        self.merger = merger
        self.logger = logging.getLogger(__name__)

        # Evaluation configuration
        self.k_values = [5, 10, 20]  # Standard retrieval depths
        self.latency_thresholds = {
            "warm": {"p50": 5, "p95": 10, "p99": 20},  # ms
            "cold": {"p50": 50, "p95": 150, "p99": 300},  # ms
        }
        self.supersedence_leakage_threshold = 0.01  # 1%

    def evaluate_decision_retrieval(
        self, test_cases: list[TestCase], session_id: str | None = None, warm_cache: bool = True
    ) -> EvaluationResult:
        """
        Run comprehensive evaluation of decision retrieval quality.

        Args:
            test_cases: List of test cases to evaluate
            session_id: Optional session ID for context-specific evaluation
            warm_cache: Whether to use warm cache (affects latency targets)

        Returns:
            EvaluationResult with comprehensive metrics
        """
        start_time = time.time()
        self.logger.info(f"Starting decision retrieval evaluation with {len(test_cases)} test cases")

        # Initialize metrics
        total_queries = len(test_cases)
        all_latencies = []
        all_recalls = []
        all_precisions = []
        supersedence_leakage_count = 0

        # Run evaluation for each test case
        for i, test_case in enumerate(test_cases):
            self.logger.debug(f"Evaluating test case {i+1}/{total_queries}: {test_case.query[:50]}...")

            # Measure retrieval latency
            query_start = time.time()
            retrieved_decisions = self._retrieve_decisions_for_query(
                test_case.query, test_case.expected_entities, session_id
            )
            query_latency = (time.time() - query_start) * 1000  # Convert to ms
            all_latencies.append(query_latency)

            # Calculate recall and precision at different K values
            for k in self.k_values:
                if k <= len(retrieved_decisions):
                    recall = self._calculate_recall_at_k(retrieved_decisions[:k], test_case.expected_decisions)
                    precision = self._calculate_precision_at_k(retrieved_decisions[:k], test_case.expected_decisions)

                    if k == 10:  # Store for final metrics
                        all_recalls.append(recall)
                        all_precisions.append(precision)

            # Check for supersedence leakage
            if self._has_supersedence_leakage(retrieved_decisions):
                supersedence_leakage_count += 1

        # Calculate final metrics
        execution_time = time.time() - start_time
        failure_at_20 = self._calculate_failure_at_20(all_recalls)
        recall_at_10 = sum(all_recalls) / len(all_recalls) if all_recalls else 0.0
        precision_at_10 = sum(all_precisions) / len(all_precisions) if all_precisions else 0.0
        supersedence_leakage = supersedence_leakage_count / total_queries if total_queries > 0 else 0.0

        # Calculate latency percentiles
        latency_p50, latency_p95, latency_p99 = self._calculate_latency_percentiles(all_latencies)

        # Create evaluation result
        result = EvaluationResult(
            test_name=f"Decision Retrieval Evaluation - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            total_queries=total_queries,
            failure_at_20=failure_at_20,
            recall_at_10=recall_at_10,
            precision_at_10=precision_at_10,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            supersedence_leakage=supersedence_leakage,
            execution_time=execution_time,
            details={
                "test_cases": [tc.query for tc in test_cases],
                "latency_distribution": all_latencies,
                "recall_distribution": all_recalls,
                "precision_distribution": all_precisions,
                "warm_cache": warm_cache,
                "session_id": session_id,
            },
        )

        self.logger.info(f"Evaluation completed in {execution_time:.2f}s")
        self.logger.info(f"Failure@20: {failure_at_20:.3f}, Recall@10: {recall_at_10:.3f}")
        self.logger.info(f"Latency p95: {latency_p95:.2f}ms, Supersedence leakage: {supersedence_leakage:.3f}")

        return result

    def _retrieve_decisions_for_query(
        self, query: str, expected_entities: list[str] | None, session_id: str | None
    ) -> list[ConversationContext]:
        """Retrieve decisions for a specific query using direct search"""
        try:
            # Use direct search with session_id=None for cross-thread evaluation
            search_results = self.storage.search_decisions(query, session_id=None, limit=20)

            # Debug logging
            canonical_query = self.storage._canonicalize_query(query)
            print(f'\nQ: "{query}" (canonical: "{canonical_query}")')
            print("Top candidates:")
            print(" id     key                         head               bm25   cos   r_bm25 r_vec status")
            print(" -----  --------------------------  -----------------  -----  ----  ------ ----- ------")

            for i, result in enumerate(search_results[:10]):
                decision_key = result.get("decision_key", "N/A")
                decision_head = result.get("decision_head", "N/A")
                bm25_score = result.get("bm25_score", 0.0)
                vector_score = result.get("vector_score", 0.0)
                status = result.get("decision_status", "N/A")
                print(
                    f" {i+1:2d}     {decision_key:<25}  {decision_head:<15}  {bm25_score:.3f}  {vector_score:.3f}   N/A   N/A   {status}"
                )

            # Add per-query analysis logging
            print(f"Retrieved {len(search_results)} decisions total")
            print(f"Expected decisions: {expected_entities or []}")
            retrieved_keys = [result.get("decision_key", "") for result in search_results]
            print(f"Retrieved keys: {retrieved_keys[:5]}...")  # Show first 5

            # Convert search results to ConversationContext objects
            contexts = []
            for result in search_results[:2]:  # Cap at 2 decisions per query
                context = ConversationContext(
                    session_id=result.get("session_id", ""),
                    context_type=result.get("context_type", "decision"),
                    context_key=result.get("decision_key", result.get("context_key", "")),
                    context_value=result.get("context_value", ""),
                    relevance_score=result.get("relevance_score", 0.0),
                    metadata=result.get("metadata", {}),
                    decision_head=result.get("decision_head"),
                    decision_status=result.get("decision_status", "open"),
                    superseded_by=result.get("superseded_by"),
                    entities=result.get("entities", []),
                    files=result.get("files", []),
                )
                contexts.append(context)

            return contexts
        except Exception as e:
            self.logger.error(f"Error retrieving decisions for query '{query}': {e}")
            return []

    def _convert_merged_to_conversation_context(self, merged_ctx) -> ConversationContext:
        """Convert MergedContext to ConversationContext for compatibility"""
        # Create a ConversationContext with the merged data
        return ConversationContext(
            session_id=merged_ctx.session_id,
            context_type=merged_ctx.context_type,
            context_key=merged_ctx.context_key,
            context_value=merged_ctx.merged_content,
            relevance_score=merged_ctx.relevance_score,
            metadata=merged_ctx.metadata,
            decision_head=getattr(merged_ctx, "decision_head", None),
            decision_status=getattr(merged_ctx, "decision_status", "open") or "open",
            superseded_by=getattr(merged_ctx, "superseded_by", None),
            entities=getattr(merged_ctx, "entities", None),
            files=getattr(merged_ctx, "files", None),
        )

    def _calculate_recall_at_k(self, retrieved: list[ConversationContext], expected: list[str]) -> float:
        """Calculate recall at K for decision retrieval using decision_key"""
        if not expected:
            return 1.0  # Perfect recall if no expectations

        # Extract decision keys from retrieved contexts
        retrieved_keys = [ctx.context_key for ctx in retrieved if hasattr(ctx, "context_key") and ctx.context_key]

        # Count how many expected decisions were found (exact match on decision_key)
        found_count = sum(1 for exp in expected if exp in retrieved_keys)

        return found_count / len(expected)

    def _calculate_precision_at_k(self, retrieved: list[ConversationContext], expected: list[str]) -> float:
        """Calculate precision at K for decision retrieval using decision_key"""
        if not retrieved:
            return 0.0

        # Extract decision keys from retrieved contexts
        retrieved_keys = [ctx.context_key for ctx in retrieved if hasattr(ctx, "context_key") and ctx.context_key]

        if not retrieved_keys:
            return 0.0  # No precision if no valid decision keys

        if not expected:
            return 0.0  # No precision if no expectations

        # Count how many retrieved decisions were relevant (exact match on decision_key)
        relevant_count = sum(1 for ret in retrieved_keys if ret in expected)

        return relevant_count / len(retrieved_keys)

    def _is_semantic_match(self, expected: str, retrieved: str) -> bool:
        """Check if two decision heads are semantically similar"""
        # Simple string similarity for now - could be enhanced with embeddings
        expected_lower = expected.lower()
        retrieved_lower = retrieved.lower()

        # Exact match
        if expected_lower == retrieved_lower:
            return True

        # Contains match
        if expected_lower in retrieved_lower or retrieved_lower in expected_lower:
            return True

        # Word overlap (simple Jaccard-like)
        expected_words = set(expected_lower.split())
        retrieved_words = set(retrieved_lower.split())

        if expected_words and retrieved_words:
            overlap = len(expected_words & retrieved_words)
            union = len(expected_words | retrieved_words)
            if union > 0:
                similarity = overlap / union
                return similarity >= 0.5  # 50% word overlap threshold

        return False

    def _calculate_failure_at_20(self, recalls: list[float]) -> float:
        """Calculate Failure@20 metric (1 - average recall)"""
        if not recalls:
            return 1.0  # 100% failure if no recalls

        avg_recall = sum(recalls) / len(recalls)
        return 1.0 - avg_recall

    def _calculate_latency_percentiles(self, latencies: list[float]) -> tuple[float, float, float]:
        """Calculate p50, p95, and p99 latency percentiles"""
        if not latencies:
            return 0.0, 0.0, 0.0

        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        p50_idx = int(0.5 * n)
        p95_idx = int(0.95 * n)
        p99_idx = int(0.99 * n)

        p50 = sorted_latencies[p50_idx] if p50_idx < n else sorted_latencies[-1]
        p95 = sorted_latencies[p95_idx] if p95_idx < n else sorted_latencies[-1]
        p99 = sorted_latencies[p99_idx] if p99_idx < n else sorted_latencies[-1]

        return p50, p95, p99

    def _has_supersedence_leakage(self, retrieved_decisions: list[ConversationContext]) -> bool:
        """Check if superseded decisions are being returned inappropriately"""
        for decision in retrieved_decisions:
            if hasattr(decision, "decision_status") and decision.decision_status == "superseded":
                # Check if this superseded decision is ranked too high
                # For now, we'll consider it leakage if it's in the top 5
                if retrieved_decisions.index(decision) < 5:
                    return True
        return False

    def validate_performance_targets(self, result: EvaluationResult) -> dict[str, bool]:
        """Validate if performance targets are met"""
        targets = (
            self.latency_thresholds["warm"]
            if result.details.get("warm_cache", True)
            else self.latency_thresholds["cold"]
        )

        validation = {
            "failure_at_20_target": result.failure_at_20 <= 0.20,  # Target: ≤20%
            "supersedence_leakage_target": result.supersedence_leakage <= self.supersedence_leakage_threshold,
            "latency_p50_target": result.latency_p50 <= targets["p50"],
            "latency_p95_target": result.latency_p95 <= targets["p95"],
            "latency_p99_target": result.latency_p99 <= targets["p99"],
        }

        return validation

    def generate_evaluation_report(self, result: EvaluationResult) -> str:
        """Generate a human-readable evaluation report"""
        validation = self.validate_performance_targets(result)

        report = f"""
# Decision Retrieval Evaluation Report

## Summary
- **Test Name**: {result.test_name}
- **Timestamp**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **Total Queries**: {result.total_queries}
- **Execution Time**: {result.execution_time:.2f}s

## Quality Metrics
- **Failure@20**: {result.failure_at_20:.3f} {'✅' if validation['failure_at_20_target'] else '❌'} (Target: ≤0.20)
- **Recall@10**: {result.recall_at_10:.3f}
- **Precision@10**: {result.precision_at_10:.3f}

## Performance Metrics
- **Latency p50**: {result.latency_p50:.2f}ms {'✅' if validation['latency_p50_target'] else '❌'}
- **Latency p95**: {result.latency_p95:.2f}ms {'✅' if validation['latency_p95_target'] else '❌'}
- **Latency p99**: {result.latency_p99:.2f}ms {'✅' if validation['latency_p99_target'] else '❌'}

## Quality Targets
- **Supersedence Leakage**: {result.supersedence_leakage:.3f} {'✅' if validation['supersedence_leakage_target'] else '❌'} (Target: ≤{self.supersedence_leakage_threshold})

## Overall Status
- **All Targets Met**: {'✅' if all(validation.values()) else '❌'}
"""

        return report

    def save_evaluation_result(self, result: EvaluationResult, filepath: str) -> None:
        """Save evaluation result to JSON file"""
        try:
            # Convert datetime to string for JSON serialization
            result_dict = {
                "test_name": result.test_name,
                "timestamp": result.timestamp.isoformat(),
                "total_queries": result.total_queries,
                "failure_at_20": result.failure_at_20,
                "recall_at_10": result.recall_at_10,
                "precision_at_10": result.precision_at_10,
                "latency_p50": result.latency_p50,
                "latency_p95": result.latency_p95,
                "latency_p99": result.latency_p99,
                "supersedence_leakage": result.supersedence_leakage,
                "execution_time": result.execution_time,
                "details": result.details,
            }

            with open(filepath, "w") as f:
                json.dump(result_dict, f, indent=2)

            self.logger.info(f"Evaluation result saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving evaluation result: {e}")


def create_default_test_cases() -> list[TestCase]:
    """Create a set of default test cases for evaluation"""
    return [
        # Simple decision queries
        TestCase(
            query="What database should we use?",
            expected_decisions=["use_postgresql", "database_selection"],
            category="decision",
        ),
        TestCase(
            query="Python version for the project",
            expected_decisions=["use_python_3_11", "python_version"],
            category="decision",
        ),
        # Entity-based queries
        TestCase(
            query="Debug mode configuration",
            expected_decisions=["enable_debug_mode", "debug_configuration"],
            expected_entities=["debug", "mode"],
            category="entity",
        ),
        TestCase(
            query="Build pipeline setup",
            expected_decisions=["setup_build_pipeline", "pipeline_configuration"],
            expected_entities=["build", "pipeline"],
            category="entity",
        ),
        # Supersedence scenarios
        TestCase(
            query="Current Python version",
            expected_decisions=["use_python_3_12"],  # Should not return superseded 3.11
            category="supersedence",
        ),
        TestCase(
            query="Debug mode status",
            expected_decisions=["disable_debug_mode"],  # Should not return superseded enable
            category="supersedence",
        ),
        # Performance queries
        TestCase(
            query="Database performance optimization",
            expected_decisions=["optimize_database", "performance_tuning"],
            category="performance",
        ),
        TestCase(
            query="Caching strategy", expected_decisions=["implement_caching", "cache_strategy"], category="performance"
        ),
        # Complex queries
        TestCase(
            query="How should we handle user authentication and database connections?",
            expected_decisions=["implement_auth", "database_connections", "security_policy"],
            category="complex",
        ),
        TestCase(
            query="What's our approach to testing and deployment?",
            expected_decisions=["testing_strategy", "deployment_pipeline", "ci_cd_setup"],
            category="complex",
        ),
    ]
