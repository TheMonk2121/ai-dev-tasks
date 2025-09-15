from __future__ import annotations

def check_canary_percentage(current_percentage: int, max_percentage: int = 50) -> bool:
    """Check if canary percentage is within limits."""
    return current_percentage <= max_percentage