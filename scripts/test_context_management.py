#!/usr/bin/env python3
"""
Simplified Context Management Test

This is a simplified test version to verify the context management system works.
"""

import json
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class ContextType(Enum):
    """Enumeration of context types."""
    PROJECT = "project"
    FILE = "file"
    USER = "user"
    AGENT = "agent"


@dataclass
class ContextData:
    """Data structure for context information."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: ContextType = ContextType.FILE
    source: str = "cursor"
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)


class SimpleContextStore:
    """Simplified database-backed context storage system."""
    
    def __init__(self, db_path: str = "test_context.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create contexts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contexts (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                accessed_at REAL NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    def store_context(self, context: ContextData) -> str:
        """Store context in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO contexts 
            (id, type, source, content, metadata, created_at, updated_at, accessed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            context.id,
            context.type.value,
            context.source,
            json.dumps(context.content),
            json.dumps(context.metadata),
            context.created_at,
            context.updated_at,
            context.accessed_at
        ))
        
        conn.commit()
        conn.close()
        
        print(f"Stored context {context.id} of type {context.type.value}")
        return context.id
    
    def get_context(self, context_id: str) -> Optional[ContextData]:
        """Get context by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, type, source, content, metadata, created_at, updated_at, accessed_at
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
                metadata=json.loads(row[4]) if row[4] else {},
                created_at=row[5],
                updated_at=row[6],
                accessed_at=row[7]
            )
            return context
        
        return None


def main():
    """Test the simplified context management system."""
    print("--- Testing Simplified Context Management ---")
    
    # Create context store
    store = SimpleContextStore()
    
    # Create test context
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
    
    # Store context
    project_id = store.store_context(project_context)
    print(f"Stored project context: {project_id}")
    
    # Retrieve context
    retrieved_project = store.get_context(project_id)
    if retrieved_project:
        print(f"Retrieved project: {retrieved_project.content['project_name']}")
        print(f"Project technologies: {retrieved_project.content['technologies']}")
    else:
        print("Failed to retrieve project context")
    
    print("--- Context Management Test Complete ---")


if __name__ == "__main__":
    main() 