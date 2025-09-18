#!/usr/bin/env python3
"""
Atlas Graph Storage System
Graph-backed storage that preserves connections between conversations, decisions, code, docs, and backlog
"""

import hashlib
import json
import os

# Add project paths
import sys
import time
from datetime import datetime, timedelta
from typing import Any, cast

import numpy as np
import psycopg
from psycopg.rows import dict_row

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from sentence_transformers import SentenceTransformer

# Type alias for database cursor
Cursor = Any


class AtlasGraphStorage:
    """Graph-backed storage system that preserves connections between all knowledge layers."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.embedder: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim: int = 384

    def store_conversation_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        related_nodes: list[str] | None = None,
    ) -> str:
        """Store a conversation turn as a graph node with connections."""
        turn_id = f"conv_{session_id}_{int(time.time())}"

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # Create conversation node
                embedding = self.get_embedding(content)
                metadata = metadata or {}
                metadata.update({"role": role, "session_id": session_id, "turn_id": turn_id})

                _ = cur.execute(
                    """
                    INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding,
                        updated_at = CURRENT_TIMESTAMP
                """,
                    (
                        turn_id,
                        "conversation",
                        f"{role}: {content[:100]}...",
                        content,
                        json.dumps(metadata),
                        embedding.tolist(),
                        datetime.now() + timedelta(hours=48),
                    ),
                )

                # Create connections to related nodes
                if related_nodes:
                    for related_node in related_nodes:
                        self._create_edge(
                            cur, turn_id, related_node, "mentions", f"Conversation mentions {related_node}"
                        )

                # Extract decisions and create decision nodes
                decisions = self._extract_decisions(content)
                for decision in decisions:
                    decision_id = f"decision_{turn_id}_{hashlib.md5(decision.encode()).hexdigest()[:8]}"
                    self._create_decision_node(cur, decision_id, decision, turn_id, session_id)
                    self._create_edge(cur, turn_id, decision_id, "decides", f"Conversation decides: {decision[:100]}")

                # Extract suggestions and create suggestion nodes
                suggestions = self._extract_suggestions(content)
                for suggestion in suggestions:
                    suggestion_id = f"suggestion_{turn_id}_{hashlib.md5(suggestion.encode()).hexdigest()[:8]}"
                    self._create_suggestion_node(cur, suggestion_id, suggestion, turn_id, session_id)
                    self._create_edge(
                        cur, turn_id, suggestion_id, "suggests", f"Conversation suggests: {suggestion[:100]}"
                    )

                conn.commit()
                return turn_id

    def _create_decision_node(
        self, cur: Cursor, decision_id: str, decision: str, source_turn_id: str, session_id: str
    ) -> None:
        """Create a decision node with proper metadata."""
        embedding = self.get_embedding(decision)
        metadata = {
            "source_turn_id": source_turn_id,
            "session_id": session_id,
            "decision_type": "conversation_decision",
        }

        cur.execute(
            """
            INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (node_id) DO UPDATE SET
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding,
                updated_at = CURRENT_TIMESTAMP
        """,
            (
                decision_id,
                "decision",
                f"Decision: {decision[:100]}...",
                decision,
                json.dumps(metadata),
                embedding.tolist(),
                datetime.now() + timedelta(hours=48),
            ),
        )

    def _create_suggestion_node(
        self, cur: Cursor, suggestion_id: str, suggestion: str, source_turn_id: str, session_id: str
    ) -> None:
        """Create a suggestion node with proper metadata."""
        embedding = self.get_embedding(suggestion)
        metadata = {
            "source_turn_id": source_turn_id,
            "session_id": session_id,
            "suggestion_type": "conversation_suggestion",
        }

        cur.execute(
            """
            INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (node_id) DO UPDATE SET
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding,
                updated_at = CURRENT_TIMESTAMP
        """,
            (
                suggestion_id,
                "suggestion",
                f"Suggestion: {suggestion[:100]}...",
                suggestion,
                json.dumps(metadata),
                embedding.tolist(),
                datetime.now() + timedelta(hours=48),
            ),
        )

    def _create_edge(self, cur: Cursor, source_id: str, target_id: str, edge_type: str, evidence: str) -> None:
        """Create a typed edge between nodes."""
        cur.execute(
            """
            INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (source_node_id, target_node_id, edge_type) DO UPDATE SET
                evidence = EXCLUDED.evidence,
                weight = atlas_edge.weight + 0.1
        """,
            (source_id, target_id, edge_type, evidence),
        )

    def _extract_decisions(self, content: str) -> list[str]:
        """Extract decisions from conversation content."""
        decisions = []
        # Simple pattern matching for decisions
        decision_patterns = [
            r"we should (.+?)(?:\.|$)",
            r"let's (.+?)(?:\.|$)",
            r"i'll (.+?)(?:\.|$)",
            r"we'll (.+?)(?:\.|$)",
            r"decision: (.+?)(?:\.|$)",
            r"decided to (.+?)(?:\.|$)",
        ]

        import re

        for pattern in decision_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            decisions.extend(matches)

        return decisions

    def _extract_suggestions(self, content: str) -> list[str]:
        """Extract suggestions from conversation content."""
        suggestions = []
        # Simple pattern matching for suggestions
        suggestion_patterns = [
            r"you should (.+?)(?:\.|$)",
            r"try (.+?)(?:\.|$)",
            r"consider (.+?)(?:\.|$)",
            r"suggest (.+?)(?:\.|$)",
            r"recommend (.+?)(?:\.|$)",
            r"maybe (.+?)(?:\.|$)",
        ]

        import re

        for pattern in suggestion_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            suggestions.extend(matches)

        return suggestions

    def get_embedding(self, text: str) -> np.ndarray[Any, Any]:
        """Get embedding for text."""
        embedding = self.embedder.encode(text)
        return cast(np.ndarray[Any, Any], np.array(embedding))

    def get_conversation_graph(self, session_id: str) -> dict[str, Any]:
        """Get the conversation graph for a session."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get all nodes for this session
                _ = cur.execute(
                    """
                    SELECT n.*, e.edge_type, e.target_node_id, e.evidence
                    FROM atlas_node n
                    LEFT JOIN atlas_edge e ON n.node_id = e.source_node_id
                    WHERE n.metadata->>'session_id' = %s
                    ORDER BY n.created_at
                """,
                    (session_id,),
                )

                nodes = {}
                edges = []

                for row in cur.fetchall():
                    node_id: str = str(row["node_id"])
                    if node_id not in nodes:
                        nodes[node_id] = {
                            "id": node_id,
                            "type": str(row["node_type"]),
                            "title": str(row["title"]),
                            "content": str(row["content"]),
                            "metadata": cast(dict[str, Any], row["metadata"]) if row["metadata"] else {},
                            "created_at": str(cast(datetime, row["created_at"]).isoformat()),
                        }

                    if row["edge_type"]:
                        edges.append(
                            {
                                "source": node_id,
                                "target": str(row["target_node_id"]),
                                "type": str(row["edge_type"]),
                                "evidence": str(row["evidence"]),
                            }
                        )

                return {"nodes": list(nodes.values()), "edges": edges, "session_id": session_id}

    def search_related_conversations(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search for related conversations using graph traversal."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query_embedding = self.get_embedding(query)

                # Search for similar nodes
                _ = cur.execute(
                    """
                    SELECT n.*, 
                           (n.embedding <=> %s::vector) as distance
                    FROM atlas_node n
                    WHERE n.node_type = 'conversation'
                    ORDER BY n.embedding <=> %s::vector
                    LIMIT %s
                """,
                    (query_embedding.tolist(), query_embedding.tolist(), limit),
                )

                results = []
                for row in cur.fetchall():
                    results.append(
                        {
                            "node_id": str(row["node_id"]),
                            "title": str(row["title"]),
                            "content": str(row["content"]),
                            "metadata": cast(dict[str, Any], row["metadata"]) if row["metadata"] else {},
                            "distance": float(row["distance"]),
                            "created_at": str(cast(datetime, row["created_at"]).isoformat()),
                        }
                    )

                return results


def main() -> None:
    """Test the Atlas graph storage system."""
    storage = AtlasGraphStorage()

    # Create related nodes first
    with psycopg.connect(storage.dsn) as conn:
        with conn.cursor() as cur:
            # Create atlas_system node
            _ = cur.execute(
                """
                INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (node_id) DO NOTHING
            """,
                (
                    "atlas_system",
                    "system",
                    "Atlas Graph Storage System",
                    "Graph-backed storage system for preserving connections between conversations, decisions, and context",
                    json.dumps({"system_type": "atlas"}),
                    storage.get_embedding("Atlas Graph Storage System").tolist(),
                    datetime.now() + timedelta(days=30),
                ),
            )

            # Create graph_storage node
            _ = cur.execute(
                """
                INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (node_id) DO NOTHING
            """,
                (
                    "graph_storage",
                    "concept",
                    "Graph Storage",
                    "Storage system that preserves connections and relationships between data",
                    json.dumps({"concept_type": "storage"}),
                    storage.get_embedding("Graph Storage").tolist(),
                    datetime.now() + timedelta(days=30),
                ),
            )

            conn.commit()

    # Test storing a conversation turn
    session_id = "test_session_123"
    turn_id = storage.store_conversation_turn(
        session_id=session_id,
        role="user",
        content="I think we should implement the Atlas graph storage system. It would preserve connections between conversations and decisions much better than the current vector-only approach.",
        metadata={"test": True},
        related_nodes=["atlas_system", "graph_storage"],
    )

    print(f"✅ Stored conversation turn: {turn_id}")

    # Test retrieving the conversation graph
    graph = storage.get_conversation_graph(session_id)
    print(f"✅ Retrieved graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")

    # Test searching related conversations
    results = storage.search_related_conversations("graph storage connections", limit=5)
    print(f"✅ Found {len(results)} related conversations")

    print("🎯 Atlas graph storage system is working!")


if __name__ == "__main__":
    main()
