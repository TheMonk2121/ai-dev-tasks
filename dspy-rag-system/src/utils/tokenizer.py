#!/usr/bin/env python3.12.123.11
"""
Token-Aware Chunking for DSPy RAG System
Provides token-aware text chunking for better LLM compatibility.
"""

import tiktoken
import re
from typing import Optional, Any
from collections.abc import Iterator
import logging
from functools import lru_cache
import unicodedata

logger = logging.getLogger(__name__)

# Model-to-encoder mapping
TOKENIZER_MAPPING = {
    "gpt-4o": ("tiktoken", "cl100k_base"),
    "gpt-4": ("tiktoken", "cl100k_base"),
    "gpt-3.5-turbo": ("tiktoken", "cl100k_base"),
    "mistral-7b": ("tiktoken", "cl100k_base"),  # Fallback for now
    "llama3-70b": ("tiktoken", "cl100k_base"),  # Fallback for now
    "default": ("tiktoken", "cl100k_base")
}

class GenericEncoder:
    """Unified wrapper for different tokenizer types"""
    
    def __init__(self, model_name: str):
        """
        Initialize encoder for specific model
        
        Args:
            model_name: Model name (e.g., 'gpt-4o', 'mistral-7b')
        """
        self.model_name = model_name
        
        # Get encoder configuration
        encoder_type, encoder_name = TOKENIZER_MAPPING.get(
            model_name, TOKENIZER_MAPPING["default"]
        )
        
        if encoder_type == "tiktoken":
            try:
                self.encoder = tiktoken.get_encoding(encoder_name)
                self.encode = self.encoder.encode
                self.decode = self.encoder.decode
                logger.info(f"Initialized tiktoken encoder for {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize tiktoken encoder: {e}")
                # Fallback to default
                self.encoder = tiktoken.get_encoding("cl100k_base")
                self.encode = self.encoder.encode
                self.decode = self.encoder.decode
        else:
            # Future: Add SentencePiece support
            raise NotImplementedError(f"Encoder type {encoder_type} not yet supported")

@lru_cache(maxsize=8)
def get_encoder(model_name: str) -> GenericEncoder:
    """Get cached encoder instance"""
    return GenericEncoder(model_name)

class TokenAwareChunker:
    """Token-aware text chunking with sentence boundary awareness"""
    
    def __init__(self, model_name: str = "gpt-4o", max_tokens: int = 300, 
                 overlap_tokens: int = 50):
        """
        Initialize the token-aware chunker
        
        Args:
            model_name: Model name for tokenizer selection
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoder = get_encoder(model_name)
        
        # Compile regex patterns once
        self.sentence_end_pattern = re.compile(r'[.!?]+["\']?\s+')
        self.abbreviation_pattern = re.compile(r'\b[A-Z]\.\s*[A-Z]\.')
        
        logger.info(f"Initialized TokenAwareChunker for {model_name} "
                   f"(max_tokens={max_tokens}, overlap_tokens={overlap_tokens})")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(text))
    
    def find_sentence_boundary(self, text: str, start_pos: int, target_pos: int) -> int:
        """
        Find the best sentence boundary near the target position
        
        Args:
            text: Full text to search in
            start_pos: Start position of current chunk
            target_pos: Target end position
            
        Returns:
            Best sentence boundary position
        """
        # Look for sentence endings within the last 100 characters
        search_start = max(start_pos + self.max_tokens - 100, start_pos)
        search_end = min(target_pos, len(text))
        
        if search_start >= search_end:
            return target_pos
        
        # Find the last sentence boundary
        matches = list(self.sentence_end_pattern.finditer(text[search_start:search_end]))
        if matches:
            # Use the last match
            return search_start + matches[-1].end()
        
        return target_pos
    
    def create_chunks(self, text: str) -> list[str]:
        """
        Create token-aware chunks with optimized single encoding
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text.strip():
            return []
        
        try:
            # Clean text first
            text = self._clean_text(text)
            
            # Single encoding optimization - encode once, then slice
            all_tokens = self.encoder.encode(text)
            total_tokens = len(all_tokens)
            
            if total_tokens <= self.max_tokens:
                # Text fits in one chunk
                return [text] if text.strip() else []
            
            chunks = []
            start_token_idx = 0
            
            while start_token_idx < total_tokens:
                # Calculate end token index
                end_token_idx = min(start_token_idx + self.max_tokens, total_tokens)
                
                # Extract chunk tokens
                chunk_tokens = all_tokens[start_token_idx:end_token_idx]
                chunk_text = self.encoder.decode(chunk_tokens)
                
                # Try to find better sentence boundary (only for reasonable chunk sizes)
                if end_token_idx < total_tokens and (end_token_idx - start_token_idx) > 50:
                    # Convert token positions to character positions for boundary detection
                    start_char_pos = len(self.encoder.decode(all_tokens[:start_token_idx]))
                    target_char_pos = len(self.encoder.decode(all_tokens[:end_token_idx]))
                    
                    # Only do boundary detection if the search window is reasonable
                    if (target_char_pos - start_char_pos) < 1000:  # Limit search window
                        boundary_char_pos = self.find_sentence_boundary(
                            text, start_char_pos, target_char_pos
                        )
                        
                        # Convert back to token position
                        if boundary_char_pos > start_char_pos:
                            # Find the token index that corresponds to this character position
                            boundary_tokens = self.encoder.encode(text[:boundary_char_pos])
                            boundary_token_idx = len(boundary_tokens)
                            
                            # Only use boundary if it's reasonable
                            if (boundary_token_idx > start_token_idx and 
                                boundary_token_idx <= end_token_idx + 10):
                                end_token_idx = boundary_token_idx
                                chunk_tokens = all_tokens[start_token_idx:end_token_idx]
                                chunk_text = self.encoder.decode(chunk_tokens)
                
                # Add chunk if not empty
                if chunk_text.strip():
                    chunks.append(chunk_text.strip())
                
                # Calculate next start position with proper token-based overlap
                if end_token_idx >= total_tokens:
                    break
                
                # Calculate overlap in token space
                overlap_start = max(0, end_token_idx - self.overlap_tokens)
                start_token_idx = overlap_start
                
                # Safety check to prevent infinite loops
                if start_token_idx >= end_token_idx:
                    start_token_idx = end_token_idx
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error in create_chunks: {e}", extra={
                'model_name': self.model_name,
                'text_length': len(text),
                'max_tokens': self.max_tokens
            })
            # Fallback to simple character-based chunking
            return self._fallback_chunking(text)
    
    def _fallback_chunking(self, text: str) -> list[str]:
        """Fallback chunking method when token-based chunking fails"""
        logger.warning("Using fallback character-based chunking")
        
        # Simple character-based chunking
        chunk_size = self.max_tokens * 4  # Rough estimate
        overlap_size = self.overlap_tokens * 4
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap_size
            if start >= len(text):
                break
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text with improved Unicode handling
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Normalize Unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remove control characters (Cc) and format characters (Cf)
        cleaned_chars = []
        for char in text:
            category = unicodedata.category(char)
            if category not in ['Cc', 'Cf']:  # Keep everything except control/format
                cleaned_chars.append(char)
        
        text = ''.join(cleaned_chars)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def get_chunk_stats(self, text: str) -> dict[str, Any]:
        """Get statistics about chunking"""
        try:
            chunks = self.create_chunks(text)
            total_tokens = self.count_tokens(text)
            chunk_tokens = [self.count_tokens(chunk) for chunk in chunks]
            
            return {
                'total_chunks': len(chunks),
                'total_tokens': total_tokens,
                'avg_chunk_tokens': sum(chunk_tokens) / len(chunk_tokens) if chunk_tokens else 0,
                'min_chunk_tokens': min(chunk_tokens) if chunk_tokens else 0,
                'max_chunk_tokens': max(chunk_tokens) if chunk_tokens else 0,
                'chunk_tokens': chunk_tokens,
                'model_name': self.model_name,
                'max_tokens': self.max_tokens,
                'overlap_tokens': self.overlap_tokens
            }
        except Exception as e:
            logger.error(f"Error getting chunk stats: {e}")
            return {
                'error': str(e),
                'total_chunks': 0,
                'total_tokens': 0
            }
    
    def create_chunks_generator(self, text: str) -> Iterator[str]:
        """
        Generator version for memory-efficient processing of large texts
        
        Args:
            text: Text to chunk
            
        Yields:
            Text chunks
        """
        chunks = self.create_chunks(text)
        for chunk in chunks:
            yield chunk

def create_chunker(model_name: str = "gpt-4o", max_tokens: int = 300, 
                  overlap_tokens: int = 50) -> TokenAwareChunker:
    """Factory function to create a token-aware chunker"""
    return TokenAwareChunker(model_name, max_tokens, overlap_tokens) 