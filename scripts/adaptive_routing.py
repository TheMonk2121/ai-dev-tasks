#!/usr/bin/env python3
"""
Adaptive Routing System for Consensus Framework (B-101)

Routes different query types through optimized pipelines based on RAG research.
Implements the "routing by query type" principle from Jerry's LlamaIndex talk.

Usage:
    python3 scripts/adaptive_routing.py --query "specific question" --mode auto
    python3 scripts/adaptive_routing.py --query "broad exploration" --mode manual
"""

import argparse
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# Query type classification
class QueryType(Enum):
    POINTED = "pointed"  # Specific, targeted questions
    BROAD = "broad"  # Exploratory, comprehensive questions
    ANALYTICAL = "analytical"  # Data analysis and pattern recognition
    CREATIVE = "creative"  # Ideation and generation tasks


@dataclass
class QueryAnalysis:
    """Analysis results for a query."""

    query: str
    query_type: QueryType
    confidence: float
    keywords: list[str]
    complexity_score: float
    suggested_pipeline: str
    reasoning: str


@dataclass
class PipelineConfig:
    """Configuration for a processing pipeline."""

    name: str
    description: str
    query_types: list[QueryType]
    max_tokens: int
    context_window: int
    use_few_shot: bool
    validation_level: str
    performance_profile: str


class AdaptiveRouter:
    """Routes queries through optimized pipelines based on query type."""

    def __init__(self, config_path: str | None = None):
        self.pipelines = self._load_pipeline_configs()
        self.query_patterns = self._load_query_patterns()

    def _load_pipeline_configs(self) -> dict[str, PipelineConfig]:
        """Load pipeline configurations."""
        return {
            "fast_path": PipelineConfig(
                name="Fast Path",
                description="Optimized for pointed queries with minimal context",
                query_types=[QueryType.POINTED],
                max_tokens=1000,
                context_window=2000,
                use_few_shot=True,
                validation_level="basic",
                performance_profile="speed",
            ),
            "comprehensive": PipelineConfig(
                name="Comprehensive Analysis",
                description="Full analysis for broad exploratory queries",
                query_types=[QueryType.BROAD, QueryType.ANALYTICAL],
                max_tokens=4000,
                context_window=8000,
                use_few_shot=True,
                validation_level="strict",
                performance_profile="accuracy",
            ),
            "creative": PipelineConfig(
                name="Creative Generation",
                description="Optimized for ideation and creative tasks",
                query_types=[QueryType.CREATIVE],
                max_tokens=3000,
                context_window=6000,
                use_few_shot=True,
                validation_level="moderate",
                performance_profile="creativity",
            ),
        }

    def _load_query_patterns(self) -> dict[QueryType, list[re.Pattern]]:
        """Load regex patterns for query type detection."""
        return {
            QueryType.POINTED: [
                re.compile(r"\b(what|how|when|where|why|which|who)\b", re.IGNORECASE),
                re.compile(r"\b(specific|exact|precise|particular)\b", re.IGNORECASE),
                re.compile(r"\b(error|fix|bug|issue|problem)\b", re.IGNORECASE),
                re.compile(r"\b(implement|create|add|build)\b", re.IGNORECASE),
            ],
            QueryType.BROAD: [
                re.compile(r"\b(explore|analyze|overview|summary|review)\b", re.IGNORECASE),
                re.compile(r"\b(compare|evaluate|assess|examine)\b", re.IGNORECASE),
                re.compile(r"\b(understand|learn|study|research)\b", re.IGNORECASE),
                re.compile(r"\b(comprehensive|complete|full|detailed)\b", re.IGNORECASE),
            ],
            QueryType.ANALYTICAL: [
                re.compile(r"\b(analyze|pattern|trend|statistics|data)\b", re.IGNORECASE),
                re.compile(r"\b(performance|optimization|efficiency|metrics)\b", re.IGNORECASE),
                re.compile(r"\b(debug|profile|monitor|trace)\b", re.IGNORECASE),
                re.compile(r"\b(compare|benchmark|evaluate|measure)\b", re.IGNORECASE),
            ],
            QueryType.CREATIVE: [
                re.compile(r"\b(design|create|generate|imagine|brainstorm)\b", re.IGNORECASE),
                re.compile(r"\b(innovate|improve|enhance|optimize)\b", re.IGNORECASE),
                re.compile(r"\b(architecture|strategy|approach|solution)\b", re.IGNORECASE),
                re.compile(r"\b(creative|novel|unique|original)\b", re.IGNORECASE),
            ],
        }

    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze a query to determine its type and optimal pipeline."""
        query_lower = query.lower()

        # Calculate scores for each query type
        scores = {}
        for query_type, patterns in self.query_patterns.items():
            score = 0
            for pattern in patterns:
                matches = pattern.findall(query_lower)
                score += len(matches) * 0.5

            # Additional heuristics
            if query_type == QueryType.POINTED:
                if len(query.split()) < 10:
                    score += 1.0
                if any(word in query_lower for word in ["?", "how", "what", "why"]):
                    score += 0.5
            elif query_type == QueryType.BROAD:
                if len(query.split()) > 20:
                    score += 1.0
                if any(word in query_lower for word in ["explore", "overview", "summary"]):
                    score += 0.5
            elif query_type == QueryType.ANALYTICAL:
                if any(word in query_lower for word in ["analyze", "data", "performance"]):
                    score += 0.5
            elif query_type == QueryType.CREATIVE:
                if any(word in query_lower for word in ["design", "create", "generate"]):
                    score += 0.5

            scores[query_type] = score

        # Determine the most likely query type
        best_type = max(scores.items(), key=lambda x: x[1])
        confidence = min(best_type[1] / 3.0, 1.0)  # Normalize confidence

        # Extract keywords
        keywords = self._extract_keywords(query)

        # Calculate complexity score
        complexity_score = self._calculate_complexity(query)

        # Select optimal pipeline
        suggested_pipeline = self._select_pipeline(best_type[0], complexity_score)

        # Generate reasoning
        reasoning = self._generate_reasoning(best_type[0], scores, complexity_score)

        return QueryAnalysis(
            query=query,
            query_type=best_type[0],
            confidence=confidence,
            keywords=keywords,
            complexity_score=complexity_score,
            suggested_pipeline=suggested_pipeline,
            reasoning=reasoning,
        )

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract key terms from the query."""
        # Simple keyword extraction - could be enhanced with NLP
        words = re.findall(r"\b\w+\b", query.lower())
        # Filter out common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
        }
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return list(set(keywords))[:10]  # Limit to top 10 unique keywords

    def _calculate_complexity(self, query: str) -> float:
        """Calculate query complexity score (0.0 to 1.0)."""
        factors = []

        # Length factor
        word_count = len(query.split())
        factors.append(min(word_count / 50.0, 1.0))

        # Technical terms factor
        tech_terms = [
            "api",
            "database",
            "algorithm",
            "architecture",
            "framework",
            "protocol",
            "interface",
            "integration",
            "optimization",
            "performance",
        ]
        tech_count = sum(1 for term in tech_terms if term in query.lower())
        factors.append(min(tech_count / 5.0, 1.0))

        # Question complexity factor
        question_marks = query.count("?")
        factors.append(min(question_marks / 3.0, 1.0))

        # Average the factors
        return sum(factors) / len(factors)

    def _select_pipeline(self, query_type: QueryType, complexity: float) -> str:
        """Select the optimal pipeline based on query type and complexity."""
        if query_type == QueryType.POINTED and complexity < 0.5:
            return "fast_path"
        elif query_type == QueryType.CREATIVE:
            return "creative"
        else:
            return "comprehensive"

    def _generate_reasoning(self, query_type: QueryType, scores: dict[QueryType, float], complexity: float) -> str:
        """Generate human-readable reasoning for the classification."""
        reasons = []

        if query_type == QueryType.POINTED:
            reasons.append("Query appears to be a specific, targeted question")
            if complexity < 0.5:
                reasons.append("Low complexity suggests fast path pipeline")
        elif query_type == QueryType.BROAD:
            reasons.append("Query appears to be exploratory or comprehensive")
            reasons.append("Requires full analysis pipeline")
        elif query_type == QueryType.ANALYTICAL:
            reasons.append("Query involves data analysis or pattern recognition")
            reasons.append("Comprehensive pipeline needed for thorough analysis")
        elif query_type == QueryType.CREATIVE:
            reasons.append("Query involves creative generation or ideation")
            reasons.append("Creative pipeline optimized for generation tasks")

        if complexity > 0.7:
            reasons.append("High complexity detected - using comprehensive analysis")

        return "; ".join(reasons)

    def route_query(self, query: str, mode: str = "auto") -> dict:
        """Route a query through the appropriate pipeline."""
        analysis = self.analyze_query(query)
        pipeline_config = self.pipelines[analysis.suggested_pipeline]

        result = {
            "query": query,
            "analysis": {
                "query_type": analysis.query_type.value,
                "confidence": analysis.confidence,
                "keywords": analysis.keywords,
                "complexity_score": analysis.complexity_score,
                "reasoning": analysis.reasoning,
            },
            "routing": {
                "pipeline": analysis.suggested_pipeline,
                "pipeline_config": {
                    "name": pipeline_config.name,
                    "description": pipeline_config.description,
                    "max_tokens": pipeline_config.max_tokens,
                    "context_window": pipeline_config.context_window,
                    "use_few_shot": pipeline_config.use_few_shot,
                    "validation_level": pipeline_config.validation_level,
                    "performance_profile": pipeline_config.performance_profile,
                },
            },
            "recommendations": self._generate_recommendations(analysis, pipeline_config),
        }

        return result

    def _generate_recommendations(self, analysis: QueryAnalysis, pipeline_config: PipelineConfig) -> list[str]:
        """Generate recommendations for query processing."""
        recommendations = []

        if analysis.confidence < 0.5:
            recommendations.append("Low confidence in query classification - consider manual review")

        if analysis.complexity_score > 0.8:
            recommendations.append("High complexity detected - consider breaking into smaller queries")

        if pipeline_config.performance_profile == "speed":
            recommendations.append("Fast path selected - prioritize speed over comprehensiveness")
        elif pipeline_config.performance_profile == "accuracy":
            recommendations.append("Comprehensive analysis selected - prioritize accuracy over speed")
        elif pipeline_config.performance_profile == "creativity":
            recommendations.append("Creative pipeline selected - optimized for generation tasks")

        if pipeline_config.use_few_shot:
            recommendations.append("Few-shot examples will be injected for better context")

        return recommendations


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Adaptive Routing System for Consensus Framework")
    parser.add_argument("--query", required=True, help="Query to analyze and route")
    parser.add_argument("--mode", choices=["auto", "manual"], default="auto", help="Routing mode (auto or manual)")
    parser.add_argument("--output", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--config", help="Path to custom pipeline configuration")

    args = parser.parse_args()

    router = AdaptiveRouter(args.config)
    result = router.route_query(args.query, args.mode)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Query: {result['query']}")
        print(f"Type: {result['analysis']['query_type']} (confidence: {result['analysis']['confidence']:.2f})")
        print(f"Pipeline: {result['routing']['pipeline']}")
        print(f"Reasoning: {result['analysis']['reasoning']}")
        print("\nRecommendations:")
        for rec in result["recommendations"]:
            print(f"  - {rec}")


if __name__ == "__main__":
    main()
