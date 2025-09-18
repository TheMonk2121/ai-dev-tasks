#!/usr/bin/env python3
"""
Atlas Query-Reply Extractor
Extracts your queries, my replies, and creates connecting vector space relationships
Following established chunking and embedding guidelines
"""

import json
import os
import re

# Add project paths
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, cast

import numpy as np
import psycopg
from psycopg import Cursor
from psycopg.rows import dict_row

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from sentence_transformers import SentenceTransformer

# Use your established configuration
from src.config.models import RAG


@dataclass
class QueryReplyPair:
    """A query-reply pair with connecting relationships."""

    query_id: str
    reply_id: str
    query_content: str
    reply_content: str
    query_embedding: list[float]
    reply_embedding: list[float]
    connection_strength: float
    semantic_topics: list[str]
    created_at: datetime


class AtlasQueryReplyExtractor:
    """Extracts query-reply pairs and creates connecting vector space relationships."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

        # Use your established RAG configuration
        self.rag_config: RAG = RAG()
        self.embedder: SentenceTransformer = SentenceTransformer(self.rag_config.embedder_name)
        self.embedding_dim: int = self.rag_config.embedding_dim

        # Chunking parameters from your guidelines
        self.chunk_size: int = self.rag_config.chunk_size  # 450
        self.overlap_ratio: float = self.rag_config.overlap_ratio  # 0.10
        self.overlap_size: int = int(self.chunk_size * self.overlap_ratio)  # 45

    def extract_query_reply_pairs(self, session_id: str) -> list[QueryReplyPair]:
        """Extract query-reply pairs from a conversation session."""
        pairs = []

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get conversation turns in order
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

                # Pair consecutive user/assistant turns
                for i in range(len(turns) - 1):
                    current_turn = turns[i]
                    next_turn = turns[i + 1]

                    current_metadata = (
                        cast(
                            dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]],
                            json.loads(cast(str, current_turn["metadata"])),
                        )
                        if current_turn["metadata"]
                        else {}
                    )
                    next_metadata = (
                        cast(
                            dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]],
                            json.loads(cast(str, next_turn["metadata"])),
                        )
                        if next_turn["metadata"]
                        else {}
                    )

                    # Check if this is a user->assistant pair
                    if current_metadata.get("role") == "user" and next_metadata.get("role") == "assistant":

                        pair = self._create_query_reply_pair(query_turn=current_turn, reply_turn=next_turn)
                        pairs.append(pair)

        return pairs

    def _create_query_reply_pair(
        self,
        query_turn: dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]],
        reply_turn: dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]],
    ) -> QueryReplyPair:
        """Create a query-reply pair with connecting relationships."""
        query_id = cast(str, query_turn["node_id"])
        reply_id = cast(str, reply_turn["node_id"])
        query_content = cast(str, query_turn["content"])
        reply_content = cast(str, reply_turn["content"])

        # Get embeddings
        query_embedding_array = self.embedder.encode(query_content)
        query_embedding = cast(list[float], query_embedding_array.tolist())
        reply_embedding_array = self.embedder.encode(reply_content)
        reply_embedding = cast(list[float], reply_embedding_array.tolist())

        # Calculate connection strength (cosine similarity)
        connection_strength = self._calculate_connection_strength(query_embedding, reply_embedding)

        # Extract semantic topics
        semantic_topics = self._extract_semantic_topics(query_content, reply_content)

        return QueryReplyPair(
            query_id=query_id,
            reply_id=reply_id,
            query_content=query_content,
            reply_content=reply_content,
            query_embedding=query_embedding,
            reply_embedding=reply_embedding,
            connection_strength=connection_strength,
            semantic_topics=semantic_topics,
            created_at=(
                query_turn["created_at"]
                if isinstance(query_turn["created_at"], datetime)
                else datetime.fromisoformat(cast(str, query_turn["created_at"]))
            ),
        )

    def _calculate_connection_strength(self, query_embedding: list[float], reply_embedding: list[float]) -> float:
        """Calculate connection strength between query and reply embeddings."""
        # Convert to numpy arrays
        query_array = np.array(query_embedding, dtype=np.float64)
        reply_array = np.array(reply_embedding, dtype=np.float64)

        # Cosine similarity
        dot_product = float(np.dot(query_array, reply_array))
        norm_query = float(np.linalg.norm(query_array))
        norm_reply = float(np.linalg.norm(reply_array))

        if norm_query == 0 or norm_reply == 0:
            return 0.0

        result = dot_product / (norm_query * norm_reply)
        # Clamp to valid cosine similarity range to handle floating point precision issues
        return max(-1.0, min(1.0, result))

    def _extract_semantic_topics(self, query_content: str, reply_content: str) -> list[str]:
        """Extract semantic topics from query-reply pair."""
        topics = []

        # Project-specific topics
        project_topics = [
            "RAGChecker",
            "DSPy",
            "memory system",
            "Atlas",
            "graph storage",
            "conversation",
            "decision",
            "suggestion",
            "backlog",
            "PRD",
            "evaluation",
            "baseline",
            "precision",
            "recall",
            "F1 score",
            "vector",
            "embedding",
            "pgvector",
            "PostgreSQL",
            "database",
            "chunking",
            "retrieval",
            "generation",
            "optimization",
        ]

        combined_content = (query_content + " " + reply_content).lower()

        for topic in project_topics:
            if topic.lower() in combined_content:
                topics.append(topic)

        return topics

    def store_query_reply_relationships(self, pairs: list[QueryReplyPair]) -> None:
        """Store query-reply relationships in the Atlas graph."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                for pair in pairs:
                    # Store query-reply relationship edge
                    self._create_query_reply_edge(cur, pair)

                    # Store semantic topic connections
                    self._create_topic_connections(cur, pair)

                    # Store chunked content if needed
                    if self._should_chunk_content(pair.query_content) or self._should_chunk_content(pair.reply_content):
                        self._create_chunked_content(cur, pair)

                conn.commit()

    def _create_query_reply_edge(self, cur: Cursor[Any], pair: QueryReplyPair) -> None:
        """Create the main query-reply relationship edge."""
        _ = cur.execute(
            """
            INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence, weight)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source_node_id, target_node_id, edge_type) DO UPDATE SET
                evidence = EXCLUDED.evidence,
                weight = EXCLUDED.weight
        """,
            (
                pair.query_id,
                pair.reply_id,
                "replies_to",
                f"Query-reply pair with connection strength {pair.connection_strength:.3f}",
                pair.connection_strength,
            ),
        )

    def _create_topic_connections(self, cur: Cursor[Any], pair: QueryReplyPair) -> None:
        """Create connections to semantic topics."""
        for topic in pair.semantic_topics:
            # Ensure topic node exists
            topic_id = f"topic_{topic.replace(' ', '_').lower()}"
            self._ensure_topic_node_exists(cur, topic_id, topic)

            # Connect query to topic
            cur.execute(
                """
                INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence, weight)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_node_id, target_node_id, edge_type) DO NOTHING
            """,
                (pair.query_id, topic_id, "mentions_topic", f"Query mentions topic: {topic}", 0.8),
            )

            # Connect reply to topic
            cur.execute(
                """
                INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence, weight)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_node_id, target_node_id, edge_type) DO NOTHING
            """,
                (pair.reply_id, topic_id, "addresses_topic", f"Reply addresses topic: {topic}", 0.9),
            )

    def _ensure_topic_node_exists(self, cur: Cursor[Any], topic_id: str, topic_name: str) -> None:
        """Ensure a topic node exists in the graph."""
        cur.execute(
            """
            INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (node_id) DO NOTHING
        """,
            (
                topic_id,
                "topic",
                f"Topic: {topic_name}",
                f"Semantic topic: {topic_name}",
                json.dumps({"topic_name": topic_name, "topic_type": "semantic"}),
                self.embedder.encode(topic_name).tolist(),
                datetime.now() + timedelta(days=30),  # Topics don't expire quickly
            ),
        )

    def _should_chunk_content(self, content: str) -> bool:
        """Determine if content should be chunked based on your guidelines."""
        return len(content) > self.chunk_size

    def _create_chunked_content(self, cur: Cursor[Any], pair: QueryReplyPair) -> None:
        """Create chunked versions of long content following your guidelines."""
        # Chunk query if needed
        if self._should_chunk_content(pair.query_content):
            self._chunk_and_store_content(cur, pair.query_id, pair.query_content, "query_chunk", pair.query_embedding)

        # Chunk reply if needed
        if self._should_chunk_content(pair.reply_content):
            self._chunk_and_store_content(cur, pair.reply_id, pair.reply_content, "reply_chunk", pair.reply_embedding)

    def _chunk_and_store_content(
        self, cur: Cursor[Any], parent_id: str, content: str, chunk_type: str, _parent_embedding: list[float]
    ) -> None:
        """Chunk content following your established guidelines."""
        chunks = self._chunk_content_semantic(content)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{parent_id}_chunk_{i}"
            chunk_embedding = self.embedder.encode(chunk["content"])

            # Create chunk node
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
                    chunk_id,
                    chunk_type,
                    f"{chunk_type}: {chunk['content'][:100]}...",
                    chunk["content"],
                    json.dumps(
                        {
                            "parent_id": parent_id,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "chunk_size": len(chunk["content"]),
                            "overlap_start": chunk.get("overlap_start", 0),
                            "overlap_end": chunk.get("overlap_end", 0),
                        }
                    ),
                    chunk_embedding.tolist(),
                    datetime.now() + timedelta(hours=48),
                ),
            )

            # Create edge to parent
            cur.execute(
                """
                INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence, weight)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (source_node_id, target_node_id, edge_type) DO NOTHING
            """,
                (parent_id, chunk_id, "contains_chunk", f"Parent contains chunk {i}", 1.0),
            )

            # Create sequential edges between chunks
            if i > 0:
                prev_chunk_id = f"{parent_id}_chunk_{i-1}"
                cur.execute(
                    """
                    INSERT INTO atlas_edge (source_node_id, target_node_id, edge_type, evidence, weight)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (source_node_id, target_node_id, edge_type) DO NOTHING
                """,
                    (prev_chunk_id, chunk_id, "follows_chunk", f"Chunk {i-1} follows chunk {i}", 0.8),
                )

    def _chunk_content_semantic(self, content: str) -> list[dict[str, Any]]:
        """Chunk content using your established semantic chunking guidelines."""
        if len(content) <= self.chunk_size:
            return [{"content": content, "overlap_start": 0, "overlap_end": 0}]

        # Simple sentence-based chunking with your overlap ratio
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = ""
        chunk_start = 0

        for i, sentence in enumerate(sentences):
            if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                # Create chunk
                chunks.append(
                    {
                        "content": current_chunk.strip(),
                        "overlap_start": chunk_start,
                        "overlap_end": chunk_start + len(current_chunk),
                    }
                )

                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(sentences, i, self.overlap_size)
                current_chunk = " ".join(overlap_sentences) + " " + sentence
                chunk_start = chunk_start + len(current_chunk) - len(sentence)
            else:
                current_chunk += " " + sentence

        # Add final chunk
        if current_chunk.strip():
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "overlap_start": chunk_start,
                    "overlap_end": chunk_start + len(current_chunk),
                }
            )

        return chunks

    def _get_overlap_sentences(self, sentences: list[str], current_index: int, overlap_size: int) -> list[str]:
        """Get overlap sentences for chunk continuity."""
        overlap_sentences: list[str] = []
        current_length = 0

        for i in range(current_index - 1, -1, -1):
            if current_length + len(sentences[i]) > overlap_size:
                break
            overlap_sentences.insert(0, sentences[i])
            current_length += len(sentences[i])

        return overlap_sentences

    def get_query_reply_graph(self, session_id: str) -> dict[str, Any]:
        """Get the query-reply graph for a session."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get query-reply pairs
                _ = cur.execute(
                    """
                    SELECT q.node_id as query_id, q.content as query_content,
                           r.node_id as reply_id, r.content as reply_content,
                           e.weight as connection_strength, e.evidence
                    FROM atlas_node q
                    JOIN atlas_edge e ON q.node_id = e.source_node_id
                    JOIN atlas_node r ON e.target_node_id = r.node_id
                    WHERE e.edge_type = 'replies_to'
                    AND q.metadata->>'session_id' = %s
                    ORDER BY q.created_at
                """,
                    (session_id,),
                )

                pairs = []
                for row in cur.fetchall():
                    pairs.append(
                        {
                            "query_id": row["query_id"],
                            "reply_id": row["reply_id"],
                            "query_content": row["query_content"],
                            "reply_content": row["reply_content"],
                            "connection_strength": float(row["connection_strength"]),
                            "evidence": row["evidence"],
                        }
                    )

                # Get topic connections
                _ = cur.execute(
                    """
                    SELECT DISTINCT t.node_id as topic_id, t.title as topic_name
                    FROM atlas_node t
                    JOIN atlas_edge e ON t.node_id = e.target_node_id
                    WHERE e.edge_type IN ('mentions_topic', 'addresses_topic')
                    AND e.source_node_id IN (
                        SELECT node_id FROM atlas_node 
                        WHERE metadata->>'session_id' = %s
                    )
                """,
                    (session_id,),
                )

                topics = [{"topic_id": row["topic_id"], "topic_name": row["topic_name"]} for row in cur.fetchall()]

                return {
                    "session_id": session_id,
                    "query_reply_pairs": pairs,
                    "topics": topics,
                    "total_pairs": len(pairs),
                    "total_topics": len(topics),
                }


def main() -> None:
    """Test the query-reply extractor."""
    print("🔗 Testing Atlas Query-Reply Extractor")

    extractor = AtlasQueryReplyExtractor()

    # Test with a session
    session_id = "test_query_reply_session"

    # Extract query-reply pairs
    pairs = extractor.extract_query_reply_pairs(session_id)
    print(f"✅ Found {len(pairs)} query-reply pairs")

    # Store relationships
    if pairs:
        extractor.store_query_reply_relationships(pairs)
        print("✅ Stored query-reply relationships")

        # Get graph
        graph = extractor.get_query_reply_graph(session_id)
        print(f"📊 Graph: {graph['total_pairs']} pairs, {graph['total_topics']} topics")

    print("🎯 Query-reply extractor is working!")


if __name__ == "__main__":
    main()
