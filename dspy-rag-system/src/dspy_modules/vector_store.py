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

class HybridVectorStore(Module):
    """Research-based DSPy module for hybrid vector storage and retrieval (dense + sparse)"""
    
    def __init__(self, db_connection_string: str, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__()
        self.conn_str = db_connection_string
        self.model_name = model_name
        self.model = _get_model(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
    
    def forward(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for hybrid vector store operations"""
        
        if operation == "store_chunks":
            return self._store_chunks_with_spans(**kwargs)
        elif operation == "search":
            return self._hybrid_search(**kwargs)
        elif operation == "delete_document":
            return self._delete_document(**kwargs)
        elif operation == "get_document_chunks":
            return self._get_document_chunks(**kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _hybrid_search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Research-based hybrid search: PGVector (dense) + PostgreSQL full-text (sparse)"""
        
        # Dense vector search (existing functionality)
        dense_results = self._vector_search(query, limit)
        
        # Sparse text search (research-based addition)
        sparse_results = self._text_search(query, limit)
        
        # Merge and rank results (research-based approach)
        merged_results = self._merge_hybrid_results(dense_results, sparse_results, limit)
        
        # Add span information for grounding
        results_with_spans = self._add_span_information(merged_results)
        
        return {
            "results": results_with_spans,
            "search_type": "hybrid",
            "dense_count": len(dense_results),
            "sparse_count": len(sparse_results),
            "merged_count": len(results_with_spans)
        }
    
    def _vector_search(self, query: str, limit: int) -> List[Dict]:
        """Dense vector search using PGVector"""
        # Existing vector search implementation
        return self._search(query, limit)
    
    def _text_search(self, query: str, limit: int) -> List[Dict]:
        """Sparse text search using PostgreSQL full-text search"""
        pool = _get_pool(self.conn_str)
        
        with pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Use PostgreSQL full-text search with tsvector
                search_query = f"""
                SELECT 
                    document_id,
                    chunk_index,
                    content,
                    metadata,
                    ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) as rank
                FROM document_chunks 
                WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
                ORDER BY rank DESC
                LIMIT %s
                """
                
                cur.execute(search_query, (query, query, limit))
                results = cur.fetchall()
                
                return [dict(row) for row in results]
    
    def _merge_hybrid_results(self, dense_results: List[Dict], sparse_results: List[Dict], limit: int) -> List[Dict]:
        """Research-based merging strategy for hybrid search results"""
        
        # Create lookup for results found by both methods
        dense_lookup = {f"{r['document_id']}_{r['chunk_index']}": r for r in dense_results}
        sparse_lookup = {f"{r['document_id']}_{r['chunk_index']}": r for r in sparse_results}
        
        # Boost results found by both methods
        merged_results = []
        seen_keys = set()
        
        # First, add results found by both methods (boosted)
        for key in dense_lookup.keys() & sparse_lookup.keys():
            result = dense_lookup[key].copy()
            result["hybrid_score"] = result.get("similarity", 0) + sparse_lookup[key].get("rank", 0)
            result["found_by"] = "both"
            merged_results.append(result)
            seen_keys.add(key)
        
        # Then add remaining dense results
        for key, result in dense_lookup.items():
            if key not in seen_keys:
                result["hybrid_score"] = result.get("similarity", 0)
                result["found_by"] = "dense"
                merged_results.append(result)
                seen_keys.add(key)
        
        # Finally add remaining sparse results
        for key, result in sparse_lookup.items():
            if key not in seen_keys:
                result["hybrid_score"] = result.get("rank", 0)
                result["found_by"] = "sparse"
                merged_results.append(result)
        
        # Sort by hybrid score and return top results
        merged_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return merged_results[:limit]
    
    def _add_span_information(self, results: List[Dict]) -> List[Dict]:
        """Add character offsets for precise citations (research-based)"""
        for result in results:
            # Add span information for grounding
            result["span_start"] = result.get("start_offset", 0)
            result["span_end"] = result.get("end_offset", len(result.get("content", "")))
            
            # Add citation format
            result["citation"] = f"Doc {result.get('document_id', 'unknown')}, lines {result['span_start']}-{result['span_end']}"
        
        return results
    
    @retry_database
    def _store_chunks_with_spans(self, chunks: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Research-based store document chunks with embeddings and span information"""
        
        # Generate embeddings for chunks
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        
        # Use UUID for document_id to prevent collisions
        doc_id = metadata.get("document_id") or uuid.uuid4().hex
        
        # Prepare bulk insert data with span information
        chunk_rows = []
        current_offset = 0
        
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            # Calculate span information for precise citations
            start_offset = current_offset
            end_offset = current_offset + len(chunk)
            
            chunk_rows.append((
                doc_id, 
                i, 
                chunk, 
                emb.astype(np.float32),
                start_offset,
                end_offset
            ))
            
            current_offset = end_offset + 1  # +1 for newline
        
        # Store with span metadata
        return self._insert_with_spans(chunk_rows, metadata)
    
    def _insert_with_spans(self, chunk_rows: List[Tuple], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Insert chunks with span information for precise citations"""
        
        pool = _get_pool(self.conn_str)
        
        with pool.getconn() as conn:
            with conn.cursor() as cur:
                # Insert with span information
                insert_query = """
                INSERT INTO document_chunks 
                (document_id, chunk_index, content, embedding, start_offset, end_offset, metadata)
                VALUES %s
                """
                
                execute_values(cur, insert_query, chunk_rows)
                conn.commit()
                
                return {
                    "stored_chunks": len(chunk_rows),
                    "document_id": chunk_rows[0][0] if chunk_rows else None,
                    "spans_tracked": True
                }
        
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