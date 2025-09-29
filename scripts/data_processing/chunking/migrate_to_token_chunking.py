#!/usr/bin/env python3
"""
Migrate existing documents from character-based to token-based chunking
with BGE embeddings and proper normalization.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import DSN resolution
import os

DSN = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

# Configuration
EMBEDDER_NAME = "BAAI/bge-small-en-v1.5"
CHUNK_SIZE_TOKENS = 220
CHUNK_OVERLAP_TOKENS = 48
MIN_CHAR_LENGTH = 140


def chunk_by_tokens(text: str, max_tokens: int = 220, overlap: int = 48, tokenizer: Any | None = None) -> list[str]:
    """
    Chunk text by tokens with overlap, preserving context.
    """
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(EMBEDDER_NAME)

    # Tokenize without special tokens
    ids = tokenizer.encode(text, add_special_tokens=False)
    
    # Compute step size
    step = max_tokens - overlap
    
    chunks = []
    for start in range(0, len(ids), step):
        piece = ids[start : start + max_tokens]
        if not piece:
            break

        # Decode the chunk
        chunk = tokenizer.decode(piece)
        
        # Attach headings/short lines to the chunk
        if start > 0:
            prev_lines = text[: text.find(chunk)].splitlines()
            if prev_lines:
                last_line = prev_lines[-1].strip()
                if len(last_line) < 40 or last_line.startswith(("#", "##", "###")):
                    chunk = last_line + "\n" + chunk
        
        chunks.append(chunk)
    
    return chunks


def migrate_documents():
    """Migrate all documents to token-based chunking with BGE embeddings."""
    
    # Initialize models
    print("🔄 Initializing BGE embedding model...")
    embedding_model = SentenceTransformer(EMBEDDER_NAME)
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDER_NAME)
    
    # Get database connection
    dsn = DSN
    
    with psycopg.connect(dsn) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Get all documents that need migration
            cur.execute("""
                SELECT id, file_path, file_name, content_sha, content_type, metadata
                FROM documents 
                ORDER BY id
            """)
            documents = cur.fetchall()
            
            print(f"📄 Found {len(documents)} documents to migrate")
            
            # Clear existing chunks
            print("🧹 Clearing existing document_chunks...")
            cur.execute("TRUNCATE TABLE document_chunks CASCADE")
            
            total_chunks = 0
            
            for doc_idx, doc in enumerate(documents):
                print(f"   Processing {doc_idx + 1}/{len(documents)}: {doc['file_name']}")
                
                # Read file content
                file_path = Path(doc['file_path'])
                if not file_path.exists():
                    print(f"   ⚠️  File not found: {file_path}")
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                except Exception as e:
                    print(f"   ⚠️  Error reading file: {e}")
                    continue
                
                # Remove excessive boilerplate/nav lines
                lines = [line for line in content.split("\n") if len(line.strip()) >= 40]
                content = "\n".join(lines)
                
                # Chunk by tokens
                chunks = chunk_by_tokens(
                    content, 
                    max_tokens=CHUNK_SIZE_TOKENS, 
                    overlap=CHUNK_OVERLAP_TOKENS, 
                    tokenizer=tokenizer
                )
                
                # Post-filter chunks
                chunks = [chunk for chunk in chunks if len(chunk.strip()) >= MIN_CHAR_LENGTH]
                
                if not chunks:
                    print("   ⚠️  No valid chunks after filtering")
                    continue
                
                # Generate embeddings for all chunks
                print(f"   🧠 Generating embeddings for {len(chunks)} chunks...")
                embeddings = embedding_model.encode(chunks, normalize_embeddings=True, show_progress_bar=False)
                
                # Insert chunks into database
                chunk_data = []
                for chunk_idx, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
                    chunk_metadata = {
                        "char_len": len(chunk_content),
                        "token_len": len(tokenizer.encode(chunk_content, add_special_tokens=False)),
                        "chunk_variant": f"token_{CHUNK_SIZE_TOKENS}_o{CHUNK_OVERLAP_TOKENS}",
                        "ingest_run_id": f"migration_{os.getpid()}",
                        "embedder_name": EMBEDDER_NAME,
                        "embedder_ver": "1.5",
                        "source_path": str(file_path),
                        "chunk_type": "token-based"
                    }
                    
                    chunk_data.append((
                        doc['id'],
                        chunk_idx,
                        chunk_content.strip(),
                        embedding.tolist(),
                        json.dumps(chunk_metadata)
                    ))
                
                # Batch insert chunks
                cur.executemany("""
                    INSERT INTO document_chunks 
                    (document_id, chunk_index, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, chunk_data)
                
                total_chunks += len(chunks)
                print(f"   ✅ Inserted {len(chunks)} chunks")
            
            # Update tsvector for all chunks
            print("🔍 Updating full-text search vectors...")
            cur.execute("UPDATE document_chunks SET content_tsv = to_tsvector('english', content)")
            
            # Update statistics
            cur.execute("ANALYZE document_chunks")
            
            print("\n🎉 Migration complete!")
            print(f"   📄 Documents processed: {len(documents)}")
            print(f"   📝 Total chunks created: {total_chunks}")
            print(f"   🧠 Embedding model: {EMBEDDER_NAME}")
            print(f"   📏 Chunk size: {CHUNK_SIZE_TOKENS} tokens, {CHUNK_OVERLAP_TOKENS} overlap")


if __name__ == "__main__":
    # Set environment variable to avoid tokenizer warnings
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    migrate_documents()
