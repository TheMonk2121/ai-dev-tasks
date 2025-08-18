#!/usr/bin/env python3
"""
Context Management Implementation

This module implements the shared context management system that enables seamless
context sharing between Cursor's native AI and specialized agents.

Author: AI Development Team
Date: 2024-08-06
Version: 1.0.0
"""

import json
import logging
import time
import asyncio
import sqlite3
import hashlib
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
import threading
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Enumeration of context types."""
    PROJECT = "project"
    FILE = "file"
    USER = "user"
    AGENT = "agent"


class ContextVisibility(Enum):
    """Enumeration of context visibility levels."""
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


@dataclass
class ContextData:
    """Data structure for context information."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: ContextType = ContextType.FILE
    source: str = "cursor"
    content: dict[str, Any] = field(default_factory=dict)
    relationships: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    owner_id: str | None = None
    permissions: list[str] = field(default_factory=lambda: ["read", "write"])
    visibility: ContextVisibility = ContextVisibility.PRIVATE
    size_bytes: int = 0
    access_count: int = 0


@dataclass
class ContextRelationship:
    """Data structure for context relationships."""
    id: str = field(default_factory=lambda: str(uuid4()))
    source_context_id: str = ""
    target_context_id: str = ""
    relationship_type: str = "related"
    strength: float = 0.85
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class ContextAccessLog:
    """Data structure for context access logs."""
    id: str = field(default_factory=lambda: str(uuid4()))
    context_id: str = ""
    agent_id: str = ""
    operation: str = "read"
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class ContextStore:
    """Database-backed context storage system."""
    
    def __init__(self, db_path: str = "context_store.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create contexts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contexts (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    relationships TEXT,
                    metadata TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    accessed_at REAL NOT NULL,
                    owner_id TEXT,
                    permissions TEXT,
                    visibility TEXT DEFAULT 'private',
                    size_bytes INTEGER DEFAULT 0,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # Create context relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_relationships (
                    id TEXT PRIMARY KEY,
                    source_context_id TEXT NOT NULL,
                    target_context_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL,
                    metadata TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (source_context_id) REFERENCES contexts (id),
                    FOREIGN KEY (target_context_id) REFERENCES contexts (id),
                    UNIQUE(source_context_id, target_context_id, relationship_type)
                )
            """)
            
            # Create context access log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_access_log (
                    id TEXT PRIMARY KEY,
                    context_id TEXT NOT NULL,
                    agent_id TEXT,
                    operation TEXT NOT NULL,
                    user_id TEXT,
                    metadata TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (context_id) REFERENCES contexts (id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_source ON contexts(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_owner ON contexts(owner_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_created ON contexts(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON context_relationships(source_context_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target ON context_relationships(target_context_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_log_context ON context_access_log(context_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_log_agent ON context_access_log(agent_id)")
            
            conn.commit()
            conn.close()
    
    def store_context(self, context: ContextData) -> str:
        """Store context in the database."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate size
            context.size_bytes = len(json.dumps(context.content))
            
            cursor.execute("""
                INSERT OR REPLACE INTO contexts 
                (id, type, source, content, relationships, metadata, created_at, updated_at, accessed_at, 
                 owner_id, permissions, visibility, size_bytes, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                context.id,
                context.type.value,
                context.source,
                json.dumps(context.content),
                json.dumps(context.relationships),
                json.dumps(context.metadata),
                context.created_at,
                context.updated_at,
                context.accessed_at,
                context.owner_id,
                json.dumps(context.permissions),
                context.visibility.value,
                context.size_bytes,
                context.access_count
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored context {context.id} of type {context.type.value}")
            return context.id
    
    def get_context(self, context_id: str) -> ContextData | None:
        """Get context by ID."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, type, source, content, relationships, metadata, created_at, updated_at, accessed_at,
                       owner_id, permissions, visibility, size_bytes, access_count
                FROM contexts WHERE id = ?
            """, (context_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                context = ContextData(
                    id=row[0],
                    type=ContextType(row[1]),
                    source=row[2],
                    content=json.loads(row[3]),
                    relationships=json.loads(row[4]) if row[4] else {},
                    metadata=json.loads(row[5]) if row[5] else {},
                    created_at=row[6],
                    updated_at=row[7],
                    accessed_at=row[8],
                    owner_id=row[9],
                    permissions=json.loads(row[10]) if row[10] else [],
                    visibility=ContextVisibility(row[11]),
                    size_bytes=row[12],
                    access_count=row[13]
                )
                
                # Update access count and timestamp
                self._update_access(context_id)
                return context
            
            return None
    
    def update_context(self, context_id: str, updates: dict[str, Any]) -> bool:
        """Update existing context."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current context
            cursor.execute("SELECT content, metadata FROM contexts WHERE id = ?", (context_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return False
            
            current_content = json.loads(row[0])
            current_metadata = json.loads(row[1]) if row[1] else {}
            
            # Apply updates
            if "content" in updates:
                current_content.update(updates["content"])
            if "metadata" in updates:
                current_metadata.update(updates["metadata"])
            
            # Update context
            cursor.execute("""
                UPDATE contexts 
                SET content = ?, metadata = ?, updated_at = ?, accessed_at = ?
                WHERE id = ?
            """, (
                json.dumps(current_content),
                json.dumps(current_metadata),
                time.time(),
                time.time(),
                context_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated context {context_id}")
            return True
    
    def delete_context(self, context_id: str) -> bool:
        """Delete context by ID."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM contexts WHERE id = ?", (context_id,))
            cursor.execute("DELETE FROM context_relationships WHERE source_context_id = ? OR target_context_id = ?", 
                         (context_id, context_id))
            cursor.execute("DELETE FROM context_access_log WHERE context_id = ?", (context_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted context {context_id}")
            return True
    
    def search_contexts(self, query: str, context_type: str | None = None, 
                       limit: int = 10) -> list[ContextData]:
        """Search contexts by query."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sql = """
                SELECT id, type, source, content, relationships, metadata, created_at, updated_at, accessed_at,
                       owner_id, permissions, visibility, size_bytes, access_count
                FROM contexts 
                WHERE content LIKE ?
            """
            params = [f"%{query}%"]
            
            if context_type:
                sql += " AND type = ?"
                params.append(context_type)
            
            sql += " ORDER BY accessed_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            contexts = []
            for row in rows:
                context = ContextData(
                    id=row[0],
                    type=ContextType(row[1]),
                    source=row[2],
                    content=json.loads(row[3]),
                    relationships=json.loads(row[4]) if row[4] else {},
                    metadata=json.loads(row[5]) if row[5] else {},
                    created_at=row[6],
                    updated_at=row[7],
                    accessed_at=row[8],
                    owner_id=row[9],
                    permissions=json.loads(row[10]) if row[10] else [],
                    visibility=ContextVisibility(row[11]),
                    size_bytes=row[12],
                    access_count=row[13]
                )
                contexts.append(context)
            
            return contexts
    
    def _update_access(self, context_id: str):
        """Update access count and timestamp for context."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE contexts 
                SET accessed_at = ?, access_count = access_count + 1
                WHERE id = ?
            """, (time.time(), context_id))
            
            conn.commit()
            conn.close()


class ContextCache:
    """In-memory cache for frequently accessed context data."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: dict[str, dict[str, Any]] = {}
        self.access_times: dict[str, float] = {}
        self.lock = threading.RLock()
    
    async def get(self, key: str) -> ContextData | None:
        """Get context from cache."""
        with self.lock:
            if key in self.cache:
                cache_entry = self.cache[key]
                if time.time() - cache_entry["timestamp"] < self.ttl:
                    self.access_times[key] = time.time()
                    return cache_entry["context"]
                else:
                    # Expired, remove from cache
                    del self.cache[key]
                    del self.access_times[key]
            return None
    
    async def set(self, key: str, context: ContextData):
        """Store context in cache."""
        with self.lock:
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[key] = {
                "context": context,
                "timestamp": time.time()
            }
            self.access_times[key] = time.time()
    
    async def invalidate(self, key: str):
        """Invalidate cache entry."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.access_times[key]
    
    async def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()


class ContextManager:
    """Main context management system."""
    
    def __init__(self, db_path: str = "context_store.db"):
        self.store = ContextStore(db_path)
        self.cache = ContextCache()
        self.relationships: dict[str, list[str]] = {}
        self.lock = threading.RLock()
        # Ensure database is initialized
        self.store._init_database()
    
    async def get_context(self, context_id: str) -> ContextData | None:
        """Get context by ID with caching."""
        # Try cache first
        cached_context = await self.cache.get(context_id)
        if cached_context:
            return cached_context
        
        # Get from store
        context = self.store.get_context(context_id)
        if context:
            # Cache the result
            await self.cache.set(context_id, context)
        
        return context
    
    async def store_context(self, context: ContextData) -> str:
        """Store context and return its ID."""
        # Store in database
        context_id = self.store.store_context(context)
        
        # Cache the result
        await self.cache.set(context_id, context)
        
        return context_id
    
    async def update_context(self, context_id: str, updates: dict[str, Any]) -> bool:
        """Update existing context."""
        success = self.store.update_context(context_id, updates)
        if success:
            # Invalidate cache
            await self.cache.invalidate(context_id)
        
        return success
    
    async def delete_context(self, context_id: str) -> bool:
        """Delete context by ID."""
        success = self.store.delete_context(context_id)
        if success:
            # Invalidate cache
            await self.cache.invalidate(context_id)
        
        return success
    
    async def search_contexts(self, query: str, context_type: str | None = None, 
                            limit: int = 10) -> list[ContextData]:
        """Search contexts by query."""
        return self.store.search_contexts(query, context_type, limit)
    
    async def get_related_contexts(self, context_id: str) -> list[ContextData]:
        """Get contexts related to the given context."""
        with self.lock:
            related_ids = self.relationships.get(context_id, [])
            related_contexts = []
            
            for related_id in related_ids:
                context = await self.get_context(related_id)
                if context:
                    related_contexts.append(context)
            
            return related_contexts
    
    async def add_relationship(self, source_id: str, target_id: str, 
                             relationship_type: str = "related", strength: float = 0.85):
        """Add a relationship between contexts."""
        with self.lock:
            # Add to relationships dict
            if source_id not in self.relationships:
                self.relationships[source_id] = []
            if target_id not in self.relationships:
                self.relationships[target_id] = []
            
            if target_id not in self.relationships[source_id]:
                self.relationships[source_id].append(target_id)
            if source_id not in self.relationships[target_id]:
                self.relationships[target_id].append(source_id)
            
            # Store relationship in database
            relationship = ContextRelationship(
                source_context_id=source_id,
                target_context_id=target_id,
                relationship_type=relationship_type,
                strength=strength
            )
            
            conn = sqlite3.connect(self.store.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO context_relationships 
                (id, source_context_id, target_context_id, relationship_type, strength, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                relationship.id,
                relationship.source_context_id,
                relationship.target_context_id,
                relationship.relationship_type,
                relationship.strength,
                json.dumps(relationship.metadata),
                relationship.created_at
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added relationship between {source_id} and {target_id}")
    
    async def log_access(self, context_id: str, agent_id: str, operation: str, 
                        user_id: str | None = None, metadata: dict[str, Any] | None = None):
        """Log context access."""
        access_log = ContextAccessLog(
            context_id=context_id,
            agent_id=agent_id,
            operation=operation,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        conn = sqlite3.connect(self.store.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO context_access_log 
            (id, context_id, agent_id, operation, user_id, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            access_log.id,
            access_log.context_id,
            access_log.agent_id,
            access_log.operation,
            access_log.user_id,
            json.dumps(access_log.metadata),
            access_log.created_at
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Logged {operation} access to {context_id} by {agent_id}")
    
    async def get_context_stats(self) -> dict[str, Any]:
        """Get context management statistics."""
        conn = sqlite3.connect(self.store.db_path)
        cursor = conn.cursor()
        
        # Get total contexts
        cursor.execute("SELECT COUNT(*) FROM contexts")
        total_contexts = cursor.fetchone()[0]
        
        # Get contexts by type
        cursor.execute("SELECT type, COUNT(*) FROM contexts GROUP BY type")
        contexts_by_type = dict(cursor.fetchall())
        
        # Get total size
        cursor.execute("SELECT SUM(size_bytes) FROM contexts")
        total_size = cursor.fetchone()[0] or 0
        
        # Get cache stats
        cache_stats = {
            "cache_size": len(self.cache.cache),
            "cache_hits": 0,  # Would need to track this
            "cache_misses": 0  # Would need to track this
        }
        
        conn.close()
        
        return {
            "total_contexts": total_contexts,
            "contexts_by_type": contexts_by_type,
            "total_size_bytes": total_size,
            "cache_stats": cache_stats
        }


# Example usage and testing
async def main():
    """Example usage of the Context Management System."""
    context_manager = ContextManager()
    
    # Test context creation and storage
    print("--- Testing Context Management ---")
    
    # Create test contexts
    project_context = ContextData(
        type=ContextType.PROJECT,
        source="cursor",
        content={
            "project_name": "AI Development Ecosystem",
            "description": "Comprehensive AI-powered development system",
            "technologies": ["Python", "PostgreSQL", "DSPy"]
        },
        metadata={"version": "1.0.0", "status": "active"}
    )
    
    file_context = ContextData(
        type=ContextType.FILE,
        source="research",
        content={
            "file_path": "cursor_ai_integration_framework.py",
            "language": "python",
            "purpose": "Core integration framework"
        },
        metadata={"lines": 450, "complexity": "medium"}
    )
    
    # Store contexts
    project_id = await context_manager.store_context(project_context)
    file_id = await context_manager.store_context(file_context)
    
    print(f"Stored project context: {project_id}")
    print(f"Stored file context: {file_id}")
    
    # Add relationship
    await context_manager.add_relationship(project_id, file_id, "contains")
    
    # Retrieve contexts
    retrieved_project = await context_manager.get_context(project_id)
    retrieved_file = await context_manager.get_context(file_id)
    
    print(f"Retrieved project: {retrieved_project.content['project_name']}")
    print(f"Retrieved file: {retrieved_file.content['file_path']}")
    
    # Get related contexts
    related_contexts = await context_manager.get_related_contexts(project_id)
    print(f"Related contexts for project: {len(related_contexts)}")
    
    # Search contexts
    search_results = await context_manager.search_contexts("AI Development")
    print(f"Search results: {len(search_results)} contexts found")
    
    # Log access
    await context_manager.log_access(project_id, "research", "read", "user123")
    
    # Get stats
    stats = await context_manager.get_context_stats()
    print(f"Context stats: {stats}")
    
    print("--- Context Management Test Complete ---")


if __name__ == "__main__":
    asyncio.run(main()) 