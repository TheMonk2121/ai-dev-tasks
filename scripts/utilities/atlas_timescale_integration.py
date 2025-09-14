#!/usr/bin/env python3
"""
Atlas TimescaleDB Integration
Time-series analysis for conversation patterns and cross-thread relationships
"""

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer


@dataclass
class ConversationMetrics:
    """Time-series metrics for conversation analysis."""
    timestamp: datetime
    thread_id: str
    query_count: int
    reply_count: int
    avg_response_time: float  # seconds
    topic_diversity: float
    engagement_score: float


@dataclass
class CrossThreadInsight:
    """Insights from cross-thread analysis."""
    insight_id: str
    pattern_type: str
    description: str
    confidence: float
    affected_threads: list[str]
    first_observed: datetime
    last_observed: datetime


class AtlasTimescaleIntegration:
    """TimescaleDB integration for conversation time-series analysis."""
    
    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.embedder = SentenceTransformer("BAAI/bge-large-en-v1.5")
        
        # Ensure TimescaleDB extension and hypertables
        self._setup_timescale_tables()
    
    def _setup_timescale_tables(self):
        """Set up TimescaleDB hypertables for time-series analysis."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # Enable TimescaleDB extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                
                # Create conversation_metrics hypertable
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_metrics (
                        timestamp TIMESTAMPTZ NOT NULL,
                        thread_id TEXT NOT NULL,
                        query_count INTEGER DEFAULT 0,
                        reply_count INTEGER DEFAULT 0,
                        avg_response_time FLOAT DEFAULT 0.0,
                        topic_diversity FLOAT DEFAULT 0.0,
                        engagement_score FLOAT DEFAULT 0.0,
                        metadata JSONB DEFAULT '{}'
                    );
                """)
                
                # Convert to hypertable if not already
                try:
                    cur.execute("SELECT create_hypertable('conversation_metrics', 'timestamp', if_not_exists => TRUE);")
                except psycopg2.errors.DuplicateTable:
                    pass  # Already a hypertable
                
                # Create cross_thread_insights table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS cross_thread_insights (
                        timestamp TIMESTAMPTZ NOT NULL,
                        insight_id TEXT NOT NULL,
                        pattern_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        confidence FLOAT NOT NULL,
                        affected_threads TEXT[] NOT NULL,
                        metadata JSONB DEFAULT '{}'
                    );
                """)
                
                # Convert to hypertable
                try:
                    cur.execute("SELECT create_hypertable('cross_thread_insights', 'timestamp', if_not_exists => TRUE);")
                except psycopg2.errors.DuplicateTable:
                    pass
                
                # Create indexes for efficient querying
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversation_metrics_thread_time 
                    ON conversation_metrics (thread_id, timestamp DESC);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cross_thread_insights_type_time 
                    ON cross_thread_insights (pattern_type, timestamp DESC);
                """)
                
                conn.commit()
    
    def record_conversation_metrics(self, thread_id: str, time_window: int = 3600) -> ConversationMetrics:
        """Record conversation metrics for a thread over a time window."""
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=time_window)
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get conversation data for time window
                cur.execute("""
                    SELECT 
                        COUNT(CASE WHEN metadata->>'role' = 'user' THEN 1 END) as query_count,
                        COUNT(CASE WHEN metadata->>'role' = 'assistant' THEN 1 END) as reply_count,
                        AVG(EXTRACT(EPOCH FROM (
                            SELECT created_at FROM atlas_node r 
                            WHERE r.metadata->>'role' = 'assistant' 
                            AND r.metadata->>'thread_id' = %s
                            AND r.created_at > q.created_at
                            ORDER BY r.created_at LIMIT 1
                        ) - q.created_at)) as avg_response_time
                    FROM atlas_node q
                    WHERE q.metadata->>'thread_id' = %s
                    AND q.created_at BETWEEN %s AND %s
                    AND q.node_type = 'conversation'
                """, (thread_id, thread_id, start_time, end_time))
                
                metrics_row = cur.fetchone()
                
                # Calculate topic diversity
                cur.execute("""
                    SELECT DISTINCT 
                        UNNEST(STRING_TO_ARRAY(LOWER(content), ' ')) as word
                    FROM atlas_node 
                    WHERE metadata->>'thread_id' = %s
                    AND created_at BETWEEN %s AND %s
                    AND node_type = 'conversation'
                """, (thread_id, start_time, end_time))
                
                words = [row['word'] for row in cur.fetchall()]
                topic_diversity = len(set(words)) / max(len(words), 1)
                
                # Calculate engagement score (queries per hour)
                query_count = metrics_row['query_count'] or 0
                engagement_score = query_count / (time_window / 3600.0)
                
                metrics = ConversationMetrics(
                    timestamp=end_time,
                    thread_id=thread_id,
                    query_count=query_count,
                    reply_count=metrics_row['reply_count'] or 0,
                    avg_response_time=float(metrics_row['avg_response_time'] or 0.0),
                    topic_diversity=topic_diversity,
                    engagement_score=engagement_score
                )
                
                # Store metrics
                cur.execute("""
                    INSERT INTO conversation_metrics 
                    (timestamp, thread_id, query_count, reply_count, avg_response_time, topic_diversity, engagement_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    metrics.timestamp,
                    metrics.thread_id,
                    metrics.query_count,
                    metrics.reply_count,
                    metrics.avg_response_time,
                    metrics.topic_diversity,
                    metrics.engagement_score
                ))
                
                conn.commit()
                
                return metrics
    
    def analyze_cross_thread_patterns(self, time_window_hours: int = 24) -> list[CrossThreadInsight]:
        """Analyze patterns across threads over time."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        insights = []
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Find threads with similar query patterns
                cur.execute("""
                    WITH thread_queries AS (
                        SELECT 
                            metadata->>'thread_id' as thread_id,
                            content as query_content,
                            created_at
                        FROM atlas_node 
                        WHERE metadata->>'role' = 'user'
                        AND created_at BETWEEN %s AND %s
                        AND node_type = 'conversation'
                    ),
                    similar_queries AS (
                        SELECT 
                            t1.thread_id as thread1,
                            t2.thread_id as thread2,
                            COUNT(*) as similarity_count
                        FROM thread_queries t1
                        JOIN thread_queries t2 ON t1.thread_id != t2.thread_id
                        WHERE t1.query_content <-> t2.query_content < 0.7
                        GROUP BY t1.thread_id, t2.thread_id
                        HAVING COUNT(*) >= 2
                    )
                    SELECT 
                        thread1,
                        thread2,
                        similarity_count,
                        ARRAY[thread1, thread2] as affected_threads
                    FROM similar_queries
                    ORDER BY similarity_count DESC
                """, (start_time, end_time))
                
                for row in cur.fetchall():
                    insight = CrossThreadInsight(
                        insight_id=f"similarity_{int(time.time())}_{hash(str(row['affected_threads'])) % 1000}",
                        pattern_type="similar_query_patterns",
                        description=f"Threads {row['thread1']} and {row['thread2']} have {row['similarity_count']} similar queries",
                        confidence=min(row['similarity_count'] / 5.0, 1.0),
                        affected_threads=row['affected_threads'],
                        first_observed=start_time,
                        last_observed=end_time
                    )
                    insights.append(insight)
                
                # Find temporal patterns (queries at similar times)
                cur.execute("""
                    WITH hourly_activity AS (
                        SELECT 
                            metadata->>'thread_id' as thread_id,
                            EXTRACT(HOUR FROM created_at) as hour_of_day,
                            COUNT(*) as query_count
                        FROM atlas_node 
                        WHERE metadata->>'role' = 'user'
                        AND created_at BETWEEN %s AND %s
                        AND node_type = 'conversation'
                        GROUP BY metadata->>'thread_id', EXTRACT(HOUR FROM created_at)
                    ),
                    peak_hours AS (
                        SELECT 
                            thread_id,
                            hour_of_day,
                            query_count,
                            RANK() OVER (PARTITION BY thread_id ORDER BY query_count DESC) as rank
                        FROM hourly_activity
                    )
                    SELECT 
                        hour_of_day,
                        COUNT(DISTINCT thread_id) as thread_count,
                        AVG(query_count) as avg_queries
                    FROM peak_hours
                    WHERE rank = 1
                    GROUP BY hour_of_day
                    HAVING COUNT(DISTINCT thread_id) >= 2
                    ORDER BY thread_count DESC
                """, (start_time, end_time))
                
                for row in cur.fetchall():
                    insight = CrossThreadInsight(
                        insight_id=f"temporal_{int(time.time())}_{int(row['hour_of_day'])}",
                        pattern_type="temporal_pattern",
                        description=f"Peak activity at hour {int(row['hour_of_day'])} across {row['thread_count']} threads",
                        confidence=min(row['thread_count'] / 5.0, 1.0),
                        affected_threads=[],  # Would need to get specific thread IDs
                        first_observed=start_time,
                        last_observed=end_time
                    )
                    insights.append(insight)
                
                # Store insights
                for insight in insights:
                    cur.execute("""
                        INSERT INTO cross_thread_insights 
                        (timestamp, insight_id, pattern_type, description, confidence, affected_threads)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        insight.last_observed,
                        insight.insight_id,
                        insight.pattern_type,
                        insight.description,
                        insight.confidence,
                        insight.affected_threads
                    ))
                
                conn.commit()
        
        return insights
    
    def get_thread_activity_timeline(self, thread_id: str, hours: int = 24) -> list[dict[str, Any]]:
        """Get activity timeline for a thread."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        time_bucket('1 hour', timestamp) as hour_bucket,
                        AVG(query_count) as avg_queries,
                        AVG(reply_count) as avg_replies,
                        AVG(engagement_score) as avg_engagement,
                        AVG(topic_diversity) as avg_diversity
                    FROM conversation_metrics
                    WHERE thread_id = %s
                    AND timestamp BETWEEN %s AND %s
                    GROUP BY hour_bucket
                    ORDER BY hour_bucket
                """, (thread_id, start_time, end_time))
                
                timeline = []
                for row in cur.fetchall():
                    timeline.append({
                        "hour": row['hour_bucket'],
                        "queries": float(row['avg_queries'] or 0),
                        "replies": float(row['avg_replies'] or 0),
                        "engagement": float(row['avg_engagement'] or 0),
                        "diversity": float(row['avg_diversity'] or 0)
                    })
                
                return timeline
    
    def get_cross_thread_summary(self, hours: int = 24) -> dict[str, Any]:
        """Get summary of cross-thread activity."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get total activity
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT thread_id) as active_threads,
                        SUM(query_count) as total_queries,
                        SUM(reply_count) as total_replies,
                        AVG(engagement_score) as avg_engagement
                    FROM conversation_metrics
                    WHERE timestamp BETWEEN %s AND %s
                """, (start_time, end_time))
                
                activity = cur.fetchone()
                
                # Get top insights
                cur.execute("""
                    SELECT 
                        pattern_type,
                        description,
                        confidence,
                        affected_threads
                    FROM cross_thread_insights
                    WHERE timestamp BETWEEN %s AND %s
                    ORDER BY confidence DESC
                    LIMIT 5
                """, (start_time, end_time))
                
                insights = [dict(row) for row in cur.fetchall()]
                
                return {
                    "time_window": f"{hours} hours",
                    "active_threads": activity['active_threads'] or 0,
                    "total_queries": activity['total_queries'] or 0,
                    "total_replies": activity['total_replies'] or 0,
                    "avg_engagement": float(activity['avg_engagement'] or 0.0),
                    "top_insights": insights
                }


def main():
    """Test TimescaleDB integration."""
    print("⏰ Testing Atlas TimescaleDB Integration")
    
    timescale = AtlasTimescaleIntegration()
    
    # Record metrics for a test thread
    test_thread_id = "test_timescale_thread"
    metrics = timescale.record_conversation_metrics(test_thread_id)
    print(f"✅ Recorded metrics: {metrics.query_count} queries, {metrics.engagement_score:.2f} engagement")
    
    # Analyze cross-thread patterns
    insights = timescale.analyze_cross_thread_patterns()
    print(f"✅ Found {len(insights)} cross-thread insights")
    
    # Get timeline
    timeline = timescale.get_thread_activity_timeline(test_thread_id)
    print(f"✅ Timeline: {len(timeline)} hourly buckets")
    
    # Get summary
    summary = timescale.get_cross_thread_summary()
    print(f"✅ Summary: {summary['active_threads']} threads, {summary['total_queries']} queries")
    
    print("🎯 TimescaleDB integration is working!")


if __name__ == "__main__":
    main()
