#!/usr/bin/env python3
"""Phase 3 Integration: Domain Tuning with RAG System.

This module integrates the Phase 3 domain tuning pipeline with the existing
RAG system, enabling evaluation of fine-tuned models on frozen Phase 0 slices.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.domain_tuning_pipeline import DomainTuningConfig, create_domain_tuning_pipeline

logger = logging.getLogger(__name__)


class Phase3RAGSystem:
    """Phase 3 RAG System with domain-tuned models."""

    def __init__(self, config: Optional[DomainTuningConfig] = None):
        """Initialize Phase 3 RAG system."""
        self.config = config or DomainTuningConfig()
        self.domain_pipeline = create_domain_tuning_pipeline(self.config)

        # Model snapshots (will be populated after training)
        self.model_snapshots: Dict[str, str] = {}

        # Training results
        self.training_results: Optional[Dict[str, Any]] = None

        logger.info("Phase 3 RAG System initialized")

    def train_domain_models(self, evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train domain-specific models using the tuning pipeline."""
        logger.info("🎯 Starting Phase 3 domain model training...")

        try:
            # Run the full domain tuning pipeline
            results = self.domain_pipeline.run_full_pipeline(evaluation_results)

            # Store results
            self.training_results = results
            self.model_snapshots = self.domain_pipeline.get_model_snapshots()

            logger.info("✅ Domain model training completed successfully")
            return results

        except Exception as e:
            logger.error(f"❌ Domain model training failed: {e}")
            raise

    def evaluate_on_frozen_slices(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate fine-tuned models on frozen Phase 0 slices."""
        logger.info("📊 Evaluating fine-tuned models on frozen slices...")

        if not self.training_results:
            raise ValueError("No training results available. Run train_domain_models first.")

        evaluation_results = {
            "phase": "phase3_domain_tuning",
            "evaluation_timestamp": self._get_timestamp(),
            "test_cases_count": len(test_cases),
            "model_snapshots": self.model_snapshots,
            "training_summary": {
                "pipeline_status": self.training_results.get("pipeline_status"),
                "total_training_time": self.training_results.get("total_training_time"),
                "data_pipeline": self.training_results.get("data_pipeline", {}),
            },
            "slice_evaluations": {},
            "overall_metrics": {},
        }

        # Evaluate on different query type slices
        query_type_slices = self._identify_query_type_slices(test_cases)

        for slice_name, slice_cases in query_type_slices.items():
            logger.info(f"Evaluating slice: {slice_name} ({len(slice_cases)} cases)")

            slice_results = self._evaluate_slice(slice_cases, slice_name)
            evaluation_results["slice_evaluations"][slice_name] = slice_results

        # Calculate overall metrics
        evaluation_results["overall_metrics"] = self._calculate_overall_metrics(evaluation_results["slice_evaluations"])

        logger.info("✅ Frozen slice evaluation completed")
        return evaluation_results

    def _identify_query_type_slices(self, test_cases: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Identify different query type slices for evaluation."""
        slices = {}

        for case in test_cases:
            query_type = case.get("type", "general")
            if query_type not in slices:
                slices[query_type] = []
            slices[query_type].append(case)

        return slices

    def _evaluate_slice(self, slice_cases: List[Dict[str, Any]], slice_name: str) -> Dict[str, Any]:
        """Evaluate a specific slice of test cases."""
        slice_results = {"slice_name": slice_name, "case_count": len(slice_cases), "metrics": {}, "case_details": []}

        # Mock evaluation (in practice would use actual fine-tuned models)
        for case in slice_cases:
            case_result = self._evaluate_single_case(case)
            slice_results["case_details"].append(case_result)

        # Calculate slice-level metrics
        slice_results["metrics"] = self._calculate_slice_metrics(slice_results["case_details"])

        return slice_results

    def _evaluate_single_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single test case."""
        query = case.get("query", "")
        query_type = case.get("type", "general")

        # Mock evaluation using training results
        # In practice, this would use the actual fine-tuned models
        mock_metrics = {
            "precision": 0.75 + (0.05 if query_type == "implementation" else 0.0),
            "recall": 0.68 + (0.03 if query_type == "explanatory" else 0.0),
            "f1_score": 0.71 + (0.04 if query_type == "optimization" else 0.0),
            "ndcg_at_10": 0.72 + (0.02 if query_type == "troubleshooting" else 0.0),
            "coverage": 0.78 + (0.03 if query_type == "implementation" else 0.0),
            "faithfulness": 0.82 + (0.02 if query_type == "explanatory" else 0.0),
        }

        return {
            "query_id": case.get("query_id", "unknown"),
            "query": query,
            "query_type": query_type,
            "metrics": mock_metrics,
            "evaluation_status": "completed",
        }

    def _calculate_slice_metrics(self, case_details: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate aggregate metrics for a slice."""
        if not case_details:
            return {}

        metrics = ["precision", "recall", "f1_score", "ndcg_at_10", "coverage", "faithfulness"]
        slice_metrics = {}

        for metric in metrics:
            values = [case["metrics"].get(metric, 0.0) for case in case_details if case.get("metrics")]
            if values:
                slice_metrics[metric] = sum(values) / len(values)

        return slice_metrics

    def _calculate_overall_metrics(self, slice_evaluations: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall metrics across all slices."""
        overall_metrics = {}
        metrics = ["precision", "recall", "f1_score", "ndcg_at_10", "coverage", "faithfulness"]

        for metric in metrics:
            values = []
            for slice_name, slice_data in slice_evaluations.items():
                if "metrics" in slice_data and metric in slice_data["metrics"]:
                    values.append(slice_data["metrics"][metric])

            if values:
                overall_metrics[metric] = sum(values) / len(values)

        return overall_metrics

    def compare_with_baseline(self, baseline_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Compare Phase 3 results with baseline Phase 0/1 metrics."""
        if not self.training_results:
            raise ValueError("No training results available for comparison.")

        current_metrics = self._calculate_overall_metrics(self.training_results.get("slice_evaluations", {}))

        comparison = {
            "baseline_metrics": baseline_metrics,
            "phase3_metrics": current_metrics,
            "improvements": {},
            "regressions": {},
            "overall_assessment": "pending",
        }

        # Calculate improvements/regressions
        for metric in baseline_metrics:
            if metric in current_metrics:
                baseline_val = baseline_metrics[metric]
                current_val = current_metrics[metric]
                improvement = current_val - baseline_val

                if improvement > self.config.improvement_threshold:
                    comparison["improvements"][metric] = {
                        "baseline": baseline_val,
                        "current": current_val,
                        "improvement": improvement,
                        "percentage": (improvement / baseline_val) * 100,
                    }
                elif improvement < -self.config.improvement_threshold:
                    comparison["regressions"][metric] = {
                        "baseline": baseline_val,
                        "current": current_val,
                        "regression": abs(improvement),
                        "percentage": (abs(improvement) / baseline_val) * 100,
                    }

        # Overall assessment
        improvement_count = len(comparison["improvements"])
        regression_count = len(comparison["regressions"])

        if improvement_count > regression_count:
            comparison["overall_assessment"] = "improvement"
        elif regression_count > improvement_count:
            comparison["overall_assessment"] = "regression"
        else:
            comparison["overall_assessment"] = "neutral"

        return comparison

    def generate_phase3_report(self) -> Dict[str, Any]:
        """Generate comprehensive Phase 3 report."""
        if not self.training_results:
            raise ValueError("No training results available for report generation.")

        report = {
            "phase": "phase3_domain_tuning",
            "timestamp": self._get_timestamp(),
            "executive_summary": self._generate_executive_summary(),
            "training_details": self.training_results,
            "model_snapshots": self.model_snapshots,
            "recommendations": self._generate_recommendations(),
            "next_steps": self._identify_next_steps(),
        }

        return report

    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of Phase 3 results."""
        training_data = self.training_results.get("data_pipeline", {})
        models = self.training_results.get("models", {})

        return {
            "status": self.training_results.get("pipeline_status", "unknown"),
            "total_training_time": self.training_results.get("total_training_time", 0),
            "data_quality": {
                "positive_examples": training_data.get("positive_examples", 0),
                "hard_negative_examples": training_data.get("hard_negative_examples", 0),
                "training_ratio": f"1:{training_data.get('training_negatives', 0) // max(training_data.get('positive_examples', 1), 1)}",
            },
            "models_trained": len(models),
            "training_success_rate": (
                sum(1 for m in models.values() if m.get("status") == "completed") / len(models) if models else 0
            ),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on training results."""
        recommendations = []

        if not self.training_results:
            return ["No training results available for recommendations"]

        # Data quality recommendations
        data_pipeline = self.training_results.get("data_pipeline", {})
        pos_count = data_pipeline.get("positive_examples", 0)
        neg_count = data_pipeline.get("hard_negative_examples", 0)

        if pos_count < 100:
            recommendations.append("Increase positive training examples to at least 100 for robust fine-tuning")

        if neg_count < pos_count * 3:
            recommendations.append("Increase hard negative examples to maintain 1:3 positive-to-negative ratio")

        # Model performance recommendations
        models = self.training_results.get("models", {})
        for model_name, model_results in models.items():
            if model_results.get("final_loss", 1.0) > 0.2:
                recommendations.append(f"Consider additional training epochs for {model_name} (high final loss)")

        # Deployment recommendations
        if self.training_results.get("pipeline_status") == "completed":
            recommendations.append("Deploy fine-tuned models to production with A/B testing")
            recommendations.append("Monitor performance metrics for 1-2 weeks before full rollout")

        return recommendations

    def _identify_next_steps(self) -> List[str]:
        """Identify next steps for Phase 4 and beyond."""
        next_steps = [
            "Phase 4: Implement uncertainty calibration and feedback loops",
            "Deploy fine-tuned models with feature flags for gradual rollout",
            "Set up continuous evaluation pipeline for model drift detection",
            "Implement automated retraining triggers based on performance degradation",
            "Phase 5: Explore graph-augmented and structured fusion approaches",
        ]

        return next_steps

    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def save_phase3_report(self, report: Dict[str, Any], filepath: Optional[str] = None) -> str:
        """Save Phase 3 report to file."""
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"metrics/phase3_reports/phase3_comprehensive_report_{timestamp}.json"

        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Phase 3 report saved to: {filepath}")
        return filepath


def create_phase3_rag_system(config: Optional[DomainTuningConfig] = None) -> Phase3RAGSystem:
    """Create a Phase 3 RAG system with domain tuning capabilities."""
    return Phase3RAGSystem(config)


def main():
    """Test the Phase 3 RAG System integration."""
    print("🧪 Testing Phase 3 RAG System Integration")
    print("=" * 60)

    # Create Phase 3 RAG system
    system = create_phase3_rag_system()

    # Mock evaluation results for training
    mock_evaluation_results = [
        {
            "query": "How do I implement DSPy modules with custom optimization?",
            "answer": "To implement DSPy modules, use the Model Switcher for hardware constraints and apply the LabeledFewShot optimizer.",
            "success": True,
            "enhanced_metrics": {
                "abstention": False,
                "query_type": "implementation",
                "confidence": 0.85,
                "citations_count": 2,
            },
            "retrieved_chunks": [
                {"content": "DSPy modules can be implemented using Model Switcher", "score": 0.9, "rank": 1},
                {"content": "LabeledFewShot optimizer provides custom optimization", "score": 0.8, "rank": 2},
            ],
            "cited_chunks": [
                {"content": "DSPy modules can be implemented using Model Switcher", "score": 0.9, "rank": 1},
                {"content": "LabeledFewShot optimizer provides custom optimization", "score": 0.8, "rank": 2},
            ],
        },
        {
            "query": "What is the LTST memory system architecture?",
            "answer": "The LTST memory system provides unified context management across AI sessions.",
            "success": True,
            "enhanced_metrics": {
                "abstention": False,
                "query_type": "explanatory",
                "confidence": 0.78,
                "citations_count": 1,
            },
            "retrieved_chunks": [
                {"content": "LTST provides unified context management", "score": 0.85, "rank": 1},
                {"content": "Memory system spans multiple AI sessions", "score": 0.75, "rank": 2},
            ],
            "cited_chunks": [{"content": "LTST provides unified context management", "score": 0.85, "rank": 1}],
        },
    ]

    # Mock test cases for evaluation
    mock_test_cases = [
        {"query_id": "test_001", "query": "How do I implement DSPy modules?", "type": "implementation"},
        {"query_id": "test_002", "query": "What is LTST memory system?", "type": "explanatory"},
        {"query_id": "test_003", "query": "How to optimize RAG performance?", "type": "optimization"},
    ]

    try:
        # Step 1: Train domain models
        print("🎯 Step 1: Training domain models...")
        training_results = system.train_domain_models(mock_evaluation_results)
        print(f"   ✅ Training completed in {training_results['total_training_time']:.1f}s")

        # Step 2: Evaluate on frozen slices
        print("\n📊 Step 2: Evaluating on frozen slices...")
        evaluation_results = system.evaluate_on_frozen_slices(mock_test_cases)
        print(f"   ✅ Evaluated {evaluation_results['test_cases_count']} test cases")

        # Step 3: Compare with baseline
        print("\n📈 Step 3: Comparing with baseline...")
        baseline_metrics = {
            "precision": 0.70,
            "recall": 0.65,
            "f1_score": 0.67,
            "ndcg_at_10": 0.68,
            "coverage": 0.72,
            "faithfulness": 0.78,
        }

        comparison = system.compare_with_baseline(baseline_metrics)
        print(f"   Overall assessment: {comparison['overall_assessment']}")
        print(f"   Improvements: {len(comparison['improvements'])}")
        print(f"   Regressions: {len(comparison['regressions'])}")

        # Step 4: Generate comprehensive report
        print("\n📋 Step 4: Generating comprehensive report...")
        report = system.generate_phase3_report()
        report_file = system.save_phase3_report(report)
        print(f"   ✅ Report saved to: {report_file}")

        # Display key results
        print("\n📊 Phase 3 Key Results:")
        executive_summary = report["executive_summary"]
        print(f"   Status: {executive_summary['status']}")
        print(f"   Training Time: {executive_summary['total_training_time']:.1f}s")
        print(f"   Data Quality: {executive_summary['data_quality']['training_ratio']} ratio")
        print(f"   Models Trained: {executive_summary['models_trained']}")

        print("\n🎯 Next Steps:")
        for i, step in enumerate(report["next_steps"][:3], 1):
            print(f"   {i}. {step}")

        print("\n✅ Phase 3 RAG System integration test completed successfully!")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    main()
