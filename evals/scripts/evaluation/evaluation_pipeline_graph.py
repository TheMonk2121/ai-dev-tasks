#!/usr/bin/env python3
"""
Evaluation Pipeline Graph - DiGraph-based visualization and optimization
Supports gold, real, and mock evaluation profiles with comprehensive pipeline analysis
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import networkx as nx

# Optional matplotlib import for visualization
try:
    import matplotlib.pyplot as plt
    _matplotlib_available = True
except ImportError:
    _matplotlib_available = False
    plt = None  # type: ignore[assignment]


class EvaluationProfile(Enum):
    GOLD = "gold"
    REAL = "real" 
    MOCK = "mock"


class EvaluationStage(Enum):
    INITIALIZATION = "initialization"
    PROFILE_SETUP = "profile_setup"
    DATA_LOADING = "data_loading"
    MEMORY_HYDRATION = "memory_hydration"
    RETRIEVAL = "retrieval"
    RERANKING = "reranking"
    GENERATION = "generation"
    SCORING = "scoring"
    METRICS_CALCULATION = "metrics_calculation"
    RESULTS_STORAGE = "results_storage"
    CLEANUP = "cleanup"


class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class EvaluationNode:
    """Represents a node in the evaluation pipeline graph"""
    node_id: str
    stage: EvaluationStage
    profile: EvaluationProfile
    status: StageStatus
    start_time: float | None = None
    end_time: float | None = None
    duration: float | None = None
    metadata: dict[str, str] = None
    dependencies: list[str] = None
    outputs: list[str] = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata: dict[str, Any] = {}
        if self.dependencies is None:
            self.dependencies: list[Any] = []
        if self.outputs is None:
            self.outputs: list[Any] = []
@dataclass
class EvaluationEdge:
    """Represents an edge in the evaluation pipeline graph"""
    source_id: str
    target_id: str
    edge_type: str  # 'dependency', 'data_flow', 'control_flow'
    weight: float = 1.0
    metadata: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata: dict[str, Any] = {}
class EvaluationPipelineGraph:
    """DiGraph-based evaluation pipeline management and visualization"""
    
    def __init__(self, profile: EvaluationProfile) -> None:
        self.graph: nx.DiGraph[str] = nx.DiGraph()
        self.profile: EvaluationProfile = profile
        self.nodes: dict[str, EvaluationNode] = {}
        self.edges: dict[tuple[str, str], EvaluationEdge] = {}
        self.execution_order: list[str] = []
        self.parallel_groups: list[list[str]] = []
        
    def build_pipeline(self) -> None:
        """Build the evaluation pipeline graph based on profile"""
        if self.profile == EvaluationProfile.GOLD:
            self._build_gold_pipeline()
        elif self.profile == EvaluationProfile.REAL:
            self._build_real_pipeline()
        elif self.profile == EvaluationProfile.MOCK:
            self._build_mock_pipeline()
        else:
            raise ValueError(f"Unknown profile: {self.profile}")
    
    def _build_gold_pipeline(self) -> None:
        """Build gold evaluation pipeline (real RAG + gold cases)"""
        stages: list[tuple[str, EvaluationStage, list[str]]] = [
            ("init", EvaluationStage.INITIALIZATION, []),
            ("profile_setup", EvaluationStage.PROFILE_SETUP, ["init"]),
            ("data_loading", EvaluationStage.DATA_LOADING, ["profile_setup"]),
            ("memory_hydration", EvaluationStage.MEMORY_HYDRATION, ["data_loading"]),
            ("retrieval", EvaluationStage.RETRIEVAL, ["memory_hydration"]),
            ("reranking", EvaluationStage.RERANKING, ["retrieval"]),
            ("generation", EvaluationStage.GENERATION, ["reranking"]),
            ("scoring", EvaluationStage.SCORING, ["generation"]),
            ("metrics", EvaluationStage.METRICS_CALCULATION, ["scoring"]),
            ("storage", EvaluationStage.RESULTS_STORAGE, ["metrics"]),
            ("cleanup", EvaluationStage.CLEANUP, ["storage"])
        ]
        
        self._add_stages(stages)
        self._add_profile_specific_edges()
    
    def _build_real_pipeline(self) -> None:
        """Build real evaluation pipeline (real RAG + project data)"""
        stages: list[tuple[str, EvaluationStage, list[str]]] = [
            ("init", EvaluationStage.INITIALIZATION, []),
            ("profile_setup", EvaluationStage.PROFILE_SETUP, ["init"]),
            ("data_loading", EvaluationStage.DATA_LOADING, ["profile_setup"]),
            ("memory_hydration", EvaluationStage.MEMORY_HYDRATION, ["data_loading"]),
            ("retrieval", EvaluationStage.RETRIEVAL, ["memory_hydration"]),
            ("reranking", EvaluationStage.RERANKING, ["retrieval"]),
            ("generation", EvaluationStage.GENERATION, ["reranking"]),
            ("scoring", EvaluationStage.SCORING, ["generation"]),
            ("metrics", EvaluationStage.METRICS_CALCULATION, ["scoring"]),
            ("storage", EvaluationStage.RESULTS_STORAGE, ["metrics"]),
            ("cleanup", EvaluationStage.CLEANUP, ["storage"])
        ]
        
        self._add_stages(stages)
        self._add_profile_specific_edges()
    
    def _build_mock_pipeline(self) -> None:
        """Build mock evaluation pipeline (synthetic responses)"""
        stages: list[tuple[str, EvaluationStage, list[str]]] = [
            ("init", EvaluationStage.INITIALIZATION, []),
            ("profile_setup", EvaluationStage.PROFILE_SETUP, ["init"]),
            ("data_loading", EvaluationStage.DATA_LOADING, ["profile_setup"]),
            ("generation", EvaluationStage.GENERATION, ["data_loading"]),  # Skip retrieval/reranking
            ("scoring", EvaluationStage.SCORING, ["generation"]),
            ("metrics", EvaluationStage.METRICS_CALCULATION, ["scoring"]),
            ("storage", EvaluationStage.RESULTS_STORAGE, ["metrics"]),
            ("cleanup", EvaluationStage.CLEANUP, ["storage"])
        ]
        
        self._add_stages(stages)
        self._add_profile_specific_edges()
    
    def _add_stages(self, stages: list[tuple[str, EvaluationStage, list[str]]]) -> None:
        """Add stages to the pipeline graph"""
        for node_id, stage, dependencies in stages:
            node = EvaluationNode(
                node_id=node_id,
                stage=stage,
                profile=self.profile,
                status=StageStatus.PENDING,
                dependencies=dependencies,
                metadata={
                    "profile": self.profile.value,
                    "stage_type": stage.value,
                    "created_at": str(time.time())
                }
            )
            
            self.graph.add_node(node_id, **node.__dict__)
            self.nodes[node_id] = node
            
            # Add dependency edges
            for dep in dependencies:
                if dep in self.nodes:
                    edge = EvaluationEdge(
                        source_id=dep,
                        target_id=node_id,
                        edge_type="dependency",
                        weight=1.0,
                        metadata={"dependency_type": "sequential"}
                    )
                    self.graph.add_edge(dep, node_id, **edge.__dict__)
                    self.edges[(dep, node_id)] = edge
    
    def _add_profile_specific_edges(self) -> None:
        """Add profile-specific edges and optimizations"""
        if self.profile == EvaluationProfile.GOLD:
            self._add_parallel_retrieval_edges()
        elif self.profile == EvaluationProfile.REAL:
            self._add_data_processing_edges()
        elif self.profile == EvaluationProfile.MOCK:
            self._add_synthetic_edges()
    
    def _add_parallel_retrieval_edges(self) -> None:
        """Add edges for parallel retrieval in gold profile"""
        if "retrieval" in self.nodes and "reranking" in self.nodes:
            parallel_retrieval = EvaluationEdge(
                source_id="retrieval",
                target_id="reranking",
                edge_type="data_flow",
                weight=0.8,
                metadata={"parallel_execution": "true", "strategy": "multi_retrieval"}
            )
            self.graph.add_edge("retrieval", "reranking", **parallel_retrieval.__dict__)
    
    def _add_data_processing_edges(self) -> None:
        """Add edges for data processing in real profile"""
        if "data_loading" in self.nodes and "memory_hydration" in self.nodes:
            data_edge = EvaluationEdge(
                source_id="data_loading",
                target_id="memory_hydration",
                edge_type="data_flow",
                weight=0.9,
                metadata={"parallel_processing": "true", "data_sources": "multiple"}
            )
            self.graph.add_edge("data_loading", "memory_hydration", **data_edge.__dict__)
    
    def _add_synthetic_edges(self) -> None:
        """Add edges for synthetic data generation in mock profile"""
        if "data_loading" in self.nodes and "generation" in self.nodes:
            synthetic_edge = EvaluationEdge(
                source_id="data_loading",
                target_id="generation",
                edge_type="data_flow",
                weight=0.7,
                metadata={"synthetic_generation": "true", "parallel_workers": "3"}
            )
            self.graph.add_edge("data_loading", "generation", **synthetic_edge.__dict__)
    
    def get_execution_order(self) -> list[str]:
        """Get the correct execution order for the pipeline"""
        try:
            self.execution_order = list(nx.topological_sort(self.graph))
            return self.execution_order
        except nx.NetworkXError as e:
            raise ValueError(f"Pipeline has circular dependencies: {e}")
    
    def find_parallel_opportunities(self) -> list[list[str]]:
        """Find stages that can be executed in parallel"""
        execution_order = self.get_execution_order()
        parallel_groups: list[list[str]] = []
        
        for i, stage in enumerate(execution_order):
            parallel: list[str] = [stage]
            for j, other_stage in enumerate(execution_order):
                if (i != j and 
                    not nx.has_path(self.graph, stage, other_stage) and
                    not nx.has_path(self.graph, other_stage, stage)):
                    parallel.append(other_stage)
            
            if len(parallel) > 1:
                parallel_groups.append(parallel)
        
        self.parallel_groups = parallel_groups
        return parallel_groups
    
    def analyze_pipeline_performance(self) -> dict[str, str | int | float | list[str] | list[list[str]] | dict[str, str | int | float | list[str]]]:
        """Analyze pipeline performance and bottlenecks"""
        analysis: dict[str, str | int | float | list[str] | list[list[str]] | dict[str, str | int | float | list[str]]] = {
            "profile": self.profile.value,
            "total_stages": len(self.nodes),
            "total_edges": len(self.edges),
            "execution_order": self.get_execution_order(),
            "parallel_opportunities": self.find_parallel_opportunities(),
            "critical_path": self._find_critical_path(),
            "bottlenecks": self._find_bottlenecks(),
            "pipeline_efficiency": self._calculate_efficiency(),
            "stage_dependencies": self._analyze_dependencies()
        }
        return analysis
    
    def _find_critical_path(self) -> list[str]:
        """Find the critical path through the pipeline"""
        return self.get_execution_order()
    
    def _find_bottlenecks(self) -> list[str]:
        """Identify pipeline bottlenecks using centrality measures"""
        try:
            centrality = nx.betweenness_centrality(self.graph)
            return [node for node, _ in sorted(\1.items()
        except Exception:
            return []
    
    def _calculate_efficiency(self) -> float:
        """Calculate pipeline efficiency score"""
        density: float = float(nx.density(self.graph))
        parallel_ratio = len(self.find_parallel_opportunities()) / max(len(self.nodes), 1)
        return 1.0 - (density * 0.3) + (parallel_ratio * 0.2)
    
    def _analyze_dependencies(self) -> dict[str, str | int | float | list[str]]:
        """Analyze stage dependencies and complexity"""
        dependency_analysis: dict[str, str | int | float | list[str]] = {
            "max_dependencies": 0,
            "avg_dependencies": 0.0,
            "complex_stages": [],
            "simple_stages": []
        }
        
        dep_counts: list[int] = []
        for node_id, node in self.\1.items()
            dep_count = len(node.dependencies or [])
            dep_counts.append(dep_count)
            
            if dep_count > 3:
                complex_stages = result.get("key", "")
                if isinstance(complex_stages, list):
                    complex_stages.append(node_id)
            elif dep_count <= 1:
                simple_stages = result.get("key", "")
                if isinstance(simple_stages, list):
                    simple_stages.append(node_id)
        
        if dep_counts:
            result.get("key", "")
            result.get("key", "")
        
        return dependency_analysis
    
    def visualize_pipeline(self, output_path: str = "evaluation_pipeline.png") -> None:
        """Create a visual representation of the evaluation pipeline"""
        if not _matplotlib_available or plt is None:
            print("matplotlib not available, skipping visualization")
            return
        
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        
        stage_colors = {
            EvaluationStage.INITIALIZATION: 'lightblue',
            EvaluationStage.PROFILE_SETUP: 'lightgreen',
            EvaluationStage.DATA_LOADING: 'lightyellow',
            EvaluationStage.MEMORY_HYDRATION: 'lightcoral',
            EvaluationStage.RETRIEVAL: 'lightpink',
            EvaluationStage.RERANKING: 'lightgray',
            EvaluationStage.GENERATION: 'lightsteelblue',
            EvaluationStage.SCORING: 'lightcyan',
            EvaluationStage.METRICS_CALCULATION: 'lightgoldenrodyellow',
            EvaluationStage.RESULTS_STORAGE: 'lightseagreen',
            EvaluationStage.CLEANUP: 'lightsalmon'
        }
        
        colors: list[Any] = []
        for node_id in self.graph.nodes():
            stage = self.nodes[node_id].stage
            colors.append(result.get("key", "")
        
        plt.figure(figsize=(14, 10))
        nx.draw(self.graph, pos, 
                node_color=colors,
                with_labels=True,
                arrows=True,
                edge_color='gray',
                node_size=2000,
                font_size=8,
                font_weight='bold')
        
        plt.title(f"Evaluation Pipeline Graph - {self.profile.value.upper()} Profile", 
                 fontsize=16, fontweight='bold')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def export_pipeline_data(self, output_path: str = "evaluation_pipeline.json") -> None:
        """Export pipeline data for analysis"""
        pipeline_data = {
            "profile": self.profile.value,
            "nodes": {node_id: node.__dict__ for node_id, node in self.\1.items()
            "edges": {f"{src}_{tgt}": edge.__dict__ for (src, tgt), edge in self.\1.items()
            "analysis": self.analyze_pipeline_performance(),
            "created_at": datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(pipeline_data, f, indent=2, default=str)
    
    def get_stage_metadata(self, stage: EvaluationStage) -> dict[str, str]:
        """Get metadata for a specific stage"""
        for _node_id, node in self.\1.items()
            if node.stage == stage:
                return node.metadata or {}
        return {}
    
    def update_stage_status(self, node_id: str, status: StageStatus, 
                          error_message: str | None = None) -> None:
        """Update the status of a pipeline stage"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.status = status
            node.error_message = error_message
            
            if status == StageStatus.RUNNING:
                node.start_time = time.time()
            elif status in [StageStatus.COMPLETED, StageStatus.FAILED]:
                node.end_time = time.time()
                if node.start_time:
                    node.duration = node.end_time - node.start_time
            
            self.graph.nodes[node_id].update(node.__dict__)


def main() -> None:
    """Main entry point for testing the evaluation pipeline graph"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluation Pipeline Graph")
    _ = parser.add_argument("--profile", choices=["gold", "real", "mock"], 
                       default="gold", help="Evaluation profile")
    _ = parser.add_argument("--visualize", action="store_true", 
                       help="Generate pipeline visualization")
    _ = parser.add_argument("--export", action="store_true", 
                       help="Export pipeline data")
    _ = parser.add_argument("--analyze", action="store_true", 
                       help="Analyze pipeline performance")
    
    args = parser.parse_args()
    
    profile = EvaluationProfile(args.profile)
    pipeline = EvaluationPipelineGraph(profile)
    pipeline.build_pipeline()
    
    print(f"🔧 Built {args.profile.upper()} evaluation pipeline")
    print(f"📊 Total stages: {len(pipeline.nodes)}")
    print(f"🔗 Total edges: {len(pipeline.edges)}")
    
    if args.analyze:
        analysis = pipeline.analyze_pipeline_performance()
        print("\n📈 Pipeline Analysis:")
        efficiency = result.get("key", "")
        if isinstance(efficiency, (int, float)):
            print(f"   Efficiency: {efficiency:.2f}")
        
        parallel_opps = result.get("key", "")
        if isinstance(parallel_opps, list):
            print(f"   Parallel opportunities: {len(parallel_opps)}")
        
        critical_path = result.get("key", "")
        if isinstance(critical_path, list) and all(isinstance(item, str) for item in critical_path):
            # Ensure critical_path is a list of strings for join()
            path_strs: list[str] = [str(item) for item in critical_path]
            print(f"   Critical path: {' → '.join(path_strs)}")
    
    if args.visualize:
        output_file = f"evaluation_pipeline_{args.profile}.png"
        pipeline.visualize_pipeline(output_file)
        print(f"📊 Visualization saved: {output_file}")
    
    if args.export:
        output_file = f"evaluation_pipeline_{args.profile}.json"
        pipeline.export_pipeline_data(output_file)
        print(f"💾 Pipeline data exported: {output_file}")


if __name__ == "__main__":
    main()