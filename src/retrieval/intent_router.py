"""
Phase 1.5: Intent Router for Structured Query Early Routing

Routes structured queries (lookup/id/date/metric) to specialized handlers before text RAG.
Implements rule-based classification with feature flags for canary deployment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class IntentClassification:
    """Result of intent classification."""

    intent_type: str  # 'structured', 'text_rag', 'hybrid'
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Human-readable explanation
    route_target: str  # 'sql', 'kg', 'rag', 'hybrid'
    structured_fields: Dict[str, Any] = None  # Extracted structured data
    should_short_circuit: bool = False  # Whether to skip text RAG


@dataclass
class IntentRouterConfig:
    """Configuration for intent routing."""

    # Intent detection thresholds
    structured_confidence_threshold: float = 0.7
    hybrid_confidence_threshold: float = 0.5

    # Feature flags
    enable_structured_routing: bool = True
    enable_hybrid_routing: bool = True
    enable_canary: bool = False
    canary_sample_pct: float = 0.1

    # Structured query patterns
    lookup_patterns: List[str] = None
    id_patterns: List[str] = None
    date_patterns: List[str] = None
    metric_patterns: List[str] = None

    # SQL/KG routing preferences
    prefer_sql_for: List[str] = None
    prefer_kg_for: List[str] = None


class StructuredQueryDetector:
    """Detects structured queries that can be handled by SQL/KG systems."""

    def __init__(self, config: IntentRouterConfig):
        self.config = config

        # Default lookup patterns
        if not self.config.lookup_patterns:
            self.config.lookup_patterns = [
                r"\b(find|get|show|list|search)\s+(all|the|every)\s+(\w+)\b",  # find all users
                r"\b(count|how\s+many)\s+(\w+)\b",  # count users
                r"\b(exists|does\s+exist)\s+(\w+)\b",  # user exists
                r"\b(select|query)\s+(\w+)\b",  # select users
                r"\b(count\s+all\s+\w+)\b",  # count all users
                r"\b(how\s+many\s+\w+)\b",  # how many users
            ]

        # Default ID patterns
        if not self.config.id_patterns:
            self.config.id_patterns = [
                r"\b(id|user_id|document_id|file_id)\s*[=:]\s*(\w+)\b",  # id=123
                r"\b(\w+)\s+with\s+id\s+(\w+)\b",  # user with id 123
                r"\b(\w+)\s+#(\w+)\b",  # user #123
                r"\b(\w+)\s+(\d{3,})\b",  # user 12345
            ]

        # Default date patterns
        if not self.config.date_patterns:
            self.config.date_patterns = [
                r"\b(created|updated|modified|published)\s+(before|after|on|since)\s+([^\s]+)\b",
                r"\b(\w+)\s+in\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})\b",
                r"\b(\w+)\s+between\s+([^\s]+)\s+and\s+([^\s]+)\b",
                r"\b(\w+)\s+from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\b",
                r"\b(\d{4}-\d{2}-\d{2})\b",  # YYYY-MM-DD format
                r"\b(\d{4})\b",  # Just year
            ]

        # Default metric patterns
        if not self.config.metric_patterns:
            self.config.metric_patterns = [
                r"\b(avg|average|mean|median|sum|total|count|min|max)\s+(of\s+)?(\w+)\b",
                r"\b(performance|accuracy|speed|efficiency|quality)\s+(metrics?|scores?|ratings?)\b",
                r"\b(compare|vs|versus)\s+(\w+)\s+and\s+(\w+)\s+(performance|accuracy|speed)\b",
                r"\b(top|best|worst)\s+(\d+)\s+(\w+)\s+(by|in)\s+(\w+)\b",
                r"\b(average|avg)\s+(performance|accuracy|speed)\b",  # average performance
                r"\b(\w+)\s+vs\s+(\w+)\b",  # A vs B
            ]

        # Default routing preferences
        if not self.config.prefer_sql_for:
            self.config.prefer_sql_for = ["count", "exists", "lookup", "aggregate", "metric"]

        if not self.config.prefer_kg_for:
            self.config.prefer_kg_for = ["relationship", "connection", "path", "graph", "entity"]

    def detect_structured_intent(self, query: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Detect if query has structured intent.

        Returns:
            (intent_type, confidence, extracted_data)
        """
        query_lower = query.lower()
        confidence = 0.0
        extracted_data = {}

        # Check lookup patterns
        lookup_score = self._check_patterns(query_lower, self.config.lookup_patterns)
        if lookup_score > 0:
            confidence += lookup_score * 0.4
            extracted_data["lookup_type"] = "data_retrieval"

        # Check ID patterns
        id_score = self._check_patterns(query_lower, self.config.id_patterns)
        if id_score > 0:
            confidence += id_score * 0.35
            extracted_data["id_type"] = "identifier_lookup"

        # Check date patterns
        date_score = self._check_patterns(query_lower, self.config.date_patterns)
        if date_score > 0:
            confidence += date_score * 0.35
            extracted_data["date_type"] = "temporal_query"

        # Check metric patterns
        metric_score = self._check_patterns(query_lower, self.config.metric_patterns)
        if metric_score > 0:
            confidence += metric_score * 0.3
            extracted_data["metric_type"] = "analytical_query"

        # Determine intent type
        if confidence >= 0.5:
            intent_type = "structured"
        elif confidence >= 0.2:
            intent_type = "hybrid"
        else:
            intent_type = "text_rag"

        return intent_type, confidence, extracted_data

    def _check_patterns(self, query: str, patterns: List[str]) -> float:
        """Check how many patterns match the query."""
        matches = 0
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                matches += 1

        # Return normalized score (0.0 to 1.0)
        return min(1.0, matches / len(patterns)) if patterns else 0.0


class RouteTargetSelector:
    """Selects the best route target (SQL, KG, RAG) for structured queries."""

    def __init__(self, config: IntentRouterConfig):
        self.config = config

    def select_route_target(
        self, intent_type: str, extracted_data: Dict[str, Any], query: str
    ) -> Tuple[str, float, str]:
        """
        Select the best route target for the query.

        Returns:
            (route_target, confidence, reasoning)
        """
        if intent_type == "text_rag":
            return "rag", 1.0, "Text-based query, use RAG"

        # For structured queries, determine best target
        route_scores = {"sql": 0.0, "kg": 0.0, "rag": 0.0}

        reasoning = []

        # Score SQL routing
        sql_score = self._calculate_sql_score(extracted_data, query)
        route_scores["sql"] = sql_score
        if sql_score > 0:
            reasoning.append(f"SQL score: {sql_score:.2f}")

        # Score KG routing
        kg_score = self._calculate_kg_score(extracted_data, query)
        route_scores["kg"] = kg_score
        if kg_score > 0:
            reasoning.append(f"KG score: {kg_score:.2f}")

        # Score RAG routing
        rag_score = self._calculate_rag_score(extracted_data, query)
        route_scores["rag"] = rag_score
        if rag_score > 0:
            reasoning.append(f"RAG score: {rag_score:.2f}")

        # Select best route
        best_route = max(route_scores.keys(), key=lambda k: route_scores[k])
        best_score = route_scores[best_route]

        # Hybrid routing if scores are close
        if intent_type == "hybrid" and best_score < 0.8:
            best_route = "hybrid"
            best_score = 0.7
            reasoning.append("Hybrid routing: multiple approaches needed")

        reasoning_str = "; ".join(reasoning) if reasoning else f"Selected {best_route}"

        return best_route, best_score, reasoning_str

    def _calculate_sql_score(self, extracted_data: Dict[str, Any], query: str) -> float:
        """Calculate SQL routing score."""
        score = 0.0

        # High score for lookup and ID queries
        if "lookup_type" in extracted_data:
            score += 0.4
        if "id_type" in extracted_data:
            score += 0.3

        # High score for metric queries
        if "metric_type" in extracted_data:
            score += 0.5

        # Check for SQL-friendly terms
        sql_terms = ["count", "sum", "avg", "select", "where", "table", "database"]
        sql_matches = sum(1 for term in sql_terms if term in query.lower())
        score += min(0.3, sql_matches * 0.1)

        return min(1.0, score)

    def _calculate_kg_score(self, extracted_data: Dict[str, Any], query: str) -> float:
        """Calculate Knowledge Graph routing score."""
        score = 0.0

        # High score for relationship queries
        if any(term in query.lower() for term in ["relationship", "connection", "path", "graph"]):
            score += 0.6

        # High score for entity queries
        if any(term in query.lower() for term in ["entity", "person", "organization", "file"]):
            score += 0.4

        # Check for graph-friendly terms
        kg_terms = ["connected", "linked", "related", "neighbor", "traverse", "walk"]
        kg_matches = sum(1 for term in kg_terms if term in query.lower())
        score += min(0.3, kg_matches * 0.1)

        return min(1.0, score)

    def _calculate_rag_score(self, extracted_data: Dict[str, Any], query: str) -> float:
        """Calculate RAG routing score."""
        score = 0.0

        # High score for complex, multi-part queries
        if len(query.split()) > 15:
            score += 0.3

        # High score for explanatory queries
        if any(term in query.lower() for term in ["explain", "how", "why", "what is", "describe"]):
            score += 0.4

        # High score for comparison queries
        if any(term in query.lower() for term in ["compare", "difference", "similar", "versus"]):
            score += 0.3

        return min(1.0, score)


class IntentRouter:
    """Main intent router for structured query early routing."""

    def __init__(self, config: IntentRouterConfig):
        self.config = config
        self.detector = StructuredQueryDetector(config)
        self.route_selector = RouteTargetSelector(config)

    def classify_intent(self, query: str, request_id: Optional[str] = None) -> IntentClassification:
        """
        Classify query intent and determine routing strategy.

        Args:
            query: User query
            request_id: Optional request ID for canary tracking

        Returns:
            IntentClassification with routing decision
        """
        # Detect structured intent
        intent_type, confidence, extracted_data = self.detector.detect_structured_intent(query)

        # Select route target
        route_target, route_confidence, route_reasoning = self.route_selector.select_route_target(
            intent_type, extracted_data, query
        )

        # Determine if we should short-circuit
        should_short_circuit = (
            self.config.enable_structured_routing
            and intent_type == "structured"
            and confidence >= self.config.structured_confidence_threshold
            and route_target in ["sql", "kg"]
        )

        # Canary deployment check
        if self.config.enable_canary and request_id:
            should_short_circuit = self._should_enable_canary(request_id) and should_short_circuit

        # Build reasoning
        reasoning_parts = [
            f"Intent: {intent_type} (confidence: {confidence:.2f})",
            f"Route: {route_target} (confidence: {route_confidence:.2f})",
            f"Route reasoning: {route_reasoning}",
        ]

        if should_short_circuit:
            reasoning_parts.append("Short-circuit: routing to structured handler")
        else:
            reasoning_parts.append("Continuing with text RAG pipeline")

        reasoning = "; ".join(reasoning_parts)

        return IntentClassification(
            intent_type=intent_type,
            confidence=confidence,
            reasoning=reasoning,
            route_target=route_target,
            structured_fields=extracted_data,
            should_short_circuit=should_short_circuit,
        )

    def _should_enable_canary(self, request_id: str) -> bool:
        """Determine if canary should be enabled for this request."""
        if not self.config.enable_canary:
            return False

        # Simple hash-based sampling
        import hashlib

        hash_value = int(hashlib.md5(request_id.encode()).hexdigest()[:8], 16)
        sample_threshold = int(self.config.canary_sample_pct * 0xFFFFFFFF)

        return hash_value < sample_threshold


def create_intent_router(config: Optional[IntentRouterConfig] = None) -> IntentRouter:
    """Factory function to create an IntentRouter."""

    if not config:
        config = IntentRouterConfig()

    return IntentRouter(config)
