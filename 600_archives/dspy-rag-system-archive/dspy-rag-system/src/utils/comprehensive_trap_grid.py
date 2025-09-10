#!/usr/bin/env python3
"""
Comprehensive Trap Grid - Right Questions Coverage
Balanced evaluation dataset covering ops/health, DB workflows, RAG QA, meta-ops, and negative controls
"""

import json
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any


class TrapCategory(Enum):
    """Categories of evaluation traps."""

    OPS_HEALTH = "ops_health"
    DB_WORKFLOWS = "db_workflows"
    RAG_QA = "rag_qa"
    META_OPS = "meta_ops"
    NEGATIVE_CONTROLS = "negative_controls"


@dataclass
class TrapCase:
    """Individual trap case for evaluation."""

    id: str
    category: TrapCategory
    question: str
    expected_behavior: str
    success_criteria: list[str]
    oracle_answer: str | None = None
    context_required: bool = True
    difficulty: str = "medium"  # easy, medium, hard
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ComprehensiveTrapGrid:
    """Comprehensive trap grid for evaluation coverage."""

    def __init__(self):
        self.traps: list[TrapCase] = []
        self._initialize_traps()

    def _initialize_traps(self):
        """Initialize the comprehensive trap grid."""

        # Ops/Health Traps (must call the right tools)
        ops_health_traps = [
            TrapCase(
                id="ops_001",
                category=TrapCategory.OPS_HEALTH,
                question="Verify that pgvector extension is properly installed and active",
                expected_behavior="Agent should run healthcheck tool and report pgvector status",
                success_criteria=[
                    "Calls healthcheck tool",
                    "Reports pgvector extension status",
                    "Provides actionable guidance if issues found",
                ],
                oracle_answer="pgvector extension is installed and active",
                tags=["healthcheck", "pgvector", "extension"],
            ),
            TrapCase(
                id="ops_002",
                category=TrapCategory.OPS_HEALTH,
                question="Detect any BM25 prefix leakage in the document chunks",
                expected_behavior="Agent should check for chunks starting with 'Document:' prefix",
                success_criteria=[
                    "Queries document_chunks table",
                    "Checks bm25_text field for prefix patterns",
                    "Reports leakage count and examples",
                ],
                oracle_answer="No prefix leakage detected (all chunks start with content, not 'Document:')",
                tags=["prefix_leakage", "bm25", "data_quality"],
            ),
            TrapCase(
                id="ops_003",
                category=TrapCategory.OPS_HEALTH,
                question="Confirm embedding dimensions are consistent across all chunks",
                expected_behavior="Agent should verify all embeddings have correct dimension (384)",
                success_criteria=[
                    "Checks embedding dimensions",
                    "Reports consistency status",
                    "Identifies any mismatches",
                ],
                oracle_answer="All embeddings have consistent dimension of 384",
                tags=["embedding_dimensions", "consistency", "vector_store"],
            ),
        ]

        # DB Workflows Traps
        db_workflow_traps = [
            TrapCase(
                id="db_001",
                category=TrapCategory.DB_WORKFLOWS,
                question="Show the top 5 slowest queries in the system",
                expected_behavior="Agent should query pg_stat_statements or similar for slow queries",
                success_criteria=[
                    "Accesses query performance data",
                    "Ranks queries by execution time",
                    "Provides query text and timing",
                ],
                oracle_answer="List of top 5 slowest queries with execution times",
                tags=["slow_queries", "performance", "pg_stat_statements"],
            ),
            TrapCase(
                id="db_002",
                category=TrapCategory.DB_WORKFLOWS,
                question="Create a plan to rebuild vector indexes for better performance",
                expected_behavior="Agent should analyze current indexes and propose rebuild strategy",
                success_criteria=[
                    "Analyzes current vector indexes",
                    "Identifies optimization opportunities",
                    "Provides step-by-step rebuild plan",
                ],
                oracle_answer="Comprehensive vector index rebuild plan with timing and impact analysis",
                tags=["vector_indexes", "rebuild", "optimization"],
            ),
            TrapCase(
                id="db_003",
                category=TrapCategory.DB_WORKFLOWS,
                question="Explain how FTS (Full Text Search) ranking works in our system",
                expected_behavior="Agent should explain ts_rank, ts_rank_cd, and ranking algorithms",
                success_criteria=[
                    "Explains FTS ranking concepts",
                    "Describes ts_rank vs ts_rank_cd",
                    "Provides examples from our schema",
                ],
                oracle_answer="Detailed explanation of FTS ranking with examples from our document_chunks table",
                tags=["fts", "ranking", "ts_rank", "explanation"],
            ),
        ]

        # RAG QA Traps
        rag_qa_traps = [
            TrapCase(
                id="rag_001",
                category=TrapCategory.RAG_QA,
                question="What is DSPy and how does it work?",
                expected_behavior="Agent should retrieve relevant DSPy documentation and provide comprehensive answer",
                success_criteria=[
                    "Retrieves DSPy-related chunks",
                    "Provides accurate definition",
                    "Explains key concepts (modules, signatures, teleprompters)",
                ],
                oracle_answer="DSPy is a framework for programming with foundation models that provides systematic approaches to building AI applications",
                context_required=True,
                tags=["dspy", "framework", "definition"],
            ),
            TrapCase(
                id="rag_002",
                category=TrapCategory.RAG_QA,
                question="How do I implement a custom RAG pipeline with hybrid retrieval?",
                expected_behavior="Agent should provide step-by-step implementation guide",
                success_criteria=[
                    "Explains hybrid retrieval concept",
                    "Provides implementation steps",
                    "Includes code examples or references",
                ],
                oracle_answer="Step-by-step guide to implementing hybrid RAG with dense and sparse retrieval",
                context_required=True,
                tags=["rag", "hybrid_retrieval", "implementation"],
            ),
            TrapCase(
                id="rag_003",
                category=TrapCategory.RAG_QA,
                question="What are the performance benchmarks for our current chunking strategy?",
                expected_behavior="Agent should retrieve and analyze performance data",
                success_criteria=[
                    "Finds performance benchmark data",
                    "Analyzes chunking strategy metrics",
                    "Provides comparative analysis",
                ],
                oracle_answer="Performance benchmarks showing chunking strategy effectiveness",
                context_required=True,
                tags=["performance", "benchmarks", "chunking"],
            ),
            TrapCase(
                id="rag_004",
                category=TrapCategory.RAG_QA,
                question="When was the last evaluation run and what were the results?",
                expected_behavior="Agent should find recent evaluation results and summarize",
                success_criteria=[
                    "Locates recent evaluation data",
                    "Summarizes key metrics",
                    "Identifies trends or issues",
                ],
                oracle_answer="Summary of most recent evaluation run with key metrics and insights",
                context_required=True,
                tags=["evaluation", "results", "metrics"],
            ),
        ]

        # Meta-Ops Traps
        meta_ops_traps = [
            TrapCase(
                id="meta_001",
                category=TrapCategory.META_OPS,
                question="Generate a complete evaluation runbook for production deployment",
                expected_behavior="Agent should create comprehensive runbook with all steps",
                success_criteria=[
                    "Includes pre-deployment checks",
                    "Covers evaluation steps",
                    "Provides rollback procedures",
                    "Includes monitoring guidelines",
                ],
                oracle_answer="Complete production evaluation runbook with all necessary steps and procedures",
                tags=["runbook", "production", "deployment"],
            ),
            TrapCase(
                id="meta_002",
                category=TrapCategory.META_OPS,
                question="Explain the agent tool schemas and how to use them",
                expected_behavior="Agent should document tool schemas and usage patterns",
                success_criteria=[
                    "Lists available tools",
                    "Explains tool schemas",
                    "Provides usage examples",
                    "Documents validation rules",
                ],
                oracle_answer="Comprehensive documentation of agent tool schemas and usage patterns",
                tags=["tool_schemas", "documentation", "agent_tools"],
            ),
            TrapCase(
                id="meta_003",
                category=TrapCategory.META_OPS,
                question="Why did this specific evaluation case fail at the oracle stage?",
                expected_behavior="Agent should analyze oracle failure and provide diagnostic information",
                success_criteria=[
                    "Identifies oracle stage failure",
                    "Analyzes root cause",
                    "Provides diagnostic steps",
                    "Suggests remediation",
                ],
                oracle_answer="Detailed analysis of oracle stage failure with root cause and remediation steps",
                tags=["oracle_failure", "diagnostics", "troubleshooting"],
            ),
        ]

        # Negative Controls (cases with no answer in corpus)
        negative_control_traps = [
            TrapCase(
                id="neg_001",
                category=TrapCategory.NEGATIVE_CONTROLS,
                question="What is the capital of Mars?",
                expected_behavior="Agent should decline to answer and explain why",
                success_criteria=[
                    "Recognizes question is outside corpus",
                    "Declines to hallucinate answer",
                    "Explains limitation clearly",
                    "Suggests alternative approach",
                ],
                oracle_answer="I cannot answer this question as it's outside the scope of our documentation corpus",
                context_required=False,
                tags=["negative_control", "hallucination_prevention", "scope_limitation"],
            ),
            TrapCase(
                id="neg_002",
                category=TrapCategory.NEGATIVE_CONTROLS,
                question="How do I configure a quantum computer for machine learning?",
                expected_behavior="Agent should decline and explain scope limitations",
                success_criteria=[
                    "Recognizes topic is outside corpus",
                    "Does not provide speculative answer",
                    "Explains corpus scope",
                    "Offers relevant alternatives",
                ],
                oracle_answer="This question is outside the scope of our documentation. I can help with DSPy, RAG systems, or vector databases instead.",
                context_required=False,
                tags=["negative_control", "quantum_computing", "scope_limitation"],
            ),
            TrapCase(
                id="neg_003",
                category=TrapCategory.NEGATIVE_CONTROLS,
                question="What is the exact revenue of OpenAI in 2024?",
                expected_behavior="Agent should decline and explain why this information isn't available",
                success_criteria=[
                    "Recognizes financial data not in corpus",
                    "Declines to speculate",
                    "Explains information limitation",
                    "Maintains professional tone",
                ],
                oracle_answer="I don't have access to OpenAI's financial information in our documentation corpus",
                context_required=False,
                tags=["negative_control", "financial_data", "information_limitation"],
            ),
        ]

        # Combine all traps
        self.traps = ops_health_traps + db_workflow_traps + rag_qa_traps + meta_ops_traps + negative_control_traps

    def get_traps_by_category(self, category: TrapCategory) -> list[TrapCase]:
        """Get traps filtered by category."""
        return [trap for trap in self.traps if trap.category == category]

    def get_traps_by_difficulty(self, difficulty: str) -> list[TrapCase]:
        """Get traps filtered by difficulty."""
        return [trap for trap in self.traps if trap.difficulty == difficulty]

    def get_traps_by_tags(self, tags: list[str]) -> list[TrapCase]:
        """Get traps that match any of the specified tags."""
        return [trap for trap in self.traps if any(tag in trap.tags for tag in tags)]

    def get_balanced_sample(self, n_per_category: int = 2) -> list[TrapCase]:
        """Get a balanced sample of traps across all categories."""
        balanced_sample = []

        for category in TrapCategory:
            category_traps = self.get_traps_by_category(category)
            if len(category_traps) >= n_per_category:
                # Randomly sample n_per_category traps from this category
                sampled = random.sample(category_traps, n_per_category)
                balanced_sample.extend(sampled)
            else:
                # Take all traps from this category if fewer than n_per_category
                balanced_sample.extend(category_traps)

        return balanced_sample

    def export_to_jsonl(self, filename: str, traps: list[TrapCase] | None = None):
        """Export traps to JSONL format for evaluation."""
        if traps is None:
            traps = self.traps

        with open(filename, "w") as f:
            for trap in traps:
                trap_dict = {
                    "id": trap.id,
                    "category": trap.category.value,
                    "question": trap.question,
                    "expected_behavior": trap.expected_behavior,
                    "success_criteria": trap.success_criteria,
                    "oracle_answer": trap.oracle_answer,
                    "context_required": trap.context_required,
                    "difficulty": trap.difficulty,
                    "tags": trap.tags,
                }
                f.write(json.dumps(trap_dict) + "\n")

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the trap grid."""
        stats = {
            "total_traps": len(self.traps),
            "by_category": {},
            "by_difficulty": {},
            "by_context_requirement": {
                "context_required": sum(1 for t in self.traps if t.context_required),
                "no_context_required": sum(1 for t in self.traps if not t.context_required),
            },
        }

        # Count by category
        for category in TrapCategory:
            stats["by_category"][category.value] = len(self.get_traps_by_category(category))

        # Count by difficulty
        difficulties = set(trap.difficulty for trap in self.traps)
        for difficulty in difficulties:
            stats["by_difficulty"][difficulty] = len(self.get_traps_by_difficulty(difficulty))

        return stats


def main():
    """Generate and export the comprehensive trap grid."""
    trap_grid = ComprehensiveTrapGrid()

    # Print statistics
    stats = trap_grid.get_statistics()
    print("🎯 Comprehensive Trap Grid Statistics")
    print("=" * 50)
    print(f"Total Traps: {stats['total_traps']}")
    print("\nBy Category:")
    for category, count in stats["by_category"].items():
        print(f"  {category}: {count}")
    print("\nBy Difficulty:")
    for difficulty, count in stats["by_difficulty"].items():
        print(f"  {difficulty}: {count}")
    print("\nContext Requirements:")
    print(f"  Required: {stats['by_context_requirement']['context_required']}")
    print(f"  Not Required: {stats['by_context_requirement']['no_context_required']}")

    # Export full grid
    trap_grid.export_to_jsonl("eval/comprehensive_trap_grid.jsonl")
    print("\n📁 Full trap grid exported to: eval/comprehensive_trap_grid.jsonl")

    # Export balanced sample
    balanced_sample = trap_grid.get_balanced_sample(n_per_category=2)
    trap_grid.export_to_jsonl("eval/balanced_trap_sample.jsonl", balanced_sample)
    print("📁 Balanced sample exported to: eval/balanced_trap_sample.jsonl")

    # Export by category
    for category in TrapCategory:
        category_traps = trap_grid.get_traps_by_category(category)
        filename = f"eval/traps_{category.value}.jsonl"
        trap_grid.export_to_jsonl(filename, category_traps)
        print(f"📁 {category.value} traps exported to: {filename}")


if __name__ == "__main__":
    main()
