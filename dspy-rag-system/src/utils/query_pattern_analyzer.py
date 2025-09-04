#!/usr/bin/env python3
"""
Query Pattern Analysis System

Analyzes query patterns and builds knowledge graph relationships for
predicting user needs and surfacing relevant information proactively.
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.conversation_storage import ConversationStorage
from utils.database_resilience import execute_query, get_database_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryPatternAnalyzer:
    """Analyzes query patterns and builds knowledge graph relationships."""

    def __init__(
        self, conversation_storage: Optional[ConversationStorage] = None, model_name: str = "all-MiniLM-L6-v2"
    ):
        """Initialize the query pattern analyzer.

        Args:
            conversation_storage: Storage instance for conversation data
            model_name: Name of the sentence transformer model to use
        """
        self.storage = conversation_storage or ConversationStorage()
        self.model = SentenceTransformer(model_name)
        self.db_manager = get_database_manager()

        # Pattern detection thresholds
        self.similarity_threshold = 0.7
        self.sequence_min_length = 3
        self.recurring_min_count = 2

    def analyze_query_sequence(self, user_id: str, time_window: int = 30) -> Dict[str, Any]:
        """Analyze patterns in user's query sequences.

        Args:
            user_id: User identifier
            time_window: Number of days to look back for analysis

        Returns:
            Dictionary containing detected patterns
        """
        try:
            logger.info(f"Analyzing query sequence for user {user_id} over {time_window} days")

            queries = self._get_recent_queries(user_id, time_window)
            if len(queries) < 2:
                logger.warning(f"Insufficient queries ({len(queries)}) for pattern analysis")
                return self._empty_pattern_result()

            patterns = {
                "topic_evolution": self._detect_topic_evolution(queries),
                "recurring_themes": self._detect_recurring_themes(queries),
                "question_sequences": self._detect_question_sequences(queries),
                "context_shifts": self._detect_context_shifts(queries),
                "intention_patterns": self._analyze_intention_patterns(queries),
                "temporal_patterns": self._analyze_temporal_patterns(queries),
                "analysis_metadata": {
                    "user_id": user_id,
                    "time_window_days": time_window,
                    "query_count": len(queries),
                    "analysis_timestamp": datetime.now().isoformat(),
                },
            }

            # Store patterns in database
            self._store_patterns(user_id, patterns)

            logger.info(
                f"Completed pattern analysis for user {user_id}: found {sum(len(v) if isinstance(v, list) else 0 for k, v in patterns.items() if k != 'analysis_metadata')} total patterns"
            )

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing query sequence for user {user_id}: {e}")
            return self._empty_pattern_result()

    def _get_recent_queries(self, user_id: str, days: int) -> List[Dict[str, Any]]:
        """Get recent queries for a user."""
        try:
            since_date = (datetime.now() - timedelta(days=days)).isoformat()

            query = """
                SELECT cm.message_id, cm.content, cm.timestamp, cm.embedding, cm.metadata,
                       cm.session_id, cs.session_name
                FROM conversation_messages cm
                JOIN conversation_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.user_id = %s
                  AND cm.role = 'human'
                  AND cm.timestamp >= %s
                ORDER BY cm.timestamp ASC
            """

            results = execute_query(query, (user_id, since_date))

            return [
                {
                    "message_id": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "embedding": row[3] if row[3] is not None else self._generate_embedding(row[1]),
                    "metadata": row[4] or {},
                    "session_id": row[5],
                    "session_name": row[6],
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting recent queries for user {user_id}: {e}")
            return []

    def _detect_topic_evolution(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect how topics evolve over the conversation."""
        if len(queries) < 3:
            return []

        evolutions = []
        window_size = 3

        for i in range(len(queries) - window_size + 1):
            window = queries[i : i + window_size]

            # Calculate semantic drift between consecutive queries
            semantic_drift = []
            for j in range(1, len(window)):
                similarity = self._cosine_similarity(window[j - 1]["embedding"], window[j]["embedding"])
                semantic_drift.append(1 - similarity)  # Convert to drift

            avg_drift = np.mean(semantic_drift)

            # Detect significant topic evolution
            if avg_drift > 0.3:  # Threshold for topic shift
                evolution = {
                    "start_query": window[0]["content"][:100],
                    "end_query": window[-1]["content"][:100],
                    "semantic_drift": avg_drift,
                    "time_span": (window[-1]["timestamp"] - window[0]["timestamp"]).total_seconds() / 3600,  # hours
                    "query_ids": [q["message_id"] for q in window],
                    "evolution_type": self._classify_evolution_type(window, semantic_drift),
                }
                evolutions.append(evolution)

        return evolutions

    def _detect_recurring_themes(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect recurring themes in user queries."""
        if len(queries) < self.recurring_min_count:
            return []

        # Group queries by semantic similarity
        similarity_groups = []
        used_queries = set()

        for i, query1 in enumerate(queries):
            if i in used_queries:
                continue

            similar_group = [query1]
            used_queries.add(i)

            for j, query2 in enumerate(queries[i + 1 :], i + 1):
                if j in used_queries:
                    continue

                similarity = self._cosine_similarity(query1["embedding"], query2["embedding"])
                if similarity > self.similarity_threshold:
                    similar_group.append(query2)
                    used_queries.add(j)

            if len(similar_group) >= self.recurring_min_count:
                similarity_groups.append(similar_group)

        # Convert to recurring themes
        themes = []
        for group in similarity_groups:
            # Calculate centroid
            embeddings = [q["embedding"] for q in group]
            centroid = np.mean(embeddings, axis=0)

            # Calculate time distribution
            timestamps = [q["timestamp"] for q in group]
            time_span = (max(timestamps) - min(timestamps)).days

            theme = {
                "theme_signature": self._generate_theme_signature(group),
                "queries": [{"message_id": q["message_id"], "content": q["content"][:100]} for q in group],
                "frequency": len(group),
                "time_span_days": time_span,
                "centroid_embedding": centroid.tolist(),
                "coherence_score": self._calculate_group_coherence(embeddings),
                "recurrence_pattern": self._analyze_recurrence_pattern(timestamps),
            }
            themes.append(theme)

        return themes

    def _detect_question_sequences(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect common question sequences and progressions."""
        if len(queries) < self.sequence_min_length:
            return []

        sequences = []

        # Look for sequences of related questions
        for i in range(len(queries) - self.sequence_min_length + 1):
            sequence_candidate = queries[i : i + self.sequence_min_length]

            # Check if queries form a logical sequence
            is_sequence = True
            sequence_strength = 0.0

            for j in range(1, len(sequence_candidate)):
                prev_query = sequence_candidate[j - 1]
                curr_query = sequence_candidate[j]

                # Check temporal proximity (should be within reasonable time)
                time_diff = (curr_query["timestamp"] - prev_query["timestamp"]).total_seconds() / 3600
                if time_diff > 24:  # More than 24 hours apart
                    is_sequence = False
                    break

                # Check semantic relationship
                similarity = self._cosine_similarity(prev_query["embedding"], curr_query["embedding"])
                if similarity < 0.3:  # Too different
                    is_sequence = False
                    break

                sequence_strength += similarity

            if is_sequence:
                sequence_strength /= len(sequence_candidate) - 1

                sequence = {
                    "sequence_queries": [
                        {"message_id": q["message_id"], "content": q["content"][:100]} for q in sequence_candidate
                    ],
                    "sequence_strength": sequence_strength,
                    "sequence_type": self._classify_sequence_type(sequence_candidate),
                    "time_span_hours": (
                        sequence_candidate[-1]["timestamp"] - sequence_candidate[0]["timestamp"]
                    ).total_seconds()
                    / 3600,
                    "progression_pattern": self._analyze_progression_pattern(sequence_candidate),
                }
                sequences.append(sequence)

        return sequences

    def _detect_context_shifts(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect significant context shifts in conversations."""
        if len(queries) < 2:
            return []

        shifts = []

        for i in range(1, len(queries)):
            prev_query = queries[i - 1]
            curr_query = queries[i]

            # Calculate semantic distance
            similarity = self._cosine_similarity(prev_query["embedding"], curr_query["embedding"])
            semantic_distance = 1 - similarity

            # Check for significant context shift
            if semantic_distance > 0.5:  # Threshold for context shift
                shift = {
                    "from_query": prev_query["content"][:100],
                    "to_query": curr_query["content"][:100],
                    "semantic_distance": semantic_distance,
                    "time_gap_minutes": (curr_query["timestamp"] - prev_query["timestamp"]).total_seconds() / 60,
                    "shift_type": self._classify_shift_type(semantic_distance),
                    "from_message_id": prev_query["message_id"],
                    "to_message_id": curr_query["message_id"],
                }
                shifts.append(shift)

        return shifts

    def _analyze_intention_patterns(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze patterns in user intentions."""
        intention_patterns = []

        # Classify each query's intention
        intentions = []
        for query in queries:
            intention = self._classify_query_intention(query["content"])
            intentions.append(
                {
                    "message_id": query["message_id"],
                    "content": query["content"][:100],
                    "intention": intention,
                    "timestamp": query["timestamp"],
                }
            )

        # Analyze intention sequences
        intention_sequence = [i["intention"] for i in intentions]
        intention_counts = Counter(intention_sequence)

        # Find common intention transitions
        transitions = defaultdict(int)
        for i in range(1, len(intention_sequence)):
            transition = (intention_sequence[i - 1], intention_sequence[i])
            transitions[transition] += 1

        # Most common intentions
        common_intentions = [
            {"intention": intention, "frequency": count, "percentage": count / len(intentions) * 100}
            for intention, count in intention_counts.most_common(5)
        ]

        # Most common transitions
        common_transitions = [
            {
                "from_intention": transition[0],
                "to_intention": transition[1],
                "frequency": count,
                "percentage": count / (len(intentions) - 1) * 100,
            }
            for transition, count in sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        intention_patterns.append(
            {
                "common_intentions": common_intentions,
                "common_transitions": common_transitions,
                "intention_diversity": len(intention_counts) / len(intentions) if intentions else 0,
                "total_queries": len(intentions),
            }
        )

        return intention_patterns

    def _analyze_temporal_patterns(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in user queries."""
        if len(queries) < 2:
            return {}

        timestamps = [q["timestamp"] for q in queries]

        # Time between queries
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600  # hours
            intervals.append(interval)

        # Hour of day distribution
        hours = [ts.hour for ts in timestamps]
        hour_distribution = Counter(hours)

        # Day of week distribution
        weekdays = [ts.weekday() for ts in timestamps]  # 0=Monday, 6=Sunday
        weekday_distribution = Counter(weekdays)

        return {
            "avg_interval_hours": np.mean(intervals) if intervals else 0,
            "median_interval_hours": np.median(intervals) if intervals else 0,
            "most_active_hours": [hour for hour, _ in hour_distribution.most_common(3)],
            "most_active_weekdays": [day for day, _ in weekday_distribution.most_common(3)],
            "query_burst_periods": self._detect_burst_periods(timestamps),
            "consistency_score": self._calculate_temporal_consistency(intervals),
        }

    def _store_patterns(self, user_id: str, patterns: Dict[str, Any]) -> None:
        """Store detected patterns in the database."""
        try:
            # Store query patterns
            for pattern_type, pattern_list in patterns.items():
                if pattern_type == "analysis_metadata" or not isinstance(pattern_list, list):
                    continue

                for pattern in pattern_list:
                    self._store_pattern(user_id, pattern_type, pattern)

        except Exception as e:
            logger.error(f"Error storing patterns for user {user_id}: {e}")

    def _store_pattern(self, user_id: str, pattern_type: str, pattern: Dict[str, Any]) -> None:
        """Store a single pattern in the database."""
        try:
            # Generate pattern signature and embedding
            pattern_signature = json.dumps(pattern, default=str, sort_keys=True)
            pattern_embedding = self._generate_embedding(pattern_signature)

            # Extract query IDs if available
            query_ids = []
            if "query_ids" in pattern:
                query_ids = pattern["query_ids"]
            elif "queries" in pattern:
                query_ids = [q.get("message_id") for q in pattern["queries"] if q.get("message_id")]

            # Calculate pattern strength based on type
            pattern_strength = self._calculate_pattern_strength(pattern_type, pattern)

            query = """
                INSERT INTO query_patterns (
                    user_id, pattern_type, pattern_signature, queries_in_pattern,
                    pattern_embedding, pattern_strength, occurrence_count, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """

            execute_query(
                query,
                (
                    user_id,
                    pattern_type,
                    pattern_signature[:500],  # Truncate if too long
                    query_ids,
                    pattern_embedding,
                    pattern_strength,
                    pattern.get("frequency", 1),
                    json.dumps(pattern),
                ),
            )

        except Exception as e:
            logger.error(f"Error storing pattern: {e}")

    # Helper methods
    def _empty_pattern_result(self) -> Dict[str, Any]:
        """Return empty pattern result structure."""
        return {
            "topic_evolution": [],
            "recurring_themes": [],
            "question_sequences": [],
            "context_shifts": [],
            "intention_patterns": [],
            "temporal_patterns": {},
            "analysis_metadata": {"error": "Insufficient data for analysis"},
        }

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            embedding = self.model.encode([text])[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * 384  # Return zero vector as fallback

    def _cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        except Exception:
            return 0.0

    def _classify_evolution_type(self, window: List[Dict[str, Any]], drift_scores: List[float]) -> str:
        """Classify the type of topic evolution."""
        avg_drift = np.mean(drift_scores)

        if avg_drift > 0.7:
            return "major_pivot"
        elif avg_drift > 0.5:
            return "topic_shift"
        elif avg_drift > 0.3:
            return "refinement"
        else:
            return "continuation"

    def _generate_theme_signature(self, queries: List[Dict[str, Any]]) -> str:
        """Generate a signature for a recurring theme."""
        contents = [q["content"] for q in queries]
        combined_text = " ".join(contents)

        # Simple approach: take most common words (could be improved with better NLP)
        words = combined_text.lower().split()
        word_counts = Counter(words)
        common_words = [word for word, _ in word_counts.most_common(5)]

        return " ".join(common_words)

    def _calculate_group_coherence(self, embeddings: List[List[float]]) -> float:
        """Calculate coherence score for a group of embeddings."""
        if len(embeddings) < 2:
            return 1.0

        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = self._cosine_similarity(embeddings[i], embeddings[j])
                similarities.append(sim)

        return np.mean(similarities) if similarities else 0.0

    def _analyze_recurrence_pattern(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze the recurrence pattern of timestamps."""
        if len(timestamps) < 2:
            return {"pattern": "single_occurrence"}

        # Calculate intervals between occurrences
        intervals = []
        for i in range(1, len(timestamps)):
            interval_days = (timestamps[i] - timestamps[i - 1]).days
            intervals.append(interval_days)

        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        # Classify pattern based on regularity
        if std_interval < avg_interval * 0.3:
            pattern_type = "regular"
        elif std_interval < avg_interval * 0.7:
            pattern_type = "semi_regular"
        else:
            pattern_type = "irregular"

        return {
            "pattern": pattern_type,
            "avg_interval_days": avg_interval,
            "std_interval_days": std_interval,
            "total_occurrences": len(timestamps),
        }

    def _classify_sequence_type(self, queries: List[Dict[str, Any]]) -> str:
        """Classify the type of question sequence."""
        # Simple heuristic based on content analysis
        contents = [q["content"].lower() for q in queries]

        # Look for common patterns
        if any("how" in c for c in contents) and any("why" in c for c in contents):
            return "exploration_sequence"
        elif any("error" in c or "problem" in c for c in contents):
            return "troubleshooting_sequence"
        elif any("implement" in c or "create" in c for c in contents):
            return "implementation_sequence"
        else:
            return "general_sequence"

    def _analyze_progression_pattern(self, queries: List[Dict[str, Any]]) -> str:
        """Analyze how queries progress in a sequence."""
        # Simplified analysis of query complexity or specificity
        word_counts = [len(q["content"].split()) for q in queries]

        if word_counts[-1] > word_counts[0] * 1.5:
            return "increasing_detail"
        elif word_counts[-1] < word_counts[0] * 0.7:
            return "simplifying"
        else:
            return "consistent_level"

    def _classify_shift_type(self, semantic_distance: float) -> str:
        """Classify the type of context shift."""
        if semantic_distance > 0.8:
            return "major_topic_change"
        elif semantic_distance > 0.6:
            return "topic_pivot"
        else:
            return "subtopic_shift"

    def _classify_query_intention(self, content: str) -> str:
        """Classify the intention behind a query."""
        content_lower = content.lower()

        # Simple rule-based classification (could be improved with ML)
        if any(word in content_lower for word in ["how", "tutorial", "guide", "learn"]):
            return "learn"
        elif any(word in content_lower for word in ["error", "bug", "problem", "issue", "fix"]):
            return "debug"
        elif any(word in content_lower for word in ["implement", "create", "build", "make"]):
            return "implement"
        elif any(word in content_lower for word in ["what", "which", "explore", "find"]):
            return "explore"
        elif any(word in content_lower for word in ["optimize", "improve", "better", "faster"]):
            return "optimize"
        elif any(word in content_lower for word in ["explain", "clarify", "understand", "mean"]):
            return "clarify"
        else:
            return "general"

    def _detect_burst_periods(self, timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detect periods of high query activity."""
        if len(timestamps) < 3:
            return []

        # Group queries by hour and find periods with high activity
        hourly_counts = defaultdict(int)
        for ts in timestamps:
            hour_key = ts.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] += 1

        # Find bursts (more than 2 queries in an hour)
        bursts = []
        for hour, count in hourly_counts.items():
            if count > 2:
                bursts.append({"start_time": hour.isoformat(), "query_count": count, "duration_hours": 1})

        return sorted(bursts, key=lambda x: x["query_count"], reverse=True)

    def _calculate_temporal_consistency(self, intervals: List[float]) -> float:
        """Calculate how consistent the user's query timing is."""
        if not intervals:
            return 0.0

        # Lower coefficient of variation indicates higher consistency
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        if mean_interval == 0:
            return 0.0

        cv = std_interval / mean_interval
        # Convert to consistency score (0-1, where 1 is most consistent)
        consistency = max(0, 1 - cv)

        return min(1.0, consistency)

    def _calculate_pattern_strength(self, pattern_type: str, pattern: Dict[str, Any]) -> float:
        """Calculate strength score for a pattern."""
        if pattern_type == "recurring_themes":
            return pattern.get("coherence_score", 0.0)
        elif pattern_type == "question_sequences":
            return pattern.get("sequence_strength", 0.0)
        elif pattern_type == "topic_evolution":
            return 1.0 - pattern.get("semantic_drift", 1.0)  # Invert drift to get stability
        elif pattern_type == "context_shifts":
            return pattern.get("semantic_distance", 0.0)
        else:
            return 0.5  # Default medium strength
