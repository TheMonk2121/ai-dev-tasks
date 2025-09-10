#!/usr/bin/env python3
"""
Specific Technical Review using DSPy Roles
Runs targeted technical review prompts through DSPy roles for specific engineering feedback.
"""

import os
import sys
from pathlib import Path

# Add the dspy-rag-system to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.dspy_modules.context_models import CoderContext, ImplementerContext, PlannerContext, ResearcherContext
from src.dspy_modules.model_switcher import ModelSwitcher


def run_specific_technical_review():
    """Run specific technical reviews through DSPy roles."""

    # Set up environment
    os.environ.setdefault("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")

    # Initialize the model switcher
    model_switcher = ModelSwitcher()

    # Initialize RAG pipeline
    rag_pipeline = model_switcher.rag_pipeline

    # Specific technical review prompts
    specific_prompts = {
        "Researcher": """
Review the 13 core documentation files for these SPECIFIC technical issues:

1. **Database Schema Documentation**: Are PostgreSQL table structures, indexes, and constraints clearly documented?
2. **API Endpoints**: Are all DSPy module interfaces, parameters, and return types specified?
3. **Error Handling**: Are failure modes, exceptions, and recovery procedures documented?
4. **Performance Characteristics**: Are memory usage, latency, and scalability limits mentioned?
5. **Security Considerations**: Are authentication, authorization, and data protection measures documented?

Provide concrete examples of what's missing or unclear.
""",
        "Planner": """
Analyze the 13 core documents for these SPECIFIC planning gaps:

1. **Dependency Management**: Are all external dependencies, versions, and compatibility requirements listed?
2. **Deployment Procedures**: Are installation, configuration, and deployment steps detailed?
3. **Monitoring & Alerting**: Are health checks, metrics, and alerting thresholds specified?
4. **Backup & Recovery**: Are data backup, restore, and disaster recovery procedures documented?
5. **Scaling Strategy**: Are horizontal/vertical scaling approaches and resource requirements defined?

List specific missing elements that could cause deployment or operational issues.
""",
        "Implementer": """
Examine the 13 core documents for these SPECIFIC implementation risks:

1. **Code Examples**: Are there sufficient code snippets showing actual usage patterns?
2. **Configuration Files**: Are sample config files, environment variables, and settings documented?
3. **Testing Procedures**: Are unit test examples, integration test scenarios, and validation steps provided?
4. **Debugging Guides**: Are troubleshooting procedures, log analysis, and debugging tools documented?
5. **Integration Points**: Are API integrations, data flows, and system boundaries clearly defined?

Identify specific implementation gaps that could cause development delays or bugs.
""",
        "Coder": """
Review the 13 core documents for these SPECIFIC coding issues:

1. **Type Definitions**: Are all data structures, classes, and interfaces properly typed?
2. **Function Signatures**: Are method parameters, return types, and side effects documented?
3. **Code Patterns**: Are design patterns, best practices, and anti-patterns explained?
4. **Performance Code**: Are optimization techniques, caching strategies, and performance tips included?
5. **Error Codes**: Are all error codes, exception types, and error handling patterns documented?

Provide specific code examples of what's missing or could be improved.
""",
    }

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

    # Run specific reviews through different roles
    roles = [
        (
            "Researcher",
            ResearcherContext(
                session_id="specific_tech_review_researcher",
                research_topic="specific technical accuracy and completeness analysis",
                methodology="analysis",
                sources=core_docs,
                user_id="technical_reviewer",
                vector_enhancement_timestamp=None,
            ),
        ),
        (
            "Planner",
            PlannerContext(
                session_id="specific_tech_review_planner",
                project_scope="specific technical documentation gaps and planning risks",
                backlog_priority="P0",
                strategic_goals=[
                    "identify specific technical gaps",
                    "assess implementation risks",
                    "improve engineering precision",
                ],
                user_id="technical_reviewer",
                vector_enhancement_timestamp=None,
            ),
        ),
        (
            "Implementer",
            ImplementerContext(
                session_id="specific_tech_review_implementer",
                implementation_plan="Review specific technical implementation details and code examples",
                target_environment="development",
                user_id="technical_reviewer",
                vector_enhancement_timestamp=None,
                rollback_strategy="documentation backup",
            ),
        ),
        (
            "Coder",
            CoderContext(
                session_id="specific_tech_review_coder",
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

    print("🔍 Running SPECIFIC Technical Review through DSPy Roles...")
    print("=" * 80)

    results = {}

    for role_name, context in roles:
        print(f"\n🎭 {role_name.upper()} ROLE SPECIFIC TECHNICAL REVIEW")
        print("=" * 60)

        try:
            # Get the specific prompt for this role
            specific_prompt = specific_prompts[role_name]

            # Run the specific review through the RAG pipeline
            result = rag_pipeline.answer(specific_prompt)

            # Extract the answer - RAGPipeline.answer() returns dict[str, Any]
            if result is None:
                answer = "No result"
                context_info = ""
            elif isinstance(result, dict):
                answer = result.get("answer", str(result))
                context_info = result.get("context", "")
            else:
                # Fallback for unexpected return types
                answer = str(result) if result is not None else "No result"
                context_info = ""

            print(str(answer) if answer is not None else "No answer generated")

            if context_info:
                print(f"\n🔍 {role_name} Context Information:")
                print("-" * 40)
                print(context_info[:500] + "..." if len(context_info) > 500 else context_info)

            results[role_name] = answer

        except Exception as e:
            print(f"❌ Error running {role_name} specific review: {e}")
            results[role_name] = f"Error: {e}"

    # Provide summary
    print("\n" + "=" * 80)
    print("📋 SPECIFIC TECHNICAL REVIEW SUMMARY")
    print("=" * 80)

    for role_name, review_result in results.items():
        print(f"\n🎭 {role_name} Specific Technical Findings:")
        print("-" * 40)
        # Extract key points from the result
        lines = review_result.split("\n")
        key_points = [
            line.strip()
            for line in lines
            if line.strip().startswith("*")
            or line.strip().startswith("-")
            or "missing" in line.lower()
            or "unclear" in line.lower()
            or "error" in line.lower()
            or "risk" in line.lower()
            or "gap" in line.lower()
        ]
        for point in key_points[:10]:  # Show first 10 key points
            print(f"  {point}")

    return results


if __name__ == "__main__":
    results = run_specific_technical_review()
    sys.exit(0)
