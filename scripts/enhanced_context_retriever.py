#!/usr/bin/env python3
"""
Enhanced Context Retriever for Vector-Based System Mapping

Task 2.2: Enhanced Context Retrieval
Implements advanced context retrieval capabilities using vector store.
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    print("❌ Vector libraries not available")


class EnhancedContextRetriever:
    """Enhanced context retrieval using vector embeddings and semantic search."""

    def __init__(self, vector_store_dir: str = "metrics/vector_store"):
        self.vector_store_dir = vector_store_dir
        self.component_embeddings = {}
        self.component_analysis = {}
        self.embedding_model = None
        self.retrieval_stats = {
            "queries_processed": 0,
            "contexts_retrieved": 0,
            "average_similarity": 0.0,
            "retrieval_time": 0.0,
        }

    def load_vector_store(self) -> bool:
        """Load vector store data from files."""
        try:
            # Load component embeddings
            embeddings_file = os.path.join(self.vector_store_dir, "component_embeddings.json")
            if not os.path.exists(embeddings_file):
                print(f"❌ Embeddings file not found: {embeddings_file}")
                return False

            print(f"📂 Loading component embeddings from: {embeddings_file}")
            with open(embeddings_file, "r", encoding="utf-8") as f:
                self.component_embeddings = json.load(f)

            # Load component analysis
            analysis_file = os.path.join(self.vector_store_dir, "component_analysis.json")
            if os.path.exists(analysis_file):
                with open(analysis_file, "r", encoding="utf-8") as f:
                    self.component_analysis = json.load(f)

            print(f"✅ Loaded {len(self.component_embeddings)} component embeddings")
            return True

        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            return False

    def initialize_embedding_model(self) -> bool:
        """Initialize the sentence transformer model for embeddings."""
        if not VECTOR_AVAILABLE:
            print("❌ Vector libraries not available")
            return False

        try:
            print("🤖 Initializing embedding model...")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Embedding model initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing embedding model: {e}")
            return False

    def retrieve_context(self, query: str, top_k: int = 5, min_similarity: float = 0.2) -> List[Dict[str, Any]]:
        """Retrieve relevant context based on semantic similarity."""
        if not self.embedding_model or not self.component_embeddings:
            print("❌ No embeddings available for context retrieval")
            return []

        try:
            start_time = time.time()

            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=False)

            # Calculate similarities
            similarities = []
            for component_id, component_data in self.component_embeddings.items():
                component_embedding = np.array(component_data["embedding"])
                similarity = np.dot(query_embedding, component_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(component_embedding)
                )

                if similarity >= min_similarity:
                    similarities.append(
                        {
                            "component_id": component_id,
                            "similarity": float(similarity),
                            "component_data": component_data,
                            "context": component_data.get("context", ""),
                            "file_path": component_data.get("file_path", ""),
                            "component_type": component_data.get("component_type", "unknown"),
                        }
                    )

            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            results = similarities[:top_k]

            # Update statistics
            self.retrieval_stats["queries_processed"] += 1
            self.retrieval_stats["contexts_retrieved"] += len(results)
            if results:
                avg_similarity = sum(r["similarity"] for r in results) / len(results)
                self.retrieval_stats["average_similarity"] = (
                    self.retrieval_stats["average_similarity"] * (self.retrieval_stats["queries_processed"] - 1)
                    + avg_similarity
                ) / self.retrieval_stats["queries_processed"]

            self.retrieval_stats["retrieval_time"] = time.time() - start_time

            return results

        except Exception as e:
            print(f"❌ Error in context retrieval: {e}")
            return []

    def retrieve_by_component_type(self, query: str, component_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve context filtered by component type."""
        all_results = self.retrieve_context(query, top_k=100)  # Get more results to filter

        # Filter by component type
        filtered_results = [result for result in all_results if result["component_type"] == component_type]

        return filtered_results[:top_k]

    def retrieve_related_components(self, file_path: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve components related to a specific file."""
        # Find the component for the given file path
        target_component = None
        for component_id, component_data in self.component_embeddings.items():
            if component_data.get("file_path") == file_path:
                target_component = component_data
                break

        if not target_component:
            print(f"❌ Component not found for file: {file_path}")
            return []

        # Use the component's context as a query
        context = target_component.get("context", "")
        return self.retrieve_context(context, top_k=top_k)

    def analyze_context_patterns(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze patterns in context retrieval."""
        if not queries:
            return {}

        print("🔍 Analyzing context retrieval patterns...")

        pattern_analysis = {
            "total_queries": len(queries),
            "query_results": {},
            "component_type_distribution": {},
            "similarity_distribution": [],
        }

        for query in queries:
            results = self.retrieve_context(query, top_k=10)

            pattern_analysis["query_results"][query] = {
                "results_count": len(results),
                "avg_similarity": sum(r["similarity"] for r in results) / len(results) if results else 0,
                "component_types": [r["component_type"] for r in results],
            }

            # Update component type distribution
            for result in results:
                comp_type = result["component_type"]
                if comp_type not in pattern_analysis["component_type_distribution"]:
                    pattern_analysis["component_type_distribution"][comp_type] = 0
                pattern_analysis["component_type_distribution"][comp_type] += 1

            # Collect similarity scores
            pattern_analysis["similarity_distribution"].extend([r["similarity"] for r in results])

        # Calculate similarity statistics
        if pattern_analysis["similarity_distribution"]:
            similarities = pattern_analysis["similarity_distribution"]
            pattern_analysis["similarity_stats"] = {
                "min": min(similarities),
                "max": max(similarities),
                "avg": sum(similarities) / len(similarities),
                "median": sorted(similarities)[len(similarities) // 2],
            }

        return pattern_analysis

    def export_retrieval_results(self, results: List[Dict[str, Any]], output_file: str) -> str:
        """Export retrieval results to JSON file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        export_data = {
            "timestamp": datetime.now().isoformat(),
            "retrieval_stats": self.retrieval_stats,
            "results": results,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"📊 Retrieval results exported to: {output_file}")
        return output_file

    def create_enhanced_context_system(self) -> Dict[str, Any]:
        """Create enhanced context retrieval system."""
        start_time = time.time()

        print("🚀 Creating enhanced context retrieval system...")

        # Initialize embedding model
        if not self.initialize_embedding_model():
            return {}

        # Load vector store
        if not self.load_vector_store():
            return {}

        # Test context retrieval with sample queries
        test_queries = [
            "database connection and management",
            "file processing and analysis",
            "API integration and communication",
            "testing framework and validation",
            "memory system and context management",
            "dependency analysis and graph construction",
            "vector embeddings and similarity search",
            "web visualization and user interface",
        ]

        print("🧪 Testing enhanced context retrieval...")

        all_results = {}
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = self.retrieve_context(query, top_k=5)
            all_results[query] = results

            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['file_path']} (similarity: {result['similarity']:.3f})")
                print(f"     Type: {result['component_type']}")

        # Analyze patterns
        pattern_analysis = self.analyze_context_patterns(test_queries)

        # Export results
        output_dir = "metrics/enhanced_context"
        os.makedirs(output_dir, exist_ok=True)

        export_files = {}

        # Export all results
        all_results_file = os.path.join(output_dir, "context_retrieval_results.json")
        self.export_retrieval_results(all_results, all_results_file)
        export_files["results"] = all_results_file

        # Export pattern analysis
        pattern_file = os.path.join(output_dir, "pattern_analysis.json")
        with open(pattern_file, "w", encoding="utf-8") as f:
            json.dump(pattern_analysis, f, indent=2, ensure_ascii=False)
        export_files["patterns"] = pattern_file

        # Export retrieval statistics
        stats_file = os.path.join(output_dir, "retrieval_stats.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(self.retrieval_stats, f, indent=2, ensure_ascii=False)
        export_files["stats"] = stats_file

        return {
            "timestamp": datetime.now().isoformat(),
            "project": "Vector-Based System Mapping",
            "retrieval_stats": self.retrieval_stats,
            "pattern_analysis": pattern_analysis,
            "export_files": export_files,
            "total_queries_tested": len(test_queries),
            "total_results_retrieved": sum(len(results) for results in all_results.values()),
        }

    def print_summary(self, result: Dict[str, Any]):
        """Print enhanced context retrieval summary."""
        stats = result.get("retrieval_stats", {})
        patterns = result.get("pattern_analysis", {})

        print("\n" + "=" * 60)
        print("🔍 ENHANCED CONTEXT RETRIEVAL SUMMARY")
        print("=" * 60)

        print(f"🟢 Queries Processed: {stats.get('queries_processed', 0)}")
        print(f"🔗 Contexts Retrieved: {stats.get('contexts_retrieved', 0)}")
        print(f"📊 Average Similarity: {stats.get('average_similarity', 0):.3f}")
        print(f"⏱️ Retrieval Time: {stats.get('retrieval_time', 0):.3f}s")

        if patterns.get("similarity_stats"):
            sim_stats = patterns["similarity_stats"]
            print("\n📈 Similarity Statistics:")
            print(f"  • Min: {sim_stats['min']:.3f}")
            print(f"  • Max: {sim_stats['max']:.3f}")
            print(f"  • Average: {sim_stats['avg']:.3f}")
            print(f"  • Median: {sim_stats['median']:.3f}")

        if patterns.get("component_type_distribution"):
            print("\n📊 Component Type Distribution:")
            for comp_type, count in patterns["component_type_distribution"].items():
                print(f"  • {comp_type}: {count} retrievals")

        print("\n🎯 B-1047 Phase 2 Progress:")
        print("  ✅ Task 2.1: Vector Store Integration for System Components - COMPLETED")
        print("  ✅ Task 2.2: Enhanced Context Retrieval - COMPLETED")
        print("  🔄 Task 2.3: Smart Integration with Coder Role - NEXT")


def main():
    """Main function for enhanced context retrieval."""
    print("🚀 Continuing B-1047 Phase 2: Enhanced Context Integration")
    print("=" * 60)
    print("📋 Task 2.2: Enhanced Context Retrieval")
    print("=" * 60)

    # Initialize context retriever
    retriever = EnhancedContextRetriever()

    # Create enhanced context system
    result = retriever.create_enhanced_context_system()

    if result:
        # Print summary
        retriever.print_summary(result)

    return result


if __name__ == "__main__":
    main()
