#!/usr/bin/env python3
"""
VectorStore DSPy Module
Handles PostgreSQL vector storage and retrieval operations for the RAG system.
"""

import os
import json
import uuid
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
import dspy
from dspy import Module
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import SimpleConnectionPool
from sentence_transformers import SentenceTransformer
from ..utils.retry_wrapper import retry_database
from ..utils.database_resilience import get_database_manager, execute_query, execute_transaction

# Global connection pool
_POOL: Optional[SimpleConnectionPool] = None

def _get_pool(conn_str: str) -> SimpleConnectionPool:
    """Get or create the global connection pool with timeout configuration"""
    global _POOL
    if _POOL is None:
        # Load timeout configuration
        from ..utils.timeout_config import get_timeout_config
        timeout_config = get_timeout_config()
        
        # Create pool with timeout settings
        _POOL = SimpleConnectionPool(
            minconn=1, 
            maxconn=10, 
            dsn=conn_str,
            # Add connection timeout parameters
            options=f"-c statement_timeout={timeout_config.db_read_timeout}s "
                   f"-c idle_in_transaction_session_timeout={timeout_config.db_write_timeout}s"
        )
        
        # Register pgvector adapter once
        with _POOL.getconn() as conn:
            try:
                from pgvector.psycopg2 import register_vector
                register_vector(conn)
            except ImportError:
                # Fallback if pgvector not installed
                pass
            _POOL.putconn(conn)
    return _POOL

@lru_cache(maxsize=1)
def _get_model(name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Singleton model loader to prevent repeated loads"""
    return SentenceTransformer(name)

class VectorStore(Module):
    """DSPy module for PostgreSQL vector storage and retrieval"""
    
    def __init__(self, db_connection_string: str, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__()
        self.conn_str = db_connection_string
        self.model_name = model_name
        self.model = _get_model(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
    
    def forward(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for vector store operations"""
        
        if operation == "store_chunks":
            return self._store_chunks(**kwargs)
        elif operation == "search":
            return self._search(**kwargs)
        elif operation == "delete_document":
            return self._delete_document(**kwargs)
        elif operation == "get_document_chunks":
            return self._get_document_chunks(**kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    @retry_database
    def _store_chunks(self, chunks: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store document chunks with embeddings in PostgreSQL using bulk insert"""
        
        # Generate embeddings for chunks
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        
        # Use UUID for document_id to prevent collisions
        doc_id = metadata.get("document_id") or uuid.uuid4().hex
        
        # Prepare bulk insert data
        chunk_rows = [
            (doc_id, i, chunk, emb.astype(np.float32))
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]
        
        # Use database resilience manager
        db_manager = get_database_manager()
        
        # Set connection timeout
        from ..utils.timeout_config import get_timeout_config
        timeout_config = get_timeout_config()
        
        try:
            with conn, conn.cursor() as cur:
                # Set statement timeout for this connection
                cur.execute(f"SET statement_timeout = {timeout_config.db_write_timeout * 1000}")
                # Bulk insert chunks
                execute_values(
                    cur,
                    """
                    INSERT INTO document_chunks
                         (document_id, chunk_index, content, embedding)
                    VALUES %s
                    """,
                    chunk_rows,
                    template="(%s,%s,%s,%s)"
                )
                
                # Insert/update document record
                cur.execute("""
                    INSERT INTO documents
                           (document_id, filename, file_type, file_size,
                            chunk_count, metadata)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (document_id)
                    DO UPDATE SET chunk_count = EXCLUDED.chunk_count,
                                  metadata = EXCLUDED.metadata,
                                  updated_at = CURRENT_TIMESTAMP
                """, (
                    doc_id,
                    metadata.get("filename"),
                    metadata.get("file_type"),
                    metadata.get("file_size", 0),
                    len(chunks),
                    json.dumps(metadata),
                ))
            
            return {
                "status": "success",
                "document_id": doc_id,
                "chunks_stored": len(chunks)
            }
            
        except Exception as e:
            conn.rollback()
            raise
        finally:
            pool.putconn(conn)
    
    @retry_database
    def _search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search for similar chunks using vector similarity"""
        
        # Generate embedding for query
        query_emb = self.model.encode([query])[0].astype(np.float32)
        
        # Use database resilience manager
        db_manager = get_database_manager()
        
        # Set connection timeout
        from ..utils.timeout_config import get_timeout_config
        timeout_config = get_timeout_config()
        
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Set statement timeout for this connection
                    cur.execute(f"SET statement_timeout = {timeout_config.db_read_timeout * 1000}")
                    cur.execute("""
                        SELECT document_id, chunk_index, content,
                               1 - (embedding <=> %s) AS similarity
                        FROM document_chunks
                        ORDER BY embedding <=> %s
                        LIMIT %s
                    """, (query_emb, query_emb, limit))
                    
                    results = cur.fetchall()
                
                # Format results
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "content": result["content"],
                        "document_id": result["document_id"],
                        "chunk_index": result["chunk_index"],
                        "similarity_score": float(result["similarity"])
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": formatted_results,
                    "total_results": len(formatted_results)
                }
                
        except Exception as e:
            raise
    
    def _delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete all chunks for a specific document"""
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    # Delete chunks
                    cur.execute("""
                        DELETE FROM document_chunks 
                        WHERE document_id = %s
                    """, (document_id,))
                    
                    # Delete document record
                    cur.execute("""
                        DELETE FROM documents 
                        WHERE document_id = %s
                    """, (document_id,))
                
                return {
                    "status": "success",
                    "document_id": document_id,
                    "message": "Document and all chunks deleted"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_document_chunks(self, document_id: str) -> Dict[str, Any]:
        """Retrieve all chunks for a specific document"""
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT chunk_index, content, created_at
                        FROM document_chunks
                        WHERE document_id = %s
                        ORDER BY chunk_index
                    """, (document_id,))
                    
                    results = cur.fetchall()
                
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "chunk_index": result["chunk_index"],
                        "content": result["content"],
                        "created_at": result["created_at"].isoformat() if result["created_at"] else None
                    })
                
                return {
                    "status": "success",
                    "document_id": document_id,
                    "chunks": formatted_results,
                    "total_chunks": len(formatted_results)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get total chunks
                    cur.execute("SELECT COUNT(*) FROM document_chunks")
                    total_chunks = cur.fetchone()[0]
                    
                    # Get total documents
                    cur.execute("SELECT COUNT(*) FROM documents")
                    total_documents = cur.fetchone()[0]
                    
                    # Get total conversations (if table exists)
                    try:
                        cur.execute("SELECT COUNT(*) FROM conversation_memory")
                        total_conversations = cur.fetchone()[0]
                    except:
                        total_conversations = 0
                    
                    # Get document types
                    cur.execute("""
                        SELECT file_type, COUNT(*) 
                        FROM documents 
                        GROUP BY file_type
                    """)
                    document_types = dict(cur.fetchall())
                
                return {
                    "status": "success",
                    "total_chunks": total_chunks,
                    "total_documents": total_documents,
                    "total_conversations": total_conversations,
                    "document_types": document_types
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class VectorStorePipeline(Module):
    """DSPy module for complete vector store pipeline"""
    
    def __init__(self, db_connection_string: str):
        super().__init__()
        self.vector_store = VectorStore(db_connection_string)
    
    def forward(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Complete vector store pipeline"""
        return self.vector_store(operation, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Test the vector store
    db_connection = "postgresql://ai_user:ai_password@localhost:5432/ai_agency"
    vector_store = VectorStore(db_connection)
    
    # Test search
    result = vector_store("search", query="What is DSPy?", limit=3)
    print(f"Search result: {result}")
    
    # Test stats
    stats = vector_store.get_stats()
    print(f"Database stats: {stats}") 