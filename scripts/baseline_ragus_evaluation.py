#!/usr/bin/env python3
"""
Baseline RAGUS Evaluation System

This module provides stable, version-controlled baseline evaluations for the memory system.
The evaluation criteria are fixed and don't change over time, ensuring reliable progress measurement.

Version: 1.0
Created: 2025-08-30
"""

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# Import faithfulness evaluator
from faithfulness_evaluator import FaithfulnessEvaluator

# Import ground truth evaluator
from ground_truth_evaluator import GroundTruthEvaluator, GroundTruthItem


class EvaluationCategory(Enum):
    MEMORY_HIERARCHY = "memory_hierarchy"
    WORKFLOW_CHAIN = "workflow_chain"
    ROLE_SPECIFIC = "role_specific"


@dataclass
class BaselineEvaluationCase:
    """Fixed baseline evaluation case that doesn't change over time."""

    name: str
    query: str
    role: str = "planner"
    category: EvaluationCategory = EvaluationCategory.MEMORY_HIERARCHY
    expected_sources: List[str] = field(default_factory=list)
    expected_content: List[str] = field(default_factory=list)
    expected_workflow: List[str] = field(default_factory=list)
    expected_commands: List[str] = field(default_factory=list)


class BaselineEvaluator:
    """Stable baseline evaluator with fixed criteria that don't change over time."""

    def __init__(self, version: str = "1.0"):
        self.version = version
        self.memory_orchestrator_path = "scripts/unified_memory_orchestrator.py"
        self.baseline_criteria = self.load_baseline_criteria(version)
        self.faithfulness_evaluator = FaithfulnessEvaluator()
        self.ground_truth_evaluator = GroundTruthEvaluator()
        self.ground_truth_dataset = self.load_ground_truth_dataset()

    def load_baseline_criteria(self, version: str) -> Dict[str, Any]:
        """Load fixed baseline criteria for consistent evaluation."""
        return {
            "version": version,
            "scoring": {
                "sources": {"max_points": 30, "threshold": 0.8},
                "content": {"max_points": 30, "threshold": 0.7},
                "workflow": {"max_points": 15, "threshold": 0.6},
                "commands": {"max_points": 15, "threshold": 0.6},
                "faithfulness": {"max_points": 20, "threshold": 0.7},  # New RAGAS-style metric
            },
            "pass_threshold": 65,
            "bonus_points": False,  # Fixed, no bonus points
            "strict_matching": True,  # Fixed, strict matching
            "partial_credit": False,  # Fixed, no partial credit
        }

    def create_baseline_evaluation_cases(self) -> List[BaselineEvaluationCase]:
        """Create fixed baseline evaluation cases that don't change over time."""
        cases = []

        # 1. Memory Hierarchy Tests (Fixed)
        cases.extend(
            [
                BaselineEvaluationCase(
                    name="Current Project Status Query",
                    query="What is the current project status and backlog priorities?",
                    role="planner",
                    category=EvaluationCategory.MEMORY_HIERARCHY,
                    expected_sources=["100_cursor-memory-context.md", "000_backlog.md"],
                    expected_content=["current sprint", "backlog items", "priorities"],
                ),
                BaselineEvaluationCase(
                    name="PRD Creation Workflow",
                    query="How do I create a new PRD for a feature?",
                    role="planner",
                    category=EvaluationCategory.MEMORY_HIERARCHY,
                    expected_sources=["001_create-prd.md", "400_system-overview.md"],
                    expected_content=["prd", "product requirements", "create prd"],
                ),
                BaselineEvaluationCase(
                    name="DSPy Integration Patterns",
                    query="What are the DSPy integration patterns and optimization techniques?",
                    role="planner",
                    category=EvaluationCategory.MEMORY_HIERARCHY,
                    expected_sources=["400_07_ai-frameworks-dspy.md", "104_dspy-development-context.md"],
                    expected_content=["DSPy signatures", "optimization", "multi-agent system"],
                ),
            ]
        )

        # 2. Workflow Chain Tests (Fixed)
        cases.extend(
            [
                BaselineEvaluationCase(
                    name="Complete Development Workflow",
                    query="I want to implement a new feature for memory optimization. What's the complete workflow?",
                    role="planner",
                    category=EvaluationCategory.WORKFLOW_CHAIN,
                    expected_sources=["003_process-task-list.md", "400_system-overview.md"],
                    expected_workflow=["backlog intake → PRD creation → task generation → execution → archive"],
                    expected_commands=[
                        "python3 scripts/single_doorway.py generate",
                        "python3 scripts/unified_memory_orchestrator.py",
                    ],
                    expected_content=["single_doorway.py", "unified_memory_orchestrator.py", "workflow chain"],
                ),
                BaselineEvaluationCase(
                    name="Interrupted Session Continuation",
                    query="How do I continue an interrupted development session?",
                    role="planner",
                    category=EvaluationCategory.WORKFLOW_CHAIN,
                    expected_sources=["003_process-task-list.md", "100_cursor-memory-context.md"],
                    expected_workflow=["memory rehydration → context restoration → task continuation"],
                    expected_commands=["python3 scripts/single_doorway.py continue B-XXX"],
                    expected_content=["continue", "backlog item", "session", "interrupted"],
                ),
            ]
        )

        # 3. Role-Specific Tests (Fixed)
        cases.extend(
            [
                BaselineEvaluationCase(
                    name="Planner Role - Development Priorities",
                    query="What are our current development priorities and roadmap?",
                    role="planner",
                    category=EvaluationCategory.ROLE_SPECIFIC,
                    expected_sources=["000_backlog.md", "400_00_getting-started-and-index.md"],
                    expected_content=["backlog", "roadmap", "sprint planning", "dependencies"],
                ),
                BaselineEvaluationCase(
                    name="Implementer Role - DSPy Implementation",
                    query="How do I implement DSPy modules and optimize performance?",
                    role="implementer",
                    category=EvaluationCategory.ROLE_SPECIFIC,
                    expected_sources=["400_07_ai-frameworks-dspy.md", "104_dspy-development-context.md"],
                    expected_content=["coding standards", "testing", "integration", "LabeledFewShot"],
                ),
                BaselineEvaluationCase(
                    name="Researcher Role - Memory System Analysis",
                    query="What are the latest memory system optimizations and research findings?",
                    role="researcher",
                    category=EvaluationCategory.ROLE_SPECIFIC,
                    expected_sources=["400_06_memory-and-context-systems.md", "500_research/"],
                    expected_content=["memory system", "optimization", "lean hybrid", "context management"],
                ),
                BaselineEvaluationCase(
                    name="Coder Role - Codebase Structure",
                    query="What's the current codebase structure and how do I navigate it?",
                    role="coder",
                    category=EvaluationCategory.ROLE_SPECIFIC,
                    expected_sources=["400_system-overview.md", "dspy-rag-system/README.md"],
                    expected_content=["file organization", "testing", "deployment", "dspy-rag-system"],
                ),
            ]
        )

        return cases

    def run_memory_query(self, query: str, role: str = "planner") -> Dict[str, Any]:
        """Run a memory query using the unified orchestrator."""
        env = os.environ.copy()
        env["POSTGRES_DSN"] = "mock://test"

        cmd = [
            "python3",
            self.memory_orchestrator_path,
            "--systems",
            "ltst",
            "cursor",
            "go_cli",
            "prime",
            "--role",
            role,
            "--format",
            "json",
            query,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)

            if result.returncode == 0:
                return {"success": True, "output": result.stdout, "error": None}
            else:
                return {"success": False, "output": result.stdout, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Query timed out after 60 seconds"}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

    def _extract_retrieved_context(self, response: Dict[str, Any]) -> str:
        """Extract retrieved context from memory system response for faithfulness evaluation."""
        try:
            # Parse the response to get retrieved context
            response_data = json.loads(response["output"])

            # Try to extract context from different possible fields
            context_sources = []

            # Check for LTST memory content
            if "ltst_memory" in response_data:
                context_sources.append(response_data["ltst_memory"])

            # Check for Cursor memory content
            if "cursor_memory" in response_data:
                context_sources.append(response_data["cursor_memory"])

            # Check for Go CLI memory content
            if "go_cli_memory" in response_data:
                context_sources.append(response_data["go_cli_memory"])

            # Check for Prime memory content
            if "prime_memory" in response_data:
                context_sources.append(response_data["prime_memory"])

            # Check for formatted output (fallback)
            if "formatted_output" in response_data:
                context_sources.append(response_data["formatted_output"])

            # Combine all context sources
            if context_sources:
                return " ".join(context_sources)
            else:
                # Fallback to raw output
                return response["output"]

        except Exception:
            # If parsing fails, use raw output as context
            return response["output"]

    def load_ground_truth_dataset(self) -> Dict[str, Any]:
        """Load ground truth dataset for evaluation."""
        try:
            with open("config/baseline_evaluations/ground_truth_dataset.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load ground truth dataset: {e}")
            return {"ground_truth_items": []}

    def get_ground_truth_item(self, case_name: str) -> Optional[GroundTruthItem]:
        """Get ground truth item for a specific test case."""
        for item in self.ground_truth_dataset.get("ground_truth_items", []):
            if item["name"] == case_name:
                return GroundTruthItem(
                    query=item["query"],
                    expected_answer=item["expected_answer"],
                    key_facts=item["key_facts"],
                    critical_information=item["critical_information"],
                    context_requirements=item["context_requirements"],
                )
        return None

    def evaluate_response(self, case: BaselineEvaluationCase, response: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a response using fixed baseline criteria."""

        if not response["success"]:
            return {"score": 0, "passed": False, "errors": [response["error"]], "details": "Query failed to execute"}

        # Parse the response
        try:
            response_data = json.loads(response["output"])
            response_text = response_data.get("formatted_output", "")
        except json.JSONDecodeError:
            response_text = response["output"]

        score = 0
        errors = []
        details = []

        # Fixed baseline evaluation logic - no changes over time

        # Check for expected sources (30 points max)
        if case.expected_sources:
            source_score = 0
            for source in case.expected_sources:
                if source.lower() in response_text.lower():
                    source_score += 15
                else:
                    errors.append(f"Missing expected source: {source}")
            score += min(source_score, 30)
            details.append(f"Source coverage: {source_score}/30")

        # Check for expected content (30 points max)
        if case.expected_content:
            content_score = 0
            for content in case.expected_content:
                if content.lower() in response_text.lower():
                    content_score += 10
                else:
                    errors.append(f"Missing expected content: {content}")
            score += min(content_score, 30)
            details.append(f"Content coverage: {content_score}/30")

        # Check for expected workflow (15 points max)
        if case.expected_workflow:
            workflow_score = 0
            for workflow in case.expected_workflow:
                if workflow.lower() in response_text.lower():
                    workflow_score += 15
                else:
                    errors.append(f"Missing expected workflow: {workflow}")
            score += min(workflow_score, 15)
            details.append(f"Workflow coverage: {workflow_score}/15")

            # Check for expected commands (15 points max)
        if case.expected_commands:
            command_score = 0
            for command in case.expected_commands:
                if command.lower() in response_text.lower():
                    command_score += 7.5
                else:
                    errors.append(f"Missing expected command: {command}")
            score += min(command_score, 15)
            details.append(f"Command coverage: {command_score}/15")

        # Check faithfulness (20 points max) - RAGAS-style evaluation
        faithfulness_score = 0
        try:
            # Get retrieved context from memory system response
            retrieved_context = self._extract_retrieved_context(response)

            # Evaluate faithfulness
            faithfulness_result = self.faithfulness_evaluator.evaluate_faithfulness(response_text, retrieved_context)
            faithfulness_score = faithfulness_result.faithfulness_score * 20  # Convert to points

            details.append(
                f"Faithfulness: {faithfulness_result.faithfulness_score:.2f}/1.00 ({faithfulness_score:.1f}/20)"
            )
            details.append(f"Claims: {faithfulness_result.verified_claims}/{faithfulness_result.total_claims} verified")

            if faithfulness_result.hallucinated_claims > 0:
                errors.append(f"Hallucinated claims detected: {faithfulness_result.hallucinated_claims}")

        except Exception as e:
            errors.append(f"Faithfulness evaluation failed: {str(e)}")
            details.append("Faithfulness: ERROR (0/20)")

        score += faithfulness_score

        # Check ground truth evaluation (20 points max) - RAGAS-style context recall and completeness
        ground_truth_score = 0
        try:
            # Get ground truth item for this test case
            ground_truth_item = self.get_ground_truth_item(case.name)

            if ground_truth_item:
                # Get retrieved context
                retrieved_context = self._extract_retrieved_context(response)

                # Evaluate ground truth
                ground_truth_result = self.ground_truth_evaluator.evaluate_ground_truth(
                    ground_truth_item, retrieved_context, response_text
                )

                # Convert to points (overall score * 20)
                ground_truth_score = ground_truth_result.overall_score * 20

                details.append(
                    f"Ground Truth: {ground_truth_result.overall_score:.2f}/1.00 ({ground_truth_score:.1f}/20)"
                )
                details.append(
                    f"Context Recall: {ground_truth_result.context_recall_score:.2f}, Completeness: {ground_truth_result.answer_completeness_score:.2f}"
                )

                if ground_truth_result.overall_score < 0.7:
                    errors.append(f"Poor ground truth alignment: {ground_truth_result.overall_assessment}")

            else:
                details.append("Ground Truth: No ground truth data available (0/20)")

        except Exception as e:
            errors.append(f"Ground truth evaluation failed: {str(e)}")
            details.append("Ground Truth: ERROR (0/20)")

        score += ground_truth_score

        return {
            "score": score,
            "passed": score >= self.baseline_criteria["pass_threshold"],
            "errors": errors,
            "details": details,
            "response_length": len(response_text),
            "faithfulness_result": faithfulness_result if "faithfulness_result" in locals() else None,
            "ground_truth_result": ground_truth_result if "ground_truth_result" in locals() else None,
        }

    def run_baseline_evaluation(self) -> Dict[str, Any]:
        """Run the complete baseline RAGUS evaluation."""

        cases = self.create_baseline_evaluation_cases()

        print("🧠 Starting Baseline RAGUS Evaluation")
        print(f"📊 Version: {self.version}")
        print(f"📋 Testing {len(cases)} baseline cases")
        print("=" * 60)

        results = {
            "timestamp": time.time(),
            "version": self.version,
            "total_cases": len(cases),
            "passed_cases": 0,
            "failed_cases": 0,
            "total_score": 0,
            "category_scores": {},
            "case_results": [],
        }

        for i, case in enumerate(cases, 1):
            print(f"\n🔍 Test {i}/{len(cases)}: {case.name}")
            print(f"   Query: {case.query}")
            print(f"   Role: {case.role}")
            print(f"   Category: {case.category.value}")

            # Run the memory query
            response = self.run_memory_query(case.query, case.role)

            # Evaluate the response using fixed baseline criteria
            evaluation = self.evaluate_response(case, response)

            # Store results
            case_result = {
                "name": case.name,
                "query": case.query,
                "role": case.role,
                "category": case.category.value,
                "score": evaluation["score"],
                "passed": evaluation["passed"],
                "errors": evaluation["errors"],
                "details": evaluation["details"],
                "response_length": evaluation["response_length"],
            }

            results["case_results"].append(case_result)
            results["total_score"] += evaluation["score"]

            if evaluation["passed"]:
                results["passed_cases"] += 1
                print(f"   ✅ PASSED (Score: {evaluation['score']}/100)")
            else:
                results["failed_cases"] += 1
                print(f"   ❌ FAILED (Score: {evaluation['score']}/100)")

        # Calculate category scores
        category_totals = {}
        category_counts = {}

        for case_result in results["case_results"]:
            category = case_result["category"]
            if category not in category_totals:
                category_totals[category] = 0
                category_counts[category] = 0
            category_totals[category] += case_result["score"]
            category_counts[category] += 1

        for category in category_totals:
            results["category_scores"][category] = {
                "total": category_totals[category],
                "count": category_counts[category],
                "average": category_totals[category] / category_counts[category],
            }

        # Calculate overall average
        results["average_score"] = results["total_score"] / len(cases)
        results["pass_rate"] = results["passed_cases"] / len(cases)

        # Determine RAGUS level
        if results["average_score"] >= 85:
            results["ragus_level"] = "🥇 EXCELLENT"
        elif results["average_score"] >= 80:
            results["ragus_level"] = "🥈 VERY GOOD"
        elif results["average_score"] >= 75:
            results["ragus_level"] = "🥉 GOOD"
        elif results["average_score"] >= 70:
            results["ragus_level"] = "📊 FAIR"
        else:
            results["ragus_level"] = "⚠️ NEEDS WORK"

        # Print summary
        print("\n" + "=" * 60)
        print("📊 BASELINE RAGUS EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Overall Score: {results['average_score']:.1f}/100")
        print(f"✅ Pass Rate: {results['pass_rate']:.1%} ({results['passed_cases']}/{results['total_cases']})")
        print(f"🏆 RAGUS Level: {results['ragus_level']}")
        print(f"📋 Version: {self.version}")

        # Category breakdown
        for category, scores in results["category_scores"].items():
            print(f"🎭 {category.replace('_', ' ').title()}: {scores['average']:.1f}/100")

        return results

    def save_baseline_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> None:
        """Save baseline evaluation results to a JSON file."""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            metrics_dir = "metrics/baseline_ragus_evaluations"
            os.makedirs(metrics_dir, exist_ok=True)
            filename = os.path.join(metrics_dir, f"baseline_ragus_v{self.version}_{timestamp}.json")

        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"💾 Baseline results saved to: {filename}")


def main():
    """Main function to run baseline RAGUS evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Run baseline RAGUS evaluation")
    parser.add_argument("--version", default="1.0", help="Baseline version to use")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Create baseline evaluator
    evaluator = BaselineEvaluator(version=args.version)

    # Run baseline evaluation
    results = evaluator.run_baseline_evaluation()

    # Save results
    evaluator.save_baseline_results(results, args.output)

    return results


if __name__ == "__main__":
    main()
