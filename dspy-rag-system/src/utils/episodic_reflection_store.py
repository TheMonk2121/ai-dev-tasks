"""
Episodic Reflection Store

Extends the LTST Memory System with episodic memory capabilities for learning from past work.
Provides reflection generation, storage, and retrieval for improved task performance.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def _maybe_json_loads(val: Any) -> Any:
    """Return parsed JSON if val is a JSON string; otherwise return val.

    Psycopg2 with JSONB may already return Python types. Avoid double-parsing.
    """
    if isinstance(val, (dict, list)):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return val
    return val


@dataclass
class EpisodicReflection:
    """Represents a reflection on a completed task or conversation."""

    agent: str
    task_type: str
    summary: str
    what_worked: List[str]
    what_to_avoid: List[str]
    outcome_metrics: Dict[str, Any]
    source_refs: Dict[str, Any]
    span_hash: str
    created_at: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class EpisodicContext:
    """Context retrieved from episodic memory for current task."""

    similar_episodes: List[EpisodicReflection]
    what_worked_bullets: List[str]
    what_to_avoid_bullets: List[str]
    confidence_score: float
    retrieval_time_ms: float


class EpisodicReflectionStore:
    """Stores and retrieves episodic reflections for learning from past work."""

    def __init__(self, db_connection=None):
        """Initialize the episodic reflection store."""
        self.db_connection = db_connection
        self.embedder = None  # Will be initialized when needed

        # Configuration
        self.max_what_worked_items = 5
        self.max_what_to_avoid_items = 5
        self.max_episodes_retrieved = 3
        self.similarity_threshold = 0.7

    def _get_db_connection(self):
        """Get database connection, creating one if needed."""
        if self.db_connection is None:
            # Use your existing database connection logic
            import os

            dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
            self.db_connection = psycopg2.connect(dsn)
        return self.db_connection

    def _get_embedder(self):
        """Get embedder for generating vector embeddings."""
        if self.embedder is None:
            try:
                # Use your existing embedder from the LTST system
                from .context_merger import ContextMerger

                _ = ContextMerger  # mark as used to satisfy linters
                # This is a placeholder - you'll need to adapt to your actual embedder
                self.embedder = "placeholder_embedder"
            except ImportError:
                logger.warning("Could not import embedder, using mock embeddings")
                self.embedder = "mock_embedder"
        return self.embedder

    def _generate_span_hash(self, input_text: str, output_text: str) -> str:
        """Generate a stable hash for the input/output span."""
        combined = f"{input_text}|{output_text}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        embedder = self._get_embedder()
        if embedder == "mock_embedder":
            # Mock embedding for testing
            return [0.1] * 384
        else:
            # Use your actual embedder
            # This is a placeholder - implement with your actual embedder
            return [0.1] * 384

    def store_reflection(self, reflection: EpisodicReflection) -> bool:
        """Store an episodic reflection in the database."""
        try:
            conn = self._get_db_connection()
            with conn.cursor() as cursor:
                # Generate embedding for the summary
                embedding = self._generate_embedding(reflection.summary)

                # Create search vector for full-text search
                search_text = (
                    f"{reflection.summary} {' '.join(reflection.what_worked)} {' '.join(reflection.what_to_avoid)}"
                )

                # Insert the reflection
                cursor.execute(
                    """
                    INSERT INTO episodic_reflections (
                        agent, task_type, summary, what_worked, what_to_avoid,
                        outcome_metrics, source_refs, span_hash, embedding, search_vector
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, to_tsvector('english', %s)
                    ) RETURNING id, created_at
                """,
                    (
                        reflection.agent,
                        reflection.task_type,
                        reflection.summary,
                        json.dumps(reflection.what_worked),
                        json.dumps(reflection.what_to_avoid),
                        json.dumps(reflection.outcome_metrics),
                        json.dumps(reflection.source_refs),
                        reflection.span_hash,
                        embedding,
                        search_text,
                    ),
                )

                result = cursor.fetchone()
                if not result:
                    raise RuntimeError("Insert returned no row; unable to populate reflection id/timestamp")
                reflection.id = result[0]
                reflection.created_at = result[1]

                conn.commit()
                logger.info(f"Stored episodic reflection {reflection.id} for agent {reflection.agent}")
                return True

        except Exception as e:
            logger.error(f"Failed to store episodic reflection: {e}")
            return False

    def retrieve_similar_episodes(
        self, query: str, agent: Optional[str] = None, limit: Optional[int] = None
    ) -> List[EpisodicReflection]:
        """Retrieve similar episodes using hybrid search (vector + text)."""
        if limit is None:
            limit = self.max_episodes_retrieved

        try:
            conn = self._get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Generate query embedding
                query_embedding = self._generate_embedding(query)

                # Build the query with optional agent filter
                agent_filter = "AND agent = %s" if agent else ""
                agent_param = [agent] if agent else []

                # Hybrid search: combine vector similarity and text search
                cursor.execute(
                    f"""
                    SELECT
                        id, agent, task_type, summary, what_worked, what_to_avoid,
                        outcome_metrics, source_refs, span_hash, created_at,
                        (1 - (embedding <=> %s)) as cosine_similarity,
                        ts_rank(search_vector, to_tsquery('english', %s)) as text_rank
                    FROM episodic_reflections
                    WHERE
                        (1 - (embedding <=> %s)) > %s
                        {agent_filter}
                    ORDER BY
                        (0.6 * (1 - (embedding <=> %s)) + 0.4 * ts_rank(search_vector, to_tsquery('english', %s))) DESC
                    LIMIT %s
                """,
                    [
                        query_embedding,  # cosine_similarity
                        query.replace(" ", " & "),  # text_rank
                        query_embedding,  # vector filter
                        self.similarity_threshold,  # similarity threshold
                        query_embedding,  # ordering vector
                        query.replace(" ", " & "),  # ordering text
                        limit,
                    ]
                    + agent_param,
                )

                episodes = []
                for row in cursor.fetchall():
                    episode = EpisodicReflection(
                        id=row["id"],
                        agent=row["agent"],
                        task_type=row["task_type"],
                        summary=row["summary"],
                        what_worked=_maybe_json_loads(row.get("what_worked")),
                        what_to_avoid=_maybe_json_loads(row.get("what_to_avoid")),
                        outcome_metrics=_maybe_json_loads(row.get("outcome_metrics")),
                        source_refs=_maybe_json_loads(row.get("source_refs")),
                        span_hash=row["span_hash"],
                        created_at=row["created_at"],
                    )
                    episodes.append(episode)

                logger.info(f"Retrieved {len(episodes)} similar episodes for query: {query[:50]}...")
                return episodes

        except Exception as e:
            logger.error(f"Failed to retrieve similar episodes: {e}")
            return []

    def get_episodic_context(self, query: str, agent: Optional[str] = None) -> EpisodicContext:
        """Get episodic context for a query, including compressed bullets."""
        start_time = time.time()

        # Retrieve similar episodes
        episodes = self.retrieve_similar_episodes(query, agent)

        # Compress what_worked and what_to_avoid into bullets
        what_worked_bullets = []
        what_to_avoid_bullets = []

        for episode in episodes:
            what_worked_bullets.extend(episode.what_worked[:2])  # Take top 2 from each
            what_to_avoid_bullets.extend(episode.what_to_avoid[:2])  # Take top 2 from each

        # Deduplicate and limit
        what_worked_bullets = list(dict.fromkeys(what_worked_bullets))[: self.max_what_worked_items]
        what_to_avoid_bullets = list(dict.fromkeys(what_to_avoid_bullets))[: self.max_what_to_avoid_items]

        # Calculate confidence score based on number of episodes and recency
        confidence_score = min(len(episodes) / self.max_episodes_retrieved, 1.0)
        if episodes:
            # Boost confidence for recent episodes
            latest_episode = max(episodes, key=lambda e: e.created_at or datetime.min)
            latest_created_at = latest_episode.created_at or datetime.min
            days_old = (datetime.now() - latest_created_at).days
            if days_old < 7:
                confidence_score *= 1.2

        retrieval_time_ms = (time.time() - start_time) * 1000

        return EpisodicContext(
            similar_episodes=episodes,
            what_worked_bullets=what_worked_bullets,
            what_to_avoid_bullets=what_to_avoid_bullets,
            confidence_score=min(confidence_score, 1.0),
            retrieval_time_ms=retrieval_time_ms,
        )

    def generate_reflection_from_task(
        self,
        task_description: str,
        input_text: str,
        output_text: str,
        agent: str = "cursor_ai",
        task_type: str = "general",
        outcome_metrics: Optional[Dict[str, Any]] = None,
        source_refs: Optional[Dict[str, Any]] = None,
    ) -> EpisodicReflection:
        """Generate a reflection from a completed task."""

        # Generate span hash
        span_hash = self._generate_span_hash(input_text, output_text)

        # Create a simple summary (in a real implementation, you'd use an LLM)
        summary = f"Completed {task_type} task: {task_description[:100]}..."

        # Placeholder what_worked and what_to_avoid
        # In a real implementation, you'd analyze the task execution
        what_worked = ["Task completed successfully", "No errors encountered"]

        what_to_avoid = ["Avoid similar patterns that caused issues"]

        if outcome_metrics is None:
            outcome_metrics = {"success": True, "completion_time": "unknown"}

        if source_refs is None:
            source_refs = {"task_description": task_description}

        return EpisodicReflection(
            agent=agent,
            task_type=task_type,
            summary=summary,
            what_worked=what_worked,
            what_to_avoid=what_to_avoid,
            outcome_metrics=outcome_metrics,
            source_refs=source_refs,
            span_hash=span_hash,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored reflections."""
        try:
            conn = self._get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_reflections,
                        COUNT(DISTINCT agent) as unique_agents,
                        COUNT(DISTINCT task_type) as unique_task_types,
                        AVG(jsonb_array_length(what_worked)) as avg_what_worked_items,
                        AVG(jsonb_array_length(what_to_avoid)) as avg_what_to_avoid_items
                    FROM episodic_reflections
                """
                )

                result = cursor.fetchone()
                if not result:
                    return {
                        "total_reflections": 0,
                        "unique_agents": 0,
                        "unique_task_types": 0,
                        "avg_what_worked_items": 0.0,
                        "avg_what_to_avoid_items": 0.0,
                    }

                return {
                    "total_reflections": result[0],
                    "unique_agents": result[1],
                    "unique_task_types": result[2],
                    "avg_what_worked_items": float(result[3]) if result[3] else 0.0,
                    "avg_what_to_avoid_items": float(result[4]) if result[4] else 0.0,
                }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            # Offline/mock mode can return zeroed stats to keep system stable
            import os

            dsn = os.getenv("POSTGRES_DSN", "")
            if (
                os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1"
                or os.getenv("EPISODIC_OFFLINE_OK", "0") == "1"
                or dsn.startswith("mock://")
            ):
                return {
                    "total_reflections": 0,
                    "unique_agents": 0,
                    "unique_task_types": 0,
                    "avg_what_worked_items": 0.0,
                    "avg_what_to_avoid_items": 0.0,
                }
            return {}


def create_episodic_reflections_table():
    """Create the episodic_reflections table in the database."""
    try:
        import os

        dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        conn = psycopg2.connect(dsn)

        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS episodic_reflections (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    agent VARCHAR(100) NOT NULL,
                    task_type VARCHAR(100) NOT NULL,
                    summary TEXT NOT NULL,
                    what_worked JSONB NOT NULL DEFAULT '[]',
                    what_to_avoid JSONB NOT NULL DEFAULT '[]',
                    outcome_metrics JSONB NOT NULL DEFAULT '{}',
                    source_refs JSONB NOT NULL DEFAULT '{}',
                    span_hash VARCHAR(64) NOT NULL,
                    embedding VECTOR(384),
                    search_vector TSVECTOR
                );

                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_episodic_reflections_agent ON episodic_reflections(agent);
                CREATE INDEX IF NOT EXISTS idx_episodic_reflections_task_type ON episodic_reflections(task_type);
                CREATE INDEX IF NOT EXISTS idx_episodic_reflections_span_hash ON episodic_reflections(span_hash);
                CREATE INDEX IF NOT EXISTS idx_episodic_reflections_created_at ON episodic_reflections(created_at);

                -- Vector similarity index
                CREATE INDEX IF NOT EXISTS idx_episodic_reflections_embedding
                ON episodic_reflections USING hnsw (embedding vector_cosine_ops);

                -- Full-text search index
                CREATE INDEX IF NOT EXISTS idx_episodic_reflections_search_vector
                ON episodic_reflections USING gin (search_vector);
            """
            )

            conn.commit()
            print("✅ Created episodic_reflections table with indexes")
            return True

    except Exception as e:
        print(f"❌ Failed to create episodic_reflections table: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    # Test the episodic reflection store
    print("🧠 Testing Episodic Reflection Store...")

    # Create the table
    if create_episodic_reflections_table():
        print("✅ Table created successfully")

        # Test storing a reflection
        store = EpisodicReflectionStore()
        reflection = store.generate_reflection_from_task(
            task_description="Test task for episodic memory",
            input_text="Test input",
            output_text="Test output",
            agent="test_agent",
            task_type="testing",
        )

        if store.store_reflection(reflection):
            print("✅ Reflection stored successfully")

            # Test retrieval
            context = store.get_episodic_context("test task", "test_agent")
            print(f"✅ Retrieved context with {len(context.similar_episodes)} episodes")
            print(f"   What worked: {context.what_worked_bullets}")
            print(f"   What to avoid: {context.what_to_avoid_bullets}")

            # Test stats
            stats = store.get_stats()
            print(f"✅ Stats: {stats}")
        else:
            print("❌ Failed to store reflection")
    else:
        print("❌ Failed to create table")
