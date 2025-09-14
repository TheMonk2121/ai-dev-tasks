from __future__ import annotations
import logging
import os
import re
from typing import Any
from transformers import pipeline
import argparse
import sys
from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
Borderline NLI Gate for Final RAGAS Push

Implements a lightweight NLI check for sentences within ε of the keep threshold.
Only runs on borderline sentences to minimize computational cost while maximizing
precision gains and reducing unsupported claims.

Based on the proven strategy: Premise = best evidence snippet; Hypothesis = candidate sentence.
Keep borderline sentences only if entailment ≥ 0.60.
"""

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class BorderlineNLIGate:
    """Lightweight NLI gate for borderline sentence filtering."""

    def __init__(self):
        self.model = None
        self.cache = {}
        self.cache_enabled = True

        # Configuration from environment
        self.enabled = os.getenv("RAGCHECKER_NLI_ENABLE", "0") == "1"
        self.borderline_only = os.getenv("RAGCHECKER_NLI_ON_BORDERLINE", "1") == "1"
        self.borderline_band = float(os.getenv("RAGCHECKER_BORDERLINE_BAND", "0.02"))
        self.nli_threshold = float(os.getenv("RAGCHECKER_NLI_P_THRESHOLD", "0.60"))

        # Initialize model if enabled
        if self.enabled:
            self._initialize_model()

    def _initialize_model(self):
        """Initialize the NLI model."""
        try:

            logger.info("🔄 Loading NLI model for borderline gate...")
            # Use a lightweight NLI model
            self.model = pipeline(
                "text-classification", model="facebook/bart-large-mnli", device=-1
            )  # CPU only for efficiency
            logger.info("✅ NLI model loaded successfully")
        except ImportError:
            logger.warning("⚠️ transformers not available - NLI gate disabled")
            self.model = None
        except Exception as e:
            logger.error(f"❌ Failed to load NLI model: {e}")
            self.model = None

    def _get_cache_key(self, premise: str, hypothesis: str) -> str:
        """Generate cache key for premise-hypothesis pair."""
        return f"{hash(premise)}_{hash(hypothesis)}"

    def _check_entailment(self, premise: str, hypothesis: str) -> float:
        """Check entailment between premise and hypothesis."""
        if not self.model:
            return 0.0

        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(premise, hypothesis)
            if cache_key in self.cache:
                return self.cache[cache_key]

        try:
            # Run NLI prediction
            result = self.model(f"{premise} [SEP] {hypothesis}")

            # Extract entailment score
            entailment_score = 0.0
            for item in result:
                if item["label"] == "ENTAILMENT":
                    entailment_score = item["score"]
                    break

            # Cache the result
            if self.cache_enabled:
                self.cache[cache_key] = entailment_score

            return entailment_score
        except Exception as e:
            logger.warning(f"⚠️ NLI prediction failed: {e}")
            return 0.0

    def _find_best_evidence_snippet(self, sentence: str, contexts: list[str]) -> str | None:
        """Find the best evidence snippet for a sentence."""
        if not contexts:
            return None

        # Simple heuristic: find context with highest token overlap
        sentence_tokens = set(sentence.lower().split())
        best_context = None
        best_overlap = 0

        for context in contexts:
            context_tokens = set(context.lower().split())
            overlap = len(sentence_tokens & context_tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                best_context = context

        return best_context

    def _is_borderline_sentence(self, sentence: str, contexts: list[str], base_score: float, threshold: float) -> bool:
        """Check if a sentence is within the borderline band."""
        if not self.borderline_only:
            return True

        # Check if score is within borderline band of threshold
        return abs(base_score - threshold) <= self.borderline_band

    def filter_borderline_sentences(
        self, sentences: list[str], contexts: list[str], base_scores: list[float], threshold: float
    ) -> list[bool]:
        """Filter borderline sentences using NLI gate."""
        if not self.enabled or not self.model:
            # Return all True if NLI not available
            return [True] * len(sentences)

        logger.info(f"🔄 Running NLI gate on {len(sentences)} sentences...")

        keep_decisions = []
        nli_used_count = 0

        for i, (sentence, base_score) in enumerate(zip(sentences, base_scores)):
            # Check if sentence is borderline
            if self._is_borderline_sentence(sentence, contexts, base_score, threshold):
                # Find best evidence snippet
                premise = self._find_best_evidence_snippet(sentence, contexts)

                if premise:
                    # Run NLI check
                    entailment_score = self._check_entailment(premise, sentence)
                    nli_used_count += 1

                    # Keep if entailment ≥ threshold
                    keep = entailment_score >= self.nli_threshold
                    keep_decisions.append(keep)

                    if not keep:
                        logger.debug(f"🚫 NLI rejected: {sentence[:50]}... (entailment: {entailment_score:.3f})")
                else:
                    # No evidence snippet found, keep by default
                    keep_decisions.append(True)
            else:
                # Not borderline, keep based on base score
                keep_decisions.append(base_score >= threshold)

        logger.info(f"✅ NLI gate completed: {nli_used_count} sentences checked, {sum(keep_decisions)} kept")
        return keep_decisions

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.cache),
            "cache_enabled": self.cache_enabled,
            "model_loaded": self.model is not None,
            "enabled": self.enabled,
            "borderline_only": self.borderline_only,
            "borderline_band": self.borderline_band,
            "nli_threshold": self.nli_threshold,
        }

    def clear_cache(self):
        """Clear the NLI cache."""
        self.cache.clear()
        logger.info("🧹 NLI cache cleared")

class EnhancedEvidenceFilterWithNLI:
    """Enhanced evidence filter with NLI borderline gate."""

    def __init__(self):
        self.nli_gate = BorderlineNLIGate()

    def filter_with_nli_gate(self, answer: str, contexts: list[str]) -> str:
        """Filter evidence with NLI borderline gate."""
        # Split into sentences
        sentences = self._split_sentences(answer)
        if not sentences:
            return answer

        # Calculate base evidence scores
        base_scores = []
        for sentence in sentences:
            score = self._calculate_base_evidence_score(sentence, contexts)
            base_scores.append(score)

        # Get threshold
        threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))

        # Apply NLI gate to borderline sentences
        keep_decisions = self.nli_gate.filter_borderline_sentences(sentences, contexts, base_scores, threshold)

        # Filter sentences based on decisions
        filtered_sentences = []
        for sentence, keep in zip(sentences, keep_decisions):
            if keep:
                filtered_sentences.append(sentence)

        return " ".join(filtered_sentences)

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_base_evidence_score(self, sentence: str, contexts: list[str]) -> float:
        """Calculate base evidence score using existing methods."""
        # This would integrate with the existing evidence scoring logic
        # For now, return a simple token overlap score
        sentence_tokens = set(sentence.lower().split())
        max_overlap = 0

        for context in contexts:
            context_tokens = set(context.lower().split())
            overlap = len(sentence_tokens & context_tokens)
            if overlap > max_overlap:
                max_overlap = overlap

        return max_overlap / len(sentence_tokens) if sentence_tokens else 0.0

def main():
    """Test the NLI borderline gate."""

    parser = argparse.ArgumentParser(description="NLI Borderline Gate Test")
    parser.add_argument("--test", action="store_true", help="Run basic test")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache")

    args = parser.parse_args()

    # Enable NLI gate
    os.environ["RAGCHECKER_NLI_ENABLE"] = "1"

    nli_gate = BorderlineNLIGate()

    if args.stats:
        stats = nli_gate.get_cache_stats()
        print("📊 NLI Gate Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    if args.clear_cache:
        nli_gate.clear_cache()
        print("✅ Cache cleared")

    if args.test:
        print("🧪 Running NLI gate test...")

        # Test data
        sentences = [
            "The memory system uses a three-tier architecture.",
            "Memory rehydration is handled by the unified orchestrator.",
            "The system supports both local and cloud-based storage.",
            "Cross-encoder reranking improves precision significantly.",
        ]
        contexts = [
            "The memory system architecture consists of three main components: SQL database for structured data, pgvector for semantic embeddings, and knowledge graph for relational information.",
            "Memory rehydration is a critical process that restores context from previous sessions using the unified memory orchestrator.",
        ]
        base_scores = [0.08, 0.06, 0.05, 0.04]  # Some borderline scores
        threshold = 0.07

        # Test NLI gate
        keep_decisions = nli_gate.filter_borderline_sentences(sentences, contexts, base_scores, threshold)

        print("📊 NLI Gate Results:")
        for i, (sentence, keep) in enumerate(zip(sentences, keep_decisions), 1):
            status = "✅ KEEP" if keep else "🚫 REJECT"
            print(f"  {i}. {status} - {sentence[:50]}...")

        # Test enhanced filter
        enhanced_filter = EnhancedEvidenceFilterWithNLI()
        test_answer = " ".join(sentences)
        filtered = enhanced_filter.filter_with_nli_gate(test_answer, contexts)

        print(f"\n📝 Original: {len(test_answer)} chars")
        print(f"📝 Filtered: {len(filtered)} chars")
        print(f"📝 Filtered text: {filtered[:200]}...")

if __name__ == "__main__":
    main()
