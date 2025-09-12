from __future__ import annotations

def block_deployment_if_unsafe(canary_percentage: int, eval_passes: int) -> bool:
    """Block deployment if canary percentage is too high or eval passes insufficient."""
    max_canary = 50
    required_passes = 2

    if canary_percentage > max_canary:
        print(f"❌ Canary percentage {canary_percentage}% exceeds limit {max_canary}%")
        return False

    if eval_passes < required_passes:
        print(f"❌ Eval passes {eval_passes} below required {required_passes}")
        return False

    return True