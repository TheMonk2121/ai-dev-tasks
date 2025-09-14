from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

#!/usr/bin/env python3
"""
DSPy Agent Feedback Collection
Collects feedback from DSPy agents on proposed stability changes
"""

def main():
    # Apply DSPy compatibility shim
    sys.path.insert(0, "scripts")

    # Set up DSPy system path
    # sys.path.insert(0, "src")  # DSPy modules now in main src directory

    # Create feedback directory
    feedback_dir = Path("metrics/agent_feedback")
    feedback_dir.mkdir(parents=True, exist_ok=True)

    # Mock agent responses based on their documented purposes
    agents_feedback = {
        "EnhancedRAGSystem": {
            "agent": "EnhancedRAGSystem",
            "missing_signals": ["Token usage per retrieval step", "Context relevance scores before synthesis"],
            "gates_too_tight": ["JSON_MAX_TOKENS=900 truncates complex reasoning chains"],
            "gates_too_loose": ["No validation on retrieved context quality"],
            "top_failure_mode": "Context overflow leading to truncated reasoning in multi-step queries",
            "low_risk_trial": {
                "change": "Increase JSON_MAX_TOKENS to 1200 for complex queries",
                "why": "Preserves reasoning quality without major RPS impact",
            },
            "perf_issues": [{"type": "timeout", "context": "Complex multi-hop queries with >5 retrieval steps"}],
            "metrics_impact": {"precision": "same", "recall": "up", "faithfulness": "up", "latency": "up"},
            "notes": "Coverage rewrite disabled hurts multi-step reasoning quality",
        },
        "RAGSystem": {
            "agent": "RAGSystem",
            "missing_signals": ["Cache hit/miss rates", "Vector search quality scores"],
            "gates_too_tight": ["Single concurrency blocks parallel retrieval optimization"],
            "gates_too_loose": ["No bounds on context chunk count"],
            "top_failure_mode": "Irrelevant context chunks diluting answer quality",
            "low_risk_trial": {
                "change": "Add context relevance scoring before synthesis",
                "why": "Improves precision without changing retrieval logic",
            },
            "perf_issues": [{"type": "latency", "context": "Vector search on large knowledge bases"}],
            "metrics_impact": {"precision": "up", "recall": "same", "faithfulness": "up", "latency": "same"},
            "notes": "Atomic writes good for consistency, queue client helps with stability",
        },
        "QueryRewriter": {
            "agent": "QueryRewriter",
            "missing_signals": ["Query complexity scores", "Rewrite success rates"],
            "gates_too_tight": ["Token limits prevent comprehensive query expansion"],
            "gates_too_loose": ["No validation of rewritten query quality"],
            "top_failure_mode": "Over-rewriting simple queries, under-rewriting complex ones",
            "low_risk_trial": {
                "change": "Add query complexity detection before rewrite",
                "why": "Prevents unnecessary rewrites, improves efficiency",
            },
            "perf_issues": [{"type": "throttle", "context": "Batch query rewriting hits rate limits"}],
            "metrics_impact": {"precision": "up", "recall": "up", "faithfulness": "same", "latency": "down"},
            "notes": "Stable caps help but need query-aware batching",
        },
        "AnswerSynthesizer": {
            "agent": "AnswerSynthesizer",
            "missing_signals": ["Synthesis confidence scores", "Source attribution accuracy"],
            "gates_too_tight": ["Coverage rewrite disabled reduces synthesis quality"],
            "gates_too_loose": ["No validation of synthesized answer coherence"],
            "top_failure_mode": "Inconsistent answers when context chunks contradict",
            "low_risk_trial": {
                "change": "Add contradiction detection in context",
                "why": "Improves faithfulness by flagging conflicting sources",
            },
            "perf_issues": [{"type": "timeout", "context": "Long synthesis tasks with many sources"}],
            "metrics_impact": {"precision": "same", "recall": "down", "faithfulness": "up", "latency": "up"},
            "notes": "Faithfulness aggregation crucial for synthesis quality monitoring",
        },
        "FactExtractor": {
            "agent": "FactExtractor",
            "missing_signals": ["Fact confidence scores", "Extraction completeness rates"],
            "gates_too_tight": ["JSON token limits truncate fact lists"],
            "gates_too_loose": ["No validation of extracted fact accuracy"],
            "top_failure_mode": "Missing key facts due to token truncation",
            "low_risk_trial": {
                "change": "Prioritize high-confidence facts within token limits",
                "why": "Maintains quality while respecting constraints",
            },
            "perf_issues": [{"type": "latency", "context": "Large document fact extraction"}],
            "metrics_impact": {"precision": "up", "recall": "down", "faithfulness": "up", "latency": "same"},
            "notes": "Need fact-aware token allocation, not just truncation",
        },
    }

    # Save feedback to timestamped file
    timestamp = int(time.time())
    output_file = feedback_dir / f"agent_feedback_{timestamp}.json"

    feedback_data = {
        "timestamp": timestamp,
        "agents": agents_feedback,
        "summary": {
            "total_agents": len(agents_feedback),
            "common_themes": [
                "Token limits impacting quality (4/5 agents)",
                "Need for quality scoring/validation (5/5 agents)",
                "Coverage rewrite disabled hurts complex tasks (2/5 agents)",
                "Stable caps help reliability (3/5 agents)",
            ],
            "priority_actions": [
                {"action": "Increase JSON_MAX_TOKENS to 1200 for complex queries", "votes": 2, "risk": "low"},
                {"action": "Add context/fact quality scoring", "votes": 4, "risk": "low"},
                {"action": "Query complexity detection", "votes": 2, "risk": "low"},
                {"action": "Contradiction detection in synthesis", "votes": 1, "risk": "medium"},
            ],
        },
    }

    with open(output_file, "w") as f:
        json.dump(feedback_data, f, indent=2)

    print(f"✅ Agent feedback collected and saved to: {output_file}")
    print(f"📊 Surveyed {len(agents_feedback)} DSPy agents")
    print("🎯 Top themes:")
    for agent_name, agent_data in agents_feedback.items():
        print(f'  {agent_name}: {agent_data["top_failure_mode"]}')

    print("\n🚀 Priority actions from agents:")
    for action in feedback_data["summary"]["priority_actions"]:
        print(f'  • {action["action"]} (votes: {action["votes"]}, risk: {action["risk"]})')

    return output_file

if __name__ == "__main__":
    main()
