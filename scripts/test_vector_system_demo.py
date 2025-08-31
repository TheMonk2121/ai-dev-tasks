#!/usr/bin/env python3
"""
Vector-Based System Mapping Demo

Demonstrates the system in action with real-world test queries.
"""

import sys

sys.path.append(".")

from scripts.coder_role_integration import CoderRoleIntegration


def run_demo():
    """Run a comprehensive demo of the vector-based system mapping."""
    print("🚀 Vector-Based System Mapping Demo")
    print("=" * 60)

    # Initialize the integration system
    integration = CoderRoleIntegration()

    if not integration.initialize_embedding_model():
        print("❌ Failed to initialize embedding model")
        return

    if not integration.load_integration_data():
        print("❌ Failed to load integration data")
        return

    # Test queries that demonstrate different aspects of the system
    demo_queries = [
        "How can I optimize the performance of the memory system?",
        "What security vulnerabilities should I check in the API integration?",
        "How can I improve the testing coverage for the database components?",
        "What are the best practices for refactoring the dependency analysis code?",
        "How can I enhance the error handling in the file processing system?",
    ]

    print("🧪 Running Demo Queries...")
    print("=" * 60)

    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 40)

        # Get enhanced context
        enhanced_context = integration.enhance_coder_context(query, top_k=3)

        if enhanced_context:
            # Show relevant components
            print("📊 Relevant Components Found:")
            for j, comp in enumerate(enhanced_context.get("relevant_components", []), 1):
                comp_data = comp["component_data"]
                print(f"  {j}. {comp_data['file_path']}")
                print(f"     Similarity: {comp['similarity']:.3f}")
                print(f"     Type: {comp_data['component_type']}")
                print(f"     Functions: {comp_data['functions']}, Classes: {comp_data['classes']}")

            # Show recommendations
            print("\n💡 Intelligent Recommendations:")
            for rec in enhanced_context.get("recommendations", []):
                print(f"  • [{rec['priority'].upper()}] {rec['type']}: {rec['message']}")
                if rec.get("components"):
                    print(f"    Components: {', '.join(rec['components'][:2])}")

            # Show system context
            sys_context = enhanced_context.get("system_context", {})
            if sys_context.get("component_types"):
                print("\n📈 Component Type Distribution:")
                for comp_type, count in sys_context["component_types"].items():
                    print(f"  • {comp_type}: {count}")

        print("\n" + "=" * 60)

    print("\n🎉 Demo Complete!")
    print("\n📊 System Performance Summary:")
    print(f"  • Total Queries: {len(demo_queries)}")
    print(f"  • Context Integrations: {integration.integration_stats['context_integrations']}")
    print(f"  • Recommendations Generated: {integration.integration_stats['recommendations_generated']}")
    print(f"  • Average Integration Time: {integration.integration_stats['integration_time']:.3f}s")


if __name__ == "__main__":
    run_demo()
