#!/usr/bin/env python3
"""
Query Pattern Knowledge Graph Demo

Demonstrates the complete query pattern knowledge graph system including:
- Query pattern analysis
- Vector analysis and clustering
- Predictive query modeling
- Proactive information surfacing
- Integration with LTST Memory System
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

from utils.query_pattern_knowledge_graph import create_query_pattern_knowledge_graph

from utils.conversation_storage import ConversationMessage, ConversationSession
from utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryPatternKnowledgeGraphDemo:
    """Demo class for query pattern knowledge graph functionality."""

    def __init__(self, database_url: str = None):
        """Initialize the demo.

        Args:
            database_url: Database connection URL
        """
        self.kg_system = create_query_pattern_knowledge_graph(database_url)
        self.demo_user_id = "demo_user_001"
        self.demo_session_id = f"demo_session_{int(datetime.now().timestamp())}"

    def run_complete_demo(self) -> None:
        """Run the complete demo showcasing all features."""
        print("\n🧠 Query Pattern Knowledge Graph Demo")
        print("=" * 50)

        try:
            # Step 1: Setup
            print("\n📋 Step 1: Setting up demo environment...")
            self._setup_demo_data()

            # Step 2: Initialize knowledge graph
            print("\n🔧 Step 2: Initializing knowledge graph...")
            self._demo_initialization()

            # Step 3: Process queries and show pattern analysis
            print("\n🔍 Step 3: Analyzing query patterns...")
            self._demo_pattern_analysis()

            # Step 4: Vector analysis and clustering
            print("\n🎯 Step 4: Vector analysis and clustering...")
            self._demo_vector_analysis()

            # Step 5: Query prediction
            print("\n🔮 Step 5: Query prediction...")
            self._demo_query_prediction()

            # Step 6: Proactive information surfacing
            print("\n💡 Step 6: Proactive information surfacing...")
            self._demo_proactive_information()

            # Step 7: Enhanced memory bundle
            print("\n🧠 Step 7: Enhanced memory bundle...")
            self._demo_enhanced_memory()

            # Step 8: Knowledge graph export
            print("\n📊 Step 8: Knowledge graph analysis...")
            self._demo_knowledge_graph_analysis()

            print("\n✅ Demo completed successfully!")
            print("\nThe system now:")
            print("- Stores every query you make")
            print("- Analyzes patterns in your questions")
            print("- Predicts what you might ask next")
            print("- Surfaces relevant information proactively")
            print("- Builds a knowledge graph of query relationships")

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed: {e}")

    def _setup_demo_data(self) -> None:
        """Setup demo data with sample queries."""
        print("  📝 Creating demo session and queries...")

        # Create demo session
        ConversationSession(
            session_id=self.demo_session_id,
            user_id=self.demo_user_id,
            session_name="Query Pattern Demo Session",
            session_type="demo",
        )

        # Sample queries that demonstrate different patterns
        demo_queries = [
            # Learning sequence about Python
            "How do I create a Python virtual environment?",
            "What's the difference between pip and conda?",
            "How do I install packages in a virtual environment?",
            # Debugging sequence
            "I'm getting a ImportError in Python, how do I fix it?",
            "The error says 'module not found', what does this mean?",
            "How do I check if a Python module is installed?",
            # Topic evolution - Python to web development
            "How do I create a web API with Python?",
            "What's the best Python web framework?",
            "How do I deploy a Flask app to production?",
            # Recurring theme - database questions
            "How do I connect to a PostgreSQL database from Python?",
            "What's the best way to handle database migrations?",
            "How do I optimize database queries for performance?",
            # Context shift - different domain
            "What are the best practices for machine learning model training?",
            "How do I evaluate ML model performance?",
            "What's overfitting in machine learning?",
            # Back to original theme - more database questions
            "How do I implement database connection pooling?",
            "What's the difference between SQL and NoSQL databases?",
        ]

        # Store queries as conversation messages
        for i, query_text in enumerate(demo_queries):
            message = ConversationMessage(
                session_id=self.demo_session_id,
                role="human",
                content=query_text,
                message_type="message",
                metadata={"demo": True, "sequence_number": i + 1, "timestamp": datetime.now().isoformat()},
            )

            # Store message
            self.kg_system.storage.store_message(message)

            # Simulate some time between queries
            import time

            time.sleep(0.1)

        print(f"  ✅ Created demo session with {len(demo_queries)} queries")

    def _demo_initialization(self) -> None:
        """Demo knowledge graph initialization."""
        print("  🚀 Initializing user knowledge graph...")

        success = self.kg_system.initialize_user_knowledge_graph(self.demo_user_id)

        if success:
            print("  ✅ Knowledge graph initialized successfully")

            # Show some basic stats
            if self.demo_user_id in self.kg_system.knowledge_graphs:
                kg = self.kg_system.knowledge_graphs[self.demo_user_id]
                print(f"     📊 Graph: {kg.number_of_nodes()} nodes, {kg.number_of_edges()} edges")
        else:
            print("  ❌ Knowledge graph initialization failed")

    def _demo_pattern_analysis(self) -> None:
        """Demo pattern analysis capabilities."""
        print("  🔍 Running pattern analysis...")

        analysis = self.kg_system.analyze_user_query_patterns(self.demo_user_id)

        if "error" in analysis:
            print(f"  ❌ Pattern analysis failed: {analysis['error']}")
            return

        pattern_analysis = analysis.get("pattern_analysis", {})

        # Show detected patterns
        print("  📈 Pattern Analysis Results:")

        # Topic evolution
        topic_evolutions = pattern_analysis.get("topic_evolution", [])
        print(f"     🔄 Topic Evolutions: {len(topic_evolutions)}")
        for i, evolution in enumerate(topic_evolutions[:2]):  # Show first 2
            print(
                f"       {i + 1}. {evolution.get('evolution_type', 'unknown')} - "
                f"drift: {evolution.get('semantic_drift', 0):.3f}"
            )

        # Recurring themes
        recurring_themes = pattern_analysis.get("recurring_themes", [])
        print(f"     🔁 Recurring Themes: {len(recurring_themes)}")
        for i, theme in enumerate(recurring_themes[:2]):  # Show first 2
            print(
                f'       {i + 1}. "{theme.get("theme_signature", "unknown")}" - frequency: {theme.get("frequency", 0)}'
            )

        # Question sequences
        sequences = pattern_analysis.get("question_sequences", [])
        print(f"     📝 Question Sequences: {len(sequences)}")
        for i, seq in enumerate(sequences[:2]):  # Show first 2
            print(
                f"       {i + 1}. {seq.get('sequence_type', 'unknown')} sequence - "
                f"strength: {seq.get('sequence_strength', 0):.3f}"
            )

        # Context shifts
        context_shifts = pattern_analysis.get("context_shifts", [])
        print(f"     ↗️ Context Shifts: {len(context_shifts)}")

    def _demo_vector_analysis(self) -> None:
        """Demo vector analysis and clustering."""
        print("  🎯 Running vector analysis...")

        analysis = self.kg_system.analyze_user_query_patterns(self.demo_user_id)
        cluster_analysis = analysis.get("cluster_analysis", {})

        clusters = cluster_analysis.get("clusters", [])
        print(f"  📊 Detected {len(clusters)} query clusters:")

        for i, cluster in enumerate(clusters[:3]):  # Show first 3 clusters
            print(f"     Cluster {i + 1}:")
            print(f"       Size: {cluster.get('size', 0)} queries")
            print(f"       Coherence: {cluster.get('coherence', 0):.3f}")
            print(f"       Time span: {cluster.get('time_span_days', 0)} days")

            # Show first few queries in cluster
            queries = cluster.get("queries", [])
            for j, query in enumerate(queries[:2]):  # Show first 2 queries
                content = query.get("content", "")[:60]
                print(f'         - "{content}{"..." if len(query.get("content", "")) > 60 else ""}"')

        # Evolution analysis
        evolution_analysis = analysis.get("evolution_analysis", {})
        if evolution_analysis:
            print("  📈 Query Evolution Analysis:")
            trajectory_count = len(evolution_analysis.get("trajectory_vectors", []))
            print(f"     Trajectory vectors analyzed: {trajectory_count}")

            semantic_drift = evolution_analysis.get("semantic_drift", [])
            if semantic_drift:
                avg_similarity = sum(d.get("similarity", 0) for d in semantic_drift) / len(semantic_drift)
                print(f"     Average semantic similarity: {avg_similarity:.3f}")

    def _demo_query_prediction(self) -> None:
        """Demo query prediction capabilities."""
        print("  🔮 Generating query predictions...")

        # Use a recent context for prediction
        current_context = "How do I optimize database queries for performance?"

        predictions = self.kg_system.predictor.predict_next_query_topics(
            self.demo_user_id, current_context, max_predictions=5, include_rationale=True
        )

        print(f'  🎯 Based on context: "{current_context}"')
        print(f"  📊 Generated {len(predictions)} predictions:")

        for i, pred in enumerate(predictions):
            confidence = pred.get("confidence", 0)
            method = pred.get("prediction_method", "unknown")
            topic = pred.get("predicted_topic", "")[:80]
            rationale = pred.get("rationale", "No rationale provided")

            print(f'     {i + 1}. "{topic}{"..." if len(pred.get("predicted_topic", "")) > 80 else ""}"')
            print(f"        Confidence: {confidence:.1%} | Method: {method}")
            print(f"        Rationale: {rationale}")

    def _demo_proactive_information(self) -> None:
        """Demo proactive information surfacing."""
        print("  💡 Surfacing proactive information...")

        current_context = "I'm getting performance issues with my database queries"

        proactive_info = self.kg_system.predictor.proactive_information_surfacing(
            self.demo_user_id, current_context, max_suggestions=3
        )

        print(f'  🎯 Based on context: "{current_context}"')
        print(f"  💡 Found {len(proactive_info)} proactive information items:")

        for i, info in enumerate(proactive_info):
            info_type = info.get("info_type", "unknown")
            content = info.get("content", "")[:80]
            relevance = info.get("relevance", 0)
            pattern_strength = info.get("pattern_strength", 0)

            print(f'     {i + 1}. [{info_type}] "{content}{"..." if len(info.get("content", "")) > 80 else ""}"')
            print(f"        Relevance: {relevance:.1%} | Pattern strength: {pattern_strength:.1%}")

    def _demo_enhanced_memory(self) -> None:
        """Demo enhanced memory bundle."""
        print("  🧠 Creating enhanced memory bundle...")

        current_query = "What are the best practices for database indexing?"

        enhanced_bundle = self.kg_system.get_enhanced_memory_bundle(
            self.demo_user_id, current_query, self.demo_session_id
        )

        if "error" in enhanced_bundle:
            print(f"  ❌ Enhanced memory bundle failed: {enhanced_bundle['error']}")
            return

        print("  📋 Enhanced Memory Bundle includes:")

        # Show predictions
        predictions = enhanced_bundle.get("next_query_predictions", [])
        print(f"     🔮 Query predictions: {len(predictions)}")

        # Show proactive info
        proactive = enhanced_bundle.get("proactive_information", [])
        print(f"     💡 Proactive information: {len(proactive)}")

        # Show pattern analysis summary
        pattern_analysis = enhanced_bundle.get("query_pattern_analysis", {})
        if pattern_analysis and "pattern_analysis" in pattern_analysis:
            patterns = pattern_analysis["pattern_analysis"]
            total_patterns = sum(
                len(v) if isinstance(v, list) else 0 for k, v in patterns.items() if k != "analysis_metadata"
            )
            print(f"     📊 Total patterns detected: {total_patterns}")

        # Show LTST bundle info
        ltst_bundle = enhanced_bundle.get("ltst_memory_bundle", {})
        if ltst_bundle and "conversation_history" in ltst_bundle:
            conv_history = ltst_bundle["conversation_history"]
            print(f"     💬 Conversation history: {len(conv_history)} messages")

        metadata = enhanced_bundle.get("enhancement_metadata", {})
        print(f"     ⏰ Enhanced at: {metadata.get('enhanced_at', 'unknown')}")

    def _demo_knowledge_graph_analysis(self) -> None:
        """Demo knowledge graph analysis and export."""
        print("  📊 Analyzing knowledge graph...")

        # Get graph metrics
        analysis = self.kg_system.analyze_user_query_patterns(self.demo_user_id)
        kg_metrics = analysis.get("knowledge_graph_metrics", {})

        if kg_metrics:
            print("  📈 Knowledge Graph Metrics:")
            print(f"     Nodes: {kg_metrics.get('node_count', 0)}")
            print(f"     Edges: {kg_metrics.get('edge_count', 0)}")
            print(f"     Density: {kg_metrics.get('density', 0):.3f}")
            print(f"     Avg Clustering: {kg_metrics.get('average_clustering', 0):.3f}")
            print(f"     Connected Components: {kg_metrics.get('connected_components', 0)}")

            if "max_centrality" in kg_metrics:
                print(f"     Max Centrality: {kg_metrics['max_centrality']:.3f}")

        # Export sample
        print("  💾 Generating knowledge graph export sample...")
        export_data = self.kg_system.export_user_knowledge_graph(self.demo_user_id, "json")

        if export_data:
            # Parse to get summary info
            try:
                export_dict = json.loads(export_data)
                graph_data = export_dict.get("relationship_graph", {})
                nodes = graph_data.get("nodes", [])
                edges = graph_data.get("edges", [])

                print(f"     📄 Export contains {len(nodes)} nodes and {len(edges)} relationships")
                print(f"     📁 Export size: {len(export_data)} characters")

                # Show sample of graph structure
                if edges:
                    print("     🔗 Sample relationships:")
                    for i, edge in enumerate(edges[:3]):  # Show first 3 edges
                        source = edge.get("source", "unknown")
                        target = edge.get("target", "unknown")
                        attrs = edge.get("attributes", {})
                        weight = attrs.get("weight", 0)
                        print(f"       {i + 1}. {source} → {target} (similarity: {weight:.3f})")

            except Exception as e:
                print(f"     ⚠️ Could not parse export data: {e}")
        else:
            print("     ❌ Export failed")

    def run_interactive_demo(self) -> None:
        """Run an interactive demo where user can input queries."""
        print("\n🧠 Interactive Query Pattern Knowledge Graph Demo")
        print("=" * 55)
        print("Enter queries and see real-time pattern analysis and predictions!")
        print("Type 'quit' to exit, 'analyze' to see current patterns, 'export' to export graph\n")

        # Initialize if not already done
        self.kg_system.initialize_user_knowledge_graph(self.demo_user_id)

        query_count = 0

        while True:
            try:
                user_input = input(f"\n[Query {query_count + 1}] Your query: ").strip()

                if user_input.lower() == "quit":
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == "analyze":
                    self._show_interactive_analysis()
                    continue
                elif user_input.lower() == "export":
                    self._show_interactive_export()
                    continue
                elif not user_input:
                    continue

                # Process the query
                print(f'\n🔄 Processing: "{user_input}"')

                result = self.kg_system.process_new_query(self.demo_user_id, user_input, self.demo_session_id)

                # Show results
                self._show_interactive_results(result)

                query_count += 1

            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    def _show_interactive_analysis(self) -> None:
        """Show current analysis in interactive mode."""
        print("\n📊 Current Pattern Analysis:")
        analysis = self.kg_system.analyze_user_query_patterns(self.demo_user_id)

        if "error" not in analysis:
            pattern_analysis = analysis.get("pattern_analysis", {})

            themes = len(pattern_analysis.get("recurring_themes", []))
            sequences = len(pattern_analysis.get("question_sequences", []))
            evolutions = len(pattern_analysis.get("topic_evolution", []))
            shifts = len(pattern_analysis.get("context_shifts", []))

            print(f"  🔁 Recurring themes: {themes}")
            print(f"  📝 Question sequences: {sequences}")
            print(f"  🔄 Topic evolutions: {evolutions}")
            print(f"  ↗️ Context shifts: {shifts}")

            clusters = analysis.get("cluster_analysis", {}).get("clusters", [])
            print(f"  📊 Query clusters: {len(clusters)}")

            metadata = analysis.get("analysis_metadata", {})
            total_queries = metadata.get("total_queries_analyzed", 0)
            print(f"  📈 Total queries analyzed: {total_queries}")

    def _show_interactive_export(self) -> None:
        """Show export in interactive mode."""
        print("\n💾 Exporting knowledge graph...")
        export_data = self.kg_system.export_user_knowledge_graph(self.demo_user_id, "json")

        if export_data:
            # Save to file
            filename = f"query_kg_export_{int(datetime.now().timestamp())}.json"
            try:
                with open(filename, "w") as f:
                    f.write(export_data)
                print(f"✅ Exported to: {filename}")
                print(f"📁 File size: {len(export_data)} characters")
            except Exception as e:
                print(f"❌ Failed to save file: {e}")
        else:
            print("❌ Export failed")

    def _show_interactive_results(self, result: Dict[str, Any]) -> None:
        """Show processing results in interactive mode."""
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return

        # Show predictions
        predictions = result.get("predictions", [])
        if predictions:
            print(f"\n🔮 Predictions ({len(predictions)}):")
            for i, pred in enumerate(predictions[:3]):  # Show top 3
                topic = pred.get("predicted_topic", "")[:60]
                confidence = pred.get("confidence", 0)
                method = pred.get("prediction_method", "unknown")
                print(f'  {i + 1}. "{topic}{"..." if len(pred.get("predicted_topic", "")) > 60 else ""}"')
                print(f"     ({confidence:.1%} via {method})")

        # Show proactive info
        proactive = result.get("proactive_information", [])
        if proactive:
            print(f"\n💡 Proactive Information ({len(proactive)}):")
            for i, info in enumerate(proactive[:2]):  # Show top 2
                content = info.get("content", "")[:60]
                relevance = info.get("relevance", 0)
                print(f'  {i + 1}. "{content}{"..." if len(info.get("content", "")) > 60 else ""}"')
                print(f"     (relevance: {relevance:.1%})")

        # Show similar queries
        similar = result.get("similar_queries", [])
        if similar:
            print(f"\n🔍 Similar Past Queries ({len(similar)}):")
            for i, sim in enumerate(similar[:2]):  # Show top 2
                content = sim.get("content", "")[:60]
                similarity = sim.get("similarity", 0)
                print(f'  {i + 1}. "{content}{"..." if len(sim.get("content", "")) > 60 else ""}"')
                print(f"     (similarity: {similarity:.1%})")


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Query Pattern Knowledge Graph Demo")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run interactive demo")
    parser.add_argument("--database-url", help="Database connection URL")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    try:
        demo = QueryPatternKnowledgeGraphDemo(args.database_url)

        if args.interactive:
            demo.run_interactive_demo()
        else:
            demo.run_complete_demo()

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
