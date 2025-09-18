#!/usr/bin/env python3
"""
Atlas Simple Extractor
Simple extraction of: your queries, my replies, and connecting vector space
Following your established chunking/embedding guidelines
"""

import json
import os

# Add project paths
import sys
from typing import Any, cast

import numpy as np
import psycopg
from psycopg.rows import dict_row

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from sentence_transformers import SentenceTransformer


class AtlasSimpleExtractor:
    """Simple extractor for query-reply relationships."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

        # Use your established configuration from the codebase
        self.embedder: SentenceTransformer = SentenceTransformer("BAAI/bge-large-en-v1.5")
        self.embedding_dim: int = 1024

        # Your chunking guidelines (from src/config/models.py)
        self.chunk_size: int = 450  # Default from RAG config
        self.overlap_ratio: float = 0.10  # Default from RAG config

    def extract_queries_and_replies(self, session_id: str) -> dict[str, Any]:
        """Extract your queries and my replies with connecting vector space."""

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get all conversation turns
                _ = cur.execute(
                    """
                    SELECT node_id, content, metadata, created_at
                    FROM atlas_node 
                    WHERE metadata->>'session_id' = %s 
                    AND node_type = 'conversation'
                    ORDER BY created_at
                """,
                    (session_id,),
                )

                turns = cur.fetchall()

                # Separate queries and replies
                queries = []
                replies = []

                for turn in turns:
                    metadata = (
                        cast(
                            dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]],
                            json.loads(cast(str, turn["metadata"])),
                        )
                        if turn["metadata"]
                        else {}
                    )
                    role = metadata.get("role", "unknown")

                    if role == "user":
                        queries.append(
                            {
                                "id": turn["node_id"],
                                "content": turn["content"],
                                "created_at": turn["created_at"],
                                "embedding": cast(list[float], self.embedder.encode(turn["content"]).tolist()),
                            }
                        )
                    elif role == "assistant":
                        replies.append(
                            {
                                "id": turn["node_id"],
                                "content": turn["content"],
                                "created_at": turn["created_at"],
                                "embedding": cast(list[float], self.embedder.encode(turn["content"]).tolist()),
                            }
                        )

                # Create connections between queries and replies
                connections = self._create_connections(queries, replies)

                return {
                    "session_id": session_id,
                    "queries": queries,
                    "replies": replies,
                    "connections": connections,
                    "total_queries": len(queries),
                    "total_replies": len(replies),
                    "total_connections": len(connections),
                }

    def _create_connections(
        self,
        queries: list[dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]],
        replies: list[dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]],
    ) -> list[dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]]:
        """Create connections between queries and replies."""
        connections = []

        # Simple pairing: each query connects to the next reply
        for i in range(min(len(queries), len(replies))):
            query = queries[i]
            reply = replies[i]

            # Calculate connection strength (cosine similarity)
            query_emb = cast(list[float], query["embedding"])
            reply_emb = cast(list[float], reply["embedding"])
            connection_strength = self._cosine_similarity(query_emb, reply_emb)

            connections.append(
                {
                    "query_id": cast(str, query["id"]),
                    "reply_id": cast(str, reply["id"]),
                    "connection_strength": connection_strength,
                    "query_preview": cast(str, query["content"])[:100] + "...",
                    "reply_preview": cast(str, reply["content"])[:100] + "...",
                }
            )

        return connections

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_array = np.array(vec1, dtype=np.float64)
        vec2_array = np.array(vec2, dtype=np.float64)

        dot_product = float(np.dot(vec1_array, vec2_array))
        norm1 = float(np.linalg.norm(vec1_array))
        norm2 = float(np.linalg.norm(vec2_array))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        result = dot_product / (norm1 * norm2)
        # Clamp to valid cosine similarity range to handle floating point precision issues
        return max(-1.0, min(1.0, result))

    def get_vector_space_summary(self, session_id: str) -> str:
        """Get a summary of the vector space connections."""
        data = self.extract_queries_and_replies(session_id)

        summary = f"""
## 🔗 Query-Reply Vector Space Summary

**Session**: {session_id}
**Queries**: {data['total_queries']}
**Replies**: {data['total_replies']}
**Connections**: {data['total_connections']}

### Your Queries:
"""

        queries = cast(
            list[dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]], data["queries"]
        )
        for i, query in enumerate(queries[:5]):  # Show first 5
            summary += f"{i+1}. {cast(str, query['content'])[:150]}...\n"

        summary += "\n### My Replies:\n"

        replies = cast(
            list[dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]], data["replies"]
        )
        for i, reply in enumerate(replies[:5]):  # Show first 5
            summary += f"{i+1}. {cast(str, reply['content'])[:150]}...\n"

        summary += "\n### Vector Space Connections:\n"

        connections = cast(
            list[dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]],
            data["connections"],
        )
        for i, conn in enumerate(connections[:5]):  # Show first 5
            summary += f"{i+1}. Strength: {cast(float, conn['connection_strength']):.3f}\n"
            summary += f"   Query: {cast(str, conn['query_preview'])}\n"
            summary += f"   Reply: {cast(str, conn['reply_preview'])}\n\n"

        return summary


def main() -> None:
    """Test the simple extractor."""
    print("🔗 Testing Atlas Simple Extractor")

    extractor = AtlasSimpleExtractor()

    # Test with a session
    session_id = "test_simple_session"

    # Extract data
    data = extractor.extract_queries_and_replies(session_id)
    print(f"✅ Extracted {data['total_queries']} queries and {data['total_replies']} replies")
    print(f"✅ Created {data['total_connections']} connections")

    # Show summary
    summary = extractor.get_vector_space_summary(session_id)
    print(summary)

    print("🎯 Simple extractor is working!")


if __name__ == "__main__":
    main()
