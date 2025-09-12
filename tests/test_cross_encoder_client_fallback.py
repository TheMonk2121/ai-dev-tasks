from __future__ import annotations
import asyncio
import time
from src.retrieval.cross_encoder_client import CrossEncoderClient
from tests.property._regression_capture import record_case
import os
#!/usr/bin/env python3
"""
Test CrossEncoderClient timeout/fallback behavior.
"""

class _SlowDummyCrossEncoder:
    def rerank(self, query, batch, text_field):
        # Simulate slow inference beyond timeout
        time.sleep(0.05)
        return [0.5 for _ in batch]

def test_cross_encoder_timeout_falls_back_to_heuristic():
    async def _run():
        client = CrossEncoderClient(onnx_path=None, timeout_ms=1, max_timeout_ms=1)
        # Inject dummy to force using cross-encoder path, then exceed timeout
        client.cross_encoder = _SlowDummyCrossEncoder()

        candidates = [
            {"text": "Alpha beta gamma", "score": 0.1},
            {"text": "Gamma delta epsilon", "score": 0.2},
        ]

        res = await client.rerank_async("alpha", candidates, text_field="text")
        if res.method != "heuristic_fallback":
            record_case("cross_encoder_timeout_not_fallback", {"method": res.method, "scores": res.scores})
        assert res.method == "heuristic_fallback"
        assert len(res.scores) == len(candidates)
        # Scores normalized 0-1 by heuristic fallback
        assert all(0.0 <= s <= 1.0 for s in res.scores)

    asyncio.run(_run())
