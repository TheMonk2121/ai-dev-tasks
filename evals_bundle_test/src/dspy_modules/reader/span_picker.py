#!/usr/bin/env python3
"""
Rule-first span picker for deterministic extractive answers.
Falls back to LLM only when deterministic extraction fails.
"""

import re

SQL_HINTS = r"(create|alter|drop|index|table|materialized|view|foreign key|primary key|using|gin|gist|ivfflat|to_tsvector|tsquery|websearch_to_tsquery)"


def looks_like_command(question: str) -> bool:
    """Check if question is asking for a command or operational instruction."""
    ql = question.lower()
    return any(k in ql for k in ("how do i run", "command", "profile", "run the gold", "evaluate"))


def extract_code_block(text: str) -> str | None:
    """Extract the first code block from text."""
    # Look for code blocks with backticks
    code_block_match = re.search(r"```(?:bash|sh|python|py)?\n(.*?)\n```", text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1).strip()

    # Look for indented code blocks (4+ spaces)
    lines = text.split("\n")
    code_lines = []
    in_code_block = False

    for line in lines:
        if re.match(r"^    ", line):  # 4+ spaces
            in_code_block = True
            code_lines.append(line[4:])  # Remove indentation
        elif in_code_block and line.strip() == "":
            code_lines.append("")
        elif in_code_block and not re.match(r"^    ", line):
            break

    if code_lines:
        return "\n".join(code_lines).strip()

    return None


# Command extraction regex for shell commands
CMD_RE = re.compile(r"(?m)^\s*(?:env\s+[-\w= ]+ )?(?:uv|python|pipx|make)\b[^\n]*$")


def extract_command_line(text: str) -> str | None:
    """Extract command lines from text."""
    # Look for command patterns: uv run, python, make, etc.
    match = CMD_RE.search(text)
    if match:
        return match.group(0).strip()
    return None


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

    # Special handling for command-style questions
    if looks_like_command(question):
        # Look for code blocks first
        code_block = extract_code_block(context)
        if code_block and len(code_block) <= 200:
            return code_block

        # Look for command lines using regex
        command_line = extract_command_line(context)
        if command_line and len(command_line) <= 200:
            return command_line

        # Fallback: Look for command-like lines
        lines = [line.strip() for line in context.splitlines() if line.strip()]
        for line in lines:
            # Match command patterns: uv run, python, make, etc.
            if re.search(r"^(uv run|python|make|npm|yarn|git|docker)", line) and len(line) <= 200:
                return line

    # For general questions, be very selective about span extraction
    # Only extract spans for specific question types
    general_question_indicators = ["what", "how", "why", "when", "where", "who"]
    question_lower = question.lower()
    is_general_question = any(indicator in question_lower for indicator in general_question_indicators)

    if is_general_question:
        # For general questions, only extract spans if they're very specific matches
        # Skip most span extraction to let DSPy generator handle it
        return None

    lines = [line.strip() for line in context.splitlines() if line.strip()]

    # 1) Exact file path match (highest priority)
    # Only extract file paths if the question is asking for file paths specifically
    file_keywords = ["file", "path", "where", "location", "guide", "doc", "document"]
    question_lower = question.lower()
    is_file_question = any(keyword in question_lower for keyword in file_keywords)

    if is_file_question:
        for line in lines:
            # Match file paths like: path/to/file.ext, ./file.ext, file.ext
            # Exclude database connection strings and URLs
            if re.search(r"[A-Za-z0-9/_\-]+\.[A-Za-z0-9]+", line) and not re.search(
                r"(postgresql://|http://|https://|://)", line
            ):
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
            # Filter out database connection strings and other non-answer content
            filtered_quoted = [
                q
                for q in quoted
                if not re.search(
                    r"(postgresql://|http://|https://|://|database|connection|DATABASE_URL|connection_string)", q
                )
            ]
            if filtered_quoted:
                # Return the longest filtered quoted phrase
                longest_quote = max(filtered_quoted, key=len)
                if len(longest_quote) <= 180:
                    return longest_quote

    # 4) Single line answers (fourth priority) - be much more selective
    for line in lines:
        # Only return lines that look like actual answers, not system artifacts
        if (
            len(line) <= 180
            and not line.startswith("===")
            and not re.search(
                r"(postgresql://|http://|https://|://|❌|✅|├──|└──|scripts/|test_|MEMORY_SYSTEM|database|connection|os\.getenv|connection_string)",
                line,
            )
            and len(line.split()) >= 3  # At least 3 words
            and not line.isupper()  # Not all caps
            and not re.search(r"^[A-Za-z0-9_\-\.]+$", line)  # Not just identifiers
            and not re.search(r"=.*postgresql://", line)  # Not assignment statements with postgresql
        ):
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

    # Remove metadata chunks like [file.md#chunk:abc123]
    normalized = re.sub(r"\[[^\]]*\.md#[^\]]*\]", "", normalized)

    # Remove excessive whitespace and clean up
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # Limit length for better readability
    if len(normalized) > 300:
        normalized = normalized[:297] + "..."

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
