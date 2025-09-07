#!/usr/bin/env python3
"""
Enhanced Chunking Module
- Tokenizer-first approach aligned with embedder
- Recursive splitting with hard caps
- Proportional overlap and smart deduplication
- Contextual retrieval augmentation
- Dual-text storage for embedding and BM25
"""

import hashlib
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union


@dataclass
class ChunkingConfig:
    """Configuration for enhanced chunking"""

    embedder_name: str
    chunk_size: int
    overlap_ratio: float = 0.15
    max_tokens: int = 1024
    ngram_size: int = 5
    jaccard_threshold: float = 0.8
    use_contextual_prefix: bool = True
    
    # Production configuration metadata
    chunk_version: str = ""
    ingest_run_id: str = ""

    def __post_init__(self):
        """Override with environment variables if set"""
        # Load from environment variables (production mode)
        if os.getenv("CHUNK_SIZE"):
            self.chunk_size = int(os.getenv("CHUNK_SIZE"))
        if os.getenv("OVERLAP_RATIO"):
            self.overlap_ratio = float(os.getenv("OVERLAP_RATIO"))
        if os.getenv("JACCARD_THRESHOLD"):
            self.jaccard_threshold = float(os.getenv("JACCARD_THRESHOLD"))
        if os.getenv("PREFIX_POLICY"):
            # PREFIX_POLICY="A" means no prefix in BM25, "B" means prefix in both
            self.use_contextual_prefix = True
        if os.getenv("CHUNK_VERSION"):
            self.chunk_version = os.getenv("CHUNK_VERSION")
        if os.getenv("INGEST_RUN_ID"):
            self.ingest_run_id = os.getenv("INGEST_RUN_ID")


class EnhancedChunker:
    """Enhanced chunking with tokenizer-first approach and recursive splitting"""

    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.tokenizer = self._init_tokenizer()
        self.overlap = self._calculate_overlap()
        # Pre-warm tokenizer to avoid lazy loading issues
        if self.tokenizer:
            try:
                # Try transformers-style encode first
                self.tokenizer.encode("test", truncation=True, max_length=512)  # pyright: ignore[reportCallIssue]
            except TypeError:
                try:
                    # Fallback to basic encode
                    self.tokenizer.encode("test")
                except Exception:
                    pass  # Tokenizer might not be ready yet

    def _init_tokenizer(self) -> Union[Any, None]:
        """Initialize tokenizer once - embedder-first approach"""
        try:
            from transformers import AutoTokenizer

            return AutoTokenizer.from_pretrained(self.config.embedder_name)
        except Exception:
            try:
                import tiktoken

                return tiktoken.get_encoding("cl100k_base")
            except Exception:
                return None  # fallback to heuristic

    def _calculate_overlap(self) -> int:
        """Calculate proportional overlap with bounds"""
        overlap = min(int(round(self.config.chunk_size * self.config.overlap_ratio)), 200)
        assert 0 < overlap < self.config.chunk_size, "bad overlap settings"
        return overlap

    def token_len(self, s: str) -> int:
        """Get accurate token count using embedder's tokenizer"""
        if self.tokenizer:
            try:
                # Try transformers-style encode first
                tokens = self.tokenizer.encode(s, truncation=True, max_length=512)  # pyright: ignore[reportCallIssue]
                return len(tokens)
            except TypeError:
                try:
                    # Fallback to basic encode
                    tokens = self.tokenizer.encode(s)
                    return len(tokens)
                except Exception:
                    # Fallback to heuristic if tokenizer fails
                    return max(1, round(len(s) / 4))
        return max(1, round(len(s) / 4))  # last-resort heuristic

    def window_by_tokens(self, text: str, max_tokens: int, overlap: int) -> List[str]:
        """Window text by tokens, not characters"""
        if not self.tokenizer:
            # Fallback to character-based windowing
            return self._window_by_chars(text, max_tokens, overlap)

        ids = self.tokenizer.encode(text)
        if max_tokens <= 0:
            return [text]

        stride = max(1, max_tokens - overlap)
        chunks = []

        for start in range(0, len(ids), stride):
            end = min(start + max_tokens, len(ids))
            if start >= end:
                break

            try:
                # Try transformers-style decode first
                chunk = self.tokenizer.decode(
                    ids[start:end], skip_special_tokens=True
                )  # pyright: ignore[reportCallIssue]
            except TypeError:
                # Fallback to basic decode
                chunk = self.tokenizer.decode(ids[start:end])

            chunks.append(chunk)
            if end == len(ids):
                break

        return chunks

    def _window_by_chars(self, text: str, max_tokens: int, overlap: int) -> List[str]:
        """Fallback character-based windowing"""
        # Rough estimate: 4 chars per token
        max_chars = max_tokens * 4
        overlap_chars = overlap * 4
        stride = max_chars - overlap_chars

        chunks = []
        for start in range(0, len(text), stride):
            end = min(start + max_chars, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break

        return chunks

    def split_by_structure(self, text: str) -> List[str]:
        """Split by document structure (headings, code blocks)"""
        # Keep fenced code intact
        blocks = re.split(r"(\n```.*?\n```)", text, flags=re.DOTALL)
        sections = []

        for i, block in enumerate(blocks):
            if i % 2 == 1:  # Code block
                sections.append(block)
            else:  # Text block
                # Split on headings
                parts = re.split(r"(?=^#{1,6}\s)", block, flags=re.MULTILINE)
                sections.extend([p for p in parts if p.strip()])

        return sections

    def split_by_paragraphs(self, text: str) -> List[str]:
        """Split by paragraph boundaries"""
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        return paras

    def split_by_sentences(self, text: str) -> List[str]:
        """Split by sentence boundaries"""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def is_header_only(self, chunk: str) -> bool:
        """Check if chunk is header-only (needs merging)"""
        lines = chunk.strip().split("\n")
        if len(lines) <= 2:
            # Check if it's just a header
            return any(line.strip().startswith("#") for line in lines)
        return False

    def protect_structure(self, chunks: List[str]) -> List[str]:
        """Protect pathological sections from being split"""
        protected = []
        for chunk in chunks:
            if self.is_header_only(chunk) and protected:
                # Merge header-only chunks into previous chunk
                protected[-1] += "\n" + chunk
            else:
                protected.append(chunk)
        return protected

    def jaccard(self, a: set, b: set) -> float:
        """Calculate Jaccard similarity"""
        return len(a & b) / max(1, len(a | b))

    def extract_ngrams(self, text: str, n: int) -> set:
        """Extract n-grams from text"""
        words = text.split()
        return {tuple(words[i : i + n]) for i in range(0, max(0, len(words) - n + 1))}

    def dedup_chunks(self, chunks: List[str]) -> List[str]:
        """Remove near-duplicate chunks using Jaccard threshold"""
        kept, signatures = [], []

        for chunk in chunks:
            ngrams = self.extract_ngrams(chunk, self.config.ngram_size)

            # Check if too similar to any existing chunk
            if any(self.jaccard(ngrams, prev) >= self.config.jaccard_threshold for prev in signatures):
                continue

            kept.append(chunk)
            signatures.append(ngrams)

        return kept

    def create_contextual_prefix(self, metadata: Dict[str, Any]) -> str:
        """Create contextual prefix for embedding augmentation"""
        if not self.config.use_contextual_prefix:
            return ""

        prefix_parts = []
        if metadata.get("title"):
            prefix_parts.append(f"Document: {metadata['title']}")
        if metadata.get("section_path"):
            prefix_parts.append(f"Section: {metadata['section_path']}")
        if metadata.get("content_type"):
            prefix_parts.append(f"Type: {metadata['content_type']}")

        if prefix_parts:
            return "\n".join(prefix_parts) + "\n\n"
        return ""

    def create_chunk_pair(self, chunk: str, metadata: Dict[str, Any]) -> Tuple[str, str, Dict[str, int], str]:
        """Create dual-text pair: embedding_text (with context) and bm25_text (clean or with prefix)"""
        contextual_prefix = self.create_contextual_prefix(metadata)
        embedding_text = contextual_prefix + chunk

        # Check prefix policy from environment or config
        prefix_policy = os.getenv("PREFIX_POLICY", "A")
        if prefix_policy == "B":
            bm25_text = contextual_prefix + chunk  # Add prefix to BM25 too
        else:
            bm25_text = chunk  # Keep BM25 clean (policy A)

        # Store token counts for both versions
        token_counts = {
            "embedding_token_count": self.token_len(embedding_text),
            "bm25_token_count": self.token_len(bm25_text),
        }

        # Create stable chunk ID based on content hash and configuration
        content_hash = hashlib.sha256(embedding_text.encode()).hexdigest()[:16]
        config_hash = hashlib.sha256(
            f"{self.config.chunk_size}-{self.config.overlap_ratio}-{self.config.jaccard_threshold}-{prefix_policy}".encode()
        ).hexdigest()[:8]
        chunk_id = f"{content_hash}-{config_hash}"

        return embedding_text, bm25_text, token_counts, chunk_id

    def recursive_split(self, content: str, metadata: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, int], str]]:
        """Recursive splitting with hard cap enforcement"""
        # Level 1: Split by document structure
        sections = self.split_by_structure(content)

        # Level 2: Process sections
        chunks = []
        for section in sections:
            if self.token_len(section) <= self.config.chunk_size:
                chunks.append(section)
            else:
                # Split by paragraphs
                paras = self.split_by_paragraphs(section)
                chunks.extend(self._process_paragraphs(paras))

        # Level 3: Final windowing pass for any remaining monsters
        final_chunks = []
        for chunk in chunks:
            if self.token_len(chunk) <= self.config.chunk_size:
                final_chunks.append(chunk)
            else:
                # Token-level windowing
                windowed = self.window_by_tokens(chunk, self.config.chunk_size, self.overlap)
                final_chunks.extend(windowed)

        # Protect structure and deduplicate
        final_chunks = self.protect_structure(final_chunks)
        final_chunks = self.dedup_chunks(final_chunks)

        # Create dual-text pairs with token counts and stable IDs
        chunk_pairs = []
        for chunk in final_chunks:
            if self.token_len(chunk) > 10:  # Filter tiny chunks (lowered threshold)
                embedding_text, bm25_text, token_counts, chunk_id = self.create_chunk_pair(chunk, metadata)
                chunk_pairs.append((embedding_text, bm25_text, token_counts, chunk_id))

        return chunk_pairs

    def _process_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """Process paragraphs with overlap"""
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self.token_len(para)

            if current_chunk and current_tokens + para_tokens > self.config.chunk_size:
                # Finalize current chunk
                chunks.append("\n\n".join(current_chunk))

                # Start new chunk with overlap
                if self.overlap > 0:
                    overlap_text = " ".join(" ".join(current_chunk).split()[-self.overlap :])
                    current_chunk = [overlap_text] if overlap_text else []
                    current_tokens = self.token_len(overlap_text)
                else:
                    current_chunk = []
                    current_tokens = 0

            current_chunk.append(para)
            current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def chunk_document(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Chunk a document and return results with metadata"""
        start_time = time.time()

        # Extract metadata
        metadata = {
            "title": file_path.stem,
            "section_path": str(file_path),
            "content_type": "markdown" if file_path.suffix.lower() == ".md" else "text",
            "file_size": len(content),
        }

        # Chunk the content
        chunk_pairs = self.recursive_split(content, metadata)

        # Extract embedding and BM25 texts, token counts, and chunk IDs
        embedding_texts = [pair[0] for pair in chunk_pairs]
        bm25_texts = [pair[1] for pair in chunk_pairs]
        token_counts_list = [pair[2] for pair in chunk_pairs]
        chunk_ids = [pair[3] for pair in chunk_pairs]

        # Calculate metrics
        processing_time = time.time() - start_time
        bm25_token_counts = [counts["bm25_token_count"] for counts in token_counts_list]
        embedding_token_counts = [counts["embedding_token_count"] for counts in token_counts_list]

        return {
            "embedding_texts": embedding_texts,
            "bm25_texts": bm25_texts,
            "token_counts": token_counts_list,
            "chunk_ids": chunk_ids,
            "metadata": metadata,
            "metrics": {
                "chunk_count": len(chunk_pairs),
                "pre_split_tokens": self.token_len(content),
                "post_split_tokens_mean": sum(bm25_token_counts) / len(bm25_token_counts) if bm25_token_counts else 0,
                "post_split_tokens_p95": (
                    sorted(bm25_token_counts)[int(0.95 * len(bm25_token_counts))] if bm25_token_counts else 0
                ),
                "post_split_tokens_max": max(bm25_token_counts) if bm25_token_counts else 0,
                "chunks_over_budget": sum(1 for t in embedding_token_counts if t > self.config.max_tokens),
                "processing_time": processing_time,
                "time_per_1k_tokens": processing_time / (self.token_len(content) / 1000) if content else 0,
                "avg_embedding_tokens": (
                    sum(embedding_token_counts) / len(embedding_token_counts) if embedding_token_counts else 0
                ),
                "avg_bm25_tokens": sum(bm25_token_counts) / len(bm25_token_counts) if bm25_token_counts else 0,
            },
        }

    def validate_chunking(self, chunk_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Validate chunking results"""
        bm25_texts = [pair[1] for pair in chunk_pairs]
        token_counts = [self.token_len(text) for text in bm25_texts]

        return {
            "budget_compliance": max(token_counts) <= self.config.max_tokens if token_counts else True,
            "zero_over_budget": sum(1 for t in token_counts if t > self.config.max_tokens) == 0,
            "chunk_count": len(chunk_pairs),
            "avg_tokens": sum(token_counts) / len(token_counts) if token_counts else 0,
            "max_tokens": max(token_counts) if token_counts else 0,
            "min_tokens": min(token_counts) if token_counts else 0,
        }


# Embedder-specific configurations
EMBEDDER_CONFIGS = {
    "intfloat/e5-large-v2": {"chunk_size": 800, "overlap_ratio": 0.15, "max_tokens": 1024},
    "BAAI/bge-large-en-v1.5": {"chunk_size": 800, "overlap_ratio": 0.15, "max_tokens": 1024},
    "sentence-transformers/all-MiniLM-L6-v2": {"chunk_size": 400, "overlap_ratio": 0.15, "max_tokens": 512},
    "BAAI/bge-base-en-v1.5": {"chunk_size": 400, "overlap_ratio": 0.15, "max_tokens": 512},
}


def get_chunk_config(embedder_name: str) -> ChunkingConfig:
    """Get chunking configuration for embedder"""
    config_dict = EMBEDDER_CONFIGS.get(embedder_name, {"chunk_size": 400, "overlap_ratio": 0.15, "max_tokens": 512})

    return ChunkingConfig(
        embedder_name=embedder_name,
        chunk_size=config_dict["chunk_size"],
        overlap_ratio=config_dict["overlap_ratio"],
        max_tokens=config_dict["max_tokens"],
    )


def create_enhanced_chunker(embedder_name: str) -> EnhancedChunker:
    """Create enhanced chunker for embedder"""
    config = get_chunk_config(embedder_name)
    return EnhancedChunker(config)
