"""
Phase 2: Multi-Hop RAG Integration

Integrates the data-driven multi-hop planner with the existing RAG system,
adding mid-generation callbacks and evidence synthesis.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

# Import our Phase 2 components
try:
    from retrieval.multihop_planner import MultiHopPlanner, create_multihop_planner
    from telemetry.request_logger import log_rag_request
except ImportError:
    # Handle relative imports for different contexts
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from retrieval.multihop_planner import MultiHopPlanner, create_multihop_planner
    from telemetry.request_logger import log_rag_request


class Phase2RAGSystem:
    """Enhanced RAG system with Phase 2 multi-hop planning and data-driven gating."""

    def __init__(
        self,
        base_retriever,
        multihop_config: Optional[Dict[str, Any]] = None,
        enable_midgen_callbacks: bool = True,
        enable_telemetry: bool = True
    ):
        self.base_retriever = base_retriever
        self.enable_midgen_callbacks = enable_midgen_callbacks
        self.enable_telemetry = enable_telemetry

        # Initialize multi-hop planner
        self.multihop_planner = create_multihop_planner(multihop_config)

        # Mid-generation callback threshold
        self.midgen_uncertainty_threshold = 0.4

    async def query_with_multihop(
        self,
        query: str,
        sub_claims: Optional[List[str]] = None,
        enable_multihop: bool = True,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute query with optional multi-hop planning.
        
        Args:
            query: User query
            sub_claims: Optional sub-claims for coverage tracking
            enable_multihop: Whether to use multi-hop planning
            request_id: Optional request ID for telemetry correlation
            
        Returns:
            Enhanced answer with multi-hop evidence and planning trace
        """
        start_time = time.time()
        stage_timings = {}

        try:
            # Stage 1: Query analysis and complexity assessment
            stage_start = time.time()
            complexity = self._assess_query_complexity(query)
            should_use_multihop = enable_multihop and complexity['use_multihop']
            stage_timings['complexity_analysis'] = (time.time() - stage_start) * 1000

            if should_use_multihop:
                # Stage 2: Multi-hop planning and retrieval
                stage_start = time.time()
                multihop_result = await self._execute_multihop_planning(
                    query, sub_claims, request_id
                )
                stage_timings['multihop_planning'] = (time.time() - stage_start) * 1000

                # Stage 3: Evidence synthesis and answer generation
                stage_start = time.time()
                final_answer = await self._synthesize_multihop_answer(
                    query, multihop_result, request_id
                )
                stage_timings['answer_synthesis'] = (time.time() - stage_start) * 1000

                result = {
                    **final_answer,
                    'multihop_used': True,
                    'planning_trace': multihop_result['planning_trace'],
                    'complexity_analysis': complexity
                }

            else:
                # Stage 2: Single-hop retrieval (fallback)
                stage_start = time.time()
                single_hop_result = await self._execute_single_hop(query, request_id)
                stage_timings['single_hop_retrieval'] = (time.time() - stage_start) * 1000

                result = {
                    **single_hop_result,
                    'multihop_used': False,
                    'complexity_analysis': complexity
                }

            # Add timing information
            result['stage_timings'] = stage_timings
            result['total_latency_ms'] = (time.time() - start_time) * 1000

            # Stage 4: Telemetry logging
            if self.enable_telemetry:
                await self._log_phase2_request(query, result, request_id)

            return result

        except Exception as e:
            error_result = {
                'answer': f'Error in Phase 2 processing: {str(e)}',
                'confidence': 0.0,
                'error': str(e),
                'multihop_used': False,
                'stage_timings': stage_timings,
                'total_latency_ms': (time.time() - start_time) * 1000
            }

            if self.enable_telemetry:
                await self._log_phase2_request(query, error_result, request_id)

            return error_result

    def _assess_query_complexity(self, query: str) -> Dict[str, Any]:
        """Assess whether query needs multi-hop planning."""

        word_count = len(query.split())
        has_conjunctions = any(conj in query.lower() for conj in ['and', 'or', 'but', 'however'])
        has_comparisons = any(comp in query.lower() for comp in ['compare', 'difference', 'versus', 'vs', 'traditional'])
        has_multi_part = query.count('?') > 1 or query.count('.') > 2
        has_causal = any(causal in query.lower() for causal in ['why', 'how', 'because', 'cause', 'effect'])

        # Multi-hop indicators
        multihop_indicators = [
            word_count > 10,                # Complex queries (lowered threshold)
            has_conjunctions,               # Multiple parts
            has_comparisons,                # Requires multiple perspectives
            has_multi_part,                 # Multiple questions
            has_causal                      # Causal reasoning
        ]

        complexity_score = sum(multihop_indicators)
        use_multihop = complexity_score >= 1  # Lowered threshold for multi-hop

        return {
            'word_count': word_count,
            'has_conjunctions': has_conjunctions,
            'has_comparisons': has_comparisons,
            'has_multi_part': has_multi_part,
            'has_causal': has_causal,
            'complexity_score': complexity_score,
            'use_multihop': use_multihop,
            'reasoning': f"Complexity score {complexity_score}/5, multihop threshold: 2"
        }

    async def _execute_multihop_planning(
        self,
        query: str,
        sub_claims: Optional[List[str]],
        request_id: Optional[str]
    ) -> Dict[str, Any]:
        """Execute multi-hop planning with data-driven gating."""

        # Create retrieval function that interfaces with base retriever
        async def retrieval_fn(subquery: str) -> List[Dict[str, Any]]:
            try:
                # Use base retriever (could be Phase 1 hybrid retriever)
                if hasattr(self.base_retriever, 'retrieve'):
                    results = self.base_retriever.retrieve(subquery)
                else:
                    # Fallback for different retriever interfaces
                    results = await self.base_retriever(subquery)

                # Normalize results format
                if isinstance(results, dict) and 'results' in results:
                    results = results['results']

                return results[:10]  # Limit results per sub-query

            except Exception as e:
                print(f"Retrieval failed for subquery '{subquery}': {e}")
                return []

        # Execute multi-hop planning
        multihop_result = await self.multihop_planner.plan_multihop_retrieval(
            query=query,
            retrieval_fn=retrieval_fn,
            sub_claims=sub_claims
        )

        return multihop_result

    async def _synthesize_multihop_answer(
        self,
        query: str,
        multihop_result: Dict[str, Any],
        request_id: Optional[str]
    ) -> Dict[str, Any]:
        """Synthesize final answer from multi-hop evidence with mid-gen callbacks."""

        evidence = multihop_result.get('evidence', [])
        base_answer = multihop_result.get('answer', '')
        base_confidence = multihop_result.get('confidence', 0.0)

        # Mid-generation callback for uncertainty
        if (self.enable_midgen_callbacks and
            base_confidence < self.midgen_uncertainty_threshold and
            len(evidence) > 0):

            enhanced_answer = await self._midgen_callback_enhancement(
                query, base_answer, evidence, request_id
            )

            return {
                'answer': enhanced_answer['text'],
                'confidence': enhanced_answer['confidence'],
                'evidence': evidence,
                'citations': self._extract_citations(evidence),
                'midgen_enhancement': True,
                'enhancement_reason': f"Low confidence ({base_confidence:.3f}) triggered callback"
            }

        return {
            'answer': base_answer,
            'confidence': base_confidence,
            'evidence': evidence,
            'citations': self._extract_citations(evidence),
            'midgen_enhancement': False
        }

    async def _midgen_callback_enhancement(
        self,
        query: str,
        base_answer: str,
        evidence: List[Dict[str, Any]],
        request_id: Optional[str]
    ) -> Dict[str, Any]:
        """Mid-generation callback to enhance uncertain answers."""

        # Identify unresolved spans in base answer
        unresolved_spans = self._identify_unresolved_spans(base_answer, evidence)

        if not unresolved_spans:
            return {'text': base_answer, 'confidence': 0.5}

        # Generate targeted follow-up queries for unresolved spans
        followup_queries = []
        for span in unresolved_spans:
            followup = f"What specific information about {span} in relation to {query}?"
            followup_queries.append(followup)

        # Retrieve additional evidence for follow-ups
        additional_evidence = []
        for followup in followup_queries[:2]:  # Limit follow-ups
            try:
                if hasattr(self.base_retriever, 'retrieve'):
                    results = self.base_retriever.retrieve(followup)
                else:
                    results = await self.base_retriever(followup)

                if isinstance(results, dict) and 'results' in results:
                    results = results['results']

                additional_evidence.extend(results[:3])  # Top 3 per followup

            except Exception as e:
                print(f"Follow-up retrieval failed: {e}")
                continue

        # Enhanced synthesis with additional evidence
        enhanced_text = self._enhance_answer_with_evidence(
            base_answer, additional_evidence, unresolved_spans
        )

        # Improved confidence with additional evidence
        enhanced_confidence = min(0.9, base_answer and len(additional_evidence) > 0 and 0.7 or 0.4)

        return {
            'text': enhanced_text,
            'confidence': enhanced_confidence,
            'followup_queries': followup_queries,
            'additional_evidence_count': len(additional_evidence)
        }

    def _identify_unresolved_spans(
        self,
        answer: str,
        evidence: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify spans in answer that lack supporting evidence."""

        # Simple implementation: look for unsupported claims
        answer_words = set(answer.lower().split())
        evidence_words = set()

        for item in evidence:
            text = item.get('text', '')
            evidence_words.update(text.lower().split())

        # Find words in answer but not in evidence (simplified)
        unsupported = answer_words - evidence_words

        # Filter to content words (not stopwords)
        content_words = [
            word for word in unsupported
            if len(word) > 3 and word.isalpha()
        ]

        return content_words[:5]  # Top 5 unresolved spans

    def _enhance_answer_with_evidence(
        self,
        base_answer: str,
        additional_evidence: List[Dict[str, Any]],
        unresolved_spans: List[str]
    ) -> str:
        """Enhance answer with additional evidence for unresolved spans."""

        if not additional_evidence:
            return base_answer

        # Simple enhancement: append relevant evidence snippets
        enhancements = []
        for item in additional_evidence[:2]:
            text = item.get('text', '')
            if any(span.lower() in text.lower() for span in unresolved_spans):
                snippet = text[:100] + '...' if len(text) > 100 else text
                enhancements.append(snippet)

        if enhancements:
            enhanced = base_answer + f" Additional context: {' '.join(enhancements)}"
            return enhanced

        return base_answer

    async def _execute_single_hop(
        self,
        query: str,
        request_id: Optional[str]
    ) -> Dict[str, Any]:
        """Execute single-hop retrieval as fallback."""

        try:
            if hasattr(self.base_retriever, 'retrieve'):
                results = self.base_retriever.retrieve(query)
            else:
                results = await self.base_retriever(query)

            if isinstance(results, dict) and 'results' in results:
                evidence = results['results'][:8]
            else:
                evidence = results[:8] if results else []

            # Simple answer generation (would use LLM in production)
            if evidence:
                answer_text = f"Based on retrieved evidence: {evidence[0].get('text', '')[:200]}..."
                confidence = min(0.8, len(evidence) * 0.1)
            else:
                answer_text = "No relevant information found."
                confidence = 0.0

            return {
                'answer': answer_text,
                'confidence': confidence,
                'evidence': evidence,
                'citations': self._extract_citations(evidence)
            }

        except Exception as e:
            return {
                'answer': f"Single-hop retrieval failed: {str(e)}",
                'confidence': 0.0,
                'evidence': [],
                'citations': []
            }

    def _extract_citations(self, evidence: List[Dict[str, Any]]) -> List[str]:
        """Extract citations from evidence."""
        citations = []
        for item in evidence:
            source = item.get('source') or item.get('document_id') or 'Unknown'
            citations.append(source)
        return list(set(citations))  # Deduplicate

    async def _log_phase2_request(
        self,
        query: str,
        result: Dict[str, Any],
        request_id: Optional[str]
    ) -> None:
        """Log Phase 2 request for telemetry."""

        try:
            await log_rag_request(
                query=query,
                answer=result.get('answer', ''),
                request_id=request_id,
                confidence=result.get('confidence'),
                stage_timings=result.get('stage_timings', {}),
                multihop_used=result.get('multihop_used', False),
                evidence_count=len(result.get('evidence', [])),
                planning_trace=result.get('planning_trace'),
                total_latency_ms=result.get('total_latency_ms')
            )
        except Exception as e:
            print(f"Telemetry logging failed: {e}")


def create_phase2_rag_system(
    base_retriever,
    config: Optional[Dict[str, Any]] = None
) -> Phase2RAGSystem:
    """Factory function to create Phase 2 RAG system."""

    if not config:
        config = {}

    multihop_config = config.get('multihop', {})

    return Phase2RAGSystem(
        base_retriever=base_retriever,
        multihop_config=multihop_config,
        enable_midgen_callbacks=config.get('enable_midgen_callbacks', True),
        enable_telemetry=config.get('enable_telemetry', True)
    )
