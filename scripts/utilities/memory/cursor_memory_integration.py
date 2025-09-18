#!/usr/bin/env python3
"""
Memory consolidation integration for Cursor AI conversations.
Processes captured conversations with advanced NLP features.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any

from psycopg.rows import DictRow

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config

# Set environment variable for memory graph
os.environ["APP_USE_MEMORY_GRAPH"] = "true"

# Import memory consolidation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from memory_graphs.consolidate import ConsolidationResult
from memory_graphs.consolidate import run as consolidate_memory


class CursorMemoryIntegration:
    """Memory consolidation integration for Cursor conversations."""

    def __init__(self, role: str = "default"):
        self.role = role
        print("🧠 Memory Integration initialized")

    def process_conversation_turns(self, thread_id: str, session_id: str) -> dict[str, object]:
        """Process conversation turns with memory consolidation."""
        print(f"🔄 Processing conversation turns for thread {thread_id}")

        try:
            with Psycopg3Config.get_cursor(self.role) as cur:
                # Get conversation turns
                cur.execute(
                    """
                    SELECT turn_id, role, content, timestamp, metadata
                    FROM atlas_conversation_turn 
                    WHERE thread_id = %s
                    ORDER BY timestamp
                """,
                    (thread_id,),
                )

                turns_data: list[dict[str, Any]] = cur.fetchall()

                if not turns_data:
                    print("⚠️  No conversation turns found")
                    return {}

                # Convert to format expected by memory consolidation
                turns: list[dict[str, object]] = []
                for row in turns_data:
                    turn_id = row["turn_id"]
                    role = row["role"]
                    content = row["content"]
                    timestamp = row["timestamp"]
                    metadata = row["metadata"]
                    # Normalize metadata to a dictionary
                    meta: dict[str, object] = {}
                    if metadata:
                        if isinstance(metadata, (bytes | bytearray)):
                            try:
                                meta = json.loads(metadata.decode("utf-8", "ignore"))
                            except Exception:
                                meta = {}
                        elif isinstance(metadata, str):
                            try:
                                meta: Any = json.loads(metadata)
                            except Exception:
                                meta = {}
                        elif isinstance(metadata, dict):
                            meta = metadata

                    turn: dict[str, object] = {
                        "turn_id": turn_id,
                        "role": role,
                        "content": content,
                        "timestamp": timestamp.isoformat() if timestamp else datetime.now().isoformat(),
                        "metadata": meta,
                    }
                    turns.append(turn)

                print(f"📝 Processing {len(turns)} conversation turns...")

                # Run memory consolidation
                result = consolidate_memory(turns)

                if result:
                    # Store consolidation results
                    self._store_consolidation_results(cur, thread_id, session_id, result)

                    summary_text = getattr(result, "summary", "")
                    facts_list = getattr(result, "facts", [])
                    entities_list = getattr(result, "entities", [])
                    links_list = getattr(result, "entity_links", [])
                    processing_meta = getattr(result, "processing_metadata", {})

                    print("✅ Memory consolidation completed")
                    print(f"   Summary: {summary_text[:100]}...")
                    print(f"   Facts extracted: {len(facts_list)}")
                    print(f"   Entities found: {len(entities_list)}")
                    print(f"   Entity links: {len(links_list)}")

                    return {
                        "success": True,
                        "summary": summary_text,
                        "facts_count": len(facts_list),
                        "entities_count": len(entities_list),
                        "entity_links_count": len(links_list),
                        "processing_metadata": processing_meta,
                    }
                else:
                    print("❌ Memory consolidation failed")
                    return {"success": False, "error": "Consolidation failed"}

        except Exception as e:
            print(f"❌ Error processing conversation turns: {e}")
            return {"success": False, "error": str(e)}

    def _store_consolidation_results(
        self,
        cur: Any,
        thread_id: str,
        session_id: str,
        result: ConsolidationResult,
    ) -> None:
        """Store memory consolidation results in the database."""
        try:
            # Store summary in atlas_node
            summary_node_id = f"summary_{thread_id}_{int(time.time())}"
            cur.execute(
                """
                INSERT INTO atlas_node 
                (node_id, node_type, title, content, metadata, created_at, updated_at, session_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (node_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    updated_at = EXCLUDED.updated_at
            """,
                (
                    summary_node_id,
                    "conversation_summary",
                    f"Summary: {result.summary[:50]}...",
                    result.summary,
                    json.dumps(
                        {
                            "thread_id": thread_id,
                            "session_id": session_id,
                            "consolidation_type": "memory_graph",
                            "processing_metadata": result.processing_metadata,
                        }
                    ),
                    datetime.now(),
                    datetime.now(),
                    session_id,
                ),
            )

            # Store facts
            for i, fact in enumerate(getattr(result, "facts", [])):
                fact_node_id = f"fact_{thread_id}_{i}_{int(time.time())}"
                cur.execute(
                    """
                    INSERT INTO atlas_node 
                    (node_id, node_type, title, content, metadata, created_at, updated_at, session_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        updated_at = EXCLUDED.updated_at
                """,
                    (
                        fact_node_id,
                        "fact",
                        f"Fact: {getattr(fact, 'text', '')[:50]}...",
                        getattr(fact, "text", ""),
                        json.dumps(
                            {
                                "fact_type": getattr(fact, "fact_type", ""),
                                "confidence": getattr(fact, "confidence", 0.0),
                                "source_turn_id": getattr(fact, "source_turn", -1),
                                "thread_id": thread_id,
                                "session_id": session_id,
                            }
                        ),
                        datetime.now(),
                        datetime.now(),
                        session_id,
                    ),
                )

                # Create edge to summary
                cur.execute(
                    """
                    INSERT INTO atlas_edge 
                    (edge_id, source_node_id, target_node_id, edge_type, weight, metadata, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (edge_id) DO NOTHING
                """,
                    (
                        f"edge_{fact_node_id}_{summary_node_id}",
                        fact_node_id,
                        summary_node_id,
                        "supports",
                        getattr(fact, "confidence", 0.0),
                        json.dumps({"relationship": "fact_to_summary"}),
                        datetime.now(),
                    ),
                )

            # Store entities
            entity_id_by_text: dict[str, str] = {}
            for i, entity in enumerate(getattr(result, "entities", [])):
                entity_node_id = f"entity_{thread_id}_{i}_{int(time.time())}"
                entity_id_by_text[getattr(entity, "text", str(i))] = entity_node_id
                cur.execute(
                    """
                    INSERT INTO atlas_node 
                    (node_id, node_type, title, content, metadata, created_at, updated_at, session_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        updated_at = EXCLUDED.updated_at
                """,
                    (
                        entity_node_id,
                        "entity",
                        f"Entity: {getattr(entity, 'text', '')}",
                        getattr(entity, "text", ""),
                        json.dumps(
                            {
                                "entity_type": getattr(entity, "entity_type", ""),
                                "confidence": getattr(entity, "confidence", 0.0),
                                "context": getattr(entity, "context", ""),
                                "aliases": getattr(entity, "aliases", []),
                                "thread_id": thread_id,
                                "session_id": session_id,
                            }
                        ),
                        datetime.now(),
                        datetime.now(),
                        session_id,
                    ),
                )

            # Store entity links
            for i, link in enumerate(getattr(result, "entity_links", [])):
                link_id = f"link_{thread_id}_{i}_{int(time.time())}"
                cur.execute(
                    """
                    INSERT INTO atlas_edge 
                    (edge_id, source_node_id, target_node_id, edge_type, weight, metadata, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (edge_id) DO NOTHING
                """,
                    (
                        link_id,
                        entity_id_by_text.get(getattr(link, "source_entity", ""), ""),
                        entity_id_by_text.get(getattr(link, "target_entity", ""), ""),
                        getattr(link, "relationship_type", "related_to"),
                        getattr(link, "confidence", 0.0),
                        json.dumps({"relationship": "entity_link", "thread_id": thread_id, "session_id": session_id}),
                        datetime.now(),
                    ),
                )

            print("✅ Consolidation results stored in database")

        except Exception as e:
            print(f"❌ Error storing consolidation results: {e}")
            raise

    def get_thread_insights(self, thread_id: str) -> dict[str, object]:
        """Get insights for a specific thread."""
        try:
            with Psycopg3Config.get_cursor(self.role) as cur:
                # Get thread info
                cur.execute(
                    """
                    SELECT title, content, metadata, created_at, last_activity
                    FROM atlas_thread 
                    WHERE thread_id = %s
                """,
                    (thread_id,),
                )

                row: dict[str, Any] | None = cur.fetchone()
                if not row:
                    return {"error": "Thread not found"}
                title = row["title"]
                content = row["content"]
                _metadata = row["metadata"]
                created_at = row["created_at"]
                last_activity = row["last_activity"]

                # Get conversation turns count
                cur.execute(
                    """
                    SELECT COUNT(*) FROM atlas_conversation_turn 
                    WHERE thread_id = %s
                """,
                    (thread_id,),
                )
                rc: dict[str, Any] | None = cur.fetchone()
                turns_count = int(rc["count"]) if rc is not None else 0

                # Get facts count
                cur.execute(
                    """
                    SELECT COUNT(*) FROM atlas_node 
                    WHERE node_type = 'fact' AND metadata->>'thread_id' = %s
                """,
                    (thread_id,),
                )
                rc: dict[str, Any] | None = cur.fetchone()
                facts_count = int(rc["count"]) if rc is not None else 0

                # Get entities count
                cur.execute(
                    """
                    SELECT COUNT(*) FROM atlas_node 
                    WHERE node_type = 'entity' AND metadata->>'thread_id' = %s
                """,
                    (thread_id,),
                )
                rc: dict[str, Any] | None = cur.fetchone()
                entities_count = int(rc["count"]) if rc is not None else 0

                # Get summary
                cur.execute(
                    """
                    SELECT content FROM atlas_node 
                    WHERE node_type = 'conversation_summary' AND metadata->>'thread_id' = %s
                    ORDER BY created_at DESC LIMIT 1
                """,
                    (thread_id,),
                )
                summary_data: dict[str, Any] | None = cur.fetchone()
                summary = summary_data["content"] if summary_data else None

                return {
                    "thread_id": thread_id,
                    "title": title,
                    "content": content,
                    "turns_count": turns_count,
                    "facts_count": facts_count,
                    "entities_count": entities_count,
                    "summary": summary,
                    "created_at": created_at.isoformat() if created_at else None,
                    "last_activity": last_activity.isoformat() if last_activity else None,
                }

        except Exception as e:
            print(f"❌ Error getting thread insights: {e}")
            return {"error": str(e)}


def main() -> Any:
    """Test the memory integration system."""
    print("🧠 Testing Memory Integration System")
    print("=" * 50)

    # Initialize memory integration
    memory = CursorMemoryIntegration()

    # Test with a sample thread (you would get this from the capture system)
    test_thread_id = "test_thread_123"
    test_session_id = "test_session_123"

    print(f"📝 Testing memory consolidation for thread {test_thread_id}")

    # Process conversation turns
    result: Any = memory.process_conversation_turns(test_thread_id, test_session_id)

    if result.get("success"):
        print("✅ Memory consolidation successful")
        print(f"   Facts: {result['facts_count']}")
        print(f"   Entities: {result['entities_count']}")
        print(f"   Entity Links: {result['entity_links_count']}")
    else:
        print(f"❌ Memory consolidation failed: {result.get('error')}")

    print("\n🎉 Memory integration test completed!")


if __name__ == "__main__":
    main()
