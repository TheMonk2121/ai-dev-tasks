#!/usr/bin/env python3
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportAny=false, reportUnusedCallResult=false, reportUnnecessaryComparison=false, reportMissingTypeArgument=false
"""
Memory Relationship Graph System

This module provides DiGraph-based relationship modeling for the AI Dev Tasks memory systems.
It can model and analyze:

1. Memory System Relationships - How LTST, Cursor, Go CLI, and Prime systems interact
2. Context Evolution - How memory context changes and evolves over time
3. Memory Clusters - Group related memories and contexts together
4. Retrieval Patterns - Model how memories are retrieved and connected
5. Session Continuity - Track memory relationships across sessions

Usage:
    python memory_relationship_graph.py --memory-type system-relationships --analyze
    python memory_relationship_graph.py --memory-type context-evolution --visualize
    python memory_relationship_graph.py --memory-type memory-clusters --export
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any

import networkx as nx
from networkx import DiGraph

if TYPE_CHECKING:
    from networkx import DiGraph as DiGraphType
else:
    DiGraphType = DiGraph


class MemoryType(Enum):
    """Types of memory relationships that can be modeled"""

    SYSTEM_RELATIONSHIPS = "system-relationships"
    CONTEXT_EVOLUTION = "context-evolution"
    MEMORY_CLUSTERS = "memory-clusters"
    RETRIEVAL_PATTERNS = "retrieval-patterns"
    SESSION_CONTINUITY = "session-continuity"


class MemoryNodeType(Enum):
    """Types of nodes in the memory graph"""

    MEMORY_SYSTEM = "memory_system"
    CONTEXT = "context"
    SESSION = "session"
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    CHUNK = "chunk"
    USER = "user"
    AGENT = "agent"
    QUERY = "query"
    RESPONSE = "response"


class MemoryEdgeType(Enum):
    """Types of edges in the memory graph"""

    CONTAINS = "contains"
    REFERENCES = "references"
    SIMILAR_TO = "similar_to"
    EVOLVES_FROM = "evolves_from"
    TRIGGERS = "triggers"
    INFLUENCES = "influences"
    RETRIEVES = "retrieves"
    STORES = "stores"
    UPDATES = "updates"
    DEPENDS_ON = "depends_on"
    COMMUNICATES_WITH = "communicates_with"
    LEARNS_FROM = "learns_from"
    COORDINATES = "coordinates"
    USES = "uses"
    PRODUCES = "produces"


@dataclass
class MemoryNode:
    """Represents a node in the memory relationship graph"""

    id: str
    name: str
    node_type: MemoryNodeType
    description: str
    content: str = ""
    timestamp: datetime = None
    confidence: float = 1.0
    relevance_score: float = 0.0
    metadata: dict[str, Any] = None
    tags: list[str] = None
    source_system: str = ""

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = []


@dataclass
class MemoryEdge:
    """Represents an edge in the memory relationship graph"""

    source: str
    target: str
    edge_type: MemoryEdgeType
    weight: float = 1.0
    strength: float = 1.0
    description: str = ""
    timestamp: datetime = None
    confidence: float = 1.0
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class MemoryRelationshipGraph:
    """DiGraph-based memory relationship modeling and analysis system"""

    def __init__(self, memory_type: MemoryType) -> None:
        self.memory_type: Any = memory_type
        self.graph: DiGraphType = DiGraph()
        self.nodes: dict[str, MemoryNode] = {}
        self.edges: list[MemoryEdge] = []
        self._build_memory_graph()

    def _build_memory_graph(self) -> None:
        """Build the memory relationship graph based on the memory type"""
        if self.memory_type == MemoryType.SYSTEM_RELATIONSHIPS:
            self._build_system_relationships()
        elif self.memory_type == MemoryType.CONTEXT_EVOLUTION:
            self._build_context_evolution()
        elif self.memory_type == MemoryType.MEMORY_CLUSTERS:
            self._build_memory_clusters()
        elif self.memory_type == MemoryType.RETRIEVAL_PATTERNS:
            self._build_retrieval_patterns()
        elif self.memory_type == MemoryType.SESSION_CONTINUITY:
            self._build_session_continuity()

    def _build_system_relationships(self) -> None:
        """Build memory system relationship graph"""
        # Core memory systems
        systems = [
            MemoryNode(
                "ltst",
                "LTST Memory",
                MemoryNodeType.MEMORY_SYSTEM,
                "Long-term semantic tracking for cross-session continuity",
                source_system="ltst",
                confidence=0.9,
            ),
            MemoryNode(
                "cursor",
                "Cursor Memory",
                MemoryNodeType.MEMORY_SYSTEM,
                "IDE integration memory for development context",
                source_system="cursor",
                confidence=0.8,
            ),
            MemoryNode(
                "go_cli",
                "Go CLI Memory",
                MemoryNodeType.MEMORY_SYSTEM,
                "Command-line interface memory for tool usage",
                source_system="go_cli",
                confidence=0.7,
            ),
            MemoryNode(
                "prime",
                "Prime Memory",
                MemoryNodeType.MEMORY_SYSTEM,
                "Primary memory orchestrator for system coordination",
                source_system="prime",
                confidence=0.95,
            ),
            MemoryNode(
                "unified_orchestrator",
                "Unified Orchestrator",
                MemoryNodeType.MEMORY_SYSTEM,
                "Coordinates all memory systems with one interface",
                source_system="orchestrator",
                confidence=0.9,
            ),
        ]

        # Add nodes
        for system in systems:
            self._add_node(system)

        # Define system relationships
        relationships = [
            ("unified_orchestrator", "ltst", MemoryEdgeType.COORDINATES, "Orchestrator coordinates LTST"),
            ("unified_orchestrator", "cursor", MemoryEdgeType.COORDINATES, "Orchestrator coordinates Cursor"),
            ("unified_orchestrator", "go_cli", MemoryEdgeType.COORDINATES, "Orchestrator coordinates Go CLI"),
            ("unified_orchestrator", "prime", MemoryEdgeType.COORDINATES, "Orchestrator coordinates Prime"),
            ("ltst", "cursor", MemoryEdgeType.COMMUNICATES_WITH, "LTST and Cursor share context"),
            ("cursor", "go_cli", MemoryEdgeType.COMMUNICATES_WITH, "Cursor and Go CLI share tool context"),
            ("prime", "ltst", MemoryEdgeType.DEPENDS_ON, "Prime depends on LTST for long-term storage"),
            ("prime", "cursor", MemoryEdgeType.DEPENDS_ON, "Prime depends on Cursor for IDE context"),
            ("prime", "go_cli", MemoryEdgeType.DEPENDS_ON, "Prime depends on Go CLI for tool context"),
        ]

        # Add edges
        for source, target, edge_type, description in relationships:
            self._add_edge(source, target, edge_type, description, weight=0.8)

    def _build_context_evolution(self) -> None:
        """Build context evolution graph showing how memory context changes over time"""
        # Create a timeline of context evolution
        base_time = datetime.now() - timedelta(hours=24)

        contexts = [
            MemoryNode(
                "initial_context",
                "Initial Context",
                MemoryNodeType.CONTEXT,
                "Starting context for the session",
                timestamp=base_time,
                confidence=0.9,
            ),
            MemoryNode(
                "task_context",
                "Task Context",
                MemoryNodeType.CONTEXT,
                "Context focused on current task",
                timestamp=base_time + timedelta(hours=2),
                confidence=0.8,
            ),
            MemoryNode(
                "expanded_context",
                "Expanded Context",
                MemoryNodeType.CONTEXT,
                "Context expanded with additional information",
                timestamp=base_time + timedelta(hours=4),
                confidence=0.7,
            ),
            MemoryNode(
                "refined_context",
                "Refined Context",
                MemoryNodeType.CONTEXT,
                "Context refined based on learnings",
                timestamp=base_time + timedelta(hours=6),
                confidence=0.9,
            ),
            MemoryNode(
                "final_context",
                "Final Context",
                MemoryNodeType.CONTEXT,
                "Final context with all accumulated knowledge",
                timestamp=base_time + timedelta(hours=8),
                confidence=0.95,
            ),
        ]

        # Add nodes
        for context in contexts:
            self._add_node(context)

        # Define evolution relationships
        evolution_chain = [
            ("initial_context", "task_context", MemoryEdgeType.EVOLVES_FROM, "Task context evolves from initial"),
            ("task_context", "expanded_context", MemoryEdgeType.EVOLVES_FROM, "Expanded context evolves from task"),
            (
                "expanded_context",
                "refined_context",
                MemoryEdgeType.EVOLVES_FROM,
                "Refined context evolves from expanded",
            ),
            ("refined_context", "final_context", MemoryEdgeType.EVOLVES_FROM, "Final context evolves from refined"),
        ]

        # Add edges
        for source, target, edge_type, description in evolution_chain:
            self._add_edge(source, target, edge_type, description, weight=0.9)

    def _build_memory_clusters(self) -> None:
        """Build memory cluster graph showing related memories grouped together"""
        # Create memory clusters
        clusters = [
            # Development cluster
            MemoryNode(
                "dev_cluster",
                "Development Cluster",
                MemoryNodeType.CONTEXT,
                "Cluster of development-related memories",
                tags=["development", "coding", "implementation"],
            ),
            MemoryNode(
                "dev_memory_1",
                "Code Implementation Memory",
                MemoryNodeType.CHUNK,
                "Memory about implementing specific features",
                tags=["development", "implementation"],
            ),
            MemoryNode(
                "dev_memory_2",
                "Debugging Memory",
                MemoryNodeType.CHUNK,
                "Memory about debugging techniques and solutions",
                tags=["development", "debugging"],
            ),
            MemoryNode(
                "dev_memory_3",
                "Architecture Memory",
                MemoryNodeType.CHUNK,
                "Memory about system architecture decisions",
                tags=["development", "architecture"],
            ),
            # Evaluation cluster
            MemoryNode(
                "eval_cluster",
                "Evaluation Cluster",
                MemoryNodeType.CONTEXT,
                "Cluster of evaluation-related memories",
                tags=["evaluation", "testing", "metrics"],
            ),
            MemoryNode(
                "eval_memory_1",
                "RAGChecker Memory",
                MemoryNodeType.CHUNK,
                "Memory about RAGChecker evaluation results",
                tags=["evaluation", "ragchecker"],
            ),
            MemoryNode(
                "eval_memory_2",
                "Performance Memory",
                MemoryNodeType.CHUNK,
                "Memory about performance optimization",
                tags=["evaluation", "performance"],
            ),
            # Documentation cluster
            MemoryNode(
                "doc_cluster",
                "Documentation Cluster",
                MemoryNodeType.CONTEXT,
                "Cluster of documentation-related memories",
                tags=["documentation", "guides", "knowledge"],
            ),
            MemoryNode(
                "doc_memory_1",
                "Guide Memory",
                MemoryNodeType.CHUNK,
                "Memory about creating and maintaining guides",
                tags=["documentation", "guides"],
            ),
        ]

        # Add nodes
        for cluster in clusters:
            self._add_node(cluster)

        # Define cluster relationships
        cluster_relationships = [
            # Development cluster
            ("dev_cluster", "dev_memory_1", MemoryEdgeType.CONTAINS, "Dev cluster contains implementation memory"),
            ("dev_cluster", "dev_memory_2", MemoryEdgeType.CONTAINS, "Dev cluster contains debugging memory"),
            ("dev_cluster", "dev_memory_3", MemoryEdgeType.CONTAINS, "Dev cluster contains architecture memory"),
            ("dev_memory_1", "dev_memory_2", MemoryEdgeType.SIMILAR_TO, "Implementation and debugging are related"),
            ("dev_memory_2", "dev_memory_3", MemoryEdgeType.SIMILAR_TO, "Debugging and architecture are related"),
            # Evaluation cluster
            ("eval_cluster", "eval_memory_1", MemoryEdgeType.CONTAINS, "Eval cluster contains RAGChecker memory"),
            ("eval_cluster", "eval_memory_2", MemoryEdgeType.CONTAINS, "Eval cluster contains performance memory"),
            ("eval_memory_1", "eval_memory_2", MemoryEdgeType.SIMILAR_TO, "RAGChecker and performance are related"),
            # Documentation cluster
            ("doc_cluster", "doc_memory_1", MemoryEdgeType.CONTAINS, "Doc cluster contains guide memory"),
            # Cross-cluster relationships
            ("dev_memory_1", "eval_memory_1", MemoryEdgeType.INFLUENCES, "Implementation influences evaluation"),
            ("eval_memory_1", "doc_memory_1", MemoryEdgeType.INFLUENCES, "Evaluation results influence documentation"),
        ]

        # Add edges
        for source, target, edge_type, description in cluster_relationships:
            self._add_edge(source, target, edge_type, description, weight=0.7)

    def _build_retrieval_patterns(self) -> None:
        """Build retrieval pattern graph showing how memories are retrieved and connected"""
        # Create retrieval pattern nodes
        patterns = [
            MemoryNode(
                "query_processing",
                "Query Processing",
                MemoryNodeType.QUERY,
                "Initial query processing and understanding",
            ),
            MemoryNode(
                "context_search",
                "Context Search",
                MemoryNodeType.QUERY,
                "Searching for relevant context in memory systems",
            ),
            MemoryNode(
                "memory_retrieval",
                "Memory Retrieval",
                MemoryNodeType.QUERY,
                "Retrieving specific memories from storage",
            ),
            MemoryNode(
                "context_synthesis",
                "Context Synthesis",
                MemoryNodeType.RESPONSE,
                "Synthesizing retrieved context into coherent response",
            ),
            MemoryNode(
                "memory_update",
                "Memory Update",
                MemoryNodeType.RESPONSE,
                "Updating memory systems with new information",
            ),
            MemoryNode(
                "ltst_retrieval", "LTST Retrieval", MemoryNodeType.MEMORY_SYSTEM, "Retrieval from LTST long-term memory"
            ),
            MemoryNode(
                "cursor_retrieval", "Cursor Retrieval", MemoryNodeType.MEMORY_SYSTEM, "Retrieval from Cursor IDE memory"
            ),
            MemoryNode(
                "go_cli_retrieval",
                "Go CLI Retrieval",
                MemoryNodeType.MEMORY_SYSTEM,
                "Retrieval from Go CLI tool memory",
            ),
        ]

        # Add nodes
        for pattern in patterns:
            self._add_node(pattern)

        # Define retrieval relationships
        retrieval_flow = [
            ("query_processing", "context_search", MemoryEdgeType.TRIGGERS, "Query processing triggers context search"),
            ("context_search", "memory_retrieval", MemoryEdgeType.TRIGGERS, "Context search triggers memory retrieval"),
            ("memory_retrieval", "ltst_retrieval", MemoryEdgeType.USES, "Memory retrieval uses LTST"),
            ("memory_retrieval", "cursor_retrieval", MemoryEdgeType.USES, "Memory retrieval uses Cursor"),
            ("memory_retrieval", "go_cli_retrieval", MemoryEdgeType.USES, "Memory retrieval uses Go CLI"),
            ("ltst_retrieval", "context_synthesis", MemoryEdgeType.PRODUCES, "LTST produces context for synthesis"),
            ("cursor_retrieval", "context_synthesis", MemoryEdgeType.PRODUCES, "Cursor produces context for synthesis"),
            ("go_cli_retrieval", "context_synthesis", MemoryEdgeType.PRODUCES, "Go CLI produces context for synthesis"),
            ("context_synthesis", "memory_update", MemoryEdgeType.TRIGGERS, "Synthesis triggers memory update"),
        ]

        # Add edges
        for source, target, edge_type, description in retrieval_flow:
            self._add_edge(source, target, edge_type, description, weight=0.8)

    def _build_session_continuity(self) -> None:
        """Build session continuity graph showing memory relationships across sessions"""
        # Create session timeline
        base_time = datetime.now() - timedelta(days=7)

        sessions = [
            MemoryNode(
                "session_1",
                "Session 1",
                MemoryNodeType.SESSION,
                "First session with initial context",
                timestamp=base_time,
            ),
            MemoryNode(
                "session_2",
                "Session 2",
                MemoryNodeType.SESSION,
                "Second session building on previous context",
                timestamp=base_time + timedelta(days=1),
            ),
            MemoryNode(
                "session_3",
                "Session 3",
                MemoryNodeType.SESSION,
                "Third session with accumulated knowledge",
                timestamp=base_time + timedelta(days=2),
            ),
            MemoryNode(
                "session_4",
                "Session 4",
                MemoryNodeType.SESSION,
                "Fourth session with refined understanding",
                timestamp=base_time + timedelta(days=3),
            ),
            MemoryNode(
                "current_session",
                "Current Session",
                MemoryNodeType.SESSION,
                "Current session with full context",
                timestamp=datetime.now(),
            ),
        ]

        # Add nodes
        for session in sessions:
            self._add_node(session)

        # Define continuity relationships
        continuity_chain = [
            ("session_1", "session_2", MemoryEdgeType.EVOLVES_FROM, "Session 2 builds on Session 1"),
            ("session_2", "session_3", MemoryEdgeType.EVOLVES_FROM, "Session 3 builds on Session 2"),
            ("session_3", "session_4", MemoryEdgeType.EVOLVES_FROM, "Session 4 builds on Session 3"),
            ("session_4", "current_session", MemoryEdgeType.EVOLVES_FROM, "Current session builds on Session 4"),
            ("session_1", "current_session", MemoryEdgeType.INFLUENCES, "Session 1 influences current session"),
            ("session_2", "current_session", MemoryEdgeType.INFLUENCES, "Session 2 influences current session"),
            ("session_3", "current_session", MemoryEdgeType.INFLUENCES, "Session 3 influences current session"),
        ]

        # Add edges
        for source, target, edge_type, description in continuity_chain:
            self._add_edge(source, target, edge_type, description, weight=0.9)

    def _add_node(self, node: MemoryNode) -> None:
        """Add a node to the graph"""
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            name=node.name,
            node_type=node.node_type.value,
            description=node.description,
            content=node.content,
            timestamp=node.timestamp.isoformat() if node.timestamp else None,
            confidence=node.confidence,
            relevance_score=node.relevance_score,
            metadata=node.metadata,
            tags=node.tags,
            source_system=node.source_system,
        )

    def _add_edge(
        self,
        source: str,
        target: str,
        edge_type: MemoryEdgeType,
        description: str = "",
        weight: float = 1.0,
        strength: float = 1.0,
    ) -> None:
        """Add an edge to the graph"""
        edge = MemoryEdge(source, target, edge_type, weight, strength, description)
        self.edges.append(edge)
        self.graph.add_edge(
            source,
            target,
            edge_type=edge_type.value,
            weight=edge.weight,
            strength=edge.strength,
            description=description,
            timestamp=edge.timestamp.isoformat() if edge.timestamp else None,
            confidence=edge.confidence,
            metadata=edge.metadata,
        )

    def find_memory_clusters(self) -> list[list[str]]:
        """Find clusters of related memories using community detection"""
        try:
            import networkx.algorithms.community as nx_comm

            communities = nx_comm.greedy_modularity_communities(self.graph.to_undirected())
            return [list(community) for community in communities]
        except ImportError:
            # Fallback to simple connected components
            return [list(component) for component in nx.connected_components(self.graph.to_undirected())]

    def find_memory_paths(self, source: str, target: str, max_length: int = 5) -> list[list[str]]:
        """Find paths between memory nodes"""
        try:
            return list(nx.all_simple_paths(self.graph, source, target, cutoff=max_length))
        except nx.NetworkXNoPath:
            return []

    def analyze_memory_relationships(self) -> dict[str, Any]:
        """Analyze memory relationship patterns"""
        if not self.graph.nodes():
            return {"error": "No nodes in memory graph"}

        # Basic metrics
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = float(nx.density(self.graph))

        # Memory clusters
        clusters: Any = self.find_memory_clusters()
        num_clusters = len(clusters)
        avg_cluster_size = sum(len(cluster) for cluster in clusters) / num_clusters if clusters else 0

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

        # Memory system analysis
        memory_systems = {}
        for node_id in self.graph.nodes():
            source_system = self.graph.nodes[node_id].get("source_system", "unknown")
            memory_systems[source_system] = memory_systems.get(source_system, 0) + 1

        return {
            "memory_type": self.memory_type.value,
            "total_nodes": num_nodes,
            "total_edges": num_edges,
            "density": density,
            "num_clusters": num_clusters,
            "avg_cluster_size": avg_cluster_size,
            "clusters": clusters,
            "node_type_distribution": node_types,
            "edge_type_distribution": edge_types,
            "memory_system_distribution": memory_systems,
            "is_connected": nx.is_weakly_connected(self.graph),
            "has_cycles": not nx.is_directed_acyclic_graph(self.graph),
        }

    def visualize_memory_graph(self, output_path: str = "memory_graph.png") -> None:
        """Visualize the memory relationship graph"""
        try:
            import matplotlib.patches as mpatches  # type: ignore[import-untyped]
            import matplotlib.pyplot as plt  # type: ignore[import-untyped]
        except ImportError:
            print("Matplotlib not available for visualization")
            return

        _ = plt.figure(figsize=(16, 12))

        # Use hierarchical layout
        pos: Any = nx.spring_layout(self.graph, k=3, iterations=50)

        # Color nodes by type
        node_colors = []
        node_type_colors = {
            "memory_system": "#FF6B6B",
            "context": "#4ECDC4",
            "session": "#45B7D1",
            "conversation": "#96CEB4",
            "document": "#FFEAA7",
            "chunk": "#DDA0DD",
            "user": "#98D8C8",
            "agent": "#F7DC6F",
            "query": "#BB8FCE",
            "response": "#85C1E9",
        }

        for node_id in self.graph.nodes():
            node_type = self.graph.nodes[node_id].get("node_type", "unknown")
            node_colors.append(node_type_colors.get(node_type, "#CCCCCC"))

        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=1000, alpha=0.8)

        # Draw edges with different styles for different types
        edge_styles = {
            "contains": "solid",
            "references": "dashed",
            "similar_to": "dotted",
            "evolves_from": "solid",
            "triggers": "solid",
            "influences": "dashed",
            "retrieves": "solid",
            "stores": "dashed",
            "updates": "dotted",
            "depends_on": "solid",
            "communicates_with": "dashed",
            "learns_from": "dotted",
        }

        for edge_type, style in edge_styles.items():
            edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get("edge_type") == edge_type]
            if edges:
                nx.draw_networkx_edges(
                    self.graph,
                    pos,
                    edgelist=edges,
                    edge_color="gray",
                    style=style,
                    arrows=True,
                    arrowsize=20,
                    alpha=0.6,
                )

        # Draw labels
        labels = {node_id: self.graph.nodes[node_id].get("name", node_id) for node_id in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)

        # Create legend
        legend_elements = [
            mpatches.Patch(color=color, label=node_type.title()) for node_type, color in node_type_colors.items()
        ]
        _ = plt.legend(handles=legend_elements, loc="upper right")

        plt.title(f"{self.memory_type.value.replace('-', ' ').title()} Memory Graph", fontsize=16, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"📊 Memory graph saved: {output_path}")

    def export_memory_data(self, output_path: str = "memory_data.json") -> None:
        """Export memory relationship data to JSON"""
        data = {
            "memory_type": self.memory_type.value,
            "created_at": datetime.now().isoformat(),
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "node_type": node.node_type.value,
                    "description": node.description,
                    "content": node.content,
                    "timestamp": node.timestamp.isoformat() if node.timestamp else None,
                    "confidence": node.confidence,
                    "relevance_score": node.relevance_score,
                    "metadata": node.metadata,
                    "tags": node.tags,
                    "source_system": node.source_system,
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "edge_type": edge.edge_type.value,
                    "weight": edge.weight,
                    "strength": edge.strength,
                    "description": edge.description,
                    "timestamp": edge.timestamp.isoformat() if edge.timestamp else None,
                    "confidence": edge.confidence,
                    "metadata": edge.metadata,
                }
                for edge in self.edges
            ],
            "analysis": self.analyze_memory_relationships(),
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"💾 Memory data exported: {output_path}")


def main() -> None:
    """Main function for command-line usage"""
    import argparse

    parser: Any = argparse.ArgumentParser(description="Memory Relationship Graph System")
    parser.add_argument(
        "--memory-type",
        choices=[mt.value for mt in MemoryType],
        default=MemoryType.SYSTEM_RELATIONSHIPS.value,
        help="Type of memory relationships to model",
    )
    parser.add_argument("--analyze", action="store_true", help="Analyze memory relationships")
    parser.add_argument("--visualize", action="store_true", help="Generate memory graph visualization")
    parser.add_argument("--export", action="store_true", help="Export memory data to JSON")
    parser.add_argument("--output-dir", default=".", help="Output directory for generated files")

    args: Any = parser.parse_args()

    # Create memory graph
    memory_type = MemoryType(args.memory_type)
    graph = MemoryRelationshipGraph(memory_type)

    print(f"🔧 Built {memory_type.value} memory graph")
    print(f"📊 Total nodes: {graph.graph.number_of_nodes()}")
    print(f"🔗 Total edges: {graph.graph.number_of_edges()}")

    # Analyze memory relationships
    if args.analyze:
        analysis: Any = graph.analyze_memory_relationships()
        print("\n📈 Memory Analysis:")
        print(f"   Density: {analysis['density']:.3f}")
        print(f"   Clusters: {analysis['num_clusters']}")
        print(f"   Avg cluster size: {analysis['avg_cluster_size']:.1f}")
        print(f"   Is connected: {analysis['is_connected']}")
        print(f"   Has cycles: {analysis['has_cycles']}")

        if analysis.get("clusters"):
            print(f"   Memory clusters: {[len(cluster) for cluster in analysis['clusters']]}")

    # Visualize memory graph
    if args.visualize:
        output_path = f"{args.output_dir}/memory_{memory_type.value}.png"
        graph.visualize_memory_graph(output_path)

    # Export memory data
    if args.export:
        output_path = f"{args.output_dir}/memory_{memory_type.value}.json"
        graph.export_memory_data(output_path)


if __name__ == "__main__":
    main()
