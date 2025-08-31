#!/usr/bin/env python3
"""
Vector System Mapper for Vector-Based System Mapping

Task 2.1: Vector Store Integration for System Components
Integrates vector store capabilities for enhanced system component mapping.
"""

import hashlib
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
    print("⚠️ Vector libraries not available - installing...")
    os.system("pip install sentence-transformers numpy")
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer

        VECTOR_AVAILABLE = True
    except ImportError:
        VECTOR_AVAILABLE = False
        print("❌ Failed to install vector libraries")


class VectorSystemMapper:
    """Maps system components using vector embeddings for enhanced context retrieval."""

    def __init__(self, dependency_file: str = "metrics/dependency_analysis.json"):
        self.dependency_file = dependency_file
        self.dependency_data = None
        self.vector_store = {}
        self.component_embeddings = {}
        self.embedding_model = None
        self.mapping_stats = {
            "components_processed": 0,
            "embeddings_generated": 0,
            "vector_queries": 0,
            "mapping_time": 0.0,
        }

    def initialize_embedding_model(self) -> bool:
        """Initialize the sentence transformer model for embeddings."""
        if not VECTOR_AVAILABLE:
            print("❌ Vector libraries not available")
            return False

        try:
            print("🤖 Initializing embedding model...")
            # Use a lightweight model for performance
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Embedding model initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing embedding model: {e}")
            return False

    def load_dependencies(self) -> bool:
        """Load dependency data from JSON file."""
        try:
            if not os.path.exists(self.dependency_file):
                print(f"❌ Dependency file not found: {self.dependency_file}")
                return False

            print(f"📂 Loading dependencies from: {self.dependency_file}")
            with open(self.dependency_file, "r", encoding="utf-8") as f:
                self.dependency_data = json.load(f)

            print(f"✅ Loaded {len(self.dependency_data.get('dependencies', {}))} files")
            return True

        except Exception as e:
            print(f"❌ Error loading dependencies: {e}")
            return False

    def extract_component_context(self, file_path: str, file_deps: Dict[str, Any]) -> str:
        """Extract contextual information from a component."""
        context_parts = []

        # File path context
        context_parts.append(f"File: {file_path}")

        # Import context
        imports = file_deps.get("imports", [])
        if imports:
            import_modules = [imp.get("module", "") for imp in imports if imp.get("module")]
            context_parts.append(f"Imports: {', '.join(import_modules[:10])}")  # Limit to first 10

        # Function context
        functions = file_deps.get("functions", [])
        if functions:
            func_names = [func.get("name", "") for func in functions[:5]]  # Limit to first 5
            context_parts.append(f"Functions: {', '.join(func_names)}")

        # Class context
        classes = file_deps.get("classes", [])
        if classes:
            class_names = [cls.get("name", "") for cls in classes[:5]]  # Limit to first 5
            context_parts.append(f"Classes: {', '.join(class_names)}")

        # Directory structure context
        path_parts = file_path.split("/")
        if len(path_parts) > 1:
            context_parts.append(f"Directory: {'/'.join(path_parts[:-1])}")

        return " | ".join(context_parts)

    def generate_component_embeddings(self, max_components: int = 1000) -> Dict[str, Any]:
        """Generate vector embeddings for system components."""
        if not self.embedding_model:
            print("❌ Embedding model not initialized")
            return {}

        if not self.dependency_data:
            print("❌ No dependency data loaded")
            return {}

        print("🔍 Generating component embeddings...")

        components_processed = 0
        embeddings_generated = 0

        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if not file_deps.get("parse_success", False) or components_processed >= max_components:
                continue

            try:
                # Extract component context
                context = self.extract_component_context(file_path, file_deps)

                # Generate embedding
                embedding = self.embedding_model.encode(context, convert_to_tensor=False)

                # Store component data
                component_id = hashlib.md5(file_path.encode()).hexdigest()[:8]

                self.component_embeddings[component_id] = {
                    "file_path": file_path,
                    "context": context,
                    "embedding": embedding.tolist(),
                    "imports": len(file_deps.get("imports", [])),
                    "functions": len(file_deps.get("functions", [])),
                    "classes": len(file_deps.get("classes", [])),
                    "component_type": self._determine_component_type(file_path, file_deps),
                }

                components_processed += 1
                embeddings_generated += 1

                if components_processed % 100 == 0:
                    print(f"  📊 Processed {components_processed} components...")

            except Exception as e:
                print(f"⚠️ Error processing {file_path}: {e}")
                continue

        self.mapping_stats["components_processed"] = components_processed
        self.mapping_stats["embeddings_generated"] = embeddings_generated

        print(f"✅ Generated embeddings for {embeddings_generated} components")
        return self.component_embeddings

    def _determine_component_type(self, file_path: str, file_deps: Dict[str, Any]) -> str:
        """Determine the type of component based on its characteristics."""
        imports = len(file_deps.get("imports", []))
        functions = len(file_deps.get("functions", []))
        classes = len(file_deps.get("classes", []))

        # Determine component type based on characteristics
        if classes > functions and classes > 0:
            return "class_library"
        elif functions > 10:
            return "utility_module"
        elif imports > 10:
            return "integration_module"
        elif "test" in file_path.lower():
            return "test_module"
        elif "script" in file_path.lower():
            return "script"
        else:
            return "module"

    def find_similar_components(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar components using vector similarity."""
        if not self.embedding_model or not self.component_embeddings:
            print("❌ No embeddings available for similarity search")
            return []

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=False)

            # Calculate similarities
            similarities = []
            for component_id, component_data in self.component_embeddings.items():
                component_embedding = np.array(component_data["embedding"])
                similarity = np.dot(query_embedding, component_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(component_embedding)
                )
                similarities.append(
                    {"component_id": component_id, "similarity": float(similarity), "component_data": component_data}
                )

            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)

            self.mapping_stats["vector_queries"] += 1

            return similarities[:top_k]

        except Exception as e:
            print(f"❌ Error in similarity search: {e}")
            return []

    def analyze_component_clusters(self) -> Dict[str, Any]:
        """Analyze component clusters based on embeddings."""
        if not self.component_embeddings:
            print("❌ No component embeddings available")
            return {}

        print("🔍 Analyzing component clusters...")

        # Group components by type
        component_types = {}
        for component_id, component_data in self.component_embeddings.items():
            comp_type = component_data["component_type"]
            if comp_type not in component_types:
                component_types[comp_type] = []
            component_types[comp_type].append(
                {
                    "component_id": component_id,
                    "file_path": component_data["file_path"],
                    "imports": component_data["imports"],
                    "functions": component_data["functions"],
                    "classes": component_data["classes"],
                }
            )

        # Calculate statistics for each type
        type_stats = {}
        for comp_type, components in component_types.items():
            if components:
                type_stats[comp_type] = {
                    "count": len(components),
                    "avg_imports": sum(c["imports"] for c in components) / len(components),
                    "avg_functions": sum(c["functions"] for c in components) / len(components),
                    "avg_classes": sum(c["classes"] for c in components) / len(components),
                    "components": components,
                }

        return {
            "component_types": type_stats,
            "total_components": len(self.component_embeddings),
            "type_distribution": {t: len(c) for t, c in component_types.items()},
        }

    def export_vector_store(self, output_dir: str = "metrics/vector_store") -> Dict[str, str]:
        """Export vector store data."""
        os.makedirs(output_dir, exist_ok=True)

        export_files = {}

        # Export component embeddings
        embeddings_file = os.path.join(output_dir, "component_embeddings.json")
        with open(embeddings_file, "w", encoding="utf-8") as f:
            json.dump(self.component_embeddings, f, indent=2, ensure_ascii=False)

        export_files["embeddings"] = embeddings_file

        # Export component analysis
        analysis = self.analyze_component_clusters()
        analysis_file = os.path.join(output_dir, "component_analysis.json")
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        export_files["analysis"] = analysis_file

        # Export mapping statistics
        stats_file = os.path.join(output_dir, "mapping_stats.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(self.mapping_stats, f, indent=2, ensure_ascii=False)

        export_files["stats"] = stats_file

        return export_files

    def create_vector_mapping(self, max_components: int = 1000) -> Dict[str, Any]:
        """Create complete vector mapping of system components."""
        start_time = time.time()

        print("🚀 Creating vector system mapping...")

        # Initialize embedding model
        if not self.initialize_embedding_model():
            return {}

        # Load dependencies
        if not self.load_dependencies():
            return {}

        # Generate embeddings
        embeddings = self.generate_component_embeddings(max_components)

        # Analyze clusters
        analysis = self.analyze_component_clusters()

        # Export data
        export_files = self.export_vector_store()

        self.mapping_stats["mapping_time"] = time.time() - start_time

        return {
            "timestamp": datetime.now().isoformat(),
            "project": "Vector-Based System Mapping",
            "mapping_stats": self.mapping_stats,
            "component_analysis": analysis,
            "export_files": export_files,
            "total_embeddings": len(embeddings),
        }

    def print_summary(self, result: Dict[str, Any]):
        """Print vector mapping summary."""
        stats = result.get("mapping_stats", {})
        analysis = result.get("component_analysis", {})

        print("\n" + "=" * 60)
        print("🔍 VECTOR SYSTEM MAPPING SUMMARY")
        print("=" * 60)

        print(f"🟢 Components Processed: {stats.get('components_processed', 0)}")
        print(f"🔗 Embeddings Generated: {stats.get('embeddings_generated', 0)}")
        print(f"🔍 Vector Queries: {stats.get('vector_queries', 0)}")
        print(f"⏱️ Mapping Time: {stats.get('mapping_time', 0):.3f}s")

        if analysis.get("component_types"):
            print("\n📊 Component Type Distribution:")
            for comp_type, type_data in analysis["component_types"].items():
                print(f"  • {comp_type}: {type_data['count']} components")

        print("\n🎯 B-1047 Phase 2 Progress:")
        print("  ✅ Task 2.1: Vector Store Integration for System Components - COMPLETED")
        print("  🔄 Task 2.2: Enhanced Context Retrieval - NEXT")
        print("  ⏳ Task 2.3: Smart Integration with Coder Role - PENDING")


def main():
    """Main function for vector system mapping."""
    print("🚀 Starting B-1047 Phase 2: Enhanced Context Integration")
    print("=" * 60)
    print("📋 Task 2.1: Vector Store Integration for System Components")
    print("=" * 60)

    # Initialize vector mapper
    mapper = VectorSystemMapper()

    # Create vector mapping
    result = mapper.create_vector_mapping()

    if result:
        # Print summary
        mapper.print_summary(result)

        # Test similarity search
        print("\n🧪 Testing similarity search...")
        test_queries = ["database connection", "file processing", "API integration", "testing framework"]

        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            similar_components = mapper.find_similar_components(query, top_k=3)

            for i, comp in enumerate(similar_components, 1):
                print(f"  {i}. {comp['component_data']['file_path']} (similarity: {comp['similarity']:.3f})")

    return result


if __name__ == "__main__":
    main()
