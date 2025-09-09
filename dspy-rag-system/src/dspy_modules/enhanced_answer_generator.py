#!/usr/bin/env python3
"""
Enhanced Answer Generator with Answer Discipline
Implements the coach's strategy: extractive-first, citations, abstention
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class EnhancedAnswerGenerator:
    """
    Enhanced answer generator implementing the coach's strategy:
    - Extractive-first approach
    - Require 2+ citations
    - Abstention for insufficient context
    - Code-aware formatting
    """

    def __init__(
        self,
        min_citations: int = 2,
        max_answer_length: int = 500,
        enable_abstention: bool = True,
        code_formatting: bool = True,
    ):
        self.min_citations = min_citations
        self.max_answer_length = max_answer_length
        self.enable_abstention = enable_abstention
        self.code_formatting = code_formatting

        logger.info(
            f"EnhancedAnswerGenerator initialized: min_citations={min_citations}, "
            f"max_length={max_answer_length}, abstention={enable_abstention}"
        )

    def generate_enhanced_answer(
        self, query: str, retrieved_chunks: list[dict[str, Any]], query_type: str | None = None
    ) -> dict[str, Any]:
        """
        Generate enhanced answer with discipline
        """
        try:
            # Validate context sufficiency
            if not self._has_sufficient_context(retrieved_chunks):
                if self.enable_abstention:
                    return self._generate_abstention_response(query)
                else:
                    logger.warning("Insufficient context but abstention disabled")

            # Generate structured answer
            answer = self._generate_structured_answer(query, retrieved_chunks, query_type)

            # Validate answer quality
            validation = self._validate_answer_quality(answer, retrieved_chunks)

            return {
                "answer": answer,
                "validation": validation,
                "metadata": {
                    "query_type": query_type,
                    "chunks_used": len(retrieved_chunks),
                    "citations_count": validation.get("citations_count", 0),
                    "abstention": False,
                },
            }

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return self._generate_error_response(query, str(e))

    def _has_sufficient_context(self, chunks: list[dict]) -> bool:
        """Check if we have sufficient context for a quality answer"""
        if not chunks:
            return False

        # Check for minimum content length
        total_content = sum(len(chunk.get("text", "")) for chunk in chunks)
        if total_content < 200:  # Minimum 200 chars
            return False

        # Check for diverse sources
        unique_sources = len(set(chunk.get("chunk_id", "") for chunk in chunks))
        if unique_sources < 2:  # Need at least 2 different chunks
            return False

        return True

    def _generate_abstention_response(self, query: str) -> dict[str, Any]:
        """Generate abstention response when context is insufficient"""
        abstention_text = (
            f"I cannot provide a complete answer to '{query}' based on the available context. "
            "The retrieved information is insufficient to give a comprehensive and accurate response. "
            "Please try rephrasing your question or provide more specific context."
        )

        return {
            "answer": abstention_text,
            "validation": {
                "citations_count": 0,
                "has_sufficient_context": False,
                "abstention_reason": "insufficient_context",
            },
            "metadata": {"query_type": "abstention", "chunks_used": 0, "citations_count": 0, "abstention": True},
        }

    def _generate_structured_answer(self, query: str, chunks: list[dict], query_type: str | None) -> str:
        """Generate structured answer with proper formatting"""

        # Start with direct answer
        if query_type == "implementation":
            answer = self._generate_implementation_answer(query, chunks)
        else:
            answer = self._generate_explanatory_answer(query, chunks)

        # Add citations
        answer += self._add_citations(chunks)

        # Add confidence statement
        answer += self._add_confidence_statement(chunks)

        return answer

    def _generate_implementation_answer(self, query: str, chunks: list[dict]) -> str:
        """Generate implementation-focused answer"""
        # Find code chunks first
        code_chunks = [c for c in chunks if c.get("chunk_type", "").startswith("code")]
        other_chunks = [c for c in chunks if not c.get("chunk_type", "").startswith("code")]

        # Prioritize code chunks for implementation queries
        prioritized_chunks = code_chunks + other_chunks

        answer = f"Based on the available code and documentation, here's how to implement {query}:\n\n"

        # Add implementation details
        for i, chunk in enumerate(prioritized_chunks[:3]):  # Top 3 chunks
            chunk_text = chunk.get("text", "")
            if chunk.get("chunk_type", "").startswith("code"):
                # Format code properly
                answer += f"**Code Example {i+1}:**\n```\n{chunk_text}\n```\n\n"
            else:
                answer += f"**Implementation Detail {i+1}:** {chunk_text}\n\n"

        return answer

    def _generate_explanatory_answer(self, query: str, chunks: list[dict]) -> str:
        """Generate explanatory answer"""
        answer = f"Here's what I found about {query}:\n\n"

        # Add explanation from chunks
        for i, chunk in enumerate(chunks[:3]):  # Top 3 chunks
            chunk_text = chunk.get("text", "")
            answer += f"**Point {i+1}:** {chunk_text}\n\n"

        return answer

    def _add_citations(self, chunks: list[dict]) -> str:
        """Add citations to the answer"""
        citations = []

        for i, chunk in enumerate(chunks[: self.min_citations]):
            chunk_id = chunk.get("chunk_id", f"chunk_{i+1}")
            chunk_type = chunk.get("chunk_type", "unknown")

            citation = f"[{i+1}] {chunk_id}"
            if chunk_type.startswith("code"):
                citation += " (code)"
            elif chunk_type.startswith("markdown"):
                citation += " (documentation)"

            citations.append(citation)

        if citations:
            return "\n**Sources:**\n" + "\n".join(citations) + "\n"
        else:
            return "\n**Sources:** No specific sources identified.\n"

    def _add_confidence_statement(self, chunks: list[dict]) -> str:
        """Add confidence statement based on context quality"""
        total_chunks = len(chunks)
        avg_completeness = sum(chunk.get("metadata", {}).get("completeness_score", 0.5) for chunk in chunks) / max(
            total_chunks, 1
        )

        if avg_completeness > 0.8 and total_chunks >= 3:
            confidence = "high"
        elif avg_completeness > 0.6 and total_chunks >= 2:
            confidence = "moderate"
        else:
            confidence = "limited"

        return f"\n**Confidence:** {confidence.capitalize()} (based on {total_chunks} context chunks)"

    def _validate_answer_quality(self, answer: str, chunks: list[dict]) -> dict[str, Any]:
        """Validate answer quality"""
        citations_count = answer.count("[") // 2  # Rough count of [X] citations

        validation = {
            "citations_count": citations_count,
            "has_sufficient_context": len(chunks) >= 2,
            "answer_length": len(answer),
            "meets_citation_requirement": citations_count >= self.min_citations,
            "chunk_diversity": len(set(c.get("chunk_id", "") for c in chunks)),
        }

        return validation

    def _generate_error_response(self, query: str, error_msg: str) -> dict[str, Any]:
        """Generate error response"""
        return {
            "answer": f"Error generating answer for '{query}': {error_msg}",
            "validation": {"citations_count": 0, "has_sufficient_context": False, "error": True},
            "metadata": {
                "query_type": "error",
                "chunks_used": 0,
                "citations_count": 0,
                "abstention": False,
                "error": error_msg,
            },
        }

    def get_generator_stats(self) -> dict[str, Any]:
        """Get generator statistics"""
        return {
            "min_citations": self.min_citations,
            "max_answer_length": self.max_answer_length,
            "enable_abstention": self.enable_abstention,
            "code_formatting": self.code_formatting,
            "generator_type": "enhanced_disciplined",
        }


def create_enhanced_generator(
    min_citations: int = 2, max_answer_length: int = 500, enable_abstention: bool = True, code_formatting: bool = True
) -> EnhancedAnswerGenerator:
    """Factory function to create enhanced answer generator"""
    return EnhancedAnswerGenerator(
        min_citations=min_citations,
        max_answer_length=max_answer_length,
        enable_abstention=enable_abstention,
        code_formatting=code_formatting,
    )
