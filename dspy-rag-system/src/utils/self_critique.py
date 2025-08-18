#!/usr/bin/env python3.12.123.11
"""
Self-Critique Module - Anthropic-Style Reflection Checkpoints
-------------------------------------------------------------
Implements Anthropic's Constitutional AI reflection pattern for bundle validation.
Asks the model to critique its own context before execution to reduce silent failures.

Based on:
- Anthropic Constitutional AI: Reflection checkpoints
- Stanford Self-Refine: Self-evaluation patterns
- Berkeley Reflexion: Self-critique mechanisms
"""

from dataclasses import dataclass
from typing import Any

from .logger import get_logger

logger = get_logger("self_critique")


@dataclass
class CritiqueResult:
    """Result of self-critique evaluation"""

    is_sufficient: bool
    confidence_score: float  # 0.0-1.0
    missing_context: list[str]
    suggestions: list[str]
    critique_text: str
    verification_passed: bool


class SelfCritiqueEngine:
    """Self-critique engine for bundle validation"""

    def __init__(self):
        self.critique_prompt_template = """
You are evaluating the context bundle provided to you for a specific task.

TASK: {task}
ROLE: {role}

CONTEXT BUNDLE:
{bundle_text}

CRITIQUE INSTRUCTIONS:
1. Evaluate if this context is sufficient for the given task
2. Identify any missing critical information
3. Suggest improvements if needed
4. Verify the echo verification hashes match

Please respond in this exact JSON format:
{{
    "is_sufficient": true/false,
    "confidence_score": 0.0-1.0,
    "missing_context": ["list", "of", "missing", "items"],
    "suggestions": ["list", "of", "improvements"],
    "verification_passed": true/false,
    "critique_text": "detailed explanation"
}}

Focus on:
- Task relevance of provided context
- Completeness for the specific role
- Quality and recency of information
- Echo verification integrity
"""

    def critique_bundle(self, bundle_text: str, task: str, role: str = "planner") -> CritiqueResult:
        """Perform self-critique of bundle"""
        try:
            # Extract echo verification from bundle
            echo_verification = self._extract_echo_verification(bundle_text)

            # Generate critique prompt (for future LLM integration)
            # prompt = self.critique_prompt_template.format(task=task, role=role, bundle_text=bundle_text)

            # For now, we'll simulate the critique
            # In production, this would call the LLM
            critique_result = self._simulate_critique(bundle_text, task, role, echo_verification)

            logger.info(
                "Self-critique completed",
                extra={
                    "task": task,
                    "role": role,
                    "is_sufficient": critique_result.is_sufficient,
                    "confidence_score": critique_result.confidence_score,
                    "verification_passed": critique_result.verification_passed,
                },
            )

            return critique_result

        except Exception as e:
            logger.error("Self-critique failed", extra={"error": str(e), "task": task, "role": role})

            # Return default critique on failure
            return CritiqueResult(
                is_sufficient=True,  # Default to allowing execution
                confidence_score=0.5,
                missing_context=[],
                suggestions=["Self-critique failed, proceeding with caution"],
                critique_text=f"Self-critique failed: {str(e)}",
                verification_passed=False,
            )

    def _extract_echo_verification(self, bundle_text: str) -> dict[str, Any]:
        """Extract echo verification from bundle text"""
        try:
            # Find echo verification section
            if "[ECHO VERIFICATION]" not in bundle_text:
                return {}

            echo_section = bundle_text.split("[ECHO VERIFICATION]")[1].split("\n\n")[0]

            verification = {}
            for line in echo_section.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "Bundle Hash":
                        verification["bundle_hash"] = value
                    elif key == "Pins Hash":
                        verification["pins_hash"] = value
                    elif key == "Evidence Hashes":
                        verification["evidence_hashes"] = [h.strip() for h in value.split(",")]
                    elif key == "Entities":
                        verification["entities"] = [e.strip() for e in value.split(",")]

            return verification

        except Exception as e:
            logger.warning("Failed to extract echo verification", extra={"error": str(e)})
            return {}

    def _simulate_critique(
        self, bundle_text: str, task: str, role: str, echo_verification: dict[str, Any]
    ) -> CritiqueResult:
        """Simulate critique for testing (replace with actual LLM call)"""

        # Basic verification checks
        verification_passed = True
        missing_context = []
        suggestions = []

        # Check if bundle has required sections
        if "[TLDR]" not in bundle_text:
            missing_context.append("TLDR section")
            verification_passed = False

        if "[EVIDENCE]" not in bundle_text:
            missing_context.append("Evidence section")
            verification_passed = False

        # Check echo verification
        if not echo_verification.get("bundle_hash"):
            missing_context.append("Bundle hash verification")
            verification_passed = False

        # Role-specific checks
        if role == "planner":
            if "backlog" not in bundle_text.lower() and "priority" not in bundle_text.lower():
                suggestions.append("Consider adding backlog/priority context for planning tasks")

        elif role == "implementer":
            if "code" not in bundle_text.lower() and "implementation" not in bundle_text.lower():
                suggestions.append("Consider adding code/implementation context for coding tasks")

        # Determine sufficiency
        is_sufficient = len(missing_context) == 0 and verification_passed
        confidence_score = 0.8 if is_sufficient else 0.4

        critique_text = f"Bundle {'sufficient' if is_sufficient else 'insufficient'} for {role} task: {task}. "
        if missing_context:
            critique_text += f"Missing: {', '.join(missing_context)}. "
        if suggestions:
            critique_text += f"Suggestions: {', '.join(suggestions)}."

        return CritiqueResult(
            is_sufficient=is_sufficient,
            confidence_score=confidence_score,
            missing_context=missing_context,
            suggestions=suggestions,
            critique_text=critique_text,
            verification_passed=verification_passed,
        )

    def add_critique_to_bundle(self, bundle_text: str, critique: CritiqueResult) -> str:
        """Add critique results to bundle"""
        critique_section = "\n\n[SELF-CRITIQUE]\n"
        critique_section += f"Sufficient: {critique.is_sufficient}\n"
        critique_section += f"Confidence: {critique.confidence_score:.2f}\n"
        critique_section += f"Verification: {'PASSED' if critique.verification_passed else 'FAILED'}\n"

        if critique.missing_context:
            critique_section += f"Missing: {', '.join(critique.missing_context)}\n"

        if critique.suggestions:
            critique_section += f"Suggestions: {', '.join(critique.suggestions)}\n"

        critique_section += f"\nCritique: {critique.critique_text}\n"

        return bundle_text + critique_section


# Global critique engine
critique_engine = SelfCritiqueEngine()


def add_self_critique(bundle_text: str, task: str, role: str = "planner") -> str:
    """Add self-critique to bundle"""
    critique = critique_engine.critique_bundle(bundle_text, task, role)
    return critique_engine.add_critique_to_bundle(bundle_text, critique)
