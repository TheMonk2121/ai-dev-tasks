#!/usr/bin/env python3
"""
Faithfulness Evaluator for RAG Systems

This module implements faithfulness testing following RAGAS standards to measure
factual consistency between generated responses and retrieved context.

RAGAS Faithfulness: Measures the factual consistency of the generated answer 
against the given context. If any claims are made in the answer that cannot be 
deduced from context, then these will be penalized.

Implementation follows the two-step paradigm:
1. Extract claims from the generated answer
2. Verify each claim against the retrieved context
"""

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class ClaimType(Enum):
    """Types of claims that can be extracted from responses."""
    FACT = "fact"
    ASSERTION = "assertion"
    STATEMENT = "statement"
    CLAIM = "claim"


@dataclass
class ExtractedClaim:
    """Represents a single claim extracted from a response."""
    text: str
    claim_type: ClaimType
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class FaithfulnessResult:
    """Result of faithfulness evaluation."""
    faithfulness_score: float  # 0-1 scale
    total_claims: int
    verified_claims: int
    unverified_claims: int
    hallucinated_claims: int
    claim_details: List[Dict[str, Any]]
    overall_assessment: str


class FaithfulnessEvaluator:
    """Evaluates faithfulness of responses against retrieved context."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.claim_extraction_prompt = self._create_claim_extraction_prompt()
        self.claim_verification_prompt = self._create_claim_verification_prompt()
    
    def _create_claim_extraction_prompt(self) -> str:
        """Create prompt for extracting claims from responses."""
        return """
        Extract factual claims from the following response. A claim is a statement that can be verified as true or false.

        Guidelines:
        - Focus on factual statements, not opinions or questions
        - Extract specific claims that can be verified
        - Include claims about processes, systems, features, or capabilities
        - Exclude general statements that are too vague to verify

        Response to analyze:
        {response}

        Extract claims in JSON format:
        [
            {
                "claim": "specific factual statement",
                "type": "fact|assertion|statement",
                "confidence": 0.0-1.0,
                "start_pos": character_position,
                "end_pos": character_position
            }
        ]
        """
    
    def _create_claim_verification_prompt(self) -> str:
        """Create prompt for verifying claims against context."""
        return """
        Verify if the following claim can be supported by the provided context.

        Claim: {claim}

        Context: {context}

        Instructions:
        1. Determine if the claim is directly supported by the context
        2. Look for explicit statements that support the claim
        3. Consider if the claim can be logically inferred from the context
        4. Be strict - if the context doesn't clearly support the claim, mark it as unverified

        Respond with JSON:
        {{
            "verified": true/false,
            "confidence": 0.0-1.0,
            "reasoning": "explanation of why the claim is verified or not",
            "supporting_evidence": "specific text from context that supports the claim (if verified)"
        }}
        """
    
    def extract_claims(self, response: str) -> List[ExtractedClaim]:
        """Extract factual claims from a response."""
        
        if self.llm_client:
            # Use LLM for sophisticated claim extraction
            return self._extract_claims_with_llm(response)
        else:
            # Fallback to rule-based extraction
            return self._extract_claims_rule_based(response)
    
    def _extract_claims_with_llm(self, response: str) -> List[ExtractedClaim]:
        """Extract claims using LLM for sophisticated analysis."""
        try:
            prompt = self.claim_extraction_prompt.format(response=response)
            result = self.llm_client.generate(prompt)
            
            # Parse JSON response
            claims_data = json.loads(result)
            claims = []
            
            for claim_data in claims_data:
                claim = ExtractedClaim(
                    text=claim_data["claim"],
                    claim_type=ClaimType(claim_data["type"]),
                    confidence=claim_data["confidence"],
                    start_pos=claim_data["start_pos"],
                    end_pos=claim_data["end_pos"]
                )
                claims.append(claim)
            
            return claims
            
        except Exception as e:
            print(f"LLM claim extraction failed: {e}")
            return self._extract_claims_rule_based(response)
    
    def _extract_claims_rule_based(self, response: str) -> List[ExtractedClaim]:
        """Extract claims using rule-based patterns."""
        claims = []
        
        # Pattern-based claim extraction
        claim_patterns = [
            r'(The system|Our system|This system|The framework|Our framework) (is|has|provides|supports|includes|contains|uses|implements) ([^.]*)',
            r'(We|Our team|The project) (have|has|implemented|created|built|developed) ([^.]*)',
            r'(The baseline|Our baseline|The evaluation|Our evaluation) (score|result|performance) (is|was) ([^.]*)',
            r'(The memory|Our memory|The context|Our context) (system|framework|orchestrator) (can|does|provides|supports) ([^.]*)',
            r'(Users|Developers|Teams) (can|should|must|need to) ([^.]*)',
        ]
        
        for pattern in claim_patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                claim_text = match.group(0)
                claim = ExtractedClaim(
                    text=claim_text,
                    claim_type=ClaimType.FACT,
                    confidence=0.7,  # Medium confidence for rule-based extraction
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                claims.append(claim)
        
        # Remove duplicates and overlapping claims
        claims = self._deduplicate_claims(claims)
        
        return claims
    
    def _deduplicate_claims(self, claims: List[ExtractedClaim]) -> List[ExtractedClaim]:
        """Remove duplicate and overlapping claims."""
        if not claims:
            return claims
        
        # Sort by start position
        claims.sort(key=lambda x: x.start_pos)
        
        deduplicated = [claims[0]]
        
        for claim in claims[1:]:
            # Check if this claim overlaps with the last one
            last_claim = deduplicated[-1]
            if claim.start_pos > last_claim.end_pos:
                deduplicated.append(claim)
            elif claim.confidence > last_claim.confidence:
                # Replace with higher confidence claim
                deduplicated[-1] = claim
        
        return deduplicated
    
    def verify_claim(self, claim: str, context: str) -> Dict[str, Any]:
        """Verify if a claim is supported by the context."""
        
        if self.llm_client:
            # Use LLM for sophisticated verification
            return self._verify_claim_with_llm(claim, context)
        else:
            # Fallback to rule-based verification
            return self._verify_claim_rule_based(claim, context)
    
    def _verify_claim_with_llm(self, claim: str, context: str) -> Dict[str, Any]:
        """Verify claim using LLM for sophisticated analysis."""
        try:
            prompt = self.claim_verification_prompt.format(claim=claim, context=context)
            result = self.llm_client.generate(prompt)
            
            # Parse JSON response
            verification = json.loads(result)
            return verification
            
        except Exception as e:
            print(f"LLM claim verification failed: {e}")
            return self._verify_claim_rule_based(claim, context)
    
    def _verify_claim_rule_based(self, claim: str, context: str) -> Dict[str, Any]:
        """Verify claim using rule-based patterns."""
        
        # Convert to lowercase for comparison
        claim_lower = claim.lower()
        context_lower = context.lower()
        
        # Extract key terms from claim
        claim_terms = self._extract_key_terms(claim_lower)
        
        # Check if key terms appear in context
        matching_terms = [term for term in claim_terms if term in context_lower]
        
        # Calculate verification score
        if len(claim_terms) == 0:
            verification_score = 0.0
        else:
            verification_score = len(matching_terms) / len(claim_terms)
        
        # Determine if verified (threshold-based)
        verified = verification_score >= 0.6
        
        return {
            "verified": verified,
            "confidence": verification_score,
            "reasoning": f"Found {len(matching_terms)}/{len(claim_terms)} key terms in context",
            "supporting_evidence": f"Matched terms: {', '.join(matching_terms)}" if matching_terms else "No supporting evidence found"
        }
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for verification."""
        # Remove common words and punctuation
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms
    
    def evaluate_faithfulness(self, response: str, context: str) -> FaithfulnessResult:
        """Evaluate faithfulness of response against context."""
        
        # Extract claims from response
        claims = self.extract_claims(response)
        
        if not claims:
            return FaithfulnessResult(
                faithfulness_score=1.0,  # No claims to verify = perfect faithfulness
                total_claims=0,
                verified_claims=0,
                unverified_claims=0,
                hallucinated_claims=0,
                claim_details=[],
                overall_assessment="No factual claims found in response"
            )
        
        # Verify each claim
        claim_details = []
        verified_count = 0
        unverified_count = 0
        hallucinated_count = 0
        
        for claim in claims:
            verification = self.verify_claim(claim.text, context)
            
            claim_detail = {
                "claim": claim.text,
                "claim_type": claim.claim_type.value,
                "confidence": claim.confidence,
                "verified": verification["verified"],
                "verification_confidence": verification["confidence"],
                "reasoning": verification["reasoning"],
                "supporting_evidence": verification.get("supporting_evidence", "")
            }
            
            claim_details.append(claim_detail)
            
            if verification["verified"]:
                verified_count += 1
            else:
                unverified_count += 1
                # Consider high-confidence unverified claims as hallucinations
                if claim.confidence > 0.8 and verification["confidence"] < 0.3:
                    hallucinated_count += 1
        
        # Calculate faithfulness score
        if verified_count + unverified_count == 0:
            faithfulness_score = 1.0
        else:
            faithfulness_score = verified_count / (verified_count + unverified_count)
        
        # Determine overall assessment
        if faithfulness_score >= 0.9:
            assessment = "Excellent faithfulness - minimal hallucinations"
        elif faithfulness_score >= 0.7:
            assessment = "Good faithfulness - some unverified claims"
        elif faithfulness_score >= 0.5:
            assessment = "Fair faithfulness - significant unverified claims"
        else:
            assessment = "Poor faithfulness - many hallucinations detected"
        
        return FaithfulnessResult(
            faithfulness_score=faithfulness_score,
            total_claims=len(claims),
            verified_claims=verified_count,
            unverified_claims=unverified_count,
            hallucinated_claims=hallucinated_count,
            claim_details=claim_details,
            overall_assessment=assessment
        )
    
    def generate_faithfulness_report(self, result: FaithfulnessResult) -> str:
        """Generate a human-readable faithfulness report."""
        
        report = f"""
🧠 FAITHFULNESS EVALUATION REPORT
{'='*50}

📊 OVERALL SCORE: {result.faithfulness_score:.2f}/1.00
📋 ASSESSMENT: {result.overall_assessment}

📈 CLAIM BREAKDOWN:
   • Total Claims: {result.total_claims}
   • Verified Claims: {result.verified_claims} ✅
   • Unverified Claims: {result.unverified_claims} ⚠️
   • Hallucinated Claims: {result.hallucinated_claims} ❌

🔍 DETAILED CLAIM ANALYSIS:
"""
        
        for i, claim_detail in enumerate(result.claim_details, 1):
            status = "✅" if claim_detail["verified"] else "❌"
            report += f"""
{i}. {status} Claim: "{claim_detail['claim']}"
   Type: {claim_detail['claim_type']}
   Confidence: {claim_detail['confidence']:.2f}
   Verification: {claim_detail['verification_confidence']:.2f}
   Reasoning: {claim_detail['reasoning']}
"""
        
        return report


def main():
    """Test the faithfulness evaluator."""
    evaluator = FaithfulnessEvaluator()
    
    # Test case
    response = """
    The baseline RAGUS evaluation system provides a fixed scoring framework with 73.3/100 performance.
    Our memory system uses PostgreSQL with pgvector for efficient retrieval. The system includes
    four memory systems: LTST, Cursor, Go CLI, and Prime. Users can access the system through
    the unified memory orchestrator script.
    """
    
    context = """
    The baseline RAGUS evaluation system was implemented with fixed criteria that never change.
    The initial baseline score was established at 73.3/100. The memory system architecture
    includes multiple components: LTST memory system, Cursor memory context, Go CLI integration,
    and Prime system. The unified memory orchestrator provides access to all systems.
    """
    
    result = evaluator.evaluate_faithfulness(response, context)
    report = evaluator.generate_faithfulness_report(result)
    
    print(report)


if __name__ == "__main__":
    main()
