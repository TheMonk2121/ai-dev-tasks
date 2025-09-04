#!/usr/bin/env python3
"""
Query Vector Analysis System

Advanced vector analysis for query pattern recognition, clustering, and
knowledge graph construction for predictive query analysis.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import networkx as nx
import numpy as np
from sentence_transformers import SentenceTransformer

# Optional dependencies with fallbacks
try:
    import hdbscan

    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    hdbscan = None

try:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import silhouette_score

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    KMeans = None
    PCA = None
    silhouette_score = None

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.conversation_storage import ConversationStorage
from utils.database_resilience import execute_query, get_database_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryVectorAnalyzer:
    """Advanced vector analysis for query pattern recognition."""

    def __init__(
        self, conversation_storage: Optional[ConversationStorage] = None, model_name: str = "all-MiniLM-L6-v2"
    ):
        """Initialize the query vector analyzer.

        Args:
            conversation_storage: Storage instance for conversation data
            model_name: Name of the sentence transformer model to use
        """
        self.storage = conversation_storage or ConversationStorage()
        self.model = SentenceTransformer(model_name)
        self.db_manager = get_database_manager()

        # Configuration
        self.embedding_dim = 384
        self.similarity_threshold = 0.7
        self.min_cluster_size = 3

        # Check for optional dependencies
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Check and log availability of optional dependencies."""
        if not HDBSCAN_AVAILABLE:
            logger.warning("HDBSCAN not available. Will use fallback clustering methods.")
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Some analysis features will be limited.")

    def detect_query_clusters(
        self, user_id: str, min_cluster_size: Optional[int] = None, time_window_days: int = 90
    ) -> List[Dict[str, Any]]:
        """Detect clusters of semantically similar queries.

        Args:
            user_id: User identifier
            min_cluster_size: Minimum size for clusters (defaults to self.min_cluster_size)
            time_window_days: Days to look back for queries

        Returns:
            List of detected query clusters with metadata
        """
        try:
            min_cluster_size = min_cluster_size or self.min_cluster_size
            logger.info(f"Detecting query clusters for user {user_id} with min_cluster_size={min_cluster_size}")

            # Get user's query embeddings
            query_data = self._get_user_query_embeddings(user_id, time_window_days)
            if len(query_data) < min_cluster_size:
                logger.warning(f"Insufficient queries ({len(query_data)}) for clustering")
                return []

            embeddings = np.array([q["embedding"] for q in query_data])

            # Perform clustering
            cluster_labels = self._perform_clustering(embeddings, min_cluster_size)

            # Build cluster information
            clusters = self._build_cluster_info(query_data, cluster_labels)

            # Store clusters in database
            self._store_clusters(user_id, clusters)

            logger.info(f"Detected {len(clusters)} clusters for user {user_id}")
            return clusters

        except Exception as e:
            logger.error(f"Error detecting query clusters for user {user_id}: {e}")
            return []

    def analyze_query_evolution_vectors(self, user_id: str, time_window_days: int = 60) -> Dict[str, Any]:
        """Analyze how query vectors evolve over time.

        Args:
            user_id: User identifier
            time_window_days: Days to look back for analysis

        Returns:
            Dictionary containing evolution analysis results
        """
        try:
            logger.info(f"Analyzing query evolution vectors for user {user_id}")

            queries = self._get_chronological_queries(user_id, time_window_days)
            if len(queries) < 2:
                logger.warning(f"Insufficient queries ({len(queries)}) for evolution analysis")
                return {}

            evolution_analysis = {
                "trajectory_vectors": [],
                "semantic_drift": [],
                "topic_transitions": [],
                "complexity_evolution": [],
                "learning_progression": [],
                "analysis_metadata": {
                    "user_id": user_id,
                    "query_count": len(queries),
                    "time_span_days": (queries[-1]["timestamp"] - queries[0]["timestamp"]).days,
                    "analysis_timestamp": datetime.now().isoformat(),
                },
            }

            # Analyze consecutive query transitions
            for i in range(1, len(queries)):
                prev_query = queries[i - 1]
                curr_query = queries[i]

                # Calculate transition vector
                transition_vector = np.array(curr_query["embedding"]) - np.array(prev_query["embedding"])
                transition_magnitude = np.linalg.norm(transition_vector)

                evolution_analysis["trajectory_vectors"].append(
                    {
                        "from_query": prev_query["content"][:100],
                        "to_query": curr_query["content"][:100],
                        "from_message_id": prev_query["message_id"],
                        "to_message_id": curr_query["message_id"],
                        "transition_vector": transition_vector.tolist(),
                        "magnitude": float(transition_magnitude),
                        "timestamp": (
                            curr_query["timestamp"].isoformat()
                            if isinstance(curr_query["timestamp"], datetime)
                            else curr_query["timestamp"]
                        ),
                    }
                )

                # Calculate semantic drift
                cosine_sim = self._cosine_similarity(prev_query["embedding"], curr_query["embedding"])
                drift = 1 - cosine_sim

                evolution_analysis["semantic_drift"].append(
                    {
                        "similarity": float(cosine_sim),
                        "drift": float(drift),
                        "timestamp": (
                            curr_query["timestamp"].isoformat()
                            if isinstance(curr_query["timestamp"], datetime)
                            else curr_query["timestamp"]
                        ),
                        "time_gap_hours": self._calculate_time_gap_hours(
                            prev_query["timestamp"], curr_query["timestamp"]
                        ),
                    }
                )

                # Classify topic transition
                transition_type = self._classify_topic_transition(cosine_sim, transition_magnitude)
                evolution_analysis["topic_transitions"].append(
                    {
                        "transition_type": transition_type,
                        "similarity": float(cosine_sim),
                        "magnitude": float(transition_magnitude),
                        "timestamp": (
                            curr_query["timestamp"].isoformat()
                            if isinstance(curr_query["timestamp"], datetime)
                            else curr_query["timestamp"]
                        ),
                    }
                )

            # Analyze complexity evolution
            evolution_analysis["complexity_evolution"] = self._analyze_complexity_evolution(queries)

            # Analyze learning progression
            evolution_analysis["learning_progression"] = self._analyze_learning_progression(queries)

            return evolution_analysis

        except Exception as e:
            logger.error(f"Error analyzing query evolution for user {user_id}: {e}")
            return {}

    def build_query_similarity_graph(
        self, user_id: str, similarity_threshold: Optional[float] = None, time_window_days: int = 90
    ) -> nx.Graph:
        """Build graph of query similarities above threshold.

        Args:
            user_id: User identifier
            similarity_threshold: Minimum similarity for edges (defaults to self.similarity_threshold)
            time_window_days: Days to look back for queries

        Returns:
            NetworkX graph of query similarities
        """
        try:
            similarity_threshold = similarity_threshold or self.similarity_threshold
            logger.info(f"Building query similarity graph for user {user_id} with threshold={similarity_threshold}")

            queries = self._get_user_query_embeddings(user_id, time_window_days)
            if len(queries) < 2:
                logger.warning(f"Insufficient queries ({len(queries)}) for graph construction")
                return nx.Graph()

            G = nx.Graph()

            # Add nodes
            for query in queries:
                G.add_node(
                    query["message_id"],
                    content=query["content"],
                    timestamp=(
                        query["timestamp"].isoformat()
                        if isinstance(query["timestamp"], datetime)
                        else query["timestamp"]
                    ),
                    embedding=query["embedding"],
                    session_id=query.get("session_id"),
                )

            # Add similarity edges
            for i, query1 in enumerate(queries):
                for query2 in queries[i + 1 :]:
                    similarity = self._cosine_similarity(query1["embedding"], query2["embedding"])

                    if similarity >= similarity_threshold:
                        G.add_edge(
                            query1["message_id"],
                            query2["message_id"],
                            weight=float(similarity),
                            semantic_distance=float(1 - similarity),
                            time_diff_hours=self._calculate_time_gap_hours(query1["timestamp"], query2["timestamp"]),
                        )

            # Add graph-level metrics
            G.graph["user_id"] = user_id
            G.graph["node_count"] = G.number_of_nodes()
            G.graph["edge_count"] = G.number_of_edges()
            G.graph["density"] = nx.density(G)
            G.graph["created_at"] = datetime.now().isoformat()

            logger.info(f"Built similarity graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            return G

        except Exception as e:
            logger.error(f"Error building similarity graph for user {user_id}: {e}")
            return nx.Graph()

    def find_query_neighborhoods(self, user_id: str, target_query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find k most similar queries to a target query.

        Args:
            user_id: User identifier
            target_query: Query text to find neighbors for
            k: Number of neighbors to return

        Returns:
            List of similar queries with similarity scores
        """
        try:
            logger.info(f"Finding neighborhoods for query in user {user_id} context")

            # Generate embedding for target query
            target_embedding = self.model.encode([target_query])[0]

            # Get user's query embeddings
            queries = self._get_user_query_embeddings(user_id)
            if not queries:
                logger.warning(f"No queries found for user {user_id}")
                return []

            # Calculate similarities
            similarities = []
            for query in queries:
                similarity = self._cosine_similarity(target_embedding, query["embedding"])
                similarities.append(
                    {
                        "message_id": query["message_id"],
                        "content": query["content"],
                        "similarity": float(similarity),
                        "timestamp": (
                            query["timestamp"].isoformat()
                            if isinstance(query["timestamp"], datetime)
                            else query["timestamp"]
                        ),
                        "session_id": query.get("session_id"),
                    }
                )

            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:k]

        except Exception as e:
            logger.error(f"Error finding query neighborhoods for user {user_id}: {e}")
            return []

    def analyze_query_embedding_space(self, user_id: str, time_window_days: int = 90) -> Dict[str, Any]:
        """Analyze the structure of user's query embedding space.

        Args:
            user_id: User identifier
            time_window_days: Days to look back for analysis

        Returns:
            Dictionary containing embedding space analysis
        """
        try:
            logger.info(f"Analyzing query embedding space for user {user_id}")

            queries = self._get_user_query_embeddings(user_id, time_window_days)
            if len(queries) < 5:
                logger.warning(f"Insufficient queries ({len(queries)}) for embedding space analysis")
                return {}

            embeddings = np.array([q["embedding"] for q in queries])

            analysis = {
                "dimensionality_analysis": self._analyze_dimensionality(embeddings),
                "density_analysis": self._analyze_density(embeddings),
                "coherence_metrics": self._calculate_coherence_metrics(embeddings),
                "diversity_metrics": self._calculate_diversity_metrics(embeddings),
                "temporal_dynamics": self._analyze_temporal_dynamics(queries),
                "analysis_metadata": {
                    "user_id": user_id,
                    "query_count": len(queries),
                    "embedding_dimension": embeddings.shape[1],
                    "analysis_timestamp": datetime.now().isoformat(),
                },
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing embedding space for user {user_id}: {e}")
            return {}

    # Helper methods
    def _get_user_query_embeddings(self, user_id: str, time_window_days: int = 90) -> List[Dict[str, Any]]:
        """Get user's query embeddings from database."""
        try:
            since_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()

            query = """
                SELECT cm.message_id, cm.content, cm.timestamp, cm.embedding, cm.session_id
                FROM conversation_messages cm
                JOIN conversation_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.user_id = %s
                  AND cm.role = 'human'
                  AND cm.timestamp >= %s
                  AND cm.embedding IS NOT NULL
                ORDER BY cm.timestamp ASC
            """

            results = execute_query(query, (user_id, since_date))

            return [
                {
                    "message_id": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "embedding": row[3] if isinstance(row[3], list) else self._parse_embedding(row[3]),
                    "session_id": row[4],
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting user query embeddings: {e}")
            return []

    def _get_chronological_queries(self, user_id: str, time_window_days: int = 60) -> List[Dict[str, Any]]:
        """Get user queries in chronological order."""
        return self._get_user_query_embeddings(user_id, time_window_days)

    def _perform_clustering(self, embeddings: np.ndarray, min_cluster_size: int) -> np.ndarray:
        """Perform clustering on embeddings."""
        if HDBSCAN_AVAILABLE and len(embeddings) >= min_cluster_size:
            # Use HDBSCAN for density-based clustering
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size, metric="cosine", cluster_selection_epsilon=0.3
            )
            cluster_labels = clusterer.fit_predict(embeddings)
        elif SKLEARN_AVAILABLE and len(embeddings) >= min_cluster_size:
            # Fallback to KMeans
            n_clusters = min(max(2, len(embeddings) // min_cluster_size), 10)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
        else:
            # Simple similarity-based clustering as final fallback
            cluster_labels = self._simple_similarity_clustering(embeddings, min_cluster_size)

        return cluster_labels

    def _simple_similarity_clustering(self, embeddings: np.ndarray, min_cluster_size: int) -> np.ndarray:
        """Simple similarity-based clustering fallback."""
        cluster_labels = np.full(len(embeddings), -1)
        next_cluster_id = 0

        for i, embedding in enumerate(embeddings):
            if cluster_labels[i] != -1:
                continue

            # Find similar embeddings
            similar_indices = [i]
            for j, other_embedding in enumerate(embeddings[i + 1 :], i + 1):
                if cluster_labels[j] != -1:
                    continue

                similarity = self._cosine_similarity(embedding, other_embedding)
                if similarity > self.similarity_threshold:
                    similar_indices.append(j)

            # Create cluster if meets minimum size
            if len(similar_indices) >= min_cluster_size:
                for idx in similar_indices:
                    cluster_labels[idx] = next_cluster_id
                next_cluster_id += 1

        return cluster_labels

    def _build_cluster_info(self, query_data: List[Dict[str, Any]], cluster_labels: np.ndarray) -> List[Dict[str, Any]]:
        """Build cluster information from labels."""
        clusters = []
        unique_labels = set(cluster_labels)

        for cluster_id in unique_labels:
            if cluster_id == -1:  # Skip noise points
                continue

            cluster_queries = [query_data[i] for i, label in enumerate(cluster_labels) if label == cluster_id]

            if not cluster_queries:
                continue

            # Calculate cluster centroid
            cluster_embeddings = [q["embedding"] for q in cluster_queries]
            centroid = np.mean(cluster_embeddings, axis=0)

            # Calculate cluster metrics
            coherence = self._calculate_cluster_coherence(cluster_embeddings)
            time_span = self._calculate_time_span(cluster_queries)
            recurrence_freq = self._calculate_recurrence_frequency(cluster_queries)
            success_rate = self._estimate_success_rate(cluster_queries)

            cluster_info = {
                "cluster_id": int(cluster_id),
                "queries": [
                    {
                        "message_id": q["message_id"],
                        "content": q["content"][:200],  # Truncate for storage
                        "timestamp": (
                            q["timestamp"].isoformat() if isinstance(q["timestamp"], datetime) else q["timestamp"]
                        ),
                    }
                    for q in cluster_queries
                ],
                "centroid": centroid.tolist(),
                "size": len(cluster_queries),
                "coherence": float(coherence),
                "time_span_days": time_span,
                "recurring_frequency": float(recurrence_freq),
                "resolution_success_rate": float(success_rate),
                "cluster_signature": self._generate_cluster_signature(cluster_queries),
            }

            clusters.append(cluster_info)

        return clusters

    def _store_clusters(self, user_id: str, clusters: List[Dict[str, Any]]) -> None:
        """Store cluster information in database."""
        try:
            for cluster in clusters:
                message_ids = [q["message_id"] for q in cluster["queries"]]

                query = """
                    INSERT INTO query_clusters (
                        user_id, cluster_name, cluster_centroid, message_ids,
                        cluster_coherence, cluster_size, time_span_days,
                        recurring_frequency, resolution_success_rate, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """

                execute_query(
                    query,
                    (
                        user_id,
                        cluster["cluster_signature"],
                        cluster["centroid"],
                        message_ids,
                        cluster["coherence"],
                        cluster["size"],
                        cluster["time_span_days"],
                        cluster["recurring_frequency"],
                        cluster["resolution_success_rate"],
                        json.dumps(cluster),
                    ),
                )

        except Exception as e:
            logger.error(f"Error storing clusters: {e}")

    def _cosine_similarity(self, embedding1: Any, embedding2: Any) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        except Exception:
            return 0.0

    def _parse_embedding(self, embedding_data: Any) -> List[float]:
        """Parse embedding from database format."""
        if isinstance(embedding_data, list):
            return embedding_data
        elif isinstance(embedding_data, str):
            try:
                return json.loads(embedding_data)
            except:
                return [0.0] * self.embedding_dim
        else:
            return [0.0] * self.embedding_dim

    def _calculate_cluster_coherence(self, embeddings: List[List[float]]) -> float:
        """Calculate coherence score for a cluster."""
        if len(embeddings) < 2:
            return 1.0

        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = self._cosine_similarity(embeddings[i], embeddings[j])
                similarities.append(sim)

        return np.mean(similarities) if similarities else 0.0

    def _calculate_time_span(self, queries: List[Dict[str, Any]]) -> int:
        """Calculate time span in days for a cluster."""
        if len(queries) < 2:
            return 0

        timestamps = []
        for q in queries:
            if isinstance(q["timestamp"], datetime):
                timestamps.append(q["timestamp"])
            elif isinstance(q["timestamp"], str):
                try:
                    timestamps.append(datetime.fromisoformat(q["timestamp"].replace("Z", "+00:00")))
                except:
                    continue

        if len(timestamps) < 2:
            return 0

        return (max(timestamps) - min(timestamps)).days

    def _calculate_recurrence_frequency(self, queries: List[Dict[str, Any]]) -> float:
        """Calculate recurrence frequency for a cluster."""
        time_span = self._calculate_time_span(queries)
        if time_span == 0:
            return 0.0

        return len(queries) / max(1, time_span)

    def _estimate_success_rate(self, queries: List[Dict[str, Any]]) -> float:
        """Estimate success rate for queries in cluster (placeholder)."""
        # This would require more sophisticated analysis of follow-up queries
        # For now, return a baseline estimate
        return 0.7

    def _generate_cluster_signature(self, queries: List[Dict[str, Any]]) -> str:
        """Generate a signature for a cluster."""
        # Simple approach: combine first few words from queries
        words = []
        for q in queries[:3]:  # Use first 3 queries
            content_words = q["content"].lower().split()[:3]
            words.extend(content_words)

        return " ".join(words[:10])  # Max 10 words

    def _classify_topic_transition(self, similarity: float, magnitude: float) -> str:
        """Classify the type of topic transition."""
        if similarity > 0.8:
            return "refinement"
        elif similarity > 0.6:
            return "evolution"
        elif similarity > 0.4:
            return "shift"
        else:
            return "pivot"

    def _calculate_time_gap_hours(self, timestamp1: Any, timestamp2: Any) -> float:
        """Calculate time gap in hours between two timestamps."""
        try:
            if isinstance(timestamp1, str):
                timestamp1 = datetime.fromisoformat(timestamp1.replace("Z", "+00:00"))
            if isinstance(timestamp2, str):
                timestamp2 = datetime.fromisoformat(timestamp2.replace("Z", "+00:00"))

            return abs((timestamp2 - timestamp1).total_seconds()) / 3600.0
        except Exception:
            return 0.0

    def _analyze_complexity_evolution(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how query complexity evolves."""
        if len(queries) < 2:
            return {}

        # Simple complexity metric based on query length and vocabulary diversity
        complexities = []
        for query in queries:
            word_count = len(query["content"].split())
            unique_words = len(set(query["content"].lower().split()))
            complexity = word_count * (unique_words / max(1, word_count))  # Normalized diversity
            complexities.append(complexity)

        return {
            "complexity_trend": "increasing" if complexities[-1] > complexities[0] else "decreasing",
            "avg_complexity": np.mean(complexities),
            "complexity_variance": np.var(complexities),
            "complexity_progression": complexities,
        }

    def _analyze_learning_progression(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze learning progression in queries."""
        # Simplified analysis based on question types and specificity
        learning_indicators = []

        for query in queries:
            content = query["content"].lower()

            # Basic heuristics for learning progression
            score = 0.0
            if any(word in content for word in ["how", "what", "why"]):
                score += 0.3  # Basic questions
            if any(word in content for word in ["implement", "optimize", "best practice"]):
                score += 0.7  # Advanced application
            if any(word in content for word in ["error", "debug", "issue"]):
                score += 0.5  # Problem-solving

            learning_indicators.append(score)

        return {
            "learning_trend": "advancing" if learning_indicators[-1] > learning_indicators[0] else "stable",
            "avg_learning_level": np.mean(learning_indicators),
            "learning_progression": learning_indicators,
        }

    def _analyze_dimensionality(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """Analyze dimensionality characteristics of embeddings."""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available"}

        # PCA analysis
        pca = PCA()
        pca.fit(embeddings)

        # Find effective dimensionality (95% variance explained)
        cumsum_variance = np.cumsum(pca.explained_variance_ratio_)
        effective_dim = np.argmax(cumsum_variance >= 0.95) + 1

        return {
            "effective_dimensionality": int(effective_dim),
            "total_dimensionality": embeddings.shape[1],
            "variance_explained_95": float(cumsum_variance[effective_dim - 1]),
            "top_10_components_variance": pca.explained_variance_ratio_[:10].tolist(),
        }

    def _analyze_density(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """Analyze density characteristics of embedding space."""
        # Calculate pairwise distances
        distances = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                dist = 1 - self._cosine_similarity(embeddings[i], embeddings[j])
                distances.append(dist)

        return {
            "avg_distance": np.mean(distances),
            "distance_std": np.std(distances),
            "min_distance": np.min(distances),
            "max_distance": np.max(distances),
            "distance_distribution_quartiles": np.percentile(distances, [25, 50, 75]).tolist(),
        }

    def _calculate_coherence_metrics(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """Calculate coherence metrics for embedding space."""
        return {
            "overall_coherence": self._calculate_cluster_coherence([emb.tolist() for emb in embeddings]),
            "centroid_distance_variance": float(
                np.var([1 - self._cosine_similarity(emb, np.mean(embeddings, axis=0)) for emb in embeddings])
            ),
        }

    def _calculate_diversity_metrics(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """Calculate diversity metrics for embedding space."""
        # Calculate maximum distance between any two embeddings
        max_distance = 0.0
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                dist = 1 - self._cosine_similarity(embeddings[i], embeddings[j])
                max_distance = max(max_distance, dist)

        return {
            "max_semantic_distance": float(max_distance),
            "embedding_spread": float(
                np.mean([1 - self._cosine_similarity(emb, np.mean(embeddings, axis=0)) for emb in embeddings])
            ),
        }

    def _analyze_temporal_dynamics(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal dynamics of embedding evolution."""
        if len(queries) < 3:
            return {}

        # Calculate change velocities between consecutive queries
        velocities = []
        for i in range(1, len(queries)):
            prev_emb = np.array(queries[i - 1]["embedding"])
            curr_emb = np.array(queries[i]["embedding"])

            time_gap = self._calculate_time_gap_hours(queries[i - 1]["timestamp"], queries[i]["timestamp"])
            if time_gap > 0:
                velocity = np.linalg.norm(curr_emb - prev_emb) / time_gap
                velocities.append(velocity)

        return {
            "avg_change_velocity": np.mean(velocities) if velocities else 0.0,
            "velocity_trend": "accelerating" if len(velocities) > 1 and velocities[-1] > velocities[0] else "stable",
            "velocity_variance": np.var(velocities) if velocities else 0.0,
        }
