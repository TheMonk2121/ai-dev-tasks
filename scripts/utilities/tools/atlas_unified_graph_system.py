#!/usr/bin/env python3
"""
Atlas Unified Graph System
Complete graph database for query-response relationships, cross-thread analysis, and pattern discovery
"""

import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer


@dataclass
class QueryResponseRelationship:
    """A relationship between a query and response."""
    relationship_id: str
    query_id: str
    response_id: str
    thread_id: str
    session_id: str
    similarity_score: float
    response_time: float  # seconds
    topic_tags: list[str]
    relationship_type: str  # 'direct_reply', 'follow_up', 'clarification', 'expansion'
    created_at: datetime


@dataclass
class ThreadPattern:
    """Patterns discovered within a thread."""
    pattern_id: str
    thread_id: str
    pattern_type: str  # 'question_type', 'response_style', 'topic_evolution', 'engagement_pattern'
    description: str
    confidence: float
    frequency: int
    first_seen: datetime
    last_seen: datetime


@dataclass
class CrossThreadInsight:
    """Insights from cross-thread analysis."""
    insight_id: str
    insight_type: str  # 'similar_threads', 'temporal_patterns', 'topic_clusters', 'response_patterns'
    description: str
    confidence: float
    affected_threads: list[str]
    supporting_evidence: list[dict[str, Any]]
    created_at: datetime


class AtlasUnifiedGraphSystem:
    """Unified graph system for comprehensive conversation analysis."""
    
    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim = 384
        
        # Initialize graph schema
        self._setup_unified_graph_schema()
    
    def _setup_unified_graph_schema(self):
        """Set up the unified graph database schema."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # Enable required extensions
                try:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                except psycopg2.errors.FeatureNotSupported:
                    print("⚠️ TimescaleDB not available, using regular PostgreSQL tables")
                    conn.rollback()
                
                try:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                except psycopg2.errors.FeatureNotSupported:
                    print("⚠️ pgvector not available, using regular float arrays")
                    conn.rollback()
                
                # Core conversation nodes (already exists from previous setup)
                # Thread nodes
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS atlas_thread (
                        thread_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        last_activity TIMESTAMPTZ DEFAULT NOW(),
                        metadata JSONB DEFAULT '{}',
                        embedding FLOAT[]
                    );
                """)
                
                # Query-Response relationships
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS atlas_query_response_relationship (
                        relationship_id TEXT PRIMARY KEY,
                        query_id TEXT NOT NULL,
                        response_id TEXT NOT NULL,
                        thread_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        similarity_score FLOAT NOT NULL,
                        response_time FLOAT NOT NULL,
                        topic_tags TEXT[] DEFAULT '{}',
                        relationship_type TEXT NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        metadata JSONB DEFAULT '{}',
                        
                        FOREIGN KEY (query_id) REFERENCES atlas_node(node_id),
                        FOREIGN KEY (response_id) REFERENCES atlas_node(node_id),
                        FOREIGN KEY (thread_id) REFERENCES atlas_thread(thread_id)
                    );
                """)
                
                # Thread patterns
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS atlas_thread_pattern (
                        pattern_id TEXT PRIMARY KEY,
                        thread_id TEXT NOT NULL,
                        pattern_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        confidence FLOAT NOT NULL,
                        frequency INTEGER DEFAULT 1,
                        first_seen TIMESTAMPTZ DEFAULT NOW(),
                        last_seen TIMESTAMPTZ DEFAULT NOW(),
                        metadata JSONB DEFAULT '{}',
                        
                        FOREIGN KEY (thread_id) REFERENCES atlas_thread(thread_id)
                    );
                """)
                
                # Cross-thread insights
                cur.execute("""
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
                """)
                
                # Create TimescaleDB hypertables for time-series data (if available)
                # Check if TimescaleDB is available first
                try:
                    cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'timescaledb';")
                    has_timescale = cur.fetchone() is not None
                except:
                    has_timescale = False
                
                if has_timescale:
                    try:
                        cur.execute("SELECT create_hypertable('atlas_query_response_relationship', 'created_at', if_not_exists => TRUE);")
                    except (psycopg2.errors.DuplicateTable, psycopg2.errors.UndefinedFunction):
                        pass
                    
                    try:
                        cur.execute("SELECT create_hypertable('atlas_thread_pattern', 'first_seen', if_not_exists => TRUE);")
                    except (psycopg2.errors.DuplicateTable, psycopg2.errors.UndefinedFunction):
                        pass
                    
                    try:
                        cur.execute("SELECT create_hypertable('atlas_cross_thread_insight', 'created_at', if_not_exists => TRUE);")
                    except (psycopg2.errors.DuplicateTable, psycopg2.errors.UndefinedFunction):
                        pass
                
                # Create indexes for efficient querying
                cur.execute("CREATE INDEX IF NOT EXISTS idx_query_response_thread ON atlas_query_response_relationship (thread_id, created_at DESC);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_query_response_similarity ON atlas_query_response_relationship (similarity_score DESC);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_thread_pattern_type ON atlas_thread_pattern (pattern_type, confidence DESC);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_cross_thread_type ON atlas_cross_thread_insight (insight_type, confidence DESC);")
                
                # Create vector indexes (if pgvector available)
                try:
                    # Check if pgvector is available
                    cur.execute("SELECT 1 FROM pg_type WHERE typname = 'vector';")
                    has_vector = cur.fetchone() is not None
                    
                    if has_vector:
                        cur.execute("CREATE INDEX IF NOT EXISTS idx_atlas_thread_embedding ON atlas_thread USING hnsw (embedding vector_cosine_ops);")
                    else:
                        # Fallback to regular index
                        cur.execute("CREATE INDEX IF NOT EXISTS idx_atlas_thread_embedding ON atlas_thread USING gin (embedding);")
                except (psycopg2.errors.FeatureNotSupported, psycopg2.errors.DatatypeMismatch):
                    # Rollback and try fallback
                    conn.rollback()
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_atlas_thread_embedding ON atlas_thread USING gin (embedding);")
                
                conn.commit()
    
    def create_thread(self, title: str, session_id: str = None, metadata: dict = None) -> str:
        """Create a new conversation thread."""
        thread_id = f"thread_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        if not session_id:
            session_id = f"session_{thread_id}"
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # Create thread embedding
                thread_embedding = self.embedder.encode(title)
                
                cur.execute("""
                    INSERT INTO atlas_thread (thread_id, session_id, title, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (thread_id) DO UPDATE SET
                        last_activity = NOW(),
                        metadata = EXCLUDED.metadata
                """, (
                    thread_id,
                    session_id,
                    title,
                    json.dumps(metadata or {}),
                    thread_embedding.tolist()
                ))
                conn.commit()
        
        return thread_id
    
    def add_conversation_turn(self, thread_id: str, role: str, content: str, 
                            metadata: dict = None) -> str:
        """Add a conversation turn to a thread."""
        turn_id = f"turn_{thread_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # Enhanced metadata
                enhanced_metadata = {
                    "role": role,
                    "thread_id": thread_id,
                    "turn_id": turn_id,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }
                
                # Get embedding
                embedding = self.embedder.encode(content)
                
                # Store in atlas_node
                cur.execute("""
                    INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    turn_id,
                    "conversation",
                    f"{role}: {content[:100]}...",
                    content,
                    json.dumps(enhanced_metadata),
                    embedding.tolist(),
                    datetime.now() + timedelta(hours=48)
                ))
                
                # Update thread activity
                cur.execute("""
                    UPDATE atlas_thread 
                    SET last_activity = NOW()
                    WHERE thread_id = %s
                """, (thread_id,))
                
                conn.commit()
        
        return turn_id
    
    def analyze_query_response_relationships(self, thread_id: str) -> list[QueryResponseRelationship]:
        """Analyze relationships between queries and responses in a thread."""
        relationships = []
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all conversation turns in the thread
                cur.execute("""
                    SELECT node_id, content, metadata, created_at
                    FROM atlas_node 
                    WHERE metadata->>'thread_id' = %s 
                    AND node_type = 'conversation'
                    ORDER BY created_at
                """, (thread_id,))
                
                turns = cur.fetchall()
                
                # Find query-response pairs
                for i in range(len(turns) - 1):
                    current_turn = turns[i]
                    next_turn = turns[i + 1]
                    
                    current_metadata = json.loads(current_turn['metadata']) if current_turn['metadata'] else {}
                    next_metadata = json.loads(next_turn['metadata']) if next_turn['metadata'] else {}
                    
                    # Check if this is a user->assistant pair
                    if (current_metadata.get('role') == 'user' and 
                        next_metadata.get('role') == 'assistant'):
                        
                        # Calculate similarity
                        query_embedding = self.embedder.encode(current_turn['content'])
                        response_embedding = self.embedder.encode(next_turn['content'])
                        similarity_score = self._cosine_similarity(query_embedding, response_embedding)
                        
                        # Calculate response time
                        response_time = (next_turn['created_at'] - current_turn['created_at']).total_seconds()
                        
                        # Extract topic tags
                        topic_tags = self._extract_topic_tags(current_turn['content'], next_turn['content'])
                        
                        # Determine relationship type
                        relationship_type = self._determine_relationship_type(
                            current_turn['content'], next_turn['content']
                        )
                        
                        relationship = QueryResponseRelationship(
                            relationship_id=f"rel_{thread_id}_{int(time.time())}_{i}",
                            query_id=current_turn['node_id'],
                            response_id=next_turn['node_id'],
                            thread_id=thread_id,
                            session_id=current_metadata.get('session_id', ''),
                            similarity_score=similarity_score,
                            response_time=response_time,
                            topic_tags=topic_tags,
                            relationship_type=relationship_type,
                            created_at=current_turn['created_at']
                        )
                        
                        relationships.append(relationship)
                        
                        # Store relationship in database
                        self._store_query_response_relationship(relationship)
        
        return relationships
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _extract_topic_tags(self, query_content: str, response_content: str) -> list[str]:
        """Extract topic tags from query-response pair."""
        # Project-specific topics
        project_topics = [
            "RAGChecker", "DSPy", "memory system", "Atlas", "graph storage",
            "conversation", "decision", "suggestion", "backlog", "PRD",
            "evaluation", "baseline", "precision", "recall", "F1 score",
            "vector", "embedding", "pgvector", "PostgreSQL", "database",
            "chunking", "retrieval", "generation", "optimization", "thread",
            "timescale", "pattern", "insight", "relationship"
        ]
        
        combined_content = (query_content + " " + response_content).lower()
        found_topics = []
        
        for topic in project_topics:
            if topic.lower() in combined_content:
                found_topics.append(topic)
        
        return found_topics
    
    def _determine_relationship_type(self, query_content: str, response_content: str) -> str:
        """Determine the type of relationship between query and response."""
        query_lower = query_content.lower()
        response_lower = response_content.lower()
        
        if "?" in query_content and "here" in response_lower:
            return "direct_reply"
        elif "follow up" in query_lower or "also" in query_lower:
            return "follow_up"
        elif "clarify" in query_lower or "what do you mean" in query_lower:
            return "clarification"
        elif "more" in query_lower or "expand" in query_lower:
            return "expansion"
        else:
            return "direct_reply"
    
    def _store_query_response_relationship(self, relationship: QueryResponseRelationship):
        """Store query-response relationship in database."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO atlas_query_response_relationship 
                    (relationship_id, query_id, response_id, thread_id, session_id, 
                     similarity_score, response_time, topic_tags, relationship_type, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (relationship_id) DO UPDATE SET
                        similarity_score = EXCLUDED.similarity_score,
                        response_time = EXCLUDED.response_time,
                        topic_tags = EXCLUDED.topic_tags
                """, (
                    relationship.relationship_id,
                    relationship.query_id,
                    relationship.response_id,
                    relationship.thread_id,
                    relationship.session_id,
                    relationship.similarity_score,
                    relationship.response_time,
                    relationship.topic_tags,
                    relationship.relationship_type,
                    relationship.created_at
                ))
                conn.commit()
    
    def discover_thread_patterns(self, thread_id: str) -> list[ThreadPattern]:
        """Discover patterns within a thread."""
        patterns = []
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all relationships for this thread
                cur.execute("""
                    SELECT * FROM atlas_query_response_relationship
                    WHERE thread_id = %s
                    ORDER BY created_at
                """, (thread_id,))
                
                relationships = cur.fetchall()
                
                if not relationships:
                    return patterns
                
                # Analyze question types
                question_types = {}
                for rel in relationships:
                    # Get the query content
                    cur.execute("SELECT content FROM atlas_node WHERE node_id = %s", (rel['query_id'],))
                    query_row = cur.fetchone()
                    if query_row:
                        query_type = self._classify_question_type(query_row['content'])
                        question_types[query_type] = question_types.get(query_type, 0) + 1
                
                # Create patterns for question types
                for question_type, frequency in question_types.items():
                    if frequency >= 2:  # Need at least 2 instances
                        pattern = ThreadPattern(
                            pattern_id=f"pattern_{thread_id}_{question_type}_{int(time.time())}",
                            thread_id=thread_id,
                            pattern_type="question_type",
                            description=f"Frequently asks {question_type} questions ({frequency} times)",
                            confidence=min(frequency / 5.0, 1.0),
                            frequency=frequency,
                            first_seen=relationships[0]['created_at'],
                            last_seen=relationships[-1]['created_at']
                        )
                        patterns.append(pattern)
                
                # Analyze response times
                response_times = [rel['response_time'] for rel in relationships]
                avg_response_time = sum(response_times) / len(response_times)
                
                if avg_response_time < 60:  # Less than 1 minute
                    pattern = ThreadPattern(
                        pattern_id=f"pattern_{thread_id}_fast_response_{int(time.time())}",
                        thread_id=thread_id,
                        pattern_type="response_style",
                        description=f"Fast response pattern (avg {avg_response_time:.1f}s)",
                        confidence=0.8,
                        frequency=len(response_times),
                        first_seen=relationships[0]['created_at'],
                        last_seen=relationships[-1]['created_at']
                    )
                    patterns.append(pattern)
                
                # Store patterns
                for pattern in patterns:
                    self._store_thread_pattern(pattern)
        
        return patterns
    
    def _classify_question_type(self, query_content: str) -> str:
        """Classify the type of question."""
        query_lower = query_content.lower()
        
        if "how" in query_lower:
            return "how_questions"
        elif "what" in query_lower:
            return "what_questions"
        elif "why" in query_lower:
            return "why_questions"
        elif "can you" in query_lower or "could you" in query_lower:
            return "request_questions"
        elif "implement" in query_lower or "create" in query_lower:
            return "implementation_questions"
        elif "fix" in query_lower or "debug" in query_lower:
            return "problem_solving_questions"
        else:
            return "general_questions"
    
    def _store_thread_pattern(self, pattern: ThreadPattern):
        """Store thread pattern in database."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO atlas_thread_pattern 
                    (pattern_id, thread_id, pattern_type, description, confidence, 
                     frequency, first_seen, last_seen)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (pattern_id) DO UPDATE SET
                        confidence = EXCLUDED.confidence,
                        frequency = EXCLUDED.frequency,
                        last_seen = EXCLUDED.last_seen
                """, (
                    pattern.pattern_id,
                    pattern.thread_id,
                    pattern.pattern_type,
                    pattern.description,
                    pattern.confidence,
                    pattern.frequency,
                    pattern.first_seen,
                    pattern.last_seen
                ))
                conn.commit()
    
    def analyze_cross_thread_insights(self, time_window_hours: int = 24) -> list[CrossThreadInsight]:
        """Analyze insights across multiple threads."""
        insights = []
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Find similar threads based on topic tags
                cur.execute("""
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
                """, (start_time, end_time))
                
                for row in cur.fetchall():
                    insight = CrossThreadInsight(
                        insight_id=f"similar_threads_{int(time.time())}_{hash(str([row['thread1'], row['thread2']])) % 1000}",
                        insight_type="similar_threads",
                        description=f"Threads {row['thread1']} and {row['thread2']} share {row['shared_topics']} topics: {', '.join(row['common_topics'][:3])}",
                        confidence=min(row['shared_topics'] / 5.0, 1.0),
                        affected_threads=[row['thread1'], row['thread2']],
                        supporting_evidence=[{
                            "shared_topics": row['shared_topics'],
                            "common_topics": row['common_topics']
                        }],
                        created_at=end_time
                    )
                    insights.append(insight)
                
                # Find temporal patterns
                cur.execute("""
                    WITH hourly_activity AS (
                        SELECT 
                            thread_id,
                            EXTRACT(HOUR FROM created_at) as hour_of_day,
                            COUNT(*) as activity_count
                        FROM atlas_query_response_relationship
                        WHERE created_at BETWEEN %s AND %s
                        GROUP BY thread_id, EXTRACT(HOUR FROM created_at)
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
                """, (start_time, end_time))
                
                for row in cur.fetchall():
                    insight = CrossThreadInsight(
                        insight_id=f"temporal_{int(time.time())}_{int(row['hour_of_day'])}",
                        insight_type="temporal_patterns",
                        description=f"Peak activity at hour {int(row['hour_of_day'])} across {row['thread_count']} threads",
                        confidence=min(row['thread_count'] / 5.0, 1.0),
                        affected_threads=[],  # Would need to get specific thread IDs
                        supporting_evidence=[{
                            "hour_of_day": int(row['hour_of_day']),
                            "thread_count": row['thread_count'],
                            "avg_activity": float(row['avg_activity'])
                        }],
                        created_at=end_time
                    )
                    insights.append(insight)
                
                # Store insights
                for insight in insights:
                    self._store_cross_thread_insight(insight)
        
        return insights
    
    def _store_cross_thread_insight(self, insight: CrossThreadInsight):
        """Store cross-thread insight in database."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO atlas_cross_thread_insight 
                    (insight_id, insight_type, description, confidence, 
                     affected_threads, supporting_evidence, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (insight_id) DO UPDATE SET
                        confidence = EXCLUDED.confidence,
                        supporting_evidence = EXCLUDED.supporting_evidence
                """, (
                    insight.insight_id,
                    insight.insight_type,
                    insight.description,
                    insight.confidence,
                    insight.affected_threads,
                    json.dumps(insight.supporting_evidence),
                    insight.created_at
                ))
                conn.commit()
    
    def get_thread_summary(self, thread_id: str) -> dict[str, Any]:
        """Get comprehensive summary of a thread."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get thread info
                cur.execute("SELECT * FROM atlas_thread WHERE thread_id = %s", (thread_id,))
                thread_info = cur.fetchone()
                
                if not thread_info:
                    return {"error": "Thread not found"}
                
                # Get relationship stats
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_relationships,
                        AVG(similarity_score) as avg_similarity,
                        AVG(response_time) as avg_response_time,
                        ARRAY_AGG(DISTINCT UNNEST(topic_tags)) as all_topics
                    FROM atlas_query_response_relationship
                    WHERE thread_id = %s
                """, (thread_id,))
                
                rel_stats = cur.fetchone()
                
                # Get patterns
                cur.execute("""
                    SELECT pattern_type, description, confidence, frequency
                    FROM atlas_thread_pattern
                    WHERE thread_id = %s
                    ORDER BY confidence DESC
                """, (thread_id,))
                
                patterns = [dict(row) for row in cur.fetchall()]
                
                return {
                    "thread_id": thread_id,
                    "title": thread_info['title'],
                    "status": thread_info['status'],
                    "created_at": thread_info['created_at'],
                    "last_activity": thread_info['last_activity'],
                    "relationships": {
                        "total": rel_stats['total_relationships'] or 0,
                        "avg_similarity": float(rel_stats['avg_similarity'] or 0.0),
                        "avg_response_time": float(rel_stats['avg_response_time'] or 0.0),
                        "topics": rel_stats['all_topics'] or []
                    },
                    "patterns": patterns
                }
    
    def get_cross_thread_dashboard(self) -> dict[str, Any]:
        """Get dashboard view of cross-thread insights."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get active threads
                cur.execute("""
                    SELECT COUNT(*) as active_threads
                    FROM atlas_thread
                    WHERE status = 'active'
                """)
                active_threads = cur.fetchone()['active_threads']
                
                # Get recent insights
                cur.execute("""
                    SELECT insight_type, description, confidence, created_at
                    FROM atlas_cross_thread_insight
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    ORDER BY confidence DESC
                    LIMIT 10
                """)
                
                recent_insights = [dict(row) for row in cur.fetchall()]
                
                # Get topic distribution
                cur.execute("""
                    SELECT 
                        UNNEST(topic_tags) as topic,
                        COUNT(*) as frequency
                    FROM atlas_query_response_relationship
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY UNNEST(topic_tags)
                    ORDER BY frequency DESC
                    LIMIT 10
                """)
                
                topic_distribution = [dict(row) for row in cur.fetchall()]
                
                return {
                    "active_threads": active_threads,
                    "recent_insights": recent_insights,
                    "topic_distribution": topic_distribution,
                    "last_updated": datetime.now().isoformat()
                }


def main():
    """Test the unified graph system."""
    print("🔗 Testing Atlas Unified Graph System")
    
    system = AtlasUnifiedGraphSystem()
    
    # Create test threads
    thread1 = system.create_thread("RAGChecker Optimization", metadata={"topic": "performance"})
    thread2 = system.create_thread("Atlas Graph Storage", metadata={"topic": "memory"})
    
    print(f"✅ Created threads: {thread1}, {thread2}")
    
    # Add conversation turns
    system.add_conversation_turn(thread1, "user", "How can we improve RAGChecker precision?")
    system.add_conversation_turn(thread1, "assistant", "Here are several strategies to improve precision...")
    
    system.add_conversation_turn(thread2, "user", "I want to implement graph storage for conversations")
    system.add_conversation_turn(thread2, "assistant", "Great idea! Let me show you how to implement Atlas...")
    
    # Analyze relationships
    relationships1 = system.analyze_query_response_relationships(thread1)
    relationships2 = system.analyze_query_response_relationships(thread2)
    
    print(f"✅ Thread 1 relationships: {len(relationships1)}")
    print(f"✅ Thread 2 relationships: {len(relationships2)}")
    
    # Discover patterns
    patterns1 = system.discover_thread_patterns(thread1)
    patterns2 = system.discover_thread_patterns(thread2)
    
    print(f"✅ Thread 1 patterns: {len(patterns1)}")
    print(f"✅ Thread 2 patterns: {len(patterns2)}")
    
    # Analyze cross-thread insights
    insights = system.analyze_cross_thread_insights()
    print(f"✅ Cross-thread insights: {len(insights)}")
    
    # Get summaries
    summary1 = system.get_thread_summary(thread1)
    summary2 = system.get_thread_summary(thread2)
    
    print(f"✅ Thread 1 summary: {summary1['relationships']['total']} relationships")
    print(f"✅ Thread 2 summary: {summary2['relationships']['total']} relationships")
    
    # Get dashboard
    dashboard = system.get_cross_thread_dashboard()
    print(f"✅ Dashboard: {dashboard['active_threads']} active threads")
    
    print("🎯 Unified graph system is working!")


if __name__ == "__main__":
    main()
