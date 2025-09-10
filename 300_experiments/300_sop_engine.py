#!/usr/bin/env python3
"""
SOP (Standard Operating Procedures) Engine with Graph-Based Process Representation
Based on ChatGPT Pro's recommendations for lessons-learned → SOP conversion
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx


class SOPNodeType(Enum):
    TASK = "task"
    DATA = "data"
    DECISION = "decision"
    GATEWAY = "gateway"
    RESULT = "result"


class SOPEdgeType(Enum):
    CONTROL_FLOW = "control_flow"
    DATA_FLOW = "data_flow"
    CONDITIONAL = "conditional"
    SEQUENTIAL = "sequential"


@dataclass
class SOPNode:
    """Represents a node in an SOP process graph"""

    node_id: str
    node_type: SOPNodeType
    label: str
    description: str
    metadata: Dict[str, Any]
    preconditions: List[str] = None
    effects: List[str] = None


@dataclass
class SOPEdge:
    """Represents an edge in an SOP process graph"""

    source_id: str
    target_id: str
    edge_type: SOPEdgeType
    condition: Optional[str] = None
    metadata: Dict[str, Any] = None


class SOPEngine:
    """Graph-based SOP engine for lessons-learned → SOP conversion"""

    def __init__(self):
        self.sop_graphs = {}  # sop_id -> NetworkX graph
        self.sop_metadata = {}
        self.similarity_model = None

    def create_sop_from_lessons(self, lessons: List[Dict[str, Any]], sop_id: str) -> str:
        """Convert lessons-learned into a structured SOP graph"""
        graph = nx.DiGraph()

        # Extract process steps from lessons
        process_steps = self._extract_process_steps(lessons)

        # Create nodes for each step
        for i, step in enumerate(process_steps):
            node_id = f"{sop_id}_step_{i}"

            # Determine node type based on step characteristics
            node_type = self._determine_node_type(step)

            sop_node = SOPNode(
                node_id=node_id,
                node_type=node_type,
                label=step.get("title", f"Step {i + 1}"),
                description=step.get("description", ""),
                metadata={
                    "step_order": i,
                    "source_lessons": step.get("source_lessons", []),
                    "confidence": step.get("confidence", 0.8),
                    "category": step.get("category", "general"),
                },
                preconditions=step.get("preconditions", []),
                effects=step.get("effects", []),
            )

            graph.add_node(node_id, **sop_node.__dict__)

        # Create edges based on process flow
        self._create_process_edges(graph, process_steps, sop_id)

        # Store the SOP
        self.sop_graphs[sop_id] = graph
        self.sop_metadata[sop_id] = {
            "title": lessons[0].get("title", f"SOP {sop_id}"),
            "description": lessons[0].get("description", ""),
            "source_lessons": [l.get("id") for l in lessons],
            "created_at": lessons[0].get("timestamp"),
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
        }

        return sop_id

    def augment_sop(self, sop_id: str, augmentation_type: str = "syntactic") -> str:
        """Apply augmentation to an SOP (following paper's Cat-1/Cat-2 approach)"""
        if sop_id not in self.sop_graphs:
            raise ValueError(f"SOP {sop_id} not found")

        original_graph = self.sop_graphs[sop_id]
        augmented_id = f"{sop_id}_aug_{augmentation_type}"

        if augmentation_type == "syntactic":
            return self._apply_syntactic_sop_augmentation(original_graph, augmented_id)
        elif augmentation_type == "semantic":
            return self._apply_semantic_sop_augmentation(original_graph, augmented_id)
        else:
            raise ValueError(f"Unknown augmentation type: {augmentation_type}")

    def _apply_syntactic_sop_augmentation(self, original_graph: nx.DiGraph, augmented_id: str) -> str:
        """Apply Cat-2 augmentation: swap adjacent tasks, modify metadata"""
        graph = original_graph.copy()

        # Swap adjacent tasks (Cat-2)
        nodes = list(graph.nodes())
        for i in range(len(nodes) - 1):
            if graph.nodes[nodes[i]]["node_type"] == "task" and graph.nodes[nodes[i + 1]]["node_type"] == "task":
                # Swap node positions in metadata
                graph.nodes[nodes[i]]["metadata"]["step_order"] = i + 1
                graph.nodes[nodes[i + 1]]["metadata"]["step_order"] = i

        # Modify metadata fields
        for node_id in graph.nodes():
            metadata = graph.nodes[node_id]["metadata"]
            metadata["augmentation_type"] = "syntactic"
            metadata["original_sop"] = augmented_id.split("_aug_")[0]
            # Add slight variation to confidence
            if "confidence" in metadata:
                metadata["confidence"] = max(0.1, min(1.0, metadata["confidence"] + 0.1))

        self.sop_graphs[augmented_id] = graph
        self.sop_metadata[augmented_id] = {
            **self.sop_metadata[augmented_id.split("_aug_")[0]],
            "augmentation_type": "syntactic",
            "original_sop": augmented_id.split("_aug_")[0],
        }

        return augmented_id

    def _apply_semantic_sop_augmentation(self, original_graph: nx.DiGraph, augmented_id: str) -> str:
        """Apply Cat-1 augmentation: delete non-critical nodes/edges"""
        graph = original_graph.copy()

        # Delete 10-20% of non-critical nodes
        nodes_to_delete = []
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]
            # Don't delete critical nodes (start/end, decision points)
            if node_data["node_type"] not in ["gateway", "decision"] and len(nodes_to_delete) < len(graph.nodes) * 0.15:
                nodes_to_delete.append(node_id)

        # Remove selected nodes
        for node_id in nodes_to_delete:
            graph.remove_node(node_id)

        # Update remaining node metadata
        for node_id in graph.nodes():
            metadata = graph.nodes[node_id]["metadata"]
            metadata["augmentation_type"] = "semantic"
            metadata["original_sop"] = augmented_id.split("_aug_")[0]

        self.sop_graphs[augmented_id] = graph
        self.sop_metadata[augmented_id] = {
            **self.sop_metadata[augmented_id.split("_aug_")[0]],
            "augmentation_type": "semantic",
            "original_sop": augmented_id.split("_aug_")[0],
        }

        return augmented_id

    def find_similar_sops(self, query_sop_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar SOPs using graph similarity"""
        if query_sop_id not in self.sop_graphs:
            return []

        query_graph = self.sop_graphs[query_sop_id]
        similarities = []

        for sop_id, graph in self.sop_graphs.items():
            if sop_id == query_sop_id:
                continue

            # Calculate graph similarity (simplified)
            similarity = self._calculate_graph_similarity(query_graph, graph)
            similarities.append((sop_id, similarity))

        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def recommend_sop_template(self, requirements: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Recommend SOP templates based on requirements"""
        recommendations = []

        for sop_id, metadata in self.sop_metadata.items():
            if metadata.get("augmentation_type"):
                continue  # Skip augmented SOPs for template recommendations

            # Calculate match score based on requirements
            match_score = self._calculate_requirement_match(requirements, metadata)
            if match_score > 0.3:  # Threshold for relevance
                recommendations.append((sop_id, match_score))

        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations

    def _extract_process_steps(self, lessons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract process steps from lessons-learned"""
        steps = []

        for lesson in lessons:
            # Extract structured steps from lesson content
            content = lesson.get("content", "")

            # Simple step extraction (in practice, use NLP)
            if "step" in content.lower() or "process" in content.lower():
                steps.append(
                    {
                        "title": lesson.get("title", "Process Step"),
                        "description": content,
                        "source_lessons": [lesson.get("id")],
                        "category": lesson.get("category", "general"),
                        "confidence": lesson.get("confidence", 0.8),
                    }
                )

        return steps

    def _determine_node_type(self, step: Dict[str, Any]) -> SOPNodeType:
        """Determine the type of SOP node based on step characteristics"""
        description = step.get("description", "").lower()

        if "decision" in description or "choose" in description:
            return SOPNodeType.DECISION
        elif "gateway" in description or "checkpoint" in description:
            return SOPNodeType.GATEWAY
        elif "result" in description or "output" in description:
            return SOPNodeType.RESULT
        elif "data" in description or "information" in description:
            return SOPNodeType.DATA
        else:
            return SOPNodeType.TASK

    def _create_process_edges(self, graph: nx.DiGraph, steps: List[Dict[str, Any]], sop_id: str):
        """Create edges between process steps"""
        nodes = list(graph.nodes())

        for i in range(len(nodes) - 1):
            source = nodes[i]
            target = nodes[i + 1]

            # Determine edge type based on node types
            source_type = graph.nodes[source]["node_type"]
            graph.nodes[target]["node_type"]

            if source_type == "decision":
                edge_type = SOPEdgeType.CONDITIONAL
            else:
                edge_type = SOPEdgeType.SEQUENTIAL

            graph.add_edge(source, target, edge_type=edge_type.value, metadata={"sop_id": sop_id, "step_sequence": i})

    def _calculate_graph_similarity(self, graph1: nx.DiGraph, graph2: nx.DiGraph) -> float:
        """Calculate similarity between two SOP graphs"""
        # Simple similarity based on node types and structure
        nodes1 = set(graph1.nodes())
        nodes2 = set(graph2.nodes())

        # Jaccard similarity of node types
        types1 = set([graph1.nodes[n]["node_type"] for n in nodes1])
        types2 = set([graph2.nodes[n]["node_type"] for n in nodes2])

        if not types1 and not types2:
            return 1.0
        if not types1 or not types2:
            return 0.0

        intersection = len(types1.intersection(types2))
        union = len(types1.union(types2))

        return intersection / union if union > 0 else 0.0

    def _calculate_requirement_match(self, requirements: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """Calculate how well an SOP matches given requirements"""
        match_score = 0.0

        # Match on category
        if requirements.get("category") == metadata.get("category"):
            match_score += 0.4

        # Match on complexity (node count)
        req_complexity = requirements.get("complexity", "medium")
        actual_complexity = (
            "high" if metadata.get("node_count", 0) > 10 else "medium" if metadata.get("node_count", 0) > 5 else "low"
        )

        if req_complexity == actual_complexity:
            match_score += 0.3

        # Match on domain/keywords
        req_keywords = set(requirements.get("keywords", []))
        sop_keywords = set(metadata.get("keywords", []))

        if req_keywords and sop_keywords:
            keyword_match = len(req_keywords.intersection(sop_keywords)) / len(req_keywords.union(sop_keywords))
            match_score += keyword_match * 0.3

        return match_score

    def export_sop(self, sop_id: str) -> Dict[str, Any]:
        """Export SOP for analysis or persistence"""
        if sop_id not in self.sop_graphs:
            return {}

        graph = self.sop_graphs[sop_id]
        return {
            "sop_id": sop_id,
            "metadata": self.sop_metadata[sop_id],
            "graph": {
                "nodes": dict(graph.nodes(data=True)),
                "edges": [(u, v, d) for u, v, d in graph.edges(data=True)],
            },
        }


# Example usage
if __name__ == "__main__":
    # Create SOP engine
    sop_engine = SOPEngine()

    # Example lessons-learned data
    lessons = [
        {
            "id": "lesson_1",
            "title": "RAG Optimization Process",
            "description": "Step 1: Analyze current performance. Step 2: Identify bottlenecks. Step 3: Apply optimizations.",
            "category": "technical",
            "confidence": 0.9,
        }
    ]

    # Create SOP from lessons
    sop_id = sop_engine.create_sop_from_lessons(lessons, "rag_optimization")

    # Apply augmentations
    augmented_syntactic = sop_engine.augment_sop(sop_id, "syntactic")
    augmented_semantic = sop_engine.augment_sop(sop_id, "semantic")

    # Find similar SOPs
    similar_sops = sop_engine.find_similar_sops(sop_id)

    # Recommend templates
    requirements = {"category": "technical", "complexity": "medium"}
    recommendations = sop_engine.recommend_sop_template(requirements)

    print(f"Created SOP: {sop_id}")
    print(f"Augmented SOPs: {augmented_syntactic}, {augmented_semantic}")
    print(f"Similar SOPs: {similar_sops}")
    print(f"Recommendations: {recommendations}")
