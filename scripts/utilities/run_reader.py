from __future__ import annotations

import json
import os
import sys
from typing import Any

#!/usr/bin/env python3
"""
Mock reader script for testing the reader gate.
"""


def mock_reader(query: str, context: str, tag: str, case_id: str) -> str:
    """
    Mock reader that returns answers based on query patterns.
    """
    query_lower: Any = query.lower()

    # Pattern matching for known queries
    if "dspy" in query_lower and "framework" in query_lower:
        return "a framework for declarative optimization of prompts and programs"

    if "core workflow guides" in query_lower or "000_core" in query_lower:
        return "000_evaluation-system-entry-point.md, 001_create-prd-TEMPLATE.md, 002_generate-tasks-TEMPLATE.md, 003_process-task-list-TEMPLATE.md"

    if "memory system" in query_lower and "400_06" in query_lower:
        return "a sophisticated memory context system to maintain state across Cursor AI sessions"

    # Generic fallback based on context
    if context and context.strip():
        # Look for key phrases in context
        context_lower: Any = context.lower()

        if "framework" in context_lower and "optimization" in context_lower:
            return "a framework for declarative optimization of prompts and programs"

        if "memory" in context_lower and "context" in context_lower:
            return "a sophisticated memory context system to maintain state across AI sessions"

        if "workflow" in context_lower and "template" in context_lower:
            return "core workflow guides include evaluation system entry point, PRD creation template, task generation template, and task processing template"

    # Final fallback
    return f"Based on the context, this appears to be related to {tag}."


def main() -> Any:
    """Main entry point for the reader script."""
    try:
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())

        query: Any = input_data.get("query", "")
        context: Any = input_data.get("context", "")
        tag: Any = input_data.get("tag", "")
        case_id: Any = input_data.get("case_id", "")

        # Generate answer
        answer = mock_reader(query, context, tag, case_id)

        # Return JSON response
        response = {"answer": answer, "query": query, "tag": tag, "case_id": case_id}

        print(json.dumps(response))

    except Exception as e:
        # Return error response
        error_response = {"answer": f"Error processing query: {str(e)}", "error": str(e)}
        print(json.dumps(error_response))
        sys.exit(1)


if __name__ == "__main__":
    main()
