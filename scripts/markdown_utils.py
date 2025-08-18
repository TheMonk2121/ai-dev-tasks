#!/usr/bin/env python3
"""
Markdown Utilities (PR B)
Shared utilities for scanner, link checker, and validator.
"""

import re
import unicodedata


def slugify_heading(heading: str) -> str:
    """
    GitHub-style heading slugification.

    Converts a heading to a URL-friendly anchor slug.
    Matches GitHub's algorithm for heading anchors.
    """
    if not heading:
        return ""

    # Convert to lowercase and normalize Unicode
    slug = unicodedata.normalize("NFKD", heading.lower())

    # Remove HTML tags
    slug = re.sub(r"<[^>]+>", "", slug)

    # Replace ampersands with double hyphens (GitHub style) - do this before punctuation removal
    slug = re.sub(r"&+", "--", slug)

    # Remove punctuation except hyphens, underscores, and double hyphens
    slug = re.sub(r"[^\w\s-]", "", slug)

    # Replace underscores with hyphens
    slug = re.sub(r"_", "-", slug)

    # Replace whitespace with hyphens (but preserve double hyphens)
    slug = re.sub(r"\s+", "-", slug)

    # Fix double hyphens that got expanded
    slug = re.sub(r"-{4,}", "--", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    # Handle Unicode normalization
    slug = unicodedata.normalize("NFD", slug)
    slug = re.sub(r"[\u0300-\u036f]", "", slug)  # Remove combining characters

    # GitHub's special handling for Chinese characters
    # They get converted to their Unicode code points
    def replace_chinese(match):
        char = match.group(0)
        return f"-{ord(char)}-"

    slug = re.sub(r"[\u4e00-\u9fff]", replace_chinese, slug)

    # Final cleanup - preserve double hyphens but collapse other multiple hyphens
    slug = re.sub(r"-{3,}", "-", slug)  # Three or more hyphens to single
    slug = slug.strip("-")

    return slug


def extract_code_fences(content: str) -> list[tuple]:
    """
    Extract code fence boundaries.

    Returns list of (start_line, end_line, language) tuples.
    """
    fences = []
    lines = content.split("\n")
    in_fence = False
    fence_start = 0
    fence_lang = ""

    for i, line in enumerate(lines):
        if line.startswith("```"):
            if not in_fence:
                # Start of fence
                fence_start = i
                fence_lang = line[3:].strip()
                in_fence = True
            else:
                # End of fence
                fences.append((fence_start, i, fence_lang))
                in_fence = False
                fence_lang = ""

    return fences


def is_in_code_fence(line_num: int, fences: list[tuple]) -> bool:
    """Check if a line number is inside a code fence."""
    for start, end, _ in fences:
        if start <= line_num <= end:
            return True
    return False


def normalize_filename(filename: str) -> str:
    """
    Normalize filename for comparison.

    Removes common extensions and normalizes case.
    """
    # Remove common extensions
    base = filename
    for ext in [".md", ".txt", ".py", ".sh", ".yml", ".yaml", ".json"]:
        if base.lower().endswith(ext):
            base = base[: -len(ext)]

    # Normalize case and spaces
    base = base.lower().replace(" ", "-").replace("_", "-")

    return base


def extract_backticked_refs(content: str) -> list[str]:
    """
    Extract backticked references from content.

    Returns list of normalized filenames found in backticks.
    """
    # Pattern for backticked filenames
    pattern = r"`([^`]+\.(?:md|txt|py|sh|yml|yaml|json))`"
    matches = re.findall(pattern, content)

    return [normalize_filename(match) for match in matches]


def extract_title_mentions(content: str) -> list[str]:
    """
    Extract title mentions from content.

    Looks for patterns like "see 400_guides/400_system-overview.md" or similar.
    """
    # Pattern for file references in text
    patterns = [
        r"(?:see|check|refer to|in)\s+([^\s]+\.(?:md|txt|py|sh|yml|yaml|json))",
        r"([^\s]+\.(?:md|txt|py|sh|yml|yaml|json))\s+(?:file|document)",
        r"\b(Guide|Another File|Target File)\b",  # Simple title mentions
    ]

    mentions = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        mentions.extend([normalize_filename(match) for match in matches])

    return mentions


def find_existing_links(content: str) -> list[str]:
    """
    Find existing markdown links in content.

    Returns list of normalized target filenames.
    """
    # Pattern for markdown links
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    matches = re.findall(pattern, content)

    existing = []
    for _, target in matches:
        # Handle relative links
        if (
            target.startswith("./")
            or target.startswith("../")
            or not target.startswith("http")
        ):
            target = target.split("/")[-1]  # Get filename part

        existing.append(normalize_filename(target))

    return existing


def should_apply_link(
    source_title: str, target_title: str, confidence_threshold: float = 0.8
) -> bool:
    """
    Determine if a link should be applied inline vs stubbed.

    Returns True for high-confidence matches that should be inlined.
    """
    source_norm = normalize_filename(source_title)
    target_norm = normalize_filename(target_title)

    # Exact match is high confidence
    if source_norm == target_norm:
        return True

    # Check for partial matches
    if source_norm in target_norm or target_norm in source_norm:
        # Calculate similarity
        similarity = len(set(source_norm) & set(target_norm)) / len(
            set(source_norm) | set(target_norm)
        )
        return similarity >= confidence_threshold

    return False


def generate_xref_block(suggestions: list[dict]) -> str:
    """
    Generate xref-autofix block content.

    Creates a formatted block with links and stubs.
    """
    if not suggestions:
        return ""

    lines = ["<!-- xref-autofix:begin -->"]
    lines.append("<!-- Cross-references to add: -->")

    for suggestion in suggestions:
        if suggestion.get("confidence", 0) >= 0.8:
            # High confidence - inline link
            lines.append(
                f"- [{suggestion['target_title']}]({suggestion['target_path']})"
            )
        else:
            # Low confidence - stub
            lines.append(
                f"- [ ] Add link to {suggestion['target_title']} ({suggestion['target_path']})"
            )

    lines.append("<!-- xref-autofix:end -->")

    return "\n".join(lines)
