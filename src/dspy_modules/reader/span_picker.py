from __future__ import annotations
import re
import os
#!/usr/bin/env python3
"""
Rule-first span picker for deterministic extractive answers.
Falls back to LLM only when deterministic extraction fails.
"""


SQL_HINTS = r"(create|alter|drop|index|table|materialized|view|foreign key|primary key|using|gin|gist|ivfflat|to_tsvector|tsquery|websearch_to_tsquery)"


def pick_span(context: str, question: str, tag: str) -> str | None:
    """
    Deterministically extract the best answer span from context.

    Args:
        context: Retrieved context text
        question: User question
        tag: Query tag (e.g., 'db_workflows', 'rag_qa_single')

    Returns:
        Extracted span or None if no deterministic match
    """
    if not context or not context.strip():
        return None

    lines = [line.strip() for line in context.splitlines() if line.strip()]

    # 1) Exact file path match (highest priority)
    # If question mentions file/guide/doc/path/where, prioritize file paths
    # Note: file_priority detection could be used for future enhancements

    for line in lines:
        # Match file paths like: path/to/file.ext, ./file.ext, file.ext
        if re.search(r"[A-Za-z0-9/_\-]+\.[A-Za-z0-9]+", line):
            # Clean up the path
            path_match = re.search(r"[A-Za-z0-9/_\-]+\.[A-Za-z0-9]+", line)
            if path_match:
                return path_match.group(0)

    # 2) SQL lines for db_workflows (second priority)
    if tag == "db_workflows":
        sql_lines = [line for line in lines if re.search(SQL_HINTS, line.lower())]
        if sql_lines:
            # Return the shortest SQL line (most precise)
            shortest_sql = min(sql_lines, key=len)
            # Limit to 180 chars for consistency
            return shortest_sql[:180]

    # 3) Quoted phrases (third priority)
    for line in lines:
        # Look for quoted strings
        quoted = re.findall(r'"([^"]+)"', line)
        if quoted:
            # Return the longest quoted phrase
            longest_quote = max(quoted, key=len)
            if len(longest_quote) <= 180:
                return longest_quote

    # 4) Single line answers (fourth priority)
    for line in lines:
        if len(line) <= 180 and not line.startswith("==="):
            return line

    return None


def normalize_answer(answer: str, tag: str = "") -> str:
    """
    Post-process answer to improve F1 scoring.

    Args:
        answer: Raw answer from model or span picker
        tag: Query tag for tag-specific normalization

    Returns:
        Normalized answer
    """
    if not answer:
        return "I don't know"

    # Strip trailing semicolons, backticks, double spaces
    normalized = answer.strip()
    normalized = re.sub(r";+$", "", normalized)  # Remove trailing semicolons
    normalized = re.sub(r"`+$", "", normalized)  # Remove trailing backticks
    normalized = re.sub(r"\s+", " ", normalized)  # Normalize whitespace

    # Tag-specific normalization for db_workflows
    if tag == "db_workflows":
        # Trim to first line for SQL statements
        normalized = normalized.split("\n")[0].strip()
        # If multiple SQL keywords, keep the shortest line
        if len(re.findall(r"\b(create|alter|drop|index|table)\b", normalized.lower())) > 1:
            lines = [line.strip() for line in answer.split("\n") if line.strip()]
            sql_lines = [line for line in lines if re.search(r"\b(create|alter|drop|index|table)\b", line.lower())]
            if sql_lines:
                normalized = min(sql_lines, key=len)

    # Enforce 180 char limit
    if len(normalized) > 180:
        normalized = normalized[:177] + "..."

    return normalized
