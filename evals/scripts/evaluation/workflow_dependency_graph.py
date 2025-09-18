#!/usr/bin/env python3
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportAny=false, reportUnusedImport=false, reportRedeclaration=false, reportUnusedCallResult=false, reportUnnecessaryTypeIgnoreComment=false
"""
Workflow Dependency Graph System

This module provides DiGraph-based workflow visualization and dependency tracking
for the AI Dev Tasks project. It can model and analyze:

1. Task Dependencies - How tasks depend on each other
2. Agent Workflows - The flow of work between different agents
3. System Components - How different parts of the system interact
4. Development Pipelines - The flow from backlog → PRD → tasks → execution

Usage:
    python workflow_dependency_graph.py --workflow-type task-dependencies --analyze
    python workflow_dependency_graph.py --workflow-type agent-workflows --visualize
    python workflow_dependency_graph.py --workflow-type system-components --export
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import networkx as nx
from networkx import DiGraph

if TYPE_CHECKING:
    from networkx import DiGraph as DiGraphType
else:
    DiGraphType = DiGraph


class WorkflowType(Enum):
    """Types of workflows that can be modeled"""

    TASK_DEPENDENCIES = "task-dependencies"
    AGENT_WORKFLOWS = "agent-workflows"
    SYSTEM_COMPONENTS = "system-components"
    DEVELOPMENT_PIPELINE = "development-pipeline"


class NodeType(Enum):
    """Types of nodes in the workflow graph"""

    TASK = "task"
    AGENT = "agent"
    COMPONENT = "component"
    STAGE = "stage"
    RESOURCE = "resource"
    DECISION = "decision"


class EdgeType(Enum):
    """Types of edges in the workflow graph"""

    DEPENDS_ON = "depends_on"
    TRIGGERS = "triggers"
    COMMUNICATES_WITH = "communicates_with"
    USES = "uses"
    PRODUCES = "produces"
    CONSUMES = "consumes"
    BLOCKS = "blocks"
    ENABLES = "enables"
    MONITORS = "monitors"


@dataclass
class WorkflowNode:
    """Represents a node in the workflow graph"""

    id: str
    name: str
    node_type: NodeType
    description: str
    status: str = "pending"
    priority: int = 1
    estimated_duration: float = 0.0
    actual_duration: float = 0.0
    dependencies: list[str] = None
    resources: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies: Any = []
        if self.resources is None:
            self.resources: Any = []
        if self.metadata is None:
            self.metadata: Any = {}


@dataclass
class WorkflowEdge:
    """Represents an edge in the workflow graph"""

    source: str
    target: str
    edge_type: EdgeType
    weight: float = 1.0
    description: str = ""
    conditions: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.conditions is None:
            self.conditions: Any = []
        if self.metadata is None:
            self.metadata: Any = {}


class WorkflowDependencyGraph:
    """DiGraph-based workflow dependency tracking and analysis system"""

    def __init__(self, workflow_type: WorkflowType) -> None:
        self.workflow_type: Any = workflow_type
        self.graph: DiGraphType = DiGraph()  # pyright: ignore[reportUnknownVariableType,reportMissingTypeArgument]
        self.nodes: dict[str, WorkflowNode] = {}
        self.edges: list[WorkflowEdge] = []
        self._build_workflow()

    def _build_workflow(self) -> None:
        """Build the workflow graph based on the workflow type"""
        if self.workflow_type == WorkflowType.TASK_DEPENDENCIES:
            self._build_task_dependencies()
        elif self.workflow_type == WorkflowType.AGENT_WORKFLOWS:
            self._build_agent_workflows()
        elif self.workflow_type == WorkflowType.SYSTEM_COMPONENTS:
            self._build_system_components()
        elif self.workflow_type == WorkflowType.DEVELOPMENT_PIPELINE:
            self._build_development_pipeline()

    def _build_task_dependencies(self) -> None:
        """Build task dependency workflow"""
        # Core development tasks
        tasks = [
            WorkflowNode(
                "backlog_analysis",
                "Backlog Analysis",
                NodeType.TASK,
                "Analyze and prioritize backlog items",
                priority=1,
                estimated_duration=2.0,
            ),
            WorkflowNode(
                "prd_creation",
                "PRD Creation",
                NodeType.TASK,
                "Create Product Requirements Document",
                priority=2,
                estimated_duration=4.0,
            ),
            WorkflowNode(
                "task_generation",
                "Task Generation",
                NodeType.TASK,
                "Generate detailed task list from PRD",
                priority=3,
                estimated_duration=1.5,
            ),
            WorkflowNode(
                "execution_planning",
                "Execution Planning",
                NodeType.TASK,
                "Plan execution strategy and resource allocation",
                priority=4,
                estimated_duration=2.0,
            ),
            WorkflowNode(
                "implementation",
                "Implementation",
                NodeType.TASK,
                "Implement the solution",
                priority=5,
                estimated_duration=8.0,
            ),
            WorkflowNode(
                "testing", "Testing", NodeType.TASK, "Test the implementation", priority=6, estimated_duration=3.0
            ),
            WorkflowNode(
                "documentation",
                "Documentation",
                NodeType.TASK,
                "Update documentation",
                priority=7,
                estimated_duration=2.0,
            ),
            WorkflowNode(
                "deployment", "Deployment", NodeType.TASK, "Deploy the solution", priority=8, estimated_duration=1.0
            ),
        ]

        # Add nodes to graph
        for task in tasks:
            self._add_node(task)

        # Define dependencies
        dependencies = [
            ("backlog_analysis", "prd_creation", EdgeType.DEPENDS_ON),
            ("prd_creation", "task_generation", EdgeType.DEPENDS_ON),
            ("task_generation", "execution_planning", EdgeType.DEPENDS_ON),
            ("execution_planning", "implementation", EdgeType.DEPENDS_ON),
            ("implementation", "testing", EdgeType.DEPENDS_ON),
            ("testing", "documentation", EdgeType.DEPENDS_ON),
            ("documentation", "deployment", EdgeType.DEPENDS_ON),
        ]

        # Add edges
        for source, target, edge_type in dependencies:
            self._add_edge(source, target, edge_type, f"{source} must complete before {target}")

    def _build_agent_workflows(self) -> None:
        """Build agent workflow system"""
        # Agent roles
        agents = [
            WorkflowNode("planner", "Planner Agent", NodeType.AGENT, "Strategic planning and architecture", priority=1),
            WorkflowNode(
                "researcher", "Researcher Agent", NodeType.AGENT, "Technical research and analysis", priority=2
            ),
            WorkflowNode(
                "implementer", "Implementer Agent", NodeType.AGENT, "Code implementation and integration", priority=3
            ),
            WorkflowNode("coder", "Coder Agent", NodeType.AGENT, "Specific coding tasks and debugging", priority=4),
        ]

        # Add nodes
        for agent in agents:
            self._add_node(agent)

        # Define agent interactions
        interactions = [
            ("planner", "researcher", EdgeType.TRIGGERS, "Planner requests research"),
            ("researcher", "planner", EdgeType.PRODUCES, "Research results inform planning"),
            ("planner", "implementer", EdgeType.TRIGGERS, "Planner assigns implementation"),
            ("implementer", "coder", EdgeType.TRIGGERS, "Implementer delegates coding tasks"),
            ("coder", "implementer", EdgeType.PRODUCES, "Coder delivers code"),
            ("implementer", "planner", EdgeType.PRODUCES, "Implementation status updates"),
        ]

        # Add edges
        for source, target, edge_type, description in interactions:
            self._add_edge(source, target, edge_type, description)

    def _build_system_components(self) -> None:
        """Build system component interaction graph"""
        # Core system components
        components = [
            WorkflowNode(
                "memory_system",
                "Memory System",
                NodeType.COMPONENT,
                "Long-term semantic tracking and context management",
            ),
            WorkflowNode(
                "evaluation_system", "Evaluation System", NodeType.COMPONENT, "RAGChecker and performance evaluation"
            ),
            WorkflowNode(
                "dspy_modules", "DSPy Modules", NodeType.COMPONENT, "Neural program synthesis and optimization"
            ),
            WorkflowNode("database", "Database", NodeType.COMPONENT, "PostgreSQL with pgvector for data storage"),
            WorkflowNode("retrieval_system", "Retrieval System", NodeType.COMPONENT, "Document retrieval and ranking"),
            WorkflowNode(
                "monitoring", "Monitoring System", NodeType.COMPONENT, "Performance monitoring and health checks"
            ),
        ]

        # Add nodes
        for component in components:
            self._add_node(component)

        # Define component interactions
        interactions = [
            ("memory_system", "evaluation_system", EdgeType.USES, "Memory provides context for evaluation"),
            ("evaluation_system", "dspy_modules", EdgeType.USES, "Evaluation tests DSPy modules"),
            ("dspy_modules", "retrieval_system", EdgeType.USES, "DSPy optimizes retrieval"),
            ("retrieval_system", "database", EdgeType.USES, "Retrieval queries database"),
            ("database", "memory_system", EdgeType.PRODUCES, "Database stores memory data"),
            ("monitoring", "evaluation_system", EdgeType.MONITORS, "Monitoring tracks evaluation performance"),
            ("monitoring", "retrieval_system", EdgeType.MONITORS, "Monitoring tracks retrieval performance"),
        ]

        # Add edges
        for source, target, edge_type, description in interactions:
            self._add_edge(source, target, edge_type, description)

    def _build_development_pipeline(self) -> None:
        """Build development pipeline workflow"""
        # Development stages
        stages = [
            WorkflowNode("backlog", "Backlog", NodeType.STAGE, "Idea capture and initial prioritization"),
            WorkflowNode("prd", "PRD", NodeType.STAGE, "Product Requirements Document creation"),
            WorkflowNode("tasks", "Task Generation", NodeType.STAGE, "Detailed task breakdown and planning"),
            WorkflowNode("execution", "Execution", NodeType.STAGE, "Implementation and development"),
            WorkflowNode("testing", "Testing", NodeType.STAGE, "Quality assurance and validation"),
            WorkflowNode("deployment", "Deployment", NodeType.STAGE, "Release and production deployment"),
            WorkflowNode("archive", "Archive", NodeType.STAGE, "Documentation and knowledge capture"),
        ]

        # Add nodes
        for stage in stages:
            self._add_node(stage)

        # Define pipeline flow
        pipeline_flow = [
            ("backlog", "prd", EdgeType.TRIGGERS, "Backlog items trigger PRD creation"),
            ("prd", "tasks", EdgeType.TRIGGERS, "PRD triggers task generation"),
            ("tasks", "execution", EdgeType.TRIGGERS, "Tasks trigger execution"),
            ("execution", "testing", EdgeType.TRIGGERS, "Implementation triggers testing"),
            ("testing", "deployment", EdgeType.TRIGGERS, "Testing triggers deployment"),
            ("deployment", "archive", EdgeType.TRIGGERS, "Deployment triggers archiving"),
        ]

        # Add edges
        for source, target, edge_type, description in pipeline_flow:
            self._add_edge(source, target, edge_type, description)

    def _add_node(self, node: WorkflowNode) -> None:
        """Add a node to the graph"""
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            name=node.name,
            node_type=node.node_type.value,
            description=node.description,
            status=node.status,
            priority=node.priority,
            estimated_duration=node.estimated_duration,
            actual_duration=node.actual_duration,
            dependencies=node.dependencies,
            resources=node.resources,
            metadata=node.metadata,
        )

    def _add_edge(self, source: str, target: str, edge_type: EdgeType, description: str = "") -> None:
        """Add an edge to the graph"""
        edge = WorkflowEdge(source, target, edge_type, description=description)
        self.edges.append(edge)
        self.graph.add_edge(
            source,
            target,
            edge_type=edge_type.value,
            weight=edge.weight,
            description=description,
            conditions=edge.conditions,
            metadata=edge.metadata,
        )

    def get_execution_order(self) -> list[str]:
        """Get the topological order of execution"""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXError:
            return list(self.graph.nodes())

    def find_critical_path(self) -> list[str]:
        """Find the critical path through the workflow"""
        if not self.graph.nodes():
            return []

        # Calculate longest path (critical path)
        try:
            # Find all possible paths and get the longest one
            longest_path = []
            max_length = 0

            for source in self.graph.nodes():
                for target in self.graph.nodes():
                    if source != target:
                        try:
                            path: Any = nx.shortest_path(self.graph, source, target)
                            if len(path) > max_length:
                                max_length = len(path)
                                longest_path = path
                        except nx.NetworkXNoPath:
                            continue

            return longest_path
        except Exception:
            return list(self.graph.nodes())

    def find_parallel_opportunities(self) -> list[list[str]]:
        """Find tasks that can be executed in parallel"""
        parallel_groups = []
        remaining_nodes = set(self.graph.nodes())

        while remaining_nodes:
            # Find nodes with no incoming edges from remaining nodes
            current_group = []
            for node in list(remaining_nodes):
                incoming = set(self.graph.predecessors(node))
                if not incoming.intersection(remaining_nodes):
                    current_group.append(node)

            if not current_group:
                # If no nodes can be processed, add remaining nodes as individual groups
                for node in remaining_nodes:
                    parallel_groups.append([node])
                break

            parallel_groups.append(current_group)
            remaining_nodes -= set(current_group)

        return parallel_groups

    def analyze_workflow_performance(self) -> dict[str, Any]:
        """Analyze workflow performance metrics"""
        if not self.graph.nodes():
            return {"error": "No nodes in workflow"}

        # Basic metrics
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = float(nx.density(self.graph))

        # Critical path analysis
        critical_path: Any = self.find_critical_path()
        critical_path_length = len(critical_path)

        # Parallel opportunities
        parallel_groups: Any = self.find_parallel_opportunities()
        max_parallel = max(len(group) for group in parallel_groups) if parallel_groups else 1

        # Node analysis
        node_types = {}
        for node_id in self.graph.nodes():
            node_type = self.graph.nodes[node_id].get("node_type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

        # Edge analysis
        edge_types = {}
        for source, target in self.graph.edges():
            edge_type = self.graph.edges[source, target].get("edge_type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        return {
            "workflow_type": self.workflow_type.value,
            "total_nodes": num_nodes,
            "total_edges": num_edges,
            "density": density,
            "critical_path_length": critical_path_length,
            "critical_path": critical_path,
            "max_parallel_tasks": max_parallel,
            "parallel_groups": parallel_groups,
            "node_type_distribution": node_types,
            "edge_type_distribution": edge_types,
            "is_dag": nx.is_directed_acyclic_graph(self.graph),
            "has_cycles": not nx.is_directed_acyclic_graph(self.graph),
        }

    def visualize_workflow(self, output_path: str = "workflow_graph.png") -> None:
        """Visualize the workflow graph"""
        try:
            import matplotlib.patches as mpatches  # type: ignore[import-untyped]
            import matplotlib.pyplot as plt  # type: ignore[import-untyped]
        except ImportError:
            print("Matplotlib not available for visualization")
            return

        plt.figure(figsize=(16, 12))

        # Use hierarchical layout
        pos: Any = nx.spring_layout(self.graph, k=3, iterations=50)

        # Color nodes by type
        node_colors = []
        node_type_colors = {
            "task": "#FF6B6B",
            "agent": "#4ECDC4",
            "component": "#45B7D1",
            "stage": "#96CEB4",
            "resource": "#FFEAA7",
            "decision": "#DDA0DD",
        }

        for node_id in self.graph.nodes():
            node_type = self.graph.nodes[node_id].get("node_type", "unknown")
            node_colors.append(node_type_colors.get(node_type, "#CCCCCC"))

        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=1000, alpha=0.8)

        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, edge_color="gray", arrows=True, arrowsize=20, alpha=0.6)

        # Draw labels
        labels = {node_id: self.graph.nodes[node_id].get("name", node_id) for node_id in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)

        # Create legend
        legend_elements = [
            mpatches.Patch(color=color, label=node_type.title()) for node_type, color in node_type_colors.items()
        ]
        plt.legend(handles=legend_elements, loc="upper right")

        plt.title(
            f"{self.workflow_type.value.replace('-', ' ').title()} Workflow Graph", fontsize=16, fontweight="bold"
        )
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"📊 Workflow graph saved: {output_path}")

    def export_workflow_data(self, output_path: str = "workflow_data.json") -> None:
        """Export workflow data to JSON"""
        data = {
            "workflow_type": self.workflow_type.value,
            "created_at": datetime.now().isoformat(),
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "node_type": node.node_type.value,
                    "description": node.description,
                    "status": node.status,
                    "priority": node.priority,
                    "estimated_duration": node.estimated_duration,
                    "actual_duration": node.actual_duration,
                    "dependencies": node.dependencies,
                    "resources": node.resources,
                    "metadata": node.metadata,
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "edge_type": edge.edge_type.value,
                    "weight": edge.weight,
                    "description": edge.description,
                    "conditions": edge.conditions,
                    "metadata": edge.metadata,
                }
                for edge in self.edges
            ],
            "analysis": self.analyze_workflow_performance(),
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"💾 Workflow data exported: {output_path}")


def main() -> None:
    """Main function for command-line usage"""
    import argparse

    parser: Any = argparse.ArgumentParser(description="Workflow Dependency Graph System")
    parser.add_argument(
        "--workflow-type",
        choices=[wt.value for wt in WorkflowType],
        default=WorkflowType.TASK_DEPENDENCIES.value,
        help="Type of workflow to model",
    )
    parser.add_argument("--analyze", action="store_true", help="Analyze workflow performance")
    parser.add_argument("--visualize", action="store_true", help="Generate workflow visualization")
    parser.add_argument("--export", action="store_true", help="Export workflow data to JSON")
    parser.add_argument("--output-dir", default=".", help="Output directory for generated files")

    args: Any = parser.parse_args()

    # Create workflow graph
    workflow_type = WorkflowType(args.workflow_type)
    graph = WorkflowDependencyGraph(workflow_type)

    print(f"🔧 Built {workflow_type.value} workflow")
    print(f"📊 Total nodes: {graph.graph.number_of_nodes()}")
    print(f"🔗 Total edges: {graph.graph.number_of_edges()}")

    # Analyze workflow
    if args.analyze:
        analysis: Any = graph.analyze_workflow_performance()
        print("\n📈 Workflow Analysis:")
        print(f"   Density: {analysis['density']:.3f}")
        print(f"   Critical path length: {analysis['critical_path_length']}")
        print(f"   Max parallel tasks: {analysis['max_parallel_tasks']}")
        print(f"   Is DAG: {analysis['is_dag']}")
        print(f"   Has cycles: {analysis['has_cycles']}")

        if analysis.get("critical_path"):
            # Ensure critical_path is a list of strings for join()
            critical_path = analysis["critical_path"]
            if isinstance(critical_path, list) and all(isinstance(item, str) for item in critical_path):
                path_strs: list[str] = [str(item) for item in critical_path]
                print(f"   Critical path: {' → '.join(path_strs)}")
            else:
                print(f"   Critical path: {critical_path}")

    # Visualize workflow
    if args.visualize:
        output_path = f"{args.output_dir}/workflow_{workflow_type.value}.png"
        graph.visualize_workflow(output_path)

    # Export workflow data
    if args.export:
        output_path = f"{args.output_dir}/workflow_{workflow_type.value}.json"
        graph.export_workflow_data(output_path)


if __name__ == "__main__":
    main()
