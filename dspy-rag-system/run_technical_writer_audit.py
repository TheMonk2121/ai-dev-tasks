#!/usr/bin/env python3
"""
Technical Writer Flow Audit using DSPy Researcher Role
Analyzes the 13 core documentation files for logical flow and cohesion.
"""

import os
import sys
from pathlib import Path

# Add the dspy-rag-system to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.dspy_modules.context_models import ResearcherContext
from src.dspy_modules.model_switcher import ModelSwitcher


def run_technical_writer_audit():
    """Run the Technical Writer Flow Audit using DSPy Researcher."""

    # Set up environment
    os.environ.setdefault("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")

    # Initialize the model switcher
    model_switcher = ModelSwitcher()

    # Initialize RAG pipeline
    rag_pipeline = model_switcher.rag_pipeline

    # Create researcher context (unused but required for context)
    _context = ResearcherContext(
        session_id="technical_writer_audit_001",
        research_topic="documentation flow and cohesion analysis for 13 core documents",
        methodology="analysis",
        sources=[
            "400_guides/400_00_memory-system-overview.md",
            "400_guides/400_01_memory-system-architecture.md",
            "400_guides/400_02_memory-rehydration-context-management.md",
            "400_guides/400_03_system-overview-and-architecture.md",
            "400_guides/400_04_development-workflow-and-standards.md",
            "400_guides/400_05_codebase-organization-patterns.md",
            "400_guides/400_06_backlog-management-priorities.md",
            "400_guides/400_07_project-planning-roadmap.md",
            "400_guides/400_08_task-management-workflows.md",
            "400_guides/400_09_ai-frameworks-dspy.md",
            "400_guides/400_10_integrations-models.md",
            "400_guides/400_11_performance-optimization.md",
            "400_guides/400_12_advanced-configurations.md",
        ],
        user_id=None,
        vector_enhancement_timestamp=None,
    )

    # Technical Writer Flow Audit prompt
    audit_prompt = """
## Prompt for real local dspy agents:

Prompt: Technical Writer Flow Audit (RTCO)

Role
You are a seasoned technical writer reviewing a set of 13 interdependent core documents inside a developer repo. Your task is to ensure these documents flow logically, are cohesive, and enable readers to onboard effectively. You should not rewrite content, but instead analyze and recommend structural, narrative, and consistency improvements.

Task

Map how the 13 documents depend on each other. Identify where concepts are introduced too late or assumed too early.

Assess whether the documents, read sequentially, form a logical progression of ideas (like a guided narrative).

Identify inconsistencies in terminology, tone, and style across the docs.

Flag redundancies: note when explanations repeat and whether the repetition is reinforcing or bloating.

Suggest improvements to ordering, scoping, and cross-referencing between documents.

Extract a potential glossary of core terms and check whether those terms are defined early and used consistently.

Context

The repo has 13 core documents that serve as the "spine" of the system.

Audience is mixed: developers, AI agents, and future collaborators unfamiliar with the system.

The goal is not only correctness but also flow: a new reader should be able to build a coherent mental model by following the docs in order.

Related lenses (engineer, PM, researcher) exist, but this review should prioritize clarity, flow, and coherence above technical detail.

Output
Provide a structured audit with the following sections:

Dependency Graph: which doc introduces what concepts, and where flow breaks.

Narrative Order Check: suggested re-ordering (if any) and justification.

Terminology & Glossary: list of terms that should be standardized.

Redundancy & Bloat: areas of overlap, and whether to merge, delete, or reinforce.

Cohesion & Cross-Referencing: opportunities to add forward/backward links or summaries.

Final Recommendations: prioritized list of fixes (quick wins vs. deep restructuring).
"""

    print("🔍 Running Technical Writer Flow Audit...")
    print("=" * 60)

    try:
        # Run the audit through the RAG pipeline
        result = rag_pipeline.answer(audit_prompt)

        # Extract the answer
        if isinstance(result, dict):
            answer = result.get("answer", str(result))
            context_info = result.get("context", "")
        else:
            answer = getattr(result, "answer", str(result)) if result is not None else str(result)
            context_info = getattr(result, "context", "") if result is not None else ""

        print("\n📋 TECHNICAL WRITER FLOW AUDIT RESULTS")
        print("=" * 60)
        print(str(answer) if answer is not None else "No answer generated")

        if context_info:
            print("\n🔍 CONTEXT INFORMATION")
            print("=" * 40)
            print(context_info)

    except Exception as e:
        print(f"❌ Error running technical writer audit: {e}")
        return False

    return True


if __name__ == "__main__":
    success = run_technical_writer_audit()
    sys.exit(0 if success else 1)
