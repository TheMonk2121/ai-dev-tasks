#!/usr/bin/env python3
"""
Enhanced Query Pattern Knowledge Graph with Semantic Process Graph Representation
Based on the research paper and ChatGPT Pro's recommendations
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import networkx as nx


class NodeType(Enum):
    TASK = "task"
    DATA = "data"
    QUERY = "query"
    INTENT = "intent"


class EdgeType(Enum):
    CONTROL_FLOW = "control_flow"
    DATA_FLOW = "data_flow"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    TEMPORAL_SEQUENCE = "temporal_sequence"


@dataclass
class SemanticNode:
    """Represents a node in the semantic process graph"""

    node_id: str
    node_type: NodeType
    content: str
    metadata: dict[str, Any]
    embedding: list[float] | None = None


@dataclass
class SemanticEdge:
    """Represents an edge in the semantic process graph"""

    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float
    metadata: dict[str, Any]


class EnhancedQueryPatternGraph:
    """Enhanced Query Pattern Knowledge Graph with semantic process representation"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_metadata = {}
        self.edge_metadata = {}

    def add_query_pattern(self, query: str, intent: str, context: dict[str, Any]) -> str:
        """Add a query pattern as a semantic process graph"""
        pattern_id = f"pattern_{len(self.graph.nodes)}"

        # Create nodes
        query_node = SemanticNode(
            node_id=f"{pattern_id}_query",
            node_type=NodeType.QUERY,
            content=query,
            metadata={"original_query": query, "timestamp": context.get("timestamp")},
        )

        intent_node = SemanticNode(
            node_id=f"{pattern_id}_intent",
            node_type=NodeType.INTENT,
            content=intent,
            metadata={"intent_type": context.get("intent_type"), "confidence": context.get("confidence")},
        )

        # Add nodes to graph
        self.graph.add_node(query_node.node_id, **query_node.__dict__)
        self.graph.add_node(intent_node.node_id, **intent_node.__dict__)

        # Add semantic similarity edge
        semantic_edge = SemanticEdge(
            source_id=query_node.node_id,
            target_id=intent_node.node_id,
            edge_type=EdgeType.SEMANTIC_SIMILARITY,
            weight=context.get("similarity_score", 0.8),
            metadata={"relationship": "expresses_intent"},
        )

        self.graph.add_edge(semantic_edge.source_id, semantic_edge.target_id, **semantic_edge.__dict__)

        return pattern_id

    def augment_pattern(self, pattern_id: str, augmentation_type: str = "syntactic") -> str:
        """Apply augmentation to a query pattern (Cat-1 or Cat-2 from paper)"""
        if augmentation_type == "syntactic":
            return self._apply_syntactic_augmentation(pattern_id)
        elif augmentation_type == "semantic":
            return self._apply_semantic_augmentation(pattern_id)
        else:
            raise ValueError(f"Unknown augmentation type: {augmentation_type}")

    def _apply_syntactic_augmentation(self, pattern_id: str) -> str:
        """Apply Cat-2 augmentation: swap adjacent tasks/data, modify metadata"""
        # Find pattern nodes
        pattern_nodes = [n for n in self.graph.nodes if n.startswith(pattern_id)]

        if len(pattern_nodes) < 2:
            return pattern_id  # Can't augment single-node patterns

        # Create augmented version
        augmented_id = f"{pattern_id}_aug_syntactic"

        # Copy original nodes with modifications
        for node_id in pattern_nodes:
            original_data = self.graph.nodes[node_id]
            new_node_id = node_id.replace(pattern_id, augmented_id)

            # Apply syntactic variations
            augmented_content = self._generate_syntactic_variant(original_data["content"])
            augmented_metadata = original_data["metadata"].copy()
            augmented_metadata["augmentation_type"] = "syntactic"
            augmented_metadata["original_pattern"] = pattern_id

            self.graph.add_node(
                new_node_id,
                **{
                    "node_id": new_node_id,
                    "node_type": original_data["node_type"],
                    "content": augmented_content,
                    "metadata": augmented_metadata,
                },
            )

        # Copy edges with potential modifications
        edges_to_copy = [
            (source, target, data)
            for source, target, data in self.graph.edges(data=True)
            if source.startswith(pattern_id) and target.startswith(pattern_id)
        ]

        for source, target, data in edges_to_copy:
            new_source = source.replace(pattern_id, augmented_id)
            new_target = target.replace(pattern_id, augmented_id)

            # Slightly modify edge weight for variation
            modified_weight = data["weight"] * (0.9 + 0.2 * hash(augmented_id) % 100 / 100)

            self.graph.add_edge(
                new_source,
                new_target,
                **{**data, "weight": modified_weight, "metadata": {**data["metadata"], "augmented": True}},
            )

        return augmented_id

    def _apply_semantic_augmentation(self, pattern_id: str) -> str:
        """Apply Cat-1 augmentation: delete non-critical nodes/edges"""
        # Find pattern nodes
        pattern_nodes = [n for n in self.graph.nodes if n.startswith(pattern_id)]

        if len(pattern_nodes) < 3:
            return pattern_id  # Need at least 3 nodes for safe deletion

        # Create augmented version
        augmented_id = f"{pattern_id}_aug_semantic"

        # Copy most nodes (delete 10-20% randomly)
        nodes_to_delete = set()
        if len(pattern_nodes) > 2:
            # Delete 1 non-critical node 10-20% of the time
            import random

            if random.random() < 0.15:  # 15% chance
                # Don't delete query or intent nodes, prefer data nodes
                data_nodes = [n for n in pattern_nodes if "data" in n.lower()]
                if data_nodes:
                    nodes_to_delete.add(random.choice(data_nodes))

        # Copy remaining nodes
        for node_id in pattern_nodes:
            if node_id in nodes_to_delete:
                continue

            original_data = self.graph.nodes[node_id]
            new_node_id = node_id.replace(pattern_id, augmented_id)

            self.graph.add_node(
                new_node_id,
                **{**original_data, "metadata": {**original_data["metadata"], "augmentation_type": "semantic"}},
            )

        # Copy edges (excluding those connected to deleted nodes)
        edges_to_copy = [
            (source, target, data)
            for source, target, data in self.graph.edges(data=True)
            if (
                source.startswith(pattern_id)
                and target.startswith(pattern_id)
                and source not in nodes_to_delete
                and target not in nodes_to_delete
            )
        ]

        for source, target, data in edges_to_copy:
            new_source = source.replace(pattern_id, augmented_id)
            new_target = target.replace(pattern_id, augmented_id)

            self.graph.add_edge(new_source, new_target, **{**data, "metadata": {**data["metadata"], "augmented": True}})

        return augmented_id

    def _generate_syntactic_variant(self, content: str) -> str:
        """Generate syntactic variations of content"""
        # Simple word order variations and synonym replacement
        words = content.split()
        if len(words) > 2:
            # Swap adjacent words occasionally
            import random

            if random.random() < 0.3:
                i = random.randint(0, len(words) - 2)
                words[i], words[i + 1] = words[i + 1], words[i]

        return " ".join(words)

    def generate_triplets(self, num_triplets: int = 100) -> list[tuple[str, str, str]]:
        """Generate (anchor, positive, negative) triplets for training"""
        triplets = []
        pattern_ids = list(set([n.split("_")[0] for n in self.graph.nodes if "_" in n]))

        for _ in range(num_triplets):
            # Select anchor pattern
            anchor = pattern_ids[hash(str(_)) % len(pattern_ids)]

            # Find positive (augmented version of same pattern)
            positives = [pid for pid in pattern_ids if pid.startswith(anchor) and pid != anchor]
            positive = positives[0] if positives else anchor

            # Find negative (different pattern)
            negatives = [pid for pid in pattern_ids if not pid.startswith(anchor)]
            negative = negatives[hash(str(_) + "neg") % len(negatives)] if negatives else anchor

            triplets.append((anchor, positive, negative))

        return triplets

    def export_graph(self) -> dict[str, Any]:
        """Export graph for analysis or persistence"""
        return {
            "nodes": dict(self.graph.nodes(data=True)),
            "edges": [(u, v, d) for u, v, d in self.graph.edges(data=True)],
            "metadata": {
                "total_nodes": len(self.graph.nodes),
                "total_edges": len(self.graph.edges),
                "node_types": list(set([data.get("node_type") for _, data in self.graph.nodes(data=True)])),
                "edge_types": list(set([data.get("edge_type") for _, _, data in self.graph.edges(data=True)])),
            },
        }


# Example usage
if __name__ == "__main__":
    # Create enhanced graph
    graph = EnhancedQueryPatternGraph()

    # Add some query patterns
    graph.add_query_pattern(
        "How do I optimize RAG performance?",
        "performance_optimization",
        {"intent_type": "technical_question", "confidence": 0.9},
    )

    graph.add_query_pattern(
        "What are the best practices for memory systems?",
        "best_practices_inquiry",
        {"intent_type": "knowledge_seeking", "confidence": 0.85},
    )

    # Apply augmentations
    pattern_id = "pattern_0"
    augmented_syntactic = graph.augment_pattern(pattern_id, "syntactic")
    augmented_semantic = graph.augment_pattern(pattern_id, "semantic")

    # Generate triplets for training
    triplets = graph.generate_triplets(10)

    # Export for analysis
    graph_data = graph.export_graph()

    print(
        f"Created graph with {graph_data['metadata']['total_nodes']} nodes and {graph_data['metadata']['total_edges']} edges"
    )
    print(f"Generated {len(triplets)} triplets for training")
    print(f"Augmented patterns: {augmented_syntactic}, {augmented_semantic}")
