#!/usr/bin/env python3
"""
Atlas Complete Graph System
Complete implementation for multi-thread chat management with graph relationships
"""

import json
import os

# Add project paths
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, cast

import numpy as np
import psycopg
from psycopg.rows import dict_row

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from sentence_transformers import SentenceTransformer


class ThreadStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class RelationshipType(Enum):
    DIRECT_REPLY = "direct_reply"
    FOLLOW_UP = "follow_up"
    CLARIFICATION = "clarification"
    EXPANSION = "expansion"
    CROSS_REFERENCE = "cross_reference"


@dataclass
class ChatThread:
    """A chat thread representing a single chat tab."""

    thread_id: str
    session_id: str
    tab_id: str
    title: str
    status: ThreadStatus
    created_at: datetime
    last_activity: datetime
    metadata: dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]


@dataclass
class ConversationTurn:
    """A single conversation turn (query or response)."""

    turn_id: str
    thread_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    embedding: list[float]
    metadata: dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]


@dataclass
class QueryResponseRelationship:
    """Relationship between a query and response."""

    relationship_id: str
    query_id: str
    response_id: str
    thread_id: str
    similarity_score: float
    response_time: float  # seconds
    relationship_type: RelationshipType
    topic_tags: list[str]
    created_at: datetime


@dataclass
class CrossThreadInsight:
    """Insights discovered across multiple threads."""

    insight_id: str
    insight_type: str
    description: str
    confidence: float
    affected_threads: list[str]
    supporting_evidence: dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]]
    created_at: datetime


class AtlasCompleteGraphSystem:
    """Complete graph system for multi-thread chat management."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.embedder: SentenceTransformer = SentenceTransformer("BAAI/bge-large-en-v1.5")
        self.embedding_dim: int = 1024

        # Initialize database schema
        self._setup_complete_schema()

    def _setup_complete_schema(self) -> None:
        """Set up the complete graph database schema."""
        # Enable TimescaleDB extension
        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    _ = cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                    conn.commit()
                    print("✅ TimescaleDB enabled")
        except psycopg.errors.FeatureNotSupported:
            print("⚠️ TimescaleDB not available, using regular PostgreSQL")

        # Enable pgvector extension
        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    _ = cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    conn.commit()
                    print("✅ pgvector enabled")
        except psycopg.errors.FeatureNotSupported:
            print("⚠️ pgvector not available, using float arrays")

        # Create tables
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:

                # 1. Thread management table
                _ = cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS atlas_thread (
                        thread_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        tab_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'active',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        last_activity TIMESTAMPTZ DEFAULT NOW(),
                        metadata JSONB DEFAULT '{}',
                        embedding vector(384)
                    );
                """
                )

                # 2. Conversation turns table (extends existing atlas_node)
                _ = cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS atlas_conversation_turn (
                        turn_id TEXT PRIMARY KEY,
                        thread_id TEXT NOT NULL,
                        role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                        content TEXT NOT NULL,
                        timestamp TIMESTAMPTZ DEFAULT NOW(),
                        embedding vector(384),
                        metadata JSONB DEFAULT '{}',
                        
                        FOREIGN KEY (thread_id) REFERENCES atlas_thread(thread_id)
                    );
                """
                )

                # 3. Query-Response relationships table
                _ = cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS atlas_query_response_relationship (
                        relationship_id TEXT PRIMARY KEY,
                        query_id TEXT NOT NULL,
                        response_id TEXT NOT NULL,
                        thread_id TEXT NOT NULL,
                        similarity_score FLOAT NOT NULL,
                        response_time FLOAT NOT NULL,
                        relationship_type TEXT NOT NULL,
                        topic_tags TEXT[] DEFAULT '{}',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        metadata JSONB DEFAULT '{}',
                        
                        FOREIGN KEY (query_id) REFERENCES atlas_conversation_turn(turn_id),
                        FOREIGN KEY (response_id) REFERENCES atlas_conversation_turn(turn_id),
                        FOREIGN KEY (thread_id) REFERENCES atlas_thread(thread_id)
                    );
                """
                )

                # 4. Cross-thread insights table
                _ = cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS atlas_cross_thread_insight (
                        insight_id TEXT PRIMARY KEY,
                        insight_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        confidence FLOAT NOT NULL,
                        affected_threads TEXT[] NOT NULL,
                        supporting_evidence JSONB DEFAULT '{}',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        metadata JSONB DEFAULT '{}'
                    );
                """
                )

                # 5. Thread relationships table
                _ = cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS atlas_thread_relationship (
                        relationship_id TEXT PRIMARY KEY,
                        source_thread_id TEXT NOT NULL,
                        target_thread_id TEXT NOT NULL,
                        relationship_type TEXT NOT NULL,
                        strength FLOAT NOT NULL,
                        evidence TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        
                        FOREIGN KEY (source_thread_id) REFERENCES atlas_thread(thread_id),
                        FOREIGN KEY (target_thread_id) REFERENCES atlas_thread(thread_id),
                        UNIQUE(source_thread_id, target_thread_id, relationship_type)
                    );
                """
                )

                conn.commit()
                print("✅ Tables created")

        # Create TimescaleDB hypertables in separate connection
        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    _ = cur.execute(
                        "SELECT create_hypertable('atlas_conversation_turn', 'timestamp', if_not_exists => TRUE);"
                    )
                    _ = cur.execute(
                        "SELECT create_hypertable('atlas_query_response_relationship', 'created_at', if_not_exists => TRUE);"
                    )
                    _ = cur.execute(
                        "SELECT create_hypertable('atlas_cross_thread_insight', 'created_at', if_not_exists => TRUE);"
                    )
                    _ = cur.execute(
                        "SELECT create_hypertable('atlas_thread_relationship', 'created_at', if_not_exists => TRUE);"
                    )
                    conn.commit()
                    print("✅ TimescaleDB hypertables created")
        except (psycopg.errors.FeatureNotSupported, psycopg.errors.UndefinedFunction):
            print("⚠️ TimescaleDB hypertables not available")

        # Create indexes in separate connection
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_thread_session ON atlas_thread (session_id, created_at DESC);"
                )
                _ = cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_thread_status ON atlas_thread (status, last_activity DESC);"
                )
                _ = cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conversation_thread ON atlas_conversation_turn (thread_id, timestamp DESC);"
                )
                _ = cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conversation_role ON atlas_conversation_turn (role, timestamp DESC);"
                )
                _ = cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_relationship_thread ON atlas_query_response_relationship (thread_id, created_at DESC);"
                )
                _ = cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_relationship_similarity ON atlas_query_response_relationship (similarity_score DESC);"
                )
                _ = cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_insight_type ON atlas_cross_thread_insight (insight_type, confidence DESC);"
                )
                _ = cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_thread_rel_source ON atlas_thread_relationship (source_thread_id, relationship_type);"
                )

                # Create vector indexes
                try:
                    _ = cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_thread_embedding ON atlas_thread USING hnsw (embedding vector_cosine_ops);"
                    )
                    _ = cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_conversation_embedding ON atlas_conversation_turn USING hnsw (embedding vector_cosine_ops);"
                    )
                    print("✅ Vector indexes created")
                except (psycopg.errors.FeatureNotSupported, psycopg.errors.DatatypeMismatch):
                    print("⚠️ Vector indexes not available")

                conn.commit()
                print("✅ Complete graph schema initialized")

    def create_thread(self, title: str, session_id: str | None = None, tab_index: int = 0) -> ChatThread:
        """Create a new chat thread (represents a single chat tab)."""
        # Generate unique IDs
        timestamp = int(time.time())
        thread_id = f"thread_{timestamp}_{uuid.uuid4().hex[:8]}"

        if not session_id:
            # Create session ID based on date and user
            date_str = datetime.now().strftime("%Y_%m_%d")
            session_id = f"session_{date_str}_danieljacobs"

        tab_id = f"tab_{thread_id}_{tab_index}"

        # Create thread embedding
        thread_embedding_array = self.embedder.encode(title)
        thread_embedding = cast(list[float], thread_embedding_array.tolist())

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    """
                    INSERT INTO atlas_thread (thread_id, session_id, tab_id, title, status, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (thread_id) DO UPDATE SET
                        last_activity = NOW(),
                        metadata = EXCLUDED.metadata
                """,
                    (
                        thread_id,
                        session_id,
                        tab_id,
                        title,
                        ThreadStatus.ACTIVE.value,
                        thread_embedding,
                        json.dumps(
                            {"created_by": "danieljacobs", "tab_index": tab_index, "thread_type": "cursor_chat"}
                        ),
                    ),
                )
                conn.commit()

        return ChatThread(
            thread_id=thread_id,
            session_id=session_id,
            tab_id=tab_id,
            title=title,
            status=ThreadStatus.ACTIVE,
            created_at=datetime.now(UTC),
            last_activity=datetime.now(UTC),
            metadata={"tab_index": tab_index},
        )

    def add_conversation_turn(
        self,
        thread_id: str,
        role: str,
        content: str,
        metadata: dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]] | None = None,
    ) -> ConversationTurn:
        """Add a conversation turn to a thread."""
        turn_id = f"turn_{thread_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(UTC)

        # Get embedding
        embedding_array = self.embedder.encode(content)
        embedding = cast(list[float], embedding_array.tolist())

        # Enhanced metadata
        enhanced_metadata = {
            "role": role,
            "thread_id": thread_id,
            "turn_id": turn_id,
            "timestamp": timestamp.isoformat(),
            "content_length": len(content),
            "word_count": len(content.split()),
            **(metadata or {}),
        }

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # Store conversation turn
                _ = cur.execute(
                    """
                    INSERT INTO atlas_conversation_turn 
                    (turn_id, thread_id, role, content, timestamp, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (turn_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                """,
                    (turn_id, thread_id, role, content, timestamp, embedding, json.dumps(enhanced_metadata)),
                )

                # Update thread activity
                _ = cur.execute(
                    """
                    UPDATE atlas_thread 
                    SET last_activity = NOW()
                    WHERE thread_id = %s
                """,
                    (thread_id,),
                )

                conn.commit()

        return ConversationTurn(
            turn_id=turn_id,
            thread_id=thread_id,
            role=role,
            content=content,
            timestamp=timestamp,
            embedding=embedding,
            metadata=enhanced_metadata,
        )

    def analyze_query_response_relationships(self, thread_id: str) -> list[QueryResponseRelationship]:
        """Analyze relationships between queries and responses in a thread."""
        relationships = []

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get conversation turns in chronological order
                _ = cur.execute(
                    """
                    SELECT turn_id, role, content, timestamp
                    FROM atlas_conversation_turn
                    WHERE thread_id = %s
                    ORDER BY timestamp
                """,
                    (thread_id,),
                )

                turns = cur.fetchall()

                # Find query-response pairs
                for i in range(len(turns) - 1):
                    current_turn = turns[i]
                    next_turn = turns[i + 1]

                    # Check if this is a user->assistant pair
                    if current_turn["role"] == "user" and next_turn["role"] == "assistant":

                        # Calculate similarity
                        query_content = cast(str, current_turn["content"])
                        response_content = cast(str, next_turn["content"])
                        query_embedding_array = self.embedder.encode(query_content)
                        query_embedding = cast(list[float], query_embedding_array.tolist())
                        response_embedding_array = self.embedder.encode(response_content)
                        response_embedding = cast(list[float], response_embedding_array.tolist())
                        similarity_score = self._cosine_similarity(query_embedding, response_embedding)

                        # Calculate response time
                        current_timestamp = cast(datetime, current_turn["timestamp"])
                        next_timestamp = cast(datetime, next_turn["timestamp"])
                        response_time = float((next_timestamp - current_timestamp).total_seconds())

                        # Extract topic tags
                        topic_tags = self._extract_topic_tags(query_content, response_content)

                        # Determine relationship type
                        relationship_type = self._determine_relationship_type(query_content, response_content)

                        relationship = QueryResponseRelationship(
                            relationship_id=f"rel_{thread_id}_{int(time.time())}_{i}",
                            query_id=cast(str, current_turn["turn_id"]),
                            response_id=cast(str, next_turn["turn_id"]),
                            thread_id=thread_id,
                            similarity_score=float(similarity_score),
                            response_time=float(response_time),
                            relationship_type=relationship_type,
                            topic_tags=topic_tags,
                            created_at=cast(datetime, current_turn["timestamp"]),
                        )

                        relationships.append(relationship)

                        # Store relationship
                        self._store_query_response_relationship(relationship)

        return relationships

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

    def _extract_topic_tags(self, query_content: str, response_content: str) -> list[str]:
        """Extract topic tags from query-response pair."""
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
            "thread",
            "timescale",
            "pattern",
            "insight",
            "relationship",
            "multi-thread",
        ]

        combined_content = (query_content + " " + response_content).lower()
        found_topics = []

        for topic in project_topics:
            if topic.lower() in combined_content:
                found_topics.append(topic)

        return found_topics

    def _determine_relationship_type(self, query_content: str, response_content: str) -> RelationshipType:
        """Determine the type of relationship between query and response."""
        query_lower = query_content.lower()
        response_lower = response_content.lower()

        if "?" in query_content and "here" in response_lower:
            return RelationshipType.DIRECT_REPLY
        elif "follow up" in query_lower or "also" in query_lower:
            return RelationshipType.FOLLOW_UP
        elif "clarify" in query_lower or "what do you mean" in query_lower:
            return RelationshipType.CLARIFICATION
        elif "more" in query_lower or "expand" in query_lower:
            return RelationshipType.EXPANSION
        elif "thread" in query_lower or "other chat" in query_lower:
            return RelationshipType.CROSS_REFERENCE
        else:
            return RelationshipType.DIRECT_REPLY

    def _store_query_response_relationship(self, relationship: QueryResponseRelationship) -> None:
        """Store query-response relationship in database."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    """
                    INSERT INTO atlas_query_response_relationship 
                    (relationship_id, query_id, response_id, thread_id, similarity_score, 
                     response_time, relationship_type, topic_tags, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (relationship_id) DO UPDATE SET
                        similarity_score = EXCLUDED.similarity_score,
                        response_time = EXCLUDED.response_time,
                        topic_tags = EXCLUDED.topic_tags
                """,
                    (
                        relationship.relationship_id,
                        relationship.query_id,
                        relationship.response_id,
                        relationship.thread_id,
                        relationship.similarity_score,
                        relationship.response_time,
                        relationship.relationship_type.value,
                        relationship.topic_tags,
                        relationship.created_at,
                    ),
                )
                conn.commit()

    def analyze_cross_thread_insights(self, time_window_hours: int = 24) -> list[CrossThreadInsight]:
        """Analyze insights across multiple threads."""
        insights = []
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(hours=time_window_hours)

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Find threads with similar topics
                _ = cur.execute(
                    """
                    WITH thread_topics AS (
                        SELECT 
                            thread_id,
                            UNNEST(topic_tags) as topic,
                            COUNT(*) as topic_frequency
                        FROM atlas_query_response_relationship
                        WHERE created_at BETWEEN %s AND %s
                        GROUP BY thread_id, UNNEST(topic_tags)
                    ),
                    similar_threads AS (
                        SELECT 
                            t1.thread_id as thread1,
                            t2.thread_id as thread2,
                            COUNT(*) as shared_topics,
                            ARRAY_AGG(t1.topic) as common_topics
                        FROM thread_topics t1
                        JOIN thread_topics t2 ON t1.thread_id < t2.thread_id AND t1.topic = t2.topic
                        GROUP BY t1.thread_id, t2.thread_id
                        HAVING COUNT(*) >= 2
                    )
                    SELECT 
                        thread1,
                        thread2,
                        shared_topics,
                        common_topics
                    FROM similar_threads
                    ORDER BY shared_topics DESC
                """,
                    (start_time, end_time),
                )

                for row in cur.fetchall():
                    insight = CrossThreadInsight(
                        insight_id=f"similar_threads_{int(time.time())}_{hash(str([row['thread1'], row['thread2']])) % 1000}",
                        insight_type="similar_threads",
                        description=f"Threads {row['thread1']} and {row['thread2']} share {row['shared_topics']} topics: {', '.join(cast(list[str], row['common_topics'])[:3])}",
                        confidence=min(cast(float, row["shared_topics"]) / 5.0, 1.0),
                        affected_threads=[cast(str, row["thread1"]), cast(str, row["thread2"])],
                        supporting_evidence={
                            "shared_topics": cast(int, row["shared_topics"]),
                            "common_topics": cast(list[str], row["common_topics"]),
                        },
                        created_at=end_time,
                    )
                    insights.append(insight)

                # Find temporal patterns
                _ = cur.execute(
                    """
                    WITH hourly_activity AS (
                        SELECT 
                            thread_id,
                            EXTRACT(HOUR FROM timestamp) as hour_of_day,
                            COUNT(*) as activity_count
                        FROM atlas_conversation_turn
                        WHERE timestamp BETWEEN %s AND %s
                        GROUP BY thread_id, EXTRACT(HOUR FROM timestamp)
                    ),
                    peak_hours AS (
                        SELECT 
                            hour_of_day,
                            COUNT(DISTINCT thread_id) as thread_count,
                            AVG(activity_count) as avg_activity
                        FROM hourly_activity
                        GROUP BY hour_of_day
                        HAVING COUNT(DISTINCT thread_id) >= 2
                        ORDER BY thread_count DESC
                    )
                    SELECT hour_of_day, thread_count, avg_activity
                    FROM peak_hours
                    LIMIT 3
                """,
                    (start_time, end_time),
                )

                for row in cur.fetchall():
                    insight = CrossThreadInsight(
                        insight_id=f"temporal_{int(time.time())}_{int(cast(int, row['hour_of_day']))}",
                        insight_type="temporal_patterns",
                        description=f"Peak activity at hour {int(cast(int, row['hour_of_day']))} across {cast(int, row['thread_count'])} threads",
                        confidence=min(cast(int, row["thread_count"]) / 5.0, 1.0),
                        affected_threads=[],
                        supporting_evidence={
                            "hour_of_day": cast(int, row["hour_of_day"]),
                            "thread_count": cast(int, row["thread_count"]),
                            "avg_activity": cast(float, row["avg_activity"]),
                        },
                        created_at=end_time,
                    )
                    insights.append(insight)

                # Store insights
                for insight in insights:
                    self._store_cross_thread_insight(insight)

        return insights

    def _store_cross_thread_insight(self, insight: CrossThreadInsight) -> None:
        """Store cross-thread insight in database."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    """
                    INSERT INTO atlas_cross_thread_insight 
                    (insight_id, insight_type, description, confidence, 
                     affected_threads, supporting_evidence, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (insight_id) DO UPDATE SET
                        confidence = EXCLUDED.confidence,
                        supporting_evidence = EXCLUDED.supporting_evidence
                """,
                    (
                        insight.insight_id,
                        insight.insight_type,
                        insight.description,
                        insight.confidence,
                        insight.affected_threads,
                        json.dumps(insight.supporting_evidence),
                        insight.created_at,
                    ),
                )
                conn.commit()

    def get_thread_summary(self, thread_id: str) -> dict[str, Any]:
        """Get comprehensive summary of a thread."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get thread info
                _ = cur.execute("SELECT * FROM atlas_thread WHERE thread_id = %s", (thread_id,))
                thread_info = cur.fetchone()

                if not thread_info:
                    return {"error": "Thread not found"}

                # Get conversation stats
                _ = cur.execute(
                    """
                    SELECT 
                        COUNT(*) as total_turns,
                        COUNT(CASE WHEN role = 'user' THEN 1 END) as user_turns,
                        COUNT(CASE WHEN role = 'assistant' THEN 1 END) as assistant_turns,
                        MIN(timestamp) as first_turn,
                        MAX(timestamp) as last_turn
                    FROM atlas_conversation_turn
                    WHERE thread_id = %s
                """,
                    (thread_id,),
                )

                conv_stats_row = cur.fetchone()
                if not conv_stats_row:
                    conv_stats: dict[
                        str, str | int | float | bool | list[str] | dict[str, str | int | float | bool] | None
                    ] = {
                        "total_turns": 0,
                        "user_turns": 0,
                        "assistant_turns": 0,
                        "first_turn": None,
                        "last_turn": None,
                    }
                else:
                    conv_stats = dict(conv_stats_row)

                # Get relationship stats
                _ = cur.execute(
                    """
                    SELECT 
                        COUNT(*) as total_relationships,
                        AVG(similarity_score) as avg_similarity,
                        AVG(response_time) as avg_response_time
                    FROM atlas_query_response_relationship
                    WHERE thread_id = %s
                """,
                    (thread_id,),
                )

                # Get topics separately
                _ = cur.execute(
                    """
                    SELECT DISTINCT UNNEST(topic_tags) as topic
                    FROM atlas_query_response_relationship
                    WHERE thread_id = %s
                """,
                    (thread_id,),
                )

                topics = [row["topic"] for row in cur.fetchall()]

                rel_stats_row = cur.fetchone()
                if not rel_stats_row:
                    rel_stats: dict[str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]] = {
                        "total_relationships": 0,
                        "avg_similarity": 0.0,
                        "avg_response_time": 0.0,
                    }
                else:
                    rel_stats = dict(rel_stats_row)

                return {
                    "thread_id": thread_id,
                    "title": cast(str, thread_info["title"]),
                    "status": cast(str, thread_info["status"]),
                    "created_at": cast(str, thread_info["created_at"]),
                    "last_activity": cast(str, thread_info["last_activity"]),
                    "conversation": {
                        "total_turns": cast(int, conv_stats["total_turns"] or 0),
                        "user_turns": cast(int, conv_stats["user_turns"] or 0),
                        "assistant_turns": cast(int, conv_stats["assistant_turns"] or 0),
                        "first_turn": cast(str | None, conv_stats["first_turn"]),
                        "last_turn": cast(str | None, conv_stats["last_turn"]),
                    },
                    "relationships": {
                        "total": cast(int, rel_stats["total_relationships"] or 0),
                        "avg_similarity": cast(float, rel_stats["avg_similarity"] or 0.0),
                        "avg_response_time": cast(float, rel_stats["avg_response_time"] or 0.0),
                        "topics": cast(list[str], topics),
                    },
                }

    def get_session_dashboard(self, session_id: str) -> dict[str, Any]:
        """Get dashboard view of all threads in a session."""
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get all threads in session
                _ = cur.execute(
                    """
                    SELECT thread_id, title, status, created_at, last_activity
                    FROM atlas_thread
                    WHERE session_id = %s
                    ORDER BY created_at
                """,
                    (session_id,),
                )

                threads = [dict(row) for row in cur.fetchall()]

                # Get session stats
                _ = cur.execute(
                    """
                    SELECT 
                        COUNT(DISTINCT ct.thread_id) as total_threads,
                        COUNT(*) as total_turns,
                        AVG(qrr.response_time) as avg_response_time
                    FROM atlas_conversation_turn ct
                    LEFT JOIN atlas_query_response_relationship qrr ON ct.thread_id = qrr.thread_id
                    WHERE ct.thread_id IN (
                        SELECT thread_id FROM atlas_thread WHERE session_id = %s
                    )
                """,
                    (session_id,),
                )

                session_stats_row = cur.fetchone()
                if not session_stats_row:
                    session_stats: dict[str, Any] = {"total_threads": 0, "total_turns": 0, "avg_response_time": 0.0}
                else:
                    session_stats = dict(session_stats_row)

                # Get recent insights
                _ = cur.execute(
                    """
                    SELECT insight_type, description, confidence, created_at
                    FROM atlas_cross_thread_insight
                    WHERE %s = ANY(affected_threads)
                    ORDER BY created_at DESC
                    LIMIT 5
                """,
                    (session_id,),
                )

                recent_insights = [dict(row) for row in cur.fetchall()]

                return {
                    "session_id": session_id,
                    "threads": threads,
                    "stats": {
                        "total_threads": session_stats["total_threads"] or 0,
                        "total_turns": session_stats["total_turns"] or 0,
                        "avg_response_time": float(session_stats["avg_response_time"] or 0.0),
                    },
                    "recent_insights": recent_insights,
                    "last_updated": datetime.now(UTC).isoformat(),
                }


def main() -> None:
    """Test the complete graph system."""
    print("🔗 Testing Atlas Complete Graph System")

    system = AtlasCompleteGraphSystem()

    # Create test threads (simulating multiple chat tabs)
    session_id = "session_2025_09_13_danieljacobs"

    thread1 = system.create_thread("RAGChecker Optimization", session_id, tab_index=0)
    thread2 = system.create_thread("Atlas Graph Storage", session_id, tab_index=1)
    thread3 = system.create_thread("Memory System Design", session_id, tab_index=2)

    print(f"✅ Created threads: {thread1.thread_id}, {thread2.thread_id}, {thread3.thread_id}")

    # Add conversation turns to each thread
    # Thread 1: RAGChecker
    _ = system.add_conversation_turn(thread1.thread_id, "user", "How can we improve RAGChecker precision?")
    _ = system.add_conversation_turn(
        thread1.thread_id, "assistant", "Here are several strategies to improve precision..."
    )

    # Thread 2: Atlas
    _ = system.add_conversation_turn(thread2.thread_id, "user", "I want to implement graph storage for conversations")
    _ = system.add_conversation_turn(
        thread2.thread_id, "assistant", "Great idea! Let me show you how to implement Atlas..."
    )

    # Thread 3: Memory
    _ = system.add_conversation_turn(thread3.thread_id, "user", "How should we handle multi-thread chat management?")
    _ = system.add_conversation_turn(
        thread3.thread_id, "assistant", "We need a hierarchical ID system with thread-level isolation..."
    )

    # Analyze relationships
    relationships1 = system.analyze_query_response_relationships(thread1.thread_id)
    relationships2 = system.analyze_query_response_relationships(thread2.thread_id)
    relationships3 = system.analyze_query_response_relationships(thread3.thread_id)

    print(f"✅ Thread 1 relationships: {len(relationships1)}")
    print(f"✅ Thread 2 relationships: {len(relationships2)}")
    print(f"✅ Thread 3 relationships: {len(relationships3)}")

    # Analyze cross-thread insights
    insights = system.analyze_cross_thread_insights()
    print(f"✅ Cross-thread insights: {len(insights)}")

    # Get thread summaries
    summary1 = system.get_thread_summary(thread1.thread_id)
    summary2 = system.get_thread_summary(thread2.thread_id)
    summary3 = system.get_thread_summary(thread3.thread_id)

    print(
        f"✅ Thread 1: {summary1['conversation']['total_turns']} turns, {summary1['relationships']['total']} relationships"
    )
    print(
        f"✅ Thread 2: {summary2['conversation']['total_turns']} turns, {summary2['relationships']['total']} relationships"
    )
    print(
        f"✅ Thread 3: {summary3['conversation']['total_turns']} turns, {summary3['relationships']['total']} relationships"
    )

    # Get session dashboard
    dashboard = system.get_session_dashboard(session_id)
    print(
        f"✅ Session dashboard: {dashboard['stats']['total_threads']} threads, {dashboard['stats']['total_turns']} turns"
    )

    print("🎯 Complete graph system is working!")


if __name__ == "__main__":
    main()
