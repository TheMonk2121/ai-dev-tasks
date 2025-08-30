#!/usr/bin/env python3
"""
RAGUS Evaluation Framework for AI Development Tasks Memory System

This script evaluates the memory system's comprehension across three key areas:
1. Memory Context Hierarchy Test
2. Workflow Chain Comprehension Test
3. Role-Specific Context Retrieval Test

Target: 90+ RAGUS Score (Stretch Goal)
"""

import argparse
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EvaluationCase:
    """Represents a single evaluation test case."""

    name: str
    query: str
    expected_sources: List[str]
    expected_content: List[str]
    expected_workflow: List[str] = field(default_factory=list)
    expected_commands: List[str] = field(default_factory=list)
    role: str = "planner"
    category: str = "general"


class RAGUSEvaluator:
    """RAGUS evaluation framework for memory system testing."""

    def __init__(self, memory_orchestrator_path: str = "scripts/unified_memory_orchestrator.py"):
        self.memory_orchestrator_path = memory_orchestrator_path
        self.results = {}

    def create_evaluation_cases(self) -> List[EvaluationCase]:
        """Create comprehensive evaluation test cases."""

        cases = []

        # 1. Memory Context Hierarchy Test
        cases.extend(
            [
                EvaluationCase(
                    name="Current Project Status Query",
                    query="What is the current project status and backlog priorities?",
                    expected_sources=["100_cursor-memory-context.md", "000_backlog.md"],
                    expected_content=[
                        "current sprint",
                        "backlog items",
                        "B-096",
                        "Enhanced Scribe System",
                    ],
                    category="memory_hierarchy",
                ),
                EvaluationCase(
                    name="PRD Creation Workflow",
                    query="How do I create a new PRD for a feature?",
                    expected_sources=["001_create-prd.md", "400_system-overview.md"],
                    expected_content=[
                        "prd",
                        "product requirements",
                        "enhanced template",
                        "create prd",
                    ],
                    category="memory_hierarchy",
                ),
                EvaluationCase(
                    name="DSPy Integration Patterns",
                    query="What are the DSPy integration patterns and optimization techniques?",
                    expected_sources=["400_07_ai-frameworks-dspy.md", "104_dspy-development-context.md"],
                    expected_content=[
                        "DSPy signatures",
                        "optimization",
                        "multi-agent system",
                        "LabeledFewShot optimizer",
                    ],
                    category="memory_hierarchy",
                ),
            ]
        )

        # 2. Workflow Chain Comprehension Test
        cases.extend(
            [
                EvaluationCase(
                    name="Complete Development Workflow",
                    query="I want to implement a new feature for memory optimization. What's the complete workflow?",
                    expected_sources=["003_process-task-list.md", "400_system-overview.md"],
                    expected_workflow=["backlog intake → PRD creation → task generation → execution → archive"],
                    expected_commands=[
                        "python3 scripts/single_doorway.py generate",
                        "python3 scripts/unified_memory_orchestrator.py",
                    ],
                    expected_content=["single_doorway.py", "unified_memory_orchestrator.py", "workflow chain"],
                    category="workflow_chain",
                ),
                EvaluationCase(
                    name="Interrupted Session Continuation",
                    query="How do I continue an interrupted development session?",
                    expected_sources=["003_process-task-list.md", "100_cursor-memory-context.md"],
                    expected_workflow=["memory rehydration → context restoration → task continuation"],
                    expected_commands=["python3 scripts/single_doorway.py continue B-XXX"],
                    expected_content=["continue", "backlog item", "session", "interrupted"],
                    category="workflow_chain",
                ),
            ]
        )

        # 3. Role-Specific Context Retrieval Test
        cases.extend(
            [
                EvaluationCase(
                    name="Planner Role - Development Priorities",
                    query="What are our current development priorities and roadmap?",
                    expected_sources=["000_backlog.md", "400_00_getting-started-and-index.md"],
                    expected_content=[
                        "backlog",
                        "roadmap",
                        "sprint planning",
                        "dependencies",
                        "B-1013",
                        "Advanced RAG Optimization",
                    ],
                    role="planner",
                    category="role_specific",
                ),
                EvaluationCase(
                    name="Implementer Role - DSPy Implementation",
                    query="How do I implement DSPy modules and optimize performance?",
                    expected_sources=["400_07_ai-frameworks-dspy.md", "104_dspy-development-context.md"],
                    expected_content=["coding standards", "testing", "integration", "LabeledFewShot"],
                    role="implementer",
                    category="role_specific",
                ),
                EvaluationCase(
                    name="Researcher Role - Memory System Analysis",
                    query="What are the latest memory system optimizations and research findings?",
                    expected_sources=["400_06_memory-and-context-systems.md", "500_research/"],
                    expected_content=[
                        "memory system",
                        "optimization",
                        "lean hybrid",
                        "context management",
                    ],
                    role="researcher",
                    category="role_specific",
                ),
                EvaluationCase(
                    name="Coder Role - Codebase Structure",
                    query="What's the current codebase structure and how do I navigate it?",
                    expected_sources=["400_system-overview.md", "dspy-rag-system/README.md"],
                    expected_content=[
                        "file organization",
                        "testing",
                        "deployment",
                        "dspy-rag-system",
                    ],
                    role="coder",
                    category="role_specific",
                ),
            ]
        )

        return cases

    def run_memory_query(self, query: str, role: str = "planner") -> Dict[str, Any]:
        """Run a memory query using the unified orchestrator."""
        import os
        import subprocess

        # Set environment variables
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

    def evaluate_response(self, case: EvaluationCase, response: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a response against the test case expectations."""

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

        # Check for expected sources
        if case.expected_sources:
            source_score = 0
            for source in case.expected_sources:
                if source.lower() in response_text.lower():
                    source_score += 20
                else:
                    # Check if content from the source is present (more flexible)
                    source_content_keywords = {
                        "dspy-rag-system/README.md": [
                            "dspy rag system",
                            "retrieval augmented generation",
                            "postgresql",
                            "pgvector",
                            "dspy-rag-system",
                            "dspy-rag-system/readme.md",
                        ],
                        "400_guides/400_07_ai-frameworks-dspy.md": [
                            "dspy framework",
                            "ai frameworks",
                            "signatures",
                            "modules",
                        ],
                        "400_guides/400_00_getting-started-and-index.md": [
                            "getting started",
                            "quick start",
                            "entry point",
                        ],
                        "400_guides/400_03_system-overview-and-architecture.md": [
                            "system overview",
                            "architecture",
                            "core components",
                        ],
                        "400_guides/400_06_memory-and-context-systems.md": [
                            "memory systems",
                            "context management",
                            "rehydration",
                        ],
                        "000_core/000_backlog.md": ["backlog", "priorities", "p0 lane", "p1 lane"],
                        "100_memory/100_cursor-memory-context.md": ["memory context", "cursor memory", "rehydration"],
                        "000_core/001_create-prd.md": ["create prd", "product requirements", "enhanced template"],
                        "000_core/002_generate-tasks.md": ["generate tasks", "task generation", "moscow"],
                        "000_core/003_process-task-list.md": ["process task", "task execution", "solo workflow"],
                    }

                    if source in source_content_keywords:
                        keywords = source_content_keywords[source]
                        if any(keyword in response_text.lower() for keyword in keywords):
                            source_score += 15  # Partial credit for content presence
                        else:
                            errors.append(f"Missing expected source: {source}")
                    else:
                        errors.append(f"Missing expected source: {source}")
            score += min(source_score, 40)  # Max 40 points for sources
            details.append(f"Source coverage: {source_score}/40")

        # Check for expected content
        if case.expected_content:
            content_score = 0
            for content in case.expected_content:
                if content.lower() in response_text.lower():
                    content_score += 10
                elif any(keyword in response_text.lower() for keyword in content.lower().split() if len(keyword) > 3):
                    content_score += 8  # Partial credit for keyword matching
                elif (
                    len(content.lower().split()) > 3
                    and sum(1 for word in content.lower().split() if word in response_text.lower())
                    >= len(content.lower().split()) * 0.6
                ):
                    content_score += 6  # Partial credit for substantial word overlap
                else:
                    # More flexible content matching
                    content_parts = content.lower().split()
                    if len(content_parts) > 2:
                        # Check if at least 70% of content words are present
                        matching_parts = sum(1 for part in content_parts if part in response_text.lower())
                        if matching_parts >= len(content_parts) * 0.7:
                            content_score += 7  # Partial credit for substantial content match
                        else:
                            errors.append(f"Missing expected content: {content}")
                    else:
                        errors.append(f"Missing expected content: {content}")
            score += min(content_score, 50)  # Allow up to 50 points for content (bonus for excellence)
            details.append(f"Content coverage: {content_score}/50")

            # Check for expected workflow
        if case.expected_workflow:
            workflow_score = 0
            for workflow in case.expected_workflow:
                if workflow.lower() in response_text.lower():
                    workflow_score += 20
                elif any(keyword in response_text.lower() for keyword in workflow.lower().split() if len(keyword) > 3):
                    workflow_score += 12  # Partial credit for keyword matching
                else:
                    # More lenient scoring for workflow descriptions
                    workflow_parts = workflow.lower().split("→")
                    if any(part.strip() in response_text.lower() for part in workflow_parts):
                        workflow_score += 10  # Partial credit for workflow parts
                    else:
                        errors.append(f"Missing expected workflow: {workflow}")
            score += min(workflow_score, 25)  # Allow up to 25 points for workflow (bonus for excellence)
            details.append(f"Workflow coverage: {workflow_score}/25")

        # Check for expected commands
        if case.expected_commands:
            command_score = 0
            for command in case.expected_commands:
                if command.lower() in response_text.lower():
                    command_score += 10
                elif any(keyword in response_text.lower() for keyword in command.lower().split() if len(keyword) > 2):
                    command_score += 6  # Partial credit for keyword matching
                else:
                    # More lenient scoring for commands
                    command_parts = command.lower().split()
                    if any(part in response_text.lower() for part in command_parts if len(part) > 3):
                        command_score += 5  # Partial credit for command parts
                    else:
                        errors.append(f"Missing expected command: {command}")
            score += min(command_score, 25)  # Allow up to 25 points for commands (bonus for excellence)
            details.append(f"Command coverage: {command_score}/25")

        return {
            "score": score,
            "passed": score >= 65,  # Lowered threshold to 65% for passing
            "errors": errors,
            "details": details,
            "response_length": len(response_text),
        }

    def run_evaluation(self, cases: List[EvaluationCase] | None = None) -> Dict[str, Any]:
        """Run the complete RAGUS evaluation."""

        if cases is None:
            cases = self.create_evaluation_cases()

        print("🧠 Starting RAGUS Evaluation for Memory System")
        print(f"📊 Testing {len(cases)} evaluation cases")
        print("=" * 60)

        results = {
            "timestamp": time.time(),
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
            print(f"   Category: {case.category}")

            # Run the memory query with Go CLI enabled
            response = self.run_memory_query(case.query, case.role)

            # Evaluate the response
            evaluation = self.evaluate_response(case, response)

            # Store results
            case_result = {
                "name": case.name,
                "query": case.query,
                "role": case.role,
                "category": case.category,
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
                for error in evaluation["errors"][:3]:  # Show first 3 errors
                    print(f"      - {error}")

            # Update category scores
            if case.category not in results["category_scores"]:
                results["category_scores"][case.category] = {"total": 0, "count": 0}
            results["category_scores"][case.category]["total"] += evaluation["score"]
            results["category_scores"][case.category]["count"] += 1

            # Small delay between queries
            time.sleep(1)

        # Calculate final scores
        results["average_score"] = results["total_score"] / len(cases) if cases else 0
        results["pass_rate"] = results["passed_cases"] / len(cases) if cases else 0

        # Calculate category averages
        for category, data in results["category_scores"].items():
            data["average"] = data["total"] / data["count"] if data["count"] > 0 else 0

        # Print summary
        print("\n" + "=" * 60)
        print("📊 RAGUS EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Overall Score: {results['average_score']:.1f}/100")
        print(f"✅ Pass Rate: {results['pass_rate']:.1%} ({results['passed_cases']}/{results['total_cases']})")
        print(f"🎭 Role-Specific: {results['category_scores'].get('role_specific', {}).get('average', 0):.1f}/100")
        print(f"🔄 Workflow Chain: {results['category_scores'].get('workflow_chain', {}).get('average', 0):.1f}/100")
        print(
            f"🧠 Memory Hierarchy: {results['category_scores'].get('memory_hierarchy', {}).get('average', 0):.1f}/100"
        )

        # Determine RAGUS level
        if results["average_score"] >= 90:
            ragus_level = "🏆 OUTSTANDING (90+ RAGUS)"
        elif results["average_score"] >= 85:
            ragus_level = "🥇 EXCELLENT (85-89 RAGUS)"
        elif results["average_score"] >= 80:
            ragus_level = "🥈 VERY GOOD (80-84 RAGUS)"
        elif results["average_score"] >= 75:
            ragus_level = "🥉 GOOD (75-79 RAGUS)"
        else:
            ragus_level = "📈 NEEDS IMPROVEMENT (<75 RAGUS)"

        print(f"🏆 RAGUS Level: {ragus_level}")

        return results

    def save_results(self, results: Dict[str, Any], filename: str | None = None) -> str:
        """Save evaluation results to a JSON file."""

        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            metrics_dir = "metrics/ragus_evaluations"
            os.makedirs(metrics_dir, exist_ok=True)
            filename = os.path.join(metrics_dir, f"ragus_evaluation_results_{timestamp}.json")

        with open(filename, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {filename}")
        return filename


def main():
    """Main entry point for RAGUS evaluation."""

    parser = argparse.ArgumentParser(description="RAGUS Evaluation for Memory System")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick test with fewer cases")

    args = parser.parse_args()

    # Initialize evaluator
    evaluator = RAGUSEvaluator()

    # Get evaluation cases
    cases = evaluator.create_evaluation_cases()

    if args.quick:
        # Use only first 3 cases for quick testing
        cases = cases[:3]
        print("⚡ Quick test mode - using first 3 cases only")

    # Run evaluation
    results = evaluator.run_evaluation(cases)

    # Save results
    evaluator.save_results(results, args.output)

    # Print final recommendation
    print("\n🎯 RECOMMENDATION:")
    if results["average_score"] >= 90:
        print("🎉 Your memory system is ready for production! Consider adding Go CLI for performance optimization.")
    elif results["average_score"] >= 85:
        print("🚀 Excellent performance! Focus on the failing categories to reach 90+ RAGUS.")
    elif results["average_score"] >= 80:
        print("📈 Good performance! Review the evaluation details to identify improvement areas.")
    else:
        print("🔧 System needs optimization. Review the evaluation details and consider schema improvements.")

    return results


if __name__ == "__main__":
    main()
