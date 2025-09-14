#!/usr/bin/env python3
"""
Atlas Thread Manager
Manages multiple concurrent chat threads with proper session isolation and cross-thread analysis
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
class ChatThread:
    """A chat thread with metadata and relationships."""
    thread_id: str
    session_id: str
    title: str
    created_at: datetime
    last_activity: datetime
    status: str  # 'active', 'paused', 'archived'
    metadata: dict[str, Any]


@dataclass
class CrossThreadPattern:
    """Patterns discovered across multiple threads."""
    pattern_id: str
    query_pattern: str
    response_pattern: str
    thread_count: int
    confidence: float
    first_seen: datetime
    last_seen: datetime


class AtlasThreadManager:
    """Manages multiple chat threads and cross-thread analysis."""
    
    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.embedder = SentenceTransformer("BAAI/bge-large-en-v1.5")
        self.embedding_dim = 1024
        
        # Thread management
        self.active_threads = {}  # thread_id -> ChatThread
        self.thread_relationships = {}  # thread_id -> [related_thread_ids]
    
    def create_thread(self, title: str = None, metadata: dict = None) -> ChatThread:
        """Create a new chat thread."""
        thread_id = f"thread_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        session_id = f"session_{thread_id}"
        
        thread = ChatThread(
            thread_id=thread_id,
            session_id=session_id,
            title=title or f"Chat Thread {len(self.active_threads) + 1}",
            created_at=datetime.now(),
            last_activity=datetime.now(),
            status='active',
            metadata=metadata or {}
        )
        
        self.active_threads[thread_id] = thread
        self._store_thread_metadata(thread)
        
        return thread
    
    def get_or_create_thread(self, thread_identifier: str) -> ChatThread:
        """Get existing thread or create new one."""
        # Try to find by thread_id first
        if thread_identifier in self.active_threads:
            return self.active_threads[thread_identifier]
        
        # Try to find in database
        existing_thread = self._find_thread_by_identifier(thread_identifier)
        if existing_thread:
            self.active_threads[existing_thread.thread_id] = existing_thread
            return existing_thread
        
        # Create new thread
        return self.create_thread(title=f"Thread: {thread_identifier}")
    
    def add_conversation_turn(self, thread_id: str, role: str, content: str, 
                            metadata: dict = None) -> str:
        """Add a conversation turn to a specific thread."""
        thread = self.get_or_create_thread(thread_id)
        
        # Update thread activity
        thread.last_activity = datetime.now()
        thread.status = 'active'
        
        # Store conversation turn with thread context
        turn_id = self._store_conversation_turn(thread, role, content, metadata)
        
        # Update thread metadata
        self._update_thread_activity(thread)
        
        return turn_id
    
    def _store_conversation_turn(self, thread: ChatThread, role: str, content: str, 
                               metadata: dict = None) -> str:
        """Store conversation turn with thread context."""
        turn_id = f"turn_{thread.thread_id}_{int(time.time())}"
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # Enhanced metadata with thread context
                enhanced_metadata = {
                    "role": role,
                    "session_id": thread.session_id,
                    "thread_id": thread.thread_id,
                    "thread_title": thread.title,
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
                
                conn.commit()
        
        return turn_id
    
    def _store_thread_metadata(self, thread: ChatThread):
        """Store thread metadata in database."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (node_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    thread.thread_id,
                    "thread",
                    thread.title,
                    f"Chat thread: {thread.title}",
                    json.dumps({
                        "thread_id": thread.thread_id,
                        "session_id": thread.session_id,
                        "title": thread.title,
                        "status": thread.status,
                        "created_at": thread.created_at.isoformat(),
                        "last_activity": thread.last_activity.isoformat()
                    }),
                    self.embedder.encode(thread.title).tolist(),
                    datetime.now() + timedelta(days=30)  # Threads last longer
                ))
                conn.commit()
    
    def _find_thread_by_identifier(self, identifier: str) -> ChatThread | None:
        """Find thread by various identifiers."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT node_id, title, metadata, created_at
                    FROM atlas_node 
                    WHERE node_type = 'thread'
                    AND (node_id = %s OR metadata->>'thread_id' = %s OR title ILIKE %s)
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (identifier, identifier, f"%{identifier}%"))
                
                row = cur.fetchone()
                if row:
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    return ChatThread(
                        thread_id=row['node_id'],
                        session_id=metadata.get('session_id', f"session_{row['node_id']}"),
                        title=row['title'],
                        created_at=row['created_at'],
                        last_activity=datetime.fromisoformat(metadata.get('last_activity', row['created_at'].isoformat())),
                        status=metadata.get('status', 'active'),
                        metadata=metadata
                    )
        
        return None
    
    def _update_thread_activity(self, thread: ChatThread):
        """Update thread activity timestamp."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE atlas_node 
                    SET metadata = jsonb_set(metadata, '{last_activity}', %s)
                    WHERE node_id = %s
                """, (json.dumps(thread.last_activity.isoformat()), thread.thread_id))
                conn.commit()
    
    def get_active_threads(self) -> list[ChatThread]:
        """Get all active threads."""
        return [t for t in self.active_threads.values() if t.status == 'active']
    
    def get_thread_timeline(self, thread_id: str) -> list[dict[str, Any]]:
        """Get timeline of conversation turns in a thread."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT node_id, content, metadata, created_at
                    FROM atlas_node 
                    WHERE metadata->>'thread_id' = %s 
                    AND node_type = 'conversation'
                    ORDER BY created_at
                """, (thread_id,))
                
                turns = []
                for row in cur.fetchall():
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    turns.append({
                        "turn_id": row['node_id'],
                        "content": row['content'],
                        "role": metadata.get('role', 'unknown'),
                        "timestamp": row['created_at'],
                        "thread_id": thread_id
                    })
                
                return turns
    
    def analyze_cross_thread_patterns(self) -> list[CrossThreadPattern]:
        """Analyze patterns across all threads."""
        patterns = []
        
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all query-reply pairs across threads
                cur.execute("""
                    SELECT 
                        q.metadata->>'thread_id' as thread_id,
                        q.content as query_content,
                        r.content as reply_content,
                        q.created_at as query_time,
                        r.created_at as reply_time
                    FROM atlas_node q
                    JOIN atlas_node r ON r.metadata->>'thread_id' = q.metadata->>'thread_id'
                    WHERE q.metadata->>'role' = 'user'
                    AND r.metadata->>'role' = 'assistant'
                    AND r.created_at > q.created_at
                    AND r.created_at < q.created_at + INTERVAL '1 hour'
                    ORDER BY q.created_at
                """)
                
                query_reply_pairs = cur.fetchall()
                
                # Group by similar query patterns
                query_groups = {}
                for pair in query_reply_pairs:
                    query_key = self._extract_query_pattern(pair['query_content'])
                    if query_key not in query_groups:
                        query_groups[query_key] = []
                    query_groups[query_key].append(pair)
                
                # Create patterns from groups
                for query_pattern, pairs in query_groups.items():
                    if len(pairs) >= 2:  # Need at least 2 instances
                        response_pattern = self._extract_response_pattern([p['reply_content'] for p in pairs])
                        
                        pattern = CrossThreadPattern(
                            pattern_id=f"pattern_{hash(query_pattern) % 10000}",
                            query_pattern=query_pattern,
                            response_pattern=response_pattern,
                            thread_count=len(set(p['thread_id'] for p in pairs)),
                            confidence=min(len(pairs) / 10.0, 1.0),  # Max confidence at 10 instances
                            first_seen=min(p['query_time'] for p in pairs),
                            last_seen=max(p['query_time'] for p in pairs)
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def _extract_query_pattern(self, query_content: str) -> str:
        """Extract pattern from query content."""
        # Simple pattern extraction - could be more sophisticated
        query_lower = query_content.lower()
        
        # Common patterns
        if "how does" in query_lower:
            return "how_does_question"
        elif "what is" in query_lower:
            return "what_is_question"
        elif "why" in query_lower:
            return "why_question"
        elif "can you" in query_lower:
            return "can_you_request"
        elif "implement" in query_lower:
            return "implementation_request"
        elif "fix" in query_lower:
            return "fix_request"
        else:
            return "general_question"
    
    def _extract_response_pattern(self, reply_contents: list[str]) -> str:
        """Extract pattern from response contents."""
        # Analyze common response patterns
        all_replies = " ".join(reply_contents).lower()
        
        if "here's what" in all_replies or "let me" in all_replies:
            return "explanatory_response"
        elif "i'll" in all_replies or "let me implement" in all_replies:
            return "implementation_response"
        elif "you're right" in all_replies or "good point" in all_replies:
            return "agreement_response"
        elif "i think" in all_replies or "i suggest" in all_replies:
            return "suggestion_response"
        else:
            return "general_response"
    
    def get_thread_relationships(self, thread_id: str) -> list[dict[str, Any]]:
        """Get relationships between threads."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Find threads that share similar topics or patterns
                cur.execute("""
                    SELECT DISTINCT 
                        t2.metadata->>'thread_id' as related_thread_id,
                        t2.title as related_title,
                        COUNT(*) as shared_topics
                    FROM atlas_node t1
                    JOIN atlas_node t2 ON t1.metadata->>'thread_id' != t2.metadata->>'thread_id'
                    WHERE t1.metadata->>'thread_id' = %s
                    AND t1.node_type = 'conversation'
                    AND t2.node_type = 'conversation'
                    AND t1.embedding <=> t2.embedding < 0.7  -- Similarity threshold
                    GROUP BY t2.metadata->>'thread_id', t2.title
                    ORDER BY shared_topics DESC
                    LIMIT 5
                """, (thread_id,))
                
                relationships = []
                for row in cur.fetchall():
                    relationships.append({
                        "thread_id": row['related_thread_id'],
                        "title": row['related_title'],
                        "similarity_score": 1.0 - float(row['shared_topics']) / 10.0,  # Convert to similarity
                        "shared_topics": row['shared_topics']
                    })
                
                return relationships


def main():
    """Test the thread manager."""
    print("🧵 Testing Atlas Thread Manager")
    
    manager = AtlasThreadManager()
    
    # Create test threads
    thread1 = manager.create_thread("RAGChecker Optimization", {"topic": "performance"})
    thread2 = manager.create_thread("Atlas Graph Storage", {"topic": "memory"})
    
    print(f"✅ Created threads: {thread1.thread_id}, {thread2.thread_id}")
    
    # Add conversation turns
    manager.add_conversation_turn(thread1.thread_id, "user", "How can we improve RAGChecker precision?")
    manager.add_conversation_turn(thread1.thread_id, "assistant", "Here are several strategies to improve precision...")
    
    manager.add_conversation_turn(thread2.thread_id, "user", "I want to implement graph storage for conversations")
    manager.add_conversation_turn(thread2.thread_id, "assistant", "Great idea! Let me show you how to implement Atlas...")
    
    # Get timelines
    timeline1 = manager.get_thread_timeline(thread1.thread_id)
    timeline2 = manager.get_thread_timeline(thread2.thread_id)
    
    print(f"✅ Thread 1 timeline: {len(timeline1)} turns")
    print(f"✅ Thread 2 timeline: {len(timeline2)} turns")
    
    # Analyze patterns
    patterns = manager.analyze_cross_thread_patterns()
    print(f"✅ Found {len(patterns)} cross-thread patterns")
    
    # Get relationships
    relationships = manager.get_thread_relationships(thread1.thread_id)
    print(f"✅ Thread 1 has {len(relationships)} related threads")
    
    print("🎯 Thread manager is working!")


if __name__ == "__main__":
    main()
