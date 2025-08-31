#!/usr/bin/env python3
"""
Technical Review using DSPy Roles
Runs the technical review prompt through Researcher, Planner, Implementer, and Coder roles for comprehensive engineering feedback.
"""

import os
import sys
from pathlib import Path

# Add the dspy-rag-system to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.dspy_modules.context_models import CoderContext, ImplementerContext, PlannerContext, ResearcherContext
from src.dspy_modules.model_switcher import ModelSwitcher


def run_technical_review():
    """Run the Technical Review through multiple DSPy roles."""

    # Set up environment
    os.environ.setdefault("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")

    # Initialize the model switcher
    model_switcher = ModelSwitcher()

    # Initialize RAG pipeline
    rag_pipeline = model_switcher.rag_pipeline

    # Technical Review prompt
    review_prompt = """
Role
You are a senior software engineer reviewing 13 core documents inside a developer repo. Your focus is on technical accuracy, completeness, and system robustness. You care less about narrative flow and more about whether the docs capture edge cases, dependencies, and implementation-level detail.

Task

Verify that each document is technically accurate and internally consistent.

Check whether system design decisions are clearly explained with trade-offs noted.

Identify missing details (edge cases, assumptions, failure modes).

Flag ambiguous technical language that could cause implementation drift.

Check that inter-doc references reflect real dependencies (not just hand-waving).

Highlight risks where incomplete documentation could lead to rework or bugs.

Context

Repo has 13 "spine" docs that describe a RAG/CAG/Memory system stack.

Audience: future engineers, contributors, and AI agents needing precision for implementation.

Goal: ensure correctness, technical depth, and resilience of documentation over time.

Output
Provide a structured review with the following sections:

Technical Completeness: What's fully captured, what's missing.

Edge Cases & Assumptions: What's implied vs. explicit, and risks of ambiguity.

Accuracy Check: Potential technical misstatements or contradictions.

Dependencies & Interactions: Whether inter-doc dependencies are faithfully described.

Implementation Risk: Where unclear docs could lead to drift, errors, or tech debt.

Final Recommendations: Ranked fixes for ensuring engineering robustness.
"""

    # Define the 13 core documents with absolute paths
    base_path = Path("/Users/danieljacobs/Code/ai-dev-tasks")
    core_docs = [
        str(base_path / "400_guides/400_00_memory-system-overview.md"),
        str(base_path / "400_guides/400_01_memory-system-architecture.md"),
        str(base_path / "400_guides/400_02_memory-rehydration-context-management.md"),
        str(base_path / "400_guides/400_03_system-overview-and-architecture.md"),
        str(base_path / "400_guides/400_04_development-workflow-and-standards.md"),
        str(base_path / "400_guides/400_05_codebase-organization-patterns.md"),
        str(base_path / "400_guides/400_06_backlog-management-priorities.md"),
        str(base_path / "400_guides/400_07_project-planning-roadmap.md"),
        str(base_path / "400_guides/400_08_task-management-workflows.md"),
        str(base_path / "400_guides/400_09_ai-frameworks-dspy.md"),
        str(base_path / "400_guides/400_10_integrations-models.md"),
        str(base_path / "400_guides/400_11_performance-optimization.md"),
        str(base_path / "400_guides/400_12_advanced-configurations.md"),
    ]

    # Run review through different roles
    roles = [
        (
            "Researcher",
            ResearcherContext(
                session_id="technical_review_researcher",
                research_topic="technical accuracy and completeness analysis of 13 core documents",
                methodology="analysis",
                sources=core_docs,
                user_id="technical_reviewer",
                vector_enhancement_timestamp=None,
            ),
        ),
        (
            "Planner",
            PlannerContext(
                session_id="technical_review_planner",
                project_scope="technical documentation review and engineering robustness assessment",
                backlog_priority="P0",
                strategic_goals=[
                    "ensure technical accuracy",
                    "identify implementation risks",
                    "improve engineering robustness",
                ],
                user_id="technical_reviewer",
                vector_enhancement_timestamp=None,
            ),
        ),
        (
            "Implementer",
            ImplementerContext(
                session_id="technical_review_implementer",
                implementation_plan="Review technical documentation for implementation accuracy, edge cases, and system dependencies",
                target_environment="development",
                user_id="technical_reviewer",
                vector_enhancement_timestamp=None,
                rollback_strategy="documentation backup",
            ),
        ),
        (
            "Coder",
            CoderContext(
                session_id="technical_review_coder",
                codebase_path="/Users/danieljacobs/Code/ai-dev-tasks",
                language="python",
                framework="dspy",
                current_file="400_guides/400_00_memory-system-overview.md",
                file_context=core_docs,
                user_id="technical_reviewer",
                vector_enhancement_timestamp=None,
                cursor_model="llama3.1:8b",
            ),
        ),
    ]

    print("🔍 Running Technical Review through DSPy Roles...")
    print("=" * 80)

    results = {}

    for role_name, context in roles:
        print(f"\n🎭 {role_name.upper()} ROLE TECHNICAL REVIEW")
        print("=" * 60)

        try:
            # Run the review through the RAG pipeline
            result = rag_pipeline.answer(review_prompt)

            # Extract the answer - RAGPipeline.answer() returns Dict[str, Any]
            if result is None:
                answer = "No result"
                context_info = ""
            elif isinstance(result, dict):
                answer = result.get("answer", str(result))
                context_info = result.get("context", "")
            else:
                # Use assertion for type narrowing as recommended in Pyright troubleshooting
                assert result is not None, "Result should not be None at this point"
                answer = str(result)
                context_info = ""

            # Use explicit null check as recommended in Pyright troubleshooting
            if answer is not None:
                print(str(answer))
            else:
                print("No answer generated")

            if context_info:
                print(f"\n🔍 {role_name} Context Information:")
                print("-" * 40)
                print(context_info[:500] + "..." if len(context_info) > 500 else context_info)

            results[role_name] = answer

        except Exception as e:
            print(f"❌ Error running {role_name} review: {e}")
            results[role_name] = f"Error: {e}"

    # Provide summary
    print("\n" + "=" * 80)
    print("📋 TECHNICAL REVIEW SUMMARY")
    print("=" * 80)

    for role_name, review_result in results.items():
        print(f"\n🎭 {role_name} Key Technical Insights:")
        print("-" * 40)
        # Extract key points from the result
        lines = review_result.split("\n")
        key_points = [
            line.strip()
            for line in lines
            if line.strip().startswith("*")
            or line.strip().startswith("-")
            or "risk" in line.lower()
            or "missing" in line.lower()
            or "edge case" in line.lower()
        ]
        for point in key_points[:8]:  # Show first 8 key points
            print(f"  {point}")

    return results


if __name__ == "__main__":
    results = run_technical_review()
    sys.exit(0)
