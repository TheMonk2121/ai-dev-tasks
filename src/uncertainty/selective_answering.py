"""
Phase 4: Selective Answering Module

Implements evidence quality-based abstention mechanisms and selective
prediction grounding for production-safe RAG responses.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class AbstentionReason(Enum):
    """Reasons for abstaining from answering."""
    LOW_CONFIDENCE = "low_confidence"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW_COVERAGE = "low_coverage"
    HIGH_DISPERSION = "high_dispersion"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    OUT_OF_DOMAIN = "out_of_domain"
    UNCLEAR_INTENT = "unclear_intent"


@dataclass
class EvidenceQuality:
    """Evidence quality metrics for selective answering."""
    
    # Coverage metrics
    coverage_score: float  # Fraction of sub-claims with supporting evidence
    claim_coverage: Dict[str, float]  # Per-claim coverage scores
    
    # Concentration metrics
    dispersion_score: float  # How scattered the evidence is (lower = better)
    top_score_mean: float  # Mean of top evidence scores
    top_score_std: float  # Standard deviation of top evidence scores
    
    # Evidence strength
    max_evidence_score: float  # Highest evidence score
    mean_evidence_score: float  # Mean evidence score
    evidence_count: int  # Number of evidence pieces
    
    # Contradiction detection
    has_contradictions: bool  # Whether evidence contains contradictions
    contradiction_score: float  # Strength of contradictions (0-1)


@dataclass
class SelectiveAnsweringConfig:
    """Configuration for selective answering."""
    
    # Confidence thresholds
    min_confidence: float = 0.3
    abstain_threshold: float = 0.4
    high_confidence_threshold: float = 0.8
    
    # Coverage thresholds
    min_coverage: float = 0.6
    min_claim_coverage: float = 0.5
    
    # Concentration thresholds
    max_dispersion: float = 0.4
    min_top_score_mean: float = 0.6
    
    # Evidence thresholds
    min_evidence_count: int = 2
    min_max_evidence_score: float = 0.5
    
    # Contradiction thresholds
    max_contradiction_score: float = 0.3
    
    # Intent classification
    enable_intent_classification: bool = True
    unclear_intent_threshold: float = 0.3
    
    # Output configuration
    show_evidence_on_abstain: bool = True
    include_abstention_reason: bool = True
    suggest_alternatives: bool = True


class SelectiveAnswering:
    """
    Implements selective answering with evidence quality-based abstention.
    
    Features:
    - Evidence coverage and concentration analysis
    - Contradiction detection
    - Intent classification for unclear queries
    - Configurable abstention thresholds
    - Evidence surfacing on abstention
    """
    
    def __init__(self, config: SelectiveAnsweringConfig):
        self.config = config
        logger.info("Initialized Selective Answering with evidence quality thresholds")
    
    def evaluate_answer_quality(
        self,
        query: str,
        answer: str,
        evidence_chunks: List[Dict[str, Any]],
        confidence_score: float,
        sub_claims: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of an answer for selective answering decisions.
        
        Args:
            query: User query
            answer: Generated answer
            evidence_chunks: List of evidence chunks with scores
            confidence_score: Raw confidence score
            sub_claims: List of sub-claims to check coverage
            
        Returns:
            Quality evaluation results
        """
        logger.info(f"Evaluating answer quality for query: {query[:50]}...")
        
        # Extract evidence quality metrics
        evidence_quality = self._analyze_evidence_quality(
            evidence_chunks, sub_claims
        )
        
        # Analyze answer consistency with evidence
        consistency_score = self._check_answer_consistency(answer, evidence_chunks)
        
        # Classify query intent
        intent_classification = self._classify_query_intent(query)
        
        # Determine if we should abstain
        abstention_decision = self._make_abstention_decision(
            confidence_score, evidence_quality, consistency_score, intent_classification
        )
        
        # Generate abstention reason if applicable
        abstention_reason = None
        if abstention_decision["should_abstain"]:
            abstention_reason = self._determine_abstention_reason(
                confidence_score, evidence_quality, consistency_score, intent_classification
            )
        
        return {
            "should_abstain": abstention_decision["should_abstain"],
            "abstention_reason": abstention_reason,
            "confidence_score": confidence_score,
            "evidence_quality": evidence_quality,
            "consistency_score": consistency_score,
            "intent_classification": intent_classification,
            "quality_score": abstention_decision["quality_score"],
            "recommendations": abstention_decision["recommendations"]
        }
    
    def _analyze_evidence_quality(
        self,
        evidence_chunks: List[Dict[str, Any]],
        sub_claims: Optional[List[str]] = None
    ) -> EvidenceQuality:
        """Analyze the quality of evidence chunks."""
        
        if not evidence_chunks:
            return EvidenceQuality(
                coverage_score=0.0,
                claim_coverage={},
                dispersion_score=1.0,
                top_score_mean=0.0,
                top_score_std=0.0,
                max_evidence_score=0.0,
                mean_evidence_score=0.0,
                evidence_count=0,
                has_contradictions=False,
                contradiction_score=0.0
            )
        
        # Extract scores
        scores = [chunk.get("score", 0.0) for chunk in evidence_chunks]
        scores = np.array(scores)
        
        # Basic statistics
        evidence_count = len(scores)
        max_evidence_score = np.max(scores)
        mean_evidence_score = np.mean(scores)
        
        # Top score analysis (top 3)
        top_k = min(3, evidence_count)
        top_scores = np.sort(scores)[-top_k:]
        top_score_mean = np.mean(top_scores)
        top_score_std = np.std(top_scores) if top_k > 1 else 0.0
        
        # Dispersion analysis
        dispersion_score = self._calculate_dispersion(scores)
        
        # Coverage analysis
        coverage_score, claim_coverage = self._calculate_coverage(
            evidence_chunks, sub_claims
        )
        
        # Contradiction detection
        has_contradictions, contradiction_score = self._detect_contradictions(
            evidence_chunks
        )
        
        return EvidenceQuality(
            coverage_score=coverage_score,
            claim_coverage=claim_coverage,
            dispersion_score=dispersion_score,
            top_score_mean=top_score_mean,
            top_score_std=top_score_std,
            max_evidence_score=max_evidence_score,
            mean_evidence_score=mean_evidence_score,
            evidence_count=evidence_count,
            has_contradictions=has_contradictions,
            contradiction_score=contradiction_score
        )
    
    def _calculate_dispersion(self, scores: np.ndarray) -> float:
        """Calculate how scattered the evidence scores are."""
        if len(scores) <= 1:
            return 0.0
        
        # Normalize scores to 0-1 range
        if np.max(scores) > 0:
            normalized_scores = scores / np.max(scores)
        else:
            return 0.0
        
        # Calculate coefficient of variation
        mean_score = np.mean(normalized_scores)
        if mean_score > 0:
            cv = np.std(normalized_scores) / mean_score
            # Convert to 0-1 scale where 0 = no dispersion, 1 = high dispersion
            return min(1.0, cv)
        else:
            return 0.0
    
    def _calculate_coverage(
        self,
        evidence_chunks: List[Dict[str, Any]],
        sub_claims: Optional[List[str]] = None
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate coverage of evidence across sub-claims."""
        
        if not sub_claims:
            # If no sub-claims specified, use overall evidence strength
            if evidence_chunks:
                avg_score = np.mean([chunk.get("score", 0.0) for chunk in evidence_chunks])
                return avg_score, {}
            else:
                return 0.0, {}
        
        # Calculate per-claim coverage
        claim_coverage = {}
        covered_claims = 0
        
        for claim in sub_claims:
            # Find evidence chunks that support this claim
            supporting_chunks = [
                chunk for chunk in evidence_chunks
                if self._claim_supported_by_chunk(claim, chunk)
            ]
            
            if supporting_chunks:
                # Calculate claim coverage based on evidence strength
                claim_scores = [chunk.get("score", 0.0) for chunk in supporting_chunks]
                claim_coverage[claim] = np.mean(claim_scores)
                if np.mean(claim_scores) >= self.config.min_claim_coverage:
                    covered_claims += 1
            else:
                claim_coverage[claim] = 0.0
        
        # Overall coverage is fraction of claims with sufficient evidence
        overall_coverage = covered_claims / len(sub_claims)
        
        return overall_coverage, claim_coverage
    
    def _claim_supported_by_chunk(
        self, 
        claim: str, 
        chunk: Dict[str, Any]
    ) -> bool:
        """Check if a claim is supported by an evidence chunk."""
        # Simple keyword matching - could be enhanced with semantic similarity
        chunk_text = chunk.get("text", "").lower()
        claim_keywords = claim.lower().split()
        
        # Check if key claim words appear in chunk
        keyword_matches = sum(1 for keyword in claim_keywords if keyword in chunk_text)
        return keyword_matches >= max(1, len(claim_keywords) // 2)
    
    def _detect_contradictions(
        self, 
        evidence_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, float]:
        """Detect contradictions in evidence chunks."""
        
        if len(evidence_chunks) < 2:
            return False, 0.0
        
        # Simple contradiction detection based on semantic similarity
        # In production, this could use more sophisticated NLP techniques
        
        contradiction_score = 0.0
        has_contradictions = False
        
        # Check for high-scoring chunks with very different content
        high_scoring_chunks = [
            chunk for chunk in evidence_chunks
            if chunk.get("score", 0.0) > self.config.min_max_evidence_score
        ]
        
        if len(high_scoring_chunks) >= 2:
            # Calculate pairwise similarity (simplified)
            similarities = []
            for i, chunk1 in enumerate(high_scoring_chunks):
                for j, chunk2 in enumerate(high_scoring_chunks[i+1:], i+1):
                    similarity = self._calculate_chunk_similarity(chunk1, chunk2)
                    similarities.append(similarity)
            
            if similarities:
                avg_similarity = np.mean(similarities)
                # Low similarity with high scores suggests potential contradictions
                if avg_similarity < 0.3:
                    has_contradictions = True
                    contradiction_score = 1.0 - avg_similarity
        
        return has_contradictions, contradiction_score
    
    def _calculate_chunk_similarity(
        self, 
        chunk1: Dict[str, Any], 
        chunk2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two evidence chunks."""
        # Simple Jaccard similarity on words
        text1 = set(chunk1.get("text", "").lower().split())
        text2 = set(chunk2.get("text", "").lower().split())
        
        if not text1 or not text2:
            return 0.0
        
        intersection = len(text1.intersection(text2))
        union = len(text1.union(text2))
        
        return intersection / union if union > 0 else 0.0
    
    def _check_answer_consistency(
        self, 
        answer: str, 
        evidence_chunks: List[Dict[str, Any]]
    ) -> float:
        """Check if the answer is consistent with the evidence."""
        
        if not evidence_chunks:
            return 0.0
        
        # Extract key information from answer
        answer_keywords = set(answer.lower().split())
        
        # Check how many evidence chunks support the answer
        supporting_chunks = 0
        total_score = 0.0
        
        for chunk in evidence_chunks:
            chunk_text = chunk.get("text", "").lower()
            chunk_score = chunk.get("score", 0.0)
            
            # Check if chunk supports answer content
            if self._chunk_supports_answer(chunk_text, answer_keywords):
                supporting_chunks += 1
                total_score += chunk_score
        
        if supporting_chunks == 0:
            return 0.0
        
        # Consistency score based on supporting evidence strength
        avg_supporting_score = total_score / supporting_chunks
        support_ratio = supporting_chunks / len(evidence_chunks)
        
        return (avg_supporting_score + support_ratio) / 2
    
    def _chunk_supports_answer(
        self, 
        chunk_text: str, 
        answer_keywords: set
    ) -> bool:
        """Check if a chunk supports the answer content."""
        # Simple keyword overlap check
        chunk_words = set(chunk_text.split())
        overlap = len(answer_keywords.intersection(chunk_words))
        
        # Require at least some keyword overlap
        return overlap >= max(1, len(answer_keywords) // 4)
    
    def _classify_query_intent(self, query: str) -> Dict[str, Any]:
        """Classify the intent of the query."""
        
        if not self.config.enable_intent_classification:
            return {"intent": "general", "confidence": 1.0}
        
        query_lower = query.lower()
        
        # Simple rule-based intent classification
        intent_patterns = {
            "lookup": ["what is", "who is", "when", "where", "definition"],
            "comparison": ["compare", "difference", "vs", "versus", "better"],
            "explanation": ["why", "how", "explain", "reason", "cause"],
            "analysis": ["analyze", "evaluate", "assess", "review"],
            "structured": ["sql", "query", "table", "data", "number"]
        }
        
        intent_scores = {}
        for intent, patterns in intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in query_lower)
            intent_scores[intent] = score / len(patterns)
        
        # Find best intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # Check if intent is unclear
        is_unclear = best_intent[1] < self.config.unclear_intent_threshold
        
        return {
            "intent": best_intent[0] if not is_unclear else "unclear",
            "confidence": best_intent[1],
            "is_unclear": is_unclear,
            "all_scores": intent_scores
        }
    
    def _make_abstention_decision(
        self,
        confidence_score: float,
        evidence_quality: EvidenceQuality,
        consistency_score: float,
        intent_classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make the final abstention decision."""
        
        should_abstain = False
        reasons = []
        quality_score = 0.0
        
        # Check confidence threshold
        if confidence_score < self.config.abstain_threshold:
            should_abstain = True
            reasons.append("Confidence below abstain threshold")
        
        # Check evidence coverage
        if evidence_quality.coverage_score < self.config.min_coverage:
            should_abstain = True
            reasons.append("Insufficient evidence coverage")
        
        # Check evidence concentration
        if evidence_quality.dispersion_score > self.config.max_dispersion:
            should_abstain = True
            reasons.append("Evidence too scattered")
        
        # Check evidence strength
        if evidence_quality.max_evidence_score < self.config.min_max_evidence_score:
            should_abstain = True
            reasons.append("Evidence too weak")
        
        # Check evidence count
        if evidence_quality.evidence_count < self.config.min_evidence_count:
            should_abstain = True
            reasons.append("Too few evidence pieces")
        
        # Check contradictions
        if evidence_quality.has_contradictions and \
           evidence_quality.contradiction_score > self.config.max_contradiction_score:
            should_abstain = True
            reasons.append("Contradictory evidence detected")
        
        # Check intent clarity
        if intent_classification.get("is_unclear", False):
            should_abstain = True
            reasons.append("Unclear query intent")
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(
            confidence_score, evidence_quality, consistency_score, intent_classification
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            should_abstain, reasons, quality_score, evidence_quality
        )
        
        return {
            "should_abstain": should_abstain,
            "quality_score": quality_score,
            "reasons": reasons,
            "recommendations": recommendations
        }
    
    def _calculate_quality_score(
        self,
        confidence_score: float,
        evidence_quality: EvidenceQuality,
        consistency_score: float,
        intent_classification: Dict[str, Any]
    ) -> float:
        """Calculate overall quality score."""
        
        # Weighted combination of factors
        weights = {
            "confidence": 0.3,
            "coverage": 0.25,
            "concentration": 0.2,
            "consistency": 0.15,
            "intent": 0.1
        }
        
        # Normalize scores to 0-1 range
        coverage_norm = min(1.0, evidence_quality.coverage_score / self.config.min_coverage)
        concentration_norm = max(0.0, 1.0 - evidence_quality.dispersion_score)
        intent_norm = intent_classification.get("confidence", 0.0)
        
        quality_score = (
            weights["confidence"] * confidence_score +
            weights["coverage"] * coverage_norm +
            weights["concentration"] * concentration_norm +
            weights["consistency"] * consistency_score +
            weights["intent"] * intent_norm
        )
        
        return min(1.0, max(0.0, quality_score))
    
    def _generate_recommendations(
        self,
        should_abstain: bool,
        reasons: List[str],
        quality_score: float,
        evidence_quality: EvidenceQuality
    ) -> List[str]:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        if should_abstain:
            if "Insufficient evidence coverage" in reasons:
                recommendations.append("Refine query to be more specific")
                recommendations.append("Expand search scope or use broader terms")
            
            if "Evidence too scattered" in reasons:
                recommendations.append("Focus query on a single aspect")
                recommendations.append("Use more specific search terms")
            
            if "Evidence too weak" in reasons:
                recommendations.append("Check data source quality")
                recommendations.append("Consider alternative information sources")
            
            if "Too few evidence pieces" in reasons:
                recommendations.append("Broaden search to include more sources")
                recommendations.append("Use less restrictive search criteria")
            
            if "Contradictory evidence detected" in reasons:
                recommendations.append("Verify data source consistency")
                recommendations.append("Check for data staleness or conflicts")
            
            if "Unclear query intent" in reasons:
                recommendations.append("Rephrase query with more specific terms")
                recommendations.append("Clarify what type of information is needed")
        else:
            if quality_score < 0.7:
                recommendations.append("Consider refining query for better results")
                recommendations.append("Monitor answer quality in production")
            
            if evidence_quality.evidence_count < 5:
                recommendations.append("Additional evidence sources may improve confidence")
        
        return recommendations
    
    def _determine_abstention_reason(
        self,
        confidence_score: float,
        evidence_quality: EvidenceQuality,
        consistency_score: float,
        intent_classification: Dict[str, Any]
    ) -> AbstentionReason:
        """Determine the primary reason for abstention."""
        
        # Priority order for abstention reasons
        if confidence_score < self.config.abstain_threshold:
            return AbstentionReason.LOW_CONFIDENCE
        
        if evidence_quality.coverage_score < self.config.min_coverage:
            return AbstentionReason.LOW_COVERAGE
        
        if evidence_quality.dispersion_score > self.config.max_dispersion:
            return AbstentionReason.HIGH_DISPERSION
        
        if evidence_quality.has_contradictions:
            return AbstentionReason.CONTRADICTORY_EVIDENCE
        
        if intent_classification.get("is_unclear", False):
            return AbstentionReason.UNCLEAR_INTENT
        
        if evidence_quality.evidence_count < self.config.min_evidence_count:
            return AbstentionReason.INSUFFICIENT_EVIDENCE
        
        return AbstentionReason.INSUFFICIENT_EVIDENCE
    
    def format_abstention_response(
        self,
        query: str,
        evaluation_result: Dict[str, Any],
        evidence_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format a response when abstaining from answering."""
        
        response = {
            "query": query,
            "answer": None,
            "abstained": True,
            "abstention_reason": evaluation_result["abstention_reason"].value,
            "confidence_score": evaluation_result["confidence_score"],
            "quality_score": evaluation_result["quality_score"]
        }
        
        if self.config.include_abstention_reason:
            response["reason"] = evaluation_result["abstention_reason"].value
            response["recommendations"] = evaluation_result["recommendations"]
        
        if self.config.show_evidence_on_abstain and evidence_chunks:
            # Show top evidence pieces to help user understand
            top_chunks = sorted(
                evidence_chunks, 
                key=lambda x: x.get("score", 0.0), 
                reverse=True
            )[:3]
            
            response["top_evidence"] = [
                {
                    "text": chunk.get("text", "")[:200] + "...",
                    "score": chunk.get("score", 0.0),
                    "source": chunk.get("source", "unknown")
                }
                for chunk in top_chunks
            ]
        
        if self.config.suggest_alternatives:
            response["suggestions"] = [
                "Refine your query to be more specific",
                "Use different search terms",
                "Check if the information exists in our knowledge base",
                "Contact support for assistance"
            ]
        
        return response
