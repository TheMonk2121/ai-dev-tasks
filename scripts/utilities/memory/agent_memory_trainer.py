#!/usr/bin/env python3
"""
Agent Memory Training System

Trains agents to be experts on:
1. Evaluation system execution and troubleshooting
2. Memory system usage and optimization
3. Current system status and bottlenecks
4. Lessons learned and best practices

This creates a comprehensive knowledge base that agents can query
to understand exactly how to execute evaluations and use memory systems.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvaluationSystemStatus(BaseModel):
    """Current evaluation system status and metrics with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # RAGChecker Baseline (September 2, 2025)
    current_baseline: dict[str, float] = Field(
        default_factory=lambda: {"precision": 0.159, "recall": 0.166, "f1_score": 0.159, "faithfulness": 0.0},  # TBD
        description="Current baseline metrics",
    )

    # Target Metrics
    target_metrics: dict[str, float] = Field(
        default_factory=lambda: {"precision": 0.20, "recall": 0.45, "f1_score": 0.22, "faithfulness": 0.60},
        description="Target metrics to achieve",
    )

    # Critical Issues
    critical_issues: list[str] = Field(
        default_factory=lambda: [
            "Fallback mode evaluation - advanced features not active",
            "Precision knobs not affecting results",
            "Cross-encoder and NLI gate inactive",
            "Configuration disconnect between setup and evaluation",
        ],
        description="List of critical issues to address",
    )

    # System State
    system_state: str = Field(default="Production-ready but integration issues", description="Overall system state")
    database_status: str = Field(default="Empty - needs population", description="Database status")
    memory_systems: str = Field(default="Implemented but not populated", description="Memory systems status")

    @field_validator("current_baseline", "target_metrics")
    @classmethod
    def validate_metrics(cls, v):
        """Validate metrics are within valid ranges."""
        for key, value in v.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"Metric {key} must be numeric")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Metric {key} must be between 0.0 and 1.0")
        return v


class EvaluationWorkflow(BaseModel):
    """Step-by-step evaluation execution workflow with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    workflow_name: str = Field(..., min_length=1, description="Name of the workflow")
    steps: list[dict[str, Any]] = Field(..., description="List of workflow steps")
    troubleshooting: list[dict[str, Any]] = Field(default_factory=list, description="Troubleshooting information")
    success_criteria: list[str] = Field(..., description="Success criteria for the workflow")

    @field_validator("workflow_name")
    @classmethod
    def validate_workflow_name(cls, v):
        """Validate workflow name is not empty."""
        if not v or not v.strip():
            raise ValueError("Workflow name cannot be empty")
        return v.strip()

    @field_validator("steps", "success_criteria")
    @classmethod
    def validate_non_empty_lists(cls, v):
        """Validate that required lists are not empty."""
        if not v:
            raise ValueError("List cannot be empty")
        return v


class MemorySystemKnowledge(BaseModel):
    """Memory system usage and optimization knowledge with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Available Memory Systems
    memory_systems: dict[str, dict[str, Any]] = Field(
        default_factory=lambda: {
            "ltst": {
                "description": "LTST Memory Integration with async context retrieval",
                "usage": "Primary memory system for context retrieval",
                "status": "Implemented but empty",
                "key_methods": ["retrieve_context", "search_similar_contexts"],
            },
            "cursor": {
                "description": "Cursor memory rehydrator for session continuity",
                "usage": "Cross-session memory and context management",
                "status": "Implemented but empty",
                "key_methods": ["rehydrate_memory", "get_cursor_memory"],
            },
            "unified_orchestrator": {
                "description": "Unified memory orchestrator coordinating all systems",
                "usage": "Main entry point for memory operations",
                "status": "Fully functional",
                "key_methods": ["orchestrate_memory", "get_ltst_memory", "get_cursor_memory"],
            },
            "episodic_memory": {
                "description": "Episodic memory system with three phases",
                "usage": "Enhanced context with heuristics and few-shot learning",
                "status": "Implemented but disabled",
                "key_methods": ["get_enhanced_context", "enhance_system_prompt"],
            },
        }
    )

    # 48-Hour Hot Memory Pool
    hot_memory_pool: dict[str, Any] = Field(
        default_factory=lambda: {
            "table": "conv_chunks",
            "retention_policy": "48 hours",
            "purpose": "Recent high-signal context for agent training",
            "status": "Empty - needs population",
            "usage": "Query recent decisions, files, todos, lessons learned",
        },
        description="Hot memory pool configuration",
    )

    # Database Tables
    memory_tables: list[str] = Field(
        default_factory=lambda: [
            "conversation_sessions",
            "conversation_messages",
            "conversation_memory",
            "memory_retrieval_cache",
            "memory_performance_metrics",
            "session_relationships",
            "conversation_context",
        ],
        description="List of memory-related database tables",
    )


class LessonsLearned(BaseModel):
    """Historical insights and lessons learned with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    evaluation_lessons: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {
                "lesson": "Fallback mode evaluation prevents advanced features",
                "impact": "Critical - all precision knobs ineffective",
                "solution": "Fix evaluation integration to use real RAG system",
                "status": "Open",
            },
            {
                "lesson": "Empty database prevents context retrieval",
                "impact": "RAG system returns 0 contexts",
                "solution": "Populate database with 000-500 content",
                "status": "In Progress",
            },
            {
                "lesson": "Memory systems implemented but not integrated",
                "impact": "Sophisticated memory infrastructure unused",
                "solution": "Integrate memory systems with RAG evaluation",
                "status": "Planned",
            },
            {
                "lesson": "Configuration drift between setup and execution",
                "impact": "Applied parameters don't affect evaluation",
                "solution": "Ensure configuration reaches evaluation logic",
                "status": "Open",
            },
        ],
        description="Lessons learned from evaluation system",
    )

    memory_lessons: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {
                "lesson": "48-hour hot memory pool needs population",
                "impact": "No recent context available for agents",
                "solution": "Populate conv_chunks with evaluation knowledge",
                "status": "Planned",
            },
            {
                "lesson": "Session continuity not established",
                "impact": "No cross-session memory for agents",
                "solution": "Create evaluation sessions and maintain continuity",
                "status": "Planned",
            },
        ],
        description="Lessons learned from memory system",
    )

    @field_validator("evaluation_lessons", "memory_lessons")
    @classmethod
    def validate_lessons(cls, v):
        """Validate lesson structure."""
        for lesson in v:
            required_fields = ["lesson", "impact", "solution", "status"]
            for field in required_fields:
                if field not in lesson:
                    raise ValueError(f"Lesson missing required field: {field}")
                if not isinstance(lesson[field], str) or not lesson[field].strip():
                    raise ValueError(f"Lesson field {field} must be non-empty string")
        return v


class AgentMemoryTrainer:
    """Trains agents on evaluation system and memory usage"""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.eval_status = EvaluationSystemStatus()
        self.memory_knowledge = MemorySystemKnowledge()
        self.lessons_learned = LessonsLearned()

    def create_evaluation_workflows(self) -> dict[str, EvaluationWorkflow]:
        """Create comprehensive evaluation workflows for agent training"""

        workflows = {}

        # RAGChecker Evaluation Workflow
        workflows["ragchecker_evaluation"] = EvaluationWorkflow(
            workflow_name="RAGChecker Official Evaluation",
            steps=[
                {
                    "step": 1,
                    "action": "Check database population",
                    "command": "psql -c 'SELECT COUNT(*) FROM document_chunks;'",
                    "expected": "> 0 chunks",
                    "troubleshooting": "If 0, run ingestion first",
                },
                {
                    "step": 2,
                    "action": "Set environment variables",
                    "command": "export POSTGRES_DSN='postgresql://...' && export GOLD_FILE='300_evals/evals/data/gold/v1/gold_cases.jsonl'",
                    "expected": "Environment set",
                    "troubleshooting": "Verify DSN and file paths",
                },
                {
                    "step": 3,
                    "action": "Run evaluation",
                    "command": "uv run python 300_evals/scripts/evaluation/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable",
                    "expected": "Real evaluation (not fallback)",
                    "troubleshooting": "Check for fallback mode warnings",
                },
                {
                    "step": 4,
                    "action": "Verify results",
                    "command": "Check metrics/baseline_evaluations/ for results",
                    "expected": "Precision ≥ 0.159, Recall ≥ 0.166",
                    "troubleshooting": "If below baseline, check database population",
                },
            ],
            troubleshooting=[
                {
                    "issue": "Real evaluation failed, falling back to mock",
                    "cause": "Empty database or configuration issues",
                    "solution": "Populate database and verify configuration",
                },
                {
                    "issue": "Context assembly produced 0 contexts",
                    "cause": "Empty document_chunks table",
                    "solution": "Run semantic ingestion on 000-500 directories",
                },
                {
                    "issue": "Fallback mode evaluation",
                    "cause": "Advanced features not integrated",
                    "solution": "Fix evaluation integration in _ragchecker_eval_impl.py",
                },
            ],
            success_criteria=[
                "Real evaluation runs (not fallback)",
                "Precision ≥ 0.159 (current baseline)",
                "Recall ≥ 0.166 (current baseline)",
                "Results stored in metrics/baseline_evaluations/",
            ],
        )

        # Memory System Usage Workflow
        workflows["memory_system_usage"] = EvaluationWorkflow(
            workflow_name="Memory System Integration",
            steps=[
                {
                    "step": 1,
                    "action": "Check memory system status",
                    "command": "uv run python scripts/utilities/unified_memory_orchestrator.py --systems ltst cursor --role planner 'current status'",
                    "expected": "Memory systems operational",
                    "troubleshooting": "Check database connection and imports",
                },
                {
                    "step": 2,
                    "action": "Populate hot memory pool",
                    "command": "Populate conv_chunks with evaluation knowledge",
                    "expected": "Recent context available",
                    "troubleshooting": "Ensure 48-hour retention policy active",
                },
                {
                    "step": 3,
                    "action": "Enable session continuity",
                    "command": "Create evaluation sessions and maintain continuity",
                    "expected": "Cross-session memory working",
                    "troubleshooting": "Check session_relationships table",
                },
            ],
            troubleshooting=[
                {
                    "issue": "Memory systems not available",
                    "cause": "Import errors or database issues",
                    "solution": "Check virtual environment and database connection",
                },
                {
                    "issue": "Empty memory tables",
                    "cause": "No data populated",
                    "solution": "Run memory population scripts",
                },
            ],
            success_criteria=[
                "Memory systems respond to queries",
                "Hot memory pool has recent data",
                "Session continuity established",
            ],
        )

        return workflows

    def populate_agent_knowledge_base(self) -> dict[str, Any]:
        """Populate comprehensive agent knowledge base"""

        workflows = self.create_evaluation_workflows()

        knowledge_base = {
            "evaluation_system_status": self.eval_status.__dict__,
            "memory_systems": self.memory_knowledge.__dict__,
            "lessons_learned": self.lessons_learned.__dict__,
            "workflows": {name: workflow.__dict__ for name, workflow in workflows.items()},
            "quick_reference": {
                "current_baseline": "Precision: 0.159, Recall: 0.166, F1: 0.159",
                "critical_issue": "Fallback mode evaluation - advanced features inactive",
                "database_status": "Empty - needs population with 000-500 content",
                "memory_status": "Implemented but not populated",
                "next_action": "Populate database and fix evaluation integration",
            },
            "agent_instructions": {
                "evaluation_expertise": [
                    "Always check database population before running evaluations",
                    "Verify real evaluation (not fallback mode) is running",
                    "Monitor precision/recall against current baseline (0.159/0.166)",
                    "Use memory systems for context retrieval and session continuity",
                ],
                "memory_system_usage": [
                    "Use unified_memory_orchestrator for memory operations",
                    "Query hot memory pool for recent context (48-hour window)",
                    "Maintain session continuity across evaluation runs",
                    "Leverage episodic memory for enhanced context",
                ],
                "troubleshooting": [
                    "If evaluation fails with 0 contexts: populate database",
                    "If fallback mode: fix evaluation integration",
                    "If memory systems empty: run population scripts",
                    "If configuration drift: verify parameter application",
                ],
            },
        }

        return knowledge_base

    def store_agent_knowledge(self, knowledge_base: dict[str, Any]) -> bool:
        """Store agent knowledge in database for memory system integration"""

        try:
            conn = psycopg2.connect(self.dsn)
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Create agent knowledge table if not exists
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_knowledge_base (
                    id SERIAL PRIMARY KEY,
                    knowledge_type VARCHAR(100) NOT NULL,
                    knowledge_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Store knowledge base
            cur.execute(
                """
                INSERT INTO agent_knowledge_base (knowledge_type, knowledge_data)
                VALUES (%s, %s)
                ON CONFLICT (knowledge_type) 
                DO UPDATE SET 
                    knowledge_data = EXCLUDED.knowledge_data,
                    updated_at = CURRENT_TIMESTAMP
            """,
                ("comprehensive_agent_training", json.dumps(knowledge_base)),
            )

            # Store in conv_chunks for hot memory pool
            knowledge_text = """
AGENT EVALUATION EXPERTISE KNOWLEDGE BASE

CURRENT SYSTEM STATUS:
- RAGChecker Baseline: Precision 0.159, Recall 0.166, F1 0.159
- Critical Issue: Fallback mode evaluation prevents advanced features
- Database Status: Empty - needs population with 000-500 content
- Memory Systems: Implemented but not populated

EVALUATION WORKFLOW:
1. Check database population (SELECT COUNT(*) FROM document_chunks)
2. Set environment variables (POSTGRES_DSN, GOLD_FILE)
3. Run evaluation (uv run python 300_evals/scripts/evaluation/ragchecker_official_evaluation.py)
4. Verify results (Precision ≥ 0.159, Recall ≥ 0.166)

MEMORY SYSTEM USAGE:
- Use unified_memory_orchestrator for memory operations
- Query hot memory pool for recent context (48-hour window)
- Maintain session continuity across evaluation runs
- Leverage episodic memory for enhanced context

TROUBLESHOOTING:
- If 0 contexts: populate database with semantic ingestion
- If fallback mode: fix evaluation integration
- If memory empty: run population scripts
- If config drift: verify parameter application

LESSONS LEARNED:
- Fallback mode evaluation prevents precision knobs from working
- Empty database prevents context retrieval
- Memory systems implemented but not integrated with RAG
- Configuration drift between setup and execution
            """.strip()

            # Store in conv_chunks for 48-hour hot memory
            cur.execute(
                """
                INSERT INTO conv_chunks (session_id, chunk_text, embedding, entities, salience_score, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    "agent_training_session",
                    knowledge_text,
                    None,  # Will be populated by embedding
                    ["evaluation", "memory", "agent_training", "expertise"],
                    1.0,  # High salience for agent training
                    "now()",
                ),
            )

            conn.commit()
            conn.close()

            print("✅ Agent knowledge base stored in database")
            return True

        except Exception as e:
            print(f"❌ Failed to store agent knowledge: {e}")
            return False

    def train_agents(self) -> bool:
        """Main method to train agents on evaluation system and memory usage"""

        print("🧠 Training agents on evaluation system and memory usage...")

        # 1. Populate knowledge base
        knowledge_base = self.populate_agent_knowledge_base()

        # 2. Store in database
        success = self.store_agent_knowledge(knowledge_base)

        if success:
            print("✅ Agent training complete!")
            print("📚 Agents now have comprehensive knowledge of:")
            print("   - Current evaluation system status and bottlenecks")
            print("   - Step-by-step evaluation workflows")
            print("   - Memory system usage and optimization")
            print("   - Troubleshooting patterns and solutions")
            print("   - Lessons learned and best practices")
            print("   - Quick reference for common tasks")

        return success


def main():
    """Main entry point for agent memory training"""

    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

    trainer = AgentMemoryTrainer(dsn)
    success = trainer.train_agents()

    if success:
        print("\n🎯 Next steps:")
        print("1. Populate database with 000-500 content")
        print("2. Fix evaluation integration to use real RAG system")
        print("3. Enable memory system integration in RAG pipeline")
        print("4. Test agent knowledge with evaluation runs")
    else:
        print("\n❌ Agent training failed - check database connection")


if __name__ == "__main__":
    main()
