def track_few_shot_provenance(few_shot_ids: list[str], pool_version: str, selector_seed: int) -> dict[str, Any]:
    """Track few-shot provenance information."""
    return {
        "few_shot_ids": few_shot_ids,
        "pool_version": pool_version,
        "selector_seed": selector_seed,
        "timestamp": datetime.now().isoformat(),
        "leakage_guard": True,
    }
