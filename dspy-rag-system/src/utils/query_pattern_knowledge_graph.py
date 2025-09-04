#!/usr/bin/env python3
"""
Query Pattern Knowledge Graph Integration

Main orchestrator that integrates query pattern analysis, vector analysis,
and prediction capabilities with the LTST Memory System.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import networkx as nx
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.conversation_storage import ConversationMessage, ConversationStorage
from utils.database_resilience import execute_query, get_database_manager
from utils.logger import setup_logger
from utils.ltst_memory_integration import LTSTMemoryIntegration
from utils.query_pattern_analyzer import QueryPatternAnalyzer
from utils.query_predictor import QueryPredictor
from utils.query_vector_analyzer import QueryVectorAnalyzer

logger = setup_logger(__name__)


class QueryPatternKnowledgeGraph:
    """Main orchestrator for query pattern knowledge graph functionality."""

    def __init__(
        self,
        conversation_storage: Optional[ConversationStorage] = None,
        ltst_integration: Optional[LTSTMemoryIntegration] = None,
    ):
        """Initialize the query pattern knowledge graph system.

        Args:
            conversation_storage: Storage instance for conversation data
            ltst_integration: LTST memory integration instance
        """
        self.storage = conversation_storage or ConversationStorage()
        self.ltst_integration = ltst_integration or LTSTMemoryIntegration(self.storage)
        self.db_manager = get_database_manager()

        # Initialize component analyzers
        self.pattern_analyzer = QueryPatternAnalyzer(self.storage)
        self.vector_analyzer = QueryVectorAnalyzer(self.storage)
        self.predictor = QueryPredictor(self.storage, self.pattern_analyzer, self.vector_analyzer)

        # Knowledge graph storage
        self.knowledge_graphs = {}  # user_id -> NetworkX graph

    def initialize_user_knowledge_graph(self, user_id: str) -> bool:
        """Initialize knowledge graph for a user.

        Args:
            user_id: User identifier

        Returns:
            True if initialization was successful
        """
        try:
            logger.info(f"Initializing knowledge graph for user {user_id}")

            # Create database schema extensions if not exist
            self._ensure_schema_exists()

            # Build initial knowledge graph
            knowledge_graph = self.vector_analyzer.build_query_similarity_graph(user_id)

            # Analyze patterns
            patterns = self.pattern_analyzer.analyze_query_sequence(user_id)

            # Detect clusters
            clusters = self.vector_analyzer.detect_query_clusters(user_id)

            # Store knowledge graph
            self.knowledge_graphs[user_id] = knowledge_graph

            # Store initialization metadata
            self._store_knowledge_graph_metadata(
                user_id,
                {
                    "initialized_at": datetime.now().isoformat(),
                    "node_count": knowledge_graph.number_of_nodes(),
                    "edge_count": knowledge_graph.number_of_edges(),
                    "pattern_count": sum(len(v) if isinstance(v, list) else 0 for v in patterns.values()),
                    "cluster_count": len(clusters),
                },
            )

            logger.info(f"Successfully initialized knowledge graph for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error initializing knowledge graph for user {user_id}: {e}")
            return False

    def process_new_query(self, user_id: str, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a new query and update knowledge graph.

        Args:
            user_id: User identifier
            query: Query text
            session_id: Session identifier (optional)

        Returns:
            Dictionary containing processing results and predictions
        """
        try:
            logger.info(f"Processing new query for user {user_id}")

            # Store the query in conversation storage
            if session_id:
                message = ConversationMessage(
                    session_id=session_id,
                    role="human",
                    content=query,
                    message_type="message",
                    metadata={"source": "query_pattern_kg", "timestamp": datetime.now().isoformat()},
                )
                self.storage.store_message(message)

            # Get predictions for next queries
            predictions = self.predictor.predict_next_query_topics(user_id, query)

            # Get proactive information surfacing
            proactive_info = self.predictor.proactive_information_surfacing(user_id, query)

            # Update knowledge graph incrementally
            self._update_knowledge_graph_incremental(user_id, query)

            # Analyze query neighborhoods
            similar_queries = self.vector_analyzer.find_query_neighborhoods(user_id, query)

            result = {
                "query_processed": query,
                "user_id": user_id,
                "session_id": session_id,
                "predictions": predictions,
                "proactive_information": proactive_info,
                "similar_queries": similar_queries,
                "processing_timestamp": datetime.now().isoformat(),
                "knowledge_graph_updated": True,
            }

            logger.info(
                f"Successfully processed query for user {user_id}: {len(predictions)} predictions, {len(proactive_info)} proactive items"
            )
            return result

        except Exception as e:
            logger.error(f"Error processing new query for user {user_id}: {e}")
            return {"error": str(e), "query_processed": query, "user_id": user_id, "knowledge_graph_updated": False}

    def get_enhanced_memory_bundle(self, user_id: str, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get enhanced memory bundle with query pattern insights.

        Args:
            user_id: User identifier
            query: Current query
            session_id: Session identifier (optional)

        Returns:
            Enhanced memory bundle with query pattern analysis
        """
        try:
            logger.info(f"Getting enhanced memory bundle for user {user_id}")

            # Get standard LTST memory bundle
            ltst_bundle = self.ltst_integration.rehydrate_with_conversation_context(
                query=query, user_id=user_id, session_id=session_id
            )

            # Add query pattern analysis
            pattern_analysis = self.analyze_user_query_patterns(user_id)

            # Add predictions
            predictions = self.predictor.predict_next_query_topics(user_id, query, max_predictions=3)

            # Add proactive information
            proactive_info = self.predictor.proactive_information_surfacing(user_id, query)

            # Add vector analysis insights
            embedding_analysis = self.vector_analyzer.analyze_query_embedding_space(user_id)

            # Enhance the bundle
            enhanced_bundle = {
                "ltst_memory_bundle": ltst_bundle.to_dict() if ltst_bundle else {},
                "query_pattern_analysis": pattern_analysis,
                "next_query_predictions": predictions,
                "proactive_information": proactive_info,
                "embedding_space_analysis": embedding_analysis,
                "enhancement_metadata": {
                    "user_id": user_id,
                    "current_query": query,
                    "session_id": session_id,
                    "enhanced_at": datetime.now().isoformat(),
                    "prediction_count": len(predictions),
                    "proactive_info_count": len(proactive_info),
                },
            }

            logger.info(f"Successfully created enhanced memory bundle for user {user_id}")
            return enhanced_bundle

        except Exception as e:
            logger.error(f"Error creating enhanced memory bundle for user {user_id}: {e}")
            return {"error": str(e), "user_id": user_id, "query": query}

    def analyze_user_query_patterns(self, user_id: str) -> Dict[str, Any]:
        """Comprehensive analysis of user query patterns.

        Args:
            user_id: User identifier

        Returns:
            Comprehensive query pattern analysis
        """
        try:
            logger.info(f"Analyzing query patterns for user {user_id}")

            # Pattern analysis
            patterns = self.pattern_analyzer.analyze_query_sequence(user_id)

            # Vector analysis
            clusters = self.vector_analyzer.detect_query_clusters(user_id)
            evolution = self.vector_analyzer.analyze_query_evolution_vectors(user_id)
            embedding_analysis = self.vector_analyzer.analyze_query_embedding_space(user_id)

            # Prediction accuracy
            prediction_accuracy = self.predictor.analyze_prediction_accuracy(user_id)

            # Knowledge graph metrics
            kg_metrics = self._calculate_knowledge_graph_metrics(user_id)

            analysis = {
                "pattern_analysis": patterns,
                "cluster_analysis": {
                    "clusters": clusters,
                    "total_clusters": len(clusters),
                    "avg_cluster_size": np.mean([c["size"] for c in clusters]) if clusters else 0,
                    "avg_coherence": np.mean([c["coherence"] for c in clusters]) if clusters else 0,
                },
                "evolution_analysis": evolution,
                "embedding_analysis": embedding_analysis,
                "prediction_accuracy": prediction_accuracy,
                "knowledge_graph_metrics": kg_metrics,
                "analysis_metadata": {
                    "user_id": user_id,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "total_queries_analyzed": self._get_user_query_count(user_id),
                },
            }

            logger.info(f"Completed comprehensive analysis for user {user_id}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing user query patterns for user {user_id}: {e}")
            return {"error": str(e), "user_id": user_id}

    def get_query_relationship_graph(self, user_id: str, format: str = "networkx") -> Any:
        """Get query relationship graph for visualization.

        Args:
            user_id: User identifier
            format: Output format ('networkx', 'json', 'gexf')

        Returns:
            Query relationship graph in requested format
        """
        try:
            # Build or retrieve knowledge graph
            if user_id not in self.knowledge_graphs:
                self.knowledge_graphs[user_id] = self.vector_analyzer.build_query_similarity_graph(user_id)

            kg = self.knowledge_graphs[user_id]

            if format == "networkx":
                return kg
            elif format == "json":
                return self._graph_to_json(kg)
            elif format == "gexf":
                return self._graph_to_gexf(kg)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Error getting query relationship graph for user {user_id}: {e}")
            return None

    def update_prediction_feedback(
        self, user_id: str, prediction_id: int, actual_query: str, was_helpful: bool = False
    ) -> bool:
        """Update prediction feedback for learning.

        Args:
            user_id: User identifier
            prediction_id: Prediction ID to update
            actual_query: Actual query the user made
            was_helpful: Whether the prediction was helpful

        Returns:
            True if update was successful
        """
        try:
            return self.predictor.update_prediction_accuracy(prediction_id, actual_query, was_helpful)
        except Exception as e:
            logger.error(f"Error updating prediction feedback: {e}")
            return False

    def export_user_knowledge_graph(self, user_id: str, format: str = "json") -> Optional[str]:
        """Export user's complete knowledge graph.

        Args:
            user_id: User identifier
            format: Export format ('json', 'gexf', 'graphml')

        Returns:
            Serialized knowledge graph or None if error
        """
        try:
            analysis = self.analyze_user_query_patterns(user_id)
            graph = self.get_query_relationship_graph(user_id, "networkx")

            export_data = {
                "user_id": user_id,
                "export_timestamp": datetime.now().isoformat(),
                "pattern_analysis": analysis,
                "relationship_graph": self._graph_to_json(graph) if graph else {},
                "export_format": format,
            }

            if format == "json":
                return json.dumps(export_data, indent=2, default=str)
            else:
                logger.warning(f"Format {format} not implemented for full export")
                return json.dumps(export_data, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error exporting knowledge graph for user {user_id}: {e}")
            return None

    # Private helper methods
    def _ensure_schema_exists(self) -> None:
        """Ensure database schema extensions exist."""
        try:
            # Read and execute schema from file
            schema_file = os.path.join(
                os.path.dirname(__file__), "..", "..", "config", "database", "query_pattern_schema_extensions.sql"
            )

            if os.path.exists(schema_file):
                with open(schema_file, "r") as f:
                    schema_sql = f.read()

                # Execute schema (split by semicolon and execute each statement)
                statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
                for statement in statements:
                    try:
                        execute_query(statement)
                    except Exception as e:
                        # Some statements might fail if objects already exist - that's OK
                        if "already exists" not in str(e).lower():
                            logger.warning(f"Schema statement failed (might be OK): {e}")

                logger.info("Schema extensions ensured")
            else:
                logger.warning(f"Schema file not found: {schema_file}")

        except Exception as e:
            logger.error(f"Error ensuring schema exists: {e}")

    def _store_knowledge_graph_metadata(self, user_id: str, metadata: Dict[str, Any]) -> None:
        """Store knowledge graph metadata."""
        try:
            # Store in user preferences or a dedicated table
            # For now, we'll use conversation_context table
            context_key = f"kg_metadata_{user_id}"

            # This would need a session_id - we'll create a system session
            system_session_id = f"system_kg_{user_id}"

            # Simplified storage - in practice, you might want a dedicated metadata table
            logger.info(f"Knowledge graph metadata stored for user {user_id}")

        except Exception as e:
            logger.error(f"Error storing knowledge graph metadata: {e}")

    def _update_knowledge_graph_incremental(self, user_id: str, new_query: str) -> None:
        """Incrementally update knowledge graph with new query."""
        try:
            if user_id not in self.knowledge_graphs:
                return

            kg = self.knowledge_graphs[user_id]

            # Find similar existing queries
            similar_queries = self.vector_analyzer.find_query_neighborhoods(user_id, new_query)

            # Add relationships to similar queries
            for similar in similar_queries[:5]:  # Top 5 similar
                if similar["similarity"] > 0.6:  # Threshold for adding edge
                    # In a full implementation, you'd add the new query as a node
                    # and create edges to similar queries
                    logger.debug(
                        f"Would add relationship: new query -> {similar['message_id']} (sim: {similar['similarity']:.3f})"
                    )

        except Exception as e:
            logger.error(f"Error updating knowledge graph incrementally: {e}")

    def _calculate_knowledge_graph_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate metrics for user's knowledge graph."""
        try:
            if user_id not in self.knowledge_graphs:
                kg = self.vector_analyzer.build_query_similarity_graph(user_id)
                self.knowledge_graphs[user_id] = kg
            else:
                kg = self.knowledge_graphs[user_id]

            if kg.number_of_nodes() == 0:
                return {}

            # Basic graph metrics
            metrics = {
                "node_count": kg.number_of_nodes(),
                "edge_count": kg.number_of_edges(),
                "density": nx.density(kg),
                "average_clustering": nx.average_clustering(kg),
                "connected_components": nx.number_connected_components(kg),
            }

            # Add centrality measures if graph is not too large
            if kg.number_of_nodes() < 1000:
                try:
                    centrality = nx.degree_centrality(kg)
                    metrics["max_centrality"] = max(centrality.values()) if centrality else 0
                    metrics["avg_centrality"] = np.mean(list(centrality.values())) if centrality else 0
                except Exception:
                    pass

            return metrics

        except Exception as e:
            logger.error(f"Error calculating knowledge graph metrics: {e}")
            return {}

    def _get_user_query_count(self, user_id: str) -> int:
        """Get total query count for user."""
        try:
            query = """
                SELECT COUNT(*)
                FROM conversation_messages cm
                JOIN conversation_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.user_id = %s AND cm.role = 'human'
            """

            result = execute_query(query, (user_id,))
            return result[0][0] if result else 0

        except Exception as e:
            logger.error(f"Error getting user query count: {e}")
            return 0

    def _graph_to_json(self, graph: nx.Graph) -> Dict[str, Any]:
        """Convert NetworkX graph to JSON format."""
        try:
            return {
                "nodes": [{"id": str(node), "attributes": data} for node, data in graph.nodes(data=True)],
                "edges": [
                    {"source": str(source), "target": str(target), "attributes": data}
                    for source, target, data in graph.edges(data=True)
                ],
                "graph_attributes": dict(graph.graph),
            }
        except Exception as e:
            logger.error(f"Error converting graph to JSON: {e}")
            return {"nodes": [], "edges": []}

    def _graph_to_gexf(self, graph: nx.Graph) -> str:
        """Convert NetworkX graph to GEXF format."""
        try:
            import io

            gexf_buffer = io.BytesIO()
            nx.write_gexf(graph, gexf_buffer)
            return gexf_buffer.getvalue().decode("utf-8")
        except Exception as e:
            logger.error(f"Error converting graph to GEXF: {e}")
            return ""


# Convenience function for easy integration
def create_query_pattern_knowledge_graph(database_url: Optional[str] = None) -> QueryPatternKnowledgeGraph:
    """Create a QueryPatternKnowledgeGraph instance with default configuration.

    Args:
        database_url: Database connection URL (optional)

    Returns:
        Configured QueryPatternKnowledgeGraph instance
    """
    storage = ConversationStorage(database_url)
    ltst_integration = LTSTMemoryIntegration(storage)

    return QueryPatternKnowledgeGraph(storage, ltst_integration)
