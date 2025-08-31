#!/usr/bin/env python3
"""
DSPy-Vector Integration Bridge

Core integration layer between DSPy roles and Vector-Based System Mapping.
Provides seamless context enhancement and intelligent recommendations for all DSPy roles.
"""

import json
import logging
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
    print("⚠️ Vector libraries not available - some features will be limited")

# Import DSPy context models
try:
    import sys

    sys.path.append("dspy-rag-system/src")
    from dspy_modules.context_models import AIRole, BaseContext, ContextFactory

    DSPY_AVAILABLE = True
except ImportError as e:
    DSPY_AVAILABLE = False
    print(f"⚠️ DSPy context models not available: {e}")

_LOG = logging.getLogger("dspy_vector_integration")


class VectorContextEnhancement:
    """Enhances DSPy role contexts with vector-based insights and recommendations."""

    def __init__(self, vector_store_dir: str = "metrics/vector_store"):
        self.vector_store_dir = vector_store_dir
        self.component_embeddings = {}
        self.embedding_model = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL

    def initialize(self) -> bool:
        """Initialize the vector context enhancement system."""
        if not VECTOR_AVAILABLE:
            print("❌ Vector libraries not available")
            return False

        try:
            # Load component embeddings
            embeddings_file = os.path.join(self.vector_store_dir, "component_embeddings.json")
            if not os.path.exists(embeddings_file):
                print(f"❌ Embeddings file not found: {embeddings_file}")
                return False

            print("📂 Loading component embeddings...")
            with open(embeddings_file, "r", encoding="utf-8") as f:
                self.component_embeddings = json.load(f)

            # Initialize embedding model
            print("🤖 Initializing embedding model...")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

            print(f"✅ Vector context enhancement initialized with {len(self.component_embeddings)} components")
            return True

        except Exception as e:
            print(f"❌ Error initializing vector context enhancement: {e}")
            return False

    def get_component_recommendations(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get component recommendations based on semantic similarity."""
        if not self.embedding_model or not self.component_embeddings:
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
            return similarities[:top_k]

        except Exception as e:
            _LOG.error(f"Error getting component recommendations: {e}")
            return []

    def get_role_specific_recommendations(self, role: AIRole, context: str, top_k: int = 5) -> Dict[str, Any]:
        """Get role-specific recommendations based on context and role type."""
        recommendations = self.get_component_recommendations(context, top_k)

        # Role-specific recommendation enhancement
        if role == AIRole.CODER:
            return self._enhance_coder_recommendations(recommendations, context)
        elif role == AIRole.PLANNER:
            return self._enhance_planner_recommendations(recommendations, context)
        elif role == AIRole.RESEARCHER:
            return self._enhance_researcher_recommendations(recommendations, context)
        elif role == AIRole.IMPLEMENTER:
            return self._enhance_implementer_recommendations(recommendations, context)
        else:
            return {"recommendations": recommendations, "role": role.value}

    def _enhance_coder_recommendations(self, recommendations: List[Dict], context: str) -> Dict[str, Any]:
        """Enhance recommendations specifically for coder role."""
        enhanced = {
            "role": "coder",
            "recommendations": recommendations,
            "code_quality_insights": [],
            "dependency_analysis": [],
            "testing_suggestions": [],
            "performance_tips": [],
        }

        for rec in recommendations:
            comp_data = rec["component_data"]

            # Code quality insights
            if comp_data.get("functions", 0) > 20:
                enhanced["code_quality_insights"].append(
                    {
                        "component": comp_data["file_path"],
                        "insight": "High complexity component - consider refactoring",
                        "priority": "medium",
                    }
                )

            # Dependency analysis
            if comp_data.get("imports", 0) > 10:
                enhanced["dependency_analysis"].append(
                    {
                        "component": comp_data["file_path"],
                        "insight": "High dependency component - review coupling",
                        "priority": "high",
                    }
                )

            # Testing suggestions
            if "test" in comp_data["file_path"].lower():
                enhanced["testing_suggestions"].append(
                    {
                        "component": comp_data["file_path"],
                        "insight": "Test component - review coverage and patterns",
                        "priority": "low",
                    }
                )

        return enhanced

    def _enhance_planner_recommendations(self, recommendations: List[Dict], context: str) -> Dict[str, Any]:
        """Enhance recommendations specifically for planner role."""
        enhanced = {
            "role": "planner",
            "recommendations": recommendations,
            "architecture_insights": [],
            "impact_analysis": [],
            "complexity_assessment": [],
            "strategic_recommendations": [],
        }

        for rec in recommendations:
            comp_data = rec["component_data"]

            # Architecture insights
            enhanced["architecture_insights"].append(
                {
                    "component": comp_data["file_path"],
                    "type": comp_data.get("component_type", "unknown"),
                    "complexity": "high" if comp_data.get("functions", 0) > 20 else "medium",
                }
            )

            # Impact analysis
            if comp_data.get("imports", 0) > 15:
                enhanced["impact_analysis"].append(
                    {
                        "component": comp_data["file_path"],
                        "impact_level": "high",
                        "reason": "Many dependencies - changes will affect multiple components",
                    }
                )

        return enhanced

    def _enhance_researcher_recommendations(self, recommendations: List[Dict], context: str) -> Dict[str, Any]:
        """Enhance recommendations specifically for researcher role."""
        enhanced = {
            "role": "researcher",
            "recommendations": recommendations,
            "pattern_analysis": [],
            "technology_insights": [],
            "best_practices": [],
            "research_opportunities": [],
        }

        for rec in recommendations:
            comp_data = rec["component_data"]

            # Pattern analysis
            enhanced["pattern_analysis"].append(
                {
                    "component": comp_data["file_path"],
                    "patterns": {
                        "functions": comp_data.get("functions", 0),
                        "classes": comp_data.get("classes", 0),
                        "imports": comp_data.get("imports", 0),
                    },
                }
            )

            # Research opportunities
            if comp_data.get("functions", 0) > 30:
                enhanced["research_opportunities"].append(
                    {
                        "component": comp_data["file_path"],
                        "opportunity": "High complexity - investigate refactoring strategies",
                        "priority": "high",
                    }
                )

        return enhanced

    def _enhance_implementer_recommendations(self, recommendations: List[Dict], context: str) -> Dict[str, Any]:
        """Enhance recommendations specifically for implementer role."""
        enhanced = {
            "role": "implementer",
            "recommendations": recommendations,
            "integration_patterns": [],
            "dependency_mapping": [],
            "architecture_compliance": [],
            "implementation_strategy": [],
        }

        for rec in recommendations:
            comp_data = rec["component_data"]

            # Integration patterns
            if comp_data.get("component_type") == "integration_module":
                enhanced["integration_patterns"].append(
                    {
                        "component": comp_data["file_path"],
                        "pattern": "Integration module",
                        "complexity": comp_data.get("functions", 0),
                    }
                )

            # Dependency mapping
            if comp_data.get("imports", 0) > 10:
                enhanced["dependency_mapping"].append(
                    {
                        "component": comp_data["file_path"],
                        "dependency_count": comp_data.get("imports", 0),
                        "risk_level": "medium" if comp_data.get("imports", 0) > 15 else "low",
                    }
                )

        return enhanced


class DSPyVectorIntegrationBridge:
    """Main integration bridge between DSPy roles and Vector-Based System Mapping."""

    def __init__(self):
        self.vector_enhancement = VectorContextEnhancement()
        self.performance_metrics = {
            "context_enhancements": 0,
            "total_enhancement_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        self.initialized = False

    def initialize(self) -> bool:
        """Initialize the integration bridge."""
        if not DSPY_AVAILABLE:
            print("❌ DSPy context models not available")
            return False

        if not self.vector_enhancement.initialize():
            print("❌ Vector enhancement system failed to initialize")
            return False

        self.initialized = True
        print("✅ DSPy-Vector Integration Bridge initialized successfully")
        return True

    def enhance_role_context(self, role: AIRole, context: str, **kwargs) -> Dict[str, Any]:
        """Enhance DSPy role context with vector-based insights."""
        if not self.initialized:
            print("❌ Integration bridge not initialized")
            return {}

        start_time = time.time()

        try:
            # Get role-specific recommendations
            enhanced_recommendations = self.vector_enhancement.get_role_specific_recommendations(role, context, top_k=5)

            # Create enhanced context
            enhanced_context = {
                "original_context": context,
                "role": role.value,
                "vector_enhancements": enhanced_recommendations,
                "enhancement_timestamp": datetime.now().isoformat(),
                "performance_metrics": {
                    "enhancement_time_ms": (time.time() - start_time) * 1000,
                    "components_analyzed": len(enhanced_recommendations.get("recommendations", [])),
                    "cache_status": "hit" if context in self.vector_enhancement.cache else "miss",
                },
            }

            # Update performance metrics
            self.performance_metrics["context_enhancements"] += 1
            self.performance_metrics["total_enhancement_time"] += time.time() - start_time

            if context in self.vector_enhancement.cache:
                self.performance_metrics["cache_hits"] += 1
            else:
                self.performance_metrics["cache_misses"] += 1

            return enhanced_context

        except Exception as e:
            _LOG.error(f"Error enhancing role context: {e}")
            return {
                "original_context": context,
                "role": role.value,
                "error": str(e),
                "enhancement_timestamp": datetime.now().isoformat(),
            }

    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status and performance metrics."""
        return {
            "initialized": self.initialized,
            "dspy_available": DSPY_AVAILABLE,
            "vector_available": VECTOR_AVAILABLE,
            "performance_metrics": self.performance_metrics,
            "vector_components": len(self.vector_enhancement.component_embeddings),
            "cache_size": len(self.vector_enhancement.cache),
        }

    def clear_cache(self) -> None:
        """Clear the enhancement cache."""
        self.vector_enhancement.cache.clear()
        print("✅ Enhancement cache cleared")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for the integration bridge."""
        if self.performance_metrics["context_enhancements"] == 0:
            return {"status": "No enhancements performed yet"}

        avg_time = self.performance_metrics["total_enhancement_time"] / self.performance_metrics["context_enhancements"]
        cache_hit_rate = (
            self.performance_metrics["cache_hits"]
            / (self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"])
            if (self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]) > 0
            else 0
        )

        return {
            "total_enhancements": self.performance_metrics["context_enhancements"],
            "average_enhancement_time_ms": avg_time * 1000,
            "cache_hit_rate": f"{cache_hit_rate:.2%}",
            "total_enhancement_time_ms": self.performance_metrics["total_enhancement_time"] * 1000,
        }


def main():
    """Main function for testing the integration bridge."""
    print("🚀 DSPy-Vector Integration Bridge Test")
    print("=" * 50)

    # Initialize the bridge
    bridge = DSPyVectorIntegrationBridge()

    if not bridge.initialize():
        print("❌ Failed to initialize integration bridge")
        return

    # Test context enhancement for different roles
    test_contexts = {
        AIRole.CODER: "How can I improve the code quality of the database connection module?",
        AIRole.PLANNER: "What's the impact of refactoring the memory system on our architecture?",
        AIRole.RESEARCHER: "What patterns exist in our testing implementation across components?",
        AIRole.IMPLEMENTER: "How should I integrate the new vector system with existing DSPy modules?",
    }

    print("\n🧪 Testing Role Context Enhancement...")
    print("=" * 50)

    for role, context in test_contexts.items():
        print(f"\n🔍 Testing {role.value.upper()} role:")
        print(f"Context: {context}")

        enhanced = bridge.enhance_role_context(role, context)

        if "error" in enhanced:
            print(f"❌ Error: {enhanced['error']}")
        else:
            print(
                f"✅ Enhanced with {len(enhanced.get('vector_enhancements', {}).get('recommendations', []))} components"
            )
            print(f"⏱️ Enhancement time: {enhanced['performance_metrics']['enhancement_time_ms']:.2f}ms")

    # Show performance summary
    print("\n📊 Performance Summary:")
    print("=" * 50)
    summary = bridge.get_performance_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Show integration status
    print("\n🔧 Integration Status:")
    print("=" * 50)
    status = bridge.get_integration_status()
    for key, value in status.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
