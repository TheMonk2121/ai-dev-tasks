#!/usr/bin/env python3
"""
Enhanced Implementer Role Integration for DSPy-Vector System

Task 3.2: Enhanced Implementer Role Integration
Extends implementer role with vector-based integration patterns, dependency mapping,
and implementation strategy using the Vector-Based System Mapping.
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
    from dspy_modules.context_models import AIRole, ContextFactory, ImplementerContext

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

_LOG = logging.getLogger("enhanced_implementer_role")


class EnhancedImplementerRole:
    """Enhanced implementer role with vector-based system mapping capabilities."""

    def __init__(self, vector_store_dir: str = "metrics/vector_store"):
        self.vector_store_dir = vector_store_dir
        self.component_embeddings = {}
        self.embedding_model = None
        self.implementer_stats = {
            "integration_analyses": 0,
            "dependency_mappings": 0,
            "implementation_strategies": 0,
            "architecture_compliance": 0,
            "deployment_plans": 0,
            "total_analysis_time": 0.0,
        }

    def initialize(self) -> bool:
        """Initialize the enhanced implementer role system."""
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

            print("📂 Loading component embeddings for enhanced implementer role...")
            with open(embeddings_file, "r", encoding="utf-8") as f:
                self.component_embeddings = json.load(f)

            # Initialize embedding model
            print("🤖 Initializing embedding model for implementer analysis...")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

            print(f"✅ Enhanced implementer role initialized with {len(self.component_embeddings)} components")
            return True

        except Exception as e:
            print(f"❌ Error initializing enhanced implementer role: {e}")
            return False

    def analyze_integration_patterns(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze integration patterns using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze integration patterns
            integration_insights = self._analyze_integration_patterns(components)

            # Generate integration recommendations
            recommendations = self._generate_integration_recommendations(integration_insights)

            analysis_time = time.time() - start_time
            self.implementer_stats["integration_analyses"] += 1
            self.implementer_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "integration_patterns",
                "query": query,
                "components_analyzed": len(components),
                "integration_insights": integration_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error analyzing integration patterns: {e}")
            return {"error": str(e), "analysis_type": "integration_patterns"}

    def map_dependencies(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Map dependencies using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze dependency patterns
            dependency_insights = self._analyze_dependency_patterns(components)

            # Generate dependency map
            dependency_map = self._generate_dependency_map(dependency_insights)

            analysis_time = time.time() - start_time
            self.implementer_stats["dependency_mappings"] += 1
            self.implementer_stats["total_analysis_time"] += analysis_time

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
            _LOG.error(f"Error mapping dependencies: {e}")
            return {"error": str(e), "analysis_type": "dependency_mapping"}

    def create_implementation_strategy(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Create implementation strategy using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze implementation patterns
            implementation_insights = self._analyze_implementation_patterns(components)

            # Generate implementation strategy
            strategy = self._generate_implementation_strategy(implementation_insights)

            analysis_time = time.time() - start_time
            self.implementer_stats["implementation_strategies"] += 1
            self.implementer_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "implementation_strategy",
                "query": query,
                "components_analyzed": len(components),
                "implementation_insights": implementation_insights,
                "implementation_strategy": strategy,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error creating implementation strategy: {e}")
            return {"error": str(e), "analysis_type": "implementation_strategy"}

    def check_architecture_compliance(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Check architecture compliance using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze compliance patterns
            compliance_insights = self._analyze_compliance_patterns(components)

            # Generate compliance recommendations
            recommendations = self._generate_compliance_recommendations(compliance_insights)

            analysis_time = time.time() - start_time
            self.implementer_stats["architecture_compliance"] += 1
            self.implementer_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "architecture_compliance",
                "query": query,
                "components_analyzed": len(components),
                "compliance_insights": compliance_insights,
                "recommendations": recommendations,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error checking architecture compliance: {e}")
            return {"error": str(e), "analysis_type": "architecture_compliance"}

    def create_deployment_plan(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Create deployment plan using vector-based system mapping."""
        start_time = time.time()

        try:
            # Get relevant components
            components = self._get_relevant_components(query, top_k)

            # Analyze deployment patterns
            deployment_insights = self._analyze_deployment_patterns(components)

            # Generate deployment plan
            plan = self._generate_deployment_plan(deployment_insights)

            analysis_time = time.time() - start_time
            self.implementer_stats["deployment_plans"] += 1
            self.implementer_stats["total_analysis_time"] += analysis_time

            return {
                "analysis_type": "deployment_planning",
                "query": query,
                "components_analyzed": len(components),
                "deployment_insights": deployment_insights,
                "deployment_plan": plan,
                "analysis_time_ms": analysis_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            _LOG.error(f"Error creating deployment plan: {e}")
            return {"error": str(e), "analysis_type": "deployment_planning"}

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

    def _analyze_integration_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze integration patterns from components."""
        insights = {
            "integration_points": [],
            "api_patterns": [],
            "data_flow_patterns": [],
            "service_integration": [],
            "integration_risks": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            file_path = comp_data["file_path"].lower()

            # Integration point detection
            if any(integration in file_path for integration in ["api", "endpoint", "interface"]):
                insights["integration_points"].append(
                    {
                        "component": comp_data["file_path"],
                        "integration_type": "API",
                        "complexity": "high" if comp_data.get("imports", 0) > 10 else "medium",
                        "recommendation": "Ensure proper API documentation and versioning",
                    }
                )

            # Service integration detection
            if any(service in file_path for service in ["service", "client", "connector"]):
                insights["service_integration"].append(
                    {
                        "component": comp_data["file_path"],
                        "integration_type": "Service",
                        "dependencies": comp_data.get("imports", 0),
                        "recommendation": "Implement proper error handling and retry logic",
                    }
                )

            # Data flow patterns
            if any(data in file_path for data in ["data", "model", "entity", "repository"]):
                insights["data_flow_patterns"].append(
                    {
                        "component": comp_data["file_path"],
                        "pattern_type": "Data Flow",
                        "responsibility": "Data access and persistence",
                        "recommendation": "Implement proper data validation and error handling",
                    }
                )

            # Integration risks
            if comp_data.get("imports", 0) > 15:
                insights["integration_risks"].append(
                    {
                        "component": comp_data["file_path"],
                        "risk_type": "High Coupling",
                        "severity": "medium",
                        "description": "High dependency count increases integration complexity",
                        "mitigation": "Consider interface segregation and dependency injection",
                    }
                )

        return insights

    def _analyze_dependency_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze dependency patterns from components."""
        insights = {
            "dependency_graph": [],
            "circular_dependencies": [],
            "critical_dependencies": [],
            "dependency_clusters": [],
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

            # Critical dependencies
            if comp_data.get("imports", 0) > 15:
                insights["critical_dependencies"].append(
                    {
                        "component": comp_data["file_path"],
                        "criticality": "high",
                        "dependency_count": comp_data.get("imports", 0),
                        "risk": "High dependency count increases maintenance complexity",
                        "recommendation": "Consider breaking into smaller, focused components",
                    }
                )

            # Optimization opportunities
            if comp_data.get("imports", 0) > 20:
                insights["optimization_opportunities"].append(
                    {
                        "component": comp_data["file_path"],
                        "opportunity": "Dependency Reduction",
                        "current_state": f"{comp_data.get('imports', 0)} dependencies",
                        "target": "Reduce to < 15 dependencies",
                        "effort": "medium",
                    }
                )

        return insights

    def _analyze_implementation_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze implementation patterns from components."""
        insights = {
            "implementation_approaches": [],
            "code_organization": [],
            "testing_patterns": [],
            "error_handling": [],
            "performance_patterns": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            file_path = comp_data["file_path"].lower()

            # Implementation approach detection
            if any(approach in file_path for approach in ["factory", "builder", "strategy"]):
                insights["implementation_approaches"].append(
                    {
                        "component": comp_data["file_path"],
                        "approach": "Design Pattern",
                        "pattern_type": "creational/behavioral",
                        "maturity": "established",
                        "recommendation": "Continue using established design patterns",
                    }
                )

            # Code organization
            if comp_data.get("functions", 0) <= 20:
                insights["code_organization"].append(
                    {
                        "component": comp_data["file_path"],
                        "organization": "Good",
                        "function_count": comp_data.get("functions", 0),
                        "recommendation": "Maintain current code organization standards",
                    }
                )

            # Testing patterns
            if "test" in file_path:
                insights["testing_patterns"].append(
                    {
                        "component": comp_data["file_path"],
                        "pattern": "Test Organization",
                        "coverage": "good",
                        "recommendation": "Maintain comprehensive test coverage",
                    }
                )

            # Error handling patterns
            if any(error in file_path for error in ["error", "exception", "handler"]):
                insights["error_handling"].append(
                    {
                        "component": comp_data["file_path"],
                        "pattern": "Error Handling",
                        "approach": "explicit",
                        "recommendation": "Ensure consistent error handling across components",
                    }
                )

        return insights

    def _analyze_compliance_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze compliance patterns from components."""
        insights = {
            "architecture_compliance": [],
            "coding_standards": [],
            "security_compliance": [],
            "performance_compliance": [],
            "documentation_compliance": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            file_path = comp_data["file_path"].lower()

            # Architecture compliance
            if any(arch in file_path for arch in ["api", "service", "model"]):
                insights["architecture_compliance"].append(
                    {
                        "component": comp_data["file_path"],
                        "compliance": "Good",
                        "layer": "appropriate",
                        "recommendation": "Maintain architectural boundaries",
                    }
                )

            # Coding standards
            if comp_data.get("functions", 0) <= 25:
                insights["coding_standards"].append(
                    {
                        "component": comp_data["file_path"],
                        "standard": "Function Size",
                        "compliance": "Good",
                        "recommendation": "Maintain function size standards",
                    }
                )

            # Security compliance
            if any(security in file_path for security in ["auth", "security", "encryption"]):
                insights["security_compliance"].append(
                    {
                        "component": comp_data["file_path"],
                        "compliance": "Security",
                        "status": "implemented",
                        "recommendation": "Regular security audits and updates",
                    }
                )

            # Documentation compliance
            if any(doc in file_path for doc in ["readme", "docs", "documentation"]):
                insights["documentation_compliance"].append(
                    {
                        "component": comp_data["file_path"],
                        "compliance": "Documentation",
                        "status": "present",
                        "recommendation": "Keep documentation up to date",
                    }
                )

        return insights

    def _analyze_deployment_patterns(self, components: List[Dict]) -> Dict[str, Any]:
        """Analyze deployment patterns from components."""
        insights = {
            "deployment_requirements": [],
            "environment_dependencies": [],
            "scalability_considerations": [],
            "monitoring_requirements": [],
            "rollback_strategies": [],
        }

        for comp in components:
            comp_data = comp["component_data"]
            file_path = comp_data["file_path"].lower()

            # Deployment requirements
            if any(deploy in file_path for deploy in ["config", "settings", "environment"]):
                insights["deployment_requirements"].append(
                    {
                        "component": comp_data["file_path"],
                        "requirement": "Configuration",
                        "type": "environment-specific",
                        "recommendation": "Use environment-specific configuration management",
                    }
                )

            # Environment dependencies
            if any(env in file_path for env in ["database", "cache", "queue"]):
                insights["environment_dependencies"].append(
                    {
                        "component": comp_data["file_path"],
                        "dependency": "External Service",
                        "type": "infrastructure",
                        "recommendation": "Ensure proper environment setup and monitoring",
                    }
                )

            # Scalability considerations
            if comp_data.get("imports", 0) > 10:
                insights["scalability_considerations"].append(
                    {
                        "component": comp_data["file_path"],
                        "consideration": "High Integration",
                        "impact": "scalability",
                        "recommendation": "Consider horizontal scaling and load balancing",
                    }
                )

            # Monitoring requirements
            if any(monitor in file_path for monitor in ["log", "metric", "monitor"]):
                insights["monitoring_requirements"].append(
                    {
                        "component": comp_data["file_path"],
                        "requirement": "Monitoring",
                        "type": "observability",
                        "recommendation": "Implement comprehensive logging and metrics",
                    }
                )

        return insights

    def _generate_integration_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate integration recommendations."""
        recommendations = []

        # Integration point recommendations
        for integration in insights.get("integration_points", []):
            recommendations.append(
                {
                    "type": "integration_improvement",
                    "priority": "medium",
                    "component": integration["component"],
                    "message": integration["recommendation"],
                    "effort": "medium",
                }
            )

        # Integration risk recommendations
        for risk in insights.get("integration_risks", []):
            recommendations.append(
                {
                    "type": "risk_mitigation",
                    "priority": risk["severity"],
                    "component": risk["component"],
                    "message": risk["mitigation"],
                    "effort": "high",
                }
            )

        return recommendations

    def _generate_dependency_map(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dependency map."""
        dependency_map = {
            "components": [],
            "relationships": [],
            "critical_paths": [],
            "optimization_targets": [],
        }

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
        for critical in insights.get("critical_dependencies", []):
            dependency_map["critical_paths"].append(
                {
                    "component": critical["component"],
                    "criticality": critical["criticality"],
                    "risk": critical["risk"],
                    "recommendation": critical["recommendation"],
                }
            )

        return dependency_map

    def _generate_implementation_strategy(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation strategy."""
        strategy = {
            "implementation_phases": [],
            "quality_gates": [],
            "testing_strategy": [],
            "deployment_approach": [],
            "success_metrics": [],
        }

        # Implementation phases
        strategy["implementation_phases"].extend(
            [
                {
                    "phase": "Foundation",
                    "focus": "Core infrastructure and basic patterns",
                    "duration": "1-2 weeks",
                    "priority": "high",
                },
                {
                    "phase": "Integration",
                    "focus": "Component integration and API development",
                    "duration": "2-3 weeks",
                    "priority": "high",
                },
                {
                    "phase": "Testing",
                    "focus": "Comprehensive testing and quality assurance",
                    "duration": "1-2 weeks",
                    "priority": "medium",
                },
                {
                    "phase": "Deployment",
                    "focus": "Production deployment and monitoring",
                    "duration": "1 week",
                    "priority": "medium",
                },
            ]
        )

        # Quality gates
        strategy["quality_gates"].extend(
            [
                {
                    "gate": "Code Review",
                    "criteria": "All code reviewed and approved",
                    "automation": "Pull request workflow",
                },
                {
                    "gate": "Testing",
                    "criteria": "All tests passing with >80% coverage",
                    "automation": "CI/CD pipeline",
                },
                {
                    "gate": "Integration",
                    "criteria": "All integration tests passing",
                    "automation": "Integration test suite",
                },
                {
                    "gate": "Performance",
                    "criteria": "Performance benchmarks met",
                    "automation": "Performance testing",
                },
            ]
        )

        return strategy

    def _generate_compliance_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate compliance recommendations."""
        recommendations = []

        # Architecture compliance recommendations
        for compliance in insights.get("architecture_compliance", []):
            recommendations.append(
                {
                    "type": "compliance_maintenance",
                    "priority": "low",
                    "component": compliance["component"],
                    "message": compliance["recommendation"],
                    "effort": "low",
                }
            )

        return recommendations

    def _generate_deployment_plan(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment plan."""
        plan = {
            "deployment_stages": [],
            "environment_setup": [],
            "monitoring_setup": [],
            "rollback_procedures": [],
            "success_criteria": [],
        }

        # Deployment stages
        plan["deployment_stages"].extend(
            [
                {
                    "stage": "Development",
                    "environment": "Local/Dev",
                    "focus": "Feature development and testing",
                    "automation": "Local development setup",
                },
                {
                    "stage": "Staging",
                    "environment": "Staging",
                    "focus": "Integration testing and validation",
                    "automation": "Automated deployment pipeline",
                },
                {
                    "stage": "Production",
                    "environment": "Production",
                    "focus": "Live deployment and monitoring",
                    "automation": "Blue-green deployment",
                },
            ]
        )

        # Environment setup
        for requirement in insights.get("deployment_requirements", []):
            plan["environment_setup"].append(
                {
                    "requirement": requirement["requirement"],
                    "setup": requirement["type"],
                    "automation": "Infrastructure as Code",
                }
            )

        return plan

    def get_implementer_stats(self) -> Dict[str, Any]:
        """Get implementer role statistics."""
        return {
            "total_analyses": sum(
                [
                    self.implementer_stats["integration_analyses"],
                    self.implementer_stats["dependency_mappings"],
                    self.implementer_stats["implementation_strategies"],
                    self.implementer_stats["architecture_compliance"],
                    self.implementer_stats["deployment_plans"],
                ]
            ),
            "analyses_by_type": {
                "integration_analysis": self.implementer_stats["integration_analyses"],
                "dependency_mapping": self.implementer_stats["dependency_mappings"],
                "implementation_strategy": self.implementer_stats["implementation_strategies"],
                "architecture_compliance": self.implementer_stats["architecture_compliance"],
                "deployment_planning": self.implementer_stats["deployment_plans"],
            },
            "total_analysis_time_ms": self.implementer_stats["total_analysis_time"] * 1000,
            "average_analysis_time_ms": (
                self.implementer_stats["total_analysis_time"]
                / max(
                    1,
                    sum(
                        [
                            self.implementer_stats["integration_analyses"],
                            self.implementer_stats["dependency_mappings"],
                            self.implementer_stats["implementation_strategies"],
                            self.implementer_stats["architecture_compliance"],
                            self.implementer_stats["deployment_plans"],
                        ]
                    ),
                )
                * 1000
            ),
        }


def main():
    """Main function for testing the enhanced implementer role."""
    print("🚀 Enhanced Implementer Role Test")
    print("=" * 50)

    # Initialize the enhanced implementer role
    implementer_role = EnhancedImplementerRole()

    if not implementer_role.initialize():
        print("❌ Failed to initialize enhanced implementer role")
        return

    # Test different analysis types
    test_queries = [
        "What integration patterns should I use for connecting our services?",
        "How should I map the dependencies between our components?",
        "What's the best implementation strategy for this feature?",
        "Are our components compliant with our architecture standards?",
        "What deployment plan should I create for this system?",
    ]

    print("\n🧪 Testing Enhanced Implementer Role Capabilities...")
    print("=" * 50)

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        print("-" * 40)

        # Determine analysis type based on query
        if "integration" in query.lower():
            result = implementer_role.analyze_integration_patterns(query)
        elif "dependency" in query.lower():
            result = implementer_role.map_dependencies(query)
        elif "implementation" in query.lower() or "strategy" in query.lower():
            result = implementer_role.create_implementation_strategy(query)
        elif "compliance" in query.lower():
            result = implementer_role.check_architecture_compliance(query)
        elif "deployment" in query.lower():
            result = implementer_role.create_deployment_plan(query)
        else:
            result = implementer_role.analyze_integration_patterns(query)

        if "error" in result:
            print(f"❌ Analysis failed: {result['error']}")
        else:
            print(f"✅ Analysis completed in {result['analysis_time_ms']:.2f}ms")
            print(f"📊 Components analyzed: {result['components_analyzed']}")

            # Show key insights based on analysis type
            if "integration_insights" in result:
                insights = result["integration_insights"]
                if insights.get("integration_points"):
                    print(f"   🔗 Integration points: {len(insights['integration_points'])}")
                if insights.get("integration_risks"):
                    print(f"   ⚠️ Integration risks: {len(insights['integration_risks'])}")

            if "dependency_insights" in result:
                insights = result["dependency_insights"]
                if insights.get("critical_dependencies"):
                    print(f"   🔴 Critical dependencies: {len(insights['critical_dependencies'])}")

            if "recommendations" in result:
                print(f"   💡 Recommendations: {len(result['recommendations'])}")

    # Show implementer statistics
    print("\n📊 Enhanced Implementer Role Statistics:")
    print("=" * 50)
    stats = implementer_role.get_implementer_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
