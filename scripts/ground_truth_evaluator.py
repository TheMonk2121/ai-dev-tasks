#!/usr/bin/env python3
"""
Ground Truth Evaluator for RAG Systems

This module implements ground truth evaluation following RAGAS standards to measure
context recall and answer completeness against annotated ground truth.

RAGAS Context Recall: Measures the recall of the retrieved context using the
annotated answer as ground truth. An annotated answer is taken as proxy for
ground truth context.

RAGAS Answer Completeness: Measures to what extent the response is complete
(not missing critical information) with respect to the ground truth.
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class EvaluationType(Enum):
    """Types of ground truth evaluation."""

    CONTEXT_RECALL = "context_recall"
    ANSWER_COMPLETENESS = "answer_completeness"
    BOTH = "both"


@dataclass
class GroundTruthItem:
    """Represents a ground truth item for evaluation."""

    query: str
    expected_answer: str
    key_facts: List[str]
    critical_information: List[str]
    context_requirements: List[str]


@dataclass
class GroundTruthResult:
    """Result of ground truth evaluation."""

    context_recall_score: float  # 0-1 scale
    answer_completeness_score: float  # 0-1 scale
    overall_score: float  # 0-1 scale
    context_recall_details: Dict[str, Any]
    completeness_details: Dict[str, Any]
    overall_assessment: str


class GroundTruthEvaluator:
    """Evaluates responses against ground truth for context recall and completeness."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.context_recall_prompt = self._create_context_recall_prompt()
        self.completeness_prompt = self._create_completeness_prompt()

    def _create_context_recall_prompt(self) -> str:
        """Create prompt for context recall evaluation."""
        return """
        Evaluate how much of the ground truth information is captured in the retrieved context.

        Ground Truth Answer: {ground_truth}
        Retrieved Context: {retrieved_context}

        Instructions:
        1. Identify key facts and information from the ground truth answer
        2. Check if each key fact appears in the retrieved context
        3. Calculate the percentage of ground truth information that is present in context
        4. Consider both exact matches and semantic similarity

        Respond with JSON:
        {{
            "recall_score": 0.0-1.0,
            "covered_facts": ["fact1", "fact2"],
            "missing_facts": ["fact3", "fact4"],
            "reasoning": "explanation of recall calculation"
        }}
        """

    def _create_completeness_prompt(self) -> str:
        """Create prompt for answer completeness evaluation."""
        return """
        Evaluate how complete the response is compared to the ground truth answer.

        Ground Truth Answer: {ground_truth}
        Actual Response: {actual_response}

        Instructions:
        1. Identify critical information from the ground truth answer
        2. Check if each critical piece of information is present in the response
        3. Calculate the percentage of critical information that is covered
        4. Consider both explicit mentions and implicit coverage

        Respond with JSON:
        {{
            "completeness_score": 0.0-1.0,
            "covered_info": ["info1", "info2"],
            "missing_info": ["info3", "info4"],
            "reasoning": "explanation of completeness calculation"
        }}
        """

    def evaluate_context_recall(self, ground_truth: str, retrieved_context: str) -> Dict[str, Any]:
        """Evaluate context recall using ground truth as reference."""

        if self.llm_client:
            # Use LLM for sophisticated recall evaluation
            return self._evaluate_context_recall_with_llm(ground_truth, retrieved_context)
        else:
            # Fallback to rule-based evaluation
            return self._evaluate_context_recall_rule_based(ground_truth, retrieved_context)

    def _evaluate_context_recall_with_llm(self, ground_truth: str, retrieved_context: str) -> Dict[str, Any]:
        """Evaluate context recall using LLM for sophisticated analysis."""
        try:
            prompt = self.context_recall_prompt.format(ground_truth=ground_truth, retrieved_context=retrieved_context)
            result = self.llm_client.generate(prompt)

            # Parse JSON response
            recall_data = json.loads(result)
            return recall_data

        except Exception as e:
            print(f"LLM context recall evaluation failed: {e}")
            return self._evaluate_context_recall_rule_based(ground_truth, retrieved_context)

    def _evaluate_context_recall_rule_based(self, ground_truth: str, retrieved_context: str) -> Dict[str, Any]:
        """Evaluate context recall using rule-based patterns."""

        # Extract key facts from ground truth
        ground_truth_facts = self._extract_key_facts(ground_truth)

        if not ground_truth_facts:
            return {
                "recall_score": 1.0,  # No facts to check = perfect recall
                "covered_facts": [],
                "missing_facts": [],
                "reasoning": "No key facts found in ground truth",
            }

        # Check which facts are present in retrieved context
        covered_facts = []
        missing_facts = []

        for fact in ground_truth_facts:
            if self._fact_in_context(fact, retrieved_context):
                covered_facts.append(fact)
            else:
                missing_facts.append(fact)

        # Calculate recall score
        recall_score = len(covered_facts) / len(ground_truth_facts)

        return {
            "recall_score": recall_score,
            "covered_facts": covered_facts,
            "missing_facts": missing_facts,
            "reasoning": f"Found {len(covered_facts)}/{len(ground_truth_facts)} key facts in context",
        }

    def evaluate_answer_completeness(self, ground_truth: str, actual_response: str) -> Dict[str, Any]:
        """Evaluate answer completeness against ground truth."""

        if self.llm_client:
            # Use LLM for sophisticated completeness evaluation
            return self._evaluate_completeness_with_llm(ground_truth, actual_response)
        else:
            # Fallback to rule-based evaluation
            return self._evaluate_completeness_rule_based(ground_truth, actual_response)

    def _evaluate_completeness_with_llm(self, ground_truth: str, actual_response: str) -> Dict[str, Any]:
        """Evaluate completeness using LLM for sophisticated analysis."""
        try:
            prompt = self.completeness_prompt.format(ground_truth=ground_truth, actual_response=actual_response)
            result = self.llm_client.generate(prompt)

            # Parse JSON response
            completeness_data = json.loads(result)
            return completeness_data

        except Exception as e:
            print(f"LLM completeness evaluation failed: {e}")
            return self._evaluate_completeness_rule_based(ground_truth, actual_response)

    def _evaluate_completeness_rule_based(self, ground_truth: str, actual_response: str) -> Dict[str, Any]:
        """Evaluate completeness using rule-based patterns."""

        # Extract critical information from ground truth
        critical_info = self._extract_critical_information(ground_truth)

        if not critical_info:
            return {
                "completeness_score": 1.0,  # No critical info to check = perfect completeness
                "covered_info": [],
                "missing_info": [],
                "reasoning": "No critical information found in ground truth",
            }

        # Check which critical information is present in response
        covered_info = []
        missing_info = []

        for info in critical_info:
            if self._info_in_response(info, actual_response):
                covered_info.append(info)
            else:
                missing_info.append(info)

        # Calculate completeness score
        completeness_score = len(covered_info) / len(critical_info)

        return {
            "completeness_score": completeness_score,
            "covered_info": covered_info,
            "missing_info": missing_info,
            "reasoning": f"Covered {len(covered_info)}/{len(critical_info)} critical information points",
        }

    def _extract_key_facts(self, text: str) -> List[str]:
        """Extract key facts from text for context recall evaluation."""
        facts = []

        # Pattern-based fact extraction
        fact_patterns = [
            r"(The system|Our system|This system|The framework|Our framework) (is|has|provides|supports|includes|contains|uses|implements) ([^.]*)",
            r"(We|Our team|The project) (have|has|implemented|created|built|developed) ([^.]*)",
            r"(The baseline|Our baseline|The evaluation|Our evaluation) (score|result|performance) (is|was) ([^.]*)",
            r"(The memory|Our memory|The context|Our context) (system|framework|orchestrator) (can|does|provides|supports) ([^.]*)",
            r"(Users|Developers|Teams) (can|should|must|need to) ([^.]*)",
            r"(The workflow|Our workflow|The process|Our process) (involves|includes|consists of|requires) ([^.]*)",
            r"(The file|Our file|The script|Our script) (contains|includes|provides|implements) ([^.]*)",
        ]

        for pattern in fact_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                fact = match.group(0).strip()
                if fact not in facts:
                    facts.append(fact)

        return facts

    def _extract_critical_information(self, text: str) -> List[str]:
        """Extract critical information from text for completeness evaluation."""
        critical_info = []

        # Extract key terms and concepts
        key_terms = self._extract_key_terms(text)

        # Look for specific information patterns
        info_patterns = [
            r"(score|result|performance|baseline) (of|is|was) ([^.]*)",
            r"(system|framework|tool|script) (called|named|is) ([^.]*)",
            r"(file|document|guide) (located|found|in) ([^.]*)",
            r"(command|script|tool) (to|for) ([^.]*)",
            r"(process|workflow|steps) (are|include|involve) ([^.]*)",
        ]

        for pattern in info_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                info = match.group(0).strip()
                if info not in critical_info:
                    critical_info.append(info)

        # Add key terms as critical information
        for term in key_terms:
            if len(term) > 3 and term not in critical_info:
                critical_info.append(term)

        return critical_info

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        # Remove common words and punctuation
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
        }

        # Extract words
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter out stop words and short words
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]

        return key_terms

    def _fact_in_context(self, fact: str, context: str) -> bool:
        """Check if a fact is present in the context."""
        fact_lower = fact.lower()
        context_lower = context.lower()

        # Extract key terms from fact
        fact_terms = self._extract_key_terms(fact_lower)

        if not fact_terms:
            return False

        # Check if key terms appear in context
        matching_terms = [term for term in fact_terms if term in context_lower]

        # Consider fact present if majority of key terms are found
        return len(matching_terms) / len(fact_terms) >= 0.6

    def _info_in_response(self, info: str, response: str) -> bool:
        """Check if critical information is present in response."""
        info_lower = info.lower()
        response_lower = response.lower()

        # Extract key terms from info
        info_terms = self._extract_key_terms(info_lower)

        if not info_terms:
            return False

        # Check if key terms appear in response
        matching_terms = [term for term in info_terms if term in response_lower]

        # Consider info present if majority of key terms are found
        return len(matching_terms) / len(info_terms) >= 0.6

    def evaluate_ground_truth(
        self,
        ground_truth_item: GroundTruthItem,
        retrieved_context: str,
        actual_response: str,
        evaluation_type: EvaluationType = EvaluationType.BOTH,
    ) -> GroundTruthResult:
        """Evaluate response against ground truth for context recall and completeness."""

        context_recall_details = {}
        completeness_details = {}

        # Evaluate context recall
        if evaluation_type in [EvaluationType.CONTEXT_RECALL, EvaluationType.BOTH]:
            context_recall_details = self.evaluate_context_recall(ground_truth_item.expected_answer, retrieved_context)
            context_recall_score = context_recall_details["recall_score"]
        else:
            context_recall_score = 1.0  # Default perfect score if not evaluating

        # Evaluate answer completeness
        if evaluation_type in [EvaluationType.ANSWER_COMPLETENESS, EvaluationType.BOTH]:
            completeness_details = self.evaluate_answer_completeness(ground_truth_item.expected_answer, actual_response)
            completeness_score = completeness_details["completeness_score"]
        else:
            completeness_score = 1.0  # Default perfect score if not evaluating

        # Calculate overall score (weighted average)
        if evaluation_type == EvaluationType.BOTH:
            overall_score = (context_recall_score * 0.6) + (completeness_score * 0.4)
        else:
            overall_score = (
                context_recall_score if evaluation_type == EvaluationType.CONTEXT_RECALL else completeness_score
            )

        # Determine overall assessment
        if overall_score >= 0.9:
            assessment = "Excellent ground truth alignment"
        elif overall_score >= 0.7:
            assessment = "Good ground truth alignment"
        elif overall_score >= 0.5:
            assessment = "Fair ground truth alignment"
        else:
            assessment = "Poor ground truth alignment"

        return GroundTruthResult(
            context_recall_score=context_recall_score,
            answer_completeness_score=completeness_score,
            overall_score=overall_score,
            context_recall_details=context_recall_details,
            completeness_details=completeness_details,
            overall_assessment=assessment,
        )

    def generate_ground_truth_report(self, result: GroundTruthResult) -> str:
        """Generate a human-readable ground truth evaluation report."""

        report = f"""
🎯 GROUND TRUTH EVALUATION REPORT
{'='*50}

📊 OVERALL SCORE: {result.overall_score:.2f}/1.00
📋 ASSESSMENT: {result.overall_assessment}

📈 COMPONENT SCORES:
   • Context Recall: {result.context_recall_score:.2f}/1.00
   • Answer Completeness: {result.answer_completeness_score:.2f}/1.00

🔍 CONTEXT RECALL DETAILS:
"""

        if result.context_recall_details:
            recall = result.context_recall_details
            report += f"""
   • Recall Score: {recall.get('recall_score', 0):.2f}
   • Covered Facts: {len(recall.get('covered_facts', []))}
   • Missing Facts: {len(recall.get('missing_facts', []))}
   • Reasoning: {recall.get('reasoning', 'N/A')}
"""

        report += """
🔍 ANSWER COMPLETENESS DETAILS:
"""

        if result.completeness_details:
            completeness = result.completeness_details
            report += f"""
   • Completeness Score: {completeness.get('completeness_score', 0):.2f}
   • Covered Information: {len(completeness.get('covered_info', []))}
   • Missing Information: {len(completeness.get('missing_info', []))}
   • Reasoning: {completeness.get('reasoning', 'N/A')}
"""

        return report


def main():
    """Test the ground truth evaluator."""
    evaluator = GroundTruthEvaluator()

    # Test case
    ground_truth_item = GroundTruthItem(
        query="What is the current project status and backlog priorities?",
        expected_answer="The current project is in sprint X focusing on memory system optimization. The baseline RAGUS score is 73.3/100. Key priorities include implementing faithfulness testing and creating ground truth datasets.",
        key_facts=[
            "current project is in sprint X",
            "focusing on memory system optimization",
            "baseline RAGUS score is 73.3/100",
            "key priorities include implementing faithfulness testing",
        ],
        critical_information=["sprint X", "memory system optimization", "73.3/100", "faithfulness testing"],
        context_requirements=["project status", "backlog priorities", "current sprint", "baseline score"],
    )

    retrieved_context = """
    The current project is in sprint X focusing on memory system optimization.
    The baseline RAGUS evaluation system was implemented with fixed criteria.
    The initial baseline score was established at 73.3/100.
    """

    actual_response = """
    The current project is in sprint X focusing on memory system optimization.
    The baseline RAGUS score is 73.3/100. Key priorities include implementing
    faithfulness testing and creating ground truth datasets.
    """

    result = evaluator.evaluate_ground_truth(ground_truth_item, retrieved_context, actual_response)

    report = evaluator.generate_ground_truth_report(result)
    print(report)


if __name__ == "__main__":
    main()
