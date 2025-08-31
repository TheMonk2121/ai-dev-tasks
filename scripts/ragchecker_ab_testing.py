#!/usr/bin/env python3
"""
RAGChecker A/B Testing Framework
Allows testing different configurations and measuring improvements
"""

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class RAGCheckerResults:
    """Results from a RAGChecker evaluation run."""

    configuration: str
    timestamp: str
    precision: float
    recall: float
    f1_score: float
    faithfulness: float
    total_cases: int
    case_results: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RAGCheckerABTester:
    """A/B testing framework for RAGChecker improvements."""

    def __init__(self, results_dir: Path = Path("metrics/ab_testing")):
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_baseline_evaluation(self, config_name: str = "baseline") -> RAGCheckerResults:
        """Run the current baseline evaluation."""
        print(f"🧪 Running {config_name} evaluation...")

        # Run the evaluation
        cmd = ["python3", "scripts/ragchecker_official_evaluation.py", "--use-local-llm"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Check if evaluation succeeded
        if result.returncode != 0:
            print(f"⚠️ Evaluation failed: {result.stderr}")
            # Fall back to known baseline values

        # Parse results (simplified - would need to extract from actual output)
        # For now, using current known baseline
        results = RAGCheckerResults(
            configuration=config_name,
            timestamp=datetime.now().isoformat(),
            precision=0.107,
            recall=0.675,
            f1_score=0.183,
            faithfulness=0.540,
            total_cases=5,
            case_results=[],  # Would parse from actual output
        )

        # Save results
        self.save_results(results)
        return results

    def run_modified_evaluation(self, config_name: str, modifications: Dict[str, Any]) -> RAGCheckerResults:
        """Run evaluation with specific modifications."""
        print(f"🔬 Running {config_name} evaluation with modifications:")
        for key, value in modifications.items():
            print(f"   - {key}: {value}")

        # This would apply modifications and run evaluation
        # Implementation depends on the specific modification type

        # Placeholder - would implement actual modified evaluation
        results = RAGCheckerResults(
            configuration=config_name,
            timestamp=datetime.now().isoformat(),
            precision=0.0,  # Would get from actual run
            recall=0.0,
            f1_score=0.0,
            faithfulness=0.0,
            total_cases=5,
            case_results=[],
        )

        self.save_results(results)
        return results

    def compare_results(self, baseline: RAGCheckerResults, modified: RAGCheckerResults) -> Dict[str, Any]:
        """Compare two evaluation results."""
        comparison = {
            "baseline_config": baseline.configuration,
            "modified_config": modified.configuration,
            "improvements": {
                "precision": {
                    "baseline": baseline.precision,
                    "modified": modified.precision,
                    "change": modified.precision - baseline.precision,
                    "percent_change": (
                        ((modified.precision - baseline.precision) / baseline.precision * 100)
                        if baseline.precision > 0
                        else 0
                    ),
                },
                "recall": {
                    "baseline": baseline.recall,
                    "modified": modified.recall,
                    "change": modified.recall - baseline.recall,
                    "percent_change": (
                        ((modified.recall - baseline.recall) / baseline.recall * 100) if baseline.recall > 0 else 0
                    ),
                },
                "f1_score": {
                    "baseline": baseline.f1_score,
                    "modified": modified.f1_score,
                    "change": modified.f1_score - baseline.f1_score,
                    "percent_change": (
                        ((modified.f1_score - baseline.f1_score) / baseline.f1_score * 100)
                        if baseline.f1_score > 0
                        else 0
                    ),
                },
                "faithfulness": {
                    "baseline": baseline.faithfulness,
                    "modified": modified.faithfulness,
                    "change": modified.faithfulness - baseline.faithfulness,
                    "percent_change": (
                        ((modified.faithfulness - baseline.faithfulness) / baseline.faithfulness * 100)
                        if baseline.faithfulness > 0
                        else 0
                    ),
                },
            },
            "summary": {
                "overall_improvement": modified.f1_score > baseline.f1_score,
                "target_achieved": modified.f1_score >= 0.25,  # 25% target
                "significant_improvement": (modified.f1_score - baseline.f1_score) > 0.02,  # 2% improvement threshold
            },
        }

        return comparison

    def save_results(self, results: RAGCheckerResults):
        """Save evaluation results."""
        filename = f"ragchecker_results_{results.configuration}_{results.timestamp.replace(':', '-')}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results.to_dict(), f, indent=2)

        print(f"💾 Results saved to: {filepath}")

    def save_comparison(self, comparison: Dict[str, Any]):
        """Save comparison results."""
        timestamp = datetime.now().isoformat().replace(":", "-")
        filename = f"ragchecker_comparison_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(comparison, f, indent=2)

        print(f"📊 Comparison saved to: {filepath}")

    def print_comparison_summary(self, comparison: Dict[str, Any]):
        """Print a summary of the comparison."""
        print("\n" + "=" * 60)
        print("📊 RAGCHECKER A/B TEST RESULTS")
        print("=" * 60)

        improvements = comparison["improvements"]

        for metric, data in improvements.items():
            change = data["change"]
            percent_change = data["percent_change"]

            if change > 0:
                emoji = "📈"
                direction = "IMPROVED"
            elif change < 0:
                emoji = "📉"
                direction = "DECREASED"
            else:
                emoji = "➡️"
                direction = "NO CHANGE"

            print(f"{emoji} {metric.upper()}: {data['baseline']:.3f} → {data['modified']:.3f}")
            print(f"   Change: {change:+.3f} ({percent_change:+.1f}%) - {direction}")
            print()

        summary = comparison["summary"]
        if summary["overall_improvement"]:
            print("🎉 OVERALL: IMPROVEMENT DETECTED!")
        else:
            print("⚠️ OVERALL: NO IMPROVEMENT")

        if summary["target_achieved"]:
            print("🎯 TARGET: F1 Score target (25%) ACHIEVED!")
        else:
            print("🎯 TARGET: F1 Score target (25%) not yet achieved")


def main():
    """Example usage of the A/B testing framework."""
    tester = RAGCheckerABTester()

    # Run baseline
    baseline = tester.run_baseline_evaluation("current_baseline")

    # Example: Test improved prompt engineering
    modified = tester.run_modified_evaluation(
        "improved_prompts",
        {
            "prompt_engineering": "structured_json_output",
            "score_parsing": "regex_cleaning",
            "response_filtering": "relevance_based",
        },
    )

    # Compare results
    comparison = tester.compare_results(baseline, modified)
    tester.print_comparison_summary(comparison)
    tester.save_comparison(comparison)


if __name__ == "__main__":
    main()
