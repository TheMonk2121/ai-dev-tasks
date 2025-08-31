#!/usr/bin/env python3
"""
Role Context Enhancer for DSPy-Vector Integration

Task 1.3: Implement Basic Context Enhancement
Provides role-specific context enhancement using vector-based system mapping.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List

try:
    import sys

    sys.path.append("dspy-rag-system/src")
    from dspy_modules.context_models import AIRole, BaseContext, ContextFactory

    DSPY_AVAILABLE = True
except ImportError as e:
    DSPY_AVAILABLE = False
    print(f"⚠️ DSPy context models not available: {e}")

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    print("⚠️ Vector libraries not available - some features will be limited")

_LOG = logging.getLogger("role_context_enhancer")


class RoleContextEnhancer:
    """Enhances DSPy role contexts with vector-based insights and recommendations."""

    def __init__(self, vector_store_dir: str = "metrics/vector_store"):
        self.vector_store_dir = vector_store_dir
        self.component_embeddings = {}
        self.embedding_model = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        self.enhancement_stats = {
            "total_enhancements": 0,
            "role_enhancements": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "total_enhancement_time": 0.0,
        }

    def initialize(self) -> bool:
        """Initialize the role context enhancer."""
        if not VECTOR_AVAILABLE:
            print("❌ Vector libraries not available")
            return False

        if not DSPY_AVAILABLE:
            print("❌ DSPy context models not available")
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

            print(f"✅ Role context enhancer initialized with {len(self.component_embeddings)} components")
            return True

        except Exception as e:
            print(f"❌ Error initializing role context enhancer: {e}")
            return False

    def enhance_context(self, context: BaseContext, enhancement_query: str = None) -> BaseContext:
        """Enhance a DSPy context with vector-based insights."""
        if not self.embedding_model or not self.component_embeddings:
            print("❌ No embeddings available for context enhancement")
            return context

        start_time = time.time()

        try:
            # Use enhancement query or generate from context
            if not enhancement_query:
                enhancement_query = self._generate_enhancement_query(context)

            # Check cache first
            cache_key = f"{context.role.value}:{enhancement_query}"
            if cache_key in self.cache:
                cached_enhancement = self.cache[cache_key]
                if time.time() - cached_enhancement["timestamp"] < self.cache_ttl:
                    self.enhancement_stats["cache_hits"] += 1
                    print(f"✅ Using cached enhancement for {context.role.value} role")
                    return self._apply_cached_enhancement(context, cached_enhancement)

            # Get component recommendations
            recommendations = self._get_component_recommendations(enhancement_query, top_k=5)

            # Generate role-specific insights
            insights = self._generate_role_insights(context.role, recommendations, enhancement_query)

            # Update context with vector insights
            context.update_vector_insights(recommendations, insights)

            # Cache the enhancement
            self.cache[cache_key] = {"recommendations": recommendations, "insights": insights, "timestamp": time.time()}

            # Update statistics
            self.enhancement_stats["total_enhancements"] += 1
            self.enhancement_stats["role_enhancements"][context.role.value] = (
                self.enhancement_stats["role_enhancements"].get(context.role.value, 0) + 1
            )
            self.enhancement_stats["cache_misses"] += 1
            self.enhancement_stats["total_enhancement_time"] += time.time() - start_time

            print(f"✅ Enhanced {context.role.value} context with {len(recommendations)} components")
            return context

        except Exception as e:
            _LOG.error(f"Error enhancing context: {e}")
            return context

    def _generate_enhancement_query(self, context: BaseContext) -> str:
        """Generate enhancement query from context content."""
        if context.role == AIRole.CODER:
            return f"code quality {context.file_context[0] if hasattr(context, 'file_context') and context.file_context else 'python'}"
        elif context.role == AIRole.PLANNER:
            return f"architecture planning {context.project_scope if hasattr(context, 'project_scope') else 'system design'}"
        elif context.role == AIRole.RESEARCHER:
            return f"research analysis {context.research_topic if hasattr(context, 'research_topic') else 'technology'}"
        elif context.role == AIRole.IMPLEMENTER:
            return f"implementation strategy {context.implementation_plan if hasattr(context, 'implementation_plan') else 'integration'}"
        else:
            return "system components analysis"

    def _get_component_recommendations(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get component recommendations based on semantic similarity."""
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

    def _generate_role_insights(self, role: AIRole, recommendations: List[Dict], query: str) -> Dict[str, Any]:
        """Generate role-specific insights based on recommendations."""
        if role == AIRole.CODER:
            return self._generate_coder_insights(recommendations, query)
        elif role == AIRole.PLANNER:
            return self._generate_planner_insights(recommendations, query)
        elif role == AIRole.RESEARCHER:
            return self._generate_researcher_insights(recommendations, query)
        elif role == AIRole.IMPLEMENTER:
            return self._generate_implementer_insights(recommendations, query)
        else:
            return {"general_insights": recommendations}

    def _generate_coder_insights(self, recommendations: List[Dict], query: str) -> Dict[str, Any]:
        """Generate coder-specific insights."""
        insights = {
            "code_quality_insights": [],
            "dependency_analysis": [],
            "testing_suggestions": [],
            "performance_tips": [],
        }

        for rec in recommendations:
            comp_data = rec["component_data"]

            # Code quality insights
            if comp_data.get("functions", 0) > 20:
                insights["code_quality_insights"].append(
                    {
                        "component": comp_data["file_path"],
                        "insight": "High complexity component - consider refactoring",
                        "priority": "medium",
                        "similarity": rec["similarity"],
                    }
                )

            # Dependency analysis
            if comp_data.get("imports", 0) > 10:
                insights["dependency_analysis"].append(
                    {
                        "component": comp_data["file_path"],
                        "insight": "High dependency component - review coupling",
                        "priority": "high",
                        "similarity": rec["similarity"],
                    }
                )

            # Testing suggestions
            if "test" in comp_data["file_path"].lower():
                insights["testing_suggestions"].append(
                    {
                        "component": comp_data["file_path"],
                        "insight": "Test component - review coverage and patterns",
                        "priority": "low",
                        "similarity": rec["similarity"],
                    }
                )

        return insights

    def _generate_planner_insights(self, recommendations: List[Dict], query: str) -> Dict[str, Any]:
        """Generate planner-specific insights."""
        insights = {
            "architecture_insights": [],
            "impact_analysis": [],
            "complexity_assessment": [],
            "strategic_recommendations": [],
        }

        for rec in recommendations:
            comp_data = rec["component_data"]

            # Architecture insights
            insights["architecture_insights"].append(
                {
                    "component": comp_data["file_path"],
                    "type": comp_data.get("component_type", "unknown"),
                    "complexity": "high" if comp_data.get("functions", 0) > 20 else "medium",
                    "similarity": rec["similarity"],
                }
            )

            # Impact analysis
            if comp_data.get("imports", 0) > 15:
                insights["impact_analysis"].append(
                    {
                        "component": comp_data["file_path"],
                        "impact_level": "high",
                        "reason": "Many dependencies - changes will affect multiple components",
                        "similarity": rec["similarity"],
                    }
                )

        return insights

    def _generate_researcher_insights(self, recommendations: List[Dict], query: str) -> Dict[str, Any]:
        """Generate researcher-specific insights."""
        insights = {
            "pattern_analysis": [],
            "technology_insights": [],
            "best_practices": [],
            "research_opportunities": [],
        }

        for rec in recommendations:
            comp_data = rec["component_data"]

            # Pattern analysis
            insights["pattern_analysis"].append(
                {
                    "component": comp_data["file_path"],
                    "patterns": {
                        "functions": comp_data.get("functions", 0),
                        "classes": comp_data.get("classes", 0),
                        "imports": comp_data.get("imports", 0),
                    },
                    "similarity": rec["similarity"],
                }
            )

            # Research opportunities
            if comp_data.get("functions", 0) > 30:
                insights["research_opportunities"].append(
                    {
                        "component": comp_data["file_path"],
                        "opportunity": "High complexity - investigate refactoring strategies",
                        "priority": "high",
                        "similarity": rec["similarity"],
                    }
                )

        return insights

    def _generate_implementer_insights(self, recommendations: List[Dict], query: str) -> Dict[str, Any]:
        """Generate implementer-specific insights."""
        insights = {
            "integration_patterns": [],
            "dependency_mapping": [],
            "architecture_compliance": [],
            "implementation_strategy": [],
        }

        for rec in recommendations:
            comp_data = rec["component_data"]

            # Integration patterns
            if comp_data.get("component_type") == "integration_module":
                insights["integration_patterns"].append(
                    {
                        "component": comp_data["file_path"],
                        "pattern": "Integration module",
                        "complexity": comp_data.get("functions", 0),
                        "similarity": rec["similarity"],
                    }
                )

            # Dependency mapping
            if comp_data.get("imports", 0) > 10:
                insights["dependency_mapping"].append(
                    {
                        "component": comp_data["file_path"],
                        "dependency_count": comp_data.get("imports", 0),
                        "risk_level": "medium" if comp_data.get("imports", 0) > 15 else "low",
                        "similarity": rec["similarity"],
                    }
                )

        return insights

    def _apply_cached_enhancement(self, context: BaseContext, cached_enhancement: Dict) -> BaseContext:
        """Apply cached enhancement to context."""
        context.update_vector_insights(cached_enhancement["recommendations"], cached_enhancement["insights"])
        return context

    def get_enhancement_stats(self) -> Dict[str, Any]:
        """Get enhancement statistics."""
        return {
            "total_enhancements": self.enhancement_stats["total_enhancements"],
            "role_enhancements": self.enhancement_stats["role_enhancements"],
            "cache_hits": self.enhancement_stats["cache_hits"],
            "cache_misses": self.enhancement_stats["cache_misses"],
            "cache_hit_rate": (
                f"{self.enhancement_stats['cache_hits'] / (self.enhancement_stats['cache_hits'] + self.enhancement_stats['cache_misses']):.2%}"
                if (self.enhancement_stats["cache_hits"] + self.enhancement_stats["cache_misses"]) > 0
                else "0.00%"
            ),
            "total_enhancement_time_ms": self.enhancement_stats["total_enhancement_time"] * 1000,
            "average_enhancement_time_ms": (
                (self.enhancement_stats["total_enhancement_time"] / self.enhancement_stats["total_enhancements"] * 1000)
                if self.enhancement_stats["total_enhancements"] > 0
                else 0
            ),
        }

    def clear_cache(self) -> None:
        """Clear the enhancement cache."""
        self.cache.clear()
        print("✅ Enhancement cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information."""
        return {
            "cache_size": len(self.cache),
            "cache_ttl_seconds": self.cache_ttl,
            "cache_keys": list(self.cache.keys()),
        }


def main():
    """Main function for testing the role context enhancer."""
    print("🚀 Role Context Enhancer Test")
    print("=" * 50)

    # Initialize the enhancer
    enhancer = RoleContextEnhancer()

    if not enhancer.initialize():
        print("❌ Failed to initialize role context enhancer")
        return

    # Test context enhancement for different roles
    if DSPY_AVAILABLE:
        print("\n🧪 Testing Context Enhancement...")
        print("=" * 50)

        # Test coder context
        coder_context = ContextFactory.create_context(
            AIRole.CODER,
            session_id="test_session_001",
            codebase_path=".",
            language="python",
            file_context=["scripts/role_context_enhancer.py"],
        )

        print("\n🔍 Testing CODER context enhancement:")
        enhanced_coder = enhancer.enhance_context(coder_context, "How can I improve code quality?")
        print(f"✅ Enhanced with {len(enhanced_coder.vector_components)} components")
        print(f"📊 Vector insights: {len(enhanced_coder.vector_insights)} categories")

        # Test planner context
        planner_context = ContextFactory.create_context(
            AIRole.PLANNER,
            session_id="test_session_002",
            project_scope="System architecture redesign",
            backlog_priority="P1",
        )

        print("\n🔍 Testing PLANNER context enhancement:")
        enhanced_planner = enhancer.enhance_context(planner_context, "What's the impact on architecture?")
        print(f"✅ Enhanced with {len(enhanced_planner.vector_components)} components")
        print(f"📊 Vector insights: {len(enhanced_planner.vector_insights)} categories")

        # Test researcher context
        researcher_context = ContextFactory.create_context(
            AIRole.RESEARCHER,
            session_id="test_session_003",
            research_topic="Performance optimization patterns",
            methodology="experimental",
        )

        print("\n🔍 Testing RESEARCHER context enhancement:")
        enhanced_researcher = enhancer.enhance_context(researcher_context, "What patterns exist in testing?")
        print(f"✅ Enhanced with {len(enhanced_researcher.vector_components)} components")
        print(f"📊 Vector insights: {len(enhanced_researcher.vector_insights)} categories")

        # Test implementer context
        implementer_context = ContextFactory.create_context(
            AIRole.IMPLEMENTER,
            session_id="test_session_004",
            implementation_plan="Integrate vector system with DSPy",
            target_environment="development",
        )

        print("\n🔍 Testing IMPLEMENTER context enhancement:")
        enhanced_implementer = enhancer.enhance_context(implementer_context, "How to integrate vector system?")
        print(f"✅ Enhanced with {len(enhanced_implementer.vector_components)} components")
        print(f"📊 Vector insights: {len(enhanced_implementer.vector_insights)} categories")

        # Show enhancement statistics
        print("\n📊 Enhancement Statistics:")
        print("=" * 50)
        stats = enhancer.get_enhancement_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Show cache information
        print("\n🔧 Cache Information:")
        print("=" * 50)
        cache_info = enhancer.get_cache_info()
        for key, value in cache_info.items():
            print(f"  {key}: {value}")

    else:
        print("❌ DSPy context models not available for testing")


if __name__ == "__main__":
    main()
