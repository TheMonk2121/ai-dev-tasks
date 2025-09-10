#!/usr/bin/env python3
"""
Optimized Embedding Generation
- Device-aware model loading (MPS/CUDA/CPU)
- Batch processing for efficiency
- Tokenizer reuse to avoid re-initialization
- Threading optimization
"""

import logging
import os
import time

import torch
from sentence_transformers import SentenceTransformer

LOG = logging.getLogger(__name__)


class OptimizedEmbedder:
    """Optimized embedding generator with device awareness and batching."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        batch_size: int = 64,
        max_sequence_length: int = 512,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_sequence_length = max_sequence_length

        # Device selection with MPS optimization
        if device is None:
            if torch.backends.mps.is_available():
                self.device = "mps"
                LOG.info("Using MPS (Apple Silicon) for embeddings")
                # MPS-specific optimizations
                torch.mps.empty_cache()
            elif torch.cuda.is_available():
                self.device = "cuda"
                LOG.info("Using CUDA for embeddings")
            else:
                self.device = "cpu"
                LOG.info("Using CPU for embeddings")
        else:
            self.device = device

        # Threading optimization - tune for your system
        if self.device == "mps":
            torch.set_num_threads(8)  # MPS can handle more threads
        elif self.device == "cuda":
            torch.set_num_threads(4)  # CUDA threading
        else:
            torch.set_num_threads(4)  # CPU threading

        # Load model once
        self._load_model()

    def _load_model(self):
        """Load the embedding model with device optimization."""
        start_time = time.time()

        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=os.path.join(os.getcwd(), ".cache", "sentence_transformers"),
            )

            # Warm up the model with a dummy inference
            dummy_text = "This is a warmup text for the embedding model."
            _ = self.model.encode(dummy_text, convert_to_tensor=True)

            load_time = time.time() - start_time
            LOG.info(f"Model loaded in {load_time:.2f}s on {self.device}")

        except Exception as e:
            LOG.error(f"Failed to load model on {self.device}: {e}")
            # Fallback to CPU
            if self.device != "cpu":
                LOG.info("Falling back to CPU")
                self.device = "cpu"
                self.model = SentenceTransformer(
                    self.model_name,
                    device="cpu",
                    cache_folder=os.path.join(os.getcwd(), ".cache", "sentence_transformers"),
                )
            else:
                raise

    def encode_single(self, text: str) -> list[float]:
        """Encode a single text with optimized settings."""
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * 384  # all-MiniLM-L6-v2 dimension

        try:
            embedding = self.model.encode(
                text, convert_to_tensor=False, normalize_embeddings=True, show_progress_bar=False, batch_size=1
            )
            return embedding.tolist()
        except Exception as e:
            LOG.error(f"Failed to encode text: {e}")
            # Return zero vector as fallback
            return [0.0] * 384

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """Encode a batch of texts efficiently."""
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            return [[0.0] * 384] * len(texts)

        try:
            embeddings = self.model.encode(
                valid_texts,
                batch_size=min(self.batch_size, len(valid_texts)),
                convert_to_tensor=False,
                normalize_embeddings=True,
                show_progress_bar=False,
                device=self.device,
            )

            # Convert to list format
            result = []
            valid_idx = 0

            for text in texts:
                if text and text.strip():
                    result.append(embeddings[valid_idx].tolist())
                    valid_idx += 1
                else:
                    result.append([0.0] * 384)

            return result

        except Exception as e:
            LOG.error(f"Failed to encode batch: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 384] * len(texts)

    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension for this model."""
        # Common model dimensions
        dim_map = {
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "all-distilroberta-v1": 768,
            "intfloat/e5-large-v2": 1024,
            "text-embedding-ada-002": 1536,
        }
        return dim_map.get(self.model_name, 384)

    def benchmark(self, num_texts: int = 100) -> dict:
        """Benchmark embedding performance."""
        import random
        import string

        # Generate random texts
        texts = [
            "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(50, 500)))
            for _ in range(num_texts)
        ]

        # Single encoding benchmark
        start_time = time.time()
        for text in texts[:10]:  # Test with 10 texts
            _ = self.encode_single(text)
        single_time = (time.time() - start_time) / 10

        # Batch encoding benchmark
        start_time = time.time()
        _ = self.encode_batch(texts)
        batch_time = (time.time() - start_time) / num_texts

        return {
            "device": self.device,
            "model": self.model_name,
            "single_encoding_ms": single_time * 1000,
            "batch_encoding_ms": batch_time * 1000,
            "speedup": single_time / batch_time if batch_time > 0 else 0,
            "dimension": self.get_embedding_dimension(),
        }


# Global instance for reuse
_embedder_instance: OptimizedEmbedder | None = None


def get_embedder() -> OptimizedEmbedder:
    """Get or create the global embedder instance."""
    global _embedder_instance

    if _embedder_instance is None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "64"))
        device = os.getenv("EMBEDDING_DEVICE")

        _embedder_instance = OptimizedEmbedder(model_name=model_name, device=device, batch_size=batch_size)

    return _embedder_instance


def encode_text(text: str) -> list[float]:
    """Convenience function for single text encoding."""
    return get_embedder().encode_single(text)


def encode_texts(texts: list[str]) -> list[list[float]]:
    """Convenience function for batch text encoding."""
    return get_embedder().encode_batch(texts)


if __name__ == "__main__":
    # Benchmark the embedder
    embedder = OptimizedEmbedder()
    results = embedder.benchmark()

    print("🔍 Embedding Performance Benchmark")
    print("=" * 50)
    print(f"Device: {results['device']}")
    print(f"Model: {results['model']}")
    print(f"Dimension: {results['dimension']}")
    print(f"Single encoding: {results['single_encoding_ms']:.1f}ms")
    print(f"Batch encoding: {results['batch_encoding_ms']:.1f}ms")
    print(f"Speedup: {results['speedup']:.1f}x")

    if results["batch_encoding_ms"] < 50:
        print("✅ Performance: Excellent")
    elif results["batch_encoding_ms"] < 100:
        print("✅ Performance: Good")
    elif results["batch_encoding_ms"] < 200:
        print("⚠️  Performance: Acceptable")
    else:
        print("❌ Performance: Needs optimization")
