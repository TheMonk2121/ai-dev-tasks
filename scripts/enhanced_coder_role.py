#!/usr/bin/env python3
"""
Enhanced Coder Role Integration for DSPy-Vector System

Task 2.1: Enhanced Coder Role Integration
Extends coder role with vector-based code quality analysis, dependency management,
and testing strategies using the Vector-Based System Mapping.
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
    from dspy_modules.context_models import AIRole, CoderContext, ContextFactory

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

_LOG = logging.getLogger("enhanced_coder_role")


class EnhancedCoderRole:
    """Enhanced coder role with vector-based system mapping capabilities."""

    def __init__(self, vector_store_dir: str = "metrics/vector_store"):
        self.vector_store_dir = vector_store_dir
        self.component_embeddings = {}
        self.embedding_model = None
        self.coder_stats = {
            "code_quality_analyses": 0,
            "dependency_analyses": 0,
            "testing_strategies": 0,
            "security_insights": 0,
            "performance_analyses": 0,
            "total_analysis_time": 0.0,
        }

    def initialize(self) -> bool:
        """Initialize the enhanced coder role system."""
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

            print("📂 Loading component embeddings for enhanced coder role...")
            with open(embeddings_file, "r", encoding="utf-8") as f:
                self.component_embeddings = json.load(f)

            # Initialize embedding model
            print("🤖 Initializing embedding model for coder analysis...")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

            print(f"✅ Enhanced coder role initialized with {len(self.component_embeddings)} components")
            return True

        except Exception as e:
            print(f"❌ Error initializing enhanced coder role: {e}")
            return False

    def analyze_code_quality(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze code quality using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze code quality patterns
            quality_insights = self._analyze_quality_patterns(components)

            # Generate recommendations
            recommendations = self._generate_quality_recommendations(quality_insights)

            analysis_time = time.time() - start_time
            self.coder_stats["code_quality_analyses"] += 1
            self.coder_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "code_quality",
                "query": query,
                "components_analyzed": len(components),
                "quality_insights": quality_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error analyzing code quality: {e}")
            return {"error": str(e), "analysis_type": "code_quality"}

    def analyze_dependencies(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze dependencies using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze dependency patterns
            dependency_insights = self._analyze_dependency_patterns(components)

            # Generate dependency recommendations
            recommendations = self._generate_dependency_recommendations(dependency_insights)

            analysis_time = time.time() - start_time
            self.coder_stats["dependency_analyses"] += 1
            self.coder_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "dependency_analysis",
                "query": query,
                "components_analyzed": len(components),
                "dependency_insights": dependency_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error analyzing dependencies: {e}")
            return {"error": str(e), "analysis_type": "dependency_analysis"}

    def generate_testing_strategy(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Generate testing strategy using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze testing patterns
            testing_insights = self._analyze_testing_patterns(components)

            # Generate testing strategy
            strategy = self._generate_testing_strategy_plan(testing_insights)

            analysis_time = time.time() - start_time
            self.coder_stats["testing_strategies"] += 1
            self.coder_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "testing_strategy",
                "query": query,
                "components_analyzed": len(components),
                "testing_insights": testing_insights,
                "strategy": strategy,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error generating testing strategy: {e}")
            return {"error": str(e), "analysis_type": "testing_strategy"}

    def analyze_security_patterns(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze security patterns using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze security patterns
            security_insights = self._analyze_security_patterns(components)

            # Generate security recommendations
            recommendations = self._generate_security_recommendations(security_insights)

            analysis_time = time.time() - start_time
            self.coder_stats["security_insights"] += 1
            self.coder_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "security_analysis",
                "query": query,
                "components_analyzed": len(components),
                "security_insights": security_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error analyzing security patterns: {e}")
            return {"error": str(e), "analysis_type": "security_analysis"}

    def analyze_performance_patterns(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze performance patterns using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze performance patterns
            performance_insights = self._analyze_performance_patterns(components)

            # Generate performance recommendations
            recommendations = self._generate_performance_recommendations(performance_insights)

            analysis_time = time.time() - start_time
            self.coder_stats["performance_analyses"] += 1
            self.coder_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "performance_analysis",
                "query": query,
                "components_analyzed": len(components),
                "performance_insights": performance_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error analyzing performance patterns: {e}")
            return {"error": str(e), "analysis_type": "performance_analysis"}

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

    def _analyze_quality_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze code quality patterns from components."""
        insights = {
            "complexity_analysis": [],
            "maintainability_metrics": [],
            "code_smells": [],
            "best_practices": [],
            "refactoring_opportunities": [],
        }

        for comp in components:
            comp_data = comp["component_data"]

            # Complexity analysis
            function_count = comp_data.get("functions", 0)
            class_count = comp_data.get("classes", 0)

            if function_count > 20:
                insights["complexity_analysis"].append(
                    {
                        "component": comp_data["file_path"],
                        "complexity_level": "high",
                        "functions": function_count,
                        "classes": class_count,
                        "recommendation": "Consider breaking into smaller modules",
                    }
                )
            elif function_count > 10:
                insights["complexity_analysis"].append(
                    {
                        "component": comp_data["file_path"],
                        "complexity_level": "medium",
                        "functions": function_count,
                        "classes": class_count,
                        "recommendation": "Monitor for complexity growth",
                    }
                )

            # Code smells detection
            if comp_data.get("imports", 0) > 15:
                insights["code_smells"].append(
                    {
                        "component": comp_data["file_path"],
                        "smell_type": "high_coupling",
                        "metric": f"{comp_data.get('imports', 0)} imports",
                        "recommendation": "Review dependencies and reduce coupling",
                    }
                )

            # Best practices
            if "test" in comp_data["file_path"].lower():
                insights["best_practices"].append(
                    {
                        "component": comp_data["file_path"],
                        "practice": "Test file naming",
                        "status": "good",
                        "recommendation": "Maintain clear test naming conventions",
                    }
                )

        return insights

    def _analyze_dependency_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze dependency patterns from components."""
        insights = {
            "dependency_graph": [],
            "circular_dependencies": [],
            "high_coupling_components": [],
            "dependency_risks": [],
            "optimization_opportunities": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            import_count = comp_data.get("imports", 0)

            # High coupling analysis
            if import_count > 15:
                insights["high_coupling_components"].append(
                    {
                        "component": comp_data["file_path"],
                        "import_count": import_count,
                        "risk_level": "high",
                        "recommendation": "Review and reduce dependencies",
                    }
                )
            elif import_count > 10:
                insights["high_coupling_components"].append(
                    {
                        "component": comp_data["file_path"],
                        "import_count": import_count,
                        "risk_level": "medium",
                        "recommendation": "Monitor dependency growth",
                    }
                )

            # Dependency risks
            if import_count > 20:
                insights["dependency_risks"].append(
                    {
                        "component": comp_data["file_path"],
                        "risk_type": "maintenance_burden",
                        "description": "High dependency count increases maintenance complexity",
                        "mitigation": "Consider dependency injection or interface segregation",
                    }
                )

        return insights

    def _analyze_testing_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze testing patterns from components."""
        insights = {
            "test_coverage_patterns": [],
            "testing_strategies": [],
            "test_quality_metrics": [],
            "testing_best_practices": [],
            "improvement_opportunities": [],
        }

        test_components = [comp for comp in components if "test" in comp["component_data"]["file_path"].lower()]

        for comp in test_components:
            comp_data = comp["component_data"]

            # Test coverage patterns
            if comp_data.get("functions", 0) > 10:
                insights["test_coverage_patterns"].append(
                    {
                        "component": comp_data["file_path"],
                        "test_functions": comp_data.get("functions", 0),
                        "coverage_estimate": "good",
                        "recommendation": "Maintain comprehensive test coverage",
                    }
                )

            # Testing best practices
            insights["testing_best_practices"].append(
                {
                    "component": comp_data["file_path"],
                    "practice": "Test file organization",
                    "status": "good",
                    "recommendation": "Keep tests organized and focused",
                }
            )

        # Improvement opportunities
        if len(test_components) < len(components) * 0.3:  # Less than 30% test coverage
            insights["improvement_opportunities"].append(
                {
                    "area": "test_coverage",
                    "current_state": f"{len(test_components)} test files for {len(components)} components",
                    "recommendation": "Increase test coverage across components",
                    "priority": "high",
                }
            )

        return insights

    def _analyze_security_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze security patterns from components."""
        insights = {
            "security_risks": [],
            "authentication_patterns": [],
            "authorization_patterns": [],
            "input_validation": [],
            "security_best_practices": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            file_path = comp_data["file_path"].lower()

            # Security risk detection
            if any(keyword in file_path for keyword in ["auth", "login", "password", "token"]):
                insights["authentication_patterns"].append(
                    {
                        "component": comp_data["file_path"],
                        "pattern_type": "authentication",
                        "security_level": "medium",
                        "recommendation": "Ensure proper authentication validation",
                    }
                )

            # Input validation
            if any(keyword in file_path for keyword in ["api", "endpoint", "request", "form"]):
                insights["input_validation"].append(
                    {
                        "component": comp_data["file_path"],
                        "validation_type": "input_handling",
                        "security_level": "medium",
                        "recommendation": "Implement comprehensive input validation",
                    }
                )

        return insights

    def _analyze_performance_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze performance patterns from components."""
        insights = {
            "performance_bottlenecks": [],
            "optimization_opportunities": [],
            "resource_usage_patterns": [],
            "scalability_concerns": [],
            "performance_best_practices": [],
        }

        for comp in components:
            comp_data = comp["component_data"]

            # Performance bottleneck detection
            if comp_data.get("functions", 0) > 30:
                insights["performance_bottlenecks"].append(
                    {
                        "component": comp_data["file_path"],
                        "bottleneck_type": "high_complexity",
                        "metric": f"{comp_data.get('functions', 0)} functions",
                        "recommendation": "Consider breaking into smaller, focused functions",
                    }
                )

            # Optimization opportunities
            if comp_data.get("imports", 0) > 20:
                insights["optimization_opportunities"].append(
                    {
                        "component": comp_data["file_path"],
                        "opportunity_type": "dependency_optimization",
                        "current_state": f"{comp_data.get('imports', 0)} imports",
                        "recommendation": "Review and optimize import statements",
                    }
                )

        return insights

    def _generate_quality_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate code quality recommendations."""
        recommendations = []

        # Complexity recommendations
        for insight in insights.get("complexity_analysis", []):
            if insight["complexity_level"] == "high":
                recommendations.append(
                    {
                        "type": "refactoring",
                        "priority": "high",
                        "component": insight["component"],
                        "message": insight["recommendation"],
                        "effort": "medium",
                    }
                )

        # Code smell recommendations
        for insight in insights.get("code_smells", []):
            recommendations.append(
                {
                    "type": "improvement",
                    "priority": "medium",
                    "component": insight["component"],
                    "message": insight["recommendation"],
                    "effort": "low",
                }
            )

        return recommendations

    def _generate_dependency_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate dependency recommendations."""
        recommendations = []

        # High coupling recommendations
        for insight in insights.get("high_coupling_components", []):
            recommendations.append(
                {
                    "type": "dependency_reduction",
                    "priority": insight["risk_level"],
                    "component": insight["component"],
                    "message": insight["recommendation"],
                    "effort": "medium",
                }
            )

        # Risk mitigation recommendations
        for insight in insights.get("dependency_risks", []):
            recommendations.append(
                {
                    "type": "risk_mitigation",
                    "priority": "high",
                    "component": insight["component"],
                    "message": insight["mitigation"],
                    "effort": "high",
                }
            )

        return recommendations

    def _generate_testing_strategy_plan(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate testing strategy plan."""
        strategy = {"coverage_goals": [], "testing_priorities": [], "implementation_steps": [], "quality_metrics": []}

        # Coverage goals
        if insights.get("improvement_opportunities"):
            strategy["coverage_goals"].append(
                {
                    "goal": "Increase test coverage",
                    "target": "80% coverage across all components",
                    "timeline": "2-3 weeks",
                    "priority": "high",
                }
            )

        # Testing priorities
        strategy["testing_priorities"].extend(
            [
                {
                    "priority": "high",
                    "focus": "Critical path components",
                    "approach": "Comprehensive unit and integration tests",
                },
                {
                    "priority": "medium",
                    "focus": "High complexity components",
                    "approach": "Focused unit tests with edge cases",
                },
                {"priority": "low", "focus": "Utility and helper components", "approach": "Basic functionality tests"},
            ]
        )

        return strategy

    def _generate_security_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security recommendations."""
        recommendations = []

        for pattern in insights.get("authentication_patterns", []):
            recommendations.append(
                {
                    "type": "security_enhancement",
                    "priority": "high",
                    "component": pattern["component"],
                    "message": pattern["recommendation"],
                    "effort": "medium",
                }
            )

        for validation in insights.get("input_validation", []):
            recommendations.append(
                {
                    "type": "security_enhancement",
                    "priority": "high",
                    "component": validation["component"],
                    "message": validation["recommendation"],
                    "effort": "medium",
                }
            )

        return recommendations

    def _generate_performance_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance recommendations."""
        recommendations = []

        for bottleneck in insights.get("performance_bottlenecks", []):
            recommendations.append(
                {
                    "type": "performance_optimization",
                    "priority": "medium",
                    "component": bottleneck["component"],
                    "message": bottleneck["recommendation"],
                    "effort": "medium",
                }
            )

        for opportunity in insights.get("optimization_opportunities", []):
            recommendations.append(
                {
                    "type": "performance_optimization",
                    "priority": "low",
                    "component": opportunity["component"],
                    "message": opportunity["recommendation"],
                    "effort": "low",
                }
            )

        return recommendations

    def get_coder_stats(self) -> Dict[str, Any]:
        """Get coder role statistics."""
        return {
            "total_analyses": sum(
                [
                    self.coder_stats["code_quality_analyses"],
                    self.coder_stats["dependency_analyses"],
                    self.coder_stats["testing_strategies"],
                    self.coder_stats["security_insights"],
                    self.coder_stats["performance_analyses"],
                ]
            ),
            "analyses_by_type": {
                "code_quality": self.coder_stats["code_quality_analyses"],
                "dependency_analysis": self.coder_stats["dependency_analyses"],
                "testing_strategies": self.coder_stats["testing_strategies"],
                "security_insights": self.coder_stats["security_insights"],
                "performance_analyses": self.coder_stats["performance_analyses"],
            },
            "total_analysis_time_ms": self.coder_stats["total_analysis_time"] * 1000,
            "average_analysis_time_ms": (
                self.coder_stats["total_analysis_time"]
                / max(
                    1,
                    sum(
                        [
                            self.coder_stats["code_quality_analyses"],
                            self.coder_stats["dependency_analyses"],
                            self.coder_stats["testing_strategies"],
                            self.coder_stats["security_insights"],
                            self.coder_stats["performance_analyses"],
                        ]
                    ),
                )
                * 1000
            ),
        }


def main():
    """Main function for testing the enhanced coder role."""
    print("🚀 Enhanced Coder Role Test")
    print("=" * 50)

    # Initialize the enhanced coder role
    coder_role = EnhancedCoderRole()

    if not coder_role.initialize():
        print("❌ Failed to initialize enhanced coder role")
        return

    # Test different analysis types
    test_queries = [
        "How can I improve the code quality of the database connection module?",
        "What are the dependency patterns in our memory system?",
        "What testing strategy should I use for the vector system?",
        "Are there any security concerns in our authentication system?",
        "How can I optimize performance in our data processing components?",
    ]

    print("\n🧪 Testing Enhanced Coder Role Capabilities...")
    print("=" * 50)

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        print("-" * 40)

        # Determine analysis type based on query
        if "quality" in query.lower():
            result = coder_role.analyze_code_quality(query)
        elif "dependency" in query.lower():
            result = coder_role.analyze_dependencies(query)
        elif "test" in query.lower():
            result = coder_role.generate_testing_strategy(query)
        elif "security" in query.lower():
            result = coder_role.analyze_security_patterns(query)
        elif "performance" in query.lower():
            result = coder_role.analyze_performance_patterns(query)
        else:
            result = coder_role.analyze_code_quality(query)

        if "error" in result:
            print(f"❌ Analysis failed: {result['error']}")
        else:
            print(f"✅ Analysis completed in {result['analysis_time_ms']:.2f}ms")
            print(f"📊 Components analyzed: {result['components_analyzed']}")

            # Show key insights
            if "quality_insights" in result:
                insights = result["quality_insights"]
                if insights.get("complexity_analysis"):
                    print(f"   🔍 Complexity insights: {len(insights['complexity_analysis'])}")
                if insights.get("code_smells"):
                    print(f"   🚨 Code smells detected: {len(insights['code_smells'])}")

            if "recommendations" in result:
                print(f"   💡 Recommendations: {len(result['recommendations'])}")

    # Show coder statistics
    print("\n📊 Enhanced Coder Role Statistics:")
    print("=" * 50)
    stats = coder_role.get_coder_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
