#!/usr/bin/env python3
"""
Cursor Atlas Integration
Automatically captures Cursor conversations and stores them in the Atlas graph system
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any

import psycopg2

# Add src to path for memory consolidation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from .atlas_graph_storage import AtlasGraphStorage

# Import memory consolidation
try:
    from memory_graphs.consolidate import run as consolidate_memory
except ImportError:
    # Fallback for when running as script
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
    from memory_graphs.consolidate import run as consolidate_memory


class CursorAtlasIntegration:
    """Integrates Cursor conversations with Atlas graph storage."""

    def __init__(self, dsn: str | None = None) -> None:
        resolved_dsn = (
            dsn or os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL") or "postgresql://localhost:5432/ai_agency"
        )
        self.atlas: AtlasGraphStorage = AtlasGraphStorage(resolved_dsn)
        self.session_id: str = self._get_or_create_session_id()

    def _get_or_create_session_id(self) -> str:
        """Get or create a session ID for this Cursor session."""
        # Try to get from environment or create new
        session_id = os.getenv("CURSOR_SESSION_ID")
        if not session_id:
            session_id = f"cursor_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
            print(f"🆔 Created new Cursor session: {session_id}")
        else:
            print(f"🔄 Using existing Cursor session: {session_id}")
        return session_id

    def capture_user_message(
        self, content: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> str:
        """Capture a user message and store it in Atlas."""
        print(f"👤 Capturing user message: {content[:100]}...")

        metadata = metadata or {}
        metadata.update({"message_type": "user", "timestamp": datetime.now().isoformat(), "cursor_session": True})

        # Extract related concepts from the message
        related_nodes = self._extract_related_concepts(content)

        turn_id = self.atlas.store_conversation_turn(
            session_id=self.session_id, role="user", content=content, metadata=metadata, related_nodes=related_nodes
        )

        print(f"✅ Stored user message: {turn_id}")
        return turn_id

    def capture_assistant_response(
        self, content: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> str:
        """Capture an assistant response and store it in Atlas."""
        print(f"🤖 Capturing assistant response: {content[:100]}...")

        metadata = metadata or {}
        metadata.update({"message_type": "assistant", "timestamp": datetime.now().isoformat(), "cursor_session": True})

        # Extract related concepts from the response
        related_nodes = self._extract_related_concepts(content)

        turn_id = self.atlas.store_conversation_turn(
            session_id=self.session_id,
            role="assistant",
            content=content,
            metadata=metadata,
            related_nodes=related_nodes,
        )

        print(f"✅ Stored assistant response: {turn_id}")
        return turn_id

    def process_conversation_with_memory_consolidation(
        self, conversation_turns: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Process a conversation using the memory consolidation system."""
        print("🧠 Processing conversation with memory consolidation...")

        try:
            # Run memory consolidation
            result = consolidate_memory(conversation_turns)

            print("✅ Memory consolidation completed:")
            print(f"   Summary: {result.summary[:100]}...")
            print(f"   Facts extracted: {len(result.facts)}")
            print(f"   Entities found: {len(result.entities)}")
            print(f"   Entity links: {len(result.entity_links)}")

            # Store the consolidated results
            consolidation_id = self._store_consolidation_results(result)

            return {
                "status": "success",
                "consolidation_id": consolidation_id,
                "summary": result.summary,
                "facts_count": len(result.facts),
                "entities_count": len(result.entities),
                "links_count": len(result.entity_links),
                "processing_time": result.processing_metadata.get("processing_time", 0),
            }

        except Exception as e:
            print(f"❌ Memory consolidation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    def _store_consolidation_results(self, result: Any) -> str:
        """Store memory consolidation results in the database."""
        consolidation_id = f"consolidation_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"

        with psycopg2.connect(self.atlas.dsn) as conn:
            with conn.cursor() as cur:
                # Store consolidation summary
                cur.execute(
                    """
                    INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        consolidation_id,
                        "memory_consolidation",
                        f"Memory Consolidation: {result.summary[:50]}...",
                        result.summary,
                        json.dumps(
                            {
                                "facts_count": len(result.facts),
                                "entities_count": len(result.entities),
                                "links_count": len(result.entity_links),
                                "processing_time": result.processing_metadata.get("processing_time", 0),
                                "turns_processed": result.processing_metadata.get("turns_processed", 0),
                            }
                        ),
                        [0.0] * 1024,  # Placeholder embedding
                        datetime.now() + timedelta(hours=48),
                    ),
                )

                conn.commit()

        return consolidation_id

    def _extract_related_concepts(self, content: str) -> list[str]:
        """Extract related concepts from content for graph connections."""
        concepts = []

        # Look for project-specific concepts
        project_concepts = [
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
        ]

        content_lower = content.lower()
        for concept in project_concepts:
            if concept.lower() in content_lower:
                concept_id = concept.replace(" ", "_").lower()
                # Ensure the concept node exists
                self._ensure_concept_node_exists(concept_id, concept)
                concepts.append(concept_id)

        return concepts

    def _ensure_concept_node_exists(self, concept_id: str, concept_name: str) -> None:
        """Ensure a concept node exists in the Atlas graph."""
        with psycopg2.connect(self.atlas.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO NOTHING
                """,
                    (
                        concept_id,
                        "concept",
                        concept_name,
                        f"Concept: {concept_name}",
                        json.dumps({"concept_type": "project_concept"}),
                        self.atlas.get_embedding(concept_name).tolist(),
                        datetime.now() + timedelta(days=30),
                    ),
                )
                conn.commit()

    def get_conversation_context(self, limit: int = 10) -> dict[str, Any]:
        """Get conversation context for memory rehydration."""
        print(f"🧠 Getting conversation context for session: {self.session_id}")

        # Get the conversation graph
        graph = self.atlas.get_conversation_graph(self.session_id)

        # Get recent related conversations
        recent_conversations = self.atlas.search_related_conversations("conversation context memory", limit=limit)

        return {
            "session_id": self.session_id,
            "conversation_graph": graph,
            "recent_conversations": recent_conversations,
            "total_nodes": len(graph["nodes"]),
            "total_edges": len(graph["edges"]),
        }

    def store_conversation_turn(
        self, role: str, content: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> str:
        """Store a conversation turn (user or assistant)."""
        if role == "user":
            return self.capture_user_message(content, metadata)
        elif role == "assistant":
            return self.capture_assistant_response(content, metadata)
        else:
            raise ValueError(f"Unknown role: {role}")

    def get_memory_context(self) -> str:
        """Get formatted memory context for Cursor."""
        context = self.get_conversation_context()

        # Format the context for Cursor
        context_text = f"""
## 🧠 Cursor Memory Context

**Session ID**: {context['session_id']}
**Total Nodes**: {context['total_nodes']}
**Total Edges**: {context['total_edges']}

### Recent Conversation Graph
"""

        # Add recent nodes
        for node in context["conversation_graph"]["nodes"][-5:]:  # Last 5 nodes
            context_text += f"- **{node['type']}**: {node['title']}\n"

        # Add recent edges
        if context["conversation_graph"]["edges"]:
            context_text += "\n### Recent Connections\n"
            for edge in context["conversation_graph"]["edges"][-3:]:  # Last 3 edges
                context_text += f"- {edge['source']} --[{edge['type']}]--> {edge['target']}\n"

        return context_text


def main() -> None:
    """Test the Cursor Atlas integration."""
    integration = CursorAtlasIntegration()

    # Simulate a conversation
    print("🔄 Simulating Cursor conversation...")

    # User message
    _ = integration.capture_user_message(
        "I think we should implement the Atlas graph storage system. It would preserve connections between conversations and decisions much better than the current vector-only approach."
    )

    # Assistant response
    _ = integration.capture_assistant_response(
        "You're absolutely right! A graph structure would preserve the connections between queries, conversations, and context much better than just storing isolated vectors. Let me search for your previous git commits on this topic to follow the trail."
    )

    # Get memory context
    context = integration.get_memory_context()
    print("\n" + context)

    print("🎯 Cursor Atlas integration is working!")


if __name__ == "__main__":
    main()
