#!/usr/bin/env python3
"""
Query Prediction System

Predicts likely next queries based on pattern analysis and proactively
surfaces relevant information to anticipate user needs.
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.conversation_storage import ConversationStorage
from utils.database_resilience import execute_query, get_database_manager
from utils.logger import setup_logger
from utils.query_pattern_analyzer import QueryPatternAnalyzer
from utils.query_vector_analyzer import QueryVectorAnalyzer

logger = setup_logger(__name__)


class QueryPredictor:
    """Predicts likely next queries based on pattern analysis."""

    def __init__(
        self,
        conversation_storage: ConversationStorage | None = None,
        pattern_analyzer: QueryPatternAnalyzer | None = None,
        vector_analyzer: QueryVectorAnalyzer | None = None,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        """Initialize the query predictor.

        Args:
            conversation_storage: Storage instance for conversation data
            pattern_analyzer: Pattern analyzer for detecting query patterns
            vector_analyzer: Vector analyzer for similarity computations
            model_name: Name of the sentence transformer model to use
        """
        self.storage = conversation_storage or ConversationStorage()
        self.pattern_analyzer = pattern_analyzer or QueryPatternAnalyzer(self.storage)
        self.vector_analyzer = vector_analyzer or QueryVectorAnalyzer(self.storage)
        self.model = SentenceTransformer(model_name)
        self.db_manager = get_database_manager()

        # Prediction configuration
        self.max_predictions = 5
        self.min_confidence = 0.3
        self.context_window_size = 3

    def predict_next_query_topics(
        self, user_id: str, current_context: str, max_predictions: int | None = None, include_rationale: bool = True
    ) -> list[dict[str, Any]]:
        """Predict what the user is likely to ask next.

        Args:
            user_id: User identifier
            current_context: Current conversation context or latest query
            max_predictions: Maximum number of predictions to return
            include_rationale: Whether to include prediction rationale

        Returns:
            List of predicted query topics with confidence scores
        """
        try:
            max_predictions = max_predictions or self.max_predictions
            logger.info(f"Predicting next query topics for user {user_id}")

            # Get user's historical patterns
            patterns = self.pattern_analyzer.analyze_query_sequence(user_id)

            # Current context embedding
            current_embedding = self.model.encode([current_context])[0]

            predictions = []

            # Sequence-based predictions
            if patterns.get("question_sequences"):
                sequence_predictions = self._predict_from_sequences(
                    patterns["question_sequences"], current_context, current_embedding
                )
                predictions.extend(sequence_predictions)

            # Topic evolution predictions
            if patterns.get("topic_evolution"):
                evolution_predictions = self._predict_topic_evolution(
                    patterns["topic_evolution"], current_embedding, user_id
                )
                predictions.extend(evolution_predictions)

            # Recurring pattern predictions
            if patterns.get("recurring_themes"):
                recurring_predictions = self._predict_recurring_themes(
                    patterns["recurring_themes"], current_context, current_embedding
                )
                predictions.extend(recurring_predictions)

            # Context shift predictions
            context_predictions = self._predict_context_shifts(user_id, current_embedding)
            predictions.extend(context_predictions)

            # Intention-based predictions
            if patterns.get("intention_patterns"):
                intention_predictions = self._predict_from_intentions(patterns["intention_patterns"], current_context)
                predictions.extend(intention_predictions)

            # Merge and rank predictions
            merged_predictions = self._merge_and_rank_predictions(predictions)

            # Filter by confidence and limit results
            filtered_predictions = [p for p in merged_predictions if p["confidence"] >= self.min_confidence][
                :max_predictions
            ]

            # Store predictions for accuracy tracking
            self._store_predictions(user_id, current_context, filtered_predictions)

            # Add rationale if requested
            if include_rationale:
                for pred in filtered_predictions:
                    pred["rationale"] = self._generate_prediction_rationale(pred)

            logger.info(f"Generated {len(filtered_predictions)} predictions for user {user_id}")
            return filtered_predictions

        except Exception as e:
            logger.error(f"Error predicting next query topics for user {user_id}: {e}")
            return []

    def proactive_information_surfacing(
        self, user_id: str, context: str, max_suggestions: int = 3
    ) -> list[dict[str, Any]]:
        """Surface relevant information before user asks.

        Args:
            user_id: User identifier
            context: Current conversation context
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of proactive information suggestions
        """
        try:
            logger.info(f"Surfacing proactive information for user {user_id}")

            # Find similar historical contexts
            similar_contexts = self._find_similar_historical_contexts(user_id, context)

            information_to_surface = []

            for similar_ctx in similar_contexts:
                # What did they ask after this context?
                follow_up_queries = self._get_follow_up_queries(similar_ctx["session_id"], similar_ctx["message_id"])

                # What information helped resolve those queries?
                for query in follow_up_queries:
                    resolution_info = self._extract_resolution_information(query)
                    if resolution_info:
                        information_to_surface.append(
                            {
                                "info_type": resolution_info["type"],
                                "content": resolution_info["content"],
                                "relevance": self._calculate_relevance(context, resolution_info["content"]),
                                "pattern_strength": similar_ctx["similarity"],
                                "source_context": similar_ctx["content"][:100],
                                "historical_success_rate": resolution_info.get("success_rate", 0.7),
                            }
                        )

            # Rank and filter suggestions
            ranked_suggestions = sorted(
                information_to_surface, key=lambda x: x["relevance"] * x["pattern_strength"], reverse=True
            )[:max_suggestions]

            logger.info(f"Surfaced {len(ranked_suggestions)} proactive information items for user {user_id}")
            return ranked_suggestions

        except Exception as e:
            logger.error(f"Error surfacing proactive information for user {user_id}: {e}")
            return []

    def analyze_prediction_accuracy(self, user_id: str, days_back: int = 30) -> dict[str, Any]:
        """Analyze accuracy of previous predictions.

        Args:
            user_id: User identifier
            days_back: Number of days to analyze

        Returns:
            Dictionary containing prediction accuracy metrics
        """
        try:
            logger.info(f"Analyzing prediction accuracy for user {user_id}")

            # Get predictions with actual outcomes
            predictions_with_outcomes = self._get_predictions_with_outcomes(user_id, days_back)

            if not predictions_with_outcomes:
                logger.warning(f"No predictions with outcomes found for user {user_id}")
                return {}

            # Calculate accuracy metrics
            total_predictions = len(predictions_with_outcomes)
            accurate_predictions = sum(1 for p in predictions_with_outcomes if p["was_accurate"])

            # Accuracy by prediction method
            method_accuracy = defaultdict(list)
            for p in predictions_with_outcomes:
                method_accuracy[p["prediction_method"]].append(p["was_accurate"])

            method_stats = {}
            for method, accuracies in method_accuracy.items():
                method_stats[method] = {
                    "accuracy": np.mean(accuracies),
                    "total_predictions": len(accuracies),
                    "accurate_count": sum(accuracies),
                }

            # Confidence calibration
            confidence_bins = defaultdict(list)
            for p in predictions_with_outcomes:
                bin_key = f"{int(p['confidence'] * 10) * 10}%-{int(p['confidence'] * 10) * 10 + 10}%"
                confidence_bins[bin_key].append(p["was_accurate"])

            calibration = {}
            for bin_key, accuracies in confidence_bins.items():
                calibration[bin_key] = {"accuracy": np.mean(accuracies), "count": len(accuracies)}

            accuracy_analysis = {
                "overall_accuracy": accurate_predictions / total_predictions,
                "total_predictions_analyzed": total_predictions,
                "accurate_predictions_count": accurate_predictions,
                "accuracy_by_method": method_stats,
                "confidence_calibration": calibration,
                "analysis_period_days": days_back,
                "analysis_timestamp": datetime.now().isoformat(),
            }

            return accuracy_analysis

        except Exception as e:
            logger.error(f"Error analyzing prediction accuracy for user {user_id}: {e}")
            return {}

    def update_prediction_accuracy(self, prediction_id: int, actual_query: str, was_helpful: bool = False) -> bool:
        """Update prediction accuracy based on actual user query.

        Args:
            prediction_id: ID of the prediction to update
            actual_query: The actual query the user made
            was_helpful: Whether the prediction was helpful to the user

        Returns:
            True if update was successful
        """
        try:
            # Calculate accuracy score
            accuracy_score = self._calculate_prediction_accuracy(prediction_id, actual_query)

            # Update prediction record
            update_query = """
                UPDATE query_predictions
                SET prediction_accuracy = %s, was_helpful = %s, verified_at = CURRENT_TIMESTAMP
                WHERE prediction_id = %s
            """

            execute_query(update_query, (accuracy_score, was_helpful, prediction_id))

            logger.info(f"Updated prediction accuracy for prediction {prediction_id}: {accuracy_score}")
            return True

        except Exception as e:
            logger.error(f"Error updating prediction accuracy: {e}")
            return False

    # Prediction methods
    def _predict_from_sequences(
        self, sequences: list[dict[str, Any]], current_context: str, current_embedding: np.ndarray
    ) -> list[dict[str, Any]]:
        """Predict next queries based on sequence patterns."""
        predictions = []

        for sequence in sequences:
            sequence_queries = sequence.get("sequence_queries", [])
            if len(sequence_queries) < 2:
                continue

            # Find most similar query in sequence to current context
            max_similarity = 0.0
            best_position = -1

            for i, query in enumerate(sequence_queries):
                # Note: We don't have embeddings in sequence_queries, so use content similarity
                query_embedding = self.model.encode([query["content"]])[0]
                similarity = self._cosine_similarity(current_embedding, query_embedding)

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_position = i

            # Predict next query in sequence
            if best_position >= 0 and best_position < len(sequence_queries) - 1:
                next_query = sequence_queries[best_position + 1]
                confidence = max_similarity * sequence.get("sequence_strength", 0.5)

                predictions.append(
                    {
                        "predicted_topic": next_query["content"][:200],
                        "confidence": float(confidence),
                        "prediction_method": "sequence_based",
                        "source_pattern": "question_sequence",
                        "pattern_strength": sequence.get("sequence_strength", 0.5),
                    }
                )

        return predictions

    def _predict_topic_evolution(
        self, evolutions: list[dict[str, Any]], current_embedding: np.ndarray, user_id: str
    ) -> list[dict[str, Any]]:
        """Predict topic evolution based on historical patterns."""
        predictions = []

        # Get recent query evolution
        recent_queries = self._get_recent_queries_with_embeddings(user_id, limit=5)
        if len(recent_queries) < 2:
            return predictions

        # Calculate current evolution trajectory
        current_trajectory = self._calculate_evolution_trajectory(recent_queries)

        for evolution in evolutions:
            evolution_type = evolution.get("evolution_type", "continuation")
            semantic_drift = evolution.get("semantic_drift", 0.0)

            # Predict continuation of current trajectory
            if evolution_type in ["refinement", "topic_shift"]:
                predicted_topic = self._extrapolate_topic_evolution(current_trajectory, evolution_type, semantic_drift)

                confidence = min(0.8, 1.0 - semantic_drift)  # Higher confidence for lower drift

                predictions.append(
                    {
                        "predicted_topic": predicted_topic,
                        "confidence": float(confidence),
                        "prediction_method": "topic_evolution",
                        "source_pattern": "topic_evolution",
                        "evolution_type": evolution_type,
                    }
                )

        return predictions

    def _predict_recurring_themes(
        self, themes: list[dict[str, Any]], current_context: str, current_embedding: np.ndarray
    ) -> list[dict[str, Any]]:
        """Predict based on recurring themes."""
        predictions = []

        for theme in themes:
            theme_embedding = theme.get("centroid_embedding", [])
            if not theme_embedding:
                continue

            # Calculate similarity to current context
            similarity = self._cosine_similarity(current_embedding, theme_embedding)

            if similarity > 0.5:  # Threshold for theme relevance
                # Predict user might return to this theme
                theme_signature = theme.get("theme_signature", "")
                frequency = theme.get("frequency", 1)
                coherence = theme.get("coherence_score", 0.5)

                confidence = similarity * coherence * min(1.0, frequency / 10.0)

                predictions.append(
                    {
                        "predicted_topic": f"Returning to theme: {theme_signature}",
                        "confidence": float(confidence),
                        "prediction_method": "recurring_pattern",
                        "source_pattern": "recurring_theme",
                        "theme_frequency": frequency,
                        "theme_coherence": coherence,
                    }
                )

        return predictions

    def _predict_context_shifts(self, user_id: str, current_embedding: np.ndarray) -> list[dict[str, Any]]:
        """Predict potential context shifts."""
        predictions = []

        # Get user's typical context shift patterns
        shift_patterns = self._get_context_shift_patterns(user_id)

        for pattern in shift_patterns:
            shift_type = pattern.get("shift_type", "subtopic_shift")
            avg_semantic_distance = pattern.get("avg_semantic_distance", 0.5)
            frequency = pattern.get("frequency", 1)

            # Predict likelihood of context shift
            if frequency > 1:  # Only predict if it's a recurring pattern
                confidence = min(0.7, frequency / 10.0 * (1.0 - avg_semantic_distance))

                predictions.append(
                    {
                        "predicted_topic": f"Potential {shift_type} to new area",
                        "confidence": float(confidence),
                        "prediction_method": "context_shift",
                        "source_pattern": "context_shift",
                        "shift_type": shift_type,
                    }
                )

        return predictions

    def _predict_from_intentions(
        self, intention_patterns: list[dict[str, Any]], current_context: str
    ) -> list[dict[str, Any]]:
        """Predict based on intention patterns."""
        predictions = []

        # Classify current context intention
        current_intention = self._classify_intention(current_context)

        for pattern_data in intention_patterns:
            transitions = pattern_data.get("common_transitions", [])

            for transition in transitions:
                if transition["from_intention"] == current_intention:
                    confidence = transition["frequency"] / 100.0  # Convert percentage to confidence

                    predictions.append(
                        {
                            "predicted_topic": f"Query with {transition['to_intention']} intention",
                            "confidence": float(confidence),
                            "prediction_method": "intention_based",
                            "source_pattern": "intention_transition",
                            "from_intention": transition["from_intention"],
                            "to_intention": transition["to_intention"],
                        }
                    )

        return predictions

    def _merge_and_rank_predictions(self, predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge similar predictions and rank by confidence."""
        if not predictions:
            return []

        # Simple deduplication based on similar predicted topics
        unique_predictions = []
        seen_topics = set()

        for pred in predictions:
            topic_key = pred["predicted_topic"][:50].lower()  # First 50 chars as key

            if topic_key not in seen_topics:
                unique_predictions.append(pred)
                seen_topics.add(topic_key)
            else:
                # Merge with existing prediction (boost confidence)
                for existing in unique_predictions:
                    existing_key = existing["predicted_topic"][:50].lower()
                    if existing_key == topic_key:
                        existing["confidence"] = min(1.0, existing["confidence"] + pred["confidence"] * 0.3)
                        break

        # Sort by confidence
        return sorted(unique_predictions, key=lambda x: x["confidence"], reverse=True)

    def _store_predictions(self, user_id: str, current_context: str, predictions: list[dict[str, Any]]) -> None:
        """Store predictions for accuracy tracking."""
        try:
            # Get current context message ID (if it exists)
            context_message_id = self._get_latest_message_id(user_id)

            for pred in predictions:
                predicted_embedding = self.model.encode([pred["predicted_topic"]])[0]

                query = """
                    INSERT INTO query_predictions (
                        user_id, current_context_message_id, predicted_query_topics,
                        prediction_embeddings, confidence_scores, prediction_method, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                execute_query(
                    query,
                    (
                        user_id,
                        context_message_id,
                        [pred["predicted_topic"]],
                        [predicted_embedding.tolist()],
                        [pred["confidence"]],
                        pred["prediction_method"],
                        json.dumps(pred),
                    ),
                )

        except Exception as e:
            logger.error(f"Error storing predictions: {e}")

    # Helper methods
    def _find_similar_historical_contexts(self, user_id: str, context: str, limit: int = 5) -> list[dict[str, Any]]:
        """Find similar historical contexts for the user."""
        try:
            context_embedding = self.model.encode([context])[0]

            # Get user's message embeddings
            query = """
                SELECT cm.message_id, cm.content, cm.embedding, cm.session_id, cm.timestamp
                FROM conversation_messages cm
                JOIN conversation_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.user_id = %s
                  AND cm.role = 'human'
                  AND cm.embedding IS NOT NULL
                ORDER BY cm.timestamp DESC
                LIMIT 100
            """

            results = execute_query(query, (user_id,))

            similarities = []
            for row in results:
                message_embedding = row[2] if isinstance(row[2], list) else self._parse_embedding(row[2])
                similarity = self._cosine_similarity(context_embedding, message_embedding)

                if similarity > 0.6:  # Threshold for similar context
                    similarities.append(
                        {
                            "message_id": row[0],
                            "content": row[1],
                            "similarity": float(similarity),
                            "session_id": row[3],
                            "timestamp": row[4],
                        }
                    )

            return sorted(similarities, key=lambda x: x["similarity"], reverse=True)[:limit]

        except Exception as e:
            logger.error(f"Error finding similar contexts: {e}")
            return []

    def _get_follow_up_queries(self, session_id: str, message_id: int, limit: int = 5) -> list[dict[str, Any]]:
        """Get follow-up queries after a specific message."""
        try:
            query = """
                SELECT message_id, content, timestamp, metadata
                FROM conversation_messages
                WHERE session_id = %s
                  AND message_id > %s
                  AND role = 'human'
                ORDER BY message_id ASC
                LIMIT %s
            """

            results = execute_query(query, (session_id, message_id, limit))

            return [
                {"message_id": row[0], "content": row[1], "timestamp": row[2], "metadata": row[3] or {}}
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting follow-up queries: {e}")
            return []

    def _extract_resolution_information(self, query: dict[str, Any]) -> dict[str, Any] | None:
        """Extract information that helped resolve a query."""
        # Simplified implementation - in practice, this would analyze
        # the conversation following the query to identify helpful information

        content = query["content"].lower()

        # Basic heuristics for resolution info type
        if any(word in content for word in ["error", "bug", "issue"]):
            info_type = "debugging_info"
        elif any(word in content for word in ["how", "implement", "create"]):
            info_type = "implementation_guide"
        elif any(word in content for word in ["what", "explain", "understand"]):
            info_type = "conceptual_explanation"
        else:
            info_type = "general_guidance"

        return {
            "type": info_type,
            "content": f"Information relevant to: {query['content'][:100]}",
            "success_rate": 0.7,  # Default success rate
        }

    def _calculate_relevance(self, context: str, info_content: str) -> float:
        """Calculate relevance score between context and information."""
        try:
            context_embedding = self.model.encode([context])[0]
            info_embedding = self.model.encode([info_content])[0]
            return float(self._cosine_similarity(context_embedding, info_embedding))
        except Exception:
            return 0.5  # Default medium relevance

    def _get_predictions_with_outcomes(self, user_id: str, days_back: int) -> list[dict[str, Any]]:
        """Get predictions with their actual outcomes."""
        try:
            since_date = (datetime.now() - timedelta(days=days_back)).isoformat()

            query = """
                SELECT prediction_id, predicted_query_topics, confidence_scores,
                       prediction_method, prediction_accuracy, was_helpful,
                       predicted_at, verified_at, metadata
                FROM query_predictions
                WHERE user_id = %s
                  AND predicted_at >= %s
                  AND prediction_accuracy IS NOT NULL
                ORDER BY predicted_at DESC
            """

            results = execute_query(query, (user_id, since_date))

            predictions = []
            for row in results:
                metadata = json.loads(row[8]) if row[8] else {}

                predictions.append(
                    {
                        "prediction_id": row[0],
                        "predicted_topics": row[1],
                        "confidence": row[2][0] if row[2] and len(row[2]) > 0 else 0.0,
                        "prediction_method": row[3],
                        "accuracy": row[4],
                        "was_accurate": row[4] > 0.5 if row[4] is not None else False,
                        "was_helpful": row[5],
                        "predicted_at": row[6],
                        "verified_at": row[7],
                        "metadata": metadata,
                    }
                )

            return predictions

        except Exception as e:
            logger.error(f"Error getting predictions with outcomes: {e}")
            return []

    def _calculate_prediction_accuracy(self, prediction_id: int, actual_query: str) -> float:
        """Calculate accuracy of a prediction against actual query."""
        try:
            # Get the original prediction
            query = """
                SELECT predicted_query_topics, prediction_embeddings
                FROM query_predictions
                WHERE prediction_id = %s
            """

            result = execute_query(query, (prediction_id,))
            if not result:
                return 0.0

            predicted_topics = result[0][0]
            prediction_embeddings = result[0][1]

            if not predicted_topics or not prediction_embeddings:
                return 0.0

            # Calculate semantic similarity between prediction and actual query
            actual_embedding = self.model.encode([actual_query])[0]

            max_similarity = 0.0
            for i, predicted_embedding in enumerate(prediction_embeddings):
                similarity = self._cosine_similarity(actual_embedding, predicted_embedding)
                max_similarity = max(max_similarity, similarity)

            return float(max_similarity)

        except Exception as e:
            logger.error(f"Error calculating prediction accuracy: {e}")
            return 0.0

    def _get_recent_queries_with_embeddings(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent queries with embeddings."""
        try:
            query = """
                SELECT cm.message_id, cm.content, cm.timestamp, cm.embedding
                FROM conversation_messages cm
                JOIN conversation_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.user_id = %s
                  AND cm.role = 'human'
                  AND cm.embedding IS NOT NULL
                ORDER BY cm.timestamp DESC
                LIMIT %s
            """

            results = execute_query(query, (user_id, limit))

            return [
                {
                    "message_id": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "embedding": row[3] if isinstance(row[3], list) else self._parse_embedding(row[3]),
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting recent queries: {e}")
            return []

    def _calculate_evolution_trajectory(self, queries: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate the current evolution trajectory."""
        if len(queries) < 2:
            return {}

        # Calculate direction of change over recent queries
        embeddings = [q["embedding"] for q in queries]

        # Simple trajectory: vector from first to last query
        trajectory_vector = np.array(embeddings[-1]) - np.array(embeddings[0])
        trajectory_magnitude = np.linalg.norm(trajectory_vector)

        return {
            "trajectory_vector": trajectory_vector.tolist(),
            "magnitude": float(trajectory_magnitude),
            "direction": "evolving" if trajectory_magnitude > 0.3 else "stable",
        }

    def _extrapolate_topic_evolution(self, trajectory: dict[str, Any], evolution_type: str, drift: float) -> str:
        """Extrapolate topic evolution based on trajectory."""
        # Simplified implementation - in practice, this would be more sophisticated

        if evolution_type == "refinement":
            return "More specific or detailed questions about the current topic"
        elif evolution_type == "topic_shift":
            return "Questions about related but distinct topics"
        elif evolution_type == "major_pivot":
            return "Questions about completely different topics"
        else:
            return "Continued exploration of current topic"

    def _get_context_shift_patterns(self, user_id: str) -> list[dict[str, Any]]:
        """Get user's context shift patterns from database."""
        try:
            query = """
                SELECT metadata
                FROM query_patterns
                WHERE user_id = %s
                  AND pattern_type = 'context_shifts'
                ORDER BY last_seen DESC
                LIMIT 10
            """

            results = execute_query(query, (user_id,))

            patterns = []
            for row in results:
                if row[0]:
                    metadata = json.loads(row[0])
                    patterns.append(metadata)

            # Aggregate patterns by shift type
            shift_aggregates = defaultdict(list)
            for pattern in patterns:
                if isinstance(pattern, list):
                    for shift in pattern:
                        shift_type = shift.get("shift_type", "unknown")
                        shift_aggregates[shift_type].append(shift)

            aggregated_patterns = []
            for shift_type, shifts in shift_aggregates.items():
                if len(shifts) > 1:  # Only include recurring patterns
                    avg_distance = np.mean([s.get("semantic_distance", 0.5) for s in shifts])
                    aggregated_patterns.append(
                        {
                            "shift_type": shift_type,
                            "frequency": len(shifts),
                            "avg_semantic_distance": float(avg_distance),
                        }
                    )

            return aggregated_patterns

        except Exception as e:
            logger.error(f"Error getting context shift patterns: {e}")
            return []

    def _classify_intention(self, content: str) -> str:
        """Classify the intention behind a query."""
        content_lower = content.lower()

        # Simple rule-based classification
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
        else:
            return "general"

    def _get_latest_message_id(self, user_id: str) -> int | None:
        """Get the latest message ID for a user."""
        try:
            query = """
                SELECT cm.message_id
                FROM conversation_messages cm
                JOIN conversation_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.user_id = %s
                  AND cm.role = 'human'
                ORDER BY cm.timestamp DESC
                LIMIT 1
            """

            result = execute_query(query, (user_id,))
            return result[0][0] if result else None

        except Exception as e:
            logger.error(f"Error getting latest message ID: {e}")
            return None

    def _parse_embedding(self, embedding_data: Any) -> list[float]:
        """Parse embedding from database format."""
        if isinstance(embedding_data, list):
            return embedding_data
        elif isinstance(embedding_data, str):
            try:
                return json.loads(embedding_data)
            except:
                return [0.0] * 384
        else:
            return [0.0] * 384

    def _cosine_similarity(self, embedding1: Any, embedding2: Any) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        except Exception:
            return 0.0

    def _generate_prediction_rationale(self, prediction: dict[str, Any]) -> str:
        """Generate human-readable rationale for a prediction."""
        method = prediction.get("prediction_method", "unknown")
        confidence = prediction.get("confidence", 0.0)

        if method == "sequence_based":
            return f"Based on your typical question sequences (confidence: {confidence:.1%})"
        elif method == "topic_evolution":
            return f"Following your usual topic evolution patterns (confidence: {confidence:.1%})"
        elif method == "recurring_pattern":
            return f"Based on recurring themes in your questions (confidence: {confidence:.1%})"
        elif method == "context_shift":
            return f"Predicting a context shift based on your patterns (confidence: {confidence:.1%})"
        elif method == "intention_based":
            return f"Based on typical intention transitions (confidence: {confidence:.1%})"
        else:
            return f"Based on pattern analysis (confidence: {confidence:.1%})"
