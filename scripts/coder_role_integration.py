#!/usr/bin/env python3
"""
Coder Role Integration for Vector-Based System Mapping

Task 2.3: Smart Integration with Coder Role
Integrates vector-based system mapping with the coder role for enhanced capabilities.
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


class CoderRoleIntegration:
    """Integrates vector-based system mapping with coder role capabilities."""

    def __init__(
        self, vector_store_dir: str = "metrics/vector_store", enhanced_context_dir: str = "metrics/enhanced_context"
    ):
        self.vector_store_dir = vector_store_dir
        self.enhanced_context_dir = enhanced_context_dir
        self.component_embeddings = {}
        self.context_retriever = None
        self.embedding_model = None
        self.integration_stats = {
            "coder_queries_processed": 0,
            "context_integrations": 0,
            "recommendations_generated": 0,
            "integration_time": 0.0,
        }

    def load_integration_data(self) -> bool:
        """Load all necessary data for coder role integration."""
        try:
            # Load component embeddings
            embeddings_file = os.path.join(self.vector_store_dir, "component_embeddings.json")
            if not os.path.exists(embeddings_file):
                print(f"❌ Embeddings file not found: {embeddings_file}")
                return False

            print("📂 Loading component embeddings...")
            with open(embeddings_file, "r", encoding="utf-8") as f:
                self.component_embeddings = json.load(f)

            # Load enhanced context data
            context_file = os.path.join(self.enhanced_context_dir, "context_retrieval_results.json")
            if os.path.exists(context_file):
                with open(context_file, "r", encoding="utf-8") as f:
                    self.context_data = json.load(f)
            else:
                self.context_data = {}

            print(f"✅ Loaded {len(self.component_embeddings)} component embeddings")
            return True

        except Exception as e:
            print(f"❌ Error loading integration data: {e}")
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

    def enhance_coder_context(self, coder_query: str, top_k: int = 5) -> Dict[str, Any]:
        """Enhance coder role context with vector-based system mapping."""
        if not self.embedding_model or not self.component_embeddings:
            print("❌ No embeddings available for context enhancement")
            return {}

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(coder_query, convert_to_tensor=False)

            # Find similar components
            similarities = []
            for component_id, component_data in self.component_embeddings.items():
                component_embedding = np.array(component_data["embedding"])
                similarity = np.dot(query_embedding, component_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(component_embedding)
                )

                similarities.append(
                    {"component_id": component_id, "similarity": float(similarity), "component_data": component_data}
                )

            # Sort by similarity and get top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            top_components = similarities[:top_k]

            # Build enhanced context
            enhanced_context = {
                "original_query": coder_query,
                "relevant_components": top_components,
                "system_context": self._build_system_context(top_components),
                "recommendations": self._generate_recommendations(coder_query, top_components),
                "integration_timestamp": datetime.now().isoformat(),
            }

            self.integration_stats["coder_queries_processed"] += 1
            self.integration_stats["context_integrations"] += 1

            return enhanced_context

        except Exception as e:
            print(f"❌ Error in context enhancement: {e}")
            return {}

    def _build_system_context(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comprehensive system context from relevant components."""
        system_context = {
            "component_types": {},
            "file_paths": [],
            "imports_analysis": {},
            "function_analysis": {},
            "class_analysis": {},
        }

        for comp in components:
            comp_data = comp["component_data"]

            # Component type analysis
            comp_type = comp_data.get("component_type", "unknown")
            if comp_type not in system_context["component_types"]:
                system_context["component_types"][comp_type] = 0
            system_context["component_types"][comp_type] += 1

            # File path analysis
            file_path = comp_data.get("file_path", "")
            if file_path:
                system_context["file_paths"].append(file_path)

            # Import analysis
            imports_count = comp_data.get("imports", 0)
            if imports_count > 0:
                if "high_imports" not in system_context["imports_analysis"]:
                    system_context["imports_analysis"]["high_imports"] = []
                if imports_count > 10:
                    system_context["imports_analysis"]["high_imports"].append(file_path)

            # Function analysis
            functions_count = comp_data.get("functions", 0)
            if functions_count > 0:
                if "high_functions" not in system_context["function_analysis"]:
                    system_context["function_analysis"]["high_functions"] = []
                if functions_count > 20:
                    system_context["function_analysis"]["high_functions"].append(file_path)

            # Class analysis
            classes_count = comp_data.get("classes", 0)
            if classes_count > 0:
                if "high_classes" not in system_context["class_analysis"]:
                    system_context["class_analysis"]["high_classes"] = []
                if classes_count > 5:
                    system_context["class_analysis"]["high_classes"].append(file_path)

        return system_context

    def _generate_recommendations(self, query: str, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate intelligent recommendations based on the query and components."""
        recommendations = []

        # Analyze query intent
        query_lower = query.lower()

        # Code quality recommendations
        if any(word in query_lower for word in ["quality", "improve", "optimize", "refactor"]):
            recommendations.append(
                {
                    "type": "code_quality",
                    "priority": "high",
                    "message": "Consider code quality improvements for identified components",
                    "components": [comp["component_data"]["file_path"] for comp in components[:3]],
                }
            )

        # Testing recommendations
        if any(word in query_lower for word in ["test", "testing", "validate", "verify"]):
            recommendations.append(
                {
                    "type": "testing",
                    "priority": "medium",
                    "message": "Ensure comprehensive testing coverage for related components",
                    "components": [comp["component_data"]["file_path"] for comp in components[:3]],
                }
            )

        # Performance recommendations
        if any(word in query_lower for word in ["performance", "speed", "efficient", "optimize"]):
            recommendations.append(
                {
                    "type": "performance",
                    "priority": "medium",
                    "message": "Analyze performance characteristics of identified components",
                    "components": [comp["component_data"]["file_path"] for comp in components[:3]],
                }
            )

        # Security recommendations
        if any(word in query_lower for word in ["security", "secure", "vulnerability", "safe"]):
            recommendations.append(
                {
                    "type": "security",
                    "priority": "high",
                    "message": "Review security implications of identified components",
                    "components": [comp["component_data"]["file_path"] for comp in components[:3]],
                }
            )

        # Dependency recommendations
        if any(word in query_lower for word in ["dependency", "import", "module", "package"]):
            recommendations.append(
                {
                    "type": "dependency",
                    "priority": "medium",
                    "message": "Review dependency relationships and potential conflicts",
                    "components": [comp["component_data"]["file_path"] for comp in components[:3]],
                }
            )

        # Default recommendation
        if not recommendations:
            recommendations.append(
                {
                    "type": "general",
                    "priority": "low",
                    "message": "Consider reviewing related components for consistency and best practices",
                    "components": [comp["component_data"]["file_path"] for comp in components[:2]],
                }
            )

        self.integration_stats["recommendations_generated"] += len(recommendations)
        return recommendations

    def analyze_coder_performance(self, coder_queries: List[str]) -> Dict[str, Any]:
        """Analyze coder role performance with enhanced context."""
        print("🔍 Analyzing coder role performance with enhanced context...")

        performance_analysis = {
            "total_queries": len(coder_queries),
            "enhanced_contexts": {},
            "recommendation_distribution": {},
            "component_type_usage": {},
            "similarity_analysis": [],
        }

        for query in coder_queries:
            enhanced_context = self.enhance_coder_context(query)

            if enhanced_context:
                performance_analysis["enhanced_contexts"][query] = enhanced_context

                # Analyze recommendations
                for rec in enhanced_context.get("recommendations", []):
                    rec_type = rec["type"]
                    if rec_type not in performance_analysis["recommendation_distribution"]:
                        performance_analysis["recommendation_distribution"][rec_type] = 0
                    performance_analysis["recommendation_distribution"][rec_type] += 1

                # Analyze component types
                for comp in enhanced_context.get("relevant_components", []):
                    comp_type = comp["component_data"].get("component_type", "unknown")
                    if comp_type not in performance_analysis["component_type_usage"]:
                        performance_analysis["component_type_usage"][comp_type] = 0
                    performance_analysis["component_type_usage"][comp_type] += 1

                # Analyze similarities
                similarities = [comp["similarity"] for comp in enhanced_context.get("relevant_components", [])]
                if similarities:
                    performance_analysis["similarity_analysis"].extend(similarities)

        # Calculate similarity statistics
        if performance_analysis["similarity_analysis"]:
            similarities = performance_analysis["similarity_analysis"]
            performance_analysis["similarity_stats"] = {
                "min": min(similarities),
                "max": max(similarities),
                "avg": sum(similarities) / len(similarities),
                "median": sorted(similarities)[len(similarities) // 2],
            }

        return performance_analysis

    def export_integration_results(
        self, results: Dict[str, Any], output_dir: str = "metrics/coder_integration"
    ) -> Dict[str, str]:
        """Export integration results to files."""
        os.makedirs(output_dir, exist_ok=True)

        export_files = {}

        # Export integration results
        results_file = os.path.join(output_dir, "integration_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        export_files["results"] = results_file

        # Export integration statistics
        stats_file = os.path.join(output_dir, "integration_stats.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(self.integration_stats, f, indent=2, ensure_ascii=False)
        export_files["stats"] = stats_file

        return export_files

    def create_coder_integration(self) -> Dict[str, Any]:
        """Create complete coder role integration system."""
        start_time = time.time()

        print("🚀 Creating coder role integration system...")

        # Initialize embedding model
        if not self.initialize_embedding_model():
            return {}

        # Load integration data
        if not self.load_integration_data():
            return {}

        # Test coder role queries
        coder_queries = [
            "How can I improve the code quality of the database connection module?",
            "What testing should I implement for the file processing system?",
            "How can I optimize the performance of the API integration?",
            "What security considerations should I review in the memory system?",
            "How can I refactor the dependency analysis components?",
            "What best practices should I apply to the vector embedding system?",
            "How can I enhance the web visualization interface?",
            "What documentation improvements are needed for the coder role?",
        ]

        print("🧪 Testing coder role integration...")

        # Analyze performance
        performance_analysis = self.analyze_coder_performance(coder_queries)

        # Export results
        export_files = self.export_integration_results(performance_analysis)

        self.integration_stats["integration_time"] = time.time() - start_time

        return {
            "timestamp": datetime.now().isoformat(),
            "project": "Vector-Based System Mapping",
            "integration_stats": self.integration_stats,
            "performance_analysis": performance_analysis,
            "export_files": export_files,
            "total_queries_tested": len(coder_queries),
        }

    def print_summary(self, result: Dict[str, Any]):
        """Print coder role integration summary."""
        stats = result.get("integration_stats", {})
        analysis = result.get("performance_analysis", {})

        print("\n" + "=" * 60)
        print("🤖 CODER ROLE INTEGRATION SUMMARY")
        print("=" * 60)

        print(f"🟢 Coder Queries Processed: {stats.get('coder_queries_processed', 0)}")
        print(f"🔗 Context Integrations: {stats.get('context_integrations', 0)}")
        print(f"💡 Recommendations Generated: {stats.get('recommendations_generated', 0)}")
        print(f"⏱️ Integration Time: {stats.get('integration_time', 0):.3f}s")

        if analysis.get("similarity_stats"):
            sim_stats = analysis["similarity_stats"]
            print("\n📈 Similarity Statistics:")
            print(f"  • Min: {sim_stats['min']:.3f}")
            print(f"  • Max: {sim_stats['max']:.3f}")
            print(f"  • Average: {sim_stats['avg']:.3f}")
            print(f"  • Median: {sim_stats['median']:.3f}")

        if analysis.get("recommendation_distribution"):
            print("\n💡 Recommendation Distribution:")
            for rec_type, count in analysis["recommendation_distribution"].items():
                print(f"  • {rec_type}: {count} recommendations")

        if analysis.get("component_type_usage"):
            print("\n📊 Component Type Usage:")
            for comp_type, count in analysis["component_type_usage"].items():
                print(f"  • {comp_type}: {count} usages")

        print("\n🎯 B-1047 Phase 2 Progress:")
        print("  ✅ Task 2.1: Vector Store Integration for System Components - COMPLETED")
        print("  ✅ Task 2.2: Enhanced Context Retrieval - COMPLETED")
        print("  ✅ Task 2.3: Smart Integration with Coder Role - COMPLETED")
        print("\n🚀 Phase 2 Complete! Ready for Phase 3.")


def main():
    """Main function for coder role integration."""
    print("🚀 Continuing B-1047 Phase 2: Enhanced Context Integration")
    print("=" * 60)
    print("📋 Task 2.3: Smart Integration with Coder Role")
    print("=" * 60)

    # Initialize coder role integration
    integration = CoderRoleIntegration()

    # Create coder integration system
    result = integration.create_coder_integration()

    if result:
        # Print summary
        integration.print_summary(result)

    return result


if __name__ == "__main__":
    main()
