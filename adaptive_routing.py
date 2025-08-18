#!/usr/bin/env python3
"""
Adaptive Routing module.

Provides lightweight query classification and routing utilities used by tests.
The implementation favors readability and deterministic behavior over ML.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import (
    TypedDict,
    cast,
)


class QueryType(str, Enum):
    """Types of queries recognized by the router."""

    POINTED = "pointed"
    BROAD = "broad"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    UNKNOWN = "unknown"


@dataclass
class PipelineConfig:
    """Configuration for a routing pipeline."""

    name: str
    description: str
    max_tokens: int
    context_window: int
    use_few_shot: bool
    validation_level: str
    performance_profile: str


@dataclass
class QueryAnalysis:
    """Structured analysis of a query prior to routing."""

    query: str
    query_type: QueryType
    confidence: float
    keywords: list[str]
    complexity_score: float
    reasoning: str
    suggested_pipeline: str


class AdaptiveRouter:
    """Simple rule-based router for directing queries to processing pipelines."""

    def __init__(self) -> None:
        self.pipelines: dict[str, PipelineConfig] = {
            "fast_path": PipelineConfig(
                name="fast_path",
                description="Low-latency route for simple, pointed queries",
                max_tokens=1024,
                context_window=3000,
                use_few_shot=False,
                validation_level="light",
                performance_profile="speed",
            ),
            "comprehensive": PipelineConfig(
                name="comprehensive",
                description="High-context, accuracy-optimized route for deep exploration and analysis",
                max_tokens=4096,
                context_window=8192,
                use_few_shot=True,
                validation_level="strict",
                performance_profile="accuracy",
            ),
            "creative": PipelineConfig(
                name="creative",
                description="Divergent thinking route for ideation and design tasks",
                max_tokens=2048,
                context_window=4096,
                use_few_shot=True,
                validation_level="moderate",
                performance_profile="creativity",
            ),
        }

        self.query_patterns: dict[QueryType, list[re.Pattern[str]]] = {
            QueryType.POINTED: [
                re.compile(r"\bwhat\b"),
                re.compile(r"\bhow\b"),
                re.compile(r"\bwhen\b"),
                re.compile(r"\bwhich\b"),
                re.compile(r"\berror\b"),
                re.compile(r"\bfix\b"),
                re.compile(r"\bline\b"),
                re.compile(r"\?"),
            ],
            QueryType.BROAD: [
                re.compile(r"\bexplore\b"),
                re.compile(r"\bcomprehensive\b"),
                re.compile(r"\boverview\b"),
                re.compile(r"\bstudy\b"),
                re.compile(r"\barchitecture\b"),
            ],
            QueryType.ANALYTICAL: [
                re.compile(r"\banaly(?:ze|sis)\b"),
                re.compile(r"\bprofile\b"),
                re.compile(r"\bmetrics?\b"),
                re.compile(r"\bcompare\b"),
                re.compile(r"\befficienc(?:y|ies)\b"),
                re.compile(r"\bperformance\b"),
                re.compile(r"\bpatterns?\b"),
            ],
            QueryType.CREATIVE: [
                re.compile(r"\bdesign\b"),
                re.compile(r"\bbrainstorm\b"),
                re.compile(r"\bimagine\b"),
                re.compile(r"\bnovel\b"),
                re.compile(r"\bnew\b"),
            ],
            QueryType.UNKNOWN: [],
        }

        self._stopwords = {
            "the",
            "is",
            "a",
            "an",
            "of",
            "our",
            "with",
            "and",
            "to",
            "in",
            "this",
            "do",
            "i",
            "how",
            "what",
            "which",
            "when",
            "does",
            "return",
            "for",
            "on",
            "it",
        }

    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze a query to determine type, confidence, keywords, and routing.

        The analysis is intentionally simple but deterministic for tests.
        """

        text = (query or "").strip()
        normalized = text.lower()

        type_scores = self._score_query_types(normalized)
        best_type, confidence = self._select_query_type(type_scores)

        keywords = self._extract_keywords(normalized)
        complexity_score = self._estimate_complexity(normalized, keywords)
        suggested_pipeline = self._select_pipeline(best_type, complexity_score)

        reasoning = self._build_reasoning(
            best_type, confidence, complexity_score, suggested_pipeline
        )

        return QueryAnalysis(
            query=text,
            query_type=best_type,
            confidence=confidence,
            keywords=keywords,
            complexity_score=complexity_score,
            reasoning=reasoning,
            suggested_pipeline=suggested_pipeline,
        )

    def route_query(self, query: str) -> ResultDict:
        """Route a query and return a JSON-serializable structure."""

        analysis = self.analyze_query(query)
        pipeline_cfg = self.pipelines.get(
            analysis.suggested_pipeline, self.pipelines["fast_path"]
        )

        analysis_dict: AnalysisDict = {
            "query_type": analysis.query_type.value,
            "confidence": analysis.confidence,
            "keywords": analysis.keywords,
            "complexity_score": analysis.complexity_score,
            "reasoning": analysis.reasoning,
            "suggested_pipeline": analysis.suggested_pipeline,
        }

        routing: RoutingDict = {
            "pipeline": analysis.suggested_pipeline,
            "pipeline_config": cast(PipelineConfigDict, asdict(pipeline_cfg)),
        }

        recommendations = self._generate_recommendations(analysis)

        result: ResultDict = {
            "query": analysis.query,
            "analysis": analysis_dict,
            "routing": routing,
            "recommendations": recommendations,
        }

        # Validate JSON serializability during development
        json.dumps(result)
        return result

    def _score_query_types(self, normalized_query: str) -> dict[QueryType, int]:
        scores: dict[QueryType, int] = {}
        for qtype, patterns in self.query_patterns.items():
            scores[qtype] = sum(len(p.findall(normalized_query)) for p in patterns)
        return scores

    def _select_query_type(
        self, scores: dict[QueryType, int]
    ) -> tuple[QueryType, float]:
        non_unknown = {k: v for k, v in scores.items() if k is not QueryType.UNKNOWN}
        total_matches = sum(non_unknown.values())
        if total_matches == 0:
            return QueryType.POINTED, 0.1

        # Using lambda avoids Optional[int] from dict.get type and satisfies type checkers
        best_type = max(non_unknown, key=lambda k: non_unknown[k])
        max_score = non_unknown[best_type]
        fraction = max_score / total_matches if total_matches > 0 else 0.0
        confidence = max(0.0, min(1.0, 0.3 + 0.7 * fraction))
        return best_type, confidence

    def _extract_keywords(self, normalized_query: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z]+", normalized_query)
        deduped: list[str] = []
        seen = set()
        for token in tokens:
            if token in self._stopwords:
                continue
            if token in seen:
                continue
            seen.add(token)
            deduped.append(token)
        return deduped

    def _estimate_complexity(self, normalized_query: str, keywords: list[str]) -> float:
        length_factor = min(1.0, len(keywords) / 30.0)
        modifier = 0.0
        if "comprehensive" in normalized_query:
            modifier += 0.05
        if "distributed" in normalized_query:
            modifier += 0.05
        if "multiple" in normalized_query:
            modifier += 0.05
        if "replication" in normalized_query:
            modifier += 0.05
        score = max(0.0, min(1.0, length_factor + modifier))
        return score

    def _select_pipeline(self, query_type: QueryType, complexity_score: float) -> str:
        if query_type is QueryType.POINTED and complexity_score < 0.3:
            return "fast_path"
        if query_type is QueryType.BROAD:
            return "comprehensive"
        if query_type is QueryType.ANALYTICAL:
            return "comprehensive" if complexity_score >= 0.3 else "fast_path"
        if query_type is QueryType.CREATIVE:
            return "creative"
        return "fast_path"

    def _build_reasoning(
        self,
        query_type: QueryType,
        confidence: float,
        complexity_score: float,
        pipeline: str,
    ) -> str:
        return (
            f"Classified as {query_type.value} (confidence={confidence:.2f}), "
            f"complexity={complexity_score:.2f}. Using pipeline '{pipeline}'."
        )

    def _generate_recommendations(self, analysis: QueryAnalysis) -> list[str]:
        recs: list[str] = []
        if analysis.confidence < 0.3:
            recs.append(
                "Low confidence in classification. Consider rephrasing for clarity."
            )

        if analysis.query_type in {QueryType.BROAD, QueryType.ANALYTICAL}:
            recs.append(
                "Provide additional context or constraints to improve accuracy."
            )

        if analysis.query_type is QueryType.CREATIVE:
            recs.append("Try multiple diverse prompts to encourage novel solutions.")

        if (
            analysis.suggested_pipeline == "fast_path"
            and analysis.complexity_score >= 0.5
        ):
            recs.append(
                "High complexity detected. Consider switching to the comprehensive pipeline."
            )

        if not recs:
            recs.append("Proceed with the suggested pipeline.")
        return recs


class AnalysisDict(TypedDict):
    query_type: str
    confidence: float
    keywords: list[str]
    complexity_score: float
    reasoning: str
    suggested_pipeline: str


class PipelineConfigDict(TypedDict):
    name: str
    description: str
    max_tokens: int
    context_window: int
    use_few_shot: bool
    validation_level: str
    performance_profile: str


class RoutingDict(TypedDict):
    pipeline: str
    pipeline_config: PipelineConfigDict


class ResultDict(TypedDict):
    query: str
    analysis: AnalysisDict
    routing: RoutingDict
    recommendations: list[str]


__all__ = ["AdaptiveRouter", "PipelineConfig", "QueryAnalysis", "QueryType"]
