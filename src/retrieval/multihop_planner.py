"""
Phase 2: Multi-Hop & Answer Planning with Data-Driven Gating

Implements plan → retrieve per sub-question → merge → answer pipeline with:
- Coverage: fraction of sub-claims with ≥1 high-score window supporting it
- Concentration: low dispersion of top scores (evidence not scattered/noisy)
- Novelty: 2nd-hop only if sub-queries aren't near-duplicates of hop-1
- Ceiling: hard cap of 2 hops + token budget (+512 input tokens max)
- Mid-gen callbacks: trigger only for unresolved sub-spans
"""

from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass, field
from typing import Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


@dataclass
class SubQuestion:
    """A sub-question generated during query decomposition."""

    text: str
    parent_claim: str | None = None
    hop_level: int = 1
    resolved: bool = False
    evidence_score: float = 0.0
    retrieved_spans: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class PlanningState:
    """Current state of multi-hop planning."""

    original_query: str
    sub_questions: list[SubQuestion] = field(default_factory=list)
    current_hop: int = 1
    token_budget_used: int = 0
    resolved_claims: set[str] = field(default_factory=set)
    evidence_scores: list[float] = field(default_factory=list)
    should_continue: bool = True
    stop_reason: str | None = None


@dataclass
class CoverageMetrics:
    """Coverage and concentration metrics for gating."""

    coverage: float  # Fraction of sub-claims with supporting evidence
    concentration: float  # Evidence concentration (1.0 - dispersion)
    novelty: float  # How novel are new sub-queries vs existing
    token_budget_remaining: int  # Remaining token budget

    # Detailed breakdowns
    total_claims: int = 0
    supported_claims: int = 0
    evidence_dispersion: float = 0.0
    duplicate_similarity: float = 0.0


class MultiHopPlanner:
    """Data-driven multi-hop planning with coverage/concentration/novelty gating."""

    def __init__(
        self,
        max_hops: int = 2,
        token_budget: int = 512,
        coverage_threshold: float = 0.7,  # τ₁ for sub-claims support
        concentration_threshold: float = 0.6,  # Low dispersion threshold
        novelty_threshold: float = 0.8,  # Cosine similarity threshold for duplicates
        min_evidence_score: float = 0.3,  # Minimum reranker score
    ):
        self.max_hops = max_hops
        self.token_budget = token_budget
        self.coverage_threshold = coverage_threshold
        self.concentration_threshold = concentration_threshold
        self.novelty_threshold = novelty_threshold
        self.min_evidence_score = min_evidence_score

        # Initialize TF-IDF for novelty checks
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(max_features=200, stop_words="english", ngram_range=(1, 2))
        else:
            self.vectorizer = None

    async def plan_multihop_retrieval(
        self, query: str, retrieval_fn, sub_claims: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Execute multi-hop planning with data-driven gating.

        Args:
            query: Original user query
            retrieval_fn: Function that takes query and returns ranked documents
            sub_claims: Optional list of sub-claims to track coverage

        Returns:
            Dict with final answer, evidence, metrics, and planning trace
        """
        # Initialize planning state
        state = PlanningState(
            original_query=query,
            token_budget_used=int(len(query.split()) * 1.3),  # Rough token estimate
        )

        # Decompose initial query into sub-questions
        initial_subqs = self._decompose_query(query, sub_claims)
        state.sub_questions.extend(initial_subqs)

        hop_results = []

        # Execute planning loop with gating
        while state.should_continue and state.current_hop <= self.max_hops:
            hop_start = time.time()

            # Retrieve for unresolved sub-questions
            hop_evidence = await self._retrieve_for_hop(state, retrieval_fn)

            # Compute coverage/concentration/novelty metrics
            metrics = self._compute_gating_metrics(state, sub_claims)

            # Data-driven gating decision
            continue_decision = self._should_continue_multihop(state, metrics)

            hop_result = {
                "hop": state.current_hop,
                "sub_questions": len([sq for sq in state.sub_questions if sq.hop_level == state.current_hop]),
                "evidence_retrieved": len(hop_evidence),
                "metrics": metrics,
                "continue_decision": continue_decision,
                "latency_ms": (time.time() - hop_start) * 1000,
            }
            hop_results.append(hop_result)

            # Update state
            state.current_hop += 1
            state.should_continue = continue_decision["should_continue"]
            state.stop_reason = continue_decision["reason"]

            # Generate follow-up sub-questions if continuing
            if state.should_continue and state.current_hop <= self.max_hops:
                followup_subqs = self._generate_followup_questions(state, hop_evidence, metrics)
                state.sub_questions.extend(followup_subqs)

        # Synthesize final answer
        final_answer = self._synthesize_multihop_answer(state)

        return {
            "answer": final_answer["text"],
            "confidence": final_answer["confidence"],
            "evidence": self._collect_all_evidence(state),
            "planning_trace": {
                "hops_executed": state.current_hop - 1,
                "stop_reason": state.stop_reason,
                "hop_results": hop_results,
                "final_metrics": self._compute_gating_metrics(state, sub_claims),
            },
            "sub_questions": [sq.text for sq in state.sub_questions],
            "token_budget_used": state.token_budget_used,
        }

    def _decompose_query(self, query: str, sub_claims: list[str] | None = None) -> list[SubQuestion]:
        """Decompose query into initial sub-questions."""
        subquestions = []

        # Simple decomposition based on conjunctions and question complexity
        if " and " in query.lower() or " or " in query.lower():
            # Split on conjunctions
            parts = re.split(r"\s+(and|or)\s+", query.lower(), flags=re.IGNORECASE)
            for i, part in enumerate(parts):
                if part.lower() not in ["and", "or"]:
                    subq = SubQuestion(
                        text=part.strip(),
                        hop_level=1,
                        parent_claim=sub_claims[i] if sub_claims and i < len(sub_claims) else None,
                    )
                    subquestions.append(subq)
        else:
            # Single question
            subq = SubQuestion(text=query, hop_level=1, parent_claim=sub_claims[0] if sub_claims else None)
            subquestions.append(subq)

        return subquestions

    async def _retrieve_for_hop(self, state: PlanningState, retrieval_fn) -> list[dict[str, Any]]:
        """Retrieve evidence for current hop's sub-questions."""
        hop_evidence = []

        current_hop_questions = [
            sq for sq in state.sub_questions if sq.hop_level == state.current_hop and not sq.resolved
        ]

        for subq in current_hop_questions:
            try:
                # Retrieve evidence for this sub-question
                retrieved = await retrieval_fn(subq.text)

                # Filter by minimum evidence score
                high_score_spans = [span for span in retrieved if span.get("score", 0.0) >= self.min_evidence_score]

                # Update sub-question with evidence
                subq.retrieved_spans = high_score_spans
                subq.evidence_score = max([s.get("score", 0.0) for s in high_score_spans], default=0.0)

                # Mark as resolved if we have good evidence
                if high_score_spans:
                    subq.resolved = True
                    if subq.parent_claim:
                        state.resolved_claims.add(subq.parent_claim)

                hop_evidence.extend(high_score_spans)
                state.evidence_scores.extend([s.get("score", 0.0) for s in high_score_spans])

                # Update token budget
                for span in high_score_spans:
                    tokens = int(len(span.get("text", "").split()) * 1.3)
                    state.token_budget_used += tokens

            except Exception as e:
                print(f"Retrieval failed for sub-question '{subq.text}': {e}")
                continue

        return hop_evidence

    def _compute_gating_metrics(self, state: PlanningState, sub_claims: list[str] | None = None) -> CoverageMetrics:
        """Compute coverage, concentration, and novelty metrics for gating."""

        # Coverage: fraction of sub-claims with ≥1 high-score window
        total_claims = len(sub_claims) if sub_claims else len(state.sub_questions)
        supported_claims = (
            len(state.resolved_claims) if sub_claims else sum(1 for sq in state.sub_questions if sq.resolved)
        )
        coverage = supported_claims / total_claims if total_claims > 0 else 1.0

        # Concentration: 1.0 - dispersion of evidence scores
        if len(state.evidence_scores) > 1:
            mean_score = sum(state.evidence_scores) / len(state.evidence_scores)
            variance = sum((s - mean_score) ** 2 for s in state.evidence_scores) / len(state.evidence_scores)
            dispersion = math.sqrt(variance) / mean_score if mean_score > 0 else 1.0
            concentration = max(0.0, 1.0 - dispersion)
        else:
            concentration = 1.0 if state.evidence_scores else 0.0

        # Novelty: compute similarity of current hop vs previous hops
        novelty = self._compute_novelty_score(state)

        return CoverageMetrics(
            coverage=coverage,
            concentration=concentration,
            novelty=novelty,
            token_budget_remaining=max(0, self.token_budget - state.token_budget_used),
            total_claims=total_claims,
            supported_claims=supported_claims,
            evidence_dispersion=1.0 - concentration,
            duplicate_similarity=1.0 - novelty,
        )

    def _compute_novelty_score(self, state: PlanningState) -> float:
        """Compute novelty score for current hop questions vs previous hops."""

        if state.current_hop <= 1:
            return 1.0  # First hop is always novel

        # Get current and previous hop questions
        current_questions = [sq.text for sq in state.sub_questions if sq.hop_level == state.current_hop]
        previous_questions = [sq.text for sq in state.sub_questions if sq.hop_level < state.current_hop]

        if not current_questions or not previous_questions:
            return 1.0

        if not HAS_SKLEARN or not self.vectorizer:
            # Fallback: simple token overlap
            return self._compute_token_novelty(current_questions, previous_questions)

        try:
            # Use TF-IDF + cosine similarity for novelty
            all_questions = previous_questions + current_questions
            tfidf_matrix = self.vectorizer.fit_transform(all_questions)

            prev_vectors = tfidf_matrix[: len(previous_questions)]
            curr_vectors = tfidf_matrix[len(previous_questions) :]

            # Compute max similarity between any current and previous question
            similarities = cosine_similarity(curr_vectors, prev_vectors)
            max_similarity = similarities.max()

            # Novelty = 1 - max_similarity
            return max(0.0, 1.0 - max_similarity)

        except Exception:
            # Fallback to token-based novelty
            return self._compute_token_novelty(current_questions, previous_questions)

    def _compute_token_novelty(self, current: list[str], previous: list[str]) -> float:
        """Fallback token-based novelty computation."""
        max_overlap = 0.0

        for curr_q in current:
            curr_tokens = set(curr_q.lower().split())
            if not curr_tokens:
                continue

            for prev_q in previous:
                prev_tokens = set(prev_q.lower().split())
                if not prev_tokens:
                    continue

                overlap = len(curr_tokens & prev_tokens) / len(curr_tokens | prev_tokens)
                max_overlap = max(max_overlap, overlap)

        return max(0.0, 1.0 - max_overlap)

    def _should_continue_multihop(self, state: PlanningState, metrics: CoverageMetrics) -> dict[str, Any]:
        """Data-driven gating decision for whether to continue multi-hop."""

        reasons = []
        should_continue = True

        # Hard constraints
        if state.current_hop >= self.max_hops:
            should_continue = False
            reasons.append(f"Hit max hops limit ({self.max_hops})")

        if metrics.token_budget_remaining <= 50:  # Reserve some tokens
            should_continue = False
            reasons.append(f"Token budget exhausted ({state.token_budget_used}/{self.token_budget})")

        # Data-driven gating
        if metrics.coverage >= self.coverage_threshold:
            if metrics.concentration >= self.concentration_threshold:
                should_continue = False
                reasons.append(f"High coverage ({metrics.coverage:.3f}) + concentration ({metrics.concentration:.3f})")

        if metrics.novelty < (1.0 - self.novelty_threshold):
            should_continue = False
            reasons.append(f"Low novelty ({metrics.novelty:.3f}) - near duplicate sub-queries")

        # Override: continue if very low coverage despite other factors
        if metrics.coverage < 0.3 and state.current_hop < self.max_hops:
            should_continue = True
            reasons = [f"Override: Very low coverage ({metrics.coverage:.3f}), continue searching"]

        return {
            "should_continue": should_continue,
            "reason": "; ".join(reasons) if reasons else "No stopping criteria met",
            "gating_scores": {
                "coverage": metrics.coverage,
                "concentration": metrics.concentration,
                "novelty": metrics.novelty,
                "token_budget": metrics.token_budget_remaining,
            },
        }

    def _generate_followup_questions(
        self, state: PlanningState, hop_evidence: list[dict[str, Any]], metrics: CoverageMetrics
    ) -> list[SubQuestion]:
        """Generate follow-up sub-questions based on unresolved spans."""

        followup_questions = []

        # Only generate follow-ups if we have low coverage
        if metrics.coverage >= self.coverage_threshold:
            return followup_questions

        # Identify unresolved claims/topics
        unresolved_subqs = [sq for sq in state.sub_questions if not sq.resolved]

        for subq in unresolved_subqs[:2]:  # Limit follow-ups
            # Generate clarification question
            if subq.evidence_score < self.min_evidence_score:
                followup_text = f"What specific information about {subq.text.lower().replace('?', '')}?"

                followup = SubQuestion(
                    text=followup_text, parent_claim=subq.parent_claim, hop_level=state.current_hop + 1
                )
                followup_questions.append(followup)

        return followup_questions

    def _synthesize_multihop_answer(self, state: PlanningState) -> dict[str, Any]:
        """Synthesize final answer from multi-hop evidence."""

        # Collect all evidence from resolved sub-questions
        all_evidence = []
        for subq in state.sub_questions:
            if subq.resolved:
                all_evidence.extend(subq.retrieved_spans)

        # Sort by evidence score
        all_evidence.sort(key=lambda x: x.get("score", 0.0), reverse=True)

        # Take top evidence spans
        top_evidence = all_evidence[:5]

        # Simple synthesis (would use LLM in production)
        evidence_texts = [span.get("text", "") for span in top_evidence]
        answer_text = f"Based on multi-hop analysis: {' '.join(evidence_texts[:200])}..."

        # Compute confidence based on coverage and concentration
        final_metrics = self._compute_gating_metrics(state)
        confidence = (final_metrics.coverage + final_metrics.concentration) / 2.0

        return {
            "text": answer_text,
            "confidence": confidence,
            "evidence_count": len(top_evidence),
            "hops_used": state.current_hop - 1,
        }

    def _collect_all_evidence(self, state: PlanningState) -> list[dict[str, Any]]:
        """Collect all evidence from multi-hop retrieval."""
        all_evidence = []

        for subq in state.sub_questions:
            for span in subq.retrieved_spans:
                evidence_item = {
                    **span,
                    "sub_question": subq.text,
                    "hop_level": subq.hop_level,
                    "resolved": subq.resolved,
                }
                all_evidence.append(evidence_item)

        # Sort by score descending
        all_evidence.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return all_evidence


def create_multihop_planner(config: dict[str, Any] | None = None) -> MultiHopPlanner:
    """Factory function to create a MultiHopPlanner from config."""

    if not config:
        return MultiHopPlanner()

    return MultiHopPlanner(
        max_hops=config.get("max_hops", 2),
        token_budget=config.get("token_budget", 512),
        coverage_threshold=config.get("coverage_threshold", 0.7),
        concentration_threshold=config.get("concentration_threshold", 0.6),
        novelty_threshold=config.get("novelty_threshold", 0.8),
        min_evidence_score=config.get("min_evidence_score", 0.3),
    )
