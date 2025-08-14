"""
Test Selection Utilities

Helper functions for marker-based test selection and tier mapping.
"""

from typing import List, Optional

# Tier mapping from criticality guide
TIER_ALIASES = {
    "1": "tier1",
    "2": "tier2",
    "3": "tier3",
}

# Test kind mapping
KIND_ALIASES = {
    "unit": "unit",
    "integration": "integration",
    "e2e": "e2e",
    "smoke": "smoke",
}

# Tier 1 critical components (from 400_code-criticality-guide.md)
TIER1_COMPONENTS = [
    "vector_store",
    "document_processor",
    "memory_rehydrator",
    "cursor_model_router",
]

# Tier 2 high priority components
TIER2_COMPONENTS = [
    "database_resilience",
    "prompt_sanitizer",
    "error_pattern_recognition",
    "anchor_metadata_parser",
]

# Tier 3 supporting components
TIER3_COMPONENTS = [
    "logger",
    "tokenizer",
    "metadata_extractor",
    "retry_wrapper",
]


def normalize_tier(tier: str) -> str:
    """Normalize tier input to standard format"""
    return TIER_ALIASES.get(tier, tier)


def normalize_kind(kind: str) -> str:
    """Normalize test kind input to standard format"""
    return KIND_ALIASES.get(kind, kind)


def build_marker_expression(
    tiers: Optional[List[str]] = None, kinds: Optional[List[str]] = None, extra_expr: Optional[str] = None
) -> Optional[str]:
    """
    Build pytest marker expression from tier and kind specifications.

    Args:
        tiers: List of tier specifications (e.g., ["1", "tier2"])
        kinds: List of test kinds (e.g., ["unit", "smoke"])
        extra_expr: Additional marker expression to combine

    Returns:
        Combined marker expression or None if no filters specified
    """
    parts = []

    if tiers:
        # Normalize and deduplicate tiers
        tier_marks = [normalize_tier(t) for t in tiers]
        tier_marks = sorted(set(tier_marks))
        parts.append("(" + " or ".join(tier_marks) + ")")

    if kinds:
        # Normalize and deduplicate kinds
        kind_marks = [normalize_kind(k) for k in kinds]
        kind_marks = sorted(set(kind_marks))
        parts.append("(" + " or ".join(kind_marks) + ")")

    if extra_expr:
        parts.append(f"({extra_expr})")

    if not parts:
        return None  # No marker filter → run everything (legacy default)

    return " and ".join(parts)


def get_tier_for_component(component_name: str) -> Optional[str]:
    """
    Get the tier for a given component name.

    Args:
        component_name: Name of the component (e.g., "vector_store")

    Returns:
        Tier string or None if not found
    """
    if component_name in TIER1_COMPONENTS:
        return "tier1"
    elif component_name in TIER2_COMPONENTS:
        return "tier2"
    elif component_name in TIER3_COMPONENTS:
        return "tier3"
    return None


def validate_marker_expression(expr: str) -> bool:
    """
    Basic validation of marker expression syntax.

    Args:
        expr: Marker expression to validate

    Returns:
        True if expression appears valid
    """
    if not expr:
        return True

    # Basic syntax checks
    open_parens = expr.count("(")
    close_parens = expr.count(")")

    if open_parens != close_parens:
        return False

    # Check for basic logical operators
    valid_operators = [" and ", " or ", " not "]
    has_operator = any(op in expr for op in valid_operators)

    # Simple expressions without operators are valid
    if not has_operator and "(" not in expr and ")" not in expr:
        return True

    # Expressions with operators should have parentheses
    if has_operator and open_parens == 0:
        return False

    return True


def get_suggested_markers() -> dict:
    """
    Get suggested marker combinations for common scenarios.

    Returns:
        Dictionary of scenario descriptions to marker expressions
    """
    return {
        "Fast PR Gate": "tier1 and smoke",
        "Critical Unit Tests": "tier1 and unit",
        "Production Integration": "tier1 and tier2 and integration",
        "Full Critical Path": "tier1",
        "All High Priority": "tier1 or tier2",
        "Supporting Utilities": "tier3",
        "End-to-End Only": "e2e",
        "No End-to-End": "not e2e",
    }
