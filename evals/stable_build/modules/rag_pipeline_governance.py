#!/usr/bin/env python3
"""
RAG Pipeline Governance with Semantic Graph Representation
Based on ChatGPT Pro's recommendations for treating RAG workflows as sequential semantic graphs
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import networkx as nx


class PipelineStage(Enum):
    INGEST = "ingest"
    CHUNK = "chunk"
    RETRIEVE = "retrieve"
    RERANK = "rerank"
    GENERATE = "generate"
    VALIDATE = "validate"


class PipelineNodeType(Enum):
    STAGE = "stage"
    PARAMETER = "parameter"
    CONFIG = "config"
    RESULT = "result"


class PipelineEdgeType(Enum):
    SEQUENTIAL = "sequential"
    PARAMETER_FLOW = "parameter_flow"
    DATA_FLOW = "data_flow"
    CONDITIONAL = "conditional"


@dataclass
class PipelineNode:
    """Represents a node in the RAG pipeline graph"""

    node_id: str
    node_type: PipelineNodeType
    stage: PipelineStage | None
    label: str
    parameters: dict[str, Any]
    metadata: dict[str, Any]


@dataclass
class PipelineEdge:
    """Represents an edge in the RAG pipeline graph"""

    source_id: str
    target_id: str
    edge_type: PipelineEdgeType
    condition: str | None = None
    metadata: dict[str, Any] = None


class RAGPipelineGovernance:
    """Governance system for RAG pipelines using semantic graph representation"""

    def __init__(self):
        self.pipeline_graphs = {}  # pipeline_id -> NetworkX graph
        self.pipeline_metadata = {}
        self.similarity_model = None
        self.known_good_patterns = set()

    def create_pipeline_graph(self, pipeline_config: dict[str, Any], pipeline_id: str) -> str:
        """Create a semantic graph representation of a RAG pipeline"""
        graph = nx.DiGraph()

        # Create nodes for each pipeline stage
        stages = [
            PipelineStage.INGEST,
            PipelineStage.CHUNK,
            PipelineStage.RETRIEVE,
            PipelineStage.RERANK,
            PipelineStage.GENERATE,
            PipelineStage.VALIDATE,
        ]

        for i, stage in enumerate(stages):
            stage_node_id = f"{pipeline_id}_{stage.value}"

            # Get stage configuration
            stage_config = pipeline_config.get("stages", {}).get(stage.value, {})

            stage_node = PipelineNode(
                node_id=stage_node_id,
                node_type=PipelineNodeType.STAGE,
                stage=stage,
                label=f"{stage.value.title()} Stage",
                parameters=stage_config,
                metadata={
                    "stage_order": i,
                    "config": stage_config,
                    "pipeline_id": pipeline_id,
                },
            )

            # Convert enum to string for storage
            node_data = stage_node.__dict__.copy()
            # Add stage node to graph
            graph.add_node(stage_node_id, **node_data)

            # Add parameter nodes for this stage
            for param_name, param_value in stage_config.items():
                param_node_id = f"{stage_node_id}_param_{param_name}"

                param_node = PipelineNode(
                    node_id=param_node_id,
                    node_type=PipelineNodeType.PARAMETER,
                    stage=None,
                    label=f"{param_name}",
                    parameters={"value": param_value},
                    metadata={
                        "parent_stage": stage_node_id,
                        "parameter_name": param_name,
                        "pipeline_id": pipeline_id,
                    },
                )

                # Convert enum to string for storage
                param_data = param_node.__dict__.copy()
                graph.add_node(param_node_id, **param_data)

                # Add parameter flow edge
                graph.add_edge(
                    stage_node_id,
                    param_node_id,
                    edge_type=PipelineEdgeType.PARAMETER_FLOW.value,
                    metadata={"relationship": "has_parameter"},
                )

        # Create sequential edges between stages
        stage_nodes = [n for n in graph.nodes() if graph.nodes[n]["node_type"] == "stage"]
        for i in range(len(stage_nodes) - 1):
            graph.add_edge(
                stage_nodes[i],
                stage_nodes[i + 1],
                edge_type=PipelineEdgeType.SEQUENTIAL.value,
                metadata={"relationship": "sequential_flow"},
            )

        # Store the pipeline
        self.pipeline_graphs[pipeline_id] = graph
        self.pipeline_metadata[pipeline_id] = {
            "config": pipeline_config,
            "created_at": datetime.now().isoformat(),
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "stages": [stage.value for stage in stages],
        }

        return pipeline_id

    def augment_pipeline(self, pipeline_id: str, augmentation_type: str = "syntactic") -> str:
        """Apply augmentation to a pipeline (following paper's approach)"""
        if pipeline_id not in self.pipeline_graphs:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        original_graph = self.pipeline_graphs[pipeline_id]
        augmented_id = f"{pipeline_id}_aug_{augmentation_type}"

        if augmentation_type == "syntactic":
            return self._apply_syntactic_pipeline_augmentation(original_graph, augmented_id)
        elif augmentation_type == "semantic":
            return self._apply_semantic_pipeline_augmentation(original_graph, augmented_id)
        else:
            raise ValueError(f"Unknown augmentation type: {augmentation_type}")

    def _apply_syntactic_pipeline_augmentation(self, original_graph: nx.DiGraph, augmented_id: str) -> str:
        """Apply Cat-2 augmentation: swap adjacent stages, modify parameters"""
        graph = original_graph.copy()

        # Swap adjacent stages (Cat-2)
        stage_nodes = [n for n in graph.nodes() if graph.nodes[n]["node_type"] == "stage"]

        # Find adjacent stages that can be swapped
        for i in range(len(stage_nodes) - 1):
            current_stage = graph.nodes[stage_nodes[i]]["stage"]
            next_stage = graph.nodes[stage_nodes[i + 1]]["stage"]

            # Only swap if both stages are not critical (e.g., not ingest or validate)
            if current_stage not in [
                PipelineStage.INGEST,
                PipelineStage.VALIDATE,
            ] and next_stage not in [
                PipelineStage.INGEST,
                PipelineStage.VALIDATE,
            ]:
                # Swap stage orders in metadata
                graph.nodes[stage_nodes[i]]["metadata"]["stage_order"] = i
                graph.nodes[stage_nodes[i + 1]]["metadata"]["stage_order"] = i + 1

        # Modify parameters slightly
        for node_id in graph.nodes():
            if graph.nodes[node_id]["node_type"] == "parameter":
                params = graph.nodes[node_id]["parameters"]
                if "value" in params and isinstance(params["value"], (int, float)):
                    # Add small variation to numeric parameters
                    params["value"] = params["value"] * 1.01

                # Mark as augmented
                graph.nodes[node_id]["metadata"]["augmentation_type"] = "syntactic"
                graph.nodes[node_id]["metadata"]["original_pipeline"] = augmented_id.split("_aug_")[0]

        self.pipeline_graphs[augmented_id] = graph
        self.pipeline_metadata[augmented_id] = {
            **self.pipeline_metadata[augmented_id.split("_aug_")[0]],
            "augmentation_type": "syntactic",
            "original_pipeline": augmented_id.split("_aug_")[0],
        }

        return augmented_id

    def _apply_semantic_pipeline_augmentation(self, original_graph: nx.DiGraph, augmented_id: str) -> str:
        """Apply Cat-1 augmentation: remove non-critical stages/parameters"""
        graph = original_graph.copy()

        # Remove some non-critical parameters (10-20% of the time)
        param_nodes = [n for n in graph.nodes() if graph.nodes[n]["node_type"] == "parameter"]

        import random

        if random.random() < 0.15:  # 15% chance
            # Remove one non-critical parameter
            non_critical_params = [n for n in param_nodes if "threshold" in n.lower() or "limit" in n.lower()]
            if non_critical_params:
                node_to_remove = random.choice(non_critical_params)
                graph.remove_node(node_to_remove)

        # Mark remaining nodes as augmented
        for node_id in graph.nodes():
            graph.nodes[node_id]["metadata"]["augmentation_type"] = "semantic"
            graph.nodes[node_id]["metadata"]["original_pipeline"] = augmented_id.split("_aug_")[0]

        self.pipeline_graphs[augmented_id] = graph
        self.pipeline_metadata[augmented_id] = {
            **self.pipeline_metadata[augmented_id.split("_aug_")[0]],
            "augmentation_type": "semantic",
            "original_pipeline": augmented_id.split("_aug_")[0],
        }

        return augmented_id

    def validate_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        """Validate a pipeline against known good patterns"""
        if pipeline_id not in self.pipeline_graphs:
            return {"valid": False, "errors": ["Pipeline not found"]}

        graph = self.pipeline_graphs[pipeline_id]
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": [],
        }

        # Check for required stages (only if they have actual configuration)
        required_stages = ["ingest", "retrieve", "generate"]
        stage_nodes = [n for n in graph.nodes() if graph.nodes[n]["node_type"] == "stage"]
        present_stages = []

        for node in stage_nodes:
            stage = graph.nodes[node]["stage"]
            # Stage is now stored as string value
            stage_name = str(stage)
            # Only count stages that have actual configuration (not empty)
            # Check both parameters and metadata for configuration
            has_config = graph.nodes[node].get("parameters", {}) or graph.nodes[node].get("metadata", {}).get(
                "config", {}
            )
            if has_config:
                present_stages.append(stage_name)

        for required_stage in required_stages:
            if required_stage not in present_stages:
                validation_results["missing_stages"].append(required_stage.value)

        # Check for unusual patterns
        if self._detect_unusual_patterns(graph):
            validation_results["unusual_patterns"] = True

        # Check parameter ranges
        param_issues = self._check_parameter_ranges(graph)
        validation_results["parameter_issues"] = param_issues

        return validation_results

    def suggest_pipeline_variant(self, pipeline_id: str) -> str | None:
        """Suggest a known-good variant of a pipeline"""
        if pipeline_id not in self.pipeline_graphs:
            return None

        query_graph = self.pipeline_graphs[pipeline_id]

        # Find most similar known-good pipeline
        best_match = None
        best_similarity = 0.0

        for known_pipeline_id in self.known_good_patterns:
            if known_pipeline_id in self.pipeline_graphs:
                similarity = self._calculate_pipeline_similarity(query_graph, self.pipeline_graphs[known_pipeline_id])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = known_pipeline_id

        return best_match if best_similarity > 0.7 else None

    def flag_unusual_plans(self, pipeline_id: str) -> bool:
        """Flag if a pipeline plan is unusual"""
        if pipeline_id not in self.pipeline_graphs:
            return True

        graph = self.pipeline_graphs[pipeline_id]
        return self._detect_unusual_patterns(graph)

    def auto_fill_missing_steps(self, partial_pipeline_id: str) -> str:
        """Auto-fill missing steps in a partial pipeline"""
        if partial_pipeline_id not in self.pipeline_graphs:
            return partial_pipeline_id

        graph = self.pipeline_graphs[partial_pipeline_id]

        # Find missing stages
        all_stages = [
            PipelineStage.INGEST,
            PipelineStage.CHUNK,
            PipelineStage.RETRIEVE,
            PipelineStage.RERANK,
            PipelineStage.GENERATE,
            PipelineStage.VALIDATE,
        ]

        present_stages = set()
        stage_nodes = [n for n in graph.nodes() if graph.nodes[n]["node_type"] == "stage"]
        for node in stage_nodes:
            stage = graph.nodes[node]["stage"]
            if stage:
                present_stages.add(stage)

        missing_stages = [stage for stage in all_stages if stage not in present_stages]

        # Add missing stages with default configurations
        for stage in missing_stages:
            stage_node_id = f"{partial_pipeline_id}_{stage.value}_auto"

            stage_node = PipelineNode(
                node_id=stage_node_id,
                node_type=PipelineNodeType.STAGE,
                stage=stage,
                label=f"{stage.value.title()} Stage (Auto-filled)",
                parameters=self._get_default_stage_parameters(stage),
                metadata={
                    "stage_order": len(present_stages),
                    "auto_filled": True,
                    "pipeline_id": partial_pipeline_id,
                },
            )

            graph.add_node(stage_node_id, **stage_node.__dict__)

        return partial_pipeline_id

    def _detect_unusual_patterns(self, graph: nx.DiGraph) -> bool:
        """Detect unusual patterns in a pipeline graph"""
        # Check for missing sequential connections
        stage_nodes = [n for n in graph.nodes() if graph.nodes[n]["node_type"] == "stage"]

        # Count sequential edges
        sequential_edges = 0
        for u, v, data in graph.edges(data=True):
            if graph.nodes[u]["node_type"] == "stage" and graph.nodes[v]["node_type"] == "stage":
                sequential_edges += 1

        # Unusual if too few sequential connections
        expected_sequential = len(stage_nodes) - 1
        if sequential_edges < expected_sequential * 0.5:
            return True

        return False

    def _check_parameter_ranges(self, graph: nx.DiGraph) -> list[str]:
        """Check if parameters are within reasonable ranges"""
        warnings = []

        for node_id in graph.nodes():
            if graph.nodes[node_id]["node_type"] == "parameter":
                params = graph.nodes[node_id]["parameters"]
                param_name = graph.nodes[node_id]["metadata"]["parameter_name"]

                if "value" in params:
                    value = params["value"]

                    # Check specific parameter ranges
                    if param_name == "chunk_size" and (value < 100 or value > 2000):
                        warnings.append(f"Chunk size {value} may be outside optimal range (100-2000)")
                    elif param_name == "top_k" and (value < 1 or value > 50):
                        warnings.append(f"Top-k {value} may be outside optimal range (1-50)")
                    elif param_name == "temperature" and (value < 0.0 or value > 2.0):
                        warnings.append(f"Temperature {value} may be outside optimal range (0.0-2.0)")

        return warnings

    def _calculate_pipeline_similarity(self, graph1: nx.DiGraph, graph2: nx.DiGraph) -> float:
        """Calculate similarity between two pipeline graphs"""
        # Compare stage configurations
        stages1 = set(
            [
                graph1.nodes[n]["stage"]
                for n in graph1.nodes()
                if graph1.nodes[n]["node_type"] == "stage" and graph1.nodes[n]["stage"]
            ]
        )
        stages2 = set(
            [
                graph2.nodes[n]["stage"]
                for n in graph2.nodes()
                if graph2.nodes[n]["node_type"] == "stage" and graph2.nodes[n]["stage"]
            ]
        )

        if not stages1 and not stages2:
            return 1.0
        if not stages1 or not stages2:
            return 0.0

        intersection = len(stages1.intersection(stages2))
        union = len(stages1.union(stages2))

        return intersection / union if union > 0 else 0.0

    def _get_default_stage_parameters(self, stage: PipelineStage) -> dict[str, Any]:
        """Get default parameters for a pipeline stage"""
        defaults = {
            PipelineStage.INGEST: {"batch_size": 100, "encoding": "utf-8"},
            PipelineStage.CHUNK: {"chunk_size": 512, "overlap": 50},
            PipelineStage.RETRIEVE: {"top_k": 5, "similarity_threshold": 0.7},
            PipelineStage.RERANK: {"rerank_top_k": 3, "model": "cross-encoder"},
            PipelineStage.GENERATE: {"temperature": 0.7, "max_tokens": 1000},
            PipelineStage.VALIDATE: {"min_length": 10, "max_length": 5000},
        }

        return stage_ranges

    def export_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        """Export pipeline for analysis or persistence"""
        if pipeline_id not in self.pipeline_graphs:
            return {}

        graph = self.pipeline_graphs[pipeline_id]
        return {
            "pipeline_id": pipeline_id,
            "metadata": self.pipeline_metadata[pipeline_id],
            "graph": {
                "nodes": dict(graph.nodes(data=True)),
                "edges": [(u, v, d) for u, v, d in graph.edges(data=True)],
            },
        }


# Example usage
if __name__ == "__main__":
    # Create RAG pipeline governance
    governance = RAGPipelineGovernance()

    # Example pipeline configuration
    pipeline_config = {
        "ingest": {"parameters": {"batch_size": 100}},
        "chunk": {"parameters": {"chunk_size": 512, "overlap": 50}},
        "retrieve": {"parameters": {"top_k": 5}},
        "rerank": {"parameters": {"rerank_top_k": 3}},
        "generate": {"parameters": {"temperature": 0.7}},
        "validate": {"parameters": {"min_length": 10}},
    }

    # Create pipeline graph
    pipeline_id = governance.create_pipeline_graph(pipeline_config, "example_rag_pipeline")

    # Apply augmentations
    augmented_syntactic = governance.augment_pipeline(pipeline_id, "syntactic")
    augmented_semantic = governance.augment_pipeline(pipeline_id, "semantic")

    # Validate pipeline
    validation = governance.validate_pipeline(pipeline_id)

    # Check for unusual patterns
    is_unusual = governance.flag_unusual_plans(pipeline_id)

    print(f"Created pipeline: {pipeline_id}")
    print(f"Augmented pipelines: {augmented_syntactic}, {augmented_semantic}")
    print(f"Validation: {validation}")
    print(f"Is unusual: {is_unusual}")
