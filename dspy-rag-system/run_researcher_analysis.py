#!/usr/bin/env python3
"""
DSPy Researcher Role Analysis Script
Activates the DSPy Researcher role to analyze 00-12 core documentation structure
"""

import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.context_models import ResearcherContext
from dspy_modules.model_switcher import ModelSwitcher


def run_researcher_analysis():
    """Run the DSPy Researcher role analysis on 00-12 documentation"""

    print("🔬 DSPY RESEARCHER ROLE ANALYSIS")
    print("=" * 50)

    # Create researcher context
    researcher_context = ResearcherContext(
        session_id="doc_analysis_001",
        research_topic="Core documentation structure analysis for 00-12 guides",
        methodology="analysis",
        hypotheses=[
            "Current documentation has flow issues",
            "Multiple entry points create confusion",
            "Logical progression is unclear",
            "Cross-references may be inconsistent",
        ],
        constraints={
            "focus": "00-12 core documentation files",
            "output": "cohesive structure recommendations",
            "scope": "user journey optimization",
        },
    )

    print(f"🎭 Role: {researcher_context.role}")
    print(f"📋 Topic: {researcher_context.research_topic}")
    print(f"🔬 Methodology: {researcher_context.methodology}")
    print(f"💡 Hypotheses: {len(researcher_context.hypotheses)}")

    # Initialize model switcher
    switcher = ModelSwitcher()

    # Create research query
    research_query = """
    Based on the current 00-12 documentation files, provide a specific implementation plan for restructuring with this priority order:

    **PRIORITY ORDER:**
    1. Memory System (00-02)
    2. Codebase (03-05)
    3. Backlog (06-08)
    4. Advanced Topics (09-12)

    **SPECIFIC TASKS:**
    1. Map current files to new structure
    2. Identify which files should move where
    3. List cross-references that need updating
    4. Provide step-by-step migration commands
    5. Suggest rollback strategy

    Focus on practical, actionable steps that preserve all content.
    """

    print("\n🔍 RESEARCHING DOCUMENTATION STRUCTURE...")
    print("=" * 50)

    # Use the RAG pipeline to analyze the documentation
    try:
        # Get the RAG pipeline from the model switcher
        rag_pipeline = switcher.rag_pipeline

        # Run the research query
        result = rag_pipeline.answer(research_query)

        print("\n📊 RESEARCH FINDINGS:")
        print("=" * 50)

        # Handle different result formats
        if isinstance(result, dict):
            answer = result.get("answer", str(result))
            context = result.get("context", [])
        else:
            answer = getattr(result, "answer", str(result))
            context = getattr(result, "context", [])

        print(answer)

        if context:
            print(f"\n📚 SOURCES CONSULTED: {len(context)} documents")
            for i, doc in enumerate(context[:5], 1):  # Show first 5
                print(f"  {i}. {doc}")

        return {
            "success": True,
            "findings": answer,
            "sources": context,
            "role": researcher_context.role.value,
        }

    except Exception as e:
        print(f"❌ Error during research analysis: {e}")
        return {"success": False, "error": str(e), "role": researcher_context.role.value}


if __name__ == "__main__":
    results = run_researcher_analysis()

    print("\n✅ RESEARCH COMPLETE")
    print(f"🎭 Role Used: {results['role']}")
    print(f"📊 Success: {results['success']}")

    if not results["success"]:
        print(f"❌ Error: {results['error']}")
