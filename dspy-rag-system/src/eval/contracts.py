"""
Strongly typed contracts for RAG evaluation framework.
Eliminates magical dicts and provides clear interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Protocol, TypedDict

# Type aliases for clarity
Split = Literal["train", "dev", "test"]
RunMode = Literal["dense", "hybrid_rerank", "sparse"]
MetricName = Literal[
    "R@20",
    "R@10",
    "MRR@10",
    "nDCG@10",
    "faithfulness",
    "unsupported_rate",
    "evidence_precision",
    "context_utilization",
    "latency_p50_ms",
    "latency_p95_ms",
    "precision_at_k",
    "reranker_lift",
    "query_rewrite_improvement",
]


class QuerySample(TypedDict):
    """Individual query sample with optional gold labels"""

    id: str
    question: str
    # Optional gold labels depending on task
    gold_doc_ids: Optional[List[str]]
    gold_pages: Optional[List[str]]
    claim: Optional[str]
    expected_answer: Optional[str]


@dataclass(frozen=True)
class DatasetConfig:
    """Configuration for evaluation dataset"""

    name: str  # e.g., "beir:nfcorpus", "nq_500", "hotpot_500", "fever_1k"
    split: Split
    max_queries: int  # tiny slices for local dev
    task: Literal["retrieval", "multihop", "faithfulness", "latency", "robustness"]


@dataclass
class RunMetrics:
    """Strongly typed metrics from evaluation run"""

    dataset: str
    mode: RunMode
    metrics: Dict[MetricName, float]
    samples_evaluated: int
    timestamp: float


@dataclass
class QualityTargets:
    """Production quality targets for each metric"""

    recall_at_20_min: float = 0.65
    recall_at_20_max: float = 0.75
    precision_at_k_min: float = 0.20
    precision_at_k_max: float = 0.35
    reranker_lift_min: float = 0.10
    reranker_lift_max: float = 0.20
    faithfulness_min: float = 0.60
    faithfulness_max: float = 0.75
    unsupported_claim_rate_max: float = 0.15
    context_utilization_min: float = 0.60
    p50_latency_max: float = 2000.0  # 2 seconds in ms
    p95_latency_max: float = 4000.0  # 4 seconds in ms
    query_rewrite_improvement_min: float = 0.10


# Protocol definitions for evaluation components
class Retriever(Protocol):
    """Protocol for retrieval components"""

    def retrieve(self, query: str, k: int = 20) -> List[str]: ...


class ReRanker(Protocol):
    """Protocol for reranking components"""

    def rerank(self, query: str, doc_ids: List[str], top_m: int = 10) -> List[str]: ...


class RAGChecker(Protocol):
    """
    Contract subset for RAGChecker wrapper.
    Implementations should return pre-typed values (no raw dicts).
    """

    def evaluate_retrieval(self, *, dataset: DatasetConfig, mode: RunMode) -> RunMetrics: ...
    def evaluate_faithfulness(self, *, dataset: DatasetConfig) -> RunMetrics: ...
    def evaluate_latency(self, *, dataset: DatasetConfig) -> RunMetrics: ...
    def evaluate_robustness(self, *, dataset: DatasetConfig) -> RunMetrics: ...


class QualityGate(Protocol):
    """Protocol for quality gate evaluation"""

    def evaluate(self, metrics: RunMetrics, targets: QualityTargets) -> bool: ...
    def get_failures(self, metrics: RunMetrics, targets: QualityTargets) -> List[str]: ...


@dataclass
class EvaluationResult:
    """Complete evaluation result with quality gate status"""

    metrics: RunMetrics
    targets: QualityTargets
    passed: bool
    failures: List[str]
    warnings: List[str]
