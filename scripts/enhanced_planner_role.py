#!/usr/bin/env python3
"""
Enhanced Planner Role Integration for DSPy-Vector System

Task 2.2: Enhanced Planner Role Integration
Extends planner role with vector-based system architecture insights, impact analysis,
and strategic planning capabilities using the Vector-Based System Mapping.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List

try:
    import sys

    sys.path.append("dspy-rag-system/src")
    from dspy_modules.context_models import AIRole, ContextFactory, PlannerContext

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

_LOG = logging.getLogger("enhanced_planner_role")


class EnhancedPlannerRole:
    """Enhanced planner role with vector-based system mapping capabilities."""

    def __init__(self, vector_store_dir: str = "metrics/vector_store"):
        self.vector_store_dir = vector_store_dir
        self.component_embeddings = {}
        self.embedding_model = None
        self.planner_stats = {
            "architecture_analyses": 0,
            "impact_analyses": 0,
            "complexity_assessments": 0,
            "strategic_plans": 0,
            "dependency_mappings": 0,
            "total_analysis_time": 0.0,
        }

    def initialize(self) -> bool:
        """Initialize the enhanced planner role system."""
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

            print("📂 Loading component embeddings for enhanced planner role...")
            with open(embeddings_file, "r", encoding="utf-8") as f:
                self.component_embeddings = json.load(f)

            # Initialize embedding model
            print("🤖 Initializing embedding model for planner analysis...")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

            print(f"✅ Enhanced planner role initialized with {len(self.component_embeddings)} components")
            return True

        except Exception as e:
            print(f"❌ Error initializing enhanced planner role: {e}")
            return False

    def analyze_system_architecture(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze system architecture using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze architecture patterns
            architecture_insights = self._analyze_architecture_patterns(components)

            # Generate architecture recommendations
            recommendations = self._generate_architecture_recommendations(architecture_insights)

            analysis_time = time.time() - start_time
            self.planner_stats["architecture_analyses"] += 1
            self.planner_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "system_architecture",
                "query": query,
                "components_analyzed": len(components),
                "architecture_insights": architecture_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error analyzing system architecture: {e}")
            return {"error": str(e), "analysis_type": "system_architecture"}

    def analyze_change_impact(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze change impact using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze impact patterns
            impact_insights = self._analyze_impact_patterns(components)

            # Generate impact recommendations
            recommendations = self._generate_impact_recommendations(impact_insights)

            analysis_time = time.time() - start_time
            self.planner_stats["impact_analyses"] += 1
            self.planner_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "change_impact",
                "query": query,
                "components_analyzed": len(components),
                "impact_insights": impact_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error analyzing change impact: {e}")
            return {"error": str(e), "analysis_type": "change_impact"}

    def assess_system_complexity(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Assess system complexity using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze complexity patterns
            complexity_insights = self._analyze_complexity_patterns(components)

            # Generate complexity recommendations
            recommendations = self._generate_complexity_recommendations(complexity_insights)

            analysis_time = time.time() - start_time
            self.planner_stats["complexity_assessments"] += 1
            self.planner_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "system_complexity",
                "query": query,
                "components_analyzed": len(components),
                "complexity_insights": complexity_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error assessing system complexity: {e}")
            return {"error": str(e), "analysis_type": "system_complexity"}

    def create_strategic_plan(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Create strategic plan using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze strategic patterns
            strategic_insights = self._analyze_strategic_patterns(components)

            # Generate strategic plan
            plan = self._generate_strategic_plan(strategic_insights)

            analysis_time = time.time() - start_time
            self.planner_stats["strategic_plans"] += 1
            self.planner_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "strategic_planning",
                "query": query,
                "components_analyzed": len(components),
                "strategic_insights": strategic_insights,
                "strategic_plan": plan,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error creating strategic plan: {e}")
            return {"error": str(e), "analysis_type": "strategic_planning"}

    def map_system_dependencies(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Map system dependencies using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze dependency patterns
            dependency_insights = self._analyze_dependency_patterns(components)

            # Generate dependency map
            dependency_map = self._generate_dependency_map(dependency_insights)

            analysis_time = time.time() - start_time
            self.planner_stats["dependency_mappings"] += 1
            self.planner_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "dependency_mapping",
                "query": query,
                "components_analyzed": len(components),
                "dependency_insights": dependency_insights,
                "dependency_map": dependency_map,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error mapping system dependencies: {e}")
            return {"error": str(e), "analysis_type": "dependency_mapping"}

    def _get_relevant_components(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Get relevant components based on semantic similarity."""
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
            _LOG.error(f"Error getting relevant components: {e}")
            return []

    def _analyze_architecture_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze architecture patterns from components."""
        insights = {
            "architectural_layers": [],
            "component_types": [],
            "integration_patterns": [],
            "architectural_concerns": [],
            "design_principles": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            file_path = comp_data["file_path"].lower()

            # Component type analysis
            component_type = comp_data.get("component_type", "unknown")
            insights["component_types"].append(
                {
                    "component": comp_data["file_path"],
                    "type": component_type,
                    "complexity": "high" if comp_data.get("functions", 0) > 20 else "medium",
                    "dependencies": comp_data.get("imports", 0),
                }
            )

            # Architectural layer detection
            if any(layer in file_path for layer in ["api", "endpoint", "controller"]):
                insights["architectural_layers"].append(
                    {
                        "component": comp_data["file_path"],
                        "layer": "presentation",
                        "responsibility": "User interface and request handling",
                    }
                )
            elif any(layer in file_path for layer in ["service", "business", "logic"]):
                insights["architectural_layers"].append(
                    {
                        "component": comp_data["file_path"],
                        "layer": "business",
                        "responsibility": "Business logic and rules",
                    }
                )
            elif any(layer in file_path for layer in ["data", "model", "entity", "repository"]):
                insights["architectural_layers"].append(
                    {
                        "component": comp_data["file_path"],
                        "layer": "data",
                        "responsibility": "Data access and persistence",
                    }
                )

            # Integration patterns
            if comp_data.get("imports", 0) > 10:
                insights["integration_patterns"].append(
                    {
                        "component": comp_data["file_path"],
                        "pattern": "high_integration",
                        "integration_count": comp_data.get("imports", 0),
                        "recommendation": "Consider interface segregation",
                    }
                )

        return insights

    def _analyze_impact_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze impact patterns from components."""
        insights = {
            "high_impact_components": [],
            "dependency_chains": [],
            "risk_assessments": [],
            "change_propagation": [],
            "mitigation_strategies": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            import_count = comp_data.get("imports", 0)

            # High impact components
            if import_count > 15:
                insights["high_impact_components"].append(
                    {
                        "component": comp_data["file_path"],
                        "impact_level": "high",
                        "reason": f"Many dependencies ({import_count} imports)",
                        "risk": "Changes will affect multiple components",
                    }
                )
            elif import_count > 10:
                insights["high_impact_components"].append(
                    {
                        "component": comp_data["file_path"],
                        "impact_level": "medium",
                        "reason": f"Moderate dependencies ({import_count} imports)",
                        "risk": "Changes may affect several components",
                    }
                )

            # Risk assessments
            if comp_data.get("functions", 0) > 30:
                insights["risk_assessments"].append(
                    {
                        "component": comp_data["file_path"],
                        "risk_type": "high_complexity",
                        "risk_level": "medium",
                        "description": "High function count increases change risk",
                        "mitigation": "Break into smaller, focused components",
                    }
                )

        return insights

    def _analyze_complexity_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze complexity patterns from components."""
        insights = {
            "complexity_distribution": [],
            "cognitive_load": [],
            "maintainability_metrics": [],
            "refactoring_opportunities": [],
            "complexity_trends": [],
        }

        total_functions = 0
        total_classes = 0
        total_imports = 0

        for comp in components:
            comp_data = comp["component_data"]
            functions = comp_data.get("functions", 0)
            classes = comp_data.get("classes", 0)
            imports = comp_data.get("imports", 0)

            total_functions += functions
            total_classes += classes
            total_imports += imports

            # Complexity distribution
            if functions > 30:
                complexity_level = "very_high"
            elif functions > 20:
                complexity_level = "high"
            elif functions > 10:
                complexity_level = "medium"
            else:
                complexity_level = "low"

            insights["complexity_distribution"].append(
                {
                    "component": comp_data["file_path"],
                    "complexity_level": complexity_level,
                    "functions": functions,
                    "classes": classes,
                    "imports": imports,
                }
            )

            # Refactoring opportunities
            if functions > 25 or imports > 15:
                insights["refactoring_opportunities"].append(
                    {
                        "component": comp_data["file_path"],
                        "opportunity_type": "complexity_reduction",
                        "current_metrics": {"functions": functions, "classes": classes, "imports": imports},
                        "recommendation": "Consider breaking into smaller, focused components",
                    }
                )

        # Overall complexity metrics
        avg_functions = total_functions / len(components) if components else 0
        avg_classes = total_classes / len(components) if components else 0
        avg_imports = total_imports / len(components) if components else 0

        insights["cognitive_load"] = {
            "average_functions": round(avg_functions, 2),
            "average_classes": round(avg_classes, 2),
            "average_imports": round(avg_imports, 2),
            "overall_complexity": "high" if avg_functions > 20 or avg_imports > 15 else "medium",
        }

        return insights

    def _analyze_strategic_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze strategic patterns from components."""
        insights = {
            "technology_stack": [],
            "architectural_decisions": [],
            "scalability_patterns": [],
            "maintainability_patterns": [],
            "strategic_opportunities": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            file_path = comp_data["file_path"].lower()

            # Technology stack analysis
            if any(tech in file_path for tech in ["api", "rest", "graphql"]):
                insights["technology_stack"].append(
                    {
                        "component": comp_data["file_path"],
                        "technology": "API Framework",
                        "maturity": "established",
                        "recommendation": "Continue with current API approach",
                    }
                )

            if any(tech in file_path for tech in ["vector", "embedding", "ml"]):
                insights["technology_stack"].append(
                    {
                        "component": comp_data["file_path"],
                        "technology": "Machine Learning",
                        "maturity": "emerging",
                        "recommendation": "Invest in ML capabilities and expertise",
                    }
                )

            # Scalability patterns
            if comp_data.get("functions", 0) > 20:
                insights["scalability_patterns"].append(
                    {
                        "component": comp_data["file_path"],
                        "pattern": "high_complexity",
                        "scalability_concern": "High complexity may limit scalability",
                        "recommendation": "Consider microservices or modular architecture",
                    }
                )

        return insights

    def _analyze_dependency_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze dependency patterns from components."""
        insights = {
            "dependency_graph": [],
            "circular_dependencies": [],
            "dependency_clusters": [],
            "critical_paths": [],
            "optimization_opportunities": [],
        }

        # Build dependency graph
        for comp in components:
            comp_data = comp["component_data"]
            dependencies = []

            # Simulate dependency analysis (in real implementation, this would parse actual imports)
            if comp_data.get("imports", 0) > 0:
                dependencies = [f"import_{i}" for i in range(min(comp_data.get("imports", 0), 5))]

            insights["dependency_graph"].append(
                {
                    "component": comp_data["file_path"],
                    "dependencies": dependencies,
                    "dependency_count": comp_data.get("imports", 0),
                    "is_critical": comp_data.get("imports", 0) > 15,
                }
            )

            # Critical path identification
            if comp_data.get("imports", 0) > 15:
                insights["critical_paths"].append(
                    {
                        "component": comp_data["file_path"],
                        "criticality": "high",
                        "reason": "Many dependencies",
                        "impact": "Changes affect multiple components",
                    }
                )

        return insights

    def _generate_architecture_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate architecture recommendations."""
        recommendations = []

        # Component type recommendations
        high_complexity_components = [
            comp for comp in insights.get("component_types", []) if comp["complexity"] == "high"
        ]

        for comp in high_complexity_components:
            recommendations.append(
                {
                    "type": "architecture_refactoring",
                    "priority": "high",
                    "component": comp["component"],
                    "message": "Consider breaking high-complexity component into smaller modules",
                    "effort": "medium",
                }
            )

        # Integration pattern recommendations
        for pattern in insights.get("integration_patterns", []):
            recommendations.append(
                {
                    "type": "integration_optimization",
                    "priority": "medium",
                    "component": pattern["component"],
                    "message": pattern["recommendation"],
                    "effort": "low",
                }
            )

        return recommendations

    def _generate_impact_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate impact recommendations."""
        recommendations = []

        # High impact component recommendations
        for component in insights.get("high_impact_components", []):
            recommendations.append(
                {
                    "type": "impact_mitigation",
                    "priority": component["impact_level"],
                    "component": component["component"],
                    "message": f"Implement comprehensive testing for {component['reason']}",
                    "effort": "high" if component["impact_level"] == "high" else "medium",
                }
            )

        # Risk mitigation recommendations
        for risk in insights.get("risk_assessments", []):
            recommendations.append(
                {
                    "type": "risk_mitigation",
                    "priority": risk["risk_level"],
                    "component": risk["component"],
                    "message": risk["mitigation"],
                    "effort": "medium",
                }
            )

        return recommendations

    def _generate_complexity_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate complexity recommendations."""
        recommendations = []

        # Refactoring recommendations
        for opportunity in insights.get("refactoring_opportunities", []):
            recommendations.append(
                {
                    "type": "complexity_reduction",
                    "priority": "medium",
                    "component": opportunity["component"],
                    "message": opportunity["recommendation"],
                    "effort": "high",
                }
            )

        # Overall complexity recommendations
        cognitive_load = insights.get("cognitive_load", {})
        if cognitive_load.get("overall_complexity") == "high":
            recommendations.append(
                {
                    "type": "system_architecture",
                    "priority": "high",
                    "component": "system_wide",
                    "message": "Consider architectural refactoring to reduce overall complexity",
                    "effort": "very_high",
                }
            )

        return recommendations

    def _generate_strategic_plan(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic plan."""
        plan = {
            "technology_roadmap": [],
            "architectural_goals": [],
            "implementation_priorities": [],
            "success_metrics": [],
            "timeline": [],
        }

        # Technology roadmap
        for tech in insights.get("technology_stack", []):
            plan["technology_roadmap"].append(
                {
                    "technology": tech["technology"],
                    "current_maturity": tech["maturity"],
                    "target_maturity": "mature",
                    "timeline": "6-12 months",
                    "priority": "high" if tech["maturity"] == "emerging" else "medium",
                }
            )

        # Architectural goals
        plan["architectural_goals"].extend(
            [
                {
                    "goal": "Reduce system complexity",
                    "target": "Average functions per component < 15",
                    "timeline": "3-6 months",
                    "priority": "high",
                },
                {
                    "goal": "Improve maintainability",
                    "target": "Dependency count per component < 10",
                    "timeline": "3-6 months",
                    "priority": "medium",
                },
                {
                    "goal": "Enhance scalability",
                    "target": "Modular architecture with clear boundaries",
                    "timeline": "6-12 months",
                    "priority": "medium",
                },
            ]
        )

        return plan

    def _generate_dependency_map(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dependency map."""
        dependency_map = {"components": [], "relationships": [], "critical_paths": [], "optimization_targets": []}

        # Component mapping
        for comp in insights.get("dependency_graph", []):
            dependency_map["components"].append(
                {
                    "id": comp["component"],
                    "dependencies": comp["dependencies"],
                    "dependency_count": comp["dependency_count"],
                    "critical": comp["is_critical"],
                }
            )

        # Critical paths
        for path in insights.get("critical_paths", []):
            dependency_map["critical_paths"].append(
                {
                    "component": path["component"],
                    "criticality": path["criticality"],
                    "reason": path["reason"],
                    "impact": path["impact"],
                }
            )

        return dependency_map

    def get_planner_stats(self) -> Dict[str, Any]:
        """Get planner role statistics."""
        return {
            "total_analyses": sum(
                [
                    self.planner_stats["architecture_analyses"],
                    self.planner_stats["impact_analyses"],
                    self.planner_stats["complexity_assessments"],
                    self.planner_stats["strategic_plans"],
                    self.planner_stats["dependency_mappings"],
                ]
            ),
            "analyses_by_type": {
                "architecture": self.planner_stats["architecture_analyses"],
                "impact_analysis": self.planner_stats["impact_analyses"],
                "complexity_assessment": self.planner_stats["complexity_assessments"],
                "strategic_planning": self.planner_stats["strategic_plans"],
                "dependency_mapping": self.planner_stats["dependency_mappings"],
            },
            "total_analysis_time_ms": self.planner_stats["total_analysis_time"] * 1000,
            "average_analysis_time_ms": (
                self.planner_stats["total_analysis_time"]
                / max(
                    1,
                    sum(
                        [
                            self.planner_stats["architecture_analyses"],
                            self.planner_stats["impact_analyses"],
                            self.planner_stats["complexity_assessments"],
                            self.planner_stats["strategic_plans"],
                            self.planner_stats["dependency_mappings"],
                        ]
                    ),
                )
                * 1000
            ),
        }


def main():
    """Main function for testing the enhanced planner role."""
    print("🚀 Enhanced Planner Role Test")
    print("=" * 50)

    # Initialize the enhanced planner role
    planner_role = EnhancedPlannerRole()

    if not planner_role.initialize():
        print("❌ Failed to initialize enhanced planner role")
        return

    # Test different analysis types
    test_queries = [
        "What's the current system architecture of our memory system?",
        "What would be the impact of refactoring the database layer?",
        "How complex is our current vector system implementation?",
        "What's our strategic technology roadmap for the next year?",
        "How are our components interconnected and what are the dependencies?",
    ]

    print("\n🧪 Testing Enhanced Planner Role Capabilities...")
    print("=" * 50)

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        print("-" * 40)

        # Determine analysis type based on query
        if "architecture" in query.lower():
            result = planner_role.analyze_system_architecture(query)
        elif "impact" in query.lower():
            result = planner_role.analyze_change_impact(query)
        elif "complex" in query.lower():
            result = planner_role.assess_system_complexity(query)
        elif "strategic" in query.lower() or "roadmap" in query.lower():
            result = planner_role.create_strategic_plan(query)
        elif "interconnected" in query.lower() or "dependencies" in query.lower():
            result = planner_role.map_system_dependencies(query)
        else:
            result = planner_role.analyze_system_architecture(query)

        if "error" in result:
            print(f"❌ Analysis failed: {result['error']}")
        else:
            print(f"✅ Analysis completed in {result['analysis_time_ms']:.2f}ms")
            print(f"📊 Components analyzed: {result['components_analyzed']}")

            # Show key insights based on analysis type
            if "architecture_insights" in result:
                insights = result["architecture_insights"]
                if insights.get("architectural_layers"):
                    print(f"   🏗️ Architectural layers: {len(insights['architectural_layers'])}")
                if insights.get("component_types"):
                    print(f"   🔧 Component types: {len(insights['component_types'])}")

            if "impact_insights" in result:
                insights = result["impact_insights"]
                if insights.get("high_impact_components"):
                    print(f"   ⚠️ High impact components: {len(insights['high_impact_components'])}")

            if "complexity_insights" in result:
                insights = result["complexity_insights"]
                if insights.get("refactoring_opportunities"):
                    print(f"   🔄 Refactoring opportunities: {len(insights['refactoring_opportunities'])}")

            if "recommendations" in result:
                print(f"   💡 Recommendations: {len(result['recommendations'])}")

    # Show planner statistics
    print("\n📊 Enhanced Planner Role Statistics:")
    print("=" * 50)
    stats = planner_role.get_planner_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
