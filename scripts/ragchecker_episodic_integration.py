#!/usr/bin/env python3
"""
RAGChecker Episodic Integration

Integrates episodic memory with RAGChecker evaluation to measure the impact
of episodic context on retrieval performance.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path modification
from scripts.episodic_workflow_integration import EpisodicWorkflowIntegration


class RAGCheckerEpisodicIntegration:
    """Integrates episodic memory with RAGChecker evaluation."""

    def __init__(self):
        """Initialize the integration."""
        self.episodic_integration = EpisodicWorkflowIntegration()
        print("🧠 RAGChecker Episodic Integration initialized")

    def enhance_query_with_episodic_context(self, query: str, agent: str = "cursor_ai") -> Dict[str, Any]:
        """Enhance a query with episodic context for RAGChecker evaluation."""
        try:
            # Get episodic context
            context = self.episodic_integration.get_context_for_task(query, agent)

            if context and "episodic_context" in context:
                episodic = context["episodic_context"]

                # Create enhanced query with episodic context
                enhanced_query = {
                    "original_query": query,
                    "episodic_context": {
                        "what_worked": episodic["what_worked_bullets"],
                        "what_to_avoid": episodic["what_to_avoid_bullets"],
                        "confidence_score": episodic["confidence_score"],
                        "similar_episodes_count": len(episodic["similar_episodes"]),
                    },
                    "enhanced_query": self._create_enhanced_query(query, episodic),
                }

                print(f"✅ Enhanced query with episodic context (confidence: {episodic['confidence_score']:.2f})")
                return enhanced_query
            else:
                print("🧠 No episodic context available for query")
                return {"original_query": query, "episodic_context": None, "enhanced_query": query}

        except Exception as e:
            print(f"❌ Failed to enhance query with episodic context: {e}")
            return {"original_query": query, "episodic_context": None, "enhanced_query": query}

    def _create_enhanced_query(self, original_query: str, episodic_context: Dict[str, Any]) -> str:
        """Create an enhanced query that includes episodic context."""
        enhanced_parts = [original_query]

        if episodic_context["what_worked_bullets"]:
            enhanced_parts.append("\n\nConsider these successful patterns from similar tasks:")
            for item in episodic_context["what_worked_bullets"]:
                enhanced_parts.append(f"- {item}")

        if episodic_context["what_to_avoid_bullets"]:
            enhanced_parts.append("\n\nAvoid these patterns from similar tasks:")
            for item in episodic_context["what_to_avoid_bullets"]:
                enhanced_parts.append(f"- {item}")

        return "\n".join(enhanced_parts)

    def store_evaluation_result(
        self,
        query: str,
        original_response: str,
        enhanced_response: str,
        metrics: Dict[str, Any],
        agent: str = "ragchecker",
    ) -> bool:
        """Store the results of an episodic-enhanced evaluation."""
        try:
            # Create a reflection about the evaluation
            task_description = f"RAGChecker evaluation with episodic context: {query[:50]}..."

            # Determine what worked and what to avoid based on metrics
            what_worked = []
            what_to_avoid = []

            if metrics.get("precision", 0) > 0.2:
                what_worked.append("Episodic context improved precision")
            else:
                what_to_avoid.append("Episodic context did not improve precision")

            if metrics.get("recall", 0) > 0.4:
                what_worked.append("Episodic context improved recall")
            else:
                what_to_avoid.append("Episodic context did not improve recall")

            if metrics.get("f1_score", 0) > 0.22:
                what_worked.append("Episodic context improved F1 score")
            else:
                what_to_avoid.append("Episodic context did not improve F1 score")

            # Store the reflection
            success = self.episodic_integration.on_task_completion(
                task_description=task_description,
                input_text=original_response,
                output_text=enhanced_response,
                agent=agent,
                task_type="evaluation",
                outcome_metrics=metrics,
                source_refs={"query": query, "evaluation_type": "ragchecker"},
            )

            if success:
                print(f"✅ Stored evaluation reflection for: {query[:50]}...")

            return success

        except Exception as e:
            print(f"❌ Failed to store evaluation result: {e}")
            return False

    def run_ablation_study(self, queries: list, agent: str = "cursor_ai") -> Dict[str, Any]:
        """Run an ablation study comparing queries with and without episodic context."""
        results = {
            "total_queries": len(queries),
            "with_episodic": 0,
            "without_episodic": 0,
            "improvements": 0,
            "degradations": 0,
            "no_change": 0,
            "results": [],
        }

        for i, query in enumerate(queries):
            print(f"🔍 Processing query {i + 1}/{len(queries)}: {query[:50]}...")

            # Get episodic context
            enhanced_query_data = self.enhance_query_with_episodic_context(query, agent)

            if enhanced_query_data["episodic_context"]:
                results["with_episodic"] += 1
                print("   ✅ Enhanced with episodic context")
            else:
                results["without_episodic"] += 1
                print("   ⚠️  No episodic context available")

            results["results"].append(enhanced_query_data)

        print("\n📊 Ablation Study Results:")
        print(f"   Total queries: {results['total_queries']}")
        print(f"   With episodic context: {results['with_episodic']}")
        print(f"   Without episodic context: {results['without_episodic']}")

        return results


def main():
    """Main CLI interface for RAGChecker episodic integration."""
    parser = argparse.ArgumentParser(description="RAGChecker Episodic Integration")
    parser.add_argument("command", choices=["enhance", "ablation", "test"], help="Command to execute")
    parser.add_argument("--query", help="Query to enhance")
    parser.add_argument("--queries-file", help="File containing queries for ablation study")
    parser.add_argument("--agent", default="cursor_ai", help="Agent name")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    integration = RAGCheckerEpisodicIntegration()

    if args.command == "enhance":
        if not args.query:
            print("❌ --query is required for enhance command")
            sys.exit(1)

        enhanced_query = integration.enhance_query_with_episodic_context(args.query, args.agent)

        if args.format == "json":
            print(json.dumps(enhanced_query, indent=2))
        else:
            print("📝 Enhanced Query:")
            print(enhanced_query["enhanced_query"])
            if enhanced_query["episodic_context"]:
                print(
                    f"\n🧠 Episodic Context (confidence: {enhanced_query['episodic_context']['confidence_score']:.2f}):"
                )
                print(f"   What worked: {enhanced_query['episodic_context']['what_worked']}")
                print(f"   What to avoid: {enhanced_query['episodic_context']['what_to_avoid']}")

    elif args.command == "ablation":
        if not args.queries_file:
            print("❌ --queries-file is required for ablation command")
            sys.exit(1)

        try:
            with open(args.queries_file, "r") as f:
                queries = [line.strip() for line in f if line.strip()]

            results = integration.run_ablation_study(queries, args.agent)

            if args.format == "json":
                print(json.dumps(results, indent=2))
            else:
                print("\n📊 Ablation Study Complete")
                print(f"   Enhanced queries: {results['with_episodic']}/{results['total_queries']}")

        except FileNotFoundError:
            print(f"❌ File not found: {args.queries_file}")
            sys.exit(1)

    elif args.command == "test":
        print("🧪 Testing RAGChecker episodic integration...")

        # Test query enhancement
        test_query = "implement error handling for database connections"
        enhanced_query = integration.enhance_query_with_episodic_context(test_query, args.agent)

        if enhanced_query["episodic_context"]:
            print("✅ Query enhancement test passed")
            print(f"   Enhanced query length: {len(enhanced_query['enhanced_query'])} chars")
            print(f"   Confidence score: {enhanced_query['episodic_context']['confidence_score']:.2f}")
        else:
            print("⚠️  Query enhancement test - no episodic context found")

        # Test evaluation result storage
        test_metrics = {"precision": 0.25, "recall": 0.45, "f1_score": 0.32}

        success = integration.store_evaluation_result(
            query=test_query,
            original_response="Original response",
            enhanced_response="Enhanced response",
            metrics=test_metrics,
        )

        if success:
            print("✅ Evaluation result storage test passed")
        else:
            print("❌ Evaluation result storage test failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
