from __future__ import annotations
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any
import sys
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Episodic Memory Mock Implementation

Mock version of episodic memory for testing without database dependencies.
This allows us to test the implementation logic before setting up the full database.
"""

@dataclass
class EpisodicReflection:
    """Represents a reflection on a completed task or conversation."""

    agent: str
    task_type: str
    summary: str
    what_worked: list[str]
    what_to_avoid: list[str]
    outcome_metrics: dict[str, Any]
    source_refs: dict[str, Any]
    span_hash: str
    created_at: datetime | None = None
    id: int | None = None

@dataclass
class EpisodicContext:
    """Context retrieved from episodic memory for current task."""

    similar_episodes: list[EpisodicReflection]
    what_worked_bullets: list[str]
    what_to_avoid_bullets: list[str]
    confidence_score: float
    retrieval_time_ms: float

class MockEpisodicReflectionStore:
    """Mock implementation of episodic reflection store for testing."""

    def __init__(self):
        """Initialize the mock store."""
        self.reflections: list[EpisodicReflection] = []
        self.next_id = 1

        # Configuration
        self.max_what_worked_items = 5
        self.max_what_to_avoid_items = 5
        self.max_episodes_retrieved = 3
        self.similarity_threshold = 0.1  # Lower threshold for testing

        # Add some sample data for testing
        self._add_sample_data()

    def _add_sample_data(self):
        """Add sample reflections for testing."""
        sample_reflections = [
            {
                "agent": "cursor_ai",
                "task_type": "coding",
                "summary": "Successfully implemented a new feature with proper error handling",
                "what_worked": [
                    "Used proper error handling with try-catch blocks",
                    "Added comprehensive unit tests",
                    "Followed existing code patterns",
                ],
                "what_to_avoid": [
                    "Don't skip error handling for edge cases",
                    "Avoid hardcoding values that should be configurable",
                ],
                "outcome_metrics": {"success": True, "test_coverage": 0.95},
                "source_refs": {"files": ["src/feature.py", "tests/test_feature.py"]},
            },
            {
                "agent": "cursor_ai",
                "task_type": "debugging",
                "summary": "Fixed a memory leak in the data processing pipeline",
                "what_worked": [
                    "Used memory profiling to identify the leak",
                    "Implemented proper resource cleanup",
                    "Added monitoring for memory usage",
                ],
                "what_to_avoid": [
                    "Don't ignore memory usage warnings",
                    "Avoid keeping large objects in memory unnecessarily",
                ],
                "outcome_metrics": {"success": True, "memory_reduction": "60%"},
                "source_refs": {"files": ["src/processor.py"], "issue": "B-1234"},
            },
            {
                "agent": "dspy_agent",
                "task_type": "optimization",
                "summary": "Optimized DSPy model performance by adjusting hyperparameters",
                "what_worked": [
                    "Used systematic hyperparameter tuning",
                    "Measured performance before and after changes",
                    "Documented all parameter changes",
                ],
                "what_to_avoid": [
                    "Don't change multiple parameters simultaneously",
                    "Avoid optimizing without measuring baseline performance",
                ],
                "outcome_metrics": {"success": True, "performance_improvement": "25%"},
                "source_refs": {"files": ["dspy-rag-system/src/optimizer.py"]},
            },
        ]

        for sample in sample_reflections:
            reflection = EpisodicReflection(
                id=self.next_id,
                agent=sample["agent"],
                task_type=sample["task_type"],
                summary=sample["summary"],
                what_worked=sample["what_worked"],
                what_to_avoid=sample["what_to_avoid"],
                outcome_metrics=sample["outcome_metrics"],
                source_refs=sample["source_refs"],
                span_hash=f"sample_{self.next_id}",
                created_at=datetime.now(),
            )
            self.reflections.append(reflection)
            self.next_id += 1

    def store_reflection(self, reflection: EpisodicReflection) -> bool:
        """Store an episodic reflection."""
        try:
            reflection.id = self.next_id
            reflection.created_at = datetime.now()
            self.reflections.append(reflection)
            self.next_id += 1
            print(f"✅ Stored reflection {reflection.id} for agent {reflection.agent}")
            return True
        except Exception as e:
            print(f"❌ Failed to store reflection: {e}")
            return False

    def retrieve_similar_episodes(
        self, query: str, agent: str | None = None, limit: int | None = None
    ) -> list[EpisodicReflection]:
        """Retrieve similar episodes using simple keyword matching."""
        if limit is None:
            limit = self.max_episodes_retrieved

        try:
            # Simple keyword-based similarity (in real implementation, this would use embeddings)
            query_lower = query.lower()
            scored_episodes = []

            for episode in self.reflections:
                if agent and episode.agent != agent:
                    continue

                # Calculate simple similarity score based on keyword overlap
                episode_text = (
                    f"{episode.summary} {' '.join(episode.what_worked)} {' '.join(episode.what_to_avoid)}".lower()
                )
                query_words = set(query_lower.split())
                episode_words = set(episode_text.split())

                if query_words and episode_words:
                    similarity = len(query_words.intersection(episode_words)) / len(query_words.union(episode_words))
                else:
                    similarity = 0.0

                if similarity >= self.similarity_threshold:
                    scored_episodes.append((episode, similarity))

            # Sort by similarity and return top results
            scored_episodes.sort(key=lambda x: x[1], reverse=True)
            return [episode for episode, score in scored_episodes[:limit]]

        except Exception as e:
            print(f"❌ Failed to retrieve similar episodes: {e}")
            return []

    def get_episodic_context(self, query: str, agent: str | None = None) -> EpisodicContext:
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
            days_old = (datetime.now() - (latest_episode.created_at or datetime.min)).days
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
        outcome_metrics: dict[str, Any] | None = None,
        source_refs: dict[str, Any] | None = None,
    ) -> EpisodicReflection:
        """Generate a reflection from a completed task."""

        # Generate span hash
        span_hash = f"task_{hash(task_description + input_text + output_text) % 10000}"

        # Create a simple summary
        summary = f"Completed {task_type} task: {task_description[:100]}..."

        # Generate more realistic what_worked and what_to_avoid based on task type
        if "database" in task_type.lower():
            what_worked = [
                "Used proper connection pooling",
                "Implemented retry logic for failed connections",
                "Added comprehensive error logging",
            ]
            what_to_avoid = ["Don't leave database connections open", "Avoid hardcoding connection strings"]
        elif "error" in task_description.lower():
            what_worked = [
                "Used try-catch blocks for error handling",
                "Added specific error messages for debugging",
                "Implemented graceful degradation",
            ]
            what_to_avoid = ["Don't ignore error conditions", "Avoid generic error messages"]
        else:
            what_worked = ["Task completed successfully", "No errors encountered", "Followed existing patterns"]
            what_to_avoid = ["Avoid similar patterns that caused issues", "Don't skip validation steps"]

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

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about stored reflections."""
        return {
            "total_reflections": len(self.reflections),
            "unique_agents": len(set(r.agent for r in self.reflections)),
            "unique_task_types": len(set(r.task_type for r in self.reflections)),
            "avg_what_worked_items": (
                sum(len(r.what_worked) for r in self.reflections) / len(self.reflections) if self.reflections else 0
            ),
            "avg_what_to_avoid_items": (
                sum(len(r.what_to_avoid) for r in self.reflections) / len(self.reflections) if self.reflections else 0
            ),
        }

def test_episodic_memory():
    """Test the mock episodic memory implementation."""
    print("🧠 Testing Mock Episodic Memory Implementation...")

    # Create store
    store = MockEpisodicReflectionStore()

    # Test storing a reflection
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
        print(f"   Confidence: {context.confidence_score:.2f}")

        # Test stats
        stats = store.get_stats()
        print(f"✅ Stats: {stats}")

        # Test with sample data
        print("\n🔍 Testing with sample data...")
        coding_context = store.get_episodic_context("implement feature with error handling", "cursor_ai")
        print(f"✅ Coding context: {len(coding_context.similar_episodes)} episodes")
        print(f"   What worked: {coding_context.what_worked_bullets}")
        print(f"   What to avoid: {coding_context.what_to_avoid_bullets}")

        debugging_context = store.get_episodic_context("fix memory leak", "cursor_ai")
        print(f"✅ Debugging context: {len(debugging_context.similar_episodes)} episodes")
        print(f"   What worked: {debugging_context.what_worked_bullets}")
        print(f"   What to avoid: {debugging_context.what_to_avoid_bullets}")

        return True
    else:
        print("❌ Failed to store reflection")
        return False

if __name__ == "__main__":
    success = test_episodic_memory()
    if success:
        print("\n🎉 Mock episodic memory implementation working correctly!")
    else:
        print("\n❌ Mock episodic memory implementation failed")
